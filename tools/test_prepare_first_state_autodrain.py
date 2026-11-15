"""Fresh disabled derivative: exact parent bytes/hash VALUES, not self-repins."""
import copy
import hashlib
import importlib.util
import json
from pathlib import Path
import tempfile
import unittest

TOOL = Path(__file__).with_name('prepare_first_state_autodrain.py')


def module():
    spec = importlib.util.spec_from_file_location('prepare_autodrain', TOOL)
    result = importlib.util.module_from_spec(spec); spec.loader.exec_module(result); return result


class BuilderTests(unittest.TestCase):
    def setUp(self):
        self.assertTrue(TOOL.exists(), 'disabled autonomous package builder missing')
        self.m = module(); self.tmp = tempfile.TemporaryDirectory(); self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)/'fresh-disabled'

    def create(self): return self.m.build(self.root)

    def test_actual_full_parent_inverse_and_new_closure(self):
        receipt = self.create()
        self.assertEqual((receipt['runtime_pins'],receipt['method_runtime_pins'],receipt['unchanged_parent_files']), (154,75,90))
        self.assertFalse(receipt['native_ready'])
        manifest = json.loads((self.root/'source-manifest.json').read_text())
        self.assertTrue(manifest['new_matched_control_required'])
        self.assertFalse(manifest['prior_control_transfer_authorized'])
        self.assertEqual(self.m.verify_package(self.root), {k:v for k,v in receipt.items() if k!='manifest_sha256'})

    def repin(self, relative):
        path = self.root/relative; path.write_bytes(path.read_bytes()+b'\n# repinned drift\n')
        p = self.root/'source-manifest.json'; m = json.loads(p.read_text())
        m['runtime_dependencies'][str(path)] = hashlib.sha256(path.read_bytes()).hexdigest()
        c = self.root/'method-api/source-manifest.json'; cm = json.loads(c.read_text())
        if str(path) in cm['runtime_dependencies']:
            cm['runtime_dependencies'][str(path)] = m['runtime_dependencies'][str(path)]
            c.write_bytes(self.m.dump(cm))
            m['runtime_dependencies'][str(c)] = hashlib.sha256(c.read_bytes()).hexdigest()
            m['method_api']['manifest_sha256'] = m['runtime_dependencies'][str(c)]
        p.write_bytes(self.m.dump(m))

    def test_self_repinned_immutable_policy_or_new_worker_rejected(self):
        self.create()
        for name in ('method-api/observer_body.js','method-api/vendor/observer/observer_policy.py',
                     'method-api/first_state_autodrain_worker.py','transaction.py'):
            with self.subTest(name=name):
                saved = {p:p.read_bytes() for p in (self.root/name,self.root/'source-manifest.json',self.root/'method-api/source-manifest.json')}
                self.repin(name)
                with self.assertRaises(Exception): self.m.verify_package(self.root)
                for path,data in saved.items(): path.write_bytes(data)

    def test_nested_hash_values_and_metadata_limits_cannot_be_self_approved(self):
        self.create(); path = self.root/'source-manifest.json'; original = path.read_bytes()
        for field,value in (('native_ready',True),('new_matched_control_required',False),
                             ('scheduler_review_required',False)):
            m = json.loads(original); m[field] = value; path.write_bytes(self.m.dump(m))
            with self.subTest(field=field), self.assertRaises(Exception): self.m.verify_package(self.root)
        path.write_bytes(original)
        cm = self.root/'method-api/source-manifest.json'; m = json.loads(cm.read_text())
        key = next(iter(m['runtime_dependencies'])); m['runtime_dependencies'][key] = '0'*64
        cm.write_bytes(self.m.dump(m)); parent = json.loads(original)
        parent['runtime_dependencies'][str(cm)] = hashlib.sha256(cm.read_bytes()).hexdigest()
        parent['method_api']['manifest_sha256'] = parent['runtime_dependencies'][str(cm)]
        path.write_bytes(self.m.dump(parent))
        with self.assertRaises(Exception): self.m.verify_package(self.root)

    def test_wrong_parent_and_existing_output_are_not_overwritten(self):
        with self.assertRaises(Exception): self.m.build(self.root,parent_manifest_sha256='0'*64)
        self.assertFalse(self.root.exists())
        self.create(); before = (self.root/'source-manifest.json').read_bytes()
        with self.assertRaises(FileExistsError): self.m.build(self.root)
        self.assertEqual((self.root/'source-manifest.json').read_bytes(),before)


if __name__ == '__main__': unittest.main()
