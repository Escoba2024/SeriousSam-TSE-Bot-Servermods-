# Reacquire ownership mechanism reproduced; Skulls cause remains open

The normal portable SDK107 Bridge suite passed3541 checks with0 failures in one
7.004s invocation. Nine added assertions reproduce the ownership/contact mechanism
without changing production code or weakening the0.5 floor-normal guard. No ASan
rerun, Retail/DLL build, Wine, display, Frida or game process was started.

## Paired frozen-pose fixture

The existing `nativeContactFixture` supplies the same fixed supported pose, static
WorldBase reference, StandOn polygon, normal0.3976075, floor distance2.4784336 and
native stepDown1.5. The existing real-source `BotSupplyTick` and `BotCecilSafeMotion`
run once per tick through `groundProgressTick`. Ownership comes from the actual
Driver expression extracted as `bridgeDriverOwns`, not a copied hand-made predicate.

Each arm has70 actual proposals over ticks0.05..3.5s, identical pose/zero velocity,
hint and original hint deadline. The paired arms differ only in targetVisible.
The third arm changes only exact StandOn identity from the second arm. The ray
stub's world answers remain identical; executed query counts may differ with
branch selection and are not presented as an identical cast stream.

| Arm | Proposals | Actual Driver owners | Stalled calls | Escape-return calls | UnsupportedNormal calls | Final stationary time |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| Ordinary visible combat |70|0|0|0|70|0s|
| No visible target |70|70|30|12|40|3.45s|
| No visible target, wrong StandOn polygon |70|70|30|0|70|3.45s|

The countercase retains the true owner/stall denominator while removing all
escape approvals. It therefore exercises the current-contact guard rather than
assuming the low normal should pass. An escape-return means a source-approved
bounded action, **not** physical movement: these tests intentionally freeze pose.

The false-owner arm passes the same proposed vector to final Safety to isolate
the ownership contract. It does not recreate the Human combat vector or final
Retail action. Fresh timestamps, actual unchanged life/world and deterministic
casts are source fixtures, not newly measured native game states.

## Exact source interpretation

The production source matches the actual026 overlay and manifest:

- `BotSupplyNative.h`: `92712d4e626fdc3a4b027aa964226b4dca5a3b89684148a36df1826ee9c6b635`.
- `cecil_motion.h`: `a32870d3a4d47c95f927e25d1b3bb881de8297f9245dedb632c56069cda88e09`.
- `BotDriver.cpp`: `9e8a1ed5c058c4bd0a45c99b07ddedf29580bca38940c4dbb27403c05816b153`.

Reacquire creates its proposal at `BotSupplyNative.h:1153–1163`. Driver1451–1457
can retain ordinary visible combat instead; Driver1550 passes the actual owner
to SafeMotion. `groundObserved`2254 becomes false for a rejected Nav owner;
`CecilGroundProgress::Update`21–22 then resets its position timer. This is an
existing intentional owner contract, now exercised with the actual arbitration
expression. If Nav owns, position is observed at2263–2284 before final casts:
later vetos do not generally erase that observation. Wall/UnsupportedNormal does
not automatically reject the hint; the narrow target-rejection rule2413–2437
requires a definite aligned stationary NoFloor failure. Existing six-second
hint/backoff deadlines remain unchanged.

The full native Skulls026 proposal→arbitration→cast ownership/contact chain is
still missing. These fixtures do not determine which branch caused the24 proposals
or the16.546s stationary episode. No historical result or cause is relabeled.

## Original Cecil versus current combat recovery

Local primary source `/srv/tse-cecilbot-reference-20261020` is exactly
`953b477e53fdc5a5d84c8ae8d759c84fdf6c973c`. In `BotStructure.cpp:323–330`,
actual displacement>2m refreshes position time; `BotThinking` calls pathfinding485
and then movement492. `BotMovement.cpp:395–433` includes enemy strafing, while
the same movement function561–577 uses NoPosChange/static-obstacle avoidance
and can jump for a visible player. It has no separate Supply-owner gate.
However `NoPosChange`25–30 itself refreshes its timer after>1s, and pathfinding129
can consume that check first. This is source comparison, not identical timing,
physics or complete Cecil parity.

Current `bot_human.h:523–550` chooses movement from health, target distance and
tick-based strafe variation; it has no displacement-over-time stall detector.
Driver1471 enables legacy `ObstacleRecovery` only when SupplyNavigation is off;
Driver1503 otherwise resets it. With SupplyNavigation on and Human combat owning,
the ground watchdog cannot accumulate time as demonstrated above. SafeMotion's
ordinary collision escape remains available; this is a missing **position-time
combat watchdog**, not absence of every collision response.

A future design could either separately observe combat-owned actual position and
test bounded combat-safe alternatives, or establish whether accepted Nav stalls
fail the already existing exact-contact guards. Neither option may lend offgraph
Nav authority to Human motion, loosen the normal cutoff or infer physical success
from a returned proposal. Before choosing, the particular episode still needs
its actual ownership/contact boundaries; no product fix is implemented here.

Root's narrower design proposal is legitimate as a separate missing combat-recovery
feature, with an important distinction: the real SafeMotion caller is inside
`automatic && bot_bSupplyNavigation` (`BotDriver.cpp:1530`). Here rejected Supply
ownership means this bot's own automatic combat policy retained movement, not a
foreign human's input. A distinct `combatRecoveryRequested` may therefore describe
`automatic && humanMode && targetVisible && !supplyActive` plus an actual nonneutral
movement request, while `useReacquire` remains false. The existing fresh ground
observation/movement/support stamps were produced earlier in the same SupplyTick;
they must still pass identical recoveryContext, entity/life/world, clocks, budget,
gravity, native contact and physical guards. The countercase demonstrates why a
false contact identity must continue to veto recovery.

Such a request must not acquire a NAV goal/hint, mutate hint Tried/backoff or grant
FlightAccepted; only a real observed stall/valid active escape could gain the
existing0.3 cap and freshly checked bounded movement. Neutral/manual/nonautomatic,
nonvisible, unsupported or stale contexts remain excluded. These are design
constraints, not tests of an implemented new boolean. The reproducer supports the
feature's motivation; it does not qualify that future implementation or establish
the cause of the026 native episode. No production change is included.

## Reproduction and private evidence

One normal invocation, preserving all old checks:

```sh
python3 -B poc/candidates/redstation-supply-20261107/test_cecil_native_bridge.py --support-dir poc/candidates/redstation-supply-20261107 --sdk-player /srv/tse-sdk-20261021/Sources/EntitiesMP/Player.es
```

Private0700 directory `/srv/tse-reacquire-ownership-reproducer-evidence-20261115`,
normal output `bridge-once-normal.log`0600, SHA256
`614a96c4411a6c151d6c5281297acd26e33ba22d780d4396cb38bce02755a480`.
Its receipt pins this test and the original/adapter sources. No repeated parent
runs or sanitizer runs were used. Root source review/integration remains separate.
