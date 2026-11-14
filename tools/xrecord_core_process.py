"""Bounded fresh-exec IPC and exact own-child cleanup; no X libraries."""
import json
import os
from pathlib import Path
import selectors
import signal
import subprocess
import time

MAX_IPC=16384


def start_ticks(pid):return int((Path('/proc')/str(pid)/'stat').read_text().rsplit(') ',1)[1].split()[19])


def proc_bytes(path,limit):
 with path.open('rb')as f:data=f.read(limit+1)
 if len(data)>limit:raise ValueError('own proc field byte bound')
 return data


def actual_identity(process,_expected_display):
 p=Path('/proc')/str(process.pid)
 environment=proc_bytes(p/'environ',65536)
 values=[entry[len(b'DISPLAY='):]for entry in environment.split(b'\0')if entry.startswith(b'DISPLAY=')]
 if len(values)!=1:raise ValueError('own DISPLAY environment missing/duplicate')
 actual_display=values[0].decode('ascii')
 argv=[x.decode()for x in proc_bytes(p/'cmdline',16384).rstrip(b'\0').split(b'\0')]
 return dict(pid=process.pid,start_ticks=start_ticks(process.pid),argv=argv,display=actual_display)


def identity_matches(expected,actual):
 return all(actual.get(k)==expected.get(k)for k in('pid','start_ticks','argv','display'))and type(expected.get('pid'))is int and expected['pid']>0 and type(expected.get('start_ticks'))is int and expected['start_ticks']>0


class OwnChild:
 def __init__(self,argv,directory,display,*,ttl,role):
  self.argv=list(argv);self.directory=Path(directory).resolve();self.display=display;self.role=role;self.process=None;self.identity=None;self.buffer=b'';self.serial=0;self.errors=[];self.closed=False;self.forced=False
  self.started=time.monotonic();self.deadline=self.started+ttl
  self.log=os.fdopen(os.open(self.directory/(role+'-stderr.log'),os.O_WRONLY|os.O_CREAT|os.O_EXCL,0o600),'wb')
  try:
   self.process=subprocess.Popen(self.argv,stdin=subprocess.PIPE,stdout=subprocess.PIPE,stderr=self.log,cwd=self.directory,start_new_session=True,close_fds=True,env={'DISPLAY':display,'PATH':'/usr/bin:/bin','LANG':'C.UTF-8'})
   # Persist the Popen handle before any /proc operation can fail.
   owner=dict(pid=self.process.pid,argv=self.argv,display=display,phase='POPEN_CREATED_BEFORE_IDENTITY')
   with os.fdopen(os.open(self.directory/(role+'-owner.json'),os.O_WRONLY|os.O_CREAT|os.O_EXCL,0o600),'w')as f:json.dump(owner,f)
   # No X libraries in parent.
   self.identity=dict(pid=self.process.pid,start_ticks=start_ticks(self.process.pid),argv=self.argv,display=display)
   self.guard()
   with os.fdopen(os.open(self.directory/(role+'-bound.json'),os.O_WRONLY|os.O_CREAT|os.O_EXCL,0o600),'w')as f:json.dump(self.identity,f)
  except BaseException as error:
   result=self.cleanup();result['start_error']=repr(error)[:1024]
   try:
    with os.fdopen(os.open(self.directory/(role+'-start-failure.json'),os.O_WRONLY|os.O_CREAT|os.O_EXCL,0o600),'w')as f:json.dump(result,f)
   except BaseException:pass # Preserve the original failure; owner/Popen were kept.
   raise
 def guard(self):
  if self.process is None or self.process.poll()is not None:raise RuntimeError('own child exited')
  actual=actual_identity(self.process,self.display)
  if not identity_matches(self.identity,actual):raise RuntimeError('own child identity changed: '+repr(actual))
  if os.getpgid(self.process.pid)!=self.process.pid or(Path('/proc')/str(self.process.pid)/'cwd').resolve()!=self.directory:raise RuntimeError('own child group/CWD changed')
  if self.display not in self.argv:raise RuntimeError('display missing in exact argv')
  if os.fstat(self.log.fileno()).st_size>2097152:raise ValueError('own stderr byte bound')
 def call(self,command,*,timeout,**fields):
  self.guard();deadline=min(time.monotonic()+timeout,self.deadline)
  self.serial+=1;request=dict(id=self.serial,command=command,**fields);wire=json.dumps(request,allow_nan=False).encode()+b'\n'
  if len(wire)>MAX_IPC:raise ValueError('IPC request bound')
  try:
   with selectors.DefaultSelector()as selector:
    fd=self.process.stdin.fileno();os.set_blocking(fd,False);selector.register(fd,selectors.EVENT_WRITE)
    offset=0
    while offset<len(wire):
     left=deadline-time.monotonic()
     if left<=0 or not selector.select(left):raise TimeoutError('bounded own IPC write')
     offset+=os.write(fd,wire[offset:])
   with selectors.DefaultSelector()as selector:
    fd=self.process.stdout.fileno();os.set_blocking(fd,False);selector.register(fd,selectors.EVENT_READ)
    while b'\n'not in self.buffer:
     left=deadline-time.monotonic()
     if left<=0 or not selector.select(left):raise TimeoutError('bounded own IPC reply')
     part=os.read(fd,min(4096,MAX_IPC+1-len(self.buffer)))
     if not part:raise EOFError('own IPC closed')
     self.buffer+=part
     if len(self.buffer)>MAX_IPC:raise ValueError('IPC reply bound')
   line,self.buffer=self.buffer.split(b'\n',1);reply=json.loads(line)
   if type(reply.get('id'))is not int or reply.get('id')!=self.serial or reply.get('ok')is not True:raise ValueError('own IPC receipt failed:'+str(reply.get('error',''))[:1024])
   # stop is an authenticated final reply; exiting normally afterwards is expected.
   if command!='stop':self.guard()
   return reply
  except BaseException as error:self.errors.append(type(error).__name__+':'+str(error));raise
 def signal_own(self,sig):
  if self.process is None or self.process.poll()is not None:return
  # An unreaped live Popen PID cannot be reused. A partial constructor still
  # owns this exact new session, even if its first /proc read failed.
  if self.identity is not None and start_ticks(self.process.pid)!=self.identity['start_ticks']:raise RuntimeError('own PID reused')
  if os.getpgid(self.process.pid)!=self.process.pid:raise RuntimeError('own child left group')
  os.killpg(self.process.pid,sig)
 def cleanup(self,*,stop_timeout=None,normal_signal=False):
  if self.closed:return self.receipt()
  self.closed=True;deadline=time.monotonic()+5
  try:
   if self.process is not None:
    if self.process.poll()is None and normal_signal:self.signal_own(signal.SIGTERM)
    if self.process.poll()is None and stop_timeout is not None:
     try:self.call('stop',timeout=min(stop_timeout,max(.001,deadline-time.monotonic())))
     except BaseException as error:self.errors.append('normal stop:'+repr(error))
    try:self.process.wait(timeout=max(.001,min(4. if normal_signal else 1.,deadline-time.monotonic())))
    except subprocess.TimeoutExpired:
     self.forced=True;self.errors.append('own child required forced cleanup');self.signal_own(signal.SIGTERM)
     try:self.process.wait(timeout=max(.001,min(1.,deadline-time.monotonic())))
     except subprocess.TimeoutExpired:self.signal_own(signal.SIGKILL);self.process.wait(timeout=max(.001,deadline-time.monotonic()))
    for stream in(self.process.stdin,self.process.stdout):
     if stream is not None:stream.close()
  except BaseException as error:self.errors.append('cleanup:'+repr(error))
  finally:self.log.close()
  return self.receipt()
 def receipt(self):return dict(role=self.role,identity=self.identity,argv=self.argv,closed=self.process is not None and self.process.poll()is not None,reaped=self.process is not None and self.process.returncode is not None,exit_code=None if self.process is None else self.process.returncode,forced=self.forced,errors=list(self.errors))
