"""Sequential rollout against real staged files and the existing service boundary."""
import copy
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

import fleet_names_apply_policy as P
import fleet_names_sequential as S
import fleet_names_transaction as T
from test_fleet_names_transaction import FleetFixture


class Sequential(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.f = FleetFixture(Path(self.temp.name))
        self.b = self.new_backend()
        self.before_generations = copy.deepcopy(self.f.m.running)

    def new_backend(self):
        f = self.f
        return S.Backend(f.m, f.out, f.stage, roots=f.roots, stage_dir=f.stage_dir,
                         source_fingerprint="a"*64)

    def saved_backend(self):
        b = self.new_backend()
        b.load_recovery(json.loads((self.f.out/"journal.json").read_text()))
        return b

    def stop_instances(self):
        return [self.f.m.units[unit][0]["id"] for unit, _ in self.f.m.stop_history]

    def assert_untouched(self, instances):
        for instance in instances:
            root = Path(self.f.roots[instance])
            for path, data in self.f.old.items():
                if Path(path).is_relative_to(root):
                    self.assertEqual(Path(path).read_bytes(), data, path)
            for role in ("botA", "botB"):
                unit = instance+"-"+role+".service"
                self.assertEqual(self.f.m.running[unit], self.before_generations[unit])

    def apply_selected(self, instance):
        b = self.b
        b.begin_instance(instance)
        b.close_instance()
        b.backup_instance_after_close()
        b.apply_instance()
        b.start_instance()
        b.verify_instance()
        b.accept_instance()

    def test_fixed_order_dev_verified_before_each_public_mutation_and_final_48(self):
        original_stop = self.f.m.stop
        def stop(target, out):
            instance = self.f.m.units[target["unit"]][0]["id"]
            index = S.ORDER.index(instance)
            self.assertEqual(self.b.state["rollout"]["completed"], list(S.ORDER[:index]))
            return original_stop(target, out)
        self.f.m.stop = stop
        result = S.transaction(self.b)
        self.assertEqual(self.stop_instances(), [i for i in S.ORDER for _ in range(2)])
        self.assertEqual(self.f.m.start_history, [i+"-"+r+".service" for i in S.ORDER for r in ("botA", "botB")])
        self.assertEqual(self.b.state["rollout"]["completed"], list(S.ORDER))
        self.assertIsNone(self.b.state["rollout"]["active"])
        self.assertEqual(result["own_count"], 48)
        self.assertEqual(self.b.state["status"], "applied_names_only")
        self.assertEqual(set(self.b.state["mutated"]), {r["path"] for r in self.f.stage["files"] if r["changed"]})
        for inst in self.f.m.fleet:
            unit = inst["server"]["unit"]
            self.assertEqual(self.f.m.running[unit], self.before_generations[unit])
        self.assertFalse((Path(self.f.roots["redstation"])/"rotation-count").exists())

    def test_public_selection_and_cross_instance_write_reject(self):
        self.b.initialize()
        with self.assertRaisesRegex(ValueError, "order"):
            self.b.begin_instance("redstation")
        self.b.begin_instance("development")
        foreign = Path(self.f.roots["redstation"])/"botA/Players/Player0.plr"
        with self.assertRaisesRegex(ValueError, "selected instance"):
            self.b.replace(foreign, foreign.read_bytes())
        self.assertEqual(self.f.m.stop_history, [])

    def test_dev_log_failure_rolls_back_only_dev_and_stops_rollout(self):
        verify = self.b.verify_instance
        def fail():
            client = Path(self.f.roots["development"])/"botA/SeriousSam.log"
            with client.open("a") as stream:
                stream.write("SYNCBAD: fixture candidate error\n")
            return verify()
        self.b.verify_instance = fail
        with self.assertRaisesRegex(ValueError, "client.*error"):
            S.transaction(self.b)
        self.assertEqual(set(self.stop_instances()), {"development"})
        self.assertEqual(self.b.state["rollout"]["completed"], [])
        self.assertEqual(self.b.state["status"], "partial_rolled_back")
        self.assert_untouched(set(P.INSTANCES)-{"development"})
        for path, data in self.f.old.items():
            if Path(path).is_relative_to(self.f.roots["development"]):
                self.assertEqual(Path(path).read_bytes(), data)

    def test_red_partial_write_failure_preserves_accepted_dev_and_restores_only_red(self):
        original = self.b.replace
        failed = False
        def fail(path, data, **kwargs):
            nonlocal failed
            if not failed and str(path).startswith(self.f.roots["redstation"]+"/"):
                failed = True
                original(path, data, **kwargs)
                raise OSError("injected red write interruption")
            return original(path, data, **kwargs)
        self.b.replace = fail
        with self.assertRaisesRegex(OSError, "red write"):
            S.transaction(self.b)
        self.assertEqual(self.b.state["rollout"]["completed"], ["development"])
        self.assertEqual(self.stop_instances().count("development"), 2)
        self.assertEqual(set(self.stop_instances()), {"development", "redstation"})
        self.assert_untouched({"yodeller", "skulls", "trouble", "hole"})
        for row in self.f.stage["files"]:
            if Path(row["path"]).is_relative_to(self.f.roots["development"]):
                self.assertEqual(T.sha(Path(row["path"]).read_bytes()), row["after_sha256"])
        for path, data in self.f.old.items():
            if Path(path).is_relative_to(self.f.roots["redstation"]):
                self.assertEqual(Path(path).read_bytes(), data)
        self.assertFalse((Path(self.f.roots["redstation"])/"rotation-count").exists())
        self.assertEqual(self.b.state["status"], "partial_rolled_back")

    def test_mixed_state_source_drift_stops_before_next_instance_without_recapture(self):
        accept = self.b.accept_instance
        changed = Path(self.f.roots["hole"])/"botA/Controls/Controls0.ctl"
        def drift():
            accept()
            if self.b.state["rollout"]["completed"] == ["development"]:
                changed.write_bytes(b"unreviewed change")
        self.b.accept_instance = drift
        with self.assertRaisesRegex(ValueError, "source drift"):
            S.transaction(self.b)
        self.assertEqual(self.stop_instances(), ["development", "development"])
        self.assertEqual(changed.read_bytes(), b"unreviewed change")
        self.assertEqual(self.b.state["rollout"]["completed"], ["development"])
        self.assertNotEqual(self.b.state["status"], "applied_names_only")

    def test_new_foreign_collision_blocks_next_instance_without_touching_it(self):
        accept = self.b.accept_instance
        def collide():
            accept()
            self.f.m.extra_names = [self.f.stage["receipts"][0]["native_name"]]
        self.b.accept_instance = collide
        with self.assertRaisesRegex(ValueError, "collid"):
            S.transaction(self.b)
        self.assertEqual(self.stop_instances(), ["development", "development"])
        self.assert_untouched(set(P.INSTANCES)-{"development"})

    def test_resume_after_accepted_dev_never_recloses_dev(self):
        self.b.initialize()
        self.apply_selected("development")
        dev = copy.deepcopy({k: v for k, v in self.f.m.running.items() if k.startswith("development-bot")})
        resumed = self.saved_backend()
        result = S.transaction(resumed, resume=True)
        self.assertEqual(result["own_count"], 48)
        self.assertEqual(self.stop_instances().count("development"), 2)
        self.assertEqual({k: self.f.m.running[k] for k in dev}, dev)

    def test_interrupted_start_recovers_only_affected_instance_then_explicit_resume(self):
        b = self.b
        b.initialize(); b.begin_instance("development"); b.close_instance()
        b.backup_instance_after_close(); b.apply_instance()
        unit = "development-botA.service"
        self.f.m.unresolvable.add(unit)
        with self.assertRaisesRegex(RuntimeError, "native start"):
            b.start_instance()
        self.f.m.unresolvable.clear()
        recovered = self.saved_backend()
        with self.assertRaisesRegex(ValueError, "recover.*active|active.*recover"):
            S.transaction(recovered, resume=True)
        S.recover(recovered)
        self.assertEqual(recovered.state["status"], "partial_rolled_back")
        self.assertEqual(set(self.stop_instances()), {"development"})
        self.assert_untouched(set(P.INSTANCES)-{"development"})
        resumed = self.saved_backend()
        self.assertEqual(S.transaction(resumed, resume=True)["own_count"], 48)

    def test_unreceipted_started_process_is_not_adopted_by_recovery(self):
        b = self.b
        b.initialize(); b.begin_instance("development"); b.close_instance()
        b.backup_instance_after_close(); b.apply_instance()
        self.f.m.interrupt_command = True
        with self.assertRaises(SystemExit):
            b.start_instance()
        recovered = self.saved_backend()
        stops = len(self.f.m.stop_history)
        with self.assertRaisesRegex((ValueError, RuntimeError), "unrecorded|invocation"):
            S.recover(recovered)
        self.assertEqual(len(self.f.m.stop_history), stops)
        self.assert_untouched(set(P.INSTANCES)-{"development"})
        self.assertNotEqual(recovered.state["status"], "applied_names_only")

    def test_changed_completed_generation_rejects_final_48_success(self):
        final = self.b.verify_final
        def replace_generation():
            self.f.m.spawn("development-botA.service")
            return final()
        self.b.verify_final = replace_generation
        with self.assertRaisesRegex(ValueError, "generation"):
            S.transaction(self.b)
        self.assertEqual(len(self.f.m.stop_history), 12)
        self.assertEqual(self.b.state["status"], "rollout_verification_failed")
        self.assertEqual(self.b.state["rollout"]["completed"], list(S.ORDER))

    def test_new_server_delta_stops_rollout_after_dev_and_keeps_failure_evidence(self):
        verify = self.b.verify_instance
        def fail():
            path = Path(self.f.roots["development"])/"server/Dedicated_BotTest.log"
            with path.open("a") as stream:
                stream.write("SYNCBAD: Client 'fixture', Sequence 2 Tick 3 - bad 1\n")
            return verify()
        self.b.verify_instance = fail
        with self.assertRaisesRegex(ValueError, "server log sync"):
            S.transaction(self.b)
        self.assertEqual(set(self.stop_instances()), {"development"})
        self.assertEqual(self.b.state["status"], "partial_rolled_back")
        self.assertTrue(self.b.state["server_log_checks"][-1]["instances"]["development"]["new_events"]["bad_sync"])

    def test_recovery_rejects_nonprefix_completion_and_foreign_active_scope(self):
        self.b.initialize()
        original = json.loads((self.f.out/"journal.json").read_text())
        for mutate in (lambda s: s["rollout"].update(completed=["redstation"]),
                       lambda s: s["rollout"].update(active={"instance": "hole", "attempt": 1,
                           "phase": "instance_close", "mutation_possible": True, "payload": "before"})):
            bad = copy.deepcopy(original); mutate(bad)
            (self.f.out/"journal.json").write_text(json.dumps(bad))
            with self.assertRaises(ValueError):
                self.new_backend().load_recovery(bad)
            self.assertEqual(self.f.m.stop_history, [])

    def test_first_close_phase_journal_failure_does_not_stop_any_client(self):
        event = self.b.event
        def fail(state, **fields):
            if state == "instance_close":
                raise OSError("journal unavailable")
            return event(state, **fields)
        self.b.event = fail
        with self.assertRaisesRegex(OSError, "journal unavailable"):
            S.transaction(self.b)
        self.assertEqual(self.f.m.stop_history, [])
        self.assert_untouched(P.INSTANCES)

    def test_source_drift_after_selection_blocks_the_first_close(self):
        self.b.initialize(); self.b.begin_instance("development")
        path = Path(self.f.roots["hole"])/"botA/Controls/Controls0.ctl"
        path.write_bytes(b"changed after selection")
        with self.assertRaisesRegex(ValueError, "source drift"):
            self.b.close_instance()
        self.assertEqual(self.f.m.stop_history, [])

    def test_completed_replacement_after_selection_is_never_adopted_before_public_close(self):
        self.b.initialize(); self.apply_selected("development")
        self.b.begin_instance("redstation")
        self.f.m.spawn("development-botA.service")
        with self.assertRaisesRegex(ValueError, "generation|invocation|replaced"):
            self.b.close_instance()
        self.assertEqual(self.stop_instances(), ["development", "development"])

    def test_interrupted_rollback_recloses_only_recorded_affected_generation(self):
        b = self.b
        b.initialize(); b.begin_instance("development"); b.close_instance()
        b.backup_instance_after_close(); b.apply_instance(); b.start_instance()
        start = b.start_one
        def interrupt(inst, role, client, rollback=False):
            start(inst, role, client, rollback)
            if rollback and role == "botA":
                raise OSError("interrupted rollback after durable first start")
        b.start_one = interrupt
        with self.assertRaisesRegex(OSError, "interrupted rollback"):
            b.rollback_active()
        recovered = self.saved_backend()
        S.recover(recovered)
        self.assertEqual(recovered.state["status"], "partial_rolled_back")
        self.assertEqual(set(self.stop_instances()), {"development"})
        self.assert_untouched(set(P.INSTANCES)-{"development"})

    def test_interrupted_red_partial_payload_recovers_against_mixed_stage(self):
        b = self.b
        b.initialize(); self.apply_selected("development")
        b.begin_instance("redstation"); b.close_instance(); b.backup_instance_after_close()
        replace = b.replace
        def interrupt(path, data, **kwargs):
            replace(path, data, **kwargs)
            raise OSError("interrupted after atomic payload")
        b.replace = interrupt
        with self.assertRaisesRegex(OSError, "atomic payload"):
            b.apply_instance()
        recovered = self.saved_backend()
        S.recover(recovered)
        self.assertEqual(recovered.state["rollout"]["completed"], ["development"])
        self.assertEqual(self.stop_instances().count("development"), 2)
        self.assert_untouched({"yodeller", "skulls", "trouble", "hole"})
        self.assertEqual(recovered.state["status"], "partial_rolled_back")

    def test_resume_rechecks_original_disk_reserve_before_more_mutation(self):
        self.b.initialize(); self.apply_selected("development")
        resumed = self.saved_backend()
        usage = T.shutil.disk_usage(self.f.out)
        with patch.object(T.shutil, "disk_usage", return_value=usage._replace(free=1)):
            with self.assertRaisesRegex(ValueError, "disk reserve"):
                S.transaction(resumed, resume=True)
        self.assertEqual(self.stop_instances(), ["development", "development"])
        self.assert_untouched(set(P.INSTANCES)-{"development"})

    def test_complete_stage_boundary_still_requires_all_48_and_51(self):
        broken = copy.deepcopy(self.f.stage)
        broken["receipts"] = [r for r in broken["receipts"] if r["instance"] == "development"]
        with self.assertRaisesRegex(ValueError, "48"):
            S.Backend(self.f.m, self.f.out, broken, roots=self.f.roots, stage_dir=self.f.stage_dir)


class MixedPolicy(unittest.TestCase):
    def baseline(self):
        from test_fleet_names_apply_policy import fixture
        rows, observations = fixture()
        before = copy.deepcopy(observations)
        for n, local in enumerate(before["development"]["locals"]):
            name = before["redstation"]["locals"][n]["native"]
            local.update(native=name, profile_native=name)
            before["development"]["query_names"][n] = name
        return rows, before, observations

    def test_only_exact_original_duplicate_slots_are_accepted_before_dev(self):
        rows, before, after = self.baseline()
        self.assertEqual(S.validate_mixed(rows, before, before, set())["own_count"], 48)
        self.assertEqual(S.validate_mixed(rows, after, before, {"development"})["own_count"], 48)
        changed = copy.deepcopy(before)
        changed["development"]["locals"][0].update(native="Other", profile_native="Other")
        changed["development"]["query_names"][0] = "Other"
        with self.assertRaisesRegex(ValueError, "immutable expectation"):
            S.validate_mixed(rows, changed, before, set())

    def test_new_name_colliding_with_untouched_old_name_rejects_mixed_state(self):
        rows, before, after = self.baseline()
        name = after["development"]["locals"][0]["native"]
        for ob in (before, after):
            ob["redstation"]["locals"][0].update(native=name, profile_native=name)
            ob["redstation"]["query_names"][0] = name
        with self.assertRaisesRegex(ValueError, "mixed fleet.*collision"):
            S.validate_mixed(rows, after, before, {"development"})


if __name__ == "__main__":
    unittest.main()
