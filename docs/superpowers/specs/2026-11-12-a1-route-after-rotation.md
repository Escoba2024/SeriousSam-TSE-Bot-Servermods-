# A1: Original pickup and normal fire after proven rotation
Date: 2026-11-12
Owner: /root/review_names_transaction
Status: approved scope from Root; OFFLINE implementation; native execution belongs to Root.

## Goal and boundary
Prepare one disabled successor to A1 input diagnostics V3. Run the exact unchanged RD.run_calibration once, then the original S.Route pickup corridor for botA and one bounded normal 2-second fire hold. Completion records input delivery and observed weapon acquisition only. qualified, input_once_proven, actual_shot_proven, foreign_hit_proven and first_processed_state_proven remain false. No native launches, builds, hooks, memory writes or engine calls in this task.

## Actual baseline
Reviewed V3 package /srv/tse-a1-input-diagnostics-completion-v3-20261112; manifest 0f15a0cb6e82ebfe8694ddf8cc007c74a5318f42bae2fc984138ffb460029e26.
Actual native window a1-input-diagnostics-completion-v3-20261112-090901 completed limited rotation capture and all close/restore steps. The join mapping is vanilla=0, botA=1. All 35 valid server snapshots put botA (entity563) at [70.875,0.3763999938964844,63], yaw90.00000762939453, spawned_tick7.900012016296387, weapon2/owned3. This matches the existing Route guard; no name-based spawn inference is used.

## Chosen design
Add preparation_policy.py as a small pure orchestration layer. Keep rotation_diagnostics.py, shooter_policy.py and shooter-plan.json byte-identical. Never call legacy S.run_program, which would repeat the old unconfirmed calibration.
Read both role rows through the existing V3 paired-reader acquisition, including its exact transient consistency error allowlist, max8 acquisition attempts and fresh0.2-second requirement. A role frame binds the current pair to its exact server snapshot. Store returned frames before validation and preserve every failed/partial raw paired attempt as before.
Anchor server/Vanilla reader process identities and both server-observed player life/world keys before calibration. Require these identities, alive/initialized/connected state and monotonic native ticks throughout. Force a new requested read before every input and inside the last pre-emission callback; never select a favorable older sample and never retry input.
One shared 85-second policy clock begins at the controller's existing input-window start. Existing90-second input guard remains. Count all calibration, route and fire actions toward48. Check budget before and after observations, capture, input and terminal success. Route45, flight8 and selection3-second deadlines reject even a successful late observation. Route/flight budgets remain valid during captures and any pre-emission preparation.
Calibration retains double-reader acknowledgements, view-rest checks, exact12/-12 impulses, both normal forward holds and strict2-second ACK/settle guards. A new successful calibration is required on every run.
Route uses only botA forward controls from the original plan, acquires owned bit64 at the original destination and waits for current/wanted weapon7. Fresh pre-emission state must still support the pending corridor/weapon action. Finish with one normal2-second fire control hold; do not call it one bullet or a hit.
Original lifecycle, host budgets, namespaces, identities, modules, locks, normal close, complete log closure and file restoration remain unchanged.

## Alternatives and decision
Calling legacy S.run_program would repeat unconfirmed calibration and reset the85-second budget; rejected.
Adding Fire/Bullet/Damage instrumentation now would change executable code through hooks and add a separate instrumented/control validation problem; deferred. Passive fire_requested is intent, not actual shot proof.
The bounded orchestration layer preserves the natively successful diagnostic and the original route implementation while making the handoff explicit and testable.

## Acceptance
- Actual controller wiring calls the new orchestration, never legacy run_program.
- Actual RD and Route execute in deterministic tests; calibration failure causes no botA input.
- Fresh double-reader role frames reject cached timestamps, wrong process/life/world, reversed tick and missing/ambiguous roles.
- No input after deadline, input-count exhaustion or failed pre-emission guard.
- Successful but late route, flight, selection and terminal observations fail and retain evidence.
- One normal fire hold only after observed pickup/current/wanted7.
- Existing116 private regressions plus new targeted tests pass without native work or builds.
- Old V3 and original helper bytes remain unchanged. New manifest freezes all runtime, own and evidence files; gatefalse.
- Root independently reviews and runs a frozen copy; no A1 acceptance is claimed here.

## Concrete next A1 evidence step
After a successful normal route/control window, the next concrete step is normal movement/aiming toward the own second player from freshly observed real positions, then passive Original shot/Damage/lifecycle evidence. The existing two-player lifecycle/hook preparation is a candidate only, not native authorization. Any instrumented Original weapon/foreign-Damage window needs separate review with an identical uninstrumented control. Existing damage-dual-v2 code validates exact Original getters/Damage bytes, TLS/current tick, life/world and known foreign inflictor; only DMT_BULLET4 with the Original weapon path and actual health decrease could establish a normal hit. first_processed_state additionally needs a continuous same-life lifecycle witness from InitializePlayer completion through a defined first completed processing boundary. INITIALIZED/APPLIEDACTION flags and SpawnClock equality alone do not establish that ordinal. Existing lifecycle analysis states Deathmatch RespawnInPlace is not applicable. Ordinary death/Fire-respawn and actual unchanged spawn markers/LOS must be observed. No current preparation result upgrades those claims.
