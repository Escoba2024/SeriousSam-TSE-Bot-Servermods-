# External population watchdog implementation plan

**Goal:** Clean up only clients launched by a surviving external watchdog after its controller exits, including a hard exit.

**Scope and authorization:** The user requested autonomous implementation, review, portable tests and a local commit on `codex/portable-qa-watchdog-20261017`. No additional design approval, remote publication, main changes, retail execution or DLL work.

**Design:** An opt-in launcher owns installation locks, a unique in-memory owner GUID, the controller handle and every client handle. The controller requests starts/stops over a per-run local file mailbox. The guardian launches only its immutable, configured plans and records the child identity before acknowledging a start. The controller never launches clients in this mode. PID, exact UTC start time, executable path and owner identity must match the retained handle on every stop. The guardian never loads process ownership from disk, adopts existing clients, enumerates process trees for cleanup or kills by PID. Locks remain held until cleanup completes. Existing direct mode and PR #7 readiness logic remain intact.

**Failure policy:** A live (including paused/unresponsive) controller is not an orphan. Confirmed controller exit triggers cleanup. Missing/unreadable/mismatched identity refuses termination and reports failure. A guardian crash, machine loss, hostile same-user code and kernel identity API failures are qualification boundaries; no state-based recovery claims.

**Implementation sequence:**

- [x] Add failing mock tests for exact ownership, stale/reused PID, start/path/owner mismatches, unreadable identity, controller-live hold and safe idempotent cleanup.
- [x] Implement focused watchdog core, mailbox client and external launcher; add optional supervisor transport while preserving direct mode.
- [x] Add real child-process regressions for hard exit, normal completion, outstanding start, concurrent restart/lock contention, stale state and unrelated/live-process preservation. Use PowerShell children only, no game/network.
- [x] Run new and existing portable suites, review independently, fix material findings with regression coverage, document evidence and native gaps, prepare only explicit changed files for a local commit.

**Review focus:** launch/ack race; controller exit during launch; PID reuse and mutation of receipts; guardian restart while a live guardian holds locks; failure to inspect/stop must not report successful cleanup.

**Validation:** `powershell -NoProfile -File poc/scripts/Test-PopulationWatchdog.Tests.ps1`, `Test-PopulationWatchdogProcess.Tests.ps1` and existing portable PowerShell suites (excluding retail cleanup and qualified local package fixtures). Python fixtures only if a usable interpreter is available. All output is portable evidence, never retail acceptance.

**Results:** New suites PASS with 35 + 26 checks on Windows PowerShell 5.1; full discovered portable scope PASS 27/27 on PowerShell 7.6.6 with local CIM access. Of these, two concurrently authored boundary suites are outside this watchdog commit; the baseline plus watchdog scope is 25 suites. Python unavailable. Independent read-only review found no Critical/Important defect and requested additional coverage, now present. See `docs/reports/2026-10-17-external-watchdog.md` for exact boundaries.

**Implementation decisions:** Retain guardian ownership across acknowledgement/persistence errors; never reconstruct it from state. Add per-request IDs after the replay regression exposed a stale rejection matching the next valid sequence. Read temporarily absent executable metadata for at most 500 ms from the pinned object. Preserve and exclude concurrent worktree edits from the watchdog commit. Each decision is exercised by regressions or the explicit commit file list.
