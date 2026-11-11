# Supply acquisition follow-up and passive diagnostics

The retained private build003 observation is `/srv/tse-milestone-a-evidence-20261111/arena003-trial-1-195642`. Its result records 240.02098 seconds, zero bad-sync/disconnect matches and completed normal cleanup. Candidate DLL SHA256 is `0ae31bb552ea4d97bd6c6f9d74ea90c84dd4b80b06f84e2c965d24936e5ee9c4`. These are limited session observations, not rapid weapon acquisition acceptance.

Useful ranged acquisition uses gained ownership bits masked with `0x3df8`: IDs 4–14 excluding melee 10. Double Colt does not qualify. New botB has 17 observed spawn lives, 12 lives with a useful ownership gain and five completed lives dying without one. Four final lives are censored by the end of observation; all four already obtained a useful weapon. Initial local lives are: local0 gain after 7.4 seconds; local1 death after 13.7 seconds without gain; local2 death after 73.1 seconds without gain; local3 gain after 10.05 seconds. The Double Colt gain in local2's first life does not satisfy the criterion. The approximately 63-second successful gains belong to old botA; new local2 generation9 takes 51.7 seconds.

There is specific progress in diagnosis, but no demonstrated availability-based behavior fix yet. New local2's Laser goal ends unavailable at ticks164 and921, exactly when new local0 obtains that Laser; at164 local1 also loses the same goal. The pickup record has `goal_picked=0`, while the external query reports weapons-stay enabled. Existing `unavailable` text conflates hidden/deleted/render-type rejection, per-player picked mask, invalid data and typed need. Shared visual hiding, normal item rules and field interpretation are hypotheses requiring actual native values; the coincidence alone does not distinguish them.

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
