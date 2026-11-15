"""Method-only whole-packet batching around the unchanged strict observer core.

No synthetic old ObserverSession result or merged drain packet is produced.
Full Parent guards enclose batches; worker/native/event guards remain separate.
"""
import copy
import hashlib
import time
try:
    from . import first_state_autodrain_protocol as protocol
    from . import first_state_method_transport as legacy_transport
except ImportError:
    import first_state_autodrain_protocol as protocol
    import first_state_method_transport as legacy_transport


class BatchPorts(legacy_transport.LegacyWorkerPorts):
    """Same host archive/identity/reap methods; explicit new binary RPCs only."""
    def command(self, method, *, timeout=.1, cleanup=False, **kwargs):
        value = self.proxy.call(method, timeout=timeout, cleanup=cleanup, **kwargs)
        reply = value['reply']
        protocol.require(not value['captures'], 'control reply unexpectedly contains captures')
        protocol.require(reply['ok'] is True, 'worker control command failed')
        if not cleanup: protocol.require(reply['failed'] is False, 'sticky worker control failure')
        return reply['value']
    def connect(self): return self.command('connect', timeout=3)
    def load(self): return self.command('load', timeout=3)
    def rpc(self, method, config=None):
        protocol.require(method == 'arm', 'old single-packet drain/stop is not a batch API')
        return self.command('arm', timeout=3, config=config)
    def batch(self, *, next_serial, cleanup=False):
        return self.proxy.call('batch', timeout=.1, cleanup=cleanup, next_serial=next_serial)
    def barrier(self): return self.proxy.call('stop_barrier', timeout=2, cleanup=True)
    def failed_batch(self, *, next_serial):
        wire = self.proxy.take_failed_wire()
        if wire is None: return None
        return protocol.decode_batch(wire, request_id=self.proxy.sequence,
                                     expected_serial=next_serial, views=True)
    def unload(self): return self.command('unload', timeout=2, cleanup=True)
    def detach(self): return self.command('detach', timeout=2, cleanup=True)


class BatchObserverSession:
    """Compose the old arm/host/Trace logic; adapt transport and cleanup only."""
    def __init__(self, core, *, validate_packet):
        self.core = core; self.validate_packet = validate_packet; self.ports = core.ports
        self.next_serial = 1; self.stop_serial = None; self.final_serial = None
        self.packet_receipts = []; self.event_counts = []; self.cutoff_sequence = None
        self.last_packet = None; self.last_archive_end = 0; self.last_capture_finish = None
        self.last_capture_start = None; self.finished = False; self.stop_requested = False

    def _error(self, label, error):
        self.core.errors.append(label + ': ' + repr(error))

    def start(self): return self.core.start()

    def _barriers(self, batch):
        for name in ('stop_serial', 'final_serial'):
            value = batch[name]
            protocol.require(value is None or protocol.integer(value), 'invalid ' + name)
            previous = getattr(self, name)
            protocol.require(previous is None or value == previous, 'immutable ' + name + ' moved')
            if value is not None: setattr(self, name, value)
        protocol.require(self.final_serial is None or self.stop_serial is not None and
                         self.final_serial >= self.stop_serial, 'invalid S/F relation')
        self._cutoff()

    def _cutoff(self):
        if self.stop_serial is not None and self.next_serial > self.stop_serial:
            value = self.event_counts[self.stop_serial - 1] if self.stop_serial else 0
            protocol.require(self.cutoff_sequence is None or self.cutoff_sequence == value,
                             'positive event cutoff moved')
            self.cutoff_sequence = value

    def _consume(self, batch):
        try: self._barriers(batch)
        except BaseException as error: self._error('barrier', error)
        reply = batch.get('reply', {})
        if reply.get('ok') is not True or reply.get('failed') is not False:
            self._error('worker', ValueError('sticky worker failure'))
        for row in batch['captures']:
            receipt = {key: value for key, value in row.items() if key != 'raw'}
            receipt.update(attempted=True, accepted=False)
            self.packet_receipts.append(receipt)
            try:
                protocol.require(row['serial'] == self.next_serial, 'capture sequence gap/duplicate')
                self.next_serial += 1  # every serial gets one attempt, even malformed JSON
                protocol.require(row['archive_offset'] >= self.last_archive_end, 'archive range reversed/overlap')
                self.last_archive_end = row['archive_offset'] + row['archive_length']
                protocol.require(protocol.finite(row['started']) and protocol.finite(row['finished']) and
                                 row['finished'] >= row['started'] and
                                 row['finished'] - row['started'] <= .1, 'capture timing bound')
                if self.last_capture_finish is not None:
                    protocol.require(row['started'] >= self.last_capture_finish and
                                     row['started'] - self.last_capture_start <= .1,
                                     'capture service gap/backwards')
                self.last_capture_start = row['started']; self.last_capture_finish = row['finished']
                raw = row['raw']
                protocol.require(len(raw) == row['archive_length'] and
                    hashlib.sha256(raw).hexdigest() == row['sha256'], 'capture raw hash/length')
                # memoryview retains the one wire buffer; parsing needs a bounded
                # temporary bytes value, not a reserialized/normalized substitute.
                value = protocol.strict_json(bytes(raw))
                self.validate_packet(value)  # still attempted after an earlier sticky Trace error
                self.core.trace.consume(value)  # unchanged exact schema/counters/order/life logic
                if self.stop_serial is None or row['serial'] <= self.stop_serial:
                    protocol.require(value.get('enabled') is True and value.get('stop_reason') is None,
                                     'active observation coverage stopped')
                self.last_packet = value
                receipt.update(accepted=True, event_count=len(value['events']))
            except BaseException as error:
                receipt['error'] = repr(error); self._error('capture', error)
            finally:
                if len(self.event_counts) < self.next_serial - 1:
                    self.event_counts.append(len(self.core.trace.events))
        try: self._cutoff()
        except BaseException as error: self._error('cutoff', error)

    def _exchange(self, method, *, cleanup=False):
        failures = []; value = None
        def attempt(label, callback):
            try: return callback()
            except BaseException as error:
                failures.append(label + ': ' + repr(error)); return None
        attempt('clock-before', lambda: self.core._clock(cleanup))
        # STOP is special: send through the already PID/start-bound proxy and
        # worker ownership guard FIRST. Full subprocess-based Parent guards
        # must never leave admission open while they run. Ordinary batches
        # retain full before/after guards; Stop retains the full after guard.
        if method != 'stop_barrier': attempt('identity-before', self.core._identity)
        if failures and not cleanup:
            self.core.errors.extend(failures)
            raise RuntimeError('; '.join(failures))
        try:
            value = (self.ports.barrier() if method == 'stop_barrier' else
                     self.ports.batch(next_serial=self.next_serial, cleanup=cleanup))
        except BaseException as error:
            failures.append('batch RPC: ' + repr(error))
            # A complete raw frame may already have been retained before a
            # reply/host failure. Still attempt its original packets; never
            # relabel the failed RPC or source binding as accepted evidence.
            if hasattr(self.ports, 'failed_batch'):
                value = attempt('retained failed frame', lambda:
                    self.ports.failed_batch(next_serial=self.next_serial))
        # Full Parent guard after every attempted batch, including failed IPC.
        attempt('identity-after', self.core._identity)
        attempt('clock-after', lambda: self.core._clock(cleanup))
        self.core.errors.extend(failures)
        if value is not None: self._consume(value)
        try:
            self.core._archive({'operation': method, 'capture_next': self.next_serial,
                'stop_serial': self.stop_serial, 'final_serial': self.final_serial,
                'failures': failures})  # wire/raw already archived, never duplicate full packets
        except BaseException as error: self._error('batch metadata archive', error)
        # The last packet's semantic work and metadata fsync also consume the
        # immutable observer budget, even if the next collect can return early.
        try:
            if self.core._clock(True) >= self.core.deadline:
                self._error('deadline-after-processing', TimeoutError('original absolute observer deadline'))
        except BaseException as error: self._error('clock-after-processing', error)
        return value

    def poll(self):
        protocol.require(not self.finished and not self.core.errors and self.core.loaded,
                         'sticky/disabled batch session')
        self._exchange('batch')
        if self.core.errors: raise RuntimeError('sticky batch observation failure')
        return {'tls_bound': self.last_packet is not None and self.last_packet['tls_binding'] is not None,
                'in_flight': self.last_packet['in_flight'] if self.last_packet else 0}

    def _stop(self):
        if not self.stop_requested:
            self.stop_requested = True
            self._exchange('stop_barrier', cleanup=True)
        protocol.require(self.stop_serial is not None, 'stop barrier missing')

    def _collect(self, *, final):
        # Original2s cleanup RPC bound becomes a bounded backlog wait, not an
        # extended admission/TTL. Late validation still invalidates the case.
        began = time.monotonic()
        for unused in range(protocol.MAX_CAPTURES + 1):
            # Check again after the preceding consume/archive before success:
            # complete serial coverage does not excuse late validation.
            if time.monotonic() - began >= 2: raise TimeoutError('bounded batch cleanup2s')
            if self.core._clock(True) >= self.core.deadline:
                self._error('deadline', TimeoutError('original absolute observer deadline'))
            target = self.final_serial if final else self.stop_serial
            if target is not None and self.next_serial > target: return
            before = self.next_serial
            value = self._exchange('batch', cleanup=True)
            if value is None: raise RuntimeError('batch retrieval failed; raw journal retained')
            if self.next_serial == before:
                if self.final_serial is not None:
                    raise RuntimeError('final capture coverage incomplete')
                time.sleep(.01)
        raise RuntimeError('bounded capture validation attempts exhausted')

    def mark_cutoff(self):
        protocol.require(self.cutoff_sequence is None and not self.stop_requested, 'cutoff exactly once')
        self.core._clock()
        self._stop()  # admission closes BEFORE backlog validation, even if it is slow
        self._collect(final=False)
        self._cutoff()
        if self.core.errors: raise RuntimeError('sticky cutoff failure')

    def finish(self):
        protocol.require(not self.finished, 'batch cleanup exactly once'); self.finished = True
        cleanup = []; external = None; unloaded = False; detached = False
        def attempt(label, callback):
            row = {'operation': label, 'attempted': True, 'succeeded': False}; cleanup.append(row)
            try: row['result'] = callback(); row['succeeded'] = True
            except BaseException as error: row['error'] = repr(error); self._error(label, error)
            try: self.core._archive(row)
            except BaseException as error: self._error('cleanup archive', error)
        if self.core.load_attempted:
            attempt('stop-barrier', self._stop)
            attempt('all-serials-through-final', lambda: self._collect(final=True))
            def unload():
                nonlocal unloaded
                errors = []
                for callback in (self.core._identity, self.ports.unload, self.core._identity):
                    try:
                        value = callback()
                        if type(value) is dict and value.get('unloaded') is True: unloaded = True
                    except BaseException as error: errors.append(repr(error))
                if errors: raise RuntimeError('; '.join(errors))
            attempt('unload', unload)
        if self.core.connected:
            def detach():
                nonlocal detached
                errors = []
                for callback in (self.core._identity, self.ports.detach, self.core._identity):
                    try:
                        value = callback()
                        if type(value) is dict and value.get('detached') is True: detached = True
                    except BaseException as error: errors.append(repr(error))
                if errors: raise RuntimeError('; '.join(errors))
            attempt('detach', detach)
        def restore():
            nonlocal external
            external = {'schema': 'a1.first-state.external-restore.v1', 'before_identity': None,
                'after_identity': None, 'script_unloaded': unloaded, 'session_detached': detached,
                'prior_errors': list(self.core.errors), 'regions': {}}
            errors = []
            for name, callback in (('before_identity', self.core._identity),
                                   ('regions', self.ports.read_regions), ('after_identity', self.core._identity)):
                try: external[name] = callback()
                except BaseException as error: errors.append(name + ': ' + repr(error))
            self.core._archive({'operation': 'external-restore', 'raw': external, 'errors': errors})
            if errors: raise RuntimeError('; '.join(errors))
            self.core.trace.finish(external)
        attempt('external-restore', restore)
        complete = (self.stop_serial is not None and self.final_serial is not None and
                    self.next_serial == self.final_serial + 1 and
                    len(self.packet_receipts) == self.final_serial and
                    all(r['accepted'] for r in self.packet_receipts))
        if not complete: self._error('coverage', ValueError('serial1..F not fully accepted'))
        events = self.core.trace.events[:self.cutoff_sequence or 0]
        ticks = [event for event in events if event.get('kind') == 'process_game_tick'
                 and event.get('thread_id') == self.core.identity['pid']
                 and event.get('data', {}).get('scope') == 'context']
        enters = {e['call_id'] for e in ticks if e.get('edge') == 'enter'}
        leaves = {e['call_id'] for e in ticks if e.get('edge') == 'leave'}
        return {'schema': 'a1.first-state.autodrain-session.v1',
            'status': 'AUTODRAIN_OBSERVER_TRANSPORT_COMPLETE_ONLY' if not self.core.errors else 'FAIL',
            'qualified': False, 'native_qualified': False, 'first_processed_state_proven': False,
            'errors': list(self.core.errors), 'external_restore': external, 'cleanup': cleanup,
            'stop_serial': self.stop_serial, 'final_serial': self.final_serial,
            'coverage_complete': complete, 'validated_packets': sum(r['accepted'] for r in self.packet_receipts),
            'packet_receipts': self.packet_receipts, 'cutoff_sequence': self.cutoff_sequence,
            'tls_binding': self.last_packet.get('tls_binding') if self.last_packet else None,
            'identity': copy.deepcopy(self.core.identity), 'main_tick_pair_before_cutoff': bool(enters & leaves),
            'observed_callback_kinds_before_cutoff': sorted({e['kind'] for e in events})}


def ObserverSession(identity, config, ports, *, deadline):
    """Runtime factory; exact old strict core/policy imported from pinned APIroot."""
    from observer_session import ObserverSession as OldSession
    from source_loader import observer_policy
    return BatchObserverSession(OldSession(identity, config, ports, deadline=deadline),
                                validate_packet=observer_policy().validate_packet)
