"""Focused OS IPC/cleanup adversaries; no Frida or game/display is loaded."""
import fcntl
import importlib.util
import json
import os
from pathlib import Path
import socket
import subprocess
import sys
import tempfile
import threading
import time
import unittest
from unittest.mock import patch

try:
    from tools import first_state_method_transport as m
except ImportError:m=None


class TransportTests(unittest.TestCase):
    def setUp(self):self.assertIsNotNone(m,'transport adapter absent')

    def idle(self,value):
        return {'enabled':False,'stop_reason':'host requested','in_flight':0 if value else 1,'callbacks':0,'getter_callbacks':0,'active_calls':0,'active_damage':0,'idle':value,'detached':False}

    def proxy(self,handler):
        a,b=socket.socketpair();logs=[]
        def serve():
            try:
                raw=b.makefile('rb').readline();handler(b,json.loads(raw))
            finally:b.close()
        t=threading.Thread(target=serve);t.start();self.addCleanup(t.join,2)
        self.addCleanup(a.close)
        return m.WorkerProxy(subprocess.Popen([sys.executable,'-c','pass']),a,lambda raw,complete:logs.append((raw,complete))),logs

    def test_raw_persisted_before_malformed_validation(self):
        p,rows=self.proxy(lambda b,r:b.sendall(b'{malformed\n'))
        with self.assertRaises(ValueError):p.call('drain')
        self.assertEqual(rows,[(b'{malformed',True)]);self.assertTrue(p.failed);p.process.wait()

    def test_more_than_old_one_mib_is_lossless(self):
        value='x'*(1024*1024+20)
        p,rows=self.proxy(lambda b,r:b.sendall(json.dumps({'id':r['id'],'ok':True,'result':value}).encode()+b'\n'))
        self.assertEqual(p.call('drain',timeout=1),value);self.assertEqual(json.loads(rows[0][0])['result'],value);p.process.wait()

    def test_payload_over_two_mib_rejected_after_raw_archive(self):
        value='x'*(2*1024*1024)
        p,rows=self.proxy(lambda b,r:b.sendall(json.dumps({'id':r['id'],'ok':True,'result':value}).encode()+b'\n'))
        with self.assertRaises(ValueError):p.call('drain',timeout=1)
        self.assertEqual(json.loads(rows[0][0])['result'],value);self.assertTrue(p.failed);p.process.wait()

    def test_wrong_reply_id_sticky(self):
        p,rows=self.proxy(lambda b,r:b.sendall(b'{"id":99,"ok":true,"result":null}\n'))
        with self.assertRaises(ValueError):p.call('drain')
        with self.assertRaises(RuntimeError):p.call('drain')
        self.assertTrue(rows);p.process.wait()

    def test_timeout_does_not_signal_and_reap_needs_roles_closed(self):
        a,b=socket.socketpair();kid=subprocess.Popen([sys.executable,'-c','import time;time.sleep(20)'])
        p=m.WorkerProxy(kid,a,lambda *x:None)
        try:
            with self.assertRaises(TimeoutError):p.call('drain',timeout=.02)
            self.assertIsNone(kid.poll())
            with self.assertRaises(RuntimeError):p.finish_after_roles_closed(roles_closed=False)
            self.assertIsNone(kid.poll());receipt=p.finish_after_roles_closed(roles_closed=True)
            self.assertTrue(receipt['reaped']);self.assertTrue(receipt['sticky_failure'])
        finally:
            b.close();a.close()
            if kid.poll()is None:kid.terminate();kid.wait(1)

    def test_start_pin_failure_reaps_only_unarmed_child(self):
        made=[];real=subprocess.Popen
        def popen(*args,**kwargs):
            child=real([sys.executable,'-c','import time;time.sleep(20)']);made.append(child);return child
        with patch.object(m,'RUNTIME_REVIEWED',True),patch.object(m.subprocess,'Popen',popen),patch.object(m,'start_ticks',side_effect=ValueError('pin fail')):
            with self.assertRaises(ValueError):m.WorkerProxy.start('/unused',lambda *x:None)
        self.assertIsNotNone(made[0].poll())

    def test_owner_receipt_failure_reaps_before_any_admission(self):
        made=[];real=subprocess.Popen
        def popen(*args,**kwargs):
            child=real([sys.executable,'-c','import time;time.sleep(20)']);made.append(child);return child
        with tempfile.TemporaryDirectory()as tmp:
            (Path(tmp)/'worker-owner.json').write_text('occupied')
            try:
                with patch.object(m,'RUNTIME_REVIEWED',True),patch.object(m.subprocess,'Popen',popen):
                    with self.assertRaises(FileExistsError):m.WorkerProxy.start('/unused',m.WireArchive(tmp))
                self.assertIsNotNone(made[0].poll())
            finally:
                for kid in made:
                    if kid.poll()is None:kid.terminate();kid.wait(1)

    def test_pid_reuse_blocks_worker_signal(self):
        a,b=socket.socketpair();kid=subprocess.Popen([sys.executable,'-c','import time;time.sleep(20)']);p=m.WorkerProxy(kid,a,lambda *x:None)
        try:
            with patch.object(m.base,'start_ticks',return_value=p.start_ticks+1):
                with self.assertRaises(RuntimeError):p.finish_after_roles_closed(roles_closed=True)
            self.assertIsNone(kid.poll())
        finally:b.close();a.close();kid.terminate();kid.wait(1)

    def collector(self,sequence,deadline=None):
        c=m.Collector.__new__(m.Collector);c.deadline=time.monotonic()+.2 if deadline is None else deadline;c.idle_detached=False;c.failed=False;c.cleanup_errors=[];c.journal=[];c.ports=type('P',(),{'messages':[]})()
        c.raw=lambda method,arg=None:c.journal.append(method)or sequence.pop(0)
        return c

    def test_stop_waits_actual_idle_and_finishstop(self):
        c=self.collector([{'stopped':False,'stop_reason':'host requested'}, self.idle(False), self.idle(True), {'stopped':True,'stop_reason':'host requested'}])
        self.assertEqual(c.stop(),{'stopped':True,'stop_reason':'host requested'});self.assertTrue(c.idle_detached)
        self.assertEqual(c.journal,['stop','status','status','finishstop'])

    def test_expired_active_stop_never_detaches(self):
        c=self.collector([{'stopped':False,'stop_reason':'host requested'},self.idle(False)],deadline=time.monotonic()-1)
        with self.assertRaises(TimeoutError):c.stop()
        self.assertFalse(c.idle_detached);self.assertNotIn('finishstop',c.journal)

    def test_sticky_observer_fault_still_finishes_idle_cleanup(self):
        c=self.collector([{'stopped':False,'stop_reason':'fault:x'},self.idle(True),{'stopped':True,'stop_reason':'fault:x'}])
        with self.assertRaises(RuntimeError):c.stop()
        self.assertTrue(c.idle_detached);self.assertEqual(c.journal[-1],'finishstop')

    def test_unload_unsafe_blocked_and_sticky_safe_cleanup_continues(self):
        c=self.collector([])
        with self.assertRaises(RuntimeError):c.unload()
        ops=[];c.idle_detached=True
        c.context=type('C',(),{'require_original_regions':lambda s:ops.append('verify')})()
        c.ports=type('P',(),{'messages':[{'error':'sticky'}],'unload':lambda s:ops.append('unload')})()
        with self.assertRaises(RuntimeError):c.unload()
        self.assertEqual(ops,['verify','unload'])

    def test_malformed_idle_cannot_authorize_detach(self):
        c=self.collector([{'stopped':False,'stop_reason':'host requested'}, {'idle':True}])
        with self.assertRaises(RuntimeError):c.stop()
        self.assertFalse(c.idle_detached);self.assertNotIn('finishstop',c.journal)

    def test_archive_failure_cannot_skip_safe_idle_cleanup(self):
        c=m.Collector.__new__(m.Collector);c.failed=False;c.cleanup_errors=[];c.deadline=time.monotonic()+.1;c.idle_detached=False;c.guard=lambda:None
        seq=[{'stopped':False,'stop_reason':'host requested'},self.idle(True),{'stopped':True,'stop_reason':'host requested'}];ops=[]
        class Exports:
            def __getattr__(self,name):
                return lambda:ops.append(name)or seq.pop(0)
        class Ports:
            messages=[]
            script=type('Script',(),{'exports_sync':Exports()})()
            def archive(self,row):raise OSError('journal full')
        c.ports=Ports()
        with self.assertRaises(RuntimeError):c.stop()
        self.assertTrue(c.idle_detached);self.assertTrue(c.failed);self.assertEqual(ops,['stop','status','finishstop'])

    def test_wire_private_exclusive_and_exact_payload_boundary(self):
        with tempfile.TemporaryDirectory()as tmp:
            archive=m.WireArchive(tmp);archive(b'raw',True)
            path=Path(tmp)/'worker-wire-00001.bin'
            self.assertEqual(path.stat().st_mode&0o777,0o600)
            with self.assertRaises(FileExistsError):m.private_write(path,b'overwrite')
            self.assertEqual(path.read_bytes(),b'raw')
        value='x'*(m.MAX_PAYLOAD-2)
        p,rows=self.proxy(lambda b,r:b.sendall(m.canonical({'id':r['id'],'ok':True,'result':value})+b'\n'))
        self.assertEqual(p.call('drain',timeout=1),value);p.process.wait()

    def test_real_own_lock_three_roles_and_changed_start_rejected(self):
        with tempfile.TemporaryDirectory()as tmp:
            arena=Path(tmp);children=[]
            with (arena/'runtime.lock').open('w')as lock:
                fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
                st=os.fstat(lock.fileno());roles={}
                try:
                    for role in('server','vanilla','botA'):
                        (arena/role).mkdir()
                        kid=subprocess.Popen([sys.executable,'-c','import time;time.sleep(10)'],cwd=arena/role);children.append(kid)
                        cg=(Path('/proc')/str(kid.pid)/'cgroup').read_text().strip().split(':',2)[-1].rstrip('/').split('/')[-1]
                        roles[role]={'identity':[kid.pid,m.start_ticks(kid.pid)],'unit':cg,'net_namespace_inode':(Path('/proc')/str(kid.pid)/'ns/net').stat().st_ino}
                    config={'arena':tmp,'parent':{'pid':os.getpid(),'start_ticks':m.start_ticks(os.getpid()),'lock_file':[st.st_dev,st.st_ino]},'roles':roles}
                    cp=arena/'config.json';cp.write_text(json.dumps(config))
                    source=str(Path(m.__file__).resolve())
                    code='import importlib.util,json,sys;s=importlib.util.spec_from_file_location("transport",sys.argv[1]);m=importlib.util.module_from_spec(s);sys.path.insert(0,str(__import__("pathlib").Path(sys.argv[1]).parent));s.loader.exec_module(m);m.ownership_gate(json.load(open(sys.argv[2])))'
                    good=subprocess.run([sys.executable,'-c',code,source,str(cp)],capture_output=True,timeout=2)
                    self.assertEqual(good.returncode,0,good.stderr)
                    roles['botA']['identity'][1]+=1;cp.write_text(json.dumps(config))
                    bad=subprocess.run([sys.executable,'-c',code,source,str(cp)],capture_output=True,timeout=2)
                    self.assertNotEqual(bad.returncode,0);self.assertIn(b'own role start changed',bad.stderr)
                finally:
                    for kid in children:kid.terminate();kid.wait(1)

    def test_no_parent_frida_and_disabled_start(self):
        before={n for n in sys.modules if n=='frida'or n.startswith('frida.')}
        with self.assertRaises(RuntimeError):m.WorkerProxy.start('/unused',lambda *x:None)
        self.assertEqual(before,{n for n in sys.modules if n=='frida'or n.startswith('frida.')})

if __name__=='__main__':unittest.main()
