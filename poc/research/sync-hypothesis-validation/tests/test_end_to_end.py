"""End-to-end pipeline tests on synthetic data.

These tests chain generator -> probes -> bundle audit -> verdict engine ->
result comparison, exactly as documented in README.md. They also check the two
discriminating outcomes the native plan expects:

* entity divergence with identical action bytes  -> H4 supported, H2 refuted
* checksum-visible action divergence             -> H2 supported, H4 not supported
"""

from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

import _support
from _support import FixtureDir, make_bundle, run_json


def _verdict(payload, ident):
    for entry in payload["hypotheses"]:
        if entry["id"] == ident:
            return entry["verdict"]
    raise AssertionError("hypothesis not found: %s" % ident)


class PipelineTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls._fixtures = FixtureDir()
        cls.fixtures = cls._fixtures.__enter__()

    @classmethod
    def tearDownClass(cls):
        cls._fixtures.__exit__(None, None, None)

    def test_documented_pipeline_runs_on_synthetic_fixtures(self):
        with tempfile.TemporaryDirectory() as tmp:
            directory = Path(tmp)
            fp, code_fp = run_json("fp_determinism_probe.py", "--ticks", "200",
                                   "--out", str(directory / "fp.json"))
            cadence, code_cad = run_json(
                "cadence_model.py", "--telemetry",
                str(self.fixtures / "telemetry_starved.csv"),
                "--source-class", "simulation", "--out", str(directory / "cad.json"))
            coverage, code_cov = run_json(
                "checksum_coverage_probe.py",
                "--client-trace", str(self.fixtures / "actions_client.csv"),
                "--server-trace", str(self.fixtures / "actions_server_outside_diff.csv"),
                "--layout", str(self.fixtures / "layout_verified.json"),
                "--out", str(directory / "cov.json"))
            audit, code_audit = run_json(
                "evidence_bundle_audit.py", "--bundle",
                str(self.fixtures / "bundle_simulated"),
                "--out", str(directory / "audit.json"))

            self.assertEqual((code_fp, code_cad, code_cov, code_audit), (3, 3, 3, 5))

            verdicts, code_verdicts = run_json(
                "verdict_engine.py",
                str(directory / "fp.json"), str(directory / "cad.json"),
                str(directory / "cov.json"), str(directory / "audit.json"),
                "--out", str(directory / "verdicts.json"))
            # No conflict (the artifacts agree), but nothing is native either.
            self.assertEqual(code_verdicts, 0)

            payload, code_compare = run_json(
                "result_compare.py",
                "--input", "fp=%s" % (directory / "fp.json"),
                "--input", "cadence=%s" % (directory / "cad.json"),
                "--input", "coverage=%s" % (directory / "cov.json"),
                "--input", "audit=%s" % (directory / "audit.json"),
                "--input", "verdicts=%s" % (directory / "verdicts.json"),
                "--out", str(directory / "compare.json"))

        self.assertEqual(code_compare, 4)
        self.assertEqual(payload["overall"], "INSUFFICIENT")
        self.assertIn("bundle_complete", payload["missing_evidence"])
        # No offline artifact may be graded as native.
        self.assertEqual(verdicts["native_supported"], [])
        self.assertEqual(coverage["evidence_class"], "simulation")
        self.assertEqual(audit["evidence_class_after_audit"], "simulation")
        _support.assert_no_false_claim(self, payload)
        _support.assert_no_false_claim(self, verdicts)

    def test_entity_divergence_scenario_supports_h4_only(self):
        with tempfile.TemporaryDirectory() as tmp:
            directory = Path(tmp)
            bundle = make_bundle(directory / "bundle", with_dumps=True, marker=False)
            audit, _ = run_json("evidence_bundle_audit.py", "--bundle", str(bundle))
            coverage, _ = run_json(
                "checksum_coverage_probe.py",
                "--client-trace", str(self.fixtures / "actions_client.csv"),
                "--server-trace", str(self.fixtures / "actions_server_identical.csv"),
                "--layout", str(self.fixtures / "layout_verified.json"),
                "--trace-class", "telemetry")
            audit_path = directory / "audit.json"
            coverage_path = directory / "coverage.json"
            audit_path.write_text(json.dumps(audit), encoding="utf-8")
            coverage_path.write_text(json.dumps(coverage), encoding="utf-8")
            verdicts, code = run_json("verdict_engine.py", str(audit_path),
                                      str(coverage_path))

        self.assertEqual(audit["verdict"], "COMPLETE")
        self.assertEqual(_verdict(verdicts, "H4_CLIENT_SIM_MODIFICATION"),
                         "NATIVE_SUPPORTED")
        self.assertEqual(_verdict(verdicts, "H2_ACTION_COMPOSITION"), "REFUTED")
        self.assertEqual(_verdict(verdicts, "H6_LOG_ARTIFACT"), "REFUTED")
        self.assertEqual(code, 0)
        self.assertEqual(verdicts["root_cause_status"], "NOT_ESTABLISHED")
        self.assertIn("H4_CLIENT_SIM_MODIFICATION", verdicts["native_supported"])

    def test_action_divergence_scenario_supports_h2_only(self):
        with tempfile.TemporaryDirectory() as tmp:
            directory = Path(tmp)
            bundle = make_bundle(directory / "bundle", with_dumps=True, marker=False)
            # Remove the entity difference so only the action path remains.
            client_dump = bundle / "dumps" / "client" / "c420.txt"
            client_dump.write_text(
                client_dump.read_text(encoding="utf-8")
                .replace("3.0625", "3.0"), encoding="utf-8")
            audit, _ = run_json("evidence_bundle_audit.py", "--bundle", str(bundle))
            coverage, _ = run_json(
                "checksum_coverage_probe.py",
                "--client-trace", str(self.fixtures / "actions_client.csv"),
                "--server-trace", str(self.fixtures / "actions_server_visible_diff.csv"),
                "--layout", str(self.fixtures / "layout_verified.json"),
                "--first-bad-tick", "200", "--trace-class", "telemetry")
            audit_path = directory / "audit.json"
            coverage_path = directory / "coverage.json"
            audit_path.write_text(json.dumps(audit), encoding="utf-8")
            coverage_path.write_text(json.dumps(coverage), encoding="utf-8")
            verdicts, _ = run_json("verdict_engine.py", str(audit_path),
                                   str(coverage_path))

        self.assertFalse(audit["dumps"]["entity_state_divergence"])
        self.assertEqual(_verdict(verdicts, "H2_ACTION_COMPOSITION"),
                         "NATIVE_SUPPORTED")
        self.assertEqual(_verdict(verdicts, "H4_CLIENT_SIM_MODIFICATION"), "REFUTED")
        self.assertEqual(verdicts["root_cause_status"], "NOT_ESTABLISHED")

    def test_generated_fixtures_never_yield_native_support(self):
        with tempfile.TemporaryDirectory() as tmp:
            directory = Path(tmp)
            audit, _ = run_json("evidence_bundle_audit.py", "--bundle",
                                str(self.fixtures / "bundle_simulated"))
            audit_path = directory / "audit.json"
            audit_path.write_text(json.dumps(audit), encoding="utf-8")
            verdicts, code = run_json("verdict_engine.py", str(audit_path))
        self.assertEqual(verdicts["native_supported"], [])
        self.assertEqual(verdicts["model_supported"], [])
        self.assertEqual(code, 4)
        self.assertNotIn("NATIVE_SUPPORTED", verdicts["counts"])


if __name__ == "__main__":
    unittest.main()
