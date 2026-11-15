"""Authentic collector ACKs can close the denominator without erasing FAIL."""
import json
from pathlib import Path
import tempfile
from types import SimpleNamespace
import unittest

from tools.first_state_autodrain_worker import CaptureJournal, DrainPump, JournalCollector
from tools.first_state_autodrain_protocol import decode_batch


class FaultStopTests(unittest.TestCase):
    def make(self, reason):
        tmp = tempfile.TemporaryDirectory(); self.addCleanup(tmp.cleanup)
        path = Path(tmp.name)/'observer-rpc.jsonl'
        journal = CaptureJournal(path); self.addCleanup(journal.close)
        obj = JournalCollector.__new__(JournalCollector)
        obj.journal = journal; obj.failed = False; obj.cleanup_errors = []
        obj._capture_serial = None; obj.last_capture = None; obj.idle_detached = False
        obj.loaded = True
        obj.guard = lambda: True; obj.context = SimpleNamespace(guard=lambda: {'own':True},expected={})
        calls = []
        packet = {'enabled':False,'stop_reason':reason,'events':[],
                  'counters':{'faults':1,'dropped':0},'errors':[{'message':reason}]}
        def rpc(name, result):
            calls.append(name); return result
        state = {'enabled':False,'stop_reason':reason,'in_flight':0,'callbacks':0,
                 'getter_callbacks':0,'active_calls':0,'active_damage':0,'idle':True,'detached':False}
        exports = SimpleNamespace(arm=lambda cfg:rpc('arm',{'armed':True}),
            drain=lambda:rpc('drain',packet),
            stop=lambda:rpc('stop',{'stopped':False,'stop_reason':reason}),
            status=lambda:rpc('status',state),
            finishstop=lambda:rpc('finishstop',{'stopped':True,'stop_reason':reason}))
        obj.ports = SimpleNamespace(script=SimpleNamespace(exports_sync=exports),messages=[])
        clock = [10.]
        pump = DrainPump(obj,journal,deadline=25.,clock=lambda:clock[0])
        pump.arm({}); pump.tick(); self.assertEqual(pump.index.count,1)
        pump.stop_barrier(); clock[0]+=.001
        return pump,obj,journal,path,calls,clock,state,exports

    def test_actual_nonhost_ack_finalizes_once_but_every_reason_stays_failure(self):
        for reason in ('fault: Error: bound getter changed','TTL','queue overflow'):
            with self.subTest(reason=reason):
                pump,obj,journal,path,calls,clock,state,exports = self.make(reason)
                pump.tick()
                self.assertTrue(obj.idle_detached)
                self.assertTrue(pump.failed)
                self.assertTrue(any('non-host stop' in error for error in pump.errors))
                self.assertEqual(pump.index.stop_serial,1)
                self.assertEqual(pump.index.final_serial,2)
                wire=pump.batch(request_id=1,next_serial=1)
                batch=decode_batch(wire,request_id=1,expected_serial=1)
                self.assertEqual(batch['stop_serial'],1);self.assertEqual(batch['final_serial'],2)
                self.assertEqual([x['serial']for x in batch['captures']],[1,2])
                self.assertTrue(all(json.loads(x['raw'])['stop_reason']==reason for x in batch['captures']))
                count=len(calls);size=path.stat().st_size;errors=list(pump.errors)
                for unused in range(20): clock[0]+=.02;pump.tick()
                self.assertEqual(len(calls),count);self.assertEqual(path.stat().st_size,size)
                self.assertEqual(pump.errors,errors)
                self.assertEqual(calls.count('finishstop'),1)

    def test_wrong_finishstop_shape_or_changed_reason_never_finalizes(self):
        for bad in ({'stopped':False,'stop_reason':'TTL'},
                    {'stopped':True,'stop_reason':'host requested'},
                    {'stopped':True},
                    {'stopped':True,'stop_reason':'TTL','extra':0}):
            with self.subTest(bad=bad):
                pump,obj,journal,path,calls,clock,state,exports = self.make('TTL')
                exports.finishstop=lambda:bad
                pump.tick();self.assertTrue(pump.failed)
                self.assertIsNone(pump.index.final_serial)
                self.assertEqual(pump.index.count,1)

    def test_active_callback_veto_and_deadline_are_unchanged(self):
        pump,obj,journal,path,calls,clock,state,exports = self.make('fault: getter')
        state.update(in_flight=1,callbacks=1,active_calls=1,idle=False)
        pump.tick();self.assertNotIn('finishstop',calls)
        self.assertFalse(obj.idle_detached);self.assertIsNone(pump.index.final_serial)
        clock[0]=25.;pump.tick();self.assertTrue(pump.expired)
        count=len(calls);pump.tick();self.assertEqual(len(calls),count)

    def test_final_raw_failure_retains_failed_attempt_denominator(self):
        pump,obj,journal,path,calls,clock,state,exports = self.make('fault: getter')
        original=journal.value
        def fail_final(operation,value,*,serial=None):
            if operation=='worker-drain' and serial==2:raise OSError('final fsync failed')
            return original(operation,value,serial=serial)
        journal.value=fail_final
        pump.tick()
        self.assertTrue(pump.failed);self.assertTrue(obj.idle_detached)
        self.assertEqual(pump.index.final_serial,2)
        self.assertEqual(pump.index.attempted,2);self.assertEqual(pump.index.count,1)
        self.assertTrue(obj.failed)

if __name__=='__main__':unittest.main()
