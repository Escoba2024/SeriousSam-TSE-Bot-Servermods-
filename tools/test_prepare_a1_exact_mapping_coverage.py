"""New disabled fork scope and immutable historical-source reuse."""
import json
from pathlib import Path
import tempfile
import unittest


class CoveragePackageTests(unittest.TestCase):
 def test_disabled_fork_reuses_exact_helper_and_preserves_inputs_hooks_and_receipts(self):
  try:import prepare_a1_exact_mapping_coverage as builder
  except ImportError:self.fail('missing exact-coverage disabled package builder')
  with tempfile.TemporaryDirectory()as directory:
   out=Path(directory)/'new';builder.prepare(out)
   m=json.loads((out/'source-manifest.json').read_text())
   self.assertFalse(m['runtime_reviewed']);self.assertFalse(m['runtime_performed'])
   self.assertEqual(builder.sha(out/'mapped_rows.py'),builder.HELPER_SHA)
   self.assertEqual((out/'mapped_rows.py').read_bytes(),(builder.HISTORICAL/'mapped_rows.py').read_bytes())
   self.assertEqual((out/'test_mapped_rows.py').read_bytes(),(builder.HISTORICAL/'test_mapped_rows.py').read_bytes())
   for path,h in m['runtime_dependencies'].items():self.assertEqual(builder.sha(path),h,path)
   for path,h in m['diagnostic_source_sha256'].items():self.assertEqual(builder.sha(out/path),h,path)
   nested=json.loads((out/'collector/source-manifest.json').read_text())
   self.assertFalse(nested['runtime_reviewed'])
   for path,h in nested['source_pins'].items():self.assertEqual(builder.sha(path),h,path)
   for name in('collector/a1_original_input_readonly.js','collector/original-input-guards.json','a1_mapping_failure_receipt.py','colt_preparation.py','a1_trace_scope.py','rotation_diagnostics.py','dual_input.py','transaction.py','tools/retail_inventory_readonly.py'):
    self.assertEqual((out/name).read_bytes(),(builder.PARENT/name).read_bytes(),name)
   self.assertEqual((out/'a1_input_worker.py').read_text().replace('RUNTIME_REVIEWED=False','RUNTIME_REVIEWED=True'),(builder.PARENT/'a1_input_worker.py').read_text())
   old=json.loads((builder.PARENT/'source-manifest.json').read_text())
   for key in('originals','preparation','host_budget','trace_supervision'):
    self.assertEqual(m[key],old[key],key)
   self.assertEqual(len(m['runtime_dependencies']),len(old['runtime_dependencies'])+1)
   with self.assertRaises(ValueError):builder.prepare(out)

 def test_unpinned_backend_is_rejected(self):
  try:import prepare_a1_exact_mapping_coverage as builder
  except ImportError:self.fail('missing pinned backend transformation')
  with self.assertRaises(ValueError):builder.transform_backend('unexpected source')


if __name__=='__main__':unittest.main()
