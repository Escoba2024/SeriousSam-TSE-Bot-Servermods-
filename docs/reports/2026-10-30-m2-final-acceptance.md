# M2 final native acceptance campaign — 30 October 2026

**Status: IN_PROGRESS / NATIVE_QA_PENDING. M2 is not accepted.**
M1 remains IN_PROGRESS / NOT_ACCEPTED; its eight-bot/120-minute test is deferred.
No public activation, original-server modification, qualified-DLL replacement,
main merge, threshold increase, protected-data deletion or additional service.

## Baseline and changes

Fresh GitHub lookup confirmed draft PR81 at889978f on PR80/619a807. Main remains
ab0c740 remotely and fdfc46e locally; no checkout/reset/update of main. Preserved
all existing worktrees, including foreign dirty/untracked work. Four unpublished
continuation commits74174ca..72580c2 were retained as ancestors of isolated branch
`agent/lead/20261030-m2-final`, worktree `/srv/tse-m2-final-20261030`.
The supplied native continuation design/plan is reused. New persistent execution
plan: `../superpowers/plans/2026-10-30-m2-final-acceptance.md`.

Changes address test coverage and evidence, with the actual AI DLL unchanged:

- Independent validated `--m2-skill 1..5` / `--m2-persona 0..5` now reach the
  native constructor, startup before enable, and result metadata. Previously
  the starter hardcoded expert/Duelist. All30 generated combinations tested.
- Original opponent keyboard probe disables only mouse-look axes in its copied
  controls, retaining native Pressed/Released commands. No game-memory writes.
- Explicit finite-ammo Red Station staging retains map query validation and
  existing one/two-bot/300-second bounds. A first native attempt exposed an
  incorrect guessed basename `DM_RedStation.wld`; corrected to pinned PR73's
  `RedStation.wld` with a reproducing regression. Failed fixture preserved.
- `combat_evidence.py` separates emitted fire inputs, sampled Colt clip decreases,
  same-entity health/frag deltas and alive-after-death transitions. It never grants
  full M2 acceptance. Respawn attribution also needs stable roster/session evidence.

## Source/build and original protection

No new AI source change or rebuild has occurred in this continuation.
Retained build source81f00be322f30f953b541e34e239eedac50d06f9, successful15-unit
MSVC x86 build, PE32 Retail candidate; private build02. Fresh42/42 source hashes
and candidate bytes match its manifest. DLL SHA256:
`860ae6d7fbc91de301f80a963599d970692b872a51d0e0330dbd30ccd11e134b`.

Fresh rollback check:415/415 original,415/415 restore-copy and415/415 tar-member
hashes match; archive SHA256
`d7b3650d55a21fc88614d5b969e126ac1cfcc52585262a1ef139eb0be1632b7d`.
Qualified61DC reference preserved. Native copies use owned overlays, namespace,
global locks, process identity and original pins. Existing guards remain CPU<85%,
RAM>=768MiB / next-client reserve>=1068MiB, disk>=8GiB. Initial host RAM3819MiB,
no swap, available~2.5GiB, disk~8.7GiB. Protected Codex/OpenCode/MCP services live.

## Fresh verification

- Actual M2 policy741, adapter tail29, native attach/reset35, final action43:
  PASS. Real driver integration PASS. Inherited composition1243 and regression
  29414 assertions, all10 inherited C++ suites: PASS.
- Candidate Python staging/input/evidence tests:40/40 PASS at56cf70b.
- Profile change RED: CLI rejected new options and generated tier1/persona0
  incorrectly remained5/2. GREEN covers all30 scripts, invalid ranges and safe
  defaults. Mouse-axis test RED on absent helper, then GREEN. Map regression
  RED on wrong original basename, then GREEN. Evidence tests initially absent
  module, then6/6 GREEN.
- Independent read-only review before and after: no Critical/Important remaining.
  Prior profile hardcoding coverage gap resolved; no native actions by reviewer.

## New native cases

| Case | Result | Scope and actual observations |
|---|---|---|
| Little Trouble, one bot,300s, tier5/persona2 | PASS_SCOPED_COMBAT_AND_ORIGINAL_RESPAWN | wrapper/controller0, guard FINISHED, six successful unmounts. Actual Colt clip decreases11, emitted combat inputs19; original same entity health100→70→40→10→-20, bot frags0→1, original same entity alive100 after ordinary fire-button respawn. No bot-death claim from this case. |
| Red Station finite-ammo fixture04 | FAIL_FIXTURE_CORRECTED | Wrong map filename prevented original join; controller1, native original-Retail join timeout. Eight successful unmounts; failure retained, no gameplay acceptance. |
| Red Station finite-ammo05, two bots,300s | RUNNING | At interim observation: original actor and one bot died; same bot entity returned alive, other bot frag counter reached2. Final scope depends on full receipts and cleanup. |
| Five-skill/six-persona native axes | QUEUED_SERIAL | All30 combinations covered offline; nine additional two-bot150s cases exercise each remaining tier/persona with normal original-opponent input. This is explicitly not30 native Cartesian cells. |

Little Trouble fresh native case: elapsed307.409s after readiness, host CPU
mean44.231% / peak77.912%, minimum available RAM1898.785MiB, cgroup peak514.563MiB,
minimum disk8.591GiB, zero throttled periods. No observed sync/disconnect failure.
Two aborted private input directors remain preserved: one had an incorrect route
predicate; the corrected restart stopped because immediate yaw calibration showed
zero effect. Manual guarded normal inputs subsequently established movement,
aim changes, damage, kill and original respawn. Dispatch alone was never accepted
as gameplay proof. Input latency/timing has not been calibrated for exact aiming.

Retained predecessor duel01 was externally interrupted and remains failed;
duel02 had a clean300s lifecycle result but no target/fire. Historical outer143
remains quarantined. These are not relabeled by new successful tests.

## Open final gates

Native weapon breadth, finite reserve exhaustion/fallback, post-bot-respawn firing,
native skill/persona behavior coverage and final stability/cleanup review remain
open until final campaign receipts. Colt magazine is not the finite bullet pool;
current logs do not supply every weapon's ammo reserve. No shot count is inferred
from SetAction acknowledgement. No M2_NATIVE_QA_ACCEPTED claim at this checkpoint.

Private raw evidence/controllers are retained under
`/root/ssam-ai-backups/m2-final-20261030`; no private profiles, identifiers, raw
logs, screenshots or Retail binaries are published. Sanitized final evidence and
GitHub publication follow after the serial campaign and final audit.
