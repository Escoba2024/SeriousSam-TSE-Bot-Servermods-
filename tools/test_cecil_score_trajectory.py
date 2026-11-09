import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

PATH = Path(__file__).with_name("analyze_cecil_qualification.py")
SPEC = importlib.util.spec_from_file_location("cecil_score_analysis", PATH)
ANALYZER = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(ANALYZER)


def report(bots=1):
    return dict(schema_version=1, bots=bots, dll_sha256="a" * 64, elapsed_s=30,
                status="DURATION_ACTIVITY_SYNC_PASS_BEHAVIOR_REVIEW_REQUIRED",
                gate=False, errors=[])


def records(values, bots=1):
    return [{"sample": dict(elapsed_s=t, scores={
        "Dev-" + str(i): value if i == 1 else 0 for i in range(1, bots + 1)})}
        for t, value in enumerate(values)]


class ScoreTrajectory(unittest.TestCase):
    def analyze(self, rows, bots=1):
        return ANALYZER.analyze(rows, report(bots))

    def test_gain_then_loss_is_visible_despite_zero_net_score(self):
        result = self.analyze(records([0, 1, 0]))
        self.assertEqual(result["score_deltas"], {"Dev-1": 0})
        self.assertEqual(result["score_trajectory"]["Dev-1"], dict(
            status="OBSERVED", first=0, last=0, min=0, max=1, change_count=2,
            positive_change_count=1, negative_change_count=1,
            observed_samples=3, missing_samples=0))
        self.assertFalse(result["qualified"])
        self.assertEqual(result["duration_gate"]["status"], "NOT_MET")

    def test_counts_changes_not_score_units_or_repeated_values(self):
        result = self.analyze(records([0, 0, 3, 3, -2, -2]))["score_trajectory"]["Dev-1"]
        self.assertEqual((result["first"], result["last"], result["min"], result["max"]),
                         (0, -2, -2, 3))
        self.assertEqual((result["change_count"], result["positive_change_count"],
                          result["negative_change_count"]), (2, 1, 1))

    def test_expected_identities_only_for_each_supported_population(self):
        for bots in (1, 4, 8):
            with self.subTest(bots=bots):
                rows = records([0, 1], bots)
                for row in rows:
                    row["sample"]["scores"]["private external name"] = 900
                result = self.analyze(rows, bots)["score_trajectory"]
                self.assertEqual(set(result), {"Dev-" + str(i) for i in range(1, bots + 1)})
                self.assertEqual(result["Dev-1"]["positive_change_count"], 1)
                self.assertEqual(result["Dev-" + str(bots)]["observed_samples"], 2)

    def test_missing_samples_remain_open_and_do_not_bridge_changes(self):
        for missing in ({}, {"scores": {}}, {"scores": {"Dev-2": 1}}):
            with self.subTest(missing=missing):
                rows = records([0, 0, 1])
                rows[1]["sample"] = dict(elapsed_s=1, **missing)
                result = self.analyze(rows)
                trajectory = result["score_trajectory"]["Dev-1"]
                self.assertEqual(trajectory["status"], "OPEN")
                self.assertEqual((trajectory["first"], trajectory["last"],
                                  trajectory["min"], trajectory["max"]), (0, 1, 0, 1))
                self.assertEqual(trajectory["observed_samples"], 2)
                self.assertEqual(trajectory["missing_samples"], 1)
                self.assertEqual(trajectory["change_count"], 0)
                self.assertEqual(result["score_deltas"], {"Dev-1": 1})

    def test_no_observations_never_invent_scores_for_expected_bots(self):
        result = self.analyze([], 8)["score_trajectory"]
        self.assertEqual(len(result), 8)
        for trajectory in result.values():
            self.assertEqual(trajectory["status"], "OPEN")
            self.assertEqual(trajectory["observed_samples"], 0)
            self.assertTrue(all(trajectory[k] is None for k in ("first", "last", "min", "max")))
        one = self.analyze(records([-1]))["score_trajectory"]["Dev-1"]
        self.assertEqual(one["status"], "OPEN")
        self.assertEqual(one["first"], -1)
        self.assertEqual(one["change_count"], 0)

    def test_partially_missing_identities_remain_separately_open(self):
        rows = records([0, 1], 4)
        del rows[0]["sample"]["scores"]["Dev-2"]
        del rows[1]["sample"]["scores"]["Dev-3"]
        result = self.analyze(rows, 4)
        self.assertEqual(result["score_deltas"], {"Dev-1": 1, "Dev-4": 0})
        for name in ("Dev-2", "Dev-3"):
            self.assertEqual(result["score_trajectory"][name]["status"], "OPEN")
            self.assertEqual(result["score_trajectory"][name]["observed_samples"], 1)

    def test_malformed_or_nonfinite_expected_scores_rejected_even_midwindow(self):
        for bad in (None, "1", True, [], {}, float("nan"), float("inf"), -float("inf")):
            with self.subTest(value=bad):
                rows = records([0, bad, 0])
                with self.assertRaises(ValueError):
                    self.analyze(rows)
        for bad in (None, [], "scores"):
            with self.subTest(scores=bad):
                rows = records([0, 1, 0])
                rows[1]["sample"]["scores"] = bad
                with self.assertRaises(ValueError):
                    self.analyze(rows)

    def test_cli_is_read_only_and_rejects_invalid_score_evidence(self):
        with tempfile.TemporaryDirectory(prefix="cecil-score-test-") as directory:
            root = Path(directory)
            meta = root / "report.json"
            series = root / "timeseries.jsonl"
            meta.write_text(json.dumps(report()))
            series.write_text("".join(json.dumps(row) + "\n" for row in records([0, 1, 0])))
            original = meta.read_bytes(), series.read_bytes()
            process = subprocess.run([sys.executable, "-B", str(PATH), directory],
                                     capture_output=True, text=True)
            self.assertEqual(process.returncode, 0, process.stderr)
            result = json.loads(process.stdout)
            self.assertEqual(result["score_trajectory"]["Dev-1"]["positive_change_count"], 1)
            self.assertFalse(result["qualified"])
            self.assertEqual((meta.read_bytes(), series.read_bytes()), original)
            series.write_text("".join(json.dumps(row) + "\n" for row in records([0, None, 0])))
            process = subprocess.run([sys.executable, "-B", str(PATH), directory],
                                     capture_output=True, text=True)
            self.assertEqual(process.returncode, 2)
            self.assertIn("Evidence error", process.stderr)
            self.assertEqual(process.stdout, "")


if __name__ == "__main__":
    unittest.main()
