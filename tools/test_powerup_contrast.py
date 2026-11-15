"""Portable contrast tests; no controller import or native/runtime calls."""
import importlib.util
import json
import os
from pathlib import Path
import tempfile
import unittest


def log(flag, before=(1,2,3,4,5,6), after=None, removed=None):
 if after is None:after=before if flag==0 else(0,before[1],0,*before[3:])
 if removed is None:removed=0 if flag==0 else before[0]+before[2]
 def row(phase,values):
  return '[DevPowerups] enabled=%d phase=%s '%(flag,phase)+' '.join('%s=%d'%(k,v)for k,v in zip(('invisibility','invulnerability','damage','speed','bomb','unknown'),values))
 return 'unrelated startup\n'+row('before',before)+'\n[DevPowerups] removed=%d\n'%removed+row('after',after)+'\nunrelated gameplay\n'


class ContrastPolicy(unittest.TestCase):
 def policy(self):
  self.assertIsNotNone(importlib.util.find_spec('powerup_contrast_policy'),'missing fixed flag/census policy')
  import powerup_contrast_policy as p
  return p
 def test_fixed_options(self):
  p=self.policy()
  for flag in(0,1):p.options('redstation',600,0,flag)
  for args in [('skulls',600,0,0),('redstation',599,0,0),('redstation',601,0,0),('redstation',True,0,0),('redstation',600,1,0),('redstation',600,False,0),('redstation',600,0,True),('redstation',600,0,-1),('redstation',600,0,2)]:
   with self.assertRaises(ValueError):p.options(*args)
 def test_role_separation(self):
  p=self.policy();bot='ec820d0461313c41fec2b477f57109310d3c71a77b4423955ac69f3807566530'
  self.assertEqual(p.game_sha('server'),p.DEDICATED_SHA)
  self.assertEqual(p.game_sha('vanilla'),p.ORIGINAL_SHA)
  for role in('botA','botB'):self.assertEqual(p.game_sha(role),bot)
  with self.assertRaises(ValueError):p.game_sha('unknown')
 def test_exact_effective_census_off_on(self):
  p=self.policy()
  for flag in(0,1):
   r=p.census(log(flag),flag);self.assertEqual(r['flag'],flag);self.assertEqual(r['affected_before'],4)
   self.assertEqual(r['removed'],4 if flag else 0);self.assertFalse(r['crc_cause_proven'])
 def test_missing_duplicate_reordered_or_malformed_marker(self):
  p=self.policy();raw=log(1)
  for bad in('',raw.replace('[DevPowerups] removed=4\n',''),raw+raw,raw.replace('phase=before','phase=after'),raw.replace('removed=4','removed=4 extra'),raw.replace('bomb=5','bomb=-5'),raw.replace('invisibility=1','invisibility=nan'),raw.replace('[DevPowerups] removed','prefix [DevPowerups] removed')):
   with self.assertRaises(ValueError):p.census(bad,1)
 def test_invocation_flag_must_match_twice(self):
  p=self.policy()
  for raw,flag in[(log(0),1),(log(1),0),(log(1).replace('enabled=1 phase=after','enabled=0 phase=after'),1)]:
   with self.assertRaises(ValueError):p.census(raw,flag)
  for flag in(True,-1,2):
   with self.assertRaises(ValueError):p.census(log(1),flag)
 def test_nonzero_affected_required_in_both_arms(self):
  p=self.policy()
  for flag in(0,1):
   with self.assertRaisesRegex(ValueError,'uninformative'):p.census(log(flag,before=(0,2,0,4,5,6)),flag)
 def test_off_must_not_remove_or_change_any_type(self):
  p=self.policy()
  for raw in(log(0,removed=1),log(0,after=(0,2,3,4,5,6)),log(0,after=(1,2,3,4,5,7))):
   with self.assertRaises(ValueError):p.census(raw,0)
 def test_on_exact_type0_type2_removal_preserves_others(self):
  p=self.policy()
  for raw in(log(1,removed=3),log(1,after=(1,2,0,4,5,6)),log(1,after=(0,2,1,4,5,6)),log(1,after=(0,0,0,4,5,6)),log(1,after=(0,2,0,4,5,0))):
   with self.assertRaises(ValueError):p.census(raw,1)
 def test_private_snapshot_preserved_before_rejection_and_no_overwrite(self):
  p=self.policy()
  with tempfile.TemporaryDirectory()as d:
   dest=Path(d)/'bad.log';p.archive_log(dest,log(0))
   self.assertEqual(os.stat(dest).st_mode&0o777,0o600)
   with self.assertRaises(ValueError):p.census(dest.read_text(),1)
   self.assertEqual(dest.read_text(),log(0))
   with self.assertRaises(FileExistsError):p.archive_log(dest,'overwrite')


if __name__=='__main__':unittest.main()
