"""Guarded names-only backend; no standalone entry point or runtime authority.

The caller supplies canonical roots, frozen stage data, exclusive lock ownership,
and a reviewed native/service adapter. Tests simulate that external boundary and
use real files. No Dedicated-server stop or binary write operation exists here.
"""
from pathlib import Path
import contextlib
import copy
import fcntl
import hashlib
import json
import os
import re
import shutil
import stat
import uuid

import fleet_names_apply_policy as P
import names_staging as N
from native_closed_log_evidence import archive_closed_role_logs, scan_log_errors
from fleet_names_service_policy import (
    SERVICE_POLICY_FIELDS, parse_service_policy, validate_launch_policy,
)

sha = lambda data: hashlib.sha256(data).hexdigest()
SCOPE = "NAMES_ONLY_NO_DLL_PROMOTION"
STOP_POLICY = ("ExecStop", "KillMode", "SendSIGKILL", "TimeoutStopUSec")
TERMINAL = {"applied_names_only", "rolled_back"}
RECOVERABLE = {
    "close_own_clients", "backup_after_close", "postclose_durable", "apply_51",
    "write_intent", "start_own_clients", "client_start_intent",
    "service_start_invocation", "started_identity", "verify_all_48", "apply_failed",
    "client_stop_intent", "own_normal_close", "closed_log_archived",
    "interrupted_start_identity_recovered", "rollback_close_own_clients",
    "rollback_restore_with_rotation_bypassed", "rollback_start_exact_old_names",
    "rollback_start_reset_identity_records", "rollback_verify_old_names",
    "rollback_restore_original_launch_policy", "rollback_incomplete", "server_log_checked",
}


def canonical(path, *, exists=True):
    path = Path(path)
    P.require(path.is_absolute() and path.resolve(strict=exists) == path,
              "canonical path required: " + str(path))
    return path


def signature(st):
    return (st.st_dev, st.st_ino, st.st_size, st.st_mtime_ns, st.st_ctime_ns)


def read(path):
    path = canonical(path)
    before = path.lstat()
    P.require(stat.S_ISREG(before.st_mode) and before.st_nlink == 1,
              "single-link regular file required")
    fd = os.open(path, os.O_RDONLY | os.O_NOFOLLOW)
    with os.fdopen(fd, "rb") as stream:
        opened = os.fstat(stream.fileno())
        data = stream.read()
        finished = os.fstat(stream.fileno())
    P.require(signature(before) == signature(opened) == signature(finished) ==
              signature(path.lstat()), "file changed during read")
    return data, dict(uid=before.st_uid, gid=before.st_gid, mode=before.st_mode & 0o7777)


def sync_dir(path):
    fd = os.open(canonical(path), os.O_RDONLY | os.O_DIRECTORY)
    try:
        os.fsync(fd)
    finally:
        os.close(fd)


def atomic(path, data, *, expected=None, meta=None, create_only=False):
    path = Path(path)
    canonical(path.parent)
    P.require(path.is_absolute() and not path.is_symlink(), "atomic destination alias")
    if path.exists():
        current, _ = read(path)
        P.require(not create_only, "atomic destination already exists")
        if expected is not None:
            P.require(sha(current) == expected, "atomic source drift: " + str(path))
    else:
        P.require(expected is None, "expected source is missing")
    tmp = path.with_name("." + path.name + ".names-" + uuid.uuid4().hex)
    fd = os.open(tmp, os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW, 0o600)
    try:
        with os.fdopen(fd, "wb") as stream:
            P.require(stream.write(data) == len(data), "short atomic write")
            stream.flush()
            if meta:
                os.fchown(stream.fileno(), meta["uid"], meta["gid"])
                os.fchmod(stream.fileno(), meta["mode"])
            os.fsync(stream.fileno())
        if expected is not None:
            P.require(sha(read(path)[0]) == expected, "atomic second source drift")
        elif create_only:
            P.require(not path.exists() and not path.is_symlink(), "atomic create race")
        else:
            P.require(not path.is_symlink(), "atomic destination changed to alias")
        os.replace(tmp, path)
        sync_dir(path.parent)
    finally:
        if tmp.exists():
            tmp.unlink()


def lock_paths(install_parent, deployment_lock, roots):
    P.require(set(roots) == set(P.INSTANCES), "lock roots incomplete")
    paths = [Path(install_parent)/"fleet-install.lock", Path(deployment_lock),
             Path(roots["redstation"])/"identity-rotation.lock"]
    for instance in P.INSTANCES:
        paths.extend(Path(roots[instance])/name for name in
                     ("cecil-runtime.lock", "supply-rollout.lock"))
    P.require(len(set(paths)) == len(paths), "duplicate lock paths")
    return paths


@contextlib.contextmanager
def exclusive_locks(paths):
    """Acquire in the supplied, reviewed order; retain and check inode ownership."""
    handles = []
    def check():
        for path, fd, identity in handles:
            P.require((path.stat().st_dev, path.stat().st_ino) == identity and
                      (os.fstat(fd).st_dev, os.fstat(fd).st_ino) == identity and
                      not path.is_symlink(), "held lock replaced")
    try:
        for path in paths:
            path = Path(path)
            canonical(path.parent)
            P.require(not path.is_symlink(), "lock alias")
            fd = os.open(path, os.O_RDWR | os.O_CREAT | os.O_NOFOLLOW, 0o600)
            try:
                st = os.fstat(fd)
                P.require(stat.S_ISREG(st.st_mode) and st.st_nlink == 1, "lock file alias")
                fcntl.flock(fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
            except BaseException:
                os.close(fd)
                raise
            handles.append((path, fd, (st.st_dev, st.st_ino)))
        check()
        yield check
    finally:
        for _, fd, _ in reversed(handles):
            os.close(fd)


def verify_manifest(path, *, files, dependencies, data_files, pinned_sha256):
    """The caller enumerates the complete import/data closure; omission rejects."""
    raw = read(path)[0]
    P.require(sha(raw) == pinned_sha256, "source manifest pin mismatch")
    manifest = json.loads(raw)
    P.require(manifest.get("schema") == 1, "source manifest schema")
    for key, expected in (("files", files), ("dependencies", dependencies), ("data", data_files)):
        entries = manifest.get(key)
        P.require(isinstance(entries, dict) and set(entries) == set(map(str, expected)),
                  "incomplete manifest closure: " + key)
        for name, digest in entries.items():
            P.require(re.fullmatch("[0-9a-f]{64}", digest) is not None and
                      sha(read(Path(name))[0]) == digest, "dependency/data drift: " + name)
    return manifest


def stage_fingerprint(stage):
    return sha(json.dumps(stage, sort_keys=True, separators=(",", ":")).encode())


def validate_stage(stage, roots, stage_dir):
    P.require(stage.get("profile_count") == 48 and stage.get("changed_files") == 51,
              "staging scope")
    P.assignments(stage["receipts"])
    records = stage["files"]
    P.require(isinstance(records, list) and len(records) >= 51, "staging files")
    paths = [r["path"] for r in records]
    P.require(len(paths) == len(set(paths)), "duplicate staging path")
    changed = [r for r in records if r["changed"] is True]
    P.name_only_paths([r["path"] for r in changed], roots)
    before, after = {}, {}
    for row in records:
        path = Path(row["path"])
        P.require(path.is_absolute() and str(path) == row["path"], "staging path")
        P.require(type(row["changed"]) is bool, "staging changed flag")
        for which, digest in (("before", row["sha256"]), ("after", row["after_sha256"])):
            rel = Path(row[which+"_blob"])
            P.require(not rel.is_absolute() and re.fullmatch(r"(before|after)/[0-9]+\.bin", str(rel)),
                      "staging blob path")
            payload = read(stage_dir/rel)[0]
            P.require(sha(payload) == digest, "staging payload drift")
            (before if which == "before" else after)[row["path"]] = payload
        if not row["changed"]:
            P.require(before[row["path"]] == after[row["path"]], "undeclared staged mutation")
    red = roots["redstation"]
    pins = {red+"/launch-bot"+s+".sh": sha(before[red+"/launch-bot"+s+".sh"]) for s in ("A", "B")}
    expected, _ = N.plan(stage["receipts"], before, roots, pins)
    P.require(set(expected) == {r["path"] for r in changed}, "name-only payload scope")
    for path, payload in expected.items():
        P.require(after[path] == payload, "staged payload is not the independently derived name-only plan")


def read_log_prefix(path):
    """Read the current bounded prefix of an append-only log, allowing later appends."""
    path = canonical(path)
    before = path.lstat()
    P.require(stat.S_ISREG(before.st_mode) and before.st_nlink == 1 and
              0 < before.st_size <= 512*1024*1024, 'server log size/type')
    fd = os.open(path, os.O_RDONLY | os.O_NOFOLLOW)
    with os.fdopen(fd, 'rb') as stream:
        opened = os.fstat(stream.fileno())
        data = stream.read(before.st_size)
        finished = os.fstat(stream.fileno())
    after = path.lstat()
    identity = [before.st_dev, before.st_ino]
    P.require(len(data) == before.st_size and all(
        [st.st_dev, st.st_ino] == identity and st.st_size >= before.st_size
        for st in (opened, finished, after)), 'server log changed while reading prefix')
    return data, identity


def log_bytes(target, adapter):
    """Require a writable FD of the exact native generation to reference this log."""
    path = canonical(Path(target["root"])/"SeriousSam.log")
    P.require(adapter.same(target["identity"]), "log process generation changed")
    before = path.stat()
    P.require(stat.S_ISREG(before.st_mode) and 0 < before.st_size <= 512*1024*1024,
              "log size/type")
    proc = Path(getattr(adapter, "proc", "/proc"))/str(target["identity"]["pid"])
    matched = False
    for fd in (proc/"fd").iterdir():
        try:
            st = fd.stat()
            if (st.st_dev, st.st_ino) != (before.st_dev, before.st_ino):
                continue
            flags = re.search(r"(?m)^flags:\s*([0-7]+)$", (proc/"fdinfo"/fd.name).read_text())
            if flags and int(flags[1], 8) & 3 in (os.O_WRONLY, os.O_RDWR):
                matched = True
                break
        except (FileNotFoundError, ProcessLookupError):
            continue
    P.require(matched, "current native generation does not own writable log FD")
    fd = os.open(path, os.O_RDONLY | os.O_NOFOLLOW)
    with os.fdopen(fd, "rb") as stream:
        opened = os.fstat(stream.fileno())
        data = stream.read(before.st_size)
        finished = os.fstat(stream.fileno())
    after = path.stat()
    P.require(len(data) == before.st_size and
              all((st.st_dev, st.st_ino) == (before.st_dev, before.st_ino)
                  for st in (opened, finished, after)) and
              after.st_size >= before.st_size, "live log rotated or truncated during read")
    P.require(adapter.same(target["identity"]), "log process changed after read")
    text = data.decode("latin1")
    P.require(text.count("--- Serious Engine Startup ---") == 1, "ambiguous startup log epoch")
    return text


class Backend:
    def __init__(self, m, out, stage, *, roots, stage_dir, lock_guard=None,
                 source_fingerprint=None, launch_helper_pins=None):
        self.m, self.out, self.stage = m, canonical(out), copy.deepcopy(stage)
        self.roots = {i: str(canonical(roots[i])) for i in P.INSTANCES}
        P.require(set(roots) == set(P.INSTANCES) and len(set(self.roots.values())) == 6, "six roots")
        self.stage_dir = canonical(stage_dir)
        self.lock_guard = lock_guard
        self.source_fingerprint = source_fingerprint
        self.launch_helper_pins = dict(launch_helper_pins or {})
        allowed_helpers = {str(Path(root)/"wait-server.py")
                           for key, root in self.roots.items() if key != "redstation"}
        P.require(set(self.launch_helper_pins) <= allowed_helpers and all(
            isinstance(digest, str) and re.fullmatch("[0-9a-f]{64}", digest)
            for digest in self.launch_helper_pins.values()), "reviewed launch helper scope")
        self.guard_launch_helpers()
        validate_stage(self.stage, self.roots, self.stage_dir)
        self.fleet = json.loads(read(m.MATRIX)[0])["instances"]
        P.require(len(self.fleet) == 6 and {x["id"] for x in self.fleet} == set(P.INSTANCES),
                  "six actual instances")
        units = []
        for inst in self.fleet:
            inst["port"] = int(inst["address"].rsplit(":", 1)[1])
            P.require(len(inst["clients"]) == 2, "exactly two clients")
            units.append(inst["server"]["unit"])
            for role, client in zip(("botA", "botB"), inst["clients"]):
                P.require(client["root"] == self.roots[inst["id"]]+"/"+role, "matrix client root")
                units.append(client["unit"])
        P.require(len(set(units)) == 18, "distinct server/client services")
        self.rows = self.stage["receipts"]
        self.state = dict(schema=3, scope=SCOPE, status="PREPARED", events=[],
                          roots=self.roots, stage_sha256=stage_fingerprint(self.stage),
                          source_fingerprint=source_fingerprint,
                          launch_helper_pins=self.launch_helper_pins.copy(), boot_id=m.boot_id(),
                          before={}, server_log_baselines={}, backups={}, started={}, start_intents={}, stop_intents={},
                          stop_acks={}, mutated=[], qualified=False)
        self._journal_digest = None

    def event(self, state, **fields):
        self.state["status"] = state
        self.state["events"].append(dict(state=state, utc=self.m.utc(), **fields))
        raw = (json.dumps(self.state, indent=2)+"\n").encode()
        atomic(self.out/"journal.json", raw, expected=self._journal_digest,
               create_only=self._journal_digest is None)
        self._journal_digest = sha(raw)

    def clients(self):
        for inst in self.fleet:
            for role, client in zip(("botA", "botB"), inst["clients"]):
                yield inst, role, client

    def invocation(self, unit):
        value = self.m.ops["properties"](unit, "InvocationID")["InvocationID"]
        P.require(re.fullmatch("[0-9a-f]{32}", value) and int(value, 16), "service invocation missing")
        return value

    def guard_launch_helpers(self):
        for path, digest in self.launch_helper_pins.items():
            P.require(sha(read(path)[0]) == digest, "reviewed launch helper drift: " + path)

    def stop_policy(self, unit):
        # properties() is last-row-wins; raw show preserves repeated pre/stop commands.
        raw = self.m.command("systemctl", "show", "--all", unit,
                             *("-p"+key for key in SERVICE_POLICY_FIELDS))
        policy = parse_service_policy(raw)
        P.require(set(STOP_POLICY) <= policy.keys(), "incomplete service stop policy")
        client = next(c for _, _, c in self.clients() if c["unit"] == unit)
        validate_launch_policy(policy, client_root=client["root"],
                               launch_helper_pins=self.launch_helper_pins,
                               read_bytes=lambda path: read(path)[0])
        return policy

    def public_query(self, inst):
        host, port = inst["address"].rsplit(":", 1)
        q = self.m.query(host, int(port)+1, timeout=2, attempts=2)
        P.require(q.get("gamever") == "1.07" and q.get("hostport") == port, "public endpoint identity")
        names = [v for k, v in q.items() if re.fullmatch(r"player_\d+", k)]
        P.require(int(q["numplayers"]) == len(names), "incomplete public name list")
        return q, names

    def target(self, inst, role, client):
        P.require(self.m.props(client["unit"])["ActiveState"] == "active", "own client service state")
        invocation = self.invocation(client["unit"])
        target = dict(role=role, server=False, root=client["root"], unit=client["unit"],
                      identity=self.m.native(client["root"], client["unit"]),
                      pins=self.m.pins(client["root"], False), invocation_id=invocation)
        P.require(self.invocation(client["unit"]) == invocation, "invocation changed during identity read")
        return target

    def guard_servers(self):
        self.guard_launch_helpers()
        if self.lock_guard:
            self.lock_guard()
        P.require(self.m.boot_id() == self.state["boot_id"], "host rebooted since transaction")
        for inst in self.fleet:
            old = self.state["before"][inst["id"]]["server"]
            server = inst["server"]
            P.require(self.m.native(server["root"], server["unit"], True) == old["identity"],
                      "Dedicated PID/start changed")
            P.require(self.m.pins(server["root"], True) == old["pins"], "Dedicated files changed")

    def generation_log(self, target):
        P.require(self.invocation(target["unit"]) == target["invocation_id"], "log invocation changed")
        text = log_bytes(target, self.m)
        P.require(self.invocation(target["unit"]) == target["invocation_id"], "log invocation changed")
        return text

    def actual_rows(self, target):
        return P.attach_rows(self.generation_log(target))

    def observation(self, inst, *, scan_errors=False):
        locals_, targets, logs = [], {}, {}
        for role, client in zip(("botA", "botB"), inst["clients"]):
            target = self.target(inst, role, client)
            targets[role] = target
            root = Path(client["root"])
            text = self.generation_log(target)
            if scan_errors:
                data = text.encode('latin1')
                logs[role] = dict(bytes=len(data), sha256=sha(data), events=scan_log_errors(data),
                                  scope='CURRENT_STARTED_NATIVE_GENERATION_SNAPSHOT')
            for row in P.attach_rows(text):
                data = read(root/f'Players/Player{row["local"]}.plr')[0]
                n, _, guid = N.parse_plc(data)
                P.require(read(root/f'Players/Player{row["local"]}.plr.guid')[0] == guid, "GUID sidecar drift")
                locals_.append(dict(row, role=role, guid=guid.hex(),
                                    profile_native=data[8:8+n].decode("ascii")))
            P.require(self.target(inst, role, client) == target, "process changed during local evidence")
        q, names = self.public_query(inst)
        return dict(locals=locals_, query_names=names, query=q, targets=targets, logs=logs)

    def capture_server_log_baseline(self, inst):
        server = inst['server']
        expected = self.state['before'][inst['id']]['server']['identity']
        P.require(self.m.native(server['root'], server['unit'], True) == expected,
                  'server generation changed before log baseline')
        source = Path(server['root'])/'Dedicated_BotTest.log'
        data, identity = read_log_prefix(source)
        P.require(self.m.native(server['root'], server['unit'], True) == expected,
                  'server generation changed during log baseline')
        folder = self.out/'server-log-baselines'
        folder.mkdir(exist_ok=True, mode=0o700)
        sync_dir(self.out)
        path = folder/(inst['id']+'.log')
        atomic(path, data, create_only=True)
        self.state['server_log_baselines'][inst['id']] = dict(
            path=str(path), source=str(source), source_identity=identity,
            generation=expected, bytes=len(data), sha256=sha(data), events=scan_log_errors(data),
            scope='HISTORICAL_DEDICATED_PREFIX_NOT_RUNTIME_QUALIFICATION')

    def validate_server_baseline(self, inst, baseline, expected):
        P.require(baseline['path'] == str(self.out/'server-log-baselines'/(inst['id']+'.log')) and
                  baseline['source'] == str(Path(inst['server']['root'])/'Dedicated_BotTest.log') and
                  baseline['generation'] == expected, 'server log baseline scope/generation')
        prefix = read(baseline['path'])[0]
        P.require(type(baseline['bytes']) is int and baseline['bytes'] == len(prefix) and
                  sha(prefix) == baseline['sha256'], 'server log baseline prefix corrupt')
        P.require(isinstance(baseline['source_identity'], list) and len(baseline['source_identity']) == 2 and
                  all(type(n) is int and n > 0 for n in baseline['source_identity']), 'server log baseline identity')
        return prefix

    def check_server_logs(self, purpose):
        self.guard_servers()
        checks = {}
        for inst in self.fleet:
            baseline = self.state['server_log_baselines'][inst['id']]
            prefix = self.validate_server_baseline(inst, baseline,
                self.state['before'][inst['id']]['server']['identity'])
            data, identity = read_log_prefix(baseline['source'])
            P.require(identity == baseline['source_identity'], 'server log identity changed: '+inst['id'])
            P.require(len(data) >= len(prefix) and data[:len(prefix)] == prefix,
                      'server log prefix changed or truncated: '+inst['id'])
            events = scan_log_errors(data, after=len(prefix))
            checks[inst['id']] = dict(bytes=len(data), sha256=sha(data),
                baseline_bytes=len(prefix), baseline_sha256=baseline['sha256'],
                new_events={k: events[k] for k in ('bad_sync', 'sync_disconnect')})
        self.guard_servers()
        self.state.setdefault('server_log_checks', []).append(dict(purpose=purpose, instances=checks))
        self.event('server_log_checked', purpose=purpose)
        P.require(not any(any(r['new_events'].values()) for r in checks.values()),
                  'new server log sync error after preflight baseline')

    def preflight(self):
        P.require(shutil.disk_usage(self.out).free > 8*2**30, "disk reserve")
        observations = {}
        for inst in self.fleet:
            server = inst['server']
            self.state['before'][inst['id']] = dict(server=dict(
                identity=self.m.native(server['root'], server['unit'], True),
                pins=self.m.pins(server['root'], True)))
            self.capture_server_log_baseline(inst)
            ob = self.observation(inst)
            self.state['before'][inst['id']].update(observation=ob,
                stop_policies={c['unit']: self.stop_policy(c['unit']) for c in inst['clients']})
            observations[inst['id']] = ob
        self.event('server_log_baselines_durable')
        P.fleet(self.rows, observations)
        for row in self.stage["files"]:
            P.require(sha(read(row["path"])[0]) == row["sha256"], "staging source drift; recapture/review required")
        self.check_server_logs("preflight")
        self.event("fresh_six_public_queries_and_48_local_identities")

    def backup(self, label):
        folder = self.out/label
        folder.mkdir(mode=0o700)
        sync_dir(self.out)
        records = {}
        for n, row in enumerate(self.stage["files"]):
            path = Path(row["path"])
            data, meta = read(path)
            blob = folder/f"{n:04d}.bin"
            atomic(blob, data, create_only=True)
            records[str(path)] = dict(blob=str(blob), sha256=sha(data), meta=meta)
        self.state["backups"][label] = records
        self.event(label+"_durable")

    def backup_before_close(self):
        self.backup("preclose")

    def stopped(self, client):
        P.require(not self.m.ops["service_processes"](client["unit"]), "own service not quiescent")
        P.require(self.m.props(client["unit"])["ActiveState"] in ("inactive", "failed"), "own service not stopped")

    def archive(self, inst, role, client, label):
        folder = self.out/inst["id"]
        folder.mkdir(exist_ok=True)
        root = Path(client["root"])
        dest = folder/(role+"-"+label+"-"+uuid.uuid4().hex+"-closed.log")
        result = archive_closed_role_logs(role_roots={role: root}, source_logs={role: root/"SeriousSam.log"},
            archive_logs={role: dest}, cleanup={role: {"closed": True}}, expected_roles=[role],
            max_log_bytes=512*1024*1024)
        if dest.exists():
            with dest.open("rb") as stream:
                os.fsync(stream.fileno())
            sync_dir(folder)
        self.state.setdefault("closed_logs", []).append(dict(instance=inst["id"], role=role,
            label=label, path=str(dest), accepted=result.accepted, reasons=result.reasons, logs=result.logs))
        self.event("closed_log_archived")
        retained_failure = label == "rollback" and role in result.logs and all(
            why == "log_events:"+role for why in result.reasons)
        P.require(result.accepted or retained_failure, "closed log rejected: "+repr(result.reasons))

    def own_current(self, inst, role, client):
        key = inst["id"]+"/"+role
        target = self.target(inst, role, client)
        old = self.state["before"][inst["id"]]["observation"]["targets"][role]
        intent = self.state["start_intents"].get(key)
        recorded = self.state["started"].get(key)
        if intent and recorded is None:
            invocation = intent.get("invocation_id")
            P.require(invocation and target["invocation_id"] == invocation,
                      "unrecorded interrupted start invocation; explicit identity review required")
            P.require(target["identity"]["start"] >= intent["floor_ticks"] and
                      target["identity"] != old["identity"] and target["pins"] == old["pins"],
                      "interrupted start identity/pins mismatch")
            self.state["started"][key] = target
            self.event("interrupted_start_identity_recovered", key=key)
            return target
        expected = recorded or old
        P.require(target["invocation_id"] == expected["invocation_id"], "refuse replaced service invocation")
        P.require(target == expected, "refuse to close unrecorded/replaced client")
        return target

    def close_one(self, inst, role, client, label):
        self.guard_servers()
        key, unit = inst["id"]+"/"+role, client["unit"]
        if self.m.ops["service_processes"](unit):
            target = self.own_current(inst, role, client)
            record_role = role+"-"+label+"-"+uuid.uuid4().hex
            self.state["stop_intents"][key] = dict(target=target, record_role=record_role)
            self.event("client_stop_intent", key=key)
            folder = self.out/inst["id"]
            folder.mkdir(exist_ok=True)
            self.m.stop(dict(target, role=record_role), folder)
        self.stopped(client)
        intent = self.state["stop_intents"].get(key)
        P.require(intent is not None, "stopped client lacks own normal-close intent")
        ack = json.loads(read(self.out/inst["id"]/(intent["record_role"]+"-stop.ack"))[0])
        P.require(ack.get("closed") is True and ack.get("identity") == intent["target"]["identity"],
                  "normal-close acknowledgement identity")
        self.state["stop_acks"][key] = ack["identity"]
        self.event("own_normal_close", instance=inst["id"], role=role)
        self.archive(inst, role, client, label)

    def close_own_clients(self):
        for inst, role, client in self.clients():
            self.close_one(inst, role, client, "apply")
        self.no_own_names_connected()
        self.guard_servers()

    def no_own_names_connected(self):
        for inst in self.fleet:
            own = {P.legacy_display(r["native"]) for r in self.state["before"][inst["id"]]["observation"]["locals"]}
            started_roles = {role for role in ('botA', 'botB')
                             if (intent := self.state['start_intents'].get(inst['id']+'/'+role))
                             and intent.get('invocation_id') and not intent['rollback']}
            own.update(P.legacy_display(r['native_name']) for r in self.rows
                       if r['instance'] == inst['id'] and r['role'] in started_roles)
            self.m.wait(lambda: not (own & {P.legacy_display(n) for n in self.public_query(inst)[1]}),
                        45, "own names still present; do not remove others")

    def backup_after_close(self):
        for _, _, client in self.clients():
            self.stopped(client)
        self.backup("postclose")
        for path, row in self.state["backups"]["postclose"].items():
            P.require(row["sha256"] == self.state["backups"]["preclose"][path]["sha256"],
                      "post-close input changed; reviewed restage needed")

    def changed(self):
        return [r for r in self.stage["files"] if r["changed"]]

    def replace(self, path, data, *, restore_meta=None):
        allowed = self.mutable_paths() if restore_meta is not None else {r['path'] for r in self.changed()}
        P.require(str(path) in allowed, 'write scope excludes binaries, servers and undeclared files')
        current, meta = read(path)
        if restore_meta is not None:
            meta = restore_meta
        self.state["mutated"].append(str(path))
        self.event("write_intent", path=str(path), before=sha(current), after=sha(data))
        self.guard_servers()
        atomic(path, data, expected=sha(current), meta=meta)

    def check_collision_now(self):
        from collections import Counter
        proposed = P.assignments(self.rows)
        for inst in self.fleet:
            active = []
            for role, client in zip(("botA", "botB"), inst["clients"]):
                key = inst["id"]+"/"+role
                if key in self.state["started"]:
                    target = self.own_current(inst, role, client)
                    active.extend(P.legacy_display(r["native"]) for r in self.actual_rows(target))
            names = Counter(P.legacy_display(n) for n in self.public_query(inst)[1])
            for name in active:
                P.require(names[name] == 1, "running own name ambiguous")
                del names[name]
            P.require(not (set(names) & proposed), "fresh occupied-name collision")

    def apply_names(self):
        self.guard_servers()
        self.check_collision_now()
        for _, _, client in self.clients():
            self.stopped(client)
        P.name_only_paths([r["path"] for r in self.changed()], self.roots)
        validate_stage(self.stage, self.roots, self.stage_dir)
        for row in self.changed():
            P.require(sha(read(row["path"])[0]) == row["sha256"], "apply source drift")
            self.replace(Path(row["path"]), read(self.stage_dir/row["after_blob"])[0])
        self.guard_servers()

    def start_one(self, inst, role, client, rollback=False):
        self.guard_servers()
        self.stopped(client)
        P.require(self.stop_policy(client["unit"]) == self.state["before"][inst["id"]]["stop_policies"][client["unit"]],
                  "normal-close service policy not restored")
        key = inst["id"]+"/"+role
        log = Path(client["root"])/"SeriousSam.log"
        st = log.stat()
        old = self.state["before"][inst["id"]]["observation"]["targets"][role]
        self.state["started"].pop(key, None)
        previous_invocation = self.m.ops['properties'](client['unit'], 'InvocationID')['InvocationID']
        self.state["start_intents"][key] = dict(floor_ticks=self.m.clock_ticks(),
            previous_invocation=previous_invocation, invocation_id=None, log_before=list(signature(st)), rollback=rollback)
        self.event("client_start_intent", instance=inst["id"], role=role, rollback=rollback)
        self.m.command("systemctl", "start", "--no-block", client["unit"])
        def invocation_ready():
            try:
                invocation = self.invocation(client["unit"])
            except ValueError:
                return False
            if invocation in (previous_invocation, old['invocation_id']):
                return False
            if self.m.props(client['unit'])['ActiveState'] not in ('activating', 'active'):
                return False
            self.state["start_intents"][key]["invocation_id"] = invocation
            self.event("service_start_invocation", key=key)
            return True
        self.m.wait(invocation_ready, 15, "own service invocation not identified")
        def native_ready():
            try:
                target = self.target(inst, role, client)
            except (OSError, ValueError, AssertionError, RuntimeError):
                return False
            P.require(target["invocation_id"] == self.state["start_intents"][key]["invocation_id"],
                      "started invocation changed")
            P.require(target["pins"] == old["pins"], "DLL/config changed")
            P.require(target["identity"]["start"] >= self.state["start_intents"][key]["floor_ticks"] and
                      target["identity"] != old["identity"], "native start predates start intent")
            self.state["started"][key] = target
            self.event("started_identity", key=key)
            return True
        self.m.wait(native_ready, 40, "own client native start not identified")
        expected = ({r["local"]: r["native"] for r in self.state["before"][inst["id"]]["observation"]["locals"] if r["role"] == role}
                    if rollback else {r["local"]: r["native_name"] for r in self.rows if r["instance"] == inst["id"] and r["role"] == role})
        def joined():
            self.guard_servers()
            target = self.own_current(inst, role, client)
            P.require(list(signature(log.stat())) != self.state["start_intents"][key]["log_before"],
                      "unchanged pre-start log")
            try:
                actual = self.actual_rows(target)
                names = [P.legacy_display(x) for x in self.public_query(inst)[1]]
                return {r["local"]: r["native"] for r in actual} == expected and all(
                    names.count(P.legacy_display(n)) == 1 for n in expected.values())
            except (OSError, ValueError, AssertionError):
                return False
        self.m.wait(joined, 150, "all four actual locals failed to join")

    def start_own_clients(self):
        for inst, role, client in self.clients():
            self.check_collision_now()
            self.start_one(inst, role, client)

    def require_started_generations(self, observations):
        expected = {inst['id']+'/'+role for inst, role, _ in self.clients()}
        P.require(set(self.state['started']) == expected, 'final generation records incomplete')
        for inst, role, client in self.clients():
            recorded = self.state['started'][inst['id']+'/'+role]
            observed = observations[inst['id']]['targets'][role]
            P.require(observed == recorded and self.target(inst, role, client) == recorded,
                      'final client generation differs from durable started identity')
            P.require(not any(observations[inst['id']]['logs'][role]['events'].values()),
                      'new client generation log contains error events')

    def verify_applied(self):
        observations = {i["id"]: self.observation(i, scan_errors=True) for i in self.fleet}
        self.state["after"] = observations
        self.require_started_generations(observations)
        result = P.fleet(self.rows, observations, applied=True)
        self.check_server_logs("verify_applied")
        for path, row in self.state["backups"]["postclose"].items():
            expected = next((x["after_sha256"] for x in self.changed() if x["path"] == path), row["sha256"])
            P.require(sha(read(path)[0]) == expected, "unexpected live file mutation")
        self.require_started_generations(observations)
        return dict(result, query_scope="HOST_TO_PUBLIC_IP_ORIGINAL_GAMESPY",
                    external_browser_or_WAN_qualification=False)

    def rollback_close(self):
        errors = []
        for inst, role, client in self.clients():
            try:
                self.close_one(inst, role, client, "rollback")
            except BaseException as error:
                errors.append(repr(error))
        P.require(not errors, "rollback normal-close failures: "+repr(errors))
        for _, _, client in self.clients():
            self.stopped(client)
        self.no_own_names_connected()

    def mutable_paths(self):
        mutable = {r["path"] for r in self.changed()}
        for row in self.stage["files"]:
            path = Path(row["path"])
            for _, _, client in self.clients():
                if path.is_relative_to(Path(client["root"])):
                    rel = path.relative_to(client["root"])
                    if len(rel.parts) > 1 and rel.parts[0] in ("Players", "Controls", "Scripts", "Data"):
                        mutable.add(str(path))
        return mutable

    def validate_backup(self, label, records):
        expected = {r["path"]: n for n, r in enumerate(self.stage["files"])}
        P.require(label in ("preclose", "postclose") and set(records) == set(expected), "backup scope")
        for path, row in records.items():
            P.require(row["blob"] == str(self.out/label/f"{expected[path]:04d}.bin"), "backup blob escape")
            data = read(row["blob"])[0]
            P.require(sha(data) == row["sha256"], "backup corrupt")
            meta = row["meta"]
            P.require(set(meta) == {"uid", "gid", "mode"} and all(type(v) is int and v >= 0 for v in meta.values()) and
                      meta["mode"] <= 0o7777, "backup metadata")

    def rollback_restore(self):
        self.guard_servers()
        for _, _, client in self.clients():
            self.stopped(client)
        label = "postclose" if "postclose" in self.state["backups"] else "preclose"
        backup = self.state["backups"][label]
        self.validate_backup(label, backup)
        self.state["rollback_base"] = backup
        mutable = self.mutable_paths()
        # Validate every immutable file before the first restore write.
        for path, row in backup.items():
            if path not in mutable:
                P.require(sha(read(path)[0]) == row["sha256"], "nonmutable file changed")
        for path, row in backup.items():
            if path not in mutable:
                continue
            p, data = Path(path), read(row["blob"])[0]
            if path in (self.roots["redstation"]+"/launch-botA.sh", self.roots["redstation"]+"/launch-botB.sh"):
                data = N.patch_launcher(data, self.roots["redstation"], p.stem[-1], row["sha256"])
            self.replace(p, data, restore_meta=row["meta"])
            # Restore original metadata, including after a normal save changed it.
            P.require(read(p)[1] == row["meta"], "restored metadata differs")

    def rollback_start(self):
        self.state["started"] = {}
        self.event("rollback_start_reset_identity_records")
        for inst, role, client in self.clients():
            self.start_one(inst, role, client, rollback=True)

    def rollback_verify(self):
        from collections import Counter
        self.guard_servers()
        observations = {i["id"]: self.observation(i, scan_errors=True) for i in self.fleet}
        self.state['rollback_observations'] = observations
        self.require_started_generations(observations)
        for instance, ob in observations.items():
            old = self.state["before"][instance]["observation"]["locals"]
            P.require([(r["role"], r["local"], r["native"], r["guid"]) for r in ob["locals"]] ==
                      [(r["role"], r["local"], r["native"], r["guid"]) for r in old],
                      "rollback actual local identities")
            names = Counter(P.legacy_display(n) for n in ob["query_names"])
            P.require(all(names[P.legacy_display(r["native"])] == 1 for r in old), "rollback public query identity")
        self.state["rollback_observations"] = observations

    def rollback_launch_policy(self):
        for side in ("A", "B"):
            path = Path(self.roots["redstation"])/f"launch-bot{side}.sh"
            row = self.state["rollback_base"][str(path)]
            data = read(row["blob"])[0]
            P.require(sha(read(path)[0]) == sha(N.patch_launcher(data, self.roots["redstation"], side, row["sha256"])),
                      "rollback bypass launcher drift")
            self.replace(path, data)
        for path, row in self.state["rollback_base"].items():
            data, meta = read(path)
            P.require(sha(data) == row["sha256"] and meta == row["meta"], "rollback final byte/metadata mismatch")
        self.guard_servers()

    def load_recovery(self, state):
        P.require(state.get("schema") == 3 and state.get("scope") == SCOPE and
                  state.get("status") in RECOVERABLE and state.get("qualified") is False,
                  "recovery state not eligible")
        self._load_bound_recovery(state)

    def _load_bound_recovery(self, state):
        """Shared exact bindings; each controller checks its own schema/phases first."""
        P.require(state.get("roots") == self.roots and state.get("stage_sha256") == stage_fingerprint(self.stage) and
                  state.get("source_fingerprint") == self.source_fingerprint and
                  state.get("launch_helper_pins") == self.launch_helper_pins and
                  state.get("boot_id") == self.m.boot_id(), "recovery source/root/boot mismatch")
        P.require(set(state.get("before", {})) == set(P.INSTANCES) and
                  "preclose" in state.get("backups", {}), "recovery lacks complete preclose evidence")
        for label, records in state["backups"].items():
            self.validate_backup(label, records)
        P.require(set(state.get('server_log_baselines', {})) == set(P.INSTANCES), 'recovery server log baselines incomplete')
        for inst in self.fleet:
            self.validate_server_baseline(inst, state['server_log_baselines'][inst['id']],
                                          state['before'][inst['id']]['server']['identity'])
        expected = {i["id"]+"/"+r: (i, r, c) for i, r, c in self.clients()}
        for mapping in ("started", "start_intents", "stop_intents", "stop_acks"):
            P.require(isinstance(state.get(mapping), dict) and set(state[mapping]) <= set(expected),
                      "recovery client scope")
        P.require(set(state.get("mutated", [])) <= self.mutable_paths(), "recovery write scope")
        for key, target in state["started"].items():
            inst, role, client = expected[key]
            P.require(target["role"] == role and target["root"] == client["root"] and
                      target["unit"] == client["unit"] and target["server"] is False,
                      "recovery recorded target scope")
        for key, intent in state["stop_intents"].items():
            inst, role, client = expected[key]
            target = intent["target"]
            P.require(target["root"] == client["root"] and target["unit"] == client["unit"] and
                      target["server"] is False and target["role"] == role and
                      re.fullmatch(role+r"-(apply|rollback)-[0-9a-f]{32}", intent["record_role"]),
                      "recovery stop intent scope")
        for intent in state["start_intents"].values():
            P.require(type(intent["floor_ticks"]) is int and intent["floor_ticks"] > 0 and
                      (intent["invocation_id"] is None or re.fullmatch("[0-9a-f]{32}", intent["invocation_id"])),
                      "recovery start intent")
        self.state = copy.deepcopy(state)
        raw = read(self.out/"journal.json")[0]
        P.require(json.loads(raw) == state, "recovery journal changed")
        self._journal_digest = sha(raw)
        self.guard_servers()
