import copy
import importlib.util
import unittest
from pathlib import Path

spec = importlib.util.spec_from_file_location('obstacle', Path(__file__).with_name('Test-ObstacleEvidence.py'))
m = importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)

class EvidenceTests(unittest.TestCase):
    def setUp(self):
        self.nav = {}
        for tick in range(1, 44):
            self.nav[(0, tick)] = dict(active='1', phase='2', alive='1', began='0', finished='0',
                delta='0', forward='1', front='3', left='3', right='0.2', pos=f'({tick/5},0,0)',
                hold='0', reason='1', hitType='0')
        self.nav[(0, 1)].update(active='1', phase='1', began='1', forward='0', delta='2.25', front='0.2', hitType='4')
        self.nav[(0, 41)]['finished'] = '1'
        self.nav[(0, 42)].update(active='0', phase='0', forward='0')
        self.nav[(0, 43)].update(active='0', phase='0', forward='0')
        self.combat = {(0, t): dict(ready='1') for t in range(1, 244)}
        self.driver = {(0, t): int(t == 43) for t in range(1, 244)}

    def audit(self):
        return m.audit_rows(self.nav, self.combat, self.driver, (0,), 43)

    def test_valid(self):
        self.assertEqual(self.audit()[0]['advancesAtLeast2m'], 1)

    def test_missing_navigation(self):
        self.nav = {}
        with self.assertRaisesRegex(AssertionError, 'missing navigation'): self.audit()

    def test_model_hit_does_not_prove_wall(self):
        self.nav[(0, 1)]['hitType'] = '2'
        with self.assertRaisesRegex(AssertionError, 'actual brush'): self.audit()

    def test_stationary_completion_is_not_success(self):
        for v in self.nav.values(): v['pos'] = '(0,0,0)'
        with self.assertRaisesRegex(AssertionError, 'actual brush'): self.audit()

    def test_fire_during_turn_rejected(self):
        self.driver[(0, 1)] = 1
        with self.assertRaisesRegex(AssertionError, 'attack while'): self.audit()

    def test_unbounded_attempt_rejected(self):
        self.driver = {(0, t): 0 for t in range(1, 244)}
        self.nav[(0, 41)]['finished'] = '0'
        for tick in range(2, 244):
            self.nav[(0, tick)] = copy.deepcopy(self.nav[(0, 1)])
            self.nav[(0, tick)]['began'] = '0'
        with self.assertRaisesRegex(AssertionError, 'overall attempt'): self.audit()

    def test_unrelated_stuck_success_does_not_prove_wall_recovery(self):
        self.nav[(0, 2)].update(active='0', phase='0', forward='0')
        self.nav[(0, 3)].update(began='1', reason='2')
        with self.assertRaisesRegex(AssertionError, 'actual brush'): self.audit()

    def test_missing_matching_action_rejected(self):
        del self.driver[(0, 2)]
        with self.assertRaisesRegex(AssertionError, 'matching combat/driver'): self.audit()

    def test_missing_native_tick_rejected(self):
        self.nav[(0, 44)] = self.nav.pop((0, 20))
        with self.assertRaisesRegex(AssertionError, 'missing native navigation'): self.audit()

if __name__ == '__main__': unittest.main()
