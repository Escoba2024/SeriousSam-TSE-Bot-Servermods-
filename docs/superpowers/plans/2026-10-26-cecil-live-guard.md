# Cecil native A/B public admission implementation plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (- [x]) syntax for tracking.

**Goal:** Guard the existing Cecil session harness against false public-safety PASS from stale or incomplete metadata before native A/B runs.

**Architecture:** Pure validation helpers for public result and health snapshot and exact roster matching; call at live_public_guard creation and throughout monitoring. Fail closed without mutation or game start. Maintain current isolated runner's locks and runtime protection.

**Tech Stack:** Python 3 standard library, unittest, existing tools/qualify_bot_sessions.py.

**Spec:** docs/superpowers/specs/2026-10-26-cecil-live-guard-design.md

## Constraints
- Never stop/restart/replace any public PID, game file or runtime.
- All changes in isolated worktree; no secrets, identifiers or raw logs in Git.
- No bypass of native kick or host reserve gates.
- A refusal is correct until health producer is generation-bound and fresh.

### Task 1: Fail-closed guard
- [x] Write RED unit tests for missing expected_names, stale health, absent generation identity, insufficient sync coverage, mismatching process generation, and extra/unknown roster entries.
- [x] Minimal helper and live guard integration, then focused suite GREEN and existing full Python suite.
- [x] Read-only current-generation probe MUST return BLOCKED, not PASS.
- [x] Document exact host/runtime blocker and required safe producer fields.

### Task 2: Integrate evidence

Status: Local code and evidence verified; remote GitHub publication is independently gated.
- [x] Persist report with version hashes, test count, explicit next native experiment and blocker.
- [x] Commit independently; publish separate draft PR based on P1 branch, no auto merge.
- [x] Verify protected PIDs and main agent worktree remain unchanged.
