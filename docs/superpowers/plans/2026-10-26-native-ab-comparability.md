# Native A/B Comparability Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (- [ ]) syntax for tracking.

**Goal:** Produce a tested read-only prerequisite that prevents false Cecil P1 A/B causality claims.

**Architecture:** Read two native receipt folders; require pin identity and exactly one explicit feature flag contrast; classify reasons without reading private logs. Keep all operations isolated from the public runtime and master integrations.

**Tech Stack:** Python 3 standard library, unittest, Git in a dedicated Hetzner worktree.

**Spec:** docs/superpowers/specs/2026-10-26-native-ab-comparability-design.md

## Global constraints
- Do not access or mutate any public game process, cgroup, port, GameMP, Engine, retail asset or other agent worktree.
- Do not publish raw native logs, IPs, GUIDs, profiles or local player data.
- No claim of native sync root cause or Stable Candidate 1 release readiness from comparing metadata.

## Review Focus
- Missing Cecil flag must not silently default to false; test missing flag.
- Build or harness hash differences must invalidate clean A/B; test each separately.
- Invalid/missing metadata must not pass; test bad JSON and bad hash.
- Non-native receipt must not pass; test wrong scope.
- Output must not copy private raw fields; test safe fields only.

### Task 1: Native receipt comparison

**Files:**
- Create: `tools/native_ab_comparability.py`
- Create: `tools/test_native_ab_comparability.py`

**Interfaces:**
- `compare_runs(control_dir: pathlib.Path, candidate_dir: pathlib.Path) -> dict`
- `main(argv: list[str] | None = None) -> int`

- [x] Step 1: Write unittest fixtures and failing tests for controlled toggle, confounded colors, binary, harness, missing flag, invalid provenance and non-native scope. Expected RED: import or missing behavior.
- [x] Step 2: Implement strict stdlib-only parser and non-sensitive comparison output. Exit 0 only for controlled toggle preflight, exit 3 for confounds, exit 2 for invalid input.
- [x] Step 3: Run focused suite GREEN and all `tools/test_*.py` suite; verify no private fields escape.
- [x] Step 4: Execute read-only comparison on retained Cecil P1 vs Build04/Build06 directories, record exact confounders, no causal inference.
- [x] Step 5: Commit code/tests/docs/report; leave handoff with explicit next owned native A/B test. Never deploy or merge.

## Completion
- [x] Branch has committed artifacts.
- [x] RED and GREEN verified.
- [x] Existing unit suite unchanged.
- [x] Public PIDs/hashes untouched; no native runtime changed.
- [x] Native P1 root cause and Stable Candidate 1 remain OPEN until independently proven.