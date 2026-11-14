"""Private diagnostic audit; request provenance is not a gain/damage proof."""
import hashlib
import json
import math
from pathlib import Path
import struct


def xtest(row,opcode):
 raw=bytes.fromhex(row['wire_hex']);endian='>'if row['client_swapped']else'<'
 if len(raw)!=36 or raw[0]!=opcode or raw[1]!=2 or struct.unpack_from(endian+'H',raw,2)[0]!=9:return None
 if row['kind']=='xtest_relative_motion':return dict(type=raw[4],detail=raw[5],motion=list(struct.unpack_from(endian+'hh',raw,24)),device=raw[35])
 if row['kind']=='unsupported'and raw[0]>=128 and raw[4]in(2,3,4,5):return dict(type=raw[4],detail=raw[5],device=raw[35])
 return None


def bind_emissions(rows,emissions,bases,*,xtest_opcode):
 if type(xtest_opcode)is not int or not 128<=xtest_opcode<=255:raise ValueError('dynamic XTEST opcode required')
 if set(bases)!={'controller_transport','original_window_owner'}or len(set(bases.values()))!=2 or any(type(v)is not int or v<=3 for v in bases.values()):raise ValueError('actual resource owner bindings missing')
 if not isinstance(emissions,list)or not 1<=len(emissions)<=96:raise ValueError('bounded actual emission program absent')
 controller=bases['controller_transport'];owner=bases['original_window_owner'];used=set();source=[(i,row,xtest(row,xtest_opcode))for i,row in enumerate(rows)if row['client_base']==controller and xtest(row,xtest_opcode)is not None]
 for index,event in enumerate(emissions):
  if event.get('index')!=index or event.get('error')or not event.get('return_value'):raise ValueError('failed/reversed native emission cannot prove actual input')
  interval=event['sequence_interval'];a,b=interval
  if type(a)is not int or type(b)is not int or not 0<a<b<=0xffffffff or b-a>4:raise ValueError('actual request sequence interval invalid')
  args=event['arguments'];name=event['function']
  if name=='XTestFakeRelativeMotionEvent':
   if len(args)!=4 or args[3]!=0 or any(type(v)is not int for v in args)or(args[1]==0)==(args[2]==0)or not 1<=max(abs(args[1]),abs(args[2]))<=12:raise ValueError('fixed normal mouse arguments differ')
   wanted=dict(type=6,detail=1,motion=args[1:3],device=0)
  elif name=='XTestFakeKeyEvent':
   if len(args)!=4 or any(type(v)is not int for v in args)or not 8<=args[1]<=255 or args[2]not in(0,1)or args[3]!=0:raise ValueError('fixed normal key arguments differ')
   wanted=dict(type=2 if args[2]else 3,detail=args[1],device=0)
  else:raise ValueError('no new controller input kind allowed')
  matches=[i for i,row,decoded in source if a<=row['client_sequence']<b and decoded==wanted]
  if len(matches)!=1 or matches[0]in used:raise ValueError('exact controller XTEST binding missing/ambiguous')
  used.add(matches[0])
 if len(used)!=len(source):raise ValueError('unexplained controller XTEST record')
 unsupported=[row for row in rows if row['kind']=='unsupported'];typed=[row for row in unsupported if xtest(row,xtest_opcode)is not None]
 return dict(status='BOUND_PARTIAL_PASSIVE_TRACE_ONLY',bound_emissions=len(used),controller_query_records=sum(row['client_base']==controller and row['kind']in('query_pointer_request','query_pointer_reply')for row in rows),window_owner_query_records=sum(row['client_base']==owner and row['kind']in('query_pointer_request','query_pointer_reply')for row in rows),unattributed_query_records=sum(row['client_base']not in(controller,owner)and row['kind']in('query_pointer_request','query_pointer_reply')for row in rows),window_owner_warp_records=sum(row['client_base']==owner and row['kind']=='warp_request'for row in rows),unattributed_warp_records=sum(row['client_base']not in(controller,owner)and row['kind']=='warp_request'for row in rows),device_motion_records=sum(row['kind']=='device_motion'for row in rows),delivered_motion_records=sum(row['kind']=='delivered_motion'for row in rows),method_decoder_unsupported=len(unsupported),adapter_typed_noncursor_xtest=len(typed),unparsed_selected_records=len(unsupported)-len(typed),unattributed_xtest_records=sum(xtest(row,xtest_opcode)is not None and row['client_base']!=controller for row in rows),pid_equals_clientbase=False,device_originating_client=None,xi2_complete=False,retail_qualified=False,a1_pass=False,gain_fixed=False,clock_scope='receipt_monotonic_is_not_server_time_or_JS_time')


def bind_phases(emissions,phases,forward_key):
 """Existing parent-monotonic action frames, never X-server/JS clock guesses."""
 if not isinstance(phases,list)or not 1<=len(phases)<=48:raise ValueError('existing bounded A1 phases missing')
 offset=0
 def finite(*values):return all(type(v)in(int,float)and math.isfinite(v)for v in values)
 for index,phase in enumerate(phases):
  if phase.get('index')!=index or set(phase.get('actions',{}))!={'vanilla'}or len(phase.get('emissions',[]))!=1:raise ValueError('existing A1 phase shape differs')
  old=phase['emissions'][0];control=phase['actions']['vanilla']
  if old.get('role')!='vanilla'or old.get('control')!=control or old.get('request_confirmed')is not True:raise ValueError('existing actual A1 emission absent')
  if offset>=len(emissions):raise ValueError('actual controller emission missing')
  event=emissions[offset];offset+=1;a,b=event['started_monotonic'],event['finished_monotonic'];c,d=old.get('started'),old.get('finished')
  if not finite(a,b,c,d)or not c<=a<=b<=d:raise ValueError('actual source call outside existing emission')
  args=event['arguments']
  if control=='forward':
   if event['function']!='XTestFakeKeyEvent'or args[1:]!=[forward_key,1,0]or offset>=len(emissions):raise ValueError('existing forward press differs')
   up=emissions[offset];offset+=1;x,y=up['started_monotonic'],up['finished_monotonic'];r,z=phase.get('release_started'),phase.get('finished')
   if up['function']!='XTestFakeKeyEvent'or up['arguments']!=[args[0],forward_key,0,0]or not finite(x,y,r,z)or not r<=x<=y<=z:raise ValueError('existing forward release differs')
  elif control in('look_right','look_left','look_horizontal','look_vertical'):
   pixels=old.get('pixels');delta=[0,pixels]if control=='look_vertical'else[pixels,0]
   if type(pixels)is not int or not 1<=abs(pixels)<=12 or event['function']!='XTestFakeRelativeMotionEvent'or args[1:]!=delta+[0]:raise ValueError('existing normal mouse pixels differ')
  else:raise ValueError('no new A1 control admitted')
 if offset!=len(emissions):raise ValueError('unexplained controller native call outside A1 phases')
 return len(phases)


def audit_trace(directory,emissions,arm,native,phases):
 path=Path(directory)/'record-raw.jsonl'
 if path.is_symlink()or path.stat().st_size>2097152:raise ValueError('passive raw byte/path bound')
 raw=path.read_bytes();lines=raw.splitlines()
 if not raw.endswith(b'\n')or not 2<=len(lines)<=1024:raise ValueError('passive raw count/boundary')
 rows=[json.loads(line)for line in lines];last=-1.
 for i,row in enumerate(rows):
  now=row.get('received_monotonic')
  if row.get('callback_serial')!=i+1 or type(now)not in(int,float)or not math.isfinite(now)or now<last:raise ValueError('passive raw clock/serial invalid')
  last=now
 if rows[0]['kind']!='start'or rows[-1]['kind']!='end'or sum(r['kind']=='start'for r in rows)!=1 or sum(r['kind']=='end'for r in rows)!=1:raise ValueError('passive Start/End boundary not proved')
 if not isinstance(native,dict)or native.get('errors')or native.get('cleanup_errors')or native.get('records')!=len(rows)or native.get('calls')!=native.get('freed')or native.get('calls')!=len(rows):raise ValueError('passive callback coverage/cleanup differs')
 if native.get('bytes')!=len(raw)or native.get('start_count')!=1 or native.get('end_count')!=1:raise ValueError('passive serialized byte/boundary counters differ')
 if any(native.get(k)!=0 for k in('malformed','dropped'))or native.get('budget_failed')is not False or any(native.get(k)is not True for k in('context_freed','connections_closed','end_verified')):raise ValueError('passive native failure counters/cleanup')
 if native.get('unknown_records')!=sum(r['kind']=='unsupported'for r in rows):raise ValueError('unsupported raw accounting differs')
 bound_phases=bind_phases(emissions,phases,arm['forward_keycode'])
 result=bind_emissions(rows,emissions,arm['bindings'],xtest_opcode=arm['xtest_opcode']);result['bound_existing_a1_phases']=bound_phases;result.update(raw_sha256=hashlib.sha256(raw).hexdigest(),raw_records=len(rows),raw_bytes=len(raw))
 return result
