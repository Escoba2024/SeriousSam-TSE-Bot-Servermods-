# SSAM.AI – M1–M4 GOAL LEDGER
Updated: 2026-10-26, Hetzner UTC. Public gameserver explicitly disabled by user; do not auto-start.
Worktree: /srv/tse-m1-m4-integration-20261026
Branch: agent/chat/20261026-m1-m4-integration
Baseline origin/main: ab0c7400353a108f8461bb82280c539fdfe81499

| Goal | Status | Verified evidence / remaining gate |
|---|---|---|
| 0 Baseline and consolidation | COMPLETE | Exclusive integration worktree, host/worktree census, user-authorized server shutdown; 415/415 protected files SHA256 MATCH; rollback archive SHA256 MATCH; original DLL hashes checked. Other worktrees remain protected. |
| 1 Synchronization | IN_PROGRESS | Historic P1 four-bot FAIL (5 SYNCBAD). New controlled same-DLL P1 OFF/ON runs documented in docs/reports/2026-10-26-m1-controlled-cecil-native-ab.md; root cause and 60/60/120-minute gates OPEN. |
| 2 Reliability | IN_PROGRESS | Imported C1 PR50-derived ownership/sync/archive fixes into isolated integration source; RED 5/11 then GREEN 11/11 audit; integrated 131 tests, 0 fails/errors, 1 native skip. NOT_DEPLOYED, earlier DLL pin, native restart/hour gates OPEN. |
| 3 Combat AI 2.0 | BLOCKED | PR45 original qualified version exists; PR57/P1 unqualified due four-bot SYNCBAD; PR66 offline only. |
| 4 Navigation 2.0 | BLOCKED | PR69 research-only; no native movement/item integration acceptance. |
| 5 Dynamic Sessions | BLOCKED | AI2 session tests exist; PR68 offline only; no final mixed native acceptance. |
| 6 Integrated candidate | NOT_STARTED | No shared M1-M4 native build. |
| 7 Native final acceptance | NOT_STARTED | 60/60/120-minute duration gates outstanding. |
| 8 Final documentation | IN_PROGRESS | Plan + ledger + continuation; no final report claim. |

## Durable evidence (as of writing)
- User ordered explicit public server shutdown, PID 399158, 399232, 399305; verified ports 25600/25601 free after signals.
- Pre-shutdown receipts: /root/ssam-ai-backups/shutdown-20261026-0033/ (PRIVATE; do not commit).
- Host initial 3.7 GiB RAM, 8.8 GiB free disk; after shutdown 2.7 GiB RAM available; swap 0.
- PR71 SHA 3b06a2a; cherry-pick integrated as 90adf81; test: `python3 -m unittest discover -s tools -p 'test_*.py'` -> 56 OK.
- PR73 SHA c798853 is ONLY in its AI2/P1 ancestry, not merged to main/integration; existing fail-closed metadata guard.
- Private historic native Cecil-P1 four-bot receipt: FAIL, 97.93 seconds, five SYNCBAD; no paired CRC/state/action producer.
- Server hash of unmodified Engine.dll observed: b79bf8bb3927fe4f8f252e141d721ae5c738df02218f0ecc12da5c1afbcb534f.
- Immutable qualified GameMP reference: 61dc27e0e7b80badcf9ae705c30fca88edd3935737715dffff59e90c26f1fef9.
- Reference hashes were checked; full 415-file rollback claim remains to re-verify.

## Next task
Establish exact private P1 OFF/ON preflight using the existing PR73 guarded harness while public server is intentionally offline, then get same-DLL receipts or record explicit resource/producer blocker. Do not confuse pass of comparator with native sync pass.

## Native execution checkpoint – 2026-10-26
- PR73 guarded native private 1-bot P1 OFF: PASS_LIMITED_SESSION_LIFECYCLE, 77.40 s, zero server SYNCBAD.
- master-four-off-20261026: PASS_LIMITED_SESSION_LIFECYCLE, 152.38 s, peak 4, observed server SYNCBAD=0, controller guard=FINISHED.
- master-four-on-20261026: PASS_LIMITED_SESSION_LIFECYCLE, 152.43 s, peak 4, observed server SYNCBAD=0, controller guard=FINISHED.
- Distinguish short healthy native runs from long term stability. M1–M4 remain not finally accepted.

## M1 follow-up audit
- PR73 fail-closed guarded-harness Python suite fresh: `python3 -m unittest discover -s tools -p 'test_*.py'` in `/srv/tse-cecil-guard-20261026` -> 186 PASS.
- Historic P1 four-bot failure and new ON result share exactly the same DLL, visible settings and four-bot peak, but differ in `qualify_bot_sessions.py`; see `docs/reports/2026-10-26-m1-repeatability-review.md`.
- Earlier AI2 eight-bot Build06 PASS_LIMITED is from a different DLL; cannot qualify Cecil P1.
- GitHub PR: https://github.com/Escoba2024/SeriousSam-TSE-Bot-Servermods-/pull/74 (DRAFT). Confirm remote HEAD/tree before modifying it.


## M1 native handler-reachability continuation (2026-10-26)
- Read `docs/reports/2026-10-26-m1-native-sync-handler-probe.md` before further native instrumentation.
- Original 1.07 `Engine.dll` source hash and Wine /proc/maps executable RVA were verified.
- Private native 1-bot count-only: 116.78s PASS_LIMITED, 1,272 actual server handler entries in 20.39s, no Frida error or reported SYNCBAD.
- **Failed interior CMP hook**: experimental native run FAIL with Wine page fault at `0x601a2d57`; no valid CRC pairs; hooks now blocked before attach.
- TDD probe module: 25 checks; total tools suite: 81 PASS. Only handler counting qualified as limited native reachability, NOT server/client action/CRC pair.
- Ruling: prohibit unsafe interior instruction patching until relocation/semantics are independently qualified; preserve public shutdown and 8 GiB disk reserve.
- Next technical goal: safe, attributable action/CRC/state producer or verified alternative data source; do not promote synthetic evidence to M1 complete.


## M1 reliability offline integration checkpoint – 26 October 2026
- Five independent reliability defects reproduced (RED), exact audited fix patch applied to own worktree (GREEN). Evidence: `docs/reports/2026-10-26-m1-reliability-offline-integration.md`.
- 130 tests in combined integration suite (129 passed, 1 native/Wine test deliberately skipped) and 11/11 focused regression tests.
- Imported supervisor still pins historical `7fc94a...` DLL and its original manifest; Cecil P1 `7dc961c8...` has NO native reliability admission. No service installed or started.
- Ruling: keep operations code unactivated and source-pinned to historic candidate until M1 full native validation. A provenance-preserving offline import minimizes accidental change to live game.
- Next safe work: native sync producer validation plus full M1 runtime acceptance, then candidate-specific supervisor binding and bounded isolated crash-recovery tests.

- Additional M1 source-level TDD: absent Dedicated_BotTest.log previously produced sync_scan_complete=true (RED); current integration forces incomplete and blocks safe recovery (GREEN). See tools/test_m1_missing_sync_log.py. Total integrated tests now 131, 130 passed + 1 native skipped.
