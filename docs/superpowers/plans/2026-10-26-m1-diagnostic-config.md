# M1 diagnostic config validation repair

> **For agentic workers:** Use superpowers:executing-plans task by task.

**Goal:** Resolve the final diagnostic validator/runner configuration mismatch and assess the preserved eight-bot diagnostic without changing historical receipts.
**Architecture:** Mirror only the pinned producer log-bound contract: omitted max_log_mib defaults to 32; explicit values must be integers in 1..128. Read-only retrospective validation is a new derived receipt, never a rewrite of the original BLOCKED result.
**Tech Stack:** Python unittest, Retail 1.07 Wine receipts, isolated Hetzner worktree.
**Spec:** Existing M1-M4 master plan, AGENTS.md, producer performance/native/tools/bot_sessions.py validate_config, and user instruction to continue.

## Global constraints
- Preserve all foreign worktrees, binaries, original receipts and public shutdown.
- No native spawn, restart, policy repin or release is authorized by this correction alone.
- Diagnostic PASS cannot count as M1 duration/recovery acceptance.
- Private raw data remains private. Publish source and sanitized conclusions only.

## Review focus
Missing optional log bound; explicit malformed values including bool/null/float; upper bound; complete-log scanning; preserved source and receipt provenance.

### Task 1: Correct diagnostic log-bound contract
**Files:** performance/diagnostic_native_evidence.py; performance/test_diagnostic_native_evidence.py.
**Interfaces:** Consumes raw JSON config; produces same diagnostic verdict and complete bounded scan.
- [x] Add regression: omitted field accepts complete evidence and scans a >1 MiB log within the 32 MiB default, without mutating input.
- [x] Add regression: explicit invalid bounds null/bool/float/string/zero/negative/129 are rejected; explicit 128 remains valid.
- [x] Run focused suite; expect missing default and 129 regressions RED.
- [x] Apply minimal default/range correction; run performance suite normal and optimized, then tools suite with only documented native test excluded.
- [x] Commit code, tests and evidence summary.

### Task 2: Reassess preserved diagnostic
**Files:** private derived receipt under /root/ssam-ai-backups/m1-diagnostic-reassessment-20261026/; docs/reports/2026-10-26-m1-diagnostic-reassessment.md; docs/coordination/M1-M4-CONTINUATION.md.
**Interfaces:** Consumes exact archived producer/policy/runtime receipts and corrected validator; produces separately hash-pinned retrospective verdict.
- [x] Verify old producer/input pins, original result/guard and independent fresh process/mount census.
- [x] Run corrected read-only evaluator; expect diagnostic-only verdict or explicit failed gate.
- [x] Summarize CPU-attribution/resource evidence and actual next acceptance gate; preserve historical BLOCKED.
- [x] Whole-branch independent review, verification and commit.

## Progress ledger
- Baseline: isolated branch agent/chat/20261026-m1-diagnostic-fix from Manus 4c20198; performance suite 66 PASS.
- Ruling: continue in a separate worktree because original integration has uncommitted CRC work and Manus is a separate writer. No foreign changes imported beyond committed base.
- Root cause: controller passes raw config, runner normalizes omitted max_log_mib to 32, validator demanded explicit positive int. Existing synthetic fixtures always specified it.

- Task 1 complete: RED missing default /129 reproduced; GREEN69 performance tests normal and optimized; full tools220 run/219 PASS/one documented native skip.
- Task 2 complete: all archived pins verified, fresh census clean, derived diagnostic-only PASS; original receipts hash-identical. CPU attribution and limits documented.
- Final review: independent read-only reviewer clean; focused18 tests independently PASS normal and optimized.
- No release, merge, policy alteration or new native runtime performed by these tasks.
