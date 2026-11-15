"""Fresh-exec interface, wire retention and role-first ownership adversaries."""
import ast
import hashlib
import os
from pathlib import Path
import socket
import tempfile
import unittest
from unittest.mock import patch

from tools import first_state_autodrain_worker as worker
from tools import first_state_autodrain_protocol as protocol


class Child:
    pid = os.getpid()
    returncode = 0
    ended = False
    def poll(self): return 0 if self.ended else None
    def wait(self, timeout): self.ended = True; return 0
    def terminate(self): self.ended = True
    def kill(self): self.ended = True


class Archive:
    def __init__(self): self.rows = []; self.owner = None
    def __call__(self, raw, complete): self.rows.append((bytes(raw), complete))
    def record_owner(self, value): self.owner = value


class ProxyTests(unittest.TestCase):
    def make(self):
        self.assertTrue(hasattr(worker, 'WorkerProxy'), 'binary FreshExec proxy missing')
        left, right = socket.socketpair(); self.addCleanup(left.close); self.addCleanup(right.close)
        archive = Archive(); proxy = worker.WorkerProxy(Child(), left, archive)
        return proxy, right, archive

    def test_raw_before_parse_and_bad_reply_sticky(self):
        proxy, peer, archive = self.make()
        wire = protocol.encode_batch([], request_id=99, stop_serial=None,
                                     final_serial=None, reply=None)
        peer.sendall(wire)
        with self.assertRaises(Exception): proxy.call('batch', next_serial=1)
        self.assertEqual(archive.rows, [(bytes(wire), True)])
        self.assertTrue(proxy.failed)

    def test_whole_2mib_raw_binary_reply_no_base64_or_quote_expansion(self):
        proxy, peer, archive = self.make()
        # Host socket buffer cannot hold2MiB; recv fixture fragments the real
        # bounded frame without creating threads or a runtime observer.
        raw = b'{' + b' ' * (protocol.MAX_PAYLOAD - 2) + b'}'
        row = dict(serial=1, raw=raw, sha256=hashlib.sha256(raw).hexdigest(),
                   started=10., finished=10.001, archive_offset=0, archive_length=len(raw))
        wire = protocol.encode_batch([row], request_id=1, stop_serial=None,
            final_serial=None, reply={'method':'batch','ok':True,'value':None,
                'error':None,'failed':False,'error_count':0,
                'captures_attempted':1,'captures_indexed':1})
        class Channel:
            def settimeout(self, value): pass
            def sendall(self, value): pass
            def recv(self, amount):
                result = bytes(memoryview(wire)[self.offset:self.offset + amount])
                self.offset += len(result); return result
            offset = 0
        proxy.channel = Channel()
        result = proxy.call('batch', next_serial=1)
        self.assertEqual(result['captures'][0]['raw'], raw)
        self.assertEqual(len(archive.rows[0][0]), len(wire))

    def test_parent_timeout_and_roles_first_reap(self):
        proxy, peer, archive = self.make()
        with self.assertRaises(TimeoutError): proxy.call('batch', timeout=.001, next_serial=1)
        self.assertTrue(proxy.failed)
        with self.assertRaises(RuntimeError): proxy.finish_after_roles_closed(roles_closed=False)
        self.assertFalse(proxy.reaped)
        self.assertTrue(proxy.finish_after_roles_closed(roles_closed=True)['reaped'])

    def test_changed_worker_start_rejected_before_stop_ipc(self):
        proxy, peer, archive = self.make()
        with patch.object(worker.legacy, 'start_ticks', return_value=proxy.start_ticks + 1):
            with self.assertRaises(Exception): proxy.call('stop_barrier', cleanup=True)
        self.assertTrue(proxy.failed)
        peer.setblocking(False)
        with self.assertRaises(BlockingIOError): peer.recv(1)
        self.assertEqual(archive.rows, [])

    def test_fresh_exec_owner_before_first_command_and_no_inherited_fds(self):
        self.assertTrue(hasattr(worker, 'WorkerProxy'), 'binary FreshExec proxy missing')
        archive = Archive(); calls = []
        def popen(args, **kwargs): calls.append((args, kwargs)); return Child()
        with patch.object(worker, 'RUNTIME_REVIEWED', True), patch.object(worker.subprocess, 'Popen', popen):
            proxy = worker.WorkerProxy.start('/private/config.json', archive)
        self.addCleanup(proxy.channel.close)
        self.assertEqual(proxy.sequence, 0)
        self.assertEqual(archive.owner['state'], 'UNARMED_NO_COMMAND_SENT')
        self.assertTrue(calls[0][1]['close_fds'])
        self.assertEqual(len(calls[0][1]['pass_fds']), 1)
        self.assertIn('--worker', calls[0][0])

    def test_imports_do_not_load_frida_and_cli_is_disabled(self):
        tree = ast.parse(Path(worker.__file__).read_text())
        self.assertFalse(any(isinstance(n, ast.Import) and
                             any(x.name == 'frida' for x in n.names) for n in ast.walk(tree)))
        self.assertFalse(worker.RUNTIME_REVIEWED)


if __name__ == '__main__': unittest.main()
