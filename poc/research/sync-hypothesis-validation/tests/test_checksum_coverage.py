"""Checksum-scope probe: coverage table, alignment and fail-closed verdicts."""

from __future__ import annotations

import json
import unittest

import _support
from _support import FixtureDir, run_json, run_tool

import checksum_coverage_probe as probe
from syncval_common import parse_action_trace, parse_layout, read_json, differing_bytes


class CoverageFixtureTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls._fixtures = FixtureDir()
        cls.fixtures = cls._fixtures.__enter__()

    @classmethod
    def tearDownClass(cls):
        cls._fixtures.__exit__(None, None, None)

    def _probe(self, server: str, layout: str = "layout_verified.json",
               *extra):
        return run_json(
            "checksum_coverage_probe.py",
            "--client-trace", str(self.fixtures / "actions_client.csv"),
            "--server-trace", str(self.fixtures / server),
            "--layout", str(self.fixtures / layout),
            *extra,
        )

    def test_identical_traces_have_no_divergence(self):
        payload, code = self._probe("actions_server_identical.csv")
        self.assertEqual(payload["verdict"], "NO_ACTION_DIVERGENCE")
        self.assertEqual(code, 0)
        self.assertIsNone(payload["first_checksum_visible_divergence_tick"])
        self.assertIsNone(payload["first_any_divergence_tick"])

    def test_visible_divergence_inside_scope(self):
        payload, code = self._probe("actions_server_visible_diff.csv")
        self.assertEqual(payload["verdict"], "CHECKSUM_VISIBLE_DIVERGENCE")
        self.assertEqual(code, 3)
        self.assertEqual(payload["first_checksum_visible_divergence_tick"], 137)
        self.assertEqual(payload["divergent_sample_count"], 1)
        fields = payload["divergent_samples"][0]["fields_visible"]
        self.assertIn("pa_aRotation", fields)

    def test_divergence_outside_scope_is_classified_separately(self):
        payload, code = self._probe("actions_server_outside_diff.csv")
        self.assertEqual(payload["verdict"], "DIVERGENCE_OUTSIDE_CHECKSUM_SCOPE")
        self.assertEqual(code, 3)
        self.assertIsNone(payload["first_checksum_visible_divergence_tick"])
        self.assertEqual(payload["first_any_divergence_tick"], 90)
        self.assertEqual(payload["divergent_samples"][0]["visible_in_checksum"], [])
        self.assertIn("pa_aViewRotation", payload["divergent_samples"][0]["fields_outside"])

    def test_truncated_trace_is_incomplete(self):
        payload, code = self._probe("actions_server_truncated.csv")
        self.assertEqual(payload["verdict"], "INCOMPLETE")
        self.assertEqual(code, 4)
        self.assertGreater(payload["alignment"]["client_only"], 0)

    def test_unverified_layout_cannot_be_native_evidence(self):
        payload, code = self._probe("actions_server_visible_diff.csv",
                                    "layout_unverified.json")
        self.assertEqual(payload["verdict"], "LAYOUT_UNVERIFIED")
        self.assertEqual(code, 5)
        self.assertIn("hypothesis", payload["verdict_detail"])

    def test_consistency_before_log_tick(self):
        payload, _ = self._probe("actions_server_visible_diff.csv",
                                 "layout_verified.json",
                                 "--first-bad-tick", "200")
        self.assertEqual(payload["consistency_with_log"]["status"],
                         "CONSISTENT_PRECEDES")

    def test_consistency_after_log_tick_is_inconsistent(self):
        payload, _ = self._probe("actions_server_visible_diff.csv",
                                 "layout_verified.json",
                                 "--first-bad-tick", "83.4")
        self.assertEqual(payload["consistency_with_log"]["status"],
                         "INCONSISTENT_TOO_LATE")
        self.assertIn("cannot explain", payload["consistency_with_log"]["detail"])

    def test_coverage_table_names_never_covered_fields(self):
        payload, _ = self._probe("actions_server_identical.csv")
        coverage = payload["coverage"]
        self.assertEqual(coverage["covered_byte_offsets"], [4, 5, 6, 7, 16, 17, 18, 19])
        # The covered window slices *into* the two 12-byte vectors, so neither
        # field is fully covered: only one float of each vector reaches the
        # checksum. That is exactly the kind of scope statement the probe makes.
        self.assertEqual(coverage["fields_fully_covered"], [])
        self.assertEqual(coverage["fields_partially_covered"],
                         ["pa_vTranslation", "pa_aRotation"])
        self.assertIn("pa_ulButtons", coverage["fields_never_covered"])

    def test_trace_class_defaults_to_simulation(self):
        payload, _ = self._probe("actions_server_identical.csv")
        for obs in payload["observations"]:
            self.assertIn(obs["evidence_class"], ("simulation", "model"))

    def test_payload_never_claims_a_pass(self):
        payload, _ = self._probe("actions_server_identical.csv")
        _support.assert_no_false_claim(self, payload)


class CoverageUnitTests(unittest.TestCase):
    def test_differing_bytes_rejects_length_mismatch(self):
        with self.assertRaises(Exception):
            differing_bytes(b"\x00\x01", b"\x00")

    def test_layout_validation_catches_out_of_range(self):
        bad = {
            "status": "VERIFIED_107",
            "struct_size": 8,
            "fields": [{"name": "wide", "offset": 4, "size": 8}],
            "checksum_calls": [{"offset": 6, "length": 4}],
        }
        layout = parse_layout(bad, "inline")
        self.assertTrue(any("struct_size" in error for error in layout.errors))

    def test_duplicate_trace_sample_is_an_error(self):
        import tempfile
        from pathlib import Path
        text = ("#syncval-action-trace,rev=1\n#tick,slot,bytes_hex\n"
                "0,0,0000\n0,0,0000\n")
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "dup.csv"
            path.write_text(text, encoding="utf-8")
            trace = parse_action_trace(str(path))
        self.assertTrue(any("duplicate" in error for error in trace.errors))

    def test_odd_hex_payload_is_rejected(self):
        import tempfile
        from pathlib import Path
        text = "#syncval-action-trace,rev=1\n0,0,abc\n"
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "odd.csv"
            path.write_text(text, encoding="utf-8")
            trace = parse_action_trace(str(path))
        self.assertTrue(any("odd hex" in error for error in trace.errors))

    def test_trace_growth_requires_new_sample(self):
        """A missing sample must never be silently filled with the previous one."""
        import tempfile
        from pathlib import Path
        text = ("#syncval-action-trace,rev=1\n0,0,0000\n2,0,0000\n")
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "gap.csv"
            path.write_text(text, encoding="utf-8")
            trace = parse_action_trace(str(path))
        self.assertEqual(sorted(trace.samples), [(0, 0), (2, 0)])
        self.assertNotIn((1, 0), trace.samples)


if __name__ == "__main__":
    unittest.main()
