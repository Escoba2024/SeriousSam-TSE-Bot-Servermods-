"""Disabled own-display Core method parent; never imports or calls X libraries."""
import json
import math
import struct
import fcntl
import hashlib
import os
import resource
import signal
import shutil
import stat
import sys
import time
from pathlib import Path

from xrecord_core_process import identity_matches, OwnChild

RUNTIME_REVIEWED=False
DISPLAY=':167'


def validate_display(display):
 if display!=DISPLAY:raise ValueError('only own display167')
 return display


def cleanup_owned(recorder,driver,display,errors):
 for role,close in(('recorder',recorder),('driver',driver),('display',display)):
  try:close()
  except BaseException as error:errors.append(role+':'+repr(error))


def method_verdict(row):
 required=('start_of_data','end_of_data','request_client_bound','recorder_closed','driver_closed','display_closed','children_reaped','record_context_freed','record_data_freed','connections_closed')
 good=not row.get('errors')and all(row.get(k)is True for k in required)
 good=good and row.get('record_version')==[1,13]and row.get('xtest_version')==[2,2]
 good=good and all(row.get(k)==0 for k in('unknown_records','malformed','dropped'))
 good=good and all(row.get(k)is False for k in('overflow','recorder_expired','tse_started'))and row.get('resources',{}).get('measured')is True
 good=good and row.get('xtest_relative_requests')==[dict(dx=12,dy=0)]and row.get('warp_requests')==[dict(dst_x=400,dst_y=300)]and row.get('query_positions')==[[412,300],[400,300]]
 good=good and row.get('device_motion_positions')==[[412,300],[400,300]]and {tuple(x)for x in row.get('delivered_motion_positions',[])}=={(412,300),(400,300)}
 return dict(status='PASS_METHOD_PARTIAL_CORE_REQUESTS_ONLY'if good else'FAIL_METHOD_CORE_EVIDENCE',retail_qualified=False,xi2_complete=False,a1_pass=False,device_motion_count=len(row.get('device_motion_positions',[])),delivered_motion_count=len(row.get('delivered_motion_positions',[])))


def bind_trace(rows,driver):
 """Bind client records to the owned window and exact public query sequence.

 Device events remain unattributed to a client. Delivered copies are separate.
 """
 if not isinstance(rows,list)or len(rows)>1024:raise ValueError('bounded raw records')
 prior=0.;serial=0
 for row in rows:
  serial+=1;now=row.get('received_monotonic')
  if row.get('callback_serial')!=serial or type(now)not in(int,float)or not math.isfinite(now)or now<prior:raise ValueError('record order/clock')
  prior=now
 def kind(name):return[r for r in rows if r['kind']==name]
 relative=kind('xtest_relative_motion');warp=kind('warp_request');queries=kind('query_pointer_request');replies=kind('query_pointer_reply');device=kind('device_motion');delivered=kind('delivered_motion')
 if len(relative)!=1 or len(warp)!=1 or len(queries)!=2 or len(replies)!=2 or len(device)!=2 or not delivered:raise ValueError('method evidence counts')
 bases={r['client_base']for r in relative+warp+queries+replies+delivered}
 if len(bases)!=1 or next(iter(bases))<=3:raise ValueError('own client basis differs')
 def field(row,fmt,offset):
  try:return struct.unpack_from(('>'if row['client_swapped']else'<')+fmt,bytes.fromhex(row['wire_hex']),offset)
  except (ValueError,struct.error)as error:raise ValueError('wire binding')from error
 if relative[0].get('dx')!=12 or relative[0].get('dy')!=0 or field(relative[0],'hh',24)!=(12,0):raise ValueError('relative request differs')
 if warp[0].get('dst_x')!=400 or warp[0].get('dst_y')!=300 or field(warp[0],'hh',20)!=(400,300)or field(warp[0],'II',4)!=(0,driver['root']):raise ValueError('warp binding differs')
 if not(relative[0]['callback_serial']<queries[0]['callback_serial']<replies[0]['callback_serial']<warp[0]['callback_serial']<queries[1]['callback_serial']<replies[1]['callback_serial']):raise ValueError('request/reply method order')
 positions=[]
 if len(driver.get('queries',[]))!=2:raise ValueError('driver query receipts missing')
 for index,(request,reply,own,pos)in enumerate(zip(queries,replies,driver['queries'],([412,300],[400,300]))):
  if field(request,'I',4)!=(driver['window'],)or own['window']!=driver['window']or own['root']!=driver['root']or own['position']!=pos:raise ValueError('own query window/position differs')
  if request['client_sequence']!=own['sequence']or reply.get('request_sequence')!=own['sequence']or field(reply,'H',2)!=(own['sequence']&65535,):raise ValueError('own query sequence differs')
  if reply.get('same_screen')is not True or field(reply,'I',8)!=(driver['root'],)or field(reply,'hh',16)!=tuple(pos)or[reply.get('root_x'),reply.get('root_y')]!=pos:raise ValueError('actual query reply differs')
  positions.append(pos)
 for row in delivered:
  if field(row,'I',12)!=(driver['window'],)or field(row,'I',8)!=(driver['root'],):raise ValueError('delivered own window/root differs')
 for row in device:
  if row['client_base']!=0 or struct.unpack_from('<I',bytes.fromhex(row['wire_hex']),8)!=(driver['root'],):raise ValueError('device root differs')
 return dict(request_client_bound=True,client_binding_basis='own_window_plus_recorded_query_request_reply_sequences',device_motion_originating_client=None,xtest_relative_requests=[dict(dx=12,dy=0)],warp_requests=[dict(dst_x=400,dst_y=300)],query_positions=positions,device_motion_positions=[[r['root_x'],r['root_y']]for r in device],delivered_motion_positions=[[r['root_x'],r['root_y']]for r in delivered])


XSOCKET=Path('/tmp/.X11-unix/X167')
XLOCK=Path('/tmp/.X167-lock')
XVFB='/usr/bin/Xvfb'
XVFB_SHA256='6b27845931670c8c9b3ce7423696a452ce3cab1c7f316ce5f7ea7f1297fa2f84'


def display_absent():return not XSOCKET.exists()and not XSOCKET.is_symlink()and not XLOCK.exists()and not XLOCK.is_symlink()


def fresh_display_available():
 if not display_absent():raise ValueError('display167 occupied; no existing display may be used')
 if hashlib.sha256(Path(XVFB).read_bytes()).hexdigest()!=XVFB_SHA256:raise ValueError('Xvfb pin changed')


def check_disk(directory):
 free=shutil.disk_usage(directory).free
 if free<8*1024**3:raise ValueError('less than8GiB disk')
 return free


def listening_inode(text):
 # /proc/net/unix: accept() sockets may repeat the listener pathname. Bind the
 # exact listening stream socket (SO_ACCEPTCON), not any connected copy.
 matches=[]
 for line in text.splitlines()[1:]:
  row=line.split()
  if len(row)==8 and row[7]==str(XSOCKET)and row[3:6]==['00010000','0001','01']:matches.append(row[6])
 if len(matches)!=1 or not matches[0].isdigit():raise ValueError('own listening socket absent/ambiguous')
 return matches[0]


def guard_display(child):
 child.guard()
 if XLOCK.is_symlink()or XSOCKET.is_symlink()or not stat.S_ISSOCK(XSOCKET.stat().st_mode)or int(XLOCK.read_text().strip())!=child.identity['pid']:raise ValueError('own Xvfb lock/socket binding')
 inode=listening_inode(Path('/proc/net/unix').read_text())
 links=[];paths=list((Path('/proc')/str(child.identity['pid'])/'fd').iterdir())
 if len(paths)>128:raise ValueError('own display FD count')
 for p in paths:
  try:links.append(os.readlink(p))
  except FileNotFoundError:pass
 if 'socket:['+inode+']'not in links:raise ValueError('own display socket FD missing')
 child.guard()


def wait_display(child,deadline):
 end=min(deadline,time.monotonic()+5.)
 while True:
  child.guard()
  if XLOCK.exists()and XSOCKET.exists():guard_display(child);return
  if time.monotonic()>=end:raise TimeoutError('own display startup')
  time.sleep(.01)


def bounded_json(path,limit=16384):
 if path.is_symlink()or path.stat().st_size>limit:raise ValueError('private receipt bound/path')
 return json.loads(path.read_bytes())


def verify_package():
 directory=Path(__file__).resolve().parent;manifest=bounded_json(directory/'source-manifest.json',65536)
 if manifest.get('runtime_enabled')is not True:raise RuntimeError('disabled method manifest')
 if manifest.get('schema')!='OWN_CORE_XRECORD_METHOD_V1'or manifest.get('limits')!=dict(display=':167',recorder_seconds=15,records=1024,total_bytes=2097152,record_bytes=16384,arm_seconds=3,stop_seconds=3,driver_seconds=2,controller_seconds=30,cleanup_seconds=5):raise ValueError('method manifest scope')
 if not {'xrecord_core_controller.py','xrecord_core_process.py','xrecord_core_method.py','xrecord_core_native.py','xrecord_core_worker.py'}.issubset(manifest.get('files',{})):raise ValueError('runtime pins incomplete')
 for name,sha in manifest['files'].items():
  if Path(name).name!=name or hashlib.sha256((directory/name).read_bytes()).hexdigest()!=sha:raise ValueError('method source pin:'+name)
 return manifest


def execute(directory):
 if not RUNTIME_REVIEWED:raise RuntimeError('disabled own XRecord controller')
 directory=Path(directory).resolve();started=time.monotonic();deadline=started+30.;cpu0=resource.getrusage(resource.RUSAGE_CHILDREN);self0=resource.getrusage(resource.RUSAGE_SELF)
 errors=[];roles={};native={};identities={};driver_queries=[];versions={};initial={}
 def call(role,command,timeout,**fields):
  left=deadline-time.monotonic()
  if left<=0:raise TimeoutError('method controller30s')
  for child in roles.values():child.guard()
  guard_display(roles['display']);check_disk(directory)
  return roles[role].call(command,timeout=min(timeout,left),**fields)['value']
 def close(role):
  if role not in roles:return
  result=roles[role].cleanup(stop_timeout=(3 if role=='recorder'else 2)if role!='display'else None,normal_signal=role=='display')
  identities[role]=result
  errors.extend(role+':'+x for x in result['errors'])
  if not result['closed']or not result['reaped']or result['forced']or result['exit_code']not in(0,-15):errors.append(role+':not normal closed/reaped')
  if role!='display':
   try:
    receipt=bounded_json(directory/(role+'-native-close.json'));errors.extend(role+':'+x for x in receipt['errors']);native[role]=receipt['native']
    if native[role]is None:raise ValueError('missing native close')
    errors.extend(role+':'+x for x in native[role].get('cleanup_errors',[])+native[role].get('errors',[]))
   except BaseException as error:errors.append(role+':native receipt:'+repr(error))
 try:
  fresh_display_available();check_disk(directory)
  roles['display']=OwnChild([XVFB,DISPLAY,'-screen','0','800x600x24','-nolisten','tcp','-noreset'],directory,DISPLAY,ttl=30,role='display')
  wait_display(roles['display'],deadline)
  source=Path(__file__).resolve().parent
  for role in('driver','recorder'):
   roles[role]=OwnChild(['/usr/bin/python3','-E','-s','-B',str(source/'xrecord_core_worker.py'),'--role',role,'--directory',str(directory),'--display',DISPLAY],directory,DISPLAY,ttl=15 if role=='recorder'else 30,role=role)
   if role=='driver':initial=call(role,'initialize',2)
  versions=call('recorder','arm',3)
  if versions.get('start_count')!=1 or versions.get('ranges_verified')is not True or versions.get('record_version')!=[1,13]or versions.get('xtest_version')!=[2,2]:raise ValueError('record arm receipt incomplete')
  driver_queries.append(call('driver','relative',2));call('recorder','observe',2,target=1)
  driver_queries.append(call('driver','warp',2));call('recorder','observe',2,target=2)
 except BaseException as error:errors.append(type(error).__name__+':'+str(error))
 finally:cleanup_owned(lambda:close('recorder'),lambda:close('driver'),lambda:close('display'),errors)
 row=dict(errors=errors,**{k:versions[k]for k in('record_version','xtest_version')if k in versions},tse_started=False,xi2_complete=False,malformed=None,dropped=None,overflow=None,recorder_expired=None)
 try:
  path=directory/'record-raw.jsonl'
  if path.is_symlink()or path.stat().st_size>2097152:raise ValueError('raw stream bound/path')
  raw=path.read_bytes();lines=raw.splitlines()
  if not raw.endswith(b'\n')or len(lines)>1024:raise ValueError('raw stream record boundary/bound')
  rows=[json.loads(line)for line in lines];row.update(bind_trace(rows,dict(window=initial['window'],root=initial['root'],queries=driver_queries)))
  row['raw_sha256']=hashlib.sha256(raw).hexdigest();row['raw_bytes']=len(raw)
  row['start_of_data']=len([r for r in rows if r['kind']=='start'])==1
  row['end_of_data']=len([r for r in rows if r['kind']=='end'])==1
  rn=native.get('recorder',{});dn=native.get('driver',{})
  row.update(unknown_records=rn.get('unknown_records'),malformed=rn.get('malformed'),dropped=rn.get('dropped'),record_context_freed=rn.get('context_freed')is True,record_data_freed=rn.get('calls',-1)==rn.get('freed',-2),connections_closed=rn.get('connections_closed')is True and dn.get('connections_closed')is True,overflow=rn.get('budget_failed')is not False,recorder_expired=identities.get('recorder',{}).get('exit_code')==-signal.SIGALRM or any('TTL'in x for x in rn.get('errors',[])))
  if rn.get('records')!=len(rows):raise ValueError('native raw record coverage differs')
  if rn.get('start_count')!=1 or rn.get('end_count')!=1 or rn.get('end_verified')is not True or dn.get('window_destroyed')is not True:raise ValueError('native end/window cleanup not proved')
 except BaseException as error:errors.append('evidence:'+repr(error))
 row.update(recorder_closed=identities.get('recorder',{}).get('closed')is True,driver_closed=identities.get('driver',{}).get('closed')is True,display_closed=identities.get('display',{}).get('closed')is True and display_absent(),children_reaped=len(identities)==3 and all(x.get('reaped')is True for x in identities.values()),children=identities)
 cpu1=resource.getrusage(resource.RUSAGE_CHILDREN);self1=resource.getrusage(resource.RUSAGE_SELF)
 row['resources']=dict(measured=True,wall_seconds=time.monotonic()-started,parent_cpu_seconds=self1.ru_utime+self1.ru_stime-self0.ru_utime-self0.ru_stime,children_cpu_seconds=cpu1.ru_utime+cpu1.ru_stime-cpu0.ru_utime-cpu0.ru_stime,children_maxrss_kib=cpu1.ru_maxrss,disk_free_bytes=shutil.disk_usage(directory).free)
 if row['resources']['disk_free_bytes']<8*1024**3:errors.append('final resource check:less than8GiB disk')
 row.update(method_verdict(row));wire=json.dumps(row,allow_nan=False,indent=2)
 with os.fdopen(os.open(directory/'method-result.json',os.O_WRONLY|os.O_CREAT|os.O_EXCL,0o600),'w')as f:f.write(wire)
 return row


def run_method(directory):
 if not RUNTIME_REVIEWED:raise RuntimeError('disabled own XRecord method; Root reviewed freeze required')
 verify_package();directory=Path(directory).resolve();directory.mkdir(mode=0o700,exist_ok=False)
 lock=Path('/run/lock/ssam-own-xrecord-core-method167.lock')
 with os.fdopen(os.open(lock,os.O_CREAT|os.O_RDWR|os.O_NOFOLLOW,0o600),'r+')as fd:
  if os.fstat(fd.fileno()).st_uid!=os.geteuid():raise ValueError('method lock owner')
  fcntl.flock(fd,fcntl.LOCK_EX|fcntl.LOCK_NB)
  return execute(directory)


if __name__=='__main__':
 import argparse
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--directory',required=True,type=Path)
 print(json.dumps(run_method(p.parse_args().directory),indent=2))
