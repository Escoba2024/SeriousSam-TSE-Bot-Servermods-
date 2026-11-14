"""Offline complete-package pin and scope checks; no native imports."""
import json
from pathlib import Path
import tempfile
import unittest


class MappingPackageTests(unittest.TestCase):
 def test_new_disabled_package_preserves_hook_input_worker_receipt_and_original_pins(self):
  import prepare_a1_mapping_failure_receipt as builder
  with tempfile.TemporaryDirectory()as directory:
   out=Path(directory)/'new';builder.prepare(out)
   m=json.loads((out/'source-manifest.json').read_text())
   self.assertFalse(m['runtime_reviewed']);self.assertFalse(m['runtime_performed'])
   self.assertFalse(m['mapping_receipt_derivation']['accepted_new_mappings'])
   for path,h in m['runtime_dependencies'].items():self.assertEqual(builder.sha(path),h,path)
   for path,h in m['diagnostic_source_sha256'].items():self.assertEqual(builder.sha(out/path),h,path)
   nested=json.loads((out/'collector/source-manifest.json').read_text())
   self.assertFalse(nested['runtime_reviewed'])
   for path,h in nested['source_pins'].items():self.assertEqual(builder.sha(path),h,path)
   for name in('collector/a1_original_input_readonly.js','collector/original-input-guards.json','colt_preparation.py','rotation_diagnostics.py','a1_trace_scope.py','dual_input.py','transaction.py','tools/retail_inventory_readonly.py'):
    self.assertEqual((out/name).read_bytes(),(builder.PARENT/name).read_bytes(),name)
   self.assertEqual((out/'a1_input_worker.py').read_text().replace('RUNTIME_REVIEWED=False','RUNTIME_REVIEWED=True'),(builder.PARENT/'a1_input_worker.py').read_text())
   collector=(out/'collector/a1_original_input_collector.py').read_text().replace('RUNTIME_REVIEWED = False','RUNTIME_REVIEWED = True').replace(str(out/'collector'),str(builder.PARENT/'collector'))
   self.assertEqual(collector,(builder.PARENT/'collector/a1_original_input_collector.py').read_text())
   parent=json.loads((builder.PARENT/'source-manifest.json').read_text())
   self.assertEqual(m['originals'],parent['originals']);self.assertEqual(m['preparation'],parent['preparation']);self.assertEqual(m['host_budget'],parent['host_budget'])
   self.assertEqual(m['trace_supervision'],parent['trace_supervision'])
   self.assertEqual(len(m['runtime_dependencies']),len(parent['runtime_dependencies'])+1)
   with self.assertRaises(ValueError):builder.prepare(out)

 def test_transformers_refuse_unpinned_parent_sources(self):
  import prepare_a1_mapping_failure_receipt as builder
  for name in('transform_backend','transform_runner'):
   with self.subTest(name=name),self.assertRaises(ValueError):getattr(builder,name)('unreviewed source')


if __name__=='__main__':unittest.main()
