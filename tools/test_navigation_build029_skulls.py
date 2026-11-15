"""One fixed disabled029 package; exact complete manifests, no runtime import."""
import ast
import copy
import importlib.util
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

class Skulls029(unittest.TestCase):
 def builder(self):
  self.assertIsNotNone(importlib.util.find_spec('prepare_navigation_build029_skulls'),'missing029 builder')
  import prepare_navigation_build029_skulls as b
  return b
 def test_fixed_case_and_three_exact_retarget_inverses(self):
  b=self.builder();from navigation_build029_skulls_policy import options
  options('skulls',600,1,'029')
  for args in [('hole',600,1,'029'),('skulls',600,1,'027'),('skulls',599,1,'029'),('skulls',600,True,'029')]:
   with self.assertRaises(ValueError):options(*args)
  self.assertEqual(set(b.CHANGED),{'run-a4.py','adapter_policy.py','navigation_comparison_policy.py'})
  for name in b.CHANGED:
   old=(b.PARENT/name).read_text();new=b.transform(name,old);ast.parse(new)
   self.assertEqual(b.reverse(name,new),old)
   with self.assertRaises(ValueError):b.transform(name,new)
 def test_complete_new_build_hashsets_and_productive_delta(self):
  b=self.builder();pins=b.validate_build();self.assertEqual(len(pins),79)
  change=b.validate_productive_delta()
  for group in ('source_sha256','overlay_sha256'):
   self.assertEqual(change[group]['changed'],['BotDriver.cpp','BotSupplyNative.h'])
   self.assertEqual(change[group]['added'],['driver_final_decision.h'])
  original=json.loads((b.BUILD/'manifest.json').read_text())
  for key,value in [('build_ok',False),('qualified',True),('repo_commit','0'*40),('repo_tree','0'*40),('dll_sha256','0'*64),('candidate',str(b.OLD_BUILD/'Sources/Game/GameMP.dll')),('source_count',14)]:
   m=copy.deepcopy(original);m[key]=value
   with self.assertRaises(ValueError):b.validate_build_manifest(m)
  for group in ('source_sha256','overlay_sha256'):
   m=copy.deepcopy(original);key=next(iter(m[group]));m[group][key]='0'*64
   with self.assertRaises(ValueError):b.validate_build_manifest(m)
   m=copy.deepcopy(original);value=m[group].pop(key);m[group]['same_count_wrong_name.h']=value
   with self.assertRaises(ValueError):b.validate_build_manifest(m)
 def test_fresh_disabled_all_values_and_no_old_targets(self):
  b=self.builder();parent=json.loads((b.PARENT/'source-manifest.json').read_text())
  with tempfile.TemporaryDirectory()as tmp:
   dest=Path(tmp)/'disabled';r=b.prepare(dest);m=json.loads((dest/'source-manifest.json').read_text())
   for k in ('runtime_reviewed','runtime_performed','qualified','functional_pass'):self.assertIs(m[k],False)
   for key in ('host_budget','read_contract','canonical_profile_migration'):self.assertEqual(m[key],parent[key])
   self.assertEqual(m['comparison']['arm'],'029');self.assertEqual(m['map_case']['bot_count'],8)
   self.assertEqual(m['map_case']['bot_tier'],3);self.assertEqual(m['map_case']['original_observer_fps'],20)
   self.assertFalse(m['map_case']['automatic_retry']);self.assertFalse(m['map_case']['automatic_sequence'])
   for name in parent['sources']:
    new=(dest/name).read_text()if name in (*b.CHANGED,'strict_backend.py')else None
    if name=='run-a4.py':
     from cleanup_failure_receipt import reverse_controller
     self.assertEqual(b.reverse(name,reverse_controller(new)),(b.PARENT/name).read_text())
    elif name in b.CHANGED:self.assertEqual(b.reverse(name,new),(b.PARENT/name).read_text())
    elif name=='strict_backend.py':
     from native_cgroup_exit_patch import reverse
     self.assertEqual(reverse(new),(b.PARENT/name).read_text())
    else:self.assertEqual((dest/name).read_bytes(),(b.PARENT/name).read_bytes(),name)
   old={k:v for k,v in parent['runtime_dependencies'].items()if Path(k).is_relative_to(b.OLD_BUILD)}
   self.assertEqual(len(old),77);self.assertFalse(set(old)&set(m['runtime_dependencies']))
   expected={}
   for name,value in parent['runtime_dependencies'].items():
    p=Path(name)
    if p.is_relative_to(b.OLD_BUILD)or p==b.PARENT/'navigation_build027_skulls_policy.py':continue
    if p.is_relative_to(b.PARENT):p=dest/p.relative_to(b.PARENT);value=b.sha(p)
    expected[str(p)]=value
   expected.update(b.validate_build())
   for name in ('navigation_build029_skulls_policy.py','cleanup_failure_receipt.py'):expected[str(dest/name)]=b.sha(dest/name)
   self.assertEqual(m['runtime_dependencies'],expected)
   self.assertEqual({k:v for k,v in expected.items()if Path(k).is_relative_to(b.BUILD)},b.validate_build())
   self.assertEqual(m['sources'],{name:b.sha(dest/name)for name in sorted(set(parent['sources'])|set(b.ADDITIONS)|set(b.DIFF_NAMES))})
   self.assertEqual(m['draft_source_sha256'],{p.name:b.sha(p)for p in sorted(dest.glob('*.py'))})
   for group,base in [('runtime_dependencies',Path('/')),('sources',dest),('draft_source_sha256',dest)]:
    for p,value in m[group].items():self.assertEqual(b.sha(base/p),value,(group,p))
   self.assertIn('RUNTIME_REVIEWED=False',(dest/'run-a4.py').read_text());self.assertFalse(r['qualified'])
   with self.assertRaises(ValueError):b.prepare(dest)
 def test_manifest_guard_changes_fail_before_destination(self):
  b=self.builder();original=json.loads((b.PARENT/'source-manifest.json').read_text())
  for section,key,value in [('comparison','arm','029'),('map_case','bot_tier',2),('map_case','hard_difficulty',3),('comparison','diagnostics',0)]:
   mutant=copy.deepcopy(original);mutant[section][key]=value
   with self.assertRaises(ValueError):b.validate_parent_manifest(mutant)
  real=b.sha
  for target in (b.PARENT/'source-manifest.json',b.PARENT/'canonical.ini',b.BUILD/'manifest.json',b.DLL):
   with tempfile.TemporaryDirectory()as tmp,patch.object(b,'sha',side_effect=lambda p,t=target:'0'*64 if Path(p)==t else real(p)):
    dest=Path(tmp)/'none'
    with self.assertRaises(ValueError):b.prepare(dest)
    self.assertFalse(dest.exists())
 def test_old77_exact_targets_not_just_count(self):
  b=self.builder();original=json.loads((b.PARENT/'source-manifest.json').read_text())
  self.assertTrue(hasattr(b,'validate_old_targets'),'missing explicit full old build closure check')
  good=b.validate_old_targets(original);self.assertEqual(len(good),77)
  for change_name in (False,True):
   m=copy.deepcopy(original);key=next(p for p in good if p.endswith('/BotDriver.cpp'))
   if change_name:m['runtime_dependencies'][str(b.OLD_BUILD/'same-count.h')]=m['runtime_dependencies'].pop(key)
   else:m['runtime_dependencies'][key]='0'*64
   with self.assertRaises(ValueError):b.validate_old_targets(m)

if __name__=='__main__':unittest.main()
