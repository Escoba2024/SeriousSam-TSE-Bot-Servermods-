"""Actual private Observer source in the existing VM; no Retail bytes in Git."""
import hashlib
import importlib.util
from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest

PARENT=Path('/srv/tse-a1-first-state-inputfree-method-final-disabled-20261115/method-api')
HARNESS=Path('/srv/tse-a1-first-state-respawn-completion-20261112/successor/tests/observer_harness.js')
TOOL=Path(__file__).with_name('first_state_wine_identity_patch.py')
BODY_SHA='7d93b441ca9657fa09771a011440c4e651136c656e8c0504a2ddf9420f681158'
COMPILED_SHA='fec627f202376fae1a5682102fb8344f4ef814ab6ba3e462080e4099adc329a6'


def module():
    spec=importlib.util.spec_from_file_location('winepatch',TOOL)
    result=importlib.util.module_from_spec(spec);spec.loader.exec_module(result);return result


class ActualWineIdentityVM(unittest.TestCase):
    def run_case(self,case,name='Engine.dll'):
        body=(PARENT/'observer_body.js').read_text();compiled=(PARENT/'vendor/observer/observer.js').read_text()
        self.assertEqual(hashlib.sha256(body.encode()).hexdigest(),BODY_SHA)
        self.assertEqual(hashlib.sha256(compiled.encode()).hexdigest(),COMPILED_SHA)
        source=module().patch_compiled(compiled)if TOOL.exists()else compiled
        with tempfile.TemporaryDirectory(prefix='first-state-wine-vm-')as tmp:
            root=Path(tmp);(root/'tests').mkdir();(root/'bindings').mkdir()
            shutil.copyfile(PARENT/'vendor/observer/bindings/original-bindings.json',root/'bindings/original-bindings.json')
            harness=HARNESS.read_text()
            old="getModuleByName:n=>moduleOverrides[n]||{base:P(bases[n]),size:G.modules[n].image_size}"
            self.assertEqual(harness.count(old),1)
            harness=harness.replace(old,"getModuleByName:n=>{throw Error('unable to find module '+n);}")
            anchor=" const bases={'Engine.dll':Number(cfg.engine_base),'EntitiesMP.dll':Number(cfg.entities_base)};"
            self.assertEqual(harness.count(anchor),1)
            harness=harness.replace(anchor,anchor+"""
 for(const[name,base]of Object.entries(bases)){
  const b=Buffer.alloc(4096),nt=name==='Engine.dll'?264:248;
  b.writeUInt16LE(0x5a4d,0);b.writeUInt32LE(nt,0x3c);b.writeUInt32LE(0x4550,nt);
  b.writeUInt16LE(0x14c,nt+4);b.writeUInt16LE(224,nt+20);b.writeUInt16LE(0x10b,nt+24);
  b.writeUInt32LE(G.modules[name].image_size,nt+80);put(base,b);
 }
""")
            harness=harness.replace('cb.onEnter.call({threadId:thread,context:{eax:P(2),edx:P(0x900000)}});',
                "(typeof cb==='function'?cb:cb.onEnter).call({threadId:thread,context:{eax:P(2),edx:P(0x900000)}});")
            (root/'tests/observer_harness.js').write_text(harness);(root/'observer.js').write_text(source)
            r=subprocess.run(['node',str(Path(__file__).with_name('test_first_state_wine_identity_vm.js')),str(root/'tests/observer_harness.js'),case,name],capture_output=True,text=True,timeout=10)
            self.assertEqual(r.returncode,0,r.stdout+r.stderr)

    def test_wine_absent_pe_module_list_and_exact_i1_i2_chain(self):self.run_case('wine')
    def test_bad_base_before_any_attach(self):self.run_case('base')
    def test_unaligned_base_before_any_attach(self):self.run_case('unaligned')
    def test_wrapping_base_before_any_attach(self):self.run_case('overflow')
    def test_bad_mz_before_any_attach(self):self.run_case('mz')
    def test_bad_pe_before_any_attach(self):self.run_case('pe')
    def test_bad_machine_before_any_attach(self):self.run_case('machine')
    def test_bad_optional_size_before_any_attach(self):self.run_case('optional_size')
    def test_bad_optional_magic_before_any_attach(self):self.run_case('optional_magic')
    def test_bad_image_size_before_any_attach(self):self.run_case('image_size')
    def test_wrong_original_nt_offset_before_any_attach(self):self.run_case('nt_exact')
    def test_unbounded_nt_offset_before_any_attach(self):self.run_case('nt_bounds')
    def test_missing_header_memory_before_any_attach(self):self.run_case('missing')
    def test_valid_header_does_not_bypass_full_original_body(self):self.run_case('body')
    def test_valid_header_does_not_bypass_iat(self):self.run_case('iat')
    def test_lifetime_header_mutation_stays_sticky(self):self.run_case('lifetime')
    def test_header_failure_in_admitted_leave_after_stop_stays_failure(self):self.run_case('leavefault')
    def test_default_disabled(self):self.run_case('disabled')

    def test_entities_header_guards_also_precede_any_attach(self):
        for case in('mz','pe','machine','optional_size','optional_magic','image_size','nt_exact','nt_bounds','missing'):
            with self.subTest(case=case):self.run_case(case,'EntitiesMP.dll')

    def test_complete_source_inverses_and_g_mutation_rejected(self):
        if not TOOL.exists():self.fail('wine identity transform not implemented')
        m=module();old=(PARENT/'observer_body.js').read_text();compiled=(PARENT/'vendor/observer/observer.js').read_text()
        new=m.patch_body(old);self.assertEqual(m.reverse_body(new),old)
        changed=m.patch_compiled(compiled);self.assertEqual(m.reverse_compiled(changed),compiled)
        self.assertEqual(changed[:-len(new)],compiled[:-len(old)])
        with self.assertRaises(ValueError):m.patch_body(old.replace("'TLS index changed'","'changed'"))
        with self.assertRaises(ValueError):m.reverse_body(new.replace("'TLS index changed'","'changed'"))
        with self.assertRaises(ValueError):m.reverse_compiled(changed.replace('const G=', 'const G= ',1))


if __name__=='__main__':unittest.main()
