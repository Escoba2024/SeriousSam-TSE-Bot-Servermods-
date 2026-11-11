# Three-tier arena policy — portable implementation only

Scope: A3 bounded changes in `poc/candidates/redstation-supply-20261107`, based on
Cecil048 source commit `4d04ab4ad190a0f6cd078d96f5416e0eea9e1da0`, with the bounded
tracking/arbitration follow-up based on milestone commit `b011220`. No DLL built,
installed or qualified in this task; no runtime processes changed. Existing
server power-up filtering, health, damage, ammo, blood/gibs and network action format
remain outside this change.

## Release profile and migration

The active candidate's `BotHumanAttach` now creates one of three arena profiles.
`bot_iArenaTier=0` migrates historical roster skills 1/2/3 to MITTEL, 4 to STARK,
5 to DEMON; the existing eight slots therefore become 6 MITTEL, 1 STARK,
1 DEMON. Values 1/2/3 explicitly select MITTEL/STARK/DEMON for the process.
Invalid values log rejection and use MITTEL. Configuration is applied when
profiles attach/reset, not dynamically each tick. Existing profile-slot selection
and roster offsets remain available, including per-slot mixed tiers in mode 0.

All tiers use the same duelist movement/personality, acquisition range, LOS
budget, weapon knowledge, hysteresis and item/navigation capabilities. Historical
roster entries remain only as migration/seed input. Seeds retain their original
slot derivation even when difficulty changes. Visible player names and internal
session identity are not changed by administrative profile labels.

| Parameter | MITTEL | STARK | DEMON |
| --- | ---: | ---: | ---: |
| Reaction seconds | 0.20 | 0.10 | 0.05 |
| Aim noise sigma, degrees | 0.90 | 0.45 | 0.15 |
| Turn limit, degrees/second | 300 | 420 | 540 |
| Turn acceleration, degrees/second² | 1000 | 1600 | 2400 |
| Tracking proportional response, 1/second | 10 | 14 | 20 |
| Settle seconds | 0.10 | 0.05 | 0 |
| Existing projectile lead gain | 0.75 | 0.90 | 1.00 |

Common weapon dwell is 0.6 s, switch margin 1.15, nominal engagement distance
16 units, 90° awareness half-angle, 100-unit acquisition range and eight requested
LOS rays per bot tick (the existing global ray budget still limits execution).
These are calibration hypotheses, not measured human difficulty rankings.

Arena profiles preserve these values through `HumanBotPolicy::Configure` rather
than replacing them with the independent Cecil preset difficulty. The existing
bounded Human aim controller supplies rotation/acceleration; the second Cecil
angular envelope and random prediction floor do not override arena intent.
Cecil shooting, target-search, allowed-weapon, movement and navigation switches
still apply. Legacy `BuildProfile` remains unchanged for historical control tests;
it is not the candidate's ordinary release-profile path. Attach logs preserve the
existing `tier=` parser field and add `model=arena-v1`.

Activation still requires `bot_bAutoCombat=1` and either `bot_bHumanAI=1` or
`bot_bSupplyNavigation=1`. Logs produced by attach alone do not prove that path
runs. Release configuration must retain `bot_bCombatSkipLocals=0` for sibling
opponents and a nonzero `bot_fStrafeScale` when strafing is intended. Mode guards
remain deathmatch-only; this change does not port cooperative play.

## Weapon-suitable targets

A separate arena engagement rule limits either Colt to 18 units and preserves
Cecil safety ranges for other weapons. Original Cecil rating tables remain
byte-for-byte unchanged. Target selection, current-target locks, remembered-target
continuation and weapon selection all use the same arena range eligibility.
Arena uses the same Cecil scoring/range model with or without supply navigation,
so its feasibility test cannot fall back to a knife at an otherwise feasible
90-unit Tommy target. A distant low-health opponent cannot displace a close feasible fight when only
Colts are usable. With no feasible target, the policy releases it to the existing
weapon/item navigation rather than firing or pursuing it. A newly usable owned
long-range weapon makes distant opponents eligible again. Allowed-weapon masks,
fresh LOS for fire, weapon-switch readiness and per-slot state remain intact.

The follow-up removes a concrete arbitration defect: any ordinary item goal used
to override visible combat whenever the opponent was more than ten units away,
discarding aim and fire. Ordinary pickups now yield to a feasible visible fight.
Urgent health/ammo/weapon goals and traversal controls retain movement ownership;
navigation continues normally when no feasible opponent is visible. The existing
reachable mapped-weapon acquisition remains intact, including directed paths,
physical connector checks, bounded goal lifetime and the close-threat gate.
An extracted-Driver test composes the actual Human policy and native typed urgency:
with only spawn Colts a first useful ranged pickup owns movement at 10/30 units;
after a usable Tommy pickup, combat wins over an ordinary subsequent pickup.
This demonstrates policy ownership, not a new native acquisition-time result.
Existing safe navigation, stuck recovery, travel-knife behavior and jumps are
retained. No new cover solver, human-priority classifier or independently measured
knife speed benefit is claimed.

## Tracking and trigger follow-up

A controlled 20°/s target crossing exposed a mismatch between aim and trigger:
the controller measured final crosshair residual but gated firing on its pre-turn
perceived error. With identical seed 123, DEMON aligned for 699/699 measured ticks
but fired only seven. A RED test also caught fire outside the final tolerance.
Arena now settles against final residual, fresh LOS and the current selected
weapon. MITTEL/STARK/DEMON require respectively 0.10/0.05/0 seconds of consecutive
alignment. LOS loss, target change, invalid input, nonconsecutive ticks, death or
weapon mismatch reset this per-policy state. The native current/wanted-weapon,
range and fire-state guards still run after arbitration.

The next RED test exposed identical proportional response in all tiers: at
40°/s, the shared 10/s response left DEMON outside tolerance for most ticks despite
lower aim noise. Arena now uses the ordered response values above, inside the
unchanged rate and acceleration caps. Legacy profiles default to exactly 10/s.
Validation rejects nonfinite/out-of-range response gains. No target snapping or
entity/health/damage writes were added.

The committed feedback fixture uses a Tommy, 30-unit range, a reversing angular
crossing, seeds 123/77123/20261111, 800 ticks per run and 699 measured ticks after
warmup. These are firing-intent ticks, not bullets, hits, damage or frags:

| Target speed | Fire ticks MITTEL/STARK/DEMON (each /2097) | Mean final error, degrees |
| --- | --- | --- |
| 20°/s | 866 / 1978 / 2097 | 1.530 / 0.754 / 0.234 |
| 40°/s | 420 / 1648 / 2097 | 2.191 / 1.007 / 0.234 |
| 60°/s | 72 / 1095 / 2097 | 3.124 / 1.396 / 0.235 |

Tests require ordered aggregated fire/error, no fire outside tolerance, bounded
acceleration through reversals, meaningful DEMON fire availability, fresh settling
after interruptions and independent interleaved local-bot trigger state. This
does not establish ordering for every trajectory, weapon or native condition.

## Verification and remaining gates

The initial new regression failed on the historical roster's personality.
The short-Colt regression also fails against a separate pristine-HEAD control:
its distant low-health target incorrectly defeats the nearby useful fight.
A further RED/GREEN regression caught and fixed the HumanAI-only arena scoring
mismatch described above. The implemented policy passes migration/invalid selection, all four Cecil preset
configuration cases, short-Colt ownership/range/allowed-mask cases, LOS/death/coop
suppression, sibling targeting, independent reaction state and entity replacement.
A replacement becomes targetable after normal reaction only; no spawn grace added.

Completed commands/checks:

- `python3 tools/test_arena_combat.py`: actual C++ policy compiled and run.
- All ten candidate `test_*.cpp` programs compiled with GCC C++17,
  AddressSanitizer and UndefinedBehaviorSanitizer and executed successfully.
- `python3 -m unittest discover -s tools -p 'test_*.py'`: 183 tests passed;
  printed missing-column/query failures are expected negative fixtures.
- Initial patch: `make -C poc/botcore test`: all seven legacy portable programs passed,
  including the 555-check Human policy suite. These are compatibility controls,
  not validation of the new candidate headers.
- New arena tracking feedback in three gravity frames: bounded angle increments
  and >100 firing ticks for each tier. The synthetic scenario yielded
  MITTEL/STARK/DEMON 165/497/499 firing ticks after warmup, identically per frame.
  The faster crossing measurements above are the stronger ordered-policy check.
- `python3 poc/candidates/redstation-supply-20261107/test_cecil_action_native.py
  --sdk-player /srv/tse-sdk-20261021/Sources/EntitiesMP/Player.es`: actual Driver
  guards/ownership and typed acquisition/combat composition pass under ASan/UBSan.
- `python3 poc/candidates/redstation-supply-20261107/test_cecil_native_bridge.py
  --sanitize --sdk-player /srv/tse-sdk-20261021/Sources/EntitiesMP/Player.es`:
  1335 checks passed, including reachable/unreachable mapped-weapon goals,
  close-threat handling, goal lifetime and collision/control ownership. SDK
  Player.es SHA256: `85c92933fa5b0cc726be7b42a3bc82d4c95b255507ec8b1fffe2666fcf3888af`.

The integration owner still needs a full native build and fresh manifest/DLL hash,
three matched baseline/candidate comparisons with exchanged starts and measurements
of weapons, hits/damage, deaths/frags and stuck behavior, plus Vanilla sync and all
applicable map/resource/stability gates. Existing qualified binaries and old test
windows confer no acceptance on this source change. A3 remains incomplete.
