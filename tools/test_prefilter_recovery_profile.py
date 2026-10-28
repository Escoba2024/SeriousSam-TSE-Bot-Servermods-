import copy
import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
import m1_prefilter_recovery_profile as p

class ProfileTests(unittest.TestCase):
    def matrix(self):
        return {'status':'DURATION_MATRIX_ACCEPTED_PRIVATE_ONLY','m1_complete':False,'stages':[
            {'root':'/srv/tse-session-qualification-master-m1-prefilter-'+name+'-20261028',
             'verdict':{'status':'DURATION_RECEIPTS_ACCEPTED','bots':b,'required_s':s,
                        'continuous_full_population_s':s+1,'dll_sha256':'a'*64,'reasons':[],'m1_complete':False}}
            for b,s,name in [(1,3600,'one-hour-joinsearch-r1'),(4,3600,'four-hour-joinsearch-r1'),(8,7200,'eight-two-hours-joinsearch-r1')]]}
    def test_exact_new_roots_and_full_matrix_required(self):
        matrix=self.matrix()
        self.assertEqual([x[1:] for x in p.validated_stages(matrix,'a'*64)],[(1,3600),(4,3600),(8,7200)])
        for variant in ('empty','duplicate','old_root','wrong_dll','short','false_acceptance','short_actual'):
            m=copy.deepcopy(matrix)
            if variant=='empty':m['stages']=[]
            if variant=='duplicate':m['stages'][2]=copy.deepcopy(m['stages'][1])
            if variant=='old_root':m['stages'][0]['root']='/srv/tse-session-qualification-master-m1-one-hour-20261026'
            if variant=='wrong_dll':m['stages'][2]['verdict']['dll_sha256']='b'*64
            if variant=='short':m['stages'][2]['verdict']['required_s']=3600
            if variant=='false_acceptance':m['status']='BLOCKED'
            if variant=='short_actual':m['stages'][2]['verdict']['continuous_full_population_s']=7199
            with self.subTest(variant=variant),self.assertRaises(ValueError):p.validated_stages(m,'a'*64)
    def test_new_driver_default_does_not_create_native_or_replace_files(self):
        script=Path(p.__file__).with_name('qualify_prefilter_m1_recovery.py')
        with tempfile.TemporaryDirectory() as d:
            base=Path(d);(base/'matrix.json').write_text(json.dumps(self.matrix()))
            marker=base/'recovery-qualification.json';marker.write_text('preserve')
            r=subprocess.run([sys.executable,str(script),'--evidence-root',d],capture_output=True,text=True)
            self.assertEqual(r.returncode,0,r.stderr)
            self.assertFalse(json.loads(r.stdout)['native_actions'])
            self.assertEqual(marker.read_text(),'preserve')
            self.assertEqual(len(list(base.iterdir())),2)
    def test_driver_import_has_no_cli_or_native_effects(self):
        script=Path(p.__file__).with_name('qualify_prefilter_m1_recovery.py')
        spec=importlib.util.spec_from_file_location('prefilter_recovery_import',script)
        module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
        self.assertTrue(callable(module.main))

class RecoveryOwnershipTests(unittest.TestCase):
    def test_binding_failure_keeps_unbound_child_for_cleanup_without_signaling(self):
        active=[None];process=object()
        def failing_owner(child):raise RuntimeError('binding unavailable')
        with self.assertRaises(RuntimeError):
            p.bind_and_track(process,failing_owner,active,Path('/synthetic'),['server'])
        self.assertIs(active[0][0],process)
        self.assertIsNone(active[0][1])
        self.assertEqual(active[0][2],Path('/synthetic'))

    def test_repeated_interrupts_during_cleanup_do_not_raise_or_signal(self):
        cleaning=[False];handler=p.interrupt_handler(cleaning)
        with self.assertRaisesRegex(RuntimeError,'interrupt'):handler(15,None)
        cleaning[0]=True
        for sig in (15,2,15,2):self.assertIsNone(handler(sig,None))

class RecoveryFreshnessTests(unittest.TestCase):
    def test_prior_recovery_state_or_hold_blocks_without_overwrite(self):
        for name in ('recovery-qualification.json','recovery-HOLD.json'):
            with self.subTest(name=name),tempfile.TemporaryDirectory() as d:
                base=Path(d);p.require_fresh_recovery(base)
                path=base/name;path.write_text('preserve previous evidence')
                with self.assertRaises(RuntimeError):p.require_fresh_recovery(base)
                self.assertEqual(path.read_text(),'preserve previous evidence')

if __name__=='__main__':unittest.main()
