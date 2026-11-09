"""Offline raw-log evidence tests; no game, services, network or real /proc."""
import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

SCRIPT = Path(__file__).with_name("audit_cecil_native_log.py")
EPOCH = dict(pid=123, start_ticks=456, dll_sha256="a" * 64, world="Levels/Test.wld", map_crc32="1234abcd")
LOAD = "[CecilLoad] policy=cecil-human-v1 schema=1 world=Levels/Test.wld ready=1 nodes=2 map_crc=1234abcd nav_crc=abcd1234\n"


def state(tick, **changes):
    fields = dict(local=0, tick=tick, generation=1, entity=30, alive=1, pos="(0,0,0)", owned=3,
                  shots=0, vis=0, deaths=0, respawns=1, current=2, wanted=2)
    fields.update(changes)
    return "[CecilState] " + " ".join(str(k) + "=" + str(v) for k, v in fields.items()) + "\n"


def goal(tick, entity=10, weapon=8, kind=0):
    return f"[CecilGoal] local=0 tick={tick} entity={entity} kind={kind} weapon={weapon} anchor=1 pos=(1,0,0)\n"


def pickup(tick, **changes):
    fields = dict(local=0, tick=tick, old=3, owned=131, current=8, goal_entity=10, goal_picked=1, pos="(1,0,0)")
    fields.update(changes)
    return "[CecilPickup] " + " ".join(str(k) + "=" + str(v) for k, v in fields.items()) + "\n"


def ending(tick, entity=10, reason="unavailable"):
    return f"[CecilGoalEnd] local=0 tick={tick} entity={entity} reason={reason}\n"


def spawn(tick, generation=1, count=1):
    return f"[CecilSpawn] local=0 tick={tick} entity=30 generation={generation} respawns={count} pos=(0,0,0)\n"


def death(tick, generation=1, count=1):
    return f"[CecilDeath] local=0 tick={tick} entity=30 generation={generation} deaths={count}\n"


class NativeLogAudit(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.module = None
        if SCRIPT.exists():
            spec = importlib.util.spec_from_file_location("native_log_audit", SCRIPT)
            cls.module = importlib.util.module_from_spec(spec); spec.loader.exec_module(cls.module)

    def audit(self, text, **kwargs):
        self.assertIsNotNone(self.module, "Raw native-log analyzer not implemented")
        return self.module.audit(text.splitlines(), EPOCH, useful_weapon_mask=1 << 7, **kwargs)

    def test_complete_startup_events_are_retained_and_never_full_qualification(self):
        result = self.audit(LOAD + goal(2) + pickup(3) + ending(4) + state(20))
        self.assertFalse(result["qualified"])
        self.assertEqual(result["epoch_evidence"], "CONSISTENT_FRESH_PREFIX")
        goals = result["weapon_scenario"]["first_ten"]
        self.assertEqual(goals[0]["tick"], 2)
        self.assertEqual(goals[0]["acquisition"], "OWNERSHIP_GAIN_MATCHING_GOAL_AND_MASK")
        self.assertEqual(goals[0]["end_reason"], "unavailable")

    def test_first_ten_selections_are_frozen_including_repeated_entities(self):
        text = LOAD + state(20)
        for i in range(12):
            text += goal(30 + i * 2) + ending(31 + i * 2, reason="timeout")
        result = self.audit(text)["weapon_scenario"]
        self.assertEqual(result["observed_weapon_selections"], 12)
        self.assertEqual([g["tick"] for g in result["first_ten"]], list(range(30, 50, 2)))
        self.assertEqual(result["corroborated_goal_count"], 0)
        self.assertNotIn("PASS", result["gate"])

    def test_nine_matching_gains_are_reported_for_native_review(self):
        text = LOAD + state(20)
        for i in range(10):
            text += goal(30 + i * 3)
            if i < 9: text += pickup(31 + i * 3)
            text += ending(32 + i * 3)
        result = self.audit(text)["weapon_scenario"]
        self.assertEqual(result["corroborated_goal_count"], 9)
        self.assertEqual(result["gate"], "OWNERSHIP_CORROBORATION_MET_REVIEW_REQUIRED")

    def test_mask_only_wrong_goal_or_wrong_weapon_never_become_acquisitions(self):
        for changes, expected in ((dict(owned=3), "MASK_ONLY"),
                                  (dict(goal_entity=11), "NO_MATCHING_ACQUISITION"),
                                  (dict(owned=259), "MASK_ONLY")):
            with self.subTest(changes=changes):
                result = self.audit(LOAD + state(20) + goal(21) + pickup(22, **changes) + ending(23))
                self.assertEqual(result["weapon_scenario"]["first_ten"][0]["acquisition"], expected)
                self.assertEqual(result["weapon_scenario"]["corroborated_goal_count"], 0)

    def test_respawning_item_gain_without_stay_mask_is_still_corroboration(self):
        result = self.audit(LOAD + state(20) + goal(21) + pickup(22, goal_picked=0) + ending(23))
        row = result["weapon_scenario"]["first_ten"][0]
        self.assertEqual(row["acquisition"], "OWNERSHIP_GAIN_MATCHING_GOAL")
        self.assertEqual(row["distance_from_selected_item_m"], 0)
        self.assertEqual(result["weapon_scenario"]["corroborated_goal_count"], 1)
        self.assertEqual(result["weapon_scenario"]["confirmed_native_receipts"], 0)

    def test_nonweapon_goal_supersedes_prior_weapon_attempt(self):
        result = self.audit(LOAD + state(20) + goal(21) + goal(22, kind=1, weapon=0) + pickup(23))
        self.assertEqual(result["weapon_scenario"]["first_ten"][0]["end_reason"], "superseded")
        self.assertEqual(result["weapon_scenario"]["corroborated_goal_count"], 0)

    def test_generation_boundary_cannot_keep_old_goal_active(self):
        text = LOAD + state(20) + goal(21) + state(40, generation=2, respawns=2) + pickup(41)
        result = self.audit(text)["weapon_scenario"]
        self.assertEqual(result["first_ten"][0]["end_reason"], "spawn_or_generation_boundary")
        self.assertEqual(result["corroborated_goal_count"], 0)

    def test_exact_lifecycle_closes_old_goal_before_next_sample(self):
        text = LOAD + spawn(1) + state(20) + goal(21) + death(22) + spawn(23, generation=2, count=2)
        text += pickup(24) + state(40, generation=2, respawns=2, deaths=1)
        result = self.audit(text)["weapon_scenario"]
        self.assertEqual(result["corroborated_goal_count"], 0)
        self.assertEqual(result["first_ten"][0]["end_reason"], "observed_death")

    def test_new_goal_selected_after_exact_spawn_survives_first_new_state(self):
        text = LOAD + spawn(1) + state(20) + death(22) + spawn(23, generation=2, count=2)
        text += goal(24, entity=11) + state(40, generation=2, respawns=2, deaths=1) + pickup(41, goal_entity=11)
        result = self.audit(text)["weapon_scenario"]
        self.assertEqual(result["corroborated_goal_count"], 1)
        self.assertIsNone(result["first_ten"][0]["end_reason"])

    def test_death_censor_lower_bound_uses_last_alive_not_first_dead_sample(self):
        result = self.audit(LOAD + state(20) + state(800, alive=0, deaths=1))
        spawn = result["spawn_pickups"]["first_ten"][0]
        self.assertEqual(spawn["pickup_latency_bounds_s"], [0, None])

    def test_initial_spawn_already_dead_is_retained_in_prospective_cohort(self):
        text = LOAD + state(20, alive=0, deaths=1) + state(40, deaths=1, respawns=2, generation=2) + pickup(60)
        result = self.audit(text)["spawn_pickups"]
        self.assertEqual(result["cohort_size"], 2)
        self.assertEqual(result["first_ten"][0]["pickup_observation"], "NO_PICKUP_BEFORE_OBSERVED_DEATH_OR_RESET")
        self.assertEqual(result["first_ten"][0]["pickup_latency_bounds_s"], [0, None])
        self.assertEqual(result["first_ten"][1]["pickup_observation"], "OBSERVED_NEW_USEFUL_WEAPON_BIT")

    def test_dead_with_zero_respawns_is_prespawn_not_a_failed_cohort_member(self):
        text = LOAD + state(20, alive=0, respawns=0) + state(40, respawns=1, generation=2) + pickup(60)
        audited = self.audit(text)
        result = audited["spawn_pickups"]
        self.assertEqual(result["cohort_size"], 1)
        self.assertEqual(result["first_ten"][0]["respawn_counter"], 1)
        self.assertEqual(result["first_ten"][0]["pickup_latency_bounds_s"], [1, 2])
        self.assertEqual(audited["death_respawn"]["observed_dead_episodes"], 0)

    def test_initial_spawn_and_respawn_pickup_have_explicit_time_bounds(self):
        result = self.audit(LOAD + state(20) + pickup(100) + state(200, alive=0, deaths=1)
                            + state(220, alive=0, deaths=1)
                            + state(240, generation=2, respawns=2, deaths=1) + pickup(300)
                            + state(320, generation=2, respawns=2, deaths=1))
        spawns = result["spawn_pickups"]["first_ten"]
        self.assertEqual(spawns[0]["spawn_bounds_s"], [0, 1])
        self.assertEqual(spawns[0]["pickup_latency_bounds_s"], [4, 5])
        self.assertEqual(spawns[1]["spawn_bounds_s"], [11, 12])
        self.assertEqual(spawns[1]["pickup_latency_bounds_s"], [3, 4])

    def test_missing_pickup_is_right_censored_and_not_dropped(self):
        result = self.audit(LOAD + state(20) + state(800))
        row = result["spawn_pickups"]["first_ten"][0]
        self.assertEqual(row["pickup_observation"], "RIGHT_CENSORED_NO_PICKUP")
        self.assertEqual(row["pickup_latency_bounds_s"], [39, None])
        self.assertEqual(result["spawn_pickups"]["cohort_size"], 1)
        self.assertNotIn("WITHIN", result["spawn_pickups"]["gate"])

    def test_ten_spawn_upper_bounds_can_establish_frozen_latency_limits(self):
        text = LOAD + state(20) + pickup(100)
        for i in range(1, 10):
            text += state(200*i, alive=0, deaths=i, respawns=i, generation=i)
            text += state(200*i+20, deaths=i, respawns=i+1, generation=i+1)
            text += pickup(200*i+100)
        result = self.audit(text)["spawn_pickups"]
        self.assertEqual(result["cohort_size"], 10)
        self.assertEqual(result["median_latency_bounds_s"], [4, 5])
        self.assertEqual(result["p95_latency_bounds_s"], [4, 5])
        self.assertEqual(result["gate"], "UPPER_BOUNDS_WITHIN_FROZEN_LIMITS_REVIEW_REQUIRED")

    def test_optional_exact_spawn_death_events_tighten_intervals(self):
        text = LOAD + state(20, alive=0, respawns=0) + spawn(25, generation=2)
        text += state(40, generation=2) + pickup(100) + death(205, generation=2)
        text += state(220, alive=0, deaths=1, generation=2) + spawn(235, generation=3, count=2)
        text += state(240, deaths=1, generation=3, respawns=2) + pickup(300)
        result = self.audit(text)
        spawns = result["spawn_pickups"]["first_ten"]
        self.assertEqual(spawns[0]["spawn_bounds_s"], [1.25, 1.25])
        self.assertEqual(spawns[0]["pickup_latency_bounds_s"], [3.75, 3.75])
        self.assertEqual(spawns[1]["pickup_latency_bounds_s"], [3.25, 3.25])
        self.assertEqual(result["death_respawn"]["respawn_delay_bounds_s"], [[1.5, 1.5]])

    def test_exact_initial_spawn_after_earlier_alive_or_skipped_count_is_inconclusive(self):
        for text in (LOAD + state(20) + spawn(30) + pickup(40),
                     LOAD + spawn(1, count=2) + state(20, respawns=2) + pickup(40)):
            with self.subTest(text=text[-80:]):
                result = self.audit(text)
                self.assertTrue(result["issues"])
                self.assertEqual(result["spawn_pickups"]["gate"], "INCONCLUSIVE")

    def test_goal_mapping_and_absolute_deadline_are_preserved_as_evidence(self):
        text = LOAD + state(20) + goal(21).rstrip() + " mapped=1 deadline=42.25\n" + pickup(22)
        row = self.audit(text)["weapon_scenario"]["first_ten"][0]
        self.assertEqual(row["mapped"], 1)
        self.assertEqual(row["deadline"], 42.25)

    def test_death_counter_is_count_only_and_respawn_timing_is_bounded(self):
        result = self.audit(LOAD + state(20) + state(40, alive=0, deaths=1)
                            + state(60, alive=0, deaths=1) + state(80, deaths=1, respawns=2, generation=2))
        deaths = result["death_respawn"]
        self.assertEqual(deaths["death_counter_delta"], 1)
        self.assertEqual(deaths["observed_dead_episodes"], 1)
        self.assertEqual(deaths["respawn_delay_bounds_s"], [[1, 3]])

    def test_missing_prefix_map_change_and_tick_reset_are_inconclusive(self):
        for text in (state(2000), LOAD.replace("1234abcd", "ffffffff") + state(20),
                     LOAD + state(20) + LOAD + state(40), LOAD + state(40) + state(20)):
            with self.subTest(text=text[:40]):
                result = self.audit(text)
                self.assertNotEqual(result["epoch_evidence"], "CONSISTENT_FRESH_PREFIX")
                self.assertEqual(result["status"], "INCONCLUSIVE")

    def test_native_errors_malformed_rows_and_nonfinite_positions_are_retained_as_issues(self):
        for extra in ("SYNCBAD count=1\n", "[CecilGoal] local=0 tick=21\n", state(40, pos="(nan,0,0)"),
                      state(20), goal(21, weapon=0)):
            result = self.audit(LOAD + state(20) + extra)
            self.assertTrue(result["issues"])
            self.assertFalse(result["qualified"])

    def test_wrong_explicit_epoch_pins_are_rejected(self):
        self.assertIsNotNone(self.module, "Raw native-log analyzer not implemented")
        for changes in (dict(pid=0), dict(start_ticks=0), dict(dll_sha256="wrong"), dict(map_crc32="bad")):
            epoch = dict(EPOCH); epoch.update(changes)
            with self.subTest(changes=changes), self.assertRaises(ValueError):
                self.module.audit([LOAD, state(20)], epoch, useful_weapon_mask=128)

    def test_cli_preserves_input_and_excludes_raw_positions(self):
        self.assertIsNotNone(self.module, "Raw native-log analyzer not implemented")
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory); log = root / "native.log"; epoch = root / "epoch.json"
            log.write_text(LOAD + state(20) + goal(21) + pickup(22))
            epoch.write_text(json.dumps(EPOCH)); before = log.read_bytes()
            process = subprocess.run([sys.executable, "-B", str(SCRIPT), str(log), "--epoch", str(epoch),
                                      "--useful-weapon-mask", "0x80"], capture_output=True, text=True)
            self.assertEqual(process.returncode, 0, process.stderr)
            result = json.loads(process.stdout)
            self.assertEqual(log.read_bytes(), before)
            self.assertFalse(result["qualified"])
            self.assertNotIn("pos=", process.stdout)
            self.assertIn("input_sha256", result)


if __name__ == "__main__":
    unittest.main()
