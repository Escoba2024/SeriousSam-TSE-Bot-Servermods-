"""Offline actual-VM tests: private Original bindings never enter this repository."""
import hashlib
import importlib.util
import json
from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest

PARENT=Path('/srv/tse-a1-first-state-respawn-completion-20261112/successor')
BODY_SHA='38275a9f15d9f867bccbefb1f523352c74aad78c8c5ff559da1b1589894fde71'
TOOL=Path(__file__).with_name('first_state_method_patch.py')


def patched(body):
    if not TOOL.exists():return body
    spec=importlib.util.spec_from_file_location('methodpatch',TOOL)
    module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
    return module.patch_body(body)


class ActualObserverVM(unittest.TestCase):
    def run_case(self,case):
        body=(PARENT/'observer_body.js').read_text()
        self.assertEqual(hashlib.sha256(body.encode()).hexdigest(),BODY_SHA)
        with tempfile.TemporaryDirectory(prefix='first-state-vm-')as tmp:
            root=Path(tmp);(root/'tests').mkdir();(root/'bindings').mkdir()
            shutil.copyfile(PARENT/'bindings/original-bindings.json',root/'bindings/original-bindings.json')
            harness=(PARENT/'tests/observer_harness.js').read_text()
            harness=harness.replace('cb.onEnter.call({threadId:thread,context:{eax:P(2),edx:P(0x900000)}});',
                "(typeof cb==='function'?cb:cb.onEnter).call({threadId:thread,context:{eax:P(2),edx:P(0x900000)}});")
            (root/'tests/observer_harness.js').write_text(harness)
            generated=(PARENT/'observer.js').read_text()
            self.assertTrue(generated.endswith(body))
            (root/'observer.js').write_text(generated[:-len(body)]+patched(body))
            result=subprocess.run(['node',str(Path(__file__).with_name('test_first_state_method_vm.js')),str(root/'tests/observer_harness.js'),case],capture_output=True,text=True,timeout=10)
            self.assertEqual(result.returncode,0,result.stdout+result.stderr)

    def test_getter_function(self):self.run_case('getter')
    def test_host_stop_active_pair(self):self.run_case('active')
    def test_stop_inside_callback(self):self.run_case('callback')
    def test_ttl_after_hoststop_is_sticky(self):self.run_case('ttl')
    def test_fault_after_hoststop_is_sticky(self):self.run_case('fault')
    def test_detach_failure_sticky_cleanup(self):self.run_case('detach')
    def test_drain_schema_and_limits_unchanged(self):self.run_case('schema')
    def test_exact_i1_i2_chain(self):self.run_case('chain')
    def test_admitted_nested_i2_leaves_complete_after_host_stop(self):self.run_case('chainstop')
    def test_default_disabled(self):self.run_case('disabled')

    def test_reverse_body_and_guard_mutation_rejected(self):
        if not TOOL.exists():self.fail('patch module missing')
        spec=importlib.util.spec_from_file_location('methodpatch',TOOL);m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
        old=(PARENT/'observer_body.js').read_text();new=m.patch_body(old)
        self.assertEqual(m.reverse_body(new),old)
        with self.assertRaises(ValueError):m.patch_body(old.replace("'TLS index changed'","'MUTATED'"))
        with self.assertRaises(ValueError):m.reverse_body(new.replace("'TLS index changed'","'MUTATED'"))

if __name__=='__main__':unittest.main()
