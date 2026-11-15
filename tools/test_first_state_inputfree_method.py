"""Input-free method orchestration with fake clocks/ports, no runtime imports."""
from pathlib import Path
import sys
import tempfile
import types
import unittest
from unittest.mock import patch
try:
    from tools import first_state_inputfree_method as m
except ImportError:m=None


class Clock:
    def __init__(self,value=1):self.value=value
    def __call__(self):return self.value
    def sleep(self,t):self.value+=t


def finished_trace():
    identity={'pid':123,'start_ticks':456}
    events=[{'kind':'process_game_tick','call_id':1,'edge':edge,'thread_id':123,'data':{'scope':'context'}}for edge in('enter','leave')]
    return {'status':'OBSERVER_TRANSPORT_COMPLETE_ONLY','errors':[], 'packets':[{'events':events,'tls_binding':{'thread_id':123},'identity':identity}],
      'external_restore':{'script_unloaded':True,'session_detached':True,'prior_errors':[],'regions':{str(i):{}for i in range(38)}}}


class MethodTests(unittest.TestCase):
    def setUp(self):self.assertIsNotNone(m,'method orchestration absent');self.tmp=tempfile.TemporaryDirectory();self.addCleanup(self.tmp.cleanup)
    def window(self,mode='control',clock=None):
        clock=clock or Clock();ops=[];record={};evidence=Path(self.tmp.name)/str(len(list(Path(self.tmp.name).iterdir())));evidence.mkdir();records={r:{'identity':[100+i,200+i],'closed':False}for i,r in enumerate(('server','vanilla','botA'))}
        w=m.MethodWindow(mode=mode,api_root=Path(self.tmp.name)/'method-api',arena=Path(self.tmp.name),evidence=evidence,parent_started=0,frame={},records=records,pins={},own_identity=lambda r:ops.append('identity:'+r),unit=lambda r:'own-'+r+'.service',periodic=lambda:ops.append('periodic'),save=lambda:None,record=record,clock=clock,sleep=clock.sleep)
        return w,clock,ops
    def fake_api(self,ops,*,start_error=False):
        class Context:
            def __init__(self,*a):ops.append('context');self.expected={'pid':123,'start_ticks':456}
            def require_original_regions(self):return {str(i):{}for i in range(38)}
            def close(self):ops.append('context-close')
        class Proxy:
            pid=500;start_ticks=600
            @classmethod
            def start(cls,*a):ops.append('worker-start');return cls()
            def finish_after_roles_closed(self,*,roles_closed):
                if roles_closed is not True:raise RuntimeError('roles remain')
                ops.append('worker-reap');return {'reaped':True}
        class Observer:
            def __init__(self,identity,config,ports,*,deadline):ops.append(('config',config,deadline));self.result=finished_trace()
            def start(self):
                ops.append('observer-start')
                if start_error:raise RuntimeError('arm fail')
            def poll(self):ops.append('drain');return {'tls_bound':True,'in_flight':0}
            def mark_cutoff(self):ops.append('cutoff')
            def finish(self):ops.append('stop-finaldrain-unload-detach-external');return self.result
        return types.SimpleNamespace(NativeContext=Context),types.SimpleNamespace(WorkerProxy=Proxy,WireArchive=lambda p:None,LegacyWorkerPorts=lambda *a:types.SimpleNamespace(finish_after_roles_closed=Proxy().finish_after_roles_closed)),types.SimpleNamespace(ObserverSession=Observer)
    def run_trace(self,*,clock=None,start_error=False):
        w,c,ops=self.window('trace',clock)
        with patch.object(m,'load_trace_api',return_value=self.fake_api(ops,start_error=start_error)),patch.object(m,'worker_config',return_value={'mock':True}):
            w.run()
        return w,c,ops
    def test_control_exact_ten_seconds_no_api_or_worker_import(self):
        w,c,ops=self.window()
        with patch.object(m,'load_trace_api',side_effect=AssertionError('trace import forbidden')):w.run()
        self.assertAlmostEqual(c.value,11);self.assertEqual(w.record['observed_seconds'],10)
        self.assertFalse(w.record['worker_created']);self.assertNotIn('worker-start',ops)
        w.finish_before_roles();w.finish_after_roles_closed(roles_closed=True)
    def test_control_rejects_foreign_preloaded_frida(self):
        w,c,ops=self.window()
        with patch.dict(sys.modules,{'frida':types.ModuleType('frida')}):
            with self.assertRaises(RuntimeError):w.run()
    def test_setup_cost_consumes_original_budget(self):
        w,c,ops=self.window(clock=Clock(76))
        with self.assertRaises(RuntimeError):w.run()
        self.assertNotIn('periodic',ops)
    def test_context_cost_expired_budget_prevents_worker_or_arm(self):
        w,c,ops=self.window('trace',Clock(74));nat,transport,session=self.fake_api(ops)
        old=nat.NativeContext
        class SlowContext(old):
            def require_original_regions(self):c.value=90;return super().require_original_regions()
        nat.NativeContext=SlowContext
        with patch.object(m,'load_trace_api',return_value=(nat,transport,session)),patch.object(m,'worker_config',return_value={'mock':True}):
            with self.assertRaises(RuntimeError):w.run()
        self.assertNotIn('worker-start',ops);self.assertNotIn('observer-start',ops)

    def test_trace_config_exact_limits_and_absolute_deadline(self):
        w,c,ops=self.run_trace();cfg=[x for x in ops if type(x)is tuple][0]
        self.assertEqual(cfg[1],{'pid':123,'start_ticks':456,'max_records':64,'max_damage_calls':1024,'max_order_calls':8192,'max_events':16384,'ttl_ms':15000,'binding_ms':2000,'binding_calls':256})
        self.assertEqual(cfg[2],16);self.assertEqual(w.record['observed_seconds'],10);self.assertIn('cutoff',ops)
    def test_trace_arm_failure_retains_session_and_worker_for_cleanup(self):
        w,c,ops=self.window('trace')
        with patch.object(m,'load_trace_api',return_value=self.fake_api(ops,start_error=True)),patch.object(m,'worker_config',return_value={'mock':True}):
            with self.assertRaises(RuntimeError):w.run()
        self.assertIsNotNone(w.proxy);self.assertIsNotNone(w.observer)
        w.finish_before_roles()
        with self.assertRaises(RuntimeError):w.finish_after_roles_closed(roles_closed=False)
        self.assertNotIn('worker-reap',ops);w.finish_after_roles_closed(roles_closed=True)
        self.assertLess(ops.index('stop-finaldrain-unload-detach-external'),ops.index('worker-reap'))
    def test_trace_late_start_cannot_extend_parent_deadline(self):
        w,c,ops=self.run_trace(clock=Clock(74));cfg=[x for x in ops if type(x)is tuple][0];self.assertEqual(cfg[2],85)
    def test_only_observed_tick_pair_and_tls_can_pass(self):
        w,c,ops=self.run_trace();w.finish_before_roles();w.finish_after_roles_closed(roles_closed=True)
        report=self.good_report();self.assertEqual(m.candidate_status(report,w),'PASS_LIMITED_FIRST_STATE_METHOD_OBSERVED_CALLBACKS_ONLY')
        w.record['observer_cleanup']['packets'][0]['events'].pop()
        self.assertEqual(m.candidate_status(report,w),'FAIL')
    def test_non_authoritative_tick_pair_cannot_qualify(self):
        w,c,ops=self.run_trace();w.finish_before_roles();w.finish_after_roles_closed(roles_closed=True)
        for row in w.record['observer_cleanup']['packets'][0]['events']:row['thread_id']=999;row['data']['scope']='non_main'
        self.assertEqual(m.candidate_status(self.good_report(),w),'FAIL')

    def test_missing_tls_or_restore_or_sticky_error_never_passes(self):
        for defect in('tls','restore','error'):
            w,c,ops=self.run_trace();w.finish_before_roles();w.finish_after_roles_closed(roles_closed=True)
            result=w.record['observer_cleanup']
            if defect=='tls':result['packets'][0]['tls_binding']=None
            if defect=='restore':result['external_restore']['regions'].pop('0')
            if defect=='error':result['errors']=['sticky']
            self.assertEqual(m.candidate_status(self.good_report(),w),'FAIL',defect)
    def good_report(self):return {'status':'CLEANUP_PENDING','errors':[],'cleanup':{r:{'closed':True,'identity':[100+i,200+i]}for i,r in enumerate(('server','vanilla','botA'))},'units_closed_verified':True,'restoration':{'restored':True},'post_close_logs':{'accepted':True}}
    def test_no_generic_upgrade_of_failed_or_incomplete_control(self):
        w,c,ops=self.window();w.run();w.finish_before_roles();w.finish_after_roles_closed(roles_closed=True)
        r=self.good_report();self.assertEqual(m.candidate_status(r,w),'PASS_LIMITED_UNINSTRUMENTED_TWO_ORIGINALS_ONLY')
        for key,value in(('status','FAIL'),('errors',['sticky']),('units_closed_verified',False)):
            bad={**r,key:value};self.assertEqual(m.candidate_status(bad,w),'FAIL')
    def test_invalid_mode_or_nonpositive_deadline_rejected(self):
        with self.assertRaises(ValueError):self.window('other')

if __name__=='__main__':unittest.main()
