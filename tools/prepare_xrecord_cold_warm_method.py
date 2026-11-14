"""Prepare fresh DISABLED method fork; immutable qualified parent untouched."""
import argparse
import ast
import difflib
import hashlib
import json
import os
from pathlib import Path

PARENT=Path('/srv/tse-own-xrecord-core-method-root-frozen-20261114')
PARENT_SHA='43d38e727666d171bc9c6d021d4af018c60fe0279583c6636949d246e0f549ec'
SOURCE=Path(__file__).resolve().parent
CORE=('xrecord_core_method.py','xrecord_core_process.py','xrecord_core_controller.py','xrecord_core_native.py','xrecord_core_worker.py')
ADDED=('xrecord_cold_warm_method.py','prepare_xrecord_cold_warm_method.py','test_xrecord_cold_warm_method.py')
LIBRARIES={'/lib/x86_64-linux-gnu/libX11.so.6':'edd2ddf6e00a81c40b8645f7dbb6d6603c6a0a78d583bdbe7491d8a84de6e3b6','/lib/x86_64-linux-gnu/libXtst.so.6':'a29f93b5c3eb10744ae503dbc9280f9e709061b9b8529f604e961fb77e4f2b70','/lib/x86_64-linux-gnu/libXext.so.6':'2907e6a996465de5b32a0dd10534d4416b87f1dee5670aaa7b19301a1fc93f44'}
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()


def once(text,old,new):
 if text.count(old)!=1:raise ValueError('exact single anchor required: '+old)
 return text.replace(old,new,1)


def replace_function(text,name,body):
 nodes=[n for n in ast.walk(ast.parse(text))if isinstance(n,ast.FunctionDef)and n.name==name]
 if len(nodes)!=1:raise ValueError('unique function required: '+name)
 n=nodes[0];lines=text.splitlines(True);lines[n.lineno-1:n.end_lineno]=[body+'\n'];answer=''.join(lines);ast.parse(answer);return answer


def transform_native(text):
 text=once(text,'RUNTIME_REVIEWED=True','RUNTIME_REVIEWED=False')
 text=once(text," '/lib/x86_64-linux-gnu/libXtst.so.6':'a29f93b5c3eb10744ae503dbc9280f9e709061b9b8529f604e961fb77e4f2b70'}"," '/lib/x86_64-linux-gnu/libXtst.so.6':'a29f93b5c3eb10744ae503dbc9280f9e709061b9b8529f604e961fb77e4f2b70',\n '/lib/x86_64-linux-gnu/libXext.so.6':'2907e6a996465de5b32a0dd10534d4416b87f1dee5670aaa7b19301a1fc93f44'}")
 text=once(text,'from xrecord_core_method import RecordRange, Intercept, CoreTrace, CaptureBudget, copy_payload, native_layout','from xrecord_core_method import RecordRange, Intercept, CoreTrace, CaptureBudget, copy_payload, native_layout\nfrom xrecord_cold_warm_method import MethodTrace, method_ranges')
 text=once(text,'def __init__(self,xtst,path,opcode,*,started,clock=time.monotonic):','def __init__(self,xtst,path,opcode,*,ge_opcode,started,clock=time.monotonic):')
 text=once(text,'self.trace=CoreTrace(xtest_opcode=opcode)','self.trace=MethodTrace(xtest_opcode=opcode,ge_opcode=ge_opcode)')
 text=once(text,"  selected_ranges(opcode.value);self.check();return dict(record_version=[rm.value,rn.value],xtest_version=[tm.value,tn.value],xtest_opcode=opcode.value)","  ge=I();ge_event=I();ge_error=I()\n  if not self.x.XQueryExtension(d,b'Generic Event Extension',C.byref(ge),C.byref(ge_event),C.byref(ge_error)):raise ValueError('GE extension unavailable')\n  method_ranges(opcode.value,ge.value);self.check();return dict(record_version=[rm.value,rn.value],xtest_version=[tm.value,tn.value],xtest_opcode=opcode.value,ge_opcode=ge.value)")
 text=once(text,'if not 1<=info.nranges<=4 or not info.ranges:','if not 1<=info.nranges<=6 or not info.ranges:')
 ast.parse(text);return text


def transform_worker(text):
 text=once(text,'RUNTIME_REVIEWED=True','RUNTIME_REVIEWED=False')
 text=once(text,'class Driver:', 'from xrecord_cold_warm_method import method_ranges\n\nclass Driver:')
 text=once(text,'self.root=0;self.stage=0;self.closed=False','self.root=0;self.stage=0;self.closed=False;self.attempts=[]')
 text=replace_function(text,'relative',""" def relative(self):
  if self.stage not in(1,2):raise ValueError('exactly two fixed relative calls')
  self.stage+=1
  attempt=dict(function='XTestFakeRelativeMotionEvent',arguments=[self.d,12,0,0],return_value=None,native_invoked=False)
  self.attempts.append(attempt);attempt['started_monotonic']=time.monotonic()
  first=int(self.n.x.XNextRequest(self.d));attempt['sequence_before']=first;primary=None;attempt['native_invoked']=True
  try:attempt['return_value']=self.n.t.XTestFakeRelativeMotionEvent(self.d,12,0,0)
  except BaseException as error:primary=error;attempt['native_error']=repr(error);raise
  finally:
   try:
    after=int(self.n.x.XNextRequest(self.d));attempt['sequence_after']=after;attempt['sequence_interval']=[first,after];attempt['finished_monotonic']=time.monotonic()
   except BaseException as error:
    attempt['metadata_error']=repr(error)
    if primary is None:raise
  if not attempt['return_value']:raise ValueError('relative request rejected')
  self.n.x.XSync(self.d,0);actual=self.n.query(self.d,self.window)
  wanted=[412 if self.stage==2 else 424,300]
  if actual['position']!=wanted or actual['root']!=self.root:raise ValueError('relative actual position')
  actual['attempt']=attempt;return actual""")
 text=once(text,"self.final=dict(window_destroyed=destroyed,connections_closed=closed,errors=errors)","self.final=dict(window_destroyed=destroyed,connections_closed=closed,errors=errors,attempts=self.attempts)")
 text=once(text,"self.ranges=selected_ranges(self.versions['xtest_opcode'])","self.ranges=method_ranges(self.versions['xtest_opcode'],self.versions['ge_opcode'])")
 text=once(text,'pointers=(C.POINTER(RecordRange)*4)(*allocated);clients=(C.c_ulong*1)(3)','pointers=(C.POINTER(RecordRange)*6)(*allocated);clients=(C.c_ulong*1)(3)')
 text=once(text,'XRecordCreateContext(self.control,7,clients,1,pointers,4)','XRecordCreateContext(self.control,7,clients,1,pointers,6)')
 text=once(text,"RecordSink(self.n.t,self.directory/'record-raw.jsonl',self.versions['xtest_opcode'],started=time.monotonic())","RecordSink(self.n.t,self.directory/'record-raw.jsonl',self.versions['xtest_opcode'],ge_opcode=self.versions['ge_opcode'],started=time.monotonic())")
 text=once(text,"   if target==2:wanted+=['warp_request']\n",'')
 text=once(text,"(target if k in('query_pointer_request','query_pointer_reply','device_motion','delivered_motion')else 1)",'target ')
 text=once(text,"command in('initialize','relative','warp')","command in('initialize','relative')")
 ast.parse(text);return text


def transform_controller(text):
 text=once(text,'RUNTIME_REVIEWED=True','RUNTIME_REVIEWED=False')
 text=replace_function(text,'bind_trace',"""def bind_trace(rows,driver):
 from xrecord_cold_warm_method import bind_trace as audit
 return audit(rows,driver)""")
 text=replace_function(text,'method_verdict',"""def method_verdict(row):
 from xrecord_cold_warm_method import method_verdict as verdict
 return verdict(row)""")
 text=once(text,"'OWN_CORE_XRECORD_METHOD_V1'","'OWN_COLD_WARM_XRECORD_METHOD_V1'")
 text=once(text,"'xrecord_core_worker.py'}.issubset","'xrecord_core_worker.py','xrecord_cold_warm_method.py'}.issubset")
 text=once(text,"driver_queries.append(call('driver','relative',2));call('recorder','observe',2,target=1)","driver_queries.append(call('driver','relative',2));call('recorder','observe',2,target=1)\n  a,b=driver_queries[-1]['attempt']['sequence_interval']\n  if b-a!=5:raise ValueError('first actual counter must prove cold5')")
 text=once(text,"driver_queries.append(call('driver','warp',2));call('recorder','observe',2,target=2)","driver_queries.append(call('driver','relative',2));call('recorder','observe',2,target=2)\n  a,b=driver_queries[-1]['attempt']['sequence_interval']\n  if b-a!=1:raise ValueError('second actual counter must prove warm1')")
 text=once(text,"if rn.get('records')!=len(rows):raise ValueError('native raw record coverage differs')","if rn.get('records')!=len(rows):raise ValueError('native raw record coverage differs')\n  if dn.get('attempts')!=[q['attempt']for q in driver_queries]:raise ValueError('closed driver attempts differ from actual IPC receipts')")
 ast.parse(text);return text


def prepare(destination):
 dest=Path(destination).resolve()
 if dest.exists():raise ValueError('fresh disabled method destination required')
 if sha(PARENT/'source-manifest.json')!=PARENT_SHA:raise ValueError('qualified parent manifest changed')
 parent=json.loads((PARENT/'source-manifest.json').read_text())
 for path,h in LIBRARIES.items():
  if sha(path)!=h:raise ValueError('method library changed: '+path)
 for name,h in parent['files'].items():
  if sha(PARENT/name)!=h:raise ValueError('qualified parent source changed: '+name)
 data={name:(PARENT/name).read_bytes()for name in CORE}
 for name,transform in [('xrecord_core_native.py',transform_native),('xrecord_core_worker.py',transform_worker),('xrecord_core_controller.py',transform_controller)]:data[name]=transform(data[name].decode()).encode()
 for name in ADDED:data[name]=(SOURCE/name).read_bytes()
 dest.mkdir(mode=0o700);pins={}
 for name,raw in data.items():
  with os.fdopen(os.open(dest/name,os.O_WRONLY|os.O_CREAT|os.O_EXCL,0o600),'wb')as f:f.write(raw)
  pins[name]=hashlib.sha256(raw).hexdigest()
 m=dict(schema='OWN_COLD_WARM_XRECORD_METHOD_V1',runtime_enabled=False,parent_manifest_sha256=PARENT_SHA,files=pins,limits=parent['limits'],program=dict(calls=2,dx=12,dy=0,display=':167',driver_warmup=False),claims=dict(retail_qualified=False,xi2_complete=False,a1_pass=False,method_native_executed=False),original_parent_unchanged=True,header_sha256=dict(Xproto_h='ae2c275f8b7bf4705ef993b50a34ce7418fbbc4789bcb841237116b7c0271c82',geproto_h='b831b2d821249670d8ed60a05f9f0dd85caa2c2ef101dbb6989bca5ea7ad02f1'))
 m['library_sha256']=LIBRARIES
 with os.fdopen(os.open(dest/'source-manifest.json',os.O_WRONLY|os.O_CREAT|os.O_EXCL,0o600),'w')as f:json.dump(m,f,sort_keys=True,indent=2);f.write('\n')
 diff=''.join(''.join(difflib.unified_diff((PARENT/name).read_text().splitlines(True),data[name].decode().splitlines(True),fromfile='qualified-parent/'+name,tofile='disabled-cold-warm/'+name))for name in CORE if data[name]!=(PARENT/name).read_bytes())
 with os.fdopen(os.open(dest/'method-fork.diff',os.O_WRONLY|os.O_CREAT|os.O_EXCL,0o600),'w')as f:f.write(diff)
 return m


if __name__=='__main__':
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--destination',type=Path,required=True);args=p.parse_args();m=prepare(args.destination);print(json.dumps(dict(package=str(args.destination),manifest_sha256=sha(args.destination/'source-manifest.json'),pins=len(m['files']),runtime_enabled=m['runtime_enabled'])))
