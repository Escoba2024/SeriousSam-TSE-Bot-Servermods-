# M2 Native Combat QA Implementation Plan

> **For agentic workers:** Use superpowers:executing-plans. User explicitly authorizes autonomous execution; preserve full M2 scope and native pending gates.

**Goal:** Obtain authoritative native combat/damage/weapon/respawn evidence for the actual M2 DLL, fixing genuine defects when reproduced.
**Architecture:** Original private Dedicated + one actual M2 bot + own normal original Retail opponent; controlled standard input, no game hooks or state writes.
**Tech Stack:** Existing PR73/M2 private harness, Python/X11 input, Retail1.07 binaries and original bundled map/control assets.
**Spec:** docs/superpowers/specs/2026-10-30-m2-native-combat-qa.md

## Global Constraints
- M1 IN_PROGRESS / NOT_ACCEPTED. No eight-bot/120-minute test or public activation/main merge.
- Keep all qualified binaries, foreign worktrees and services intact; retain original/resource/sync/CRC/ownership guards.
- At most one native campaign; one/two bots, <=300s per run. No heavy offline work during native measurement.
- No engine hooks, memory-state changes, teleports, unverified1.10 assumptions or M3 scope expansion.

## Review Focus
- Runtime/process records stale or replaced between target discovery and input.
- X11 event dispatch incorrectly treated as proof of accepted gameplay input.
- Native health/kill/ammo samples attributed to the wrong actor or generation.
- Private control/map staging escapes overlay or weakens existing guards.
- Exit/signal mismatch, incomplete cleanup, missing or truncated evidence accepted as PASS.

### Task 1: Native evidence reconstruction and scenario staging
**Files:** Create candidate native probe helper/tests; append sanitized evidence to existing report.
**Interfaces:** Consume existing M2 staged harness and pinned DLL860ae6d7...; produce an explicit private finite-ammo LittleTrouble scenario with original opponent control bindings.
- [ ] Reconstruct actual clip/health/frag/pose events from retained logs; record precise proof limits.
- [ ] Add failing staging/guard tests for explicit private map/finite ammo/ordinary input configuration, existing-path refusal and preservation of native bounds.
- [ ] Add smallest staging layer; normal old M2 scenarios remain reproducible.
- [ ] Test source/config output; preserve exact original control action strings and change bindings only in owned overlays.
- [ ] Commit and record provenance.

### Task 2: Own original-opponent input probe
**Files:** Add narrowly scoped PID/start/CWD/UID/netns/cgroup/window-bound input helper and tests.
**Interfaces:** Consume live MEASURING result/host guard/samples; produce private per-input receipts. Never launch a game or adopt unknown actors.
- [ ] Write failing tests for stale/foreign/missing or reused actor records and inactive guard; verify no input can occur.
- [ ] Implement target validation and bounded standard key/mouse dispatch with guaranteed release and focus verification.
- [ ] Verify real native yaw/movement/fire effects after each initial probe; stop dependent steering if unproven.
- [ ] Commit tested helper before native acceptance use.

### Task 3: Serial native gameplay and completion audit
**Files:** Private controllers/receipts; update docs/reports and M2-CONTINUATION.
**Interfaces:** Consume Tasks1–2, current build/source/config/original pins and live native lock/preflight; produce event-based evidence or concrete blockers.
- [ ] Revalidate current processes/locks/resources/public shutdown and original hashes; independent wrapper captures exit/signal/cleanup.
- [ ] Run one-bot/original-opponent probe; demonstrate received movement/aim/fire before using it for combat.
- [ ] Exercise attributable damage, loss/reacquisition, bot death/respawn and available finite weapon/ammo paths, without changing M2 intent to manufacture outcomes.
- [ ] Diagnose reproduced failures; test-first fix source when needed, rebuild as a new unqualified candidate and repeat affected native checks.
- [ ] Review coverage against all original M2 criteria; mark only proven gates. Update draft PR81 with exact remote tree verification and persistent next actions.

## Interface preflight
Task1→Task2: actual original control file/profile binding must be identified; no guessed key mapping.
Task2→Task3: input receipts require engine-side pose/rotation/fire confirmation, not only library return values.
Task1/2→Task3: new scenario/source hashes and separate external return-code receipt; no acceptance transfer from older runs.

## Progress
Start at889978f, own M2 worktree clean. Previous goal turn = progress. No native process/lock active at reinspection. First new evidence: original W input moved the actor, native Colt clip consumption and one bot kill existed in quarantined240s data; full M2 still OPEN.

## Execution ledger
- Task1: original Controls0 has duplicate StrafeLeft/Right aliases; first fixture correctly refused ambiguous arrows. Added failing bounded-alias regression, then retained native action statements and disabled duplicate alias keys in the private opponent only. Five preset tests GREEN; actual original Controls0 transforms with every Pressed/Released statement byte-equivalent after text newline normalization.
- Task1/2: new finite-ammo/known original-map stager and original-opponent input guards added. Stale/future/foreign/process-reuse/resource-state fixtures first failed for absent helper; guarded implementation now passes. No game binary/source changed. Full candidate Python tests completed before native work.
- Independent review found and fixed native constructor rejection, missing live map/20fps metadata, stale partial sample fallback, X11 routing race and unchecked release. Constructor regression first failed with `unknown private preset`; five new input cases first failed, then all26 candidate Python tests passed. Final focus/pointer+press serialized under a momentary X server grab; no sleep while grabbed. Fresh staged harness02 pins all source bytes. Protected original/restore415 files each, archive hash and42 build source hashes verified; no native process or occupied global lock before launch.
- Review follow-up: press-attempt signal regression reproduced (missing release), then fixed; rejected foreign-runtime filesystem mutation reproduced, then fixed with prevalidation and no-follow regular-file locking. All28 Python tests pass. No native launch occurred before these fixes.
