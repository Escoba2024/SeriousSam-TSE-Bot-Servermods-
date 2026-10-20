# TSE Classic Retail 1.07 — B0 Native One-Bot Sync Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: use superpowers:executing-plans inline. No subagents.

**Goal:** Reproduce and qualify one native BotClient joining an unchanged Retail 1.07 Dedicated server with an original Vanilla observer; diagnose sync, preserve binaries, and advance stability gates only after proof.

**Architecture:** Read-only preflight and SHA verification; use private owned Shadow runtime clones and owned process handles, run a restrained bot profile and observe native logs plus population; use the existing pinned comparator on aligned native captures. Persist only redacted aggregates to Git; preserve raw binaries/logs under ignored private evidence paths. Base is commit d8fba75.

**Tech Stack:** Windows PowerShell 5.1 (Shadow), Retail-1.07 x86 executable/DLL, Python comparator (pinned PR#21), Git/Linux portable regression.

**Spec:** User B0 requirement, 2026-10-20; previous P0-PAIR plan and ledger at 2026-10-19-tse-main-sync-qualification.md / 2026-10-19-tse-main-sync-progress.md.

## Global Constraints
- No unowned process stop, DLL overwrite, foreign worktree, shared branch push, fake CRC, disabling KickOnSyncBad.
- Qualified bot GameMP SHA256 61DC27E0E7B80BADCF9AE705C30FCA88EDD3935737715DFFFF59E90C26F1FEF9.
- Original Retail Engine SHA256 B79BF8BB3927FE4F8F252E141D721AE5C738DF02218F0ECC12DA5C1AFBCB534F.
- Original Retail GameMP SHA256 1C41DA35B3FC47378C407B770E1BD1DCC2B7E6BF676C140586BC6035461D4208.
- Critical failures: stop progression; do not claim continuous tick coverage from one sampled match.

## Review Focus
- Bot process launched but not actually joined/recognized: must fail.
- Bot startup configuration ignores stationary profile: must be proven effective or declared unverified.
- CRC/Sync from logs accidentally conflated with other runs: record run-specific archived logs.
- Native snapshot timing mismatch or uninstrumented versus instrumented comparison: separate outcomes.
- Unexpected process ownership/restore mismatch: refuse unsafe cleanup and fail gate.

### Task 1: Preflight and preserve isolated native test environment
- [x] Verify Shadow devices, no game processes, test ports 25640/25641, source hashes and existing P0-PAIR copies.
- [x] Create private third BotClient clone without touching source binaries, pin hashes, validate args and null bot profile.
- [x] Build own isolated run harness with strict process ownership and finally/restore behavior.

### Task 2: Native B0.1 and B0.2 gates
- [x] Accept existing proven 120s vanilla control only as historical, recheck immutable evidence.
- [x] Start dedicated, Vanilla observer and one bot on isolated localhost port; verify join, bot identity, CRC and action acceptance.
- [x] Run controlled 1-bot observation (no capture initially); record process exits, sync logs, performance and cleanup.

### Task 3: Evidence and root cause
- [x] If B0.2 clean, attempt isolated native server/observer aligned snapshot; use exact Level/Sequence/Tick comparator.
- [ ] If SYNCBAD, reproduce with smallest profile and inspect original evidence before changes.
- [ ] No fixes without root cause and RED/GREEN.

### Task 4: Qualified stability and provenance
- [ ] Only after 1 bot pass, extend to 2, 4 then 8 in separate cells; >=3600s eight-bot target.
- [ ] Record PASS/FAIL/BLOCKED for each cell and restore owned processes/configs.
- [ ] Run relevant portable tests and diff check, commit/push only own documented verified changes.
