"""Real proxy/recorder with fake C calls; no child, display or Xlib loaded."""
import json
from pathlib import Path
import tempfile
from types import SimpleNamespace
import unittest
from unittest.mock import patch
import a1_passive_xrecord as a


def recorder(directory, counters=(10,16), *, native_error=None):
 values=iter(counters);calls=[]
 def native(*args):
  calls.append(args)
  if native_error is not None:raise native_error
  return 7
 transport=SimpleNamespace(d=123,x=SimpleNamespace(XNextRequest=lambda d:next(values)),
  t=SimpleNamespace(XTestFakeRelativeMotionEvent=native))
 proxy=a.instrument_transport(transport)
 child=SimpleNamespace(cleanup=lambda **kw:dict(errors=[],closed=True,reaped=True,forced=False,exit_code=0))
 obj=a.PassiveRecorder(child,Path(directory),transport);proxy.observer=obj
 return obj,transport,calls


class Attempts(unittest.TestCase):
 def test_real_forward_down_guard_reject_still_executes_inherited_finally_keyup_once(self):
  import ast
  import math
  # Execute the unchanged inherited action_step and Endpoint/transport event
  # methods, replacing only process/display checks and the C XTEST boundary.
  source=Path('/srv/tse-a1-passive-xrecord-root-frozen-20261114/run_dual.py').read_text()
  function=next(n for n in ast.parse(source).body if isinstance(n,ast.FunctionDef)and n.name=='action_step')
  namespace=dict(math=math,P=SimpleNamespace(CONTROLS={'forward'}),PP=SimpleNamespace(RouteFlightBeforeInput=type('RouteFlightBeforeInput',(Exception,),{})))
  exec(compile(ast.Module(body=[function],type_ignores=[]),'<unchanged-action-step>','exec'),namespace)
  endpoint_source=Path('/srv/tse-a1-passive-xrecord-root-frozen-20261114/x11_endpoint.py').read_text()
  classes=[n for n in ast.parse(endpoint_source).body if isinstance(n,ast.ClassDef)and n.name in('Endpoint','X11Transport')]
  endpoint_namespace=dict(CONTROLS={'forward'})
  exec(compile(ast.Module(body=classes,type_ignores=[]),'<unchanged-endpoint>','exec'),endpoint_namespace)
  with tempfile.TemporaryDirectory()as d:
   calls=[];held=[False];counters=iter([10,16,16,17])
   def native(*args):calls.append(args);held[0]=bool(args[2]);return 7
   pin=SimpleNamespace(role='vanilla',window=7)
   transport_type=endpoint_namespace['X11Transport'];t=transport_type.__new__(transport_type)
   t.d=123;t.pin=pin;t.guard=lambda:None;t.keys={'forward':25}
   t.x=SimpleNamespace(XNextRequest=lambda display:next(counters),XSync=lambda *args:None)
   t.t=SimpleNamespace(XTestFakeKeyEvent=native);t.focused=lambda:7;t.held=lambda control:held[0]
   proxy=a.instrument_transport(t);obj=a.PassiveRecorder(None,Path(d),t);proxy.observer=obj
   endpoint=endpoint_namespace['Endpoint'](pin,t,lambda:None,lambda:None);timing={}
   with self.assertRaisesRegex(RuntimeError,'actual emission counter/clock interval invalid'):
    namespace['action_step']({'vanilla':endpoint},dict(actions={'vanilla':'forward'},seconds=.1),lambda:1.,lambda seconds:None,lambda:None,timing=timing)
   self.assertEqual(calls,[(123,25,1,0),(123,25,0,0)])
   self.assertFalse(held[0]);self.assertTrue(obj.failed);self.assertEqual(timing['status'],'FAIL')
   self.assertEqual(len(obj.attempts),2);self.assertEqual([r['validation_status']for r in obj.attempts],['REJECTED','REJECTED'])
   self.assertEqual(obj.emissions,[])
   with self.assertRaisesRegex(RuntimeError,'sticky failure'):obj.before_input()

 def test_rejected_six_request_interval_is_retained_and_cleanup_persists_it(self):
  with tempfile.TemporaryDirectory()as d:
   obj,t,calls=recorder(d)
   with patch.object(a.time,'monotonic',side_effect=[1.,2.]),self.assertRaisesRegex(ValueError,'actual emission counter/clock interval invalid'):
    t.t.XTestFakeRelativeMotionEvent(123,12,0,0)
   self.assertEqual(calls,[(123,12,0,0)]);self.assertEqual(obj.emissions,[])
   self.assertEqual(len(getattr(obj,'attempts',[])),1)
   row=obj.attempts[0];self.assertTrue(row['native_invoked']);self.assertEqual(row['validation_status'],'REJECTED')
   self.assertEqual(row['metadata']['sequence_interval'],[10,16]);self.assertEqual(row['metadata']['return_value'],7)
   self.assertEqual((row['metadata']['started_monotonic'],row['metadata']['finished_monotonic']),(1.,2.))
   result=obj.close([]);self.assertEqual(result['status'],'FAIL_PASSIVE_XRECORD_DIAGNOSTIC')
   p=Path(d)/'controller-emission-attempts.json';self.assertEqual(json.loads(p.read_text()),obj.attempts);self.assertEqual(p.stat().st_mode&0o777,0o600)
   self.assertEqual(json.loads((Path(d)/'controller-emissions.json').read_text()),[])

 def test_first_counter_error_reserves_not_invoked_and_adds_no_after_counter_or_clock(self):
  with tempfile.TemporaryDirectory()as d:
   obj,t,calls=recorder(d,counters=())
   with patch.object(a.time,'monotonic',side_effect=[1.]),self.assertRaises(StopIteration):t.t.XTestFakeRelativeMotionEvent(123,12,0,0)
   self.assertEqual(calls,[]);self.assertEqual(len(getattr(obj,'attempts',[])),1)
   row=obj.attempts[0];self.assertFalse(row['native_invoked']);self.assertEqual(row['validation_status'],'REJECTED')
   self.assertEqual(row['failure_stage'],'first_counter');self.assertNotIn('sequence_before',row);self.assertNotIn('finished_monotonic',row['metadata'])

 def test_after_counter_error_retains_native_return_and_first_counter(self):
  with tempfile.TemporaryDirectory()as d:
   obj,t,calls=recorder(d,counters=(10,))
   with patch.object(a.time,'monotonic',side_effect=[1.]),self.assertRaises(StopIteration):t.t.XTestFakeRelativeMotionEvent(123,12,0,0)
   self.assertEqual(calls,[(123,12,0,0)]);self.assertEqual(len(getattr(obj,'attempts',[])),1)
   row=obj.attempts[0];self.assertEqual(row['failure_stage'],'after_counter');self.assertEqual(row['sequence_before'],10)
   self.assertTrue(row['native_invoked']);self.assertEqual(row['metadata']['return_value'],7);self.assertNotIn('sequence_after',row)

 def test_valid_record_remains_exact_old_shape_and_attempt_is_separate(self):
  with tempfile.TemporaryDirectory()as d:
   obj,t,calls=recorder(d,counters=(10,11))
   with patch.object(a.time,'monotonic',side_effect=[1.,2.]),patch.object(a.time,'time',return_value=3.):self.assertEqual(t.t.XTestFakeRelativeMotionEvent(123,12,0,0),7)
   expected=dict(function='XTestFakeRelativeMotionEvent',arguments=[123,12,0,0],started_monotonic=1.,host_epoch_ms=3000.,return_value=7,sequence_interval=[10,11],finished_monotonic=2.,index=0)
   self.assertEqual(obj.emissions,[expected]);self.assertEqual(len(getattr(obj,'attempts',[])),1)
   self.assertEqual(obj.attempts[0]['validation_status'],'ACCEPTED');self.assertTrue(obj.attempts[0]['native_invoked'])

 def test_clock_reversal_is_still_rejected_and_actual_values_remain(self):
  with tempfile.TemporaryDirectory()as d:
   obj,t,calls=recorder(d,counters=(10,11))
   with patch.object(a.time,'monotonic',side_effect=[2.,1.]),self.assertRaisesRegex(ValueError,'counter/clock'):t.t.XTestFakeRelativeMotionEvent(123,12,0,0)
   self.assertEqual(len(getattr(obj,'attempts',[])),1);self.assertEqual(obj.attempts[0]['metadata']['finished_monotonic'],1.)
   self.assertEqual(obj.emissions,[])

 def test_native_exception_remains_primary_when_after_counter_also_fails(self):
  with tempfile.TemporaryDirectory()as d:
   error=OSError('original native failure');obj,t,calls=recorder(d,counters=(10,),native_error=error)
   with patch.object(a.time,'monotonic',side_effect=[1.]),self.assertRaises(OSError)as caught:t.t.XTestFakeRelativeMotionEvent(123,12,0,0)
   self.assertIs(caught.exception,error);self.assertEqual(len(getattr(obj,'attempts',[])),1)
   self.assertIn('original native failure',obj.attempts[0]['metadata']['error']);self.assertEqual(obj.attempts[0]['failure_stage'],'after_counter')

 def test_attempt97_is_blocked_before_counter_and_native_not_silently_executed(self):
  with tempfile.TemporaryDirectory()as d:
   obj,t,calls=recorder(d,counters=tuple(range(1,195)))
   for _ in range(96):self.assertEqual(t.t.XTestFakeRelativeMotionEvent(123,12,0,0),7)
   with self.assertRaises(RuntimeError):t.t.XTestFakeRelativeMotionEvent(123,12,0,0)
   self.assertEqual(len(calls),96);self.assertEqual(len(getattr(obj,'attempts',[])),96);self.assertEqual(len(obj.emissions),96)

 def test_attempt_journal_io_failure_does_not_skip_valid_journal_or_child_cleanup(self):
  with tempfile.TemporaryDirectory()as d:
   obj,t,calls=recorder(d,counters=(10,11));self.assertEqual(t.t.XTestFakeRelativeMotionEvent(123,12,0,0),7)
   writes=[];cleaned=[];obj.kid.cleanup=lambda **kw:(cleaned.append(kw),dict(errors=[],closed=True,reaped=True,forced=False,exit_code=0))[1]
   real=a.private_json
   def write(path,value):
    writes.append(path.name)
    if path.name=='controller-emission-attempts.json':raise OSError('attempt journal full')
    return real(path,value)
   with patch.object(a,'private_json',side_effect=write):result=obj.close([])
   self.assertEqual(writes,['controller-emissions.json','controller-emission-attempts.json']);self.assertEqual(len(cleaned),1)
   self.assertTrue(any('attempt journal full'in e for e in result['errors']));self.assertEqual(len(json.loads((Path(d)/'controller-emissions.json').read_text())),1)

 def test_original_journal_failure_still_writes_attempts_and_cleanup_is_idempotent(self):
  with tempfile.TemporaryDirectory()as d:
   obj,t,calls=recorder(d,counters=(10,11));t.t.XTestFakeRelativeMotionEvent(123,12,0,0)
   real=a.private_json
   def write(path,value):
    if path.name=='controller-emissions.json':raise OSError('original journal full')
    return real(path,value)
   with patch.object(a,'private_json',side_effect=write):result=obj.close([])
   self.assertTrue(any('original journal full'in e for e in result['errors']))
   self.assertEqual(json.loads((Path(d)/'controller-emission-attempts.json').read_text()),obj.attempts);self.assertIs(obj.close([]),result)

 def test_native_exception_remains_primary_when_validation_metadata_fails(self):
  with tempfile.TemporaryDirectory()as d:
   error=OSError('original native failure');obj,t,calls=recorder(d,counters=(10,10),native_error=error)
   obj.record_emission=lambda row:(_ for _ in()).throw(ValueError('metadata sink failed'))
   with self.assertRaises(OSError)as caught:t.t.XTestFakeRelativeMotionEvent(123,12,0,0)
   self.assertIs(caught.exception,error);self.assertEqual(obj.attempts[0]['failure_stage'],'validation')
   self.assertEqual(obj.attempts[0]['validation_error'],"ValueError('metadata sink failed')");self.assertTrue(obj.failed)

 def test_exact_four_request_boundary_and_other_counter_rejects_remain(self):
  for counters,valid in [((10,14),True),((10,15),False),((10,10),False),((10,9),False),((0,1),False),((10,2**32),False)]:
   with self.subTest(counters=counters),tempfile.TemporaryDirectory()as d:
    obj,t,calls=recorder(d,counters=counters)
    if valid:self.assertEqual(t.t.XTestFakeRelativeMotionEvent(123,12,0,0),7)
    else:
     with self.assertRaisesRegex(ValueError,'counter/clock'):t.t.XTestFakeRelativeMotionEvent(123,12,0,0)
    self.assertEqual(obj.attempts[0]['metadata']['sequence_interval'],list(counters));self.assertEqual(len(obj.emissions),int(valid))


class Package(unittest.TestCase):
 def builder(self):
  import importlib.util
  self.assertIsNotNone(importlib.util.find_spec('prepare_a1_passive_attempt_journal'),'missing disabled attempt-journal builder')
  import prepare_a1_passive_attempt_journal
  return prepare_a1_passive_attempt_journal

 def test_disabled_fork_pins_all_files_keeps_real_method_and_other_contracts(self):
  import hashlib
  b=self.builder()
  with tempfile.TemporaryDirectory()as d:
   dest=Path(d)/'disabled';receipt=b.prepare(dest);m=json.loads((dest/'source-manifest.json').read_text())
   self.assertFalse(m['runtime_reviewed']);self.assertFalse(receipt['native_performed'])
   for name in('run_dual.py','a1_input_worker.py','a1_passive_xrecord.py','a1_passive_xrecord_worker.py','collector/a1_original_input_collector.py'):
    text=(dest/name).read_text();self.assertTrue('RUNTIME_REVIEWED=False'in text or'RUNTIME_REVIEWED = False'in text)
   old=json.loads((b.PARENT/'source-manifest.json').read_text())
   self.assertEqual(m['passive_xrecord'],old['passive_xrecord'])
   for name in('colt_preparation.py','rotation_diagnostics.py','a1_trace_scope.py','x11_endpoint.py','transaction.py','host_budget.py','a1_passive_xrecord_evidence.py'):
    self.assertEqual((dest/name).read_bytes(),(b.PARENT/name).read_bytes())
   for name in b.CORE_FILES:self.assertEqual((dest/'passive-core'/name).read_bytes(),(b.PARENT/'passive-core'/name).read_bytes())
   for path,h in m['runtime_dependencies'].items():self.assertEqual(hashlib.sha256(Path(path).read_bytes()).hexdigest(),h)
   self.assertEqual(a.method_fingerprints(dest),old['passive_xrecord']['method_fingerprints'])
   with self.assertRaises(ValueError):b.prepare(dest)

 def test_method_fingerprint_change_cannot_inherit_actual_qualification(self):
  b=self.builder()
  with tempfile.TemporaryDirectory()as d,patch.object(b,'method_fingerprints',return_value={'changed':'unqualified'}):
   with self.assertRaisesRegex(ValueError,'method fingerprint'):b.prepare(Path(d)/'disabled')


if __name__=='__main__':unittest.main()
