# Arena trial 1: native MITTEL comparison, limited result

This independent review inspected completed private evidence
`arena-trial-1-193924`. It changed no runtime or source. The trial ran on isolated
Wine resources on Red Station with four old048 bots, four build002 MITTEL bots,
the original server GameMP and one unmodified Retail client. Old bots joined
first. Different spawn positions, join order and interactions prevent a causal
performance estimate from this trial alone. Three planned trials and subsequent
regressions remain separate requirements. This report grants no fleet approval.

## Candidate identity and observation window

| Role | GameMP SHA256 |
| --- | --- |
| Original server / Retail client | `1c41da35b3fc47378c407b770e1bd1dcc2b7e6bf676c140586bc6035461d4208` |
| Old048 cohort, botA | `ec820d0461313c41fec2b477f57109310d3c71a77b4423955ac69f3807566530` |
| Build002 MITTEL cohort, botB | `50b132c0d83d209b399c7178bcb41dc16c0ee1ffe7c28652cecbd69a07baafd5` |

The result records 240.085903 seconds, 100/100 queries with nine players and no
observed SYNCBAD or sync disconnect in the completed window for server, either
bot process or Retail client. Cleanup records all four owned processes closed.
The 1,561 session snapshots report spawn protection zero in all four processes;
the server game clock runs from 31.649803 to 271.607208 seconds. Population and
sampled session consistency are limited native observations, not a long-term sync
qualification or proof of every intervening simulation state.

The score changes in the query window are:

| Cohort | Local 0 | Local 1 | Local 2 | Local 3 | Total |
| --- | ---: | ---: | ---: | ---: | ---: |
| Old048 | +4 | +1 | +1 | +1 | +7 |
| Build002 MITTEL | +8 | +2 | +7 | +8 | +25 |

The Retail client's score remains zero. Score is the server's observable result;
it does not measure hit rate, damage per shot or human difficulty. The client
control log records ordinary input attempts; no game-state alteration is inferred.

## Acquisition: retain failed and censored lives

The following uses actual `CecilSpawn`, `CecilPickup` and `CecilDeath` records in
the complete retained cohort logs. A collected ranged weapon means a newly owned
weapon in IDs 4–14, excluding chainsaw. This is an ownership observation, not an
independent ammo/usability measurement for every pickup. Time is calculated as
local tick difference multiplied by 0.05 seconds. These are policy-clock
latencies: startup can include ticks while
native simulation is waiting, so they are not independently precise native-spawn
ages like the memory-derived example below. Full bot logs include startup and cleanup
tails, so these denominators differ from the exact 240-second query window.

Each entry below represents one consecutive life. A number is the first ranged
pickup latency; `D` means death without such a pickup, followed by life duration;
`C` means no pickup by the last state sample, followed by observed duration. A
successful pickup remains counted when its life is still active at log end.

| Cohort / local | Consecutive life outcomes, seconds |
| --- | --- |
| Old / 0 | 11.45; D8.20; 9.70; 3.80; 3.80; 13.45 |
| Old / 1 | 3.95; 30.60; D5.35; D19.85; 23.15; 16.60 |
| Old / 2 | D37.95; 6.00; D31.90; D0.30; D33.10; 10.70; D25.40; C3.70 |
| Old / 3 | 2.40; 46.70; 3.55; 19.25 |
| New / 0 | 53.55; 2.45 |
| New / 1 | D64.30; 53.15; 13.60 |
| New / 2 | 12.75; 7.40; D42.55; 15.45 |
| New / 3 | 24.15; 36.80; 5.10; 8.80 |

Old: 24 lives, 15 successful pickups, eight deaths without pickup, one remaining
censored acquisition. New: 13 lives, 11 successful pickups, two deaths without
pickup. A success-only average would hide the failed lives and is not used.
The new first-life 53.55-second pickup and 64.30-second failure prevent claiming
that this candidate satisfies the acquisition improvement requirement.

The first new local0 route selected weapon267 at tick35, lost it at195, selected
it again at219 and lost it at242. Further mapped targets ended as unavailable at
520 and877, before the eventual weapon267 pickup at1106. New local1 likewise
lost multiple mapped targets and died at1321 without a ranged pickup.

During these initial acquisition intervals, the one-second live state samples
show navigation owning 48/54 actions for new local0 and 61/65 for new local1;
visible combat owns the remaining six/four. Fire-intent totals reach zero/two.
This does not show persistent denial of navigation by Driver arbitration. The
actual retained mapped-goal test in `BotSupplyNative.h` treats a temporarily
nearby opponent as item unavailability, clearing the committed route, while a
later branch already supports temporary combat ownership without discarding the
attempt. The navigation agent owns the focused retention fix and its tests.
These observations do not justify changing the 18-unit Colt limit or aim values.

## Fire intent versus actual weapon execution

At the final sampled state, the fire-action counters total 201 old and 783 new.
`BotDriver.cpp` increments this counter when it emits a non-respawn Fire action;
the field named `shots` is therefore not a bullet, hit or damage counter. The
slightly unequal full log spans also prevent treating this as a window-normalized
rate. All four new bots have sampled ranged-weapon firing intents.

Native `CecilWeaponObserve` state stacks additionally contain real weapon
execution families. The Engine107 generated state table maps, among others:

| Native state | Meaning | Cohort observed |
| --- | --- | --- |
| `0192003c` | FireColt_01 | Old and new |
| `01920061` | FireSniper_01 | Old |
| `01920053`, `01920055` | FireDoubleShotgun_01 / _03 | New |
| `0192004c` | FireSingleShotgun_01 | New |
| `019200ac` | FireLaser_01 | New |
| `01920083`, `01920087`, `0192008b` | FireGrenadeLauncher family | New |
| `019200b5` | CannonFireStart_05 | Old and new |

These support actual native weapon-state execution beyond a synthetic trigger
request. The observer is driven by weapon-switch observation and is not a full
shot sampler. Counts of its state rows are biased; animation completion, correct
timing for every weapon, absence of rapid switching, hit rate and per-shot damage
are not established by those counts.

## Early post-respawn damage

The sampler's verified actual player-spawn field at `0xc14` and server game clock
at `0x4c` identify one particularly early death. Server slot3 is old local2;
its recorded spawn time is 171.855881. At server time172.155899, same-life health
changes from100 to−1085.823608: sampled age **0.300018 seconds**.

The server's kill event at private `server.log` line651 records new local2 killing
old local2 with a cannon. It is bracketed by SYNCOK times171.41 and172.41 and
matches the memory transition. The earlier same-pair cannon event at line643
belongs to a different life. Together, the later event and memory timestamps
support an ordinary weapon kill within three seconds of an actual respawn while
session spawn protection is zero. They do not resolve the exact shot tick or
prove damage in the very first simulation tick.

The earliest verified same-life health decrease for the new cohort occurs at
age5.099922 seconds; for the Retail client at3.550217 seconds. Neither supplies a
sub-three-second new-bot or Retail-client example here. Repeated early damage
across those populations, map changes and restart gates remain open.

## Rotation and movement limits of the evidence

The valid-target `BotCombat` records show maximum new MITTEL yaw/pitch increments
of15°/12° (old:17°/13.6°), consistent with the intended bounded policy. Logging is
sparse and this is not a complete per-tick rotation or visual smoothness proof.
Neither cohort emits `CecilInvalidAction`; neither emits the new
`CecilItemTransitEnd` event in this window, so the watchdog has no native trigger
demonstration here.

Using server memory positions within one life, the longest live interval staying
within0.25 units of its interval-start position is1.95 seconds old and1.40 seconds
new. This sampling measure does not exclude spatial cycles. An old local1 item290
hop53 run lasts11 seconds, travels19.28 sampled units within a5.86-unit bounding-box
diagonal, and adds no fire actions. The longest new same-item/same-hop run found
at ten seconds travels212.12 sampled units with a59.93-unit bounding-box diagonal;
it must not be classified as a stationary stall from unchanged hop labels alone.

This trial supports real native combat activity and one correlated early weapon
kill. It also retains the acquisition failures that require correction. Portable
tracking fixtures, this native trial and eventual final-candidate acceptance are
distinct evidence levels.

## Private artifact integrity

Raw logs, session bytes, player data and control configuration remain private.
The following hashes bind this sanitized review to the inspected files:

| File within private trial directory | SHA256 |
| --- | --- |
| `result.json` | `76b9a372d06ab69f057560253e7086e9e08b2ac71ffa6610f25463a4bd5cc0b5` |
| `queries.json` | `1064e7ab734298bba7735abca52be2f5e2ef837a8b065838b529ac43881ddd49` |
| `session-health.jsonl` | `4d192f3d9ac991a1ae385db0abd7cbdabf77215112e85f53622946abb3d2e437` |
| `botA-final.log` | `f2e5f2f1d41bc19fbf1af335a92f3b28ffd8142d047a016e0e3af726c12e49cd` |
| `botB-final.log` | `c8e6937ea210d09fe2a3383a2ddc982b36ace07125bdeeee243f133b820fb660` |
| `server.log` | `49c3285ecfc03e2d455ab0929932b8aa7fab174b0a36c0aacc8106d60566e781` |
