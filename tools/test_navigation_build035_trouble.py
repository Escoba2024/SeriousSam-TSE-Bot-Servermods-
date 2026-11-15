"""Narrow actual035 retarget checks, never execute/import a game controller."""
import ast,copy,importlib.util
from pathlib import Path
import unittest
from unittest.mock import patch

HERE=Path(__file__).resolve().parent
def policy():
 p=HERE/'navigation_build035_trouble_policy.py'
 if not p.exists():p=HERE/'navigation_build034_trouble_policy.py'
 spec=importlib.util.spec_from_file_location('actual035_policy',p);m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);return m

class Condition(unittest.TestCase):
 def test_actual_policy_accepts_only_the_new035_condition(self):
  policy().options('trouble',300,1,'035')
 def test_wrong_conditions_remain_rejected(self):
  for args in [('trouble',300,1,'034'),('trouble',600,1,'035'),('hole',300,1,'035'),('trouble',299,1,'035'),('trouble',True,1,'035'),('trouble',float('nan'),1,'035'),('trouble',300,True,'035'),('trouble',300,0,'035')]:
   with self.subTest(args=args),self.assertRaises(ValueError):policy().options(*args)

class Retarget(unittest.TestCase):
 def builder(self):
  import prepare_navigation_build035_trouble as b
  return b
 def test_three_whole_inverses_reject_anchor_and_foreign_behavior_mutants(self):
  b=self.builder();self.assertEqual(set(b.CHANGED),{'run-a4.py','adapter_policy.py','navigation_comparison_policy.py'})
  for name in b.CHANGED:
   text=b.read(b.PARENT/name).decode();changed=b.apply(name,text)
   self.assertEqual(b.apply(name,changed,True),text)
   for bad in(changed,text+'\n#foreign behavior mutation\n',text.replace(b.DELTAS[name][0][0],'absent',1)):
    with self.subTest(name=name),self.assertRaises(ValueError):b.apply(name,bad)
   with self.assertRaises(ValueError):b.apply(name,changed+'\n#foreign mutation\n',True)
  runner=b.apply('run-a4.py',b.read(b.PARENT/'run-a4.py').decode())
  for literal in('default=300','RUNTIME_REVIEWED=False',"choices=('trouble',)",'choices=(1,),default=1',str(b.BUILD/'Sources/Game/GameMP.dll')):self.assertIn(literal,runner)
  self.assertNotIn('a4_hard_map_policy.py',b.CHANGED)
 def test_full_actual81_values_and_header_only_source_delta(self):
  b=self.builder();new=b.load(b.BUILD/'manifest.json');old=b.load(b.OLD_BUILD/'manifest.json')
  expected={str(b.BUILD/'manifest.json'):b.BUILD_SHA,str(b.BUILD/'Sources/Game/GameMP.dll'):b.DLL_SHA}
  for group,sub in(('source_sha256','Sources/Game'),('overlay_sha256','overlay')):
   expected.update({str(b.BUILD/sub/name):value for name,value in new[group].items()})
  self.assertEqual(b.validate_build(new),expected);self.assertEqual(len(expected),81)
  for group,delta in b.input_delta(old,new).items():self.assertEqual(delta['changed'],['BotSupplyNative.h'])
  for group in('source_sha256','overlay_sha256'):
   bad=copy.deepcopy(new);key=next(k for k in bad[group]if k!='BotSupplyNative.h');bad[group][key]='0'*64
   with self.assertRaises(ValueError):b.input_delta(old,bad)
   with self.assertRaises(ValueError):b.validate_build(bad)
   bad=copy.deepcopy(new);bad[group].pop(key)
   with self.assertRaises(ValueError):b.input_delta(old,bad)
  for key,value in(('build_ok',False),('qualified',True),('repo_commit','wrong'),('repo_tree','wrong'),('dll_sha256','0'*64),('source_overlay','wrong'),('candidate','wrong'),('source_count',14)):
   bad=copy.deepcopy(new);bad[key]=value
   with self.subTest(key=key),self.assertRaises(ValueError):b.validate_build(bad)
 def test_actual_parent_contract_and_wrong_pin_values_remain_fatal(self):
  b=self.builder();m=b.load(b.PARENT/'source-manifest.json')
  for group,key,value in(('comparison','arm','035'),('comparison','seconds',600),('comparison','observer_fps',30),('comparison','map','hole'),('comparison','hard_difficulty',3),('map_case','bot_count',7),('map_case','bot_tier',2),('map_case','diagnostics',0),('map_case','automatic_retry',True)):
   bad=copy.deepcopy(m);bad[group][key]=value
   with self.subTest(key=key),patch.object(b,'load',return_value=bad),self.assertRaises(ValueError):b.validate_parent()
  bad=copy.deepcopy(m);key=next(p for p in bad['runtime_dependencies']if Path(p).is_relative_to(b.OLD_BUILD));bad['runtime_dependencies'][key]='0'*64
  with patch.object(b,'load',return_value=bad),self.assertRaises(ValueError):b.validate_parent()
 def test_existing_destination_is_rejected_before_writes(self):
  b=self.builder()
  with self.assertRaises(ValueError):b.prepare(b.PARENT)

if __name__=='__main__':unittest.main(verbosity=2)
