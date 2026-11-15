"""Exact private Runnerdelta/72-method-dependency/guard preservation tests."""
import ast
import hashlib
import json
from pathlib import Path
import tempfile
import unittest
try:
    from tools import prepare_first_state_inputfree_method as b
except ImportError:b=None


def functions(text):return {n.name:ast.dump(n,include_attributes=False)for n in ast.parse(text).body if isinstance(n,ast.FunctionDef)}


class BuilderTests(unittest.TestCase):
    def setUp(self):self.assertIsNotNone(b,'window builder absent')
    def test_exact_inverse_and_existing_top_level_functions_unchanged(self):
        old=(b.PARENT/'run_dual.py').read_text();new=b.patch_runner(old)
        self.assertEqual(b.reverse_runner(new),old)
        a=functions(old);c=functions(new)
        for name in a:
            if name!='main':self.assertEqual(c[name],a[name],name)
    def test_no_input_or_worker_import_and_normal_reap_order_in_main(self):
        source=b.patch_runner((b.PARENT/'run_dual.py').read_text());tree=ast.parse(source)
        imports=[n for n in tree.body if isinstance(n,(ast.Import,ast.ImportFrom))]
        self.assertFalse(any('worker'in ast.unparse(n)or'passive_xrecord'in ast.unparse(n)for n in imports))
        main=next(n for n in tree.body if isinstance(n,ast.FunctionDef)and n.name=='main')
        calls=[ast.unparse(n.func)for n in ast.walk(main)if isinstance(n,ast.Call)]
        for name in('X11Transport','Endpoint','instrument_transport','prepare_xtest_transport','action_step','PF.run'):self.assertNotIn(name,calls)
        self.assertNotIn('.focus()',ast.unparse(main));self.assertNotIn('bounded_step',ast.unparse(main))
        self.assertLess(source.index('method.finish_before_roles()'),source.index('cleanup_chain(close,close_displays,archive,restore'))
        self.assertLess(source.index('cleanup_chain(close,close_displays,archive,restore'),source.index('method.finish_after_roles_closed(roles_closed=True)'))
    def test_fresh_disabled_closure_and_all_method_pins(self):
        with tempfile.TemporaryDirectory()as tmp:
            root=Path(tmp)/'new';receipt=b.build(root);m=json.loads((root/'source-manifest.json').read_text())
            self.assertFalse(m['runtime_reviewed']);self.assertEqual(m['fixed_arms'],['control','trace']);self.assertEqual(m['active_seconds'],10);self.assertEqual(m['admission_budget_seconds'],90)
            self.assertEqual(receipt['method_runtime_pins'],72);self.assertTrue(b.verify_package(root)['verified'])
            self.assertEqual((root/'method-api/run_first_state.py').read_bytes(),(b.API/'run_first_state.py').read_bytes())
            self.assertIn('RUNTIME_REVIEWED=False',(root/'method-api/original_damage_worker.py').read_text())
    def test_wrong_parent_pin_or_authorized_guard_mutation_rejected(self):
        with self.assertRaises(ValueError):b.patch_runner((b.PARENT/'run_dual.py').read_text().replace("'normal close timeout:'","'MUTATED'"))
        with tempfile.TemporaryDirectory()as tmp:
            with self.assertRaises(ValueError):b.build(Path(tmp)/'new',parent_manifest_sha256='0'*64)
    def test_missing_method_pin_and_reactivated_unused_gate_rejected(self):
        with tempfile.TemporaryDirectory()as tmp:
            root=Path(tmp)/'new';b.build(root)
            path=root/'source-manifest.json';old=path.read_text();m=json.loads(old);del m['runtime_dependencies'][str(root/'method-api/observer_session.py')];path.write_text(json.dumps(m))
            with self.assertRaises(ValueError):b.verify_package(root)
            path.write_text(old)
            target=root/'a1_input_worker.py';target.write_text(target.read_text().replace('RUNTIME_REVIEWED=False','RUNTIME_REVIEWED=True'))
            m=json.loads(old);m['runtime_dependencies'][str(target)]=hashlib.sha256(target.read_bytes()).hexdigest();path.write_text(json.dumps(m))
            with self.assertRaises(ValueError):b.verify_package(root)
    def test_repinned_api_body_and_policy_cannot_pass(self):
        with tempfile.TemporaryDirectory()as tmp:
            root=Path(tmp)/'new';b.build(root)
            outer=root/'source-manifest.json';nested=root/'method-api/source-manifest.json';old_outer=outer.read_text();old_nested=nested.read_text()
            for relative in('observer_body.js','vendor/observer/observer_policy.py'):
                target=root/'method-api'/relative;old=target.read_bytes();target.write_bytes(old+b'\n# REPINNED MUTATION')
                cm=json.loads(old_nested);cm['runtime_dependencies'][str(target)]=hashlib.sha256(target.read_bytes()).hexdigest();nested.write_text(json.dumps(cm))
                m=json.loads(old_outer);m['runtime_dependencies'][str(target)]=cm['runtime_dependencies'][str(target)];m['runtime_dependencies'][str(nested)]=hashlib.sha256(nested.read_bytes()).hexdigest();outer.write_text(json.dumps(m))
                with self.subTest(relative=relative):
                    with self.assertRaises(ValueError,msg=relative):b.verify_package(root)
                target.write_bytes(old);nested.write_text(old_nested);outer.write_text(old_outer)

    def test_nested_72_mapping_and_hash_must_equal_exact_parent(self):
        with tempfile.TemporaryDirectory()as tmp:
            root=Path(tmp)/'new';b.build(root)
            outer=root/'source-manifest.json';nested=root/'method-api/source-manifest.json';old_outer=outer.read_text();old_nested=nested.read_text()
            for defect in('hash','path'):
                cm=json.loads(old_nested);key=str(root/'method-api/observer_session.py')
                if defect=='hash':cm['runtime_dependencies'][key]='0'*64
                else:cm['runtime_dependencies'][key+'-foreign']=cm['runtime_dependencies'].pop(key)
                nested.write_text(json.dumps(cm));m=json.loads(old_outer);m['runtime_dependencies'][str(nested)]=hashlib.sha256(nested.read_bytes()).hexdigest();outer.write_text(json.dumps(m))
                with self.subTest(defect=defect):
                    with self.assertRaises(ValueError,msg=defect):b.verify_package(root)
                nested.write_text(old_nested);outer.write_text(old_outer)

    def test_repinned_method_helper_cannot_pass(self):
        with tempfile.TemporaryDirectory()as tmp:
            root=Path(tmp)/'new';b.build(root)
            target=root/'first_state_inputfree_method.py';target.write_bytes(target.read_bytes()+b'\n# REPINNED MUTATION')
            path=root/'source-manifest.json';m=json.loads(path.read_text());m['runtime_dependencies'][str(target)]=hashlib.sha256(target.read_bytes()).hexdigest();path.write_text(json.dumps(m))
            with self.assertRaises(ValueError):b.verify_package(root)

    def test_fresh_only_and_no_automatic_sequence(self):
        with tempfile.TemporaryDirectory()as tmp:
            with self.assertRaises(FileExistsError):b.build(Path(tmp))
        source=b.patch_runner((b.PARENT/'run_dual.py').read_text());self.assertIn("required=True",source);self.assertIn("choices=('control','trace')",source)

if __name__=='__main__':unittest.main()
