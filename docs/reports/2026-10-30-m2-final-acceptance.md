# M2 native acceptance campaign — 30 October 2026

**M2: IN_PROGRESS / NATIVE_QA_PENDING. Full acceptance has not been granted.**
M1 remains IN_PROGRESS / NOT_ACCEPTED; its eight-bot/120-minute campaign is
explicitly deferred. Draft PR82 preserves PR81→PR80 and their dependencies.

## Verified starting point

Fresh GitHub reads confirmed PR80/619a807 and PR81/889978f are open drafts; main
remains remotely ab0c740. Existing local main fdfc46e, all other worktrees and
foreign dirty work were preserved. Four unpublished continuation commits
74174ca..72580c2 are retained as ancestors of isolated branch
`agent/lead/20261030-m2-final`, worktree `/srv/tse-m2-final-20261030`.
Persistent plan: `../superpowers/plans/2026-10-30-m2-final-acceptance.md`.
Measurement decision: `../decisions/2026-10-30-m2-native-combat-measurement.md`.

Actual host: Hetzner Ubuntu24.04.4, two CPUs,3819MiB RAM/no swap. Initial
available RAM~2.5GiB and disk~8.7GiB. Original Retail installation, pinned SDK,
MSVC x86 through Wine, private overlay/netns/cgroup/X11 harness and byte-for-byte
rollback are present. Protected Codex/OpenCode/MCP/tunnel services and preexisting
Xvfb139 remain untouched. No missing-Windows-runtime excuse is inferred here.

## Implementation and fixes

The retained PR81 candidate supplies five mechanical tiers, six personalities,
one policy/target/respawn owner, dead/replaced/expired opponent invalidation,
fresh native attach, final-action cadence acknowledgement, ammo/melee gates,
recovery ownership and bounded reverse/strafe wall checks. Existing experimental
features stay OFF by default; private tests explicitly enable P1/weapon2/lead2/
strafe2. No M3 ground planner or parallel production AI was introduced.

This continuation adds or corrects:

- Validated native skill1..5 and persona0..5 independently reach constructor,
  startup before enable and result metadata. The starter formerly forced5/2.
  All30 generated configurations and invalid/default cases are tested.
- Owned original-client keyboard controls preserve native Pressed/Released
  commands, remove duplicate strafe aliases and disable mouse-look interference.
  Supported original rotation settings60/30 affect only this test opponent.
- Explicit finite-ammo original map staging with filename/query pins. A guessed
  RedStation basename failed native join; corrected against the pinned original
  `RedStation.wld` with a reproducing regression. Hole has unsuitable vertical
  spawn separation; an unsuccessful gameplay fixture is not an AI acceptance.
- Conservative sampled evidence parsing distinguishes fire inputs, Colt clip,
  all reserve pools, health/death/frag observations and projectile witnesses.
  Malformed Windows-CRT projectile speed text is rejected without losing the scan.
- One bounded, read-only `BotAmmo` diagnostic under existing debug/cadence/lock/
  local/null guards. Fourteen integer fields/arguments match; tests execute the
  exact extracted patched statement and verify that weapon state is unchanged.

Private original-opponent steering uses only existing guarded normal input.
An initial director started before its runtime directory existed; it sent no
input and its failure remains retained. Local driver tick counters cannot be
compared across observer logs; the revised director waits for wall time and fresh
log progress. Stale-context input is refused. These private steering attempts do
not independently establish shots, hits or exact input latency.

## Build provenance and offline verification

| Candidate | Source/build | DLL SHA256 | Scope |
|---|---|---|---|
| build02 | source81f00be322f30f953b541e34e239eedac50d06f9;15 units/42 inputs | `860ae6d7fbc91de301f80a963599d970692b872a51d0e0330dbd30ccd11e134b` | Retained candidate and completed first native matrix |
| build03 | sourcec67a06a900db049cac1cc0304860323b069cdb5f;15 units/42 inputs | `a62a19e75251f69207966bb8965c019d8c7e76458099e6eb86bfddc4cb1ee5dd` | New diagnostic candidate; fresh native campaign |

MSVC Win32 Release-equivalent build03 finished14:19:31UTC. PE signature, x86
machine0x14c and PE32 optional header0x10b verified directly. SDK commit
aa7869c2c2c4db0562281814d0ac3784e6b9d6f0; Engine107 includes
94ff8cd0e63941f8601294350b616472f772ed51. All42 stored inputs and DLL bytes match
the build manifest. Of23 materialized overlay files only BotDriver.cpp changed;
removing the exact added diagnostic statement restores byte-identical build02
source. No gameplay/native qualification is transferred between DLL hashes.

Fresh checks:

- Actual M2 policy741, adapter tail29, native attach/reset35, final action43,
  driver integration and extracted ammo statement3 assertions: PASS.
- ASan/UBSan: all six M2 executables and inherited verification PASS.
- Inherited C1 composition1243/regressions29414 and all10 C++ suites: PASS.
- Tools291 run:290 PASS, one deliberate native-Wine CLI skip; benchmarks59 PASS.
- Candidate Python45 PASS before the additional Compound fixture; that fixture's
  focused regression is RED/GREEN. Final complete candidate rerun follows staging.
- Independent read-only code reviews: no Critical/Important findings remaining.
  Tier1's sampled prolonged aiming plateau does not prove a firing defect:
  perceived-error gating requires seven consecutive valid ticks, whereas the
  logged sparse error is a different true residual. Calibration remains open.

## Completed native evidence on build02

All accepted scoped cases below have controller/wrapper0, guardFINISHED,
child0, clean unmounts and no observed SYNCBAD/disconnect/CRC-error markers.
Their lifecycle PASS is narrower than full M2 acceptance.

| Cases | Measured scope | Attributable observations |
|---|---|---|
| Little Trouble03,1bot/300s,t5p2 | Actual combat and original compatibility | Colt clip decreases11; original same-entity health100→70→40→10→-20, bot frag0→1; normal-input original respawn100 |
| RedStation04 | FAIL_FIXTURE_CORRECTED | Wrong original map filename; join timeout, wrapper1; eight clean unmounts. Failure preserved |
| RedStation05,2bots/300s,t5p2 | Bot death/respawn | Local bot/index2 dead1400→alive1440; other bot frags2. Returned bot continues sensing/movement; no postreturn visible target/fire in this case |
| Native axes06..14,2bots/150s each | Five tiers and six personas | Every requested profile actually attached; all remaining tier/persona axes covered. Not30 native Cartesian cells |
| Hole15,1bot/300s,t5p0 | Lifecycle only | No target/fire; world/fall death and large floor separation. Unsuitable combat fixture |

Marksman09 and Flaky10 establish actual post-bot-respawn combat: sampled Colt
clip decreases6/7 after return, emitted-input deltas36/26 and further kills in
Flaky. Tier2/4 cases observe three/two distinct owned type0 rocket entities;
`PRT_ROCKET=0` is checked in this build's Engine107 header. Tier2 original health
100→44.7. Tier3 actual current shotgun4 consumes shell30→29 before switching to
rocket8. Concurrent rocket impact means the original100→85 change is not
attributed exclusively to shotgun damage. Tier1 selected shotgun4 but no shell
consumption occurred in its sampled firing windows. No exact shot count or
finite-exhaustion/fallback PASS is inferred.

## Fresh native campaign on build03

Serial one/two-bot tests use the same original server/client hashes, finite ammo
and unchanged resource/sync gates. No compiler or broad regression overlaps native
measurement. Current private campaign state is `ammo-profiles.json`; final
receipts take precedence over this checkpoint.

| Case | Status | Evidence |
|---|---|---|
| RedStation ammo16,1bot/300s,t5p2 | PASS_LIMITED_NATIVE_RUNTIME | Controller0, guardFINISHED,6/6 unmounts; Colt clip decreases18, original two deaths/one observed return, bot frags+2; no sync/CRC errors |
| RedStation ammo17,2bots/300s,t5p2 | PASS_LIMITED_NATIVE_RUNTIME | Controller0, guardFINISHED,8/8 unmounts; original two deaths/two returns, bot frags+2, peer health100→25; current weapons1/2/5, no sampled shell decrease |
| RedStation ammo18,t5p0 | PASS_LIMITED_NATIVE_RUNTIME | Two bots dead/alive; independent audit confirms own respawn→clip6→4→3→1, peer100→70→40→-20 and native frag-1→0; no original firing in the sequence |
| Remaining native axes ammo19..26 | RUNNING_SERIAL | Preserve every requested/actual profile and result separately; no future PASS claim |
| Compound (KuntaKinte.wld) | PREPARED_ONLY | Verified original level-discovery title/filename and finite query-pinned staging; potential additional weapon fixture |

Ammo16 host CPU mean45.918%/peak76.536%, available RAM minimum1910.988MiB,
cgroup peak526.348MiB, disk minimum8.458GiB; zero new throttled periods. `cgroup
CPU core percent` is a separate one-core-normalized measurement, not host CPU.

## Acceptance boundaries and open gates

| Criterion | Current disposition |
|---|---|
| Five skills/six personalities | PASS offline, build02 native axes; build03 matrix still running |
| Opponent sensing/LOS/target change | PASS scoped source/portable/native observations; no global reliability or map-coverage claim |
| Weapon availability/selection/ammo | PASS portable; multiple real build02 weapons; new diagnostic reserves available; physical empty-reserve fallback open |
| Actual combat | PASS scoped Colt damage/kills on both hashes; build02 shotgun consumption and owned rockets |
| Movement/strafe/retreat/wall reaction | PASS portable and scoped movement observations; full ground/path/cover planning unsupported/deferred M3 |
| Death/respawn/return to combat | PASS scoped on both builds; independent build03 audit confirms one peer kill after own return |
| Critical defects | None reproduced in reviewed M2 code; tier1 calibration and fixture/coverage limits remain explicit |
| Offline regressions/MSVC x86 | PASS, with one named native-Wine CLI skip |
| Retail tests/original compatibility | PASS limited private Wine1.07 sessions; no blanket Windows/public/24x7 acceptance |
| Sync | No observed failures in clean current cases; historical quarantined/failed runs retain their status |
| Resource safety/rollback | PASS checked scopes; final after-campaign audit pending |
| Documentation/publication | Draft PR82 exists; final sanitized receipts and final remote snapshot pending |

Physical finite-reserve exhaustion→usable fallback, close melee/cadence evidence,
new-hash broader weapon coverage, completed native profile campaign and final
cleanup/rollback audit remain open. Missing evidence is not PASS. No external
blocker is asserted merely because a combat fixture has not supplied an event.

## Reproduction and protection

Run portable verification and Python suites from the isolated source tree:

```sh
python3 poc/candidates/m2-ai2-20261030/verify.py
python3 poc/candidates/m2-ai2-20261030/verify.py --sanitize
python3 -m unittest discover -s poc/candidates/m2-ai2-20261030/tests
python3 -m unittest discover -s tools -p 'test_*.py'
python3 -m unittest discover -s tools/benchmarks -p 'test_*.py'
```

Materialize a fresh flat overlay with `apply.py --gamemp NEW_DIRECTORY`; build
with `tools/build_integrated_gamemp.py` using the pinned SDK/toolchain, exclusively
owned build prefix and new output directory. Native staging:

```sh
python3 poc/candidates/m2-ai2-20261030/stage_duel.py NEW_HARNESS --map redstation
python3 NEW_HARNESS/tools/qualify_bot_sessions.py \
  --config PRIVATE_ONE_OR_TWO_BOT_CONFIG --runtime NEW_OWNED_M2_RUNTIME \
  --duration 150 --execute --m2-combat --cecil-p1 \
  --m2-skill 5 --m2-persona 2 --build-manifest PRIVATE_BUILD_MANIFEST \
  --offline-public-marker PRIVATE_VALIDATED_PUBLIC_DISABLED_MARKER \
  --port UNUSED_PRIVATE_PORT --display UNUSED_PRIVATE_DISPLAY --preset duel
```

Use a fresh `/srv/tse-session-qualification-m2-*` runtime and the existing global
locks/preflight/guard, not copied runtime permission from this report. Profile
matrix cells are(5,0..5) and(1..4,2). Use guarded `retail_opponent_input.py` for
ordinary original movement/fire/respawn and confirm actual subsequent state.
`combat_evidence.py PRIVATE_LOG` outputs observations, never full acceptance.

Fresh original protection check:415/415 live original,415/415 restore copy and
415/415 archive-member hashes match. Rollback archive SHA256
`d7b3650d55a21fc88614d5b969e126ac1cfcc52585262a1ef139eb0be1632b7d`.
Qualified61DC DLL is unchanged. No public activation, original-server-binary
modification, production-DLL replacement, main merge, force-push, paid service,
threshold increase or protected-data deletion.

Private raw logs/configs/controllers/screenshots and licensed binaries remain under
`/root/ssam-ai-backups/m2-final-20261030` and owned private runtime roots. Historical
interrupted duel01, quarantined outer143, corrected failed fixture04 and abandoned
steering attempts are retained. They are not relabeled by subsequent clean runs.
