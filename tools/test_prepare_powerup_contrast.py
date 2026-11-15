"""Narrow offline retarget/inverse tests; never import the native controller."""
import ast
import copy
import importlib.util
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch


class ContrastBuilder(unittest.TestCase):
 def builder(self):
  self.assertIsNotNone(importlib.util.find_spec('prepare_powerup_contrast'),'missing disabled contrast builder')
  import prepare_powerup_contrast as b
  return b
 def test_whole_source_inverse_and_only_fixed_deltas(self):
  b=self.builder()
  self.assertEqual(b.CHANGED,('run-a4.py','adapter_policy.py'))
  for flag in(0,1):
   for name in b.CHANGED:
    old=(b.PARENT/name).read_text();new=b.transform(name,old,flag)
    self.assertEqual(b.reverse(name,new,flag),old);ast.parse(new)
    with self.assertRaises(ValueError):b.transform(name,new,flag)
    with self.assertRaises(ValueError):b.transform(name,old+old,flag)
   run=b.transform('run-a4.py',(b.PARENT/'run-a4.py').read_text(),flag)
   self.assertIn('RUNTIME_REVIEWED=False',run)
   self.assertIn("expected=powerups.game_sha(role)",run)
   self.assertIn("inventory=InventoryReader(server[0],server[1],R/'server',powerups.DEDICATED_SHA)",run)
   self.assertIn("shutil.copy2(DEDICATED_DLL,R/'server/Bin/GameMP.dll')",run)
   self.assertIn("str(POWERUP_FLAG)",run)
   # Keep stage after sealing; cleanup and the finalizer are byte-identical.
   self.assertLess(run.index('transaction.seal()'),run.index('stage_observer20('))
   old=(b.PARENT/'run-a4.py').read_text()
   self.assertEqual(run[run.index('  finally:\n   was_raising='):],old[old.index('  finally:\n   was_raising='):])
   self.assertNotEqual(b.reverse('run-a4.py',run.replace('INVENTORY=1','INVENTORY=0',1),flag),old)
  with self.assertRaises(ValueError):b.transform('strict_backend.py','',0)
 def test_arm_sources_normalize_only_flag_and_namespaces(self):
  b=self.builder()
  for name in b.CHANGED:
   off=b.transform(name,(b.PARENT/name).read_text(),0)
   on=b.transform(name,(b.PARENT/name).read_text(),1)
   self.assertEqual(b.normalize_arm(off,0),b.normalize_arm(on,1))
 def test_exact_81_dedicated_pins(self):
  b=self.builder();pins=b.validate_dedicated();self.assertEqual(len(pins),81)
  m=json.loads((b.BUILD/'manifest.json').read_text())
  self.assertEqual(len(m['source_sha256']),49);self.assertEqual(len(m['overlay_sha256']),30)
  for path,h in pins.items():self.assertEqual(b.sha(path),h)
 def test_candidate_provenance_and_closure_mutants(self):
  b=self.builder();original=json.loads((b.BUILD/'manifest.json').read_text())
  for key,value in [('build_ok',False),('repo_commit','0'*40),('repo_tree','0'*40),('dll_sha256','0'*64),('candidate',str(b.PARENT/'run-a4.py')),('source_overlay','/tmp/wrong'),('source_count',14)]:
   m=copy.deepcopy(original);m[key]=value
   with self.assertRaises(ValueError):b.dedicated_pins(m)
  for key in('source_sha256','overlay_sha256'):
   m=copy.deepcopy(original);h=m[key].pop(next(iter(m[key])));m[key]['../escape']=h
   with self.assertRaises(ValueError):b.dedicated_pins(m)
  real=b.sha
  for target in(b.BUILD/'manifest.json',b.DLL,b.BUILD/'Sources/Game/Game.cpp',b.OVERLAY/'DevPowerupFilter.h'):
   with patch.object(b,'sha',side_effect=lambda p,t=target:'0'*64 if Path(p)==t else real(p)):
    with self.assertRaises(ValueError):b.validate_dedicated()
 def test_parent_conditions_and_hashes_fail_before_destination(self):
  b=self.builder();original=json.loads((b.PARENT/'source-manifest.json').read_text())
  for section,key,value in [('comparison','arm','018'),('comparison','seconds',599),('comparison','diagnostics',1),('comparison','observer_fps',30),('comparison','hard_difficulty',3),('candidate','dll_sha256',b.DEDICATED_SHA)]:
   m=copy.deepcopy(original);m[section][key]=value
   with self.assertRaises(ValueError):b.validate_parent_manifest(m)
  for key,value in [('runtime_reviewed',False),('runtime_performed',True),('qualified',True),('functional_pass',True)]:
   m=copy.deepcopy(original);m[key]=value
   with self.assertRaises(ValueError):b.validate_parent_manifest(m)
  real=b.sha
  for target in(b.PARENT/'source-manifest.json',b.PARENT/'canonical.ini',b.PARENT/'a4_ordered_memory_v3.py'):
   with tempfile.TemporaryDirectory()as d,patch.object(b,'sha',side_effect=lambda p,t=target:'0'*64 if Path(p)==t else real(p)):
    dest=Path(d)/'none'
    with self.assertRaisesRegex(ValueError,'parent'):b.prepare(dest,0)
    self.assertFalse(dest.exists())
 def test_two_fresh_disabled_packages_every_pin_and_unchanged_files(self):
  b=self.builder();parent=json.loads((b.PARENT/'source-manifest.json').read_text())
  with tempfile.TemporaryDirectory()as d:
   for flag in(0,1):
    dest=Path(d)/str(flag);r=b.prepare(dest,flag);m=json.loads((dest/'source-manifest.json').read_text())
    for key in('runtime_reviewed','runtime_performed','qualified','functional_pass'):self.assertIs(m[key],False)
    self.assertFalse(r['native_started']);self.assertEqual(m['powerup_contrast']['flag'],flag)
    self.assertEqual(m['powerup_contrast']['profile'],dict(name='BOT-Expert-Rifle',tier=5,persona='marksman',canonical_index=7))
    for key in('candidate','host_budget','read_contract','canonical_profile_migration'):self.assertEqual(m[key],parent[key])
    self.assertEqual(m['comparison']['dedicated'],b.DEDICATED_SHA)
    for name in parent['sources']:
     if name in b.CHANGED:self.assertEqual(b.reverse(name,(dest/name).read_text(),flag),(b.PARENT/name).read_text())
     else:self.assertEqual((dest/name).read_bytes(),(b.PARENT/name).read_bytes(),name)
    for key,base in [('runtime_dependencies',Path('/')),('sources',dest),('draft_source_sha256',dest)]:
     for name,h in m[key].items():self.assertEqual(b.sha(base/name),h,(key,name))
    self.assertEqual({p:h for p,h in m['runtime_dependencies'].items()if Path(p).is_relative_to(b.BUILD)or Path(p).is_relative_to(b.OVERLAY)},b.validate_dedicated())
    finalizer='/srv/tse-milestone-a-20261111/tools/native_trial_evidence.py'
    self.assertEqual(m['runtime_dependencies'][finalizer],parent['runtime_dependencies'][finalizer])
    with self.assertRaises(ValueError):b.prepare(dest,flag)
   off=json.loads((Path(d)/'0/source-manifest.json').read_text());on=json.loads((Path(d)/'1/source-manifest.json').read_text())
   self.assertEqual(off['host_budget'],on['host_budget'])


if __name__=='__main__':unittest.main()
