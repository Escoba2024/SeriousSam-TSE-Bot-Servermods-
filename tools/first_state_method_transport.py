"""Disabled three-role FreshExec transport for the exact two-Original observer.

No Frida import occurs in the role-owning parent. Legacy ObserverSession and
its strict drain schema are unchanged. This API is NOT a runner activation.
"""
import hashlib
import importlib.util
import json
import math
import os
from pathlib import Path
import socket
import subprocess
import sys
import time
try:
    from . import original_damage_worker as base
except ImportError:
    import original_damage_worker as base

RUNTIME_REVIEWED=False
MAX_PAYLOAD=2*1024*1024
MAX_ENVELOPE=16*1024
MAX_PACKET=MAX_PAYLOAD+MAX_ENVELOPE
MAX_COMMAND=MAX_ENVELOPE
METHODS=('connect','load','arm','drain','stop','unload','detach')
start_ticks=base.start_ticks


def canonical(value):return json.dumps(value,allow_nan=False,separators=(',',':')).encode()


def require(condition,message):
    if not condition:raise RuntimeError(message)


def private_write(path,data):
    fd=os.open(path,os.O_WRONLY|os.O_CREAT|os.O_EXCL|os.O_NOFOLLOW,0o600)
    with os.fdopen(fd,'wb')as stream:stream.write(data);stream.flush();os.fsync(stream.fileno())


class WireArchive:
    """Bounded raw evidence, before JSON/ID/schema interpretation; never truncate."""
    def __init__(self,evidence):self.evidence=Path(evidence);self.count=0;self.total=0
    def record_owner(self,record):private_write(self.evidence/'worker-owner.json',canonical(record))
    def __call__(self,raw,complete):
        require(len(raw)<=MAX_PACKET,'wire record bound')
        require(self.count<16384 and self.total+len(raw)<=512*1024*1024,'wire journal bound')
        self.count+=1;self.total+=len(raw)
        name='worker-wire-%05d'%self.count
        private_write(self.evidence/(name+'.bin'),raw)
        private_write(self.evidence/(name+'.json'),canonical({'length':len(raw),'complete':complete,'sha256':hashlib.sha256(raw).hexdigest()}))


class WorkerProxy(base.WorkerProxy):
    def __init__(self,process,channel,archive_wire):
        super().__init__(process,channel)
        # Public constructor preserves the inherited pinned own-child lifecycle.
        self.start_ticks=start_ticks(self.pid);self.archive_wire=archive_wire

    @classmethod
    def start(cls,config_path,archive_wire):
        if not RUNTIME_REVIEWED:raise RuntimeError('disabled first-state worker: Root freeze required')
        a,b=socket.socketpair();process=None
        try:
            process=subprocess.Popen([sys.executable,str(Path(__file__).resolve()),'--worker',str(config_path),str(b.fileno())],
                pass_fds=(b.fileno(),),close_fds=True,stdin=subprocess.DEVNULL,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
            proxy=cls(process,a,archive_wire)
            archive_wire.record_owner({'pid':proxy.pid,'start_ticks':proxy.start_ticks,'state':'UNARMED_NO_COMMAND_SENT','config_path':str(config_path)})
            return proxy
        except BaseException:
            a.close()
            # start() has not returned; no admission IPC was possible. Only this
            # exact Popen child is provably unarmed and may be reaped here.
            if process is not None:
                if process.poll()is None:
                    process.terminate()
                    try:process.wait(timeout=1)
                    except subprocess.TimeoutExpired:process.kill();process.wait(timeout=1)
                else:process.wait(timeout=1)
            raise
        finally:b.close()

    def call(self,method,*,timeout=.1,cleanup=False,**kwargs):
        if self.failed and not cleanup:raise RuntimeError('first-state worker sticky failure')
        require(not self.reaped,'first-state worker already reaped')
        if method not in METHODS:raise ValueError('worker command allowlist')
        if not isinstance(timeout,(int,float))or not math.isfinite(timeout)or not 0<timeout<=3:raise ValueError('bounded IPC timeout')
        self.sequence+=1;request={'id':self.sequence,'method':method,'kwargs':kwargs}
        data=canonical(request)+b'\n'
        if len(data)>MAX_COMMAND:raise ValueError('worker command bound')
        began=time.monotonic();deadline=began+timeout
        row={'id':self.sequence,'method':method,'started':began,'deadline':deadline};self.timings.append(row)
        try:
            def remaining():
                left=deadline-time.monotonic()
                if left<=0:raise TimeoutError('first-state worker deadline: '+method)
                self.channel.settimeout(left)
            remaining();self.channel.sendall(data)
            while b'\n'not in self.buffer:
                remaining();chunk=self.channel.recv(min(65536,MAX_PACKET+1-len(self.buffer)))
                if not chunk:raise RuntimeError('first-state worker closed IPC')
                self.buffer+=chunk
                if len(self.buffer)>MAX_PACKET:
                    # Oversized stream cannot be fully admitted: retain bounded
                    # evidence explicitly marked incomplete, never a valid RPC.
                    self.archive_wire(self.buffer[:MAX_PACKET],False)
                    raise ValueError('first-state worker packet bound; incomplete raw retained')
            raw,self.buffer=self.buffer.split(b'\n',1)
            self.archive_wire(raw,True)  # MUST precede all parsing/validation.
            reply=json.loads(raw)
            if type(reply)is not dict or set(reply)!={'id','ok','result'}:raise ValueError('worker reply schema')
            if type(reply['id'])is not int or reply['id']!=self.sequence:raise ValueError('worker reply ID differs')
            payload=canonical(reply['result'])
            if len(payload)>MAX_PAYLOAD or len(raw)-len(payload)>MAX_ENVELOPE:raise ValueError('worker payload/envelope bound')
            if reply['ok']is not True:raise RuntimeError('worker error:'+str(reply['result']))
            row['ok']=True;return reply['result']
        except BaseException as error:
            self.failed=True;row.update(ok=False,error=repr(error));raise
        finally:row['finished']=time.monotonic()

    def finish_after_roles_closed(self,*,roles_closed):return self.finish(roles_closed=roles_closed)


def ownership_gate(config):
    """Same parent-owned lock/PID/start/cwd/unit/net checks as the A3 worker;
    exactly the historical server+vanilla+botA roles, never botB/AI populations.
    """
    parent=config['parent'];pid=parent['pid']
    require(start_ticks(pid)==parent['start_ticks'] and os.getppid()==pid,'own controller parent changed/orphaned')
    lock=Path(config['arena'])/'runtime.lock';st=lock.stat()
    require([st.st_dev,st.st_ino]==parent['lock_file'],'arena lock replaced')
    key=f'{os.major(st.st_dev):02x}:{os.minor(st.st_dev):02x}:{st.st_ino}'
    rows=[r.split()for r in Path('/proc/locks').read_text().splitlines()if key in r.split()]
    require(any(r[1:5]==['FLOCK','ADVISORY','WRITE',str(pid)]and r[5]==key for r in rows),'own exclusive parent lock absent')
    require(set(config['roles'])=={'server','vanilla','botA'},'exact historical own roles required')
    for role,record in config['roles'].items():
        proc=Path('/proc')/str(record['identity'][0])
        require(start_ticks(record['identity'][0])==record['identity'][1],'own role start changed')
        require(str((proc/'cwd').resolve())==str(Path(config['arena'])/role),'own role cwd changed')
        require(any(row.split(':',2)[-1].rstrip('/').endswith('/'+record['unit'])for row in(proc/'cgroup').read_text().splitlines()),'own role unit changed')
        require((proc/'ns/net').stat().st_ino==record['net_namespace_inode'],'own role namespace changed')
    return True


def load_module(name,path):
    spec=importlib.util.spec_from_file_location(name,path);module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module);return module


class Collector:
    """Worker-only owner of unmodified NativeContext/NativePorts.

    All raw Frida results are journaled before cleanup semantics are inspected.
    Potentially blocking Frida operations stay inside this process exclusively.
    """
    def __init__(self,config,guard):
        root=Path(config['controller_root']);self.deadline=config['observer_deadline']
        require(type(self.deadline)in(int,float)and math.isfinite(self.deadline)and time.monotonic()<self.deadline<=time.monotonic()+125,'original absolute observer deadline')
        self.failed=False;self.cleanup_errors=[];self.idle_detached=False;self.loaded=False;self.connected=False
        self.config=config;self.guard=guard
        sys.path.insert(0,str(root))
        module=load_module('frozen_first_state_native',root/'native_first_state.py')
        self.context=module.NativeContext(config['frame'],config['roles'],config['pins'],guard,config['evidence'])
        require(self.context.expected==config['expected_identity'],'worker/parent Original identity differs')
        self.context.require_original_regions()
        self.ports=module.NativePorts(self.context,(root/'vendor/observer/observer.js').read_text(),config['evidence'])
        self.original_verified=False

    def raw(self,method,arg=None):
        self.guard()
        exports=self.ports.script.exports_sync
        value=getattr(exports,method)(arg)if method=='arm'else getattr(exports,method)()
        # Preserve actual raw payload even if status/idle/stop validation fails.
        try:self.ports.archive({'operation':'worker-'+method,'raw':value})
        except BaseException as error:
            self.failed=True
            if method not in('stop','status','finishstop'):raise
            self.cleanup_errors.append('raw journal:'+repr(error))
        if len(canonical(value))>MAX_PAYLOAD:raise ValueError('observer actual payload exceeds 2MiB')
        return value

    def connect(self):
        require(not self.connected,'one observer connection');self.context.guard();self.ports.connect();self.connected=True;return {'connected':True}
    def load(self):
        require(self.connected and not self.loaded,'one observer load');self.context.guard();self.ports.load();self.loaded=True;return {'loaded':True}
    def arm(self,config):
        require(self.loaded,'observer not loaded');self.context.guard()
        require(all(config.get(k)==v for k,v in self.context.expected.items()),'arm identity differs')
        result=self.raw('arm',config)
        if self.ports.messages:raise RuntimeError('unexpected Frida message')
        return result
    def drain(self):
        value=self.raw('drain')
        if self.ports.messages:raise RuntimeError('unexpected Frida message')
        return value
    def stop(self):
        self.raw('stop')  # admission only, NEVER detach an active callback
        while True:
            state=self.raw('status')
            fields={'enabled','stop_reason','in_flight','callbacks','getter_callbacks','active_calls','active_damage','idle','detached'}
            require(type(state)is dict and set(state)==fields,'cleanup status schema')
            require(all(type(state[k])is bool for k in('enabled','idle','detached')),'cleanup status flags')
            require(all(type(state[k])is int and 0<=state[k]<=8192 for k in('in_flight','callbacks','getter_callbacks','active_calls','active_damage')),'cleanup status counts')
            require(state['stop_reason']is None or type(state['stop_reason'])is str,'cleanup stop reason')
            expected=not state['enabled']and all(state[k]==0 for k in('in_flight','callbacks','getter_callbacks','active_calls','active_damage'))
            require(state['idle']==expected,'cleanup idle inconsistent')
            if state['idle']:break
            if time.monotonic()>=self.deadline:raise TimeoutError('original absolute observer idle deadline')
            time.sleep(min(.01,max(0,self.deadline-time.monotonic())))
        result=self.raw('finishstop')
        require(type(result)is dict and result.get('stopped')is True,'observer finishstop incomplete')
        self.idle_detached=True
        require(result=={'stopped':True,'stop_reason':'host requested'},'observer sticky non-host stop')
        if self.ports.messages:raise RuntimeError('unexpected Frida message')
        if self.cleanup_errors:raise RuntimeError('; '.join(self.cleanup_errors))
        return result
    def unload(self):
        require(self.idle_detached,'unsafe unload before idle/detach')
        failures=[]
        try:self.context.require_original_regions();self.original_verified=True
        except BaseException as error:failures.append(repr(error))
        try:self.ports.unload()
        except BaseException as error:failures.append(repr(error))
        if self.ports.messages:failures.append('unexpected Frida message')
        if failures:raise RuntimeError('; '.join(failures))
        return {'unloaded':True,'original_verified':self.original_verified}
    def detach(self):
        require(self.idle_detached,'unsafe detach before idle/detach')
        failures=[]
        try:self.ports.detach()
        except BaseException as error:failures.append(repr(error))
        try:self.context.require_original_regions();self.original_verified=True
        except BaseException as error:failures.append(repr(error))
        if self.ports.messages:failures.append('unexpected Frida message')
        if failures:raise RuntimeError('; '.join(failures))
        return {'detached':True,'original_verified':self.original_verified}


class LegacyWorkerPorts:
    """Explicit adapter for unchanged ObserverSession; no legacy runner rewrite."""
    def __init__(self,context,evidence,proxy):
        self.context=context;self.evidence=Path(evidence);self.proxy=proxy;self.archive_bytes=0;self.archive_index=0
    def now(self):return time.monotonic()
    def guard(self):return self.context.guard()
    def archive(self,row):
        data=canonical(row)+b'\n';require(self.archive_bytes+len(data)<=512*1024*1024,'observer archive bound')
        self.archive_index+=1
        private_write(self.evidence/('legacy-rpc-%05d.json'%self.archive_index),data);self.archive_bytes+=len(data)
    def connect(self):return self.proxy.call('connect',timeout=3)
    def load(self):return self.proxy.call('load',timeout=3)
    def rpc(self,method,config=None):
        if method not in('arm','drain','stop'):raise ValueError('legacy RPC allowlist')
        kw={'config':config}if method=='arm'else{}
        return self.proxy.call(method,timeout=3 if method=='arm'else 2 if method=='stop'else .1,cleanup=method in('drain','stop'),**kw)
    def unload(self):return self.proxy.call('unload',timeout=2,cleanup=True)
    def detach(self):return self.proxy.call('detach',timeout=2,cleanup=True)
    def read_regions(self):return self.context.read_regions()
    def finish_after_roles_closed(self,*,roles_closed):return self.proxy.finish_after_roles_closed(roles_closed=roles_closed)


def worker(config_path,fd):
    if not RUNTIME_REVIEWED:raise RuntimeError('disabled first-state method worker')
    path=Path(config_path).resolve(strict=True)
    require(path.stat().st_mode&0o077==0 and not Path(config_path).is_symlink(),'private config mode/path')
    config=json.loads(path.read_text());root=Path(config['controller_root']).resolve(strict=True)
    require(root==Path(__file__).resolve().parent,'worker controller root changed')
    manifest=json.loads((root/'source-manifest.json').read_text())
    require(manifest.get('runtime_reviewed')is True,'disabled worker manifest')
    for source,digest in manifest['runtime_dependencies'].items():
        require(hashlib.sha256(Path(source).read_bytes()).hexdigest()==digest,'worker source pin:'+source)
    for name in('first_state_method_transport.py','native_first_state.py','vendor/observer/observer.js','original_damage_worker.py'):
        require(str(root/name)in manifest['runtime_dependencies'],'worker dependency outside manifest:'+name)
    ownership_gate(config);collector=Collector(config,lambda:ownership_gate(config))
    channel=socket.socket(fileno=fd);stream=channel.makefile('rb');last=0
    try:
        for raw in iter(lambda:stream.readline(MAX_COMMAND+1),b''):
            require(len(raw)<=MAX_COMMAND and raw.endswith(b'\n'),'worker command bound')
            request=json.loads(raw);seq=request['id'];method=request['method']
            require(type(seq)is int and seq==last+1,'worker command sequence');last=seq
            try:
                require(method in METHODS,'worker command allowlist')
                require(not collector.failed or method in('drain','stop','unload','detach'),'worker sticky failure')
                value=getattr(collector,method)(**request['kwargs'])
                reply={'id':seq,'ok':True,'result':value}
            except BaseException as error:
                collector.failed=True;reply={'id':seq,'ok':False,'result':{'error':repr(error)}}
            payload=canonical(reply['result']);data=canonical(reply)+b'\n'
            require(len(payload)<=MAX_PAYLOAD and len(data)<=MAX_PACKET,'worker response bound')
            channel.sendall(data)
    finally:
        # Best-effort only. May itself block; the role-owning parent has bounded
        # IPC and retains independent normal role cleanup before own-worker reap.
        try:
            if collector.loaded:
                try:collector.stop()
                finally:
                    if collector.idle_detached:
                        try:collector.unload()
                        finally:collector.detach()
        finally:collector.context.close();stream.close();channel.close()


if __name__=='__main__':
    if len(sys.argv)!=4 or sys.argv[1]!='--worker':raise SystemExit('disabled internal worker only')
    worker(sys.argv[2],int(sys.argv[3]))
