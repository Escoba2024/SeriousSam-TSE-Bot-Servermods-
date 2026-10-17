"""Synthetic-only regression tests for the read-only Retail sync snapshot comparator."""
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from compare_sync_dumps import compare, parse_snapshot, read_limited


def dump(crc="A1B2C3D4", level=1, sequence=1689, tick="83.40",
         action="pa_ulButtons: 00000001", person="PRIVATE_PERSON"):
    return (
        "__________________________________________________________________________________\n"
        f"CRC: 0x{crc}\n"
        f"Level: {level}\nSequence: {sequence}\nTick: {tick}\nPaused: 0\n"
        f"==== players: ====\nName: {person}\n"
        "-- action:\n" + action + "\n"
    )


class SyncSnapshotCompareTests(unittest.TestCase):
    def test_identical_aligned_snapshot(self):
        result = compare(dump(), dump())
        self.assertEqual(result["status"], "MATCHING_SNAPSHOT")
        self.assertTrue(result["can_compare"])
        self.assertEqual(result["state_line_differences"], 0)
        self.assertTrue(result["crc_equal"])

    def test_changed_action_is_hashed_not_leaked(self):
        server = dump(action="pa_ulButtons: 11110000", person="ConfidentialPlayer")
        client = dump(action="pa_ulButtons: 11010000", person="ConfidentialPlayer")
        result = compare(server, client)
        self.assertEqual(result["status"], "DIFFERENT_SNAPSHOT")
        self.assertEqual(result["state_line_differences"], 1)
        self.assertEqual(result["first_differences_redacted"][0]["server_label"], "pa_ulButtons")
        self.assertNotIn("ConfidentialPlayer", json.dumps(result))
        self.assertNotIn("11110000", json.dumps(result))
        self.assertEqual(len(result["first_differences_redacted"][0]["server_fingerprint"]), 12)

    def test_player_name_difference_does_not_hash_identifier(self):
        result = compare(dump(person="Sensitive-A"), dump(person="Sensitive-B"))
        diff = result["first_differences_redacted"][0]
        self.assertEqual(diff["server_label"], "<redacted>")
        self.assertEqual(diff["client_label"], "<redacted>")
        self.assertIsNone(diff["server_fingerprint"])
        self.assertIsNone(diff["client_fingerprint"])
        self.assertNotIn("Sensitive-A", json.dumps(result))
        self.assertNotIn("Sensitive-B", json.dumps(result))

    def test_crc_mismatch_even_if_printed_state_same(self):
        result = compare(dump(crc="A1B2C3D4"), dump(crc="DEADBEEF"))
        self.assertEqual(result["status"], "DIFFERENT_SNAPSHOT")
        self.assertFalse(result["crc_equal"])
        self.assertEqual(result["state_line_differences"], 0)

    def test_different_sequence_or_tick_fail_closed(self):
        for changed in [dump(sequence=1690), dump(tick="84.40"), dump(level=2)]:
            with self.subTest(changed=changed[:70]):
                result = compare(dump(), changed)
                self.assertEqual(result["status"], "UNALIGNED")
                self.assertFalse(result["can_compare"])
                self.assertNotIn("first_differences_redacted", result)

    def test_normalized_crlf_and_whitespace(self):
        one = dump()
        other = (one.replace("\n", "\r\n").replace("Paused: 0", "Paused: 0  ")
                 .replace("Tick: 83.40", "Tick: 83.4"))
        self.assertEqual(compare(one, other)["status"], "MATCHING_SNAPSHOT")

    def test_malformed_missing_required_metadata(self):
        for sample in ["SYNCBAD: bad 1", dump().replace("CRC: 0x", "CRC: "),
                       dump().replace("Tick: 83.40", "Tick: 83..40")]:
            with self.subTest(sample=sample[:25]):
                with self.assertRaises(ValueError):
                    parse_snapshot(sample)

    def test_concatenated_snapshots_rejected(self):
        with self.assertRaisesRegex(ValueError, "exactly one CRC"):
            parse_snapshot(dump() + "\n" + dump())

    def test_extra_state_line_structural_diff(self):
        changed = dump() + "unexpected state: 123\n"
        result = compare(dump(), changed)
        self.assertEqual(result["state_line_count_client"], result["state_line_count_server"] + 1)
        self.assertEqual(result["first_differences_redacted"][0]["server_label"], "<missing>")
        self.assertEqual(result["first_differences_redacted"][0]["client_label"], "<redacted>")

    def test_absent_path_and_large_file_rejected(self):
        with tempfile.TemporaryDirectory(prefix="tse-syncdump-") as temp:
            path = Path(temp) / "no-file.txt"
            with self.assertRaises(ValueError):
                read_limited(path)
            path.write_bytes(b"x" * (8 * 1024 * 1024 + 1))
            with self.assertRaises(ValueError):
                read_limited(path)

    def test_cli_exit_codes(self):
        with tempfile.TemporaryDirectory(prefix="tse-syncdump-") as temp:
            root = Path(temp)
            s = root / "server.txt"
            c = root / "client.txt"
            script = Path(__file__).with_name("compare_sync_dumps.py")
            s.write_text(dump(), encoding="utf-8")
            for content, expected in [(dump(), 0),
                                      (dump(crc="DEADBEEF"), 3),
                                      (dump(tick="84.40"), 2)]:
                c.write_text(content, encoding="utf-8")
                process = subprocess.run(
                    [sys.executable, str(script), "--server", str(s), "--client", str(c)],
                    capture_output=True, text=True
                )
                self.assertEqual(process.returncode, expected)
                self.assertEqual(json.loads(process.stdout)["can_compare"], expected != 2)


if __name__ == "__main__":
    unittest.main()
