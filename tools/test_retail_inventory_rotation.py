"""Opt-in passive rotation decoding; synthetic memory is never native evidence."""
import hashlib
import inspect
import json
import os
import struct
import unittest
import retail_inventory_readonly as r
import test_retail_inventory_readonly as baseline


class RotationSnapshotTests(unittest.TestCase):
    def diagnostic(self, read, base):
        self.assertIn('rotation_diagnostics', inspect.signature(r.snapshot).parameters,
                      'explicit optional diagnostic mode is required')
        return r.snapshot(read, base, (1, 3, 6, 9), rotation_diagnostics=True)

    def test_default_mode_keeps_original_bytes_and_exact_read_sequence(self):
        m, base = baseline.fixture()
        calls = []
        def read(address, size):
            calls.append((address, size))
            return m(address, size)
        out = r.snapshot(read, base, (1, 3, 6, 9))
        self.assertEqual(hashlib.sha256(json.dumps(out, sort_keys=True).encode()).hexdigest(),
                         '7fafd07a416c7185fa40be834be77f6d38eaf4eb668ce88edc3fb1477b4a1e9f')
        self.assertEqual(hashlib.sha256(json.dumps(calls).encode()).hexdigest(),
                         'a3903666f0f7b8e49f863819188621f079273c923380474e0f173e77cef18649')
        self.assertEqual(len(calls), 121)
        for i in range(4):
            for offset in (0x344, 0xca0, 0xcc4):
                m.put(0x30000 + i * 0x2000 + offset, 'f', float('nan'))
        self.assertEqual(r.snapshot(m, base, (1, 3, 6, 9)), out)

    def test_opt_in_decodes_four_independent_yaws_and_raw_flags(self):
        m, base = baseline.fixture()
        for i in range(4):
            player = 0x30000 + i * 0x2000
            m.put(player + 0xca0, 'f', -3.0 - i)
            m.put(player + 0x344, 'f', .5 + i)
            m.put(player + 0xcc4, 'f', -6.0 - i)
            m.put(player + 0x380, 'I', 0x401 + i)
        out = self.diagnostic(m, base)
        self.assertEqual(out['players'][0]['rotation_diagnostic'],
                         {'last_action_yaw_deg': -3.0, 'relative_view_yaw_deg': .5,
                          'local_action_yaw_deg': -6.0, 'player_flags': 0x401})
        self.assertEqual(out['players'][3]['rotation_diagnostic'],
                         {'last_action_yaw_deg': -6.0, 'relative_view_yaw_deg': 3.5,
                          'local_action_yaw_deg': -9.0, 'player_flags': 0x404})
        self.assertNotIn('first_processed_state_proven', out)

    def test_rotation_exists_without_weapon_and_missing_slot_stays_absent(self):
        m, base = baseline.fixture()
        m.put(0x30384, 'I', 0)
        m.put(0x23000 + 3 * 136, 'I', 0)
        out = self.diagnostic(m, base)
        self.assertIn('rotation_diagnostic', out['players'][0])
        self.assertIsNone(out['players'][0]['weapons'])
        self.assertEqual(out['players'][1], {'slot': 3, 'present': False})

    def test_nonfinite_diagnostic_yaw_is_rejected(self):
        for offset in (0x344, 0xca0, 0xcc4):
            for bad in (float('nan'), float('inf'), float('-inf')):
                with self.subTest(offset=hex(offset), bad=bad):
                    m, base = baseline.fixture()
                    m.put(0x30000 + offset, 'f', bad)
                    with self.assertRaisesRegex(r.EvidenceError, 'nonfinite'):
                        self.diagnostic(m, base)

    def test_second_read_checks_each_new_field_and_tick(self):
        for offset, fmt in ((0x344, 'f'), (0xca0, 'f'), (0xcc4, 'f'), (0x380, 'I')):
            with self.subTest(offset=hex(offset)):
                m, base = baseline.fixture()
                seen = set()
                def changing(address, size):
                    if (address, size) in seen:
                        m.put(0x30000 + offset, fmt, 1)
                    seen.add((address, size))
                    return m(address, size)
                with self.assertRaisesRegex(r.EvidenceError, 'state changed'):
                    self.diagnostic(changing, base)

    def test_mode_rejects_implicit_truthy_values_before_read(self):
        self.assertIn('rotation_diagnostics', inspect.signature(r.snapshot).parameters)
        for value in (1, 'yes', None, []):
            m, base = baseline.fixture()
            with self.subTest(value=value), self.assertRaises(r.EvidenceError):
                r.snapshot(m, base, (1, 3, 6, 9), rotation_diagnostics=value)
            self.assertEqual(m.calls, 0)


class RotationReaderTests(baseline.ReaderTests):
    def setUp(self):
        super().setUp()
        with (self.proc / 'mem').open('r+b') as stream:
            for offset, value in (
                (0x0ee956, 'd8a3a00c0000'), (0x0eea2f, '898ba00c0000'),
                (0x0f03d7, 'd98644030000'), (0x0f049a, '89be44030000'),
                (0x0e3ced, 'd987c40c0000'), (0x0e3cf6, '8d87c40c0000'),
                (0x0ee91e, '8b8380030000'),
            ):
                stream.seek(0x60310000 + offset)
                stream.write(bytes.fromhex(value))

    def diagnostic_reader(self):
        self.assertIn('rotation_diagnostics', inspect.signature(r.InventoryReader).parameters)
        return r.InventoryReader(123, 12345, self.root,
                                 hashlib.sha256(b'GameMP.dll').hexdigest(),
                                 _proc_root=self.proc_root, rotation_diagnostics=True)

    def test_opt_in_real_file_boundary_remains_read_only(self):
        import fcntl
        with self.diagnostic_reader() as reader:
            self.assertEqual(fcntl.fcntl(reader.fd, fcntl.F_GETFL) & os.O_ACCMODE, os.O_RDONLY)
            row = reader.sample((1, 3, 6, 9))['players'][0]
            self.assertEqual(row['rotation_diagnostic']['last_action_yaw_deg'], 0.)

    def test_every_diagnostic_code_guard_is_enforced_on_open(self):
        for offset in (0xee956, 0xeea2f, 0xf03d7, 0xf049a, 0xe3ced, 0xe3cf6, 0xee91e):
            with self.subTest(offset=hex(offset)):
                with (self.proc / 'mem').open('r+b') as stream:
                    stream.seek(0x60310000 + offset)
                    original = stream.read(1)
                    stream.seek(0x60310000 + offset)
                    stream.write(b'\x90')
                try:
                    with self.assertRaisesRegex(r.EvidenceError, 'Retail instructions differ'):
                        self.diagnostic_reader()
                finally:
                    with (self.proc / 'mem').open('r+b') as stream:
                        stream.seek(0x60310000 + offset)
                        stream.write(original)

    def test_optional_fingerprint_drift_after_open_is_rejected(self):
        with self.diagnostic_reader() as reader:
            with (self.proc / 'mem').open('r+b') as stream:
                stream.seek(0x60310000 + 0xf03d7)
                stream.write(b'\x90')
            with self.assertRaisesRegex(r.EvidenceError, 'Retail instructions differ'):
                reader.sample((1, 3, 6, 9))


if __name__ == '__main__':
    unittest.main()
