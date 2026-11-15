# Item-transit history custody: passive Source implementation plan

> **For agentic workers:** Use superpowers:executing-plans and TDD, inline/no delegation. Root alone builds/freezes/runs. Current033 exact header49229af92892fe030f74b7a09815647c90ec0572f4a1065c1ed20fc4f0590b3d is immutable parent.

**Goal:** Explain an observed `revisited_edges` or zero-marker result using bounded DIAG1 ARM/DISARM/END custody, without changing any eligibility, timer, memory of progress or motion.

**Architecture:** Separate diagnostic pre-admission cache plus diagnostic-only flags in existing history, fixed stack formatter and new process-local1024row counter (no reset/eviction). At most one ARM/DISARM/END per admitted history domain. Existing local scalars and cached domain only; no additional Engine/Ray/Clock/RNG/allocation. Whole-header inverse returns exact033; full ordered operation lanes compare parent0=current0 and parent1=current1, preserving existing DIAG0/1 GetGameTime differences.

**Scope:** BotSupplyNative.h, actual SDK bridge fixture, one new narrow source-inverse/operational test+fixture, own plan/report/claim. No Driver/A1/Root/frozen/Nav/raw/ABI or population changes. Build034 closure/pins come from Root later. Existing033 package/source remains a historical candidate, never silently modified.

## Exact contract accepted by Root

- ARM only after the first actual valid history entry. Never emit END for an empty/unadmitted history or every generic ClearGoal.
- Exact Observe returns: gravity_changed/time_back/gap/edge_metadata_changed/history_full. Disarm carries first reason; restoration never re-arms identical domain.
- Existing ClearItemTransit callsites carry literal classifications: eligibility_false, invalid_final, owner_lost, air_owner, flight_finish. No re-evaluation of the engine shortcircuit; unobserved subreasons remain UNKNOWN.
- ClearGoal emits END before deleting an admitted domain; Observe domain replacement ends the preceding admitted one. No deferred pending event is silently overwritten by reset.
- If a caller has no current existing clock, row explicitly `event_time_known=0 time=0`; cached `last` remains separately labelled Source clock. Never call GetGameTime/Timer/GetWorld to fill telemetry. Already available Observe now may be marked known.
- Fields: event/reason/coverage/globalserial, cached actor/generation/world/map/item/goal/attempt/deadline, edge/count/last/since, event_time_known/time. No PID/name raw identities in public fixtures; native Actor/Life via existing private registry/Spawn/WPO and epoch, no Tick/20 clock fusion.
- DIAG0 no rows; diagnostic flags/counter never feed decisions. Byte-identical old state/action/query behavior for each lane; diagnostics-only new fields excluded from gameplay-state equality.
- New1024rows/process total, never map/life-reset. Reserve last row CAP_REACHED with coverage=incomplete; afterwards no rows and post-audit cannot PASS complete custody. Fixed <1024bytes/row within existing2048B BotLog buffer; overflow/format failure explicit incomplete, never truncated normal row. This is a NEW total-row bound, not a falsely claimed pre-existing limit.

## TDD and verification

- [x] Write actual SDK behavior assertions using current033 Observe/Disarm/ClearGoal: missing ARM/DISARM/END and cap are real behavior RED, not new-symbol/import failures. Preserve Parent production unchanged until observed.
- [x] Minimal logging-only Header delta; exact whole inverse and mutation-rejection test for an original eligibility guard.
- [x] Adversaries: no empty END, repeated clear/disarm, first reason retained, unknown caller time, domain replacement, lifetime1024cap/no reset, row-width extreme inputs; no extra queries/allocations in actual logger; same history gameplayvalues DIAG0/1.
- [x] Announce/run normal SDK once at finished code, then one sanitizerSDK serial nice15. Reuse existing operational_source for24 full parent/current ordered calls/state/action/RNG/budget lanes; no filtering of the old differences scenarios2/4/11.
- [ ] Commit source/tests/receipt/report; Root independent review/build034 and targeted300 disabled condition later. Zero-marker remains unexercised, no automatic repeat/A4 pass.

Root F3 closed/restored17:51:13; offline tests authorized. Stop all jobs for next Root Native signal.

## Latest Root boundary: pre-admission custody

Ruling: A separate pure diagnostic cache records at most one UNADMITTED row per existing SSupplyState identity/goal/start/deadline domain, even before gameplay history can be admitted. ClearItemTransit does not erase this diagnostic cache. No early gameplay binding and no extra player dereference: accepted=false/player=NULL remains safe; world/map/actor not already observed are UNKNOWN. Later actual history admission still gets one ARM, first actual disarm one DISARM, and admitted history ending one END. Thus the newly authorized pre-admission row makes at most four rows only when all four phases occur; the global process cap remains1024. No END for unadmitted cache alone. ClearGoal or a genuinely new diagnostic domain resets the pre-admission cache; gameplay-history reset alone cannot create a fresh pre-admission allowance.

Observed RED checkpoint67d5b53:4220 checks/4 failures (missing ARM/DISARM/END/cap), unchanged033 Header. Add actual NULL/shortcircuit→UNADMITTED→laterARM adversary before production.

## Implementation ledger

- RED67d5b53: actual unchanged033 Observe/Disarm/ClearGoal emits none of the newly required custody,4220/4. Last NULL pre-admission RED8e37185:4221/5. Final fixture explicitly sets mappedWeaponGoal and Weapon kind; this corrects a previously omitted fixture qualification, without changing the old NULL shortcircuit.
- Initial passive implementation actual SDK4221/0. New adversaries exercise all five existing Observe rejection branches, no-END for unadmitted-only ClearGoal, actual domain replacement, extreme numeric formatting, DIAG0 silence, and global cap persistence.
- Root R1 review reproduced4231/1: old admitted history count could suppress an UNADMITTED row for a new directly assigned SSupplyState goal/attempt. Pure diagnostic ContainsAttempt now compares actor/generation/item/goal/start/deadline; gameplay history, decisions and prior first disarm remain untouched. Old admitted item and new unadmitted item are separately recorded. Exact pre-fix Header and failing log retained privately.
- Final normal SDK4231/0. Three Source tests PASS9.491s: whole033 inverse, real guard mutation rejection, fixed format conservative701bytes+NUL, exact24 full parent/current operation/state/action/RNG/budget lanes. Historical Parent DIAG0/1 GetGameTime differences in scenarios2/4/11 remain unfiltered.
- First lane invocation had2/3PASS: its otherwise passing operation comparison was followed by a stale historical031 Driverpin assertion. Actual unchanged033 Driver1c081af0 was verified against committed RED source and the assertion corrected; this was a test-provenance error, not a production failure.
- Single final ASan/UBSan run completed4231/0, Exit0, no sanitizer diagnostics; actual log checked. No Root/native/Retail/DLL action performed.
