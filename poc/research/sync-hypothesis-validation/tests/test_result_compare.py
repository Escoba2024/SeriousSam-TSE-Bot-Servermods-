"""Result comparison: merge, conflict detection and evidence-grade guards."""

from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

import _support
from _support import FixtureDir, make_bundle, run_json, run_tool


class ResultCompareTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls._fixtures = FixtureDir()
        cls.fixtures = cls._fixtures.__enter__()

    @classmethod
    def tearDownClass(cls):
        cls._fixtures.__exit__(None, None, None)

    # --- helpers ----------------------------------------------------------
    def _write(self, directory: Path, name: str, payload) -> Path:
        path = directory / name
        path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
        return path

    def _run(self, *inputs):
        args = []
        for kind, path in inputs:
            args.extend(["--input", "%s=%s" % (kind, path)])
        return run_json("result_compare.py", *args)

    # --- merge behaviour ---------------------------------------------------
    def test_insufficient_without_bundle_and_verdicts(self):
        with tempfile.TemporaryDirectory() as tmp:
            directory = Path(tmp)
            fp = self._write(directory, "fp.json",
                             {"tool": "fp_determinism_probe",
                              "evidence_class": "model",
                              "verdict": "MODEL_DIVERGENCE",
                              "earliest_divergence_tick": 1})
            payload, code = self._run(("fp", str(fp)))
        self.assertEqual(payload["overall"], "INSUFFICIENT")
        self.assertEqual(code, 4)
        self.assertFalse(payload["native_acceptance"])
        self.assertTrue(payload["next_actions"])

    def test_complete_bundle_and_clean_verdicts_do_not_conflict(self):
        with tempfile.TemporaryDirectory() as tmp:
            directory = Path(tmp)
            bundle = make_bundle(directory / "bundle", with_dumps=True, marker=False)
            audit, _ = run_json("evidence_bundle_audit.py", "--bundle", str(bundle))
            audit_path = self._write(directory, "audit.json", audit)
            verdicts = self._write(directory, "verdicts.json", {
                "tool": "verdict_engine", "evidence_class": "model",
                "verdict": None, "native_supported": [], "conflicts": [],
                "resolved": ["H1_ACTION_CADENCE"],
            })
            payload, code = self._run(("audit", str(audit_path)),
                                      ("verdicts", str(verdicts)))
        self.assertEqual(payload["overall"], "NO_CONFLICT")
        self.assertEqual(code, 0)
        _support.assert_no_false_claim(self, payload)

    # --- conflict rules ----------------------------------------------------
    def test_native_claim_without_bundle_is_a_conflict(self):
        with tempfile.TemporaryDirectory() as tmp:
            directory = Path(tmp)
            verdicts = self._write(directory, "verdicts.json", {
                "tool": "verdict_engine", "evidence_class": "model",
                "native_supported": ["H4_CLIENT_SIM_MODIFICATION"],
                "conflicts": [],
            })
            payload, code = self._run(("verdicts", str(verdicts)))
        rules = {conflict["rule"] for conflict in payload["conflicts"]}
        self.assertIn("NATIVE_CLAIM_WITHOUT_COMPLETE_BUNDLE", rules)
        self.assertEqual(code, 6)

    def test_simulated_bundle_with_native_claim_is_a_conflict(self):
        with tempfile.TemporaryDirectory() as tmp:
            directory = Path(tmp)
            bundle = Path(tmp) / "b"
            make_bundle(bundle, with_dumps=True, marker=True)
            audit, _ = run_json("evidence_bundle_audit.py", "--bundle", str(bundle))
            audit_path = self._write(directory, "audit.json", audit)
            verdicts = self._write(directory, "verdicts.json", {
                "tool": "verdict_engine", "evidence_class": "model",
                "native_supported": ["H4_CLIENT_SIM_MODIFICATION"], "conflicts": []})
            payload, code = self._run(("audit", str(audit_path)),
                                      ("verdicts", str(verdicts)))
        rules = {conflict["rule"] for conflict in payload["conflicts"]}
        self.assertIn("SIMULATED_INPUT_MIXED", rules)
        self.assertEqual(code, 6)

    def test_grade_inflation_is_a_conflict(self):
        with tempfile.TemporaryDirectory() as tmp:
            directory = Path(tmp)
            forged = self._write(directory, "fp_native.json", {
                "tool": "fp_determinism_probe", "evidence_class": "native",
                "verdict": "MODEL_DIVERGENCE"})
            payload, code = self._run(("fp", str(forged)))
        rules = {conflict["rule"] for conflict in payload["conflicts"]}
        self.assertIn("GRADE_INFLATION", rules)
        self.assertEqual(code, 6)

    def test_same_kind_disagreement_is_a_conflict(self):
        with tempfile.TemporaryDirectory() as tmp:
            directory = Path(tmp)
            first = self._write(directory, "c1.json", {
                "tool": "cadence_model", "evidence_class": "telemetry",
                "verdict": "CADENCE_OK"})
            second = self._write(directory, "c2.json", {
                "tool": "cadence_model", "evidence_class": "telemetry",
                "verdict": "CADENCE_DIVERGENCE"})
            payload, code = self._run(("cadence", str(first)),
                                      ("cadence", str(second)))
        rules = {conflict["rule"] for conflict in payload["conflicts"]}
        self.assertIn("TOOL_DISAGREEMENT", rules)
        self.assertEqual(code, 6)

    def test_inconsistent_timeline_is_a_conflict(self):
        with tempfile.TemporaryDirectory() as tmp:
            directory = Path(tmp)
            coverage = self._write(directory, "cov.json", {
                "tool": "checksum_coverage_probe", "evidence_class": "telemetry",
                "verdict": "CHECKSUM_VISIBLE_DIVERGENCE",
                "first_checksum_visible_divergence_tick": 137,
                "consistency_with_log": {"status": "INCONSISTENT_TOO_LATE"},
                "layout": {"status": "VERIFIED_107"}})
            payload, code = self._run(("coverage", str(coverage)))
        rules = {conflict["rule"] for conflict in payload["conflicts"]}
        self.assertIn("INCONSISTENT_TIMELINE", rules)
        self.assertEqual(code, 6)
        self.assertTrue(any("R4" in action for action in payload["next_actions"]))

    # --- usage -------------------------------------------------------------
    def test_unknown_kind_is_usage_error(self):
        result = run_tool("result_compare.py", "--input", "mystery=/dev/null")
        self.assertEqual(result.returncode, 2)

    def test_missing_input_argument_is_usage_error(self):
        result = run_tool("result_compare.py")
        self.assertEqual(result.returncode, 2)


if __name__ == "__main__":
    unittest.main()
