"""Synthetic memory tests for the opt-in Original controls diagnostic."""
import struct
import unittest
import json
import os
from pathlib import Path
import sys

try:
    import a1_controls_diagnostic as D
except ImportError:
    D = None


class Memory:
    def __init__(self):
        self.bytes = {}
        self.calls = []

    def put(self, address, fmt, *values):
        self.bytes.update({address+i: b for i, b in enumerate(struct.pack('<'+fmt, *values))})

    def __call__(self, address, size):
        self.calls.append((address, size))
        return bytes(self.bytes.get(address+i, 0) for i in range(size))


class ControlsTests(unittest.TestCase):
    def setUp(self):
        self.assertIsNotNone(D, 'Original controls diagnostic missing')

    def fixture(self):
        m = Memory()
        gb, eb, game, inp = 0x60840000, 0x600c0000, 0x30000, 0x50000
        m.put(gb+0x2fba4, 'I', game)
        m.put(eb+0x1f178c, 'I', inp)
        m.put(game+0xfa0, 'iI', 0, 0x60000)
        controls = game+0x2d4
        m.put(controls+0x15c, 'i', 0)
        for axis, bound, last, total, raw in [(4, 1, 1.5, 3., 3.), (3, 2, 0., 0., 0.)]:
            m.put(controls+0x10+36*axis, 'iffiiifff', bound, 50., 0., 0, 1, 0, 2., last, total)
            m.put(inp+0x10+20*bound, 'f', raw)
        return m, gb, eb, controls, inp

    def test_intervention_preserves_every_other_byte_and_is_idempotent(self):
        raw = b'// private profile\r\nAxis "turn l/r" "mouse X" 50 0 NotInverted Relative NotSmooth\r\nGlobalSmoothAxes\r\n'
        expected = raw.replace(b'GlobalSmoothAxes', b'GlobalDontSmoothAxes')
        self.assertEqual(D.disable_global_smoothing(raw), expected)
        self.assertEqual(D.disable_global_smoothing(expected), expected)

    def test_ambiguous_or_missing_global_control_is_rejected(self):
        for raw in [b'', b'GlobalSmoothAxes\nGlobalSmoothAxes\n',
                    b'GlobalSmoothAxes\nGlobalDontSmoothAxes\n']:
            with self.subTest(raw=raw), self.assertRaises(ValueError):
                D.disable_global_smoothing(raw)

    def test_decodes_effective_flags_and_both_axis_histories(self):
        m, gb, eb, controls, inp = self.fixture()
        result = D.snapshot(m, gb, eb, local_slot=0)
        self.assertEqual(result['controls_address'], controls)
        self.assertEqual(result['global_smooth'], 0)
        self.assertEqual(result['axes']['x']['previous_reading'], 1.5)
        self.assertEqual(result['axes']['x']['absolute_reading'], 3.)
        self.assertEqual(result['axes']['x']['engine_reading'], 3.)
        self.assertEqual(result['axes']['x']['effective_smooth'], 0)
        self.assertEqual(result['consistency'], 'two_equal_reads_not_atomic')

    def test_global_or_per_axis_smoothing_is_effective(self):
        for address_kind in ('global', 'axis'):
            m, gb, eb, controls, inp = self.fixture()
            m.put(controls+0x15c if address_kind=='global' else controls+0x10+36*4+0x14, 'i', 1)
            result = D.snapshot(m, gb, eb, local_slot=0)
            self.assertEqual(result['axes']['x']['effective_smooth'], 1)

    def test_changed_second_read_is_fatal_with_raw_evidence(self):
        m, gb, eb, controls, inp = self.fixture()
        address = controls+0x15c
        seen = []
        def read(at, size):
            if at == address:
                seen.append(at)
                if len(seen)==2:
                    m.put(address, 'i', 1)
            return m(at, size)
        with self.assertRaisesRegex(ValueError, 'changed') as caught:
            D.snapshot(read, gb, eb, local_slot=0)
        self.assertTrue(caught.exception.raw_reads)

    def test_invalid_pointer_profile_binding_or_nonfinite_axis_is_fatal(self):
        for mutation in ('pointer', 'profile', 'binding', 'nonfinite'):
            m, gb, eb, controls, inp = self.fixture()
            if mutation=='pointer':
                m.put(gb+0x2fba4, 'I', 0)
            elif mutation=='profile':
                m.put(0x30000+0xfa0, 'i', 8)
            elif mutation=='binding':
                m.put(controls+0x10+36*4, 'i', 2)
            else:
                m.put(controls+0x10+36*4+0x1c, 'f', float('nan'))
            with self.subTest(mutation=mutation), self.assertRaises(ValueError):
                D.snapshot(m, gb, eb, local_slot=0)


@unittest.skipUnless(os.environ.get('TSE_A1_PACKAGE'), 'requires hash-pinned private Original binaries')
class OriginalGuardTests(unittest.TestCase):
    def setUp(self):
        self.assertIsNotNone(D)
        self.package = Path(os.environ['TSE_A1_PACKAGE']).resolve(strict=True)
        sys.path.insert(0, str(self.package))
        from pe_original import PE
        self.binding = json.loads(D.BINDINGS.read_text())
        self.pe = {name: PE(self.package/'static'/name, digest)
                   for name, digest in self.binding['original_sha256'].items()}

    def loaded(self, shift, corrupt=None):
        bases = {name: p.base+shift for name, p in self.pe.items()}
        def read(address, size):
            name = next(n for n, p in self.pe.items() if bases[n] <= address < bases[n]+p.image)
            pe = self.pe[name]
            rva = address-bases[name]
            raw = bytearray(pe.region(rva, size))
            for offset in pe.relocations(rva, size):
                struct.pack_into('<I', raw, offset, (struct.unpack_from('<I', raw, offset)[0]+shift)&0xffffffff)
            if corrupt and name == corrupt[0] and rva <= corrupt[1] < rva+size:
                raw[corrupt[1]-rva] ^= 1
            return bytes(raw)
        return read, bases

    def test_original_instructions_match_at_preferred_and_relocated_bases(self):
        for shift in (0, 0x100000):
            read, bases = self.loaded(shift)
            D.verify_guards(read, bases, self.binding)

    def test_each_corrupted_loaded_instruction_guard_is_rejected(self):
        for g in self.binding['guards']:
            read, bases = self.loaded(0x100000, (g['module'], g['rva']))
            with self.subTest(guard=g['label']), self.assertRaisesRegex(ValueError, 'guard differs'):
                D.verify_guards(read, bases, self.binding)

    def test_engine_input_global_is_the_original_named_export(self):
        pe = self.pe['Engine.dll']
        export_rva = pe.u32(pe.opt+96)
        fields = struct.unpack('<IIHHIIIIIII', pe.region(export_rva, 40))
        funcs, names, ordinals = fields[8:11]
        found = None
        for i in range(fields[7]):
            name_rva = struct.unpack('<I', pe.region(names+i*4, 4))[0]
            name = pe.b[pe.offset(name_rva):].split(b'\0')[0].decode('ascii')
            if name == '?_pInput@@3PAVCInput@@A':
                ordinal = struct.unpack('<H', pe.region(ordinals+i*2, 2))[0]
                found = struct.unpack('<I', pe.region(funcs+ordinal*4, 4))[0]
        self.assertEqual(found, 0x1f178c)


if __name__ == '__main__':
    unittest.main()
