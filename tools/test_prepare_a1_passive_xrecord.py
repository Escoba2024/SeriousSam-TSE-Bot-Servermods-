"""Pure source/package regression; no execution of the private controller."""
import ast
import hashlib
import json
from pathlib import Path
import tempfile
import unittest
import prepare_a1_passive_xrecord as p

class Tests(unittest.TestCase):
 def test_runner_keeps_exact_action_and_fresh_read_release_gain_contracts(self):
  old=(p.PARENT/'run_dual.py').read_text();new=p.transform_runner(old)
  def function(source,name):return ast.dump(next(n for n in ast.parse(source).body if isinstance(n,ast.FunctionDef)and n.name==name),include_attributes=False)
  self.assertEqual(function(old,'action_step'),function(new,'action_step'));self.assertEqual(function(old,'read_rotation_pair'),function(new,'read_rotation_pair'))
  self.assertIn('passive.before_input()',new);self.assertLess(new.index('passive.before_input()'),new.index('before_press()  # inherited final fresh'))
  self.assertIn("RUNTIME_REVIEWED=False",new);self.assertIn('require_method_qualification',new)
 def test_package_is_disabled_core_exact_and_cp_rd_input_scope_unchanged(self):
  with tempfile.TemporaryDirectory()as d:
   root=Path(d)/'package';receipt=p.prepare(root);m=json.loads((root/'source-manifest.json').read_text())
   self.assertFalse(m['runtime_reviewed']);self.assertIsNone(m['passive_xrecord']['binding_qualification'])
   for name in('colt_preparation.py','rotation_diagnostics.py','a1_trace_scope.py','x11_endpoint.py','transaction.py','host_budget.py'):
    self.assertEqual((root/name).read_bytes(),(p.PARENT/name).read_bytes())
   for name in p.CORE_FILES:self.assertEqual((root/'passive-core'/name).read_bytes(),(p.CORE_PARENT/name).read_bytes())
   for path,sha in m['runtime_dependencies'].items():self.assertEqual(hashlib.sha256(Path(path).read_bytes()).hexdigest(),sha)
   self.assertFalse(m['passive_xrecord']['native_performed']);self.assertEqual(receipt['runtime_pins'],len(m['runtime_dependencies']))
   with self.assertRaises(ValueError):p.prepare(root)

if __name__=='__main__':unittest.main()
