"""Bounded IPC/child-ownership cases, no Frida import or game process."""
import json
import subprocess
import sys
import socket
import time
import unittest
from unittest import mock

import original_damage_worker as worker


class FakeProcess:
    pid=123456789
    returncode=None
    def __init__(self):self.calls=[]
    def poll(self):return self.returncode
    def terminate(self):self.calls.append('terminate')
    def kill(self):self.calls.append('kill')
    def wait(self,timeout):self.calls.append(('wait',timeout));self.returncode=0;return 0


class DamageWorkerProxyTests(unittest.TestCase):
    def proxy(self):
        a,b=socket.socketpair();self.addCleanup(a.close);self.addCleanup(b.close)
        proc=FakeProcess()
        with mock.patch.object(worker,'start_ticks',return_value=77):proxy=worker.WorkerProxy(proc,a)
        return proxy,b,proc

    def test_disabled_start_never_spawns(self):
        with mock.patch.object(worker.subprocess,'Popen')as popen:
            with self.assertRaises(RuntimeError):worker.WorkerProxy.start('/unused')
            popen.assert_not_called()

    def test_fresh_exec_passes_only_socket_and_closes_other_descriptors(self):
        proc=FakeProcess()
        with mock.patch.object(worker,'RUNTIME_REVIEWED',True),mock.patch.object(worker,'start_ticks',return_value=77),\
             mock.patch.object(worker.subprocess,'Popen',return_value=proc)as popen:
            proxy=worker.WorkerProxy.start('/unused')
            try:
                args,kwargs=popen.call_args
                self.assertEqual(args[0][0],worker.sys.executable)
                self.assertEqual(args[0][2:4],['--worker','/unused'])
                self.assertEqual(len(kwargs['pass_fds']),1);self.assertIs(kwargs['close_fds'],True)
                self.assertNotIn('preexec_fn',kwargs)
            finally:proxy.channel.close()

    def test_start_pin_failure_reaps_only_provably_unarmed_child(self):
        proc=FakeProcess()
        with mock.patch.object(worker,'RUNTIME_REVIEWED',True),mock.patch.object(worker,'start_ticks',side_effect=RuntimeError('pin')),\
             mock.patch.object(worker.subprocess,'Popen',return_value=proc):
            with self.assertRaises(RuntimeError):worker.WorkerProxy.start('/unused')
        self.assertEqual(proc.calls,['terminate',('wait',1)])

    def test_no_reply_is_bounded_and_timeout_remains_sticky(self):
        proxy,peer,proc=self.proxy();began=time.monotonic()
        with self.assertRaises(TimeoutError):proxy.call('drain',timeout=.01)
        self.assertLess(time.monotonic()-began,.2);self.assertTrue(proxy.failed)
        with self.assertRaises(RuntimeError):proxy.drain()
        self.assertEqual(proc.calls,[])

    def test_rpc_error_and_reply_identity_mismatch_remain_sticky(self):
        for reply in [dict(id=1,ok=False,error='synthetic RPC error'),dict(id=2,ok=True,result={})]:
            proxy,peer,proc=self.proxy();peer.sendall((json.dumps(reply)+'\n').encode())
            with self.assertRaises(RuntimeError):proxy.call('arm',timeout=.01)
            self.assertTrue(proxy.failed);self.assertEqual(proc.calls,[])

    def test_fixed_arm_drain_close_deadlines_and_cleanup_after_failure(self):
        proxy,peer,proc=self.proxy()
        with mock.patch.object(proxy,'call',return_value={})as call:
            proxy.arm();proxy.drain();proxy.close()
            self.assertEqual(call.call_args_list,[mock.call('arm',timeout=3),mock.call('drain'),mock.call('close',timeout=2,cleanup=True)])

    def test_no_worker_signal_before_normal_roles_closed(self):
        proxy,peer,proc=self.proxy()
        with self.assertRaises(RuntimeError):proxy.finish(roles_closed=False)
        self.assertEqual(proc.calls,[]);self.assertFalse(proxy.reaped)

    def test_only_same_own_child_is_reaped_after_role_quiescence(self):
        proxy,peer,proc=self.proxy();proxy.failed=True
        with mock.patch.object(worker,'start_ticks',return_value=77):result=proxy.finish(roles_closed=True)
        self.assertTrue(result['reaped']);self.assertTrue(result['sticky_failure'])
        self.assertEqual(proc.calls,['terminate',('wait',1)])

    def test_reused_worker_pid_never_receives_signal(self):
        proxy,peer,proc=self.proxy()
        with mock.patch.object(worker,'start_ticks',return_value=78):
            with self.assertRaises(RuntimeError):proxy.finish(roles_closed=True)
        self.assertEqual(proc.calls,[])

    def test_real_fresh_python_child_block_models_attach_without_blocking_parent_cleanup(self):
        a,b=socket.socketpair()
        code="import socket,sys,threading;s=socket.socket(fileno=int(sys.argv[1]));s.recv(65536);threading.Event().wait(60)"
        child=subprocess.Popen([sys.executable,'-c',code,str(b.fileno())],pass_fds=(b.fileno(),),close_fds=True,
                               stdin=subprocess.DEVNULL,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
        b.close()
        try:
            proxy=worker.WorkerProxy(child,a);began=time.monotonic()
            with self.assertRaises(TimeoutError):proxy.call('arm',timeout=.03)
            self.assertLess(time.monotonic()-began,.3)
            with self.assertRaises(RuntimeError):proxy.finish(roles_closed=False)
            self.assertIsNone(child.poll())
            result=proxy.finish(roles_closed=True)
            self.assertTrue(result['reaped']);self.assertTrue(result['sticky_failure'])
            self.assertIsNotNone(child.poll())
        finally:
            a.close()
            if child.poll()is None:child.terminate();child.wait(timeout=1)


if __name__=='__main__':unittest.main()
