"""Offline tests for the fail-closed three-slot controller (no production OpenCode)."""
import contextlib
import io
import json
import os
from pathlib import Path
import subprocess
import tempfile
import time
import unittest
from unittest import mock

import manager


def run(*args):
    return subprocess.check_output(args, text=True, stderr=subprocess.STDOUT).strip()


class MultiAgentTests(unittest.TestCase):
    def test_pid_identity_rejects_reused_or_missing_process(self):
        ticks = manager.pid_ticks(os.getpid())
        self.assertIsInstance(ticks, int)
        self.assertTrue(manager.identity_alive(os.getpid(), ticks))
        self.assertFalse(manager.identity_alive(os.getpid(), ticks + 1))
        self.assertFalse(manager.identity_alive(-1, ticks))

    def test_atomic_registry_is_owner_private(self):
        with tempfile.TemporaryDirectory() as root:
            target = Path(root) / "tasks" / "one.json"
            manager.atomic_json(target, {"state": "FINISHED"})
            self.assertEqual(manager.read_json(target)["state"], "FINISHED")
            self.assertEqual(target.stat().st_mode & 0o777, 0o600)

    def test_unknown_task_fails_closed(self):
        r = {"id": "a", "slot": "M2", "state": "RUNNING",
             "worker_pid": os.getpid(), "worker_ticks": 0}
        self.assertEqual(manager.state_status(r), "UNKNOWN_NEEDS_MANUAL_RECONCILIATION")
        self.assertEqual(manager.state_status({"state": "FINISHED"}), "FINISHED")

    def test_existing_worktree_is_never_modified(self):
        with tempfile.TemporaryDirectory() as tmp:
            w = Path(tmp)
            (w / "ssam-m1-agent-20261030").mkdir()
            marker = w / "ssam-m1-agent-20261030" / "DO_NOT_TOUCH"
            marker.write_text("safe")
            with self.assertRaisesRegex(RuntimeError, "WORKTREE_EXISTS_REFUSE_TO_TOUCH"):
                manager.setup("M1", w)
            self.assertEqual(marker.read_text(), "safe")

    def test_three_independent_workers_and_log_receipts(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            workspace = root / "workspaces"
            workspace.mkdir()
            remote = root / "remote.git"
            seed = root / "seed"
            run("git", "init", "--bare", str(remote))
            run("git", "init", "-b", "main", str(seed))
            run("git", "-C", str(seed), "config", "user.email", "test@example.invalid")
            run("git", "-C", str(seed), "config", "user.name", "Test")
            (seed / "README").write_text("test\n")
            run("git", "-C", str(seed), "add", "README")
            run("git", "-C", str(seed), "commit", "-m", "base")
            sha = run("git", "-C", str(seed), "rev-parse", "HEAD")
            run("git", "-C", str(seed), "remote", "add", "origin", str(remote))
            run("git", "-C", str(seed), "push", "-u", "origin", "main")
            run("git", "--git-dir", str(remote), "symbolic-ref", "HEAD", "refs/heads/main")
            run("git", "clone", str(remote), str(workspace / "tse-base"))

            slots = {k: {"ref": "main", "sha": sha, "worktree": k.lower() + "-worktree",
                         "branch": "agent/test/" + k.lower()} for k in ("M1", "M2", "M3")}
            fake = root / "fake-opencode"
            fake.write_text("#!/bin/sh\nsleep 2\nprintf 'FAKE_PASS from %s\\n' \"$PWD\"\n")
            fake.chmod(0o755)
            prompt = root / "prompt.txt"
            prompt.write_text("Test only: do not access any actual external project resource.")
            registry = workspace / ".ssam-multiagent"
            try:
                with mock.patch.object(manager, "SLOTS", slots), \
                     mock.patch.object(manager.os, "geteuid", return_value=1000), \
                     mock.patch.object(manager, "disk_and_ram_ok", return_value={}):
                    for slot in slots:
                        with contextlib.redirect_stdout(io.StringIO()):
                            manager.start(slot, prompt, workspace, registry, fake)
                    records = manager.all_records(registry)
                    self.assertEqual(len(records), 3)
                    self.assertEqual({x["slot"] for x in records}, set(slots))
                    self.assertEqual(len({x["worktree"] for x in records}), 3)
                    self.assertTrue(all(x["observed_state"] in ("STARTING", "RUNNING") for x in records))
                    with self.assertRaisesRegex(RuntimeError, "THREE_AGENT_CAP_REACHED_OR_UNKNOWN_TASK|SLOT_ALREADY_OWNED"):
                        manager.start("M1", prompt, workspace, registry, fake)
                    deadline = time.monotonic() + 12
                    while time.monotonic() < deadline:
                        records = manager.all_records(registry)
                        if all(x["state"] == "FINISHED" for x in records):
                            break
                        time.sleep(0.1)
                    self.assertTrue(all(x["state"] == "FINISHED" for x in records), records)
                    self.assertTrue(all(x["exit_code"] == 0 for x in records))
                    for record in records:
                        private = registry / "private" / record["id"]
                        log = (private / "opencode.log").read_text()
                        self.assertIn("FAKE_PASS", log)
                        self.assertIn(record["worktree"], log)
                        self.assertEqual((private / "prompt.txt").stat().st_mode & 0o777, 0o600)
            finally:
                # Detached workers finish in the test deadline; no production runtime touched.
                pass


if __name__ == "__main__":
    unittest.main()
