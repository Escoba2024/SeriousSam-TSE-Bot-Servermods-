# M1 optimized producer duration matrix and completion

> Use superpowers:executing-plans. User explicitly requests work through completion, with autonomous routine decisions.

**Goal:** Complete source-pinned1/4/8 native duration matrix, candidate-bound recovery and M1 review before native M2-M4 promotion.
**Architecture:** Reuse unchanged optimized native producer and reviewed hardened support primitives. New thin serial matrix controller owns exact private stages and policy, direct-child pidfd handles, bounded heartbeat/cleanup, common lock and independent census. No old receipts/policies overwritten.
**Spec:** M1-M4 master plan and current AGENTS; user completion instruction.
**Global constraints:** Original binaries unchanged; ser_iKickOnSyncBad10; RAM>=768MiB, disk>=8GiB, CPU guard unchanged; no public deployment; no competing native tests; m1_complete remains false until all gates reviewed.

### Task1: serial matrix controller
Files tools/run_prefilter_duration_matrix.py, tools/test_prefilter_duration_matrix.py.
Interfaces: consumes exact pinned producer/support/configs and private policy; produces separate perstage receipts and a matrix with actual evaluated verdicts.
- [ ] RED regression checks for missing/drifted pins, exact1/4/8 stage set, full required durations, candidate/source mismatches, no implicit native actions.
- [ ] Implement thin wrapper using audited budget/heartbeat/owned abort/census primitives; no native source edits.
- [ ] GREEN wrapper + inherited suites; independent read-only review before execution.
- [ ] Commit controller and plan. Create private immutable source/config/candidate policy and dry-run preflight.

### Task2: native gates
- [ ] Fresh1bot3720s/3600 continuous;4bot3840s/3600;8bot7680s/7200, exact same optimized producer.
- [ ] Validate every stage from actual full logs/telemetry/guard/census; stop progression on failure; no retries without diagnosis.
- [ ] After accepted matrix qualify owned client/server failure, teardown and recovery with same candidate/source pins.
- [ ] Reconcile root-cause evidence, plan and native gates; independent final M1 review; never claim missing measurements.

### Task3: M2-M4
- [ ] Review offline combat/nav candidates, resolve native source seams, integrate opt-in features one at a time.
- [ ] Build candidate, qualify gameplay, mixed sessions and final1/4/8 acceptance; preserve perbuild/source receipts.
- [ ] Publish source/tests/reports via GitHub and verify exact tree equality, no retail/raw data.

## Ledger
- Confirmed original worktrees protected, no active native game jobs,8.3GiB free and2.8GiB RAM available at18:03UTC.
- Separate combat/nav workers own isolated branches only. Parent owns shared runtime and integration.
- Existing one/four native passes are historical producer evidence, not relabeled as optimized producer acceptance.

- Matrix source TDD: missing controller RED; contract6GREEN; independent prelaunch review found under-lock freshness race and missing bounded wait for unreadable live receipt. Lifecycle RED4 failures reproduced; corrected then13GREEN normal/-O.
- Ruling: ambiguous malformed receipts retain bounded wait without extra signal; absent authoritative cleanup evidence persists HOLD even if outer exits. This is stronger than a generic BLOCKED state and prevents unsafe automatic progression.
- Source scope is unchanged15 producer/support inputs plus separately pinned candidate/config/marker artifacts. No runtime source patching during tests.

- Initial native optimized1bot trial aborted258.903s by unchanged CPUguard. Last3 hostbusy samples99.700/99.801/99.900%; RAM2085.8MiB, disk8.261GiB. Additional portablecompiler/test work overlapped; no native syncfault conclusion. Cleanup and independent census clean. Failedpolicy/receipts/source copy retained privately.
- Ruling: strict serial compute phases. No portablecompilation/bench/Winebuild during duration matrix; source inspection and short Python unitchecks only. Both offlineworkers complete. Deliberate idle-r2 retry uses new exact roots, policy andmatrix; original failedreceipt not overwritten.
- Recovery preflight review found raw-PID termination on binding failure and missing SIGTERM cleanup handler. RED2 regression errors reproduced, replaced with prebinding tracking/bounded wait/census and cleanup-state signal handler. Faulttests still require accepted exactmatrix and independently pinned original faultproducer.

## 27 October M1 continuation: measured monitor CPU overhead
- [x] Current Drive/GitHub/live census; same-tree remote/local reconciliation. main ab0c740; PR75 head4e959ad; localbf2bbfb has byte-identical tree to4e959ad. Preserve both histories; own branch agent/chat/20261027-m1-monitor-cost from published4e959ad.
- [x] idle-r2:1bot3700.687s and4bot3762.257s accepted.8bot stopped after3748.102s, fullpopulation3582.551s, CPU87.538/86.996/86.465%, RAM>=1049.7MiB/disk>=8.155GiB; clean census, recovery correctly blocked.
- [x] Short preserved-log profile: matching0.16CPU s/pass, double full log reads0.13s/pass. Native game CPU falls119.01 to110.32% of onecore; no proven hardware exhaustion.
- [ ] RED performance acceptance <=65% original matching cost on same private preserved corpus; existing semantic unit tests as regression gate.
- [ ] Collapse conservative prefilter anchors only; preserve exact original regex/identifier/flags, no caching/incremental omission, full log scans every tick. GREEN equivalence suite and native integration contract; independent review.
- [ ] Fresh immutable idle-r3 source/policy/roots; unchanged DLL/config/CPU85 guard/RAM768/disk8. Repeat1/4/8 because helper dependency changed; preserve allold receipts.
- [ ] Native recovery after accepted new matrix, final independent M1 release review, GitHub/Drive record.
Ruling: keep original qualifier/observer/game configuration unchanged; reduce measured matcher cost conservatively. No new architecture or M2-M4 promotion.

- Measured first7anchor attempt failed fullregex fallback on routineerrors/symbols; rejected. Actual8anchor candidate paired median0.58955 oldcost passes<=0.65 acceptance. Retained failed/absolute/paired receipts; no fabricated GREEN.
- Independent diff review found no blockingissue; actual8anchor delegation and routinefalsepositive tests added. Full performance72 normal/-O, tools242, focusedprofile19-O. DLL/gameconfig/protection unchanged. aptdownloadcache cleared; disk8.58GiB.


## 28 October 2026 — autonomous M1 completion, controlling execution update

**Owner:** main agent, branch `agent/lead/20261028-m1-completion`, isolated worktree `/srv/tse-m1-completion-20261028`, baseline PR78 `93a2849aa096031eaf47ef3b6a0570d3ebeb0b9a`.
**Execution:** writing-plans + executing-plans; execute routine work without intermediate approvals as explicitly requested. Existing Task3 M2-M4 is deferred until M1 acceptance. No new planning file.
**Spec:** user M1 completion task dated 28 October; `AGENTS.md`, toolchain policy, native acceptance contracts and this plan. User duration requirements are 1/3600s, 4/3600s, 8/7200s continuous full population. CPU>=85% for three consecutive existing guard samples aborts, RAM floor768MiB, disk floor8GiB; keep monitor intervals, population/activity checks and sync enforcement unchanged.
**Starting state:** GitHub main `ab0c740`, local main `fdfc46e` clean/behind6. PR74→75→76→77→78 open drafts, serial ancestry. r3 matrix BLOCKED at eight bots; one3701.053s/four3762.538s accepted only under original r3 pins. Eight unfinished; recovery never started. Public game absent in process/UDP census; unrelated Xvfb :139 and persistent runtime overlays protected. Foreign dirty worktrees inventoried and left untouched. Root cleanup commit2ba50e2 exists in separate Git object store; publication and independent protection proof outstanding. Disk initial9509568512B=8.857 GiB, availableRAM2632777728B. Evidence private under `/root/ssam-ai-backups/m1-completion-20261028/`.

### Task4: verified inventory and Issue79 reconciliation
Files: existing continuation/goals; `docs/reports/2026-10-28-m1-completion-audit.md`; prior Issue79 cleanup report imported with attribution.
- [x] Verify actual host, GitHub PR74-78/issue79, main and current process/service/lock/mount/resource state.
- [ ] Inventory all Git stores/worktrees/local changes; classify metadata damage before any repair. Verify cleanup commit, exact deletion report, protected originals/backup hashes and rollback restore-copy.
- [ ] Record current bytes/GiB, floor and target separately; no deletion unless safe cache individually classified. Close79 only when complete evidence is published and reviewed.
Acceptance: reproducible census, >=8589934592B free, protected inventory verified, documentation arithmetic corrected with source preserved. Main owns operations; independent review is read-only.

### Task5: integrated offline baseline and measured CPU correction
Files: existing performance matcher/native producer/support and their regression tests; only edit after measured cause identifies responsible file.
- [ ] Run inherited tools suite on integrated PR78, isolate historical environment failures without weakening production safety. Native CLI test explicitly excluded until owned preflight; report skip.
- [ ] Aggregate preserved r2/r3 CPU/RAM/disk/log-growth and per-process/cgroup measurements. Read-only specialist may analyze independently, no runtime operations.
- [ ] Reproduce measured bottleneck on preserved corpus; write behavior regression first, minimal correction, verify semantic equivalence and paired CPU evidence. No threshold/interval/population/simulation-rate change.
- [ ] Commit exact integrated source and independent review before native execution; prepare immutable new policy with exact sources/config/build/original pins. If unchanged producer permits historical reuse, prove full provenance; otherwise fresh entire matrix.
Acceptance: green relevant suites, documented measurements, existing safety guards unchanged, no competing heavy tasks during native windows.

### Task6: source-pinned serial native duration matrix
Files: existing `tools/run_prefilter_duration_matrix.py`, `tools/m1_duration_acceptance.py`; fresh PRIVATE policy/evidence roots only.
- [ ] Fresh per-run census/lock/namespace/ports/storage/rollback preflight; validate dry-run and immutable sources.
- [ ] 1 bot>=3600s, then4>=3600s, then8>=7200s continuous full population, same candidate/config/producer. Evaluate every receipt plus fresh independent process/mount/cgroup census before progression.
- [ ] Record activity, GameSpy, exact generations, full logs, telemetry, CPU/RAM/disk, sync, original observer and cleanup. Any guard breach stops; diagnosis required before retry. No instrumented duration acceptance.
Acceptance: all three actual receipt verdicts accepted and independently revalidated; no unexpected sync/disconnect/crash/population gap. No M1 completion from duration alone.

### Task7: native recovery and complete supervisor qualification
Files: existing `tools/qualify_prefilter_m1_recovery.py`, `tools/qualify_existing_supervisor.py`, `tools/operations/*`, focused tests. Reuse existing Runtime.
- [ ] Accepted-only candidate-bound canonical client/server fault qualification with owned identity handles and clean cleanup.
- [ ] Native existing-supervisor baseline, duplicate controller, generation/epoch/wrong PID safety, guest/unknown slot HOLD, stale health/query, restart persistence/backoff/circuit, closed-writer archive/log threshold maintenance, controlled restart and cleanup tests.
- [ ] Qualify fully healthy following generation>=3600s, then preserve source/artifact receipts and originals check. Implement missing native probes with regression tests before execution; mock evidence remains offline only.
Acceptance: every named native gate proven, no foreign signaling/adoption, no public operations, unchanged guard limits. Existing qualifier CORE verdict explicitly leaves deferred gates open until separately proven.

### Task8: independent integrated QA, rollback and final disposition
Files: existing reports, continuation and goals, minimal source fixes if independent reviewer identifies defects.
- [ ] Independent whole integrated diff and evidence review, regression/integration/security checks on actual final target version. Main implements fixes RED→GREEN and repeats relevant verification.
- [ ] Restore-copy/hash rollback proof, protected original inventory and fresh GitHub/branch state.
- [ ] Commit sanitized reports/source, publish own reviewable branch/PR with exact tree check. No main merge or public activation implied.
- [ ] Reconcile every user M1 checkbox; COMPLETE only if all pass. Else specific IN_PROGRESS/BLOCKED with evidence and precise continuation. Record M2/M3/M4 as deferred/unqualified.
Acceptance: no open M1-P0, source/build/config/runtime provenance complete, native matrix/recovery/safety and independent QA accepted. All evidence persistent; raw logs/binaries/secrets stay private.

## 28 October execution ledger
- Census saved privately as `initial-census.json`. No active Wine/game/matrix/fault processes found; shared native lock not held. Public disabled; third-party services untouched.
- Ruling: latest explicit user instruction authorizes fresh private eight-bot work, superseding PR78 historical defer note. It does not authorize public startup or guard weakening.
- Task4→5: verified disk/originals/rollback are preconditions for native work; Task5→6 exact producer pins decide historical reuse; Task6→7 accepted-only admission; Task7→8 complete native receipts are mandatory. No conflicting interfaces identified yet.

- Independent storage audit: all3Gitstores valid, no repair.415/415 original+restore+tar bytes MATCH, archiveSHA MATCH. Cleanup report arithmetic/proof gaps prevent unconditional Issue79 closure; current8.842GiB floor passes,9GiB target unachieved. No deletion.
- Task5 baseline288run/287PASS/1nativeWineCLI skip. Root avoids historical permission-fixture failures; no production safety changed.
- Selected measured correction: stateless chunked join-existence check, no cached state. Full error logs and guard/intervals untouched. Seven behavioral tests RED→GREEN; performance79 normal/-O GREEN. Paired preservedr3 median predicateCPUratio0.0114239. Fullreader prototype retained privately but not integrated.
- Ruling: modified native producer requires fresh entire matrix; new campaignm1-joinsearch-matrix-20261028-r1, unique roots/27210,27214,27218/:170,:171,:172. Old receipts/policies unchanged. Supervisor/recovery profiles rebound explicitly; no automatic fault execution before accepted matrix.

- Independent pre-native review found chunk-search late-I/O-error omission. ReproducerRED (OSError not raised); final selection complete binary UTF8 marker search with original decoder fallback. Allbytesstillread; no suppressed scans. Final7paired predicateCPUratio0.06811433. Priorchunkprototype superseded, not deployed.
- Ruling: short8bot native diagnostic before fullmatrix to obtain missing wineserver/controller/cgroup/hoststeal attribution; it cannot satisfy duration acceptance. Supplemental read-only sampler has own hash/evidence, no signal/control authority, unchanged original hostguard.

### 28 October08:34UTC — BLOCKED at actual RAM admission
Source6a32f10 native600sdiagnostic stoppedafter124.975s at6bots:1039.3MiBavailable<1068launchgate. Originalguards unchanged. CPUmean51.679/peak82.661% includesstartup/cleanup<=6bots; no8botCPUclaim.20/20unmounts, noownedprocess/mount,cgroupempty. Disk9461497856B>=8GiBfloor,<9target.0syncmarkers in8actualgamelogs isshortpartial-only. No freshmatrix orfault/supervisor test started; currentcampaignpolicy remainsunexecuted. Additionalcapacity decisionpending; no protectedservice stop, billingaction oridenticalretry.
Supervisorqualification sourcefix: oldgenerationarchivedgamelogs fullyscanned; observednativeSYNCfaultlatch persistsacrossgenerations. RED8cases→23focusedGREENnormal/-O; integrated291run290PASS1nativeWineCLIskip. Remainingnativeprobesnotimplemented/accepted. See2026-10-28-m1-completion-audit.md andcapacitydecision. M1BLOCKED;M2-M4deferred/unqualified.

- Fresh independent final-changeQA:55focusedPASS/68optimizedPASS, noCritical/Importantfindings; docsallocationclaimcorrected. Reviewer explicitly leavesfullnative8/duration/recovery/supervisor/M1QA andhistoricalcleanuprawproofunjudged. This isdraftreadiness, notM1acceptance.
- GitHubcleanup2ba50e2 exactfetch422NoCommit;localrootcommitexists. Issue79remainsopen.
- Task6nativeprogressBLOCKED byRAMbefore7; Task7newnativeexecutionBLOCKED. Task8ownchangeQAcomplete,fullM1QAopen. Awaitcapacitydecision; do notretryorstartfreshmatrixuntilnewcensusprovesadmission.
