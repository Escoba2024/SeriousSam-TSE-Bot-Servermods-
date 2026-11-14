"""Offline exact retarget checks; never import a game controller."""
import ast
import hashlib
import importlib.util
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch


class Retarget(unittest.TestCase):
 def builder(self):
  self.assertIsNotNone(importlib.util.find_spec('prepare_navigation_build024'),'missing fixed024 retarget builder')
  import prepare_navigation_build024 as b
  return b
 def test_three_sources_reverse_exact_and_only_expected_labels_change(self):
  b=self.builder()
  for name in b.CHANGED:
   old=(b.PARENT/name).read_text();new=b.transform(name,old)
   self.assertNotEqual(new,old);self.assertEqual(b.reverse(name,new),old);ast.parse(new)
  runner=b.transform('run-a4.py',(b.PARENT/'run-a4.py').read_text())
  self.assertIn('RUNTIME_REVIEWED=False',runner);self.assertIn('PRIVATE A4 024 HARD',runner)
  for bad in [runner,runner+'\n'+(b.PARENT/'run-a4.py').read_text()]:
   with self.assertRaises(ValueError):b.transform('run-a4.py',bad)
 def test_build_fresh_full_closure(self):
  b=self.builder();pins=b.validate_build()
  self.assertEqual(len(pins),77);self.assertEqual(b.DLL.stat().st_size,b.DLL_SIZE)
  for path,h in pins.items():self.assertEqual(b.sha(path),h)
 def test_build_source_changes_rejected(self):
  b=self.builder();real=b.sha
  target=b.BUILD/'overlay/BotSupplyNative.h'
  with patch.object(b,'sha',side_effect=lambda p:'0'*64 if Path(p)==target else real(p)):
   with self.assertRaisesRegex(ValueError,'candidate'):b.validate_build()
 def test_bad_manifest_rejected(self):
  b=self.builder();real=b.sha
  with patch.object(b,'sha',side_effect=lambda p:'0'*64 if Path(p)==b.BUILD/'manifest.json' else real(p)):
   with self.assertRaisesRegex(ValueError,'manifest'):b.validate_build()
 def test_fixed_options_and_tiers_same023_logic(self):
  b=self.builder();ns={};exec(b.transform('navigation_comparison_policy.py',(b.PARENT/'navigation_comparison_policy.py').read_text()),ns)
  self.assertEqual(ns['candidate']('024')['dll_sha256'],b.DLL_SHA)
  ns['options']('redstation',600,0,'024')
  for vals in [('yodeller',600,0),('redstation',599,0),('redstation',600,1)]:
   with self.assertRaises(ValueError):ns['options'](*vals,'024')
  logs={r:'\n'.join(f'[BotHuman] local={i} profile=DEMON tier=3 persona=duelist seed={i+1} model=arena-v1'for i in range(4))for r in('botA','botB')}
  self.assertEqual(ns['check_tiers'](logs,'024'),ns['check_tiers'](logs,'023'))
  with self.assertRaises(ValueError):ns['check_tiers']({'botA':logs['botA']},'024')
 def test_prepare_exact_delta_all_pins_and_fixed_metadata(self):
  b=self.builder()
  with tempfile.TemporaryDirectory()as d:
   dest=Path(d)/'disabled';r=b.prepare(dest);m=json.loads((dest/'source-manifest.json').read_text())
   old=json.loads((b.PARENT/'source-manifest.json').read_text())
   self.assertFalse(m['runtime_reviewed']);self.assertFalse(m['qualified']);self.assertFalse(r['native_started'])
   self.assertEqual(m['comparison']['arm'],'024');self.assertEqual(m['comparison']['order'],['024'])
   self.assertFalse(m['runtime_performed']);self.assertFalse(m['functional_pass'])
   derivation=m['build024_derivation']
   self.assertEqual(derivation['baseline_arm'],'023');self.assertTrue(derivation['single_arm'])
   self.assertFalse(derivation['automatic_retry']);self.assertFalse(derivation['native_started'])
   self.assertIn('proposal only',derivation['important_origin_recovery'])
   self.assertIn('replan/reset only',derivation['grounded_replan'])
   self.assertEqual(derivation['old_weapon_unavailable_reason'],'UNKNOWN')
   for key in ['canonical_profile_migration','host_budget','read_contract']:self.assertEqual(m[key],old[key])
   for key in ['map','seconds','diagnostics','hard_difficulty','same_config_nav','observer_fps','automatic_sequence','automatic_retry']:
    self.assertEqual(m['comparison'][key],old['comparison'][key])
   for name in old['sources']:
    actual=(dest/name).read_text()if name in b.CHANGED else (dest/name).read_bytes()
    self.assertEqual(b.reverse(name,actual)if name in b.CHANGED else actual,(b.PARENT/name).read_text()if name in b.CHANGED else(b.PARENT/name).read_bytes())
   for key,base in [('runtime_dependencies',Path('/')),('sources',dest),('draft_source_sha256',dest)]:
    for path,h in m[key].items():self.assertEqual(b.sha(base/path),h)
   self.assertFalse(any(Path(p).is_relative_to(b.OLD_BUILD)for p in m['runtime_dependencies']))
   with self.assertRaises(ValueError):b.prepare(dest)
 def test_parent_pin_failure_precedes_destination_creation(self):
  b=self.builder();real=b.sha
  with tempfile.TemporaryDirectory()as d,patch.object(b,'sha',side_effect=lambda p:'0'*64 if Path(p)==b.PARENT/'run-a4.py'else real(p)):
   dest=Path(d)/'never'
   with self.assertRaisesRegex(ValueError,'parent'):b.prepare(dest)
   self.assertFalse(dest.exists())

if __name__=='__main__':unittest.main()
