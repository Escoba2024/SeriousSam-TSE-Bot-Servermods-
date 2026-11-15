"""DISABLED exec-only XRes metadata and explicitly selected RECORD lifecycle."""
import ctypes as C
import hashlib
import json
import os
from pathlib import Path
import resource
import select
import signal
import sys
import time

CORE=Path(__file__).resolve().parent/'passive-core'
if CORE.is_dir():sys.path.insert(0,str(CORE))
from xrecord_core_native import RecordRange,RecordSink,CALLBACK,selected_ranges,range_coverage
from xrecord_core_worker import Recorder
from xrecord_core_process import start_ticks
from a1_passive_xrecord_worker import ResourceNative,verify_owner
from a1_passive_xrecord import private_json
from a1_xres_attribution_evidence import snapshot as validate_snapshot
from xres_pid_worker import Client,Spec,Value,Native as QualifiedPID,abi_layout
from xres_pid_method import require,uint,valid_version

RUNTIME_REVIEWED=False


def require_scope(manifest,cfg,display):
 expected={'A1_154':('a1',':154'),'OWN_METHOD_167':('method',':167')}.get(manifest.get('xres_attribution',{}).get('allowed_scope'))
 require(expected is not None and (cfg['passive']['mode'],cfg['passive']['display'])==expected and display==expected[1],'fixed manifest lifecycle scope')


def lifecycle_ranges(opcode):
 rows=selected_ranges(opcode)
 rows[0].client_started=1;rows[0].client_died=1
 return rows


class PublicPID:
 _charge=QualifiedPID._charge
 _id=QualifiedPID._id
 check=QualifiedPID.check
 def __init__(self,native,manifest):
  require(abi_layout()==manifest['xres_attribution']['abi_layout'],'qualified public XRes ABI changed')
  path='/lib/x86_64-linux-gnu/libXRes.so.1'
  require(hashlib.sha256(Path(path).read_bytes()).hexdigest()==manifest['xres_attribution']['library_sha256'][path],'XRes library pin changed')
  self.x=native.x;self.errors=native.errors;self.total_free_counts={};self.r=C.CDLL(path)
  D=C.c_void_p;I=C.c_int;P=C.POINTER
  for name,args,ret in(('XResQueryExtension',[D,P(I),P(I)],I),('XResQueryVersion',[D,P(I),P(I)],I),('XResQueryClients',[D,P(I),P(P(Client))],I),('XResQueryClientIds',[D,C.c_long,P(Spec),P(C.c_long),P(P(Value))],I),('XResGetClientPid',[P(Value)],I),('XResClientIdsDestroy',[C.c_long,P(Value)],None)):
   fn=getattr(self.r,name);fn.argtypes=args;fn.restype=ret
 def versions(self,d):
  event=C.c_int();error=C.c_int();major=C.c_int();minor=C.c_int()
  require(self.r.XResQueryExtension(d,C.byref(event),C.byref(error))==1,'XRes extension missing')
  require(self.r.XResQueryVersion(d,C.byref(major),C.byref(minor))==1,'XRes version failure')
  version=[major.value,minor.value];require(valid_version(version),'XRes protocol1.2 required');self.check();return version
 def query(self,d,context_clients,resources):
  require(isinstance(context_clients,list)and len(context_clients)==len(set(context_clients))and 2 in context_clients,'actual context/FutureClients required')
  for base in context_clients:require(type(base)is int and (base==2 or 3<base<=0xffffffff),'positive actual context base')
  targets=sorted(base for base in context_clients if base!=2);require(2<=len(targets)<=32,'max32 positive context bases')
  require(set(resources)=={'controller_transport','original_window_owner'},'two existing resources only')
  for xid in resources.values():require(uint(xid)>3,'no wildcard/resource zero')
  counts=dict(client_arrays_allocated=0,client_arrays_freed=0,id_arrays_allocated=0,id_arrays_freed=0);num=C.c_int();ptr=C.POINTER(Client)();primary=None
  try:
   status=self.r.XResQueryClients(d,C.byref(num),C.byref(ptr))
   if ptr:self._charge(counts,'client_arrays_allocated')
   require(status==1 and 1<=num.value<=64 and bool(ptr),'bounded actual QueryClients reply')
   clients=[dict(resource_base=int(ptr[i].resource_base),resource_mask=int(ptr[i].resource_mask))for i in range(num.value)];self.check()
  except BaseException as error:primary=error;raise
  finally:
   if ptr:
    try:self.x.XFree(ptr);self._charge(counts,'client_arrays_freed')
    except BaseException as error:
     self.errors.append('client array cleanup:'+repr(error))
     if primary is None:raise
  queries=[self._id(d,'base',base,counts)for base in targets]
  queries.extend(self._id(d,kind,resources[kind],counts)for kind in('controller_transport','original_window_owner'))
  return dict(query_clients_status=status,clients=clients,queries=queries,free_counts=counts,errors=list(self.errors))



def read_processes(cfg):
 verify_owner(cfg);mode=cfg['passive']['mode'];display=cfg['passive']['display']
 require((mode,display)in(('a1',':154'),('method',':167')),'fixed separate attribution scope')
 roles=dict(parent=[cfg['parent']['pid'],cfg['parent']['start_ticks']],recorder=[os.getpid(),start_ticks(os.getpid())],display=cfg['passive']['display_owner']['identity'],vanilla=cfg['roles']['vanilla']['identity'])
 result={}
 for role,(pid,ticks)in roles.items():
  require(type(pid)is int and pid>0 and type(ticks)is int and ticks>0 and start_ticks(pid)==ticks,'known own process generation changed')
  ns=os.readlink('/proc/'+str(pid)+'/ns/pid');result[role]=dict(pid=pid,start_ticks=ticks,pid_namespace=ns,display=display)
  if mode=='method'and role=='vanilla':
   proc=Path('/proc')/str(pid);expected=cfg['roles']['vanilla']
   require(proc.joinpath('cmdline').read_bytes().rstrip(b'\0').split(b'\0')==[x.encode()for x in expected['argv']],'own method driver argv changed')
   require(int(proc.joinpath('stat').read_bytes().rsplit(b') ',1)[1].split()[1])==cfg['parent']['pid'],'own method driver parent changed')
 require(len({v['pid']for v in result.values()})==4 and len({v['pid_namespace']for v in result.values()})==1,'four separate own processes in same PID namespace')
 verify_owner(cfg);return result


class LifecycleRecorder(Recorder):
 def __init__(self,native,directory,cfg,manifest):
  super().__init__(native,directory);self.cfg=cfg;self.pid=PublicPID(native,manifest);self.snapshots=[];self.metadata_attempts=[];self.metadata_errors=[];self.expected=None;self.lifecycle_verified=False;self.pid_version=None
 def _capture(self):
  require(self.armed and not self.closed and len(self.metadata_attempts)<2,'only two enabled metadata captures')
  attempt=dict(index=len(self.metadata_attempts),status='RESERVED');self.metadata_attempts.append(attempt)
  try:
   before=read_processes(self.cfg);started=time.monotonic();watermark=self.sink.calls
   self.n.context_state(self.control,self.context,self.ranges,enabled=True)
   context=list(self.n.context_snapshots[-1]['clients'])
   if self.pid_version is None:self.pid_version=self.pid.versions(self.control)
   resources={name:int(self.cfg['passive'][key])for name,key in(('controller_transport','controller_gc'),('original_window_owner','original_window'))}
   if self.expected is None:
    scope='A1_154'if self.cfg['passive']['mode']=='a1'else'OWN_METHOD_167'
    self.expected=dict(scope=scope,xtest_opcode=self.versions['xtest_opcode'],identities=before,pid_namespace=before['parent']['pid_namespace'],resources=resources,resource_roles={'controller_transport':'parent'if scope=='A1_154'else'vanilla','original_window_owner':'vanilla'})
   raw=self.pid.query(self.control,context,resources);attempt['raw']=raw
   self.n.context_state(self.control,self.context,self.ranges,enabled=True)
   after=read_processes(self.cfg)
   row=dict(raw,index=len(self.snapshots),record_enabled=self.armed,lifecycle_coverage={k:range_coverage(self.ranges)[k]for k in('client_started','client_died')},bindings=dict(self.n.bindings),context_clients=context,xres_version=self.pid_version,process_before=before,process_after=after,monotonic_started=started,monotonic_finished=time.monotonic(),callback_serial_before=watermark,callback_serial_after=self.sink.calls)
   attempt['snapshot']=row;validate_snapshot(row,self.expected);self.snapshots.append(row);attempt['status']='ACCEPTED'
   return dict(snapshot_index=row['index'],queries=len(row['queries']),lifecycle_verified=True)
  except BaseException as error:
   attempt.update(status='REJECTED',error=repr(error)[:1024]);self.metadata_errors.append(repr(error)[:1024]);raise
 def arm(self):
  # Deliberately copied bounded Core Recorder.arm: only range factory and the
  # post-StartOfData metadata capture differ. No mutation of Core globals.
  if self.control or self.armed:raise ValueError('arm repeated')
  self.control=self.n.open();self.data=self.n.open();self.versions=self.n.versions(self.control)
  self.ranges=lifecycle_ranges(self.versions['xtest_opcode']);allocated=[]
  try:
   for template in self.ranges:
    pointer=self.n.t.XRecordAllocRange()
    if not pointer:raise ValueError('XRecordAllocRange failed')
    allocated.append(pointer)
    for name,_ in RecordRange._fields_:setattr(pointer.contents,name,getattr(template,name))
   pointers=(C.POINTER(RecordRange)*4)(*allocated);clients=(C.c_ulong*1)(3)
   self.context=int(self.n.t.XRecordCreateContext(self.control,7,clients,1,pointers,4))
   if not self.context:raise ValueError('record context absent')
  finally:
   for pointer in allocated:self.n.x.XFree(pointer)
  self.n.x.XSync(self.control,0);self.n.context_state(self.control,self.context,self.ranges,enabled=False)
  self.sink=RecordSink(self.n.t,self.directory/'record-raw.jsonl',self.versions['xtest_opcode'],started=time.monotonic());self.cb=CALLBACK(self.sink.callback)
  if not self.n.t.XRecordEnableContextAsync(self.data,self.context,self.cb,None):raise ValueError('record enable failed')
  self.n.context_state(self.control,self.context,self.ranges,enabled=True);self.n.check()
  if self.sink.starts!=1 or self.sink.errors:raise ValueError('record start not proved')
  self.armed=True;self.lifecycle_verified=True;metadata=self._capture()
  return dict(**self.versions,**self.sink.receipt(),ranges_verified=True,bindings=dict(self.n.bindings),context_snapshots=list(self.n.context_snapshots),xres_metadata=metadata)
 def capture_final(self):
  require((self.cfg['passive']['mode'],self.cfg['passive']['display'])==('method',':167'),'capture_final only own167 method')
  require(len(self.snapshots)==1 and len(self.metadata_attempts)==1,'exactly second capture only')
  return self._capture()
 def close(self):
  if self.closed:return self.final
  if self.armed and len(self.snapshots)==1 and not self.metadata_errors:
   try:self._capture()
   except BaseException:pass # Sticky metadata errors retained; Core close still runs.
  final=super().close();final['lifecycle_verified']=self.lifecycle_verified
  final['cleanup_errors']=final.get('cleanup_errors',[])+['xres:'+e for e in self.metadata_errors]
  final['xres_summary']=dict(accepted_snapshots=len(self.snapshots),attempts=len(self.metadata_attempts),free_counts=dict(self.pid.total_free_counts))
  self.final=final;return final
 def metadata_receipt(self):return dict(expected=self.expected,snapshots=self.snapshots,attempts=self.metadata_attempts,errors=self.metadata_errors,free_counts=dict(self.pid.total_free_counts))


def run_worker(config_path,display):
 if not RUNTIME_REVIEWED:raise RuntimeError('disabled XRes lifecycle worker')
 path=Path(config_path).resolve(strict=True);cfg=json.loads(path.read_text());root=Path(cfg['controller_root']).resolve(strict=True)
 require(root==Path(__file__).resolve().parent and cfg['passive']['display']==display,'own frozen lifecycle scope')
 manifest=json.loads((root/'source-manifest.json').read_bytes());require(manifest.get('runtime_reviewed')is True,'disabled lifecycle manifest')
 require_scope(manifest,cfg,display)
 for p,h in manifest['runtime_dependencies'].items():require(hashlib.sha256(Path(p).read_bytes()).hexdigest()==h,'lifecycle runtime source pin')
 verify_owner(cfg);resource.setrlimit(resource.RLIMIT_FSIZE,(2097152,2097152));signal.setitimer(signal.ITIMER_REAL,15)
 directory=Path(cfg['passive']['evidence']).resolve();require(Path.cwd()==directory,'own worker CWD')
 obj=None;errors=[];sequence=0;buffer=b''
 try:
  obj=LifecycleRecorder(ResourceNative(cfg),directory,cfg,manifest)
  while True:
   if obj.armed:obj.pump(0)
   ready=select.select([sys.stdin.fileno()]+([obj.n.x.XConnectionNumber(obj.data)]if obj.armed else[]),[],[],.02)[0]
   if sys.stdin.fileno()not in ready:continue
   data=os.read(sys.stdin.fileno(),min(4096,16385-len(buffer)))
   if not data:break
   buffer+=data;require(len(buffer)<=16384,'passive IPC bound')
   if b'\n'not in buffer:continue
   line,buffer=buffer.split(b'\n',1);request=json.loads(line);sequence+=1
   require(type(request.get('id'))is int and request['id']==sequence,'passive IPC sequence');verify_owner(cfg)
   command=request.get('command')
   if command=='arm':value=obj.arm()
   elif command=='check':
    require(obj.armed,'passive observer not armed');obj.pump(0);value=obj.sink.receipt()
   elif command=='capture_final'and (cfg['passive']['mode'],display)==('method',':167'):value=obj.capture_final()
   elif command=='stop':value=obj.close()
   else:raise ValueError('strict scoped passive command allowlist')
   wire=json.dumps(dict(id=sequence,ok=True,value=value),allow_nan=False);require(len(wire.encode())<=16383,'bounded passive reply');print(wire,flush=True)
   if command=='stop':break
 except BaseException as error:
  errors.append(repr(error)[:1024]);print(json.dumps(dict(id=sequence,ok=False,error=errors[-1])),flush=True)
 finally:
  native={}
  if obj is not None:
   try:native=obj.close()
   except BaseException as error:errors.append('close:'+repr(error))
   try:
    metadata=obj.metadata_receipt();private_json(directory/'xres-attribution.json',metadata);raw=(directory/'xres-attribution.json').read_bytes();native['xres_evidence']=dict(path='xres-attribution.json',sha256=hashlib.sha256(raw).hexdigest(),bytes=len(raw))
   except BaseException as error:errors.append('xres evidence:'+repr(error))
  native['errors']=native.get('errors',[])+errors;private_json(directory/'recorder-native-close.json',native)
 return 1 if errors else 0


if __name__=='__main__':
 import argparse
 p=argparse.ArgumentParser();p.add_argument('--config',required=True);p.add_argument('--display',required=True);a=p.parse_args();sys.exit(run_worker(a.config,a.display))
