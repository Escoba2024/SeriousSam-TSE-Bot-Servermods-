#!/usr/bin/env python3
"""Portable, synthetic-only regression tests for read-only TSE sync log analysis.

No private log, retail binary, running server or network connection is required.
"""
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from analyze_sync_log import analyze


class SyncLogAnalysisTests(unittest.TestCase):
    def test_interleaved_clients_and_confirmed_disconnect(self):
        log = (
            "prefix SYNCBAD: Client 'A', Sequence 17 Tick 83.40 - bad 1\r\n"
            "SYNCBAD: Client 'B', Sequence 4 Tick 4.00 - bad 7\r\n"
            "SYNCOK: Client 'A', Tick 84.40\r\n"
            "SYNCBAD: Client 'A', Sequence 19 Tick 85.40 - bad 1\r\n"
            "Client 'B' ordered to disconnect: Too many bad syncs\r\n"
        )
        result = analyze(log)
        self.assertEqual(result["bad_events"], 3)
        self.assertEqual(result["sync_ok_events"], 1)
        self.assertEqual(result["disconnect_events"], 1)
        self.assertEqual(result["clients"]["A"]["bad_events"], 2)
        self.assertEqual(result["clients"]["A"]["max_reported_counter"], 1)
        self.assertEqual(len(result["clients"]["A"]["observed_segments"]), 2)
        self.assertEqual(result["clients"]["B"]["max_reported_counter"], 7)
        self.assertEqual(result["disconnects"][0]["line"], 5)
        self.assertIn("not a stability PASS", result["interpretation"])

    def test_consecutive_counter_and_reset_segments(self):
        log = "\n".join([
            "SYNCBAD: Client 'A', Sequence 1 Tick 1.0 - bad 1",
            "SYNCBAD: Client 'A', Sequence 2 Tick 2.0 - bad 2",
            "SYNCBAD: Client 'A', Sequence 3 Tick 3.0 - bad 3",
            "SYNCBAD: Client 'A', Sequence 4 Tick 5.0 - bad 1",
            "SYNCBAD: Client 'A', Sequence 5 Tick 6.0 - bad 2",
        ])
        result = analyze(log)["clients"]["A"]
        self.assertEqual(result["max_reported_counter"], 3)
        self.assertEqual(result["observed_segments"], [
            dict(first_tick=1.0, last_tick=3.0, first_counter=1, last_counter=3, events_seen=3),
            dict(first_tick=5.0, last_tick=6.0, first_counter=1, last_counter=2, events_seen=2),
        ])

    def test_text_without_confirmed_disconnect_is_not_failure(self):
        result = analyze(
            "Some error: Too many bad syncs\n"
            "LOG: SYNCBAD: Client 'C', Sequence 1 Tick 3.5 - bad 1\n"
            "SYNCBAD: corrupted sequence and tick\n"
        )
        self.assertEqual(result["disconnect_events"], 0)
        self.assertEqual(result["bad_events"], 1)

    def test_malformed_tick_is_ignored_not_crashed_or_truncated(self):
        log = (
            "SYNCBAD: Client 'A', Sequence 1 Tick 12..3 - bad 1\n"
            "SYNCOK: Client 'A', Tick 13..4\n"
            "SYNCOK: Client 'A', Tick 14.5\n"
        )
        result = analyze(log)
        self.assertEqual(result["bad_events"], 0)
        self.assertEqual(result["sync_ok_events"], 1)

    def test_empty_log_has_no_false_pass(self):
        result = analyze("")
        self.assertEqual(result["bad_events"], 0)
        self.assertEqual(result["disconnect_events"], 0)
        self.assertEqual(result["clients"], {})
        self.assertNotIn("PASS", result, "The analyzer must never issue runtime acceptance")

    def test_cli_json_on_synthetic_log(self):
        with tempfile.TemporaryDirectory(prefix="tse-sync-audit-") as temp:
            path = Path(temp) / "synthetic.log"
            path.write_text("Disconnected: Too many bad syncs\n", encoding="utf-8")
            completed = subprocess.run(
                [sys.executable, str(Path(__file__).with_name("analyze_sync_log.py")), str(path)],
                capture_output=True, text=True, check=True,
            )
            report = json.loads(completed.stdout)
            self.assertEqual(report[str(path)]["disconnect_events"], 1)
            self.assertEqual(report[str(path)]["bad_events"], 0)

    def test_missing_log_fails_closed(self):
        with tempfile.TemporaryDirectory(prefix="tse-sync-audit-") as temp:
            nonexistent = Path(temp) / "not-here.log"
            completed = subprocess.run(
                [sys.executable, str(Path(__file__).with_name("analyze_sync_log.py")), str(nonexistent)],
                capture_output=True, text=True,
            )
            self.assertNotEqual(completed.returncode, 0)
            self.assertIn("File not found", completed.stderr)


if __name__ == "__main__":
    unittest.main()
