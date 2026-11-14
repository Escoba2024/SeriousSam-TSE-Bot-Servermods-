"""Socket/subprocess model only. Never imports Frida or launches any game."""
import socket,subprocess,sys,time,unittest
from a1_input_worker import WorkerProxy
from a1_trace_scope import InputScope

class WorkerTests(unittest.TestCase):
    def fake(self,code):
        a,b=socket.socketpair();p=subprocess.Popen([sys.executable,'-c',code,str(b.fileno())],pass_fds=(b.fileno(),),stdin=subprocess.DEVNULL,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL);b.close()
        proxy=WorkerProxy(p,a);self.addCleanup(self.reap,proxy);return proxy
    def reap(self,p):
        p.finish(roles_closed=True)
    def test_hung_rpc_timeout_sticky_and_safe_reap(self):
        p=self.fake('import socket,sys,time;s=socket.socket(fileno=int(sys.argv[1]));s.recv(4096);time.sleep(5)')
        start=time.monotonic()
        with self.assertRaises(TimeoutError):p.call('drain',timeout=.03)
        self.assertLess(time.monotonic()-start,.3)
        with self.assertRaisesRegex(RuntimeError,'sticky'):p.call('drain',timeout=.03)
        self.assertIsNone(p.process.poll())
        with self.assertRaisesRegex(RuntimeError,'roles'):p.finish(roles_closed=False)
        self.assertIsNone(p.process.poll())
        self.assertTrue(p.finish(roles_closed=True)['reaped'])
    def test_tagged_reply_and_mismatched_reply_fail(self):
        for match in(True,False):
            p=self.fake('import socket,sys,json;s=socket.socket(fileno=int(sys.argv[1]));r=json.loads(s.makefile().readline());s.sendall((json.dumps({"id":r["id"]'+(''if match else'+1')+',"ok":True,"result":{"ready":True}})+"\\n").encode())')
            if match:self.assertEqual(p.call('drain',timeout=.5),{'ready':True})
            else:
                with self.assertRaisesRegex(RuntimeError,'reply'):p.call('drain',timeout=.5)
    def test_cleanup_can_be_attempted_after_sticky_failure(self):
        p=self.fake('import socket,sys,json;s=socket.socket(fileno=int(sys.argv[1]));f=s.makefile();r=json.loads(f.readline());s.sendall((json.dumps({"id":r["id"],"ok":False,"error":"fault"})+"\\n").encode());r=json.loads(f.readline());s.sendall((json.dumps({"id":r["id"],"ok":True,"result":{"closed":True,"original_bytes_verified":True}})+"\\n").encode())')
        with self.assertRaisesRegex(RuntimeError,'fault'):p.call('drain',timeout=.5)
        self.assertTrue(p.close()['closed'])
    def test_allowlist_exact_prefix_and_two_forward_only(self):
        s=InputScope()
        for control,pixels in s.PREFIX:s.admit('vanilla',control,.1,pixels)
        s.admit('vanilla','look_horizontal',.1,-2)
        for control in('fire','forward'):
            with self.assertRaises(ValueError):s.admit('vanilla',control,.1,None)
    def test_wrong_role_or_added_input_before_calibration_fails(self):
        for args in [('botA','look_right',.1,None),('vanilla','forward',.1,None),('vanilla','look_right',.2,None)]:
            with self.assertRaises(ValueError):InputScope().admit(*args)

if __name__=='__main__':unittest.main()

class TraceFinalizationTests(unittest.TestCase):
    def report(self):
        return {'status':'TRACE_ONLY_NO_FIRE','observer_mode':'instrumented-trace','collector_requested':True,'shooter_preparation':{'status':'TRACE_ONLY_NO_FIRE'},
            'diagnostic_only':True,'normal_route_or_fire':False,'collector_cleanup':{'closed':True,'original_bytes_verified':True},
            'collector_worker':{'reaped':True},'restoration':{'restored':True},'post_close_logs':{'accepted':True},
            'displays':{154:{'closed':True},155:{'closed':True}}}
    def test_diagnostic_never_requires_or_emits_pass(self):
        from a1_trace_scope import trace_complete
        from types import SimpleNamespace
        report=self.report();self.assertTrue(trace_complete(report,SimpleNamespace(reasons=('window_not_passed',))))
        self.assertEqual(report['status'],'TRACE_ONLY_NO_FIRE')
        for reason in ('recorded_errors','cleanup_not_closed:vanilla'):
            self.assertFalse(trace_complete(report,SimpleNamespace(reasons=('window_not_passed',reason))))
    def test_failed_restore_or_worker_or_fire_can_never_complete(self):
        from a1_trace_scope import trace_complete
        from types import SimpleNamespace
        for section,key in [('restoration','restored'),('collector_worker','reaped'),('collector_cleanup','original_bytes_verified')]:
            r=self.report();r[section][key]=False;self.assertFalse(trace_complete(r,SimpleNamespace(reasons=('window_not_passed',))))
        r=self.report();r['normal_route_or_fire']=True;self.assertFalse(trace_complete(r,SimpleNamespace(reasons=('window_not_passed',))))


class ControlScopeTests(unittest.TestCase):
    def test_control_is_separate_and_requires_no_observer_evidence(self):
        from a1_trace_scope import trace_complete
        from types import SimpleNamespace
        r=TraceFinalizationTests().report();r.update(status='CONTROL_ONLY_NO_FIRE',observer_mode='uninstrumented-control',collector_requested=False)
        for key in ('collector_cleanup','collector_worker'):del r[key]
        self.assertTrue(trace_complete(r,SimpleNamespace(reasons=('window_not_passed',))))
        for key in ('collector_arm','collector_cleanup','collector_worker','collector_ipc_timings'):
            r[key]={};self.assertFalse(trace_complete(r,SimpleNamespace(reasons=('window_not_passed',))));del r[key]
        r['status']='TRACE_ONLY_NO_FIRE';self.assertFalse(trace_complete(r,SimpleNamespace(reasons=('window_not_passed',))))

    def test_start_constructor_failure_reaps_only_unarmed_child(self):
        from unittest import mock
        import a1_input_worker as worker
        process=mock.Mock();process.poll.return_value=None
        with mock.patch.object(worker,'RUNTIME_REVIEWED',True),mock.patch.object(worker.subprocess,'Popen',return_value=process),mock.patch.object(worker,'start_ticks',side_effect=OSError('pin failure')):
            with self.assertRaisesRegex(OSError,'pin failure'):worker.WorkerProxy.start('/not-executed-fixture-config')
        process.terminate.assert_called_once();process.wait.assert_called_once_with(timeout=1)
