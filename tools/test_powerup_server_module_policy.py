"""Portable evidence-contract tests. No process, controller or memory reads."""
import copy
import importlib.util
import json
import os
from pathlib import Path
import sys
import tempfile
import unittest

PARENT=Path('/srv/tse-powerup-off0-048-red600-disabled-20261115')
IDENTITY=[1619536,134974110]  # Actual own closed061540 server, not a saved sample.
HASHES={'Engine.dll':'b79bf8bb3927fe4f8f252e141d721ae5c738df02218f0ecc12da5c1afbcb534f',
 'EntitiesMP.dll':'7f595f2a7fc96a978b3467983e8f17c70d827f17a5f4ee887f9c7a1f20b1d350',
 'GameMP.dll':'fe4a77bd1eae15a25cfeb67cf5dfdd6643cba59661f2ca3e99467a9fb15b06e0'}


def fixture():
 return dict(process_identity=IDENTITY.copy(),hashes=HASHES.copy(),consistency='two_equal_reads_not_atomic',players=[],game_tick=0.)


def original_core():
 sys.path.insert(0,str(PARENT))
 try:
  spec=importlib.util.spec_from_file_location('original_powerup_fixture_core',PARENT/'a4_fire_observer_v2.py')
  module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module);return module
 finally:sys.path.pop(0)


class ServerModulePolicy(unittest.TestCase):
 def policy(self):
  self.assertIsNotNone(importlib.util.find_spec('powerup_server_module_policy'),'missing strictly server-bound module adapter')
  import powerup_server_module_policy as p
  return p
 def test_real_reader_contract_reproduces_original_hash_failure_then_requires_adapter(self):
  sample=fixture();before=copy.deepcopy(sample)
  with self.assertRaisesRegex(ValueError,'sample Original module hashes'):original_core().check_sample(sample,IDENTITY)
  self.policy().check_sample_hashes(sample,'server',IDENTITY)
  self.assertEqual(sample,before)
 def test_only_exact_server_role_and_pid_start(self):
  p=self.policy();p.check_sample_hashes(fixture(),'server',IDENTITY)
  for role in('botA','botB','vanilla','SERVER',None):
   with self.assertRaises(ValueError):p.check_sample_hashes(fixture(),role,IDENTITY)
  for identity in([1619537,134974110],[1619536,134974111],[True,1],[],[1]):
   with self.assertRaises(ValueError):p.check_sample_hashes(fixture(),'server',identity)
 def test_wrong_original_bot_or_unknown_game_hash_stays_rejected(self):
  p=self.policy()
  for h in('1c41da35b3fc47378c407b770e1bd1dcc2b7e6bf676c140586bc6035461d4208','ec820d0461313c41fec2b477f57109310d3c71a77b4423955ac69f3807566530','0'*64):
   sample=fixture();sample['hashes']['GameMP.dll']=h
   with self.assertRaises(ValueError):p.check_sample_hashes(sample,'server',IDENTITY)
 def test_engine_entities_missing_extra_or_changed_hash_rejected(self):
  p=self.policy()
  for name in HASHES:
   for kind in('missing','wrong'):
    sample=fixture()
    if kind=='missing':sample['hashes'].pop(name)
    else:sample['hashes'][name]='0'*64
    with self.subTest(name=name,kind=kind),self.assertRaises(ValueError):p.check_sample_hashes(sample,'server',IDENTITY)
  sample=fixture();sample['hashes']['extra.dll']='0'*64
  with self.assertRaises(ValueError):p.check_sample_hashes(sample,'server',IDENTITY)


class FirstRawPreservation(unittest.TestCase):
 policy=ServerModulePolicy.policy
 def archive(self,path,sample,**extra):
  data=dict(read_serial=1,group='botA_actual',phase='paused_smoke',server_identity=IDENTITY,started=1.,ended=1.01);data.update(extra)
  return self.policy().archive_first_sample(path,sample,**data)
 def test_rejected_hash_bind_preserves_complete_first_raw_before_failure(self):
  p=self.policy();sample=fixture();sample['hashes']['GameMP.dll']='0'*64;sample['unknown_original_field']={'x':[1,2,3]};before=copy.deepcopy(sample)
  with tempfile.TemporaryDirectory()as d:
   path=Path(d)/'first.jsonl';self.archive(path,sample)
   with self.assertRaises(ValueError):p.check_sample_hashes(sample,'server',IDENTITY)
   rows=path.read_text().splitlines();self.assertEqual(len(rows),1);row=json.loads(rows[0]);self.assertEqual(row['sample'],before)
   self.assertEqual(row['read_serial'],1);self.assertEqual(row['group'],'botA_actual');self.assertEqual(row['phase'],'paused_smoke')
   self.assertEqual(row['server_identity'],IDENTITY);self.assertEqual(row['read_interval'],[1.,1.01])
   self.assertEqual(os.stat(path).st_mode&0o777,0o600);self.assertEqual(sample,before)
 def test_pid_or_consistency_failure_also_preserves_raw(self):
  p=self.policy()
  for kind in('pid','consistency'):
   sample=fixture()
   if kind=='pid':sample['process_identity'][1]+=1
   else:sample['consistency']='unknown'
   with tempfile.TemporaryDirectory()as d:
    path=Path(d)/'first.jsonl';self.archive(path,sample)
    if kind=='pid':
     with self.assertRaises(ValueError):p.check_sample_hashes(sample,'server',IDENTITY)
    self.assertEqual(json.loads(path.read_text())['sample'],sample)
 def test_exclusive_archive_cannot_duplicate_overwrite_or_follow_symlink(self):
  with tempfile.TemporaryDirectory()as d:
   path=Path(d)/'first.jsonl';self.archive(path,fixture());before=path.read_bytes()
   with self.assertRaises(FileExistsError):self.archive(path,fixture())
   self.assertEqual(path.read_bytes(),before)
   alias=Path(d)/'alias';alias.symlink_to(path)
   with self.assertRaises(FileExistsError):self.archive(alias,fixture())
 def test_only_first_paused_read_and_existing_clock_provenance(self):
  for extra in(dict(read_serial=2),dict(read_serial=True),dict(group='botB_actual'),dict(phase='gameplay'),dict(started=float('nan')),dict(ended=.5)):
   with tempfile.TemporaryDirectory()as d:
    path=Path(d)/'none.jsonl'
    with self.subTest(extra=extra),self.assertRaises(ValueError):self.archive(path,fixture(),**extra)
    self.assertFalse(path.exists())
 def test_fixed_64k_record_bound_no_unbounded_file(self):
  p=self.policy();self.assertEqual(p.MAX_FIRST_SAMPLE_BYTES,65536)
  sample=fixture();sample['large']='x'*65536
  with tempfile.TemporaryDirectory()as d:
   path=Path(d)/'none.jsonl'
   with self.assertRaises(ValueError):self.archive(path,sample)
   self.assertFalse(path.exists())


if __name__=='__main__':unittest.main()
