"""Disabled subprocess isolation for all potentially blocking Frida operations.

The input/role-owning parent never imports Frida, waits on its locks or calls its
RPC API. Deadline failure is sticky. Only the parent closes game roles normally;
this module can terminate its own worker after every bound game role is gone.
"""
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import signal
import socket
import subprocess
import sys
import time

RUNTIME_REVIEWED=False
MAX_PACKET=1024*1024


def start_ticks(pid):
    return int((Path('/proc')/str(pid)/'stat').read_text().rsplit(') ',1)[1].split()[19])


class WorkerProxy:
    def __init__(self,process,channel):
        self.process=process;self.channel=channel;self.pid=process.pid
        self.start_ticks=start_ticks(self.pid);self.sequence=0;self.failed=False
        self.buffer=b'';self.timings=[];self.reaped=False

    @classmethod
    def start(cls,config_path):
        if not RUNTIME_REVIEWED:raise RuntimeError('disabled collector worker: Root freeze required')
        a,b=socket.socketpair();process=None
        try:
            # exec a fresh interpreter: no Python/Frida mutexes, readers or arena
            # lock descriptors inherited. The socket is the sole passed fd.
            process=subprocess.Popen([sys.executable,str(Path(__file__).resolve()),'--worker',str(config_path),str(b.fileno())],
                pass_fds=(b.fileno(),),close_fds=True,stdin=subprocess.DEVNULL,
                stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
            return cls(process,a)
        except BaseException:
            a.close()
            # No arm command can have been sent before start() returns. This
            # exact Popen child is therefore unarmed even if pin acquisition
            # failed. Do not lose its handle or leave an untracked observer.
            if process is not None:
                if process.poll()is None:
                    process.terminate()
                    try:process.wait(timeout=1)
                    except subprocess.TimeoutExpired:process.kill();process.wait(timeout=1)
                else:process.wait(timeout=1)
            raise
        finally:b.close()

    def call(self,method,*,timeout=.1,cleanup=False,**kwargs):
        if self.failed and not cleanup:raise RuntimeError('collector worker sticky failure')
        if self.reaped:raise RuntimeError('collector worker already reaped')
        if method not in ('arm','drain','before_input','close'):raise ValueError('worker command allowlist')
        self.sequence+=1;request={'id':self.sequence,'method':method,'kwargs':kwargs}
        began=time.monotonic();deadline=began+timeout
        row={'id':self.sequence,'method':method,'started':began,'deadline':deadline,'host_epoch_ms':time.time()*1000}
        self.timings.append(row)
        try:
            def remaining():
                left=deadline-time.monotonic()
                if left<=0:raise TimeoutError('collector worker deadline: '+method)
                self.channel.settimeout(left)
            remaining();self.channel.sendall((json.dumps(request,allow_nan=False)+'\n').encode())
            while b'\n'not in self.buffer:
                remaining();data=self.channel.recv(min(65536,MAX_PACKET-len(self.buffer)))
                if not data:raise RuntimeError('collector worker closed IPC')
                self.buffer+=data
                if len(self.buffer)>=MAX_PACKET:raise RuntimeError('collector worker packet bound')
            raw,self.buffer=self.buffer.split(b'\n',1);reply=json.loads(raw)
            if reply.get('id')!=request['id']:raise RuntimeError('collector worker reply ID differs')
            if reply.get('ok')is not True:raise RuntimeError('collector worker:'+str(reply.get('error')))
            row['ok']=True;return reply['result']
        except BaseException as error:
            self.failed=True;row.update(ok=False,error=repr(error));raise
        finally:row['finished']=time.monotonic()

    def arm(self):return self.call('arm',timeout=3)
    def drain(self):return self.call('drain')
    def before_input(self,**kwargs):return self.call('before_input',**kwargs)
    def close(self):return self.call('close',timeout=2,cleanup=True)

    def finish(self,*,roles_closed):
        if self.reaped:return {'reaped':True,'pid':self.pid,'start_ticks':self.start_ticks}
        if roles_closed is not True:raise RuntimeError('own game roles must be normally closed before worker termination')
        # Caller proves each bound game PID/start is absent and its unit empty.
        # Only this Popen child is signalled; never a game/display process.
        self.channel.close()
        if self.process.poll()is None:
            if start_ticks(self.pid)!=self.start_ticks:raise RuntimeError('worker PID reused')
            self.process.terminate()
            try:self.process.wait(timeout=1)
            except subprocess.TimeoutExpired:
                if start_ticks(self.pid)!=self.start_ticks:raise RuntimeError('worker PID reused')
                self.process.kill();self.process.wait(timeout=1)
        else:self.process.wait(timeout=1)
        self.reaped=True
        return {'reaped':True,'pid':self.pid,'start_ticks':self.start_ticks,
                'returncode':self.process.returncode,'sticky_failure':self.failed,
                'timings':self.timings}


def ownership_gate(config):
    """Read-only ownership; the arena lock remains exclusively in the parent."""
    parent=config['parent'];pid=parent['pid']
    if start_ticks(pid)!=parent['start_ticks']:raise RuntimeError('own controller parent changed')
    if os.getppid()!=pid:raise RuntimeError('worker orphaned')
    lock=Path(config['arena'])/'runtime.lock';st=lock.stat()
    if [st.st_dev,st.st_ino]!=parent['lock_file']:raise RuntimeError('arena lock replaced')
    key=f'{os.major(st.st_dev):02x}:{os.minor(st.st_dev):02x}:{st.st_ino}'
    matches=[r.split()for r in Path('/proc/locks').read_text().splitlines()if key in r.split()]
    if not any(r[1:5]==['FLOCK','ADVISORY','WRITE',str(pid)]and r[5]==key for r in matches):
        raise RuntimeError('own parent exclusive arena lock absent')
    if set(config['roles'])!={'server','vanilla','botA'}:raise RuntimeError('exact own role set required')
    for role,rec in config['roles'].items():
        proc=Path('/proc')/str(rec['identity'][0])
        if start_ticks(rec['identity'][0])!=rec['identity'][1]:raise RuntimeError('own role start changed')
        if str((proc/'cwd').resolve())!=str(Path(config['arena'])/role):raise RuntimeError('own role cwd changed')
        if not any(r.split(':',2)[-1].rstrip('/').endswith('/'+rec['unit'])for r in(proc/'cgroup').read_text().splitlines()):
            raise RuntimeError('own role unit changed')
        if (proc/'ns/net').stat().st_ino!=rec['net_namespace_inode']:raise RuntimeError('own role namespace changed')
    return True


def worker(config_path,fd):
    if not RUNTIME_REVIEWED:raise RuntimeError('disabled worker: main freeze required')
    path=Path(config_path).resolve(strict=True);config=json.loads(path.read_text())
    root=Path(config['controller_root']).resolve(strict=True)
    if root!=Path(__file__).resolve().parent:raise RuntimeError('worker controller root changed')
    manifest=json.loads((root/'source-manifest.json').read_text())
    if manifest.get('runtime_reviewed')is not True:raise RuntimeError('disabled controller manifest')
    for source,digest in manifest['runtime_dependencies'].items():
        if hashlib.sha256(Path(source).read_bytes()).hexdigest()!=digest:raise RuntimeError('worker source pin:'+source)
    ownership_gate(config)
    sys.path.insert(0,str(root/'tools'))
    from retail_inventory_readonly import InventoryReader
    library=Path(config['collector_source'])
    if str(library)!=manifest['collector_source']or str(library)not in manifest['runtime_dependencies']:raise RuntimeError('collector source outside pinned manifest')
    spec=importlib.util.spec_from_file_location('frozen_original_input_collector',library)
    module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
    reg=config['registry'];reader=InventoryReader(reg['pid'],reg['start_ticks'],reg['cwd'],reg['game_sha256'],rotation_diagnostics=True,colt_preparation=True,mouse_input_profile=True)
    collector=module.Collector(reader,reg,Path(config['evidence']),lambda:ownership_gate(config))
    channel=socket.socket(fileno=fd);stream=channel.makefile('rb');last=0
    try:
        for raw in iter(lambda:stream.readline(MAX_PACKET),b''):
            if len(raw)>=MAX_PACKET or not raw.endswith(b'\n'):raise RuntimeError('worker command bound')
            request=json.loads(raw);seq=request['id'];method=request['method']
            if type(seq)is not int or seq!=last+1:raise RuntimeError('worker command sequence')
            last=seq
            try:
                if method not in ('arm','drain','before_input','close'):raise RuntimeError('worker command allowlist')
                if method=='close':
                    collector.close();result={'closed':collector.closed,'original_bytes_verified':collector.original_bytes_verified}
                else:result=getattr(collector,method)(**request['kwargs'])
                reply={'id':seq,'ok':True,'result':result}
            except BaseException as error:reply={'id':seq,'ok':False,'error':repr(error)}
            data=(json.dumps(reply,allow_nan=False)+'\n').encode()
            if len(data)>=MAX_PACKET:raise RuntimeError('worker response bound')
            channel.sendall(data)
    finally:
        # Best-effort safety only; these operations may themselves block. The
        # parent retains bounded role cleanup and reaps this worker afterwards.
        try:collector.close()
        finally:reader.close();stream.close();channel.close()


if __name__=='__main__':
    if len(sys.argv)!=4 or sys.argv[1]!='--worker':raise SystemExit('disabled internal worker only')
    worker(sys.argv[2],int(sys.argv[3]))
