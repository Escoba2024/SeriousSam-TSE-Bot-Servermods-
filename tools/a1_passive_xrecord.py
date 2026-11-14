"""DISABLED passive adapter. Parent uses existing Xlib handle, never loads Xlib."""
import json
import ast
import hashlib
import os
from pathlib import Path
import sys
import time

CORE=Path(__file__).resolve().parent/'passive-core'
if CORE.is_dir():sys.path.insert(0,str(CORE))
from xrecord_core_process import OwnChild

RUNTIME_REVIEWED=False


def controller_gc(transport):
 """Two public metadata getters; no allocation, pointer query or X request."""
 import ctypes as c
 x=transport.x
 x.XNextRequest.argtypes=[c.c_void_p];x.XNextRequest.restype=c.c_ulong
 x.XDefaultGC.argtypes=[c.c_void_p,c.c_int];x.XDefaultGC.restype=c.c_void_p
 x.XGContextFromGC.argtypes=[c.c_void_p];x.XGContextFromGC.restype=c.c_ulong
 gc=x.XDefaultGC(transport.d,0)
 if not gc:raise ValueError('existing default GC absent')
 xid=int(x.XGContextFromGC(gc))
 if not 3<xid<=0xffffffff:raise ValueError('existing default GC XID invalid')
 return xid


class XtstProxy:
 def __init__(self,transport):self.transport=transport;self.inner=transport.t;self.observer=None
 def __getattr__(self,name):
  fn=getattr(self.inner,name)
  if name not in('XTestFakeRelativeMotionEvent','XTestFakeKeyEvent','XTestFakeButtonEvent'):return fn
  def invoke(*args):
   if self.observer is None:return fn(*args)
   if name=='XTestFakeButtonEvent':raise RuntimeError('no-fire passive adapter rejects button input')
   row=dict(function=name,arguments=list(args),started_monotonic=time.monotonic(),host_epoch_ms=time.time()*1000,return_value=None)
   first=int(self.transport.x.XNextRequest(self.transport.d));primary=None
   try:row['return_value']=fn(*args);return row['return_value']
   except BaseException as error:primary=error;row['error']=repr(error);raise
   finally:
    try:
     row.update(sequence_interval=[first,int(self.transport.x.XNextRequest(self.transport.d))],finished_monotonic=time.monotonic())
     self.observer.record_emission(row)
    except BaseException:
     if hasattr(self.observer,'failed'):self.observer.failed=True
     if primary is None:raise
  return invoke


def instrument_transport(transport):
 if hasattr(transport,'_passive_xrecord_proxy'):raise ValueError('transport already wrapped')
 proxy=XtstProxy(transport);transport._passive_xrecord_proxy=proxy;transport.t=proxy
 return proxy


def method_fingerprints(source=None,core=None):
 source=Path(__file__).resolve().parent if source is None else Path(source)
 core=source/'passive-core'if core is None else Path(core)
 result={}
 for name,targets in(('a1_passive_xrecord.py',{'controller_gc'}),('a1_passive_xrecord_worker.py',{'lookup_resource','metadata_probe'})):
  for node in ast.walk(ast.parse((source/name).read_text())):
   if isinstance(node,ast.FunctionDef)and node.name in targets:result[name+':'+node.name]=hashlib.sha256(ast.dump(node,include_attributes=False).encode()).hexdigest()
 result['immutable_method_native']=hashlib.sha256((core/'xrecord_core_native.py').read_bytes()).hexdigest()
 return result


def require_method_qualification(scope):
 q=scope.get('binding_qualification')
 if not isinstance(q,dict)or q.get('status')!='PASS_OWN_XRECORD_METADATA_BINDING_ONLY':raise RuntimeError('new metadata method qualification missing')
 if q.get('fingerprints')!=scope.get('method_fingerprints'):raise ValueError('new metadata method fingerprint differs')
 if method_fingerprints()!=scope.get('method_fingerprints'):raise ValueError('actual metadata method source differs')
 if q.get('no_inputs')is not True or q.get('normal_closes')is not True:raise ValueError('new metadata method cleanup/no-input proof absent')
 return q


def private_json(path,value):
 data=(json.dumps(value,allow_nan=False,indent=2)+'\n').encode()
 if len(data)>262144:raise ValueError('private adapter receipt bound')
 # Only this own0700directory is used; preserve earlier evidence by distinct names.
 with os.fdopen(os.open(path,os.O_WRONLY|os.O_CREAT|os.O_EXCL,0o600),'wb')as f:f.write(data)


class PassiveRecorder:
 def __init__(self,kid,directory,transport):self.kid=kid;self.directory=directory;self.transport=transport;self.emissions=[];self.failed=False;self.closed=False;self.arm_receipt=None
 @classmethod
 def start(cls,evidence,manifest,old_config,transport):
  if not RUNTIME_REVIEWED:raise RuntimeError('disabled passive A1 XRecord; Root freeze required')
  scope=manifest['passive_xrecord'];require_method_qualification(scope)
  if transport.pin.role!='vanilla'or transport.pin.display!=':154':raise ValueError('exact own Original transport required')
  directory=Path(evidence)/'passive-xrecord';directory.mkdir(mode=0o700,exist_ok=False)
  config={k:old_config[k]for k in('controller_root','arena','parent','roles')}
  config['passive']=dict(mode='a1',display=':154',display_owner=scope['current_display_owner'],original_window=transport.pin.window,controller_gc=controller_gc(transport),evidence=str(directory))
  config_path=directory/'config.json';private_json(config_path,config)
  root=Path(__file__).resolve().parent
  kid=OwnChild(['/usr/bin/python3','-E','-s','-B',str(root/'a1_passive_xrecord_worker.py'),'--config',str(config_path),'--display',':154'],directory,':154',ttl=15,role='recorder')
  return cls(kid,directory,transport)
 def arm(self):
  try:
   self.arm_receipt=self.kid.call('arm',timeout=3)['value']
   if self.arm_receipt.get('start_count')!=1:raise ValueError('passive StartOfData absent')
   self.arm_receipt['forward_keycode']=int(self.transport.keys['forward'])
   self.transport._passive_xrecord_proxy.observer=self
   return self.arm_receipt
  except BaseException:self.failed=True;raise
 def before_input(self):
  if self.failed or self.closed or self.arm_receipt is None:raise RuntimeError('passive observer unavailable/sticky failure')
  try:return self.kid.call('check',timeout=.1)['value']
  except BaseException:self.failed=True;raise
 def record_emission(self,row):
  if self.failed or self.closed or len(self.emissions)>=96:raise RuntimeError('bounded/sticky passive emission trace')
  row=dict(row,index=len(self.emissions));a,b=row['sequence_interval']
  if type(a)is not int or type(b)is not int or not 0<a<=b<=0xffffffff or (a==b and not row.get('error'))or b-a>4 or row['finished_monotonic']<row['started_monotonic']:raise ValueError('actual emission counter/clock interval invalid')
  self.emissions.append(row)
 def close(self,phases):
  if self.closed:return self.final
  self.closed=True;self.transport._passive_xrecord_proxy.observer=None
  errors=[]
  try:private_json(self.directory/'controller-emissions.json',self.emissions)
  except BaseException as error:errors.append('emission receipt:'+repr(error))
  child=self.kid.cleanup(stop_timeout=3)
  errors.extend(child['errors'])
  native=None
  try:
   path=self.directory/'recorder-native-close.json'
   if path.stat().st_size>16384:raise ValueError('native close bound')
   native=json.loads(path.read_text());errors.extend(native.get('errors',[]))
   if native.get('cleanup_errors'):errors.extend(native['cleanup_errors'])
  except BaseException as error:errors.append('native receipt:'+repr(error))
  evidence=None
  try:
   from a1_passive_xrecord_evidence import audit_trace
   evidence=audit_trace(self.directory,self.emissions,self.arm_receipt,native,phases)
  except BaseException as error:errors.append('passive evidence:'+repr(error))
  clean=not self.failed and not errors and child['closed']and child['reaped']and not child['forced']and child['exit_code']==0
  self.final=dict(status='PASS_PASSIVE_XRECORD_DIAGNOSTIC_ONLY'if clean else'FAIL_PASSIVE_XRECORD_DIAGNOSTIC',qualified=False,a1_pass=False,gain_fixed=False,child=child,native=native,evidence=evidence,errors=errors)
  return self.final
