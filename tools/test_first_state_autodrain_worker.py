"""Offline OS/clock fixtures for the production-used autonomous pump."""
import hashlib
import json
from pathlib import Path
import socket
import tempfile
import unittest

from tools.first_state_autodrain_worker import CaptureJournal, DrainPump, NonblockingChannel
from tools import first_state_autodrain_worker as worker
from tools.first_state_autodrain_protocol import ProtocolError, decode_batch


class Clock:
    def __init__(self): self.value = 10.
    def __call__(self): return self.value


class Collector:
    def __init__(self, journal, clock):
        self.journal = journal; self.clock = clock; self.calls = []
        self.active = False; self.idle = True; self.idle_detached = False
        self.duration = 0.; self.value = {'enabled': True, 'events': []}
        self.fail_guard = False; self.identity_calls = 0
    def identity(self):
        self.identity_calls += 1
        if self.fail_guard: raise RuntimeError('own identity changed')
    def connect(self): self.calls.append('connect'); return {'connected': True}
    def load(self): self.calls.append('load'); return {'loaded': True}
    def arm(self, config): self.calls.append('arm'); self.active = True; return {'armed': True}
    def capture(self, serial):
        self.calls.append('drain'); self.clock.value += self.duration
        return self.journal.value('drain', self.value, serial=serial)
    def close_admission(self):
        self.calls.append('stop'); self.active = False
        return {'stopped': False, 'stop_reason': 'host requested'}
    def status(self):
        self.calls.append('status')
        return {'enabled': False, 'stop_reason': 'host requested',
                'in_flight': 0 if self.idle else 1, 'callbacks': 0,
                'getter_callbacks': 0, 'active_calls': 0 if self.idle else 1,
                'active_damage': 0, 'idle': self.idle, 'detached': False}
    def finishstop(self):
        self.calls.append('finishstop'); self.idle_detached = True
        return {'stopped': True, 'stop_reason': 'host requested'}


class PumpTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(); self.addCleanup(self.tmp.cleanup)
        self.clock = Clock(); self.path = Path(self.tmp.name) / 'observer-rpc.jsonl'
        self.journal = CaptureJournal(self.path); self.addCleanup(self.journal.close)
        self.collector = Collector(self.journal, self.clock)
        self.pump = DrainPump(self.collector, self.journal, deadline=25., clock=self.clock)
        self.pump.arm({})

    def test_capture_and_identity_each_side_then_archive_then_delivery(self):
        self.clock.value += .02; self.pump.tick()
        self.assertEqual(self.collector.identity_calls, 2)
        wire = self.pump.batch(request_id=1, next_serial=1)
        row = decode_batch(wire, request_id=1, expected_serial=1)['captures'][0]
        self.assertEqual(json.loads(row['raw']), self.collector.value)
        self.assertEqual(self.path.read_bytes()[row['archive_offset']:
                         row['archive_offset'] + row['archive_length']], row['raw'])
        self.assertEqual(self.path.stat().st_mode & 0o777, 0o600)

    def test_nan_is_journaled_before_fail_and_not_sanitized(self):
        self.collector.value = {'events': [float('nan')]}
        self.clock.value += .02; self.pump.tick()
        self.assertIn(b'NaN', self.path.read_bytes())
        self.assertTrue(self.pump.failed)
        # The final cleanup drain is retained too, rather than discarded after
        # the first failure. Both captures remain invalid strict JSON.
        self.assertEqual(self.pump.index.count, 2)
        rows = decode_batch(self.pump.batch(request_id=1, next_serial=1),
                            request_id=1, expected_serial=1)['captures']
        self.assertTrue(all(b'NaN' in row['raw'] for row in rows))

    def test_stop_freezes_S_immediately_and_tail_through_F_survives(self):
        self.clock.value += .02; self.pump.tick()
        self.collector.idle = False
        self.assertEqual(self.pump.stop_barrier(), 1)
        self.assertFalse(self.collector.active)
        self.clock.value += .02; self.pump.tick()
        self.assertEqual(self.pump.stop_barrier(), 1)
        self.assertIsNone(self.pump.index.final_serial)
        self.collector.idle = True
        self.clock.value += .02; self.pump.tick()
        self.assertTrue(self.collector.idle_detached)
        result = decode_batch(self.pump.batch(request_id=1, next_serial=1),
                              request_id=1, expected_serial=1)
        self.assertEqual(result['stop_serial'], 1)
        self.assertEqual(result['final_serial'], self.pump.index.count)
        self.assertEqual([r['serial'] for r in result['captures']],
                         list(range(1, self.pump.index.count + 1)))
        self.assertLess(self.collector.calls.index('stop'), self.collector.calls.index('finishstop'))

    def test_service_and_capture_overrun_fail_without_limit_change(self):
        for duration, gap in ((.100001, .02), (0, .100001)):
            with self.subTest(duration=duration, gap=gap):
                self.collector.duration = duration; self.clock.value += gap
                self.pump.tick()
                self.assertTrue(self.pump.failed)
                self.assertFalse(self.collector.active)

    def test_guard_failure_stops_admission_and_remains_sticky(self):
        self.collector.fail_guard = True
        self.clock.value += .02; self.pump.tick()
        self.assertTrue(self.pump.failed)
        self.assertFalse(self.collector.active)
        self.collector.fail_guard = False
        self.assertTrue(self.pump.failed)

    def test_raw_write_failure_stops_admission(self):
        self.journal.close()
        self.clock.value += .02; self.pump.tick()
        self.assertTrue(self.pump.failed)
        self.assertFalse(self.collector.active)

    def test_deadline_does_not_reset_at_stop(self):
        self.clock.value = 25.
        self.pump.tick()
        self.assertTrue(self.pump.failed)
        self.assertEqual(self.pump.deadline, 25.)
        self.assertFalse(self.collector.active)

    def test_expired_deadline_is_latched_without_busywait_or_duplicate_journal(self):
        self.clock.value = 25.; self.pump.tick()
        calls = list(self.collector.calls); size = self.path.stat().st_size
        errors = len(self.pump.errors)
        for unused in range(20): self.pump.tick()
        self.assertEqual(self.collector.calls, calls)
        self.assertEqual(self.path.stat().st_size, size)
        self.assertEqual(len(self.pump.errors), errors)
        self.assertTrue(hasattr(worker, 'WorkerLoop'))
        left, right = socket.socketpair()
        self.addCleanup(left.close); self.addCleanup(right.close)
        loop = worker.WorkerLoop(left, self.pump)
        self.assertGreater(loop.wait_budget(), 0)

    def test_replaced_journal_and_oversize_are_rejected_after_preservation(self):
        self.collector.value = {'large': 'x' * (2 * 1024 * 1024)}
        self.clock.value += .02; self.pump.tick()
        self.assertIn(b'large', self.path.read_bytes())
        self.assertTrue(self.pump.failed)

    def test_real_single_loop_services_capture_during_fragmented_request(self):
        self.assertTrue(hasattr(worker, 'WorkerLoop'), 'production single loop missing')
        left, right = socket.socketpair()
        self.addCleanup(left.close); self.addCleanup(right.close)
        loop = worker.WorkerLoop(left, self.pump)
        right.sendall(b'{"id":1,')
        self.clock.value += .02; loop.step(timeout=0)
        self.assertEqual(self.pump.index.count, 1)
        right.sendall(b'"method":"batch","kwargs":{"next_serial":1}}\n')
        self.clock.value += .02; loop.step(timeout=0); loop.step(timeout=0)
        raw = right.recv(16384)
        batch = decode_batch(raw, request_id=1, expected_serial=1)
        self.assertEqual([r['serial'] for r in batch['captures']], [1, 2])

    def test_real_loop_stop_closes_even_while_previous_reply_is_blocked(self):
        self.assertTrue(hasattr(worker, 'WorkerLoop'), 'production single loop missing')
        left, right = socket.socketpair()
        self.addCleanup(left.close); self.addCleanup(right.close)
        left.setsockopt(socket.SOL_SOCKET, socket.SO_SNDBUF, 4096)
        loop = worker.WorkerLoop(left, self.pump)
        loop.channel.queue(b'x' * 200000)
        self.collector.idle = False
        right.sendall(b'{"id":1,"method":"stop_barrier","kwargs":{}}\n')
        loop.step(timeout=0)
        self.assertFalse(self.collector.active)
        self.assertTrue(loop.channel.pending)
        self.assertEqual(self.pump.index.stop_serial, 1)

    def test_buffered_second_stop_command_is_not_stranded_waiting_for_fd(self):
        left, right = socket.socketpair()
        self.addCleanup(left.close); self.addCleanup(right.close)
        loop = worker.WorkerLoop(left, self.pump)
        self.collector.idle = False
        right.sendall(b'{"id":1,"method":"batch","kwargs":{"next_serial":1}}\n'
                      b'{"id":2,"method":"stop_barrier","kwargs":{}}\n')
        loop.step(timeout=0); loop.step(timeout=0)
        self.assertFalse(self.collector.active)


class ChannelTests(unittest.TestCase):
    def test_partial_command_never_blocks_tick_and_slow_parent_never_blocks_write(self):
        left, right = socket.socketpair()
        self.addCleanup(left.close); self.addCleanup(right.close)
        left.setsockopt(socket.SOL_SOCKET, socket.SO_SNDBUF, 4096)
        channel = NonblockingChannel(left)
        right.sendall(b'{"id":1,')
        self.assertIsNone(channel.receive())
        # A pump tick is free to run here; no readline/sendall in the channel.
        right.sendall(b'"method":"batch","kwargs":{}}\n')
        self.assertEqual(channel.receive()['method'], 'batch')
        channel.queue(b'x' * 200000)
        for unused in range(20): channel.flush()
        self.assertTrue(channel.pending)

    def test_command_bound_and_output_bound(self):
        left, right = socket.socketpair()
        self.addCleanup(left.close); self.addCleanup(right.close)
        channel = NonblockingChannel(left)
        right.sendall(b'x' * 16385)
        with self.assertRaises(ProtocolError): channel.receive()
        with self.assertRaises(ProtocolError): channel.queue(b'x' * (2 * 1024 * 1024 + 16385))


if __name__ == '__main__': unittest.main()
