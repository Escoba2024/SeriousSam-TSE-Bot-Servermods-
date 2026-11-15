"""Actual pinned NativePorts.load + existing FakePorts/compiled VM, no Frida."""
import ast
import json
from pathlib import Path
import tempfile
import types
import unittest
from unittest.mock import patch
from tools import first_state_v8_runtime_patch as v8
from tools import test_first_state_v8_runtime_patch as base

TOOL=Path(__file__).with_name('first_state_qjs_runtime_patch.py')
IDENTITY={'runtime':'QJS','pid':444,'arch':'ia32','pointer_size':4}

def transform():
    if TOOL.exists():
        from tools import first_state_qjs_runtime_patch
        return first_state_qjs_runtime_patch
    return v8  # Actual older explicit-runtime implementation for behavior RED.
def source(kind,patched=True):
    old=base.PARENT/base.FILES[kind];text=old.read_text()
    if v8.digest(text)!=base.PINS[kind]:raise AssertionError('exact parent')
    return getattr(transform(),'patch_'+kind)(text)if patched else text

def ports(root,value=None,fault=None):
    with patch.object(base,'source',source):ns=base.load_namespace()
    session=base.FakeSession(dict(IDENTITY)if value is None else value,fault)
    obj=ns['NativePorts'](types.SimpleNamespace(expected={'pid':444}),'same compiled source',root);obj.session=session
    return obj,session,ns

class ExplicitQJS(unittest.TestCase):
    def test_actual_load_requests_qjs_once_and_cold_receipt(self):
        with tempfile.TemporaryDirectory()as root:
            obj,session,_=ports(root)
            # A fake transport reports the runtime actually requested, not a
            # fabricated QJS response to old literalV8 during the behavior RED.
            create=session.create_script
            def requested(text,**options):
                session.script.value={**IDENTITY,'runtime':'QJS'if options.get('runtime')=='qjs'else'V8'}
                return create(text,**options)
            session.create_script=requested;obj.load()
            self.assertEqual(session.events[0],('create','same compiled source',{'runtime':'qjs'}))
            self.assertEqual([e[0]for e in session.events],['create','on','load','identity'])
            p=Path(root)/'observer-runtime-identity.json';self.assertEqual(json.loads(p.read_text()),{'requested_runtime':'qjs','identity':IDENTITY});self.assertEqual(p.stat().st_mode&0o777,0o600)
    def test_unexpected_v8_pid_arch_pointer_shape_and_types_fail_raw_first(self):
        variants=[{**IDENTITY,'runtime':'V8'},{**IDENTITY,'pid':445},{**IDENTITY,'pid':444.0},{**IDENTITY,'pid':True},
                  {**IDENTITY,'arch':'x64'},{**IDENTITY,'pointer_size':8},{**IDENTITY,'pointer_size':4.0},
                  {**IDENTITY,'extra':1},{k:v for k,v in IDENTITY.items()if k!='runtime'},[],False]
        for value in variants:
            with self.subTest(value=value),tempfile.TemporaryDirectory()as root:
                obj,s,ns=ports(root,value)
                with self.assertRaisesRegex(ns['NativeBindingError'],'runtime identity'):obj.load()
                self.assertEqual(json.loads((Path(root)/'observer-runtime-identity.json').read_text())['identity'],value)
                self.assertEqual(sum(e[0]=='create'for e in s.events),1);self.assertEqual(sum(e[0]=='identity'for e in s.events),1)
    def test_create_load_rpc_errors_do_not_fallback_cleanup_kept(self):
        for fault in('create','load','rpc'):
            with self.subTest(fault=fault),tempfile.TemporaryDirectory()as root:
                obj,s,_=ports(root,fault=fault)
                with self.assertRaises(RuntimeError):obj.load()
                self.assertEqual(sum(e[0]=='create'for e in s.events),1);self.assertEqual(s.events[0][2],{'runtime':'qjs'})
                obj.unload();obj.detach();self.assertTrue(obj.unload_attempted);self.assertTrue(obj.detached)
                self.assertEqual(obj.script is None,fault=='create')
    def test_actual_atomic_raw_failure_and_nonfinite_fail_before_arm(self):
        with tempfile.TemporaryDirectory()as root:
            obj,s,ns=ports(root);sentinel=Path(root)/'untouched';sentinel.write_text('same')
            (Path(root)/'observer-runtime-identity.json.tmp').symlink_to(sentinel)
            with self.assertRaisesRegex(ns['NativeBindingError'],'temporary path changed'):obj.load()
            self.assertEqual(sentinel.read_text(),'same');obj.unload();obj.detach()
        with tempfile.TemporaryDirectory()as root:
            obj,_,_=ports(root,{**IDENTITY,'pid':float('nan')})
            with self.assertRaises(ValueError):obj.load()
            self.assertFalse((Path(root)/'observer-runtime-identity.json').exists())
    @unittest.skipUnless(TOOL.exists(),'new transform absent during actual V8 behavior RED')
    def test_three_entire_inverses_and_compiled_g_byteequal_to_v8(self):
        q=transform()
        for kind in base.FILES:
            with self.subTest(kind=kind):self.assertEqual(getattr(q,'reverse_'+kind)(source(kind)),source(kind,False))
        self.assertEqual(source('body'),v8.patch_body(source('body',False)))
        self.assertEqual(source('compiled'),v8.patch_compiled(source('compiled',False)))
        self.assertEqual(source('compiled')[:-len(source('body'))],source('compiled',False)[:-len(source('body',False))])
        self.assertEqual(q.to_v8_python(source('python')),v8.patch_python(source('python',False)))
    @unittest.skipUnless(TOOL.exists(),'new transform absent during actual V8 behavior RED')
    def test_no_runtime_parameter_fallback_or_foreign_source_gate(self):
        q=transform();tree=ast.parse(source('python'));native=next(c for c in tree.body if isinstance(c,ast.ClassDef)and c.name=='NativePorts')
        load=next(n for n in native.body if isinstance(n,ast.FunctionDef)and n.name=='load');calls=[n for n in ast.walk(load)if isinstance(n,ast.Call)and isinstance(n.func,ast.Attribute)and n.func.attr=='create_script']
        self.assertEqual(len(calls),1);self.assertEqual([(k.arg,ast.literal_eval(k.value))for k in calls[0].keywords],[('runtime','qjs')])
        for kind in base.FILES:
            with self.subTest(kind=kind):
                with self.assertRaises(ValueError):getattr(q,'patch_'+kind)(source(kind,False)+'\n')
                with self.assertRaises(ValueError):getattr(q,'reverse_'+kind)(source(kind)+'\n')
        with self.assertRaises(ValueError):q.reverse_python(source('python').replace("runtime='qjs'","runtime='v8'",1))
        with self.assertRaises(ValueError):q.reverse_compiled(source('compiled').replace('const G=','const G= ',1))
        with self.assertRaises(ValueError):q.reverse_body(source('body').replace('const RUNTIME_REVIEWED = false;','const RUNTIME_REVIEWED = true;',1))
    def test_actual_same_compiled_vm_cold_truth_and_existing_guards(self):
        vm=base.ActualCompiled('test_runtime_metadata_does_not_open_disabled_arm')
        with patch.object(base,'source',source):
            for case in('cold','qjs','gate'):
                with self.subTest(case=case):vm.run_case(case)
            for case in('commit','ttl','identity','header','body','iat','disabled','stopinside','nonmainleave'):
                with self.subTest(case=case):vm.run_case(case,True)

if __name__=='__main__':unittest.main()
