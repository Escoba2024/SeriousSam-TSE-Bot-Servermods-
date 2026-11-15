"""Bounded offline027 retarget tests; no controller/runtime import."""
import ast
import copy
import importlib.util
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch


class Skulls027(unittest.TestCase):
 def builder(self):
  self.assertIsNotNone(importlib.util.find_spec('prepare_navigation_build027_skulls'),'missing disabled027 retarget')
  import prepare_navigation_build027_skulls as b
  return b
 def test_options(self):
  self.builder()
  from navigation_build027_skulls_policy import options
  options('skulls',600,1,'027')
  for args in [('hole',600,1,'027'),('skulls',600,1,'026'),('skulls',599,1,'027'),('skulls',601,1,'027'),('skulls',True,1,'027'),('skulls',600,True,'027'),('skulls',600,0,'027')]:
   with self.assertRaises(ValueError):options(*args)
 def test_exact_three_inverses(self):
  b=self.builder();self.assertEqual(set(b.CHANGED),{'run-a4.py','adapter_policy.py','navigation_comparison_policy.py'})
  for name in b.CHANGED:
   old=(b.PARENT/name).read_text();new=b.transform(name,old)
   self.assertNotEqual(old,new);self.assertEqual(b.reverse(name,new),old);ast.parse(new)
   with self.assertRaises(ValueError):b.transform(name,new)
   with self.assertRaises(ValueError):b.transform(name,old+old)
  with self.assertRaises(ValueError):b.transform('a4_hard_map_policy.py',(b.PARENT/'a4_hard_map_policy.py').read_text())
  run=b.transform('run-a4.py',(b.PARENT/'run-a4.py').read_text())
  self.assertIn('RUNTIME_REVIEWED=False',run)
  mutant=run.replace('INVENTORY=1','INVENTORY=0',1)
  self.assertNotEqual(b.reverse('run-a4.py',mutant),(b.PARENT/'run-a4.py').read_text())
 def test_exact_build_pins_and_two_productive_deltas(self):
  b=self.builder();pins=b.validate_build();self.assertEqual(len(pins),77)
  self.assertEqual(b.validate_productive_delta(),{'source_sha256':['BotDriver.cpp','BotSupplyNative.h'],'overlay_sha256':['BotDriver.cpp','BotSupplyNative.h']})
  for p,h in pins.items():self.assertEqual(b.sha(p),h)
 def test_build_mutants(self):
  b=self.builder();original=json.loads((b.BUILD/'manifest.json').read_text())
  for key,value in [('build_ok',False),('repo_commit','0'*40),('repo_tree','0'*40),('dll_sha256','0'*64),('candidate',str(b.OLD_BUILD/'Sources/Game/GameMP.dll')),('source_count',14)]:
   m=copy.deepcopy(original);m[key]=value
   with self.assertRaises(ValueError):b.validate_build_manifest(m)
  for key in ('source_sha256','overlay_sha256'):
   m=copy.deepcopy(original);h=m[key].pop(next(iter(m[key])));m[key]['../escape']=h
   with self.assertRaises(ValueError):b.validate_build_manifest(m)
  real=b.sha
  for target in (b.BUILD/'manifest.json',b.DLL,b.BUILD/'Sources/Game/BotSupplyNative.h',b.BUILD/'overlay/BotDriver.cpp'):
   with patch.object(b,'sha',side_effect=lambda p,t=target:'0'*64 if Path(p)==t else real(p)):
    with self.assertRaises(ValueError):b.validate_build()
 def test_parent_mutants(self):
  b=self.builder();original=json.loads((b.PARENT/'source-manifest.json').read_text())
  for section,key,value in [('comparison','arm','027'),('comparison','seconds',599),('comparison','diagnostics',0),('comparison','observer_fps',30),('map_case','map','hole'),('map_case','bot_count',7),('map_case','bot_tier',2),('map_case','hard_difficulty',3)]:
   m=copy.deepcopy(original);m[section][key]=value
   with self.assertRaises(ValueError):b.validate_parent_manifest(m)
  for key in ('runtime_reviewed','runtime_performed','functional_pass','qualified'):
   m=copy.deepcopy(original);m[key]=True
   with self.assertRaises(ValueError):b.validate_parent_manifest(m)
 def test_fresh_disabled_package_all_pins_and_unchanged_bytes(self):
  b=self.builder();parent=json.loads((b.PARENT/'source-manifest.json').read_text())
  with tempfile.TemporaryDirectory()as d:
   dest=Path(d)/'disabled';r=b.prepare(dest);m=json.loads((dest/'source-manifest.json').read_text())
   for key in ('runtime_reviewed','runtime_performed','qualified','functional_pass'):self.assertIs(m[key],False)
   self.assertFalse(r['native_started']);self.assertEqual(m['comparison']['arm'],'027')
   self.assertEqual(m['candidate']['dll_size'],446464)
   for key in ('host_budget','read_contract','canonical_profile_migration'):self.assertEqual(m[key],parent[key])
   self.assertEqual(m['map_case']['map'],'skulls');self.assertEqual(m['map_case']['seconds'],600)
   for k,v in [('hard_difficulty',2),('bot_count',8),('bot_tier',3),('original_observer_fps',20),('diagnostics',1)]:self.assertEqual(m['map_case'][k],v)
   self.assertFalse(m['map_case']['automatic_retry']);self.assertFalse(m['map_case']['automatic_sequence'])
   for name in parent['sources']:
    if name in b.CHANGED:self.assertEqual(b.reverse(name,(dest/name).read_text()),(b.PARENT/name).read_text())
    else:self.assertEqual((dest/name).read_bytes(),(b.PARENT/name).read_bytes(),name)
   for group,base in [('runtime_dependencies',Path('/')),('sources',dest),('draft_source_sha256',dest)]:
    for name,h in m[group].items():self.assertEqual(b.sha(base/name),h,(group,name))
   self.assertFalse(any(Path(p).is_relative_to(b.OLD_BUILD)for p in m['runtime_dependencies']))
   target={p:h for p,h in m['runtime_dependencies'].items()if Path(p).is_relative_to(b.BUILD)}
   self.assertEqual(target,b.validate_build());self.assertEqual(len(target),77)
   for name in ('canonical.ini','settings.txt','a4_hard_map_policy.py'):
    self.assertEqual((dest/name).read_bytes(),(b.PARENT/name).read_bytes())
   finalizer='/srv/tse-milestone-a-20261111/tools/native_trial_evidence.py'
   self.assertEqual(m['runtime_dependencies'][finalizer],parent['runtime_dependencies'][finalizer])
   with self.assertRaises(ValueError):b.prepare(dest)
 def test_parent_hash_failure_before_destination(self):
  b=self.builder();real=b.sha
  for target in (b.PARENT/'source-manifest.json',b.PARENT/'canonical.ini',b.PARENT/'a4_ordered_memory_v3.py'):
   with tempfile.TemporaryDirectory()as d,patch.object(b,'sha',side_effect=lambda p,t=target:'0'*64 if Path(p)==t else real(p)):
    dest=Path(d)/'none'
    with self.assertRaisesRegex(ValueError,'parent'):b.prepare(dest)
    self.assertFalse(dest.exists())


if __name__=='__main__':unittest.main()
