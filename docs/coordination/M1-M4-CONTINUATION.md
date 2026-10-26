# SSAM.AI – M1–M4 CONTINUATION
Updated: 2026-10-26. User explicitly requested shutdown and autonomous M1–M4 development.

## Resume priority
1. Read this file, docs/coordination/M1-M4-GOALS.md and docs/superpowers/plans/2026-10-26-m1-m4-master.md.
2. Verify actual host and active jobs BEFORE native tests: `ps -eo pid,ppid,args | grep -E 'SeriousSam|DedicatedServer|codex'`; `ss -lunp | grep -E '25600|25601'`; `free -h`; `df -h /`.
3. Check `git -C /srv/tse-m1-m4-integration-20261026 status -sb` and `git log -3 --oneline`.
4. Existing user shutdown receipt: /root/ssam-ai-backups/shutdown-20261026-0033/. Never revive public server without a deliberate choice.
5. Review PR71 integrated 90adf81 and PR73 guard source in `origin/pr-73`. PR73 requires dependent AI2/P1 history, not suitable for blind cherry-pick.
6. Next concrete action: design/verify privacy-preserving original config-pinning A/B receipts and private resource/preflight gate. Private guard has `--offline-public-marker` and `--build-manifest`. If healthy, do native Cecil OFF then ON on same P1 DLL, measuring 4 bots in isolated netns only. Test data stays private outside git.
7. Diagnose first divergent shared simulation tick from genuinely paired client/server action/CRC/state; log-only SYNCBAD cannot prove root cause.
8. No feature M2-M4 promotion until M1 native acceptance. Review existing C1–C4 isolated agent branches without modifying their worktrees.

## Known protected jobs/resources
- Existing Codex app-server on Hetzner remains running: DO NOT stop.
- Control plugin remains active; only game binaries stopped.
- Other working clones include /srv/tse-c1-combat-20261026, /srv/tse-c2-nav-20261026, /srv/tse-c3-sync-20261026, /srv/tse-c4-session-20261026 with uncommitted files. DO NOT overwrite.
- Preserve public runtime /srv/tse-experimental-public-20261025/runtime/eight-165601-zof3t2hr, 3.3 GiB.
- Available disk initially ~8.8 GiB, required floor 8.0 GiB; no unsafe deletion.
- Native private runner requirements: host ubuntu-4gb-nbg1-2, root, private /srv/tse-session-qualification-* path, unique 27000–27998 port, :130–:199 display; global /srv/tse-session-qualification.lock; no public process/port; preflight CPU/RAM/disk. Do not use source script without fully reviewing it and trusted build manifest.

## Known candidate findings
- Cecil P1 DLL: 7dc961c880e0ed68ead13ed4e8299a025be71e05619de36c437c756e964334bf (from PR57; inspect manifest before use).
- PR57 private four-bot failed: 5 SYNCBAD at reported engine tick 99.40..103.40; root cause remains unknown. Read private /srv/tse-session-qualification-cecil-p1-four-20261025/results and C3 report before new tests.
- PR71 comparator is METADATA_ONLY; does not establish live CRC correctness.
- Current tests use `cd /srv/tse-m1-m4-integration-20261026 && python3 -m unittest discover -s tools -p 'test_*.py'`.
- Full release is NOT COMPLETE. No native build or new native tests in this integration worktree yet.

## Rollback and Git
- Branch derives cleanly from origin/main ab0c740. PR71 cherry-pick 90adf81.
- Revert only own integration worktree commits; don't reset main or external worktrees.
- Keep all private logs, raw identifiers, binary retail data out of public GitHub.
- Revalidate originals + backup manifests before any deployment. Production ports 25600/25601 are explicitly offline.

## Pending
Native Cecil OFF/ON controlled run, reliable native sync producer, 1/4/8 acceptance windows, integration of reliability/combat/navigation/sessions, source/build review, final acceptance report and GitHub push.

## Updated checkpoint (2026-10-26)
- Native onebot P1 OFF limited PASS (77.40s); fourbot same DLL OFF/ON results now pinned in docs/reports/2026-10-26-m1-controlled-cecil-native-ab.md.
- Verified 415/415 files in protected manifest SHA match original source + backup tar SHA matches manifest; no files deleted.
- Recheck public ports/generation, other ongoing processes and >8GiB free before next Retail run. Next source task: actual server/client native applied-action/CRC/state producer and first divergent tick; do not assume old SYNCBAD is fixed by one short control.

## GitHub / additional QA update – 2026-10-26
- GitHub draft PR #74 holds this isolated master integration source; branch `agent/chat/20261026-m1-m4-integration`; first published commit `82a7973751ad0b3d54b2582e04fc6fa4dc21b8a8`. Direct git HTTPS push from Hetzner lacks credential; use connected GitHub connector, verify exact Git tree equality before publication.
- Local isolated worktree was safely aligned with published branch AFTER identical Git tree verification. Old local history is preserved in `agent/chat/20261026-m1-m4-pre-github-reconcile`.
- PR73 Python suite: 186 PASS; PR71 integrated comparator 56 PASS. New short native four-bot OFF/ON both PASS_LIMITED. These are not long-term acceptance.
- Read `docs/reports/2026-10-26-m1-repeatability-review.md`; historical native P1 FAIL and new short PASS have a different `qualify_bot_sessions.py` source hash. Do not infer cause.
- Immediate engineering step: seek authoritatively paired Retail 1.07 client/server applied actions+CRC/state around first divergent tick, with original engine hash, connection epoch, uninstrumented control and private logs. Do not manufacture CRC data from aggregate BotTelemetry or PR58/PR65 synthetic models.
- User ordered shutdown; public game server remains offline. Before any private test recheck resource/headroom, all processes and 8 GiB disk floor; do not change foreign worktrees.


## M1 handler debug continuation (2026-10-26)
- Pinned original Engine SHA: `b79bf8bb3927fe4f8f252e141d721ae5c738df02218f0ecc12da5c1afbcb534f`, actual Wine mapping base determined from private `/proc/PID/maps`; Frida Linux Process.enumerateModules/getModuleByName does NOT list the mapped PE Engine.dll.
- Handler-only Frida count at RVA `0x000e2d10` is proven reachable in a single-bot private Retail 1.07 run: 1,272 calls / 20.39 seconds, zero probe errors, native run 116.78s PASS_LIMITED, observed server SYNCBAD=0. This is NOT CRC causation or longer session stability.
- High-risk instruction-level hooks at `0x601a34b2` and `0x601a34ca` led to Wine page fault at `0x601a2d57` and failed private Retail run (query uncertainty >15s). Published probe now rejects `--comparisons` *before attaching*; do not repeat unsafe approach without an alternative reviewed design and fully owned test.
- Local private artifacts: `/srv/tse-session-qualification-master-sync-20261026`, `...master-sync-v2-20261026`, `...master-crc-20261026`; private controller logs under `/root/ssam-ai-backups/shutdown-20261026-0033/`. Never publish raw evidence.
- Next task is a differently qualified native applied-action, CRC and state capture across BOTH sides with authoritative tick+connection epoch; no M1-M4 final acceptance yet.
- Run `cd /srv/tse-m1-m4-integration-20261026 && python3 -m unittest discover -s tools -p 'test_*.py'` and verify current repo/GitHub branch before work.


## Reliability handoff – 26 October 2026
- Imported C1 source modules and exact patch into `tools/operations/`; source SHA checks and portable tests are in `docs/reports/2026-10-26-m1-reliability-offline-integration.md`.
- Imported four `tools/test_*operations*.py` suites and C1 audit; direct 5 RED before patch and 11 PASS after patch. Combined 130 tests, 0 fails/errors, 1 native test skipped to preserve public/private runtime.
- Not installed/activated. Simulator/test-only code; historical Build04 DLL SHA is hard pinned and must NOT be reassigned to unqualified P1.
- To rerun safe suite: import test_operations_live_recovery, set method `test_native_absent_server_wait_with_remaining_process.__unittest_skip__=True`, discover `tools/test_*.py`; do not invoke the native method without owned isolated preflight.
- Reverify source identity and public shutdown on every resume. Continue M1 action/CRC producer work without native Frida interior cmp hooking.

- Additional supervisor issue fixed: NO server SYNC log is NOT a clean scan. Current branch's health module differs from C1 patch result by a single safe complete=False default, with reproducer tools/test_m1_missing_sync_log.py (RED→GREEN). Current integrated tests 131 run, 0 failures/errors, 1 native skip. No service installation or activation.

## Active M1 completion work
Native one-hour run may still be active: inspect /srv/tse-session-qualification-master-m1-one-hour-20261026/result.json and host-guard.json before starting any test. Guarded source remains /srv/tse-cecil-guard-20261026; unchanged P1 DLL 7dc961c8. Private evidence/policy/configs under /root/ssam-ai-backups/m1-completion-20261026-0155/. New producer tools/native_sync_snapshot.py safely captured paired exported-function CRC/action observations (see docs/reports/2026-10-26-m1-export-snapshots.md). Do not instrument duration acceptance runs. Use tools/m1_duration_acceptance.py to verify actual uninterrupted full population, preserved process generations, logs/telemetry, original control, final resource guard and cleanup. Old supervisors still pin legacy 7fc94a; NO unqualified P1 admission. Continue full 1/4/8 duration gates and native candidate-bound recovery before declaring M1 complete.

### Autonomous native qualification controllers (M1)
- Private serial duration controller: /root/ssam-ai-backups/m1-completion-20261026-0155/run-duration-matrix.py. PID receipt duration-matrix-controller.pid; status duration-matrix.json; log duration-matrix-controller.log. It validates each stage before starting the next, never publishes/deploys and keeps M1 complete=false.
- Waiting fault controller: run-recovery-qualification.py; PID recovery-controller.pid; status recovery-qualification.json. It cannot start until all duration receipts are accepted and revalidated. Then original-cooldown onebot owned-client fault/rejoin (1500 s), eightbot owned server fault, verified teardown, 30-second cooldown and one fresh eightbot private generation (420 s). No unknown/human/sync/pressure recovery. Public runtime remains disabled.
- Before touching any runtime: inspect both status files and running controller PIDs; DO NOT create competing native tests or stop these owned qualification jobs.
- Latest original/rollback verification: 415/415 protected files match, archive SHA matches, qualified 61DC DLL preserved (private originals-rollback-reverified.json).
- Scope caveat: tools/m1_recovery_gate.py is isolated qualification admission, not public production activation; existing operations supervisor retains historical 7fc94a pin. All M1 criteria and release review must be reconciled with actual native receipts before completion.
