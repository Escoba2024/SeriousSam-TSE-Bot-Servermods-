import importlib.util
import json
import subprocess
import sys
import tempfile
from pathlib import Path
import unittest

PATH = Path(__file__).with_name("analyze_cecil_qualification.py")


def sample(t, cpu=6, rss=100000):
    return {"sample": {"elapsed_s": t, "players": 1, "map": "Red Station",
            "scores": {"Dev-1": int(t)}, "cpu_percent": {"botA": cpu},
            "host_percent": 40, "processes": {"botA": {
                "rss_kib": rss, "start_ticks": 10, "cpu_s": t}}}}


def state(t, **changes):
    row = dict(elapsed_s=t, tick=int(t * 20) + 1, alive=1, ready=1,
               pos=[t, 0, 0], shots=int(t), pickups=0, deaths=0, respawns=0,
               vis=1, owned=3, current=2, wanted=2, rays=4)
    row.update(changes)
    return {"slot": "botA:0", "state": row}


def event(t, text):
    return {"event": {"elapsed_s": t, "role": "botA", "line": text}}


def report():
    return dict(schema_version=1, status="DURATION_ACTIVITY_SYNC_PASS_BEHAVIOR_REVIEW_REQUIRED",
                bots=1, elapsed_s=30, required_duration_s=30, gate=False,
                dll_sha256="a" * 64, errors=[], port=25650,
                query_identity=dict(gamename="serioussamse", gamever="1.07", hostport="25650", mapname="Red Station"))


class QualificationEvidence(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.module = None
        if PATH.exists():
            spec = importlib.util.spec_from_file_location("cecil_analysis", PATH)
            cls.module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(cls.module)

    def analyze(self, rows, **kwargs):
        self.assertIsNotNone(self.module, "offline analyzer is not implemented")
        return self.module.analyze(rows, kwargs.pop("report", report()), **kwargs)

    def test_short_smoke_never_becomes_qualification(self):
        result = self.analyze([sample(0), state(0), sample(30), state(30)])
        self.assertFalse(result["qualified"])
        self.assertEqual(result["duration_gate"]["status"], "NOT_MET")
        self.assertEqual(result["duration_gate"]["required_s"], 3600)
        self.assertEqual(result["slots"]["botA:0"]["fire_actions_delta"], 30)
        self.assertNotIn('"pos":', json.dumps(result))

    def test_running_or_failed_monitor_cannot_pass(self):
        for status in ["RUNNING", "FAILED"]:
            meta = report(); meta["status"] = status
            result = self.analyze([state(0), state(1)], report=meta)
            self.assertEqual(result["monitor_status"], status)
            self.assertFalse(result["qualified"])

    def test_stationary_firing_at_visible_target_is_separate(self):
        rows = [state(t, pos=[0, 0, 0]) for t in range(13)]
        meta=report();meta["elapsed_s"]=12
        result = self.analyze(rows,report=meta)["slots"]["botA:0"]
        self.assertEqual(result["max_stationary_s"], 12)
        self.assertEqual(result["max_unexplained_stationary_s"], 0)
        self.assertEqual(result["stationary_review"], "NO_OBSERVED_BREACH")
        rows = [state(t, pos=[0, 0, 0], vis=0) for t in range(13)]
        result = self.analyze(rows)["slots"]["botA:0"]
        self.assertEqual(result["stationary_review"], "REVIEW_REQUIRED")
        self.assertEqual(result["max_unexplained_stationary_s"], 12)
        self.assertEqual(result["max_unexplained_stationary_window_s"], [0, 12])

    def test_small_steps_accumulate_from_stationary_anchor(self):
        rows = [state(t, pos=[t * .1, 0, 0], shots=0, vis=0) for t in range(20)]
        self.assertLess(self.analyze(rows)["slots"]["botA:0"]["max_stationary_s"], 4)

    def test_death_respawn_and_first_activity_are_observations(self):
        rows = [state(0), state(1, alive=0, deaths=1),
                state(2, alive=0, deaths=1),
                state(3, deaths=1, respawns=1, pos=[0, 0, 0], shots=0, vis=0),
                state(4, deaths=1, respawns=1, shots=0, vis=0)]
        result = self.analyze(rows)["slots"]["botA:0"]
        self.assertEqual(result["deaths_delta"], 1)
        self.assertEqual(result["respawns_delta"], 1)
        self.assertEqual(result["observed_dead_intervals_s"], [2])
        self.assertEqual(result["respawn_activity_delays_s"], [1])
        self.assertEqual(result["respawn_gate"], "NOT_PROVEN")

    def test_counter_reset_gap_and_missing_slot_cannot_hide(self):
        result = self.analyze([state(0), state(1, shots=-1), state(20)])
        slot = result["slots"]["botA:0"]
        self.assertIn("shots", slot["counter_resets"])
        self.assertEqual(slot["max_sample_gap_s"], 19)
        self.assertEqual(slot["fire_actions_delta"], None)
        meta = report(); meta["bots"] = 4
        self.assertEqual(self.analyze([state(0)], report=meta)["missing_slots"],
                         ["botA:1", "botA:2", "botA:3"])

    def test_first_ten_weapon_goals_are_not_cherry_picked(self):
        rows = []
        for i in range(12):
            rows.append(event(i * 2, "[CecilGoal] local=0 tick=%d entity=%d kind=0 weapon=8 anchor=1" % (i * 40, 100 + i)))
            rows.append(event(i * 2 + 1, "[CecilGoalEnd] local=0 tick=%d entity=%d reason=unavailable" % (i * 40 + 20, 100 + i)))
        result = self.analyze(rows)["weapon_scenario"]
        self.assertEqual([x["entity"] for x in result["first_ten"]], list(range(100, 110)))
        self.assertEqual(result["confirmed_reached"], 0)
        self.assertEqual(result["gate"], "NOT_PROVEN")
        self.assertTrue(all(x["outcome"] == "unavailable" for x in result["first_ten"]))

    def test_inventory_gain_is_not_proof_of_item_identity(self):
        rows = [event(0, "[CecilGoal] local=0 tick=1 entity=100 kind=0 weapon=8 anchor=1"),
                event(1, "[CecilPickup] local=0 tick=21 old=3 owned=131 current=2"),
                event(1, "[CecilGoalEnd] local=0 tick=21 entity=100 reason=unavailable")]
        r = self.analyze(rows)["weapon_scenario"]
        self.assertTrue(r["first_ten"][0]["compatible_inventory_gain"])
        self.assertEqual(r["confirmed_reached"], 0)

    def test_resource_boundaries_are_frozen_and_rss_needs_full_window(self):
        baseline = {"cpu_percent": {"botA": {"median": 5, "p95": 5}}}
        rows = [sample(t, cpu=6) for t in range(20)]
        r = self.analyze(rows, baseline=baseline)["resources"]
        self.assertEqual(r["processes"]["botA"]["cpu_limit"], "WITHIN_OBSERVED_LIMIT")
        self.assertEqual(r["processes"]["botA"]["rss_gate"], "NOT_PROVEN")
        rows[-1] = sample(19, cpu=20); rows[-2] = sample(18, cpu=20)
        r = self.analyze(rows, baseline=baseline)["resources"]
        self.assertEqual(r["processes"]["botA"]["cpu_limit"], "EXCEEDS_LIMIT")
        rows[-1]["sample"]["host_percent"] = 85
        rows[-2]["sample"]["host_percent"] = 85
        self.assertEqual(self.analyze(rows)["resources"]["host_limit"], "EXCEEDS_LIMIT")

    def test_disk_reserve_and_no_swap_require_complete_samples(self):
        rows=[sample(0),sample(1)]
        for row in rows:
            row['sample'].update(disk_free_bytes=8*2**30,memory=dict(available_kib=2048,swap_total_kib=0,swap_used_kib=0))
        r=self.analyze(rows)['resources']
        self.assertEqual(r['disk_gate'],'WITHIN_OBSERVED_LIMIT')
        self.assertEqual(r['swap_gate'],'NOT_APPLICABLE_NO_SWAP')
        rows[1]['sample']['disk_free_bytes']-=1
        self.assertEqual(self.analyze(rows)['resources']['disk_gate'],'EXCEEDS_LIMIT')
        del rows[1]['sample']['memory']
        self.assertEqual(self.analyze(rows)['resources']['swap_gate'],'NOT_PROVEN')
    def test_swap_activity_requires_review_and_rejects_invalid_samples(self):
        rows=[sample(0),sample(1)]
        for i,row in enumerate(rows):row['sample']['memory']=dict(available_kib=2048,swap_total_kib=2048,swap_used_kib=1024*i)
        r=self.analyze(rows)['resources']
        self.assertEqual(r['swap_gate'],'REVIEW_REQUIRED')
        self.assertEqual(r['swap_net_used_mib'],1)
        rows[1]['sample']['memory']['swap_used_kib']=4096
        with self.assertRaises(ValueError):self.analyze(rows)
    def test_rss_full_postwarmup_window_uses_trend_and_net(self):
        rows = [sample(t, rss=100000 + t * 40) for t in range(0, 4201, 60)]
        r = self.analyze(rows)["resources"]["processes"]["botA"]
        self.assertEqual(r["rss_gate"], "EXCEEDS_LIMIT")
        self.assertGreater(r["rss_trend_mib_min"], 1)
        self.assertGreater(r["rss_net_mib"], 32)

    def test_identity_and_nonfinite_values_rejected(self):
        bad = state(0); bad["state"]["pos"][0] = float("nan")
        with self.assertRaises(ValueError): self.analyze([bad])
        with self.assertRaises(ValueError): self.analyze([state(1), state(0)])
        rows = [sample(0), sample(1)]
        rows[1]["sample"]["processes"]["botA"]["start_ticks"] = 20
        result = self.analyze(rows)
        self.assertIn("botA", result["resources"]["process_identity_changes"])

    def test_nonweapon_goal_supersedes_weapon_attempt(self):
        rows = [event(0, "[CecilGoal] local=0 tick=1 entity=100 kind=0 weapon=8 anchor=1"),
                event(1, "[CecilGoal] local=0 tick=21 entity=200 kind=1 weapon=0 anchor=2"),
                event(2, "[CecilPickup] local=0 tick=41 old=3 owned=131 current=2")]
        r = self.analyze(rows)["weapon_scenario"]["first_ten"][0]
        self.assertEqual(r["outcome"], "superseded")
        self.assertFalse(r["compatible_inventory_gain"])

    def test_rss_irregular_sample_times_still_cover_hour(self):
        rows = [sample(t + .3, rss=100000) for t in range(0, 4261, 60)]
        rows[-1]["sample"]["elapsed_s"] += .4
        r = self.analyze(rows)["resources"]["processes"]["botA"]
        self.assertEqual(r["rss_gate"], "WITHIN_OBSERVED_LIMIT")

    def test_missing_graph_and_ray_budget_remain_visible(self):
        r = self.analyze([state(0, ready=0, rays=17)])["slots"]["botA:0"]
        self.assertEqual(r["inactive_graph_samples"], 1)
        self.assertEqual(r["ray_budget_breaches"], 1)

    def test_changed_process_identity_invalidates_cpu_comparison(self):
        rows = [sample(0), sample(1)]
        rows[1]["sample"]["processes"]["botA"]["start_ticks"] = 20
        baseline = {"cpu_percent": {"botA": {"median": 5, "p95": 5}}}
        r = self.analyze(rows, baseline=baseline)["resources"]["processes"]["botA"]
        self.assertEqual(r["cpu_limit"], "NOT_PROVEN")

    def test_optional_pickup_mask_requires_same_goal_and_new_weapon_bit(self):
        for entity, expected in [(100, True), (101, False)]:
            rows = [event(0, "[CecilGoal] local=0 tick=1 entity=100 kind=0 weapon=8 anchor=1"),
                    event(1, "[CecilPickup] local=0 tick=21 old=3 owned=131 current=2 goal_entity=%d goal_picked=1 pos=(0,0,0)" % entity)]
            r = self.analyze(rows)["weapon_scenario"]
            self.assertEqual(r["first_ten"][0]["same_goal_pick_mask_and_gain"], expected)
            self.assertEqual(r["confirmed_reached"], 0)
            self.assertNotIn("pos", r["first_ten"][0])

    def test_cli_reads_existing_files_and_rejects_truncated_json(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "report.json").write_text(json.dumps(report()))
            series = root / "timeseries.jsonl"
            series.write_text(json.dumps(state(0)) + "\n")
            original = series.read_bytes()
            process = subprocess.run([sys.executable, str(PATH), directory], capture_output=True, text=True)
            self.assertEqual(process.returncode, 0, process.stderr)
            parsed = json.loads(process.stdout)
            self.assertFalse(parsed["qualified"])
            self.assertEqual(len(parsed["input_sha256"]["timeseries"]), 64)
            self.assertEqual(series.read_bytes(), original)
            series.write_text('{"state":')
            process = subprocess.run([sys.executable, str(PATH), directory], capture_output=True, text=True)
            self.assertEqual(process.returncode, 2)
            self.assertEqual(process.stdout, "")

    def test_multibot_goals_do_not_qualify_singlebot_scenario(self):
        meta = report(); meta["bots"] = 8
        result = self.analyze([], report=meta)
        self.assertEqual(result["duration_gate"]["required_s"], 7200)
        self.assertEqual(result["weapon_scenario"]["gate"], "NOT_APPLICABLE_POPULATION")

    def test_duration_requires_coverage_of_the_entire_window(self):
        meta = report(); meta.update(elapsed_s=3600, gate=True)
        for times in (range(2880), range(721, 3601), [0, 1, 3599, 3600]):
            with self.subTest(first=times[0], last=times[-1]):
                result = self.analyze([state(t) for t in times], report=meta)
                self.assertEqual(result["telemetry_coverage"]["status"], "INCOMPLETE")
                self.assertNotEqual(result["duration_gate"]["status"], "DURATION_ONLY_MET")
                self.assertEqual(result["slots"]["botA:0"]["stationary_review"], "NOT_PROVEN_INCOMPLETE_COVERAGE")

    def test_complete_slots_and_query_samples_are_needed_for_duration(self):
        meta = report(); meta.update(elapsed_s=3600, gate=True)
        rows = [state(t) for t in range(0, 3601, 5)]
        result = self.analyze(rows, report=meta)
        self.assertEqual(result["telemetry_coverage"]["status"], "INCOMPLETE")
        self.assertEqual(result["sample_coverage"]["status"], "MISSING")
        result = self.analyze(rows + [sample(t) for t in range(0, 3601, 5)], report=meta)
        self.assertEqual(result["telemetry_coverage"]["status"], "FULL_WINDOW_COVERED")
        self.assertEqual(result["duration_gate"]["status"], "DURATION_ONLY_MET")
        self.assertFalse(result["qualified"])

    def test_crlf_goal_end_reason_has_no_carriage_return(self):
        rows = [event(0, "[CecilGoal] local=0 tick=1 entity=100 kind=0 weapon=8 anchor=1\r"),
                event(1, "[CecilGoalEnd] local=0 tick=21 entity=100 reason=unavailable\r")]
        goal = self.analyze(rows)["weapon_scenario"]["first_ten"][0]
        self.assertEqual(goal["outcome"], "unavailable")

    def test_failed_monitor_or_missing_identity_cannot_attest_long_duration(self):
        rows = [state(t) for t in range(0, 3601, 5)] + [sample(t) for t in range(0, 3601, 5)]
        for change in ({"status":"FAILED"}, {"errors":[{"role":"botA"}]}, {"query_identity":None}):
            with self.subTest(change=change):
                meta=report();meta.update(elapsed_s=3600,gate=True);meta.update(change)
                result=self.analyze(rows,report=meta)
                self.assertNotEqual(result["duration_gate"]["status"],"DURATION_ONLY_MET")

    def test_population_or_map_contamination_cannot_attest_long_duration(self):
        for changed in ({"players":2}, {"map":"Yodeller"}):
            rows = [state(t) for t in range(0, 3601, 5)] + [sample(t) for t in range(0, 3601, 5)]
            rows[-1]["sample"].update(changed)
            meta=report();meta.update(elapsed_s=3600,gate=True)
            result=self.analyze(rows,report=meta)
            self.assertEqual(result["scenario_integrity"],"FAILED")
            self.assertNotEqual(result["duration_gate"]["status"],"DURATION_ONLY_MET")


if __name__ == "__main__":
    unittest.main()
