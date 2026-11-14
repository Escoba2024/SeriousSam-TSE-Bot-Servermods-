"""Real adapter, fake C functions only; never load Xlib or open a display."""
import json
from pathlib import Path
import tempfile
from types import SimpleNamespace
import unittest
from unittest.mock import patch
import a1_passive_xrecord as a


class Fn:
 def __init__(self,fn):self.fn=fn
 def __call__(self,*args):return self.fn(*args)


def setup(version=(2,2),result=1,sync=1):
 calls=[]
 def query(d,event,error,major,minor):
  calls.append(('query',d));event._obj.value=0;error._obj.value=0;major._obj.value,minor._obj.value=version;return result
 def synchronize(d,discard):calls.append(('sync',d,discard));return sync
 t=SimpleNamespace(d=123,pin=SimpleNamespace(role='vanilla',display=':154'),guard=lambda:calls.append(('guard',)),keys={'forward':25},
  x=SimpleNamespace(XSync=Fn(synchronize)),t=SimpleNamespace(XTestQueryExtension=Fn(query)))
 proxy=a.instrument_transport(t)
 kid=SimpleNamespace(call=lambda command,**kw:(calls.append(('arm',command,kw)),dict(value=dict(start_count=1)))[1])
 obj=a.PassiveRecorder(kid,None,t)
 return calls,t,proxy,obj


class Preparation(unittest.TestCase):
 def test_public_metadata_on_same_transport_sync_precedes_arm_and_observer(self):
  calls,t,proxy,obj=setup();original=obj.kid.call
  def arm(*args,**kw):
   self.assertIsNone(proxy.observer)
   return original(*args,**kw)
  obj.kid.call=arm;receipt=obj.arm()
  self.assertEqual([r for r in calls if r[0]!='guard'],[('query',123),('sync',123,0),('arm','arm',{'timeout':3})])
  self.assertIs(proxy.observer,obj);self.assertFalse(obj.failed)
  self.assertEqual(receipt['transport_preparation'],dict(function='XTestQueryExtension',version=[2,2],return_value=1,event_base=0,error_base=0,synchronized=True,no_inputs=True))
  self.assertEqual(t.t.XTestQueryExtension.argtypes[0].__name__,'c_void_p')
  self.assertEqual(t.t.XTestQueryExtension.restype.__name__,'c_int')
 def test_invalid_return_version_or_sync_stickily_prevents_arm_and_inputs(self):
  for changes in(dict(result=0),dict(version=(1,0)),dict(version=(2,1)),dict(sync=0)):
   with self.subTest(changes=changes):
    calls,t,proxy,obj=setup(**changes)
    with self.assertRaises(ValueError):obj.arm()
    self.assertFalse(any(r[0]=='arm'for r in calls));self.assertIsNone(proxy.observer);self.assertTrue(obj.failed)
    with self.assertRaisesRegex(RuntimeError,'sticky failure'):obj.before_input()
 def test_foreign_display_role_or_observer_never_reaches_query(self):
  for mutation in('display','role','observer'):
   with self.subTest(mutation=mutation):
    calls,t,proxy,obj=setup()
    if mutation=='display':t.pin.display=':167'
    elif mutation=='role':t.pin.role='botA'
    else:proxy.observer=object()
    with self.assertRaises(ValueError):obj.arm()
    self.assertFalse(any(r[0]in('query','sync','arm')for r in calls));self.assertTrue(obj.failed)
 def test_query_exception_is_primary_and_does_not_sync_or_arm(self):
  calls,t,proxy,obj=setup();error=OSError('metadata native error')
  t.t.inner.XTestQueryExtension=Fn(lambda *args:(_ for _ in()).throw(error))
  with self.assertRaises(OSError)as caught:obj.arm()
  self.assertIs(caught.exception,error);self.assertFalse(any(r[0]in('sync','arm')for r in calls));self.assertTrue(obj.failed);self.assertIsNone(proxy.observer)
 def test_helper_has_only_public_metadata_and_sync_calls_no_input_or_new_display(self):
  import ast
  source=Path(a.__file__).read_text();node=next(n for n in ast.parse(source).body if isinstance(n,ast.FunctionDef)and n.name=='prepare_xtest_transport')
  attrs={n.attr for n in ast.walk(node)if isinstance(n,ast.Attribute)}
  self.assertFalse(attrs&{'CDLL','XOpenDisplay','XTestFakeRelativeMotionEvent','XTestFakeKeyEvent','XTestFakeButtonEvent','XQueryPointer'})
  self.assertTrue({'XTestQueryExtension','XSync'}<=attrs)


class Package(unittest.TestCase):
 def test_disabled_release_safe_parent_and_unchanged_qualified_methods(self):
  import importlib.util
  self.assertIsNotNone(importlib.util.find_spec('prepare_a1_xtest_preparation'))
  import prepare_a1_xtest_preparation as b
  with tempfile.TemporaryDirectory()as tmp:
   dest=Path(tmp)/'new';r=b.prepare(dest);m=json.loads((dest/'source-manifest.json').read_text());old=json.loads((b.PARENT/'source-manifest.json').read_text())
   self.assertFalse(r['native_performed']);self.assertFalse(m['runtime_reviewed']);self.assertEqual(m['passive_xrecord'],old['passive_xrecord'])
   for name in('colt_preparation.py','rotation_diagnostics.py','a1_trace_scope.py','x11_endpoint.py','transaction.py','host_budget.py','a1_passive_xrecord_evidence.py','a1_passive_xrecord_worker.py'):
    self.assertEqual((dest/name).read_bytes(),(b.PARENT/name).read_bytes())
   for name in b.CORE_FILES:self.assertEqual((dest/'passive-core'/name).read_bytes(),(b.PARENT/'passive-core'/name).read_bytes())
   import ast
   before=ast.parse((b.PARENT/'a1_passive_xrecord.py').read_text());after=ast.parse((dest/'a1_passive_xrecord.py').read_text())
   for name in('XtstProxy','controller_gc','instrument_transport','method_fingerprints','require_method_qualification','private_json'):
    one=next(n for n in before.body if getattr(n,'name',None)==name);two=next(n for n in after.body if getattr(n,'name',None)==name)
    self.assertEqual(ast.dump(one,include_attributes=False),ast.dump(two,include_attributes=False),name)
   one=next(n for n in before.body if getattr(n,'name',None)=='PassiveRecorder');two=next(n for n in after.body if getattr(n,'name',None)=='PassiveRecorder')
   for node in one.body:
    if isinstance(node,ast.FunctionDef)and node.name!='arm':self.assertEqual(ast.dump(node,include_attributes=False),ast.dump(next(n for n in two.body if getattr(n,'name',None)==node.name),include_attributes=False),node.name)
   self.assertEqual(a.method_fingerprints(dest),old['passive_xrecord']['method_fingerprints'])
   for pins,base in((m['runtime_dependencies'],Path('/')),(m['diagnostic_source_sha256'],dest),(json.loads((dest/'collector/source-manifest.json').read_text())['source_pins'],Path('/'))):
    for path,h in pins.items():self.assertEqual(b.sha(base/path),h)
   for name in('run_dual.py','a1_input_worker.py','a1_passive_xrecord.py','a1_passive_xrecord_worker.py','collector/a1_original_input_collector.py'):
    self.assertTrue('RUNTIME_REVIEWED=False'in(dest/name).read_text()or'RUNTIME_REVIEWED = False'in(dest/name).read_text())
   with self.assertRaises(ValueError):b.prepare(dest)
 def test_changed_actual_method_pin_prevents_copy_without_fallback(self):
  import prepare_a1_xtest_preparation as b
  for key in('METHOD_SHA','METADATA_SHA'):
   with self.subTest(key=key),tempfile.TemporaryDirectory()as tmp,patch.object(b,key,'0'*64):
    dest=Path(tmp)/'new'
    with self.assertRaisesRegex(ValueError,'actual own method result changed'):b.prepare(dest)
    self.assertFalse(dest.exists())


if __name__=='__main__':unittest.main()
