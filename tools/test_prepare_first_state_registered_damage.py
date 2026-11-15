"""Real parent transformations and strict gate/pin planning; no controller import."""
import hashlib
import importlib.util
import json
from pathlib import Path
import unittest
from tools.test_first_state_registered_damage_patch import read

ROOT=Path('/srv/tse-a1-natural-ai030-two-actor-status-v2-disabled-20261115')
HELPER=Path(__file__).with_name('prepare_first_state_registered_damage.py')

class PrepareRegistered(unittest.TestCase):
    def helper(self):
        self.assertTrue(HELPER.exists(),'new disabled registered-scope preparer absent')
        s=importlib.util.spec_from_file_location('prepare_registered',HELPER);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m

    def test_actual_parent_sources_have_full_inverses_and_disabled_gates(self):
        m=self.helper();old={n:read(ROOT/n)for n in m.CHANGED}
        new=m.changed_sources(old)
        self.assertEqual(set(new),set(m.CHANGED))
        for n in old:self.assertEqual(m.reverse_source(n,new[n]),old[n])
        body=new['method-api/observer_body.js'];compiled=new['method-api/vendor/observer/observer.js']
        self.assertTrue(compiled.endswith(body));self.assertIn(b'const RUNTIME_REVIEWED = false;',compiled)
        self.assertIn(b'PASS_LIMITED_REGISTERED_FIRST_STATE_DAMAGE_METHOD_CALLBACKS_ONLY',new['first_state_inputfree_method.py'])
        self.assertIn(b'cutoff_sequence_domain',new['first_state_inputfree_method.py'])
        self.assertIn(b'REGISTERED_FIRST_STATE_DAMAGE_V1',new['first_state_inputfree_method.py'])
        for n in old:
            with self.subTest(source=n):
                with self.assertRaises(ValueError):m.reverse_source(n,new[n]+b'\n#foreign edit\n')

    def test_manifest_contract_has_no_scope_or_runtime_transfer(self):
        m=self.helper();outer=json.loads(read(ROOT/'source-manifest.json'));nested=json.loads(read(ROOT/'method-api/source-manifest.json'))
        a,b=m.contracts(outer,nested)
        for x in(a,b):
            self.assertIs(x['runtime_reviewed'],False);self.assertIs(x['native_qualified'],False)
            self.assertEqual(x['registered_damage_contract']['measurement_scope'],'REGISTERED_FIRST_STATE_DAMAGE_V1')
            self.assertFalse(x['registered_damage_contract']['first_state_proven'])
            self.assertEqual(x['registered_damage_contract']['queue_full_rows'],64)
            self.assertEqual(x['registered_damage_contract']['max_native_edges'],16384)
        self.assertEqual(a['host_budget'],outer['host_budget'])
        self.assertEqual(a['autodrain_limits'],outer['autodrain_limits'])
        self.assertFalse(a['native_ready']);self.assertFalse(a['prior_control_transfer_authorized'])

if __name__=='__main__':unittest.main()
