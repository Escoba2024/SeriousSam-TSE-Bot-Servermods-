# Combat regression completion implementation plan

> For agentic workers: execute inline with superpowers:executing-plans and TDD.

Goal: repair confirmed PR57 combat/recovery regressions in the opt-in composed source candidate.
Architecture: keep one HumanBotPolicy, exact upstream pins, and scoped zero-fuzz source patches. Fresh perception may cancel history escape; existing reaction/aim/LOS/blast/cadence remain authoritative. Obstacle recovery owns hidden-target detours; exploratory turn holds yield to the existing navigation override callback.
Tech stack: Python3 standard library, serial C++17 portable tests, git.
Spec: delegated task; AGENTS.md and docs/decisions/2026-10-17-tse-ai-tools-mcp-policy.md; PR72 QA01/QA02 pinned 7df2867e1ad7a6101b95a54031d7583265977f72.

## Global constraints
- Change only poc/candidates/combat-master-20261026/** and this docs directory.
- Source base 63638893b40ee6b8c095a634213eb5cf2656ffbe, unchanged PR57/PR66/PR62 pins.
- No source checkout changes in other worktrees, native processes/builds, packages, Codex CLI, push, merge or deploy.
- Serial lightweight portable commands under nice19; runtime/native acceptance NOT_TESTED.
- Skill/persona capabilities and new module defaults remain unchanged.

## Review focus
- Fresh visible attacker on initial damage tick cancels escape, without bypassing reaction.
- New visible attacker during existing retreat cancels it on that same observation tick.
- Hidden/occluded/FOV-rejected enemy cannot cancel retreat or authorize fire.
- Hidden-target detour beyond45deg retains movement intent and crosses wall using real recovery.
- Exploratory travel rotates coherently and still respects injury/final movement gates.

## Task1: characterize and repair QA01/QA02
Files: tests/test_combat_regressions.cpp; combat.patch; verify.py.
Interfaces: actual HumanBotPolicy BeginTick/PlanLosQueries/Step; actual ObstacleRecovery Update. No replacement combat simulator.
- [x] Add failing tests for default-off hidden chase turn, real closed-loop wall bypass, same-tick and delayed visible ambush cancellation, and occlusion control.
- [x] Compile/run against unchanged candidate; record expected assertion failures.
- [x] Gate chase turn hold to exploratory movement without active recovery and cancel escape only on fresh perception-visible threat before escape early return.
- [x] Run regression executable and complete existing verify.py sequentially; maintain21600-row default-off compatibility corpus outside corrected scenarios.
- [x] Self-review actual patches, source manifests and all test results; commit scoped candidate and report.
