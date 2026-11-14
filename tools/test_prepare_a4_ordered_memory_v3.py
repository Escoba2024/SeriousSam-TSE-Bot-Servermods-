"""Focused disabled-controller derivation checks. Never imports its runtime."""
import ast
import json
import os
from pathlib import Path
import unittest
import prepare_a4_ordered_memory_v3 as builder


class AdapterTests(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  cls.old=(builder.PARENT/'run-a4.py').read_text();cls.new=builder.transform(cls.old)
 def test_actual_reader_query_control_sleep_and_role_cleanup_calls_identical(self):
  def calls(source):
   out=[]
   for n in ast.walk(ast.parse(source)):
    if not isinstance(n,ast.Call):continue
    direct=isinstance(n.func,ast.Name)and n.func.id in('control','sample_host','HostBudget')
    attr=isinstance(n.func,ast.Attribute)and isinstance(n.func.value,ast.Name)and n.func.value.id in('inventory','probe','B','pauseprobe','host_budget','transaction')
    sleep=isinstance(n.func,ast.Attribute)and isinstance(n.func.value,ast.Name)and n.func.value.id=='time'and n.func.attr=='sleep'
    if direct or attr or sleep:out.append(ast.dump(n,include_attributes=False))
   return sorted(out)
  self.assertEqual(calls(self.old),calls(self.new))
  for name in('close','launch','count','whole_quiescent','checked_query'):
   def function(s):return ast.dump(next(n for n in ast.walk(ast.parse(s))if isinstance(n,ast.FunctionDef)and n.name==name),include_attributes=False)
   self.assertEqual(function(self.old),function(self.new))
 def test_contract_and_attempt_begin_before_sample_and_release(self):
  s=self.new
  self.assertIn('RUNTIME_REVIEWED=False',s);self.assertIn('default=600',s);self.assertIn('gam_iStartDifficulty=2;',s)
  self.assertEqual(s.count('inventory.sample(slots)'),2)
  self.assertEqual(s.count('read_attempts.begin(read_serial,group,sample_start,'),2)
  self.assertLess(s.index("(E/'memory-observation-contract.json').write_text"),s.index('snap=inventory.sample(slots)'))
  self.assertLess(s.index("(E/'memory-observation-contract.json').write_text"),s.index("control('key','Pause',.1)"))
  self.assertIn('native_group_contract,read_attempts.records)',s)
  self.assertIn("native_registry['memory_observation_contract']=canonical_groups.read_contract(native_group_contract)",s)
  self.assertIn('except BaseException as err:',s)
  self.assertIn("('attempt_stream',attempt_stream)",s)
  self.assertNotIn('frida',s.lower())
 def test_old_v2_core_and_audit_are_exact_original_bytes(self):
  for name,h in builder.UNCHANGED.items():self.assertEqual(builder.sha(builder.PARENT/name),h);self.assertEqual(builder.sha(Path(__file__).with_name(name)),h)
 def test_wrong_inherited_anchor_refused(self):
  with self.assertRaises(ValueError):builder.transform(self.old.replace('import a4_canonical_native_groups as canonical_groups',''))


@unittest.skipUnless(os.environ.get('TSE_A4_ORDERED_PACKAGE'),'explicit disabled package required')
class PackageTests(unittest.TestCase):
 def test_fresh_all_pins_disabled_and_inherited_files(self):
  root=Path(os.environ['TSE_A4_ORDERED_PACKAGE']);m=json.loads((root/'source-manifest.json').read_text())
  for k in('runtime_reviewed','runtime_performed','qualified','functional_pass'):self.assertIs(m[k],False)
  self.assertIs(m['root_review']['approved_for_private_a4'],False)
  for p,h in m['runtime_dependencies'].items():self.assertEqual(builder.sha(p),h,p)
  for p,h in m['sources'].items():self.assertEqual(builder.sha(root/p),h,p)
  for p,h in m['draft_source_sha256'].items():self.assertEqual(builder.sha(root/p),h,p)
  for name,h in builder.UNCHANGED.items():self.assertEqual(builder.sha(root/name),h)
  self.assertEqual((root/'run-a4.py').read_text(),builder.transform((builder.PARENT/'run-a4.py').read_text()))
  for p in builder.PARENT.iterdir():
   if p.is_file()and p.name not in('run-a4.py','source-manifest.json','HANDOFF-disabled.json','test_a4_hard_maps.py'):
    self.assertEqual(builder.sha(root/p.name),builder.sha(p),p.name)


if __name__=='__main__':unittest.main()
