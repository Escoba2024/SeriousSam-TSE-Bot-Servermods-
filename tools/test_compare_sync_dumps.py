"""Synthetic-only regression tests for the read-only Retail sync snapshot comparator."""
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from compare_sync_dumps import (compare, compare_series, load_snapshot_directory,
                                parse_snapshot, read_limited)


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


    def test_repeated_metadata_fails_closed(self):
        for text in [dump() + "Tick: 999\n",
                     dump() + "Sequence: 999\n",
                     dump() + "Level: 9\n"]:
            with self.subTest(extra=text[-20:]):
                with self.assertRaisesRegex(ValueError, "exactly one"):
                    parse_snapshot(text)

    def test_first_observed_mismatch_in_aligned_series(self):
        server = [dump(sequence=10, tick="1.0"),
                  dump(sequence=11, tick="2.0"),
                  dump(sequence=12, tick="3.0")]
        client = [dump(sequence=12, tick="3.0", crc="DEADBEEF"),
                  dump(sequence=10, tick="1.0"),
                  dump(sequence=11, tick="2.0", crc="DEADBEEF")]
        result = compare_series(server, client)
        self.assertEqual(result["status"], "OBSERVED_DIFFERENCE")
        self.assertEqual(result["aligned_samples"], 3)
        self.assertEqual(result["differing_aligned_samples"], 2)
        self.assertEqual(result["first_observed_difference"]["tick"], "2.0")
        self.assertEqual(result["first_observed_difference"]["sequence"], 11)
        self.assertFalse(result["first_observed_difference"]["crc_equal"])
        self.assertNotIn("PRIVATE_PERSON", json.dumps(result))
        self.assertIn("not establish", result["interpretation"])

    def test_unpaired_capture_never_claims_complete_alignment(self):
        server = [dump(sequence=10, tick="1"), dump(sequence=12, tick="3")]
        client = [dump(sequence=10, tick="1"), dump(sequence=11, tick="2"),
                  dump(sequence=12, tick="3", crc="DEADBEEF")]
        result = compare_series(server, client)
        self.assertEqual(result["status"], "INCOMPLETE_ALIGNMENT")
        self.assertFalse(result["complete_pairing"])
        self.assertEqual(result["unpaired_client_samples"], 1)
        self.assertEqual(result["first_observed_difference"]["tick"], "3")
        self.assertEqual(result["aligned_samples"], 2)

    def test_series_without_shared_identity_is_unaligned(self):
        result = compare_series([dump(sequence=1, tick="1")],
                                [dump(sequence=2, tick="2")])
        self.assertEqual(result["status"], "UNALIGNED")
        self.assertFalse(result["can_compare"])
        self.assertIsNone(result["first_observed_difference"])

    def test_duplicate_and_multiple_levels_are_invalid(self):
        with self.assertRaisesRegex(ValueError, "duplicate"):
            compare_series([dump(), dump()], [dump()])
        with self.assertRaisesRegex(ValueError, "multiple levels"):
            compare_series([dump(level=1)], [dump(level=2)])

    def test_directory_rejects_unrelated_files(self):
        with tempfile.TemporaryDirectory(prefix="tse-dirmix-") as temp:
            directory = Path(temp)
            (directory / "one.txt").write_text(dump(), encoding="utf-8")
            (directory / "note.log").write_text("not a sync dump", encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "only regular"):
                load_snapshot_directory(directory)

    def test_directory_cli_exit_codes_and_no_identity_leak(self):
        with tempfile.TemporaryDirectory(prefix="tse-series-") as temp:
            base = Path(temp)
            server_dir, client_dir = base / "server", base / "client"
            server_dir.mkdir()
            client_dir.mkdir()
            (server_dir / "a.txt").write_text(dump(sequence=10, tick="1"), encoding="utf-8")
            (server_dir / "b.txt").write_text(dump(sequence=11, tick="2"), encoding="utf-8")
            (client_dir / "a.txt").write_text(dump(sequence=10, tick="1"), encoding="utf-8")
            changed = client_dir / "b.txt"
            for text, expected, status in [
                (dump(sequence=11, tick="2"), 0, "MATCHED_OBSERVATIONS"),
                (dump(sequence=11, tick="2", crc="DEADBEEF"), 3, "OBSERVED_DIFFERENCE"),
                (dump(sequence=12, tick="3"), 2, "INCOMPLETE_ALIGNMENT"),
            ]:
                changed.write_text(text, encoding="utf-8")
                proc = subprocess.run(
                    [sys.executable, str(Path(__file__).with_name("compare_sync_dumps.py")),
                     "--server-dir", str(server_dir), "--client-dir", str(client_dir)],
                    capture_output=True, text=True)
                self.assertEqual(proc.returncode, expected, proc.stderr)
                self.assertEqual(json.loads(proc.stdout)["status"], status)
                self.assertNotIn("PRIVATE_PERSON", proc.stdout)
            self.assertEqual(len(load_snapshot_directory(server_dir)), 2)


if __name__ == "__main__":
    unittest.main()
