"""Fake C pointers only; never opens a display or loads Xlib."""
import ctypes as C
import unittest
from types import SimpleNamespace
from unittest.mock import patch
from pathlib import Path
import os
import tempfile
from contextlib import contextmanager, ExitStack
import xrecord_core_native as core
import xrecord_core_method as m
import a1_passive_xrecord_worker as w

class Fake:
 def __init__(self):self.states={};self.contexts={};self.freed=[];self.alloc=[];self.destroyed=[];self.next=100;self.bad=False
 def XRecordAllocRange(self):r=m.RecordRange();self.alloc.append(r);return C.pointer(r)
 def XFree(self,p):self.freed.append(C.addressof(p.contents))
 def XRecordCreateContext(self,d,flags,specs,count,ptrs,nranges):
  self.next+=1;self.contexts[self.next]=int(specs[0]);return self.next
 def XRecordGetContext(self,d,context,out):
  ranges=core.selected_ranges(137);rp=(C.POINTER(m.RecordRange)*4)(*(C.pointer(r)for r in ranges));info=core.RecordClientInfo(0x200000 if self.contexts[context]==9 else 0x400000,4,rp);ip=(C.POINTER(core.RecordClientInfo)*1)(C.pointer(info));state=core.RecordState(0,7,2 if self.bad else 1,ip)
  self.states[context]=(ranges,rp,info,ip,state);C.cast(out,C.POINTER(C.POINTER(core.RecordState)))[0]=C.pointer(state);return 1
 def XRecordFreeState(self,p):self.destroyed.append('state')
 def XRecordFreeContext(self,d,ctx):self.destroyed.append(ctx);return 1
 def XSync(self,*args):pass

class Tests(unittest.TestCase):
 @contextmanager
 def owner_fixture(self):
  with tempfile.TemporaryDirectory()as directory,ExitStack()as stack:
   root=Path(directory);proc=root/'proc/444';(proc/'fd').mkdir(parents=True);(root/'proc/net').mkdir()
   (root/'tmp/.X11-unix').mkdir(parents=True);sock=root/'tmp/.X11-unix/X167';sock.touch();st=sock.stat()
   lock=root/'tmp/.X167-lock';lock.write_text('444');(proc/'cmdline').write_bytes(b'/usr/bin/Xvfb\0:167\0');(proc/'stat').write_bytes(b'444 (Xvfb) S 333\n')
   (proc/'fd/7').symlink_to('socket:[123]');unix=root/'proc/net/unix';unix.write_text('header\n000: 2 0 00010000 0001 01 123 '+str(sock)+'\n')
   cfg=dict(parent=dict(pid=333,start_ticks=10),passive=dict(mode='method',display=':167',display_owner=dict(identity=[444,20],argv=['/usr/bin/Xvfb',':167'],socket_pin=[st.st_dev,st.st_ino,st.st_uid])))
   stack.enter_context(patch.object(w,'Path',lambda p:root/str(p).lstrip('/')))
   stack.enter_context(patch.object(w.os,'getppid',return_value=333));stack.enter_context(patch.object(w,'start_ticks',side_effect=lambda pid:{333:10,444:20}[pid]))
   stack.enter_context(patch.dict(os.environ,{'DISPLAY':':167'}));stack.enter_context(patch.object(w.stat,'S_ISSOCK',return_value=True))
   yield cfg,root
 def test_own_pid_start_actual_environment_and_socket_listener_bindings_fail_closed(self):
  for change in('none','parent_start','display','argv','socket_inode','lock_pid','listener_fd','foreign_display_parent'):
   with self.subTest(change=change),self.owner_fixture()as(cfg,root):
    if change=='parent_start':cfg['parent']['start_ticks']=11
    elif change=='display':os.environ['DISPLAY']=':154'
    elif change=='argv':(root/'proc/444/cmdline').write_bytes(b'/usr/bin/Xvfb\0:168\0')
    elif change=='socket_inode':cfg['passive']['display_owner']['socket_pin'][1]+=1
    elif change=='lock_pid':(root/'tmp/.X167-lock').write_text('445')
    elif change=='listener_fd':(root/'proc/444/fd/7').unlink()
    elif change=='foreign_display_parent':(root/'proc/444/stat').write_bytes(b'444 (Xvfb) S 777\n')
    if change=='none':self.assertTrue(w.verify_owner(cfg))
    else:
     with self.assertRaises(ValueError):w.verify_owner(cfg)
 def native(self):
  n=w.ResourceNative.__new__(w.ResourceNative);n.t=n.x=Fake();n.errors=[];n.cfg={'passive':{'controller_gc':9,'original_window':10}};return n
 def test_resource_client_lookup_returns_actual_server_base_not_pid_or_xid(self):
  n=self.native();self.assertEqual(n.lookup_resource(1,9,137),0x200000);self.assertEqual(n.lookup_resource(1,10,137),0x400000)
  self.assertEqual(len(n.t.freed),8);self.assertEqual(n.t.destroyed.count('state'),2);self.assertEqual(len([x for x in n.t.destroyed if type(x)is int]),2)
 def test_bad_lookup_state_remains_fail_and_both_state_context_cleanup_run(self):
  n=self.native();n.t.bad=True
  with self.assertRaises(ValueError):n.lookup_resource(1,9,137)
  self.assertIn('state',n.t.destroyed);self.assertEqual(len([x for x in n.t.destroyed if type(x)is int]),1)
 def test_lookup_cleanup_continues_after_state_free_failure(self):
  n=self.native()
  def fail_state(p):raise OSError('state free')
  n.t.XRecordFreeState=fail_state
  with self.assertRaises(OSError):n.lookup_resource(1,9,137)
  self.assertEqual(len([x for x in n.t.destroyed if type(x)is int]),1);self.assertEqual(len(n.t.freed),4)
 def test_actual_allclient_set_excludes_only_data_client_and_requires_both_resources(self):
  n=self.native();n.bindings={'controller_transport':0x200000,'original_window_owner':0x400000};n.initial_clients=None;n.data_client=None;n.context_snapshots=[]
  cfg={'enabled':False,'clients':[2,0x200000,0x400000,0x600000,0x800000]};keep=[]
  def state(d,context,out):
   rows=core.selected_ranges(137);rp=(C.POINTER(m.RecordRange)*4)(*(C.pointer(r)for r in rows));infos=[core.RecordClientInfo(v,4,rp)for v in cfg['clients']];ip=(C.POINTER(core.RecordClientInfo)*len(infos))(*(C.pointer(v)for v in infos));value=core.RecordState(int(cfg['enabled']),7,len(infos),ip);keep.append((rows,rp,infos,ip,value));C.cast(out,C.POINTER(C.POINTER(core.RecordState)))[0]=C.pointer(value);return 1
  n.t.XRecordGetContext=state
  self.assertTrue(n.context_state(1,77,core.selected_ranges(137),enabled=False));cfg['enabled']=True;cfg['clients'].remove(0x800000)
  self.assertTrue(n.context_state(1,77,core.selected_ranges(137),enabled=True));self.assertEqual(n.data_client,0x800000)
  cfg['clients'].append(0xa00000);self.assertTrue(n.context_state(1,77,core.selected_ranges(137),enabled=True))
  cfg['clients'].remove(0x200000)
  with self.assertRaises(ValueError):n.context_state(1,77,core.selected_ranges(137),enabled=True)
  cfg['clients'].append(0x200000);cfg['clients'].append(0x800000)
  with self.assertRaises(ValueError):n.context_state(1,77,core.selected_ranges(137),enabled=True)
 def test_disabled_worker_fails_before_config_read_or_native_call(self):
  with self.assertRaisesRegex(RuntimeError,'disabled'):w.run_worker('/must-not-read',':154')
 def test_failed_open_checks_close_the_new_connection_before_propagating(self):
  n=self.native();n.cfg={'passive':{'display':':154'}};n.connections=[];closed=[]
  n.x.XOpenDisplay=lambda d:17;n.x.XCloseDisplay=closed.append
  n.check=lambda:(_ for _ in()).throw(ValueError('native X error'))
  with patch.object(w,'verify_owner',return_value=True),self.assertRaisesRegex(ValueError,'native X error'):n.open()
  self.assertEqual(closed,[17])
 def test_separate_metadata_method_executes_public_request_counter_and_no_inputs(self):
  class Fn:
   def __init__(self,f):self.f=f
   def __call__(self,*args):return self.f(*args)
  calls=[];opened=[]
  class MethodFake:
   def __init__(self,cfg):
    self.errors=[];self.x=SimpleNamespace(XDefaultRootWindow=lambda d:99,XCreateSimpleWindow=lambda *a:10,XSync=lambda *a:None,
     XDefaultGC=Fn(lambda *a:9),XGContextFromGC=Fn(lambda g:9),XNextRequest=Fn(lambda d:(calls.append('counter'),10+len(calls))[1]),
     XDestroyWindow=lambda *a:calls.append('destroy'),XCloseDisplay=lambda d:calls.append(('close',d)))
   def open(self):opened.append(len(opened)+1);return opened[-1]
   def versions(self,d):return dict(xtest_opcode=137)
   def lookup_resource(self,d,spec,opcode):return 0x200000 if spec==9 else 0x400000
   def check(self):pass
  with patch.object(w,'ResourceNative',MethodFake):answer=w.metadata_probe({})
  self.assertEqual(calls.count('counter'),2);self.assertTrue(answer['normal_closes']);self.assertEqual(answer['status'],'PASS_OWN_XRECORD_METADATA_BINDING_ONLY')
  self.assertEqual(answer['metadata_request_interval'],[11,12]);self.assertEqual(calls[-2:],[('close',2),('close',1)])

if __name__=='__main__':unittest.main()
