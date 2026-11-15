"""Fixed new034/300 condition: real inherited behavior RED, no runtime imports."""
import ast,copy,importlib.util,unittest
from unittest.mock import patch
from pathlib import Path
HERE=Path(__file__).resolve().parent
PARENT=Path('/srv/tse-nav20-032-trouble600-diag1-disabled-20261115')
def policy():
 p=HERE/'navigation_build034_trouble_policy.py'
 if not p.exists():p=PARENT/'navigation_build032_trouble_policy.py'
 spec=importlib.util.spec_from_file_location('prospective034_policy',p);m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);return m

def hardmap_options():
 from prepare_navigation_build031_hole import read
 text=read(PARENT/'a4_hard_map_policy.py').decode()
 p=HERE/'prepare_navigation_build034_trouble.py'
 if p.exists():
  spec=importlib.util.spec_from_file_location('prospective034_builder',p);b=importlib.util.module_from_spec(spec);spec.loader.exec_module(b)
  text=b.apply('a4_hard_map_policy.py',text)
 elif hasattr(policy(),'duration_source'):text=policy().duration_source(text)
 tree=ast.parse(text);tree.body=[n for n in tree.body if isinstance(n,ast.FunctionDef)and n.name in ('need','options')]
 env={};exec(compile(tree,'actual-extracted-hardmap-options','exec'),env);return env['options']

class Condition(unittest.TestCase):
 def test_actual034_policy_admits_only_new_condition(self):
  try:policy().options('trouble',300,1,'034');admitted=True
  except ValueError:admitted=False
  self.assertTrue(admitted,'actual inherited032/600 policy cannot admit the authorized034/300 condition yet')
 def test_actual_hardmap_options_accepts_new300(self):
  try:hardmap_options()('trouble',300,1,{'trouble':{}});admitted=True
  except ValueError:admitted=False
  self.assertTrue(admitted,'actual inherited hardmap.options still requires600 seconds')
 def test_wrong_conditions_fail(self):
  for args in [('trouble',600,1,'034'),('trouble',300,1,'033'),('trouble',300,1,'035'),('hole',300,1,'034'),('trouble',299,1,'034'),('trouble',True,1,'034'),('trouble',float('nan'),1,'034'),('trouble',300,True,'034'),('trouble',300,0,'034')]:
   with self.subTest(args=args),self.assertRaises(ValueError):policy().options(*args)
class Retarget(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  import prepare_navigation_build034_trouble as b;cls.b=b
 def test_four_exact_inverses_and_staging(self):
  b=self.b
  self.assertEqual(set(b.CHANGED),{'run-a4.py','adapter_policy.py','navigation_comparison_policy.py','a4_hard_map_policy.py'})
  for name in b.CHANGED:
   text=b.read(PARENT/name).decode();changed=b.apply(name,text)
   self.assertEqual(b.apply(name,changed,True),text)
   anchor=b.DELTAS[name][0][0]
   for bad in [changed,text+'\n'+anchor,text.replace(anchor,'absent',1)]:
    with self.subTest(name=name),self.assertRaises(ValueError):b.apply(name,bad)
 def test_runner_hardmap_call_sampler_and_inner_guard_sources_unchanged(self):
  b=self.b;t=b.apply('run-a4.py',b.read(PARENT/'run-a4.py').decode())
  for exact in ["choices=('trouble',)",'default=300','choices=(1,),default=1','RUNTIME_REVIEWED=False',"hardmap.options(map_key,duration,diag,policy.prepared.catalog()['maps'])",str(b.BUILD/'Sources/Game/GameMP.dll')]:self.assertIn(exact,t)
  for name in ['transaction.py','a4_ordered_memory_v3.py','native_inventory.py','strict_backend.py','host_budget.py']:
   self.assertNotIn(name,b.CHANGED)
  text=b.apply('a4_hard_map_policy.py',b.read(PARENT/'a4_hard_map_policy.py').decode())
  env={};tree=ast.parse(text);tree.body=[n for n in tree.body if isinstance(n,ast.FunctionDef)and n.name in ('need','options')]
  exec(compile(tree,'actual-derived-options','exec'),env)
  for duration in [600,299,True,float('inf')]:
   with self.subTest(duration=duration),self.assertRaises(ValueError):env['options']('trouble',duration,1,{'trouble':{}})
 def test_actual_full81_closure_header_only_and_wrong_provenance(self):
  b=self.b;new=b.load(b.BUILD/'manifest.json');pins=b.validate_build(new)
  self.assertEqual(len(pins),81)
  old=b.load(b.OLD_BUILD/'manifest.json');delta=b.input_delta(old,new)
  for group in delta:self.assertEqual(delta[group]['changed'],['BotSupplyNative.h'])
  for group in ['source_sha256','overlay_sha256']:
   bad=copy.deepcopy(new);bad[group][next(k for k in bad[group]if k!='BotSupplyNative.h')]='0'*64
   with self.assertRaises(ValueError):b.input_delta(old,bad)
   with self.assertRaises(ValueError):b.validate_build(bad)
  for key,value in [('build_ok',False),('qualified',True),('repo_commit','wrong'),('repo_tree','wrong'),('dll_sha256','0'*64),('candidate',str(b.BUILD.parent/'tse-milestone-a-build-035/Sources/Game/GameMP.dll')),('source_overlay','other'),('source_count',14),('source_sha256',{}),('overlay_sha256',{})]:
   bad=copy.deepcopy(new);bad[key]=value
   with self.subTest(key=key),self.assertRaises(ValueError):b.validate_build(bad)
  with patch.object(b,'sha',return_value='0'*64),self.assertRaises(ValueError):b.validate_build(new)
 def test_parent_cohort_map_config_duration_pinvalues_failclosed(self):
  b=self.b;m=b.load(PARENT/'source-manifest.json')
  for group,key,value in [('comparison','map','hole'),('comparison','seconds',300),('comparison','diagnostics',0),('comparison','observer_fps',30),('comparison','hard_difficulty',3),('comparison','arm','034'),('map_case','bot_count',7),('map_case','bot_tier',2),('map_case','automatic_retry',True)]:
   bad=copy.deepcopy(m);bad[group][key]=value
   with self.subTest(key=key),patch.object(b,'load',return_value=bad),self.assertRaises(ValueError):b.validate_parent()
  bad=copy.deepcopy(m);old=next(p for p in bad['runtime_dependencies']if Path(p).is_relative_to(b.OLD_BUILD));bad['runtime_dependencies'][old]='0'*64
  with patch.object(b,'load',return_value=bad),self.assertRaises(ValueError):b.validate_parent()
  with patch.object(b,'sha',return_value='0'*64),self.assertRaises(ValueError):b.validate_parent()
 def test_fresh_destination_only(self):
  with self.assertRaises(ValueError):self.b.prepare(PARENT)

if __name__=='__main__':unittest.main(verbosity=2)
