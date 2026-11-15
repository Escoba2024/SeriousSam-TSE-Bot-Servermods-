"""Private package closure/inverse checks; contains no machine bytes."""
import hashlib
import json
from pathlib import Path
import tempfile
import unittest
try:
    from tools import prepare_first_state_method_adapter as b
except ImportError:b=None


class DisabledPackageTests(unittest.TestCase):
    def setUp(self):self.assertIsNotNone(b,'disabled builder absent')
    def test_private_new_package_pins_inverse_and_unchanged_runner(self):
        with tempfile.TemporaryDirectory()as tmp:
            root=Path(tmp)/'package';receipt=b.build(root)
            self.assertEqual(receipt['status'],'DISABLED_METHOD_ADAPTER_API_ONLY')
            self.assertFalse(receipt['runner_integrated']);self.assertEqual(receipt['original_restore_regions'],38)
            m=json.loads((root/'source-manifest.json').read_text())
            self.assertFalse(m['runtime_reviewed']);self.assertFalse(m['qualified'])
            self.assertEqual((root/'run_first_state.py').read_bytes(),(b.PARENT/'run_first_state.py').read_bytes())
            self.assertTrue(b.verify_package(root)['verified'])
            self.assertEqual((root/'source-manifest.json').stat().st_mode&0o777,0o600)
            self.assertEqual(receipt['body_inverse_sha256'],b.PATCH.PARENT_BODY_SHA256)
            self.assertEqual(m['transport_limits'],{'observer_payload_bytes':2097152,'ipc_envelope_bytes':16384})
    def test_fresh_only(self):
        with tempfile.TemporaryDirectory()as tmp:
            with self.assertRaises(FileExistsError):b.build(Path(tmp))
    def test_wrong_parent_manifest_fail_closed(self):
        with tempfile.TemporaryDirectory()as tmp:
            with self.assertRaises(ValueError):b.build(Path(tmp)/'out',parent_manifest_sha256='0'*64)
    def test_runner_bindings_or_gate_mutation_rejected(self):
        with tempfile.TemporaryDirectory()as tmp:
            root=Path(tmp)/'package';b.build(root)
            for relative in('run_first_state.py','vendor/observer/bindings/original-bindings.json','first_state_method_transport.py'):
                p=root/relative;old=p.read_bytes();p.write_bytes(old+b'\nMUTATED')
                with self.assertRaises(ValueError):b.verify_package(root)
                p.write_bytes(old)
            manifest=root/'source-manifest.json';old=manifest.read_text();m=json.loads(old);m['runtime_reviewed']=True;manifest.write_text(json.dumps(m))
            with self.assertRaises(ValueError):b.verify_package(root)
    def test_unused_legacy_cli_gate_cannot_be_reactivated_even_repin(self):
        with tempfile.TemporaryDirectory()as tmp:
            root=Path(tmp)/'package';b.build(root)
            worker=root/'original_damage_worker.py';worker.write_text(worker.read_text().replace('RUNTIME_REVIEWED=False','RUNTIME_REVIEWED=True'))
            manifest=root/'source-manifest.json';m=json.loads(manifest.read_text());m['runtime_dependencies'][str(worker)]=hashlib.sha256(worker.read_bytes()).hexdigest();manifest.write_text(json.dumps(m))
            with self.assertRaises(ValueError):b.verify_package(root)

    def test_missing_runtime_binding_is_rejected(self):
        with tempfile.TemporaryDirectory()as tmp:
            root=Path(tmp)/'package';b.build(root)
            manifest=root/'source-manifest.json';m=json.loads(manifest.read_text());del m['runtime_dependencies'][str(root/'native_first_state.py')];manifest.write_text(json.dumps(m))
            with self.assertRaises(ValueError):b.verify_package(root)

    def test_observer_guard_mutation_even_repin_fails_inverse(self):
        with tempfile.TemporaryDirectory()as tmp:
            root=Path(tmp)/'package';b.build(root)
            body=root/'observer_body.js';body.write_text(body.read_text().replace("'TLS index changed'","'MUTATED'"))
            m=json.loads((root/'source-manifest.json').read_text());m['runtime_dependencies'][str(body)]=hashlib.sha256(body.read_bytes()).hexdigest();(root/'source-manifest.json').write_text(json.dumps(m))
            with self.assertRaises(ValueError):b.verify_package(root)

if __name__=='__main__':unittest.main()
