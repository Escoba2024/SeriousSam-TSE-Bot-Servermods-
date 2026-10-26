# C1 Combat master candidate · 26 October 2026

An actual composition into the **single PR57 HumanBotPolicy**, rather than a
second combat policy or a post-processing simulator. Unqualified source only.
PR57's four-bot native session failed with SYNCBAD; this candidate does not fix
or waive that blocker. Protected Retail DLLs and runtime processes are untouched.

Pinned inputs:

- PR57 `6b84c5d283664bc9e968bb4961abf2dd48731c5b`: policy, perception, profiles,
  existing robust projectile intercept, P1 target utility/cadence/respawn,
  and original integrated GameMP source applier.
- PR66 `48e110a7aa7b818cf7bab5979f6aae629932a2dc`: weapon module, extracted
  `CombatStyle/StyleFor`, `StrafeController`, `DesiredRange2` functions.
- PR62 `d5fcd066c28764a6ba7fb6808364304f3ccd74e7`: QA reference, no production code.

No upstream source trees are committed here. The applier reads full Git object
pins, requires a new output directory, uses exact patches with zero fuzz, records
input/output SHA256, and never writes back to botcore/release/runtime. The GameMP
mode executes the pinned PR57 applier including its original release-input checks
inside a temporary seed; it does not use the caller's uncommitted source files.

```bash
# Run sequential portable regressions; generated files stay ignored in .generated.
python3 poc/candidates/combat-master-20261026/verify.py
# Choose an absent output path whose parent already exists.
python3 poc/candidates/combat-master-20261026/apply.py NEW_BOTCORE_DIRECTORY
python3 poc/candidates/combat-master-20261026/apply.py --gamemp NEW_GAMEMP_DIRECTORY
```

The second output is the flat source overlay consumed by the existing pinned
MSVC/Wine builder's SDK/CL/link steps. It contains the original PR57 Game.cpp,
BotDriver.cpp, BotTelemetry.h, release files and botcore headers plus four changed
or extra headers: bot_human.h, combat_master_support.h, combat2_weapon.h,
combat2_selected.h. BotDriver.cpp receives `driver.patch`. No project translation
units or linker inputs are added; the new headers are found beside BotDriver.cpp.
The parent integration can pass this directory to its builder's `--source-overlay`.
New compile/link success requires a new DLL hash; no acceptance transfers.

All new policy arguments default false:

```cpp
policy.Configure(&profile, exploratory_search, cecil_p1,
                 weapon2, lead2, strafe2);
```

Native shell wiring exists and defaults OFF:

| Symbol | Default | Semantics |
|---|---:|---|
| `bot_bCombatWeapon2` | 0 | PR66 selector before aiming; matching desired range |
| `bot_bCombatLead2` | 0 | additional explicit observation-age aim offset |
| `bot_bCombatStrafe2` | 0 | PR66 deterministic persona strafe and damage reversal |
| `bot_fCombatObservationAge` | 0 | seconds of estimated position age; finite positive values capped at 0.25 |

The three booleans latch at BotHumanAttach (join/rejoin/map reset), as does P1.
Set configuration before attachment. Age is sampled each tick; no ping/RTT
estimator is claimed. Zero, unknown, negative or nonfinite age adds no lead.
Existing PR57 projectile intercept remains; the new age offset also works for
hitscan and scales by the unchanged skill's prediction gain. No arbitrary extra
tick is added. `BotCommand.latency_lead_s` reports only the applied age component.

Strafe still requires explicit `bot_fStrafeScale>0` in the native adapter. Its
shipped default remains zero. No aim self-motion compensation or evasion benefit
is established; PR66's tolerance widening is deliberately excluded. Existing
turn/chase, route, injury hold, final movement, LOS and blast gates remain after
the new selections. Target scoring, reaction lock, target stickiness, cadence
and respawn have exactly one owner: PR57 with its existing `bot_bCecilP1` flag.
No PR66 target/respawn/profile/cover/search module is imported. Skill and persona
tables retain exact PR57 bytes.

Tests exercise actual policy outputs: close shotgun/far sniper, persona-dependent
loadout, ammo-loss fallback, blast safety, age reaching the aim controller,
invalid-age/LOS behavior, diagonal approach, damage strafe reversal, deterministic
reset, unchanged target and respawn decisions with all new modules enabled.
A separate executable pair compares 21,600 complete command rows with all three
flags off against pristine pinned PR57, across all tiers/personas and P1 modes.
All inherited PR57 tests and the real driver-block smoke run sequentially.

The completion patch also repairs two inherited PR57 regressions. Fresh accepted
perception interrupts the history escape before its early return, while normal
reaction, visibility, aim, blast and cadence gates still govern combat. The
chase turn hold now belongs only to exploratory movement without an active
recovery override; obstacle detours retain forward intent against either visible
or remembered targets. Reset clears override state, and the existing
NotifyNavigation callback supplies the current recovery decision. The existing 21,600-row compatibility
corpus is unchanged; corrected ambush/detour scenarios intentionally differ from
PR57 and have their own real-policy regression tests. A 40-seed exploratory
travel test verifies bounded turns and resumed movement. See
[completion evidence](../../../docs/reports/combat-completion-20261026/HANDOFF.md).

See [C1 handoff](../../../docs/reports/master-20261026/combat/HANDOFF.md) for
native evidence limits, ownership decisions and remaining blockers.
