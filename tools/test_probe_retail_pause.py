"""Portable tests: exact Retail instruction validation under PE32 relocation."""
import struct
import unittest

import probe_retail_pause as pause


class RelocatedPauseTests(unittest.TestCase):
    def image(self, base):
        expected = {
            pause.TOGGLE_RVA: pause.TOGGLE_BYTES,
            pause.IS_PAUSED_RVA: pause.IS_PAUSED_BYTES,
            pause.RND_RVA: pause.RND_BYTES,
            pause.RESET_RND_RVA: pause.RESET_RND_BYTES,
        }
        # Independently model the one HIGHLOW entry: original operand + delta.
        getter = bytearray(expected[pause.IS_PAUSED_RVA])
        struct.pack_into('<I', getter, 5, 0x602CD6B8 + base - 0x600C0000)
        expected[pause.IS_PAUSED_RVA] = bytes(getter)
        return expected

    def check(self, base, expected):
        reads = []
        def read(address, size):
            reads.append((address, size))
            return expected[address-base][:size]
        pause._check_instructions(read, base)
        self.assertEqual(reads, [(base+rva, len(data)) for rva, data in expected.items()])

    def test_preferred_base_unchanged(self):
        image = self.image(0x600C0000)
        self.assertEqual(image[pause.IS_PAUSED_RVA], pause.IS_PAUSED_BYTES)
        self.check(0x600C0000, image)

    def test_positive_and_negative_relocations(self):
        for base in (0x10000000, 0x61000000, 0x10000, 0xFFDD2000):
            with self.subTest(base=hex(base)):
                self.check(base, self.image(base))

    def test_unrelocated_operand_at_relocated_base_rejected(self):
        base=0x61000000
        image=self.image(base)
        image[pause.IS_PAUSED_RVA]=pause.IS_PAUSED_BYTES
        with self.assertRaisesRegex(RuntimeError, 'IsPaused instructions differ.*base=0x61000000.*expected=.*observed='):
            self.check(base,image)

    def test_each_instruction_byte_still_exact(self):
        base=0x10000000
        for rva,data in self.image(base).items():
            for i in range(len(data)):
                with self.subTest(rva=hex(rva),byte=i):
                    image=self.image(base)
                    bad=bytearray(data);bad[i]^=1;image[rva]=bytes(bad)
                    with self.assertRaisesRegex(RuntimeError, 'instructions differ'):
                        self.check(base,image)

    def test_short_instruction_is_diagnostic_failure(self):
        base=0x600C0000
        image=self.image(base)
        image[pause.IS_PAUSED_RVA]=image[pause.IS_PAUSED_RVA][:-1]
        with self.assertRaisesRegex(RuntimeError, 'IsPaused instructions differ.*observed='):
            pause._check_instructions(lambda address,size:image[address-base],base)

    def test_invalid_base_rejected_before_reads(self):
        for base in (None,True,0.0,0,-4096,0x1000,0x10001,0x600C0001,0xFFDD3000,0x100000000):
            with self.subTest(base=base):
                def forbidden_read(*args):
                    self.fail('invalid mapping must not trigger a memory read')
                with self.assertRaisesRegex(RuntimeError,'invalid Engine base'):
                    pause._check_instructions(forbidden_read,base)

    def test_diagnostics_include_actual_expected_and_base(self):
        base=0x61000000
        image=self.image(base)
        actual=b'\x90'*len(pause.IS_PAUSED_BYTES)
        image[pause.IS_PAUSED_RVA]=actual
        with self.assertRaises(RuntimeError) as caught:
            self.check(base,image)
        text=str(caught.exception)
        self.assertIn('base=0x61000000',text)
        self.assertIn('rva=0x000dab60',text)
        self.assertIn('expected='+self.image(base)[pause.IS_PAUSED_RVA].hex(),text)
        self.assertIn('observed='+actual.hex(),text)


if __name__=='__main__':
    unittest.main()
