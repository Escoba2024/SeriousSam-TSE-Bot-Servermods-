"""No runtime imports/launches: inspect the actual derived controller."""
import ast
import json
from pathlib import Path
import tempfile
import unittest


class CaptureControllerTests(unittest.TestCase):
 def source(self):
  import prepare_owned_sync_capture as b
  return b,b.transform((b.PARENT/'run-a4.py').read_text())
 def test_disabled_018_yodeller600_and_unchanged_inventory_input_sleeps(self):
  b,s=self.source();old=(b.PARENT/'run-a4.py').read_text()
  self.assertIn('RUNTIME_REVIEWED=False',s);self.assertIn("assert map_key=='yodeller' and duration==600 and diag==0",s)
  self.assertIn(str(b.BUILD/'Sources/Game/GameMP.dll'),s)
  self.assertIn('PASS_LIMITED_OWN_SAMPLED_SYNC_PROTOCOL_REVIEW_REQUIRED',s)
  self.assertNotIn('PASS_LIMITED_A4_OBSERVATION_FUNCTIONAL_REVIEW_REQUIRED',s)
  def calls(source,owner,name):
   return [ast.dump(n,include_attributes=False)for n in ast.walk(ast.parse(source))if isinstance(n,ast.Call)and isinstance(n.func,ast.Attribute)and isinstance(n.func.value,ast.Name)and n.func.value.id==owner and n.func.attr==name]
  for owner,name in [('inventory','sample'),('time','sleep'),('probe','read'),('pauseprobe','read_pause'),('B','query')]:
   self.assertEqual(calls(s,owner,name),calls(old,owner,name),(owner,name))
  self.assertEqual(s.count("control('key','Pause',.1)"),old.count("control('key','Pause',.1)"))
 def test_capture_is_bound_before_release_and_closed_before_any_game_role(self):
  _,s=self.source()
  start=s.index('capture.start()');release=s.index("control('key','Pause',.1)")
  self.assertLess(start,release)
  self.assertGreater(start,s.index("report['actual_profile_migration']"))
  finally_index=s.index('   was_raising=sys.exc_info()')
  self.assertLess(s.index('capture.close()',finally_index),s.index("for role in ('vanilla','botB','botA','server')",finally_index))
  self.assertIn("report['sync_checks']=checks;assert all(c['bad']==0",s)
  self.assertIn("if report['active_evidence']['missing_activity']:",s)
  self.assertIn('verdict=finalize_trial_evidence(report,expected_roles=',s)
 def test_partial_start_has_a_retained_capture_object_before_spawn(self):
  _,s=self.source()
  self.assertLess(s.index('capture=OwnedSyncCapture('),s.index('capture.start()'))
  self.assertIn("capture.guard()",s)
 def test_fresh_disabled_package_pins018_and_preserves_all_old_v3_rules(self):
  import prepare_owned_sync_capture as b
  with tempfile.TemporaryDirectory()as directory:
   dest=Path(directory)/'new';result=b.prepare(dest)
   m=json.loads((dest/'source-manifest.json').read_text())
   self.assertFalse(m['runtime_reviewed']);self.assertFalse(m['runtime_performed']);self.assertFalse(m['qualified'])
   self.assertEqual(m['candidate']['dll_sha256'],b.DLL);self.assertEqual(m['candidate']['source_commit'],b.SOURCE)
   for path,h in m['runtime_dependencies'].items():self.assertEqual(b.sha(path),h,path)
   for name,h in m['sources'].items():self.assertEqual(b.sha(dest/name),h,name)
   self.assertEqual(result['manifest_sha256'],b.sha(dest/'source-manifest.json'))
   for name in('a4_ordered_memory_v3.py','a4_canonical_native_groups.py','audit_a4_ordered_memory_v3.py','a4_fire_observer_v2.py','audit_a4_native_fire_observer_v2.py','transaction.py','host_budget.py','stability_hard_rules.py','a4_hard_map_policy.py','canonical.ini'):
    self.assertEqual((dest/name).read_bytes(),(b.PARENT/name).read_bytes(),name)
   self.assertIn('RUNTIME_REVIEWED=False',(dest/'owned_sync_capture.py').read_text())
   self.assertIn('RUNTIME_REVIEWED=False',(dest/'owned_capture_exec.py').read_text())
   for key in('host_budget','read_contract','canonical_profile_migration'):
    self.assertEqual(m[key],json.loads((b.PARENT/'source-manifest.json').read_text())[key])
   with self.assertRaises(ValueError):b.prepare(dest)


if __name__=='__main__':unittest.main()
