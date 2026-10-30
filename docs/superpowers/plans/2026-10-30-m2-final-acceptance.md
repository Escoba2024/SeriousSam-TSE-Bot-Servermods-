# M2 final native acceptance execution plan

> **For agentic workers:** Use superpowers:executing-plans, with systematic debugging and verification-before-completion. The user explicitly authorized autonomous execution and publication of a draft; no intermediate approval gates.

**Goal:** Reach M2 NATIVE_QA_ACCEPTED, or document a demonstrated external blocker after completing independent work.
**Architecture:** Continue PR81's single policy and existing original Retail private harness. Reuse reviewed source/build pins; one native campaign at a time, at most two bots. Normal input to an owned original opponent supplies real gameplay, without engine hooks or server changes.
**Tech Stack:** Python, portable C++, installed MSVC x86 via Wine, original Retail1.07.
**Spec:** User mandate of 30 October 2026 and `../specs/2026-10-30-m2-native-combat-qa.md`.

## Global constraints

- M1 IN_PROGRESS / NOT_ACCEPTED; eight-bot/120-minute matrix deferred.
- Disk >=8GiB; preserve all existing CPU/RAM/sync/ownership guards.
- Preserve original/qualified DLLs, backups, foreign worktrees/processes and stacked dependencies. No main merge, public activation, force push, paid services or server upgrade.
- Native campaign <=300s, serial; no compilation/broad regression while measuring.
- No native PASS from synthetic input, successful dispatch, joins or build alone.

## Review focus

- Retained tests may contain stronger evidence than summaries; reconstruct rather than discard.
- Missing or stale snapshots, slot reuse and input acknowledgement cannot establish hits.
- Offline 30-profile differentiation is distinct from a native profile matrix.
- External signals, sync failures and incomplete cleanup invalidate acceptance.
- Keep enough disk for rollback; no deletion of protected data.

### Task 1: inventory and evidence reconstruction

**Files:** This plan; final report and sanitized evidence under `docs/reports/`.
**Interface:** Consume PR81/local72580c2, original manifests, retained native receipts; produce verified baseline and coverage gaps.
- [x] Fresh GitHub PR81/open PR lookup, git fetch, worktree/process/resource census.
- [x] Create own worktree `/srv/tse-m2-final-20261030`, branch `agent/lead/20261030-m2-final`; preserve four unpublished predecessor commits.
- [x] Run inherited M2 Python staging/input suite:28/28 PASS.
- [x] Reconstruct duel01/02 evidence and verify current original/build/backup/source pins.

### Task 2: real combat and profile coverage

**Files:** Existing M2 stagers/input helper, targeted tests if defects occur; private native controllers/receipts.
**Interface:** Consume exact DLL860ae6d7 and guarded finite-ammo scene; produce attributable engine-side combat/death/respawn evidence, then native profile matrix.
- [ ] Validate actual input effects and previous steering outcome before dependent steering.
- [x] Run serial one/two-bot cases on appropriate original maps; inspect weapons/clip/health/kill/respawn and sync (build02; new build03 verification follows).
- [ ] Reproduce each defect, add failing regression, minimally fix, rebuild and retest affected native cases.
- [x] Exercise five independent skills and six personas, preserving explicit unproven cells (build02 axes; no 30-cell native claim).

### Task 3: final qualification and publication

**Files:** `docs/reports/2026-10-30-m2-final-acceptance.md`, sanitized JSON, continuation and this ledger.
**Interface:** Consume final receipts/source/build hashes; produce honest PASS/FAIL/BLOCKED matrix, branch/commit/draft PR.
- [ ] Relevant complete offline regression and source/build provenance verification; independent review.
- [ ] Full criteria audit, resources/rollback/cleanup checks, persistent handoff.
- [ ] Commit, source-only authenticated publication and remote tree verification; retain PR80→81 dependency, no merge.

## Execution ledger

- 13:10UTC fresh host: Ubuntu24.04.4, 3819MiB RAM/no swap, ~2.5GiB available, ~8.7GiB disk, low CPU. Protected Codex/OpenCode/MCP services active; no game or compiler process. main fdfc46e behind remote ab0c740; fetched without changing main.
- PR81 remote889978f is open draft on PR80/619a807. Four local continuation commits74174ca..72580c2 are clean and unpublished, now preserved as this branch's ancestors. Their plan/spec/helper work is reused, not reimplemented.
- Ruling: continue the supplied native QA design inline without another design approval — explicit autonomous mandate. No changed AI source/build yet.
- Additional retained duel01 is externally interrupted; duel02 has wrapper0 and full300s lifecycle result. Reconstruct before new test.
- Fresh42/42 build inputs and415/415 original/restore/archive-member hashes verified; archive SHA matches. M2 core741/tail29/attach35/action43, C1 composition1243/regressions29414 and10 inherited suites PASS.
- Native launcher profile gap reproduced (two failing tests), fixed in e735ae6; all30 generated profiles and invalid/default CLI tested. Original-only mouse-axis probe tested RED/GREEN.
- New finite LittleTrouble300s: clean wrapper/controller0, host guardFINISHED,6/6 unmounts, no sync faults. Actual Colt clip decrease11, original same-entity health100→-20, bot frag0→1, original same-entity respawn100 after guarded normal click. Full M2 remains pending.
- New finite RedStation04 failed original join because I extrapolated the wrong DM_ filename. Compared pinned original preset; corrected to RedStation.wld with failing/passing regression in7f6b3d7. Failure/8 clean unmounts preserved. No AI DLL/source change.
- Added conservative native evidence reducer/tests,40/40 candidate Python checks PASS. Independent follow-up review through56cf70b: no Critical/Important findings; profile gap resolved.
- RedStation05 two-bot300s active: interim original death, bot death/return alive and other bot frag2. Nine150s serial profile-axis cases queued behind its final clean receipt; no concurrent native tests or heavyweight offline suite.
- RedStation05 finished wrapper/controller0, guardFINISHED,8/8 unmounts. Local bot0/index2 death1400→alive1440;198 alive policy rows after return, continued motion/rays but no visible target/fire. Living sensing is not frozen respawn state. Other bot frags2. Resource mean57.532%/peak80.378%, RAMmin1736.586MiB, cgroup719.164MiB, diskmin8.571GiB.
- Initial publication DraftPR82 onPR81, remote660bd5ace1dc1d211d369af548d4237e3075f066 tree3955b8ab352c7c04716e8d4c279f1e0f41a192fe freshly equals local239e617. Native campaign continues; no final acceptance claim.
- Profile06/aggressor,07/survivor,08/controller clean. Remaining nine-case axis campaign ongoing under own controller/private profiles.json. Target/loadout review: extra weapons appear only at unfavourable long ranges so far; no proven weapon selector defect. Original Hole filename/title verified from licensed level archive; explicit whitelist and guard tests RED/GREEN,41 Python checksPASS; prepared only.
- Nine native axes FINISHED, controller0 for all; source/config/actual attach/map/unmount/sync checks all pass. Review found broader evidence in final tier cases: tier1 selects shotgun4, tier3 consumes shell30→29, tiers2/4 spawn distinct owned type0 rockets (Engine107 headerPRT_ROCKET), tier2 original health100→44.7. Marksman/Flaky after own respawn show Colt decreases6/7 and further kills; actual return to combat established. No exact shot or cadence/exhaustion inference.
- Hole15 one-bot300s finished cleanly, but no visible target/fire and one world/fall death; unsuitable floor/spawn separation for gunplay. Original input helper correctly refused a late W request after measurement ended. No safety bypass or world-death concealment.
- Ruling: existing telemetry cannot directly measure all eight finite reserve pools. Add one bounded, read-only BotAmmo line under the existing diagnostics/cadence; no action/policy/server/packet/state change. This requires a new explicitly unqualified MSVC candidate and fresh native checks; old860 evidence retains its old hash scope. Native log statement regression RED2/3 checks, thenGREEN3/3; parser reserve/projectile tests RED3, then44 Python testsGREEN. Core741/29/35/43 and inherited C1/10 suitesGREEN. Sanitizer run active before build.
- Sanitizer completed0 across all six M2/inherited executables. Build03 source c67a06a900db049cac1cc0304860323b069cdb5f:15 MSVC x86 units PASS,42/42 inputs and PE32/x86 verified, DLL a62a19e75251f69207966bb8965c019d8c7e76458099e6eb86bfddc4cb1ee5dd. Only BotDriver.cpp differs from build02; removing the exact bounded diagnostic statement restores byte-identical source. New candidate has no inherited native acceptance.
- Broad offline recheck:291 tools tests (one deliberate native-Wine skip),59 benchmark tests,45 candidate Python tests PASS. Malformed Windows-CRT projectile speeds previously aborted the evidence parser; failing regression then minimal reject-and-continue fix. Parser-only change does not alter the built DLL.
- Fresh build03 native ammo-16: one bot/300s, finite Red Station, tier5/persona2, own display160/port27564, serial lock and all original resource guards. Running; do not infer gameplay acceptance from startup or dispatch.
