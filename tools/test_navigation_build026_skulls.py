"""Offline fixed026 Skulls diagnostic preparation; no controller/runtime import."""
import ast
import copy
import hashlib
import importlib.util
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch


class Skulls026(unittest.TestCase):
 def builder(self):
  self.assertIsNotNone(importlib.util.find_spec('prepare_navigation_build026_skulls'),
                       'missing new disabled026 Skulls builder')
  import prepare_navigation_build026_skulls as b
  return b
 def test_strict_fixed_options(self):
  self.builder()
  from navigation_build026_skulls_policy import options
  options('skulls',600,1,'026')
  for args in [('hole',600,1,'026'),('redstation',600,1,'026'),('skulls',600,1,'024'),
               ('skulls',599,1,'026'),('skulls',601,1,'026'),('skulls',True,1,'026'),
               ('skulls',float('nan'),1,'026'),('skulls',600,0,'026'),
               ('skulls',600,True,'026'),('skulls',600,1.0,'026')]:
   with self.assertRaises(ValueError,msg=repr(args)):options(*args)
 def test_actual_existing_hardmap_options_accept_only_diag1(self):
  b=self.builder()
  with tempfile.TemporaryDirectory()as d:
   dest=Path(d)/'disabled';b.prepare(dest)
   text=(dest/'a4_hard_map_policy.py').read_text()
   functions=[n for n in ast.parse(text).body if isinstance(n,ast.FunctionDef)and n.name in ('need','options')]
   env={};exec(compile(ast.fix_missing_locations(ast.Module(body=functions,type_ignores=[])),'actual-hardmap-options','exec'),env)
   env['options']('skulls',600,1,{'skulls':{}})
   for args in [('skulls',600,0,{'skulls':{}}),('skulls',600,True,{'skulls':{}}),('skulls',599,1,{'skulls':{}}),('unknown',600,1,{'skulls':{}})]:
    with self.assertRaises(ValueError):env['options'](*args)
 def test_exact_four_source_inverses(self):
  b=self.builder();self.assertEqual(set(b.CHANGED),{'run-a4.py','adapter_policy.py','navigation_comparison_policy.py','a4_hard_map_policy.py'})
  for name in b.CHANGED:
   before=(b.PARENT/name).read_text();after=b.transform(name,before)
   self.assertNotEqual(before,after);self.assertEqual(b.reverse(name,after),before);ast.parse(after)
   with self.assertRaises(ValueError):b.transform(name,after)
   with self.assertRaises(ValueError):b.transform(name,before+before)
  run=b.transform('run-a4.py',(b.PARENT/'run-a4.py').read_text())
  self.assertIn('RUNTIME_REVIEWED=False',run)
  self.assertIn("choices=(1,),default=1",run)
  self.assertIn("choices=('skulls',)",run)
  self.assertIn('PASS_LIMITED_REACQUIRE_DIAGNOSTIC_OBSERVATION_ONLY',run)
  with self.assertRaises(ValueError):b.transform('host_budget.py',(b.PARENT/'host_budget.py').read_text())
  # The inverse is not allowed to hide a changed original resource gate.
  mutant=run.replace('INVENTORY=1','INVENTORY=0',1)
  self.assertNotEqual(b.reverse('run-a4.py',mutant),(b.PARENT/'run-a4.py').read_text())
 def test_exact_77_actual026_build_targets(self):
  b=self.builder();pins=b.validate_build();self.assertEqual(len(pins),77)
  self.assertIn(str(b.BUILD/'manifest.json'),pins);self.assertIn(str(b.DLL),pins)
  self.assertEqual(sum(Path(p).is_relative_to(b.BUILD/'Sources/Game')for p in pins),48)
  self.assertEqual(sum(Path(p).is_relative_to(b.BUILD/'overlay')for p in pins),28)
  for p,h in pins.items():self.assertEqual(b.sha(p),h)
 def test_wrong_candidate_manifest_and_closure_metadata(self):
  b=self.builder();original=json.loads((b.BUILD/'manifest.json').read_text())
  for key,value in [('build_ok',False),('repo_commit','0'*40),('repo_tree','0'*40),
                    ('dll_sha256','0'*64),('candidate',str(b.OLD_BUILD/'Sources/Game/GameMP.dll')),
                    ('source_overlay',str(b.OLD_BUILD/'overlay')),('source_count',14)]:
   m=copy.deepcopy(original);m[key]=value
   with self.assertRaises(ValueError,msg=key):b.validate_build_manifest(m)
  for key in ('source_sha256','overlay_sha256'):
   m=copy.deepcopy(original);m[key].pop(next(iter(m[key])))
   with self.assertRaises(ValueError,msg=key):b.validate_build_manifest(m)
   m=copy.deepcopy(original);value=m[key].pop(next(iter(m[key])));m[key]['../escape']=value
   with self.assertRaises(ValueError,msg=key):b.validate_build_manifest(m)
 def test_wrong_actual_build_hashes_or_size_fail(self):
  b=self.builder();real=b.sha
  for target in (b.BUILD/'manifest.json',b.DLL,b.BUILD/'Sources/Game/BotSupplyNative.h',b.BUILD/'overlay/BotSupplyNative.h'):
   with patch.object(b,'sha',side_effect=lambda p,t=target:'0'*64 if Path(p)==t else real(p)):
    with self.assertRaises(ValueError,msg=str(target)):b.validate_build()
  with patch.object(b,'DLL_SIZE',443391):
   with self.assertRaises(ValueError):b.validate_build()
 def test_parent_conditions_cannot_be_changed(self):
  b=self.builder();original=json.loads((b.PARENT/'source-manifest.json').read_text())
  for section,key,value in [('comparison','map','hole'),('comparison','arm','026'),
      ('comparison','seconds',599),('comparison','diagnostics',1),('comparison','hard_difficulty',1),
      ('comparison','observer_fps',30),('map_case','bot_count',7),('map_case','bot_tier',2),
      ('map_case','original_observer_fps',30),('map_case','diagnostics',1)]:
   m=copy.deepcopy(original);m[section][key]=value
   with self.assertRaises(ValueError,msg=repr((section,key))):b.validate_parent_manifest(m)
  m=copy.deepcopy(original);m['runtime_reviewed']=True
  with self.assertRaises(ValueError):b.validate_parent_manifest(m)
 def test_parent_config_or_manifest_change_prevents_destination(self):
  b=self.builder();real=b.sha
  for target in (b.PARENT/'source-manifest.json',b.PARENT/'canonical.ini',b.PARENT/'settings.txt',b.PARENT/'a4_ordered_memory_v3.py'):
   with tempfile.TemporaryDirectory()as d,patch.object(b,'sha',side_effect=lambda p,t=target:'0'*64 if Path(p)==t else real(p)):
    dest=Path(d)/'never'
    with self.assertRaisesRegex(ValueError,'parent'):b.prepare(dest)
    self.assertFalse(dest.exists())
 def test_assets_and_invariant_cohort_config(self):
  b=self.builder();catalog=json.loads((b.PARENT/'map-catalog.json').read_text())
  proof=b.validate_assets('skulls',catalog)
  self.assertEqual(proof['nodes'],296);self.assertFalse(proof['loaded_world_proven'])
  old=(b.PARENT/'adapter_policy.py').read_text();new=b.transform('adapter_policy.py',old)
  for name in ('assignments','replace','cohort','bootstrap','InitialObservations','active_evidence','verify_fixture_assets'):
   a=next(n for n in ast.parse(old).body if getattr(n,'name',None)==name)
   c=next(n for n in ast.parse(new).body if getattr(n,'name',None)==name)
   self.assertEqual(ast.dump(a),ast.dump(c),name)
  # Execute only actual extracted pure config functions, no runtime imports.
  selected=[n for n in ast.parse(new).body if isinstance(n,ast.FunctionDef)and n.name in ('assignments','replace','cohort')]
  import re
  env={'hashlib':hashlib,'re':re,'CANDIDATE_SHA':b.DLL_SHA,'canonical':lambda:(b.PARENT/'canonical.ini').read_text()}
  exec(compile(ast.fix_missing_locations(ast.Module(body=selected,type_ignores=[])),'actual-cohort-functions','exec'),env)
  baseline=env['assignments'](env['canonical']())
  for role,offset in [('botA','0'),('botB','4')]:
   row=env['cohort'](role,1);actual=env['assignments'](row['config']);expected=dict(baseline,bot_bDiagnostics='1',bot_iRosterOffset=offset)
   self.assertEqual(actual,expected);self.assertEqual(row['game_sha256'],b.DLL_SHA)
 def test_fresh_disabled_package_all_bytes_pins_and_no024_build_dependency(self):
  b=self.builder();parent=json.loads((b.PARENT/'source-manifest.json').read_text())
  with tempfile.TemporaryDirectory()as d:
   dest=Path(d)/'disabled';result=b.prepare(dest);m=json.loads((dest/'source-manifest.json').read_text())
   for key in ('runtime_reviewed','runtime_performed','qualified','functional_pass'):self.assertIs(m[key],False,key)
   self.assertFalse(result['native_started'])
   self.assertEqual(m['comparison']['arm'],'026');self.assertEqual(m['comparison']['map'],'skulls')
   self.assertEqual(m['comparison']['seconds'],600);self.assertEqual(m['comparison']['diagnostics'],1)
   self.assertEqual(m['comparison']['profile_semantics'],'DIAGNOSTIC_OBSERVATION_ONLY_NO_COMPARISON')
   self.assertEqual(m['map_case']['bot_count'],8);self.assertEqual(m['map_case']['bot_tier'],3)
   self.assertEqual(m['map_case']['hard_difficulty'],2);self.assertEqual(m['map_case']['original_observer_fps'],20)
   self.assertFalse(m['map_case']['automatic_sequence']);self.assertFalse(m['map_case']['automatic_retry'])
   self.assertTrue(all(value is False for key,value in m['root_review'].items()if key.startswith('approved_')))
   self.assertEqual(m['candidate']['dll_sha256'],b.DLL_SHA)
   inherited=m['inherited_build024_skulls_metadata']
   for key in ('candidate','comparison','map_case','build024_derivation'):self.assertEqual(inherited[key],parent[key])
   for key in ('host_budget','read_contract','canonical_profile_migration'):self.assertEqual(m[key],parent[key])
   unchanged=[];inverse=[]
   for name in parent['sources']:
    if name in b.CHANGED:
     self.assertEqual(b.reverse(name,(dest/name).read_text()),(b.PARENT/name).read_text());inverse.append(name)
    else:self.assertEqual((dest/name).read_bytes(),(b.PARENT/name).read_bytes(),name);unchanged.append(name)
   self.assertEqual(len(unchanged),77);self.assertEqual(len(inverse),4)
   old=[p for p in parent['runtime_dependencies']if Path(p).is_relative_to(b.OLD_BUILD)]
   self.assertEqual(len(old),77)
   self.assertFalse(any(Path(p).is_relative_to(b.OLD_BUILD)for p in m['runtime_dependencies']))
   self.assertNotIn(str(dest/'navigation_build024_maps_policy.py'),m['runtime_dependencies'])
   self.assertIn(str(dest/'navigation_build026_skulls_policy.py'),m['runtime_dependencies'])
   target={p:h for p,h in m['runtime_dependencies'].items()if Path(p).is_relative_to(b.BUILD)}
   self.assertEqual(target,b.validate_build());self.assertEqual(len(target),77)
   for group,base in [('runtime_dependencies',Path('/')),('sources',dest),('draft_source_sha256',dest)]:
    for name,h in m[group].items():self.assertEqual(b.sha(base/name),h,(group,name))
   with self.assertRaises(ValueError):b.prepare(dest)
 def test_original_finalizer_preserves_diagnostic_scope_and_failures(self):
  b=self.builder()
  import runpy
  actual=runpy.run_path('/srv/tse-milestone-a-20261111/tools/native_trial_evidence.py')['finalize_trial_evidence']
  roles=('server','botA','botB','vanilla')
  raw={'status':'PASS_LIMITED_REACQUIRE_DIAGNOSTIC_OBSERVATION_ONLY','errors':[],
       'cleanup':{r:{'identity':[200+i,1000+i],'closed':True}for i,r in enumerate(roles)},
       'functional_pass':False,'qualified':False}
  before=copy.deepcopy(raw);result=actual(raw,expected_roles=roles)
  self.assertTrue(result.accepted);self.assertEqual(result.status,raw['status']);self.assertEqual(raw,before)
  for kind in ('status','error','unclosed','missing'):
   bad=copy.deepcopy(raw)
   if kind=='status':bad['status']='FAIL'
   if kind=='error':bad['errors'].append('recorded failure')
   if kind=='unclosed':bad['cleanup']['botA']['closed']=False
   if kind=='missing':bad['cleanup'].pop('vanilla')
   result=actual(bad,expected_roles=roles);self.assertFalse(result.accepted);self.assertEqual(result.status,'FAIL')
  old=ast.parse((b.PARENT/'a4_hard_map_policy.py').read_text())
  new=ast.parse(b.transform('a4_hard_map_policy.py',(b.PARENT/'a4_hard_map_policy.py').read_text()))
  for a,c in zip(old.body,new.body):
   if isinstance(a,ast.FunctionDef)and a.name=='options':continue
   self.assertEqual(ast.dump(a),ast.dump(c))


if __name__=='__main__':unittest.main()
