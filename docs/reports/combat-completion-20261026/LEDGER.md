# SDD ledger — plan: docs/reports/combat-completion-20261026/PLAN.md

Baseline:63638893b40ee6b8c095a634213eb5cf2656ffbe. Worktree /srv/tse-combat-completion-20261026, branch agent/chat/20261026-combat-completion.
Policy read in full from /srv/tse-m1-diagnostic-fix-20261026. Source checkout /srv/tse-c1-combat-20261026 and its untracked compare_qa62.py untouched.
Ruling: import source and upstream pin objects via local fetch into /srv/tse — source objects lived in distinct /srv/tse-main-agent-20261019/.git; no network or checkout mutation required.
Ruling: delegated autonomous execution supersedes plan-confirmation pause; plan and ledger stay inside explicitly assigned docs scope.
Baseline verify.py PASS:1243 candidate checks,21600 identical command rows,10 inherited binaries, driver-block smoke, both materialization modes. Initial missing PR66 object recovered via local fetch; no production defect.
Task interface scan: regression executable and verify.py consume only materialized real headers; no independent simulator policy or shared writable sources.

RED actual unmodified candidate:321 assertions,313 failures; same-tick/delayed ambush100 escape ticks/0 shots; wall bypass false with5 reset loops. Occluded control retains100 escape ticks/0 shots. Initial fixture warning corrected before final verification.
Ruling: R02 QA source duplicates an obsolete search-heading algorithm; pinned PR57 actually uses RouteMemory::Travel, which computes coherent desired heading. Use actual policy+route+recovery rather than import the mirror.
Implementation: cancel history escape on fresh Perception::Visible, not on raw actor coordinates; gate >45deg hold to exploratory+visible target. Hidden-target path remains recovery-owned; no profile/pin/module default changes.

First GREEN attempt: default trace and1243 existing checks PASS; regression512/513 PASS. Exploratory wall had0 reset loops and58.91m lateral clearance, but did not cross behind original pillar after its target memory expired at tick30.
Ruling: require actual default-mode wall crossing; exploratory mode requires clearing the wall without reset loops, not pursuing a target whose memory expired. Debug pose trace shows deliberate route novelty after perception forgets, so changing production pursuit would invent hidden-memory behavior outside QA01. Added separate40-seed actual-policy test for bounded exploratory turning and resumed travel, and fresh-LOS/outside-FOV negative control.

GREEN full verify.py exit0 (22.84s):29397 new regression assertions,1243 existing composition assertions,21600 offtrace rows identical hash51398dd81d9f3f6265eb1d0640f0f4a5bd002aeaabb5f62a04595e23a70420aa; all10 inherited executables; driver-block smoke; both applier modes and overwrite refusal. No compiler warnings in final suite.
Fresh reviewer dispatched read-only per requesting-code-review; no extra writer/native process.

Independent mutation controls: remove fresh-visible cancellation ->29205checks/307failures; restore unflagged turn gate ->29397checks/4failures. Both use unchanged real HumanBotPolicy dependencies, compiled serial O0/nice19.

Fresh review Important: Enemy helpers and trace used uninitialized SenseInput members. Corrected value initialization in all3 candidate test sources; reran full suite PASS with same trace hash. Earlier pre-initialization RED geometry is superseded. Initialized RED against original candidate:29205checks/311failures, wall7/9reset loops;307fails without cancel,4fails without turn gating.
Fresh review Minor: wall fixture used visibility instead of actual distance/weapon recovery hold. Corrected native hold threshold and no-target movement fallback. New actual-policy50deg visible-target probe demonstrates2failures in the first gated fix.
Ruling: remove the combat bearing stop entirely, restoring movement/recovery ownership for both remembered and far visible targets; retaining it under exploratory mode still contradicts native recovery's distance-based hold. Route travel turns and final hazard/injury gates remain intact. No new state or adapter API.

Complete stop removal passed29409 new assertions but FAILED required inherited test_bot_route.cpp:190, which intentionally protects exploratory off-axis chasing before recovery. No success claim for that run.
Ruling: preserve exploratory turn hold when recovery is inactive; suppress it during existing NotifyNavigation(true) contract, for either visible or remembered targets. Keep default-off unflagged hold removed. Reset clears recovery state; NotifyNavigation(false) restores hold. This matches inherited terrain-safety intent and real adapter recovery ownership without a new API.

Final full verification PASS after preserving inherited exploratory safety and correcting fixtures/native hold inputs; exact counts and outcomes in VERIFICATION.json and RED_MUTATIONS.json. All10 inherited binaries pass again. No unresolved failed required tests. Scope remains source-only/native NOT_TESTED.

Fresh reviewer found stale recovery state when native obstacle avoidance is disabled. Initial fragment extractor was too broad and failed to compile; narrowed extraction to brace-free reset body before testing. Exact native reset-tail fragment against real HumanBotPolicy reproduces FAIL exit3 before driver fix. Added NotifyNavigation(false) to that branch in driver.patch and executable verification beyond old smoke's truncation point.

FINAL PASS after adapter disable-state correction: verify.py exit0;29414 regression checks,1243 composition checks,21600 identical compatibility rows,10 inherited executables, exact native recovery reset branch, original driver-block smoke, both applier modes. Native build/Retail acceptance remain NOT_TESTED.
Diff whitespace warnings are canonical blank context lines inside nested unified .patch artifacts, not generated-source trailing whitespace.
