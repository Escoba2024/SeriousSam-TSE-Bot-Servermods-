# Hetzner TSE Dispatcher — Acceptance & API Budget Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task. All implementation changes use RED→GREEN and a fresh end-to-end evidence check.

**Goal:** Close the existing dispatcher acceptance by preserving verified two-job, restart and recovery evidence and fixing the observed unauthenticated GitHub API exhaustion for future authorized work.

**Architecture:** Retain the single root-policy-gated systemd oneshot dispatcher and SQLite transaction ledger. A bounded polling layer skips immutable terminal jobs, persists GitHub rate-limit reset times for pending jobs, and backs off rather than exhausting GitHub's 60-request unauthenticated budget. No second worker, no game-runtime access, no merge, no Notion credential bypass.

**Tech Stack:** Ubuntu 24.04/CX23, Python 3.12 stdlib sqlite3/urllib/unittest, Git, systemd, Codex CLI, GitHub pinned manifest grant.

**Spec:** Existing `tools/notion_bridge/README.md`; authorized manifest Issues #32/#33; Issue #18.

## Global Constraints
- Isolated branch `agent/A00/18-dispatcher-api-budget-20261018`, based on `38ab237851d166bc02115d8e9fca21c45dd8d3a8`; separate worktree only.
- Allowed source: `tools/notion_bridge/development_dispatch.py`, `tools/notion_bridge/test_development_dispatch.py`, `tools/notion_bridge/systemd/tse-notion-bridge.timer`, and this plan/evidence ledger only.
- Preserve `/srv/sam`, game runtime, deployed credentials and all existing job worktrees and results. No merge, force-push or process kill.
- Admin policy remains the sole grant; old `REVIEW_READY` jobs must never be re-executed.
- No fabricated test success, no quota-limit workaround using copied credentials.
- Server evidence lives in `/var/lib/tse-agent-control/development/`; job source logs remain private.

## Review Focus
1. Already `REVIEW_READY` jobs must not call GitHub API and must keep attempt count 1.
2. A new authorized `QUEUED` job must fetch and validate its exact owner manifest before execution.
3. GitHub HTTP 403 rate-limit must persist an explicit cooldown from reset headers and leave existing jobs untouched.
4. A new server process after reboot must preserve SQLite state/attempt counts and avoid duplicate work.
5. No model launch without valid lease/manifest, and no game/foreign path access.

---

### Task 1: Snapshot current evidence and baseline

**Files:** `docs/superpowers/ledger/2026-10-18-hetzner-dispatcher-progress.md`.

**Interfaces:** consumes GitHub PR #31, #34, #35 and read-only service state; produces evidence summary and next task checkpoint.

- [ ] Capture production SHA, clean Git worktree, systemd unit/timer, SQLite status and relevant journal lines.
- [ ] Independently compare two published commits with GitHub PRs and record exact sequential event/attempt evidence.
- [ ] Confirm before/after boot IDs and controlled-fault fixture scope; explicitly distinguish synthetic fault test from live reboot.
- [ ] Commit evidence to the isolated plan branch; do not alter service state.

### Task 2: RED→GREEN — API fetch budget and fail-closed cooldown

**Files:**
- Modify: `tools/notion_bridge/development_dispatch.py`
- Modify: `tools/notion_bridge/test_development_dispatch.py`

**Interfaces:**
- Existing: `poll(db: sqlite3.Connection, root: Path, policy: dict) -> None`
- Existing: `fetch_issue(number: int) -> dict`
- Add: `class GitHubRateLimited(Transient)` with `reset_at: float`; derive from real response headers.
- Add: persist `github_rate_limit_until` under SQLite `meta`, default 0.

- [ ] Write a failing regression: two terminal jobs, poll once, assert `fetch_issue` never called and their attempts/status unchanged.
- [ ] Run that exact test; confirm meaningful assertion failure (RED).
- [ ] Skip immutable terminal jobs before API calls; leave newly queued/blocked eligible jobs subject to owner-policy verification.
- [ ] Write failing 403-reset test using a synthetic urllib HTTPError with `X-RateLimit-Remaining: 0` and reset epoch; assert SQLite cooldown and no code launch.
- [ ] Run test RED; implement conservative parsing and bounded fallback for absent/bad headers.
- [ ] Write and run regression for cooldown persistence across DB reopen and eventual revalidation of an authorized pending job; keep fail-closed on ordinary 403/auth failure.
- [ ] Run full `python3 -B -m unittest discover -s tools/notion_bridge -p test_*.py -v`; expected exit 0, no regressions.
- [ ] `git diff --check` and exact scope inspection before commit.

### Task 3: RED→GREEN — cadence policy

**Files:**
- Modify: `tools/notion_bridge/systemd/tse-notion-bridge.timer`
- Modify: `tools/notion_bridge/test_development_dispatch.py`

**Interfaces:** production timer `OnUnitInactiveSec=300s` (reduce idle API traffic, preserve `Persistent=true`).

- [ ] Add a failing static fixture regression requiring 300-second cadence.
- [ ] Run RED, change timer from 60s to 300s, run GREEN and full suite.
- [ ] Commit only approved files; publish own branch as Draft PR if tests are independently verified.

### Task 4: Production upgrade and protected verification

**Files:** isolated read-only service/source backup and private verification logs on CX23; GitHub Handoff.

- [ ] Confirm current service not running, no pending/foreign model child, backup installed files/unit/state.
- [ ] Run Linux tests as `tsecontrol` in an isolated candidate checkout, first baseline then candidate.
- [ ] Under direct owner authorization, deploy only reviewed dispatcher Python and timer; restart own timer/service after safe controlled stop. Preserve original checkout and rollback path.
- [ ] Check service hash/branch, journal, `systemctl` and SQLite; terminal jobs retain attempts 1, source_errors clears for terminal grants, and no model reruns.
- [ ] Demonstrate 403/cooldown behavior in synthetic tests (no deliberate production rate exhaustion); observe real polling after upstream reset if possible.
- [ ] If any check fails, restore only own unit/source from verified backup and report BLOCKED.

### Task 5: Final evidence and handoff

- [ ] Update persistent ledger with each test command, exit code, branch/commit, live observed boot IDs, faults and residual limits.
- [ ] Confirm PR #34/#35 and their exact SHA remain unchanged, no unintended writes/game processes, systemd timer enabled/active.
- [ ] Publish a clear review handoff in GitHub Issue #18; classify `REVIEW_READY` vs integrated `DONE`.
- [ ] Mark goal complete only after all live acceptance criteria and rate-limit repair pass; otherwise identify exact blocker and recovery instructions.

---
### Task 6: Full-CX23 reboot acceptance for the deployed API-budget release

**Files:** private evidence snapshots under `/var/lib/tse-agent-control/development/acceptance-<timestamp>-before/after-reboot-a00.json`; append to the existing persistent ledger. No source change.

**Interfaces:** existing `tse-notion-bridge.service`, `tse-notion-bridge.timer`, `development_dispatch.py --status` and persisted SQLite `development/jobs.sqlite`.

- [ ] Verify the exact installed release Git HEAD `a839ececab2e6ddb09087f94b84865afcde99d65` and clean worktree, active/enabled 300s timer, successful service, no outstanding jobs, model or third-party workload, and current boot ID.
- [ ] Capture pre-reboot SQLite jobs IDs/states/attempts/commits/event count; identify Nginx and other services as reboot-visible downtime; record a ruling under the explicit owner's requirement for real reboot acceptance.
- [ ] Confirm backups and accessible SSH, capture private pre-reboot snapshot, initiate exactly one normal OS reboot (no force, no process kill).
- [ ] Reconnect through the existing trusted SSH host key and verify changed Linux boot ID, same source and deployed unit, enabled/active timer, Nginx recovered, jobs and events byte-for-byte logically unchanged, no duplicated model attempts.
- [ ] Run service safely under `tsecontrol` through systemd, verify `Result=success` and `ExecMainStatus=0`; re-run the full 89-test suite against the immutable release.
- [ ] Record all timestamps, command outputs, test counts, remaining limitations in ledger and GitHub #18, retaining `REVIEW_READY` until separate human integration acceptance. If SSH does not return or services fail, stop, avoid destructive rollback, report precise blocker.

### Task 7: Final owner workflow / external integration gate
- [ ] Confirm optional Notion server token status without reading secrets; differentiate unavailable Notion direct API from working GitHub-authorized queue.
- [ ] Confirm deployed source commit identical to source blob in Draft PR #36 and correct order/published SHA of PRs #34/#35.
- [ ] Final plan/ledger commit+push on own documentation branch, recheck upstream clean and GitHub Issue #18 handoff link.
- [ ] Conclude the GitHub dispatcher technical acceptance if all contractual gates passed. Leave merges, game runtime deployment and optional Notion API token as explicit separate future approvals.
