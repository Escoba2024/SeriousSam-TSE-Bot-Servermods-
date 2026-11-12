"""Byte planner regressions; fixtures contain no private identities."""
import hashlib
import struct
import unittest
import names_staging as N


class NameBytes(unittest.TestCase):
    def setUp(self):
        self.guid = bytes.fromhex("0123456789abcdef0123456789abcdef")
        self.tail = bytes(4) + self.guid + bytes(range(32))
        self.before = b"PLC4" + struct.pack("<I", 3) + b"Old" + self.tail

    def test_only_length_and_name_bytes_change(self):
        after, receipt = N.patch_name(self.before, self.guid, "^c55AAFF^bPlayer^B^r")
        raw = b"^c55AAFF^bPlayer^B^r"
        self.assertEqual(after, b"PLC4" + struct.pack("<I", len(raw)) + raw + self.tail)
        self.assertEqual(receipt["tail_bytes"], 52)
        self.assertEqual(receipt["guid_hex"], self.guid.hex())

    def test_wrong_sidecar_and_modified_tail_length_reject(self):
        with self.assertRaisesRegex(ValueError, "sidecar"):
            N.patch_name(self.before, bytes.fromhex("ff"*16), "Player")
        with self.assertRaisesRegex(ValueError, "length"):
            N.parse_plc(self.before + b"x")

    def test_nonempty_team_is_not_silently_reinterpreted(self):
        bad = self.before[:11] + struct.pack("<I", 1) + self.tail[4:]
        with self.assertRaisesRegex(ValueError, "team"):
            N.parse_plc(bad)

    def test_console_escape_never_becomes_name(self):
        for value in ('Player";quit', "Player\nquit", "Player\\quit", "^xPlayer"):
            with self.subTest(value=value):
                with self.assertRaises(ValueError):
                    N.patch_name(self.before, self.guid, value)

    def test_launcher_requires_pinned_exact_rotation_and_guid_lines(self):
        root = "/example/redstation"
        before = (
            f"#!/bin/bash\n/usr/bin/python3 {root}/rotate-live-identities.py --client A || exit 87\n"
            f"/usr/bin/python3 {root}/generate-bot-roster.py --client A || exit 88\n"
            "exec harmless-fixture\n").encode()
        digest = hashlib.sha256(before).hexdigest()
        after = N.patch_launcher(before, root, "A", digest)
        self.assertIn(f"/usr/bin/python3 {root}/generate-bot-roster.py --client A || exit 88\n".encode(), after)
        self.assertTrue(after.endswith(b"exec harmless-fixture\n"))
        with self.assertRaisesRegex(ValueError, "hash"):
            N.patch_launcher(before, root, "A", "0"*64)
        duplicated = before + before.splitlines(keepends=True)[1]
        with self.assertRaisesRegex(ValueError, "line"):
            N.patch_launcher(duplicated, root, "A", hashlib.sha256(duplicated).hexdigest())


if __name__ == "__main__":
    unittest.main()
