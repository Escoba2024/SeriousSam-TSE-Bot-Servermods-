"""Pure close orchestration with fake RPCs; no process, Frida or game memory."""
import unittest
from unittest import mock
import hashlib
from pathlib import Path
import tempfile
import types

import original_damage_collector as module
from original_damage_collector import close_passive


class FakeExports:
    def __init__(self,events,statuses):self.events=events;self.statuses=list(statuses);self.stopped=True
    def drain(self):self.events.append('drain');return dict(records=[])
    def disarm(self):self.events.append('disarm');return {}
    def status(self):
        self.events.append('status');v=self.statuses.pop(0)if len(self.statuses)>1 else self.statuses[0]
        if isinstance(v,Exception):raise v
        return v
    def finishstop(self):self.events.append('finishstop');return dict(stopped=self.stopped,idle=True,detach_errors=[])


class FakeScript:
    def __init__(self,events,statuses):self.events=events;self.exports_sync=FakeExports(events,statuses);self.fail_unload=False
    def unload(self):
        self.events.append('unload')
        if self.fail_unload:raise RuntimeError('synthetic unload')


class FakeSession:
    def __init__(self,events):self.events=events
    def detach(self):self.events.append('detach')


class CloseTests(unittest.TestCase):
    def idle(self,**change):
        row=dict(admission_closed=True,idle=True,in_flight=0,active_records=0,listener_callbacks=0,getter_callbacks=0)
        row.update(change);return row

    def run_close(self,statuses,*,message_error=False,byte_error=False,unload_error=False,stopped=True,clock=None):
        events=[];script=FakeScript(events,statuses);script.fail_unload=unload_error;script.exports_sync.stopped=stopped
        def pin():events.append('pin')
        def verify():
            events.append('verify')
            if byte_error:raise RuntimeError('synthetic Originalbyte mismatch')
            return True
        def messages():
            events.append('messagecheck')
            if message_error:raise RuntimeError('synthetic sticky message error')
        kwargs=dict(sleep=lambda _:None)
        if clock is not None:kwargs['clock']=clock
        result=close_passive(script,FakeSession(events),pin,verify,messages,**kwargs)
        return result,events

    def test_disarm_pending_pair_idle_detach_bytes_before_unload_session(self):
        out,events=self.run_close([self.idle(idle=False,in_flight=1,active_records=1),self.idle()])
        self.assertTrue(out['closed']);self.assertTrue(out['original_bytes_verified']);self.assertTrue(out['detached'])
        self.assertEqual(out['cleanup_errors'],[]);self.assertEqual(len(out['packets']),2)
        order=[x for x in events if x not in('pin','messagecheck')]
        self.assertEqual(order,['drain','disarm','status','status','finishstop','drain','verify','unload','detach'])

    def test_sticky_message_error_does_not_skip_safe_original_restore_and_detach(self):
        out,events=self.run_close([self.idle()],message_error=True)
        self.assertTrue(out['closed']);self.assertTrue(out['original_bytes_verified']);self.assertTrue(out['detached'])
        self.assertTrue(out['cleanup_errors']);self.assertIn('unload',events);self.assertIn('detach',events)

    def test_timeout_during_active_callback_never_unloads_or_detaches(self):
        ticks=iter([0.,.2,.6,1.2,1.4])
        out,events=self.run_close([self.idle(idle=False,getter_callbacks=1)],clock=lambda:next(ticks))
        self.assertFalse(out['closed']);self.assertTrue(out['cleanup_errors'])
        self.assertNotIn('finishstop',events);self.assertNotIn('unload',events);self.assertNotIn('detach',events)

    def test_rpc_failure_or_false_idle_never_triggers_detach(self):
        for status in [RuntimeError('synthetic RPC'),self.idle(in_flight=1)]:
            ticks=iter([0.,.2,1.2,1.4]);out,events=self.run_close([status],clock=lambda:next(ticks))
            self.assertFalse(out['closed']);self.assertTrue(out['cleanup_errors'])
            self.assertNotIn('unload',events);self.assertNotIn('detach',events)

    def test_unconfirmed_hook_detach_or_originalbytes_never_unloads(self):
        for kwargs in [dict(stopped=False),dict(byte_error=True)]:
            out,events=self.run_close([self.idle()],**kwargs)
            self.assertFalse(out['closed']);self.assertTrue(out['cleanup_errors'])
            self.assertNotIn('unload',events);self.assertNotIn('detach',events)

    def test_unload_exception_is_sticky_but_safe_session_detach_still_attempted(self):
        out,events=self.run_close([self.idle()],unload_error=True)
        self.assertFalse(out['closed']);self.assertTrue(out['detached']);self.assertTrue(out['cleanup_errors'])
        self.assertLess(events.index('verify'),events.index('unload'));self.assertLess(events.index('unload'),events.index('detach'))


class OriginalReceiptTests(unittest.TestCase):
    def fixture(self,wrong=False):
        collector=module.Collector.__new__(module.Collector)
        collector.pin_host=mock.Mock();collector.original_receipts=[];collector.journal=mock.Mock()
        collector.reg=dict(pid=17,start_ticks=91,modules={'Engine.dll':dict(base=0x10000),'EntitiesMP.dll':dict(base=0x20000)})
        getter=dict(rva=100,expected=b'one');damage=dict(rva=200,expected=b'two22')
        collector.guards=dict(engine=dict(current_tick=getter,preferred_base=0,image_size=1000),
                              entities=dict(receive_damage=damage,preferred_base=0,image_size=1000))
        collector.policy=types.SimpleNamespace(rebased=lambda guard,*args:guard['expected'])
        memory={0x10000+100:b'one',0x20000+200:b'XXXXX'if wrong else b'two22'}
        collector.reader=types.SimpleNamespace(_read=lambda address,size:memory[address])
        return collector

    def test_full_original_receipt_contains_both_actual_and_expected_hashes(self):
        collector=self.fixture();self.assertTrue(collector.verify_original('before-unload'))
        receipt=collector.original_receipts[0]
        self.assertEqual(receipt['phase'],'before-unload');self.assertTrue(receipt['all_equal'])
        self.assertEqual([row['bytes']for row in receipt['bodies']],[3,5])
        self.assertEqual(receipt['bodies'][0]['expected_sha256'],hashlib.sha256(b'one').hexdigest())
        self.assertEqual(receipt['bodies'][0]['observed_sha256'],hashlib.sha256(b'one').hexdigest())
        collector.journal.assert_called_once_with('full-original-body-compare',receipt=receipt)

    def test_original_mismatch_is_journaled_with_both_bodies_before_failure(self):
        collector=self.fixture(wrong=True)
        with self.assertRaises(RuntimeError):collector.verify_original('before-unload')
        receipt=collector.original_receipts[0]
        self.assertFalse(receipt['all_equal']);self.assertEqual(len(receipt['bodies']),2)
        self.assertNotEqual(receipt['bodies'][1]['observed_sha256'],receipt['bodies'][1]['expected_sha256'])
        collector.journal.assert_called_once_with('full-original-body-compare',receipt=receipt)

    def test_disabled_collector_constructor_never_checks_ownership_or_imports_frida(self):
        owner=mock.Mock()
        with self.assertRaises(RuntimeError):module.Collector({},owner)
        owner.assert_not_called()

    def test_frida_lifecycle_is_called_only_by_specific_worker_collector(self):
        collector=module.Collector.__new__(module.Collector);events=[]
        collector.arm_requested=False;collector.session=None;collector.failed=False;collector.reg=dict(pid=17)
        collector.registry=dict(arm=dict(pid=17));collector.report={}
        collector.check=lambda:events.append('check');collector.pin_host=lambda:events.append('pin')
        collector.verify_original=lambda phase:events.append('full-original-before-attach')
        collector.journal=lambda *args,**kwargs:None
        collector.messages=types.SimpleNamespace(on_message=lambda *args:None)
        exports=types.SimpleNamespace(arm=lambda config:(events.append('arm')or dict(armed=True)))
        script=types.SimpleNamespace(on=lambda *args:events.append('message-handler'),load=lambda:events.append('load'),exports_sync=exports)
        session=types.SimpleNamespace(create_script=lambda text:(events.append('create-script')or script))
        device=types.SimpleNamespace(attach=lambda pid:(events.append('attach')or session))
        frida=types.SimpleNamespace(__file__=str(module.FRIDA_PACKAGE/'frida/__init__.py'),
            _frida=types.SimpleNamespace(__file__=str(module.FRIDA_PACKAGE/'frida/_frida.abi3.so')),
            __version__='17.26.2',get_local_device=lambda:device)
        with tempfile.TemporaryDirectory()as directory:
            collector.frozen=Path(directory);(collector.frozen/'damage_readonly.js').write_text('synthetic mock-only source')
            with mock.patch.dict(module.sys.modules,frida=frida):out=collector.arm()
        self.assertTrue(out['arm_result']['armed']);self.assertTrue(collector.arm_requested)
        self.assertEqual([x for x in events if x not in('pin','check')],
                         ['full-original-before-attach','attach','create-script','message-handler','load','arm'])


if __name__=='__main__':unittest.main()
