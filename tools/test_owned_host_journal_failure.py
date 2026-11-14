"""Portable review regression: fake child; no subprocess/display/game started."""
import hashlib
import json
import os
from pathlib import Path
import subprocess
import tempfile
import unittest
from unittest.mock import patch
import observe_owned_host_budget as module


class Child:
 pid=os.getpid()
 returncode=0
 def __init__(self):self.wait_calls=0
 def wait(self,timeout=None):
  self.wait_calls+=1
  if self.wait_calls==1:raise subprocess.TimeoutExpired('own-fake-child',timeout)
  return 0


class Journal:
 def __init__(self,file,repeated=False,close_error=False):self.file=file;self.repeated=repeated;self.close_error=close_error;self.flushes=0
 def __enter__(self):return self
 def __exit__(self,*exc):self.close()
 def write(self,value):return self.file.write(value)
 def flush(self):
  self.flushes+=1
  if not self.close_error and(self.flushes==2 or(self.repeated and self.flushes>2)):raise OSError('fixture journal flush failure')
  return self.file.flush()
 def close(self):
  self.file.close()
  if self.close_error:raise OSError('fixture journal close failure')


class JournalFailure(unittest.TestCase):
 def exercise(self,*,repeated=False,close_error=False):
  with tempfile.TemporaryDirectory()as temp:
   base=Path(temp);source=base/'own.py';source.write_text('pass\n');child=Child();original=module.private_open
   def open_file(path):
    file=original(path)
    return Journal(file,repeated,close_error)if path.name=='host-samples.jsonl'else file
   ticks=iter(range(1,8))
   def host():
    tick=next(ticks)
    return tick,f'cpu {50*tick} 0 0 {50*tick} 0 0 0 0',2*2**30,10*2**30
   escaped=None;row=None
   with patch.object(module.subprocess,'Popen',return_value=child),patch.object(module,'private_open',side_effect=open_file),patch.object(module,'read_host',side_effect=host):
    try:row=module.observe(source,hashlib.sha256(source.read_bytes()).hexdigest(),base/'evidence')
    except Exception as exc:escaped=repr(exc)
   self.assertIsNone(escaped,'journal failures must remain in a failed final receipt')
   self.assertEqual(row['status'],'FAIL_HOST_OBSERVATION');self.assertTrue(row['child_reaped'])
   self.assertEqual(row['child_exit_code'],0);self.assertTrue(any('journal' in e for e in row['errors']))
   self.assertFalse(any('AttributeError' in e for e in row['errors']))
   self.assertEqual(row['source_post_sha256'],hashlib.sha256(source.read_bytes()).hexdigest())
   self.assertEqual(json.loads((base/'evidence/receipt.json').read_text()),row)
 def test_one_shot_flush_error_control(self):self.exercise()
 def test_repeated_flush_error_retains_postcheck_and_receipt(self):self.exercise(repeated=True)
 def test_close_error_cannot_leave_passing_receipt(self):self.exercise(close_error=True)


if __name__=='__main__':unittest.main()
