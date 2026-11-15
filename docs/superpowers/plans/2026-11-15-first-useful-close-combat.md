# First-useful close-combat policy implementation plan

> Execute inline with superpowers:executing-plans and test-driven-development; no delegation. Root's STATICONLY admission overrides every command below.

**Goal:** Resolve the narrow urgent first-useful Weapon/closeCombat disagreement without changing physics or deadlines.

**Architecture:** Fresh typed target/owned-mask candidate, unchanged legacy closeCombat/early ownership, and one late ordinary-move/unchanged-attempt gate. Actual production BotSupplyTick and Navigator are exercised through the existing SDK107 bridge. Driver stays byte-identical; its SafeMotion remains mandatory.

**Tech stack:** Existing Python-generated portable C++ harness, serial nice15 compiler/ASan only after Root admission; no Retail build.

**Spec:** `docs/superpowers/specs/2026-11-15-first-useful-close-combat-design.md`.

## Global constraints / review focus

- No new Engine/Ray/World/Clock/RNG calls, limits, mask, radius, target snapshot or input changes.
- Owned-but-unusable ranged weapons and unsafe Grenade cases must not become first-weapon authority.
- Invalid/stale target, air/special/locks and final physical veto remain responsible for rejection.
- GoalSince/fixed deadline/attempt identity survive close-threat crossings without renewal.
- Existing urgent Health and already-armed combat behavior remain; Source-reproduced inconsistency is not Native cause proof.

## Task1: real Source RED

- [x] Read actual UrgentItem, Driver arbitration, BotSupplyTick and old pause expectation.
- [x] Write `retainedFirstUsefulCloseCombatReproduction()` in the existing SDK bridge, call it from its actual main. Two owned masks3/7, no movement implementation copied.
- [x] After Root short-job admission, actual bridge serial nice15 RED4239/2; only the two new priority assertions fail. Preserve all pins/logs.
- [x] Report exact RED/mechanism to Root before production. Commit76b5fed preserves it.

## Task2: adversaries and minimal guard change

- [x] Add real BotSupplyTick owned/usable/empty-ammo/unsafe Grenade inventory masks; basic/melee/Armor/Ammo targets, invalid weapons context/unavailable target/expired deadline. Existing urgent/nonurgent Health and armed cases remain.
- [x] Preserve the complete existing Locks/special/teleporter/air/flight/floor/ray controls; add actual final SafeMotion wall veto and Navigator two-second stuck veto. No fallback calls or synthetic arrival stamps.
- [x] Naive direct closeCombat exception FAILED4253/26, preserve diff/receipt. Root accepted the refined early-candidate/late-proof design; actual legacy Flight/Earlyreturn guards restored. Three exact inverse regions restore Parent652bb66d; three Source mutations are rejected.
- [x] Explicitly update ordinary first-Weapon policy assertions only. Threshold loop supplies bounded synthetic progress; separate stationary case preserves stuck veto. Old provenance/pickup/timeout/blocked assertions remain.
- [x] Final normal4257/0 and exactly one ASan/UBSan4257/0, serial nice15, both Exit0. All existing24 diagnostic operation lanes remain in the actual suite. Static Engine member/global call sites unchanged; intended newly admitted planning is not global per-tick call-count equality.
- [x] Final Source/tests/report and private log/source receipt prepared for commits; all compiler processes ended. Root alone reviews/integrates/builds/runs, no Native efficacy proven.
