"""Replay real private Colt controller with synthetic observations; no process access.

Run with TSE_A1_PACKAGE pointing at the separately pinned private package.
The failure this catches is judging the final gain before the existing stability
interval. Overshoot/reversal remains invalid even when its last value is correct.
"""
import os
from pathlib import Path
import sys
import unittest

package = os.environ.get('TSE_A1_PACKAGE')
if package:
    sys.path.insert(0, str(Path(package).resolve(strict=True)))
    from test_colt_preparation import ColtCase


@unittest.skipUnless(package, 'requires explicitly selected private A1 package')
class SettledAckTests(unittest.TestCase):
    def scenario(self, mode):
        c = ColtCase()
        injected = []

        def after_step(role, control):
            if control != 'look_horizontal' or injected:
                return
            injected.append(True)
            pixels = c.colt_actions[-1][3]
            delta = pixels * -.25
            origin = c.local - delta
            if mode == 'partial_then_full':
                c.pending = [origin + delta / 2, origin + delta / 2,
                             origin + delta, origin + delta, origin + delta]
            elif mode == 'persistent_double':
                c.local = c.server = origin + delta * 2
                c.view += delta
            elif mode == 'double_then_reverse':
                c.pending = [origin + delta * 2, origin + delta * 2,
                             origin + delta, origin + delta]
            else:
                raise AssertionError(mode)

        c.post_step = after_step
        return c

    def test_partial_response_must_settle_before_final_gain_verdict(self):
        c = self.scenario('partial_then_full')
        result = c.run()
        self.assertEqual(result['status'], 'PREPARATION_COMPLETED_REVIEW_REQUIRED')
        self.assertEqual(sum(x[1] == 'fire' for x in c.colt_actions), 1)
        self.assertFalse(result['actual_shot_proven'])

    def test_persistently_different_gain_fails_without_fire(self):
        c = self.scenario('persistent_double')
        with self.assertRaisesRegex(ValueError, 'calibrated axis gain'):
            c.run()
        self.assertEqual(c.receipt['status'], 'FAIL')
        self.assertFalse(any(x[1] == 'fire' for x in c.colt_actions))
        observations = c.receipt['role_observations']
        ticks = [o['frame']['roles']['vanilla']['game_tick'] for o in observations
                 if o['phase'] == 'ack-look_horizontal']
        self.assertGreaterEqual(max(ticks) - min(ticks), .1)

    def test_overshoot_then_reversal_remains_sticky_failure(self):
        c = self.scenario('double_then_reverse')
        with self.assertRaises(ValueError):
            c.run()
        self.assertEqual(c.receipt['status'], 'FAIL')
        self.assertFalse(any(x[1] == 'fire' for x in c.colt_actions))


if __name__ == '__main__':
    unittest.main()
