"""Fixed disabled diagnostic derivation only; never import a runtime controller."""
import ast
import importlib.util
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

class DiagnosticPolicy(unittest.TestCase):
 def module(self):
  self.assertIsNotNone(importlib.util.find_spec('build023_supply_diagnostic_policy'),'missing diagnostic-only policy')
  import build023_supply_diagnostic_policy as p
  return p
 def test_only_exact180_diag1_023_redstation(self):
  p=self.module();p.options('redstation',180,1,'023');p.options('redstation',180.,1,'023')
  for args in [('redstation',600,0,'023'),('redstation',180,0,'023'),('redstation',180,1,'022'),('yodeller',180,1,'023'),('redstation',179,1,'023'),('redstation',True,1,'023'),('redstation',float('nan'),1,'023'),('redstation',float('inf'),1,'023'),('redstation',180,True,'023'),('redstation',180,1.,'023')]:
   with self.subTest(args=args),self.assertRaises(ValueError):p.options(*args)
 def test_catalog_exact_and_old_policies_unrelaxed(self):
  p=self.module();p.hard_options('redstation',180,1,{'redstation':{}})
  for catalog in [{},{'yodeller':{}}]:
   with self.assertRaises(ValueError):p.hard_options('redstation',180,1,catalog)
  b=Derivation().builder()
  for name in ['navigation_comparison_policy.py','a4_hard_map_policy.py']:
   ns={};exec((b.PARENT/name).read_text(),ns)
   with self.assertRaises(ValueError):ns['options']('redstation',180,1,'023'if name.startswith('navigation')else{'redstation':{}})

class Derivation(unittest.TestCase):
 def builder(self):
  self.assertIsNotNone(importlib.util.find_spec('prepare_build023_supply_diagnostic'),'missing fixed diagnostic builder')
  import prepare_build023_supply_diagnostic as b
  return b
 def test_exact_two_source_reverse_and_no_other_functions_change(self):
  b=self.builder();self.assertEqual(set(b.CHANGED),{'run-a4.py','adapter_policy.py'})
  for name in b.CHANGED:
   old=(b.PARENT/name).read_text();new=b.transform(name,old)
   self.assertEqual(b.reverse(name,new),old);ast.parse(new)
   for text in [new,new+'\n'+old]:
    with self.assertRaises(ValueError):b.transform(name,text)
   oldfunc={n.name:ast.dump(n,include_attributes=False)for n in ast.parse(old).body if isinstance(n,ast.FunctionDef)}
   newfunc={n.name:ast.dump(n,include_attributes=False)for n in ast.parse(new).body if isinstance(n,ast.FunctionDef)}
   self.assertEqual(set(oldfunc),set(newfunc))
   for func in oldfunc:
    if func not in ('main','options'):self.assertEqual(oldfunc[func],newfunc[func],(name,func))
 def test_diagnostic_cli_and_status_without_gate_or_finalize_change(self):
  b=self.builder();old=(b.PARENT/'run-a4.py').read_text();new=b.transform('run-a4.py',old)
  for needle in ['RUNTIME_REVIEWED=False','default=180','choices=(1,),default=1','PASS_LIMITED_SUPPLY_DIAGNOSTIC_OBSERVATION_ONLY','SUPPLY_DIAGNOSTIC_ONLY_NO_QUALIFICATION','finalize_trial_evidence(report,expected_roles=(\'server\',\'botA\',\'botB\',\'vanilla\'))']:
   self.assertIn(needle,new)
  self.assertNotIn('PASS_LIMITED_A4_OBSERVATION_FUNCTIONAL_REVIEW_REQUIRED',new)
  self.assertEqual(new.count('inventory.sample('),old.count('inventory.sample('))
  self.assertEqual(new.count('time.sleep('),old.count('time.sleep('))
  self.assertEqual(new.count('checked_query()'),old.count('checked_query()'))
 def test_parent_and_build_pins_before_destination(self):
  b=self.builder();real=b.sha
  for target in [b.PARENT/'source-manifest.json',b.PARENT/'run-a4.py']:
   with tempfile.TemporaryDirectory()as tmp,patch.object(b,'sha',side_effect=lambda p:'0'*64 if Path(p)==target else real(p)):
    dest=Path(tmp)/'never'
    with self.assertRaises(ValueError):b.prepare(dest)
    self.assertFalse(dest.exists())
  with tempfile.TemporaryDirectory()as tmp,patch.object(b.build023,'validate_build',side_effect=ValueError('build pin')):
   dest=Path(tmp)/'never'
   with self.assertRaisesRegex(ValueError,'build pin'):b.prepare(dest)
   self.assertFalse(dest.exists())
 def test_package_every_pin_all_other_sources_and_conditions(self):
  b=self.builder()
  with tempfile.TemporaryDirectory()as tmp:
   dest=Path(tmp)/'disabled';result=b.prepare(dest);m=json.loads((dest/'source-manifest.json').read_text());old=json.loads((b.PARENT/'source-manifest.json').read_text())
   for field in ['runtime_reviewed','runtime_performed','qualified','functional_pass']:self.assertIs(m[field],False)
   for field in ['automatic_retry','automatic_sequence','native_started']:self.assertIs(m['diagnostic'][field],False)
   self.assertEqual((m['comparison']['arm'],m['comparison']['seconds'],m['comparison']['diagnostics']),('023',180,1))
   self.assertEqual(m['comparison']['order'],['023']);self.assertEqual(m['comparison']['observer_fps'],20)
   for key in ['canonical_profile_migration','host_budget','read_contract','candidate']:self.assertEqual(m[key],old[key])
   for key in ['map','hard_difficulty','dedicated','same_config_nav','observer_fps','automatic_sequence','automatic_retry']:self.assertEqual(m['comparison'][key],old['comparison'][key])
   for name in old['sources']:
    actual=(dest/name).read_text()if name in b.CHANGED else(dest/name).read_bytes()
    self.assertEqual(b.reverse(name,actual)if name in b.CHANGED else actual,(b.PARENT/name).read_text()if name in b.CHANGED else(b.PARENT/name).read_bytes())
   for key,base in [('runtime_dependencies',Path('/')),('sources',dest),('draft_source_sha256',dest)]:
    for name,h in m[key].items():self.assertEqual(b.sha(base/name),h)
   self.assertEqual(result['qualified'],False)
   self.assertIn('one per second',m['diagnostic']['unavailable_log_rate_limit'])
   self.assertEqual(m['diagnostic']['missing_or_ambiguous_reason'],'UNKNOWN')
   self.assertIn('different condition',m['diagnostic']['comparison_claim'])
   with self.assertRaises(ValueError):b.prepare(dest)
 def test_build_and_original_source_diagnostics_unchanged(self):
  b=self.builder();pins=b.build023.validate_build();self.assertEqual(len(pins),77)
  p=b.build023.BUILD/'overlay/BotSupplyNative.h'
  self.assertEqual(b.sha(p),'f070a62ac096c01203d6c28ebc621d591c0489346aabadfb628fae0bb685b1af')
  text=p.read_text();self.assertIn('if(!bot_bDiagnostics||!std::isfinite(now)||now<0)return false;',text)
  self.assertIn('now-last<1',text);self.assertIn('[CecilSupplyDiagUnavailable]',text)

if __name__=='__main__':unittest.main()
