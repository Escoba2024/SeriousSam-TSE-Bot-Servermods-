"""Real temporary files; only service/process/query boundaries are simulated."""
import copy
import hashlib
import json
import os
from pathlib import Path
import struct
import subprocess
import tempfile
import unittest
from unittest.mock import patch

import fleet_names_apply_policy as P
import fleet_names_transaction as T
import names_staging as N
from gaming_names import name_id


def plc(name, number):
    raw = name.encode("ascii")
    return b"PLC4" + struct.pack("<I", len(raw)) + raw + bytes(4) + number.to_bytes(16, "little") + bytes(32)


class Services:
    """External service double backed by a real filesystem and fake proc tree."""
    def __init__(self, base, fleet):
        self.MATRIX = base / "matrix.json"
        self.MATRIX.write_text(json.dumps({"instances": fleet}))
        self.proc = base / "proc"
        self.proc.mkdir()
        self.fleet = fleet
        self.running = {}
        self.loaded = {}
        self.invocations = {}
        self.units = {}
        self.stop_history = []
        self.start_history = []
        self.generation = 100
        self.unresolvable = set()
        self.interrupt_command = False
        self.extra_names = []
        self.raw_policy_rows = {}
        self.ops = {"service_processes": self.service_processes,
                    "properties": self.properties}
        for inst in fleet:
            for role, c in [("server", inst["server"]), *zip(("botA", "botB"), inst["clients"])]:
                self.units[c["unit"]] = (inst, role, c)
                self.spawn(c["unit"])

    def utc(self):
        return "2026-01-01T00:00:00+00:00"

    def boot_id(self):
        return "12345678-1234-1234-1234-123456789abc"

    def clock_ticks(self):
        return self.generation + 1

    def spawn(self, unit):
        inst, role, c = self.units[unit]
        self.generation += 1
        ident = {"pid": 1000 + self.generation, "start": self.generation}
        self.running[unit] = ident
        self.invocations[unit] = f"{self.generation:032x}"
        if role == "server":
            return
        root = Path(c["root"])
        names = [self.profile_name(root / f"Players/Player{i}.plr") for i in range(4)]
        self.loaded[unit] = names
        offset = 0 if role == "botA" else 4
        log = root / "SeriousSam.log"
        log.write_text("--- Serious Engine Startup ---\n" + "\n".join(
            f"[BotDriver] local player {i} (player index {offset+i}) is now bot-driven: {n}"
            for i, n in enumerate(names)) + "\n")
        fd = self.proc / str(ident["pid"]) / "fd"
        fd.mkdir(parents=True)
        (fd / "5").symlink_to(log)
        info = fd.parent / "fdinfo"
        info.mkdir()
        (info / "5").write_text("flags:\t0100001\n")

    @staticmethod
    def profile_name(path):
        data = path.read_bytes()
        n = struct.unpack_from("<I", data, 4)[0]
        return data[8:8+n].decode("ascii")

    def properties(self, unit, *keys):
        inst, role, client = self.units[unit]
        launcher = Path(client['root']).parent/('launch-'+role+'.sh')
        values = {'ExecStart': '{ path=/bin/bash ; argv[]=/bin/bash '+str(launcher)+' ; ignore_errors=no ; pid=123 ; }',
                  'ExecStartPre': '', "ActiveState": "active" if unit in self.running else "inactive",
                  "MainPID": str(self.running.get(unit, {}).get("pid", 0)),
                  "InvocationID": self.invocations.get(unit, ""),
                  "ExecStop": "", "KillMode": "control-group",
                  "SendSIGKILL": "yes", "TimeoutStopUSec": "1min 30s",
                  "FragmentPath": "/fixture/systemd/"+unit, "DropInPaths": ""}
        # Preserve the original adapter's last-row-wins behavior here. The new
        # policy reader must use command() raw output instead of this shortcut.
        for line in self.raw_policy_rows.get(unit, '').splitlines():
            key, separator, value = line.partition('=')
            if separator:
                values[key] = value
        return {key: values[key] for key in keys} if keys else values

    def props(self, unit):
        return self.properties(unit)

    def service_processes(self, unit):
        return [self.running[unit]] if unit in self.running else []

    def native(self, root, unit, server=False):
        if unit in self.unresolvable:
            raise AssertionError("native mapping not ready")
        if self.units[unit][2]["root"] != root:
            raise ValueError("wrong native root")
        return copy.deepcopy(self.running[unit])

    def same(self, identity):
        return identity in self.running.values()

    def pins(self, root, server):
        names = ["Bin/GameMP.dll", "Bin/Engine.dll", "Bin/EntitiesMP.dll",
                 "Bin/DedicatedServer.exe" if server else "Bin/SeriousSam.exe",
                 "Scripts/Dedicated/BotTest/1_begin.ini" if server else "Scripts/Integrated.ini"]
        return {name: T.sha((Path(root) / name).read_bytes()) for name in names}

    def query(self, host, port, **kwargs):
        inst = next(i for i in self.fleet if int(i["address"].split(":")[1])+1 == port)
        names = ["Visitor"] + self.extra_names + [
            name for c in inst["clients"] if c["unit"] in self.running
            for name in self.loaded[c["unit"]]]
        return dict(gamever="1.07", hostport=str(port-1), numplayers=str(len(names)),
                    **{f"player_{i}": n for i, n in enumerate(names)})

    def stop(self, target, out):
        unit = target["unit"]
        if target["server"] or self.running.get(unit) != target["identity"]:
            raise ValueError("attempted wrong generation or server stop")
        self.stop_history.append((unit, copy.deepcopy(target["identity"])))
        del self.running[unit]
        path = out / (target["role"] + "-stop.ack")
        path.write_text(json.dumps({"closed": True, "identity": target["identity"]}))

    def command(self, *args, **kwargs):
        if args[:3] == ('systemctl', 'show', '--all'):
            unit, keys = args[3], [arg[2:] for arg in args[4:]]
            values = self.ops['properties'](unit, *keys)
            raw = self.raw_policy_rows.get(unit, '')
            supplied = {line.partition('=')[0] for line in raw.splitlines()}
            return raw + '\n' + '\n'.join(key+'='+values[key] for key in keys if key not in supplied)
        if args[:3] != ("systemctl", "start", "--no-block"):
            raise ValueError("unexpected service operation")
        unit = args[3]
        inst, role, c = self.units[unit]
        if role == "server" or unit in self.running:
            raise ValueError("server or duplicate start")
        self.start_history.append(unit)
        # Execute the actual patched launch byte plan against harmless scripts.
        launch = Path(c["root"]).parent / ("launch-" + role + ".sh")
        subprocess.run(["/bin/bash", str(launch)], check=True, capture_output=True)
        self.spawn(unit)
        if self.interrupt_command:
            self.interrupt_command = False
            raise SystemExit("controller died before invocation receipt")

    def wait(self, fn, seconds, why):
        for _ in range(3):
            if fn():
                return
        raise RuntimeError(why)


class FleetFixture:
    def __init__(self, base):
        self.base = base
        self.roots = {i: str(base / i) for i in P.INSTANCES}
        self.stage_dir = base / "stage"
        self.stage_dir.mkdir()
        self.out = base / "evidence"
        self.out.mkdir()
        fleet, rows, files, pins = [], [], {}, {}
        serial = 0
        for k, instance in enumerate(P.INSTANCES):
            root = Path(self.roots[instance])
            root.mkdir()
            server = root / "server"
            self.write(server / "Bin/GameMP.dll", b"server dll")
            self.write(server / "Bin/Engine.dll", b"engine")
            self.write(server / "Bin/EntitiesMP.dll", b"entities")
            self.write(server / "Bin/DedicatedServer.exe", b"dedicated")
            self.write(server / "Scripts/Dedicated/BotTest/1_begin.ini", b"server config")
            self.write(server / "Dedicated_BotTest.log", b"Dedicated fixture started\n")
            inst = {"id": instance, "address": f"198.51.100.1:{20000+k*10}",
                    "server": {"root": str(server), "unit": instance+"-server.service"}, "clients": []}
            for role in ("botA", "botB"):
                client = root / role
                inst["clients"].append({"root": str(client), "unit": instance+"-"+role+".service"})
                for rel, data in [("Bin/GameMP.dll", b"qualified bot dll"), ("Bin/Engine.dll", b"engine"),
                                  ("Bin/EntitiesMP.dll", b"entities"), ("Bin/SeriousSam.exe", b"native game"),
                                  ("Scripts/Integrated.ini", b"untouched config"),
                                  ("Scripts/BotRosterIds.txt", b"original roster"),
                                  ("Controls/Controls0.ctl", b"controls"), ("Data/SeriousSam.gms", b"settings")]:
                    self.write(client / rel, data)
                    files[str(client / rel)] = data
                for n in range(4):
                    serial += 1
                    path = client / f"Players/Player{n}.plr"
                    before = plc(f"Old{serial}", serial)
                    self.write(path, before)
                    self.write(Path(str(path)+".guid"), serial.to_bytes(16, "little"))
                    files[str(path)] = before
                    files[str(path)+".guid"] = serial.to_bytes(16, "little")
                    new = f"New{serial}"
                    rows.append(dict(instance=instance, role=role, local=n,
                                     bot_id=f"{instance}.bot.{n+(4 if role=='botB' else 0):03d}",
                                     native_name=new, nickname=new, name_id=name_id(new)))
                launch = root / ("launch-"+role+".sh")
                data = b"#!/bin/bash\nexit 0\n"
                if instance == "redstation":
                    side = role[-1]
                    data = (f"#!/bin/bash\n/usr/bin/python3 {root}/rotate-live-identities.py --client {side} || exit 87\n"
                            f"/usr/bin/python3 {root}/generate-bot-roster.py --client {side} || exit 88\n").encode()
                    pins[str(launch)] = T.sha(data)
                self.write(launch, data)
                files[str(launch)] = data
            fleet.append(inst)
        red = Path(self.roots["redstation"])
        self.write(red/"rotate-live-identities.py", (
            "from pathlib import Path\np=Path(__file__).with_name('rotation-count')\n"
            "p.write_text(str(int(p.read_text())+1) if p.exists() else '1')\n").encode())
        self.write(red/"generate-bot-roster.py", b"pass\n")
        self.write(red/"roster100.json", b'{"active": [], "rotate_policy": "original"}\n')
        files[str(red/"roster100.json")] = (red/"roster100.json").read_bytes()
        changes, receipts = N.plan(rows, files, self.roots, pins)
        records = []
        for i, (name, before) in enumerate(sorted(files.items())):
            after = changes.get(name, before)
            before_blob, after_blob = f"before/{i:04d}.bin", f"after/{i:04d}.bin"
            self.write(self.stage_dir/before_blob, before)
            self.write(self.stage_dir/after_blob, after)
            records.append(dict(path=name, sha256=T.sha(before), changed=name in changes,
                                before_blob=before_blob, after_blob=after_blob, after_sha256=T.sha(after)))
        self.stage = dict(profile_count=48, changed_files=51, receipts=receipts, files=records)
        (self.stage_dir/"receipt.json").write_text(json.dumps(self.stage))
        self.m = Services(base, fleet)
        self.b = T.Backend(self.m, self.out, self.stage, roots=self.roots, stage_dir=self.stage_dir)
        self.old = files

    @staticmethod
    def write(path, data):
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(data)

    def prepare_applied(self):
        self.b.preflight()
        self.b.backup_before_close()
        self.b.close_own_clients()
        self.b.backup_after_close()
        self.b.apply_names()

    def restored(self, test):
        for name, before in self.old.items():
            test.assertEqual(Path(name).read_bytes(), before, name)
        test.assertEqual(len(self.m.running), 18)
        test.assertFalse((Path(self.roots["redstation"])/"rotation-count").exists())


class BoundaryTests(unittest.TestCase):
    def test_atomic_rejects_symlink_even_without_expected_digest(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            victim, alias = root/"victim", root/"alias"
            victim.write_bytes(b"keep")
            alias.symlink_to(victim)
            with self.assertRaises((ValueError, OSError)):
                T.atomic(alias, b"wrong")
            self.assertTrue(alias.is_symlink())
            self.assertEqual(victim.read_bytes(), b"keep")

    def test_exact_lock_order_and_conflict_fail_before_mutation(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp)
            roots={i:str(root/i) for i in P.INSTANCES}
            for path in roots.values():Path(path).mkdir()
            install=root/'installer';install.mkdir()
            paths=T.lock_paths(install,root/'deployment.lock',roots)
            self.assertEqual(paths[:3],[install/'fleet-install.lock',root/'deployment.lock',root/'redstation/identity-rotation.lock'])
            with T.exclusive_locks(paths) as guard:
                guard()
                with self.assertRaises(BlockingIOError):
                    with T.exclusive_locks(paths):pass
                paths[0].unlink();paths[0].write_text('replacement')
                with self.assertRaisesRegex(ValueError,'lock replaced'):guard()

    def test_manifest_requires_exact_dependency_and_data_closure(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp)
            paths=[root/'entry.py',root/'backend.py',root/'receipt.json']
            for i,p in enumerate(paths):p.write_text(str(i))
            manifest=dict(schema=1,files={str(paths[0]):T.sha(paths[0].read_bytes())},
                          dependencies={},data={str(paths[2]):T.sha(paths[2].read_bytes())})
            m=root/'manifest.json';m.write_text(json.dumps(manifest))
            with self.assertRaisesRegex(ValueError,'closure'):
                T.verify_manifest(m,files=[paths[0]],dependencies=[paths[1]],data_files=[paths[2]],pinned_sha256=T.sha(m.read_bytes()))
            manifest['dependencies'][str(paths[1])]=T.sha(paths[1].read_bytes())
            m.write_text(json.dumps(manifest))
            T.verify_manifest(m,files=[paths[0]],dependencies=[paths[1]],data_files=[paths[2]],pinned_sha256=T.sha(m.read_bytes()))
            paths[1].write_text('changed')
            with self.assertRaisesRegex(ValueError,'drift'):
                T.verify_manifest(m,files=[paths[0]],dependencies=[paths[1]],data_files=[paths[2]],pinned_sha256=T.sha(m.read_bytes()))

    def test_atomic_preserves_mode_and_rejects_source_drift(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp)/"data"
            path.write_bytes(b"old")
            path.chmod(0o640)
            data, meta = T.read(path)
            T.atomic(path, b"new", expected=T.sha(data), meta=meta)
            self.assertEqual(path.read_bytes(), b"new")
            self.assertEqual(path.stat().st_mode & 0o777, 0o640)
            with self.assertRaises(ValueError):
                T.atomic(path, b"unsafe", expected=T.sha(data), meta=meta)
            self.assertEqual(path.read_bytes(), b"new")


class BackendTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.f = FleetFixture(Path(self.tmp.name))

    def test_complete_names_only_apply_keeps_servers_and_visitors(self):
        f = self.f
        before_servers = {u: i for u, i in f.m.running.items() if "-server." in u}
        result = P.transaction(f.b)
        self.assertEqual(result["own_count"], 48)
        self.assertEqual(result["unknown_counts"], {i: 1 for i in P.INSTANCES})
        self.assertEqual(before_servers, {u: i for u, i in f.m.running.items() if "-server." in u})
        self.assertEqual(json.loads((f.out/"journal.json").read_text())["status"], "applied_names_only")

    def test_failed_verify_restores_all_bytes_and_bypasses_red_rotation(self):
        f = self.f
        with patch.object(f.b, "verify_applied", side_effect=RuntimeError("verification failed")):
            with self.assertRaisesRegex(RuntimeError, "verification failed"):
                P.transaction(f.b)
        f.restored(self)
        self.assertEqual(json.loads((f.out/"journal.json").read_text())["status"], "rolled_back")

    def test_interrupted_native_resolution_recovers_exact_invocation(self):
        f = self.f
        f.prepare_applied()
        inst, role, client = next(f.b.clients())
        f.m.unresolvable.add(client["unit"])
        with self.assertRaisesRegex(RuntimeError, "not identified"):
            f.b.start_one(inst, role, client)
        f.m.unresolvable.clear()
        # Read the actual durable journal, as a new controller would.
        f.b.load_recovery(json.loads((f.out/"journal.json").read_text()))
        P.rollback(f.b)
        f.restored(self)

    def test_start_without_durable_invocation_receipt_never_adopts_new_pid(self):
        f = self.f
        f.prepare_applied()
        inst, role, client = next(f.b.clients())
        f.m.interrupt_command = True
        with self.assertRaises(SystemExit):
            f.b.start_one(inst, role, client)
        started = copy.deepcopy(f.m.running[client["unit"]])
        with self.assertRaisesRegex(ValueError, "unrecorded|invocation"):
            f.b.rollback_close()
        self.assertEqual(f.m.running[client["unit"]], started)

    def test_changed_invocation_is_not_own_even_when_pid_is_same(self):
        f = self.f
        f.prepare_applied()
        inst, role, client = next(f.b.clients())
        f.b.start_one(inst, role, client)
        identity = copy.deepcopy(f.m.running[client["unit"]])
        f.m.invocations[client["unit"]] = "f"*32
        with self.assertRaisesRegex(ValueError, "invocation"):
            f.b.close_one(inst, role, client, "rollback")
        self.assertEqual(f.m.running[client["unit"]], identity)

    def test_write_intent_journal_failure_preserves_current_file(self):
        f = self.f
        f.b.preflight()
        path = Path(f.stage["receipts"][0]["path"])
        before = path.read_bytes()
        original = T.atomic
        def unavailable(p, *args, **kwargs):
            if Path(p).name == "journal.json":
                raise OSError("journal write failed")
            return original(p, *args, **kwargs)
        with patch.object(T, "atomic", side_effect=unavailable):
            with self.assertRaises(OSError):
                f.b.replace(path, b"not installed")
        self.assertEqual(path.read_bytes(), before)

    def test_recovery_rejects_backup_escape_before_mutation(self):
        f = self.f
        f.prepare_applied()
        state = json.loads((f.out/"journal.json").read_text())
        one = next(iter(state["backups"]["postclose"].values()))
        one["blob"] = str(f.base/"untrusted-backup")
        with self.assertRaisesRegex(ValueError, "backup"):
            f.b.load_recovery(state)
        self.assertFalse(f.m.start_history)

    def test_rollback_retains_failing_candidate_log_and_restores_names(self):
        f = self.f
        def fail_after_start():
            client = f.m.fleet[0]["clients"][0]
            with (Path(client["root"])/"SeriousSam.log").open("a") as stream:
                stream.write("Cannot join game: deliberate offline failure\n")
            raise RuntimeError("candidate failed")
        with patch.object(f.b, "verify_applied", side_effect=fail_after_start):
            with self.assertRaisesRegex(RuntimeError, "candidate failed"):
                P.transaction(f.b)
        f.restored(self)
        archives = list(f.out.rglob("*closed.log"))
        self.assertTrue(any(b"deliberate offline failure" in p.read_bytes() for p in archives))

    def test_rollback_restores_saved_metadata_after_engine_save(self):
        f=self.f
        f.prepare_applied()
        path=Path(f.stage['receipts'][0]['path'])
        original_mode=path.stat().st_mode & 0o7777
        path.chmod(0o600 if original_mode != 0o600 else 0o640)
        P.rollback(f.b)
        self.assertEqual(path.stat().st_mode & 0o7777,original_mode)
        f.restored(self)

    def test_new_foreign_collision_before_start_still_allows_old_name_restore(self):
        f=self.f
        original=f.b.apply_names
        def collide():
            f.m.extra_names=['New1']
            original()
        with patch.object(f.b,'apply_names',side_effect=collide):
            with self.assertRaisesRegex(ValueError,'collision'):
                P.transaction(f.b)
        f.restored(self)
        self.assertEqual(f.m.extra_names,['New1'])

    def test_stale_previous_invocation_is_retried_until_new_start_arrives(self):
        f=self.f;f.prepare_applied()
        inst,role,client=next(f.b.clients())
        original=f.m.properties
        previous=f.m.invocations[client['unit']]
        seen=[False]
        def delayed(unit,*keys):
            if keys==('InvocationID',) and unit==client['unit'] and unit in f.m.running and not seen[0]:
                seen[0]=True
                return {'InvocationID':previous}
            return original(unit,*keys)
        f.m.ops['properties']=delayed
        f.b.start_one(inst,role,client)
        self.assertEqual(f.b.state['started'][inst['id']+'/'+role]['invocation_id'],f.m.invocations[client['unit']])

    def test_changed_service_launch_command_is_rejected_before_start(self):
        f=self.f;f.prepare_applied()
        inst,role,client=next(f.b.clients())
        original=f.m.properties
        def changed(unit,*keys):
            values=original(unit,*keys)
            if unit==client['unit'] and 'ExecStart' in values:
                values['ExecStart']='{ path=/bin/bash ; argv[]=/bin/bash /unreviewed-launcher ; ignore_errors=no ; pid=123 ; }'
            return values
        f.m.ops['properties']=changed
        with self.assertRaisesRegex(ValueError,'launcher|policy'):
            f.b.start_one(inst,role,client)
        self.assertNotIn(client['unit'],f.m.running)
        self.assertFalse(f.m.start_history)

    def test_applied_final_rejects_same_names_replacement_generation(self):
        f=self.f;f.prepare_applied();f.b.start_own_clients()
        client=f.m.fleet[0]['clients'][0]
        f.m.spawn(client['unit'])
        with self.assertRaisesRegex(ValueError,'generation'):
            f.b.verify_applied()

    def test_rollback_final_rejects_same_names_replacement_generation(self):
        f=self.f;f.prepare_applied()
        f.b.rollback_close();f.b.rollback_restore();f.b.rollback_start()
        client=f.m.fleet[0]['clients'][0]
        f.m.spawn(client['unit'])
        with self.assertRaisesRegex(ValueError,'generation'):
            f.b.rollback_verify()

    def test_new_client_sync_error_before_success_rolls_back(self):
        f=self.f
        verify=f.b.verify_applied
        def append_then_verify():
            client=f.m.fleet[0]['clients'][0]
            with (Path(client['root'])/'SeriousSam.log').open('ab') as stream:
                stream.write(b"SYNCBAD: Client 'Fixture', Sequence 22 Tick 5.0 - bad 1\n")
            return verify()
        with patch.object(f.b,'verify_applied',side_effect=append_then_verify):
            with self.assertRaisesRegex(ValueError,'client.*log'):
                P.transaction(f.b)
        f.restored(self)
        self.assertEqual(json.loads((f.out/'journal.json').read_text())['status'],'rolled_back')

    def test_historical_server_errors_are_durable_baseline_not_new_errors(self):
        f=self.f
        inst=f.m.fleet[-1];serverlog=Path(inst['server']['root'])/'Dedicated_BotTest.log'
        history=b''.join(f"SYNCBAD: Client 'Fixture', Sequence {n} Tick 5.0 - bad 1\n".encode() for n in range(37))
        history+=b"Client 'Fixture' ordered to disconnect: Too many bad syncs\n"*3
        serverlog.write_bytes(history)
        f.b.preflight()
        saved=json.loads((f.out/'journal.json').read_text())
        baseline=saved['server_log_baselines'][inst['id']]
        self.assertEqual(Path(baseline['path']).read_bytes(),history)
        self.assertEqual(baseline['bytes'],len(history))
        self.assertEqual(baseline['sha256'],hashlib.sha256(history).hexdigest())
        self.assertEqual(len(baseline['events']['bad_sync']),37)
        self.assertEqual(len(baseline['events']['sync_disconnect']),3)
        f.b.backup_before_close();f.b.close_own_clients();f.b.backup_after_close()
        f.b.apply_names();f.b.start_own_clients();f.b.verify_applied()

    def test_server_error_crossing_baseline_boundary_is_new(self):
        f=self.f
        serverlog=Path(f.m.fleet[0]['server']['root'])/'Dedicated_BotTest.log'
        serverlog.write_bytes(b'Dedicated fixture started\n[SY')
        f.b.preflight();f.b.backup_before_close();f.b.close_own_clients();f.b.backup_after_close()
        f.b.apply_names();f.b.start_own_clients()
        with serverlog.open('ab') as stream:
            stream.write(b"NCBAD] Client 'Fixture', Sequence 22 Tick 5.0 - bad 1\n")
        with self.assertRaisesRegex(ValueError,'new server.*sync'):
            f.b.verify_applied()

    def test_server_prefix_rewrite_is_rejected_even_with_same_inode_and_size(self):
        f=self.f;f.prepare_applied();f.b.start_own_clients()
        serverlog=Path(f.m.fleet[0]['server']['root'])/'Dedicated_BotTest.log'
        original=serverlog.read_bytes()
        serverlog.write_bytes(b'X'+original[1:])
        with self.assertRaisesRegex(ValueError,'server log prefix'):
            f.b.verify_applied()

    def test_server_prefix_truncation_or_rotation_is_rejected(self):
        f=self.f;f.prepare_applied();f.b.start_own_clients()
        serverlog=Path(f.m.fleet[0]['server']['root'])/'Dedicated_BotTest.log'
        original=serverlog.read_bytes()
        serverlog.write_bytes(b'short')
        with self.assertRaisesRegex(ValueError,'server log prefix'):
            f.b.verify_applied()
        serverlog.rename(serverlog.with_suffix('.previous'));serverlog.write_bytes(original)
        with self.assertRaisesRegex(ValueError,'server log identity'):
            f.b.verify_applied()

    def policy_command(self, program, argv, ignore='no'):
        return '{ path='+program+' ; argv[]='+argv+' ; ignore_errors='+ignore+' ; start_time=[n/a] ; stop_time=[n/a] ; pid=0 ; code=(null) ; status=0/0 }'

    def setup_wait_helper(self):
        f=self.f
        inst=f.m.fleet[4];client=inst['clients'][1]
        helper=Path(f.roots['hole'])/'wait-server.py'
        helper.write_bytes(b'import socket, time, sys\n# reviewed offline fixture\n')
        pins={str(helper):hashlib.sha256(helper.read_bytes()).hexdigest()}
        f.b=T.Backend(f.m,f.out,f.stage,roots=f.roots,stage_dir=f.stage_dir,launch_helper_pins=pins)
        wait=self.policy_command('/usr/bin/python3','/usr/bin/python3 '+str(helper))
        sleep=self.policy_command('/bin/sleep','/bin/sleep 20')
        f.m.raw_policy_rows[client['unit']]='ExecStartPre='+wait+'\nExecStartPre='+sleep
        return inst,client,helper,wait,sleep

    def test_first_unreviewed_pre_command_cannot_hide_behind_sleep(self):
        f=self.f;client=f.m.fleet[4]['clients'][1]
        bad=self.policy_command('/usr/bin/python3','/usr/bin/python3 /unreviewed.py')
        sleep=self.policy_command('/bin/sleep','/bin/sleep 20')
        f.m.raw_policy_rows[client['unit']]='ExecStartPre='+bad+'\nExecStartPre='+sleep
        with self.assertRaisesRegex(ValueError,'pre-start|helper'):
            f.b.stop_policy(client['unit'])
        self.assertFalse(f.m.stop_history)

    def test_exact_pinned_wait_then_sleep_preserves_both_commands(self):
        inst,client,helper,wait,sleep=self.setup_wait_helper()
        original=helper.read_bytes()
        policy=self.f.b.stop_policy(client['unit'])
        self.assertEqual(policy['ExecStartPre'],[
            {'path':'/usr/bin/python3','argv':'/usr/bin/python3 '+str(helper),'ignore_errors':'no'},
            {'path':'/bin/sleep','argv':'/bin/sleep 20','ignore_errors':'no'}])
        self.assertEqual(helper.read_bytes(),original)

    def test_wait_helper_drift_blocks_before_any_close(self):
        inst,client,helper,wait,sleep=self.setup_wait_helper()
        self.f.b.preflight();self.f.b.backup_before_close()
        helper.write_bytes(helper.read_bytes()+b'# changed\n')
        with self.assertRaisesRegex(ValueError,'helper.*drift'):
            self.f.b.close_own_clients()
        self.assertFalse(self.f.m.stop_history)

    def test_wait_command_substitution_and_arguments_are_rejected(self):
        inst,client,helper,wait,sleep=self.setup_wait_helper()
        for program,argv,ignore in [('/bin/python3','/bin/python3 '+str(helper),'no'),
              ('/usr/bin/python3','/usr/bin/python3 '+str(helper)+' --extra','no'),
              ('/usr/bin/python3','/usr/bin/python3 '+str(helper),'yes'),
              ('/usr/bin/python3','/usr/bin/python3 '+str(helper.parent.parent/'trouble/wait-server.py'),'no')]:
            with self.subTest(program=program,argv=argv,ignore=ignore):
                raw=self.policy_command(program,argv,ignore)
                self.f.m.raw_policy_rows[client['unit']]='ExecStartPre='+raw+'\nExecStartPre='+sleep
                with self.assertRaisesRegex(ValueError,'pre-start|helper'):
                    self.f.b.stop_policy(client['unit'])
        self.assertFalse(self.f.m.start_history)

    def test_pre_command_order_drift_blocks_before_restart(self):
        inst,client,helper,wait,sleep=self.setup_wait_helper()
        self.f.prepare_applied()
        self.f.m.raw_policy_rows[client['unit']]='ExecStartPre='+sleep+'\nExecStartPre='+wait
        with self.assertRaisesRegex(ValueError,'policy'):
            self.f.b.start_one(inst,'botB',client)
        self.assertFalse(self.f.m.start_history)

    def test_backend_rejects_binary_write_outside_51_paths(self):
        f=self.f;f.b.preflight()
        path=Path(f.m.fleet[0]['clients'][0]['root'])/'Bin/GameMP.dll'
        before=path.read_bytes()
        with self.assertRaisesRegex(ValueError,'write scope'):
            f.b.replace(path,b'not a name')
        self.assertEqual(path.read_bytes(),before)

    def test_stale_log_not_owned_by_current_generation_rejects_preflight(self):
        f=self.f
        client=f.m.fleet[0]['clients'][0]
        fd=f.m.proc/str(f.m.running[client['unit']]['pid'])/'fd/5'
        fd.unlink()
        with self.assertRaisesRegex(ValueError,'writable log'):
            f.b.preflight()
        self.assertFalse(f.m.stop_history)

    def test_archive_retry_after_journal_failure_uses_fresh_destination(self):
        f=self.f;f.b.preflight();f.b.backup_before_close()
        inst,role,client=next(f.b.clients())
        original=f.b.event
        failed=[False]
        def event(state,**kw):
            if state=='closed_log_archived' and not failed[0]:
                failed[0]=True
                raise OSError('failed after durable archive')
            return original(state,**kw)
        with patch.object(f.b,'event',side_effect=event):
            with self.assertRaises(OSError):f.b.close_one(inst,role,client,'apply')
        f.b.close_one(inst,role,client,'rollback')
        archives=list((f.out/inst['id']).glob('*closed.log'))
        self.assertEqual(len(archives),2)
        self.assertEqual(archives[0].read_bytes(),archives[1].read_bytes())

    def test_stage_tampering_cannot_smuggle_non_name_bytes(self):
        f = self.f
        row = next(r for r in f.stage["files"] if r["changed"] and r["path"].endswith(".plr"))
        payload = f.stage_dir/row["after_blob"]
        bad = payload.read_bytes()[:-1]+b"x"
        payload.write_bytes(bad)
        row["after_sha256"] = T.sha(bad)
        with self.assertRaisesRegex(ValueError, "payload|name-only"):
            T.Backend(f.m, f.out, f.stage, roots=f.roots, stage_dir=f.stage_dir)
        self.assertFalse(f.m.stop_history)


if __name__ == "__main__":
    unittest.main()
