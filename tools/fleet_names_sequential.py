"""Dev-first names rollout with one explicit affected instance at a time.

The complete immutable stage and global lock set remain mandatory. There is no
single-instance stage mode and no override of the 48-assignment/51-write checks.
"""
from collections import Counter
import copy
import json
from pathlib import Path
import re

import fleet_names_apply_policy as P
import fleet_names_transaction as T
import names_staging as N

ORDER = ("development", "redstation", "yodeller", "skulls", "trouble", "hole")
WORKFLOW = "DEV_FIRST_ONE_INSTANCE_AT_A_TIME"
PHASES = {"instance_selected", "instance_close", "instance_postclose", "instance_apply",
          "instance_payload_durable", "instance_start", "instance_verify", "instance_verified",
          "instance_rollback_close", "instance_rollback_restore", "instance_rollback_start",
          "instance_rollback_verify", "instance_rollback_launch"}
RECOVERABLE = T.RECOVERABLE | PHASES | {
    "preclose_durable", "rollout_ready", "instance_postclose_durable", "instance_accepted",
    "instance_failed", "partial_rolled_back", "partial_failed_no_mutation",
    "rollout_verification_failed", "partial_boundary_verified",
}


def validate_mixed(rows, observations, before, applied):
    """Exact old/new slots and GUIDs; no new collision is excused as old evidence."""
    applied = set(applied)
    P.require(applied == set(ORDER[:len(applied)]), "mixed rollout order")
    P.require(set(before) == set(P.INSTANCES), "mixed original fleet incomplete")
    result = P.fleet(rows, observations, applied=applied == set(P.INSTANCES))
    assigned = {(r["instance"], r["role"], r["local"]): r["native_name"] for r in rows}
    visible = []
    for instance, ob in observations.items():
        old = {(r["role"], r["local"]): r for r in before[instance]["locals"]}
        P.require(len(old) == 8, "original slot scope")
        for local in ob["locals"]:
            key = local["role"], local["local"]
            expected = assigned[(instance, *key)] if instance in applied else old[key]["native"]
            P.require(local["native"] == expected and local["guid"] == old[key]["guid"],
                      "mixed actual name/GUID differs from immutable expectation")
            visible.append(P.legacy_display(local["native"]))
    # Original Dev/Red identities may duplicate across servers. They are bound
    # exactly above; every mixed boundary after the first completed step is unique.
    P.require(not applied or len(set(visible)) == 48, "mixed fleet visible name collision")
    return result


class Backend(T.Backend):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.state.update(schema=4, workflow=WORKFLOW, instance_backups={},
            rollout=dict(order=list(ORDER), completed=[], accepted={}, restored={}, active=None,
                         attempts={i: 0 for i in ORDER}))

    def event(self, state, **fields):
        if state == "applied_names_only":
            P.require(self.state["rollout"]["completed"] == list(ORDER) and
                      self.state["rollout"]["active"] is None and
                      self.state.get("final_verified") is True, "full rollout not verified")
        P.require(state != "rolled_back", "sequential rollback must retain partial state")
        return super().event(state, **fields)

    def instance(self, instance):
        return next(i for i in self.fleet if i["id"] == instance)

    def selected(self):
        active = self.state["rollout"]["active"]
        P.require(active is not None, "no selected instance")
        return self.instance(active["instance"])

    def selected_clients(self):
        inst = self.selected()
        return [(inst, role, client) for role, client in zip(("botA", "botB"), inst["clients"])]

    def instance_files(self, instance):
        root = Path(self.roots[instance])
        return [r for r in self.stage["files"] if Path(r["path"]).is_relative_to(root)]

    def original_observations(self):
        return {i: b["observation"] for i, b in self.state["before"].items()}

    def applied_instances(self):
        result = set(self.state["rollout"]["completed"])
        active = self.state["rollout"]["active"]
        if active and active["payload"] == "after":
            result.add(active["instance"])
        return result

    def expected_hash(self, row, applied):
        return row["after_sha256"] if any(
            Path(row["path"]).is_relative_to(self.roots[i]) for i in applied) else row["sha256"]

    def check_inputs(self):
        applied = self.applied_instances()
        for row in self.stage["files"]:
            P.require(T.sha(T.read(row["path"])[0]) == self.expected_hash(row, applied),
                      "mixed stage source drift: " + row["path"])

    def phase(self, phase, **changes):
        P.require(phase in PHASES, "unknown instance phase")
        active = self.state["rollout"]["active"]
        P.require(active is not None, "no selected instance")
        previous = copy.deepcopy(active)
        active.update(phase=phase, **changes)
        try:
            self.event(phase, instance=active["instance"], attempt=active["attempt"])
        except BaseException:
            self.state["rollout"]["active"] = previous
            raise

    def preflight(self):
        super().preflight()
        before = self.original_observations()
        assigned = {(r["instance"], r["role"], r["local"]): r["native_name"] for r in self.rows}
        # Check every planned full-instance transition before stopping Dev.
        for count in range(1, 7):
            applied = set(ORDER[:count])
            names = [P.legacy_display(assigned[(i, r["role"], r["local"])]
                     if i in applied else r["native"])
                     for i, ob in before.items() for r in ob["locals"]]
            P.require(len(set(names)) == 48, "planned mixed name collision")

    def initialize(self):
        self.event("preflight")
        self.preflight()
        self.event("backup_before_close")
        super().backup_before_close()
        self.check_inputs()
        self.event("rollout_ready")

    def verify_mixed(self):
        self.guard_servers()
        observations = {}
        for inst in self.fleet:
            touched = any(inst["id"]+"/"+role in self.state["started"] for role in ("botA", "botB"))
            observations[inst["id"]] = self.observation(inst, scan_errors=touched)
            for role, client in zip(("botA", "botB"), inst["clients"]):
                key = inst["id"]+"/"+role
                recorded = self.state["started"].get(key)
                expected = recorded or self.state["before"][inst["id"]]["observation"]["targets"][role]
                P.require(observations[inst["id"]]["targets"][role] == expected and
                          self.target(inst, role, client) == expected,
                          "mixed client generation differs from durable identity")
                if recorded:
                    P.require(not any(observations[inst["id"]]["logs"][role]["events"].values()),
                              "new client generation log contains error events")
        result = validate_mixed(self.rows, observations, self.original_observations(), self.applied_instances())
        self.check_inputs()
        self.state["last_mixed_check"] = dict(applied=sorted(self.applied_instances()), observations=observations)
        return observations, result

    def begin_instance(self, instance):
        rollout = self.state["rollout"]
        P.require(rollout["active"] is None and len(rollout["completed"]) < 6 and
                  instance == ORDER[len(rollout["completed"])], "sequential instance order")
        self.verify_mixed()
        self.check_server_logs("before_"+instance)
        for client in self.instance(instance)["clients"]:
            P.require(self.stop_policy(client["unit"]) == self.state["before"][instance]["stop_policies"][client["unit"]],
                      "service policy changed before selected close")
        previous = copy.deepcopy(rollout)
        rollout["attempts"][instance] += 1
        rollout["active"] = dict(instance=instance, attempt=rollout["attempts"][instance],
                                 phase="instance_selected", mutation_possible=False, payload="before")
        try:
            self.event("instance_selected", instance=instance)
        except BaseException:
            self.state["rollout"] = previous
            raise

    def guard_surroundings(self):
        """Recheck unchanged running instances before each forward mutation."""
        selected = self.selected()["id"]
        applied = set(self.state["rollout"]["completed"])
        for row in self.stage["files"]:
            if Path(row["path"]).is_relative_to(self.roots[selected]):
                continue
            P.require(T.sha(T.read(row["path"])[0]) == self.expected_hash(row, applied),
                      "unselected mixed source drift: "+row["path"])
        for inst, role, client in self.clients():
            if inst["id"] == selected:
                continue
            key = inst["id"]+"/"+role
            expected = self.state["started"].get(key) or self.state["before"][inst["id"]]["observation"]["targets"][role]
            P.require(self.target(inst, role, client) == expected,
                      "unselected generation differs from durable identity")

    def close_one(self, inst, role, client, label):
        P.require(inst["id"] == self.selected()["id"], "close outside selected instance")
        if label == "apply":
            self.guard_surroundings()
            self.check_collision_now()
        return super().close_one(inst, role, client, label)

    def start_one(self, inst, role, client, rollback=False):
        P.require(inst["id"] == self.selected()["id"], "start outside selected instance")
        if not rollback:
            self.guard_surroundings()
            self.check_inputs()
            self.check_collision_now()
        return super().start_one(inst, role, client, rollback)

    def replace(self, path, data, *, restore_meta=None):
        inst = self.selected()
        P.require(Path(path).is_relative_to(self.roots[inst["id"]]), "write outside selected instance")
        phase = self.state["rollout"]["active"]["phase"]
        P.require(phase in ("instance_apply", "instance_rollback_restore", "instance_rollback_launch"),
                  "write outside selected mutation phase")
        if phase == "instance_apply":
            self.guard_surroundings()
        if phase != "instance_rollback_launch":
            for _, _, client in self.selected_clients():
                self.stopped(client)
        else:
            P.require(inst["id"] == "redstation" and str(path) in
                      {self.roots["redstation"]+"/launch-bot"+s+".sh" for s in ("A", "B")},
                      "only restored Red launch policy may change while clients run")
        return super().replace(path, data, restore_meta=restore_meta)

    def no_selected_names_connected(self):
        inst = self.selected()
        own = {P.legacy_display(r["native"]) for r in self.state["before"][inst["id"]]["observation"]["locals"]}
        roles = {role for role in ("botA", "botB") if
                 (intent := self.state["start_intents"].get(inst["id"]+"/"+role)) and
                 intent.get("invocation_id") and not intent["rollback"]}
        own.update(P.legacy_display(r["native_name"]) for r in self.rows
                   if r["instance"] == inst["id"] and r["role"] in roles)
        self.m.wait(lambda: not (own & {P.legacy_display(n) for n in self.public_query(inst)[1]}),
                    45, "selected own names still present; do not remove others")

    def close_instance(self):
        self.verify_mixed()
        self.phase("instance_close", mutation_possible=True)
        for inst, role, client in self.selected_clients():
            self.close_one(inst, role, client, "apply")
        self.no_selected_names_connected()
        self.guard_servers()

    def backup_instance_after_close(self):
        self.phase("instance_postclose")
        for _, _, client in self.selected_clients():
            self.stopped(client)
        active = self.state["rollout"]["active"]
        label = "postclose-"+active["instance"]+"-"+str(active["attempt"])
        folder = self.out/label
        folder.mkdir(mode=0o700)
        T.sync_dir(self.out)
        records = {}
        for index, row in enumerate(self.instance_files(active["instance"])):
            data, meta = T.read(row["path"])
            blob = folder/(str(index)+".bin")
            T.atomic(blob, data, create_only=True)
            records[row["path"]] = dict(blob=str(blob), sha256=T.sha(data), meta=meta)
        self.state["instance_backups"][label] = records
        self.event("instance_postclose_durable", instance=active["instance"])
        # This evidence never replaces the immutable before expectation/backup.
        self.check_inputs()

    def check_collision_now(self):
        proposed = P.assignments(self.rows)
        selected = self.selected()["id"]
        for inst in self.fleet:
            own = []
            for role, client in zip(("botA", "botB"), inst["clients"]):
                if not self.m.ops["service_processes"](client["unit"]):
                    P.require(inst["id"] == selected, "unselected client stopped")
                    self.stopped(client)
                    continue
                target = self.own_current(inst, role, client)
                key = inst["id"]+"/"+role
                intent = self.state["start_intents"].get(key)
                use_after = inst["id"] in self.state["rollout"]["completed"] or (
                    key in self.state["started"] and intent and not intent["rollback"])
                expected = ({r["local"]: r["native_name"] for r in self.rows
                             if r["instance"] == inst["id"] and r["role"] == role}
                            if use_after else {r["local"]: r["native"] for r in
                             self.state["before"][inst["id"]]["observation"]["locals"] if r["role"] == role})
                actual = self.actual_rows(target)
                P.require({r["local"]: r["native"] for r in actual} == expected,
                          "mixed running local differs from known name expectation")
                own.extend(P.legacy_display(r["native"]) for r in actual)
            names = Counter(P.legacy_display(n) for n in self.public_query(inst)[1])
            for name in own:
                P.require(names[name] == 1, "running own name ambiguous")
                del names[name]
            P.require(not (set(names) & proposed), "fresh occupied-name collision")

    def apply_instance(self):
        self.phase("instance_apply")
        self.guard_servers()
        self.check_inputs()
        self.check_collision_now()
        for _, _, client in self.selected_clients():
            self.stopped(client)
        # Retain the complete global validator, then select known owned payloads.
        T.validate_stage(self.stage, self.roots, self.stage_dir)
        P.name_only_paths([r["path"] for r in self.changed()], self.roots)
        selected = self.selected()["id"]
        rows = [r for r in self.instance_files(selected) if r["changed"]]
        P.require(len(rows) == (11 if selected == "redstation" else 8), "selected payload scope")
        for row in rows:
            P.require(T.sha(T.read(row["path"])[0]) == row["sha256"], "selected apply source drift")
            self.replace(Path(row["path"]), T.read(self.stage_dir/row["after_blob"])[0])
        self.phase("instance_payload_durable", payload="after")
        self.check_inputs()

    def start_instance(self):
        self.check_inputs()
        self.guard_surroundings()
        self.phase("instance_start")
        for inst, role, client in self.selected_clients():
            self.check_collision_now()
            self.start_one(inst, role, client)

    def verify_instance(self):
        self.phase("instance_verify")
        inst = self.selected()
        P.require(self.state["rollout"]["active"]["payload"] == "after" and all(
            inst["id"]+"/"+role in self.state["started"] for role in ("botA", "botB")),
            "selected new generation records incomplete")
        observations, _ = self.verify_mixed()
        self.check_server_logs("verify_"+inst["id"])
        self.state["rollout"]["active"]["verification"] = observations[inst["id"]]
        self.phase("instance_verified")
        return dict(instance=inst["id"], own_count=8, qualified=False)

    def accept_instance(self):
        rollout = self.state["rollout"]
        active = rollout["active"]
        P.require(active and active["phase"] == "instance_verified", "instance not verified")
        previous = copy.deepcopy(rollout)
        instance = active["instance"]
        rollout["accepted"][instance] = dict(attempt=active["attempt"], observation=active["verification"])
        rollout["completed"].append(instance)
        rollout["restored"].pop(instance, None)
        rollout["active"] = None
        try:
            self.event("instance_accepted", instance=instance, completed=rollout["completed"].copy())
        except BaseException:
            self.state["rollout"] = previous
            raise

    def rollback_active(self):
        inst = self.selected()
        self.phase("instance_rollback_close")
        errors = []
        for instance, role, client in self.selected_clients():
            try:
                self.close_one(instance, role, client, "rollback")
            except BaseException as error:
                errors.append(repr(error))
        P.require(not errors, "selected rollback normal-close failures: "+repr(errors))
        self.no_selected_names_connected()
        self.phase("instance_rollback_restore", payload="before")
        backup = self.state["backups"]["preclose"]
        self.validate_backup("preclose", backup)
        files = self.instance_files(inst["id"])
        mutable = self.mutable_paths()
        for row in files:
            if row["path"] not in mutable:
                P.require(T.sha(T.read(row["path"])[0]) == row["sha256"], "selected immutable input changed")
        for row in files:
            path = row["path"]
            if path not in mutable:
                continue
            saved = backup[path]
            P.require(saved["sha256"] == row["sha256"], "original backup differs from staged before")
            data = T.read(saved["blob"])[0]
            if inst["id"] == "redstation" and path in {
                    self.roots["redstation"]+"/launch-bot"+s+".sh" for s in ("A", "B")}:
                data = N.patch_launcher(data, self.roots["redstation"], Path(path).stem[-1], saved["sha256"])
            self.replace(Path(path), data, restore_meta=saved["meta"])
        for _, role, _ in self.selected_clients():
            self.state["started"].pop(inst["id"]+"/"+role, None)
        self.phase("instance_rollback_start")
        for instance, role, client in self.selected_clients():
            self.start_one(instance, role, client, rollback=True)
        self.phase("instance_rollback_verify")
        # Red's temporary rotation bypass is restored after old identities join.
        ob = self.observation(inst, scan_errors=True)
        old = self.state["before"][inst["id"]]["observation"]
        P.require([(r["role"], r["local"], r["native"], r["guid"]) for r in ob["locals"]] ==
                  [(r["role"], r["local"], r["native"], r["guid"]) for r in old["locals"]],
                  "selected rollback actual identities")
        for instance, role, client in self.selected_clients():
            recorded = self.state["started"].get(inst["id"]+"/"+role)
            P.require(recorded and ob["targets"][role] == recorded and self.target(instance, role, client) == recorded,
                      "rollback client generation differs from durable identity")
            P.require(not any(ob["logs"][role]["events"].values()), "rollback new client log contains errors")
        names = Counter(P.legacy_display(n) for n in ob["query_names"])
        P.require(all(names[P.legacy_display(r["native"])] == 1 for r in old["locals"]), "rollback query identity")
        self.phase("instance_rollback_launch")
        if inst["id"] == "redstation":
            for side in ("A", "B"):
                path = Path(self.roots["redstation"])/("launch-bot"+side+".sh")
                saved = backup[str(path)]
                data = T.read(saved["blob"])[0]
                P.require(T.sha(T.read(path)[0]) == T.sha(N.patch_launcher(data, self.roots["redstation"], side, saved["sha256"])),
                          "rollback bypass launcher drift")
                self.replace(path, data, restore_meta=saved["meta"])
        for row in files:
            data, meta = T.read(row["path"])
            P.require(T.sha(data) == row["sha256"] and meta == backup[row["path"]]["meta"], "rollback byte/metadata mismatch")
        self.verify_mixed()
        rollout = self.state["rollout"]
        previous = copy.deepcopy(rollout)
        rollout["restored"][inst["id"]] = ob
        rollout["active"] = None
        try:
            self.event("partial_rolled_back", affected=inst["id"], completed=rollout["completed"].copy())
        except BaseException:
            self.state["rollout"] = previous
            raise

    def abandon_selection(self):
        rollout = self.state["rollout"]
        active = rollout["active"]
        P.require(not active or not active["mutation_possible"], "cannot abandon affected instance")
        rollout["active"] = None
        self.event("partial_failed_no_mutation", completed=rollout["completed"].copy())

    def resume_ready(self):
        P.require(self.state["rollout"]["active"] is None, "recover active instance before resume")
        P.require(T.shutil.disk_usage(self.out).free > 8*2**30, "disk reserve")
        self.verify_mixed()
        self.check_server_logs("resume_boundary")
        self.event("rollout_ready")

    def verify_final(self):
        P.require(self.state["rollout"]["completed"] == list(ORDER) and
                  self.state["rollout"]["active"] is None, "all six instances must be accepted")
        observations, result = self.verify_mixed()
        self.require_started_generations(observations)
        self.check_server_logs("final_sequential_48")
        self.check_inputs()
        self.require_started_generations(observations)
        self.state["final_verified"] = True
        return dict(result, rollout_order=list(ORDER), query_scope="HOST_TO_PUBLIC_IP_ORIGINAL_GAMESPY",
                    external_browser_or_WAN_qualification=False)

    def load_recovery(self, state):
        P.require(state.get("schema") == 4 and state.get("scope") == T.SCOPE and
                  state.get("workflow") == WORKFLOW and state.get("status") in RECOVERABLE and
                  state.get("qualified") is False, "sequential recovery state not eligible")
        rollout = state.get("rollout", {})
        completed = rollout.get("completed")
        P.require(isinstance(completed, list) and completed == list(ORDER[:len(completed)]) and
                  len(completed) <= 6 and rollout.get("order") == list(ORDER), "recovery completed order")
        P.require(set(rollout.get("accepted", {})) == set(completed), "recovery accepted prefix")
        next_set = {ORDER[len(completed)]} if len(completed) < 6 else set()
        P.require(set(rollout.get("restored", {})) <= next_set, "recovery restored scope")
        attempts = rollout.get("attempts", {})
        P.require(set(attempts) == set(ORDER) and all(type(v) is int and v >= 0 for v in attempts.values()) and
                  all(attempts[i] > 0 for i in completed) and
                  all(not attempts[i] for i in set(ORDER)-set(completed)-next_set), "recovery attempt scope")
        active = rollout.get("active")
        if active is not None:
            P.require(active.get("instance") in next_set and active.get("attempt") == attempts[active["instance"]] > 0 and
                      active.get("phase") in PHASES and type(active.get("mutation_possible")) is bool and
                      active.get("payload") in ("before", "after"), "recovery active instance scope")
        touched = set(completed) | set(rollout["restored"]) | ({active["instance"]} if active else set())
        keys = {i+"/"+r for i in touched for r in ("botA", "botB")}
        for mapping in ("started", "start_intents", "stop_intents", "stop_acks"):
            P.require(set(state.get(mapping, {})) <= keys, "recovery touched generation scope")
        P.require({i+"/"+r for i in set(completed)|set(rollout["restored"]) for r in ("botA", "botB")} <= set(state["started"]),
                  "recovery accepted generation records incomplete")
        for instance in completed:
            accepted = rollout["accepted"][instance]
            P.require(accepted["attempt"] == attempts[instance] and all(
                accepted["observation"]["targets"][r] == state["started"][instance+"/"+r] for r in ("botA", "botB")),
                "recovery accepted generation receipt")
        P.require(all(any(Path(p).is_relative_to(self.roots[i]) for i in touched)
                      for p in state.get("mutated", [])), "recovery mutation outside touched instances")
        for label, records in state.get("instance_backups", {}).items():
            match = re.fullmatch(r"postclose-(development|redstation|yodeller|skulls|trouble|hole)-([1-9][0-9]*)", label)
            P.require(match and match[1] in touched and int(match[2]) <= attempts[match[1]], "instance backup label scope")
            expected = {r["path"]: n for n, r in enumerate(self.instance_files(match[1]))}
            P.require(set(records) == set(expected), "instance backup file scope")
            for path, record in records.items():
                P.require(record["blob"] == str(self.out/label/(str(expected[path])+".bin")) and
                          T.sha(T.read(record["blob"])[0]) == record["sha256"], "instance backup corrupt/escape")
        self._load_bound_recovery(state)
        # Outside the interrupted instance, before/after bytes and recorded live
        # generations remain exact. No new snapshot replaces these expectations.
        for row in self.stage["files"]:
            if active and Path(row["path"]).is_relative_to(self.roots[active["instance"]]):
                continue
            P.require(T.sha(T.read(row["path"])[0]) == self.expected_hash(row, set(completed)), "recovery mixed source drift")
        for inst, role, client in self.clients():
            if active and inst["id"] == active["instance"]:
                continue
            key = inst["id"]+"/"+role
            expected = state["started"].get(key) or state["before"][inst["id"]]["observation"]["targets"][role]
            P.require(self.target(inst, role, client) == expected, "recovery unselected generation changed")


def recover(backend):
    active = backend.state["rollout"]["active"]
    if active and active["mutation_possible"]:
        try:
            backend.rollback_active()
        except BaseException as error:
            try:
                backend.event("rollback_incomplete", recovery_error=repr(error))
            except BaseException as reporting:
                error.add_note("Recovery journal failed: "+repr(reporting))
            raise
    elif active:
        backend.verify_mixed()
        backend.abandon_selection()
    else:
        backend.verify_mixed()
        backend.event("partial_boundary_verified")


def transaction(backend, *, resume=False):
    if resume:
        backend.resume_ready()
    else:
        backend.initialize()
    while len(backend.state["rollout"]["completed"]) < 6:
        instance = ORDER[len(backend.state["rollout"]["completed"])]
        try:
            backend.begin_instance(instance)
            backend.close_instance()
            backend.backup_instance_after_close()
            backend.apply_instance()
            backend.start_instance()
            backend.verify_instance()
            backend.accept_instance()
        except BaseException as error:
            journal_errors = []
            try:
                backend.event("instance_failed", instance=instance, error=repr(error))
            except BaseException as reporting:
                journal_errors.append(repr(reporting))
            active = backend.state["rollout"]["active"]
            try:
                if active and active["mutation_possible"]:
                    backend.rollback_active()
                else:
                    backend.abandon_selection()
            except BaseException as recovery:
                try:
                    backend.event("rollback_incomplete", apply_error=repr(error), recovery_error=repr(recovery),
                                  journal_errors=journal_errors)
                except BaseException as reporting:
                    journal_errors.append(repr(reporting))
                raise P.RollbackIncomplete(error, recovery, journal_errors) from recovery
            for reporting in journal_errors:
                error.add_note("Failure-report journal write failed: "+reporting)
            raise
    try:
        result = backend.verify_final()
        backend.event("applied_names_only", result=result)
        return result
    except BaseException as error:
        try:
            backend.event("rollout_verification_failed", error=repr(error))
        except BaseException as reporting:
            error.add_note("Final-verification journal failed: "+repr(reporting))
        raise
