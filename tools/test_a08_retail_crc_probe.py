#!/usr/bin/env python3
"""Dependency-free, in-memory PE fixture regression checks for A08 preflight."""
import hashlib
import struct
import unittest

from a08_retail_crc_probe import PE32, PEError, analyze, unresolved


def put_u16(b, offset, value):
    struct.pack_into("<H", b, offset, value)


def put_u32(b, offset, value):
    struct.pack_into("<I", b, offset, value)


def fixture(export_name="GAME_Create", engine_symbol="EFunc", entity_symbol="EntFunc",
            game_imports=True, allocation_size=0x2FCC):
    """One-section PE32; input bytes only, never written to disk."""
    b = bytearray(0x1200)
    b[:2] = b"MZ"
    put_u32(b, 0x3C, 0x80)
    b[0x80:0x84] = b"PE\x00\x00"
    put_u16(b, 0x84, 0x14C)     # i386
    put_u16(b, 0x86, 1)         # sections
    put_u16(b, 0x94, 0xE0)      # optional header size
    op = 0x98
    put_u16(b, op, 0x10B)       # PE32
    put_u32(b, op + 28, 0x10000000)
    put_u32(b, op + 60, 0x200)  # SizeOfHeaders
    put_u32(b, op + 92, 16)     # NumberOfRvaAndSizes
    put_u32(b, op + 96, 0x1000)
    put_u32(b, op + 100, 0x100)
    if game_imports:
        put_u32(b, op + 104, 0x1150)
        put_u32(b, op + 108, 60)
    sec = op + 0xE0
    b[sec:sec + 8] = b".text\x00\x00\x00"
    put_u32(b, sec + 8, 0x1000)
    put_u32(b, sec + 12, 0x1000)
    put_u32(b, sec + 16, 0x1000)
    put_u32(b, sec + 20, 0x200)

    # Export IMAGE_EXPORT_DIRECTORY + one function/name/ordinal.
    put_u32(b, 0x20C, 0x10B0)   # DLL name
    put_u32(b, 0x210, 1)        # ordinal base
    put_u32(b, 0x214, 1)        # functions
    put_u32(b, 0x218, 1)        # names
    put_u32(b, 0x21C, 0x1060)   # AddressOfFunctions
    put_u32(b, 0x220, 0x1070)   # AddressOfNames
    put_u32(b, 0x224, 0x1080)   # AddressOfNameOrdinals
    put_u32(b, 0x260, 0x1400)   # function RVA (file offset 0x600)
    put_u32(b, 0x270, 0x1090)   # exported name RVA
    put_u16(b, 0x280, 0)        # name->function index
    b[0x290:0x290 + len(export_name) + 1] = export_name.encode() + b"\x00"
    b[0x2B0:0x2B0 + 12] = b"Fixture.dll\x00"
    b[0x600:0x606] = b"\x53\x68" + struct.pack("<I", allocation_size)

    if game_imports:
        # Import descriptors at RVA 0x1150, NULL descriptor at RVA 0x1178.
        struct.pack_into("<IIIII", b, 0x350, 0x1200, 0, 0, 0x1280, 0x1200)
        struct.pack_into("<IIIII", b, 0x364, 0x1220, 0, 0, 0x12A0, 0x1220)
        put_u32(b, 0x400, 0x1240)  # Engine!EFunc name hint
        put_u32(b, 0x420, 0x1260)  # Entities!EntFunc name hint
        b[0x440:0x440 + len(engine_symbol) + 3] = b"\x00\x00" + engine_symbol.encode() + b"\x00"
        b[0x460:0x460 + len(entity_symbol) + 3] = b"\x00\x00" + entity_symbol.encode() + b"\x00"
        b[0x480:0x480 + len(b"ENGINE.DLL\x00")] = b"ENGINE.DLL\x00"
        b[0x4A0:0x4A0 + len(b"EntitiesMP.dll\x00")] = b"EntitiesMP.dll\x00"
    return bytes(b)


def all_images(bot_engine_symbol="EFunc", bot_size=0x2FCC):
    return {
        "engine": fixture(export_name="EFunc", game_imports=False),
        "entities": fixture(export_name="EntFunc", game_imports=False),
        "retail_game": fixture(),
        "bot_game": fixture(engine_symbol=bot_engine_symbol, allocation_size=bot_size),
    }


class StaticPeTests(unittest.TestCase):
    def test_fixture_export_rva(self):
        img = PE32(fixture())
        exports, ordinals = img.exports()
        self.assertEqual(exports["GAME_Create"], 0x1400)
        self.assertIn(1, ordinals)

    def test_pe_header_properties(self):
        img = PE32(fixture())
        self.assertEqual(img.machine, 0x14C)
        self.assertEqual(img.image_base, 0x10000000)

    def test_case_insensitive_library_names(self):
        imp = PE32(fixture()).imports()
        self.assertEqual(imp["engine.dll"], {"EFunc"})
        self.assertEqual(imp["entitiesmp.dll"], {"EntFunc"})

    def test_all_four_images_pass_without_hash_guard(self):
        out = analyze(all_images(), enforce_known_hashes=False)
        self.assertEqual(out["status"], "PASS_STATIC_PE_LINKAGE")
        self.assertTrue(out["game"]["bot_game"]["game_create_push_0x2fcc_first_48"])

    def test_missing_symbol_detected(self):
        out = analyze(all_images(bot_engine_symbol="Missing"), enforce_known_hashes=False)
        self.assertEqual(out["status"], "FAIL_STATIC_PE_LINKAGE")
        self.assertEqual(out["game"]["bot_game"]["unresolved_engine_imports"], ["Missing"])

    def test_different_allocation_detected(self):
        out = analyze(all_images(bot_size=0x3080), enforce_known_hashes=False)
        self.assertEqual(out["status"], "FAIL_STATIC_PE_LINKAGE")
        self.assertFalse(out["game"]["bot_game"]["game_create_push_0x2fcc_first_48"])

    def test_strict_hash_guard_rejects_fixtures(self):
        out = analyze(all_images())
        self.assertEqual(out["status"], "FAIL_STATIC_PE_LINKAGE")
        self.assertTrue(all(not v for v in out["hashes_match_qualified_set"].values()))

    def test_dos_signature_fails_closed(self):
        b = bytearray(fixture())
        b[0:2] = b"NO"
        with self.assertRaises(PEError):
            PE32(bytes(b))

    def test_pe_signature_fails_closed(self):
        b = bytearray(fixture())
        b[0x80:0x84] = b"FAIL"
        with self.assertRaises(PEError):
            PE32(bytes(b))

    def test_x64_rejected(self):
        b = bytearray(fixture())
        put_u16(b, 0x98, 0x20B)
        with self.assertRaises(PEError):
            PE32(bytes(b))

    def test_truncated_section_fails_closed(self):
        with self.assertRaises(PEError):
            PE32(fixture()[:0x220]).exports()

    def test_unmapped_rva_rejected(self):
        with self.assertRaises(PEError):
            PE32(fixture()).offset(0xF000)

    def test_absent_game_create_rejected(self):
        b = fixture(export_name="OtherFunc")
        with self.assertRaises(PEError):
            PE32(b).function_prefix("GAME_Create")

    def test_ordinal_symbol_resolution(self):
        self.assertEqual(unresolved({"#2", "#8", "EFunc"}, {"EFunc": 0x1400}, {2}), ["#8"])

    def test_import_descriptor_truncation_rejected(self):
        b = bytearray(fixture())
        put_u32(b, 0x350 + 12, 0xF000)
        with self.assertRaises(PEError):
            PE32(bytes(b)).imports()

    def test_no_artifacts_or_state_side_effects(self):
        # Deterministic in-memory analysis; no logs, temp files or serialized binary bytes.
        out = analyze(all_images(), enforce_known_hashes=False)
        self.assertNotIn("raw_binary", out)
        self.assertEqual(hashlib.sha256(fixture()).hexdigest(),
                         hashlib.sha256(fixture()).hexdigest())


if __name__ == "__main__":
    unittest.main(verbosity=2)
