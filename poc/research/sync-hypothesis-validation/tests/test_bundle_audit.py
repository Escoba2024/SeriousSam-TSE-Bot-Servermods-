"""Evidence bundle audit: the contract that decides what may be called native."""

from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

import _support
from _support import FixtureDir, make_bundle, run_json, run_tool


class BundleAuditTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls._fixtures = FixtureDir()
        cls.fixtures = cls._fixtures.__enter__()

    @classmethod
    def tearDownClass(cls):
        cls._fixtures.__exit__(None, None, None)

    def _audit(self, bundle: Path, *extra):
        return run_json("evidence_bundle_audit.py", "--bundle", str(bundle), *extra)

    # --- generated fixtures can never be native ---------------------------
    def test_generated_fixture_is_never_native(self):
        for name in ("bundle_simulated", "bundle_incomplete", "bundle_lowered_kick"):
            payload, code = self._audit(self.fixtures / name)
            self.assertEqual(payload["verdict"], "SIMULATED_NEVER_NATIVE", name)
            self.assertEqual(code, 5)
            self.assertEqual(payload["evidence_class_after_audit"], "simulation")
            for obs in payload["observations"]:
                self.assertEqual(obs["evidence_class"], "simulation")

    def test_simulated_flag_alone_is_enough_to_reject(self):
        with tempfile.TemporaryDirectory() as tmp:
            bundle = Path(tmp) / "b"
            make_bundle(bundle, simulated=True, with_dumps=True, marker=False)
            payload, code = self._audit(bundle)
        self.assertEqual(payload["verdict"], "SIMULATED_NEVER_NATIVE")
        self.assertEqual(code, 5)

    # --- missing pieces ---------------------------------------------------
    def test_missing_dumps_is_insufficient(self):
        with tempfile.TemporaryDirectory() as tmp:
            bundle = Path(tmp) / "b"
            make_bundle(bundle, with_dumps=False, marker=False)
            payload, code = self._audit(bundle)
        self.assertEqual(payload["verdict"], "INSUFFICIENT")
        self.assertEqual(code, 4)
        self.assertTrue(any("dumps" in item for item in payload["missing"]))
        self.assertEqual(payload["evidence_class_after_audit"], "telemetry")
        for obs in payload["observations"]:
            self.assertNotEqual(obs["evidence_class"], "native")

    # --- safety invariants ------------------------------------------------
    def test_lowered_kick_limit_invalidates_bundle(self):
        with tempfile.TemporaryDirectory() as tmp:
            bundle = Path(tmp) / "b"
            make_bundle(bundle, with_dumps=True, marker=False, kick_limit=0)
            payload, code = self._audit(bundle)
        self.assertEqual(payload["verdict"], "INVALID")
        self.assertEqual(code, 5)
        self.assertTrue(any(problem.get("config") == "ser_iKickOnSyncBad"
                            for problem in payload["problems"]))

    def test_hash_mismatch_invalidates_bundle(self):
        with tempfile.TemporaryDirectory() as tmp:
            bundle = Path(tmp) / "b"
            make_bundle(bundle, with_dumps=True, marker=False, break_hash=True)
            payload, code = self._audit(bundle)
        self.assertEqual(payload["verdict"], "INVALID")
        self.assertEqual(code, 5)
        self.assertTrue(any(problem.get("issue") == "sha256 mismatch"
                            for problem in payload["problems"]))

    def test_binary_inventory_mismatch_is_an_observation(self):
        with tempfile.TemporaryDirectory() as tmp:
            bundle = Path(tmp) / "b"
            make_bundle(bundle, with_dumps=True, marker=False)
            manifest_path = bundle / "manifest.json"
            manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
            manifest["processes"]["clients"][0]["engine_sha256"] = "A" * 64
            manifest_path.write_text(json.dumps(manifest, indent=2) + "\n",
                                     encoding="utf-8")
            payload, _ = self._audit(bundle)
        self.assertFalse(payload["hash_inventory"]["match"])
        obs = {entry["id"]: entry["value"] for entry in payload["observations"]}
        self.assertIs(obs["build.hash_inventory_match"], False)

    # --- complete bundle ---------------------------------------------------
    def test_complete_bundle_yields_native_observations(self):
        with tempfile.TemporaryDirectory() as tmp:
            bundle = Path(tmp) / "b"
            make_bundle(bundle, with_dumps=True, marker=False)
            payload, code = self._audit(bundle)
        self.assertEqual(payload["verdict"], "COMPLETE")
        self.assertEqual(code, 0)
        self.assertEqual(payload["evidence_class_after_audit"], "native")
        self.assertEqual(payload["dumps"]["aligned_pairs"], 2)
        self.assertTrue(payload["dumps"]["entity_state_divergence"])
        self.assertFalse(payload["dumps"]["action_state_divergence"])
        self.assertEqual(payload["server_log"]["first_bad_tick"], 83.4)
        self.assertEqual(payload["server_log"]["counter_jumps"], 0)
        obs = {entry["id"]: entry for entry in payload["observations"]}
        self.assertEqual(obs["dumps.aligned_pairs"]["value"], 2)
        self.assertTrue(obs["dumps.entity_state_divergence"]["value"])
        self.assertEqual(obs["evidence.bundle_complete"]["value"], True)
        for entry in payload["observations"]:
            self.assertEqual(entry["evidence_class"], "native")

    def test_complete_bundle_never_claims_stability(self):
        with tempfile.TemporaryDirectory() as tmp:
            bundle = Path(tmp) / "b"
            make_bundle(bundle, with_dumps=True, marker=False)
            payload, _ = self._audit(bundle)
        _support.assert_no_false_claim(self, payload)

    # --- crc-diff ingestion ------------------------------------------------
    def test_crc_diff_can_refine_entity_divergence(self):
        with tempfile.TemporaryDirectory() as tmp:
            bundle = Path(tmp) / "b"
            make_bundle(bundle, with_dumps=True, marker=False)
            crc = Path(tmp) / "crc.json"
            crc.write_text(json.dumps({"entity_state_divergence": True,
                                       "first_divergent_tick": 42.5}), encoding="utf-8")
            payload, _ = self._audit(bundle, "--crc-diff", str(crc))
        self.assertEqual(payload["dumps"]["first_divergent_tick"], 42.5)

    # --- template ---------------------------------------------------------
    def test_template_round_trip_is_detectably_incomplete(self):
        with tempfile.TemporaryDirectory() as tmp:
            bundle = Path(tmp) / "b"
            bundle.mkdir()
            template = bundle / "manifest.json"
            result = run_tool("evidence_bundle_audit.py", "--bundle", str(bundle),
                              "--emit-template", str(template))
            self.assertEqual(result.returncode, 0)
            payload, code = self._audit(bundle)
        self.assertEqual(payload["verdict"], "INVALID")
        self.assertEqual(code, 5)
        self.assertIn("server.log", payload["missing"])

    def test_missing_manifest_is_invalid(self):
        with tempfile.TemporaryDirectory() as tmp:
            bundle = Path(tmp) / "empty"
            bundle.mkdir()
            payload, code = self._audit(bundle)
        self.assertEqual(payload["verdict"], "INVALID")
        self.assertEqual(code, 5)
        self.assertIn("manifest.json", payload["missing"])

    def test_missing_bundle_directory_is_usage_error(self):
        result = run_tool("evidence_bundle_audit.py", "--bundle",
                          str(self.fixtures / "does-not-exist"))
        self.assertEqual(result.returncode, 2)


if __name__ == "__main__":
    unittest.main()
