"""Disabled LP64 bindings for public Xorg APIs, loaded only in fresh workers.

ABI: libXtst1.2.3 record.h / libX11-1.8.7 Xlib.h. No private Display layout.
"""
import ctypes as C
import hashlib
import json
import os
from pathlib import Path
import sys
import time
from xrecord_core_method import RecordRange, Intercept, CoreTrace, CaptureBudget, copy_payload, native_layout

RUNTIME_REVIEWED=False
LIBRARIES={
 '/lib/x86_64-linux-gnu/libX11.so.6':'edd2ddf6e00a81c40b8645f7dbb6d6603c6a0a78d583bdbe7491d8a84de6e3b6',
 '/lib/x86_64-linux-gnu/libXtst.so.6':'a29f93b5c3eb10744ae503dbc9280f9e709061b9b8529f604e961fb77e4f2b70'}
D=C.c_void_p;U=C.c_ulong;I=C.c_int;P=C.POINTER
CALLBACK=C.CFUNCTYPE(None,D,P(Intercept))
class RecordClientInfo(C.Structure):_fields_=[('client',U),('nranges',U),('ranges',P(P(RecordRange)))]
class RecordState(C.Structure):_fields_=[('enabled',I),('datum_flags',I),('nclients',U),('client_info',P(P(RecordClientInfo)))]


def range_signature(r):
 out=[]
 for name in('core_requests','core_replies','ext_requests','ext_replies','delivered_events','device_events','errors'):
  a=getattr(r,name)
  if name.startswith('ext_'):out.extend((a.ext_major.first,a.ext_major.last,a.ext_minor.first,a.ext_minor.last))
  else:out.extend((a.first,a.last))
 return out+[r.client_started,r.client_died]


def selected_ranges(opcode):
 if type(opcode)is not int or not 128<=opcode<=255:raise ValueError('dynamic extension major')
 rows=[RecordRange()for _ in range(4)]
 rows[0].core_requests.first=rows[0].core_requests.last=38;rows[0].core_replies.first=rows[0].core_replies.last=38
 rows[1].core_requests.first=rows[1].core_requests.last=41
 rows[2].ext_requests.ext_major.first=rows[2].ext_requests.ext_major.last=opcode
 rows[2].ext_requests.ext_minor.first=rows[2].ext_requests.ext_minor.last=2
 rows[3].device_events.first=rows[3].device_events.last=6;rows[3].delivered_events.first=rows[3].delivered_events.last=6
 return rows


def range_coverage(ranges):
 """Exact protocol union; GetContext repacks fields, not original rows.

 Extension coverage is restricted to this method's fixed single major/minor
 point. No alternative extension span is accepted or silently enumerated.
 """
 result={}
 for name in('core_requests','core_replies','delivered_events','device_events','errors'):
  intervals=[]
  for row in ranges:
   r=getattr(row,name);a,b=int(r.first),int(r.last)
   if(a,b)==(0,0):continue
   if not 1<=a<=b<=255:raise ValueError('invalid protocol interval')
   intervals.append((a,b))
  merged=[]
  for a,b in sorted(intervals):
   if merged and a<=merged[-1][1]+1:merged[-1]=(merged[-1][0],max(b,merged[-1][1]))
   else:merged.append((a,b))
  result[name]=tuple(merged)
 for name in('ext_requests','ext_replies'):
  points=set()
  for row in ranges:
   r=getattr(row,name);a,b=int(r.ext_major.first),int(r.ext_major.last);c,d=int(r.ext_minor.first),int(r.ext_minor.last)
   if(a,b,c,d)==(0,0,0,0):continue
   if not 128<=a==b<=255 or c!=d:raise ValueError('method extension coverage differs')
   points.add((a,c))
  result[name]=tuple(sorted(points))
 for name in('client_started','client_died'):
  values=[getattr(row,name)for row in ranges]
  if any(v not in(0,1)for v in values):raise ValueError('invalid range Bool')
  result[name]=any(values)
 return result


class RecordSink:
 """Single-thread callback; bounded private stream, all C exceptions contained."""
 def __init__(self,xtst,path,opcode,*,started,clock=time.monotonic):
  self.xtst=xtst;self.trace=CoreTrace(xtest_opcode=opcode);self.clock=clock;self.budget=CaptureBudget(started=started)
  self.errors=[];self.calls=0;self.freed=0;self.malformed=0;self.starts=0;self.ends=0;self.closed=False
  self.file=os.fdopen(os.open(path,os.O_WRONLY|os.O_CREAT|os.O_EXCL,0o600),'wb',buffering=0)
 def callback(self,closure,pointer):
  self.calls+=1
  try:
   if self.errors:raise ValueError('sticky callback failure')
   if not pointer:raise ValueError('null callback structure')
   value=pointer.contents
   if value.client_swapped not in(0,1):raise ValueError('invalid native Bool')
   raw=copy_payload(data_pointer=value.data,data_len=int(value.data_len),reader=C.string_at)
   row=self.trace.accept(category=int(value.category),client_base=int(value.id_base),client_sequence=int(value.client_seq),server_time=int(value.server_time),client_swapped=bool(value.client_swapped),wire=raw)
   row.update(callback_serial=self.calls,received_monotonic=self.clock())
   wire=json.dumps(row,allow_nan=False,separators=(',',':')).encode()+b'\n'
   self.budget.charge(record_bytes=len(raw),serialized_bytes=len(wire),now=row['received_monotonic'])
   self.file.write(wire)
   self.starts+=row['kind']=='start';self.ends+=row['kind']=='end'
  except BaseException as error:
   if not self.budget.failed:self.malformed+=1
   if len(self.errors)<8:self.errors.append(type(error).__name__+':'+str(error))
  finally:
   try:
    if not pointer:raise ValueError('cannot free null callback data')
    self.xtst.XRecordFreeData(pointer);self.freed+=1
   except BaseException as error:
    if len(self.errors)<8:self.errors.append('FreeData:'+repr(error))
 def receipt(self):return dict(calls=self.calls,freed=self.freed,records=self.budget.records,bytes=self.budget.bytes,errors=list(self.errors),start_count=self.starts,end_count=self.ends,unknown_records=self.trace.unsupported,malformed=self.malformed,dropped=self.calls-self.budget.records,budget_failed=self.budget.failed)
 def close(self):
  if not self.closed:self.file.close();self.closed=True


class Native:
 def __init__(self):
  if not RUNTIME_REVIEWED:raise RuntimeError('disabled native bindings; Root freeze required')
  if sys.byteorder!='little' or native_layout()!=dict(pointer_bytes=8,intercept_size=48,range_size=32,wire_range_bytes=24,intercept_offsets=dict(id_base=0,server_time=8,client_seq=16,category=24,client_swapped=28,data=32,data_len=40)):raise ValueError('unqualified host ABI')
  for path,sha in LIBRARIES.items():
   if hashlib.sha256(Path(path).read_bytes()).hexdigest()!=sha:raise ValueError('library pin changed')
  self.x=C.CDLL(next(iter(LIBRARIES)));self.t=C.CDLL(list(LIBRARIES)[1]);self.errors=[]
  def bind(lib,name,args,ret=I):f=getattr(lib,name);f.argtypes=args;f.restype=ret
  for name,args,ret in(
   ('XOpenDisplay',[C.c_char_p],D),('XCloseDisplay',[D],I),('XDefaultRootWindow',[D],U),
   ('XCreateSimpleWindow',[D,U,I,I,C.c_uint,C.c_uint,C.c_uint,U,U],U),('XMapWindow',[D,U],I),('XDestroyWindow',[D,U],I),('XSelectInput',[D,U,C.c_long],I),
   ('XSync',[D,I],I),('XFlush',[D],I),('XConnectionNumber',[D],I),('XNextRequest',[D],U),
   ('XWarpPointer',[D,U,U,I,I,C.c_uint,C.c_uint,I,I],I),('XQueryPointer',[D,U,P(U),P(U),P(I),P(I),P(I),P(I),P(C.c_uint)],I),
   ('XQueryExtension',[D,C.c_char_p,P(I),P(I),P(I)],I),('XFree',[D],I)):
   bind(self.x,name,args,ret)
  for name,args,ret in(
   ('XTestQueryExtension',[D,P(I),P(I),P(I),P(I)],I),('XTestFakeRelativeMotionEvent',[D,I,I,U],I),
   ('XRecordAllocRange',[],P(RecordRange)),('XRecordQueryVersion',[D,P(I),P(I)],I),('XRecordCreateContext',[D,I,P(U),I,P(P(RecordRange)),I],U),
   ('XRecordGetContext',[D,U,P(P(RecordState))],I),('XRecordFreeState',[P(RecordState)],None),
   ('XRecordEnableContextAsync',[D,U,CALLBACK,D],I),('XRecordProcessReplies',[D],None),
   ('XRecordDisableContext',[D,U],I),('XRecordFreeContext',[D,U],I),('XRecordFreeData',[P(Intercept)],None)):
   bind(self.t,name,args,ret)
  # A handler belongs to this isolated single-thread worker only. No C exception.
  self.error_callback=C.CFUNCTYPE(I,D,D)(self._xerror)
  bind(self.x,'XSetErrorHandler',[type(self.error_callback)],D);self.x.XSetErrorHandler(self.error_callback)
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
  rm=I();rn=I();event=I();error=I();tm=I();tn=I();opcode=I();ev=I();er=I()
  if not self.t.XRecordQueryVersion(d,C.byref(rm),C.byref(rn))or not self.t.XTestQueryExtension(d,C.byref(event),C.byref(error),C.byref(tm),C.byref(tn))or not self.x.XQueryExtension(d,b'XTEST',C.byref(opcode),C.byref(ev),C.byref(er)):raise ValueError('extensions unavailable')
  if(rm.value,rn.value,tm.value,tn.value)!=(1,13,2,2):raise ValueError('unqualified extension versions')
  selected_ranges(opcode.value);self.check();return dict(record_version=[rm.value,rn.value],xtest_version=[tm.value,tn.value],xtest_opcode=opcode.value)
 def query(self,d,window):
  root=U();child=U();coords=[I()for _ in range(4)];mask=C.c_uint();sequence=int(self.x.XNextRequest(d))
  if not self.x.XQueryPointer(d,window,C.byref(root),C.byref(child),*(C.byref(x)for x in coords),C.byref(mask)):raise ValueError('QueryPointer wrong screen')
  self.check();return dict(position=[coords[0].value,coords[1].value],root=int(root.value),window=int(window),sequence=sequence)
 def context_state(self,d,context,ranges,*,enabled):
  state=P(RecordState)()
  try:
   if not self.t.XRecordGetContext(d,context,C.byref(state))or not state:raise ValueError('context state absent')
   s=state.contents
   if s.enabled!=int(enabled)or s.datum_flags!=7 or s.nclients!=(3 if enabled else 4) or not s.client_info:raise ValueError('context flags/client count changed')
   clients=[]
   expected=range_coverage(ranges)
   for j in range(int(s.nclients)):
    if not s.client_info[j]:raise ValueError('null client state')
    info=s.client_info[j].contents;clients.append(int(info.client))
    if not 1<=info.nranges<=4 or not info.ranges:raise ValueError('context ranges changed')
    if any(not info.ranges[k]for k in range(int(info.nranges))):raise ValueError('null context range')
    if range_coverage([info.ranges[k].contents for k in range(int(info.nranges))])!=expected:raise ValueError('context ranges changed')
   # GetContext expands AllClients to each current client + FutureClients(2).
   # Before Enable: driver/control/data. Enable unregisters the data client.
   if len(set(clients))!=(3 if enabled else 4) or clients.count(2)!=1 or any(c<=3 for c in clients if c!=2):raise ValueError('context expanded clients changed')
   self.check();return True
  finally:
   if state:self.t.XRecordFreeState(state)
