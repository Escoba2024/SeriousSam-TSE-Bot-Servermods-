"""Batch adaptation tests, including unchanged private strict Trace validation."""
import copy
import hashlib
import importlib.util
import json
from pathlib import Path
import unittest
from unittest.mock import patch

try:
    from tools import first_state_autodrain_session as adapter
except ImportError:
    adapter = None
from tools import first_state_autodrain_protocol as protocol


def packet(events=(), *, enabled=True):
    return dict(enabled=enabled, stop_reason=None if enabled else 'host requested',
                tls_binding={'thread_id': 1}, in_flight=0, identity={'pid': 1},
                events=[e if type(e) is dict else {'kind':'fixture','marker':e} for e in events])


def batch(values, first=1, stop=None, final=None, failed=False):
    rows = []
    for serial, value in enumerate(values, first):
        raw = value if type(value) is bytes else protocol.canonical(value)
        rows.append(dict(serial=serial, raw=raw, sha256=hashlib.sha256(raw).hexdigest(),
            started=10 + serial * .02, finished=10 + serial * .02 + .001,
            archive_offset=serial * 100000, archive_length=len(raw)))
    return dict(captures=rows, stop_serial=stop, final_serial=final,
                reply={'ok':True, 'failed':failed,
                       'captures_attempted': final or (first + len(rows) - 1),
                       'captures_indexed': final or (first + len(rows) - 1)})


class Trace:
    def __init__(self): self.attempts = []; self.events = []
    def consume(self, value):
        self.attempts.append(value)
        if value.get('bad'): raise ValueError('strict packet failure')
        self.events.extend(value['events'])
    def finish(self, external): return {'status':'OBSERVER_TRANSPORT_COMPLETE_ONLY'}


class Ports:
    def __init__(self, batches, barrier): self.batches = list(batches); self.barrier_value = barrier; self.ops = []
    def batch(self, *, next_serial, cleanup=False):
        self.ops.append(('batch', next_serial)); return self.batches.pop(0)
    def barrier(self): self.ops.append('stop'); return self.barrier_value
    def unload(self): self.ops.append('unload'); return {'unloaded':True,'original_verified':True}
    def detach(self): self.ops.append('detach'); return {'detached':True,'original_verified':True}
    def read_regions(self): self.ops.append('regions'); return {str(i):{} for i in range(38)}


class Core:
    def __init__(self, ports):
        self.ports = ports; self.identity = {'pid':1}; self.trace = Trace(); self.errors = []
        self.deadline = 20.; self.loaded = True; self.load_attempted = True; self.connected = True
        self.finished = False; self.clocks = 0; self.guards = 0; self.rows = []; self.clock_value = 10.
    def _clock(self, cleanup=False): self.clocks += 1; return self.clock_value
    def _identity(self): self.guards += 1; return copy.deepcopy(self.identity)
    def _archive(self, value): self.rows.append(copy.deepcopy(value))
    def start(self): pass


class BatchSessionTests(unittest.TestCase):
    def make(self, values, *, stop=1, final=2, validate=lambda value:None):
        self.assertIsNotNone(adapter, 'method-only batch Session missing')
        ports = Ports(values, batch([], stop=stop, final=final))
        core = Core(ports)
        session = adapter.BatchObserverSession(core, validate_packet=validate)
        return session, core, ports

    def test_each_original_packet_once_and_full_guards_around_batch(self):
        s, core, ports = self.make([batch([packet([1]),packet([2])])])
        s.poll()
        self.assertEqual([e['marker'] for e in core.trace.events], [1,2]); self.assertEqual(core.guards, 2)
        self.assertEqual([r['serial'] for r in s.packet_receipts], [1,2])

    def test_malformed_and_semantic_failure_do_not_skip_later_attempts(self):
        good = packet([3]); bad = dict(packet([2]), bad=True)
        s, core, ports = self.make([batch([b'{malformed',bad,good], stop=0, final=3)], stop=0, final=3)
        with self.assertRaises(Exception): s.poll()
        self.assertEqual([r['serial'] for r in s.packet_receipts], [1,2,3])
        self.assertEqual(len(core.trace.attempts), 2)
        self.assertTrue(core.errors)

    def test_fixed_S_cutoff_tail_not_positive_and_complete_coverage(self):
        s, core, ports = self.make([batch([packet([1]),packet([2],enabled=False)],stop=1,final=2)])
        s.mark_cutoff()
        self.assertEqual(s.cutoff_sequence, 1)
        self.assertEqual(s.next_serial, 3)
        result = s.finish()
        self.assertEqual(result['status'], 'AUTODRAIN_OBSERVER_TRANSPORT_COMPLETE_ONLY')
        self.assertEqual((result['stop_serial'],result['final_serial']), (1,2))
        self.assertEqual(ports.ops[-3:], ['unload','detach','regions'])

    def test_stop_is_sent_before_backlog_validation(self):
        s, core, ports = self.make([batch([packet([1]),packet([],enabled=False)],stop=1,final=2)])
        s.mark_cutoff()
        self.assertEqual(ports.ops[0], 'stop')

    def test_stop_admission_precedes_slow_full_parent_guard(self):
        s, core, ports = self.make([batch([packet([1]),packet([],enabled=False)],stop=1,final=2)])
        def slow_guard():
            ports.ops.append('expensive-parent-guard')
            core.clock_value += .5
            return copy.deepcopy(core.identity)
        core._identity = slow_guard
        s.mark_cutoff()
        self.assertEqual(ports.ops[0], 'stop')
        self.assertLess(ports.ops.index('stop'), ports.ops.index('expensive-parent-guard'))

    def test_moving_S_missing_serial_reversed_archive_and_worker_failure_fail(self):
        for mode in ('movingS','gap','archive','worker'):
            first = batch([packet([1])],stop=1)
            second = batch([packet([],enabled=False)],first=2,stop=1,final=2)
            if mode == 'movingS': second['stop_serial'] = 2
            if mode == 'gap': second['captures'][0]['serial'] = 3
            if mode == 'archive': second['captures'][0]['archive_offset'] = 0
            if mode == 'worker': second['reply']['failed'] = True
            with self.subTest(mode=mode):
                s, core, ports = self.make([first,second]); s.poll()
                with self.assertRaises(Exception): s.poll()
                self.assertTrue(core.errors)

    def test_guard_and_raw_metadata_failure_sticky_cleanup_still_attempted(self):
        s, core, ports = self.make([batch([packet([],enabled=False)],stop=0,final=1)],stop=0,final=1)
        def drift(): raise RuntimeError('host identity drift')
        core._identity = drift
        with self.assertRaises(Exception): s.poll()
        result = s.finish()
        self.assertEqual(result['status'], 'FAIL')
        self.assertIn('unload', ports.ops); self.assertIn('detach', ports.ops)
        self.assertTrue(s.packet_receipts)

    def test_incomplete_F_and_unload_error_never_qualify(self):
        s, core, ports = self.make([batch([],stop=0,final=1)],stop=0,final=1)
        core.clock_value = 20.
        result = s.finish()
        self.assertEqual(result['status'], 'FAIL')
        self.assertIn('detach', ports.ops)

    def test_actual_unchanged_private_trace_and_full_restore_are_reused(self):
        self.assertIsNotNone(adapter, 'method-only batch Session missing')
        root = Path('/srv/tse-a1-first-state-method-monitor-disabled-20261115/method-api/vendor/observer')
        spec = importlib.util.spec_from_file_location('autodrain_actual_policy', root/'observer_policy.py')
        policy = importlib.util.module_from_spec(spec); spec.loader.exec_module(policy)
        values = json.loads(Path('/srv/tse-a1-first-state-respawn-completion-20261112/successor/tests/valid-stream.json').read_text())
        s, core, ports = self.make([batch(values,stop=1,final=len(values))], final=len(values), validate=policy.validate_packet)
        core.identity = values[0]['identity']; core.trace = policy.TraceValidator(core.identity)
        ports.read_regions = lambda:policy.expected_restore_regions(core.identity)
        result = s.finish()
        self.assertEqual(result['status'], 'AUTODRAIN_OBSERVER_TRANSPORT_COMPLETE_ONLY', result['errors'])
        self.assertEqual(result['validated_packets'], len(values))

    def test_last_batch_validation_or_archive_cannot_skip_either_deadline(self):
        for limit in ('absolute','backlog2s'):
            for stage in ('validation','archive'):
                with self.subTest(limit=limit,stage=stage):
                    wall = [100.]
                    s, core, ports = self.make([batch([packet([1]),packet([],enabled=False)],
                        stop=1,final=2)])
                    def advance():
                        if limit == 'absolute': core.clock_value = core.deadline
                        else: wall[0] += 2.
                    if stage == 'validation':
                        s.validate_packet = lambda value:advance() if value['enabled'] is False else None
                    else:
                        original_archive = core._archive
                        def archive(row):
                            original_archive(row)
                            if row['operation'] == 'batch': advance()
                        core._archive = archive
                    with patch.object(adapter.time,'monotonic',lambda:wall[0]): result = s.finish()
                    self.assertEqual(result['status'],'FAIL')
                    self.assertTrue(result['errors'])
                    self.assertTrue(result['coverage_complete'])
                    self.assertEqual(result['validated_packets'],2)
                    self.assertIn('unload',ports.ops);self.assertIn('detach',ports.ops)
                    self.assertIn('regions',ports.ops)

    def test_last_archive_within_both_original_bounds_remains_complete(self):
        s, core, ports = self.make([batch([packet([1]),packet([],enabled=False)],stop=1,final=2)])
        wall = [100.]; original_archive = core._archive
        def archive(row):
            original_archive(row)
            if row['operation'] == 'batch':
                core.clock_value = core.deadline - .001; wall[0] += 1.999
        core._archive = archive
        with patch.object(adapter.time,'monotonic',lambda:wall[0]): result = s.finish()
        self.assertEqual(result['status'],'AUTODRAIN_OBSERVER_TRANSPORT_COMPLETE_ONLY')


if __name__ == '__main__': unittest.main()
