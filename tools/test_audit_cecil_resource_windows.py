"""Offline resource arithmetic/coverage contracts; no game processes involved."""
import copy
import hashlib
import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

PATH = Path(__file__).with_name("audit_cecil_resource_windows.py")
ROLES = ("server", "botA", "botB")


def pins():
    common = dict(map="Red Station", bots=8, settings="settings-sha256",
                  seed=123, render="null", namespace="private-isolated",
                  concurrent_load="five-production-plus-matched-control")
    return dict(baseline=common.copy(), candidate=common.copy())


def fixture(rate=10, cadence=5, offset=0, duration=360, native=False):
    rows = []
    for index in range(int(duration / cadence) + 1):
        t = index * cadence
        process = {role: dict(cpu_s=t * rate / 100, start_ticks=10 + i)
                   for i, role in enumerate(ROLES)}
        if native:
            rows.append(dict(sample=dict(elapsed_s=t + offset, map="Red Station",
                                         players=8, processes=process)))
        else:
            rows.append(dict(elapsed_s=t + offset,
                             cpu_s={r: p["cpu_s"] for r, p in process.items()},
                             start_ticks={r: p["start_ticks"] for r, p in process.items()}))
    return rows if native else dict(samples=rows, pids=dict(zip(ROLES, (101, 102, 103))))


class ResourceWindows(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tool = None
        if PATH.exists():
            spec = importlib.util.spec_from_file_location("resource_windows", PATH)
            cls.tool = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(cls.tool)

    def audit(self, baseline=None, candidate=None, **kwargs):
        self.assertIsNotNone(self.tool, "resource-window audit is not implemented")
        return self.tool.analyze(
            baseline if baseline is not None else fixture(),
            candidate if candidate is not None else fixture(cadence=1, offset=600, native=True),
            scenario_pins=kwargs.pop("scenario_pins", pins()), **kwargs)

    def test_fixed_three_windows_and_default_warmup(self):
        result = self.audit()
        self.assertFalse(result["qualified"])
        self.assertEqual(result["cpu_comparison"], "WITHIN_OBSERVED_LIMIT")
        self.assertEqual([w["candidate_range_s"] for w in result["windows"]],
                         [[600, 720], [720, 840], [840, 960]])
        self.assertEqual([w["baseline_range_s"] for w in result["windows"]],
                         [[0, 120], [120, 240], [240, 360]])
        for window in result["windows"]:
            self.assertEqual(window["roles"]["botA"]["candidate"]["samples"], 24)
            self.assertAlmostEqual(window["roles"]["botA"]["candidate"]["median"], 10)
        self.assertEqual(result["pooled"]["candidate"]["samples"], 216)

    def test_native_bursts_are_aggregated_to_five_seconds_before_percentiles(self):
        candidate = fixture(rate=0, cadence=1, offset=600, native=True)
        for i, row in enumerate(candidate):
            # One 50%-CPU second followed by four idle seconds = 10% per 5s.
            cpu = ((i + 4) // 5) * .5
            for process in row["sample"]["processes"].values():
                process["cpu_s"] = cpu
        result = self.audit(candidate=candidate)
        self.assertEqual(result["cpu_comparison"], "WITHIN_OBSERVED_LIMIT")
        self.assertAlmostEqual(result["roles"]["botA"]["candidate"]["p95"], 10)

    def test_uses_actual_elapsed_seconds_not_assumed_five_second_denominator(self):
        baseline = fixture()
        for row in baseline["samples"]:
            row["elapsed_s"] *= 1.001
            row["cpu_s"] = {role: row["elapsed_s"] * .1 for role in ROLES}
        result = self.audit(baseline=baseline)
        self.assertEqual(result["cpu_comparison"], "WITHIN_OBSERVED_LIMIT")
        self.assertAlmostEqual(result["roles"]["botA"]["baseline"]["median"], 10)

    def test_nearest_rank_p95_and_twenty_percent_boundary(self):
        candidate = fixture(rate=12, cadence=1, offset=600, native=True)
        result = self.audit(candidate=candidate)
        self.assertEqual(result["cpu_comparison"], "WITHIN_OBSERVED_LIMIT")
        self.assertAlmostEqual(result["roles"]["botA"]["median_ratio"], 1.2)
        # 24 bins: two high bins put nearest-rank P95 (rank 23) above limit.
        for row in candidate:
            t = row["sample"]["elapsed_s"] - 600
            extra = max(0, min(10, t - 110)) * .01
            row["sample"]["processes"]["botA"]["cpu_s"] += extra
        result = self.audit(candidate=candidate)
        first = result["windows"][0]["roles"]["botA"]
        self.assertAlmostEqual(first["candidate"]["median"], 12)
        self.assertAlmostEqual(first["candidate"]["p95"], 13)
        self.assertEqual(first["status"], "EXCEEDS_LIMIT")
        self.assertEqual(result["cpu_comparison"], "EXCEEDS_LIMIT")

    def test_each_role_must_pass_even_if_pooled_distribution_hides_regression(self):
        candidate = fixture(rate=1, cadence=1, offset=600, native=True)
        for row in candidate:
            t = row["sample"]["elapsed_s"] - 600
            row["sample"]["processes"]["botB"]["cpu_s"] = t * .2
        result = self.audit(candidate=candidate)
        self.assertEqual(result["roles"]["botB"]["status"], "EXCEEDS_LIMIT")
        self.assertEqual(result["cpu_comparison"], "EXCEEDS_LIMIT")

    def test_missing_native_interior_sample_is_not_interpolated(self):
        candidate = fixture(cadence=1, offset=600, native=True)
        del candidate[2]  # All nominal 5s endpoints still exist.
        result = self.audit(candidate=candidate)
        self.assertEqual(result["cpu_comparison"], "OPEN")
        self.assertIn("SAMPLE_GAP", str(result["windows"][0]["candidate_coverage"]))
        self.assertLess(result["windows"][0]["roles"]["botA"]["candidate"]["samples"], 24)

    def test_missing_baseline_endpoint_and_censored_tail_are_not_synthesized(self):
        baseline = fixture()
        del baseline["samples"][3]
        baseline["samples"].pop()
        result = self.audit(baseline=baseline)
        self.assertEqual(result["cpu_comparison"], "OPEN")
        self.assertEqual(result["windows"][2]["baseline_coverage"]["status"], "INCOMPLETE")

    def test_restart_inside_bin_is_detected_even_when_endpoints_match(self):
        candidate = fixture(cadence=1, offset=600, native=True)
        candidate[2]["sample"]["processes"]["botA"]["start_ticks"] = 999
        result = self.audit(candidate=candidate)
        self.assertEqual(result["cpu_comparison"], "OPEN")
        self.assertIn("IDENTITY_CHANGE", str(result["windows"][0]["candidate_coverage"]))

    def test_pid_change_with_unchanged_start_tick_is_also_detected(self):
        candidate = fixture(cadence=1, offset=600, native=True)
        for i, row in enumerate(candidate):
            row["sample"]["processes"]["botA"]["pid"] = 100 if i < 2 else 101
        self.assertIn("IDENTITY_CHANGE", str(self.audit(candidate=candidate)))

    def test_counter_reset_and_missing_role_fail_closed(self):
        for mutate in (lambda rows: rows[2]["sample"]["processes"]["botA"].update(cpu_s=0),
                       lambda rows: rows[2]["sample"]["processes"].pop("botA")):
            candidate = fixture(cadence=1, offset=600, native=True)
            mutate(candidate)
            self.assertEqual(self.audit(candidate=candidate)["cpu_comparison"], "OPEN")

    def test_legacy_root_pid_only_baseline_is_descriptive_not_identity_proof(self):
        baseline = fixture()
        for row in baseline["samples"]:
            del row["start_ticks"]
        result = self.audit(baseline=baseline)
        self.assertEqual(result["cpu_comparison"], "OPEN")
        self.assertAlmostEqual(result["roles"]["botA"]["baseline"]["median"], 10)
        self.assertIn("IDENTITY_UNOBSERVED", str(result))

    def test_scenario_mismatch_missing_pin_and_actual_map_change_stay_open(self):
        mismatched = pins(); mismatched["candidate"]["seed"] = 124
        missing = pins(); del missing["candidate"]["render"]
        for supplied in (mismatched, missing, None):
            result = self.audit(scenario_pins=supplied)
            self.assertEqual(result["comparability"]["status"], "OPEN")
            self.assertEqual(result["cpu_comparison"], "OPEN")
        candidate = fixture(cadence=1, offset=600, native=True)
        candidate[2]["sample"]["map"] = "Hole"
        self.assertEqual(self.audit(candidate=candidate)["comparability"]["status"], "OPEN")

    def test_zero_baseline_does_not_divide_by_zero_or_serialize_infinity(self):
        self.assertEqual(self.audit(baseline=fixture(rate=0),
                                   candidate=fixture(rate=0, cadence=1, offset=600, native=True))["cpu_comparison"],
                         "WITHIN_OBSERVED_LIMIT")
        result = self.audit(baseline=fixture(rate=0))
        self.assertEqual(result["cpu_comparison"], "EXCEEDS_LIMIT")
        self.assertIsNone(result["roles"]["botA"]["median_ratio"])
        json.dumps(result, allow_nan=False)

    def test_selected_boundary_sample_and_report_map_must_match_pins(self):
        candidate = fixture(cadence=1, offset=599.5, duration=361, native=True)
        # A nearest observed boundary just before 600 is used in CPU arithmetic.
        candidate[0]["sample"]["map"] = "Hole"
        self.assertEqual(self.audit(candidate=candidate)["comparability"]["status"], "OPEN")
        self.assertEqual(self.audit(candidate_report=dict(query_identity=dict(mapname="Hole")))["comparability"]["status"], "OPEN")

    def test_present_native_report_requires_observed_query_identity(self):
        for report in ({}, {"bots": 8}, {"bots": 8, "query_identity": None},
                       {"bots": 8, "query_identity": {}},
                       {"bots": 8, "query_identity": {"mapname": None}},
                       {"bots": 8, "query_identity": {"mapname": ""}}):
            with self.subTest(report=report):
                result = self.audit(candidate_report=report)
                self.assertEqual(result["comparability"]["status"], "OPEN")
                self.assertEqual(result["cpu_comparison"], "OPEN")
                self.assertIn("REPORT_QUERY_IDENTITY_UNOBSERVED", result["comparability"]["reasons"])

    def test_declared_pid_cannot_identify_a_different_measured_process(self):
        candidate = fixture(cadence=1, offset=600, native=True)
        for row in candidate:
            row["sample"]["processes"]["botA"]["pid"] = 200
        result = self.audit(candidate=candidate, candidate_report=dict(pids=dict(botA=201)))
        self.assertEqual(result["cpu_comparison"], "OPEN")
        self.assertIn("DECLARED_PID_MISMATCH", str(result))

    def test_invalid_order_nonfinite_and_negative_counters_are_rejected(self):
        for changes in ("order", "nan", "negative"):
            candidate = fixture(cadence=1, offset=600, native=True)
            if changes == "order":
                candidate[1], candidate[2] = candidate[2], candidate[1]
            else:
                candidate[2]["sample"]["processes"]["botA"]["cpu_s"] = float("nan") if changes == "nan" else -1
            with self.assertRaises(ValueError):
                self.audit(candidate=candidate)

    def test_api_does_not_mutate_evidence(self):
        baseline = fixture(); candidate = fixture(cadence=1, offset=600, native=True)
        before = copy.deepcopy((baseline, candidate))
        self.audit(baseline, candidate)
        self.assertEqual((baseline, candidate), before)

    def test_cli_reports_exact_input_hashes_and_does_not_touch_inputs(self):
        self.assertTrue(PATH.exists(), "resource-window CLI is not implemented")
        with tempfile.TemporaryDirectory() as tmp:
            directory = Path(tmp)
            files = dict(baseline=directory / "baseline.json", candidate=directory / "candidate.jsonl",
                         scenario_pins=directory / "pins.json", candidate_report=directory / "report.json")
            files["baseline"].write_text(json.dumps(fixture()))
            files["candidate"].write_text("\n".join(json.dumps(r) for r in fixture(cadence=1, offset=600, native=True)))
            files["scenario_pins"].write_text(json.dumps(pins()))
            files["candidate_report"].write_text(json.dumps(dict(
                dll_sha256="a" * 64, bots=8, query_identity=dict(mapname="Red Station"))))
            before = {key: path.read_bytes() for key, path in files.items()}
            cmd = [sys.executable, str(PATH)]
            for key, path in files.items():
                cmd.extend(["--" + key.replace("_", "-"), str(path)])
            run = subprocess.run(cmd, capture_output=True, text=True, check=True)
            result = json.loads(run.stdout)
            self.assertEqual(result["cpu_comparison"], "WITHIN_OBSERVED_LIMIT")
            for key, raw in before.items():
                self.assertEqual(result["inputs"][key]["sha256"], hashlib.sha256(raw).hexdigest())
                self.assertEqual(files[key].read_bytes(), raw)
            self.assertEqual(result["artifacts"]["candidate_dll_sha256"], "a" * 64)
            self.assertEqual(set(directory.iterdir()), set(files.values()))


if __name__ == "__main__":
    unittest.main()
