"""Offline package provenance and disabled entrypoint tests."""
import hashlib
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
import xrecord_core_controller as c
import prepare_xrecord_core_method as p

class PackageTests(unittest.TestCase):
 def test_package_is_fresh_exact_pinned_and_all_three_gates_are_disabled(self):
  with tempfile.TemporaryDirectory()as d:
   root=Path(d)/'package';manifest=p.prepare(root)
   self.assertEqual(manifest['schema'],'OWN_CORE_XRECORD_METHOD_V1');self.assertFalse(manifest['runtime_enabled'])
   for name,sha in manifest['files'].items():self.assertEqual(hashlib.sha256((root/name).read_bytes()).hexdigest(),sha)
   for name in('xrecord_core_controller.py','xrecord_core_native.py','xrecord_core_worker.py'):self.assertIn('RUNTIME_REVIEWED=False',(root/name).read_text())
   self.assertEqual(manifest['wip_initial_sha256']['xrecord_core_method.py'],'ca4de66b67603924d00fb0acb4cf381f46877a76fc4e798784309649c52b27cf')
   with self.assertRaises(FileExistsError):p.prepare(root)
 def test_manifest_must_be_root_enabled_and_any_changed_source_still_fails(self):
  with tempfile.TemporaryDirectory()as d:
   root=Path(d)/'package';manifest=p.prepare(root)
   with patch.object(c,'__file__',str(root/'xrecord_core_controller.py')):
    with self.assertRaisesRegex(RuntimeError,'disabled'):c.verify_package()
    manifest['runtime_enabled']=True;(root/'source-manifest.json').write_text(json.dumps(manifest))
    self.assertEqual(c.verify_package()['schema'],'OWN_CORE_XRECORD_METHOD_V1')
    (root/'xrecord_core_worker.py').write_text('changed')
    with self.assertRaisesRegex(ValueError,'source pin'):c.verify_package()
 def test_wip_three_source_copies_are_byte_exact(self):
  for name,sha in p.WIP_INITIAL.items():self.assertEqual(hashlib.sha256((p.SOURCE/name).read_bytes()).hexdigest(),sha)

if __name__=='__main__':unittest.main()
