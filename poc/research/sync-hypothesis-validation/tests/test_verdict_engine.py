"""Verdict engine: grading, falsification, conflict handling, no root-cause claim."""

from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

import _support
from _support import run_json, run_tool

import verdict_engine


def obs(ident, value, evidence_class="model", source="test"):
    return {"id": ident, "value": value, "evidence_class": evidence_class,
            "source": source}


def verdicts(payload, ident):
    for entry in payload["hypotheses"]:
        if entry["id"] == ident:
            return entry
    raise AssertionError("hypothesis not found: %s" % ident)


class GradingTests(unittest.TestCase):
    def test_offline_evidence_caps_at_model_supported(self):
        payload = verdict_engine.evaluate([
            obs("cadence.divergence_windows", 5, "model"),
            obs("cadence.tick_rate_ratio", 0.5, "model"),
            obs("cadence.action_fidelity", 1.0, "model"),
        ])
        entry = verdicts(payload, "H1_ACTION_CADENCE")
        self.assertEqual(entry["verdict"], "MODEL_SUPPORTED")
        self.assertIn("offline", entry["reason"])

    def test_runtime_evidence_can_reach_native_supported(self):
        payload = verdict_engine.evaluate([
            obs("cadence.divergence_windows", 5, "telemetry"),
            obs("cadence.tick_rate_ratio", 0.5, "telemetry"),
            obs("cadence.action_fidelity", 1.0, "telemetry"),
        ])
        entry = verdicts(payload, "H1_ACTION_CADENCE")
        self.assertEqual(entry["verdict"], "NATIVE_SUPPORTED")
        self.assertIn("H1_ACTION_CADENCE", payload["native_supported"])

    def test_missing_observations_are_not_tested(self):
        payload = verdict_engine.evaluate([])
        self.assertEqual(payload["counts"].get("NOT_TESTED"), len(payload["hypotheses"]))
        self.assertFalse(payload["resolved"])

    def test_partially_measured_is_inconclusive(self):
        payload = verdict_engine.evaluate([obs("cadence.tick_rate_ratio", 1.0)])
        entry = verdicts(payload, "H1_ACTION_CADENCE")
        self.assertEqual(entry["verdict"], "INCONCLUSIVE")
        self.assertTrue(entry["missing_observations"])

    def test_refutation(self):
        payload = verdict_engine.evaluate([
            obs("cadence.divergence_windows", 0, "telemetry"),
            obs("cadence.tick_rate_ratio", 1.0, "telemetry"),
            obs("cadence.action_fidelity", 1.0, "telemetry"),
        ])
        entry = verdicts(payload, "H1_ACTION_CADENCE")
        self.assertEqual(entry["verdict"], "REFUTED")
        self.assertIn("H1_ACTION_CADENCE", payload["refuted"])

    def test_support_and_refute_together_is_conflict(self):
        payload = verdict_engine.evaluate([
            obs("coverage.verdict", "CHECKSUM_VISIBLE_DIVERGENCE", "telemetry"),
            obs("coverage.log_consistency", "INCONSISTENT_TOO_LATE", "telemetry"),
        ])
        entry = verdicts(payload, "H2_ACTION_COMPOSITION")
        self.assertEqual(entry["verdict"], "CONFLICT")
        self.assertIn("H2_ACTION_COMPOSITION", payload["conflicts"])

    def test_observation_disagreement_is_reported(self):
        payload = verdict_engine.evaluate([
            obs("cadence.tick_rate_ratio", 1.0, "telemetry", "run-a"),
            obs("cadence.tick_rate_ratio", 0.4, "telemetry", "run-b"),
            obs("cadence.divergence_windows", 0, "telemetry"),
            obs("cadence.action_fidelity", 1.0, "telemetry"),
        ])
        self.assertEqual(len(payload["observation_disagreements"]), 1)
        entry = verdicts(payload, "H1_ACTION_CADENCE")
        # Disagreeing duplicates must not be collapsed into a synthetic value.
        self.assertFalse(entry["refute_fires"])
        self.assertIn("OBSERVATION_DISAGREEMENT", payload["conflicts"])

    def test_assumptions_are_not_evaluated(self):
        payload = verdict_engine.evaluate([])
        ids = {entry["id"] for entry in payload["hypotheses"]}
        self.assertNotIn("A1_CHECKSUM_SCOPE", ids)

    def test_never_reports_a_confirmed_root_cause(self):
        payload = verdict_engine.evaluate([
            obs("dumps.entity_state_divergence", True, "native"),
            obs("dumps.aligned_pairs", 3, "native"),
        ])
        self.assertEqual(verdicts(payload, "H4_CLIENT_SIM_MODIFICATION")["verdict"],
                         "NATIVE_SUPPORTED")
        self.assertEqual(payload["root_cause_status"], "NOT_ESTABLISHED")
        _support.assert_no_false_claim(self, payload)

    def test_invalid_evidence_class_is_rejected(self):
        with self.assertRaises(Exception):
            verdict_engine.evaluate([obs("cadence.tick_rate_ratio", 1.0, "vibes")])


class CliTests(unittest.TestCase):
    def _write(self, directory: Path, name: str, payload) -> Path:
        path = directory / name
        path.write_text(json.dumps(payload), encoding="utf-8")
        return path

    def test_fp_output_can_be_fed_directly(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = self._write(Path(tmp), "fp.json",
                               {"observations": [obs("fp.earliest_divergence_tick",
                                                     1, "model")]})
            payload, code = run_json("verdict_engine.py", str(path))
        self.assertEqual(code, 4)      # nothing resolved -> incomplete
        self.assertEqual(verdicts(payload, "H3_FP_MODEL")["verdict"], "INCONCLUSIVE")

    def test_conflict_sets_exit_code_six(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = self._write(Path(tmp), "cov.json", {"observations": [
                obs("coverage.verdict", "CHECKSUM_VISIBLE_DIVERGENCE", "telemetry"),
                obs("coverage.log_consistency", "INCONSISTENT_TOO_LATE", "telemetry"),
            ]})
            payload, code = run_json("verdict_engine.py", str(path))
        self.assertEqual(code, 6)
        self.assertEqual(payload["conflicts"], ["H2_ACTION_COMPOSITION"])

    def test_input_without_observations_is_usage_error(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = self._write(Path(tmp), "empty.json", {"nothing": True})
            result = run_tool("verdict_engine.py", str(path))
        self.assertEqual(result.returncode, 2)
        self.assertIn("no observations", result.stderr)


if __name__ == "__main__":
    unittest.main()
