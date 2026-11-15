"""Actual pinned load/compiled source; fakes never load Frida or game code."""
import ast
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import tempfile
import types
import unittest
from tools.test_first_state_getter_boundary_patch import fixture_source

PARENT=Path('/srv/tse-a1-first-state-getter-receipt-disabled-20261115/method-api')
PINS={'python':'d2801018afb64702826d9329f082ee314e718ab149f6211983170e4b04a12cd7',
 'body':'abeab90d6a656c53e4acb349313686ead6a81f1b95a463e1dcd2de1262deb4d8',
 'compiled':'f5cc6498598fbd9de77dfc229ad04a4c7b0275be2b0c6541c9a5857b9c144c78'}
FILES={'python':'native_first_state.py','body':'observer_body.js','compiled':'vendor/observer/observer.js'}
TOOL=Path(__file__).with_name('first_state_v8_runtime_patch.py')
IDENTITY={'runtime':'V8','pid':444,'arch':'ia32','pointer_size':4}
DEFAULT=object()

def source(kind,patched=True):
    text=(PARENT/FILES[kind]).read_text()
    if hashlib.sha256(text.encode()).hexdigest()!=PINS[kind]:raise AssertionError('exact parent '+kind)
    if patched and TOOL.exists():
        from tools import first_state_v8_runtime_patch as p
        return getattr(p,'patch_'+kind)(text)
    return text

def load_namespace():
    tree=ast.parse(source('python'))
    nodes=[n for n in tree.body if isinstance(n,(ast.ClassDef,ast.FunctionDef))and n.name in ('NativeBindingError','require','atomic_json')]
    cls=next(n for n in tree.body if isinstance(n,ast.ClassDef)and n.name=='NativePorts')
    cls.body=[n for n in cls.body if isinstance(n,ast.FunctionDef)and n.name in ('__init__','load','unload','detach')]
    nodes.append(cls);ns={'Path':Path,'json':json,'os':os}
    exec(compile(ast.fix_missing_locations(ast.Module(body=nodes,type_ignores=[])),'actual_pinned_NativePorts.load','exec'),ns)
    return ns

class FakeScript:
    def __init__(self,events,value,fault):self.events=events;self.value=value;self.fault=fault;self.exports_sync=self
    def on(self,event,callback):self.events.append(('on',event));self.callback=callback
    def load(self):
        self.events.append(('load',))
        if self.fault=='load':raise RuntimeError('load rejected')
    def runtimeidentity(self):
        self.events.append(('identity',))
        if self.fault=='rpc':raise RuntimeError('identity RPC failed')
        return self.value
    def unload(self):self.events.append(('unload',))
class FakeSession:
    def __init__(self,value,fault=None):self.events=[];self.fault=fault;self.script=FakeScript(self.events,value,fault)
    def create_script(self,source,**options):
        self.events.append(('create',source,options))
        if self.fault=='create':raise RuntimeError('runtime unavailable')
        return self.script
    def detach(self):self.events.append(('detach',))

class ActualLoad(unittest.TestCase):
    def ports(self,root,value=DEFAULT,fault=None):
        ns=load_namespace();session=FakeSession(dict(IDENTITY)if value is DEFAULT else value,fault)
        obj=ns['NativePorts'](types.SimpleNamespace(expected={'pid':444}),'same compiled source',root);obj.session=session
        return obj,session,ns
    def test_literal_v8_request_once_no_fallback(self):
        with tempfile.TemporaryDirectory()as root:
            p,s,_=self.ports(root);p.load()
            self.assertEqual(s.events[0],('create','same compiled source',{'runtime':'v8'}))
            self.assertEqual(sum(e[0]=='create'for e in s.events),1)
    def test_actual_cold_identity_once_after_load_private_atomic_receipt(self):
        with tempfile.TemporaryDirectory()as root:
            p,s,_=self.ports(root);p.load()
            path=Path(root)/'observer-runtime-identity.json'
            self.assertTrue(path.exists(),'actual load produced no runtime receipt')
            self.assertEqual(json.loads(path.read_text()),{'requested_runtime':'v8','identity':IDENTITY})
            self.assertEqual(path.stat().st_mode&0o777,0o600)
            self.assertEqual([e[0]for e in s.events],['create','on','load','identity'])
            self.assertFalse(path.with_name(path.name+'.tmp').exists())
    def test_wrong_identity_and_exact_types_rejected_raw_preserved(self):
        variants=[{**IDENTITY,'runtime':'QJS'},{**IDENTITY,'pid':445},{**IDENTITY,'pid':444.0},
          {**IDENTITY,'pid':True},{**IDENTITY,'arch':'x64'},{**IDENTITY,'pointer_size':8},
          {**IDENTITY,'pointer_size':4.0},{**IDENTITY,'extra':1},{k:v for k,v in IDENTITY.items()if k!='arch'},[],False,None]
        for value in variants:
            with self.subTest(value=value),tempfile.TemporaryDirectory()as root:
                p,s,ns=self.ports(root,value)
                with self.assertRaisesRegex(ns['NativeBindingError'],'runtime identity'):p.load()
                self.assertEqual(json.loads((Path(root)/'observer-runtime-identity.json').read_text())['identity'],value)
                self.assertEqual(sum(e[0]=='identity'for e in s.events),1)
    def test_create_failure_no_fallback_or_cold_rpc(self):
        with tempfile.TemporaryDirectory()as root:
            p,s,_=self.ports(root,fault='create')
            with self.assertRaisesRegex(RuntimeError,'runtime unavailable'):p.load()
            self.assertEqual(s.events,[('create','same compiled source',{'runtime':'v8'})]);self.assertIsNone(p.script)
    def test_load_failure_keeps_script_for_existing_cleanup(self):
        with tempfile.TemporaryDirectory()as root:
            p,s,_=self.ports(root,fault='load')
            with self.assertRaisesRegex(RuntimeError,'load rejected'):p.load()
            p.unload();p.detach();self.assertEqual([e[0]for e in s.events],['create','on','load','unload','detach'])
    def test_cold_rpc_failure_never_retries_and_cleanup_remains_available(self):
        with tempfile.TemporaryDirectory()as root:
            p,s,_=self.ports(root,fault='rpc')
            with self.assertRaisesRegex(RuntimeError,'identity RPC failed'):p.load()
            p.unload();p.detach();self.assertEqual([e[0]for e in s.events],['create','on','load','identity','unload','detach'])
    def test_actual_atomic_receipt_write_failure_propagates_before_any_arm(self):
        with tempfile.TemporaryDirectory()as root:
            p,s,ns=self.ports(root);target=Path(root)/'untouched';target.write_text('private sentinel')
            (Path(root)/'observer-runtime-identity.json.tmp').symlink_to(target)
            with self.assertRaisesRegex(ns['NativeBindingError'],'temporary path changed'):p.load()
            self.assertEqual(target.read_text(),'private sentinel');p.unload();p.detach()
            self.assertEqual([e[0]for e in s.events],['create','on','load','identity','unload','detach'])
    def test_nonfinite_cold_reply_is_not_sanitized_or_accepted(self):
        with tempfile.TemporaryDirectory()as root:
            p,s,_=self.ports(root,{**IDENTITY,'pid':float('nan')})
            with self.assertRaises(ValueError):p.load()
            self.assertFalse((Path(root)/'observer-runtime-identity.json').exists())
    def test_message_callback_raw_behavior_unchanged(self):
        with tempfile.TemporaryDirectory()as root:
            p,s,_=self.ports(root);p.load();s.script.callback({'type':'error'},b'\x01\x02')
            self.assertEqual(json.loads((Path(root)/'observer-unexpected-messages.json').read_text()),[{'message':{'type':'error'},'data_hex':'0102'}])

class ActualCompiled(unittest.TestCase):
    def run_case(self,case,old_runner=False):
        text=fixture_source();old=' const sandbox={rpc:{exports:{}},Process:{id:444,'
        self.assertEqual(text.count(old),1);text=text.replace(old," const sandbox={Script:{runtime:'V8'},rpc:{exports:{}},Process:{id:444,",1)
        # Expose the sandbox only in the OS-free VM fixture, never production.
        old='return {commit,get pending()';self.assertEqual(text.count(old),1);text=text.replace(old,'return {sandbox,commit,get pending()',1)
        with tempfile.TemporaryDirectory(prefix='v8-cold-vm-')as directory:
            root=Path(directory);(root/'tests').mkdir();(root/'bindings').mkdir()
            shutil.copyfile(PARENT/'vendor/observer/bindings/original-bindings.json',root/'bindings/original-bindings.json')
            (root/'tests/observer_harness.js').write_text(text);(root/'observer.js').write_text(source('compiled'))
            runner='test_first_state_getter_boundary_vm.js'if old_runner else'test_first_state_v8_runtime_vm.js'
            result=subprocess.run(['node',str(Path(__file__).with_name(runner)),str(root/'tests/observer_harness.js'),case],capture_output=True,text=True,timeout=10)
            self.assertEqual(result.returncode,0,result.stdout+result.stderr)
    def test_actual_cold_runtime_rpc_exact_no_hook_or_memory_read(self):self.run_case('cold')
    def test_actual_rpc_reports_qjs_truthfully_no_v8_fallback(self):self.run_case('qjs')
    def test_runtime_metadata_does_not_open_disabled_arm(self):self.run_case('gate')
    def test_inherited_i1_i2_ttl_identity_fullbytes_iat_and_stop_on_new_compiled(self):
        for case in ('commit','ttl','identity','header','body','iat','disabled','stopinside','nonmainleave'):
            with self.subTest(case=case):self.run_case(case,True)
    @unittest.skipUnless(TOOL.exists(),'transform absent during behavior RED')
    def test_full_three_file_inverses_and_g_prefix(self):
        from tools import first_state_v8_runtime_patch as p
        for kind in FILES:
            with self.subTest(kind=kind):self.assertEqual(getattr(p,'reverse_'+kind)(source(kind)),source(kind,False))
        body=source('body');oldbody=source('body',False);compiled=source('compiled');oldcompiled=source('compiled',False)
        self.assertEqual(compiled[:-len(body)],oldcompiled[:-len(oldbody)])
        self.assertEqual(body.replace(p.JS_ADDITION,''),oldbody)
    @unittest.skipUnless(TOOL.exists(),'transform absent during behavior RED')
    def test_exact_source_and_inverse_reject_other_edits(self):
        from tools import first_state_v8_runtime_patch as p
        for kind in FILES:
            with self.subTest(kind=kind):
                with self.assertRaises(ValueError):getattr(p,'patch_'+kind)(source(kind,False)+'\n')
                with self.assertRaises(ValueError):getattr(p,'reverse_'+kind)(source(kind)+'\n')
        with self.assertRaises(ValueError):p.reverse_body(source('body').replace('const RUNTIME_REVIEWED = false;','const RUNTIME_REVIEWED = true;',1))
        with self.assertRaises(ValueError):p.reverse_compiled(source('compiled').replace('const G=','const G= ',1))

if __name__=='__main__':unittest.main()
