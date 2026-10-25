#!/usr/bin/env python3
"""Offline tests for the behavior-QA harness (poc/research/behavior-qa).

Two layers:
  1. Pure-Python tests of the orchestrator logic (aggregation, kill_rate,
     regression detection, reporting helpers). These ALWAYS run and need no
     compiled binary.
  2. Integration tests that drive ./qa_sim. These are SKIPPED automatically if
     the binary is not built, so the suite is safe to run anywhere.

Nothing here touches the retail game, a server, or the network. Passing this
suite is an OFFLINE result and never a native Retail-1.07 acceptance.

Run:  python3 -m unittest test_behavior_qa -v      (or)  python3 test_behavior_qa.py
"""
from __future__ import annotations

import json
import os
import subprocess
import unittest

import run_behavior_qa as rbq

HERE = os.path.dirname(os.path.abspath(__file__))
QA_SIM = os.path.join(HERE, "qa_sim")
HAVE_BIN = os.path.exists(QA_SIM)


def _run(args):
    return subprocess.run([QA_SIM] + args, cwd=HERE, check=True,
                          capture_output=True, text=True)


def _mk_run(scenario, tier, persona, seed, outcome, **metrics):
    m = {"digest": f"{seed:x}", "wasted_fire_invisible": 0, "los_queries_max": 1}
    m.update(metrics)
    return {"kind": "run", "scenario": scenario, "tier": tier, "persona": persona,
            "seed": seed, "outcome": outcome, "metrics": m}


# --------------------------------------------------------------------------- #
# Pure-Python orchestrator logic (no binary required)
# --------------------------------------------------------------------------- #

class TestAggregation(unittest.TestCase):
    def test_groups_and_means(self):
        runs = [
            _mk_run("gallery_static", 5, 2, 1, "kill", hit_rate=0.8, sim_dps=40.0),
            _mk_run("gallery_static", 5, 2, 2, "kill", hit_rate=0.6, sim_dps=30.0),
            _mk_run("gallery_static", 1, 2, 3, "timeout", hit_rate=0.1, sim_dps=5.0),
        ]
        agg = rbq.aggregate(runs, ["scenario", "tier"])
        self.assertAlmostEqual(agg[("gallery_static", 5)]["hit_rate"]["mean"], 0.7)
        self.assertAlmostEqual(agg[("gallery_static", 5)]["sim_dps"]["mean"], 35.0)
        self.assertAlmostEqual(agg[("gallery_static", 1)]["hit_rate"]["mean"], 0.1)
        self.assertEqual(agg[("gallery_static", 5)]["_n"], 2)

    def test_kill_rate_from_outcomes(self):
        runs = [
            _mk_run("reaction_static", 3, 2, 1, "kill"),
            _mk_run("reaction_static", 3, 2, 2, "kill"),
            _mk_run("reaction_static", 3, 2, 3, "timeout"),
            _mk_run("reaction_static", 3, 2, 4, "death"),
        ]
        agg = rbq.aggregate(runs, ["scenario", "tier"])
        cell = agg[("reaction_static", 3)]
        self.assertAlmostEqual(cell["kill_rate"]["mean"], 0.5)
        self.assertAlmostEqual(cell["death_rate"]["mean"], 0.25)

    def test_mean_of_missing_is_none(self):
        self.assertIsNone(rbq.mean_of({}, ("x", 1), "hit_rate"))

    def test_std_present_when_multiple(self):
        runs = [
            _mk_run("s", 1, 0, 1, "kill", hit_rate=0.2),
            _mk_run("s", 1, 0, 2, "kill", hit_rate=0.8),
        ]
        agg = rbq.aggregate(runs, ["scenario", "tier"])
        self.assertIn("std", agg[("s", 1)]["hit_rate"])


class TestRegressionDetection(unittest.TestCase):
    def _base(self):
        return {
            "invariants": {"I1": True, "I4-aim-monotonic": True},
            "tier": {"gallery_static|5": {"hit_rate": 0.80, "sim_dps": 40.0}},
            "weapon_dominance": {"laser": 27, "cannon": 15},
        }

    def test_clean_when_identical(self):
        self.assertEqual(rbq.detect_regressions(self._base(), self._base()), [])

    def test_invariant_flip_detected(self):
        cur = self._base()
        cur["invariants"]["I4-aim-monotonic"] = False
        regs = rbq.detect_regressions(cur, self._base())
        self.assertTrue(any("I4-aim-monotonic" in r for r in regs))

    def test_metric_beyond_tolerance_detected(self):
        cur = self._base()
        cur["tier"]["gallery_static|5"]["hit_rate"] = 0.40  # -50%
        regs = rbq.detect_regressions(cur, self._base())
        self.assertTrue(any("hit_rate" in r for r in regs))

    def test_metric_within_tolerance_ignored(self):
        cur = self._base()
        cur["tier"]["gallery_static|5"]["hit_rate"] = 0.78  # -2.5%
        regs = rbq.detect_regressions(cur, self._base())
        self.assertFalse(any("hit_rate" in r for r in regs))

    def test_weapon_dominance_change_detected(self):
        cur = self._base()
        cur["weapon_dominance"] = {"laser": 10, "sniper": 20, "cannon": 14}
        regs = rbq.detect_regressions(cur, self._base())
        self.assertTrue(any("WEAPON_DOMINANCE" in r for r in regs))


class TestReportHelpers(unittest.TestCase):
    def test_report_check_and_failed(self):
        rep = rbq.Report()
        rep.check("A", "passes", True, "ok")
        rep.check("B", "fails", False, "bad")
        self.assertEqual(len(rep.checks), 2)
        self.assertEqual([c["id"] for c in rep.failed], ["B"])

    def test_weapon_dominance_histogram(self):
        curve = {"rows": [{"best_name": "laser"}, {"best_name": "laser"},
                          {"best_name": "cannon"}]}
        self.assertEqual(rbq.weapon_dominance(curve), {"laser": 2, "cannon": 1})


# --------------------------------------------------------------------------- #
# Integration tests against ./qa_sim (skipped if not built)
# --------------------------------------------------------------------------- #

@unittest.skipUnless(HAVE_BIN, "qa_sim not built (run `make` first)")
class TestQaSimBinary(unittest.TestCase):
    def test_selftest_passes(self):
        r = subprocess.run([QA_SIM, "--selftest"], cwd=HERE,
                           capture_output=True, text=True)
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        self.assertIn("QA SELFTEST PASS", r.stdout)

    def test_list_has_expected_scenarios(self):
        d = json.loads(_run(["--list"]).stdout.strip())
        names = {i["name"] for i in d["items"]}
        for required in ["gallery_static", "reaction_static", "tracking_strafe",
                         "retreat_pressure", "multi_2v1", "long_range_lead",
                         "hitscan_latency", "weapon_boundary", "duel", "firefight"]:
            self.assertIn(required, names)

    def test_determinism_same_seed(self):
        a = json.loads(_run(["--scenario", "tracking_strafe", "--tier", "3",
                             "--persona", "2", "--seed", "77"]).stdout.strip())
        b = json.loads(_run(["--scenario", "tracking_strafe", "--tier", "3",
                             "--persona", "2", "--seed", "77"]).stdout.strip())
        self.assertEqual(a["metrics"]["digest"], b["metrics"]["digest"])

    def test_seed_changes_outcome(self):
        a = json.loads(_run(["--scenario", "tracking_strafe", "--tier", "3",
                             "--persona", "2", "--seed", "77"]).stdout.strip())
        b = json.loads(_run(["--scenario", "tracking_strafe", "--tier", "3",
                             "--persona", "2", "--seed", "78"]).stdout.strip())
        self.assertNotEqual(a["metrics"]["digest"], b["metrics"]["digest"])

    def test_no_blind_fire_and_los_budget(self):
        out = _run(["--sweep", "--scenarios", "cover_reacquire,multi_3v1",
                    "--tiers", "1,2,3,4,5", "--personas", "2", "--seeds", "3"]).stdout
        caps = {1: 4, 2: 5, 3: 6, 4: 7, 5: 8}
        n = 0
        for line in out.splitlines():
            r = json.loads(line)
            n += 1
            self.assertEqual(r["metrics"]["wasted_fire_invisible"], 0,
                             "policy fired without LOS")
            self.assertLessEqual(r["metrics"]["los_queries_max"], caps[r["tier"]])
        self.assertGreater(n, 0)

    def test_aim_monotonic_gallery(self):
        out = _run(["--sweep", "--scenarios", "gallery_static", "--tiers",
                    "1,2,3,4,5", "--personas", "2", "--seeds", "16"]).stdout
        err = {}
        for line in out.splitlines():
            r = json.loads(line)
            err.setdefault(r["tier"], []).append(r["metrics"]["true_err_visible_mean"])
        means = [sum(err[t]) / len(err[t]) for t in (1, 2, 3, 4, 5)]
        for i in range(4):
            self.assertLess(means[i + 1], means[i],
                            f"aim error not monotonic: {means}")

    def test_weapon_curve_deterministic_and_structured(self):
        a = json.loads(_run(["--weapon-curve", "--range-pref", "0"]).stdout.strip())
        b = json.loads(_run(["--weapon-curve", "--range-pref", "0"]).stdout.strip())
        self.assertEqual(a, b)
        self.assertGreaterEqual(len(a["rows"]), 40)
        for row in a["rows"]:
            self.assertIn(row["best"], range(1, 15))
            self.assertGreaterEqual(row["margin"], 0.0)

    def test_weapon_curve_dominance_characterisation(self):
        # CHARACTERISATION: pins the CURRENT loadout-table behaviour (laser is
        # the top-scoring weapon over most of 2..45 m). If a rebalance changes
        # this, the test fails ON PURPOSE - that is the regression signal the
        # findings document asks the RDC dev to expect. See docs.
        curve = json.loads(_run(["--weapon-curve", "--range-pref", "0"]).stdout.strip())
        hist = rbq.weapon_dominance(curve)
        top = max(hist, key=hist.get)
        self.assertEqual(top, "laser",
                         "dominant weapon changed from laser; loadout table was rebalanced")
        self.assertGreater(hist["laser"], len(curve["rows"]) // 2)

    def test_duel_expert_beats_beginner(self):
        out = _run(["--duel", "--duel-a", "5:2", "--duel-b", "1:2",
                    "--rounds", "11"]).stdout
        summary = next(json.loads(l) for l in out.splitlines()
                       if json.loads(l)["kind"] == "duel_summary")
        self.assertGreaterEqual(summary["wins_a"] * 2, summary["rounds"])

    def test_perf_within_budget(self):
        d = json.loads(_run(["--perf", "--candidates", "8", "--ticks", "5000"]).stdout.strip())
        for row in d["rows"]:
            self.assertLess(row["ns_per_tick"], 50_000)


if __name__ == "__main__":
    unittest.main(verbosity=2)
