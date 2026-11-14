"""Focused controller safety cases; no Wine, compiler, Frida or native app."""
import unittest
import struct
from unittest import mock


class ControllerTests(unittest.TestCase):
    def module(self):
        try:
            import win32_instruction_probe_controller as module
        except ImportError:
            self.fail('missing disabled bounded methods controller')
        return module

    def test_disabled_controller_rejects_before_processes_or_runtime_reads(self):
        m=self.module()
        with mock.patch('subprocess.Popen')as process, mock.patch('pathlib.Path.read_text')as read:
            with self.assertRaisesRegex(RuntimeError,'disabled'):m.main('baseline')
            process.assert_not_called();read.assert_not_called()

    def test_close_failure_cannot_skip_normal_native_exit_or_proven_own_worker_reap(self):
        m=self.module();events=[];errors=[]
        def close():events.append('worker_close');raise TimeoutError('bounded RPC')
        def stop():events.append('normal_Q')
        def wait():events.append('native_end');return True
        def reap(ended):events.append(('own_worker_reap',ended))
        m.cleanup(close,stop,wait,reap,errors)
        self.assertEqual(events,['worker_close','normal_Q','native_end',('own_worker_reap',True)])
        self.assertEqual(len(errors),1);self.assertIn('bounded RPC',errors[0])

    def test_live_native_or_failed_wait_never_authorizes_worker_signal(self):
        m=self.module()
        for fail in (False,True):
            calls=[];errors=[]
            def wait():
                if fail:raise TimeoutError('native still owned/live')
                return False
            m.cleanup(lambda:None,lambda:None,wait,lambda ended:calls.append(ended),errors)
            self.assertEqual(calls,[]);self.assertTrue(errors)

    def test_normal_exit_failure_stays_sticky_but_wait_is_still_attempted(self):
        m=self.module();calls=[];errors=[]
        def stop():raise OSError('stdin pipe failed')
        m.cleanup(lambda:None,stop,lambda:(calls.append('wait')or True),
                  lambda ended:calls.append('reap'),errors)
        self.assertEqual(calls,['wait','reap']);self.assertTrue(errors)

    def test_binary_header_gate_rejects_elf_x64_and_dll(self):
        m=self.module()
        for data in (b'\x7fELF'+bytes(1024),bytes(1024)):
            with self.assertRaises(ValueError):m.pe32_base(data)

    def test_own_pe32_header_requires_fixed_base_and_no_dynamic_base(self):
        m=self.module();data=bytearray(512);data[:2]=b'MZ'
        struct.pack_into('<I',data,0x3c,0x80);data[0x80:0x84]=b'PE\0\0'
        struct.pack_into('<H',data,0x84,0x14c);struct.pack_into('<H',data,0x96,2)
        struct.pack_into('<H',data,0x98,0x10b);struct.pack_into('<I',data,0x98+28,0x400000)
        self.assertEqual(m.pe32_base(bytes(data)),0x400000)
        for offset,value in ((0x84,0x8664),(0x96,0x2002),(0x98,0x20b),(0x98+70,0x40)):
            bad=bytearray(data);struct.pack_into('<H',bad,offset,value)
            with self.assertRaises(ValueError):m.pe32_base(bytes(bad))


if __name__=='__main__':unittest.main()
