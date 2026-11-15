"""Exact helper/runner deltas; no native imports, launches or game inputs."""
import hashlib
import importlib.util
from pathlib import Path
import sys
import tempfile
import types
import unittest
from unittest.mock import patch

PARENT = Path('/srv/tse-a1-first-state-method-monitor-disabled-20261115')
TOOL = Path(__file__).with_name('first_state_autodrain_window_patch.py')


def module():
    spec = importlib.util.spec_from_file_location('autodrain_window_patch', TOOL)
    out = importlib.util.module_from_spec(spec); spec.loader.exec_module(out); return out


class WindowPatchTests(unittest.TestCase):
    def transformed(self):
        self.assertTrue(TOOL.exists(), 'autonomous MethodWindow transform missing')
        p = module(); source = (PARENT/'first_state_inputfree_method.py').read_text()
        m = types.ModuleType('isolated_autodrain_window')
        exec(compile(p.patch_helper(source), '<patched-method-window>', 'exec'), m.__dict__)
        return p, m

    def test_whole_source_inverses_and_wrong_parent_fail(self):
        p, m = self.transformed()
        for name, forward, reverse in (('run_dual.py',p.patch_runner,p.reverse_runner),
                ('first_state_inputfree_method.py',p.patch_helper,p.reverse_helper)):
            source = (PARENT/name).read_text()
            self.assertEqual(reverse(forward(source)), source)
            with self.assertRaises(Exception): forward(source + '# drift\n')

    def test_control_guards_keep_old_names_and_reject_new_qualified_aliases(self):
        p, m = self.transformed()
        for name in ('frida','a1_input_worker','first_state_method_transport',
                'first_state_autodrain_worker','tools.first_state_autodrain_worker',
                'first_state_autodrain_session','tools.first_state_autodrain_protocol',
                'native_first_state','tools.native_first_state','observer_session',
                'frozen_first_state_native','tools.source_loader','a1_frozen_observer_policy'):
            with self.subTest(name=name), patch.dict(sys.modules,{name:types.ModuleType(name)}):
                with self.assertRaises(RuntimeError): m.no_trace_imports()

    def test_no_new_top_level_worker_import_or_changed_numeric_limits(self):
        p, m = self.transformed()
        self.assertEqual((m.ACTIVE_SECONDS,m.INNER_SECONDS,m.OUTER_SECONDS),(10,85,90))
        import ast
        tree = ast.parse(p.patch_helper((PARENT/'first_state_inputfree_method.py').read_text()))
        self.assertFalse(any(isinstance(node,ast.Import) and any('autodrain' in n.name for n in node.names)
                             for node in tree.body))

    def test_candidate_status_is_new_typed_scope_and_never_old_packets_pass(self):
        p, m = self.transformed()
        report = {'status':'CLEANUP_PENDING','errors':[],'units_closed_verified':True,
            'cleanup':{r:{'closed':True} for r in m.ROLES},'restoration':{'restored':True},
            'post_close_logs':{'accepted':True}}
        window = types.SimpleNamespace(mode='trace',proxy=object(),record={
            'observation_complete':True,'observed_seconds':10,'input_emissions':0,
            'before_roles_cleanup_complete':True,'after_roles_cleanup_complete':True,
            'worker_reap':{'reaped':True},'observer_cleanup':{
                'schema':'a1.first-state.autodrain-session.v1',
                'qualified':False,'native_qualified':False,'first_processed_state_proven':False,
                'status':'AUTODRAIN_OBSERVER_TRANSPORT_COMPLETE_ONLY','errors':[],
                'stop_serial':1,'final_serial':2,'coverage_complete':True,'validated_packets':2,
                'packet_receipts':[{'serial':1,'accepted':True},{'serial':2,'accepted':True}],
                'identity':{'pid':7},'tls_binding':{'thread_id':7},'cutoff_sequence':2,
                'main_tick_pair_before_cutoff':True,'observed_callback_kinds_before_cutoff':['process_game_tick'],
                'external_restore':{'script_unloaded':True,'session_detached':True,'prior_errors':[],
                                    'regions':{str(i):{} for i in range(38)}}}})
        self.assertEqual(m.candidate_status(report,window),'PASS_LIMITED_FIRST_STATE_METHOD_OBSERVED_CALLBACKS_ONLY')
        result = window.record['observer_cleanup']
        for key,value in (('schema','old-packets'),('native_qualified',True),
                ('status','OBSERVER_TRANSPORT_COMPLETE_ONLY'),('stop_serial',None),
                ('final_serial',3),('coverage_complete',False),('validated_packets',1),
                ('main_tick_pair_before_cutoff',False)):
            old = result[key]; result[key] = value
            self.assertEqual(m.candidate_status(report,window),'FAIL',key); result[key] = old
        result['tls_binding']['thread_id'] = 8
        self.assertEqual(m.candidate_status(report,window),'FAIL')

    def test_actual_window_uses_batch_api_without_any_new_input_or_limit(self):
        p, m = self.transformed(); operations = []; current = [1.]
        class Context:
            expected = {'pid':1,'start_ticks':2}
            def __init__(self,*args): operations.append('context')
            def require_original_regions(self): return {str(i):{} for i in range(38)}
        class Proxy:
            @classmethod
            def start(cls,*args): operations.append('fresh-worker'); return cls()
        class Session:
            def __init__(self,identity,config,ports,*,deadline):
                operations.append(('config',config,deadline))
            def start(self): operations.append('arm')
            def poll(self): return {'tls_bound':True,'in_flight':0}
            def mark_cutoff(self): operations.append('stop-barrier')
        nat = types.SimpleNamespace(NativeContext=Context)
        transport = types.SimpleNamespace(WorkerProxy=Proxy,legacy=types.SimpleNamespace(WireArchive=lambda evidence:None))
        session = types.SimpleNamespace(ObserverSession=Session,
            BatchPorts=lambda *args:operations.append('batch-ports') or object())
        with tempfile.TemporaryDirectory() as temp:
            evidence = Path(temp); records = {r:{'identity':[1,2]} for r in m.ROLES}
            window = m.MethodWindow(mode='trace',api_root=evidence/'method-api',arena=evidence,evidence=evidence,
                parent_started=0,frame={},records=records,pins={},own_identity=lambda role:None,
                unit=lambda role:role,periodic=lambda:None,save=lambda:None,record={},
                clock=lambda:current[0],sleep=lambda n:current.__setitem__(0,current[0]+n))
            with patch.object(m,'load_trace_api',return_value=(nat,transport,session)),patch.object(m,'worker_config',return_value={'fake':True}):
                window.run()
        self.assertIn('batch-ports',operations); self.assertIn('stop-barrier',operations)
        config = next(row for row in operations if type(row) is tuple)
        self.assertEqual(config[1],{'pid':1,'start_ticks':2,'max_records':64,'max_damage_calls':1024,
            'max_order_calls':8192,'max_events':16384,'ttl_ms':15000,'binding_ms':2000,'binding_calls':256})
        self.assertEqual(config[2],16)
        self.assertEqual(window.record['input_emissions'],0)
        self.assertEqual(window.record['minimum_admission_target_elapsed'],10)


if __name__ == '__main__': unittest.main()
