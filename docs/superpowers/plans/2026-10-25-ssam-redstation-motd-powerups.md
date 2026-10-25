# ssam.ai Red Station Server Experience Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Set ssam.ai Red Station public name, join MOTD, non-spamming five-minute chat announcement, and investigate power-up exclusion while preserving vanilla 1.07 compatibility.

**Architecture:** Extend existing isolated Red Station overlay preset, never edit verified retail binaries or original map. Make human-facing changes only in generated 1_begin.ini and Dedicated_startup.ini of freshly mounted overlays. Treat no-powerups as a separate compatibility-gated engineering task until actual vanilla join and pickups are verified.

**Tech Stack:** Python, unittest, Serious Sam TSE 1.07 console, Wine, overlayfs, Git.

**Spec:** User request 25.10.2026 to rename server, add MOTD and 5-minute server messages, and remove Red Station power-ups/invisibility.

## Global Constraints

- Do not replace game map WLD bytes, EntitiesMP.dll, client GameMP.dll, or run live server without separate safety preflight.
- Preserve original eight bot roster, GameSpy port, map, hard/infinite-ammo/flower blood/no-gibs flags.
- No unverified promises that arbitrary map power-ups have been removed.

## Review Focus

- Exact session name visible in generated 1_begin.ini and independent from MCP registry name.
- MOTD strings safe for retail shell (quote/newline escaped).
- 300-second message configured with an explicit no-duplicate guard, no arbitrary code from network input.
- No accidental modifications to vanilla original server/asset archives or inactive agents' worktrees.
- Every claim about removed power-up items needs a live map/CRC/vanilla client check.

### Task 1: Server brand and player-facing messages

**Files:** Modify `tools/redstation_preset.py`, `tools/test_redstation_preset.py`; doc `docs/decisions/2026-10-25-ssam-server-experience.md`.
- [x] Write failing test for new name/MOTD/timed message and overlay server-only application.
- [x] Run test and confirm missing functionality fails.
- [x] Implement dedicated-shell configuration and only safe fixed strings.
- [x] Run tests and smoke-generated files; inspect exact generated output.
- [ ] Commit.

### Task 2: Native compatibility assessment

**Files:** `docs/decisions/2026-10-25-ssam-server-experience.md`.
- [x] Check actual retail symbols and stock RedStation.wld for pickup types, decide whether removable by existing native gameplay flag.
- [x] If not demonstrably removable without map/Entities changes, keep vanilla runtime untouched, document blocker and required isolated map/vanilla-join qualification.
- [ ] Commit and publish status.

## Verification ledger

- 12/12 Python tests PASS and `py_compile` PASS.
- Preflight-only (overlay, no game started) PASS on isolated port 27050; generated server `1_begin.ini` and Dedicated_startup.ini inspected.
- Actual private native first attempt: FAIL `population readiness timeout`; server log pointed to unsupported custom `user INDEX` declaration; replaced with built-in `tmp_ai[9]` guard and tested offline. Native regression after correction is still required.
- Power-up removal NOT IMPLEMENTED: no stock Retail 1.07 global disable switch identified; change to world/entity code requires isolated vanilla join + sync qualification.
