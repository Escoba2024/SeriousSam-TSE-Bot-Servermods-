import hashlib
import json
from pathlib import Path
import tempfile
import time
import unittest
from unittest.mock import patch


class OwnedHostTests(unittest.TestCase):
 def setUp(self):
  self.tmp=tempfile.TemporaryDirectory();self.root=Path(self.tmp.name)
  self.source=self.root/'own.py';self.directory=self.root/'evidence'
  self.counter=0
 def tearDown(self):self.tmp.cleanup()
 def source_pin(self,text):
  self.source.write_text(text);return hashlib.sha256(self.source.read_bytes()).hexdigest()
 def read(self):
  self.counter+=100
  return(time.monotonic(),f'cpu {self.counter} 0 0 {self.counter} 0 0 0 0',2*2**30,10*2**30)
 def observer(self):
  import importlib.util
  self.assertIsNotNone(importlib.util.find_spec('observe_owned_host_budget'),'new outer observer module is missing')
  import observe_owned_host_budget as m
  self.assertTrue(callable(getattr(m,'observe',None)),'new outer observer is missing')
  return m
 def test_samples_cover_blocked_child_and_actual_reaped_exit(self):
  m=self.observer();pin=self.source_pin('import time\nprint("own child marker",flush=True)\ntime.sleep(1.1)\n')
  with patch.object(m,'read_host',self.read):r=m.observe(self.source,pin,self.directory)
  self.assertEqual(r['status'],'PASS_HOST_OBSERVATION_ONLY');self.assertEqual(r['child_exit_code'],0)
  self.assertTrue(r['child_reaped']);self.assertGreaterEqual(len(r['samples']),3)
  self.assertLessEqual(r['samples'][0]['monotonic'],r['spawn_before_monotonic'])
  self.assertGreaterEqual(r['samples'][-1]['monotonic'],r['exit_observed_monotonic'])
  self.assertIn('own child marker',(self.directory/'child.log').read_text())
  self.assertFalse(r['qualified']);self.assertFalse(r['budget_pass_claim'])
  for p in self.directory.iterdir():self.assertEqual(p.stat().st_mode&0o777,0o600)
  self.assertEqual(json.loads((self.directory/'receipt.json').read_text()),r)
 def test_bad_pin_does_not_start_or_create_evidence(self):
  m=self.observer();self.source_pin('raise RuntimeError("must not start")\n')
  with self.assertRaises(ValueError):m.observe(self.source,'0'*64,self.directory)
  self.assertFalse(self.directory.exists())
 def test_existing_evidence_is_preserved_without_child(self):
  m=self.observer();pin=self.source_pin('raise RuntimeError("must not start")\n')
  self.directory.mkdir();marker=self.directory/'keep';marker.write_text('foreign preserved')
  with self.assertRaises(FileExistsError):m.observe(self.source,pin,self.directory)
  self.assertEqual(marker.read_text(),'foreign preserved')
 def test_bad_initial_ram_or_disk_never_launches_child(self):
  m=self.observer();pin=self.source_pin('from pathlib import Path\nPath("unexpected-start").write_text("started")\n')
  for label,ram,disk in [('ram',1,10*2**30),('disk',2*2**30,1)]:
   with self.subTest(label=label),patch.object(m,'read_host',return_value=(time.monotonic(),'cpu 100 0 0 100 0 0 0 0',ram,disk)):
    r=m.observe(self.source,pin,self.root/label)
   self.assertEqual(r['status'],'FAIL_HOST_OBSERVATION');self.assertIsNone(r['child_identity'])
   self.assertFalse((self.root/'unexpected-start').exists())
 def test_violations_stay_failed_after_later_good_samples(self):
  m=self.observer();pin=self.source_pin('import time\ntime.sleep(1.1)\n');calls=0
  def read():
   nonlocal calls
   calls+=1;t,line,ram,disk=self.read()
   return t,line,1 if calls==2 else ram,disk
  with patch.object(m,'read_host',read):r=m.observe(self.source,pin,self.directory)
  self.assertEqual(r['status'],'FAIL_HOST_OBSERVATION');self.assertEqual(r['child_exit_code'],0)
  self.assertTrue(any(s['violations']for s in r['samples']));self.assertTrue(r['errors'])
  self.assertEqual(r['samples'][-1]['violations'],[])
 def test_nonzero_child_and_post_spawn_source_change_fail(self):
  m=self.observer();pin=self.source_pin('from pathlib import Path\nPath(__file__).write_text("changed own fixture")\nraise SystemExit(7)\n')
  with patch.object(m,'read_host',self.read):r=m.observe(self.source,pin,self.directory)
  self.assertEqual(r['status'],'FAIL_HOST_OBSERVATION');self.assertEqual(r['child_exit_code'],7)
  self.assertTrue(r['child_reaped']);self.assertTrue(any('source' in e for e in r['errors']))
 def test_popen_failure_and_host_read_failure_are_retained(self):
  m=self.observer();pin=self.source_pin('pass\n')
  with patch.object(m,'read_host',self.read),patch.object(m.subprocess,'Popen',side_effect=OSError('own launch failed')):
   r=m.observe(self.source,pin,self.directory)
  self.assertEqual(r['status'],'FAIL_HOST_OBSERVATION');self.assertIsNone(r['child_identity']);self.assertTrue(r['errors'])
  self.directory=self.root/'read_failure'
  with patch.object(m,'read_host',side_effect=OSError('host read failed')):
   r=m.observe(self.source,pin,self.directory)
  self.assertEqual(r['status'],'FAIL_HOST_OBSERVATION');self.assertIsNone(r['child_identity'])
  self.assertTrue(any('host read failed' in e for e in r['errors']))


if __name__=='__main__':unittest.main()
