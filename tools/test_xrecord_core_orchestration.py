"""Controller failure ordering with fake own roles; no native/display execution."""
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
import xrecord_core_controller as c
from test_xrecord_core_binding import fixture

class FakeChild:
 instances=[];fail=None;calls=[]
 def __init__(self,argv,directory,display,ttl,role):
  self.directory=Path(directory);self.role=role;self.identity=dict(pid=100+len(self.instances),start_ticks=10,argv=argv,display=display);self.errors=[];self.forced=False;self.closed=False;self.__class__.instances.append(self)
  if role==self.fail:raise OSError('start '+role)
 def guard(self):pass
 def call(self,command,timeout,**fields):
  self.__class__.calls.append((self.role,command));rows,driver=fixture()
  if command==self.fail:raise TimeoutError(command)
  if command=='initialize':return dict(value=dict(window=driver['window'],root=driver['root'],position=[400,300]))
  if command=='arm':return dict(value=dict(record_version=[1,13],xtest_version=[2,2],xtest_opcode=137,start_count=1,ranges_verified=True))
  if command in('relative','warp'):return dict(value=driver['queries'][command=='warp'])
  return dict(value={})
 def cleanup(self,stop_timeout=None,normal_signal=False):
  self.closed=True
  if self.role in('recorder','driver'):
   value=dict(connections_closed=True,window_destroyed=True,errors=[])if self.role=='driver'else dict(connections_closed=True,context_freed=True,end_verified=True,calls=len(fixture()[0])+2,freed=len(fixture()[0])+2,records=len(fixture()[0])+2,malformed=0,dropped=0,start_count=1,end_count=1,unknown_records=0,budget_failed=False,cleanup_errors=[],errors=[])
   (self.directory/(self.role+'-native-close.json')).write_text(json.dumps(dict(errors=[],native=value)))
  if self.role=='recorder':
   rows,_=fixture();start=dict(callback_serial=1,received_monotonic=.9,kind='start');end=dict(callback_serial=len(rows)+2,received_monotonic=2.,kind='end')
   for r in rows:r['callback_serial']+=1
   (self.directory/'record-raw.jsonl').write_text(''.join(json.dumps(r)+'\n'for r in[start]+rows+[end]))
  return dict(role=self.role,closed=True,reaped=True,forced=False,exit_code=0,errors=[])

class OrchestrationTests(unittest.TestCase):
 def setUp(self):FakeChild.instances=[];FakeChild.calls=[];FakeChild.fail=None
 def execute(self,d):
  with patch.object(c,'RUNTIME_REVIEWED',True),patch.object(c,'OwnChild',FakeChild),patch.object(c,'wait_display'),patch.object(c,'guard_display'),patch.object(c,'display_absent',return_value=True),patch.object(c,'fresh_display_available'),patch.object(c,'check_disk',return_value=10*1024**3):return c.execute(Path(d))
 def test_listening_socket_binding_does_not_confuse_connected_socket_copies(self):
  rows='Num RefCount Protocol Flags Type St Inode Path\n01: 2 0 00010000 0001 01 123 /tmp/.X11-unix/X167\n02: 2 0 00000000 0001 03 124 /tmp/.X11-unix/X167\n'
  self.assertEqual(c.listening_inode(rows), '123')
  with self.assertRaises(ValueError):c.listening_inode(rows.replace('00010000','00000000'))
  with self.assertRaises(ValueError):c.listening_inode(rows+rows.splitlines()[1]+'\n')
 def test_exact_init_arm_relative_observe_warp_observe_then_all_cleanup(self):
  with tempfile.TemporaryDirectory()as d:out=self.execute(d)
  self.assertEqual(out['status'],'PASS_METHOD_PARTIAL_CORE_REQUESTS_ONLY');self.assertTrue(all(x.closed for x in FakeChild.instances))
  self.assertEqual(FakeChild.calls,[('driver','initialize'),('recorder','arm'),('driver','relative'),('recorder','observe'),('driver','warp'),('recorder','observe')])
 def test_end_disk_below_eight_gib_is_sticky_fail_after_all_roles_close(self):
  from types import SimpleNamespace
  with tempfile.TemporaryDirectory()as d,patch.object(c.shutil,'disk_usage',return_value=SimpleNamespace(free=8*1024**3-1)):
   out=self.execute(d)
  self.assertEqual(out['status'],'FAIL_METHOD_CORE_EVIDENCE');self.assertTrue(any('8GiB'in error for error in out['errors']));self.assertTrue(all(child.closed for child in FakeChild.instances))
 def test_timeout_sticks_and_all_started_roles_cleanup_without_next_input(self):
  FakeChild.fail='arm'
  with tempfile.TemporaryDirectory()as d:out=self.execute(d)
  self.assertEqual(out['status'],'FAIL_METHOD_CORE_EVIDENCE');self.assertNotIn(('driver','relative'),FakeChild.calls);self.assertTrue(all(x.closed for x in FakeChild.instances))
 def test_relative_timeout_never_retries_and_never_warps(self):
  FakeChild.fail='relative'
  with tempfile.TemporaryDirectory()as d:out=self.execute(d)
  self.assertEqual(out['status'],'FAIL_METHOD_CORE_EVIDENCE');self.assertEqual(FakeChild.calls.count(('driver','relative')),1);self.assertNotIn(('driver','warp'),FakeChild.calls)
 def test_partial_start_does_not_skip_already_started_display_cleanup(self):
  FakeChild.fail='driver'
  with tempfile.TemporaryDirectory()as d:out=self.execute(d)
  self.assertEqual(out['status'],'FAIL_METHOD_CORE_EVIDENCE');self.assertTrue(FakeChild.instances[0].closed)

if __name__=='__main__':unittest.main()
