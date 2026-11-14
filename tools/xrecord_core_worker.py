"""Disabled fresh-exec driver/recorder. Every X call stays inside this child."""
import ctypes as C
import hashlib
import json
import os
from pathlib import Path
import select
import resource
import signal
import sys
import time
from xrecord_core_native import Native, RecordSink, CALLBACK, RecordRange, selected_ranges

RUNTIME_REVIEWED=False
DISPLAY=':167'

class Driver:
 def __init__(self,native):self.n=native;self.d=None;self.window=0;self.root=0;self.stage=0;self.closed=False
 def initialize(self):
  if self.stage or self.d:raise ValueError('driver initialization repeated')
  self.d=self.n.open();self.root=int(self.n.x.XDefaultRootWindow(self.d))
  self.window=int(self.n.x.XCreateSimpleWindow(self.d,self.root,0,0,800,600,0,0,0))
  if not self.window:raise ValueError('own window absent')
  self.n.x.XSelectInput(self.d,self.window,1<<6);self.n.x.XMapWindow(self.d,self.window);self.n.x.XSync(self.d,0)
  self.n.x.XWarpPointer(self.d,0,self.root,0,0,0,0,400,300);self.n.x.XSync(self.d,0)
  actual=self.n.query(self.d,self.window)
  if actual['position']!=[400,300]or actual['root']!=self.root:raise ValueError('driver initial position')
  self.stage=1;return actual
 def relative(self):
  if self.stage!=1:raise ValueError('fixed relative sequence')
  self.stage=2
  if not self.n.t.XTestFakeRelativeMotionEvent(self.d,12,0,0):raise ValueError('relative request rejected')
  self.n.x.XSync(self.d,0);actual=self.n.query(self.d,self.window)
  if actual['position']!=[412,300]or actual['root']!=self.root:raise ValueError('relative actual position')
  return actual
 def warp(self):
  if self.stage!=2:raise ValueError('fixed warp sequence')
  self.stage=3;self.n.x.XWarpPointer(self.d,0,self.root,0,0,0,0,400,300);self.n.x.XSync(self.d,0);actual=self.n.query(self.d,self.window)
  if actual['position']!=[400,300]or actual['root']!=self.root:raise ValueError('warp actual position')
  return actual
 def close(self):
  destroyed=not self.window;closed=not self.d
  if self.closed:return self.final
  errors=[]
  if self.d:
   try:
    if self.window:self.n.x.XDestroyWindow(self.d,self.window);self.n.x.XSync(self.d,0);self.n.check();destroyed=True;self.window=0
   except BaseException as error:errors.append(repr(error))
   try:self.n.x.XCloseDisplay(self.d);self.d=None;closed=True;self.n.check()
   except BaseException as error:errors.append(repr(error))
  self.closed=True;self.final=dict(window_destroyed=destroyed,connections_closed=closed,errors=errors);return self.final


class Recorder:
 def __init__(self,native,directory):
  self.n=native;self.directory=Path(directory);self.control=None;self.data=None;self.context=0;self.sink=None;self.cb=None;self.closed=False;self.versions={};self.armed=False
 def arm(self):
  if self.control or self.armed:raise ValueError('arm repeated')
  self.control=self.n.open();self.data=self.n.open();self.versions=self.n.versions(self.control)
  self.ranges=selected_ranges(self.versions['xtest_opcode']);allocated=[]
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
  self.armed=True;return dict(**self.versions,**self.sink.receipt(),ranges_verified=True)
 def pump(self,seconds):
  # ProcessReplies invokes XPending and drains already-buffered replies as well.
  self.n.t.XRecordProcessReplies(self.data);self.n.check()
  if self.sink.errors:raise ValueError('record callback failed:'+repr(self.sink.errors))
  if seconds>0 and select.select([self.n.x.XConnectionNumber(self.data)],[],[],seconds)[0]:self.n.t.XRecordProcessReplies(self.data);self.n.check()
  if self.sink.errors:raise ValueError('record callback failed:'+repr(self.sink.errors))
 def await_evidence(self,target):
  if not self.armed or type(target)is not int or target not in(1,2):raise ValueError('fixed observation target')
  deadline=time.monotonic()+1.5
  while True:
   self.pump(0)
   rows=[json.loads(s)for s in(self.directory/'record-raw.jsonl').read_bytes().splitlines()]
   wanted=['xtest_relative_motion','query_pointer_request','query_pointer_reply','device_motion','delivered_motion']
   if target==2:wanted+=['warp_request']
   counts={k:sum(r['kind']==k for r in rows)for k in wanted}
   if all(counts[k]>=(target if k in('query_pointer_request','query_pointer_reply','device_motion','delivered_motion')else 1)for k in wanted):return dict(**self.sink.receipt(),target=target)
   left=deadline-time.monotonic()
   if left<=0:raise TimeoutError('method evidence missing')
   self.pump(min(left,.02))
 def close(self):
  if self.closed:return self.final
  errors=[];context_freed=not self.context;connections_closed=True;end=False
  try:
   if self.context and self.armed:
    try:self.n.context_state(self.control,self.context,self.ranges,enabled=True)
    except BaseException as error:errors.append('final context state:'+repr(error))
    try:
     if not self.n.t.XRecordDisableContext(self.control,self.context):raise ValueError('disable failed')
     self.n.x.XSync(self.control,0);deadline=time.monotonic()+2.
     while self.sink.ends==0:
      if time.monotonic()>=deadline:raise TimeoutError('record EndOfData missing')
      self.pump(min(.02,max(0.,deadline-time.monotonic())))
     end=self.sink.ends==1;self.armed=False
    except BaseException as error:errors.append('disable/end:'+repr(error))
   if self.context:
    try:
     if not self.n.t.XRecordFreeContext(self.control,self.context):raise ValueError('FreeContext rejected')
     self.n.x.XSync(self.control,0);self.n.check();context_freed=True;self.context=0
    except BaseException as error:errors.append('context:'+repr(error))
  finally:
   # A native hang is bounded by the independent parent's stop/cleanup deadline.
   for name in('data','control'):
    d=getattr(self,name)
    if d:
     try:self.n.x.XCloseDisplay(d);setattr(self,name,None)
     except BaseException as error:connections_closed=False;errors.append(name+':'+repr(error))
   try:self.n.check()
   except BaseException as error:errors.append('native error:'+repr(error))
   if self.sink:self.sink.close();errors+=self.sink.errors
  self.closed=True;receipt={}if self.sink is None else self.sink.receipt()
  self.final=dict(**receipt,**self.versions,context_freed=context_freed,connections_closed=connections_closed,end_verified=end,cleanup_errors=errors)
  return self.final


def private_json(path,value):
 with os.fdopen(os.open(path,os.O_WRONLY|os.O_CREAT|os.O_EXCL,0o600),'w')as f:json.dump(value,f,allow_nan=False)


def run_worker(role,directory,display):
 if not RUNTIME_REVIEWED:raise RuntimeError('disabled XRecord worker; Root freeze required')
 if display!=DISPLAY or os.environ.get('DISPLAY')!=DISPLAY or role not in('driver','recorder'):raise ValueError('fixed own worker binding')
 directory=Path(directory).resolve()
 if Path.cwd()!=directory:raise ValueError('own worker CWD')
 resource.setrlimit(resource.RLIMIT_FSIZE,(2097152,2097152))
 signal.setitimer(signal.ITIMER_REAL,15 if role=='recorder' else 30)
 obj=None;errors=[]
 try:
  obj=Driver(Native())if role=='driver'else Recorder(Native(),directory)
  expected=0
  while True:
   line=sys.stdin.buffer.readline(16385)
   if not line:break
   if len(line)>16384:raise ValueError('worker IPC line bound')
   request=json.loads(line);expected+=1
   if type(request.get('id'))is not int or request.get('id')!=expected:raise ValueError('worker request order')
   command=request.get('command')
   if command=='stop':value=obj.close()
   elif role=='driver'and command in('initialize','relative','warp'):value=getattr(obj,command)()
   elif role=='recorder'and command=='arm':value=obj.arm()
   elif role=='recorder'and command=='observe':value=obj.await_evidence(request.get('target'))
   else:raise ValueError('method command allowlist')
   reply=json.dumps(dict(id=expected,ok=True,value=value),allow_nan=False)
   if len(reply.encode())>16383:raise ValueError('worker reply bound')
   print(reply,flush=True)
   if command=='stop':break
 except BaseException as error:
  errors.append(type(error).__name__+':'+str(error)[:1024])
  print(json.dumps(dict(id=locals().get('expected',0),ok=False,error=errors[-1])),flush=True)
 finally:
  closed=None
  if obj is not None:
   try:closed=obj.close()
   except BaseException as error:errors.append('final close:'+repr(error))
  private_json(directory/(role+'-native-close.json'),dict(errors=errors,native=closed))
 return 1 if errors else 0

if __name__=='__main__':
 import argparse
 p=argparse.ArgumentParser();p.add_argument('--role',choices=['driver','recorder'],required=True);p.add_argument('--directory',required=True);p.add_argument('--display',required=True);a=p.parse_args()
 sys.exit(run_worker(a.role,a.directory,a.display))
