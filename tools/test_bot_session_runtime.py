"""Portable-only checks; do not touch Retail, network, Wine or public services."""
from pathlib import Path
import os
import sqlite3
import struct
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch
import uuid

import bot_session_runtime as r
import bot_sessions as planner_module
import qualify_integrated_wine as wine_harness


def identity():
    return dict(id="mika", nickname="Mika", profile=3, color="80D8FF",
                gameplay_seed=41217, guid=uuid.uuid5(uuid.NAMESPACE_URL, "pool/seed/mika").hex)


def fixture():
    old = bytes(range(16))
    return b"PLC4" + struct.pack("<I", 3) + b"Old" + b"TEAM" + old + b"APPEARANCE-PRESERVED!", old


class ProfileAdapter(unittest.TestCase):
    def test_plain_native_identity_has_22_visible_character_limit(self):
        base,_=fixture();who=dict(identity(),nickname='A'*22)
        result=r.profile_bytes(base,who)
        self.assertEqual(struct.unpack_from('<I',result,4)[0],22)
        self.assertEqual(result[8:30],b'A'*22)
        self.assertIn('bot_iProfile0=3;',r.startup_script(who))
        for length in (23,24,25,300):
            too_long=dict(who,nickname='A'*length)
            with self.subTest(length=length),self.assertRaises(ValueError):
                r.profile_bytes(base,too_long)
            with self.subTest(length=length),self.assertRaises(ValueError):
                r.startup_script(too_long)
    def test_22_character_identity_with_native_color_fits_32_bytes(self):
        base,_=fixture();who=dict(identity(),nickname='A'*22)
        result=r.profile_bytes(base,who,colors_enabled=True)
        self.assertEqual(struct.unpack_from('<I',result,4)[0],32)
        self.assertEqual(result[8:40],b'^c80D8FF'+b'A'*22+b'^r')
    def test_weighted_native_style_reaches_profile_only_when_explicitly_enabled(self):
        base,_=fixture();who=dict(identity(),native_name='^b^i^c80D8FFMika^I^B^r')
        plain=r.profile_bytes(base,who)
        self.assertEqual(plain[8:12], b'Mika')
        styled=r.profile_bytes(base,who,colors_enabled=True)
        count=struct.unpack_from('<I',styled,4)[0]
        self.assertEqual(styled[8:8+count], b'^b^i^c80D8FFMika^I^B^r')
        self.assertEqual(styled[12+count:28+count],r.guid_bytes(who))
        with self.assertRaises(ValueError):
            r.profile_bytes(base,dict(who,native_name='^bSomeoneElse^B^r'),colors_enabled=True)
    def test_qualified_color_configuration_encodes_native_profile(self):
        base,_=fixture();who=identity()
        value=r.profile_bytes(base,who,colors_enabled=True)
        count=struct.unpack_from('<I',value,4)[0]
        self.assertEqual(value[8:8+count],b'^c80D8FFMika^r')
        self.assertEqual(value[12+count:28+count],r.guid_bytes(who))
        self.assertEqual(r.profile_bytes(base,who,colors_enabled=False),r.profile_bytes(base,who))
    def test_name_guid_changed_appearance_byte_identical(self):
        source, old_guid = fixture()
        who = identity()
        new = r.profile_bytes(source, who)
        n = struct.unpack_from("<I", new, 4)[0]
        self.assertEqual(new[:4], b"PLC4")
        self.assertEqual(n, len(who["nickname"]))
        self.assertEqual(new[8:8 + n], b"Mika")
        self.assertEqual(new[8 + n:12 + n], b"TEAM")
        self.assertEqual(new[12 + n:28 + n], r.guid_bytes(who))
        self.assertNotEqual(r.guid_bytes(who), old_guid)
        self.assertEqual(new[28 + n:], source[12 + 3 + len(old_guid):])
        self.assertEqual(r.profile_bytes(source, who), new)
    def test_real_template_readonly_layout(self):
        # Intentional offline contract: no live Retail files are read/rewritten.
        p = Path("/srv/tse-wine-runtime-20261020/install/vanilla/Players/Player0.plr")
        side = p.with_suffix(".plr.guid")
        if not p.exists() or not side.exists():
            self.skipTest("native read-only fixture missing")
        orig, guid = p.read_bytes(), side.read_bytes()
        self.assertEqual(orig[12 + struct.unpack_from("<I", orig, 4)[0]:][:16], guid)
        result = r.profile_bytes(orig, identity())
        self.assertEqual(len(result), len(orig) + len(b"Mika") - struct.unpack_from("<I", orig, 4)[0])
        self.assertEqual(p.read_bytes(), orig)
        self.assertEqual(side.read_bytes(), guid)
    def test_invalid_plc4_or_ambiguous_guid_refused(self):
        base, old_guid = fixture()
        for bad in [b"WRONG" + base[5:], b"PLC4\xff\xff\xff\xff" + base[8:],
                    base[:12], base + old_guid]:
            with self.subTest(bad=bad[:9]), self.assertRaises(ValueError):
                r.profile_bytes(bad, identity())
    def test_unsafe_nickname_seed_guid_and_roster_failclosed(self):
        base, _ = fixture()
        for key, value in [("nickname", "^cFF0000Mika"), ("nickname", "Mika;quit"),
                           ("nickname", "Änn"), ("nickname", "A" * 25),
                           ("profile", 8), ("profile", True), ("gameplay_seed", 0),
                           ("gameplay_seed", "1"), ("guid", "00"*16)]:
            with self.subTest(key=key, value=value), self.assertRaises(ValueError):
                r.profile_bytes(base, dict(identity(), **{key: value}))
    def test_seed_and_roster_reach_actual_botdriver_symbol_names(self):
        script = r.startup_script(identity())
        driver = (Path(__file__).parents[1] / "poc/candidates/integrated-human-cpu-20261021/BotDriver.cpp").read_text()
        for key in ["bot_bHumanAI", "bot_iProfile0", "bot_iProfileSeed", "bot_iRosterOffset"]:
            self.assertIn(key + "=", script)
            self.assertIn(f'"user INDEX {key};"', driver) if key != "bot_bHumanAI" else self.assertIn(key, driver)
        self.assertIn("bot_iProfile0=3;", script)
        self.assertIn("bot_iProfileSeed=41217;", script)
        self.assertNotIn("80D8FF", script)  # color gate off
        self.assertNotIn("^c", script)
        self.assertNotIn("Mika", script)  # nickname set in PLC4, never via unsafe shell
    def test_native_rejoin_probe_rejects_unsafe_flag_combination_without_io(self):
        with tempfile.TemporaryDirectory() as temp:
            root=Path(temp)/"must-not-exist"
            args=[sys.executable,str(wine_harness.__file__),
                  "--runtime",str(root),"--template","/nonexistent/template",
                  "--vanilla","/nonexistent/vanilla",
                  "--build-manifest","/nonexistent/build.json",
                  "--stage","one","--duration","1","--identity-rejoin-smoke"]
            bad=subprocess.run(args,capture_output=True,text=True,timeout=5)
            self.assertNotEqual(bad.returncode,0)
            self.assertIn("private one-bot plain-name isolation",bad.stderr)
            self.assertFalse(root.exists())
    def test_private_overlay_profile_pair_patch_and_mount_gate(self):
        who=identity()
        with tempfile.TemporaryDirectory() as temp:
            game=Path(temp)
            players=game/"Players"
            players.mkdir()
            p=players/"Player0.plr"
            side=p.with_suffix(".plr.guid")
            original,old_guid=fixture()
            p.write_bytes(original)
            side.write_bytes(old_guid)
            # The helper MUST reject non-overlay paths before writing.
            with self.assertRaises(AssertionError):
                wine_harness.change_profile_identity(game,who)
            self.assertEqual(p.read_bytes(),original)
            self.assertEqual(side.read_bytes(),old_guid)
            # Simulate only mountpoint predicate; never mount a real FS or start Wine.
            with patch.object(Path,"is_mount",return_value=True):
                digest=wine_harness.change_profile_identity(game,who)
            self.assertEqual(digest,__import__("hashlib").sha256(p.read_bytes()).hexdigest())
            self.assertEqual(side.read_bytes(),r.guid_bytes(who))
            self.assertEqual(p.read_bytes(),r.profile_bytes(original,who))
    def test_explicit_private_color_probe_only(self):
        base,_=fixture()
        who=identity()
        ordinary=r.profile_bytes(base,who)
        probe=r.profile_bytes(base,who,color_probe=True)
        self.assertNotEqual(ordinary,probe)
        length=struct.unpack_from("<I",probe,4)[0]
        self.assertEqual(probe[8:8+length],b"^c80D8FFMika^r")
        self.assertEqual(probe[12+length:28+length],r.guid_bytes(who))
        self.assertEqual(probe[28+length:],base[28+3:])
        for bad in [dict(who,color="00GGFF"),dict(who,color=None),
                    dict(who,nickname="Mika"*6)]:
            with self.assertRaises(ValueError):
                r.profile_bytes(base,bad,color_probe=True)
        self.assertEqual(r.profile_bytes(base,who),ordinary)
    def test_sidecar_equal_exact_new_guid(self):
        self.assertEqual(len(r.guid_bytes(identity())), 16)
        self.assertEqual(r.guid_bytes(identity()), uuid.UUID(hex=identity()["guid"]).bytes)


class ControllerOwnership(unittest.TestCase):
    def test_symlink_database_alias_and_release(self):
        with tempfile.TemporaryDirectory() as temp:
            db = Path(temp) / "sessions.db"
            db.touch()
            alias = Path(temp) / "alias.db"
            alias.symlink_to(db)
            with r.ControllerLock(db):
                with self.assertRaises(RuntimeError):
                    with r.ControllerLock(alias):
                        pass
            with r.ControllerLock(alias):
                pass
    def test_durable_claim_blocks_same_epoch_after_restart(self):
        with tempfile.TemporaryDirectory() as temp:
            db = Path(temp) / "sessions.db"
            with sqlite3.connect(db) as conn:
                conn.execute("CREATE TABLE session (id TEXT PRIMARY KEY, epoch INTEGER, status TEXT)")
                conn.execute("INSERT INTO session VALUES ('mika',1,'JOINING')")
            with r.ControllerLock(db) as ctl:
                self.assertFalse(ctl.claim_launch("mika", 2))
                self.assertTrue(ctl.claim_launch("mika", 1))
                self.assertFalse(ctl.claim_launch("mika", 1))
                with self.assertRaises(ValueError):
                    ctl.claim_launch("mika", True)
            with r.ControllerLock(db) as ctl:
                self.assertFalse(ctl.claim_launch("mika", 1))
            with sqlite3.connect(db) as conn:
                self.assertEqual(conn.execute("SELECT COUNT(*) FROM runtime_launch_claim").fetchone()[0], 1)
    def test_hardlink_db_alias_refused(self):
        with tempfile.TemporaryDirectory() as temp:
            db = Path(temp) / "sessions.db"
            db.touch()
            os.link(db, Path(temp) / "alias.db")
            with self.assertRaises(RuntimeError):
                with r.ControllerLock(db):
                    pass
    def test_second_real_process_is_excluded_while_owner_alive(self):
        with tempfile.TemporaryDirectory() as temp:
            db = Path(temp) / "sessions.db"
            db.touch()
            program = (
                "from bot_session_runtime import ControllerLock\n"
                f"with ControllerLock({str(db)!r}):\n"
                " print('locked',flush=True)\n"
                " input()\n"
            )
            p = subprocess.Popen([sys.executable, "-c", program], cwd=Path(__file__).parent,
                                 stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                                 stderr=subprocess.PIPE, text=True)
            try:
                self.assertEqual(p.stdout.readline().strip(), "locked")
                with self.assertRaises(RuntimeError):
                    with r.ControllerLock(db):
                        pass
                p.stdin.write("\n")
                p.stdin.flush()
                self.assertEqual(p.wait(timeout=5), 0)
                with r.ControllerLock(db):
                    pass
            finally:
                if p.poll() is None:
                    p.kill()
                    p.wait(timeout=5)
                p.stdin.close()
                p.stdout.close()
                p.stderr.close()
    def test_kernel_unlocks_on_child_exit(self):
        with tempfile.TemporaryDirectory() as temp:
            db = Path(temp) / "sessions.db"
            db.touch()
            script = ("from bot_session_runtime import ControllerLock\n"
                      f"with ControllerLock({str(db)!r}): print('owned', flush=True)\n")
            proc = subprocess.run([sys.executable, "-c", script], cwd=Path(__file__).parent,
                                  capture_output=True, text=True, timeout=5)
            self.assertEqual(proc.returncode, 0, proc.stderr)
            self.assertIn("owned", proc.stdout)
            with r.ControllerLock(db):
                pass
    def test_lock_fails_closed_with_symlink_lockfile(self):
        with tempfile.TemporaryDirectory() as temp:
            db = Path(temp) / "db"
            db.touch()
            lock = Path(temp) / "db.runtime.lock"
            target = Path(temp) / "wrong"
            target.touch()
            lock.symlink_to(target)
            with self.assertRaises(OSError):
                with r.ControllerLock(db):
                    pass


def observation(**kw):
    sample = dict(identity_id="mika", epoch=1, ownership_verified=True, fresh_query=True, process_alive=False,
                  connected=False, ghost=False, unknown_peers=False,
                  human_conflict=False)
    sample.update(kw)
    return sample


class PlannerAdapterEndToEndOffline(unittest.TestCase):
    def test_intent_journal_join_leave_cooldown_no_processes(self):
        with tempfile.TemporaryDirectory() as temp:
            db = Path(temp) / "sessions.db"
            cfg = dict(enabled=True, pool_id="runtime-test", seed=123,
                       accelerated=True, max_bots=1, reserved_human_slots=2,
                       join_interval_s=1, leave_interval_s=1,
                       startup_delay_s=[0, 0], pause_s=[40, 40],
                       session_bands=[[1, 20, 20]], servers=["one"],
                       identities=[{"id": "mika", "nickname": "Mika", "profile": 3}])
            p = planner_module.Planner(db, cfg)
            try:
                intents = p.plan("one", {"observed_at":100, "maxplayers":16,
                                        "human_names":[]}, 100)
                self.assertEqual(len(intents), 1)
                action = intents[0]
                self.assertEqual(action["action"], "join")
                state = p.states()["mika"]
                evidence = observation(epoch=action["epoch"], verified_absence=True)
                self.assertEqual(r.reconcile(state, evidence), "claim_launch")
                with r.ControllerLock(db) as ctl:
                    self.assertTrue(ctl.claim_launch("mika", action["epoch"]))
                with r.ControllerLock(db) as ctl:
                    self.assertFalse(ctl.claim_launch("mika", action["epoch"]))
                self.assertEqual(r.reconcile(state, observation(epoch=action["epoch"],
                    process_alive=True, connected=True)), "ack_join")
                self.assertTrue(p.record("mika", action["epoch"], "joined", 101))
                self.assertEqual(p.states()["mika"]["status"], "PLAYING")
                leaves = p.plan("one", {"observed_at":122, "maxplayers":16,
                                        "human_names":[]}, 122)
                self.assertEqual([(x["action"], x["reason"]) for x in leaves],
                                 [("leave", "planned")])
                state = p.states()["mika"]
                self.assertEqual(r.reconcile(state, observation(epoch=action["epoch"],
                    process_alive=True, connected=True)), "graceful_leave")
                self.assertEqual(r.reconcile(state, observation(epoch=action["epoch"],
                    query_absence_confirmed=True)), "ack_left")
                self.assertTrue(p.record("mika", action["epoch"], "left", 123))
                self.assertEqual(p.states()["mika"]["status"], "COOLDOWN")
                self.assertEqual(p.plan("one", {"observed_at":124,
                    "maxplayers":16, "human_names":[]}, 124), [])
            finally:
                p.close()


class Reconciliation(unittest.TestCase):
    def test_wrong_identity_or_epoch_fails_closed(self):
        state = {"status": "JOINING", "id": "mika", "epoch": 1}
        self.assertEqual(r.reconcile(state, observation(epoch=2, verified_absence=True)), "quarantine")
        self.assertEqual(r.reconcile(state, observation(identity_id="other", verified_absence=True)), "quarantine")
    def test_unknown_or_ghost_or_stale_never_launches(self):
        for changes in [dict(fresh_query=False), dict(ghost=True),
                        dict(unknown_peers=True), dict(human_conflict=True),
                        dict(ownership_verified=False)]:
            with self.subTest(changes=changes):
                sample = observation(verified_absence=True)
                sample.update(changes)
                self.assertEqual(r.reconcile({"status": "JOINING", "id": "mika", "epoch": 1}, sample), "quarantine")
        self.assertEqual(r.reconcile({"status": "JOINING", "id": "mika", "epoch": 1}, None), "quarantine")
        self.assertEqual(r.reconcile({"status": "JOINING", "id": "mika", "epoch": 1}, {}), "quarantine")
    def test_join_requires_both_process_and_connection(self):
        self.assertEqual(r.reconcile({"status": "JOINING", "id": "mika", "epoch": 1}, observation(
            process_alive=True, connected=True)), "ack_join")
        self.assertEqual(r.reconcile({"status": "JOINING", "id": "mika", "epoch": 1}, observation(
            process_alive=True)), "wait_join")
        self.assertEqual(r.reconcile({"status": "JOINING", "id": "mika", "epoch": 1}, observation()), "quarantine")
        self.assertEqual(r.reconcile({"status": "JOINING", "id": "mika", "epoch": 1}, observation(
            verified_absence=True)), "claim_launch")
    def test_leave_waits_for_complete_external_absence(self):
        self.assertEqual(r.reconcile({"status": "LEAVING", "id": "mika", "epoch": 1}, observation()), "quarantine")
        self.assertEqual(r.reconcile({"status": "LEAVING", "id": "mika", "epoch": 1}, observation(
            query_absence_confirmed=True)), "ack_left")
        self.assertEqual(r.reconcile({"status": "LEAVING", "id": "mika", "epoch": 1}, observation(
            process_alive=True, connected=True)), "graceful_leave")
    def test_crash_requires_confirmed_exit_and_ghost_absence(self):
        self.assertEqual(r.reconcile({"status": "PLAYING", "id": "mika", "epoch": 1}, observation()), "quarantine")
        self.assertEqual(r.reconcile({"status": "PLAYING", "id": "mika", "epoch": 1}, observation(
            exit_confirmed=True)), "record_crash")
        self.assertEqual(r.reconcile({"status": "PLAYING", "id": "mika", "epoch": 1}, observation(
            process_alive=True, connected=True)), "healthy")
    def test_cooldown_never_restores_missing_slot(self):
        for state in ("COOLDOWN", "WAITING", "OFFLINE"):
            self.assertEqual(r.reconcile({"status": state, "id": "mika", "epoch": 1}, observation()), "idle")
            self.assertEqual(r.reconcile({"status": state, "id": "mika", "epoch": 1}, observation(
                process_alive=True, connected=True)), "quarantine")


if __name__ == "__main__":
    unittest.main()
