"""Passive adapter API tests with no Frida import or native attach."""
from pathlib import Path
import tempfile
from types import SimpleNamespace
import unittest
from tools import first_state_autodrain_worker as worker
from tools import first_state_autodrain_protocol as protocol


class NativeAdapterTests(unittest.TestCase):
    def make(self):
        self.assertTrue(hasattr(worker, 'JournalCollector'), 'native journal adapter missing')
        tmp = tempfile.TemporaryDirectory(); self.addCleanup(tmp.cleanup)
        journal = worker.CaptureJournal(Path(tmp.name) / 'observer-rpc.jsonl')
        self.addCleanup(journal.close)
        obj = worker.JournalCollector.__new__(worker.JournalCollector)
        obj.journal = journal; obj.failed = False; obj.cleanup_errors = []
        obj._capture_serial = None; obj.last_capture = None; obj.idle_detached = False
        obj.guard = lambda: True; obj.context = SimpleNamespace(guard=lambda: {'own': True})
        exports = SimpleNamespace(drain=lambda: {'events': []},
            stop=lambda: {'stopped': False, 'stop_reason': 'host requested'},
            status=lambda: {'idle': True},
            finishstop=lambda: {'stopped': True, 'stop_reason': 'host requested'})
        obj.ports = SimpleNamespace(script=SimpleNamespace(exports_sync=exports), messages=[])
        return obj, journal

    def test_capture_exact_journal_then_cleanup_status_and_safe_detach_flag(self):
        obj, journal = self.make()
        row = obj.capture(1)
        self.assertEqual(row['serial'], 1)
        self.assertEqual(row['raw'], b'{"events":[]}')
        self.assertFalse(obj.close_admission()['stopped'])
        self.assertTrue(obj.finishstop()['stopped'])
        self.assertTrue(obj.idle_detached)

    def test_raw_journal_failure_does_not_skip_safe_cleanup_rpc(self):
        obj, journal = self.make(); calls = []
        obj.ports.script.exports_sync.finishstop = lambda: calls.append('finishstop') or {
            'stopped': True, 'stop_reason': 'host requested'}
        journal.close()
        self.assertTrue(obj.finishstop()['stopped'])
        self.assertEqual(calls, ['finishstop'])
        self.assertTrue(obj.idle_detached)
        self.assertTrue(obj.failed)
        self.assertTrue(obj.cleanup_errors)

    def test_nonhost_finish_reason_still_records_actual_idle_detach(self):
        obj, journal = self.make()
        obj.ports.script.exports_sync.finishstop = lambda: {'stopped': True, 'stop_reason': 'TTL'}
        self.assertEqual(obj.finishstop()['stop_reason'], 'TTL')
        self.assertTrue(obj.idle_detached)
        # The pump applies the unchanged exact host-requested acknowledgement;
        # this state only allows safe cleanup, never technical success.

    def test_unexpected_messages_and_wrong_identity_rejected(self):
        obj, journal = self.make(); obj.ports.messages.append({'unexpected': True})
        with self.assertRaises(Exception): obj.identity()
        obj.ports.messages.clear()
        def fail(): raise RuntimeError('identity drift')
        obj.context.guard = fail
        with self.assertRaises(RuntimeError): obj.identity()

    def test_actual_collector_cleanup_journal_faults_are_pump_sticky(self):
        for operation in ('stop','status','finishstop'):
            with self.subTest(operation=operation):
                obj, journal = self.make()
                obj.loaded = True; obj.context.expected = {}
                exports = obj.ports.script.exports_sync
                exports.arm = lambda cfg:{'armed':True}
                exports.status = lambda:{'enabled':False,'stop_reason':'host requested',
                    'in_flight':0,'callbacks':0,'getter_callbacks':0,'active_calls':0,
                    'active_damage':0,'idle':True,'detached':False}
                original = journal.value; injected = []
                def fail_once(name, value, *, serial=None):
                    if name == 'worker-' + operation and not injected:
                        injected.append(name); raise OSError('injected fsync failure')
                    return original(name, value, serial=serial)
                journal.value = fail_once
                clock = [10.]
                pump = worker.DrainPump(obj,journal,deadline=25.,clock=lambda:clock[0])
                pump.arm({}); pump.stop_barrier(); clock[0] += .02; pump.tick()
                self.assertTrue(injected)
                self.assertTrue(obj.idle_detached, 'safe actual finishstop ACK still usable')
                self.assertTrue(pump.failed, 'cleanup Raw failure must reach reply/session')
                self.assertTrue(pump.errors)


if __name__ == '__main__': unittest.main()
