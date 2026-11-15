"""Focused trouble-only retarget checks; never import a runtime controller."""
import copy,importlib.util,unittest
from pathlib import Path
from unittest.mock import patch
import prepare_navigation_build031_hole as hole
HERE=Path(__file__).resolve().parent
PARENT=Path('/srv/tse-nav20-031-hole600-diag1-disabled-20261115')
def policy():
 p=HERE/'navigation_build031_trouble_policy.py'
 if not p.exists():p=PARENT/'navigation_build031_hole_policy.py'
 spec=importlib.util.spec_from_file_location('trouble_policy_under_test',p);m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);return m
class Options(unittest.TestCase):
 def test_exact_new_trouble_condition(self):self.assertIsNone(policy().options('trouble',600,1,'031'))
 def test_other_conditions_fail(self):
  for args in [('hole',600,1,'031'),('skulls',600,1,'031'),('trouble',True,1,'031'),('trouble',float('nan'),1,'031'),('trouble',float('inf'),1,'031'),('trouble',599,1,'031'),('trouble',600,True,'031'),('trouble',600,0,'031'),('trouble',600,1,'030'),('trouble',600,1,'032')]:
   with self.subTest(args=args),self.assertRaises(ValueError):policy().options(*args)
class Retarget(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  if not(HERE/'prepare_navigation_build031_trouble.py').exists():raise unittest.SkipTest('actual parent policy supplies behavior RED')
  import prepare_navigation_build031_trouble as b;cls.b=b
 def test_two_whole_inverse_unique_fragments(self):
  b=self.b
  for n in b.CHANGED:
   text=hole.read(PARENT/n).decode();changed=b.apply(n,text)
   self.assertEqual(b.apply(n,changed,True),text)
   for invalid in [changed,text+'\n'+b.DELTAS[n][0][0],text.replace(b.DELTAS[n][0][0],'missing')]:
    with self.assertRaises(ValueError):b.apply(n,invalid)
 def test_runner_binding_preserves_other_fixed_conditions(self):
  b=self.b;t=b.apply('run-a4.py',hole.read(PARENT/'run-a4.py').decode())
  for value in ["choices=('trouble',)",'default=600','choices=(1,),default=1','RUNTIME_REVIEWED=False','hardmap.options(map_key,duration,diag,',str(hole.BUILD/'Sources/Game/GameMP.dll')]:self.assertIn(value,t)
 def test_all_catalog_binding_mutations_rejected(self):
  b=self.b;c=hole.load(PARENT/'map-catalog.json')
  for k in b.TROUBLE:
   m=copy.deepcopy(c);m['maps']['trouble'][k]='wrong'
   with self.subTest(k=k),self.assertRaises(ValueError):b.validate_assets(m)
 def test_asset_bytes_fail_closed(self):
  b=self.b;c=hole.load(PARENT/'map-catalog.json');p=Path(b.TROUBLE['private_nav_source'])
  with patch.object(b,'read',side_effect=lambda q:b'bad'if Path(q)==p else hole.read(q)),self.assertRaises(ValueError):b.validate_assets(c)
  with patch.object(b.zipfile.ZipFile,'read',lambda self,name,*args,**kw:b'bad'),self.assertRaises(ValueError):b.validate_assets(c)
 def test_parent_pins_and_complete81_build_values_required(self):
  b=self.b
  with patch.object(b,'sha',side_effect=lambda p:'0'*64 if str(p)==str(PARENT/'source-manifest.json')else hole.sha(p)),self.assertRaises(ValueError):b.validate_parent()
  m=hole.load(PARENT/'source-manifest.json');actual={p:h for p,h in m['runtime_dependencies'].items()if Path(p).is_relative_to(hole.BUILD)}
  self.assertEqual(len(actual),81)
  for path in actual:
   x=copy.deepcopy(m);x['runtime_dependencies'][path]='0'*64
   with self.subTest(path=path),patch.object(b,'load',return_value=x),self.assertRaises(ValueError):b.validate_parent()
 def test_existing_destination_fail(self):
  with self.assertRaises(ValueError):self.b.prepare(PARENT)
if __name__=='__main__':unittest.main()
