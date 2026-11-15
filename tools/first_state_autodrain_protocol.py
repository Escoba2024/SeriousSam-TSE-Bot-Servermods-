"""Bounded byte framing and capture index, without observer interpretation.

Raw means the worker's first journal JSON encoding of a Frida Python value,
not Frida wire bytes. Framing never parses, sanitizes or re-encodes that value.
The unchanged observer validator must subsequently inspect every packet.
"""
import hashlib
import json
import math
import struct

MAX_PAYLOAD = 2 * 1024 * 1024
MAX_ENVELOPE = 16 * 1024
MAX_PACKET = MAX_PAYLOAD + MAX_ENVELOPE
MAX_CAPTURES = 1024
MAX_JOURNAL = 512 * 1024 * 1024
SERVICE_BOUND = .1
TARGET_INTERVAL = .02
MAGIC = b'FSA1'
PREFIX = struct.Struct('!4sII')
FIELDS = {'serial', 'sha256', 'started', 'finished', 'archive_offset',
          'archive_length', 'offset', 'length'}


class ProtocolError(ValueError):
    pass


def require(value, message):
    if not value:
        raise ProtocolError(message)


def integer(value, minimum=0):
    return type(value) is int and minimum <= value <= MAX_JOURNAL


def finite(value):
    return type(value) in (int, float) and math.isfinite(value)


def canonical(value):
    return json.dumps(value, allow_nan=False, separators=(',', ':')).encode()


def strict_json(raw):
    def reject(value):
        raise ProtocolError('nonfinite JSON: ' + value)
    def pairs(items):
        out = {}
        for key, value in items:
            require(key not in out, 'duplicate JSON key')
            out[key] = value
        return out
    return json.loads(raw, parse_constant=reject, object_pairs_hook=pairs)


def _barriers(stop, final):
    require(stop is None or integer(stop), 'invalid stop serial')
    require(final is None or integer(final), 'invalid final serial')
    require(final is None or stop is not None and final >= stop, 'invalid final barrier')


def _entry(entry, previous, offset, payload_size):
    require(type(entry) is dict and set(entry) == FIELDS, 'capture metadata schema')
    require(integer(entry['serial'], 1) and entry['serial'] == previous + 1,
            'noncontiguous capture serial')
    require(integer(entry['offset']) and entry['offset'] == offset, 'payload offset gap')
    require(integer(entry['length'], 1) and entry['length'] <= MAX_PAYLOAD and
            offset + entry['length'] <= payload_size, 'capture payload bound')
    require(integer(entry['archive_offset']) and
            integer(entry['archive_length'], 1) and
            entry['archive_length'] == entry['length'] and
            entry['archive_offset'] + entry['archive_length'] <= MAX_JOURNAL,
            'capture archive range')
    require(finite(entry['started']) and finite(entry['finished']) and
            entry['finished'] >= entry['started'], 'capture timestamps')
    digest = entry['sha256']
    require(type(digest) is str and len(digest) == 64 and
            all(c in '0123456789abcdef' for c in digest), 'capture hash schema')


def encode_batch(captures, *, request_id, stop_serial, final_serial, reply=None):
    """Convenience encoder for already-owned test/control raw values.

    The production pump uses encode_indexed_batch with preadv directly into
    the wire buffer, never a list of full raw packets.
    """
    require(type(captures) is list and len(captures) <= MAX_CAPTURES, 'bounded capture list')
    entries = []
    for capture in captures:
        require(type(capture) is dict and set(capture) ==
                (FIELDS - {'offset', 'length'}) | {'raw'}, 'capture fields')
        require(type(capture['raw']) is bytes and
                0 < len(capture['raw']) <= MAX_PAYLOAD, 'opaque payload bound')
        entries.append({key: value for key, value in capture.items() if key != 'raw'})
    def read_into(entry, target):
        target[:] = captures[entry['serial'] - captures[0]['serial']]['raw']
    wire, count = encode_indexed_batch(entries, read_into, request_id=request_id,
        stop_serial=stop_serial, final_serial=final_serial, reply=reply)
    require(count == len(captures), 'batch payload/envelope bound')
    return wire


def encode_indexed_batch(entries, read_into, *, request_id, stop_serial, final_serial, reply=None):
    """Select consecutive whole journal ranges, then allocate one wire buffer.

    read_into(entry, writable_memoryview) fills that exact range; the production
    journal uses preadv. Raw values are neither accumulated nor reserialized.
    Envelope and payload independently stop the batch before the next packet.
    """
    require(integer(request_id, 1), 'request ID')
    require(type(entries) is list and len(entries) <= MAX_CAPTURES, 'bounded capture list')
    _barriers(stop_serial, final_serial)
    selected = []; payload_size = 0; previous = None
    def metadata(rows):
        return canonical({'id': request_id, 'captures': rows,
                          'stop_serial': stop_serial, 'final_serial': final_serial, 'reply': reply})
    meta = metadata(selected)
    require(PREFIX.size + len(meta) <= MAX_ENVELOPE, 'batch envelope bound')
    for source in entries:
        require(type(source) is dict and set(source) == FIELDS - {'offset', 'length'},
                'capture fields')
        entry = dict(source, offset=payload_size, length=source['archive_length'])
        if previous is None:
            previous = entry['serial'] - 1 if type(entry['serial']) is int else -1
        _entry(entry, previous, payload_size, payload_size + entry['length'])
        if payload_size + entry['length'] > MAX_PAYLOAD: break
        proposed = metadata(selected + [entry])
        if PREFIX.size + len(proposed) > MAX_ENVELOPE: break
        selected.append(entry); meta = proposed
        payload_size += entry['length']; previous = entry['serial']
    require(selected or not entries, 'one capture cannot fit batch envelope')
    wire = bytearray(PREFIX.size + len(meta) + payload_size)
    wire[:PREFIX.size] = PREFIX.pack(MAGIC, len(meta), payload_size)
    wire[PREFIX.size:PREFIX.size + len(meta)] = meta
    base = PREFIX.size + len(meta)
    for entry in selected:
        target = memoryview(wire)[base + entry['offset']:base + entry['offset'] + entry['length']]
        read_into({key: value for key, value in entry.items() if key not in ('offset', 'length')}, target)
        require(hashlib.sha256(target).hexdigest() == entry['sha256'], 'capture hash differs')
        target.release()
    return wire, len(selected)


def frame_length(prefix):
    require(len(prefix) == PREFIX.size, 'frame prefix length')
    magic, meta, payload = PREFIX.unpack(prefix)
    require(magic == MAGIC and 0 < meta <= MAX_ENVELOPE - PREFIX.size and
            payload <= MAX_PAYLOAD, 'frame prefix bound')
    return PREFIX.size + meta + payload


def decode_batch(wire, *, request_id, expected_serial, views=False):
    require(type(wire) in (bytes, bytearray) and PREFIX.size <= len(wire) <= MAX_PACKET,
            'batch wire bound')
    require(frame_length(wire[:PREFIX.size]) == len(wire), 'frame total length')
    _, meta_size, payload_size = PREFIX.unpack(wire[:PREFIX.size])
    meta = strict_json(wire[PREFIX.size:PREFIX.size + meta_size])
    require(type(meta) is dict and set(meta) ==
            {'id', 'captures', 'stop_serial', 'final_serial', 'reply'}, 'batch envelope schema')
    require(type(meta['id']) is int and meta['id'] == request_id, 'batch request ID differs')
    _barriers(meta['stop_serial'], meta['final_serial'])
    require(integer(expected_serial, 1) and type(meta['captures']) is list and
            len(meta['captures']) <= MAX_CAPTURES, 'batch index bound')
    previous = expected_serial - 1; offset = 0; rows = []
    for entry in meta['captures']:
        _entry(entry, previous, offset, payload_size)
        start = PREFIX.size + meta_size + offset
        raw = (memoryview(wire)[start:start + entry['length']] if views
               else wire[start:start + entry['length']])
        require(hashlib.sha256(raw).hexdigest() == entry['sha256'], 'capture bytes differ')
        row = {key: value for key, value in entry.items() if key not in ('offset', 'length')}
        row['raw'] = raw; rows.append(row)
        offset += entry['length']; previous = entry['serial']
    require(offset == payload_size, 'unindexed payload bytes')
    require(meta['final_serial'] is None or previous <= meta['final_serial'],
            'capture after final serial')
    return {'captures': rows, 'stop_serial': meta['stop_serial'],
            'final_serial': meta['final_serial'], 'reply': meta['reply']}


class CaptureIndex:
    """At most1024 small entries; archived packets never accumulate in this index.

    Failure remains sticky, but does not prevent recording later provenance or
    freezing cleanup barriers. It can never qualify a failed capture as success.
    """
    def __init__(self, *, armed_at):
        require(finite(armed_at), 'arm clock')
        self.armed_at = armed_at; self.entries = []; self.failed = False
        self.attempted = 0
        self.stop_serial = None; self.final_serial = None

    @property
    def count(self):
        return len(self.entries)

    def add(self, *, serial, offset, length, sha256, started, finished):
        try:
            if integer(serial, 1): self.attempted = max(self.attempted, serial)
            require(self.final_serial is None, 'capture after final barrier')
            require(self.count < MAX_CAPTURES, 'capture index bound')
            row = dict(serial=serial, archive_offset=offset, archive_length=length,
                       length=length, offset=0, sha256=sha256,
                       started=started, finished=finished)
            _entry(row, self.count, 0, length)
            previous = self.entries[-1] if self.entries else None
            require(started >= (previous['finished'] if previous else self.armed_at),
                    'capture time reversed')
            require(offset >= (previous['archive_offset'] + previous['archive_length']
                               if previous else 0), 'archive range overlap')
            # Record real provenance even if service timing invalidates the case.
            self.entries.append({key: value for key, value in row.items()
                                 if key not in ('offset', 'length')})
            require(finished - started <= SERVICE_BOUND, 'capture duration exceeds100ms')
            require(started - (previous['started'] if previous else self.armed_at)
                    <= SERVICE_BOUND, 'capture service interval exceeds100ms')
        except BaseException:
            self.failed = True
            raise

    def close_admission(self):
        if self.stop_serial is None:
            self.stop_serial = self.count
        return self.stop_serial

    def finish(self):
        self.close_admission()
        if self.final_serial is None:
            self.final_serial = self.attempted
        return {'stop_serial': self.stop_serial, 'final_serial': self.final_serial}
