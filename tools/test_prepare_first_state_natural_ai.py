"""Portable source-plan tests only. Never writes a fork or touches a role."""
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import unittest
try:
    import prepare_first_state_natural_ai as prep
except ImportError:
    prep=None
import first_state_natural_ai_patch as patch
import first_state_natural_ai as policy

P=Path('/srv/tse-a1-first-state-qjs10-v4-disabled-20261115')
def read(p):
    with os.fdopen(os.open(p.resolve(strict=True),os.O_RDONLY|os.O_NOATIME|os.O_NOFOLLOW),'rb')as f:return f.read()

class PreparationTests(unittest.TestCase):
    def test_gate_fingerprint_preserves_qualified_core_without_enabling_main(self):
        self.assertTrue(hasattr(prep,'same_gates'),'missing exact inherited gate comparison')
        for text in (b'RUNTIME_REVIEWED=False\n',b'RUNTIME_REVIEWED=True\n',b'const RUNTIME_REVIEWED = false;\n'):
            prep.same_gates(text,text)
        with self.assertRaises(ValueError):prep.same_gates(b'RUNTIME_REVIEWED=False\n',b'RUNTIME_REVIEWED=True\n')
        with self.assertRaises(ValueError):prep.same_gates(b'RUNTIME_REVIEWED=True\n',b'')
    def test_fresh_exec_method_api_and_parent_resolve_identical_policy(self):
        self.assertTrue(hasattr(prep,'helper_files'),'missing method-api-local policy for fresh Exec')
        files=prep.helper_files(Path(__file__).resolve().parent)
        self.assertEqual(files['first_state_natural_ai.py'],files['method-api/first_state_natural_ai.py'])
        self.assertEqual(files['first_state_natural_ai.py'],read(Path(__file__).with_name('first_state_natural_ai.py')))
    def test_actual_parent_plan_two_sources_and_no_input_protocol_change(self):
        self.assertIsNotNone(prep,'missing reproducible disabled source planner')
        sources={name:read(P/name)for name in patch.PARENT_SHA}
        result=prep.changed_sources(sources)
        self.assertEqual(set(result),set(sources))
        for name,data in result.items():
            self.assertEqual(patch.reverse(name,data.decode()).encode(),sources[name])
        self.assertIn(b'RUNTIME_REVIEWED=False',result['run_dual.py'])
        with self.assertRaises(ValueError):prep.changed_sources(dict(sources,**{'run_dual.py':sources['run_dual.py']+b'\n'}))

    def test_actual_active_config_has_single_fps_and_unchanged_victim(self):
        self.assertIsNotNone(prep,'missing exact actual active config planner')
        parent=read(P/'CecilObserver.ini')
        canonical=read(Path('/srv/tse-a4-build030-hard-reset-v3-timestamps-disabled-20261115/canonical.ini'))
        active=prep.active_config(parent,canonical)
        self.assertEqual(hashlib.sha256(active).hexdigest(),policy.ACTIVE_CONFIG_SHA)
        self.assertEqual(active.count(b'sam_iMaxFPSActive='),1)
        self.assertIn(b'sam_iMaxFPSActive=10;',parent)
        with self.assertRaises(ValueError):prep.active_config(parent.replace(b'Active=10',b'Active=30'),canonical)

    def test_manifest_rebase_never_relabels_external_or_historical_pins(self):
        self.assertIsNotNone(prep,'missing strict dependency rebasing')
        old=Path('/old');new=Path('/new');files={'x':b'new active source'}
        pins={'/old/x':'oldhash','/outside/x':'historical-external-pin'}
        result=prep.repin(pins,old,new,files)
        self.assertEqual(result,{'/new/x':hashlib.sha256(files['x']).hexdigest(),'/outside/x':'historical-external-pin'})
        with self.assertRaises(ValueError):prep.repin({'/old/missing':'no'},old,new,files)

if __name__=='__main__':unittest.main()
