"""Offline tests prepared for the disabled collector; never attach to a process."""
import importlib
import copy
import json
import os
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch


class CollectorPolicyTests(unittest.TestCase):
    def module(self):
        return importlib.import_module('a1_original_input_collector')

    def test_default_gate_prevents_dependencies_and_attach(self):
        m = self.module()
        with tempfile.TemporaryDirectory() as d:
            c = m.Collector(None, {}, Path(d), lambda: True)
            with patch.object(m, 'load_dependencies', side_effect=AssertionError('must not load')):
                with self.assertRaisesRegex(RuntimeError, 'review'):
                    c.arm()
            self.assertIsNone(c.session)
            c.close()
            self.assertTrue(c.closed)

    def test_only_original_vanilla_role_is_accepted(self):
        m = self.module()
        for reg in ({'role': 'server', 'game_sha256': m.ORIGINAL_GAME_SHA},
                    {'role': 'vanilla', 'game_sha256': '0'*64}):
            with self.subTest(reg=reg), self.assertRaises(ValueError):
                m.validate_registry(reg)

    def test_fault_drop_or_unexpected_stop_is_sticky(self):
        m = self.module()
        good = dict(faults=0, dropped=0, detach_errors=[], enabled=True,
                    stop_reason='', in_flight=0, native_qualified=False,
                    game_state_writes=0, records=[])
        m.validate_packet(good)
        for key, value in [('faults',1), ('dropped',1), ('stop_reason','TTL'),
                           ('enabled',False), ('game_state_writes',1)]:
            packet = dict(good); packet[key] = value
            with self.subTest(key=key), self.assertRaises(ValueError):
                m.validate_packet(packet)

    def test_final_packet_requires_zero_inflight_and_restored_hooks(self):
        m = self.module()
        good = dict(faults=0, dropped=0, detach_errors=[], enabled=False,
                    stop_reason='host requested', in_flight=0,
                    native_qualified=False, game_state_writes=0,
                    restored=True, records=[])
        m.validate_packet(good, final=True)
        for key, value in [('in_flight',1), ('restored',False),
                           ('detach_errors',['failure'])]:
            packet = dict(good); packet[key] = value
            with self.subTest(key=key), self.assertRaises(ValueError):
                m.validate_packet(packet, final=True)

    def test_cleanup_attempts_detach_and_original_verification_after_prior_error(self):
        m = self.module(); calls = []
        class Script:
            class Exports:
                def stop(self): calls.append('stop')
                def drain(self):
                    calls.append('drain')
                    return dict(faults=0,dropped=0,detach_errors=[],enabled=False,
                        stop_reason='host requested',in_flight=0,native_qualified=False,
                        game_state_writes=0,records=[],restored=True)
            exports_sync = Exports()
            def unload(self): calls.append('unload')
        class Session:
            def detach(self): calls.append('detach')
        with tempfile.TemporaryDirectory() as d:
            c = m.Collector(None, {}, Path(d), lambda: True)
            c.session = Session(); c.script = Script()
            c.policy = type('Policy', (), {'cleanup_steps': staticmethod(
                lambda steps, errors: self.run_steps(steps, errors))})
            c._host_pin = lambda: calls.append('pin')
            c._record = lambda row: calls.append('journal')
            c.verify_original = lambda: calls.append('verify_original')
            def fail_message():raise ValueError('sticky JS error')
            c.message_guard=type('G',(),{'check':staticmethod(fail_message)})()
            with self.assertRaises(RuntimeError): c.close()
        self.assertIn('unload',calls)
        self.assertIn('detach',calls)
        self.assertEqual(calls[-1], 'verify_original')

    @staticmethod
    def run_steps(steps, errors):
        for label, operation in steps:
            try: operation()
            except BaseException as error: errors.append(label+':'+repr(error))

    def test_source_has_no_load_time_attach_or_input_function(self):
        m = self.module()
        js = Path(m.__file__).with_name('a1_original_input_readonly.js').read_text()
        self.assertNotIn('NativeFunction', js)
        self.assertNotIn('Memory.write', js)
        self.assertNotIn('Interceptor.replace', js)
        self.assertNotIn('send(', js)
        self.assertIn('rpc.exports', js)

    def test_wrong_effective_controls_or_globals_fail_before_input(self):
        m = self.module()
        good = dict(local_slot=0,profile=0,global_smooth=0,source_pointer=0x50000,
                    controls_address=0x60000,axes={})
        for axis,binding in [('x',1),('y',2)]:
            good['axes'][axis]=dict(binding=binding,invert=0,relative=1,smooth=0,
                effective_smooth=0,sensitivity=50,deadzone=0,influence=1)
        arm=dict(source='0x50000',controls='0x60000')
        m.validate_effective(good,(0,.25,0),arm)
        for key in ('profile','global_smooth'):
            bad=copy.deepcopy(good);bad[key]=1
            with self.subTest(key=key),self.assertRaises(ValueError):
                m.validate_effective(bad,(0,.25,0),arm)
        for key in good['axes']['x']:
            bad=copy.deepcopy(good);bad['axes']['x'][key]+=1
            with self.subTest(key=key),self.assertRaises(ValueError):
                m.validate_effective(bad,(0,.25,0),arm)
        with self.assertRaises(ValueError):m.validate_effective(good,(0,.25,1),arm)

    def test_journal_or_read_failure_sticks_and_prevents_input_permission(self):
        m = self.module()
        for fail_at in ('pin','journal'):
            with self.subTest(fail_at=fail_at),tempfile.TemporaryDirectory() as d:
                c=m.Collector(None,{},Path(d),lambda:True)
                def fail():raise OSError('synthetic failure')
                c._pin=fail if fail_at=='pin' else lambda:None
                c._record=lambda row:fail()
                c.message_guard=type('G',(),{'check':lambda self:None})()
                packet=dict(faults=0,dropped=0,game_state_writes=0,native_qualified=False,
                    detach_errors=[],in_flight=0,records=[],enabled=True,stop_reason='')
                c.script=type('S',(),{'exports_sync':type('E',(),{'drain':lambda self:packet})()})()
                with self.assertRaises(OSError):c.before_input(control='look_horizontal',pixels=12)
                self.assertTrue(c.failed)
                with self.assertRaises(ValueError):c.before_input(control='look_horizontal',pixels=12)

    def test_warmup_never_grants_input_before_complete_pair(self):
        m=self.module()
        with tempfile.TemporaryDirectory() as d:
            c=m.Collector(None,{},Path(d),lambda:True)
            c.drain=lambda:dict(ready=False)
            with self.assertRaises(RuntimeError):c.before_input(control='look_horizontal',pixels=12)
            self.assertTrue(c.failed)

    def test_pending_callback_prevents_unload_and_detach_after_bounded_wait(self):
        m=self.module();calls=[]
        with tempfile.TemporaryDirectory() as d:
            c=m.Collector(None,{},Path(d),lambda:True)
            class Exports:
                def stop(self):calls.append('stop')
                def drain(self):return dict(in_flight=1,enabled=False,restored=False)
            c.script=type('S',(),{'exports_sync':Exports(),'unload':lambda self:calls.append('unload')})()
            c.session=type('S',(),{'detach':lambda self:calls.append('detach')})()
            c._host_pin=lambda:None;c._record=lambda row:None
            c.message_guard=type('G',(),{'check':lambda self:None})()
            c.policy=type('P',(),{'cleanup_steps':staticmethod(self.run_steps)})
            with patch.object(m.time,'monotonic',side_effect=[0,2]):
                with self.assertRaisesRegex(RuntimeError,'quiescence timeout'):c.close()
            self.assertNotIn('unload',calls);self.assertNotIn('detach',calls)
            self.assertFalse(c.closed)

    @unittest.skipUnless(os.environ.get('TSE_A1_INPUT_PRIVATE'), 'requires explicit private Original guards')
    def test_real_original_files_pin_six_sites_ten_ranges_and_timer_guards(self):
        import build_a1_input_guards as builder
        m = self.module()
        private = Path(os.environ['TSE_A1_INPUT_PRIVATE'])
        expected = m.checked(private/'original-input-guards.json',m.GUARDS_SHA)
        with tempfile.TemporaryDirectory() as d:
            output=Path(d)/'guards.json'
            receipt=builder.generate(Path('/srv/tse-a1-colt-pitch-analysis-20261112/evidence/static-originals'),output)
            self.assertEqual(receipt['sites_verified'],6)
            self.assertEqual(output.read_bytes(),expected)
        guards=json.loads(expected)
        chain=guards['timer_gate']
        self.assertEqual(chain['schema'],'original107-timer-guard-observation-v1')
        self.assertEqual(chain['network_local_pause_offset'],0x854)
        self.assertEqual(chain['controls_vtable_rva'],0x2156c)
        self.assertEqual(chain['original_getters']['get_local_pause']['va'],0x6019ac30)
        self.assertEqual(chain['original_getters']['is_paused']['rva'],0xdab60)
        self.assertEqual(len(guards['guards']),10)
        for site in guards['sites'].values():
            self.assertEqual(guards['modules'][site['module']]['preferred_base']+site['rva'],
                             site['preferred_va'])
            self.assertTrue(any(g['module']==site['module'] and g['rva']<=site['rva']
                and site['rva']+len(bytes.fromhex(site['entry_bytes']))<=g['rva']+g['length']
                for g in guards['guards']))


if __name__ == '__main__':
    unittest.main()
