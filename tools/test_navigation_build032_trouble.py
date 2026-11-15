"""Exact032 Trouble retarget policy and source bounds; no runtime imports."""
import copy,importlib.util,unittest
from unittest.mock import patch
from pathlib import Path
HERE=Path(__file__).resolve().parent
PARENT=Path('/srv/tse-nav20-031-trouble600-diag1-disabled-20261115')
def policy():
 p=HERE/'navigation_build032_trouble_policy.py'
 if not p.exists():p=PARENT/'navigation_build031_trouble_policy.py'
 spec=importlib.util.spec_from_file_location('new032_policy',p);m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);return m
class Options(unittest.TestCase):
 def test_actual_exact032_condition(self):
  try:policy().options('trouble',600,1,'032');admitted=True
  except ValueError:admitted=False
  self.assertTrue(admitted,'actual031 policy cannot yet admit the exact032 condition')
 def test_wrong_conditions_rejected(self):
  for args in [('trouble',600,1,'031'),('trouble',600,1,'033'),('hole',600,1,'032'),('trouble',599,1,'032'),('trouble',True,1,'032'),('trouble',float('nan'),1,'032'),('trouble',600,True,'032'),('trouble',600,0,'032')]:
   with self.subTest(args=args),self.assertRaises(ValueError):policy().options(*args)
class Retarget(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  import prepare_navigation_build032_trouble as b;cls.b=b
 def test_three_exact_whole_source_inverses_and_staging(self):
  b=self.b
  for name in b.CHANGED:
   text=b.read(PARENT/name).decode();changed=b.apply(name,text)
   self.assertEqual(b.apply(name,changed,True),text)
   for bad in [changed,text+'\n'+b.DELTAS[name][0][0],text.replace(b.DELTAS[name][0][0],'absent')]:
    with self.subTest(name=name),self.assertRaises(ValueError):b.apply(name,bad)
 def test_runner_conditions_unchanged(self):
  b=self.b;t=b.apply('run-a4.py',b.read(PARENT/'run-a4.py').decode())
  for exact in ["choices=('trouble',)",'default=600','choices=(1,),default=1','RUNTIME_REVIEWED=False',"hardmap.options(map_key,duration,diag,policy.prepared.catalog()['maps'])",str(b.BUILD/'Sources/Game/GameMP.dll')]:self.assertIn(exact,t)
  for n in ['transaction.py','a4_ordered_memory_v3.py','native_inventory.py']:
   self.assertNotIn(n,b.CHANGED)
 def test_actual_full81_closure_and_exact_header_only_delta(self):
  b=self.b;new=b.load(b.BUILD/'manifest.json');pins=b.validate_build(new)
  self.assertEqual(len(pins),81)
  old=b.load(b.OLD_BUILD/'manifest.json');delta=b.input_delta(old,new)
  for key in delta:self.assertEqual(delta[key]['changed'],['BotSupplyNative.h'])
  for key in ['source_sha256','overlay_sha256']:
   bad=copy.deepcopy(new);bad[key][next(k for k in bad[key]if k!='BotSupplyNative.h')]='0'*64
   with self.assertRaises(ValueError):b.input_delta(old,bad)
   with self.assertRaises(ValueError):b.validate_build(bad)
 def test_wrong_manifest_candidate_closure_rejected(self):
  b=self.b;new=b.load(b.BUILD/'manifest.json')
  for k,v in [('build_ok',False),('qualified',True),('repo_commit','wrong'),('repo_tree','wrong'),('dll_sha256','0'*64),('source_count',14),('candidate','other'),('source_overlay','other'),('source_sha256',{}),('overlay_sha256',{})]:
   bad=copy.deepcopy(new);bad[k]=v
   with self.subTest(k=k),self.assertRaises(ValueError):b.validate_build(bad)
  with patch.object(b,'sha',return_value='0'*64),self.assertRaises(ValueError):b.validate_build(new)
 def test_parent_map_duration_diag_fps_bots_and_pin_values_rejected(self):
  b=self.b;m=b.load(PARENT/'source-manifest.json')
  for group,k,v in [('comparison','map','hole'),('comparison','seconds',599),('comparison','diagnostics',0),('comparison','observer_fps',30),('comparison','hard_difficulty',3),('comparison','arm','032'),('map_case','bot_count',7),('map_case','bot_tier',2),('map_case','automatic_retry',True)]:
   bad=copy.deepcopy(m);bad[group][k]=v
   with self.subTest(k=k),patch.object(b,'load',return_value=bad),self.assertRaises(ValueError):b.validate_parent()
  bad=copy.deepcopy(m);old=next(p for p in bad['runtime_dependencies']if Path(p).is_relative_to(b.OLD_BUILD));bad['runtime_dependencies'][old]='0'*64
  with patch.object(b,'load',return_value=bad),self.assertRaises(ValueError):b.validate_parent()
  with patch.object(b,'sha',return_value='0'*64),self.assertRaises(ValueError):b.validate_parent()
 def test_fresh_destination_only(self):
  with self.assertRaises(ValueError):self.b.prepare(PARENT)
if __name__=='__main__':unittest.main()
