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

### Canonical recovery source and review fixes
The canonical fault qualifier is now tools/qualify_m1_recovery.py. Default invocation/import is side-effect-free; native work requires explicit --execute on the authorized host/evidence root. After final source tests its waiting controller replaces the earlier private script; inspect recovery-controller.pid and recovery-qualification.json for actual state.
Independent review found (and corrected) an argv JSON object/array conflict, a vacuous/incomplete duration-matrix admission and missing active-child cleanup wiring. The qualifier builds only pinned native argv, requires the exact 1/3600 + 4/3600 + 8/7200 matrix, binds each direct child through pidfd and uses bounded finally cleanup plus an independent resource census. The initial string edits failed to wire two guards; actual source was normalized and patched with asserted replacements/AST transformation before execution. No fault test was started during these fixes.
Bounded native JSON receipt reads now retry truncate/write races without stale-state fallback; source and reader SHA are pinned in the private duration policy. Active native duration process/source unchanged.
39/39 candidate build-source hashes and candidate DLL SHA were freshly reverified. The onebot running engine's effective ser_iKickOnSyncBad was passively read as original value 10; no hooks/state writes.


## Chat continuation: diagnostic validator repaired, 26 October 2026
Own isolated branch/worktree: agent/chat/20261026-m1-diagnostic-fix, /srv/tse-m1-diagnostic-fix-20261026, from committed Manus base 4c20198. Original integration has uncommitted CRC work: do not overwrite. Manus worktree remains untouched.

Read docs/reports/2026-10-26-m1-diagnostic-reassessment.md. The original 25-minute eight-bot probe stopped with final-validator error, while native result and guard passed. Corrected optional max_log_mib contract (32 default, exact int1..128) accepts preserved evidence in a separately pinned retrospective receipt: 1,331.624 s full nine-slot population, all eight healthy20Hz bot roles, zero sync markers across10 complete logs, clean fresh census. Original BLOCKED/history/policies remain unchanged. Diagnostic-only, NOT M1 duration acceptance.

Verification: performance69 PASS normal and optimized; tools220 run/219 PASS/one native skip; independent read-only review clean. No binary/service/public-runtime change. Next: same-provenance prefilter duration1/4/8 matrix, candidate-bound recovery, sync root-cause/release review. Inspect active jobs and disk8GiB floor before any new test.


## Active autonomous completion: idle-r2 matrix and integrated offline candidates
User ordered work through completion. Own branch agent/chat/20261026-m1-diagnostic-fix; matrix runtime and policy remain private.

- First new onebot attempt aborted258.903s on three hostCPU samples99.700/99.801/99.900%, during overlapping portablecompile/test work. RAM2085.8MiB/disk8.261GiB; independent final census clean. This is not a syncfault diagnosis. Failed receipts and original matrix source preserved in /root/ssam-ai-backups/m1-prefilter-matrix-20261026-1803/.
- Deliberate idle-r2 source/policy/roots are new; no prior receipt overwritten. Source-root profile is exact1/3720/3600 +4/3840/3600 +8/7680/7200. No portablecompilation, benchmark or nativebuild during this matrix.
- Active matrix: /root/ssam-ai-backups/m1-prefilter-matrix-20261026-idle-r2/matrix.json. Controller-start.json binds PID/startticks; policy.sha256 and policy.json pin15 producer/support inputs plus config/manifest/candidate/disabledmarker. Inspect actual state before any runtimeaction. Shared original matrix.lock and native qualificationlock prevent overlap. Public server remains disabled.
- Source matrixcontroller9498f75501d6190fe2e42db77d50eb281e35ec8559ffe343fd41b977e57a176a; policy759d6a09948b62ca970de39e39cf414fd0caac349fc2c78369bca9c39fae520c.
- Next after accepted matrix: tools/qualify_prefilter_m1_recovery.py --evidence-root /root/ssam-ai-backups/m1-prefilter-matrix-20261026-idle-r2 --execute --matrix-policy-sha256759d6a09948b62ca970de39e39cf414fd0caac349fc2c78369bca9c39fae520c (supply hash as a separate argv value). Do not run before verifying exactmatrix and source/legacy policy pins. Duration uses optimized producer; fault qualification deliberately preserves separately pinned legacy producer and sameP1DLL. Never relabel inventories. No fault test started yet. Recovery binding failure retains unbound child for bounded wait/census, repeated signals are suppressed in cleanup, persistent recovery-HOLD/freshness prevent unsafe retries.
- Combat fixes integrated commits7cfa578/d639dcb from6363889/d012fbac; nav source integratedd50b8c3 from6c18b51. These are OFFLINE source only. Preserve flags and kNativeNotQualified. Reports under docs/reports/combat-completion-20261026/ and nav-completion-20261026/.
- Combat portable evidence29414 regression/1243module assertions,21600 unchanged off-corpus rows,10 inherited binaries, native-tail/resetbranch smoke; nav29completion/404controller checks, inherited suites/sanitizers/compatibility/cross-C1 ownership. Parent did not repeat heavy tests during native matrix. Source-only cherry-picks preserve tested bytes.
- Python suite241 run/240PASS/one documented competing native test skipped at26cbe16; recovery freshness subsequently6focusedPASS normal/-O. Sourcebuilder now accepts a validated complete --source-overlay; no new DLL built.
- Unqualified composed flat source /srv/tse-composed-source-20261026 was materialized with exactPR57/PR66pins. Do not deploy it. Build source overlay only outside measurement windows.
- M3 nextnativeprobe must verify existing107eye/entity placement,8ammo counts/capacities,infiniteammo and world/entity metadata. No waypoint graph/native item eligibility or foot-height contract is established; do not manufacture those facts or call native snapshots fixtures.

Idle-r2 launched 2026-10-26T19:23:36.067080+01:00; actual status at checkpoint NATIVE_DURATION_RUNNING.

## 27 October M1-only continuation
M1 IN_PROGRESS. idle-r2 BLOCKED by threeCPU>=85 samples after8bot3748.102s/3582.551s fullpopulation;1/4 accepted3700.687/3762.257s against oldpolicy. Recovery notstarted. No public game runtime.
Measured conservative matcher correction: paired medianCPUratio0.58955; unchanged originalregex/fulltext/Identifier/flags/DLL/gameconfig/85guard. New source requires fresh idle-r3 matrix, no oldreceipt relabeling. See docs/reports/2026-10-27-m1-monitor-cost-and-duration.md and existing prefiltercompletionplan.
Private evidence/policy: /root/ssam-ai-backups/m1-prefilter-matrix-20261026-idle-r3/; diagnostic benchmark/failures /root/ssam-ai-backups/m1-monitor-cost-20261027/. Before runtimeaction inspect actualmatrix/process identity/locks. Final M1 native/recovery/release review stillOPEN.

## 28 October autonomous M1 completion checkpoint
Own worktree `/srv/tse-m1-completion-20261028`, branch`agent/lead/20261028-m1-completion`, basePR78`93a2849`. User now authorizes privateeightbot work; historical defer superseded. r3finishedBLOCKED,1/4historicalaccepted,8CPUfailed2665.992s; recoverynotstarted. Freshsource requires all1/4/8gates. Existing plan`2026-10-26-m1-prefilter-completion.md` Tasks4–8 controls continuation. New campaign`/root/ssam-ai-backups/m1-joinsearch-matrix-20261028-r1/`, inspect actualprocess/receipt/locks before runtime. CPU correction completebinaryUTF8joinmarker lookup, full error scans/intervals/guards unchanged. Native diagnostic and freshmatrix/recovery/supervisor stillpending. Backup415/415 originals/restore/archive verified; disk>=8but<9GiB. Issue79 arithmetic/proofgaps retained, no extra deletion. M1IN_PROGRESS;M2–M4deferred/unqualified. See`docs/reports/2026-10-28-m1-completion-audit.md`.

### 28 October08:34UTC — BLOCKED at actual RAM admission
Source6a32f10 native600sdiagnostic stoppedafter124.975s at6bots:1039.3MiBavailable<1068launchgate. Originalguards unchanged. CPUmean51.679/peak82.661% includesstartup/cleanup<=6bots; no8botCPUclaim.20/20unmounts, noownedprocess/mount,cgroupempty. Disk9461497856B>=8GiBfloor,<9target.0syncmarkers in8actualgamelogs isshortpartial-only. No freshmatrix orfault/supervisor test started; currentcampaignpolicy remainsunexecuted. Additionalcapacity decisionpending; no protectedservice stop, billingaction oridenticalretry.
Supervisorqualification sourcefix: oldgenerationarchivedgamelogs fullyscanned; observednativeSYNCfaultlatch persistsacrossgenerations. RED8cases→23focusedGREENnormal/-O; integrated291run290PASS1nativeWineCLIskip. Remainingnativeprobesnotimplemented/accepted. See2026-10-28-m1-completion-audit.md andcapacitydecision. M1BLOCKED;M2-M4deferred/unqualified.
