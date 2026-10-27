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
