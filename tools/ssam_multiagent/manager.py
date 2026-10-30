#!/usr/bin/env python3
"""Standalone, fail-closed OpenCode M1/M2/M3 controller.

STAGING ONLY: not wired into the deployed ssam.ai System Control MCP service.
Run as opencode-tse; never use root or launch inside the existing shared worktree.
"""
from __future__ import annotations

import argparse
import fcntl
import json
import os
from pathlib import Path
import subprocess
import sys
import time
import uuid

WORKSPACE = Path("/home/opencode-tse/workspaces")
REPO = WORKSPACE / "tse-base"
STATE = WORKSPACE / ".ssam-multiagent"
OPENCODE = Path("/home/opencode-tse/.opencode/bin/opencode")
MODEL = "opencode-go/kimi-k2.7-code"
GIT_LOCK = WORKSPACE / ".ssam-worktree-setup.lock"
NATIVE_LOCK = WORKSPACE / ".ssam-native-test.lock"
MIN_DISK_BYTES = 8 * 1024 ** 3
MIN_RAM_KIB = 1024 * 1024

# Immutable source pins: do not silently follow moving branch heads.
SLOTS = {
    "M1": {
        "ref": "agent/lead/20261028-m1-completion",
        "sha": "619a807b42c8877c495fc586a4b0da98567a01a4",
        "worktree": "ssam-m1-agent-20261030",
        "branch": "agent/opencode/20261030-m1",
    },
    "M2": {
        "ref": "agent/lead/20261030-m2-final",
        "sha": "586a2fb5f0a4775638abd02b6a0571ee00f15f0f",
        "worktree": "ssam-m2-agent-20261030",
        "branch": "agent/opencode/20261030-m2",
    },
    "M3": {
        "ref": "main",
        "sha": "ab0c7400353a108f8461bb82280c539fdfe81499",
        "worktree": "ssam-m3-agent-20261030",
        "branch": "agent/opencode/20261030-m3",
    },
}


def require(condition: bool, message: str) -> None:
    if not condition:
        raise RuntimeError(message)


def atomic_json(path: Path, data: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True, mode=0o700)
    temp = path.with_name(path.name + "." + str(os.getpid()) + ".tmp")
    try:
        with temp.open("x", encoding="utf-8") as fp:
            os.chmod(temp, 0o600)
            json.dump(data, fp, sort_keys=True, indent=2)
            fp.flush()
            os.fsync(fp.fileno())
        os.replace(temp, path)
    finally:
        temp.unlink(missing_ok=True)


def read_json(path: Path) -> dict:
    with path.open(encoding="utf-8") as fp:
        return json.load(fp)


def pid_ticks(pid: int) -> int | None:
    if not isinstance(pid, int) or pid <= 0:
        return None
    try:
        stat = Path("/proc") / str(pid) / "stat"
        raw = stat.read_text(encoding="utf-8")
        return int(raw[raw.rfind(")") + 2:].split()[19])
    except (ValueError, OSError, IndexError):
        return None


def identity_alive(pid: int | None, ticks: int | None) -> bool:
    return pid is not None and ticks is not None and pid_ticks(pid) == ticks


def disk_and_ram_ok(workspace: Path) -> dict:
    fs = os.statvfs(workspace)
    disk = fs.f_bavail * fs.f_frsize
    available = None
    with open("/proc/meminfo", encoding="utf-8") as fp:
        for line in fp:
            if line.startswith("MemAvailable:"):
                available = int(line.split()[1])
                break
    require(disk >= MIN_DISK_BYTES, "DISK_RESERVE_BELOW_8_GIB")
    require(available is not None and available >= MIN_RAM_KIB, "RAM_RESERVE_BELOW_1_GIB")
    return {"disk_free_bytes": disk, "mem_available_kib": available}


class FileLock:
    def __init__(self, path: Path):
        self.path = path
        self.fd: int | None = None

    def __enter__(self):
        self.path.parent.mkdir(mode=0o700, parents=True, exist_ok=True)
        self.fd = os.open(self.path, os.O_CREAT | os.O_RDWR | os.O_NOFOLLOW, 0o600)
        fcntl.flock(self.fd, fcntl.LOCK_EX)
        return self

    def __exit__(self, *_):
        assert self.fd is not None
        fcntl.flock(self.fd, fcntl.LOCK_UN)
        os.close(self.fd)
        self.fd = None


def git(*args: str, cwd: Path = REPO) -> str:
    result = subprocess.run(["git", "-C", str(cwd), *args], text=True,
                            stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                            timeout=120, check=False)
    require(result.returncode == 0, "GIT_FAILED: " + result.stderr[-500:])
    return result.stdout.strip()


def setup(slot: str, workspace: Path) -> Path:
    spec = SLOTS[slot]
    target = workspace / spec["worktree"]
    require(workspace.is_dir() and not workspace.is_symlink(), "WORKSPACE_INVALID")
    require(not target.exists() and not target.is_symlink(), "WORKTREE_EXISTS_REFUSE_TO_TOUCH")
    with FileLock(workspace / GIT_LOCK.name):
        require(not target.exists() and not target.is_symlink(), "WORKTREE_EXISTS_REFUSE_TO_TOUCH")
        # Read-only source worktree and pinned remote branch fetched separately.
        require((workspace / REPO.name / ".git").exists(), "BASE_REPOSITORY_MISSING")
        git("fetch", "--no-tags", "origin", "refs/heads/" + spec["ref"],
            cwd=workspace / REPO.name)
        fetched = git("rev-parse", "FETCH_HEAD", cwd=workspace / REPO.name)
        require(fetched == spec["sha"], "REMOTE_SOURCE_SHA_CHANGED_REQUIRE_REVIEW")
        git("worktree", "add", "-b", spec["branch"], str(target), fetched,
            cwd=workspace / REPO.name)
        require(git("rev-parse", "HEAD", cwd=target) == fetched, "WORKTREE_HEAD_MISMATCH")
    return target


def state_status(record: dict) -> str:
    if record.get("state") == "FINISHED":
        return "FINISHED"
    if record.get("state") == "STARTING" or record.get("state") == "RUNNING":
        if identity_alive(record.get("worker_pid"), record.get("worker_ticks")):
            return record["state"]
        return "UNKNOWN_NEEDS_MANUAL_RECONCILIATION"
    return "UNKNOWN_NEEDS_MANUAL_RECONCILIATION"


def all_records(state: Path) -> list[dict]:
    tasks = state / "tasks"
    if not tasks.is_dir():
        return []
    records = []
    for path in sorted(tasks.glob("*.json")):
        if path.is_symlink():
            continue
        try:
            r = read_json(path)
            r["observed_state"] = state_status(r)
            records.append(r)
        except (OSError, ValueError, KeyError):
            records.append({"id": path.stem, "observed_state": "INVALID_STATE"})
    return records


def start(slot: str, prompt_file: Path, workspace: Path, state: Path, opencode: Path):
    require(os.geteuid() != 0, "NEVER_RUN_AS_ROOT")
    require(slot in SLOTS, "UNKNOWN_SLOT")
    require(prompt_file.is_file() and not prompt_file.is_symlink(), "PROMPT_FILE_INVALID")
    prompt = prompt_file.read_text(encoding="utf-8")
    require(40 <= len(prompt) <= 20000, "PROMPT_SIZE_INVALID")
    require(opencode.is_file() and os.access(opencode, os.X_OK), "OPENCODE_UNAVAILABLE")
    require(workspace.is_dir(), "WORKSPACE_MISSING")
    require(not state.is_symlink(), "STATE_SYMLINK_BLOCKED")
    state.mkdir(parents=True, exist_ok=True, mode=0o700)
    os.chmod(state, 0o700)
    with FileLock(state / "registry.lock"):
        previous = all_records(state)
        active = [r for r in previous if r.get("observed_state") != "FINISHED"]
        require(len(active) < 3, "THREE_AGENT_CAP_REACHED_OR_UNKNOWN_TASK")
        require(all(r.get("slot") != slot for r in active), "SLOT_ALREADY_OWNED")
        disk_and_ram_ok(workspace)
        # No setup if existing slot's worktree is present: keep existing M1 safe.
        target = setup(slot, workspace)
        task_id = uuid.uuid4().hex[:24]
        record = {
            "id": task_id, "slot": slot, "model": MODEL, "state": "STARTING",
            "started_unix": time.time(), "worktree": str(target),
            "branch": SLOTS[slot]["branch"], "source_sha": SLOTS[slot]["sha"],
            "worker_pid": None, "worker_ticks": None, "exit_code": None,
        }
        (state / "tasks").mkdir(mode=0o700, parents=True, exist_ok=True)
        task_dir = state / "private" / task_id
        task_dir.mkdir(mode=0o700, parents=True, exist_ok=False)
        private_prompt = task_dir / "prompt.txt"
        with private_prompt.open("x", encoding="utf-8") as fp:
            os.chmod(private_prompt, 0o600)
            fp.write(prompt)
        dest = state / "tasks" / (task_id + ".json")
        atomic_json(dest, record)
        child = subprocess.Popen(
            [sys.executable, str(Path(__file__).resolve()),
             "--state-dir", str(state), "--opencode-bin", str(opencode),
             "worker", task_id],
            cwd=target, stdin=subprocess.DEVNULL, stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL, start_new_session=True, close_fds=True,
        )
        record["worker_pid"] = child.pid
        for _ in range(20):
            record["worker_ticks"] = pid_ticks(child.pid)
            if record["worker_ticks"] is not None:
                break
            time.sleep(0.05)
        require(record["worker_ticks"] is not None, "WORKER_PID_IDENTITY_UNAVAILABLE")
        atomic_json(dest, record)
    print(json.dumps({"task_id": task_id, "pid": child.pid, "slot": slot,
                      "model": MODEL, "worktree": str(target)}, sort_keys=True))


def worker(task_id: str, state: Path, opencode: Path) -> None:
    require(len(task_id) == 24 and all(c in "0123456789abcdef" for c in task_id),
            "INVALID_TASK_ID")
    path = state / "tasks" / (task_id + ".json")
    record = read_json(path)
    for _ in range(40):
        if record.get("worker_pid") == os.getpid() and record.get("worker_ticks") is not None:
            break
        time.sleep(0.05)
        record = read_json(path)
    require(record["worker_pid"] == os.getpid(), "WORKER_IDENTITY_MISMATCH")
    require(record["worker_ticks"] == pid_ticks(os.getpid()), "WORKER_TICKS_MISMATCH")
    private = state / "private" / task_id
    prompt = (private / "prompt.txt").read_text(encoding="utf-8")
    record["state"] = "RUNNING"
    atomic_json(path, record)
    code = 255
    try:
        with (private / "opencode.log").open("a", encoding="utf-8") as log:
            os.chmod(private / "opencode.log", 0o600)
            command = [str(opencode), "run", "--auto", "--model", MODEL,
                       "--title", "ssam-" + record["slot"] + "-" + task_id, prompt]
            child = subprocess.Popen(command, cwd=record["worktree"],
                                     stdin=subprocess.DEVNULL, stdout=log,
                                     stderr=subprocess.STDOUT, close_fds=True)
            record["opencode_pid"] = child.pid
            record["opencode_ticks"] = pid_ticks(child.pid)
            atomic_json(path, record)
            code = child.wait()
    finally:
        record["state"] = "FINISHED"
        record["exit_code"] = code
        record["finished_unix"] = time.time()
        atomic_json(path, record)


def main():
    os.umask(0o077)
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--workspace", type=Path, default=WORKSPACE)
    parser.add_argument("--state-dir", type=Path, default=STATE)
    parser.add_argument("--opencode-bin", type=Path, default=OPENCODE)
    subs = parser.add_subparsers(dest="command", required=True)
    p = subs.add_parser("start")
    p.add_argument("slot", choices=tuple(SLOTS))
    p.add_argument("--prompt-file", type=Path, required=True)
    subs.add_parser("status")
    l = subs.add_parser("logs")
    l.add_argument("task_id")
    l.add_argument("--lines", type=int, default=35)
    w = subs.add_parser("worker", help=argparse.SUPPRESS)
    w.add_argument("task_id")
    args = parser.parse_args()
    if args.command == "start":
        start(args.slot, args.prompt_file, args.workspace, args.state_dir,
              args.opencode_bin)
    elif args.command == "status":
        print(json.dumps(all_records(args.state_dir), sort_keys=True, indent=2))
    elif args.command == "logs":
        require(0 < args.lines <= 150, "LINE_LIMIT_INVALID")
        require(len(args.task_id) == 24 and all(c in "0123456789abcdef" for c in args.task_id),
                "INVALID_TASK_ID")
        require((args.state_dir / "tasks" / (args.task_id + ".json")).is_file(),
                "UNKNOWN_TASK")
        path = args.state_dir / "private" / args.task_id / "opencode.log"
        if path.is_file() and not path.is_symlink():
            print("\n".join(path.read_text(encoding="utf-8", errors="replace").splitlines()[-args.lines:]))
    elif args.command == "worker":
        worker(args.task_id, args.state_dir, args.opencode_bin)


if __name__ == "__main__":
    try:
        main()
    except (RuntimeError, OSError, ValueError, subprocess.TimeoutExpired) as exc:
        print("BLOCKED: " + str(exc), file=sys.stderr)
        sys.exit(2)
