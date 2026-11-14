# A4 local supply contention implementation plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [x]`) syntax for tracking.

**Goal:** Reduce repeated first-weapon acquisition losses to nearer bots in the same four-slot BotClient process.

**Architecture:** Record a short-lived, map/life/goal-bound observation of an unarmed local bot pursuing a mapped weapon. During new mapped weapon selection prefer an otherwise eligible uncontested item over a target with a nearer live local pursuer; retain the original candidate as fallback when no reachable alternative is found. This changes client decision state only.

**Tech Stack:** C++14; existing actual-body portable bridge harness; pinned Engine107 button/ray contracts.

**Spec:** Main-agent delegated design, 2026-11-14: avoid far local bot selecting mapped weapon actively pursued by a nearer live local bot; release on death/map/life/generation/reset/goal loss/stall; no item/replicated-state writes, no hidden pickups, no cross-process claims, no blanket exclusion without reachable alternative.

## Global constraints

- Main agent alone integrates and changes runtime. No DLL builds or game/native runtime launches here.
- Preserve live item decoding, directed graph reachability, connector rays and fixed attempt deadlines.
- Claims have only local process scope, four existing slots, no shared files/IPC or retained entity pointers.
- Publish only sanitized findings, never private raw logs or identities. Native effectiveness stays NOT_TESTED.

## Review focus

1. Dead, reset, replaced, stale, disconnected or differently mapped peer must not suppress a weapon.
2. A stationary claimant must release preference even while ticking; movement resumes its bounded observation.
3. A nearer candidate must not yield to a farther claimant; equal estimates preserve old ranking.
4. Hidden/unreachable/physically blocked alternatives must not starve the original obtainable target.
5. Existing map/air/close-combat safety and zero-allocation hot paths must remain intact.

## Task 1: Local claim and selection regression

**Files:** Modify `poc/candidates/redstation-supply-20261107/BotSupplyNative.h` and `test_cecil_native_bridge.py` in that directory.

**Interfaces:** Existing `BotSupplyTick`, `BotCecilChooseMappedWeapon`, `SSupplyState::ClearGoal/Reset`; bounded local observation helper and comparator.

- [x] Add behavioral fixtures with two actual bridge slots and distinct players in one world. Establish a nearer mapped pursuer and assert farther bot chooses the reachable alternative, while a lone reachable target remains selectable.
- [x] Run `python3 poc/candidates/redstation-supply-20261107/test_cecil_native_bridge.py --sdk-player /srv/tse-sdk-20261021/Sources/EntitiesMP/Player.es`; expect the new alternative-selection assertion to fail against unchanged production code (RED).
- [x] Implement a fresh bounded observation tied to world, map serial, entity, generation and mapped attempt. Expire stale observations after .25 seconds and stationary observations after 5 seconds; clear with existing goal/reset lifecycle. Check live local player health before preferring another target. Compare finite existing directed-route cost estimates with a 1-unit advantage; do not perform new graph searches or rays for competition.
- [x] Prefer uncontested eligible candidates in existing connector-validation loop; preserve contested candidates as fallback, no rejection/backoff merely for contention.
- [x] Add/run release, farther-peer, hidden, unreachable, blocked-alternative and diagnostics/no-allocation regressions; preserve the existing whole-bridge suite.
- [x] Run normal and ASan/UBSan bridge against SDK107 contract; expect all checks passing.

## Task 2: Verification and handoff

**Files:** Create `docs/reports/2026-11-14-a4-local-supply-contention.md`.

**Interfaces:** Task1 source/tests, existing candidate portable suite, historical sanitized evidence.

- [x] Run candidate C++ tests and applicable Python actual-body/item/action/observer tests, plus prescribed portable tooling tests. Record actual results and limitations.
- [x] Review all diffs for state writes, stale claims and starvation; main agent performs independent final review.
- [x] Record the six exact same-process pickup correlations, unresolved two losses, RED→GREEN commands and native NOT_TESTED status.
- [x] Commit only scoped source/tests/plan/sanitized report and return exact SHA for main integration.

## Ledger

- Base: 35580222aaf05608a90402d140948ad80198bb67; isolated worktree `/srv/tse-a4-contention-20261114`.
- Ruling: proceed with the explicitly authorized delegated implementation; no extra plan approval step.
- Pre-flight: Task2 consumes Task1's source/tests; native qualification is deliberately outside both tasks and remains with main.

- Task1: RED2807/2 erwartete Fehler; GREEN2807/0; zusätzliche Guards ASan/UBSan2811/0. Normaler Abschlusslauf und gesamte portable Suite laufen seriell.
- Ruling: laufende Versuche bleiben erhalten; nur neue Auswahl erhält die Präferenz, um keine unbelegten Flug-/Close-Combat-Abbrüche einzuführen. Dadurch bleibt simultane Doppelwahl vor Veröffentlichung der näheren Absicht offen.

- Task1: complete; final normal and ASan/UBSan bridge2811/2811 each. No native acceptance claimed.
- Task2: complete within delegated implementation scope;12/12 C++ executables,8/9 Python candidate scripts and344 tools tests pass. The ninth script `test_cecil_weapon_observer.py` fails compilation identically on base3558022; full suite is explicitly not green.
- Final self-review: private observation lifecycle, finite directed cost comparisons, live peer checks, connector fallback and unchanged replicated state reviewed. Independent integration review belongs to main; no additional subagent spawned.
- Ruling: leave the independently reproduced, unchanged Weaponobserver extraction failure visible for main rather than expanding this narrow AI behavior patch into unrelated Driver/observer harness repair. Cost: whole candidate suite remains FAIL until that separate issue is fixed.


## Task 3: Independent review corrections

**Files:** the same bridge header, bridge regressions and sanitized report.

- [x] Verify Driver1138 resets `bs_iTick` independently on join/rejoin; identify existing Engine107 `GetGameTime()` API at `Network.h:274` and existing Driver calls602/660.
- [x] RED: publish peer observations with local clocks.05/50 and common clock80; require both join directions, actual rejoin reset, common-clock staleness/rewind and owner-only progress.2824 checks/6 failures before correction.
- [x] GREEN: use shared `GetGameTime()` for observation freshness; retain stored owner-local time for owner deadline/progress.2824/2824.
- [x] RED: preserve reachable original target with Raybudget3/4 and9 blocked alternatives under the8-attempt cap.2833 checks/3 failures before fallback correction.
- [x] GREEN: prefer alternatives only with room for another connector and before the final bounded attempt; otherwise preserve original ranking.2833/2833.
- [x] Final normal/sanitized actual-body and relevant candidate suite, report update and commit.

- Final review finding: IMPORTANT, local slot clocks were compared across independent join/reset origins. Confirmed and corrected; no widened clock tolerance.
- Final review finding: IMPORTANT, preference could spend the sole remaining connector opportunity or all8 attempts on blocked alternatives. Confirmed and corrected without increasing either budget.
- Ruling: freshness uses the already-declared, already-used Engine107 network game clock; no new ABI field, clock offset estimate, tick equality or hidden cross-slot synchronization assumption. Native runtime validation remains NOT_TESTED.

- Task3: complete; clock RED2824/6→GREEN2824/0; fallback RED2833/3→GREEN2833/0. Final normal+ASan/UBSan2833/2833 each;12/12 C++ and8/9 Python candidate scripts. Sole unchanged Weaponobserver compile failure remains FAIL. No native test or runtime mutation performed.
