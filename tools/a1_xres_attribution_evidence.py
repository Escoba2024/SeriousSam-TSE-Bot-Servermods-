"""Pure attribution of current bounded RECORD connections, never a gain verdict."""
import json
import math
import struct
from xres_pid_method import uint,require,same,valid_version

CLAIMS=dict(qualified=False,a1_pass=False,gain_fixed=False,old_u_attributed=False,continuous_lifetime_outside_record=False)


def snapshot(s,expected):
 require(s.get('record_enabled')is True and same(s.get('lifecycle_coverage'),dict(client_started=True,client_died=True)),'enabled lifecycle observation required')
 require(valid_version(s.get('xres_version'))and type(s.get('query_clients_status'))is int and s['query_clients_status']==1,'actual XRes version/QueryClients status')
 require(s.get('errors')==[],'native metadata error')
 require(type(s.get('index'))is int and s['index']in(0,1),'distinct actual snapshot index')
 ids=expected['identities'];ns=expected['pid_namespace'];scope=expected.get('scope','A1_154')
 require(scope in('A1_154','OWN_METHOD_167'),'fixed attribution scope');display=':154'if scope=='A1_154'else':167'
 resource_roles=expected.get('resource_roles',{'controller_transport':'parent','original_window_owner':'vanilla'})
 require(same(resource_roles,{'controller_transport':'parent'if scope=='A1_154'else'vanilla','original_window_owner':'vanilla'}),'fixed actual resource-role mapping')
 require(set(ids)=={'parent','recorder','display','vanilla'}and isinstance(ns,str)and ns.startswith('pid:['),'exact owned role identities')
 for role,pin in ids.items():
  require(uint(pin.get('pid'),0x7fffffff)>0 and uint(pin.get('start_ticks'),2**64-1)>0 and pin.get('pid_namespace')==ns and pin.get('display')==display,'positive own process generation and namespace')
 for key in('process_before','process_after'):require(same(s.get(key),ids),'own PID/start/namespace changed')
 for key in('monotonic_started','monotonic_finished'):require(type(s.get(key))in(int,float)and math.isfinite(s[key])and s[key]>=0,'metadata monotonic clock')
 require(0<=s['monotonic_finished']-s['monotonic_started']<=3,'existing metadata operation deadline')
 for key in('callback_serial_before','callback_serial_after'):require(uint(s.get(key))>=1,'metadata must be inside actual RECORD interval')
 require(s['callback_serial_before']<=s['callback_serial_after'],'callback watermark reversed')
 clients=s.get('clients');require(isinstance(clients,list)and 1<=len(clients)<=64,'bounded QueryClients')
 for row in clients:
  b=uint(row.get('resource_base'));m=uint(row.get('resource_mask'));require((b==0 or b>3)and m>0 and b&m==0,'invalid background range')
 require(len({r['resource_base']for r in clients})==len(clients),'duplicate range')
 ctx=s.get('context_clients');require(isinstance(ctx,list)and len(ctx)==len(set(ctx))and 2 in ctx,'actual FutureClients and distinct context required')
 for b in ctx:require(type(b)is int and (b==2 or 3<b<=0xffffffff),'actual context base')
 targets=sorted(b for b in ctx if b!=2);require(2<=len(targets)<=32,'max32 positive context bases')
 bindings=s.get('bindings');require(isinstance(bindings,dict)and set(bindings)=={'controller_transport','original_window_owner'}and len(set(bindings.values()))==2 and set(bindings.values())<=set(targets),'actual existing resource bindings')
 queries=s.get('queries');require(isinstance(queries,list)and len(queries)==len(targets)+2<=34,'exact bounded base/resource query coverage')
 target_spec=[('base',b)for b in targets]+[(k,expected['resources'][k])for k in('controller_transport','original_window_owner')]
 answer={}
 for query,(kind,xid)in zip(queries,target_spec):
  require(uint(xid)>3 and query.get('requested_kind')==kind and type(query.get('requested_xid'))is int and query['requested_xid']==xid,'exact query target/order, no wildcard')
  matches=[c for c in clients if xid&(~c['resource_mask']&0xffffffff)==c['resource_base']];require(len(matches)==1 and matches[0]['resource_base']>3,'unique positive own target range')
  base=matches[0]['resource_base'];require(base==(xid if kind=='base'else bindings[kind]),'resource/RECORD range binding changed')
  require(type(query.get('query_status'))is int and query['query_status']==0 and type(query.get('num_ids'))is int and query['num_ids']==1 and isinstance(query.get('ids'),list)and len(query['ids'])==1,'Success0 and single PID required')
  v=query['ids'][0];require(type(v.get('mask'))is int and v['mask']==2 and type(v.get('length'))is int and v['length']==4,'PID mask/CARD32 length')
  require(uint(v.get('spec_client'))&(~matches[0]['resource_mask']&0xffffffff)==base,'reply from different client')
  pid=uint(v.get('pid'),0x7fffffff);require(pid>0,'missing PID is UNKNOWN, never interval proof')
  if kind=='base':answer[base]=pid
  else:require(answer.get(base)==pid==ids[resource_roles[kind]]['pid'],'existing resource PID differs from actual owned role')
 require(same(s.get('free_counts'),dict(client_arrays_allocated=1,client_arrays_freed=1,id_arrays_allocated=len(queries),id_arrays_freed=len(queries))),'metadata array cleanup differs')
 return answer


def lifecycle(rows,opcode):
 from xrecord_core_method import CoreTrace
 require(isinstance(rows,list)and 2<=len(rows)<=1024,'bounded full RECORD stream')
 decoder=CoreTrace(xtest_opcode=opcode);edges=set();last=-1.
 for i,row in enumerate(rows):
  require(type(row.get('callback_serial'))is int and row['callback_serial']==i+1,'complete callback order')
  clock=row.get('received_monotonic');require(type(clock)in(int,float)and math.isfinite(clock)and clock>=last,'actual callback clock order');last=clock
  require(type(row.get('client_swapped'))is bool,'actual native client-swapped Bool required')
  raw=bytes.fromhex(row['wire_hex']);fresh=decoder.accept(category=row['category'],client_base=row['client_base'],client_sequence=row['client_sequence'],server_time=row['server_time'],client_swapped=row['client_swapped'],wire=raw)
  require(fresh['kind']==row.get('kind'),'raw category/kind mismatch')
  if fresh['kind']in('client_started','client_died'):
   base=uint(row['client_base']);require(base>3,'positive lifecycle client base')
   if fresh['kind']=='client_started':
    endian='>'if row['client_swapped']else'<'
    require(len(raw)>=40 and raw[0]==1 and struct.unpack_from(endian+'H',raw,2)[0]==11 and len(raw)==8+4*struct.unpack_from(endian+'H',raw,6)[0],'valid bounded actual connection setup')
    b,m=struct.unpack_from(endian+'II',raw,12);require(b==base and m>0 and b&m==0,'setup base/mask differs from RECORD metadata')
   edges.add(base)
 require(rows[0]['kind']=='start'and rows[-1]['kind']=='end'and sum(r['kind']=='start'for r in rows)==sum(r['kind']=='end'for r in rows)==1,'actual full Start/End boundary')
 return edges


def attribute(rows,snapshots,expected,native):
 require(isinstance(native,dict)and native.get('lifecycle_verified')is True,'actual lifecycle range checks required')
 for key in('errors','cleanup_errors'):require(native.get(key)==[],'native/cleanup failure')
 for key in('malformed','dropped'):require(type(native.get(key))is int and native[key]==0,'complete native callback coverage')
 require(native.get('budget_failed')is False and all(native.get(k)is True for k in('end_verified','context_freed','connections_closed')),'normal bounded recorder close')
 require(native.get('calls')==native.get('freed')==native.get('records')==len(rows)and native.get('start_count')==native.get('end_count')==1,'full native data freed/drained')
 edges=lifecycle(rows,expected['xtest_opcode'])
 require(isinstance(snapshots,list)and len(snapshots)==2,'exactly two real enabled snapshots')
 maps=[snapshot(s,expected)for s in snapshots];a,b=snapshots
 require(all(rows[0]['received_monotonic']<=s['monotonic_started']<=s['monotonic_finished']<=rows[-1]['received_monotonic']for s in snapshots),'snapshot outside same-worker callback interval')
 require(a['index']==0 and b['index']==1 and a['monotonic_finished']<=b['monotonic_started'],'actual snapshot invocation order')
 require(1<=a['callback_serial_before']<=a['callback_serial_after']<=b['callback_serial_before']<=b['callback_serial_after']<len(rows),'snapshots strictly inside RECORD Start/End')
 original=expected['identities']['vanilla']['pid'];bound=sorted(base for base,pid in maps[0].items()if pid==original and maps[1].get(base)==original and base not in edges)
 selected=[r for r in rows if r['kind']in('query_pointer_request','query_pointer_reply','warp_request')]
 return dict(status='BOUND_CURRENT_RECORD_CONNECTION_TO_OWN_ORIGINAL_PID_ONLY',original_bases=bound,lifecycle_changed_bases=sorted(edges),own_original_request_rows=sum(r['client_base']in bound for r in selected),unknown_request_rows=sum(r['client_base']not in bound for r in selected),**CLAIMS)
