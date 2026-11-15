"""Offline derivation/pin tests; never import or execute the generated controller."""
import ast
import importlib
import json
from pathlib import Path
import tempfile
import unittest


class FeedbackPackageTests(unittest.TestCase):
 def module(self):
  self.assertIsNotNone(importlib.util.find_spec('prepare_a1_pitch_feedback'),'missing disabled pitch feedback builder')
  return importlib.import_module('prepare_a1_pitch_feedback')
 def test_disabled_mouse_fork_preserves_guards_core_and_transaction(self):
  b=self.module()
  with tempfile.TemporaryDirectory()as d:
   dest=Path(d)/'feedback';r=b.prepare(dest);m=json.loads((dest/'source-manifest.json').read_bytes());cm=json.loads((dest/'collector/source-manifest.json').read_bytes())
   self.assertIs(m['runtime_reviewed'],False);self.assertIs(cm['runtime_reviewed'],False);self.assertFalse(r['native_performed'])
   for name in('run_dual.py',*b.GATES):
    tree=ast.parse((dest/name).read_text());gate=[n for n in tree.body if isinstance(n,ast.Assign)and any(isinstance(t,ast.Name)and t.id=='RUNTIME_REVIEWED'for t in n.targets)]
    self.assertEqual(len(gate),1);self.assertIs(ast.literal_eval(gate[0].value),False,name)
   for pins,base in((m['runtime_dependencies'],Path('/')),(m['diagnostic_source_sha256'],dest),(cm['source_pins'],Path('/'))):
    for p,h in pins.items():self.assertEqual(b.sha(base/p),h,p)
   for name in b.CORE_FILES:self.assertEqual((dest/'passive-core'/name).read_bytes(),(b.PARENT/'passive-core'/name).read_bytes())
   old=ast.parse((b.PARENT/'run_dual.py').read_text());new=ast.parse((dest/'run_dual.py').read_text())
   for name in('action_step','read_rotation_pair','cleanup_chain','checked_close_original_contract','verify_close_dependency','close','close_displays','restore','own_identity','display_guard','periodic','native_rotation_pair','native_roles'):
    pick=lambda t:ast.dump(next(n for n in ast.walk(t)if isinstance(n,ast.FunctionDef)and n.name==name),include_attributes=False)
    self.assertEqual(pick(old),pick(new),name)
   trace=next(n for n in ast.walk(new)if isinstance(n,ast.FunctionDef)and n.name=='trace_preparation')
   calls=[ast.unparse(n.func)for n in ast.walk(trace)if isinstance(n,ast.Call)]
   for name in('WorkerProxy.start','PassiveRecorder.start','CP.run_preparation','install_keyboard'):self.assertNotIn(name,calls)
   self.assertIn('PF.run',calls);self.assertIn('prepare_xtest_transport',calls);self.assertIn('PF.FeedbackJournal',calls)
   text=(dest/'run_dual.py').read_text();self.assertNotIn('KeyboardTransport',text);self.assertNotIn('keyboard_controls_profile',text)
   self.assertEqual(text.count('NIP.install(transaction,E)'),1);self.assertEqual(text.count('MIP.install(transaction,E)'),1)
   self.assertEqual(m['host_budget'],json.loads((b.PARENT/'source-manifest.json').read_bytes())['host_budget'])
   q=m['pitch_feedback'];self.assertEqual((q['max_actions'],q['max_attempts'],q['active_seconds'],q['cp_seconds'],q['runner_seconds'],q['input_reserve_seconds']),(48,96,20,85,90,2.35))
   self.assertFalse(q['gain_proven']);self.assertFalse(q['normal_route_or_fire']);self.assertFalse(q['native_performed'])
   with self.assertRaises(ValueError):b.prepare(dest)
 def test_transform_is_exact_one_pass_and_fixed_mode_only(self):
  b=self.module();text=b.transform((b.PARENT/'run_dual.py').read_text())
  self.assertIn("mode=='pitch-feedback'",text);self.assertIn('PF.journal_complete(report,verdict)',text)
  self.assertNotIn('collector=WorkerProxy.start',text);self.assertNotIn('PassiveRecorder.start',text);self.assertNotIn('CP.run_preparation(',text)
  with self.assertRaises(ValueError):b.transform(text)


if __name__=='__main__':unittest.main()
