#!/usr/bin/env python3
"""Fail-closed file-scope checker for isolated TSE agent branches.

No network, no file modification, no runtime/game access. Reports ALL paths
introduced since a specified base plus any staged, unstaged or untracked paths.
"""
from __future__ import annotations

import argparse
import os
import pathlib
import stat
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


def object_entries(repo: pathlib.Path, *args: str, index: bool) -> list[tuple[str, str, str]]:
    """Read -z records without Git's quoted-path ambiguity."""
    result = []
    for record in git(repo, *args).split(b"\0"):
        if not record:
            continue
        if b"\t" not in record:
            raise ScopeError("malformed Git object record")
        header, path_bytes = record.split(b"\t", 1)
        fields = header.split(b" ")
        if len(fields) != 3:
            raise ScopeError("unexpected Git object-mode metadata")
        mode, _, third = fields
        try:
            raw_mode = mode.decode("ascii")
            raw_path = path_bytes.decode("utf-8", "surrogateescape")
            stage = third.decode("ascii") if index else "0"
        except UnicodeDecodeError as exc:
            raise ScopeError("invalid object metadata") from exc
        if not raw_mode.isdigit() or stage not in ("0", "1", "2", "3"):
            raise ScopeError("invalid Git index stage or mode")
        result.append((raw_path, raw_mode, stage))
    return result


def object_mode_gate(repo: pathlib.Path, paths: set[str]) -> set[str]:
    """Reject non-regular object modes in index and committed HEAD."""
    denied: set[str] = set()
    if not paths:
        return denied
    entries = object_entries(repo, "ls-files", "--stage", "-z", index=True)
    entries += object_entries(repo, "ls-tree", "-r", "-z", "HEAD", index=False)
    for path, mode, stage in entries:
        if path in paths and (mode not in ("100644", "100755") or stage != "0"):
            denied.add(path)
    for rel in paths:
        # Reparse points also include Windows junctions, which are not symlinks.
        candidate = repo
        for part in pathlib.PurePosixPath(rel).parts:
            candidate = candidate / part
            try:
                info = candidate.lstat()
            except (FileNotFoundError, NotADirectoryError):
                break
            except OSError as exc:
                raise ScopeError("unable to inspect path component") from exc
            if stat.S_ISLNK(info.st_mode) or (os.name == "nt" and
                    info.st_file_attributes & stat.FILE_ATTRIBUTE_REPARSE_POINT):
                denied.add(rel)
                break
    return denied




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
    unsafe_objects = object_mode_gate(repo, set(allowed))
    return sorted(set(allowed) - unsafe_objects), sorted(set(denied) | unsafe_objects)


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
