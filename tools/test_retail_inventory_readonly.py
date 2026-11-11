"""Portable guard/decoder tests; synthetic memory is not a native qualification."""
import hashlib
import os
from pathlib import Path
import struct
import tempfile
import unittest
from unittest.mock import patch

import retail_inventory_readonly as r


class Memory:
    def __init__(self):
        self.data = bytearray(0x80000)
        self.calls = 0

    def put(self, address, fmt, *values):
        struct.pack_into('<' + fmt, self.data, address, *values)

    def __call__(self, address, size):
        self.calls += 1
        if address < 0x10000 or address + size > len(self.data):
            raise r.EvidenceError('unmapped')
        return bytes(self.data[address:address + size])


def fixture():
    m = Memory()
    # Engine base is an arbitrary synthetic address; the global is relocated.
    base = -0x1ed6a4
    m.put(0x20000, 'I', 0x21000)
    m.put(0x21020, 'I', 0x22000)
    m.put(0x22004, 'I', 0x23000)
    m.put(0x2204c, 'f', 42.0)
    for index, slot in enumerate((1, 3, 6, 9)):
        player, weapon = 0x30000 + index * 0x2000, 0x40000 + index * 0x1000
        m.put(0x23000 + slot * 136, 'II', 1, player)
        m.put(player + 0x1c, 'I', 400 + index)
        m.put(player + 0x20, '6f', index, 2, 3, 4, 5, 6)
        m.put(player + 0x8c, 'I', 0x28000)
        m.put(player + 0xcc, 'f', 100 - index)
        m.put(player + 0x36c, 'If', 1 << index, index * 25)
        m.put(player + 0x384, 'I', weapon)
        m.put(player + 0xc14, 'f', 40.0 + index * .05)
        m.put(weapon + 0x1c, 'I', 500 + index)
        m.put(weapon + 0x8c, 'I', 0x28000)
        m.put(weapon + 0xdc, 'iIii', 16, 0x50000 + index * 0x100, 2, 16)
        m.put(weapon + 0xec, 'Iiiiiiiiiii', player, 1, 1, 2 + index, 3 + index,
              1, (3, 19, 2051, 8195)[index], 0, 0, 0, index)
        m.put(0x50000 + index * 0x100, '2i', 0x019200c9, 0x01920007 + index)
    return m, base


class SnapshotTests(unittest.TestCase):
    def test_four_distinct_global_slots_keep_independent_inventory_and_armor(self):
        m, base = fixture()
        result = r.snapshot(m, base, (1, 3, 6, 9))
        self.assertEqual(result['game_tick'], 42)
        self.assertEqual([p['slot'] for p in result['players']], [1, 3, 6, 9])
        self.assertEqual([p['weapons']['owned'] for p in result['players']], [3, 19, 2051, 8195])
        self.assertEqual([p['armor'] for p in result['players']], [0, 25, 50, 75])
        self.assertEqual(result['players'][2]['weapons']['state_stack'], [0x019200c9, 0x01920009])
        self.assertEqual(result['players'][2]['weapons']['current'], 4)
        self.assertEqual(result['players'][2]['weapons']['wanted'], 5)
        self.assertTrue(result['all_selected_present'])

    def test_missing_player_or_weapon_is_explicit_not_last_known_inventory(self):
        m, base = fixture()
        m.put(0x23000 + 3 * 136, 'I', 0)
        m.put(0x34000 + 0x384, 'I', 0)
        result = r.snapshot(m, base, (1, 3, 6, 9))
        self.assertFalse(result['all_selected_present'])
        self.assertEqual(result['players'][1], {'slot': 3, 'present': False})
        self.assertIsNone(result['players'][2]['weapons'])

    def test_same_tick_mutating_ownership_or_spawn_is_rejected(self):
        for address, fmt, value in [(0x40104, 'I', 8195), (0x30c14, 'f', 42.0)]:
            with self.subTest(address=address):
                m, base = fixture()
                seen = set()
                def changing(a, n):
                    if (a, n) in seen:
                        m.put(address, fmt, value)
                    seen.add((a, n))
                    return m(a, n)
                with self.assertRaises(r.EvidenceError):
                    r.snapshot(changing, base, (1, 3, 6, 9))

    def test_tick_boundary_rejects_otherwise_stable_data(self):
        m, base = fixture()
        count = 0
        def changing(a, n):
            nonlocal count
            if a == 0x2204c:
                count += 1
                if count > 1:
                    m.put(a, 'f', 42.05)
            return m(a, n)
        with self.assertRaises(r.EvidenceError):
            r.snapshot(changing, base, (1, 3, 6, 9))

    def test_invalid_ownership_identity_stack_and_numbers_fail_closed(self):
        mutations = [(0x400ec, 'I', 0x32000), (0x4008c, 'I', 0x29000),
                     (0x40010, 'I', 4), (0x30010, 'I', 4),
                     (0x400e4, 'i', 17), (0x400e4, 'i', -1),
                     (0x400dc, 'i', 1), (0x400e0, 'I', 0),
                     (0x40104, 'I', 0xffffffff), (0x400f8, 'i', 15),
                     (0x30370, 'f', float('nan')), (0x300cc, 'f', float('inf'))]
        for address, fmt, value in mutations:
            with self.subTest(address=address, value=value):
                m, base = fixture()
                m.put(address, fmt, value)
                with self.assertRaises(r.EvidenceError):
                    r.snapshot(m, base, (1, 3, 6, 9))
                self.assertLess(m.calls, 100)

    def test_four_unique_valid_slots_required(self):
        for slots in [(), (1,), (0, 0, 1, 2), (-1, 1, 2, 3), (0, 1, 2, 16), (False, 1, 2, 3)]:
            m, base = fixture()
            with self.assertRaises(r.EvidenceError):
                r.snapshot(m, base, slots)
            self.assertEqual(m.calls, 0)

    def test_short_read_cannot_be_interpreted_as_zero(self):
        m, base = fixture()
        with self.assertRaises(r.EvidenceError):
            r.snapshot(lambda a, n: m(a, n)[:-1], base, (1, 3, 6, 9))


class IdentityTests(unittest.TestCase):
    def test_stat_handles_spaces_and_parentheses_and_rejects_pid_reuse(self):
        fields = ['S'] + ['0'] * 18 + ['12345']
        text = '123 (wine (own) process) ' + ' '.join(fields)
        self.assertEqual(r.process_identity(text), (123, 12345))
        r.require_identity(text, (123, 12345))
        for expected in [(124, 12345), (123, 12346), (123, None), (True, 12345)]:
            with self.assertRaises(r.EvidenceError):
                r.require_identity(text, expected)

    def test_mapping_requires_exact_path_inode_device_and_offset_zero(self):
        path = '/fixture/Bin/Engine.dll'
        rows = '600c0000-600d0000 r--p 00000000 08:01 77 ' + path + '\n'
        self.assertEqual(r.module_base(rows, path, 77, (8, 1)), 0x600c0000)
        for bad in [rows.replace(path, path + ' (deleted)'), rows.replace(' 77 ', ' 78 '),
                    rows.replace('08:01', '08:02'), rows.replace('00000000', '00001000'),
                    rows + rows.replace('600c0000-600d0000', '610c0000-610d0000')]:
            with self.assertRaises(r.EvidenceError):
                r.module_base(bad, path, 77, (8, 1))

    def test_hash_check_detects_replaced_file(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / 'pinned.dll'
            path.write_bytes(b'original')
            pin = r.pin_file(path, hashlib.sha256(b'original').hexdigest())
            r.check_file(pin)
            replacement = path.with_suffix('.new')
            replacement.write_bytes(b'original')
            replacement.replace(path)
            with self.assertRaises(r.EvidenceError):
                r.check_file(pin)
            with self.assertRaises(r.EvidenceError):
                r.pin_file(path, '0' * 64)

    def test_memory_reads_must_fit_readable_mapping_and_bound(self):
        maps = '00010000-00012000 rw-p 00000000 00:00 0\n00012000-00013000 ---p 00000000 00:00 0\n'
        r.check_read_range(maps, 0x10000, 8)
        for address, size in [(0, 4), (0x11ffe, 4), (0x12000, 4), (0x10000, 65537), (0x10000, -1)]:
            with self.assertRaises(r.EvidenceError):
                r.check_read_range(maps, address, size)


class ReaderTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.folder = Path(self.temp.name)
        self.root = self.folder / 'fixture' / 'botA'
        (self.root / 'Bin').mkdir(parents=True)
        self.proc_root = self.folder / 'proc'
        self.proc = self.proc_root / '123'
        self.proc.mkdir(parents=True)
        (self.proc / 'cwd').symlink_to(self.root)
        self.stat = '123 (own process) ' + ' '.join(['S'] + ['0'] * 18 + ['12345'])
        (self.proc / 'stat').write_text(self.stat)
        maps = ['00010000-00080000 rw-p 00000000 00:00 0']
        bases = {'Engine.dll': 0x600c0000, 'EntitiesMP.dll': 0x60310000, 'GameMP.dll': 0x10000000}
        for name, base in bases.items():
            path = self.root / 'Bin' / name
            path.write_bytes(name.encode())
            st = path.stat()
            maps.append(f'{base:08x}-{base + 0x240000:08x} r-xp 00000000 '
                        f'{os.major(st.st_dev):02x}:{os.minor(st.st_dev):02x} {st.st_ino} {path}')
        (self.proc / 'maps').write_text('\n'.join(maps))
        m, _ = fixture()
        with (self.proc / 'mem').open('wb') as f:
            f.write(m.data)
            f.seek(0x600c0000 + 0x20d6a4)
            f.write(struct.pack('<I', 0x21000))
            # Independent short Retail instruction excerpts, no game assets.
            for module, offset, value in [('Engine.dll', 0x17020, 'd981cc000000c3'),
                                         ('Engine.dll', 0x16e10, '8b818c000000c3'),
                                         ('Engine.dll', 0xdc8d0, '8b4120d9404cc3'),
                                         ('Engine.dll', 0x103037, '8b86e4000000'),
                                         ('EntitiesMP.dll', 0xe6b90, '8b8184030000c3'),
                                         ('EntitiesMP.dll', 0x10c5d4, '858604010000'),
                                         ('EntitiesMP.dll', 0xed52a, 'd8ae70030000'),
                                         ('EntitiesMP.dll', 0xed46c, 'd8a6140c0000')]:
                f.seek(bases[module] + offset)
                f.write(bytes.fromhex(value))
        for constant, name in [('ENGINE_SHA', 'Engine.dll'), ('ENTITIES_SHA', 'EntitiesMP.dll')]:
            context = patch.object(r, constant, hashlib.sha256(name.encode()).hexdigest())
            context.start()
            self.addCleanup(context.stop)
        context = patch.object(r, 'FIXTURE', self.root.parent)
        context.start()
        self.addCleanup(context.stop)

    def reader(self):
        return r.InventoryReader(123, 12345, self.root,
                                 hashlib.sha256(b'GameMP.dll').hexdigest(),
                                 _proc_root=self.proc_root)

    def test_real_file_boundary_is_read_only_and_all_four_decoded(self):
        import fcntl
        import os
        with self.reader() as reader:
            self.assertEqual(fcntl.fcntl(reader.fd, fcntl.F_GETFL) & os.O_ACCMODE, os.O_RDONLY)
            result = reader.sample((1, 3, 6, 9))
            self.assertEqual(result['players'][3]['weapons']['owned'], 8195)
            self.assertGreater(result['bytes_read'], 0)
        self.assertIsNone(reader.fd)

    def test_pid_reuse_cwd_or_mapping_drift_aborts_after_open(self):
        for change in ('pid', 'cwd', 'mapping', 'module', 'code'):
            with self.subTest(change=change):
                with self.reader() as reader:
                    if change == 'pid':
                        (self.proc / 'stat').write_text(self.stat.replace('12345', '12346'))
                    elif change == 'cwd':
                        (self.proc / 'cwd').unlink()
                        (self.proc / 'cwd').symlink_to(self.root.parent)
                    elif change == 'mapping':
                        original = (self.proc / 'maps').read_text()
                        (self.proc / 'maps').write_text(original.replace('Engine.dll', 'Engine.dll (deleted)'))
                    elif change == 'module':
                        (self.root / 'Bin' / 'GameMP.dll').write_bytes(b'changed')
                    else:
                        with (self.proc / 'mem').open('r+b') as f:
                            f.seek(0x603f6b90)
                            f.write(b'\x90')
                    with self.assertRaises(r.EvidenceError):
                        reader.sample((1, 3, 6, 9))
                # Restore only this synthetic fixture for the next independent case.
                if change == 'pid':
                    (self.proc / 'stat').write_text(self.stat)
                elif change == 'cwd':
                    (self.proc / 'cwd').unlink()
                    (self.proc / 'cwd').symlink_to(self.root)
                elif change == 'mapping':
                    (self.proc / 'maps').write_text(original)
                elif change == 'module':
                    (self.root / 'Bin' / 'GameMP.dll').write_bytes(b'GameMP.dll')

    def test_wrong_fixture_is_rejected_before_process_memory_access(self):
        with self.assertRaises(r.EvidenceError):
            r.InventoryReader(123, 12345, self.folder, '0' * 64, _proc_root=self.proc_root)

    def test_identity_change_during_sample_is_caught_by_final_guard(self):
        with self.reader() as reader:
            original = reader._read
            def read_and_reuse(address, size):
                value = original(address, size)
                if address == 0x40104 or address == 0x400dc:
                    (self.proc / 'stat').write_text(self.stat.replace('12345', '12346'))
                return value
            reader._read = read_and_reuse
            with self.assertRaisesRegex(r.EvidenceError, 'process identity changed'):
                reader.sample((1, 3, 6, 9))


if __name__ == '__main__':
    unittest.main()
