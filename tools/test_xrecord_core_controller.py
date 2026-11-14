"""UNEXECUTED Root-window test text for own-process lifecycle and verdict.

Only synthetic processes/channels may run in later offline tests. No Xlib,
Xvfb, Wine, Frida or game is imported or launched by these test intentions.
"""
import ast
import importlib
from pathlib import Path
import unittest


def implementation(case):
    try:return importlib.import_module('xrecord_core_controller')
    except ModuleNotFoundError:case.fail('missing disabled own XRecord method controller')


class ControllerContractTests(unittest.TestCase):
    def setUp(self):self.m=implementation(self)
    def test_runtime_disabled_and_only_display_167_is_allowed(self):
        self.assertIs(self.m.RUNTIME_REVIEWED,False)
        for display in(':154',':155',':0','localhost:167',':167.1'):
            with self.subTest(display=display):
                with self.assertRaises(ValueError):self.m.validate_display(display)
        self.assertEqual(self.m.validate_display(':167'),':167')
    def test_gate_fails_before_child_or_display_start(self):
        with self.assertRaisesRegex(RuntimeError,'disabled'):self.m.run_method(Path('/nonexistent/must-not-be-read'))
    def test_own_identity_must_match_exact_start_argv_and_display(self):
        expected=dict(pid=123,start_ticks=456,argv=['python3','OWN.py','--recorder',':167'],display=':167')
        self.assertTrue(self.m.identity_matches(expected,dict(expected)))
        for field,value in[('pid',124),('start_ticks',457),('argv',['python3','FOREIGN.py']),('display',':154')]:
            actual=dict(expected);actual[field]=value
            with self.subTest(field=field):self.assertFalse(self.m.identity_matches(expected,actual))
    def test_parent_has_no_xlib_import_load_or_call(self):
        source=Path(self.m.__file__).read_text();tree=ast.parse(source)
        for node in ast.walk(tree):
            if isinstance(node,ast.Import):self.assertFalse(any(x.name in('ctypes','Xlib')for x in node.names))
            if isinstance(node,ast.ImportFrom):self.assertNotIn(node.module,('ctypes','Xlib'))
            if isinstance(node,ast.Call):
                name=ast.unparse(node.func)
                self.assertFalse(any(x in name for x in('XOpenDisplay','XRecordEnable','XTestFake','CDLL','LoadLibrary')))
    def test_cleanup_attempts_every_own_role_after_an_earlier_error(self):
        seen=[];errors=[]
        def recorder():seen.append('recorder');raise ValueError('stop failed')
        self.m.cleanup_owned(recorder,lambda:seen.append('driver'),lambda:seen.append('display'),errors)
        self.assertEqual(seen,['recorder','driver','display'])
        self.assertEqual(len(errors),1);self.assertIn('stop failed',errors[0])


class PartialVerdictTests(unittest.TestCase):
    def setUp(self):self.m=implementation(self)
    def receipt(self):
        return dict(errors=[],record_version=[1,13],xtest_version=[2,2],start_of_data=True,end_of_data=True,
            unknown_records=0,malformed=0,dropped=0,overflow=False,recorder_expired=False,
            xtest_relative_requests=[dict(dx=12,dy=0)],warp_requests=[dict(dst_x=400,dst_y=300)],
            query_positions=[[412,300],[400,300]],request_client_bound=True,
            device_motion_positions=[[412,300],[400,300]],delivered_motion_positions=[[412,300],[400,300]],
            recorder_closed=True,driver_closed=True,display_closed=True,children_reaped=True,
            record_context_freed=True,record_data_freed=True,connections_closed=True,
            resources=dict(measured=True),xi2_complete=False,tse_started=False)
    def test_success_is_only_partial_core_method_never_retail_or_xi2(self):
        out=self.m.method_verdict(self.receipt())
        self.assertEqual(out['status'],'PASS_METHOD_PARTIAL_CORE_REQUESTS_ONLY')
        self.assertFalse(out['retail_qualified']);self.assertFalse(out['xi2_complete']);self.assertFalse(out['a1_pass'])
    def test_duplicate_request_or_missing_actual_position_never_passes(self):
        for key,value in [('xtest_relative_requests',[dict(dx=12,dy=0),dict(dx=12,dy=0)]),
                          ('warp_requests',[]),('query_positions',[[412,300],[412,300]]),
                          ('request_client_bound',False),('start_of_data',False),('end_of_data',False)]:
            row=self.receipt();row[key]=value
            with self.subTest(key=key):self.assertNotEqual(self.m.method_verdict(row)['status'],'PASS_METHOD_PARTIAL_CORE_REQUESTS_ONLY')
    def test_delivered_copies_are_not_added_to_device_count(self):
        row=self.receipt();row['delivered_motion_positions']*=2
        out=self.m.method_verdict(row)
        self.assertEqual(out['device_motion_count'],2);self.assertEqual(out['delivered_motion_count'],4)
    def test_error_overflow_or_incomplete_cleanup_is_sticky_failure(self):
        for key,value in [('errors',['earlier timeout']),('malformed',1),('dropped',1),('overflow',True),
                          ('recorder_expired',True),('recorder_closed',False),('driver_closed',False),
                          ('display_closed',False),('children_reaped',False),('record_context_freed',False),
                          ('record_data_freed',False),('connections_closed',False),('tse_started',True)]:
            row=self.receipt();row[key]=value
            with self.subTest(key=key):self.assertNotEqual(self.m.method_verdict(row)['status'],'PASS_METHOD_PARTIAL_CORE_REQUESTS_ONLY')
    def test_unobserved_extensions_or_resources_cannot_be_invented(self):
        for key,value in [('record_version',None),('xtest_version',None),('resources',{'measured':False})]:
            row=self.receipt();row[key]=value
            with self.subTest(key=key):self.assertNotEqual(self.m.method_verdict(row)['status'],'PASS_METHOD_PARTIAL_CORE_REQUESTS_ONLY')


if __name__=='__main__':unittest.main()
