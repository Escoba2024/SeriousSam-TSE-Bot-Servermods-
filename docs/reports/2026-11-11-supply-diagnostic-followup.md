# Supply acquisition follow-up and passive diagnostics

The retained private build003 observation is `/srv/tse-milestone-a-evidence-20261111/arena003-trial-1-195642`. Its result records 240.02098 seconds, zero bad-sync/disconnect matches and completed normal cleanup. Candidate DLL SHA256 is `0ae31bb552ea4d97bd6c6f9d74ea90c84dd4b80b06f84e2c965d24936e5ee9c4`. These are limited session observations, not rapid weapon acquisition acceptance.

Useful ranged acquisition uses gained ownership bits masked with `0x3df8`: IDs 4–14 excluding melee 10. Double Colt does not qualify. New botB has 17 observed spawn lives, 12 lives with a useful ownership gain and five completed lives dying without one. Four final lives are censored by the end of observation; all four already obtained a useful weapon. Initial local lives are: local0 gain after 7.4 seconds; local1 death after 13.7 seconds without gain; local2 death after 73.1 seconds without gain; local3 gain after 10.05 seconds. The Double Colt gain in local2's first life does not satisfy the criterion. The approximately 63-second successful gains belong to old botA; new local2 generation9 takes 51.7 seconds.

There is specific progress in diagnosis, but no demonstrated availability-based behavior fix yet. New local2's Laser goal ends unavailable at ticks164 and921, exactly when new local0 obtains that Laser; at164 local1 also loses the same goal. The pickup record has `goal_picked=0`, while the external query emits raw `weaponsstay=1`; this must not be interpreted as enabled (see native004 correction below). Existing `unavailable` text conflates hidden/deleted/render-type rejection, per-player picked mask, invalid data and typed need. Shared visual hiding, normal item rules and field interpretation are hypotheses requiring actual native values; the coincidence alone does not distinguish them.

Local2 generation9 spends 9.7 seconds on a contested Flamer, 31.5 seconds on a Minigun attempt ending at its original deadline, then 10.5 seconds reaching a Flamer. The exact original NAV CRC is `e4571656`. On the Minigun attempt, source12 to terminal34 carries special flags42. At ticks3340–3520 its target distance decreases from roughly174 to69 metres, with absent support in every sampled state. It subsequently acquires another route and continues travelling. This is not evidence for a stationary ordinary-edge cycle, nor authority to cancel a special action in midair. No `CecilItemTransitEnd` occurs. Available alternative candidate costs were not retained, so no ground-route preference or timeout change is justified by these logs alone.

## Diagnostic-only candidate

The implementation reuses existing `bot_bDiagnostics`, default false. It changes no goal admission, ranking, retention, physical query, action, deadline, simulation RNG or replicated state. Additional per-bot timestamps control only logging and survive ClearGoal to prevent repeated selection spam; full Reset clears them. Native item filtering exposes an optional reason from its actual rejection branch. Its return values and snapshot fields remain unchanged. The selected-path accessor is const, bounds checked and returns -1 for absent/out-of-range parents.

When enabled in an owned isolated copy:

- `CecilSupplyDiagCandidate`: at most16 eligible candidate rows in the first selection scan, recording entity/weapon/anchor, path distance, item connector, vertical penalty input, total rank and first special path endpoint pair. `special_flags` is the union of those endpoints, not an effective action flag. No alternative search is run.
- `CecilSupplyDiagSelection`: at most8 existing connector attempts, with actual eligible count, emitted count, chosen entity/weapon/anchor, physical cost/rank and selected special path. `emitted=0` on retries means candidate rows were intentionally not repeated. Counts expose truncation; never assume omitted candidates are unavailable.
- `CecilSupplyDiagUnavailable`: exact item-read rejection or `typed_need`, raw flags/render, player index and picked mask/bit, weapon pickup-once/dropped/respawn/type, session weapons-stay, actual current weapon, ownership/usable masks and original goal timing. Invalid/nonweapon/deleted typed metadata has `weapon_metadata_valid=0` and `picked_for_player=-1`; its unsigned `picked_mask=0` is only a placeholder and must not be interpreted without the validity field. Real weapon metadata has `weapon_metadata_valid=1`.
- `CecilSupplyDiagTerminal`: current source/hop/anchor flags, requested ownership/fresh-point context, movement state, support entity/render/physics, target distance/height, actual velocity/gravity, acquisition time and original goal/use timing. These observations do not grant support or movement permission.

Each category has a separate one-second cooldown per local bot: at most16 candidate +8 selection +1 unavailable +1 terminal rows per diagnostic batch interval, excluding existing logging. Selected-path inspection has at most4096 parent steps per emitted candidate/selection. It performs no new ray casts, entity lookups, search, simulation RNG calls or heap allocation; existing console writing still has overhead that must be measured natively.

## Verification and next measurement

RED before implementation: two bridge assertions failed because opt-in candidate output did not exist; optional item-reason tests failed to compile against the old signature. A subsequent path test caught incorrect special-endpoint reporting and was corrected before verification. Portable tests compare enabled/disabled commands, goal/deadline, RNG, cast and world-lookup counts, retained close-combat goals, final safety actions and actual unavailable endings. They also cover row bounds, cooldown persistence, lifecycle reset, invalid clocks, exact per-player mask interpretation, selected parent bounds and first special endpoints.

Verification completed: 1402 real bridge checks passed normally and with SDK107 ASan/UBSan; the native item adapter and extracted Driver action checks passed with sanitizers; all183 tool tests passed. The compiler emitted only its existing large-function variable-tracking fallback note. These are portable results, not native acceptance. Review follow-up adds four assertions for metadata validity and missing/deleted/nonweapon cases: RED 4 failures, then 1406 checks passing; absent metadata is never reported as a known false pickup bit.

Run the real bridge and adapter tests:

```sh
python3 poc/candidates/redstation-supply-20261107/test_cecil_native_bridge.py --sanitize --sdk-player /srv/tse-sdk-20261021/Sources/EntitiesMP/Player.es
python3 poc/candidates/redstation-supply-20261107/test_cecil_items_native.py
python3 poc/candidates/redstation-supply-20261107/test_cecil_action_native.py --sdk-player /srv/tse-sdk-20261021/Sources/EntitiesMP/Player.es
python3 -m unittest discover -s tools
```

The next isolated native run must record same-binary diagnostic-off/on controls and overhead, capture one actual sibling pickup cancellation with flags/render/index/mask, and capture candidate choices before a failed special attempt. A candidate omitted by truncation remains unknown. No native instrumentation was enabled by this change; runtime and protected installations remain parent-owned. A3 acquisition, special traversal, the bounded-failure pickup/attack response and full native acceptance remain open.


## Native004 correction: actual unavailable state

The isolated same-DLL diagnostic run observed Laser267 globally render5 (`RT_EDITORMODEL`), flags65600, Respawn1, PickupOnce0, Dropped0, pickedmask0, and distinct global local-bot indices5/6/7/8. Actual session WeaponsStay0. This explains simultaneous sibling cancellation as ordinary global item cooldown, not per-player-mask corruption. Original SDK107 `SessionProperties.cpp:341` formats GameSpy `weaponsstay` as `sp_bWeaponsStay?0:1`; raw query1 was previously misread as true. Query names and source expressions are not interchangeable. No weapon rule is changed.

Independent read-only Retail countercheck binds original Engine b79bf8bb3927fe4f8f252e141d721ae5c738df02218f0ecc12da5c1afbcb534f and EntitiesMP7f595f2a7fc96a978b3467983e8f17c70d827f17a5f4ee887f9c7a1f20b1d350. Engine SwitchToEditorModel0x601bf340 writes render3→5/9→10; SwitchToModel0x601bf310 restores3/9. GetMyPlayerIndex0x60226350 normalizes predictors and searches global playerentities; Entities MarkPickedBy0x603d5750 imports that function and reads/ORs mask at+0x3a0. ItemReceived0x603d5f50 imports SwitchToEditorModel; continuation0x603d609e restores model. These are specific static disassembly checks, not a full ABI equivalence certificate or runtime hook. No evidence justifies removing hidden/render filters.

A separate review finds an8s first-cohort headstart in current harness. Reversing joinorder alone has not proven exchanged equal positions; current windows remain diagnostic. A normal-engine start barrier and actual starting-state evidence are required before accepting the requested comparisons.


### Full004-on lifecycle denominator and separate movement defect

All10newbotlives:8 useful ranged gains,1 completed death without gain(13.70s),1 right-censored without gain(≥32.50s). Gained latencies30.60,2.35,7.60,41.65,2.35,4.60,14.95,16.95s. No successful-life-only denominator or DoubleColt credit. Worst41.65s life has39/42 pre-gain sampled states NAV-owned/no visible target and3 combat-owned: close-combat yielding is not the main delay. Source86→hop176 committed at tick100; Laser267 globally unavailable101 clears navigator; Sniper401 selected130, acquisition approach node86 at140 has no source context. Ticks140–660 repeatedly cross jump-pad column, original server horizontally bounded about4.84×2.36units while height1.88–70.99. This is a separate real airborne navigation loss/loop. It does not justify cancelling physical safety or inventing floor support. A bounded preservation/recovery fix needs regression and fresh native evidence.

Censored local2/gen9: genuine special traversal and item contention; diagnostics show0eligible alternatives twice then Grenade544 sole eligible, terminal8.96units away and still progressing. No superior omitted candidate is established. Of25render5Unavailable rows,17 have confirmed weapon metadata(allactualWeaponsStay0/Respawn1/mask0);8 are nonweapon items with sentinel metadata, not respawn-confirmed weapons.
