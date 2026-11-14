"""Only own short-lived Python fake children; no Xlib/display/runtime."""
from contextlib import contextmanager
import json
from pathlib import Path
import tempfile
import time
import unittest
from unittest.mock import patch

from xrecord_core_process import OwnChild

PROGRAM='''import json,sys,time
for line in sys.stdin:
 r=json.loads(line);command=r['command']
 if command=='hang':time.sleep(30)
 elif command=='boolean':print(json.dumps(dict(id=True,ok=True)),flush=True)
 elif command=='oversize':print('x'*20000,flush=True)
 else:
  print(json.dumps(dict(id=r['id']+(1 if command=='wrong'else 0),ok=True)),flush=True)
  if command=='stop':break
'''


@contextmanager
def child():
 with tempfile.TemporaryDirectory()as directory:
  path=Path(directory)/'own-fake.py';path.write_text(PROGRAM)
  kid=OwnChild(['/usr/bin/python3','-B',str(path),'--display',':167'],directory,':167',ttl=10,role='fake')
  try:yield kid
  finally:kid.cleanup(stop_timeout=.1)


class OwnProcessTests(unittest.TestCase):
 def test_normal_stop_receipt_and_actual_child_exit_is_not_an_identity_failure(self):
  with child()as kid:
   self.assertTrue(kid.call('ping',timeout=.5)['ok'])
   receipt=kid.cleanup(stop_timeout=.5)
  self.assertTrue(receipt['closed']);self.assertTrue(receipt['reaped']);self.assertFalse(receipt['forced']);self.assertEqual(receipt['exit_code'],0);self.assertEqual(receipt['errors'],[])
 def test_timeout_is_sticky_and_only_owned_fake_child_is_reaped(self):
  with child()as kid:
   with self.assertRaises(TimeoutError):kid.call('hang',timeout=.03)
   started=time.monotonic();receipt=kid.cleanup()
  self.assertLess(time.monotonic()-started,5.);self.assertTrue(receipt['closed']);self.assertTrue(receipt['reaped']);self.assertTrue(receipt['errors']);self.assertTrue(receipt['forced'])
 def test_wrong_serial_and_oversized_reply_are_failures(self):
  for command in('wrong','oversize'):
   with self.subTest(command=command),child()as kid:
    with self.assertRaises(ValueError):kid.call(command,timeout=.5)
    self.assertTrue(kid.errors)
 def test_boolean_reply_serial_is_not_a_valid_integer_identity(self):
  with child()as kid:
   with self.assertRaises(ValueError):kid.call('boolean',timeout=.5)

 def test_changed_identity_prevents_any_ipc_write(self):
  with child()as kid:
   fake=dict(kid.identity);fake['argv']=['foreign']
   with patch('xrecord_core_process.actual_identity',return_value=fake),self.assertRaises(RuntimeError):kid.call('ping',timeout=.1)
   self.assertEqual(kid.serial,0)
 def test_actual_identity_reads_proc_display_not_the_expected_argument(self):
  import xrecord_core_process as m
  from types import SimpleNamespace
  with tempfile.TemporaryDirectory()as directory:
   root=Path(directory);process=root/'123';process.mkdir()
   (process/'cmdline').write_bytes(b'python3\0OWN.py\0:167\0')
   (process/'environ').write_bytes(b'DISPLAY=:154\0SECRET=must-not-emit\0')
   with patch.object(m,'Path',return_value=root),patch.object(m,'start_ticks',return_value=456):actual=m.actual_identity(SimpleNamespace(pid=123),':167')
   self.assertEqual(actual['display'],':154');self.assertNotIn('SECRET',str(actual));self.assertNotIn('must-not-emit',str(actual))
 def test_missing_duplicate_or_oversized_proc_display_fails_closed(self):
  import xrecord_core_process as m
  from types import SimpleNamespace
  with tempfile.TemporaryDirectory()as directory:
   root=Path(directory);process=root/'123';process.mkdir();(process/'cmdline').write_bytes(b'python3\0OWN.py\0:167\0')
   for payload in(b'OTHER=x\0',b'DISPLAY=:167\0DISPLAY=:154\0',b'X='+b'x'*65536):
    (process/'environ').write_bytes(payload)
    with self.subTest(size=len(payload)),patch.object(m,'Path',return_value=root),patch.object(m,'start_ticks',return_value=456),self.assertRaises(ValueError):m.actual_identity(SimpleNamespace(pid=123),':167')
 def test_partial_popen_start_failure_keeps_handle_reaps_child_and_private_owner(self):
  import xrecord_core_process as m
  with tempfile.TemporaryDirectory()as directory:
   path=Path(directory)/'own-fake.py';path.write_text(PROGRAM);created=[];original=m.subprocess.Popen
   def spawn(*args,**kw):p=original(*args,**kw);created.append(p);return p
   with patch.object(m.subprocess,'Popen',side_effect=spawn),patch.object(m,'start_ticks',side_effect=FileNotFoundError('partial start')),self.assertRaises(FileNotFoundError):OwnChild(['/usr/bin/python3','-B',str(path),':167'],directory,':167',ttl=10,role='partial')
   self.assertEqual(len(created),1);self.assertIsNotNone(created[0].returncode)
   owner=json.loads((Path(directory)/'partial-owner.json').read_text());self.assertEqual(owner['pid'],created[0].pid)
   self.assertEqual((Path(directory)/'partial-owner.json').stat().st_mode&0o777,0o600)
   failure=json.loads((Path(directory)/'partial-start-failure.json').read_text());self.assertTrue(failure['closed']);self.assertTrue(failure['reaped']);self.assertTrue(failure['start_error'])


if __name__=='__main__':unittest.main()
