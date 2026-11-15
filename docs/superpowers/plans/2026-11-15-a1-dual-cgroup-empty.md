# A1 dual backend empty() implementation plan

> **For agentic workers:** Use superpowers:executing-plans and test-driven-development.

**Goal:** Apply the existing reviewed read-first cgroup disappearance rule to
exactly the two current A1 monitor backend source hashes.

**Architecture:** A separate pure source transform accepts two whole-source
SHA256 values, replaces one exact method, and verifies the whole inverse.
Tests compile only the actual extracted RuntimeBackend methods with deterministic
file lifecycles; no runtime module import or systemctl execution.

**Spec:** Parent task and `tools/native_cgroup_exit_patch.py` in Root worktree:
read first; only FileNotFoundError for exactly the cgroup.procs filename may
return the result of a fresh exists check. Reappearance remains nonempty.

**Tech Stack:** Python stdlib ast/hashlib/unittest/tempfile.

## Global constraints

- Accept only outer fb759339e7de8b31dd0fc490a0f3152be78a00d9e13f0ecb39443bc7cf7f8c1c
  and nested 13394a9cb3a69d081f9071861d36a5663367995e4b62c00738d6c4e869ef121a.
- No package, services, signals, metadata, timeout, quiescence or gameplay changes.
- Root tool unchanged. No cause attribution to the historical ON failure.
- Use only focused portable tests; broader discovery explicitly excluded by Root.

## Review focus

- Wrong/absent exception filename must propagate, including permission/EIO.
- Reappeared cgroup remains occupied, with no retry or second read.
- Both whole sources must reverse exactly; unrelated edits fail closed.
- Missing PID information cannot synthesize occupancy evidence or invoke pid().
- Existing ready/same/identity bodies remain byte-identical; only empty changes.

## Task 1: exact transform and actual-body lifecycle tests

- [x] Write tests extracting actual parent empty(), then observe RED against
  unchanged source: exists/read unlink race and read-first order.
- [x] Add pure helper with exact two-parent allowlist and exact reverse.
- [x] Run focused tests for both parents, including real tempfile unlink,
  reappearance, busy/empty, wrong filename, None filename, EACCES/EIO,
  None PID owner and whole-source mutation rejection.
- [x] Save raw logs and source/hash/inverse receipt, report and commit.

Pre-flight: single task; no shared interfaces. Ruling: no full tools discovery,
as Root explicitly bounds portable tests and shared-host load.

Ledger: actual-parent RED: five tests, six assertion failures and four expected
FileNotFoundError subcases, one transform test skipped. GREEN: five tests,
0.115 s. Self-review: pure helper has no I/O/process execution; exact BEFORE
and AFTER byte-identical to Root's reviewed tool, both full-source inverses
verified. Independent Root review remains pending; no native qualification.
