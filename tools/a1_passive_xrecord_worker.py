"""DISABLED fresh-exec passive XRecord child; immutable method classes reused."""
import ctypes as C
import hashlib
import json
import os
from pathlib import Path
import resource
import select
import signal
import stat
import sys
import time
from types import SimpleNamespace

CORE=Path(__file__).resolve().parent/'passive-core'
if CORE.is_dir():sys.path.insert(0,str(CORE))
from xrecord_core_native import Native, RecordState, RecordRange, range_coverage, selected_ranges
from xrecord_core_worker import Recorder
from xrecord_core_process import start_ticks, proc_bytes
from a1_passive_xrecord import controller_gc, private_json, method_fingerprints

RUNTIME_REVIEWED=False


def verify_owner(cfg):
 parent=cfg['parent'];p=Path('/proc')/str(parent['pid'])
 if os.getppid()!=parent['pid']or start_ticks(parent['pid'])!=parent['start_ticks']:raise ValueError('own passive parent changed')
 mode=cfg['passive']['mode'];display=cfg['passive']['display']
 if(mode,display)not in(('a1',':154'),('method',':167')):raise ValueError('fixed separate display scopes')
 if os.environ.get('DISPLAY')!=display:raise ValueError('passive child DISPLAY differs')
 d=cfg['passive']['display_owner'];pid,started=d['identity'];proc=Path('/proc')/str(pid)
 if start_ticks(pid)!=started or proc_bytes(proc/'cmdline',16384).rstrip(b'\0').split(b'\0')!=[v.encode()for v in d['argv']]:raise ValueError('owned Xvfb identity differs')
 if d['argv'][0]!='/usr/bin/Xvfb'or display not in d['argv']:raise ValueError('owned Xvfb argv scope')
 if mode=='method'and int(proc_bytes(proc/'stat',16384).rsplit(b') ',1)[1].split()[1])!=parent['pid']:raise ValueError('metadata method Xvfb is not this own parent child')
 if d.get('unit')and not any(row.split(':',2)[-1].rstrip('/').endswith('/'+d['unit'])for row in(proc/'cgroup').read_text().splitlines()):raise ValueError('owned Xvfb unit differs')
 number=display[1:];sock=Path('/tmp/.X11-unix/X'+number);lock=Path('/tmp/.X'+number+'-lock');st=sock.stat()
 if sock.is_symlink()or lock.is_symlink()or not stat.S_ISSOCK(st.st_mode)or[st.st_dev,st.st_ino,st.st_uid]!=d['socket_pin']or int(lock.read_text())!=pid:raise ValueError('owned Xvfb socket differs')
 matches=[]
 for line in Path('/proc/net/unix').read_text().splitlines()[1:]:
  r=line.split()
  if len(r)==8 and r[7]==str(sock)and r[3:6]==['00010000','0001','01']:matches.append(r[6])
 fds=list((proc/'fd').iterdir());links=[]
 if len(matches)!=1 or len(fds)>128:raise ValueError('owned Xvfb listener bound')
 for fd in fds:
  try:links.append(os.readlink(fd))
  except FileNotFoundError:pass
 if 'socket:['+matches[0]+']'not in links:raise ValueError('owned Xvfb listener FD differs')
 if mode=='a1':
  from a1_input_worker import ownership_gate
  ownership_gate(cfg)
  original=Path('/proc')/str(cfg['roles']['vanilla']['identity'][0])
  if[entry for entry in proc_bytes(original/'environ',65536).split(b'\0')if entry.startswith(b'DISPLAY=')]!=[b'DISPLAY=:154']:raise ValueError('own Original DISPLAY differs')
 if start_ticks(pid)!=started:raise ValueError('Xvfb changed during owner read')
 return True


class ResourceNative(Native):
 def __init__(self,cfg):self.cfg=cfg;self.connections=[];self.bindings={};self.initial_clients=None;self.data_client=None;self.context_snapshots=[];self.opcode=None;super().__init__()
 def open(self):
  verify_owner(self.cfg);d=self.x.XOpenDisplay(self.cfg['passive']['display'].encode())
  if not d:raise ValueError('owned passive display unavailable')
  try:self.check()
  except BaseException:
   try:self.x.XCloseDisplay(d)
   except BaseException as error:self.errors.append('failed-open close:'+repr(error))
   raise
  self.connections.append(d);return d
 def lookup_resource(self,d,spec,opcode):
  if type(spec)is not int or not 3<spec<=0xffffffff:raise ValueError('valid existing resource required')
  wanted=selected_ranges(opcode);allocated=[];ctx=0;state=C.POINTER(RecordState)()
  try:
   for r in wanted:
    p=self.t.XRecordAllocRange()
    if not p:raise ValueError('metadata range allocation failed')
    allocated.append(p)
    for name,_ in RecordRange._fields_:setattr(p.contents,name,getattr(r,name))
   pointers=(C.POINTER(RecordRange)*4)(*allocated);specs=(C.c_ulong*1)(spec)
   ctx=int(self.t.XRecordCreateContext(d,7,specs,1,pointers,4))
   if not ctx:raise ValueError('metadata lookup context absent')
   self.x.XSync(d,0)
   if not self.t.XRecordGetContext(d,ctx,C.byref(state))or not state:raise ValueError('metadata lookup state absent')
   s=state.contents
   if s.enabled!=0 or s.datum_flags!=7 or s.nclients!=1 or not s.client_info or not s.client_info[0]:raise ValueError('metadata lookup state differs')
   info=s.client_info[0].contents
   if not 3<info.client<=0xffffffff or not 1<=info.nranges<=4 or not info.ranges or any(not info.ranges[i]for i in range(int(info.nranges))):raise ValueError('metadata lookup client/ranges invalid')
   if range_coverage([info.ranges[i].contents for i in range(int(info.nranges))])!=range_coverage(wanted):raise ValueError('metadata lookup ranges differ')
   self.check();return int(info.client)
  finally:
   active=sys.exc_info()[0]is not None;cleanup=[]
   if state:
    try:self.t.XRecordFreeState(state)
    except BaseException as error:cleanup.append(error)
   if ctx:
    try:
     if not self.t.XRecordFreeContext(d,ctx):raise ValueError('lookup FreeContext failed')
    except BaseException as error:cleanup.append(error)
    try:self.x.XSync(d,0)
    except BaseException as error:cleanup.append(error)
   for p in allocated:
    try:self.x.XFree(p)
    except BaseException as error:cleanup.append(error)
   self.errors.extend(('metadata cleanup:'+repr(e))[:1024]for e in cleanup[:8])
   if cleanup and not active:raise cleanup[0]
 def versions(self,d):
  result=super().versions(d);self.opcode=result['xtest_opcode'];return result
 def context_state(self,d,context,ranges,*,enabled):
  if not self.bindings:
   opcode=self.opcode
   if type(opcode)is not int:raise ValueError('version-verified opcode absent')
   self.bindings={name:self.lookup_resource(d,int(self.cfg['passive'][key]),opcode)for name,key in(('controller_transport','controller_gc'),('original_window_owner','original_window'))}
   if len(set(self.bindings.values()))!=2:raise ValueError('two distinct existing resource clients required')
  state=C.POINTER(RecordState)()
  try:
   if not self.t.XRecordGetContext(d,context,C.byref(state))or not state:raise ValueError('passive context absent')
   s=state.contents
   if s.enabled!=int(enabled)or s.datum_flags!=7 or not 3<=s.nclients<=32 or not s.client_info:raise ValueError('passive context flags/client bound')
   clients=[]
   for i in range(int(s.nclients)):
    if not s.client_info[i]:raise ValueError('null passive client info')
    info=s.client_info[i].contents;clients.append(int(info.client))
    if not 1<=info.nranges<=4 or not info.ranges or any(not info.ranges[j]for j in range(int(info.nranges))):raise ValueError('passive ranges bound')
    if range_coverage([info.ranges[j].contents for j in range(int(info.nranges))])!=range_coverage(ranges):raise ValueError('passive range coverage differs')
   current=set(clients)
   if len(current)!=len(clients)or not{2,*self.bindings.values()}.issubset(current)or any(x<=3 for x in current if x!=2):raise ValueError('required resource clients/FutureClients differ')
   if not enabled:self.initial_clients=current
   elif self.data_client is None:
    missing=self.initial_clients-current;added=current-self.initial_clients
    if len(missing)!=1 or added:raise ValueError('data connection exclusion ambiguous')
    self.data_client=next(iter(missing))
   elif self.data_client in current:raise ValueError('data client unexpectedly recorded')
   if len(self.context_snapshots)>=8:raise ValueError('passive context snapshot bound')
   self.context_snapshots.append(dict(enabled=enabled,clients=sorted(current)))
   self.check();return True
  finally:
   if state:self.t.XRecordFreeState(state)


def metadata_probe(cfg):
 """Own167 metadata method only. No XTEST, Warp or QueryPointer call."""
 n=ResourceNative(cfg);one=two=None;window=0;errors=[];answer=None;normal=False
 try:
  one=n.open();two=n.open();root=int(n.x.XDefaultRootWindow(two));window=int(n.x.XCreateSimpleWindow(two,root,0,0,1,1,0,0,0));n.x.XSync(two,0)
  gc=controller_gc(SimpleNamespace(x=n.x,d=one));n.x.XSync(one,0);opcode=n.versions(one)['xtest_opcode']
  before=int(n.x.XNextRequest(one))
  a=n.lookup_resource(one,gc,opcode);b=n.lookup_resource(one,window,opcode)
  after=int(n.x.XNextRequest(one))
  if not 0<before<after<=0xffffffff:raise ValueError('public metadata request counter interval differs')
  if a==b:raise ValueError('different own connections must have different resource clients')
  n.check();answer=dict(status='PASS_OWN_XRECORD_METADATA_BINDING_ONLY',no_inputs=True,qualified=False,a1_pass=False,metadata_request_interval=[before,after])
 except BaseException as error:errors.append(repr(error))
 finally:
  if window:
   try:n.x.XDestroyWindow(two,window);n.x.XSync(two,0)
   except BaseException as error:errors.append('window:'+repr(error))
  for d in(two,one):
   if d:
    try:n.x.XCloseDisplay(d)
    except BaseException as error:errors.append('close:'+repr(error))
  errors+=n.errors;normal=not errors
 if answer is None:answer=dict(status='FAIL_OWN_XRECORD_METADATA_BINDING',no_inputs=True,qualified=False,a1_pass=False)
 answer.update(normal_closes=normal,errors=errors)
 if not normal:answer['status']='FAIL_OWN_XRECORD_METADATA_BINDING'
 return answer


def run_worker(config_path,display):
 if not RUNTIME_REVIEWED:raise RuntimeError('disabled passive recorder; Root freeze required')
 path=Path(config_path).resolve(strict=True);cfg=json.loads(path.read_text());root=Path(cfg['controller_root']).resolve(strict=True)
 if root!=Path(__file__).resolve().parent or cfg['passive']['display']!=display:raise ValueError('passive frozen source/display binding')
 manifest=json.loads((root/'source-manifest.json').read_text())
 if manifest.get('runtime_reviewed')is not True:raise RuntimeError('disabled passive manifest')
 for p,sha in manifest['runtime_dependencies'].items():
  if hashlib.sha256(Path(p).read_bytes()).hexdigest()!=sha:raise ValueError('passive worker source pin')
 verify_owner(cfg);resource.setrlimit(resource.RLIMIT_FSIZE,(2097152,2097152));signal.setitimer(signal.ITIMER_REAL,15)
 directory=Path(cfg['passive']['evidence']).resolve()
 if Path.cwd()!=directory:raise ValueError('passive child CWD differs')
 if cfg['passive']['mode']=='method':
  answer=metadata_probe(cfg);answer['fingerprints']=method_fingerprints();private_json(directory/'metadata-method.json',answer);return 0 if not answer['errors']else 1
 obj=None;errors=[];sequence=0;buffer=b'';native=None
 try:
  obj=Recorder(ResourceNative(cfg),directory)
  while True:
   if obj.armed:obj.pump(0)
   fds=[sys.stdin.fileno()]+([obj.n.x.XConnectionNumber(obj.data)]if obj.armed else[])
   ready=select.select(fds,[],[],.02)[0]
   if sys.stdin.fileno()not in ready:continue
   data=os.read(sys.stdin.fileno(),min(4096,16385-len(buffer)))
   if not data:break
   buffer+=data
   if len(buffer)>16384:raise ValueError('passive IPC bound')
   if b'\n'not in buffer:continue
   line,buffer=buffer.split(b'\n',1);request=json.loads(line);sequence+=1
   if type(request.get('id'))is not int or request['id']!=sequence:raise ValueError('passive IPC sequence')
   command=request.get('command');verify_owner(cfg)
   if command=='arm':value=obj.arm();value.update(bindings=obj.n.bindings,context_snapshots=obj.n.context_snapshots)
   elif command=='check':
    if not obj.armed:raise ValueError('passive observer not armed')
    obj.pump(0);value=obj.sink.receipt()
   elif command=='stop':value=obj.close()
   else:raise ValueError('passive command allowlist')
   print(json.dumps(dict(id=sequence,ok=True,value=value),allow_nan=False),flush=True)
   if command=='stop':break
 except BaseException as error:
  errors.append(repr(error)[:1024]);print(json.dumps(dict(id=sequence,ok=False,error=errors[-1])),flush=True)
 finally:
  if obj is not None:
   try:native=obj.close()
   except BaseException as error:errors.append('close:'+repr(error))
  final={}if native is None else dict(native)
  final['errors']=final.get('errors',[])+errors
  private_json(directory/'recorder-native-close.json',final)
 return 1 if errors else 0

if __name__=='__main__':
 import argparse
 p=argparse.ArgumentParser();p.add_argument('--config',required=True);p.add_argument('--display',required=True);a=p.parse_args();sys.exit(run_worker(a.config,a.display))
