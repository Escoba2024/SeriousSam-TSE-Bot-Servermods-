"""Only disabled derivation and same-parent closure; never import launcher."""
import ast
import hashlib
import importlib.util
import json
from pathlib import Path
import tempfile
import unittest


class NineReadyBuilder(unittest.TestCase):
 def module(self):
  self.assertIsNotNone(importlib.util.find_spec('prepare_latejoin_nine_ready'),'new disabled readiness builder is missing')
  import prepare_latejoin_nine_ready
  return prepare_latejoin_nine_ready
 def test_disabled_package_changes_only_admission_adapter_names_and_pins(self):
  b=self.module()
  with tempfile.TemporaryDirectory()as d:
   dest=Path(d)/'new';r=b.prepare(dest);m=json.loads((dest/'source-manifest.json').read_text())
   self.assertEqual(b.sha(dest/'source-manifest.json'),r['manifest_sha256'])
   self.assertLessEqual(set(json.loads((b.PARENT/'source-manifest.json').read_text())['sources']),set(m['sources']))
   for key in ('runtime_reviewed','runtime_performed','qualified','functional_pass','a4_accepted'):self.assertIs(m[key],False)
   for key,relative in [('runtime_dependencies',False),('sources',True),('draft_source_sha256',True)]:
    for name,h in m[key].items():self.assertEqual(b.sha(dest/name if relative else name),h,name)
   for name in ('ownns_latejoin_preflight.py','ownns_latejoin_local_mapping.py','owned_latejoin_capture.py','owned_latejoin_capture_exec.py','owned_sync_capture.py','owned_capture_exec.py','analyze_retail_sync_pcap.py','host_budget.py','strict_backend.py','transaction.py','a4_ordered_memory_v3.py'):
    self.assertEqual((dest/name).read_bytes(),(b.PARENT/name).read_bytes(),name)
   before=(b.PARENT/'run-a4.py').read_text();after=(dest/'run-a4.py').read_text()
   self.assertEqual(before,after.replace('own-latejoin018-nine-ready-yodeller-','own-latejoin018-yodeller-'))
   for name in ('run-a4.py','owned_sync_capture.py','owned_latejoin_capture.py','owned_latejoin_capture_exec.py'):self.assertIn('RUNTIME_REVIEWED=False',(dest/name).read_text())
   with self.assertRaises(ValueError):b.prepare(dest)
 def test_non_admission_source_or_predicate_change_is_rejected(self):
  b=self.module();before=(b.PARENT/'ownns_latejoin_runtime.py').read_text();after=(Path(b.__file__).parent/'ownns_latejoin_runtime.py').read_text()
  b.validate_adapter(before,after)
  for changed in (after.replace('end=started+20','end=started+21'),after.replace('min(.1,remaining)','min(.2,remaining)')):
   with self.assertRaises(ValueError):b.validate_adapter(before,changed)
 def test_existing_private_prestart_body_remains_exact_ast(self):
  b=self.module();before=ast.parse((b.PARENT/'ownns_latejoin_runtime.py').read_text());after=ast.parse((Path(b.__file__).parent/'ownns_latejoin_runtime.py').read_text())
  get=lambda tree:next(n for n in ast.walk(tree)if isinstance(n,ast.FunctionDef)and n.name=='private_prestart')
  self.assertEqual(ast.dump(get(before)),ast.dump(get(after)))


if __name__=='__main__':unittest.main()
