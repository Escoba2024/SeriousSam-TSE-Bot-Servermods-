"""Fresh disabled fork, exact parent values and adversarial repinning."""
import hashlib
import json
from pathlib import Path
import tempfile
import unittest
try:
    from tools import prepare_first_state_wine_identity as b
except ImportError:b=None


def digest(path):return hashlib.sha256(path.read_bytes()).hexdigest()


class WineForkTests(unittest.TestCase):
    def setUp(self):self.assertIsNotNone(b,'Wine fork builder absent')

    def test_complete_disabled_closure_and_only_exact_three_source_inverses(self):
        with tempfile.TemporaryDirectory()as tmp:
            root=Path(tmp)/'new';r=b.build(root);self.assertTrue(b.verify_package(root)['verified'])
            self.assertEqual(r['runtime_pins'],151);self.assertEqual(r['method_runtime_pins'],72)
            m=json.loads((root/'source-manifest.json').read_text());self.assertFalse(m['runtime_reviewed']);self.assertFalse(m['native_qualified'])
            parent=json.loads((b.PARENT/'source-manifest.json').read_text());changed=[]
            for source in parent['runtime_dependencies']:
                path=Path(source)
                if not path.is_relative_to(b.PARENT):continue
                rel=path.relative_to(b.PARENT)
                if(root/rel).read_bytes()!=path.read_bytes():changed.append(str(rel))
            self.assertEqual(sorted(changed),['method-api/observer_body.js','method-api/source-manifest.json','method-api/vendor/observer/observer.js','run_dual.py'])
            self.assertEqual(b.reverse_runner((root/'run_dual.py').read_text()),(b.PARENT/'run_dual.py').read_text())
            self.assertEqual(m['active_seconds'],10);self.assertEqual(m['admission_budget_seconds'],90);self.assertEqual(m['fixed_arms'],['control','trace'])

    def test_wrong_parent_pin_and_nonfresh_directory_rejected(self):
        with tempfile.TemporaryDirectory()as tmp:
            with self.assertRaises(ValueError):b.build(Path(tmp)/'new',parent_manifest_sha256='0'*64)
            with self.assertRaises(FileExistsError):b.build(Path(tmp))

    def test_repinned_api_body_policy_bindings_or_compiled_g_still_rejected(self):
        for relative in('method-api/observer_body.js','method-api/vendor/observer/observer_policy.py','method-api/vendor/observer/bindings/original-bindings.json','method-api/vendor/observer/observer.js'):
            with self.subTest(relative=relative),tempfile.TemporaryDirectory()as tmp:
                root=Path(tmp)/'new';b.build(root);target=root/relative;target.write_bytes(target.read_bytes()+b'\n// mutation')
                cm_path=root/'method-api/source-manifest.json';cm=json.loads(cm_path.read_text());cm['runtime_dependencies'][str(target)]=digest(target);cm_path.write_text(json.dumps(cm))
                m_path=root/'source-manifest.json';m=json.loads(m_path.read_text());m['runtime_dependencies'][str(target)]=digest(target);m['runtime_dependencies'][str(cm_path)]=digest(cm_path);m_path.write_text(json.dumps(m))
                with self.assertRaises(ValueError):b.verify_package(root)

    def test_repinned_nested_72_hash_and_path_rejected(self):
        for defect in('hash','path'):
            with self.subTest(defect=defect),tempfile.TemporaryDirectory()as tmp:
                root=Path(tmp)/'new';b.build(root);cm_path=root/'method-api/source-manifest.json';cm=json.loads(cm_path.read_text());key=str(root/'method-api/observer_session.py')
                if defect=='hash':cm['runtime_dependencies'][key]='0'*64
                else:cm['runtime_dependencies'][key+'-foreign']=cm['runtime_dependencies'].pop(key)
                cm_path.write_text(json.dumps(cm));m_path=root/'source-manifest.json';m=json.loads(m_path.read_text());m['runtime_dependencies'][str(cm_path)]=digest(cm_path);m_path.write_text(json.dumps(m))
                with self.assertRaises(ValueError):b.verify_package(root)

    def test_repinned_main_and_unused_input_or_worker_gates_rejected(self):
        for relative in('run_dual.py','method-api/first_state_method_transport.py','method-api/original_damage_worker.py','a1_input_worker.py','first_state_inputfree_method.py'):
            with self.subTest(relative=relative),tempfile.TemporaryDirectory()as tmp:
                root=Path(tmp)/'new';b.build(root);target=root/relative
                text=target.read_text();target.write_text(text.replace('RUNTIME_REVIEWED=False','RUNTIME_REVIEWED=True')+'\n# changed')
                m_path=root/'source-manifest.json';m=json.loads(m_path.read_text());m['runtime_dependencies'][str(target)]=digest(target);m_path.write_text(json.dumps(m))
                with self.assertRaises(ValueError):b.verify_package(root)

    def test_missing_runtime_or_changed_limits_and_scope_rejected(self):
        for defect in('missing','ttl','scope'):
            with self.subTest(defect=defect),tempfile.TemporaryDirectory()as tmp:
                root=Path(tmp)/'new';b.build(root);p=root/'source-manifest.json';m=json.loads(p.read_text())
                if defect=='missing':m['runtime_dependencies'].pop(str(root/'method-api/observer_session.py'))
                elif defect=='ttl':m['inner_budget_seconds']=100
                else:m['scope']='QUALIFIED'
                p.write_text(json.dumps(m))
                with self.assertRaises(ValueError):b.verify_package(root)


if __name__=='__main__':unittest.main()
