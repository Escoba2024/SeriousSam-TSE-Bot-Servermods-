"""Focused pure retarget tests. No controller imports or runtime starts."""
import copy,importlib.util,unittest
from pathlib import Path
from unittest.mock import patch
import prepare_navigation_build030_skulls as old
HERE=Path(__file__).resolve().parent
PARENT=Path('/srv/tse-nav20-030-skulls600-diag1-timestamps-disabled-20261115')

def policy():
 p=HERE/'navigation_build031_hole_policy.py'
 # Behavioral RED executes the actual old options body, never an import error.
 if not p.exists():p=PARENT/'navigation_build030_skulls_policy.py'
 s=importlib.util.spec_from_file_location('hole_options_under_test',p);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m

class Options(unittest.TestCase):
 def test_exact_hole031(self):self.assertIsNone(policy().options('hole',600,1,'031'))
 def test_all_other_conditions_rejected(self):
  for i,values in enumerate([('redstation',600,1,'031'),('skulls',600,1,'031'),('hole',599,1,'031'),('hole',True,1,'031'),('hole',float('nan'),1,'031'),('hole',float('inf'),1,'031'),('hole',600,True,'031'),('hole',600,0,'031'),('hole',600,1,'030'),('hole',600,1,'032')]):
   with self.subTest(i=i),self.assertRaises(ValueError):policy().options(*values)

class Retarget(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  cls.here=HERE/'prepare_navigation_build031_hole.py'
  if not cls.here.exists():raise unittest.SkipTest('builder not written; options exercises parent RED')
  import prepare_navigation_build031_hole as b;cls.b=b
 def test_whole_three_inverse_and_unique_anchors(self):
  b=self.b
  for n in b.CHANGED:
   t=old.read(PARENT/n).decode();changed=b.apply(n,t)
   self.assertEqual(b.apply(n,changed,True),t)
   with self.assertRaises(ValueError):b.apply(n,changed)
   with self.assertRaises(ValueError):b.apply(n,t+'\n'+b.DELTAS[n][0][0])
 def test_runner_exact_fixed_case(self):
  t=self.b.apply('run-a4.py',old.read(PARENT/'run-a4.py').decode())
  self.assertIn("choices=('hole',)",t);self.assertIn('default=600',t);self.assertIn('choices=(1,),default=1',t)
  self.assertIn('RUNTIME_REVIEWED=False',t);self.assertIn('hardmap.options(map_key,duration,diag,',t)
 def test_build_maps_and_identity_adversaries(self):
  b=self.b;s=b.candidate();m=old.load(b.BUILD/'manifest.json');b.validate_build(m,s)
  for key in ['repo_commit','repo_tree','dll_sha256','candidate','source_overlay','source_count','qualified','build_ok']:
   x=copy.deepcopy(m);x[key]='wrong'
   with self.subTest(key=key),self.assertRaises(ValueError):b.validate_build(x,s)
  for key in ['source_sha256','overlay_sha256']:
   for name in s[key]:
    x=copy.deepcopy(m);x[key][name]='0'*64
    with self.subTest(key=key,name=name),self.assertRaises(ValueError):b.validate_build(x,s)
 def test_exact_input_delta(self):
  b=self.b;o=old.load(b.OLD_BUILD/'manifest.json');n=old.load(b.BUILD/'manifest.json');d=b.input_delta(o,n)
  self.assertEqual(d['source_sha256']['changed'],['BotDriver.cpp','BotSupplyNative.h'])
  self.assertEqual(d['source_sha256']['added'],['picker_custody.h'])
  x=copy.deepcopy(n);x['source_sha256']['Controls.cpp']='0'*64
  with self.assertRaises(ValueError):b.input_delta(o,x)
 def test_full81_target_values_and_missing_source(self):
  b=self.b;m=old.load(b.BUILD/'manifest.json');pins=b.build_pins(b.BUILD,b.BUILD_SHA,b.DLL_SHA,m,81)
  self.assertEqual(len(pins),81)
  for path in pins:
   with self.subTest(path=path),patch.object(b,'sha',side_effect=lambda p: '0'*64 if str(p)==path else old.sha(p)),self.assertRaises(ValueError):
    b.build_pins(b.BUILD,b.BUILD_SHA,b.DLL_SHA,m,81)
 def test_catalog_mutations_rejected_before_asset_reads(self):
  b=self.b;c=old.load(PARENT/'map-catalog.json')
  for k in c['maps']['hole']:
   x=copy.deepcopy(c);x['maps']['hole'][k]='wrong'
   with self.subTest(k=k),self.assertRaises(ValueError):b.validate_assets(x)
 def test_parent_manifest_and_config_repin_rejected(self):
  b=self.b
  with patch.object(b,'sha',side_effect=lambda p:'0'*64 if str(p)==str(PARENT/'source-manifest.json')else old.sha(p)),self.assertRaises(ValueError):b.validate_parent()
  for name in ['canonical.ini','transaction.py','a4_hard_map_policy.py','navigation_observer20.py']:
   with self.subTest(name=name),patch.object(b,'sha',side_effect=lambda p:'0'*64 if str(p)==str(PARENT/name)else old.sha(p)),self.assertRaises(ValueError):b.validate_parent()
 def test_actual_nav_bytes_rejected(self):
  b=self.b;c=old.load(PARENT/'map-catalog.json');nav=Path(b.HOLE['private_nav_source'])
  with patch.object(b,'read',side_effect=lambda p:b'bad' if Path(p)==nav else old.read(p)),self.assertRaises(ValueError):b.validate_assets(c)
 def test_actual_world_bytes_rejected(self):
  b=self.b;c=old.load(PARENT/'map-catalog.json');
  with patch.object(b.zipfile.ZipFile,'read',lambda self,name,*a,**kw:b'bad'),self.assertRaises(ValueError):b.validate_assets(c)
 def test_both_snapshot_nanosecond_fields_are_unchanged(self):
  b=self.b;m=old.load(PARENT/'source-manifest.json')
  names=[p for p in m['sources']if Path(p).name=='transaction.py']
  self.assertEqual(names,['transaction.py'])
  t=old.read(PARENT/'transaction.py').decode()
  self.assertIn("'atime_ns':st.st_atime_ns,'mtime_ns':st.st_mtime_ns",t)
  self.assertIn("os.utime(p,ns=(record['atime_ns'],record['mtime_ns']))",t)
  for name in names:self.assertEqual(old.sha(PARENT/name),'d6c76f6f1263a3c719b1200442b6e6b1a8d9e23506b6d5f3e71b23a095b41978')
 def test_fresh_destination_rejected(self):
  with self.assertRaises(ValueError):self.b.prepare(PARENT)

if __name__=='__main__':unittest.main()
