"""Fake-C and range/cleanup models only; no display/native library calls."""
import ast
import ctypes as C
import importlib
from pathlib import Path
from types import SimpleNamespace
import unittest


class Worker(unittest.TestCase):
 def module(self):return importlib.import_module('a1_xres_attribution_worker')
 def test_manifest_scope_cannot_turn_a1_fork_into_own_method_or_reverse(self):
  m=self.module()
  for allowed,mode,display in(('A1_154','method',':167'),('OWN_METHOD_167','a1',':154'),('A1_154','a1',':167'),('OWN_METHOD_167','method',':154')):
   with self.subTest(allowed=allowed,mode=mode,display=display),self.assertRaises(ValueError):m.require_scope({'xres_attribution':{'allowed_scope':allowed}},{'passive':{'mode':mode,'display':display}},display)
  m.require_scope({'xres_attribution':{'allowed_scope':'A1_154'}},{'passive':{'mode':'a1','display':':154'}},':154')
  m.require_scope({'xres_attribution':{'allowed_scope':'OWN_METHOD_167'}},{'passive':{'mode':'method','display':':167'}},':167')
 def test_lifecycle_factory_changes_only_two_flags_and_never_core_globals(self):
  m=self.module();import xrecord_core_native as core
  before=[core.range_signature(r)for r in core.selected_ranges(137)]
  new=m.lifecycle_ranges(137)
  self.assertEqual(len(new),4)
  coverage=core.range_coverage(new);old=core.range_coverage(core.selected_ranges(137))
  self.assertTrue(coverage.pop('client_started'));self.assertTrue(coverage.pop('client_died'))
  old.pop('client_started');old.pop('client_died');self.assertEqual(coverage,old)
  self.assertEqual(before,[core.range_signature(r)for r in core.selected_ranges(137)])
  tree=ast.parse(Path(m.__file__).read_text())
  for node in ast.walk(tree):
   if isinstance(node,(ast.Assign,ast.AugAssign,ast.AnnAssign)):
    targets=node.targets if isinstance(node,ast.Assign)else[node.target]
    self.assertFalse(any(isinstance(t,ast.Attribute)and isinstance(t.value,ast.Name)and t.value.id in('core','core_native','core_worker')for t in targets))
 def fake(self,*,count=5,invalid_length=False):
  m=self.module();from xres_pid_worker import Client,Value,Spec
  p=m.PublicPID.__new__(m.PublicPID);p.errors=[];p.total_free_counts={};calls=[];keep=[]
  array=(Client*max(5,count))(*[Client(b,0x1fffff)for b in(0,0x200000,0x400000,0x600000,0x800000)])
  def clients(d,num,out):num._obj.value=count;C.cast(out,C.POINTER(C.POINTER(Client)))[0]=C.cast(array,C.POINTER(Client));return 1
  def ids(d,n,spec,num,out):
   base=spec._obj.client&~0x1fffff;v=C.c_uint32(100 if base==0x200000 else 103);row=(Value*1)();row[0].spec=Spec(base,2);row[0].length=8 if invalid_length else 4;row[0].value=C.cast(C.pointer(v),C.c_void_p);keep.extend((v,row));num._obj.value=1;C.cast(out,C.POINTER(C.POINTER(Value)))[0]=C.cast(row,C.POINTER(Value));calls.append(('id',int(spec._obj.client)));return 0
  p.x=SimpleNamespace(XFree=lambda ptr:calls.append('free_clients'))
  p.r=SimpleNamespace(XResQueryClients=clients,XResQueryClientIds=ids,XResClientIdsDestroy=lambda n,ptr:calls.append('free_ids'),XResGetClientPid=lambda ptr:C.cast(ptr.contents.value,C.POINTER(C.c_uint32)).contents.value)
  return p,calls
 def test_exact_bounded_all_positive_context_bases_and_two_existing_resources(self):
  p,calls=self.fake();r=p.query(99,[2,0x600000,0x200000,0x400000],{'controller_transport':0x200001,'original_window_owner':0x400001})
  self.assertEqual([x['requested_xid']for x in r['queries']],[0x200000,0x400000,0x600000,0x200001,0x400001])
  self.assertEqual(calls.count('free_clients'),1);self.assertEqual(calls.count('free_ids'),5)
  self.assertEqual(r['free_counts'],dict(client_arrays_allocated=1,client_arrays_freed=1,id_arrays_allocated=5,id_arrays_freed=5))
 def test_invalid_count_payload_or_targets_free_without_retry_or_wildcard(self):
  for kw in(dict(count=65),dict(invalid_length=True)):
   p,calls=self.fake(**kw)
   with self.assertRaises(ValueError):p.query(99,[2,0x200000,0x400000],{'controller_transport':0x200001,'original_window_owner':0x400001})
   self.assertEqual(calls.count('free_clients'),1)
   if kw.get('invalid_length'):self.assertEqual(calls.count('free_ids'),1)
  p,calls=self.fake()
  with self.assertRaises(ValueError):p.query(99,[2]+[i*0x200000 for i in range(1,34)],{'controller_transport':0x200001,'original_window_owner':0x400001})
  self.assertEqual(calls,[])
 def test_disabled_worker_entry_precedes_config_or_native(self):
  with self.assertRaisesRegex(RuntimeError,'disabled'):self.module().run_worker('/never-read',':154')


if __name__=='__main__':unittest.main()


class RecorderLifecycle(unittest.TestCase):
 def test_first_snapshot_only_after_real_start_and_final_before_disable_even_on_error(self):
  import tempfile
  from unittest.mock import patch
  from test_a1_xres_attribution_evidence import fixture
  import xrecord_core_method as core_method
  m=importlib.import_module('a1_xres_attribution_worker');events=[];rows,s,expected,native=fixture()
  class FakeNative:
   def __init__(self):
    self.errors=[];self.bindings=s[0]['bindings'];self.context_snapshots=[];self.count=0;self.callback=None
    self.x=SimpleNamespace(XSync=lambda *args:1,XFree=lambda p:None,XCloseDisplay=lambda d:events.append('connection_close'),XConnectionNumber=lambda d:7)
    self.t=SimpleNamespace(XRecordAllocRange=lambda:C.pointer(core_method.RecordRange()),XRecordCreateContext=lambda *args:99,XRecordFreeData=lambda p:None,XRecordFreeContext=lambda *args:1,XRecordEnableContextAsync=self.enable,XRecordDisableContext=self.disable)
   def open(self):self.count+=1;return self.count
   def versions(self,d):return dict(record_version=[1,13],xtest_version=[2,2],xtest_opcode=137)
   def check(self):pass
   def context_state(self,d,context,ranges,*,enabled):
    import xrecord_core_native as core
    self.assert_coverage=core.range_coverage(ranges);self.context_snapshots.append(dict(enabled=enabled,clients=s[0]['context_clients']));return True
   def emit(self,category):
    value=core_method.Intercept();value.category=category;value.server_time=100;self.callback(None,C.pointer(value));events.append('start'if category==4 else'end')
   def enable(self,d,ctx,cb,closure):self.callback=cb;self.emit(4);return 1
   def disable(self,d,ctx):events.append('disable');self.emit(5);return 1
  class FakePID:
   def __init__(self,*args):self.total_free_counts={}
   def versions(self,d):return[1,2]
   def query(self,*args):
    events.append('snapshot');return {k:copy[k]for k in('query_clients_status','clients','queries','free_counts','errors')}
  copy=s[0]
  cfg=dict(passive=dict(mode='a1',display=':154',controller_gc=expected['resources']['controller_transport'],original_window=expected['resources']['original_window_owner']))
  with tempfile.TemporaryDirectory()as directory,patch.object(m,'PublicPID',FakePID),patch.object(m,'read_processes',return_value=expected['identities']):
   obj=m.LifecycleRecorder(FakeNative(),Path(directory),cfg,{})
   arm=obj.arm();self.assertEqual(events[:2],['start','snapshot']);self.assertEqual(len(obj.snapshots),1)
   final=obj.close();self.assertEqual(events[:5],['start','snapshot','snapshot','disable','end']);self.assertEqual(len(obj.snapshots),2);self.assertTrue(final['lifecycle_verified']);self.assertTrue(final['end_verified'])
   self.assertIs(final,obj.close());self.assertEqual(events.count('snapshot'),2)
 def test_method_only_final_capture_cannot_be_used_by_a1_or_make_third_snapshot(self):
  m=importlib.import_module('a1_xres_attribution_worker');obj=m.LifecycleRecorder.__new__(m.LifecycleRecorder);obj.cfg={'passive':{'mode':'a1','display':':154'}}
  with self.assertRaises(ValueError):obj.capture_final()
  obj.cfg={'passive':{'mode':'method','display':':167'}};obj.snapshots=[{},{}]
  with self.assertRaises(ValueError):obj.capture_final()


class StopFailure(unittest.TestCase):
 def test_metadata_error_preserves_normal_core_disable_drain_and_connection_cleanup(self):
  from unittest.mock import patch
  m=importlib.import_module('a1_xres_attribution_worker');obj=m.LifecycleRecorder.__new__(m.LifecycleRecorder)
  obj.closed=False;obj.armed=True;obj.snapshots=[{}];obj.metadata_attempts=[{}];obj.metadata_errors=[];obj.lifecycle_verified=True;obj.pid=SimpleNamespace(total_free_counts={})
  def reject():obj.metadata_errors.append('actual second metadata failure');raise ValueError('metadata')
  obj._capture=reject;calls=[]
  def core_close(self):calls.append('core_disable_end_close');self.closed=True;self.final={'cleanup_errors':[],'end_verified':True};return self.final
  with patch.object(m.Recorder,'close',core_close):r=obj.close()
  self.assertEqual(calls,['core_disable_end_close']);self.assertTrue(r['end_verified']);self.assertIn('xres:actual second metadata failure',r['cleanup_errors']);self.assertIs(r,obj.close())
