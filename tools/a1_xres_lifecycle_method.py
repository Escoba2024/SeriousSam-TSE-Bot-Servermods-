"""DISABLED one own167 Linux lifecycle method, no TSE/Wine/Frida/input."""
import fcntl
import hashlib
import json
import os
from pathlib import Path
import resource
import shutil
import signal
import struct
import sys
import time

CORE=Path(__file__).resolve().parent/'passive-core'
if CORE.is_dir():sys.path.insert(0,str(CORE))
from xrecord_core_process import OwnChild,start_ticks
from xres_pid_controller import fresh_display_available,wait_display,guard_display,display_absent,check_disk,bounded_json,role_identity,XSOCKET,XVFB
from xres_pid_method import require,same,uint
from a1_xres_attribution import audit_attribution,fingerprints
from a1_passive_xrecord import private_json
from xres_pid_worker import Native as QualifiedNative,Resources,D,U,I,P
from xrecord_core_native import Native as CoreNative

RUNTIME_REVIEWED=False
LIMITS=dict(display=':167',controller_seconds=30,recorder_seconds=15,operation_seconds=2,arm_seconds=3,stop_seconds=3,cleanup_seconds=5,snapshots=2,context_targets_max=32,queries_per_snapshot_max=34,clients_max=64,records_max=1024,bytes_max=2097152,record_bytes_max=16384,ipc_bytes=16384,metadata_bytes=262144)


def self_identity():return dict(pid=os.getpid(),start_ticks=start_ticks(os.getpid()))


def display_owner(child):
 guard_display(child);st=XSOCKET.stat();return dict(identity=[child.identity['pid'],child.identity['start_ticks']],argv=child.identity['argv'],socket_pin=[st.st_dev,st.st_ino,st.st_uid])


def verify_package():
 source=Path(__file__).resolve().parent;m=bounded_json(source/'source-manifest.json',131072)
 require(m.get('schema')=='OWN_XRES_RECORD_LIFECYCLE_METHOD_V1'and m.get('runtime_reviewed')is True and m.get('runtime_enabled')is True and same(m.get('limits'),LIMITS),'disabled/fixed lifecycle method manifest')
 for path,h in m['runtime_dependencies'].items():require(hashlib.sha256(Path(path).read_bytes()).hexdigest()==h,'method source/runtime pin')
 for section in('library_sha256','header_sha256','evidence_sha256'):
  for path,h in m[section].items():require(hashlib.sha256(Path(path).read_bytes()).hexdigest()==h,'method external pin')
 return m


def validate_method(directory,native,peer,driver,children,query):
 result=audit_attribution(directory,native);metadata=bounded_json(directory/'xres-attribution.json',262144);rows=[json.loads(line)for line in(directory/'record-raw.jsonl').read_bytes().splitlines()]
 require(same(peer['before'],peer['after']),'actual peer process changed across second snapshot')
 require(peer['before']['pid_namespace']==metadata['expected']['pid_namespace'],'peer PID namespace differs')
 snapshot=metadata['snapshots'][1];xid=peer['resource'];uint(xid);matches=[c for c in snapshot['clients']if xid&(~c['resource_mask']&0xffffffff)==c['resource_base']]
 require(len(matches)==1 and matches[0]['resource_base']>3,'known own peer resource range absent/ambiguous');base=matches[0]['resource_base']
 q=[q for q in snapshot['queries']if q['requested_kind']=='base'and q['requested_xid']==base]
 require(len(q)==1 and q[0]['ids'][0]['pid']==peer['before']['pid'],'actual peer resource/base/PID not matched')
 require(sum(r['kind']=='client_started'and r['client_base']==base for r in rows)==1 and sum(r['kind']=='client_died'and r['client_base']==base for r in rows)==1,'known own peer start/died not observed exactly once')
 require(base not in result['original_bases']and base in result['lifecycle_changed_bases'],'peer must remain interval UNKNOWN')
 require(set(result['original_bases'])==set(metadata['snapshots'][0]['bindings'].values()),'stable two driver connections lost')
 require(set(children)=={'display','driver','peer','recorder'},'all four own method roles required')
 require(driver['pid']==metadata['expected']['identities']['vanilla']['pid']and driver['start_ticks']==metadata['expected']['identities']['vanilla']['start_ticks'],'actual driver identity differs from metadata')
 require(result['own_original_request_rows']>0,'actual stable driver requests required')
 require(isinstance(query,dict)and type(query.get('sequence'))is int and query['sequence']>0 and query.get('window')==metadata['expected']['resources']['controller_transport'],'actual own driver query metadata absent')
 driver_base=metadata['snapshots'][0]['bindings']['controller_transport'];sequence=query['sequence']
 requests=[r for r in rows if r['kind']=='query_pointer_request'and r['client_base']==driver_base and r['client_sequence']==sequence]
 replies=[r for r in rows if r['kind']=='query_pointer_reply'and r['client_base']==driver_base and struct.unpack_from('<H'if not r['client_swapped']else'>H',bytes.fromhex(r['wire_hex']),2)[0]==sequence&0xffff]
 require(len(requests)==len(replies)==1 and requests[0]['callback_serial']<replies[0]['callback_serial'],'actual own driver query request/reply not unique')
 request=requests[0];reply=replies[0];endian='>'if request['client_swapped']else'<'
 require(struct.unpack_from(endian+'I',bytes.fromhex(request['wire_hex']),4)[0]==query['window'],'actual driver request window mismatch')
 wire=bytes.fromhex(reply['wire_hex']);endian='>'if reply['client_swapped']else'<'
 require(bool(wire[1])and list(struct.unpack_from(endian+'hh',wire,16))==query.get('position')and struct.unpack_from(endian+'I',wire,8)[0]==query.get('root'),'actual driver reply differs from native query')
 return dict(attribution=result,lifecycle_started=True,lifecycle_died=True,exactly_two_snapshots=True,peer_base=base,peer_interval_unknown=True,driver_requests_bound=True,driver_query=query)


def execute(directory,child_factory=OwnChild):
 if not RUNTIME_REVIEWED:raise RuntimeError('disabled lifecycle method')
 directory=Path(directory).resolve();started=time.monotonic();deadline=started+30.;cpu0=resource.getrusage(resource.RUSAGE_CHILDREN);self0=resource.getrusage(resource.RUSAGE_SELF)
 roles={};children={};native={};errors=[];peer={};driver={};facts={};query={}
 def call(role,command,timeout):
  for child in roles.values():child.guard()
  guard_display(roles['display']);check_disk(directory);left=deadline-time.monotonic();require(left>0,'method controller30s deadline')
  reply=roles[role].call(command,timeout=min(left,timeout));require(time.monotonic()<=deadline,'method controller30s deadline')
  require(type(reply.get('id'))is int and reply['id']>0 and reply.get('ok')is True,'authentic method IPC reply')
  return reply['value']
 def close(role):
  if role not in roles or role in children:return
  try:
   receipt=roles[role].cleanup(stop_timeout=(3 if role=='recorder'else 2)if role!='display'else None,normal_signal=role=='display');children[role]=receipt
   require(receipt.get('closed')is True and receipt.get('reaped')is True and receipt.get('forced')is False and receipt.get('errors')==[]and type(receipt.get('exit_code'))is int and receipt['exit_code']in((0,-15)if role=='display'else(0,)),'role not normal closed/reaped')
   if role!='display':
    packet=bounded_json(directory/(role+'-native-close.json'));require(packet.get('errors')==[],'native role error')
    if role=='recorder':native[role]=packet;require(packet.get('cleanup_errors')==[],'recorder cleanup error')
    else:
     value=packet['native'];native[role]=value;count=2 if role=='driver'else 1
     require(value.get('connections_closed')is True and value.get('windows_created')==count and value.get('windows_destroyed')==count and value.get('inputs_emitted')==0 and value.get('errors')==[],'own windows/connections not closed')
     require(packet.get('handler',{}).get('error_handler_restored')is True and packet['handler'].get('errors')==[],'native resource error handler not restored')
  except BaseException as error:errors.append(role+':'+repr(error))
 try:
  fresh_display_available();check_disk(directory);source=Path(__file__).resolve().parent
  roles['display']=child_factory([XVFB,':167','-screen','0','800x600x24','-nolisten','tcp','-noreset'],directory,':167',ttl=30,role='display');wait_display(roles['display'],deadline)
  argv=lambda role:['/usr/bin/python3','-E','-s','-B',str(source/'a1_xres_lifecycle_method.py'),'--role',role,'--directory',str(directory),'--display',':167']
  roles['driver']=child_factory(argv('driver'),directory,':167',ttl=30,role='driver');initial=call('driver','initialize',2)
  require(initial.get('mapped')is False and initial.get('inputs_emitted')==0 and len(initial.get('resources',[]))==2,'two unmapped driver resources required')
  for xid in initial['resources']:require(uint(xid)>3,'actual driver resource')
  driver=role_identity(roles['driver']);parent=self_identity()
  cfg=dict(controller_root=str(source),parent=parent,roles={'vanilla':dict(identity=[driver['pid'],driver['start_ticks']],argv=driver['argv'])},passive=dict(mode='method',display=':167',display_owner=display_owner(roles['display']),controller_gc=initial['resources'][0],original_window=initial['resources'][1],evidence=str(directory)))
  config=directory/'config.json';private_json(config,cfg)
  roles['recorder']=child_factory(['/usr/bin/python3','-E','-s','-B',str(source/'a1_xres_attribution_worker.py'),'--config',str(config),'--display',':167'],directory,':167',ttl=15,role='recorder')
  call('recorder','arm',3)
  roles['peer']=child_factory(argv('peer'),directory,':167',ttl=30,role='peer');initial_peer=call('peer','initialize',2)
  require(initial_peer.get('mapped')is False and initial_peer.get('inputs_emitted')==0 and len(initial_peer.get('resources',[]))==1,'one unmapped known peer resource')
  peer=dict(resource=initial_peer['resources'][0],before=role_identity(roles['peer']))
  query=call('driver','query',2) # One read-only query, only in the own167 method.
  call('recorder','capture_final',3);peer['after']=role_identity(roles['peer'])
  close('peer') # Normal leave while RECORD is still enabled; driver remains alive.
 except BaseException as error:errors.append(type(error).__name__+':'+str(error))
 finally:
  for role in('peer','recorder','driver','display'):close(role)
 try:facts=validate_method(directory,native['recorder'],peer,driver,children,query)
 except BaseException as error:errors.append('method evidence:'+repr(error))
 absent=display_absent()
 if not absent:errors.append('own display remains')
 cpu1=resource.getrusage(resource.RUSAGE_CHILDREN);self1=resource.getrusage(resource.RUSAGE_SELF)
 resources=dict(measured=True,wall_seconds=time.monotonic()-started,parent_cpu_seconds=self1.ru_utime+self1.ru_stime-self0.ru_utime-self0.ru_stime,children_cpu_seconds=cpu1.ru_utime+cpu1.ru_stime-cpu0.ru_utime-cpu0.ru_stime,children_maxrss_kib=cpu1.ru_maxrss,disk_free_bytes=shutil.disk_usage(directory).free)
 if resources['disk_free_bytes']<8*1024**3:errors.append('final disk below8GiB')
 row=dict(status='FAIL_OWN_XRES_RECORD_LIFECYCLE'if errors else'PASS_OWN_XRES_RECORD_LIFECYCLE_ONLY',no_inputs=True,inputs_emitted=0,tse_started=False,wine_started=False,frida_started=False,normal_closes=not errors,children=children,native_close=native,peer=peer,driver_query_attempt=query,resources=resources,errors=errors,fingerprints=fingerprints(),qualified=False,a1_pass=False,gain_fixed=False,old_u_attributed=False,display_absent=absent,**facts)
 private_json(directory/'method-result.json',row);return row


def run_method(directory):
 if not RUNTIME_REVIEWED:raise RuntimeError('disabled own167 lifecycle method')
 verify_package();directory=Path(directory).resolve();directory.mkdir(mode=0o700,exist_ok=False)
 with os.fdopen(os.open('/run/lock/ssam-own-xrecord-core-method167.lock',os.O_CREAT|os.O_RDWR|os.O_NOFOLLOW,0o600),'r+')as fd:
  require(os.fstat(fd.fileno()).st_uid==os.geteuid(),'own method lock owner');fcntl.flock(fd,fcntl.LOCK_EX|fcntl.LOCK_NB);return execute(directory)


class MethodNative(QualifiedNative):
 query=CoreNative.query # Exact previously qualified read, no pointer/input mutation.
 def __init__(self):
  super().__init__()
  import ctypes as C
  for name,args,ret in(('XNextRequest',[D],U),('XQueryPointer',[D,U,P(U),P(U),P(I),P(I),P(I),P(I),P(C.c_uint)],I)):
   fn=getattr(self.x,name);fn.argtypes=args;fn.restype=ret


class MethodDriver(Resources):
 def query(self):
  require(self.initialized and not self.closed and not getattr(self,'queried',False),'exactly one initialized own method query')
  self.queried=True;return self.n.query(self.connections[0],self.windows[0])


def run_resource_worker(role,directory,display):
 if not RUNTIME_REVIEWED:raise RuntimeError('disabled own lifecycle resource child')
 require(role in('driver','peer')and display==os.environ.get('DISPLAY')==':167','fixed own resource worker')
 directory=Path(directory).resolve();require(Path.cwd()==directory,'own resource child CWD')
 resource.setrlimit(resource.RLIMIT_FSIZE,(2097152,2097152));signal.setitimer(signal.ITIMER_REAL,30)
 native=None;obj=None;errors=[];expected=0
 try:
  native=MethodNative()if role=='driver'else QualifiedNative();obj=MethodDriver(native,2)if role=='driver'else Resources(native,1)
  while True:
   line=sys.stdin.buffer.readline(16385)
   if not line:break
   require(len(line)<=16384,'worker IPC line bound');request=json.loads(line);expected+=1
   require(type(request.get('id'))is int and request['id']==expected,'worker request order');command=request.get('command')
   if command=='stop':value=obj.close()
   elif command=='initialize':value=obj.initialize()
   elif command=='query'and role=='driver':value=obj.query()
   else:raise ValueError('strict method metadata-only command allowlist')
   reply=json.dumps(dict(id=expected,ok=True,value=value),allow_nan=False);require(len(reply.encode())<=16383,'worker reply bound');print(reply,flush=True)
   if command=='stop':break
 except BaseException as error:
  errors.append(type(error).__name__+':'+str(error)[:1024]);print(json.dumps(dict(id=expected,ok=False,error=errors[-1])),flush=True)
 finally:
  closed=None;handler=None
  if obj is not None:
   try:closed=obj.close()
   except BaseException as error:errors.append('final native close:'+repr(error))
  if native is not None:
   try:handler=native.close();errors.extend(handler['errors'])
   except BaseException as error:errors.append('native handler restore:'+repr(error))
  private_json(directory/(role+'-native-close.json'),dict(errors=errors,native=closed,handler=handler))
 return 1 if errors else 0


if __name__=='__main__':
 import argparse
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--directory',type=Path,required=True);p.add_argument('--role',choices=('driver','peer'));p.add_argument('--display',choices=(':167',));args=p.parse_args()
 if args.role:sys.exit(run_resource_worker(args.role,args.directory,args.display))
 print(json.dumps(run_method(args.directory),indent=2))
