"""Pure XRes metadata verdicts. No library loading, processes or X calls."""
import json
import math

ROLES=('display','driver','peer','attributor')
LIMITS=dict(display=':167',controller_seconds=30,metadata_seconds=15,operation_seconds=2,snapshot_seconds=3,cleanup_seconds=5,ipc_bytes=16384,clients_max=64,queries_per_snapshot=6,snapshots=2)


def require(value,message):
 if not value:raise ValueError(message)


def uint(value,maximum=0xffffffff):
 require(type(value)is int and 0<=value<=maximum,'unsigned integer/type bound')
 return value


def same(a,b):return json.dumps(a,sort_keys=True,allow_nan=False)==json.dumps(b,sort_keys=True,allow_nan=False)


def valid_version(value):
 return isinstance(value,list)and len(value)==2 and all(type(v)is int for v in value)and value[0]==1 and 2<=value[1]<=65535


def validate_snapshot(snapshot,expected):
 require(isinstance(snapshot,dict)and isinstance(expected,dict),'snapshot/expected object required')
 identities=expected.get('identities',{});namespace=expected.get('pid_namespace')
 require(set(identities)==set(ROLES)and isinstance(namespace,str)and namespace.startswith('pid:['),'four actual own role identities required')
 for role,identity in identities.items():
  require(0<uint(identity.get('pid'),0x7fffffff)and 0<uint(identity.get('start_ticks'),2**64-1),'positive PID/start generation required')
  require(identity.get('display')==':167'and identity.get('pid_namespace')==namespace,'same own display/PID namespace required')
  require(isinstance(identity.get('argv'),list)and identity['argv']and all(isinstance(v,str)for v in identity['argv']),'actual own argv required')
 require(len({v['pid']for v in identities.values()})==4,'four distinct own processes required')
 for stage in('process_before','process_after'):
  actual=snapshot.get(stage)
  require(isinstance(actual,dict)and set(actual)==set(ROLES)and same(actual,identities),'actual process/PID namespace/start changed at '+stage)
 require(valid_version(snapshot.get('xres_version')),'XRes protocol1.2 required')
 require(type(snapshot.get('index'))is int and snapshot['index']in(0,1),'actual snapshot index required')
 require(type(snapshot.get('ipc_request_serial'))is int and snapshot['ipc_request_serial']>0,'actual snapshot IPC receipt required')
 clocks=[snapshot.get(k)for k in('parent_started','monotonic_started','monotonic_finished','parent_finished')]
 require(all(type(v)in(int,float)and math.isfinite(v)for v in clocks)and 0<=clocks[0]<=clocks[1]<=clocks[2]<=clocks[3]and clocks[3]-clocks[0]<=3,'bounded actual snapshot clock envelope required')
 require(snapshot.get('errors')==[],'native X error or missing error receipt')
 require(type(snapshot.get('query_clients_status'))is int and snapshot['query_clients_status']==1,'QueryClients success1 required')
 clients=snapshot.get('clients')
 require(isinstance(clients,list)and 1<=len(clients)<=64,'bounded client range array required')
 bases=[]
 for item in clients:
  base=uint(item.get('resource_base'));mask=uint(item.get('resource_mask'))
  require((base==0 or base>3)and mask>0 and not base&mask,'invalid client range')
  bases.append(base)
 require(len(set(bases))==len(bases),'duplicate client base')
 resources=expected.get('resources')
 require(isinstance(resources,list)and len(resources)==3,'exact known connections required')
 require([(v.get('role'),v.get('connection_index'))for v in resources]==[('driver',0),('driver',1),('peer',0)]and all(type(v.get('connection_index'))is int for v in resources),'exact driver2/peer1 topology')
 results=snapshot.get('results');require(isinstance(results,list)and len(results)==6,'exactly six resource/base queries required')
 matched=[]
 for i,target in enumerate(resources):
  xid=uint(target.get('resource'));require(xid>3,'known own resource required')
  matches=[v for v in clients if xid&(~v['resource_mask']&0xffffffff)==v['resource_base']]
  require(len(matches)==1,'resource client range absent/ambiguous')
  client=matches[0];base=client['resource_base'];require(base>3,'own resource must belong to a positive client base');matched.append(base)
  for j,(kind,requested)in enumerate((('resource',xid),('base',base))):
   row=results[i*2+j]
   require(row.get('requested_kind')==kind and type(row.get('requested_xid'))is int and row['requested_xid']==requested,'actual resource/base query order differs')
   require(type(row.get('query_status'))is int and row['query_status']==0,'QueryClientIds requires Success0')
   require(type(row.get('num_ids'))is int and row['num_ids']==1 and isinstance(row.get('ids'),list)and len(row['ids'])==1,'missing/ambiguous PID is UNKNOWN')
   value=row['ids'][0]
   require(type(value.get('mask'))is int and value['mask']==2 and type(value.get('length'))is int and value['length']==4,'exact PID mask/CARD32 byte length required')
   spec=uint(value.get('spec_client'));require(spec&(~client['resource_mask']&0xffffffff)==base,'reply spec client belongs to another connection')
   pid=uint(value.get('pid'),0x7fffffff)
   require(pid>0 and pid==identities[target['role']]['pid'],'PID unavailable or wrong own process')
 require(len(set(matched))==3,'three distinct own connections required')
 require(same(snapshot.get('free_counts'),dict(client_arrays_allocated=1,client_arrays_freed=1,id_arrays_allocated=6,id_arrays_freed=6)),'all allocated arrays must be freed exactly once')
 return dict(status='SNAPSHOT_XRES_PID_MATCHED_ONLY',matched_connections=3,pid_rows=6,resource_bases=matched,historical_u_attributed=False,continuous_client_lifetime_proven=False,a1_pass=False,retail_qualified=False)


def method_verdict(row):
 errors=[]
 try:
  require(row.get('errors')==[],'method/cleanup errors')
  require(all(row.get(flag,False)is False for flag in('historical_u_attributed','continuous_client_lifetime_proven','a1_pass','retail_qualified')),'forbidden historical/interval/A1/Retail claim')
  require(isinstance(row.get('snapshots'),list)and len(row['snapshots'])==2,'two real snapshots required')
  for i,snapshot in enumerate(row['snapshots']):
   validate_snapshot(snapshot,row['expected']);require(snapshot['index']==i,'two distinct snapshot invocations required')
  first,second=row['snapshots']
  require(first['parent_finished']<=second['parent_started']and first['ipc_request_serial']<second['ipc_request_serial'],'snapshot reply order differs')
  require(set(row.get('children',{}))==set(ROLES),'all four own children must close')
  for role,child in row['children'].items():
   require(child.get('closed')is True and child.get('reaped')is True and child.get('forced')is False and child.get('errors')==[],'normal own child cleanup missing')
   require(type(child.get('exit_code'))is int and child['exit_code']in((0,-15)if role=='display'else(0,)),'normal role exit missing')
  require(row.get('display_absent')is True and row.get('native_closed')is True,'native/window/array/display close missing')
  require(row.get('inputs_emitted')==0 and type(row.get('inputs_emitted'))is int and row.get('tse_started')is False and row.get('xrecord_started')is False,'metadata-only program required')
 except(ValueError,KeyError,TypeError)as error:errors.append(str(error))
 return dict(status='FAIL_METHOD_XRES_PID_EVIDENCE'if errors else'PASS_METHOD_XRES_LOCAL_PID_METADATA_ONLY',verdict_errors=errors,qualified=False,historical_u_attributed=False,continuous_client_lifetime_proven=False,a1_pass=False,retail_qualified=False)
