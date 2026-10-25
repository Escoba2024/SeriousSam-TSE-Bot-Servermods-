#!/usr/bin/env python3
"""Fail-closed file-scope checker for isolated TSE agent branches.

No network, no file modification, no runtime/game access. Reports ALL paths
introduced since a specified base plus any staged, unstaged or untracked paths.
"""
from __future__ import annotations

import argparse
import os
import pathlib
import subprocess
import sys


class ScopeError(Exception):
    pass


def git(repo: pathlib.Path, *args: str) -> bytes:
    try:
        proc = subprocess.run(
            ["git", "-C", str(repo), *args],
            capture_output=True, check=False, timeout=20,
        )
    except (OSError, subprocess.TimeoutExpired) as exc:
        raise ScopeError("git unavailable or timed out") from exc
    if proc.returncode:
        raise ScopeError(
            "git command failed: " + " ".join(args) + "; " +
            proc.stderr.decode("utf-8", "replace")[-300:]
        )
    return proc.stdout


def decode_path(value: bytes) -> str:
    return os.fsdecode(value)


def changed_paths(repo: pathlib.Path, base: str) -> set[str]:
    # A verified merge-base accounts for branches rebased from the base.
    merge_base = decode_path(git(repo, "merge-base", base, "HEAD")).strip()
    if not merge_base:
        raise ScopeError("unable to establish merge-base")
    committed = git(
        repo, "diff", "--no-ext-diff", "--no-renames",
        "--name-only", "-z", merge_base, "HEAD", "--"
    )
    paths = {decode_path(p) for p in committed.split(b"\0") if p}
    # The -z porcelain format is unquoted and explicitly includes old paths
    # for renames/copies. Scope validation must inspect BOTH paths.
    porcelain = git(repo, "status", "--porcelain=v1", "-z", "--untracked-files=all")
    entries = porcelain.split(b"\0")
    i = 0
    while i < len(entries):
        entry = entries[i]
        i += 1
        if not entry:
            continue
        if len(entry) < 4 or entry[2:3] != b" ":
            raise ScopeError("unrecognized Git porcelain record")
        flag = entry[:2]
        paths.add(decode_path(entry[3:]))
        if b"R" in flag or b"C" in flag:
            if i >= len(entries) or not entries[i]:
                raise ScopeError("rename/copy missing original path")
            paths.add(decode_path(entries[i]))
            i += 1
    return paths


def valid_path(p: str, prefixes: tuple[str, ...]) -> bool:
    if not p or "\\" in p or ":" in p or p.startswith("/"):
        return False
    parts = pathlib.PurePosixPath(p).parts
    if not parts or "." in parts or ".." in parts:
        return False
    return any(p.startswith(prefix) for prefix in prefixes)


def inspect(repo: pathlib.Path, base: str, prefixes: tuple[str, ...]) -> tuple[list[str], list[str]]:
    if not prefixes or any(
        not p.endswith("/") or p.startswith("/") or
        ".." in pathlib.PurePosixPath(p).parts or "\\" in p or ":" in p
        for p in prefixes
    ):
        raise ScopeError("allowed prefixes must be exact repository subdirectories ending in /")
    # Require repository root (not a path within a different worktree).
    toplevel = pathlib.Path(decode_path(git(repo, "rev-parse", "--show-toplevel")).strip())
    if toplevel.resolve() != repo.resolve():
        raise ScopeError("repository path is not its own worktree root")
    paths = changed_paths(repo, base)
    allowed = sorted(p for p in paths if valid_path(p, prefixes))
    denied = sorted(paths - set(allowed))
    return allowed, denied


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo", required=True, type=pathlib.Path)
    parser.add_argument("--base", required=True)
    parser.add_argument("--allow", action="append", default=[], required=True)
    args = parser.parse_args()
    try:
        allowed, denied = inspect(args.repo, args.base, tuple(args.allow))
    except ScopeError as exc:
        print("SCOPE_ERROR:", exc, file=sys.stderr)
        return 3
    for p in allowed:
        print("ALLOW", p)
    for p in denied:
        print("DENY", p)
    print("SCOPE_PASS" if not denied else "SCOPE_FAIL", "total=" + str(len(allowed) + len(denied)))
    return 0 if not denied else 2


if __name__ == "__main__":
    sys.exit(main())
