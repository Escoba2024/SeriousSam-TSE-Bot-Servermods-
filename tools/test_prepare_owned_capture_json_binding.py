"""Exact private derivation only; no process or capture startup."""
import json
from pathlib import Path
import tempfile
import unittest


class JsonBindingPackageTests(unittest.TestCase):
 def test_fresh_parent_derivation_changes_only_library_line_and_regression_test(self):
  import prepare_owned_capture_json_binding as b
  with tempfile.TemporaryDirectory()as directory:
   dest=Path(directory)/'new';receipt=b.prepare(dest)
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


if __name__=='__main__':unittest.main()
