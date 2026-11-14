"""Package pin closure and strict unchanged native/ACK/cleanup source contract."""
import ast
import json
from pathlib import Path
import tempfile
import unittest

import prepare_a1_release_before_observation as builder


class PackageTests(unittest.TestCase):
    def test_derived_disabled_package_has_only_the_reviewed_behavior_delta(self):
        self.assertTrue(hasattr(builder,'prepare'),'missing fresh disabled package builder')
        with tempfile.TemporaryDirectory()as tmp:
            out=Path(tmp)/'new';receipt=builder.prepare(out)
            m=json.loads((out/'source-manifest.json').read_text())
            cm=json.loads((out/'collector/source-manifest.json').read_text())
            self.assertFalse(m['runtime_reviewed']);self.assertFalse(m['runtime_performed'])
            self.assertFalse(cm['runtime_reviewed']);self.assertFalse(receipt['native_started'])
            for p,h in m['runtime_dependencies'].items():self.assertEqual(builder.sha(p),h,p)
            for p,h in m['diagnostic_source_sha256'].items():self.assertEqual(builder.sha(out/p),h,p)
            for p,h in cm['source_pins'].items():self.assertEqual(builder.sha(p),h,p)
            def gates(p):
                return next(ast.literal_eval(x.value)for x in ast.parse(p.read_text()).body
                    if isinstance(x,ast.Assign)and any(isinstance(t,ast.Name)and t.id=='RUNTIME_REVIEWED'for t in x.targets))
            for name in('run_dual.py','a1_input_worker.py','collector/a1_original_input_collector.py'):
                self.assertIs(gates(out/name),False,name)
            for name in('strict_backend.py','mapped_rows.py','a1_mapping_failure_receipt.py',
                         'colt_preparation.py','rotation_diagnostics.py','a1_trace_scope.py',
                         'runtime_policy.py','host_budget.py','x11_endpoint.py','dual_input.py',
                         'transaction.py','tools/retail_inventory_readonly.py',
                         'collector/a1_original_input_readonly.js','collector/original-input-guards.json'):
                self.assertEqual((out/name).read_bytes(),(builder.PARENT/name).read_bytes(),name)
            old=json.loads((builder.PARENT/'source-manifest.json').read_text())
            for k in('originals','preparation','host_budget','trace_supervision'):
                self.assertEqual(m[k],old[k],k)
            for p,h in old['runtime_dependencies'].items():
                if not Path(p).is_relative_to(builder.PARENT):self.assertEqual(m['runtime_dependencies'][p],h,p)
            def functions(source):return{x.name:ast.dump(x,include_attributes=False)for x in ast.parse(source).body if isinstance(x,ast.FunctionDef)}
            before=functions((builder.PARENT/'run_dual.py').read_text());after=functions((out/'run_dual.py').read_text())
            for k in before.keys()-{'main','action_step'}:self.assertEqual(before[k],after[k],k)
            def nested(source):
                main=next(x for x in ast.parse(source).body if isinstance(x,ast.FunctionDef)and x.name=='main')
                return{x.name:ast.dump(x,include_attributes=False)for x in ast.walk(main)if isinstance(x,ast.FunctionDef)and x is not main}
            self.assertEqual(nested((builder.PARENT/'run_dual.py').read_text()),nested((out/'run_dual.py').read_text()))
            self.assertEqual((out/'run_dual.py').read_text(),builder.disabled_runner(builder.transform_runner((builder.PARENT/'run_dual.py').read_text())))
            self.assertEqual((out/'a1_input_worker.py').read_text().replace('RUNTIME_REVIEWED=False','RUNTIME_REVIEWED=True'),(builder.PARENT/'a1_input_worker.py').read_text())
            with self.assertRaises(ValueError):builder.prepare(out)
    def test_transform_rejects_unpinned_runner(self):
        with self.assertRaises(ValueError):builder.transform_runner('wrong runner')
    def test_existing_after_release_cp_observer_and_ack_are_preserved(self):
        source=(builder.PARENT/'colt_preparation.py').read_text()
        act=next(x for x in ast.walk(ast.parse(source))if isinstance(x,ast.FunctionDef)and x.name=='act')
        calls=[x for x in ast.walk(act)if isinstance(x,ast.Call)and isinstance(x.func,ast.Name)]
        step=next(x for x in calls if x.func.id=='step')
        after=next(x for x in calls if x.func.id=='observe'and ast.unparse(x.args[0])=="stage + '-after-input'")
        self.assertGreater(after.lineno,step.lineno)
        self.assertIn("event['after_input_frame']=observe(stage+'-after-input'",source)
        source=(builder.PARENT/'rotation_diagnostics.py').read_text()
        self.assertIn('acknowledged(',source)


if __name__=='__main__':unittest.main()
