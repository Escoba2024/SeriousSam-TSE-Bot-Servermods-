"""Exact fresh disabled boundary fork; repinning is not authorization."""
import hashlib
import json
from pathlib import Path
import tempfile
import unittest
try:
    from tools import prepare_first_state_getter_boundary as b
except ImportError:b=None


def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()


class BoundaryForkTests(unittest.TestCase):
    def setUp(self):self.assertIsNotNone(b,'boundary fork builder absent')
    def test_fresh_disabled_exact_inverses_and_no_runtime_logic_changes(self):
        with tempfile.TemporaryDirectory()as tmp:
            root=Path(tmp)/'new';r=b.build(root);self.assertTrue(b.verify_package(root)['verified']);self.assertEqual(r['runtime_pins'],151);self.assertEqual(r['method_runtime_pins'],72)
            m=json.loads((root/'source-manifest.json').read_text());self.assertFalse(m['runtime_reviewed']);self.assertFalse(m['native_qualified']);self.assertEqual(m['active_seconds'],10);self.assertEqual(m['admission_budget_seconds'],90)
            self.assertEqual(b.reverse_runner((root/'run_dual.py').read_text()),(b.PARENT/'run_dual.py').read_text())
            parent=json.loads((b.PARENT/'source-manifest.json').read_text());changed=[]
            for path in parent['runtime_dependencies']:
                source=Path(path)
                if source.is_relative_to(b.PARENT):
                    rel=source.relative_to(b.PARENT)
                    if(root/rel).read_bytes()!=source.read_bytes():changed.append(str(rel))
            self.assertEqual(sorted(changed),['method-api/observer_body.js','method-api/source-manifest.json','method-api/vendor/observer/observer.js','run_dual.py'])
    def test_wrong_parent_pin_or_nonfresh_output_rejected(self):
        with tempfile.TemporaryDirectory()as tmp:
            with self.assertRaises(ValueError):b.build(Path(tmp)/'new',parent_manifest_sha256='0'*64)
            with self.assertRaises(FileExistsError):b.build(Path(tmp))
    def test_repinned_body_compiled_g_policy_bindings_rejected(self):
        for relative in('method-api/observer_body.js','method-api/vendor/observer/observer.js','method-api/vendor/observer/observer_policy.py','method-api/vendor/observer/bindings/original-bindings.json'):
            with self.subTest(relative=relative),tempfile.TemporaryDirectory()as tmp:
                root=Path(tmp)/'new';b.build(root);target=root/relative;target.write_bytes(target.read_bytes()+b'\n// repinned')
                cp=root/'method-api/source-manifest.json';c=json.loads(cp.read_text());c['runtime_dependencies'][str(target)]=sha(target);cp.write_text(json.dumps(c));mp=root/'source-manifest.json';m=json.loads(mp.read_text());m['runtime_dependencies'][str(target)]=sha(target);m['runtime_dependencies'][str(cp)]=sha(cp);mp.write_text(json.dumps(m))
                with self.assertRaises(ValueError):b.verify_package(root)
    def test_nested_hash_path_and_limit_semantics_rejected(self):
        for defect in('hash','path','limits'):
            with self.subTest(defect=defect),tempfile.TemporaryDirectory()as tmp:
                root=Path(tmp)/'new';b.build(root);cp=root/'method-api/source-manifest.json';c=json.loads(cp.read_text());key=str(root/'method-api/observer_session.py')
                if defect=='hash':c['runtime_dependencies'][key]='0'*64
                elif defect=='path':c['runtime_dependencies'][key+'-foreign']=c['runtime_dependencies'].pop(key)
                else:c['legacy_limits']['max_records']=65
                cp.write_text(json.dumps(c));mp=root/'source-manifest.json';m=json.loads(mp.read_text());m['runtime_dependencies'][str(cp)]=sha(cp);mp.write_text(json.dumps(m))
                with self.assertRaises(ValueError):b.verify_package(root)
    def test_repinned_helpers_or_unused_gates_rejected(self):
        for relative in('first_state_inputfree_method.py','method-api/first_state_method_transport.py','method-api/original_damage_worker.py','method-api/run_first_state.py','a1_input_worker.py'):
            with self.subTest(relative=relative),tempfile.TemporaryDirectory()as tmp:
                root=Path(tmp)/'new';b.build(root);p=root/relative;p.write_text(p.read_text().replace('RUNTIME_REVIEWED=False','RUNTIME_REVIEWED=True')+'\n# repinned');mp=root/'source-manifest.json';m=json.loads(mp.read_text());m['runtime_dependencies'][str(p)]=sha(p);mp.write_text(json.dumps(m))
                with self.assertRaises(ValueError):b.verify_package(root)
    def test_missing_closure_or_outer_budget_change_rejected(self):
        for defect in('missing','budget','gate'):
            with self.subTest(defect=defect),tempfile.TemporaryDirectory()as tmp:
                root=Path(tmp)/'new';b.build(root);mp=root/'source-manifest.json';m=json.loads(mp.read_text())
                if defect=='missing':m['runtime_dependencies'].pop(str(root/'method-api/observer_session.py'))
                elif defect=='budget':m['inner_budget_seconds']=100
                else:m['runtime_reviewed']=True
                mp.write_text(json.dumps(m))
                with self.assertRaises(ValueError):b.verify_package(root)


if __name__=='__main__':unittest.main()
