"""Pure own167 Cold/Warm wire audit; no Xlib, processes or TSE imports."""
import json
import math
import struct
from xrecord_core_method import CoreTrace, RecordRange, integer

COLD=['QueryExtension:XInputExtension','QueryExtension:XTEST','QueryExtension:Generic Event Extension','GEQueryVersion','XTEST:RelativeMotion']


def method_ranges(xtest_opcode,ge_opcode):
 for value in(xtest_opcode,ge_opcode):
  if type(value)is not int or not 128<=value<=255:raise ValueError('dynamic metadata opcode required')
 if xtest_opcode==ge_opcode:raise ValueError('distinct extension opcodes required')
 rows=[RecordRange()for _ in range(6)]
 rows[0].core_requests.first=rows[0].core_requests.last=38;rows[0].core_replies.first=rows[0].core_replies.last=38
 rows[1].core_requests.first=rows[1].core_requests.last=41
 rows[2].ext_requests.ext_major.first=rows[2].ext_requests.ext_major.last=xtest_opcode;rows[2].ext_requests.ext_minor.first=rows[2].ext_requests.ext_minor.last=2
 rows[3].device_events.first=rows[3].device_events.last=6;rows[3].delivered_events.first=rows[3].delivered_events.last=6
 rows[4].core_requests.first=rows[4].core_requests.last=98;rows[4].core_replies.first=rows[4].core_replies.last=98
 for name in('ext_requests','ext_replies'):
  value=getattr(rows[5],name);value.ext_major.first=value.ext_major.last=ge_opcode;value.ext_minor.first=value.ext_minor.last=0
 return rows


class MethodTrace(CoreTrace):
 def __init__(self,*,xtest_opcode,ge_opcode):
  method_ranges(xtest_opcode,ge_opcode);super().__init__(xtest_opcode=xtest_opcode);self.ge_opcode=ge_opcode;self.metadata_pending={}
 def accept(self,*,category,client_base,client_sequence,server_time,client_swapped,wire):
  for value,maximum in((category,5),(client_base,0xffffffff),(client_sequence,0xffffffff),(server_time,0xffffffff)):integer(value,maximum)
  if type(client_swapped)is not bool or not isinstance(wire,bytes)or len(wire)>16384:raise ValueError('metadata wire bounds/types')
  endian='>'if client_swapped else'<';kind=None;key=None
  if category==1 and len(wire)>=4:
   if wire[0]==98:kind='query_extension_request'
   elif wire[0]==self.ge_opcode and wire[1]==0:kind='ge_version_request'
  elif category==0 and len(wire)>=4 and wire[0]==1:
   key=(client_base,struct.unpack_from(endian+'H',wire,2)[0])
   if key in self.metadata_pending:kind='metadata_reply'
  if kind is None:return super().accept(category=category,client_base=client_base,client_sequence=client_sequence,server_time=server_time,client_swapped=client_swapped,wire=wire)
  row=dict(category=category,client_base=client_base,client_sequence=client_sequence,server_time=server_time,client_swapped=client_swapped,wire_hex=wire.hex())
  if category==1:
   if struct.unpack_from(endian+'H',wire,2)[0]*4!=len(wire):raise ValueError('metadata request declared size')
   key=(client_base,client_sequence&0xffff)
   if key in self.metadata_pending or key in self.pending:raise ValueError('ambiguous metadata sequence')
   if kind=='query_extension_request':
    if len(wire)<8:raise ValueError('short QueryExtension')
    n=struct.unpack_from(endian+'H',wire,4)[0]
    if not 1<=n<=255 or len(wire)!=8+(n+3)//4*4:raise ValueError('QueryExtension name size')
    try:name=wire[8:8+n].decode('ascii')
    except UnicodeDecodeError as error:raise ValueError('QueryExtension name encoding')from error
    row.update(kind=kind,extension_name=name);self.metadata_pending[key]=(kind,client_sequence,name)
   else:
    if len(wire)!=8:raise ValueError('GEQueryVersion request size')
    major,minor=struct.unpack_from(endian+'HH',wire,4);row.update(kind=kind,major_version=major,minor_version=minor);self.metadata_pending[key]=(kind,client_sequence,None)
   return row
  if len(wire)!=32 or struct.unpack_from(endian+'I',wire,4)[0]!=0:raise ValueError('metadata reply size')
  request,sequence,name=self.metadata_pending.pop(key)
  if request=='query_extension_request':
   if wire[8]not in(0,1):raise ValueError('QueryExtension present Bool')
   row.update(kind='query_extension_reply',extension_name=name,present=bool(wire[8]),major_opcode=wire[9],first_event=wire[10],first_error=wire[11],request_sequence=sequence)
  else:
   if wire[1]!=0:raise ValueError('GEQueryVersion reply minor')
   major,minor=struct.unpack_from(endian+'HH',wire,8);row.update(kind='ge_version_reply',major_version=major,minor_version=minor,request_sequence=sequence)
  return row


def bind_trace(rows,driver):
 if not isinstance(rows,list)or not 2<=len(rows)<=1024:raise ValueError('bounded raw records required')
 queries=driver.get('queries')
 if not isinstance(queries,list)or len(queries)!=2:raise ValueError('two fixed actual driver calls required')
 # Determine declared dynamic opcodes from exact raw discovery replies, then
 # replay every row and compare all derived fields to the archived decoder.
 majors={}
 for name in('XTEST','Generic Event Extension'):
  found=[r for r in rows if r.get('kind')=='query_extension_reply'and r.get('extension_name')==name]
  values={r.get('major_opcode')for r in found}
  if len(values)!=1:raise ValueError('dynamic discovery absent/ambiguous')
  majors[name]=next(iter(values))
 trace=MethodTrace(xtest_opcode=majors['XTEST'],ge_opcode=majors['Generic Event Extension']);last=-1.
 canonical=lambda value:json.dumps(value,sort_keys=True,allow_nan=False,separators=(',',':'))
 for i,row in enumerate(rows):
  now=row.get('received_monotonic')
  if type(row.get('callback_serial'))is not int or row['callback_serial']!=i+1 or type(now)not in(int,float)or not math.isfinite(now)or now<last:raise ValueError('raw callback clock/order')
  last=now
  try:wire=bytes.fromhex(row['wire_hex'])
  except(ValueError,TypeError)as error:raise ValueError('raw wire encoding')from error
  decoded=trace.accept(**{k:row[k]for k in('category','client_base','client_sequence','server_time','client_swapped')},wire=wire)
  if canonical(decoded)!=canonical({k:v for k,v in row.items()if k not in('callback_serial','received_monotonic')}):raise ValueError('archived derived fields differ from raw wire')
 if trace.pending or trace.metadata_pending or trace.unsupported:raise ValueError('unanswered/unsupported selected record')
 if rows[0]['kind']!='start'or rows[-1]['kind']!='end'or sum(r['kind']=='start'for r in rows)!=1 or sum(r['kind']=='end'for r in rows)!=1:raise ValueError('single actual Start/End required')
 def field(row,fmt,offset):return struct.unpack_from(('>'if row['client_swapped']else'<')+fmt,bytes.fromhex(row['wire_hex']),offset)
 bases=[];query_pairs=[]
 for query,position in zip(queries,([412,300],[424,300])):
  if query.get('window')!=driver['window']or query.get('root')!=driver['root']or query.get('position')!=position:raise ValueError('actual driver pointer/window differs')
  candidates=[r for r in rows if r['kind']=='query_pointer_request'and r['client_sequence']==query['sequence']and field(r,'I',4)==(driver['window'],)]
  if len(candidates)!=1:raise ValueError('actual query client binding absent/ambiguous')
  base=candidates[0]['client_base'];bases.append(base)
  replies=[r for r in rows if r['kind']=='query_pointer_reply'and r['client_base']==base and r['request_sequence']==query['sequence']]
  if len(replies)!=1 or replies[0]['same_screen']is not True or field(replies[0],'I',8)!=(driver['root'],)or field(replies[0],'hh',16)!=tuple(position):raise ValueError('actual query reply differs')
  query_pairs.append((candidates[0],replies[0]))
 if bases[0]<=3 or len(set(bases))!=1:raise ValueError('same real driver connection required')
 source=[r for r in rows if r['client_base']==bases[0]];attempts=[];request_groups=[];prior=-1.;handle=None
 if sum(r['kind']=='query_pointer_request'for r in source)!=2:raise ValueError('extra driver query after capture')
 for i,query in enumerate(queries):
  a=query['attempt'];before,after=a['sequence_interval'];args=a['arguments'];start,end=a['started_monotonic'],a['finished_monotonic']
  if any(type(v)is not int for v in(before,after))or not 0<before<after<=0xffffffff or after-before!=(5 if i==0 else 1):raise ValueError('cold5/warm1 actual counter differs')
  if a.get('native_invoked')is not True or any(type(a.get(k))is not int for k in('sequence_before','sequence_after'))or(a['sequence_before'],a['sequence_after'])!=(before,after):raise ValueError('actual native invocation/counter copies differ')
  if type(query.get('sequence'))is not int or not after<=query['sequence']<=0xffffffff:raise ValueError('actual query counter precedes native completion')
  if a['function']!='XTestFakeRelativeMotionEvent'or len(args)!=4 or any(type(v)is not int for v in args)or args[0]<=0 or args[1:]!=[12,0,0]or type(a['return_value'])is not int or a['return_value']!=1:raise ValueError('actual fixed native call differs')
  if any(type(v)not in(int,float)or not math.isfinite(v)for v in(start,end))or not prior<=start<=end or end-start>2:raise ValueError('actual native call clock/deadline differs')
  if handle is not None and args[0]!=handle:raise ValueError('driver native connection changed')
  handle=args[0];prior=end;attempts.append([before,after])
  requests=[r for r in source if r['category']==1 and before<=r['client_sequence']<after]
  if [r['client_sequence']for r in requests]!=list(range(before,after)):raise ValueError('whole native interval wire coverage differs')
  request_groups.append(requests)
  labels=['QueryExtension:'+r['extension_name']if r['kind']=='query_extension_request'else'GEQueryVersion'if r['kind']=='ge_version_request'else'XTEST:RelativeMotion'if r['kind']=='xtest_relative_motion'else r['kind']for r in requests]
  if labels!=(COLD if i==0 else['XTEST:RelativeMotion']):raise ValueError('actual cold/warm requests differ')
  for r in requests:
   if r['kind']=='xtest_relative_motion':
    if(r['dx'],r['dy'],r['requested_device'])!=(12,0,0)or field(r,'II',8)!=(0,0):raise ValueError('fixed actual FakeInput differs')
   else:
    reply_kind='query_extension_reply'if r['kind']=='query_extension_request'else'ge_version_reply'
    replies=[v for v in source if v['kind']==reply_kind and v['request_sequence']==r['client_sequence']]
    if len(replies)!=1 or not r['callback_serial']<replies[0]['callback_serial']<requests[requests.index(r)+1]['callback_serial']:raise ValueError('synchronous metadata reply order differs')
    v=replies[0]
    if r['kind']=='query_extension_request':
     if v['present']is not True or not 128<=v['major_opcode']<=255:raise ValueError('metadata extension unavailable')
     expected=majors.get(r['extension_name'])
     if expected is not None and v['major_opcode']!=expected:raise ValueError('actual dynamic opcode differs')
    elif(r['major_version'],r['minor_version'],v['major_version'],v['minor_version'])!=(1,0,1,0):raise ValueError('actual GE version differs')
 for i,(request,reply)in enumerate(query_pairs):
  upper=request_groups[i+1][0]['callback_serial']if i+1<len(request_groups)else rows[-1]['callback_serial']
  if not request_groups[i][-1]['callback_serial']<request['callback_serial']<reply['callback_serial']<upper:raise ValueError('actual query callback order differs from native sections')
  if i+1<len(attempts)and not queries[i]['sequence']<attempts[i+1][0]:raise ValueError('actual query counter reaches next native section')
 selected=[r for r in source if r['kind']in('query_extension_request','ge_version_request','xtest_relative_motion')]
 if len(selected)!=6:raise ValueError('extra actual native/library request')
 if any(r['kind']=='warp_request'for r in source):raise ValueError('unexpected driver warp after capture')
 device=[r for r in rows if r['kind']=='device_motion'];delivered=[r for r in rows if r['kind']=='delivered_motion']
 if [[r['root_x'],r['root_y']]for r in device]!=[[412,300],[424,300]]or not delivered or{(r['root_x'],r['root_y'])for r in delivered}!={(412,300),(424,300)}:raise ValueError('actual motion evidence differs')
 for r in device+delivered:
  if field(r,'I',8)!=(driver['root'],)or(r['kind']=='delivered_motion'and field(r,'I',12)!=(driver['window'],)):raise ValueError('actual motion root/window differs')
 return dict(request_client_bound=True,client_binding_basis='own_window_and_actual_query_sequences',cold_requests=COLD,cold_sequence_interval=attempts[0],warm_sequence_interval=attempts[1],query_positions=[[412,300],[424,300]],device_motion_positions=[[412,300],[424,300]],delivered_motion_positions=[[r['root_x'],r['root_y']]for r in delivered],ge_version=[1,0],xi2_complete=False,retail_qualified=False,a1_pass=False)


def method_verdict(row):
 required=('start_of_data','end_of_data','request_client_bound','recorder_closed','driver_closed','display_closed','children_reaped','record_context_freed','record_data_freed','connections_closed')
 good=not row.get('errors')and all(row.get(k)is True for k in required)
 good=good and row.get('record_version')==[1,13]and row.get('xtest_version')==[2,2]and row.get('ge_version')==[1,0]
 good=good and all(type(row.get(k))is int and row[k]==0 for k in('unknown_records','malformed','dropped'))
 good=good and all(row.get(k)is False for k in('overflow','recorder_expired','tse_started'))and row.get('resources',{}).get('measured')is True
 good=good and row.get('cold_requests')==COLD and row.get('query_positions')==[[412,300],[424,300]]
 return dict(status='PASS_METHOD_COLD_WARM_LIBRARY_REQUESTS_ONLY'if good else'FAIL_METHOD_COLD_WARM_EVIDENCE',retail_qualified=False,xi2_complete=False,a1_pass=False)
