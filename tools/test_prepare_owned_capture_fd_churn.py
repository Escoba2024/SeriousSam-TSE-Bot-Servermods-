"""Fresh disabled FD-fix package, exact parent provenance and scope."""
import json
from pathlib import Path
import tempfile
import unittest


class FdChurnPackageTests(unittest.TestCase):
 def test_only_readlink_guards_and_new_regression_file_change_from_parent(self):
  import prepare_owned_capture_fd_churn as b
  with tempfile.TemporaryDirectory()as directory:
   dest=Path(directory)/'new';receipt=b.prepare(dest)
   old=json.loads((b.PARENT/'source-manifest.json').read_text());m=json.loads((dest/'source-manifest.json').read_text())
   self.assertEqual(set(m['sources'])-set(old['sources']),{'test_owned_capture_fd_churn.py'})
   self.assertEqual({n for n in old['sources']if (b.PARENT/n).read_bytes()!=(dest/n).read_bytes()},{'owned_sync_capture.py'})
   self.assertEqual((dest/'owned_sync_capture.py').read_text(),b.corrected((b.PARENT/'owned_sync_capture.py').read_text()))
   for key,relative in [('runtime_dependencies',False),('sources',True),('draft_source_sha256',True)]:
    for n,h in m[key].items():self.assertEqual(b.sha(dest/n if relative else n),h,(key,n))
   for key in('candidate','host_budget','read_contract','capture','canonical_profile_migration','derivation','json_binding_fix'):self.assertEqual(old[key],m[key],key)
   for name in('run-a4.py','owned_sync_capture.py','owned_capture_exec.py'):self.assertIn('RUNTIME_REVIEWED=False',(dest/name).read_text())
   self.assertFalse(any(m[k]for k in('runtime_reviewed','runtime_performed','qualified','functional_pass')))
   self.assertEqual(receipt['manifest_sha256'],b.sha(dest/'source-manifest.json'))
   with self.assertRaises(ValueError):b.prepare(dest)


if __name__=='__main__':unittest.main()
