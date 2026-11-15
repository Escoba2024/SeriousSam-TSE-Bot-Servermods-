"""Offline copy/pin/delta checks; never import or run a generated controller."""
import ast
import hashlib
import importlib
import json
from pathlib import Path
import tempfile
import unittest


class Builder(unittest.TestCase):
 def test_disabled_packages_share_actual_worker_core_and_method_fingerprints(self):
  a=importlib.import_module('prepare_a1_xres_attribution');b=importlib.import_module('prepare_a1_xres_lifecycle_method')
  with tempfile.TemporaryDirectory()as d:
   root=Path(d);ra=a.prepare(root/'a1');rm=b.prepare(root/'method')
   self.assertFalse(ra['runtime_reviewed']);self.assertFalse(rm['runtime_reviewed'])
   for package,scope in((root/'a1','A1_154'),(root/'method','OWN_METHOD_167')):
    m=json.loads((package/'source-manifest.json').read_bytes());self.assertFalse(m['runtime_reviewed']);self.assertEqual(m['xres_attribution']['allowed_scope'],scope)
    for path,h in m['runtime_dependencies'].items():self.assertEqual(a.sha(path),h)
    for name in a.CORE_FILES:self.assertEqual((package/'passive-core'/name).read_bytes(),(a.PARENT/'passive-core'/name).read_bytes())
   for name in a.ADAPTER_FILES:self.assertEqual((root/'a1'/name).read_bytes(),(root/'method'/name).read_bytes())
   self.assertEqual(ra['fingerprints'],rm['fingerprints'])
   m=json.loads((root/'a1/source-manifest.json').read_bytes());self.assertIsNone(m['passive_xrecord']['xres_lifecycle_qualification'])
   self.assertEqual(m['host_budget'],json.loads((a.PARENT/'source-manifest.json').read_bytes())['host_budget'])
   old=(a.PARENT/'run_dual.py').read_text();new=(root/'a1/run_dual.py').read_text()
   for name in('action_step','native_rotation_pair'):
    def body(text):return ast.dump(next(n for n in ast.walk(ast.parse(text))if isinstance(n,ast.FunctionDef)and n.name==name),include_attributes=False)
    self.assertEqual(body(old),body(new))
   with self.assertRaises(ValueError):a.prepare(root/'a1')
 def test_qualification_cannot_be_fabricated_as_snapshot_only_or_without_driver_requests(self):
  a=importlib.import_module('prepare_a1_xres_attribution')
  for row in({},dict(status='PASS_OWN_XRES_RECORD_LIFECYCLE_ONLY',driver_requests_bound=False)):
   with self.assertRaises(ValueError):a.validate_qualification(row,{})


if __name__=='__main__':unittest.main()
