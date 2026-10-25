# Red Station GameSpy live configuration gate Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox syntax for tracking.

**Goal:** Prevent a false release claim when the original Retail server exposes `infiniteammo=0` despite startup configuration specifying 1.

**Architecture:** Read-only status + rules GameSpy queries using the existing probe; compare both against explicit requirements with final-marker completeness and consistency checks. Offline fixture runs never issue a native PASS. No production startup, restart, player action or binary changes.

**Tech Stack:** Python standard library, existing `tools/gamespy_query.py` and unittest.

**Spec:** User's existing Red Station requirements, PR #63 and native runtime mismatch observed 25 Oct 2026 23:40 UTC.

## Global constraints

- Never claim 300-second chat/MOTD or actual unlimited gameplay from GameSpy configuration alone.
- No changes to protected GameMP, `.wld`, release scripts, production server or agent worktrees.
- Missing values, malformed responses, mismatch and unknown provenance fail closed.

## Review focus

- Absent `final` marker must fail.
- Divergent status/rules must fail.
- `infiniteammo=0` must fail even when static script requests 1.
- Synthetic fixture must never be reported as a qualified runtime.
- A game/mode/version/map/name mismatch must fail.

## Task 1: Acceptance gate

**Files:**
- Create `tools/release_gates/test_redstation_gate.py`
- Create `tools/release_gates/redstation_gate.py`

- [x] Write five tests covering allowed fixture, ammo mismatch, final marker, inconsistent replies and version/map/name.
- [x] Run RED: all five scenarios fail on missing implementation.
- [x] Implement CLI and validator.
- [x] Run GREEN and inherited unit tests (5 + 18 PASS).
- [x] Perform read-only live query; `CONFIG_BLOCKED`, `infiniteammo=0` in both GameSpy responses.
- [ ] Commit, publish isolated PR and handoff to Codex main integration.

## Acceptance

Deliver tested standalone gate. Live server may legitimately be BLOCKED; do not change the active server to make a check pass. Complete remediation requires separate isolated native investigation and game/player verification.
