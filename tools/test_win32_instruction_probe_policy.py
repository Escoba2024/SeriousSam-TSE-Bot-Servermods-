"""Offline verdict tests. Native source/build/execution remain Root-only."""
import unittest


class VerdictTests(unittest.TestCase):
    def policy(self):
        try:
            import win32_instruction_probe_policy as policy
        except ImportError:
            self.fail('missing bounded method verdict policy')
        return policy

    def complete(self):
        return dict(native=dict(phase='WAIT_CLEANUP',saved_edi='12345678',
                                argument_result='10203040'),
                    cleanup=dict(native_frames_returned=True,script_idle=True,
                                 hooks_detached=True,original_bytes_verified=True,
                                 script_unloaded=True,session_detached=True,
                                 process_ended=True,worker_reaped=True,errors=[]),
                    callback_records=2,callback_faults=0,callback_dropped=0,
                    callback_rows=[dict(site='saved',thread=44,stack_top=0x12345678,raw_edi='0x12345678'),
                                   dict(site='arguments',thread=44,stack_top=0x11223344,raw_edi='0x0')],
                    process_returncode=0)

    def test_baseline_and_probe_need_actual_native_sentinel_and_argument_result(self):
        p=self.policy()
        for mode in ('baseline','function-probe'):
            r=self.complete();r['callback_records']=0 if mode=='baseline'else 2
            if mode=='baseline':r['callback_rows']=[]
            self.assertEqual(p.verdict(mode,r)['status'],'PASS_METHOD_ONLY')
            for field in ('saved_edi','argument_result'):
                r=self.complete();r['native'][field]='11111111'
                r['callback_records']=0 if mode=='baseline'else 2
                if mode=='baseline':r['callback_rows']=[]
                self.assertEqual(p.verdict(mode,r)['status'],'FAIL_NATIVE_PRESERVATION')

    def test_historical_object_control_requires_specific_observed_corruption(self):
        p=self.policy();r=self.complete()
        self.assertEqual(p.verdict('historical-object',r)['status'],'CONTROL_NOT_REPRODUCED')
        r['native']['saved_edi']='7b123456'
        v=p.verdict('historical-object',r)
        self.assertEqual(v['status'],'EXPECTED_CONTROL_VIOLATION_OBSERVED')
        self.assertFalse(v['abi_preserved']);self.assertFalse(v['retail_qualified'])

    def test_missing_native_results_or_program_crash_never_count_as_expected_violation(self):
        p=self.policy()
        for change in ('missing','crash','wrong_phase','malformed'):
            r=self.complete()
            if change=='missing':r.pop('native')
            if change=='crash':r['process_returncode']=1
            if change=='wrong_phase':r['native']['phase']='READY'
            if change=='malformed':r['native']['saved_edi']='nan'
            self.assertEqual(p.verdict('historical-object',r)['status'],'FAIL_METHOD_EVIDENCE')

    def test_every_cleanup_predicate_is_required_even_for_expected_control_failure(self):
        p=self.policy()
        for key,value in self.complete()['cleanup'].items():
            r=self.complete();r['native']['saved_edi']='00000000'
            r['cleanup'][key]=['sticky failure']if key=='errors'else False
            self.assertEqual(p.verdict('historical-object',r)['status'],'FAIL_METHOD_EVIDENCE',key)

    def test_fault_drop_or_partial_callbacks_are_never_passes(self):
        p=self.policy()
        for key,value in (('callback_records',1),('callback_faults',1),('callback_dropped',1)):
            r=self.complete();r[key]=value
            self.assertEqual(p.verdict('function-probe',r)['status'],'FAIL_METHOD_EVIDENCE')

    def test_unknown_mode_cannot_select_extra_actions(self):
        with self.assertRaises(ValueError):self.policy().verdict('all',self.complete())

    def test_native_results_do_not_replace_real_bound_site_stack_and_thread_records(self):
        p=self.policy()
        for change in ('empty','wrong_site','wrong_stack','wrong_thread','wrong_edi'):
            r=self.complete()
            if change=='empty':r['callback_rows']=[{},{}]
            if change=='wrong_site':r['callback_rows'][1]['site']='saved'
            if change=='wrong_stack':r['callback_rows'][0]['stack_top']=0x123
            if change=='wrong_thread':r['callback_rows'][1]['thread']=45
            if change=='wrong_edi':r['callback_rows'][0]['raw_edi']='0x0'
            self.assertEqual(p.verdict('function-probe',r)['status'],'FAIL_METHOD_EVIDENCE',change)


if __name__=='__main__':unittest.main()
