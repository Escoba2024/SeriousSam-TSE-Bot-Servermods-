"""Disabled XRes-only own167 parent. No X libraries or input in this process."""
import fcntl
import hashlib
import json
import os
from pathlib import Path
import resource
import shutil
import stat
import sys
import time
from xrecord_core_process import OwnChild
from xres_pid_method import LIMITS,ROLES,require,same,validate_snapshot,method_verdict

RUNTIME_REVIEWED=False
DISPLAY=':167'
XSOCKET=Path('/tmp/.X11-unix/X167')
XLOCK=Path('/tmp/.X167-lock')
XVFB='/usr/bin/Xvfb'
XVFB_SHA256='6b27845931670c8c9b3ce7423696a452ce3cab1c7f316ce5f7ea7f1297fa2f84'

def validate_display(display):
 if display!=DISPLAY:raise ValueError('only own display167')
 return display

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


def private_json(path,value):
 with os.fdopen(os.open(path,os.O_WRONLY|os.O_CREAT|os.O_EXCL,0o600),'w')as out:json.dump(value,out,allow_nan=False,indent=2)


def own_namespace():return os.readlink('/proc/self/ns/pid')


def role_identity(child):
 child.guard();identity=dict(child.identity);identity['pid_namespace']=os.readlink('/proc/'+str(identity['pid'])+'/ns/pid');child.guard();return identity


def verify_package():
 root=Path(__file__).resolve().parent;m=bounded_json(root/'source-manifest.json',65536)
 require(m.get('runtime_enabled')is True,'disabled XRes manifest')
 require(m.get('schema')=='OWN_XRES_PID_METHOD_V1'and same(m.get('limits'),LIMITS),'XRes manifest contract')
 require({'xres_pid_controller.py','xres_pid_worker.py','xres_pid_method.py','xrecord_core_process.py'}.issubset(m.get('files',{})),'runtime source pins incomplete')
 for name,sha in m['files'].items():
  require(Path(name).name==name and hashlib.sha256((root/name).read_bytes()).hexdigest()==sha,'source pin:'+name)
 for section in('library_sha256','header_sha256','evidence_sha256'):
  require(isinstance(m.get(section),dict)and bool(m[section]),'required external pins:'+section)
  for name,sha in m[section].items():require(hashlib.sha256(Path(name).read_bytes()).hexdigest()==sha,'external pin:'+name)
 return m


def execute(directory,child_factory=OwnChild):
 if not RUNTIME_REVIEWED:raise RuntimeError('disabled XRes controller')
 directory=Path(directory).resolve();started=time.monotonic();deadline=started+30.;cpu0=resource.getrusage(resource.RUSAGE_CHILDREN);self0=resource.getrusage(resource.RUSAGE_SELF)
 errors=[];roles={};children={};native={};snapshots=[];expected={}
 def observe():
  guard_display(roles['display']);check_disk(directory)
  return {role:role_identity(child)for role,child in roles.items()}
 def call(role,command,timeout,**fields):
  left=deadline-time.monotonic()
  require(left>0,'method controller30s deadline')
  observe();packet=roles[role].call(command,timeout=min(timeout,left),**fields)
  require(type(packet.get('id'))is int and packet['id']>0 and packet.get('ok')is True,'authentic successful worker reply')
  require(time.monotonic()<=deadline,'method controller30s deadline')
  return packet
 def close(role):
  if role not in roles:return
  try:
   result=roles[role].cleanup(stop_timeout=(3 if role=='attributor'else 2)if role!='display'else None,normal_signal=role=='display');children[role]=result
   require(result.get('closed')is True and result.get('reaped')is True and result.get('forced')is False and result.get('errors')==[],'not normal closed/reaped')
   require(type(result.get('exit_code'))is int and result['exit_code']in((0,-15)if role=='display'else(0,)),'unexpected role exit')
   if role!='display':
    receipt=bounded_json(directory/(role+'-native-close.json'));native[role]=receipt
    require(receipt.get('errors')==[]and receipt.get('handler',{}).get('error_handler_restored')is True and receipt['handler'].get('errors')==[],'native error/handler restore missing')
  except BaseException as error:errors.append(role+':'+repr(error))
 try:
  fresh_display_available();check_disk(directory)
  roles['display']=child_factory([XVFB,DISPLAY,'-screen','0','800x600x24','-nolisten','tcp','-noreset'],directory,DISPLAY,ttl=30,role='display');wait_display(roles['display'],deadline)
  initial={};source=Path(__file__).resolve().parent
  for role in('driver','peer','attributor'):
   roles[role]=child_factory(['/usr/bin/python3','-E','-s','-B',str(source/'xres_pid_worker.py'),'--role',role,'--directory',str(directory),'--display',DISPLAY],directory,DISPLAY,ttl=15 if role=='attributor'else 30,role=role)
   initial[role]=call(role,'initialize',3 if role=='attributor'else 2)['value']
  resources=[]
  for role,count in(('driver',2),('peer',1)):
   value=initial[role];require(value.get('mapped')is False and type(value.get('connections'))is int and value['connections']==count and value.get('inputs_emitted')==0 and len(value.get('resources',[]))==count,'unmapped own metadata resources required')
   resources.extend(dict(role=role,connection_index=i,resource=xid)for i,xid in enumerate(value['resources']))
  expected=dict(pid_namespace=own_namespace(),identities=observe(),resources=resources)
  for index in range(2):
   before=observe();begin=time.monotonic();packet=call('attributor','snapshot',3,resources=[v['resource']for v in resources]);end=time.monotonic();after=observe()
   snapshot=packet['value'];snapshot.update(parent_started=begin,parent_finished=end,process_before=before,process_after=after,ipc_request_serial=packet['id']);snapshots.append(snapshot)
   private_json(directory/('snapshot-'+str(index)+'.json'),snapshot)
   validate_snapshot(snapshot,expected);require(snapshot.get('index')==index,'worker snapshot invocation differs')
 except BaseException as error:errors.append(type(error).__name__+':'+str(error))
 finally:
  for role in('attributor','peer','driver','display'):close(role)
 native_closed=False
 try:
  require(set(native)=={'driver','peer','attributor'},'all native close receipts required')
  for role,count in(('driver',2),('peer',1)):
   receipt=native[role]['native'];require(receipt.get('connections_closed')is True and receipt.get('windows_created')==count and receipt.get('windows_destroyed')==count and receipt.get('inputs_emitted')==0 and receipt.get('errors')==[],'own windows/connections close not proved')
  receipt=native['attributor']['native'];require(receipt.get('connections_closed')is True and receipt.get('snapshots')==2 and receipt.get('inputs_emitted')==0 and receipt.get('errors')==[]and same(receipt.get('free_counts'),dict(client_arrays_allocated=2,client_arrays_freed=2,id_arrays_allocated=12,id_arrays_freed=12)),'metadata arrays/connections close not proved')
  native_closed=True
 except BaseException as error:errors.append('native close:'+repr(error))
 cpu1=resource.getrusage(resource.RUSAGE_CHILDREN);self1=resource.getrusage(resource.RUSAGE_SELF)
 measured=dict(measured=True,wall_seconds=time.monotonic()-started,parent_cpu_seconds=self1.ru_utime+self1.ru_stime-self0.ru_utime-self0.ru_stime,children_cpu_seconds=cpu1.ru_utime+cpu1.ru_stime-cpu0.ru_utime-cpu0.ru_stime,children_maxrss_kib=cpu1.ru_maxrss,disk_free_bytes=shutil.disk_usage(directory).free)
 if measured['disk_free_bytes']<8*1024**3:errors.append('final disk below8GiB')
 row=dict(expected=expected,snapshots=snapshots,children=children,native_close=native,native_closed=native_closed,display_absent=display_absent(),errors=errors,resources=measured,inputs_emitted=0,tse_started=False,xrecord_started=False)
 row.update(method_verdict(row));private_json(directory/'method-result.json',row);return row


def run_method(directory):
 if not RUNTIME_REVIEWED:raise RuntimeError('disabled XRes method; reviewed Root freeze required')
 verify_package();directory=Path(directory).resolve();directory.mkdir(mode=0o700,exist_ok=False)
 lock=Path('/run/lock/ssam-own-xrecord-core-method167.lock')
 with os.fdopen(os.open(lock,os.O_CREAT|os.O_RDWR|os.O_NOFOLLOW,0o600),'r+')as fd:
  require(os.fstat(fd.fileno()).st_uid==os.geteuid(),'method lock owner');fcntl.flock(fd,fcntl.LOCK_EX|fcntl.LOCK_NB)
  return execute(directory)


if __name__=='__main__':
 import argparse
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--directory',required=True,type=Path);print(json.dumps(run_method(p.parse_args().directory),indent=2))
