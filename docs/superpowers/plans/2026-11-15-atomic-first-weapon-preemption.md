# Atomic first-weapon replacement implementation plan

> **For agentic workers:** REQUIRED SUB-SKILL: use superpowers:executing-plans inline, no delegation. Tasks use actual failing SDK bodies before production.

**Goal:** Permit only a fully validated first Useful-weapon attempt to replace a held ordinary nonurgent Health/Armor item.

**Architecture:** Keep current ChooseGoal call order and all ordinary/mapped selectors. Add narrow held-item eligibility at existing mapped admission; reuse its entire bounded candidate+connector path and its existing success-only ClearGoal commit. A failed attempt leaves old goal identity/deadline/navigation intact.

**Tech Stack:** C++14, real extracted BotSupplyNative bodies/SDK107 bridge, Python harness, g++ normal+ASan/UBSan serial nice15.

**Spec:** `docs/superpowers/specs/2026-11-15-atomic-first-weapon-preemption.md`.

## Constraints and review focus

No new clock/RNG/queryloop; no new radius/floor/locks/deadline permissions. Preserve urgent Health, close combat, usable weapon, inactive/invalid context, navigation special edge/interaction/flight ownership. Failed candidate validation must retain original goal and navigator reset serial. Old selector behavior remains for no held goal. Native unavailable receiver/alternate pool remains UNKNOWN.

### Task1: actual Source RED and bounded guard matrix

- [ ] Add fixtures to actual SDK bridge: held nonurgent Health and Armor with owned/usable3 and fresh reachable mapped WeaponID4 outside ordinary16m radius. Call actual ChooseGoal; expected mapped weapon replaces only after connector success. Current Source must fail these two assertions while a no-held-item control succeeds.
- [ ] Add actual-body adversaries: urgent Health; close enemy; usable Useful weapon; cooldown; stale/dead/mismatched actor; disabled search; invalid time; no alternative; unreachable/locked/blocked connector; exhausted budget; important/follow/interaction/flight/special traversal. Assert unchanged old identity/attempt/deadline/reset serial on failure; actual ray budgets bounded. No prematurely set anchor to force outcome.
- [ ] Run actual SDK suite serial nice15, capture RED status+source hashes. If no behavioral RED, stop and report.

### Task2: minimal atomic admission change

- [ ] Add narrowly guarded side-item eligibility at mapped entry using current immutable input and one live old-item read; keep existing candidate body and success-only commit. No BotDriver/refactor/policy widening.
- [ ] Run normal suite; inspect any failures before changing tests. Check ordinary no-goal behavior/urgent-health/ray/cooldown/source-body guards. Run one ASan/UBSan suite after normal GREEN.
- [ ] Record exact diffs/source hashes/RED+GREEN+ASan logs and fixture limits; public sanitized report/commit. Root independently reviews/integrates/builds and decides new native candidate. No own runtime.

Ledger: Task1 SourceRED4052/2;32 zusätzlicheAdversaries4116/2 vorProduktion. Task2 Minimalhelper+AdmissionGREEN4141/0, echterSDK107/Windowsfar, ASan+UBSan4141/0 Exit0. Root's zusätzlicherMarkerRuling aufgenommen: Altgoal-Ende nach Ersatzvalidierung/vorClearGoal, nie beiFehler; echter4175/2RED→4175/0GREEN. Finalmarkerist ausschließlich vorhandeneBotLog-Callsite; ASan-PräMarker getrennt belegt, kein unnötigerzweiterASan unterStorageknappheit. GanzeHeaderinverse exakt aufParent0e7ee9d1 einschließlich einzigemMarker; alleJobsbeendet. KeineNativequalifikation. PublicReport undprivatefinalReceipt enthalten Grenz-/Source-/Logpins. Rootreview/Integration/Build/NativebleibenRoot.
