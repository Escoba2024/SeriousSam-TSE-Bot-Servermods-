"""Offline builder verification only; no generated controller execution."""
import ast
import importlib
import json
from pathlib import Path
import tempfile
import unittest
import sys
sys.path.append('/srv/tse-a1-xres-lifecycle-root-frozen-20261115')


class KeyboardPackage(unittest.TestCase):
 def module(self):
  self.assertIsNotNone(importlib.util.find_spec('prepare_a1_keyboard_qualification'),'missing disabled keyboard-only builder')
  return importlib.import_module('prepare_a1_keyboard_qualification')
 def test_disabled_fork_preserves_binaries_core_guards_hold_and_restore(self):
  b=self.module()
  with tempfile.TemporaryDirectory()as d:
   dest=Path(d)/'keyboard';r=b.prepare(dest);m=json.loads((dest/'source-manifest.json').read_bytes());self.assertFalse(m['runtime_reviewed']);self.assertFalse(r['native_performed'])
   cm=json.loads((dest/'collector/source-manifest.json').read_bytes());self.assertIs(cm['runtime_reviewed'],False)
   collector=(dest/'collector/a1_original_input_collector.py').read_text();self.assertTrue('RUNTIME_REVIEWED=False'in collector or'RUNTIME_REVIEWED = False'in collector)
   for p,h in m['runtime_dependencies'].items():self.assertEqual(b.sha(p),h)
   for n in b.CORE_FILES:self.assertEqual((dest/'passive-core'/n).read_bytes(),(b.PARENT/'passive-core'/n).read_bytes())
   old=ast.parse((b.PARENT/'run_dual.py').read_text());new=ast.parse((dest/'run_dual.py').read_text())
   for name in ('action_step','read_rotation_pair','cleanup_chain','checked_close_original_contract','verify_close_dependency','close','close_displays','restore','own_identity','display_guard','periodic','native_rotation_pair'):
    pick=lambda t:ast.dump(next(n for n in ast.walk(t)if isinstance(n,ast.FunctionDef)and n.name==name),include_attributes=False)
    self.assertEqual(pick(old),pick(new),name)
   trace=next(n for n in ast.walk(new)if isinstance(n,ast.FunctionDef)and n.name=='trace_preparation');calls=[ast.unparse(n.func)for n in ast.walk(trace)if isinstance(n,ast.Call)]
   self.assertNotIn('WorkerProxy.start',calls);self.assertNotIn('PassiveRecorder.start',calls);self.assertNotIn('CP.run_preparation',calls);self.assertIn('KG.run',calls)
   self.assertEqual(m['host_budget'],json.loads((b.PARENT/'source-manifest.json').read_bytes())['host_budget']);self.assertEqual(m['keyboard_qualification']['actions'],6)
   self.assertFalse(m['keyboard_qualification']['wire_proven']);self.assertEqual(m['keyboard_qualification']['max_hold_seconds'],.35)
   with self.assertRaises(ValueError):b.prepare(dest)
 def test_controller_never_accepts_old_mouse_mode_or_forged_missing_release(self):
  b=self.module();text=b.transform((b.PARENT/'run_dual.py').read_text())
  self.assertIn("mode=='keyboard-qualification'",text);self.assertIn('keyboard_journal_complete',text)
  self.assertNotIn("collector=WorkerProxy.start",text)
  with self.assertRaises(ValueError):b.transform(text)


if __name__=='__main__':unittest.main()
