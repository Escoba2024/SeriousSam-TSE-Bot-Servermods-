# External population watchdog: implementation and portable qualification

Scope: isolated branch `codex/portable-qa-watchdog-20261017`, starting at `f56bbcd`. This extends the open external-watchdog boundary recorded in the [readiness recovery report](2026-10-16-supervisor-readiness-recovery.md). It does not reimplement the PR #7 readiness fix. No main, retail binaries, DLLs, server configuration, credentials or private runtime captures are part of this change.

`poc/scripts/Watch-BotPopulation.ps1` is an opt-in external launcher. Its separate controller uses the existing population loop through an internal transport. The guardian holds installation locks, immutable configured launch plans, its unique run identity and each actual launch process object. The controller never launches clients itself in this mode. Every stop rechecks owner identity, PID, executable path and exact UTC start time against the pinned handle. Mutable receipts never supply a process to terminate. No PID-only kill, process-tree kill, process-name kill or adoption is implemented.

The guardian observes the retained controller handle, rather than a heartbeat timeout. Confirmed controller exit triggers cleanup. A live controller preserves its clients. Client ownership is retained before metadata publication or acknowledgement; this covers controller death between launch and acknowledgement and receipt/response write failures after capture. Existing processes and reused state directories are refused. Installation locks remain held through cleanup, including during controller death and concurrent restart attempts. Exited previous-generation handles are disposed before replacing their records.

The local mailbox validates run identity, next sequence and controller PID/start/path. Responses also carry a unique request ID, so a rejection from an invalid request using the next sequence cannot be mistaken for the response to a later valid request. This is crash/race isolation under trusted local storage, not an authentication boundary against hostile code with the same OS user privileges.

## Portable evidence

Tests start only PowerShell helper processes. Query/config doubles exercise the production supervisor transport without contacting a game or external server. The broader pre-existing adapter test uses local loopback UDP only.

- `Test-PopulationWatchdog.Tests.ps1`: 35 checks covering exact ownership, delayed executable metadata, live-controller hold, idempotent cleanup, PID/handle replacement, start/path/owner mismatch, self-stop refusal, inaccessible identity, kill failure, partial cleanup failure, atomic mailbox replacement and invalid request identity/sequence fields.
- `Test-PopulationWatchdogProcess.Tests.ps1`: 26 checks covering actual controller hard exit, existing guardian lock contention, invalid mailbox owner/sequence/caller tuples with preservation of the live child, valid next sequence, Start/Stop/Start generations, receipt tampering toward an unrelated child, stale-state refusal, a fresh guardian against the same installation, normal completion, deterministic controller death after launch before acknowledgement, guardian receipt/response persistence failures, production supervisor transport and controller-side receipt failure.
- The unrelated helper uses the same executable as owned helpers and remains alive through every tested cleanup. Fixtures use held handles for teardown. No online or retail test is part of these results.

The initial RED run failed because the watchdog core was absent. Further regression runs reproduced the PowerShell 5.1 atomic-replace null-backup incompatibility, a stale rejection matching a later valid sequence, and transient missing executable metadata in PowerShell 7. Each received focused regression coverage.

Final results on this Windows host:

| Scope | Result |
| --- | --- |
| Two new watchdog suites, Windows PowerShell 5.1 | PASS, 35 + 26 checks |
| Existing portable scope plus two new watchdog suites, PowerShell 7.6.6 | PASS, 25 suites |
| Two additional concurrently authored boundary suites in this worktree | PASS, 2 suites; their files are outside this watchdog commit |
| Entire discovered portable PowerShell scope, PowerShell 7.6.6 | PASS, 27/27 suites, zero failures |
| Retail cleanup and qualified local package fixtures | SKIP, require separate native/private artifacts |
| Python fixtures and Python source-provenance runner | NOT RUN, no usable Python interpreter available; WindowsApps alias could not execute |

The initial sandboxed broad run denied local CIM process inspection in `Test-FleetProcessControl.Tests.ps1` and `Test-PopulationSupervisorAdapter.Tests.ps1`. Both passed with approved local CIM access. The final entire PowerShell run used that access and completed with exit code zero. No production identity check was weakened to accommodate the sandbox.

Commands for the new suites (use `powershell` for the 5.1 run and `pwsh` for the 7.6.6 run):

```powershell
pwsh -NoProfile -ExecutionPolicy Bypass -File poc/scripts/Test-PopulationWatchdog.Tests.ps1
pwsh -NoProfile -ExecutionPolicy Bypass -File poc/scripts/Test-PopulationWatchdogProcess.Tests.ps1
```

The final broad invocation was `pwsh -NoProfile -ExecutionPolicy Bypass -File .superpowers/watchdog-20261017-final/run.ps1`. That ignored local runner executes each `poc/scripts/*.Tests.ps1` in a separate process, skips the two artifact-dependent suites above and also runs `tools/Test-ShadowRuntimeLog.ps1`. Its private `powershell-result.json` contains 27 entries, all `exitCode=0`. No runner output, process receipts or private helper logs are included in this commit. `git diff --check` passed, and there are no changes under `poc/patch` or `poc/release` relative to the starting commit.

## Independent review

A separate read-only reviewer examined ownership, launch/acknowledgement races, controller-live hold, installation locking, stale state and error reporting. It found no Critical or Important correctness defect. Its coverage notes prompted negative mailbox tests, repeated generations, production-supervisor transport, persistence-failure cases and a real fresh guardian using the same installation. The implementation author reviewed those additions and reran the regressions.

## Native qualification gaps

Portable PASS does not establish retail acceptance. Still required: an isolated, hash-bound TSE 1.07 native run with the qualified BotClient DLL; hard exit during native start/join and after readiness; unchanged observer/human/dedicated processes; cleanup and restart evidence; graceful versus forced native shutdown classification; and preservation hashes for protected assets. Arbitrary OS scheduling races, multi-installation scale, 12/16-bot load, map-change behavior, AI-hour results, public browser operation and 24-hour/24/7 operation are not qualified here.

The watchdog must survive the controller. Guardian crash, machine loss, hostile same-user storage mutation and failed/unreadable kernel metadata are separate boundaries. If a live child's identity cannot be established, cleanup refuses termination and reports failure. A new watchdog never reconstructs ownership from a previous run's files. Existing direct controller mode retains its documented hard-exit orphan boundary.
