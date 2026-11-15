"""Disabled monitor-only derivative; scheduler remains explicitly unqualified."""
import hashlib
import json
from pathlib import Path
import tempfile
import unittest
try:
    from tools import prepare_first_state_method_monitor as b
except ImportError:b=None


def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()


class MethodMonitorFork(unittest.TestCase):
    def setUp(self):self.assertIsNotNone(b,'method monitor builder absent')
    def test_fresh_disabled_all_pins_and_unchanged_observer(self):
        with tempfile.TemporaryDirectory()as tmp:
            root=Path(tmp)/'new';r=b.build(root);self.assertTrue(b.verify_package(root)['verified']);self.assertEqual(r['runtime_pins'],151);self.assertEqual(r['method_runtime_pins'],72)
            m=json.loads((root/'source-manifest.json').read_text());self.assertFalse(m['runtime_reviewed']);self.assertFalse(m['native_ready']);self.assertFalse(m['scheduler_implemented']);self.assertTrue(m['new_matched_control_required']);self.assertEqual(m['native_summary_scope'],'JOIN_PREARM_ONLY')
            for rel in('method-api/observer_body.js','method-api/vendor/observer/observer.js','method-api/first_state_method_transport.py','method-api/original_damage_worker.py','method-api/run_first_state.py'):self.assertEqual((root/rel).read_bytes(),(b.PARENT/rel).read_bytes())
            self.assertEqual(b.patch.reverse_runner((root/'run_dual.py').read_text()),(b.PARENT/'run_dual.py').read_text());self.assertEqual(b.patch.reverse_helper((root/'first_state_inputfree_method.py').read_text()),(b.PARENT/'first_state_inputfree_method.py').read_text())
    def test_wrong_parent_and_existing_output_rejected(self):
        with tempfile.TemporaryDirectory()as tmp:
            with self.assertRaises(ValueError):b.build(Path(tmp)/'new',parent_manifest_sha256='0'*64)
            with self.assertRaises(FileExistsError):b.build(Path(tmp))
    def test_repinned_monitor_observer_worker_policy_or_gates_rejected(self):
        for rel in('run_dual.py','first_state_inputfree_method.py','method-api/observer_body.js','method-api/vendor/observer/observer.js','method-api/first_state_method_transport.py','method-api/vendor/observer/observer_policy.py'):
            with self.subTest(rel=rel),tempfile.TemporaryDirectory()as tmp:
                root=Path(tmp)/'new';b.build(root);target=root/rel;target.write_bytes(target.read_bytes()+b'\n# repinned')
                cm=root/'method-api/source-manifest.json';c=json.loads(cm.read_text())
                if str(target)in c['runtime_dependencies']:c['runtime_dependencies'][str(target)]=sha(target);cm.write_text(json.dumps(c))
                mp=root/'source-manifest.json';m=json.loads(mp.read_text());m['runtime_dependencies'][str(target)]=sha(target);m['runtime_dependencies'][str(cm)]=sha(cm);mp.write_text(json.dumps(m))
                with self.assertRaises(ValueError):b.verify_package(root)
    def test_scope_budget_closure_and_scheduler_claim_cannot_be_repinned(self):
        for defect in('missing','budget','ready','control'):
            with self.subTest(defect=defect),tempfile.TemporaryDirectory()as tmp:
                root=Path(tmp)/'new';b.build(root);mp=root/'source-manifest.json';m=json.loads(mp.read_text())
                if defect=='missing':m['runtime_dependencies'].pop(str(root/'method-api/observer_session.py'))
                elif defect=='budget':m['admission_budget_seconds']=100
                elif defect=='ready':m['scheduler_implemented']=m['native_ready']=True
                else:m['new_matched_control_required']=False
                mp.write_text(json.dumps(m))
                with self.assertRaises(ValueError):b.verify_package(root)


if __name__=='__main__':unittest.main()
