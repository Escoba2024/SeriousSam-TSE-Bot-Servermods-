"""Only pure/Fake-C transport tests; no Xlib or display."""
import unittest
from types import SimpleNamespace
from pathlib import Path
import tempfile
from unittest.mock import patch
import a1_passive_xrecord as a

class Fn:
 def __init__(self,call):self.call=call
 def __call__(self,*args):return self.call(*args)

class Tests(unittest.TestCase):
 def test_disabled_start_fails_before_any_path_getter_or_spawn(self):
  with self.assertRaisesRegex(RuntimeError,'disabled'):a.PassiveRecorder.start(None,None,None,None)
 def test_proxy_calls_actual_function_once_with_exact_arguments_and_result(self):
  called=[];events=[];seq=[10]
  def fn(*args):called.append(args);seq[0]+=2;return 7
  x=SimpleNamespace(XNextRequest=Fn(lambda d:seq[0]));t=SimpleNamespace(XTestFakeRelativeMotionEvent=Fn(fn));transport=SimpleNamespace(x=x,t=t,d=123,pin=SimpleNamespace(display=':154',role='vanilla'))
  proxy=a.instrument_transport(transport);proxy.observer=a.PassiveRecorder(None,None,transport);events=proxy.observer.emissions
  self.assertEqual(transport.t.XTestFakeRelativeMotionEvent(123,12,0,0),7);self.assertEqual(called,[(123,12,0,0)])
  self.assertEqual(len(events),1);self.assertEqual(events[0]['sequence_interval'],[10,12]);self.assertEqual(events[0]['arguments'],[123,12,0,0]);self.assertEqual(events[0]['return_value'],7)
 def test_proxy_preserves_native_exception_and_does_not_retry(self):
  count=[0];events=[]
  def fn(*args):count[0]+=1;raise OSError('exact original')
  transport=SimpleNamespace(x=SimpleNamespace(XNextRequest=Fn(lambda d:10)),t=SimpleNamespace(XTestFakeKeyEvent=Fn(fn)),d=123,pin=SimpleNamespace(display=':154',role='vanilla'))
  proxy=a.instrument_transport(transport);proxy.observer=a.PassiveRecorder(None,None,transport);events=proxy.observer.emissions
  with self.assertRaisesRegex(OSError,'exact original'):transport.t.XTestFakeKeyEvent(123,25,1,0)
  self.assertEqual(count[0],1);self.assertEqual(len(events),1);self.assertIn('exact original',events[0]['error'])
 def test_public_gc_getters_read_existing_resource_without_pointer_query(self):
  called=[]
  x=SimpleNamespace(XNextRequest=Fn(lambda d:10),XDefaultGC=Fn(lambda d,s:(called.append(('GC',d,s)),456)[1]),XGContextFromGC=Fn(lambda gc:(called.append(('XID',gc)),789)[1]))
  self.assertEqual(a.controller_gc(SimpleNamespace(x=x,d=123)),789);self.assertEqual(called,[('GC',123,0),('XID',456)]);self.assertEqual(x.XNextRequest.restype.__name__,'c_ulong');self.assertEqual(x.XNextRequest.argtypes[0].__name__,'c_void_p')
 def test_without_observer_every_function_is_a_plain_passthrough(self):
  t=SimpleNamespace(XTestFakeKeyEvent=Fn(lambda *args:5));transport=SimpleNamespace(t=t,d=123)
  a.instrument_transport(transport);self.assertEqual(transport.t.XTestFakeKeyEvent(123,25,0,0),5)
 def test_armed_proxy_rejects_fire_before_any_native_call(self):
  called=[];transport=SimpleNamespace(t=SimpleNamespace(XTestFakeButtonEvent=Fn(lambda *args:called.append(args))),d=123)
  proxy=a.instrument_transport(transport);proxy.observer=SimpleNamespace(record_emission=lambda row:None)
  with self.assertRaisesRegex(RuntimeError,'no-fire'):transport.t.XTestFakeButtonEvent(123,1,1,0)
  self.assertEqual(called,[])
 def test_private_journal_failure_does_not_skip_owned_child_cleanup(self):
  with tempfile.TemporaryDirectory()as d:
   called=[];kid=SimpleNamespace(cleanup=lambda **kw:(called.append(kw),dict(errors=[],closed=True,reaped=True,forced=False,exit_code=0))[1])
   proxy=SimpleNamespace(observer='active');obj=a.PassiveRecorder(kid,Path(d),SimpleNamespace(_passive_xrecord_proxy=proxy))
   with patch.object(a,'private_json',side_effect=OSError('full')):receipt=obj.close([])
   self.assertEqual(called,[dict(stop_timeout=3)]);self.assertIsNone(proxy.observer);self.assertTrue(receipt['errors']);self.assertEqual(receipt['status'],'FAIL_PASSIVE_XRECORD_DIAGNOSTIC')
   self.assertEqual(obj.close([]),receipt);self.assertEqual(len(called),1)
 def test_arm_failure_is_sticky_and_does_not_attach_input_observer(self):
  kid=SimpleNamespace(call=lambda *a,**kw:dict(value=dict(start_count=0)));proxy=SimpleNamespace(observer=None)
  obj=a.PassiveRecorder(kid,None,SimpleNamespace(_passive_xrecord_proxy=proxy))
  with self.assertRaises(ValueError):obj.arm()
  self.assertTrue(obj.failed);self.assertIsNone(proxy.observer)
  with self.assertRaises(RuntimeError):obj.before_input()
 def test_method_fingerprint_attestation_is_required_not_assumed(self):
  with self.assertRaisesRegex(RuntimeError,'method'):a.require_method_qualification(dict(binding_qualification=None,method_fingerprints={'a':'b'}))
  with self.assertRaises(ValueError):a.require_method_qualification(dict(binding_qualification=dict(status='PASS_OWN_XRECORD_METADATA_BINDING_ONLY',fingerprints={'a':'changed'}),method_fingerprints={'a':'b'}))

if __name__=='__main__':unittest.main()
