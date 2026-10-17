# Portable supervisor QA implementation plan

**Goal:** Independently verify f56bbcd/PR #7 recovery and bound the controller hard-exit risk without touching retail runtimes.

**Architecture:** Run every existing portable PowerShell suite in a separate process with fixture/temp output under a fresh evidence directory. Add real owned helper-process tests for controller death and installation locking, deterministic loop tests for recovery/reserve/cleanup, and negative identity tests. Preserve production behavior unless an ownership-safe fix is demonstrably possible.

**Spec:** User task dated 2026-10-17; poc/POPULATION-SUPERVISOR.md; docs/reports/2026-10-16-supervisor-readiness-recovery.md.

## Constraints

- Only this worktree; no retail/game/server changes, login, push, merge, or foreign process operations.
- Existing isolated branch codex/portable-qa-watchdog-20261017, base f56bbcd.
- RetailCleanup and LocalReleasePackage require native/private artifacts and are explicit skips.
- Native acceptance and portable helper processes are separate evidence classes.
- Execute autonomously as requested; no interactive plan approval or delegation needed.

## Tasks

- [x] Add tools/Test-PortableRegression.ps1: fresh evidence, runtime/git metadata, per-suite logs and all pass/fail/skip results, temp inside worktree. Review ruling: no forced suite timeout, because that can bypass nested helper cleanup.
- [x] Run baseline suites on PowerShell 7.6.6; inspect all failures before changes. 21 PASS, 2 CIM access-denied FAIL, 2 SKIP.
- [x] Add Test-PopulationHardExitBoundary.Tests.ps1: owned controller/child handshake, lock contention across processes, hard exit, orphan rejection, safe lock reacquisition and retained-handle cleanup. Unknown/partial locks must fail closed.
- [x] Add Test-PopulationSafetyBoundaries.Tests.ps1: wrong exe/start/parent/self and inaccessible identity; synthetic rollback boundary; deterministic readiness/outage/ObserveOnly/reserve/cleanup cases.
- [x] Run the entire portable scope after each change batch; mutation-check critical regressions using isolated source copies only. Isolated final: 23 PASS / 2 unchanged CIM FAIL / 2 SKIP. Readiness mutation rejected twice.
- [x] Write sanitized independent review and result log with exact commands, risks and Shadow native gates. Do not ship a reaper without atomic launch/ownership handoff and crash-window proof.
- [x] Verify diff and protected tracked assets. Explicit-path staging denied creating external linked-worktree index.lock; no commit possible in sandbox. No remote actions.

## Review ledger

- Separate read-only reviewer found two initial test-tooling safety issues: promote a PID-lookup candidate into cleanup ownership only after exact identity validation; avoid forcibly aborting suites and bypassing their nested helper cleanup. Both corrected and full isolated regression rerun.
- Ruling: no production reaper in this QA work. Original hard-exit adoption is intentionally refused; disk/PID receipts do not prove transferred process ownership. Concurrent separate watchdog source is excluded from this verdict.
- Ruling: preserve all concurrent foreign work; archive f56bbcd for stable independent evidence. Live-worktree final run recorded an additional concurrent watchdog-process FAIL and remains unqualified.
- Ruling: full regression is not green because real CIM is denied. Keep both failures visible; no mock fallback for original failed suites.

## Review focus

PID reuse and stale parent IDs; unknown installation lock content; locks released before orphan exit; hard exit before state publication; pending readiness during invalid UDP; no unsafe orphan adoption from disk state.
