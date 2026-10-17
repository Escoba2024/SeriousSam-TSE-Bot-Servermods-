# Independent portable supervisor review, 2026-10-17

Reviewed baseline: `f56bbcdb403ffd6b8cfa85d585bc62e399a9f284` (PR #7 on PR #3). Working branch: `codex/portable-qa-watchdog-20261017`. The baseline supervisor SHA256 is `9E4271614334780C179A8B550B8E96B78A64865B86189AE5DFBCBB06A536CCB8`, matching the source hash in the preceding native recovery report. This review changes tests/tooling/documentation only. No retail run, DLL build, game installation, server access, login, push or merge was performed.

## Verdict and findings

The PR #7 readiness fix is consistent with the bounded recovery contract: loss after a successful join re-arms a 45-second deadline once, recovery clears Pending, and a later loss receives a fresh deadline. An already-armed deadline is enforced even when subsequent queries fail. A newly occurring readiness loss is not detected while all queries are unavailable, because readiness evaluation requires a valid sample. No additional production change was justified by this review.

The original direct-controller hard-exit limitation remains confirmed. Killing an owned controller bypasses its finally; its helper child remains alive and its installation lock becomes available. The original restart guard refuses the live client rather than adopting it. The original owned-stop predicate also refuses a child whose parent is the former controller. These properties are fail closed, but do not provide automatic recovery.

`Stop-PopulationOwnedLaunch` (baseline lines 107-120) selects **all** readable processes matching executable, lower start-time bound and current parent PID. It does not identify exactly one launch. Two simultaneous matching children of the same PowerShell host are therefore both rollback candidates. The regression demonstrates this only on process doubles; no parallel live process was terminated to demonstrate the limitation. This is a review concern for shared-host/concurrent launch use and is unsuitable as an external reaper identity contract. It is not evidence that this bounded, sequential direct controller killed a foreign retail process.

A state-file reaper cannot safely close the interval between CreateProcess and durable state publication. PID/start-time/path plus a dead parent's numeric PID are also not a transfer of retained process ownership to a replacement controller. A defensible future design needs a surviving launcher/guardian that owns each actual launch handle before acknowledging it, retains installation locks through cleanup, never adopts from disk, and refuses uncertain identity or uncertain controller death. Controller pause is not controller death. A guardian's own crash and failure to pin a just-created child remain separate failure cases. A Windows Job Object design would additionally need suspended-create/assignment coverage and native descendant/breakaway testing. This QA change ships no reaper and enables no automatic killing of orphans.

## Reproducible commands

PowerShell 7.6.6 is installed locally but is not on PATH. From this worktree, the actual commands were:

```powershell
$pwsh = Join-Path $env:LOCALAPPDATA 'Programs/PowerShell/7.6.6/pwsh.exe'
New-Item -ItemType Directory -Path .qa-evidence/baseline-source -Force | Out-Null
git archive --format=zip --output=.qa-evidence/base-f56bbcd.zip f56bbcdb403ffd6b8cfa85d585bc62e399a9f284
Expand-Archive -LiteralPath .qa-evidence/base-f56bbcd.zip -DestinationPath .qa-evidence/baseline-source
Copy-Item tools/Test-PortableRegression.ps1 .qa-evidence/baseline-source/tools/
& $pwsh -NoProfile -File .qa-evidence/baseline-source/tools/Test-PortableRegression.ps1 -Evidence .qa-evidence/baseline-source/qa-results

# Add just the two new regression suites to the isolated baseline source.
Copy-Item poc/scripts/Test-PopulationHardExitBoundary.Tests.ps1,poc/scripts/Test-PopulationSafetyBoundaries.Tests.ps1 .qa-evidence/baseline-source/poc/scripts/
& $pwsh -NoProfile -File .qa-evidence/baseline-source/tools/Test-PortableRegression.ps1 -Evidence .qa-evidence/baseline-source/qa-regression-3

# Separate run of the live worktree, including concurrently supplied suites.
& $pwsh -NoProfile -File tools/Test-PortableRegression.ps1 -Evidence .qa-evidence/worktree-regression-1
```

Every runner invocation requires a fresh Evidence directory. The runner logs every suite, continues after suite failures, records FAIL rather than silently skipping access errors, and returns a nonzero status if any suite failed. Temporary fixtures remain under that evidence directory. It does not forcibly time out suites: killing a suite can bypass its own helper cleanup. A hung suite can therefore hang the runner. Python and provenance verification are separate from this PowerShell-only runner.

## Actual results

| Run | PASS | FAIL | SKIP | Qualification |
| --- | ---: | ---: | ---: | --- |
| Isolated unchanged baseline, `qa-results` | 21 | 2 | 2 | Full portable PowerShell scope |
| Baseline plus new tests, `qa-regression-1` | 23 | 2 | 2 | Initial additions |
| Baseline plus new tests, `qa-regression-2` | 23 | 2 | 2 | Added partial-lock and multi-group cleanup checks |
| Baseline plus final reviewed tests, `qa-regression-3` | 23 | 2 | 2 | Final baseline regression |
| Live worktree, `worktree-regression-1` | 25 | 2 | 2 | Also includes two concurrent watchdog suites; not an independent watchdog qualification |
| Live worktree, `worktree-final` | 24 | 3 | 2 | Concurrent watchdog process suite additionally failed; current worktree is not green |

Both unchanged baseline failures are environment failures, not passes: `Test-FleetProcessControl.Tests.ps1` fails in `Get-OwnedPinnedProcess`, and `Test-PopulationSupervisorAdapter.Tests.ps1` fails in `Stop-PopulationOwnedLaunch`. Both receive `Get-CimInstance Win32_Process: Zugriff verweigert` in this sandbox. Neither was bypassed or relabeled. The full suite is **not green**. Their native parent-identity adapter coverage still needs an unrestricted Shadow run.

`Test-RetailCleanup.Tests.ps1` is skipped because it requires a real retail run. `Test-LocalReleasePackage.Tests.ps1` is skipped because it requires qualified private SDK artifacts. LocalReleasePreparation does run, using newly generated dummy fixture bytes only. Python resolves to WindowsApps aliases; no usable interpreter was established, so no Python/provenance success is claimed here.

An initial attempt under `.codex/evidence/portable-qa-20261017/baseline` aborted because `.codex` is read-only in this sandbox. Before aborting it recorded 15 PASS, FleetProcessControl FAIL (CIM denied), Phase1Telemetry FAIL (output access denied), and one package SKIP; remaining suites were not reached and result.json could not be written. The complete runs above moved evidence to `.qa-evidence` and eliminated the telemetry output error. That aborted attempt is not counted as a complete regression run.

## New regression coverage and review

- `Test-PopulationHardExitBoundary.Tests.ps1`: 20 checks. Real owned controller and child processes, OS lock contention from another process, hard controller termination, surviving child, lock release/reacquisition, partial-lock rollback, duplicate directory deduplication, torn/foreign marker refusal. The production restart guard is exercised with supplied config/profile/executable-enumeration fixtures; the original-parent stop predicate is supplied explicitly because CIM is denied. These supplied boundaries are not real retail/CIM acceptance.
- `Test-PopulationSafetyBoundaries.Tests.ps1`: 4,770 checks. Process doubles for wrong executable, one-tick stale identity, wrong parent, self-target and unavailable identity; pure-double rollback candidate-set limitation; already-armed deadline through query outage; recovery/re-loss timing at simulated seconds 46/91; ObserveOnly; cleanup continuation after one group fails; whole-process reserve cases across max population, target, reserve, occupancy and group size.
- Existing `Test-PopulationReadinessRecovery.Tests.ps1` passes with real PowerShell children and retail-format synthetic join/disconnect logs: missing-slot permanent loss, retained-name/log-only permanent loss, transient recovery.

Mutation check: in `.qa-evidence/mutant-recovery/PopulationSupervisor.ps1` only, replace `$g.Pending=$true;$g.Deadline=$time+45` with `$g.Pending=$false`. Run its copies of `Test-PopulationReadinessRecovery.Tests.ps1` and `Test-PopulationSafetyBoundaries.Tests.ps1`. Both exited 1, respectively `Disconnected live client was not recovered within bounded readiness timeout` and `Query outage postponed owned readiness timeout`. The real source was not mutated. Both tests pass again against the unmodified baseline in the final full run.

A separate read-only reviewer examined the three new tooling/test files and the original recovery logic. It identified two safety issues in the initial additions, both corrected before the final rerun: rejected PID-lookup candidates must be disposed without entering the cleanup-owned handle set; and forcibly timing out a suite can bypass nested cleanup. No remaining must-fix was reported. The reviewer did not rerun tests. If the hard-exit fixture fails before its identity handshake, an unclaimed helper can remain until its 90-second sleep expires; immediate zero leftovers on every failed harness path is not claimed.

## Concurrency and remaining gates

Separate watchdog source, tests, launcher and production-supervisor edits appeared concurrently in this same worktree after the initially clean status. They were neither authored nor changed by this QA task. The original-source baseline above is archived from the exact commit to avoid mixing evidence. The live-worktree smoke run includes their 24-check mock and 17-check process suites, but this review does not certify their launch/ack protocol or native safety. Their qualification and commits must be kept distinct from this QA result.

The subsequent live `worktree-final` run observed more concurrent watchdog/test changes and failed `Test-PopulationWatchdogProcess.Tests.ps1`: `Fixture exited before ... ready.json`, with child diagnostics `Launched process identity is unavailable or differs from plan` and `External watchdog cleanup failed closed`. This is an additional observed FAIL, not a proven root cause or an accepted reaper. No foreign-owned source was changed to mask it. The new QA hard-exit, safety and original readiness suites still passed in this run (20, 4770, and 2/2/1 starts respectively).

Git publication gate: staging only the six QA-owned files was attempted with an explicit path list. Git refused to create its linked-worktree `index.lock` outside the writable root (`Permission denied`). Nothing was staged, and no commit was created. HEAD remained `f56bbcdb403ffd6b8cfa85d585bc62e399a9f284`. No permission escalation or alternate object/index workaround was attempted. The requested sibling result-log location is also outside this sandbox's writable root; the separate result log is delivered at worktree-local `codex-qa-result-20261017.txt` instead. This is a filesystem restriction, not an outstanding request for interactive help.

Remaining Shadow tests: rerun all portable suites with real CIM access; retain exact process handles across genuine controller death; test pause versus death and launch/ack/state-publication races; demonstrate no second client through concurrent restarts and lock release; verify stale PID/parent identity and unknown lock refusals; test failure to inspect/stop without reporting successful cleanup; run hash-bound retail recovery/query-outage/hard-exit acceptance with observer/human preservation and Human-Slot-Reserve. No public browser, AI-hour, arbitrary join-race, exact slot, 12/16-bot, 24-hour or 24/7 qualification follows from these results.

## Final unrestricted Shadow runner (2026-10-17)

After the restricted-sandbox baseline above, a separate unrestricted PowerShell 7.6.6 run completed using `tools/Test-PortableRegression.ps1` with a fresh private evidence directory in `.qa-evidence/`.

- PASS: **27** discovered portable suites, including both watchdog suites, both added safety/boundary suites and `Test-ShadowRuntimeLog.ps1`.
- FAIL: **0**.
- SKIP: **2**, explicitly `Test-RetailCleanup.Tests.ps1` (requires native retail) and `Test-LocalReleasePackage.Tests.ps1` (requires qualified private SDK).
- The runner exited with code **0**, recorded `nativeRuntimeStarted=false` and `pythonAndProvenanceRun=false`.
- Code HEAD under test: `17ec15555f59220444ce76e3a541c9dc880d95eb`; the other QA source files were present in the working tree during execution and are preserved in a separate scoped QA commit.
- This supersedes the restricted environment's two CIM-denied results for the unrestricted portable run; it does **not** establish native retail acceptance, and the private evidence logs remain untracked.
