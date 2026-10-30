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
- [ ] Run serial one/two-bot cases on appropriate original maps; inspect weapons/clip/health/kill/respawn and sync.
- [ ] Reproduce each defect, add failing regression, minimally fix, rebuild and retest affected native cases.
- [ ] Exercise five independent skills and six personas, preserving explicit unproven cells.

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
