"""Disabled own-PE method controller. Root alone freezes/builds/executes it.

Frida is imported only in a fresh worker. No TSE imports, launches or inputs.
The shared DamageWorker module supplies only its bounded IPC/Popen proxy.
"""
import argparse
import fcntl
import hashlib
import json
import os
from pathlib import Path
import selectors
import shutil
import socket
import struct
import subprocess
import sys
import time

from original_damage_worker import WorkerProxy, start_ticks, MAX_PACKET
import win32_instruction_probe_policy as policy

RUNTIME_REVIEWED=False
FRIDA_PACKAGE=Path('/srv/tse-frida-probe-20261111/lib/python3.12/site-packages')


def require(value,message):
    if not value:raise RuntimeError(message)


def sha(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def pe32_base(data):
    try:
        if data[:2]!=b'MZ':raise ValueError('own PE32 required')
        pe=struct.unpack_from('<I',data,0x3c)[0]
        if data[pe:pe+4]!=b'PE\0\0':raise ValueError('PE signature')
        machine=struct.unpack_from('<H',data,pe+4)[0]
        flags=struct.unpack_from('<H',data,pe+22)[0]
        opt=pe+24;magic=struct.unpack_from('<H',data,opt)[0]
        base=struct.unpack_from('<I',data,opt+28)[0]
        dllflags=struct.unpack_from('<H',data,opt+70)[0]
        if machine!=0x14c or magic!=0x10b or flags&0x2000 or not flags&2:
            raise ValueError('own executable IA32 required')
        if base!=0x400000 or dllflags&0x40:raise ValueError('fixed own PE base required')
        return base
    except(struct.error,IndexError)as e:raise ValueError('truncated PE32')from e


def cleanup(close_worker,normal_exit,wait_native,reap_worker,errors):
    for label,fn in (('worker close',close_worker),('normal native Q',normal_exit)):
        try:fn()
        except BaseException as e:errors.append(label+': '+repr(e))
    ended=False
    try:ended=wait_native()is True
    except BaseException as e:errors.append('native end: '+repr(e))
    if not ended:errors.append('native end not proven; worker signal refused');return
    try:reap_worker(True)
    except BaseException as e:errors.append('own worker reap: '+repr(e))


def identity(pid,config):
    proc=Path('/proc')/str(pid);record=config['native']
    require(start_ticks(pid)==record['start_ticks'],'own native PID/start changed')
    require((proc/'cwd').resolve()==Path(config['root']),'own native CWD changed')
    require((proc/'ns/net').stat().st_ino==record['netns'],'own native namespace changed')
    require(b'WINEPREFIX='+config['prefix'].encode()in(proc/'environ').read_bytes().split(b'\0'),
            'own native prefix changed')
    exe=Path(config['exe']);st=exe.stat()
    require([st.st_dev,st.st_ino]==record['exe_inode']and sha(exe)==config['exe_sha256'],
            'own executable changed')
    require(any(len(parts:=line.split(maxsplit=5))==6 and parts[5]==str(exe)
                and int(parts[4])==st.st_ino and parts[3]==f'{os.major(st.st_dev):02x}:{os.minor(st.st_dev):02x}'
                for line in(proc/'maps').read_text().splitlines()),
            'own executable mapping absent')


def owner(config):
    require(os.getppid()==config['parent']['pid'],'method worker parent changed')
    require(start_ticks(os.getppid())==config['parent']['start_ticks'],'method parent reused')
    lock=Path(config['root'])/'method.lock';st=lock.stat()
    require([st.st_dev,st.st_ino]==config['parent']['lock_inode'],'method lock changed')
    key=f'{os.major(st.st_dev):02x}:{os.minor(st.st_dev):02x}:{st.st_ino}'
    require(any(r[1:5]==['FLOCK','ADVISORY','WRITE',str(os.getppid())]and r[5]==key
                for line in Path('/proc/locks').read_text().splitlines()
                if len(r:=line.split())>=6),'own exclusive method lock absent')
    identity(config['native']['pid'],config)


class MethodProxy(WorkerProxy):
    @classmethod
    def start(cls,config_path):
        require(RUNTIME_REVIEWED,'disabled methods worker')
        a,b=socket.socketpair();process=None
        try:
            process=subprocess.Popen([sys.executable,str(Path(__file__).resolve()),'--worker',str(config_path),str(b.fileno())],
                pass_fds=(b.fileno(),),close_fds=True,stdin=subprocess.DEVNULL,
                stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
            return cls(process,a)
        except BaseException:
            a.close()
            if process is not None:
                # start() has not returned; no ARM could have been sent.
                if process.poll()is None:
                    process.terminate()
                    try:process.wait(timeout=1)
                    except subprocess.TimeoutExpired:process.kill();process.wait(timeout=1)
                else:process.wait(timeout=1)
            raise
        finally:b.close()

    def close(self,quiescent=False):return self.call('close',timeout=2,cleanup=True,quiescent=quiescent)


def verify_manifest(root):
    require(RUNTIME_REVIEWED,'disabled method controller')
    m=json.loads((root/'source-manifest.json').read_text())
    require(m.get('runtime_reviewed')is True and m.get('scope')=='OWN_WIN32_IA32_INSTRUCTION_METHOD',
            'disabled/unrecognized method manifest')
    for p,h in m['runtime_dependencies'].items():require(sha(p)==h,'method pin '+p)
    require(sha(root/'win32_instruction_probe.cpp')==m['build']['source_sha256'],'own native source differs')
    require(m['build']['exe_sha256']==sha(root/'win32_instruction_probe.exe'),'own native binary differs')
    require(pe32_base((root/'win32_instruction_probe.exe').read_bytes())==0x400000,'PE base')
    require(len(m['sites'])==2 and {s['name']for s in m['sites']}=={'saved','arguments'},'exact two method sites')
    for s in m['sites']:
        require(type(s['rva'])is int and 0x1000<=s['rva']<0x100000,'own RVA range')
        require(14<=len(bytes.fromhex(s['hex']))<=128 and s['hex'].startswith('90'*8),'own full midpoint body')
    return m


def original_bytes(config,phase):
    identity(config['native']['pid'],config);rows=[]
    with (Path('/proc')/str(config['native']['pid'])/'mem').open('rb',buffering=0)as mem:
        for site in config['sites']:
            expected=bytes.fromhex(site['hex']);mem.seek(0x400000+site['rva']);actual=mem.read(len(expected))
            rows.append(dict(phase=phase,site=site['name'],length=len(expected),
                             expected_sha256=hashlib.sha256(expected).hexdigest(),
                             actual_sha256=hashlib.sha256(actual).hexdigest(),equal=actual==expected))
    return rows


def worker(config_path,fd):
    require(RUNTIME_REVIEWED,'disabled method worker')
    config=json.loads(Path(config_path).read_text());root=Path(config['root'])
    require(root==Path(__file__).resolve().parent,'method root changed');verify_manifest(root);owner(config)
    channel=socket.socket(fileno=fd);stream=channel.makefile('rb');last=0
    session=None;script=None;errors=[];receipts=[];closed=None
    def close(quiescent=False):
        nonlocal closed
        if closed is not None:return closed
        out=dict(script_idle=False,hooks_detached=False,original_bytes_verified=False,
                 script_unloaded=False,session_detached=False,errors=[])
        owner(config)
        require(quiescent is True,'actual native frames not proven returned')
        packet=dict(records=[],faults=0,dropped=0)
        if script is not None:
            packet=script.exports_sync.stop();out['packet']=packet
            require(packet['idle']is True,'own callback idle')
            out['script_idle']=True
            require(packet['detached']is True,'own hook detach');out['hooks_detached']=True
            if packet['faults']or packet['dropped']:errors.append('own callback faults/drops remain sticky')
        else:out.update(packet=packet,script_idle=True,hooks_detached=True)
        rows=original_bytes(config,'before-unload');receipts.extend(rows)
        require(all(r['equal']for r in rows),'full own Original bytes differ')
        out['original_bytes_verified']=True;out['original_body_receipts']=rows
        try:
            if script is not None:script.unload()
            out['script_unloaded']=True
        except BaseException as e:errors.append('script unload: '+repr(e))
        try:
            if session is not None:session.detach()
            out['session_detached']=True
        except BaseException as e:errors.append('session detach: '+repr(e))
        out['errors']=list(errors);closed=out;return out
    try:
        for raw in iter(lambda:stream.readline(MAX_PACKET),b''):
            require(len(raw)<MAX_PACKET and raw.endswith(b'\n'),'method IPC bound')
            q=json.loads(raw);require(type(q['id'])is int and q['id']==last+1,'method sequence');last=q['id']
            try:
                owner(config);method=q['method'];require(method in('arm','drain','close'),'method allowlist')
                if method=='arm':
                    require(script is None and session is None,'method one arm')
                    rows=original_bytes(config,'before-attach');receipts.extend(rows);require(all(r['equal']for r in rows),'own initial bytes')
                    sys.path.insert(0,str(FRIDA_PACKAGE));import frida
                    require(frida.__version__=='17.26.2'and Path(frida.__file__).resolve().is_relative_to(FRIDA_PACKAGE),'pinned Frida version/path')
                    pinned=json.loads((root/'source-manifest.json').read_text())['runtime_dependencies']
                    for module in(frida,frida._frida):
                        require(str(Path(module.__file__).resolve())in pinned,'imported Frida module outside pins')
                    require(not errors,'sticky method failure')
                    session=frida.get_local_device().attach(config['native']['pid'])
                    script=session.create_script((root/'win32_instruction_probe.js').read_text())
                    def message(msg,data):
                        if msg.get('type')=='error'or data is not None:errors.append(str(msg)[:2048])
                    script.on('message',message);script.load();result=script.exports_sync.arm(config['mode'],config['sites'],dict(pid=config['native']['pid'],image_base='0x400000'))
                    require(not errors,'sticky arm message fault')
                elif method=='drain':require(not errors,'sticky message fault');result=script.exports_sync.status()
                else:result=close(**q['kwargs'])
                reply=dict(id=last,ok=True,result=result)
            except BaseException as e:errors.append(repr(e));reply=dict(id=last,ok=False,error=repr(e))
            data=(json.dumps(reply,allow_nan=False)+'\n').encode();require(len(data)<MAX_PACKET,'method response bound');channel.sendall(data)
    finally:stream.close();channel.close()


def read_line(stream,seconds):
    deadline=time.monotonic()+seconds;out=b''
    with selectors.DefaultSelector()as select:
        select.register(stream,selectors.EVENT_READ)
        while b'\n'not in out:
            left=deadline-time.monotonic();require(left>0 and select.select(left),'native stdout deadline')
            part=os.read(stream.fileno(),1);require(part,'native stdout EOF');out+=part
            require(len(out)<4096,'native stdout bound')
    return json.loads(out)


def prefix_pids(prefix):
    found=[]
    for proc in Path('/proc').glob('[0-9]*'):
        try:
            if b'WINEPREFIX='+str(prefix).encode()in(proc/'environ').read_bytes().split(b'\0'):found.append(int(proc.name))
        except(FileNotFoundError,ProcessLookupError):pass
    return found


def main(mode):
    require(RUNTIME_REVIEWED,'disabled own methods controller')
    require(mode in policy.MODES,'one fixed mode required')
    root=Path(__file__).resolve().parent;m=verify_manifest(root)
    require(shutil.disk_usage(root).free>=8*2**30,'8GiB disk floor')
    prefix=root/'wineprefix';require(prefix.is_dir()and not prefix.is_symlink(),'Root-prepared own nonsymlink prefix absent')
    with (root/'method.lock').open('a')as lock:
        fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
        require(not prefix_pids(prefix),'own dedicated prefix occupied')
        evidence=root/('evidence-'+mode+'-'+time.strftime('%Y%m%d-%H%M%S',time.gmtime()));evidence.mkdir(mode=0o700)
        report=dict(mode=mode,retail_qualified=False,errors=[],cleanup={},callback_records=0,callback_rows=[],callback_faults=0,callback_dropped=0)
        def save():(evidence/'result.json').write_text(json.dumps(report,indent=2)+'\n')
        report['owner']=dict(pid=os.getpid(),start_ticks=start_ticks(os.getpid()),manifest_sha256=sha(root/'source-manifest.json'));save()
        process=None;proxy=None;native=None;config=None;phase=None
        try:
            wine=Path(m['wine']);require(str(wine)in m['runtime_dependencies'],'Wine outside pins')
            env=dict(os.environ,WINEPREFIX=str(prefix),WINEARCH='win64',WINEDEBUG='-all');env.pop('DISPLAY',None)
            with (evidence/'native-stderr.log').open('xb')as err:
                process=subprocess.Popen([str(wine),str(root/'win32_instruction_probe.exe')],cwd=root,env=env,
                    stdin=subprocess.PIPE,stdout=subprocess.PIPE,stderr=err,close_fds=True)
            ready=read_line(process.stdout,10);require(ready==dict(phase='READY',schema=1),'native ready identity');phase='READY'
            candidates=[pid for pid in prefix_pids(prefix)if str(root/'win32_instruction_probe.exe')in(Path('/proc')/str(pid)/'maps').read_text()]
            require(len(candidates)==1,'own native mapping ambiguous/absent');pid=candidates[0]
            st=(root/'win32_instruction_probe.exe').stat();ls=(root/'method.lock').stat()
            native=dict(pid=pid,start_ticks=start_ticks(pid),netns=(Path('/proc')/str(pid)/'ns/net').stat().st_ino,exe_inode=[st.st_dev,st.st_ino])
            config=dict(root=str(root),prefix=str(prefix),mode=mode,native=native,exe=str(root/'win32_instruction_probe.exe'),
                        exe_sha256=m['build']['exe_sha256'],sites=m['sites'],parent=dict(pid=os.getpid(),start_ticks=start_ticks(os.getpid()),lock_inode=[ls.st_dev,ls.st_ino]))
            identity(pid,config);(evidence/'config.json').write_text(json.dumps(config,indent=2)+'\n')
            report['native_identity']=native
            initial=original_bytes(config,'parent-before-attach');report['initial_original_bytes']=initial
            require(all(r['equal']for r in initial),'parent initial original bytes')
            if mode!='baseline':
                proxy=MethodProxy.start(evidence/'config.json')
                report['worker_identity']=dict(pid=proxy.pid,start_ticks=proxy.start_ticks,config_sha256=sha(evidence/'config.json'));save()
                report['arm']=proxy.arm();save()
            phase='RUNNING';process.stdin.write(b'R');process.stdin.flush()
            report['native']=read_line(process.stdout,3);require(report['native']['phase']=='WAIT_CLEANUP','native frames not returned');phase='WAIT_CLEANUP'
        except BaseException as e:report['errors'].append(repr(e))
        finally:
            def close_worker():
                if proxy:
                    out=proxy.close(quiescent=phase in('READY','WAIT_CLEANUP'));report['worker_close']=out
                    report['cleanup'].update({k:out[k]for k in('script_idle','hooks_detached','original_bytes_verified','script_unloaded','session_detached')})
                    packet=out['packet'];report.update(callback_records=len(packet['records']),callback_rows=packet['records'],callback_faults=packet['faults'],callback_dropped=packet['dropped'])
                    require(out['errors']==[],'sticky worker faults')
                elif native is not None:
                    rows=original_bytes(config,'parent-uninstrumented-close');report['final_original_bytes']=rows
                    report['cleanup'].update(script_idle=True,hooks_detached=True,original_bytes_verified=all(r['equal']for r in rows),script_unloaded=True,session_detached=True)
            def stop():
                if process:process.stdin.write(b'Q');process.stdin.flush();process.stdin.close()
            def wait():
                if process:report['process_returncode']=process.wait(timeout=17)
                if native is None:return False
                deadline=time.monotonic()+2
                while time.monotonic()<deadline:
                    try:alive=start_ticks(native['pid'])==native['start_ticks']
                    except(FileNotFoundError,ProcessLookupError):alive=False
                    if not alive:report['cleanup']['process_ended']=True;return True
                    time.sleep(.02)
                return False
            def reap(ended):
                if proxy:report['worker_reap']=proxy.finish(roles_closed=ended)
                report['cleanup']['worker_reaped']=True
            cleanup(close_worker,stop,wait,reap,report['errors'])
            report['cleanup'].update(native_frames_returned=phase=='WAIT_CLEANUP',errors=list(report['errors']))
            report['verdict']=policy.verdict(mode,report)
            (evidence/'result.json').write_text(json.dumps(report,indent=2)+'\n')
            print(json.dumps(dict(evidence=str(evidence),verdict=report['verdict'])))
            return report


if __name__=='__main__':
    if len(sys.argv)==4 and sys.argv[1]=='--worker':worker(sys.argv[2],int(sys.argv[3]))
    else:
        parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--mode',choices=policy.MODES,required=True)
        main(parser.parse_args().mode)
