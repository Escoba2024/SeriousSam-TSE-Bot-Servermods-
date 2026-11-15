"""Disabled autonomous capture components; no Frida imports or runtime on import.

The single worker loop and native adapter are separate from the tested byte
index/journal/pump. This file never changes observer packet semantics.
"""
import hashlib
import json
import math
import os
from pathlib import Path
import select
import socket
import subprocess
import sys
import time

try:
    from . import first_state_autodrain_protocol as protocol
    from . import first_state_method_transport as legacy
except ImportError:
    import first_state_autodrain_protocol as protocol
    import first_state_method_transport as legacy

RUNTIME_REVIEWED = False
require = protocol.require


class WorkerProxy(legacy.WorkerProxy):
    """Fresh own exec and inherited roles-first reap; explicit binary batch RPC.

    Complete wirebytes are archived before metadata/observer parsing. A failed
    complete frame is retained for the Session's later validation attempt.
    """
    METHODS = {'connect', 'load', 'arm', 'batch', 'stop_barrier', 'unload', 'detach'}

    def __init__(self, process, channel, archive_wire):
        super().__init__(process, channel, archive_wire)
        self.next_serial = 1; self.failed_wire = None

    @classmethod
    def start(cls, config_path, archive_wire):
        require(RUNTIME_REVIEWED, 'disabled autonomous method worker')
        a, b = socket.socketpair(); process = None
        try:
            process = subprocess.Popen([sys.executable, str(Path(__file__).resolve()),
                '--worker', str(config_path), str(b.fileno())], pass_fds=(b.fileno(),),
                close_fds=True, stdin=subprocess.DEVNULL, stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL)
            proxy = cls(process, a, archive_wire)
            archive_wire.record_owner({'pid': proxy.pid, 'start_ticks': proxy.start_ticks,
                'state': 'UNARMED_NO_COMMAND_SENT', 'config_path': str(config_path)})
            return proxy
        except BaseException:
            a.close()
            # No command can be sent before return: exact child is still unarmed.
            if process is not None:
                if process.poll() is None:
                    process.terminate()
                    try: process.wait(timeout=1)
                    except subprocess.TimeoutExpired: process.kill(); process.wait(timeout=1)
                else: process.wait(timeout=1)
            raise
        finally: b.close()

    def call(self, method, *, timeout=.1, cleanup=False, **kwargs):
        require(method in self.METHODS, 'autodrain command allowlist')
        require(not self.reaped and (not self.failed or cleanup), 'autodrain sticky/reaped worker')
        require(protocol.finite(timeout) and 0 < timeout <= 3, 'bounded IPC timeout')
        try:
            require(self.process.poll() is None and
                    legacy.start_ticks(self.pid) == self.start_ticks,
                    'own worker PID/start is no longer live')
        except BaseException:
            self.failed = True
            raise
        if method == 'batch':
            require(kwargs.get('next_serial') == self.next_serial, 'proxy capture cursor')
        self.sequence += 1
        command = protocol.canonical({'id': self.sequence, 'method': method, 'kwargs': kwargs}) + b'\n'
        require(len(command) <= 16384, 'autodrain command bound')
        began = time.monotonic(); deadline = began + timeout; wire = None
        row = {'id': self.sequence, 'method': method, 'started': began, 'deadline': deadline}
        self.timings.append(row)
        buffer = bytearray()
        try:
            def remaining():
                left = deadline - time.monotonic()
                if left <= 0: raise TimeoutError('autodrain IPC deadline:' + method)
                self.channel.settimeout(left)
            remaining(); self.channel.sendall(command)
            wanted = protocol.PREFIX.size
            while len(buffer) < wanted:
                remaining()
                chunk = self.channel.recv(min(65536, wanted - len(buffer)))
                require(bool(chunk), 'autodrain worker IPC closed')
                buffer.extend(chunk)
                if len(buffer) == protocol.PREFIX.size:
                    try: wanted = protocol.frame_length(buffer)
                    except BaseException:
                        self.archive_wire(buffer, False); buffer = bytearray(); raise
            wire = buffer
            self.archive_wire(wire, True)  # complete bytes BEFORE JSON/schema parsing
            batch = protocol.decode_batch(wire, request_id=self.sequence,
                                           expected_serial=self.next_serial, views=True)
            reply = batch['reply']
            fields = {'method', 'ok', 'value', 'error', 'failed', 'error_count',
                      'captures_attempted', 'captures_indexed'}
            require(type(reply) is dict and set(reply) == fields and
                    reply['method'] == method and type(reply['ok']) is bool and
                    type(reply['failed']) is bool and
                    all(protocol.integer(reply[k]) for k in
                        ('error_count', 'captures_attempted', 'captures_indexed')) and
                    reply['captures_attempted'] >= reply['captures_indexed'] and
                    (reply['error'] is None or type(reply['error']) is str),
                    'autodrain reply schema/counts')
            require(reply['captures_attempted'] == reply['captures_indexed'] or reply['failed'],
                    'missing capture without sticky failure')
            if batch['captures']: self.next_serial = batch['captures'][-1]['serial'] + 1
            row['ok'] = True
            return batch
        except BaseException as error:
            self.failed = True; row.update(ok=False, error=repr(error))
            if wire is not None: self.failed_wire = wire
            elif buffer:
                try: self.archive_wire(buffer, False)
                except BaseException: pass
            raise
        finally: row['finished'] = time.monotonic()

    def take_failed_wire(self):
        value = self.failed_wire; self.failed_wire = None
        return value


class CaptureJournal:
    """Exclusive bounded raw JSONL journal, before strict semantic parsing.

    Frida returns Python values. JSONEncoder(allow_nan=True) deliberately keeps
    NaN/Infinity invalid JSON tokens so subsequent strict parsing FAILS rather
    than sanitizing them. This is the first encoding, not a Frida wire claim.
    Serial entries point at the exact raw value inside the complete journal row.
    """
    def __init__(self, path):
        self.path = Path(path)
        self.fd = os.open(self.path, os.O_RDWR | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW, 0o600)
        st = os.fstat(self.fd)
        self.identity = (st.st_dev, st.st_ino, st.st_uid, st.st_gid, st.st_mode)
        self.total = 0; self.failed = False

    def _guard(self):
        require(self.fd is not None, 'raw journal closed')
        st = os.stat(self.path, follow_symlinks=False)
        require((st.st_dev, st.st_ino, st.st_uid, st.st_gid, st.st_mode) == self.identity
                and st.st_size == self.total, 'raw journal identity/size changed')

    def _write(self, raw):
        require(self.total + len(raw) <= protocol.MAX_JOURNAL, 'raw journal512MiB bound')
        view = memoryview(raw)
        while view:
            count = os.write(self.fd, view)
            require(count > 0, 'raw journal short write')
            self.total += count; view = view[count:]

    def value(self, operation, value, *, serial=None):
        try:
            self._guard()
            prefix = protocol.canonical({'operation': operation, 'serial': serial})[:-1] + b',"raw":'
            self._write(prefix); offset = self.total
            digest = hashlib.sha256()
            # Stream to disk; do not retain a journal-sized list or sanitized copy.
            for text in json.JSONEncoder(allow_nan=True, separators=(',', ':')).iterencode(value):
                raw = text.encode(); self._write(raw); digest.update(raw)
            length = self.total - offset
            self._write(b'}\n'); os.fsync(self.fd)
            require(0 < length <= protocol.MAX_PAYLOAD, 'raw payload exceeds2MiB; journal retained')
            raw = os.pread(self.fd, length, offset)
            require(len(raw) == length and hashlib.sha256(raw).hexdigest() == digest.hexdigest(),
                    'raw journal readback differs')
            return dict(serial=serial, raw=raw, sha256=digest.hexdigest(),
                        archive_offset=offset, archive_length=length)
        except BaseException:
            self.failed = True
            raise

    def read(self, entry):
        self._guard()
        raw = os.pread(self.fd, entry['archive_length'], entry['archive_offset'])
        require(len(raw) == entry['archive_length'] and
                hashlib.sha256(raw).hexdigest() == entry['sha256'], 'archived capture changed')
        return raw

    def read_into(self, entry, target):
        self._guard()
        require(len(target) == entry['archive_length'], 'capture target size')
        filled = 0
        while filled < len(target):
            count = os.preadv(self.fd, [target[filled:]], entry['archive_offset'] + filled)
            require(count > 0, 'capture journal short read')
            filled += count
        require(hashlib.sha256(target).hexdigest() == entry['sha256'], 'archived capture changed')

    def close(self):
        if self.fd is not None:
            os.close(self.fd); self.fd = None


class JournalCollector(legacy.Collector):
    """Reuse the exact old native binding/region/lifecycle methods, not Frida ABI.

    Only raw journaling and the admission/status/finishstop split differ. The
    old transport/JS/NativeContext sources remain byte-identical and disabled.
    """
    def __init__(self, config, guard):
        super().__init__(config, guard)
        self.journal = CaptureJournal(Path(config['evidence']) / 'observer-rpc.jsonl')
        self._capture_serial = None; self.last_capture = None

    def identity(self):
        self.guard()
        require(not self.ports.messages, 'unexpected Frida message')
        return self.context.guard()

    def raw(self, method, arg=None):
        self.guard()
        exports = self.ports.script.exports_sync
        value = getattr(exports, method)(arg) if method == 'arm' else getattr(exports, method)()
        try:
            row = self.journal.value('worker-' + method, value, serial=self._capture_serial)
            self.last_capture = row
            if method != 'drain': protocol.strict_json(row['raw'])
        except BaseException as error:
            self.failed = True
            if method not in ('stop', 'status', 'finishstop'): raise
            # Actual safe cleanup acknowledgements must remain available even
            # when journaling fails; failure stays sticky and cannot qualify.
            self.cleanup_errors.append('raw journal:' + repr(error))
        require(not self.ports.messages, 'unexpected Frida message')
        return value

    def capture(self, serial):
        self.last_capture = None; self._capture_serial = serial
        try:
            self.raw('drain')
            require(self.last_capture is not None, 'capture journal missing')
            return self.last_capture
        finally: self._capture_serial = None

    def close_admission(self): return self.raw('stop')
    def status(self): return self.raw('status')
    def finishstop(self):
        result = self.raw('finishstop')
        if type(result) is dict and result.get('stopped') is True:
            self.idle_detached = True
        return result


class DrainPump:
    """Production state machine; injectable collector/clock allow offline tests.

    No schema acceptance is inferred here. Every indexed original packet must
    still be consumed by the unchanged parent TraceValidator, including tails.
    """
    def __init__(self, collector, journal, *, deadline, clock=time.monotonic):
        require(protocol.finite(deadline) and protocol.finite(clock()) and clock() < deadline,
                'original absolute pump deadline')
        self.collector = collector; self.journal = journal; self.clock = clock
        self.deadline = deadline; self.index = None; self.next_capture = None
        self.armed = False; self.stopping = False; self.failed = False; self.errors = []
        self.next_status = None
        self.attempted = 0
        self.expired = False
        self.collector_failure_recorded = False

    def error(self, error):
        self.failed = True
        text = repr(error)
        try: self.journal.value('scheduler-error', {'error': text})
        except BaseException: pass
        if len(self.errors) < 128:
            self.errors.append(text if len(text) <= 2048 else 'error text exceeds2048; raw journal required')

    def collector_failure(self):
        # Legacy cleanup raw() deliberately preserves authentic idle/stop ACKs
        # after archive failure. That allows safe detach, never a lost FAIL.
        if (getattr(self.collector, 'failed', False) or
                getattr(self.collector, 'cleanup_errors', [])) and not self.collector_failure_recorded:
            self.collector_failure_recorded = True
            self.error(RuntimeError('collector sticky error/cleanup raw failure'))

    def arm(self, config):
        require(not self.armed, 'one pump arm')
        require(self.clock() < self.deadline, 'pump expired before arm')
        result = self.collector.arm(config)
        now = self.clock(); self.index = protocol.CaptureIndex(armed_at=now)
        self.armed = True; self.next_capture = now
        return result

    def capture(self):
        started = self.clock(); row = None
        self.attempted += 1
        self.index.attempted = self.attempted
        try:
            self.collector.identity()
            row = self.collector.capture(self.attempted)
        except BaseException as error:
            self.error(error)
        finally:
            try: self.collector.identity()
            except BaseException as error: self.error(error)
            self.collector_failure()
        finished = self.clock()
        if row is not None:
            try:
                self.index.add(serial=row['serial'], offset=row['archive_offset'],
                               length=row['archive_length'], sha256=row['sha256'],
                               started=started, finished=finished)
            except BaseException as error: self.error(error)
            try: protocol.strict_json(row['raw'])
            except BaseException as error: self.error(error)
        self.next_capture = max(started + protocol.TARGET_INTERVAL,
                                finished if finished <= started + protocol.TARGET_INTERVAL
                                else finished + protocol.TARGET_INTERVAL)

    def stop_barrier(self):
        require(self.armed, 'stop before arm')
        if not self.stopping:
            # Freeze before the admission-close RPC; never wait for Parent backlog.
            self.index.close_admission(); self.stopping = True
            self.next_status = self.clock()
            try: self.collector.close_admission()
            except BaseException as error: self.error(error)
            finally: self.collector_failure()
        return self.index.stop_serial

    def _stop_step(self):
        self.next_status = self.clock() + protocol.TARGET_INTERVAL
        try:
            state = self.collector.status()
            fields = {'enabled', 'stop_reason', 'in_flight', 'callbacks', 'getter_callbacks',
                      'active_calls', 'active_damage', 'idle', 'detached'}
            require(type(state) is dict and set(state) == fields, 'cleanup status schema')
            require(all(type(state[k]) is bool for k in ('enabled', 'idle', 'detached')),
                    'cleanup status flags')
            names = ('in_flight', 'callbacks', 'getter_callbacks', 'active_calls', 'active_damage')
            require(all(type(state[k]) is int and 0 <= state[k] <= 8192 for k in names),
                    'cleanup status counts')
            require(state['stop_reason'] is None or type(state['stop_reason']) is str,
                    'cleanup stop reason')
            idle = not state['enabled'] and all(state[k] == 0 for k in names)
            require(state['idle'] == idle, 'cleanup idle inconsistent')
            if idle:
                result = self.collector.finishstop()
                require(result == {'stopped': True, 'stop_reason': 'host requested'},
                        'observer sticky non-host stop')
                self.capture()  # final raw packet after safe detach, still unchanged
                self.index.finish()
        except BaseException as error: self.error(error)
        finally: self.collector_failure()

    def tick(self):
        if not self.armed or self.expired or self.index.final_serial is not None:
            return
        if self.clock() >= self.deadline:
            self.expired = True
            self.error(TimeoutError('original absolute observer deadline'))
            self.stop_barrier()
            return  # no further status/drain after an expired original budget
        if self.clock() >= self.next_capture:
            self.capture()
        if self.failed:
            self.stop_barrier()
        if self.stopping and self.clock() >= self.next_status:
            self._stop_step()

    def batch(self, *, request_id, next_serial, reply=None):
        require(self.index is not None and type(next_serial) is int and
                1 <= next_serial <= self.index.count + 1, 'requested capture serial')
        wire, _ = protocol.encode_indexed_batch(self.index.entries[next_serial - 1:],
            self.journal.read_into, request_id=request_id, stop_serial=self.index.stop_serial,
            final_serial=self.index.final_serial, reply=reply)
        return wire


class NonblockingChannel:
    """One bounded command/reply; fragment/slow peer never makes a blocking call."""
    def __init__(self, channel):
        self.channel = channel; channel.setblocking(False)
        self.input = bytearray(); self.output = None; self.sent = 0; self.eof = False

    @property
    def pending(self):
        return self.output is not None

    def receive(self):
        if b'\n' not in self.input:
            try:
                chunk = self.channel.recv(16385 - len(self.input))
                if not chunk: self.eof = True
                self.input.extend(chunk)
            except BlockingIOError: pass
        require(len(self.input) <= 16384, 'worker command bound')
        if b'\n' not in self.input:
            return None
        raw, _, remaining = self.input.partition(b'\n'); self.input = bytearray(remaining)
        request = protocol.strict_json(raw)
        require(type(request) is dict and set(request) == {'id', 'method', 'kwargs'}
                and type(request['id']) is int and request['id'] > 0
                and type(request['method']) is str and type(request['kwargs']) is dict,
                'worker command schema')
        return request

    def queue(self, data):
        require(not self.pending, 'one bounded pending worker reply')
        require(type(data) in (bytes, bytearray) and len(data) <= protocol.MAX_PACKET, 'worker reply bound')
        self.output = data; self.sent = 0

    def flush(self):
        if not self.pending: return
        try: count = self.channel.send(memoryview(self.output)[self.sent:])
        except BlockingIOError: return
        require(count > 0, 'worker reply short write')
        self.sent += count
        if self.sent == len(self.output): self.output = None; self.sent = 0


class WorkerLoop:
    """One select loop; bounded command/reply buffers, no threads or readline.

    A stop request closes admission even if a previous reply is backpressured.
    At most one small deferred command result is retained, never another batch.
    Captures continue while socket input/output is fragmented or stalled.
    """
    METHODS = {'connect', 'load', 'arm', 'batch', 'stop_barrier', 'unload', 'detach'}

    def __init__(self, channel, pump):
        self.channel = NonblockingChannel(channel); self.pump = pump
        self.last_id = 0; self.deferred = None; self.closed = False

    def _response(self, request, *, value=None, error=None):
        reply = {'method': request['method'], 'ok': error is None,
                 'value': value, 'error': error,
                 'failed': self.pump.failed, 'error_count': len(self.pump.errors)}
        reply.update(captures_attempted=self.pump.attempted,
                     captures_indexed=self.pump.index.count if self.pump.index else 0)
        if request['method'] == 'batch':
            return self.pump.batch(request_id=request['id'],
                                   next_serial=request['kwargs']['next_serial'], reply=reply)
        index = self.pump.index
        return protocol.encode_batch([], request_id=request['id'], reply=reply,
            stop_serial=index.stop_serial if index else None,
            final_serial=index.final_serial if index else None)

    def _execute(self, request):
        require(request['method'] in self.METHODS, 'worker method allowlist')
        method = request['method']; kwargs = request['kwargs']; value = None; error = None
        try:
            require(not self.pump.failed or method in
                    ('batch', 'stop_barrier', 'unload', 'detach'), 'worker sticky failure')
            if method == 'arm':
                require(set(kwargs) == {'config'}, 'arm command fields')
                value = self.pump.arm(kwargs['config'])
            elif method == 'stop_barrier':
                require(not kwargs, 'stop command fields')
                value = {'stop_serial': self.pump.stop_barrier()}
            elif method == 'batch':
                require(set(kwargs) == {'next_serial'}, 'batch command fields')
            else:
                require(not kwargs, 'worker command fields')
                value = getattr(self.pump.collector, method)()
        except BaseException as exception:
            self.pump.error(exception); error = 'worker command failed; raw journal required'
            if self.pump.armed: self.pump.stop_barrier()
        return value, error

    def wait_budget(self):
        wait = protocol.TARGET_INTERVAL
        if self.pump.armed and not self.pump.expired and self.pump.index.final_serial is None:
            wait = min(wait, max(0., self.pump.next_capture - self.pump.clock()))
        return wait

    def step(self, *, timeout=None):
        self.pump.tick()
        if self.deferred is not None and not self.channel.pending:
            request, value, error = self.deferred
            self.channel.queue(self._response(request, value=value, error=error))
            self.deferred = None
        wait = self.wait_budget()
        if timeout is not None: wait = min(wait, max(0., timeout))
        readable = [] if self.deferred is not None else [self.channel.channel]
        ready, writable, _ = select.select(readable,
            [self.channel.channel] if self.channel.pending else [], [], wait)
        if writable: self.channel.flush()
        if ready or b'\n' in self.channel.input:
            request = self.channel.receive()
            if self.channel.eof:
                self.closed = True
                if self.pump.armed: self.pump.stop_barrier()
            if request is not None:
                require(request['id'] == self.last_id + 1, 'worker command sequence')
                self.last_id = request['id']
                if self.channel.pending and request['method'] != 'stop_barrier':
                    self.deferred = (request, None, 'overlapping command while reply pending')
                    self.pump.error(protocol.ProtocolError('overlapping worker command'))
                    if self.pump.armed: self.pump.stop_barrier()
                else:
                    value, error = self._execute(request)
                    if self.channel.pending: self.deferred = (request, value, error)
                    else: self.channel.queue(self._response(request, value=value, error=error))
        self.pump.tick()


def worker(config_path, fd):
    """Root-gated FreshExec entry only; never called by offline imports/tests."""
    require(RUNTIME_REVIEWED, 'disabled autonomous method worker')
    path = Path(config_path).resolve(strict=True)
    require(path.stat().st_mode & 0o077 == 0 and not Path(config_path).is_symlink(),
            'private config mode/path')
    require(path.stat().st_size <= protocol.MAX_PAYLOAD, 'worker config bound')
    config = protocol.strict_json(path.read_bytes())
    root = Path(config['controller_root']).resolve(strict=True)
    require(root == Path(__file__).resolve().parent, 'worker controller root changed')
    manifest = protocol.strict_json((root / 'source-manifest.json').read_bytes())
    require(manifest.get('runtime_reviewed') is True, 'disabled worker manifest')
    for source, digest in manifest['runtime_dependencies'].items():
        require(hashlib.sha256(Path(source).read_bytes()).hexdigest() == digest,
                'worker source pin:' + source)
    for name in ('first_state_autodrain_worker.py', 'first_state_autodrain_protocol.py',
                 'first_state_method_transport.py', 'native_first_state.py',
                 'vendor/observer/observer.js', 'original_damage_worker.py'):
        require(str(root / name) in manifest['runtime_dependencies'], 'worker dependency:' + name)
    legacy.ownership_gate(config)
    collector = JournalCollector(config, lambda: legacy.ownership_gate(config))
    pump = DrainPump(collector, collector.journal, deadline=config['observer_deadline'])
    channel = socket.socket(fileno=fd); loop = WorkerLoop(channel, pump)
    try:
        while not loop.closed:
            loop.step()
    except BaseException as error:
        pump.error(error)
        if pump.armed: pump.stop_barrier()
        raise
    finally:
        # May still block on Frida internally. Parent IPC is bounded and its
        # normal role cleanup is independent; inherited reap follows role close.
        try:
            if pump.armed and not pump.expired:
                pump.stop_barrier()
                while pump.index.final_serial is None and time.monotonic() < pump.deadline:
                    pump.tick(); time.sleep(protocol.TARGET_INTERVAL)
            if collector.idle_detached:
                try: collector.unload()
                finally: collector.detach()
        finally:
            collector.context.close(); collector.journal.close(); channel.close()


if __name__ == '__main__':
    require(len(sys.argv) == 4 and sys.argv[1] == '--worker', 'internal worker arguments')
    worker(sys.argv[2], int(sys.argv[3]))
