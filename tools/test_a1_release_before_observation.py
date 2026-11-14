"""Execute the actual pinned action loop with memory-only endpoints and clock."""
import ast
import importlib.util
import math
from pathlib import Path
from types import SimpleNamespace
import unittest

PARENT=Path('/srv/tse-a1-exact-coverage-root-frozen-20261114')


def actual_loop():
    source=(PARENT/'run_dual.py').read_text()
    if importlib.util.find_spec('prepare_a1_release_before_observation'):
        from prepare_a1_release_before_observation import transform_runner
        source=transform_runner(source)
    node=next(x for x in ast.parse(source).body if isinstance(x,ast.FunctionDef)and x.name=='action_step')
    env=dict(math=math,P=SimpleNamespace(CONTROLS={'forward','fire','look_right','look_left','look_horizontal','look_vertical'}),
             PP=SimpleNamespace(RouteFlightBeforeInput=type('RouteFlightBeforeInput',(Exception,),{})))
    exec(compile(ast.Module(body=[node],type_ignores=[]),'<actual-action-step>','exec'),env)
    return env['action_step']


class Clock:
    def __init__(self):self.t=0.;self.sleeps=[]
    def now(self):return self.t
    def sleep(self,s):self.sleeps.append(s);self.t+=s


class Endpoint:
    def __init__(self,c):
        self.c=c;self.pin=SimpleNamespace(role='vanilla');self.held=set();self.events=[]
        self.delays=[];self.transport_delay=0;self.release_delay=0
        self.guard_error=None;self.press_error=None;self.release_error=None
    def verify(self):
        self.events.append('verify')
        if self.held:
            if self.delays:self.c.t+=self.delays.pop(0)
            if self.guard_error:raise self.guard_error
    def check_focus(self):self.events.append('focus')
    def neutral(self,controls):self.events.append('neutral')
    def down(self,control,*,submit):
        def request():
            self.events.append('down');self.held.add(control)
            if self.press_error:raise self.press_error
            return 1
        value=submit(request);self.c.t+=self.transport_delay;return value
    def up(self,control):
        self.events.append('up');self.c.t+=self.release_delay;self.held.discard(control)
        if self.release_error:raise self.release_error
    def released(self,control):
        self.events.append('released')
        if control in self.held:raise RuntimeError('held')


class ReleaseDeadlineTests(unittest.TestCase):
    def setUp(self):
        self.clock=Clock();self.e=Endpoint(self.clock);self.timing={};self.observed=[];self.captures=[]
    def run_step(self,observe=None,capture=None,sleep=None):
        def default_observe():self.observed.append(self.clock.t)
        def default_capture():self.captures.append((self.clock.t,set(self.e.held)))
        return actual_loop()({'vanilla':self.e},{'actions':{'vanilla':'forward'},'seconds':.1},
            self.clock.now,sleep or self.clock.sleep,observe or default_observe,
            before_release=capture or default_capture,timing=self.timing)
    def assert_released(self):
        self.assertFalse(self.e.held);self.assertEqual(self.e.events.count('up'),1)
    def test_end_reached_before_guards_captures_without_any_observation(self):
        self.e.transport_delay=.1
        out=self.run_step()
        self.assertEqual(self.observed,[]);self.assertEqual(self.timing['held_observations'],0)
        self.assertEqual(self.e.events.count('verify'),2)
        self.assertEqual(self.captures,[(.1,{'forward'})]);self.assertTrue(out['released']);self.assert_released()
    def test_guard_crosses_planned_end_releases_without_late_observer(self):
        self.e.delays=[.144]
        def late():self.observed.append(self.clock.t);self.clock.t+=.208
        out=self.run_step(late)
        self.assertEqual(self.observed,[]);self.assertAlmostEqual(out['wall_seconds'],.144)
        self.assertEqual(self.timing['held_observations'],0);self.assertEqual(len(self.captures),1);self.assert_released()
    def test_recorded_early_observation_then_144ms_guard_skips_208ms_block(self):
        self.e.delays=[0,.055057156]
        def observer():
            self.observed.append(self.clock.t)
            self.clock.t+=.069365668 if len(self.observed)==1 else .208
        out=self.run_step(observer)
        self.assertEqual(len(self.observed),1);self.assertEqual(self.timing['held_observations'],1)
        self.assertAlmostEqual(out['wall_seconds'],.144422824);self.assert_released()
    def test_fast_normal_observations_are_counted_and_capture_once(self):
        self.run_step()
        self.assertGreater(len(self.observed),0);self.assertEqual(self.timing['held_observations'],len(self.observed))
        self.assertEqual(len(self.captures),1);self.assert_released()
    def test_guard_over_350ms_still_fails_before_observer(self):
        self.e.delays=[.351]
        with self.assertRaisesRegex(RuntimeError,'held guard host overrun'):self.run_step()
        self.assertEqual(self.observed,[]);self.assertEqual(self.captures,[]);self.assert_released()
    def test_on_time_started_slow_observer_over_350ms_still_fails(self):
        def slow():self.observed.append(self.clock.t);self.clock.t+=.351
        with self.assertRaisesRegex(RuntimeError,'observation host overrun'):self.run_step(slow)
        self.assertEqual(len(self.observed),1);self.assert_released()
    def test_slow_capture_over_350ms_still_fails_and_releases(self):
        def slow():self.clock.t+=.351
        with self.assertRaisesRegex(RuntimeError,'capture host overrun'):self.run_step(capture=slow)
        self.assert_released()
    def test_capture_failure_still_releases(self):
        def fail():raise ValueError('capture failed')
        with self.assertRaisesRegex(RuntimeError,'capture failed'):self.run_step(capture=fail)
        self.assert_released()
    def test_release_over_350ms_is_fail(self):
        self.e.release_delay=.351
        with self.assertRaisesRegex(RuntimeError,'input through release host overrun'):self.run_step()
        self.assert_released()
    def test_guard_error_is_fail_and_releases(self):
        self.e.guard_error=ValueError('identity changed')
        with self.assertRaisesRegex(RuntimeError,'identity changed'):self.run_step()
        self.assert_released()
    def test_uncertain_press_failure_releases_without_retry(self):
        self.e.press_error=ValueError('uncertain press')
        with self.assertRaisesRegex(RuntimeError,'uncertain press'):self.run_step()
        self.assertEqual(self.e.events.count('down'),1);self.assert_released()
    def test_release_error_stays_fail(self):
        self.e.release_error=ValueError('release failed')
        with self.assertRaisesRegex(RuntimeError,'release failed'):self.run_step()
        self.assert_released()
    def test_backwards_or_nonfinite_clock_stays_fail(self):
        for value in(-1,float('inf'),float('nan')):
            with self.subTest(value=value):
                self.setUp()
                def invalid():self.clock.t=value
                with self.assertRaisesRegex(RuntimeError,'clock invalid/backwards'):self.run_step(invalid)
                self.assert_released()
    def test_stalled_clock_still_exhausts_102_iterations(self):
        with self.assertRaisesRegex(RuntimeError,'input clock stalled'):self.run_step(sleep=lambda _:None)
        self.assertEqual(len(self.observed),102);self.assert_released()
    def test_observer_exception_stays_fail_and_releases(self):
        def fail():raise ValueError('reader failed')
        with self.assertRaisesRegex(RuntimeError,'reader failed'):self.run_step(fail)
        self.assertEqual(self.timing['held_observations'],1);self.assert_released()
    def test_existing_routeflight_cancel_is_before_input_and_observes_nothing(self):
        action=actual_loop();kind=action.__globals__['PP'].RouteFlightBeforeInput
        def cancel():raise kind('observed route flight')
        self.e.pin.role='botA'
        out=action({'botA':self.e},{'actions':{'botA':'forward'},'seconds':.1},
            self.clock.now,self.clock.sleep,lambda:self.fail('no held observer before emission'),
            before_press=cancel,timing=self.timing)
        self.assertTrue(out['cancelled_before_emission']);self.assertEqual(self.timing['held_observations'],0)
        self.assertNotIn('down',self.e.events);self.assertIsNone(self.timing['held_started'])
    def test_existing_routeflight_cancel_outside_allowed_role_is_failure(self):
        action=actual_loop();kind=action.__globals__['PP'].RouteFlightBeforeInput
        def cancel():raise kind('observed route flight')
        with self.assertRaises(RuntimeError):
            action({'vanilla':self.e},{'actions':{'vanilla':'forward'},'seconds':.1},
                self.clock.now,self.clock.sleep,lambda:None,before_press=cancel,timing=self.timing)
        self.assertEqual(self.timing['status'],'FAIL');self.assertNotIn('down',self.e.events)


if __name__=='__main__':unittest.main()
