"""Actual disabled-parent transforms; no controller/Native execution."""
import ast
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import unittest

ROOT=Path('/srv/tse-a1-registered-first-state-damage-v1-v3-disabled-20261115')
HELPER=Path(__file__).with_name('prepare_a1_original_respawn.py')

def read(p):
    with os.fdopen(os.open(Path(p).resolve(strict=True),os.O_RDONLY|os.O_NOATIME|os.O_NOFOLLOW),'rb')as f:return f.read()

class Preparation(unittest.TestCase):
    def helper(self):
        self.assertTrue(HELPER.exists(),'new normal Original respawn preparer absent')
        spec=importlib.util.spec_from_file_location('prepare_respawn',HELPER);m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);return m

    def test_actual_complete_sources_inverse_no_shared_core_change(self):
        m=self.helper();old={n:read(ROOT/n)for n in m.CHANGED};new=m.changed_sources(old)
        self.assertEqual(set(new),set(m.CHANGED))
        for n in old:
            self.assertEqual(m.reverse_source(n,new[n]),old[n]);
            with self.assertRaises(ValueError):m.reverse_source(n,new[n]+b'\n#foreign mutation\n')
        s=new['run_dual.py'].decode();ast.parse(s)
        self.assertEqual(s.count('colt_preparation=False'),2)
        self.assertIn('original_replica',s);self.assertIn('read_roles=native_roles',s)
        self.assertIn('journal=fire_journal',s);self.assertIn('RP.bind(IMW)',s)
        self.assertIn('FireTransport(pin,',s);self.assertIn('RP.publish_attempts(report,method)',s)
        self.assertIn('RUNTIME_REVIEWED=False',s)
        self.assertNotIn('CP.run_preparation(',s);self.assertNotIn('MW.MethodWindow =',s)
        self.assertNotIn("normal_route_or_fire=False,input_once_proven=False",s)
        self.assertNotIn('OWN_TWO_ORIGINAL_INPUTFREE_FIRST_STATE_METHOD_ONLY',s)
        self.assertEqual(new['natural-ai/active.ini'],old['natural-ai/active.ini'].replace(b'bot_iTestTarget=-1;',b'bot_iTestTarget=0;'))
        self.assertIn(hashlib.sha256(new['natural-ai/active.ini']).hexdigest().encode(),new['first_state_natural_ai.py'])
        self.assertIn(b'ORIGINAL_RESPAWN030_SOURCE_OWNERSHIP_V1',new['first_state_natural_ai.py'])
        self.assertEqual(new['method-api/first_state_natural_ai.py'],new['first_state_natural_ai.py'])

    def test_new_condition_metadata_is_truthful_and_limits_exact(self):
        m=self.helper();outer=json.loads(read(ROOT/'source-manifest.json'));nested=json.loads(read(ROOT/'method-api/source-manifest.json'))
        a,b=m.contracts(outer,nested)
        for old,new in((outer,a),(nested,b)):
            self.assertIs(new['runtime_reviewed'],False);self.assertIs(new['native_qualified'],False)
            self.assertEqual(new['original_respawn_condition']['native_input_attempts'],2)
            self.assertIs(new['original_respawn_condition']['readiness_changed'],True)
            self.assertIs(new['original_respawn_condition']['first_valid_state_damage_proven'],False)
            self.assertEqual(new['registered_damage_contract']['inputs'],2)
            self.assertEqual(new['registered_damage_contract']['queue_full_rows'],64)
            self.assertEqual(new['registered_damage_contract']['max_native_edges'],16384)
            for key in('host_budget','autodrain_limits','transport_limits','legacy_limits'):
                if key in old:self.assertEqual(old[key],new[key])
        self.assertFalse(a['native_ready']);self.assertFalse(a['prior_control_transfer_authorized'])

    def test_source_planner_pins_actual_parent_not_an_arbitrary_fixture(self):
        m=self.helper();old={n:read(ROOT/n)for n in m.CHANGED}
        bad=dict(old);bad['run_dual.py']+=b'\n#unrelated mutation\n'
        with self.assertRaises(ValueError):m.changed_sources(bad)

if __name__=='__main__':unittest.main()
