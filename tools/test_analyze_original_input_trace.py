"""Synthetic accounting examples only; this test never accesses a process."""
import copy
import importlib
import unittest


def trace(raw=(12,), axes=(3,), consumed=((0, -3),)):
    return {
        'complete': True, 'dropped': 0, 'pins_verified': True,
        'request': {'axis': 'x', 'pixels': 12, 'confirmed': True},
        'inputs': [{'id': i, 'thread': 7, 'prescan': False,
                    'raw_dx': dx, 'engine_x': axes[i],
                    'cursor_ok': True, 'recenter_ok': True}
                   for i, dx in enumerate(raw)],
        'actions': [{'input_id': i, 'thread': 7, 'prescan': False,
                     'local_yaw_before': 0, 'local_yaw_after': delta}
                    for i, delta in consumed],
        'settled_local_delta': sum(d for _, d in consumed),
        'calibrated_gain': -.25,
    }


class OriginalInputTraceTests(unittest.TestCase):
    def analyze(self, value):
        try:
            module = importlib.import_module('analyze_original_input_trace')
        except ImportError:
            self.fail('offline input-trace analyzer is not implemented')
        return module.analyze(value)

    def test_ordinary_gain_has_no_native_or_cause_verdict(self):
        r = self.analyze(trace())
        self.assertEqual(r['shape'], 'ordinary')
        self.assertEqual(r['raw_dx_total'], 12)
        self.assertEqual(r['local_yaw_delta_total'], -3)
        self.assertFalse(r['native_qualified'])
        self.assertFalse(r['cause_proven'])

    def test_one_request_may_have_doubled_observed_cursor_displacement(self):
        r = self.analyze(trace((24,), (6,), ((0, -6),)))
        self.assertEqual(r['shape'], 'larger_raw_displacement')
        self.assertEqual(r['requested_pixels'], 12)
        self.assertEqual(r['raw_dx_total'], 24)

    def test_distinct_input_invocations_keep_repeated_displacement_visible(self):
        r = self.analyze(trace((12, 12), (3, 3), ((0, -3), (1, -3))))
        self.assertEqual(r['shape'], 'repeated_raw_displacement')
        self.assertEqual(r['input_count'], 2)
        self.assertEqual(r['reused_input_ids'], [])

    def test_same_input_consumed_twice_is_not_mislabeled_as_two_cursor_reads(self):
        r = self.analyze(trace((12,), (3,), ((0, -3), (0, -3))))
        self.assertEqual(r['shape'], 'reused_input_observation')
        self.assertEqual(r['input_count'], 1)
        self.assertEqual(r['reused_input_ids'], [0])

    def test_single_read_engine_transform_change_is_distinct(self):
        self.assertEqual(self.analyze(trace((12,), (6,), ((0, -6),)))['shape'],
                         'engine_transform_difference')

    def test_single_action_transform_change_is_distinct(self):
        self.assertEqual(self.analyze(trace((12,), (3,), ((0, -6),)))['shape'],
                         'action_transform_difference')

    def test_combined_changes_remain_unresolved(self):
        self.assertEqual(self.analyze(trace((24,), (3,), ((0, -6),)))['shape'],
                         'unresolved_combination')

    def test_idle_reads_do_not_turn_one_larger_displacement_into_repeated_motion(self):
        r = self.analyze(trace((0,24,0), (0,6,0), ((0,0),(1,-6),(2,0))))
        self.assertEqual(r['shape'],'larger_raw_displacement')

    def test_idle_action_reuse_is_not_active_input_reuse(self):
        r = self.analyze(trace((0,12), (0,3), ((0,0),(0,0),(1,-3))))
        self.assertEqual(r['shape'],'ordinary')
        self.assertEqual(r['reused_input_ids'],[])

    def test_nonzero_input_without_any_action_is_incomplete_for_attribution(self):
        t = trace((12,0), (3,0), ((1,0),))
        with self.assertRaises(ValueError): self.analyze(t)

    def test_gaps_fail_instead_of_creating_cause(self):
        for field, value in [('complete', False), ('dropped', 1),
                             ('pins_verified', False)]:
            t = trace(); t[field] = value
            with self.subTest(field=field), self.assertRaises(ValueError):
                self.analyze(t)

    def test_invalid_cursor_recenter_request_or_binding_fails(self):
        for change in ('cursor', 'recenter', 'request', 'missing_input',
                       'thread', 'prescan', 'duplicate', 'nonfinite', 'settled'):
            t = trace()
            if change == 'cursor': t['inputs'][0]['cursor_ok'] = False
            elif change == 'recenter': t['inputs'][0]['recenter_ok'] = False
            elif change == 'request': t['request']['confirmed'] = False
            elif change == 'missing_input': t['actions'][0]['input_id'] = 3
            elif change == 'thread': t['actions'][0]['thread'] = 8
            elif change == 'prescan': t['actions'][0]['prescan'] = True
            elif change == 'duplicate': t['inputs'].append(copy.deepcopy(t['inputs'][0]))
            elif change == 'nonfinite': t['inputs'][0]['raw_dx'] = float('nan')
            elif change == 'settled': t['settled_local_delta'] = -6
            with self.subTest(change=change), self.assertRaises(ValueError):
                self.analyze(t)


if __name__ == '__main__':
    unittest.main()
