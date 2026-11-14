"""DISABLED own167 exec worker; public metadata only, no input APIs."""
import ctypes as C
import hashlib
import json
import os
from pathlib import Path
import resource
import signal
import sys
import time
from xres_pid_method import require,uint,valid_version

RUNTIME_REVIEWED=False
D=C.c_void_p;U=C.c_ulong;I=C.c_int;P=C.POINTER


class Client(C.Structure):_fields_=[('resource_base',U),('resource_mask',U)]
class Spec(C.Structure):_fields_=[('client',U),('mask',C.c_uint)]
class Value(C.Structure):_fields_=[('spec',Spec),('length',C.c_long),('value',D)]


def abi_layout():
 return dict(XID=C.sizeof(U),long=C.sizeof(C.c_long),pid_t=C.sizeof(I),CARD32=C.sizeof(C.c_uint32),Client=dict(size=C.sizeof(Client),base=Client.resource_base.offset,mask=Client.resource_mask.offset),Spec=dict(size=C.sizeof(Spec),client=Spec.client.offset,mask=Spec.mask.offset),Value=dict(size=C.sizeof(Value),spec=Value.spec.offset,length=Value.length.offset,value=Value.value.offset),pid_mask=2,Success=0)


class Native:
 def __init__(self):
  if not RUNTIME_REVIEWED:raise RuntimeError('disabled XRes native worker')
  root=Path(__file__).resolve().parent;m=json.loads((root/'source-manifest.json').read_text())
  require(m.get('runtime_enabled')is True,'disabled XRes manifest')
  require(sys.byteorder=='little'and abi_layout()==m['abi_layout'],'unqualified XRes header ABI')
  for path,h in m['library_sha256'].items():require(hashlib.sha256(Path(path).read_bytes()).hexdigest()==h,'XRes library pin changed')
  self.x=C.CDLL('/lib/x86_64-linux-gnu/libX11.so.6');self.r=C.CDLL('/lib/x86_64-linux-gnu/libXRes.so.1');self.errors=[];self.total_free_counts={};self.restored=False
  def bind(lib,name,args,ret=I):fn=getattr(lib,name);fn.argtypes=args;fn.restype=ret
  for name,args,ret in(('XOpenDisplay',[C.c_char_p],D),('XCloseDisplay',[D],I),('XDefaultRootWindow',[D],U),('XCreateSimpleWindow',[D,U,I,I,C.c_uint,C.c_uint,C.c_uint,U,U],U),('XDestroyWindow',[D,U],I),('XSync',[D,I],I),('XFree',[D],I),('XSetErrorHandler',[D],D)):bind(self.x,name,args,ret)
  for name,args,ret in(('XResQueryExtension',[D,P(I),P(I)],I),('XResQueryVersion',[D,P(I),P(I)],I),('XResQueryClients',[D,P(I),P(P(Client))],I),('XResQueryClientIds',[D,C.c_long,P(Spec),P(C.c_long),P(P(Value))],I),('XResGetClientPid',[P(Value)],I),('XResClientIdsDestroy',[C.c_long,P(Value)],None)):bind(self.r,name,args,ret)
  self.error_callback=C.CFUNCTYPE(I,D,D)(self._xerror)
  self.previous_handler=self.x.XSetErrorHandler(C.cast(self.error_callback,D))
 def _xerror(self,display,event):
  try:
   if len(self.errors)<8:self.errors.append('native X error')
  except BaseException:pass
  return 0
 def check(self):
  if self.errors:raise ValueError(';'.join(self.errors))
 def open(self):
  d=self.x.XOpenDisplay(b':167')
  if not d:raise ValueError('own display167 unavailable')
  self.check();return d
 def versions(self,d):
  event=I();error=I();major=I();minor=I()
  require(self.r.XResQueryExtension(d,C.byref(event),C.byref(error))==1,'X-Resource extension unavailable')
  require(self.r.XResQueryVersion(d,C.byref(major),C.byref(minor))==1,'XRes version query failed')
  version=[major.value,minor.value];require(valid_version(version),'XRes protocol1.2 unavailable');self.check();return version
 def _charge(self,counts,key):
  counts[key]+=1;self.total_free_counts[key]=self.total_free_counts.get(key,0)+1
 def _id(self,d,kind,xid,counts):
  spec=Spec(xid,2);num=C.c_long();values=P(Value)();primary=None
  try:
   status=self.r.XResQueryClientIds(d,1,C.byref(spec),C.byref(num),C.byref(values))
   if values:self._charge(counts,'id_arrays_allocated')
   require(status==0 and num.value==1 and bool(values),'PID missing/unknown, bad count or QueryClientIds status')
   v=values[0];require(v.spec.mask==2 and v.length==4 and bool(v.value),'invalid PID mask/length/payload')
   pid=int(self.r.XResGetClientPid(C.pointer(v)));require(0<pid<=0x7fffffff,'PID unavailable');self.check()
   return dict(requested_kind=kind,requested_xid=xid,query_status=status,num_ids=num.value,ids=[dict(spec_client=int(v.spec.client),mask=int(v.spec.mask),length=int(v.length),pid=pid)])
  except BaseException as error:primary=error;raise
  finally:
   if values:
    try:
     require(0<=num.value<=64,'unbounded ID array cannot be safely traversed; owned worker must exit')
     self.r.XResClientIdsDestroy(num.value,values);self._charge(counts,'id_arrays_freed')
    except BaseException as error:
     self.errors.append('ID array cleanup:'+repr(error))
     if primary is None:raise
 def snapshot(self,d,resources,version):
  require(isinstance(resources,list)and len(resources)==3 and len(set(resources))==3,'exact three resources')
  for xid in resources:require(uint(xid)>3,'positive resource required')
  counts=dict(client_arrays_allocated=0,client_arrays_freed=0,id_arrays_allocated=0,id_arrays_freed=0)
  num=I();pointer=P(Client)();primary=None
  try:
   status=self.r.XResQueryClients(d,C.byref(num),C.byref(pointer))
   if pointer:self._charge(counts,'client_arrays_allocated')
   require(status==1 and 1<=num.value<=64 and bool(pointer),'bounded QueryClients array/status required')
   clients=[dict(resource_base=int(pointer[i].resource_base),resource_mask=int(pointer[i].resource_mask))for i in range(num.value)];self.check()
  except BaseException as error:primary=error;raise
  finally:
   if pointer:
    try:self.x.XFree(pointer);self._charge(counts,'client_arrays_freed')
    except BaseException as error:
     self.errors.append('client array cleanup:'+repr(error))
     if primary is None:raise
  results=[]
  for xid in resources:
   matches=[v for v in clients if xid&(~v['resource_mask']&0xffffffff)==v['resource_base']]
   require(len(matches)==1,'resource range missing/ambiguous')
   results.append(self._id(d,'resource',xid,counts));results.append(self._id(d,'base',matches[0]['resource_base'],counts))
  return dict(xres_version=version,query_clients_status=status,clients=clients,results=results,errors=list(self.errors),free_counts=counts)
 def close(self):
  if not self.restored:
   self.x.XSetErrorHandler(self.previous_handler);self.restored=True
  return dict(error_handler_restored=self.restored,errors=list(self.errors))


class Resources:
 def __init__(self,native,count):self.n=native;self.count=count;self.connections=[];self.windows=[];self.initialized=False;self.closed=False
 def initialize(self):
  require(not self.initialized and not self.connections,'initialize once')
  for _ in range(self.count):
   d=self.n.open();self.connections.append(d);self.windows.append(0)
   root=int(self.n.x.XDefaultRootWindow(d));window=int(self.n.x.XCreateSimpleWindow(d,root,0,0,1,1,0,0,0));self.windows[-1]=window
   require(uint(window)>3,'own unmapped window missing');require(self.n.x.XSync(d,0)==1,'window metadata sync failed');self.n.check()
  self.initialized=True;return dict(resources=list(self.windows),connections=len(self.connections),mapped=False,inputs_emitted=0)
 def close(self):
  if self.closed:return self.final
  errors=[];destroyed=0;closed=0
  for d,window in zip(self.connections,self.windows):
   try:
    if window:self.n.x.XDestroyWindow(d,window);self.n.x.XSync(d,0);self.n.check();destroyed+=1
   except BaseException as error:errors.append('window close:'+repr(error))
   try:self.n.x.XCloseDisplay(d);closed+=1
   except BaseException as error:errors.append('connection close:'+repr(error))
  self.closed=True;self.final=dict(windows_created=len(self.windows),windows_destroyed=destroyed,connections_created=len(self.connections),connections_closed=closed==len(self.connections),inputs_emitted=0,errors=errors);return self.final


class Attributor:
 def __init__(self,native):self.n=native;self.d=None;self.version=None;self.snapshots=0;self.closed=False
 def initialize(self):
  require(self.d is None,'initialize once');self.d=self.n.open();self.version=self.n.versions(self.d);return dict(xres_version=self.version)
 def snapshot(self,resources):
  require(self.d is not None and self.version is not None and self.snapshots<2,'two initialized metadata snapshots only')
  index=self.snapshots;self.snapshots+=1;started=time.monotonic()
  row=self.n.snapshot(self.d,resources,self.version);row.update(index=index,monotonic_started=started,monotonic_finished=time.monotonic());return row
 def close(self):
  if self.closed:return self.final
  errors=[];closed=self.d is None
  if self.d is not None:
   try:self.n.x.XCloseDisplay(self.d);self.d=None;closed=True
   except BaseException as error:errors.append('metadata close:'+repr(error))
  self.closed=True;self.final=dict(connections_closed=closed,snapshots=self.snapshots,free_counts=dict(self.n.total_free_counts),inputs_emitted=0,errors=errors);return self.final


def private_json(path,value):
 with os.fdopen(os.open(path,os.O_WRONLY|os.O_CREAT|os.O_EXCL,0o600),'w')as f:json.dump(value,f,allow_nan=False)


def run_worker(role,directory,display):
 if not RUNTIME_REVIEWED:raise RuntimeError('disabled XRes worker')
 require(display==':167'and os.environ.get('DISPLAY')==':167'and role in('driver','peer','attributor'),'fixed own XRes worker binding')
 directory=Path(directory).resolve();require(Path.cwd()==directory,'own worker CWD')
 resource.setrlimit(resource.RLIMIT_FSIZE,(2097152,2097152));signal.setitimer(signal.ITIMER_REAL,15 if role=='attributor'else 30)
 native=None;obj=None;errors=[];expected=0
 try:
  native=Native();obj=Attributor(native)if role=='attributor'else Resources(native,2 if role=='driver'else 1)
  while True:
   line=sys.stdin.buffer.readline(16385)
   if not line:break
   require(len(line)<=16384,'worker IPC line bound');request=json.loads(line);expected+=1
   require(type(request.get('id'))is int and request['id']==expected,'worker request order')
   command=request.get('command')
   if command=='stop':value=obj.close()
   elif command=='initialize':value=obj.initialize()
   elif role=='attributor'and command=='snapshot':value=obj.snapshot(request.get('resources'))
   else:raise ValueError('metadata-only command allowlist')
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
 p=argparse.ArgumentParser();p.add_argument('--role',choices=['driver','peer','attributor'],required=True);p.add_argument('--directory',required=True);p.add_argument('--display',required=True);a=p.parse_args();sys.exit(run_worker(a.role,a.directory,a.display))
