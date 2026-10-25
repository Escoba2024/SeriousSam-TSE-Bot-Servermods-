#!/usr/bin/env python3
"""Reproduzierbare Offline-Tests für die TSE-Sync-Forensics-Werkzeuge.

Alle Tests arbeiten ausschließlich mit synthetischen Fixtures (siehe
tools/make_synthetic_logs.py). Es werden keine echten Logs, DLLs oder
Spieldaten gelesen. Die Tests verifizieren:

  1. Fixture-Generierung ist deterministisch (gleicher SHA256).
  2. sync_correlator: Server/Client-Korrelation, Kick-ohne-Disconnect.
  3. sync_tick_compare: Tick-Serien, Counter-Jump-Erkennung.
  4. sync_crc_diff: aligned identisch/divergent, UNALIGNED, INCOMPLETE.
  5. sync_event_mapper: Chronologie, orphan-Events.
  6. sync_error_classifier: E1..E6-Klassen.
  7. sync_incomplete_detector: Unvollständigkeitserkennung.
  8. Fail-closed-Verhalten (UNALIGNED/INCOMPLETE statt erfundener Divergenz).

Ausführung (Python 3.11+):
  python3 -m unittest discover -s poc/research/sync-forensics/tests -v
"""

from __future__ import annotations

import hashlib
import io
import json
import contextlib
import sys
import tempfile
import unittest
from pathlib import Path

TOOLS_DIR = Path(__file__).resolve().parent.parent / "tools"
sys.path.insert(0, str(TOOLS_DIR))

import make_synthetic_logs as msl  # noqa: E402
import sync_correlator  # noqa: E402
import sync_tick_compare  # noqa: E402
import sync_crc_diff  # noqa: E402
import sync_event_mapper  # noqa: E402
import sync_error_classifier  # noqa: E402
import sync_incomplete_detector  # noqa: E402
import sync_forensics_common as common  # noqa: E402


def _write(dirpath: Path, name: str, text: str) -> Path:
    p = dirpath / name
    p.write_text(text, encoding="utf-8")
    return p


class FixtureDeterminismTest(unittest.TestCase):
    """Die synthetischen Fixtures müssen reproduzierbar sein."""

    def test_sustained_log_deterministic(self):
        h1 = hashlib.sha256(msl.sustained_log(42).encode()).hexdigest()
        h2 = hashlib.sha256(msl.sustained_log(42).encode()).hexdigest()
        self.assertEqual(h1, h2)
        # und der Inhalt muss das erwartete E1-Muster haben
        text = msl.sustained_log(42)
        self.assertEqual(text.count("SYNCBAD:"), 10)
        self.assertIn("ordered to disconnect: Too many bad syncs", text)

    def test_dump_pairs(self):
        s, c = msl.dump_pair_identical()
        self.assertEqual(s, c)
        s2, c2 = msl.dump_pair_divergent()
        self.assertNotEqual(s2, c2)


class CommonParserTest(unittest.TestCase):
    def test_parse_server_events(self):
        events = common.parse_server_log_events(msl.sustained_log(1))
        kinds = [e.kind for e in events]
        self.assertEqual(kinds.count("SYNCBAD"), 10)
        self.assertEqual(kinds.count("KICK"), 1)
        bads = [e for e in events if e.kind == "SYNCBAD"]
        self.assertEqual([e.count for e in bads], list(range(1, 11)))
        self.assertEqual(bads[0].client, "127.0.0.1")

    def test_parse_client_events(self):
        events = common.parse_client_log_events(msl.client_only_log())
        kinds = [e.kind for e in events]
        self.assertIn("CLIENT_DISCONNECT", kinds)
        self.assertIn("BOT_TICK", kinds)


class CorrelatorTest(unittest.TestCase):
    def test_kick_with_client_disconnect(self):
        server = msl.sustained_log(2)
        client = msl.client_only_log(2)
        result = sync_correlator.correlate(server, client, [])
        self.assertEqual(result["server_kick_events"], 1)
        self.assertEqual(result["client_disconnect_events"], 1)
        self.assertEqual(result["kick_without_client_disconnect"], [])

    def test_kick_without_client_log(self):
        server = msl.sustained_log(3)
        result = sync_correlator.correlate(server, "", [])
        self.assertEqual(result["kick_without_client_disconnect"], ["127.0.0.1"])

    def test_telemetry_rows(self):
        csv_text = msl.telemetry_csv(5, 15)
        with tempfile.TemporaryDirectory() as td:
            p = _write(Path(td), "t.csv", csv_text)
            rows = sync_correlator.parse_bot_telemetry_csv(p)
            self.assertEqual(len(rows), 15)
            self.assertEqual(rows[0]["t_ms"], 1000.0)


class TickCompareTest(unittest.TestCase):
    def test_sustained_series_and_jumps(self):
        result = sync_tick_compare.compare_ticks(msl.sustained_log(4), "", None)
        self.assertEqual(result["server_bad_tick_series"]["ticks"], 10)
        self.assertEqual(result["bad_counter_monotonic_within_client"], True)

    def test_counter_jump_detected(self):
        result = sync_tick_compare.compare_ticks(msl.jump_log(4), "", None)
        self.assertEqual(len(result["counter_jumps"]), 1)
        self.assertEqual(result["counter_jumps"][0]["delta"], 2)
        self.assertFalse(result["bad_counter_monotonic_within_client"])

    def test_no_divergent_tick_claim(self):
        # Der Tool-Report darf niemals einen divergenten Tick behaupten.
        result = sync_tick_compare.compare_ticks(msl.sustained_log(4), "", None)
        self.assertNotIn("first_divergent_tick", result)
        self.assertIn("first_bad_tick", result)


class CrcDiffTest(unittest.TestCase):
    def _rec(self, text: str):
        return common.parse_dump_text("mem", text)

    def test_identical_aligned(self):
        s, c = msl.dump_pair_identical()
        result = sync_crc_diff.compare_snapshot(self._rec(s), self._rec(c))
        self.assertEqual(result["status"], "COMPARABLE")
        self.assertTrue(result["crc_equal"])
        self.assertEqual(result["field_difference_count"], 0)

    def test_divergent_aligned(self):
        s, c = msl.dump_pair_divergent()
        result = sync_crc_diff.compare_snapshot(self._rec(s), self._rec(c))
        self.assertEqual(result["status"], "COMPARABLE")
        self.assertFalse(result["crc_equal"])
        self.assertGreater(result["field_difference_count"], 0)

    def test_misaligned_fails_closed(self):
        s, c = msl.dump_pair_misaligned()
        result = sync_crc_diff.compare_snapshot(self._rec(s), self._rec(c))
        self.assertEqual(result["status"], "UNALIGNED")
        self.assertNotIn("field_differences", result)

    def test_missing_header_fails_closed(self):
        s = msl.dump_pair_identical()[0]
        c = "CRC: 0x11111111\n"
        result = sync_crc_diff.compare_snapshot(self._rec(s), self._rec(c))
        self.assertEqual(result["status"], "UNALIGNED")

    def test_series_first_divergence(self):
        with tempfile.TemporaryDirectory() as td:
            td = Path(td)
            # Serie: Tick 1 identisch, Tick 2 divergent
            (td / "s1.txt").write_text(msl.dump_pair_identical()[0], encoding="utf-8")
            (td / "c1.txt").write_text(msl.dump_pair_identical()[1], encoding="utf-8")
            (td / "s2.txt").write_text(
                msl.dump_text("Yodeller", 5100, 101.0, 0x11111111), encoding="utf-8")
            (td / "c2.txt").write_text(
                msl.dump_text("Yodeller", 5100, 101.0, 0x22222222), encoding="utf-8")
            # Reihenfolge: als Client-Verzeichnis die c*.txt, als Server s*.txt
            sdir = td / "server"; sdir.mkdir()
            cdir = td / "client"; cdir.mkdir()
            (sdir / "s1.txt").write_text(msl.dump_pair_identical()[0], encoding="utf-8")
            (sdir / "s2.txt").write_text(
                msl.dump_text("Yodeller", 5100, 101.0, 0x11111111), encoding="utf-8")
            (cdir / "c1.txt").write_text(msl.dump_pair_identical()[1], encoding="utf-8")
            (cdir / "c2.txt").write_text(
                msl.dump_text("Yodeller", 5100, 101.0, 0x22222222), encoding="utf-8")
            result = sync_crc_diff.compare_series(sdir, cdir)
            self.assertEqual(result["status"], "COMPARABLE")
            self.assertIsNotNone(result["first_observed_divergence"])
            self.assertEqual(result["first_observed_divergence"]["key"][2], 101.0)

    def test_series_no_aligned_pair(self):
        with tempfile.TemporaryDirectory() as td:
            td = Path(td)
            s = td / "s"; s.mkdir()
            c = td / "c"; c.mkdir()
            (s / "a.txt").write_text(msl.dump_pair_identical()[0], encoding="utf-8")
            (c / "b.txt").write_text(
                msl.dump_text("Yodeller", 9999, 999.0, 0xAAAAAAAA), encoding="utf-8")
            result = sync_crc_diff.compare_series(s, c)
            self.assertEqual(result["status"], "UNALIGNED")


class EventMapperTest(unittest.TestCase):
    def test_orphan_detection(self):
        server = msl.sustained_log(5)
        client = "Disconnected: Too many bad syncs\n"
        result = sync_event_mapper.map_events(server, client)
        self.assertEqual(result["orphan_server_kicks"], [])
        self.assertEqual(result["orphan_client_disconnects"], [])

    def test_orphan_client_disconnect(self):
        server = msl.empty_sync_log()
        client = "Disconnected: Too many bad syncs\n"
        result = sync_event_mapper.map_events(server, client)
        self.assertEqual(len(result["orphan_client_disconnects"]), 1)


class ErrorClassifierTest(unittest.TestCase):
    def test_e1_sustained(self):
        result = sync_error_classifier.classify(msl.sustained_log(6))
        classes = [c["class"] for c in result["classes"]]
        self.assertIn("E1_Sustained_CRC_Divergence", classes)

    def test_e2_transient(self):
        result = sync_error_classifier.classify(msl.transient_log(6))
        classes = [c["class"] for c in result["classes"]]
        self.assertIn("E2_Transient_Divergence", classes)

    def test_e3_jump(self):
        result = sync_error_classifier.classify(msl.jump_log(6))
        classes = [c["class"] for c in result["classes"]]
        self.assertIn("E3_Counter_Jump", classes)

    def test_e4_kick_only(self):
        result = sync_error_classifier.classify(msl.kick_only_log())
        classes = [c["class"] for c in result["classes"]]
        self.assertIn("E4_Kick_Without_Root_Events", classes)

    def test_e5_no_kick(self):
        result = sync_error_classifier.classify(msl.bad_no_kick_log(6))
        classes = [c["class"] for c in result["classes"]]
        self.assertIn("E5_Log_Only_No_Kick", classes)

    def test_e6_empty(self):
        result = sync_error_classifier.classify(msl.empty_sync_log())
        classes = [c["class"] for c in result["classes"]]
        self.assertEqual(classes, ["E6_No_Sync_Events"])


class IncompleteDetectorTest(unittest.TestCase):
    def test_complete_run(self):
        # Server-Log ohne Sync-Events + Client ohne Disconnect = unvollständig.
        result = sync_incomplete_detector.detect_incomplete(
            msl.empty_sync_log(), msl.empty_sync_log(), None, [])
        self.assertFalse(result["complete"])
        self.assertTrue(any(i["kind"] == "client_log_no_disconnect"
                            for i in result["issues"]))

    def test_dump_issues(self):
        with tempfile.TemporaryDirectory() as td:
            bad = _write(Path(td), "bad.txt", "Level: X\nGARBAGE_LINE\n")
            result = sync_incomplete_detector.detect_incomplete(
                None, None, None, [bad])
            kinds = {i["kind"] for i in result["issues"]}
            self.assertIn("missing_header_field", kinds)
            self.assertIn("missing_crc", kinds)
            self.assertIn("unparsed_line", kinds)

    def test_telemetry_missing(self):
        result = sync_incomplete_detector.detect_incomplete(
            None, None, Path("/nonexistent/telemetry.csv"), [])
        self.assertTrue(any(i["kind"] == "telemetry_missing" for i in result["issues"]))


class FailClosedIntegrationTest(unittest.TestCase):
    """Gesamtsicherheit: Keine工具 darf eine Divergenz erfinden."""

    def test_crc_diff_cli_exit_codes(self):
        import subprocess
        with tempfile.TemporaryDirectory() as td:
            td = Path(td)
            s, c = msl.dump_pair_identical()
            (td / "s.txt").write_text(s, encoding="utf-8")
            (td / "c.txt").write_text(c, encoding="utf-8")
            r = subprocess.run(
                [sys.executable, str(TOOLS_DIR / "sync_crc_diff.py"),
                 "--server", str(td / "s.txt"), "--client", str(td / "c.txt")],
                capture_output=True, text=True)
            self.assertEqual(r.returncode, 0, r.stderr)

            s2, c2 = msl.dump_pair_divergent()
            (td / "s2.txt").write_text(s2, encoding="utf-8")
            (td / "c2.txt").write_text(c2, encoding="utf-8")
            r = subprocess.run(
                [sys.executable, str(TOOLS_DIR / "sync_crc_diff.py"),
                 "--server", str(td / "s2.txt"), "--client", str(td / "c2.txt")],
                capture_output=True, text=True)
            self.assertEqual(r.returncode, 3, r.stderr)

            s3, c3 = msl.dump_pair_misaligned()
            (td / "s3.txt").write_text(s3, encoding="utf-8")
            (td / "c3.txt").write_text(c3, encoding="utf-8")
            r = subprocess.run(
                [sys.executable, str(TOOLS_DIR / "sync_crc_diff.py"),
                 "--server", str(td / "s3.txt"), "--client", str(td / "c3.txt")],
                capture_output=True, text=True)
            self.assertEqual(r.returncode, 2, r.stderr)

    def test_classifier_cli(self):
        import subprocess
        with tempfile.TemporaryDirectory() as td:
            p = _write(Path(td), "sustained.log", msl.sustained_log(8))
            r = subprocess.run(
                [sys.executable, str(TOOLS_DIR / "sync_error_classifier.py"),
                 str(p)], capture_output=True, text=True)
            self.assertEqual(r.returncode, 0)
            data = json.loads(r.stdout)
            key = next(iter(data))
            classes = [c["class"] for c in data[key]["classes"]]
            self.assertIn("E1_Sustained_CRC_Divergence", classes)


if __name__ == "__main__":
    unittest.main(verbosity=2)
