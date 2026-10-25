"""Cadence model: 20 Hz / single-slot semantics over BotTelemetry.csv."""

from __future__ import annotations

import unittest

import _support
from _support import FixtureDir, run_json, run_tool

import cadence_model
from syncval_common import parse_bot_telemetry


class CadenceFixtureTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls._fixtures = FixtureDir()
        cls.fixtures = cls._fixtures.__enter__()

    @classmethod
    def tearDownClass(cls):
        cls._fixtures.__exit__(None, None, None)

    def _run(self, name, *extra):
        return run_json("cadence_model.py", "--telemetry",
                        str(self.fixtures / name), *extra)

    # --- positive controls ------------------------------------------------
    def test_clean_telemetry_is_ok(self):
        payload, code = self._run("telemetry_ok.csv")
        self.assertEqual(payload["verdict"], "CADENCE_OK")
        self.assertEqual(code, 0)
        self.assertEqual(payload["summary"]["divergence_windows"], 0)
        self.assertEqual(payload["summary"]["tick_rate_hz_measured"], 20.0)

    def test_inactive_run_is_not_counted_as_divergence(self):
        payload, code = self._run("telemetry_inactive.csv")
        self.assertEqual(payload["verdict"], "CADENCE_OK")
        self.assertEqual(code, 0)
        self.assertTrue(all(window["class"] == "INACTIVE"
                            for window in payload["windows"]))

    # --- divergence controls ---------------------------------------------
    def test_starvation_is_detected(self):
        payload, code = self._run("telemetry_starved.csv")
        self.assertEqual(payload["verdict"], "CADENCE_DIVERGENCE")
        self.assertEqual(code, 3)
        self.assertGreater(payload["summary"]["divergence_windows"], 0)
        self.assertLess(payload["summary"]["min_window_tick_ratio"], 0.8)
        classes = payload["summary"]["class_counts"]
        self.assertIn("TIMER_STARVED", classes)

    def test_dead_timer_is_detected(self):
        payload, code = self._run("telemetry_dead.csv")
        self.assertEqual(payload["verdict"], "CADENCE_DIVERGENCE")
        self.assertEqual(code, 3)
        self.assertIn("TIMER_DEAD", payload["summary"]["class_counts"])

    def test_coalesced_actions_are_detected(self):
        payload, code = self._run("telemetry_coalesced.csv")
        self.assertEqual(payload["verdict"], "CADENCE_DIVERGENCE")
        self.assertEqual(code, 3)
        self.assertIn("ACTION_COALESCED", payload["summary"]["class_counts"])

    # --- fail-closed ------------------------------------------------------
    def test_missing_columns_manifest_is_rejected(self):
        result = run_tool("cadence_model.py", "--telemetry",
                          str(self.fixtures / "telemetry_malformed.csv"))
        self.assertEqual(result.returncode, 2)
        self.assertIn("telemetry rejected", result.stderr)

    def test_absent_data_is_unmeasurable_not_healthy(self):
        empty = self.fixtures / "telemetry_zero_rows.csv"
        empty.write_text("#bot-telemetry,rev=1\n#columns,"
                         "t_ms,ticks,actions,lp,gameon,enabled\n", encoding="utf-8")
        payload, code = self._run(empty.name)
        self.assertEqual(payload["verdict"], "CADENCE_UNMEASURABLE")
        self.assertEqual(code, 4)
        self.assertIn("silence", payload["verdict_detail"])

    # --- evidence grading -------------------------------------------------
    def test_default_evidence_class_is_simulation(self):
        payload, _ = self._run("telemetry_starved.csv")
        self.assertEqual(payload["evidence_class"], "simulation")
        for obs in payload["observations"]:
            self.assertEqual(obs["evidence_class"], "simulation")

    def test_explicit_telemetry_class_for_real_runs(self):
        payload, _ = self._run("telemetry_starved.csv",
                               "--source-class", "telemetry")
        self.assertEqual(payload["evidence_class"], "telemetry")
        self.assertTrue(all(obs["evidence_class"] == "telemetry"
                            for obs in payload["observations"]))

    def test_observations_are_present_and_typed(self):
        payload, _ = self._run("telemetry_ok.csv")
        ids = {obs["id"]: obs["value"] for obs in payload["observations"]}
        self.assertEqual(ids["cadence.divergence_windows"], 0)
        self.assertAlmostEqual(ids["cadence.tick_rate_ratio"], 1.0)
        self.assertAlmostEqual(ids["cadence.action_fidelity"], 1.0)

    def test_payload_never_claims_a_pass(self):
        payload, _ = self._run("telemetry_ok.csv")
        _support.assert_no_false_claim(self, payload)


class CadenceUnitTests(unittest.TestCase):
    def test_slot_count_change_is_flagged(self):
        import tempfile
        from pathlib import Path
        header = ("#bot-telemetry,rev=1\n#columns,t_ms,ticks,actions,lp,gameon,"
                  "enabled\n")
        rows = ["0,0,0,1,1,1", "1000,20,20,1,1,1", "2000,40,60,2,1,1"]
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "t.csv"
            path.write_text(header + "\n".join(rows) + "\n", encoding="utf-8")
            tel = parse_bot_telemetry(str(path))
        payload = cadence_model.analyse(tel, 20.0, "simulation")
        flags = [window["flags"] for window in payload["windows"]]
        self.assertIn(["LOCAL_SLOT_COUNT_CHANGED", "UNMEASURABLE_SLOT_COUNT"], flags)

    def test_irregular_sampling_is_skipped(self):
        import tempfile
        from pathlib import Path
        header = ("#bot-telemetry,rev=1\n#columns,t_ms,ticks,actions,lp,gameon,"
                  "enabled\n")
        rows = ["0,0,0,1,1,1", "20,1,1,1,1,1", "1020,21,21,1,1,1"]
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "t.csv"
            path.write_text(header + "\n".join(rows) + "\n", encoding="utf-8")
            tel = parse_bot_telemetry(str(path))
        payload = cadence_model.analyse(tel, 20.0, "simulation")
        self.assertEqual(payload["summary"]["skipped_windows"], 1)
        self.assertEqual(payload["summary"]["windows"], 1)


if __name__ == "__main__":
    unittest.main()
