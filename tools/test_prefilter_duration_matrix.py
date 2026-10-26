import copy
import hashlib
import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

import run_prefilter_duration_matrix as m

class MatrixContractTests(unittest.TestCase):
    def policy(self):
        return {'candidate_sha256':'a'*64, 'stages':[{'bots':b,'required_s':s,'duration_s':d,
            'root':str(m.RUNTIME_PARENT/('tse-session-qualification-master-m1-prefilter-'+label+'-20261026')),
            'config':str(m.CONFIG_BASE/name),'port':port,'display':display}
            for b,s,d,label,name,port,display in m.STAGE_CONTRACT],
            'harness_sha256':{n:'b'*64 for n in m.PRODUCER_NAMES}}
    def test_exact_matrix_contract_accepts_only_three_complete_stages(self):
        policy=self.policy()
        m.validate_stage_contract(policy)
        for variant in ('empty','duplicate','wrong_duration','short_requirement','wrong_root','port','display'):
            p=copy.deepcopy(policy)
            if variant=='empty':p['stages']=[]
            if variant=='duplicate':p['stages'][2]=copy.deepcopy(p['stages'][1])
            if variant=='wrong_duration':p['stages'][0]['duration_s']=10
            if variant=='short_requirement':p['stages'][2]['required_s']=3600
            if variant=='wrong_root':p['stages'][0]['root']='/srv/public'
            if variant=='port':p['stages'][0]['port']=25600
            if variant=='display':p['stages'][0]['display']=':0'
            with self.subTest(variant=variant),self.assertRaises(ValueError):m.validate_stage_contract(p)
    def test_verdict_cannot_accept_rejected_short_wrong_candidate_or_bot_count(self):
        policy=self.policy();stage=policy['stages'][2]
        good={'status':'DURATION_RECEIPTS_ACCEPTED','bots':8,'required_s':7200,
              'continuous_full_population_s':7201,'dll_sha256':'a'*64,'reasons':[],'m1_complete':False}
        m.require_stage_verdict(good,stage,policy['candidate_sha256'])
        for field,value in [('status','REJECTED'),('bots',4),('required_s',3600),
                            ('continuous_full_population_s',7199),('dll_sha256','c'*64),('reasons',['gap'])]:
            v=copy.deepcopy(good);v[field]=value
            with self.subTest(field=field),self.assertRaises(RuntimeError):m.require_stage_verdict(v,stage,'a'*64)
    def test_source_pin_drift_missing_file_or_empty_inventory_block(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)/'source.py';p.write_text('unchanged')
            pins={str(p):hashlib.sha256(p.read_bytes()).hexdigest()}
            m.verify_file_pins(pins)
            p.write_text('changed')
            with self.assertRaises(RuntimeError):m.verify_file_pins(pins)
            p.unlink()
            with self.assertRaises(RuntimeError):m.verify_file_pins(pins)
            with self.assertRaises(RuntimeError):m.verify_file_pins({})
    def test_fixed_outer_command_has_no_inner_and_explicit_native_flag(self):
        stage=self.policy()['stages'][0];cmd=m.build_command(stage)
        self.assertEqual(cmd[:2],['/usr/bin/python3','-u'])
        self.assertNotIn('--inner',cmd)
        self.assertIn('--execute',cmd)
        self.assertEqual(cmd[cmd.index('--runtime')+1],stage['root'])
        self.assertEqual(cmd[cmd.index('--duration')+1],'3720')
    def test_default_cli_is_read_only_without_native_or_policy_creation(self):
        script=Path(m.__file__)
        with tempfile.TemporaryDirectory() as d:
            p=subprocess.run([sys.executable,str(script)],cwd=d,capture_output=True,text=True)
            self.assertEqual(p.returncode,0,p.stderr)
            self.assertEqual(json.loads(p.stdout)['status'],'DRY_RUN_NO_NATIVE_ACTIONS')
            self.assertEqual(list(Path(d).iterdir()),[])
    def test_import_has_no_cli_side_effects(self):
        spec=importlib.util.spec_from_file_location('matrix_import_only',m.__file__)
        module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
        self.assertTrue(callable(module.main))


class MatrixLifecycleTests(unittest.TestCase):
    def test_state_and_hold_created_during_lock_acquisition_are_preserved(self):
        from unittest.mock import patch
        from types import SimpleNamespace
        for marker in ('matrix.json','HOLD.json'):
            with self.subTest(marker=marker),tempfile.TemporaryDirectory() as d:
                base=Path(d);(base/'matrix.lock').touch()
                policy={'stages':[{'root':str(base/'native-not-created')}]}
                original='{"keep":"prior invocation"}'
                support=SimpleNamespace(TOOLS=None,load_pinned_modules=lambda:(None,None),
                    load_owned_process_class=lambda:None,
                    atomic_json=lambda *a,**kw:self.fail('existing state/HOLD must block all writes'))
                with patch.multiple(m,BASE=base,CONFIG_BASE=base,STATE=base/'matrix.json',HOLD=base/'HOLD.json'), \
                     patch.object(m,'read_object',return_value=policy),patch.object(m,'verify_policy'), \
                     patch.object(m,'load_module',return_value=support), \
                     patch.object(m.os,'geteuid',return_value=0), \
                     patch.object(m.os,'uname',return_value=SimpleNamespace(nodename='ubuntu-4gb-nbg1-2')), \
                     patch.object(m.fcntl,'flock',side_effect=lambda *a:(base/marker).write_text(original)), \
                     patch.object(sys,'argv',['matrix','--execute','--policy-sha256','a'*64]):
                    with self.assertRaisesRegex(RuntimeError,'fresh matrix'):
                        m.main()
                self.assertEqual((base/marker).read_text(),original)

    def lifecycle(self, mode):
        from unittest.mock import patch
        from types import SimpleNamespace
        with tempfile.TemporaryDirectory() as d:
            base=Path(d);root=base/'native';root.mkdir()
            (root/'result.json').write_text('{}')
            class Child:
                pid=12345
                returncode=None
                waited=0
                def poll(self):return self.returncode
                def wait(self,timeout):
                    self.waited+=1
                    if mode=='ambiguous_timeout':raise subprocess.TimeoutExpired('synthetic',timeout)
                    self.returncode=1;return 1
            child=Child();aborts=[]
            class Owned:
                start_ticks=123
                def __init__(self,p):
                    if mode=='binding_failure':raise RuntimeError('bind failed')
                    self.process=p
                def close(self):pass
            def abort(owned,timeout):
                aborts.append('owned_only');child.returncode=1
                if mode=='abort_timeout':child.returncode=None;raise RuntimeError('owned abort timeout')
            def read(path):
                if mode in ('ambiguous','ambiguous_timeout'):raise RuntimeError('unreadable JSON')
                return {'status':'FAIL' if mode=='producer_fail' else 'MEASURING'}
            def atomic(path,value,**kw):Path(path).write_text(json.dumps(value))
            def heartbeat(*a,**kw):raise RuntimeError('synthetic heartbeat loss')
            support=SimpleNamespace(TOOLS=None,ROOT=None,BOTS=None,DURATION_S=None,
                derive_budget=lambda c:{'total_s':10,'abort_wait_s':1,'cleanup_s':1},
                atomic_json=atomic,check_live_heartbeat=heartbeat,
                request_orderly_abort=abort,
                wait_for_clean_census=lambda *a,**kw:{'clean':child.poll() is not None,'errors':[]})
            state={'status':'STARTING','stages':[],'m1_complete':False}
            stage={'root':str(root),'bots':1,'duration_s':3720,'config':str(base/'config'),'required_s':3600}
            policy={'source_sha256':{},'harness_sha256':{},'candidate_sha256':'a'*64}
            # Root is made by synthetic Popen, just like real producer initialization.
            def popen(*a,**kw):
                root.mkdir(exist_ok=True)
                for name in ('result.json','host-guard.json','source-sha256.json','samples.jsonl'):
                    (root/name).write_text('{}')
                if mode=='clean':child.returncode=0
                return child
            (root/'result.json').unlink();root.rmdir()
            verdict={'status':'DURATION_RECEIPTS_ACCEPTED','bots':1,'required_s':3600,
                'continuous_full_population_s':3601,'dll_sha256':'a'*64,'reasons':[],'m1_complete':False}
            acceptance=SimpleNamespace(evaluate_runtime=lambda *a,**kw:verdict)
            with patch.multiple(m,BASE=base,STATE=base/'state.json',HOLD=base/'HOLD.json'), \
                 patch.object(m,'verify_policy'),patch.object(m,'read_object',return_value={}), \
                 patch.object(m,'build_command',return_value=['synthetic-never-executed']), \
                 patch.object(m.subprocess,'Popen',side_effect=popen),patch.object(m.time,'sleep'):
                if mode=='clean':
                    m.run_stage(stage,policy,'b'*64,support,read,acceptance,Owned,state)
                else:
                    with self.assertRaises(RuntimeError):
                        m.run_stage(stage,policy,'b'*64,support,read,acceptance,Owned,state)
            if mode=='clean':
                self.assertEqual(len(state['stages']),1)
                self.assertFalse(state['m1_complete'])
                self.assertNotIn('active',state)
                return child.waited,aborts,state['status'],(base/'HOLD.json').exists()
            self.assertEqual(state['stages'],[])
            self.assertFalse(state['m1_complete'])
            persisted=json.loads((base/'state.json').read_text())
            self.assertIn(persisted['status'],('BLOCKED','CLEANUP_HOLD'))
            return child.waited,aborts,persisted['status'],(base/'HOLD.json').exists()

    def test_unreadable_result_retains_bounded_supervision_without_blind_signal(self):
        waited,aborts,status,hold=self.lifecycle('ambiguous')
        self.assertEqual(waited,1)
        self.assertEqual(aborts,[])
        self.assertEqual(status,'CLEANUP_HOLD')
        self.assertTrue(hold)

    def test_ambiguous_cleanup_timeout_persists_hold(self):
        waited,aborts,status,hold=self.lifecycle('ambiguous_timeout')
        self.assertEqual(waited,1)
        self.assertEqual(aborts,[])
        self.assertTrue(hold)
        self.assertEqual(status,'CLEANUP_HOLD')

    def test_validated_producer_fail_waits_without_second_signal(self):
        waited,aborts,status,hold=self.lifecycle('producer_fail')
        self.assertEqual(waited,1)
        self.assertEqual(aborts,[])
        self.assertEqual(status,'BLOCKED')

    def test_active_owned_child_receives_one_orderly_abort(self):
        waited,aborts,status,hold=self.lifecycle('active')
        self.assertEqual(aborts,['owned_only'])
        self.assertEqual(status,'BLOCKED')

    def test_abort_timeout_or_binding_failure_persists_hold(self):
        for mode in ('abort_timeout','binding_failure'):
            with self.subTest(mode=mode):
                waited,aborts,status,hold=self.lifecycle(mode)
                self.assertTrue(hold)
                self.assertEqual(status,'CLEANUP_HOLD')

    def test_clean_stage_preserves_receipts_without_claiming_m1(self):
        waited,aborts,status,hold=self.lifecycle('clean')
        self.assertEqual(aborts,[])
        self.assertFalse(hold)

if __name__=='__main__':unittest.main()
