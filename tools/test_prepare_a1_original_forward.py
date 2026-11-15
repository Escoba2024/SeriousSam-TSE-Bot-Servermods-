"""Exact Source application; never import/execute generated controller."""
import ast
import importlib.util
from pathlib import Path
import tempfile
import unittest
import a1_original_forward as F

class Builder(unittest.TestCase):
    def module(self):
        p=Path(__file__).with_name('prepare_a1_original_forward.py')
        self.assertTrue(p.exists(),'fresh one-W preparation helper missing')
        s=importlib.util.spec_from_file_location('forward_builder',p);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
    def test_whole_runner_inverse_and_single_arm(self):
        B=self.module();parent=B.read(B.PARENT/'run_dual.py');new=B.transform_runner(parent)
        self.assertEqual(B.transform_runner(new,True),parent)
        self.assertIn(b"arm=='control'",new);self.assertNotIn(b"choices=('control','trace')",new)
        self.assertNotIn(b"parser.add_argument('--evidence-ram-base')",new)
        self.assertIn(b'WF.make_endpoint_class(Endpoint)',new);self.assertIn(b'WF.ownership_reads(RP',new)
    def test_real_primitive_complete_source_inverses(self):
        self.module().prove_primitives()
    def test_arbitrarily_changed_source_cannot_reverse(self):
        B=self.module();new=B.transform_runner(B.read(B.PARENT/'run_dual.py'))
        with self.assertRaises(ValueError):B.transform_runner(new.replace(b'now-start>step',b'now-start<step'),True)
    def test_forward_scope_explicit_and_old_rp_cores_unchanged(self):
        B=self.module();destination=Path('/srv/forward-uncreated-test')
        files,proof=B.files_for(destination)
        import json
        m=json.loads(files['source-manifest.json']);n=json.loads(files['method-api/source-manifest.json'])
        self.assertFalse(m['runtime_reviewed']);self.assertFalse(m['native_ready']);self.assertFalse(n['runtime_reviewed'])
        self.assertEqual(m['scope'],'DISABLED_ORIGINAL_FORWARD_TRANSLATION_V1_NOT_A1')
        self.assertEqual(m['forward_condition']['actual_native_input_calls'],2)
        self.assertTrue(m['little_trouble_condition']['historical_parent_condition_only'])
        self.assertEqual(m['fixed_arms'],['control'])
        for name in proof['immutable_parent_files']:self.assertEqual(files[name],B.read(B.PARENT/name))
        for name,pin in m['runtime_dependencies'].items():
            p=Path(name)
            if p.is_relative_to(destination):self.assertEqual(B.digest(files[str(p.relative_to(destination))]),pin)
    def test_bounded_real_journal_and_report_ports(self):
        self.assertTrue(hasattr(F,'JournalBudget'),'bounded production journal wrapper missing')
        with tempfile.TemporaryDirectory()as d:
            p=Path(d)/'raw.jsonl';budget=F.JournalBudget();stream=F.open_journal(p,budget)
            stream.write('{}\n');stream.flush();budget.used=64*1024**2
            with self.assertRaises(ValueError):stream.write('x')
            stream.close();self.assertEqual(p.read_text(),'{}\n')
            self.assertEqual(p.stat().st_mode&0o777,0o600)

if __name__=='__main__':unittest.main()
