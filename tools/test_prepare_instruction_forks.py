"""Closed-package source preparation only; no imports of native toolchains."""
from pathlib import Path
import json
import ast
import tempfile
import unittest


class InstructionForkTests(unittest.TestCase):
 def test_forks_disable_all_execution_and_preserve_inputs_readers_and_cleanup(self):
  import prepare_instruction_forks as f
  for kind in ('a1','a3'):
   with self.subTest(kind=kind),tempfile.TemporaryDirectory()as d:
    out=Path(d)/kind;f.prepare(kind,out)
    m=json.loads((out/'source-manifest.json').read_text())
    self.assertFalse(m['runtime_reviewed']);self.assertFalse(m['runtime_performed'])
    for p,h in m['runtime_dependencies'].items():self.assertEqual(f.sha(Path(p)),h,p)
    parent=f.PARENTS[kind][0]
    keep=('colt_preparation.py','a1_trace_scope.py','dual_input.py','tools/retail_inventory_readonly.py')if kind=='a1'else('original_damage_worker.py','original_damage_collector.py','damage_policy.py','transaction.py')
    for n in keep:self.assertEqual((out/n).read_bytes(),(parent/n).read_bytes(),n)
    if kind=='a1':
     self.assertEqual((out/'collector/a1_original_input_readonly.js').read_bytes(),Path(f.__file__).with_name('a1_original_input_readonly.js').read_bytes())
     for n in ('run_dual.py','a1_input_worker.py','collector/a1_original_input_collector.py'):
      self.assertNotIn('RUNTIME_REVIEWED=True',(out/n).read_text().replace(' = ','='))
     cm=json.loads((out/'collector/source-manifest.json').read_text())
     self.assertFalse(cm['runtime_reviewed'])
     for p,h in cm['source_pins'].items():self.assertEqual(f.sha(Path(p)),h,p)
    else:
     old=(parent/'frozen-v2/damage_readonly.js').read_text()
     self.assertEqual((out/'frozen-v2/damage_readonly.js').read_text(),f.patch_a3(old))
     tree=ast.parse((out/'run-a3-direct020.py').read_text())
     hashes=next(ast.literal_eval(n.value)for n in tree.body if isinstance(n,ast.Assign)and any(isinstance(t,ast.Name)and t.id=='FROZEN_HASHES'for t in n.targets))
     self.assertEqual(hashes['damage_readonly.js'],f.sha(out/'frozen-v2/damage_readonly.js'))
    with self.assertRaises(ValueError):f.prepare(kind,out)
 def test_unpinned_hook_sources_are_rejected(self):
  import prepare_instruction_forks as f
  for kind in ('a1','a3'):
   with self.subTest(kind=kind),self.assertRaises(ValueError):getattr(f,'patch_'+kind)('unexpected source')

if __name__=='__main__':unittest.main()
