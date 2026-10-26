# C1 COMBAT handoff · 26 October 2026

Source-only opt-in candidate delivered in
[`poc/candidates/combat-master-20261026`](../../../../poc/candidates/combat-master-20261026/README.md).
Writer scope stayed within that directory and this report directory; no shared
production source, main branch, runtime process, port or DLL was changed. Worktree
`/srv/tse-c1-combat-20261026`, branch `agent/c1/20261026-combat`, base `ab0c740`.
No additional agents or game processes were started by C1. Tool choice: local Git,
Python and sequential C++ compilation; no binary hypothesis required Ghidra/Frida.

## Composition and conflict resolution

| Area | Owner / decision | Reason |
|---|---|---|
| Policy | PR57 single existing HumanBotPolicy | Avoid a parallel policy and post-aim output rewriting |
| Target | PR57 TargetUtility/ChooseTarget | Fresh replicated facing/HP plus reaction and hysteresis already integrated |
| Respawn | PR57 ShouldRespawnPulse | PR57 delay ticks 40/30/20/12/5 vs incompatible PR66 26/20/15/11/8 plus persona offsets; never stack clocks |
| Cadence | PR57 P1 | Keep native action path and existing LOS/blast gating |
| Weapon/range | PR66 WeaponSelector2 + DesiredRange2 opt-in | Choice happens BEFORE aim/cadence, range follows that weapon |
| Lead | Existing PR57 full-vector InterceptTime + explicit age opt-in | PR66 scalar two-iteration opening-speed formula is less general; never infer RTT as replication delay |
| Strafe | PR66 controller opt-in | Persona/seed dynamics integrated inside MoveIntent, existing safety gates retained |
| Profile | PR57 unchanged | PR66 retuning conflates weapon/lead effects with aim/reaction changes |
| Cover/search/alert | Deferred | Navigation contract and dedicated fairness tests required |

PR66's `StrafeFireTolMult` claims weak tiers fire less, but returns values ABOVE
one, widening the allowed error. It is not self-motion feed-forward and is not
imported. PR66's simulator additionally replaces `cmd.weapon` after the real
policy's aim/fire decision; its wins/lead numbers cannot be transferred to this
composition. This candidate selects the new weapon before those decisions.
PR62's F1/F3/F5 motivate the selected modules, but its synthetic damage, latency
and movement assumptions remain assumptions. Beginner hit-floor retuning (F2),
self-motion compensation (F5) and cover survival (F4) remain unresolved.

## Reproduced portable checks

Command: `python3 poc/candidates/combat-master-20261026/verify.py`.
Sequential compiler/make execution, no runtime binaries or game assets needed.

- New integrated policy tests: **1,243 checks, zero failures**. Initial unchanged
  PR57 implementation failed six behavioral checks (close/far weapon choice,
  immediate ammo-loss fallback, persona diversity, absent age lead, approach
  strafe), before writing the composition patch.
- Default-off: **21,600 command rows byte-identical** to pristine pinned PR57,
  all five tiers, six personas, both existing P1 modes. Trace SHA256
  `51398dd81d9f3f6265eb1d0640f0f4a5bd002aeaabb5f62a04595e23a70420aa`.
- All ten inherited PR57 C++ test executables passed, including Human AI
  555 checks, Cecil P1 255 checks, projectile intercept, route, weapon, combat,
  reconnect and obstacle policies.
- Real generated BotDriver human block compiled and ran with engine stubs.
  This is a portable integration smoke, not GameMP or Retail acceptance.
- Both source materialization modes produce identical composed policy headers;
  existing-directory/dangling-symlink outputs are rejected without overwriting.
- Source manifests pin PR57 `6b84c5d283664bc9e968bb4961abf2dd48731c5b`,
  PR66 `48e110a7aa7b818cf7bab5979f6aae629932a2dc`, QA reference PR62
  `d5fcd066c28764a6ba7fb6808364304f3ccd74e7` and SHA256 of all materialized inputs.

## Existing native PR57 evidence, freshly inspected read-only

The published PR57 handoff still says four-bot pending. The existing private
result now gives a definitive failure; no raw logs are copied here.

| Existing receipt | DLL SHA256 | Actual result |
|---|---|---|
| Cecil P1 one-bot r2 | `7dc961c880e0ed68ead13ed4e8299a025be71e05619de36c437c756e964334bf` | PASS_LIMITED_SESSION_LIFECYCLE, 131.8743229001 s |
| Cecil P1 four-bot | same | FAIL, 97.9282428019 s; `server native failure: SYNCBAD` |

Read-only receipts: `/srv/tse-session-qualification-cecil-p1-one-20261025-r2/result.json`
and `/srv/tse-session-qualification-cecil-p1-four-20261025/result.json`.
Build receipt `/srv/tse-cecil-p1-build-20261025-01/manifest.json` reports
build_ok=true. Its bot_human.h, bot_profile.h and BotDriver.cpp SHA256 match the
pinned PR57 input bytes, freshly compared. The four-bot final native log gate
also records SYNCBAD in cleanup_errors. This identifies a failing gate, **not**
its cause, first divergent tick or a P1-specific causal defect. One-bot lifecycle
success provides no gunplay-quality or long-term-sync acceptance.

## Existing candidate boundaries

- Protected release `61DC27E0E7B80BADCF9AE705C30FCA88EDD3935737715DFFFF59E90C26F1FEF9`
  remains its own qualified historical candidate.
- Build04 `7fc94a39c3f5d9516f262d9e4d04a5cf38e6eb5ae3482976c32c952a99d30835`
  has the historical native evidence in the 21 October report; no inheritance.
- Build06 `54faabf01d205c034055fa03c5b4316ce12a4907c824462ad85f797b3e7845e8`
  is the separately documented experimental public user-test generation in the
  parent's 25 October master handoff. Its status was not remeasured by C1 and
  neither its processes nor any unknown external player were touched.
- The composed C1 candidate has **NOT_TESTED** native build/Retail status in C1.
  The parent can perform a distinct MSVC build with its own manifest/hash.

## Native build entry and exact blockers

Generate a fresh flat overlay with
`python3 poc/candidates/combat-master-20261026/apply.py --gamemp NEW_OUTPUT`.
Feed that output to the parent's `tools/build_integrated_gamemp.py --source-overlay`
(or use the same existing SDK/CL/link pipeline with this source overlay). The
original pinned PR57 source applier is executed, including its release pin checks;
then local patches and selected PR66 headers are added. Four header files beyond
PR57 must stay alongside BotDriver.cpp: `combat_master_support.h`,
`combat2_weapon.h`, `combat2_selected.h` and the patched `bot_human.h`.
No new translation unit, project-file entry, engine/library change is required.

Native symbols are wired and default 0: `bot_bCombatWeapon2`,
`bot_bCombatLead2`, `bot_bCombatStrafe2`, `bot_fCombatObservationAge`.
The booleans latch during existing BotHumanAttach; age is a live seconds input,
not an implemented estimator. `bot_bCecilP1` remains the one P1 switch;
`bot_fStrafeScale` remains 0 and must be explicitly configured to apply strafe.
Existing new modules are source-integrated, not native accepted runtime features.

Blocking any release/activation claim: (1) unresolved observed PR57 four-bot
SYNCBAD; (2) new MSVC compile/link and DLL hash; (3) isolated instrument-free
control, one/four-bot join/sync/lifecycle and longer acceptance for this NEW hash;
(4) real weapon firing/hits/cadence, projectile/cannon behavior and ammo tests;
(5) measured observation-age source and correct clock semantics before meaningful
latency tuning; (6) strafe self-motion compensation/evasion/CPU evidence.
No kick-threshold override, ground-feature rollout, production deploy or extra
native fleet is authorized or performed by this C1 deliverable.
