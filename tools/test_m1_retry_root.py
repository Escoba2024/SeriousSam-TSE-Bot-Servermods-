"""Offline exact-root admission fixtures, not native runtime evidence."""
import copy
import unittest
import m1_recovery_gate as gate

RETRY = '/srv/tse-session-qualification-master-m1-four-hour-r2-20261026'


def matrix():
    return dict(status='DURATION_MATRIX_ACCEPTED', stages=[
        dict(root='/srv/tse-session-qualification-master-m1-' + label + '-20261026',
             verdict=dict(status='DURATION_RECEIPTS_ACCEPTED', bots=bots,
                          required_s=seconds, dll_sha256='a' * 64))
        for label, bots, seconds in [('one-hour', 1, 3600), ('four-hour-r2', 4, 3600),
                                    ('eight-two-hours', 8, 7200)]])


class RetryRootTests(unittest.TestCase):
    def test_exact_reviewed_retry_is_accepted_for_direct_revalidation(self):
        stages = gate.validated_matrix_stages(matrix(), 'a' * 64)
        self.assertEqual(stages[1], (RETRY, 4, 3600))

    def test_unknown_retry_or_other_runtime_is_rejected(self):
        for root in [RETRY.replace('r2', 'r3'), RETRY + '-extra', RETRY.replace('20261026', '20261027'),
                     '/srv/public', '/srv/tse-session-qualification-master-m1-four-on-20261026']:
            sample = matrix()
            sample['stages'][1]['root'] = root
            with self.subTest(root=root), self.assertRaises(ValueError):
                gate.validated_matrix_stages(sample, 'a' * 64)

    def test_retry_cannot_bypass_candidate_status_or_duration(self):
        for key, value in [('dll_sha256', 'b' * 64), ('required_s', 3599), ('status', 'FAIL'), ('bots', 8)]:
            sample = matrix()
            sample['stages'][1]['verdict'][key] = value
            with self.subTest(key=key), self.assertRaises(ValueError):
                gate.validated_matrix_stages(sample, 'a' * 64)

    def test_incomplete_or_blocked_matrix_stays_blocked(self):
        for mode in ('blocked', 'missing', 'duplicate'):
            sample = matrix()
            if mode == 'blocked': sample['status'] = 'BLOCKED'
            if mode == 'missing': sample['stages'].pop()
            if mode == 'duplicate': sample['stages'][2] = copy.deepcopy(sample['stages'][1])
            with self.subTest(mode=mode), self.assertRaises(ValueError):
                gate.validated_matrix_stages(sample, 'a' * 64)


if __name__ == '__main__':
    unittest.main()
