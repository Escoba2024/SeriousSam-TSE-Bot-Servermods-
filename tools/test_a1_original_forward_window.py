"""New window integration with actual parent control class, pure game/read ports."""
import copy
import importlib.util
from pathlib import Path
import tempfile
import unittest
from types import SimpleNamespace
import a1_original_forward as F
from test_a1_original_forward import observation
from test_a1_original_forward_ports import rp,Port,Endpoint

class Window(unittest.TestCase):
    def make(self):
        self.assertTrue(hasattr(F,'bind'),'new forward-only window missing')
        R=rp();root=Path('/srv/tse-a1-original-colt-trouble030-v3-disabled-20261115')
        s=importlib.util.spec_from_file_location('forward_legacy',root/'first_state_inputfree_method.py');L=importlib.util.module_from_spec(s);s.loader.exec_module(L)
        state=SimpleNamespace(time=1.,index=0,moved=False)
        T=F.make_transport_class(Port);j=R.FireJournal(lambda:state.time);t=T(journal=j);e=F.make_endpoint_class(Endpoint)(t)
        actual=t.XTestFakeKeyEvent
        def emit(*args):
            result=actual(*args)
            if args[2]:state.moved=True
            return result
        t.XTestFakeKeyEvent=emit
        def native():
            state.time+=.04;state.index+=1
            item=observation(state.time,x=.1 if state.moved else 0.,index=state.index);item['native']['_fixture_context']=item['context'];return item['native']
        class Context:
            def __init__(self,w):self.w=w;self.closed=False
            def require_original_regions(self):return {str(i):'00'for i in range(38)}
            def input_frame(self,n):return copy.deepcopy(n['_fixture_context'])
            def close(self):self.closed=True
        kwargs=dict(mode='control',api_root=root/'method-api',arena=root,evidence=Path(self.enterContext(tempfile.TemporaryDirectory())),parent_started=0.,frame={**observation()['native'],'_fixture_context':observation()['context']},records={},pins={},own_identity=lambda _:None,unit=lambda x:x,periodic=lambda:None,save=lambda:None,record={},clock=lambda:state.time,sleep=lambda v:setattr(state,'time',state.time+v),read_roles=native,endpoint=e,journal=j,context_factory=Context)
        W=F.bind(L,R).MethodWindow;w=W(**kwargs)
        return w,state,t,j
    def test_actual_window_single_pulse_and_separate_cleanup(self):
        w,state,t,j=self.make();w.run();w.finish_before_roles();w.finish_after_roles_closed(roles_closed=True)
        self.assertEqual(t.calls,[1,0]);self.assertEqual(w.record['input_emissions'],2)
        self.assertEqual(w.record['outcome']['status'],'SERVER_OBSERVED_TRANSLATION_ONLY')
        self.assertEqual(w.record['original_regions_before'],w.record['original_regions_after'])
        self.assertTrue(w.record['after_roles_cleanup_complete']);self.assertFalse(w.record['worker_created'])
        self.assertEqual([r['down']for r in w.record['keymap_proofs']],[True,False])
    def test_initial_context_receipt_is_not_reused_as_fresh_baseline(self):
        w,state,t,j=self.make();w.run()
        self.assertEqual(w.record['read_attempts'][0]['status'],'INITIAL_CONTEXT_CUSTODY_ONLY')
        self.assertGreater(w.record['read_attempts'][1]['native']['successful_read_sequence']['index'],0)
    def test_failed_capture_attempt_stored_without_retry(self):
        w,state,t,j=self.make()
        def fail():raise ValueError('actual capture failed')
        w.read_roles=fail
        with self.assertRaisesRegex(ValueError,'capture failed'):w.run()
        self.assertEqual(t.calls,[]);self.assertEqual(len(w.record['read_attempts']),2)
        self.assertIn('capture failed',w.record['read_attempts'][-1]['error'])
    def test_trace_mode_is_denied_before_any_input(self):
        w,state,t,j=self.make();w.mode='trace'
        with self.assertRaisesRegex(ValueError,'control only'):w.run()
        self.assertEqual(t.calls,[])
    def test_full_read_bound_counts_failures_and_initial(self):
        self.assertTrue(hasattr(F,'ownership_reads'),'bounded production ownership wrapper missing')
        R=rp()
        with tempfile.TemporaryDirectory()as directory:
            owner=F.ownership_reads(R,Path(directory),lambda:1.,10.)
            def capture(d):
                import json
                p=d/'natural-ai-ownership.json';p.write_text('{}');p.chmod(0o600);return {'fresh':str(d)}
            for i in range(16):owner.read(capture)
            with self.assertRaisesRegex(ValueError,'16'):owner.read(capture)
            self.assertEqual(len(owner.attempts),16);self.assertTrue(owner.failed)

if __name__=='__main__':unittest.main()
