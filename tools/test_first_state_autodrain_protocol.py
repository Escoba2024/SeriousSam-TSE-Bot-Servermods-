"""Executed offline protocol/index tests, not native/Frida qualification."""
import hashlib
import unittest
import tracemalloc
from tools import first_state_autodrain_protocol as protocol

from tools.first_state_autodrain_protocol import (
    CaptureIndex, ProtocolError, decode_batch, encode_batch,
    MAX_PAYLOAD, MAX_ENVELOPE,
)


def raw_packet(size=64):
    # A complete opaque JSON packet; protocol must preserve every byte.
    return b'{"raw":"' + b'x' * (size - 10) + b'"}'


def record(serial, raw=None):
    raw = raw_packet() if raw is None else raw
    return {"serial": serial, "raw": raw,
            "sha256": hashlib.sha256(raw).hexdigest(),
            "started": 10 + serial * .02, "finished": 10 + serial * .02 + .001,
            "archive_offset": (serial - 1) * 100, "archive_length": len(raw)}


class BatchProtocolTests(unittest.TestCase):
    def test_full_two_mib_packet_is_preserved(self):
        raw = raw_packet(MAX_PAYLOAD)
        wire = encode_batch([record(1, raw)], request_id=7,
                            stop_serial=None, final_serial=None)
        self.assertLessEqual(len(wire), MAX_PAYLOAD + MAX_ENVELOPE)
        batch = decode_batch(wire, request_id=7, expected_serial=1)
        self.assertEqual(batch["captures"], [record(1, raw)])

    def test_payload_is_opaque_even_if_semantically_invalid(self):
        raw = b'not a valid observer packet'
        wire = encode_batch([record(3, raw)], request_id=2,
                            stop_serial=3, final_serial=3)
        batch = decode_batch(wire, request_id=2, expected_serial=3)
        self.assertEqual(batch["captures"][0]["raw"], raw)
        self.assertEqual((batch["stop_serial"], batch["final_serial"]), (3, 3))

    def test_packet_and_batch_payload_oversize_rejected(self):
        for rows in ([record(1, b'x' * (MAX_PAYLOAD + 1))],
                     [record(1, b'x' * MAX_PAYLOAD), record(2)]):
            with self.subTest(lengths=[len(r["raw"]) for r in rows]):
                with self.assertRaises(ProtocolError):
                    encode_batch(rows, request_id=1,
                                 stop_serial=None, final_serial=None)

    def test_serial_gap_duplicate_reverse_rejected(self):
        for serials in ((1, 1), (1, 3), (2, 1)):
            with self.subTest(serials=serials):
                with self.assertRaises(ProtocolError):
                    encode_batch([record(s) for s in serials], request_id=1,
                                 stop_serial=None, final_serial=None)

    def test_wrong_request_start_hash_or_trailing_data_rejected(self):
        wire = encode_batch([record(1)], request_id=8,
                            stop_serial=None, final_serial=None)
        for candidate, request_id, serial in (
                (wire, 9, 1), (wire, 8, 2),
                (wire[:-1] + bytes([wire[-1] ^ 1]), 8, 1),
                (wire + b'x', 8, 1)):
            with self.subTest(request_id=request_id, serial=serial,
                              length=len(candidate)):
                with self.assertRaises(ProtocolError):
                    decode_batch(candidate, request_id=request_id,
                                 expected_serial=serial)

    def test_missing_or_nonfinite_provenance_rejected(self):
        for field, value in (("started", float('nan')), ("archive_offset", -1),
                             ("finished", False), ("archive_length", 0)):
            row = record(1); row[field] = value
            with self.subTest(field=field), self.assertRaises(ProtocolError):
                encode_batch([row], request_id=1, stop_serial=None, final_serial=None)

    def test_production_indexed_encoding_uses_one_wire_buffer(self):
        self.assertTrue(hasattr(protocol, 'encode_indexed_batch'), 'indexed byte-range encoder missing')
        block = b'x' * 8192
        entry = record(1, b'x' * MAX_PAYLOAD)
        entry.pop('raw')
        def read_into(row, target):
            for offset in range(0, len(target), len(block)):
                target[offset:offset + len(block)] = block[:len(target[offset:offset + len(block)])]
        tracemalloc.start()
        try:
            wire, count = protocol.encode_indexed_batch([entry], read_into,
                request_id=1, stop_serial=None, final_serial=None)
            _, peak = tracemalloc.get_traced_memory()
        finally: tracemalloc.stop()
        self.assertIsInstance(wire, bytearray)
        self.assertEqual(count, 1)
        self.assertLess(peak, MAX_PAYLOAD + MAX_ENVELOPE + 512 * 1024)


class CaptureIndexTests(unittest.TestCase):
    def add(self, index, serial, started, finished, *, offset=0, length=64):
        raw = raw_packet(length)
        index.add(serial=serial, offset=offset, length=length,
                  sha256=hashlib.sha256(raw).hexdigest(),
                  started=started, finished=finished)

    def test_stop_and_final_barriers_are_immutable(self):
        index = CaptureIndex(armed_at=10.0)
        self.add(index, 1, 10.02, 10.03)
        self.assertEqual(index.close_admission(), 1)
        self.add(index, 2, 10.04, 10.05, offset=64)
        self.assertEqual(index.close_admission(), 1)
        self.assertEqual(index.finish(), {"stop_serial": 1, "final_serial": 2})
        self.assertEqual(index.finish(), {"stop_serial": 1, "final_serial": 2})
        with self.assertRaises(ProtocolError):
            self.add(index, 3, 10.06, 10.07, offset=128)

    def test_no_first_capture_can_be_fabricated_at_stop(self):
        index = CaptureIndex(armed_at=10.0)
        self.assertEqual(index.close_admission(), 0)
        self.assertEqual(index.finish(), {"stop_serial": 0, "final_serial": 0})

    def test_capture_duration_and_service_gap_are_separate_hard_failures(self):
        for start, finish in ((10.02, 10.120001), (10.100001, 10.11)):
            with self.subTest(start=start, finish=finish):
                index = CaptureIndex(armed_at=10.0)
                with self.assertRaises(ProtocolError):
                    self.add(index, 1, start, finish)
                self.assertTrue(index.failed)

    def test_nonfinite_reversed_time_and_bad_serial_fail_sticky(self):
        for serial, start, finish in ((2, 10.02, 10.03),
                                      (1, float('nan'), 10.03),
                                      (1, 10.02, float('inf')),
                                      (1, 10.03, 10.02)):
            with self.subTest(serial=serial, start=start, finish=finish):
                index = CaptureIndex(armed_at=10.0)
                with self.assertRaises(ProtocolError):
                    self.add(index, serial, start, finish)
                self.assertTrue(index.failed)

    def test_index_bound_does_not_discard_archived_capture(self):
        index = CaptureIndex(armed_at=10.0)
        for serial in range(1, 1025):
            start = 10.0 + serial * .02
            self.add(index, serial, start, start + .001,
                     offset=(serial - 1) * 64)
        with self.assertRaises(ProtocolError):
            self.add(index, 1025, 30.50, 30.501, offset=1024 * 64)
        self.assertEqual(index.count, 1024)
        self.assertTrue(index.failed)
        self.assertEqual(index.finish()['final_serial'], 1025)


if __name__ == '__main__':
    unittest.main()
