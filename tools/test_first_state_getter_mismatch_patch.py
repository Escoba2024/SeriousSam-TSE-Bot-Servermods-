"""Actual private compiled Observer: same-read fault detail, not a native proof."""
import hashlib
from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest

from tools.test_first_state_getter_boundary_patch import fixture_source

PARENT=Path('/srv/tse-a1-first-state-autodrain-cgroup-disabled-20261115/method-api')
BODY_SHA='206a232ea1cdb847657f2ba2c6a89fa95b31a701dfc5c77c89df95f39a7f4a02'
COMPILED_SHA='7108529ae5e306ee8cf6d926596bb16f2366ba2924b2841acbff215e9e7b6eb6'
TOOL=Path(__file__).with_name('first_state_getter_mismatch_patch.py')

def harness():
    source=fixture_source()
    old=' const failDetach=new Set(),attemptDetach=[],nativeWrites=[];'
    assert source.count(old)==1
    source=source.replace(old,old+'\n let getterReads=0,lastGetterRead=null,afterGetterRead=null;')
    old='readByteArray:len=>Uint8Array.from(bytes(n,len)).buffer'
    new="""readByteArray:len=>{const out=Uint8Array.from(bytes(n,len));
   if(n===Number(cfg.engine_base)+G.modules['Engine.dll'].guards.current_tick.rva&&len===22){
    getterReads++;lastGetterRead=Buffer.from(out).toString('hex');
    if(afterGetterRead){const callback=afterGetterRead;afterGetterRead=null;callback();}
   }return out.buffer;}"""
    assert source.count(old)==1;source=source.replace(old,new,1)
    old='return {commit,get pending()'
    new='return {sandbox,get getterReads(){return getterReads},get lastGetterRead(){return lastGetterRead},set afterGetterRead(v){afterGetterRead=v},commit,get pending()'
    assert source.count(old)==1;source=source.replace(old,new,1)
    return source

class GetterMismatchVM(unittest.TestCase):
    def run_case(self,case,runner='test_first_state_getter_mismatch_vm.js'):
        compiled=(PARENT/'vendor/observer/observer.js').read_text()
        self.assertEqual(hashlib.sha256(compiled.encode()).hexdigest(),COMPILED_SHA)
        if TOOL.exists():
            from tools.first_state_getter_mismatch_patch import patch_compiled
            compiled=patch_compiled(compiled)
        with tempfile.TemporaryDirectory(prefix='a1-getter-mismatch-')as directory:
            root=Path(directory);(root/'tests').mkdir();(root/'bindings').mkdir()
            shutil.copyfile(PARENT/'vendor/observer/bindings/original-bindings.json',root/'bindings/original-bindings.json')
            (root/'tests/observer_harness.js').write_text(harness());(root/'observer.js').write_text(compiled)
            result=subprocess.run(['node',str(Path(__file__).with_name(runner)),str(root/'tests/observer_harness.js'),case],capture_output=True,text=True,timeout=10)
            self.assertEqual(result.returncode,0,result.stdout+result.stderr)

    def test_actual_fault_path_retains_first_getter_read_detail(self):self.run_case('fault')
    def test_every_original_byte_mutation_and_rebased_highlow(self):self.run_case('allbytes')
    def test_pass_is_one_getter_read_and_preserves_limits_and_gates(self):self.run_case('pass')
    def test_same_read_detail_survives_memory_changing_before_throw(self):self.run_case('sameread')
    def test_stopped_drain_and_nonmain_emit_both_keep_detail(self):self.run_case('otherpaths')
    def test_probe_still_registered_and_active_callback_status_observed(self):self.run_case('pending')

    def test_inherited_strict_chains_lifetime_and_guards_on_new_compiled_source(self):
        for case in ('commit','ttl','identity','header','body','iat','disabled','stopinside','nonmainleave'):
            with self.subTest(case=case):self.run_case(case,'test_first_state_getter_boundary_vm.js')

    @unittest.skipUnless(TOOL.exists(),'transform not implemented for behavioral RED')
    def test_full_source_g_prefix_and_inverse_reject_foreign_edits(self):
        from tools import first_state_getter_mismatch_patch as patch
        body=(PARENT/'observer_body.js').read_text();compiled=(PARENT/'vendor/observer/observer.js').read_text()
        self.assertEqual(hashlib.sha256(body.encode()).hexdigest(),BODY_SHA)
        new=patch.patch_body(body);joined=patch.patch_compiled(compiled)
        self.assertEqual(patch.reverse_body(new),body);self.assertEqual(patch.reverse_compiled(joined),compiled)
        self.assertEqual(joined[:-len(new)],compiled[:-len(body)])
        self.assertEqual(new.count('requireGetterOriginal();'),3)
        for old,new_name in [("'TLS index changed'","'mutated'"),('const RUNTIME_REVIEWED = false;','const RUNTIME_REVIEWED = true;')]:
            with self.assertRaises(ValueError):patch.patch_body(body.replace(old,new_name,1))
            with self.assertRaises(ValueError):patch.reverse_body(new.replace(old,new_name,1))
        with self.assertRaises(ValueError):patch.reverse_compiled(joined.replace('const G=','const G= ',1))

if __name__=='__main__':unittest.main()
