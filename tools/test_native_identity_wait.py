"""Portable lifecycle tests: backend operations and time are injected, no /proc/runtime."""
import unittest
from native_identity_wait import wait_native_identity, IdentityWaitTimeout, IdentityMismatch


class Clock:
    def __init__(self): self.now = 0.0
    def monotonic(self): return self.now
    def sleep(self, seconds): self.now += seconds


class Backend:
    def __init__(self, identities=(), same=()):
        self.identities = list(identities); self.matches = list(same)
        self.calls = []; self.last = (1234, 5678)
    def identity(self, role, unit):
        self.calls.append(('identity', role, unit))
        value = self.identities.pop(0) if self.identities else self.last
        if isinstance(value, BaseException): raise value
        self.last = value
        return value
    def same(self, identity):
        self.calls.append(('same', identity))
        value = self.matches.pop(0) if self.matches else True
        if isinstance(value, BaseException): raise value
        return value
    def __getattr__(self, name):
        raise AssertionError('forbidden backend operation: ' + name)


class IdentityWaitTests(unittest.TestCase):
    def call(self, backend, clock=None, **kw):
        clock = clock or Clock()
        return wait_native_identity(backend, 'botA', 'own-bota.service',
                                    monotonic=clock.monotonic, sleep=clock.sleep, **kw)

    def test_one_valid_probe_is_not_stability_proof(self):
        b = Backend(); receipt = self.call(b)
        self.assertEqual(receipt.identity, (1234, 5678))
        self.assertGreaterEqual(receipt.stable_samples, 3)
        self.assertGreaterEqual(receipt.stable_seconds, .3)
        self.assertGreaterEqual(receipt.elapsed_seconds, .3)
        self.assertEqual(sum(c[0] == 'identity' for c in b.calls), receipt.attempts)
        self.assertEqual(sum(c[0] == 'same' for c in b.calls), receipt.attempts)
        self.assertTrue(all(c[1:] == ('botA', 'own-bota.service') for c in b.calls if c[0] == 'identity'))

    def test_transient_cwd_assertion_and_disappearance_are_retried_strictly(self):
        b = Backend([AssertionError('cwd'), FileNotFoundError('exec'), ProcessLookupError('pid')])
        try: receipt = self.call(b, timeout=2)
        except Exception as error: self.fail('expected transient was not retried: ' + repr(error))
        self.assertEqual(receipt.identity, (1234, 5678))
        self.assertEqual(receipt.transient_errors, 3)
        self.assertGreaterEqual(receipt.attempts, 6)

    def test_permanently_foreign_cwd_or_cgroup_times_out_with_evidence(self):
        for reason in ('foreign cwd', 'wrong cgroup'):
            b = Backend([AssertionError(reason)] * 100); c = Clock()
            with self.assertRaises(IdentityWaitTimeout) as caught:
                self.call(b, c, timeout=.5, stable_for=.2)
            ev = caught.exception.evidence
            self.assertIsNone(ev['identity'])
            self.assertGreater(ev['attempts'], 1)
            self.assertEqual(ev['transient_errors'], ev['attempts'])
            self.assertIn(reason, ev['last_transient'])
            self.assertGreaterEqual(ev['elapsed_seconds'], .5)
            self.assertLessEqual(c.now, .500001)

    def test_stale_identity_same_false_is_never_adopted(self):
        b = Backend(same=[False])
        with self.assertRaises(IdentityMismatch): self.call(b)
        self.assertEqual(len(b.calls), 2)

    def test_pid_or_start_change_is_terminal_even_if_new_identity_would_stabilize(self):
        for other in ((9999, 5678), (1234, 9999)):
            b = Backend([(1234, 5678), other])
            with self.assertRaises(IdentityMismatch): self.call(b)
            self.assertEqual(sum(c[0] == 'identity' for c in b.calls), 2)

    def test_transient_does_not_erase_original_pid_start_pin(self):
        b = Backend([(1234, 5678), AssertionError('cwd transient'), (1234, 7777)])
        with self.assertRaises(IdentityMismatch): self.call(b)

    def test_transient_restarts_consecutive_stability_period(self):
        b = Backend([(1234, 5678), (1234, 5678), AssertionError('cwd')])
        try: receipt = self.call(b, timeout=2)
        except Exception as error: self.fail('expected retry: ' + repr(error))
        self.assertGreaterEqual(receipt.elapsed_seconds, .6)
        self.assertGreaterEqual(receipt.stable_seconds, .3)
        self.assertGreaterEqual(receipt.stable_samples, 3)
        self.assertEqual(receipt.transient_errors, 1)

    def test_same_disappearance_retries_but_unexpected_errors_propagate(self):
        b = Backend(same=[FileNotFoundError('stat')])
        try: receipt = self.call(b)
        except Exception as error: self.fail('expected stat retry: ' + repr(error))
        self.assertEqual(receipt.transient_errors, 1)
        for exception in (PermissionError('denied'), RuntimeError('broken'), KeyboardInterrupt()):
            for location in ('identity', 'same'):
                b = Backend([exception] if location == 'identity' else (),
                            [exception] if location == 'same' else ())
                with self.assertRaises(type(exception)) as caught: self.call(b)
                self.assertIs(caught.exception, exception)

    def test_malformed_identity_and_non_boolean_same_fail_closed(self):
        for value in (None, (1, 2), (123, 0), (True, 8), (123, True), (123.0, 8), (123, 8, 9), '123:8'):
            with self.subTest(value=value), self.assertRaises(IdentityMismatch):
                self.call(Backend([value]))
        for value in (None, 1, 'yes'):
            with self.subTest(value=value), self.assertRaises(IdentityMismatch):
                self.call(Backend(same=[value]))

    def test_timeout_never_becomes_pass_after_slow_callback(self):
        c = Clock(); b = Backend()
        original = b.identity
        def slow(role, unit):
            c.now += .7
            return original(role, unit)
        b.identity = slow
        with self.assertRaises(IdentityWaitTimeout): self.call(b, c, timeout=.5, stable_for=.2)

    def test_cannot_accumulate_good_samples_across_foreign_intervals(self):
        b = Backend([(1234, 5678), AssertionError('foreign')] * 100)
        with self.assertRaises(IdentityWaitTimeout) as caught:
            self.call(b, timeout=.8, stable_for=.3)
        self.assertEqual(caught.exception.evidence['identity'], (1234, 5678))

    def test_invalid_limits_reject_before_backend_read(self):
        options = [dict(timeout=v) for v in (0, -1, True, float('nan'), float('inf'), 61)]
        options += [dict(stable_for=v) for v in (0, -1, float('nan'), True, 20)]
        options += [dict(interval=v) for v in (0, -1, True, float('inf'))]
        options += [dict(min_samples=v) for v in (0, 1, True, 2.5)]
        for kw in options:
            b = Backend()
            with self.subTest(kw=kw), self.assertRaises(ValueError): self.call(b, **kw)
            self.assertEqual(b.calls, [])


if __name__ == '__main__': unittest.main()
