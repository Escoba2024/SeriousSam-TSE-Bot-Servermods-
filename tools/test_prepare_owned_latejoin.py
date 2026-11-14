"""Offline transformed controller/closure review, never import its launcher."""
import ast
import importlib.util
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch


class LatejoinBuilder(unittest.TestCase):
 def test_missing_offline_builder_is_red(self):self.assertIsNotNone(importlib.util.find_spec('prepare_owned_latejoin'))
 def source(self):
  import prepare_owned_latejoin as b
  return b,b.transform((b.PARENT/'run-a4.py').read_text())
 def test_bots_are_unpaused_and_capture_precedes_real_original_launch(self):
  b,s=self.source();ast.parse(s)
  self.assertNotIn("control('key','Pause'",s);self.assertNotIn('bootstrap_cfg',s);self.assertNotIn('external_vanilla_preflight.py',s)
  self.assertIn("launch('server');count(0);launch('botA');count(4);launch('botB');count(8)",s)
  start=s.index('capture.start()');original=s.index("vanilla=launch('vanilla')")
  self.assertLess(s.index('late.prejoin_readiness('),start)
  self.assertLess(s.index('late.prejoin_readiness('),s.index('first_prestart=late.private_prestart()'))
  self.assertLess(start,original);self.assertLess(original,s.index('capture.admit('));self.assertLess(s.index('capture.admit('),s.index('capture.mark_postjoin_start()'))
  self.assertIn('late.admission(',s);self.assertIn('RUNTIME_REVIEWED=False',s)
 def test_same_gameplay_sampling_loop_and_normal_cleanup_with_no_force_game_path(self):
  b,s=self.source();old=(b.PARENT/'run-a4.py').read_text()
  for begin,end in [('   def usage():','   capture.gameplay_complete()'),("   for role in ('vanilla','botB','botA','server'):","   report['cleanup']=records;")]:
   a=old[old.index(begin):old.index(end)];n=s[s.index(begin):s.index(end)]
   if begin.startswith('   def usage'):
    n=n.replace("     assert all(sorted(p['slot']for p in x['players'])==list(range(9))for x in snapshots.values()),'native nine-slot roster changed'\n",'')
    n=n.replace('start=capture.post_started;','start=time.monotonic();')
   self.assertEqual(a,n)
  self.assertNotIn('killpg(',s)
 def test_no_a4_acceptance_from_sync_activity_or_missing_pickups(self):
  _,s=self.source()
  self.assertIn("report['latejoin_sync_activity']=sync_activity(",s)
  self.assertIn("'a4_accepted':False",s)
  self.assertNotIn("if report['active_evidence']['missing_activity']:",s)
  self.assertIn("report['active_evidence']=canonical_groups.apply(",s)
  self.assertIn('PASS_LIMITED_PRIVATE_LATEJOIN_SAMPLED_SYNC_REVIEW_REQUIRED',s)
 def test_launcher_and_identity_wait_keep_progress_and_existing_deadlines(self):
  _,s=self.source()
  self.assertIn('late.run_command(args+',s)
  self.assertIn('timeout=late.remaining(15),monotonic=late.clock',s)
  self.assertIn("late.wait(lambda:B.ready(role,unit(role)),45",s)
  self.assertIn("late.wait(ready,100",s)
 def test_fresh_disabled_package_closure_and_unchanged_decoder_external_preflights(self):
  import prepare_owned_latejoin as b
  with tempfile.TemporaryDirectory()as directory:
   dest=Path(directory)/'new';receipt=b.prepare(dest);m=json.loads((dest/'source-manifest.json').read_text())
   self.assertEqual(receipt['manifest_sha256'],b.sha(dest/'source-manifest.json'))
   for key in ('runtime_reviewed','runtime_performed','qualified','functional_pass','a4_accepted'):self.assertIs(m[key],False)
   self.assertEqual(m['candidate'],json.loads((b.PARENT/'source-manifest.json').read_text())['candidate'])
   for p,h in m['runtime_dependencies'].items():self.assertEqual(b.sha(p),h,p)
   for p,h in m['sources'].items():self.assertEqual(b.sha(dest/p),h,p)
   for n in ('analyze_retail_sync_pcap.py','owned_capture_exec.py','strict_backend.py','transaction.py','host_budget.py','a4_ordered_memory_v3.py','audit_a4_ordered_memory_v3.py','adapter_policy.py','canonical.ini'):
    self.assertEqual((dest/n).read_bytes(),(b.PARENT/n).read_bytes(),n)
   for n in ('run-a4.py','owned_sync_capture.py','owned_latejoin_capture.py','owned_latejoin_capture_exec.py'):
    self.assertIn('RUNTIME_REVIEWED=False',(dest/n).read_text())
   with self.assertRaises(ValueError):b.prepare(dest)
 def test_changed018_build_source_is_not_silently_requalified(self):
  import prepare_owned_latejoin as b
  old=json.loads((b.PARENT/'source-manifest.json').read_text());target=Path(old['candidate']['build_manifest']).parent/'Sources/Game/BotDriver.cpp';real=b.sha
  with tempfile.TemporaryDirectory()as directory,patch.object(b,'sha',side_effect=lambda p:'0'*64 if Path(p)==target else real(p)):
   with self.assertRaisesRegex(ValueError,'018 source pin'):b.prepare(Path(directory)/'new')


if __name__=='__main__':unittest.main()
