"""Targeted offline replay of the disabled no-fire private preparation copy."""
import ast
import os
from pathlib import Path
import sys
import unittest

PACKAGE=os.environ.get('TSE_A1_TRACE_PACKAGE')
if PACKAGE:
    sys.path.insert(0,str(Path(PACKAGE).resolve(strict=True)))
    from test_colt_preparation import ColtCase


@unittest.skipUnless(PACKAGE,'requires explicit disabled private trace package')
class NoFirePreparationTests(unittest.TestCase):
    def test_successful_calibration_and_aim_end_before_fire(self):
        case=ColtCase();result=case.run()
        self.assertEqual(result['status'],'TRACE_ONLY_NO_FIRE')
        self.assertFalse(any(x[1]=='fire'for x in case.colt_actions))
        self.assertEqual(sum(x[0]=='forward'for x in case.actions),2)
        self.assertEqual(case.clip,6);self.assertEqual(case.target_hp,100)

    def test_all_existing_logic_before_fire_is_byte_exact(self):
        parent=Path('/srv/tse-a1-nosmooth-root-frozen-20261114/colt_preparation.py').read_text()
        child=(Path(PACKAGE)/'colt_preparation.py').read_text()
        self.assertEqual(child.split("        receipt['stage']='diagnostic-stop-before-fire'")[0],
                         parent.split("        receipt['stage']='fire'")[0])

    def test_existing_doubled_gain_remains_failure_and_emits_no_fire(self):
        case=ColtCase();done=[]
        def after(role,control):
            if control=='look_horizontal'and not done:
                done.append(True);pixels=case.colt_actions[-1][3]
                case.local+=pixels*-.25;case.server=case.local;case.view+=pixels*-.25
        case.post_step=after
        with self.assertRaisesRegex(ValueError,'calibrated axis gain'):case.run()
        self.assertEqual(case.receipt['status'],'FAIL')
        self.assertFalse(any(x[1]=='fire'for x in case.colt_actions))

    def test_preserved_helpers_and_native_readers_match_frozen_parent(self):
        parent=Path('/srv/tse-a1-nosmooth-root-frozen-20261114')
        for name in ('rotation_diagnostics.py','runtime_policy.py','transaction.py',
                     'host_budget.py','strict_backend.py','x11_endpoint.py',
                     'tools/retail_inventory_readonly.py'):
            with self.subTest(name=name):self.assertEqual((parent/name).read_bytes(),(Path(PACKAGE)/name).read_bytes())
        def functions(text):
            return {n.name:ast.dump(n,include_attributes=False)for n in ast.parse(text).body
                    if isinstance(n,(ast.FunctionDef,ast.AsyncFunctionDef))}
        old=functions((parent/'run_dual.py').read_text());new=functions((Path(PACKAGE)/'run_dual.py').read_text())
        for name in old.keys()-{'main'}:
            with self.subTest(function=name):self.assertEqual(old[name],new[name])

    def test_actual_inherited_sequence_passes_hard_scope(self):
        from a1_trace_scope import InputScope
        case=ColtCase();scope=InputScope();original=case.step
        def step(role,control,seconds,*,before_press=lambda:None,pixels=None):
            scope.admit(role,control,seconds,pixels)
            return original(role,control,seconds,before_press=before_press,pixels=pixels)
        case.step=step
        self.assertEqual(case.run()['status'],'TRACE_ONLY_NO_FIRE')
        self.assertGreater(scope.count,6);self.assertLessEqual(scope.count,48)

    def test_all_protected_nested_read_start_close_and_restore_functions_are_exact(self):
        parent=Path('/srv/tse-a1-nosmooth-root-frozen-20261114/run_dual.py').read_text()
        child=(Path(PACKAGE)/'run_dual.py').read_text()
        def nested(text):
            main=next(n for n in ast.parse(text).body if isinstance(n,ast.FunctionDef)and n.name=='main')
            return {n.name:ast.dump(n,include_attributes=False)for n in ast.walk(main)if isinstance(n,ast.FunctionDef)}
        old,new=nested(parent),nested(child)
        changed={'main','periodic','bounded_step'}
        for name in old.keys()-changed:
            with self.subTest(function=name):self.assertEqual(old[name],new[name])

    def test_all_three_execution_gates_and_both_manifests_disabled(self):
        import json
        def assignment(path,name):
            return next(ast.literal_eval(n.value)for n in ast.parse(path.read_text()).body
                if isinstance(n,ast.Assign)and any(isinstance(t,ast.Name)and t.id==name for t in n.targets))
        root=Path(PACKAGE);library=Path('/srv/tse-a1-input-trace-controller-20261114')
        for path in(root/'run_dual.py',root/'a1_input_worker.py',library/'a1_original_input_collector.py'):
            self.assertIs(assignment(path,'RUNTIME_REVIEWED'),False)
        for path in(root/'source-manifest.json',library/'source-manifest.json'):
            self.assertIs(json.loads(path.read_text())['runtime_reviewed'],False)

    def test_offline_builder_reproduces_changed_sources_without_execution(self):
        import tempfile
        from build_a1_trace_preparation import build
        with tempfile.TemporaryDirectory(prefix='a1-trace-offline-')as temp:
            root=Path(temp)/'disabled';manifest=build(root)
            self.assertIs(manifest['runtime_reviewed'],False)
            for name in ('run_dual.py','colt_preparation.py','a1_input_worker.py','a1_trace_scope.py'):
                expected=Path(PACKAGE)/name
                # The guard-cleanup library supplies the one explicitly revised
                # Worker source; CP/runner/controls retain the old pinned bytes.
                library=os.environ.get('TSE_A1_INPUT_PRIVATE')
                if name=='a1_input_worker.py'and library and (Path(library)/name).is_file():
                    expected=Path(library)/name
                with self.subTest(name=name):self.assertEqual((root/name).read_bytes(),expected.read_bytes())

    def test_actual_control_branch_invokes_same_cp_without_collector_setup(self):
        import textwrap
        from unittest import mock
        source=(Path(PACKAGE)/'run_dual.py').read_text()
        node=next(n for n in ast.walk(ast.parse(source))if isinstance(n,ast.FunctionDef)and n.name=='trace_preparation')
        code='def isolated_control_branch():\n collector=None\n'+textwrap.indent(textwrap.dedent(ast.get_source_segment(source,node)),' ')+'\n return trace_preparation()\n'
        callbacks=[object()for _ in range(4)];cp=mock.Mock();cp.run_preparation.return_value={'status':'TRACE_ONLY_NO_FIRE'}
        env=dict(mode='uninstrumented-control',CP=cp,native_rotation_pair=callbacks[0],native_roles=callbacks[1],bounded_step=callbacks[2],capture=callbacks[3],time=__import__('time'),report={'shooter_preparation':{}},started=123)
        exec(code,env)
        self.assertEqual(env['isolated_control_branch'](),{'status':'TRACE_ONLY_NO_FIRE'})
        args,kw=cp.run_preparation.call_args
        self.assertEqual(list(args[:4]),callbacks)
        self.assertEqual(kw,dict(started=123,require_successful_read_sequence=True))
        self.assertNotIn('WorkerProxy',env)  # would raise if the control ever reached setup

    def test_actual_input_gate_requires_ready_collector_only_in_trace_mode(self):
        import textwrap,time
        from a1_trace_scope import InputScope
        source=(Path(PACKAGE)/'run_dual.py').read_text()
        node=next(n for n in ast.walk(ast.parse(source))if isinstance(n,ast.FunctionDef)and n.name=='bounded_step')
        def action(endpoints,step,clock,sleep,periodic,**kw):
            kw['before_press']();return {'released':True}
        env=dict(mode='instrumented-trace',collector=None,input_scope=InputScope(),time=time,started=time.monotonic(),duration=90,report={'input_receipts':[]},action_step=action,endpoints={},periodic=lambda:None,save=lambda:None)
        exec(textwrap.dedent(ast.get_source_segment(source,node)),env)
        with self.assertRaisesRegex(AssertionError,'complete binding'):env['bounded_step']('vanilla','look_right',.1)
        env.update(mode='uninstrumented-control',input_scope=InputScope())
        self.assertTrue(env['bounded_step']('vanilla','look_right',.1)['released'])


if __name__=='__main__':unittest.main()
