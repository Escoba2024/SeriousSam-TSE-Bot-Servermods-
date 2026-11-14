"""Offline driver policy only, with ABI-shaped fake objects; no Xlib."""
from types import SimpleNamespace
import ctypes as C
import xrecord_core_method as m
import unittest
from unittest.mock import patch
import xrecord_core_worker as w

class Fake:
 def __init__(self):self.calls=[];self.x=self;self.t=self;self.position=[400,300]
 def open(self):self.calls.append('open');return 1
 def check(self):pass
 def XDefaultRootWindow(self,d):return 99
 def XCreateSimpleWindow(self,*args):self.calls.append(('create',args));return 123
 def XSelectInput(self,*args):self.calls.append(('select',args))
 def XMapWindow(self,*args):self.calls.append('map')
 def XSync(self,*args):pass
 def XWarpPointer(self,*args):self.calls.append(('warp',args[-2:]));self.position=list(args[-2:])
 def XTestFakeRelativeMotionEvent(self,d,x,y,t):self.calls.append(('relative',x,y));self.position=[self.position[0]+x,self.position[1]+y];return 1
 def query(self,d,window):self.calls.append('query');return dict(position=list(self.position),window=window,root=99,sequence=len(self.calls))
 def XDestroyWindow(self,*args):self.calls.append('destroy')
 def XCloseDisplay(self,*args):self.calls.append('close')

class RecordFake:
 def __init__(self,fail_alloc=None):self.x=self;self.t=self;self.allocated=[];self.freed=[];self.callback=None;self.fail_alloc=fail_alloc;self.allocate_calls=0
 def open(self):return 1
 def check(self):pass
 def versions(self,d):return dict(record_version=[1,13],xtest_version=[2,2],xtest_opcode=137)
 def XRecordAllocRange(self):
  self.allocate_calls+=1
  if self.allocate_calls==self.fail_alloc:return None
  row=m.RecordRange();self.allocated.append(row);return C.pointer(row)
 def XFree(self,p):self.freed.append(C.addressof(p.contents));return 0
 def XRecordCreateContext(self,d,flags,clients,count,pointers,nranges):
  if flags!=7 or count!=1 or clients[0]!=3 or nranges!=4:raise ValueError('wrong create arguments')
  return 42
 def XSync(self,*args):return 0
 def context_state(self,*args,**kwargs):return True
 def emit(self,category):v=m.Intercept();v.category=category;self.callback(None,C.pointer(v))
 def XRecordEnableContextAsync(self,d,context,callback,closure):self.callback=callback;self.emit(4);return 1
 def XRecordFreeData(self,p):pass
 def XRecordDisableContext(self,*args):self.emit(5);return 1
 def XRecordFreeContext(self,*args):return 1
 def XCloseDisplay(self,*args):return 0


class WorkerTests(unittest.TestCase):
 def test_recorder_uses_library_allocated_ranges_and_frees_all_on_success(self):
  import tempfile
  with tempfile.TemporaryDirectory()as d:
   fake=RecordFake();recorder=w.Recorder(fake,d);arm=recorder.arm()
   self.assertEqual(fake.allocate_calls,4);self.assertEqual(len(fake.freed),4);self.assertEqual(arm['start_count'],1)
   result=recorder.close();self.assertTrue(result['context_freed']);self.assertTrue(result['connections_closed']);self.assertTrue(result['end_verified'])
 def test_partial_range_allocation_failure_frees_prior_allocation(self):
  import tempfile
  with tempfile.TemporaryDirectory()as d:
   fake=RecordFake(fail_alloc=2);recorder=w.Recorder(fake,d)
   with self.assertRaises(ValueError):recorder.arm()
   self.assertEqual(len(fake.freed),1);self.assertTrue(recorder.close()['connections_closed'])
 def test_worker_gate_fails_without_native_or_path_access(self):
  with patch.object(w,'Native',side_effect=AssertionError('native')),self.assertRaisesRegex(RuntimeError,'disabled'):w.run_worker('driver','/must-not-read',':167')
 def test_driver_initializes_before_arm_and_runs_exact_once_fixed_actions(self):
  fake=Fake();driver=w.Driver(fake);init=driver.initialize()
  self.assertEqual(init['position'],[400,300]);self.assertEqual(init['window'],123)
  self.assertEqual(driver.relative()['position'],[412,300]);self.assertEqual(driver.warp()['position'],[400,300])
  with self.assertRaises(ValueError):driver.relative()
  with self.assertRaises(ValueError):driver.warp()
  result=driver.close();self.assertTrue(result['connections_closed']);self.assertTrue(result['window_destroyed'])
  self.assertEqual([x for x in fake.calls if isinstance(x,tuple)and x[0]=='relative'],[('relative',12,0)])
  self.assertEqual([x for x in fake.calls if isinstance(x,tuple)and x[0]=='warp'],[('warp',(400,300)),('warp',(400,300))])
 def test_driver_wrong_actual_position_fails_without_retry(self):
  fake=Fake();driver=w.Driver(fake);driver.initialize();fake.query=lambda d,win:dict(position=[400,300],window=win,root=99,sequence=1)
  with self.assertRaises(ValueError):driver.relative()
  with self.assertRaises(ValueError):driver.relative()
  self.assertEqual(len([x for x in fake.calls if isinstance(x,tuple)and x[0]=='relative']),1);driver.close()
 def test_warp_cannot_precede_relative_or_initialization(self):
  fake=Fake();driver=w.Driver(fake)
  with self.assertRaises(ValueError):driver.warp()
  with self.assertRaises(ValueError):driver.relative()
  driver.initialize()
  with self.assertRaises(ValueError):driver.warp()
  driver.close()

if __name__=='__main__':unittest.main()
