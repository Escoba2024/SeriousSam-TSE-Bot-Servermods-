# Item loss during a committed special traversal

Status: portable regression fixed; native qualification remains open.

## Retained native evidence

Private native004 diagnostic trial `arena004-diag1-trial-1-202356`, botB,
local slot 1, generation 6: the first ranged weapon was acquired at tick 841,
41.65 seconds after spawn tick 8. This is a failed rapid-acquisition sample,
not a pass inferred from score.

The retained log establishes the sequence:

- Tick 100: the original jump route 84 → 86 has advanced to 86 → 176 toward
  Laser item 267. The player is in FALL, the current directed edge is accepted,
  and the existing item deadline is 20.400 seconds. Its final `floor=2` result
  is a safety-approved alternative, not acceptance of the original direction.
- Tick 101: item 267 becomes unavailable with render type 5. Another local
  player acquires that weapon at the same tick. Existing `ClearGoal()` resets
  the navigator immediately.
- Subsequent target changes leave slot 1 acquiring node 86 with no committed
  source. Ticks roughly 140–660 repeat the vertical jump-pad cycle with little
  horizontal movement; a later route finally escapes it.

This is a route-lifecycle defect. The current 86 → 176 edge has ordinary flags;
FALL or those flags alone cannot establish prior jump provenance. No item
visibility filter or pickup-mask rule is relaxed. Raw logs, session data and
player identifiers remain private.

## Change

`BotSupplyNative.h` records passive provenance on an existing committed
JUMP/TELEPORT edge while falling. It becomes usable only after the unchanged
final movement safety function accepts the route action, an intentional
neutral action, or an existing safety-approved alternative on that exact current
edge. Alternative success does not create provenance on an unrelated route. A reached-hop transition can carry that
provenance onto the route's ordinary successor. A fresh ordinary airborne
route does not create it.

If the current item becomes unreadable during that proven traversal, item
ownership ends once. The navigator may finish only its exact current directed
edge. Selection, follow replacement and important-node interaction are deferred.
The original attempt/deadline, world, map serial, entity, generation and gravity
remain pinned. The continuation ends neutrally at the original arrival radius,
grounding, deadline, stale observation, changed identity/edge or lock, or failure
to accept the final route movement or existing safe alternative. The next normal tick can select again.
Existing stuck/hold bounds and movement safety remain in force. No support,
teleport, movement, geometry, or entity-write authority is added.

`CecilFlightFinish` emits bounded begin/end lifecycle lines for native diagnosis.
The pure provenance checks use no rays, entity lookups, RNG or allocations.

## Verification

The behavioral regression executes actual `BotSupplyTick` and
`BotCecilSafeMotion` from the header. The pre-fix run failed the retained-edge
and original-deadline assertions. The ordinary airborne counterexample passed. A second RED/GREEN regression
reproduces the native `floor=2` alternative immediately before loss and the
existing held alternative: both initially failed the flight-retention assertion.
Failed/budget-deferred alternatives and lost NAV ownership do not renew it.
The final bridge run has **1513 checks, zero failures**. The suite covers arrival,
original deadline expiry, ordinary loss, map/world/entity/generation/gravity and
attempt changes, stale/backward time, death/grounding, missing/reset/locked
edges, movement ownership, failed final safety and observation cost.

Commands:

```sh
python3 poc/candidates/redstation-supply-20261107/test_cecil_native_bridge.py
python3 poc/candidates/redstation-supply-20261107/test_cecil_native_bridge.py --sanitize --sdk-player /srv/tse-sdk-20261021/Sources/EntitiesMP/Player.es
python3 poc/candidates/redstation-supply-20261107/test_cecil_items_native.py
python3 poc/candidates/redstation-supply-20261107/test_cecil_action_native.py --sdk-player /srv/tse-sdk-20261021/Sources/EntitiesMP/Player.es
```

SDK-backed ASan/UBSan bridge: 1513 checks, zero failures. Native item adapter and
actual Driver action-contract tests pass. These are portable/SDK contract
results, not Retail ABI, gameplay, sync or rendering qualification.

## Required native discriminator

Build a new isolated candidate. Repeat the frozen early-pause crossover harness
with physically exchanged DLL/policy roles and verified identical initial
positions and owned masks, plus zero within-leg spawn-clock spread. Absolute
clock offsets between legs remain separately reported; no full replay identity is claimed. Retain the old failed native004 outcome.
Correlate item-unavailable → flight-begin → retained source/hop → arrival or
bounded context end, then actual inventory acquisition per life (including
censored/failed lives). Confirm no repeated source reacquisition bounce and
no regression in ordinary item, patrol, locks, jump/teleport safety or sync.
Three final-candidate comparisons and the remaining map gates are still open.
