"""Exact private derivation only; no process or capture startup."""
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch


class JsonBindingPackageTests(unittest.TestCase):
 def test_fresh_parent_derivation_changes_only_library_line_and_regression_test(self):
  import prepare_owned_capture_json_binding as b
  with tempfile.TemporaryDirectory()as directory:
   # This historical builder accepts exactly its original one-line fix.
   # Keep that contract by reading its immutable JSON-author source, while
   # the FD-churn package has its own strict derivation test.
   dest=Path(directory)/'new'
   with patch.object(b,'__file__','/srv/tse-owned-sync018-json-binding-disabled-20261114/prepare_owned_capture_json_binding.py'):receipt=b.prepare(dest)
   old=json.loads((b.PARENT/'source-manifest.json').read_text());m=json.loads((dest/'source-manifest.json').read_text())
   self.assertEqual(set(m['sources']),set(old['sources']))
   changed={name for name in old['sources']if (b.PARENT/name).read_bytes()!=(dest/name).read_bytes()}
   self.assertEqual(changed,{'owned_sync_capture.py','test_owned_sync_capture.py'})
   library=(b.PARENT/'owned_sync_capture.py').read_text()
   self.assertEqual((dest/'owned_sync_capture.py').read_text(),library.replace('ports=selected)','ports=[list(pair)for pair in selected])'))
   for key,relative in [('runtime_dependencies',False),('sources',True),('draft_source_sha256',True)]:
    for name,h in m[key].items():self.assertEqual(b.sha(dest/name if relative else name),h,name)
   self.assertEqual(receipt['manifest_sha256'],b.sha(dest/'source-manifest.json'))
   for name in('run-a4.py','owned_sync_capture.py','owned_capture_exec.py'):self.assertIn('RUNTIME_REVIEWED=False',(dest/name).read_text())
   for key in('candidate','host_budget','read_contract','capture','canonical_profile_migration','derivation'):
    self.assertEqual(old[key],m[key],key)
   with self.assertRaises(ValueError):b.prepare(dest)
 def test_historical_json_builder_rejects_additional_runtime_edits(self):
  import prepare_owned_capture_json_binding as b
  with tempfile.TemporaryDirectory()as directory:
   with self.assertRaisesRegex(ValueError,'exact one-line runtime correction only'):b.prepare(Path(directory)/'new')


if __name__=='__main__':unittest.main()
