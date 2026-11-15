"""Offline fixed-case preparation checks; no runtime/controller imports."""
import ast
import copy
import importlib.util
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch


class MapCases(unittest.TestCase):
 def builder(self):
  self.assertIsNotNone(importlib.util.find_spec('prepare_navigation_build024_maps'),'missing disabled024 map-case builder')
  import prepare_navigation_build024_maps as b
  return b
 def test_fixed_case_options_adversarial(self):
  b=self.builder()
  import navigation_build024_maps_policy as p
  self.assertEqual(set(p.MAPS),{'skulls','trouble','hole','yodeller'})
  for case in p.MAPS:
   p.options(case,600,0,'024',case)
   for args in [(case,599,0,'024',case),(case,601,0,'024',case),(case,True,0,'024',case),(case,float('nan'),0,'024',case),(case,600,True,'024',case),(case,600,1,'024',case),(case,600,0,'023',case),('redstation',600,0,'024',case),('fortress',600,0,'024',case),('yodeller'if case!='yodeller'else'hole',600,0,'024',case),(case,600,0,'024','redstation')]:
    with self.assertRaises(ValueError,msg=repr(args)):p.options(*args)
 def test_two_changed_sources_reverse_exact_all_cases(self):
  b=self.builder();self.assertEqual(set(b.CHANGED),{'run-a4.py','adapter_policy.py'})
  for case in b.MAPS:
   for name in b.CHANGED:
    old=(b.PARENT/name).read_text();new=b.transform(name,old,case)
    self.assertNotEqual(old,new);self.assertEqual(b.reverse(name,new,case),old);ast.parse(new)
    with self.assertRaises(ValueError):b.transform(name,new,case)
   r=b.transform('run-a4.py',(b.PARENT/'run-a4.py').read_text(),case)
   self.assertIn('RUNTIME_REVIEWED=False',r)
   a=b.transform('adapter_policy.py',(b.PARENT/'adapter_policy.py').read_text(),case)
   self.assertIn("validate(map_key,duration,diag,'024',"+repr(case)+')',a)
   old=ast.parse((b.PARENT/'adapter_policy.py').read_text());new=ast.parse(a)
   for x,y in zip(old.body,new.body):
    if isinstance(x,ast.FunctionDef)and x.name=='options':continue
    self.assertEqual(ast.dump(x),ast.dump(y))
 def test_bad_case_and_ambiguous_anchors_rejected(self):
  b=self.builder()
  for key in ('redstation','compound','KuntaKinte','desert','all','',None):
   with self.assertRaises(ValueError):b.transform('run-a4.py',(b.PARENT/'run-a4.py').read_text(),key)
  raw=(b.PARENT/'run-a4.py').read_text()
  with self.assertRaises(ValueError):b.transform('run-a4.py',raw+raw,'hole')
  with self.assertRaises(ValueError):b.transform('a4_policy.py',(b.PARENT/'a4_policy.py').read_text(),'hole')
 def test_selected_actual_world_and_nav_full_pins(self):
  b=self.builder();catalog=json.loads((b.PARENT/'map-catalog.json').read_text())
  for case in b.MAPS:
   proof=b.validate_assets(case,catalog)
   self.assertEqual(proof['map'],case);self.assertEqual(proof['world_sha256'],catalog['maps'][case]['world_sha256'])
   self.assertEqual(proof['nav_sha256'],catalog['maps'][case]['nav_sha256'])
   self.assertFalse(proof['loaded_world_proven']);self.assertFalse(proof['archive_full_hash_recomputed'])
 def test_changed_asset_hashes_fail(self):
  b=self.builder();c=json.loads((b.PARENT/'map-catalog.json').read_text())
  for field in ('world_sha256','world_crc32','nav_sha256','nav_crc32','nodes'):
   bad=copy.deepcopy(c);bad['maps']['hole'][field]=0 if field=='nodes'else'0'*len(bad['maps']['hole'][field])
   with self.assertRaises(ValueError,msg=field):b.validate_assets('hole',bad)
 def test_build_full47source28overlay_closure(self):
  b=self.builder();self.assertEqual(len(b.validate_build()),77)
  import prepare_navigation_build024 as candidate
  real=candidate.sha
  with patch.object(candidate,'sha',side_effect=lambda p:'0'*64 if Path(p)==b.BUILD/'overlay/BotSupplyNative.h'else real(p)):
   with self.assertRaises(ValueError):b.validate_build()
 def test_case_packages_disabled_all_parent_sources_exact_except_two(self):
  b=self.builder();old=json.loads((b.PARENT/'source-manifest.json').read_text())
  with tempfile.TemporaryDirectory()as d:
   for case in b.MAPS:
    dest=Path(d)/case;r=b.prepare(case,dest);m=json.loads((dest/'source-manifest.json').read_text())
    self.assertFalse(m['runtime_reviewed']);self.assertFalse(m['qualified']);self.assertFalse(m['runtime_performed']);self.assertFalse(m['functional_pass']);self.assertFalse(r['native_started'])
    self.assertEqual(m['map_case']['map'],case);self.assertEqual(m['map_case']['seconds'],600);self.assertEqual(m['map_case']['diagnostics'],0);self.assertFalse(m['map_case']['automatic_sequence']);self.assertFalse(m['map_case']['automatic_retry'])
    self.assertEqual(m['comparison']['map'],case);self.assertEqual(m['comparison']['arm'],'024')
    for k in ('seconds','diagnostics','hard_difficulty','observer_fps','same_config_nav','automatic_sequence','automatic_retry'):
     self.assertEqual(m['comparison'][k],old['comparison'][k])
    for k in ('candidate','canonical_profile_migration','read_contract','host_budget'):
     self.assertEqual(m[k],old[k])
    self.assertFalse(m['root_review']['approved_for_private_a4']);self.assertFalse(m['root_review']['approved_for_private_nav_comparison'])
    for n in old['sources']:
     if n in b.CHANGED:self.assertEqual(b.reverse(n,(dest/n).read_text(),case),(b.PARENT/n).read_text())
     else:self.assertEqual((dest/n).read_bytes(),(b.PARENT/n).read_bytes(),n)
    for key,base in [('runtime_dependencies',Path('/')),('sources',dest),('draft_source_sha256',dest)]:
     for path,h in m[key].items():self.assertEqual(b.sha(base/path),h)
    self.assertIn(str(dest/'navigation_build024_maps_policy.py'),m['runtime_dependencies'])
    with self.assertRaises(ValueError):b.prepare(case,dest)
 def test_parent_pin_change_prevents_destination(self):
  b=self.builder();real=b.sha
  with tempfile.TemporaryDirectory()as d,patch.object(b,'sha',side_effect=lambda p:'0'*64 if Path(p)==b.PARENT/'a4_ordered_memory_v3.py'else real(p)):
   dest=Path(d)/'never'
   with self.assertRaisesRegex(ValueError,'parent'):b.prepare('skulls',dest)
   self.assertFalse(dest.exists())
 def test_wrong_case_prevents_destination(self):
  b=self.builder()
  with tempfile.TemporaryDirectory()as d:
   dest=Path(d)/'never'
   with self.assertRaises(ValueError):b.prepare('redstation',dest)
   self.assertFalse(dest.exists())

if __name__=='__main__':unittest.main()
