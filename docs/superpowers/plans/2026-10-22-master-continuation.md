# Alpha-Gaming: Hetzner phase completion implementation plan

> **For agentic workers:** Use superpowers:executing-plans task-by-task. Preserve the existing PR46/PR49 plans and evidence; this is their continuation, not a replacement qualification.

**Goal:** Investigate external sync failures, qualify and integrate reliability changes when their actual gates pass, then assess individual sessions and two-server capacity.

**Architecture:** Retain Build04 and the public eight-bot fleet. Develop in `/srv/tse-master-20261022`, branch `agent/lead/20261022-phase-completion`, based on published PR49 `5b0157f`. Use private resources and an exclusive local lock for any new native run. The production monitor remains read-only until a verified reversible migration.

**Tech Stack:** Ubuntu/Wine/Retail 1.07, Python standard library, systemd, existing MSVC under Wine if a DLL change becomes necessary.

**Spec:** User master task 22.10.2026; existing `2026-10-21-reliability-operations-design.md`, PR46 next-phase plan and PR49 review plan.

## Global constraints
- Hetzner `ubuntu-4gb-nbg1-2` / `91.99.75.33` only. No Windows/Shadow or additional paid resources.
- Public original processes, human players, original binaries, protected 61DC candidate, Build04, backups and foreign worktrees remain protected.
- No synthetic test, old source test, query snapshot or boot rehearsal substitutes for new native runtime, active Originalclient, external network, real reboot or 24/7 evidence.
- No force push, blind merge, raw-log/profile/GUID/binary publication, sync-check disablement or uncontrolled restart.
- User explicitly authorizes continuous execution, commits/pushes and qualified merges; routine skill design/plan approval pauses do not apply.

## Review focus
1. Repeated stop after all Wine processes and overlay mounts are gone must succeed without hiding genuine Wine errors.
2. Health collection must not age a fresh UDP query through expensive whole-log scans; historical sync faults stay visible.
3. A wildcard private query listener requires a proven ingress isolation gate.
4. External sync events do not establish client blame, network-loss causality, or an identified divergent simulation state.
5. No new fleet/recovery may consume the host reserve or evade human/foreign-process holds.

## Task 1: Inventory and P0 sync evidence
Owner: lead; dependencies: none. Files: own report `docs/reports/2026-10-22-master-inventory-sync.md` and sanitized JSON. Private evidence under `/srv/tse-master-evidence-20261022`.
- [x] Verify host/IP; refresh main; inspect PR45–49, processes, worktrees, dirty files, health and resources.
- [x] Baseline PR49 suite: 77 Python tests PASS.
- [x] Verify retained 415-file backup, active original/Build04 pins; snapshot current production configuration and source pins privately.
- [x] Stream server sync events with a bounded capture boundary; separate historical groups, own/external peers, disconnects and newly appended events. Record first/last divergence ticks and available metadata without publishing identities.
- [x] Compare current native-hour evidence and source hashes; distinguish qualifier PASS from outer cleanup FAIL.
- [x] Report actual root-cause limits and next reproducible experiment. Commit sanitized report.

- [ ] Additional P0 control after the exclusive native hour/cleanup: original Wine client + one bot,300s baseline and300s isolated netem; preserve real CRC outcomes and verify namespace cleanup.

## Task 2: Resolve demonstrated reliability regressions
Owner: lead; depends on Task1. Files: `tools/operations/fleet_supervisor.py`, `fleet_health.py`, focused new regression tests, existing PR49 report/plan in this worktree only.
- [x] Reproduce closed-prefix duplicate-stop failure and any additional safety findings as failing behavior tests.
- [x] Implement minimal fail-closed corrections; retain real command errors and human protection.
- [x] Reproduce targeted operations tests and complete root Python suite, benchmark tools and relevant C++ regressions. Review diff and commit.

## Task 3: Native supervisor qualification and integration
Owner: lead; depends on Task2; private resource exclusivity mandatory.
- [x] Check live processes/ports/mounts and host reserve immediately before starting; acquire local exclusive test lock.
- [ ] Native double-start, client/server loss, controller adoption, repeated stop, retry circuit, foreign process/window and human/unknown-query holds, log/archive/resource gates, Wine/Xvfb failure; distinguish fixtures from native tests.
- [ ] New >=3600-second Retail-1.07 eight-bot test for final code, original-client compatibility, complete logs/action telemetry, CPU/RAM/disk and private cleanup. Continuous public safety monitoring.
- [ ] Fresh independent review of final diff. Integrate #49 into #46 only when qualifying gates pass. #46 to main only when its complete gates pass. No production recovery enabled on an incomplete gate.
- [ ] Verify monitor rollback and live safety before any deployment; no host reboot during active play.

## Task 4: Sessions, resources and scaling
Owner: lead; depends on reliability qualification for execution changes. Reuse PR47 sources/evidence; do not reimplement its planner.
- [x] Verify PR47 identity/session evidence and run its portable tests in a separate reviewed snapshot if needed.
- [ ] Analyze measured per-process/cgroup RAM and CPU from retained PR47 and PR49 samples; test only justified safe optimizations.
- [ ] Evaluate two servers × eight grouped bots separately from eight individual session clients. No public second server without actual reserve and visibility gates.
- [ ] Document hardware/resource recommendation if existing capacity gate cannot pass; do not order hardware.

## Progress / handoff
2026-10-22 21:42 UTC: Task1 in progress. Public query 8/16, bots8, humans0; own SYNCBAD0/external105; monitor BLOCKED (QUERY_UNCERTAIN, historical external sync, log hold). Two production clients ~201 MiB RSS each, host MemAvailable ~2274 MiB, root free ~14.3 GiB. Existing native PR49 qualifier 3600.0039s with 648 samples passed; outer duplicate-stop failed. Foreign PR46 worktree has four dirty artifacts; foreign QA plan has an uncommitted result update: preserve both. No production changes.

2026-10-22 21:58 UTC: Task2 source fixes verified85 root/59 benchmark tests, C++ regression/smoke including555 Human-AI checks. Fresh independent review findings corrected through RED/GREEN. PR50 published b5a6cba, identical tree to local proof; direct shell credentials unavailable, GitHub connector publication works. Private final-source R2 double-start/client recovery/controller adoption/server recovery/six-unmount gates PASS; boot replay and full hour pending. Candidate monitor under actual5% quota catches all105 historical faults then ALERT, fresh UDP. Public old monitor/game processes unchanged. PR47 fresh124 tests PASS in isolated source snapshot, eight-client capacity still blocked; recommendation is4vCPU/8GiB test envelope, no order.

## Autonomous continuation — 24 October 2026

Owner: single lead, no subagents. Isolated worktree `/srv/tse-live-reliability-20261024`; starts at PR50 `a2b4ee1`. Foreign dirty worktrees remain unchanged. Evidence: `/srv/tse-live-evidence-20261024`. Current user instruction is the binding continuation spec. Available skill guidance is applied inline; skill helper scripts are not installed on this host, so ledger tracking is manual.

### Task 5: P0 outage and safe read-only monitoring repair
- [x] Identify host, PR45/46/47/49/50 heads, worktrees, locks, public process identities and ports.
- [x] Reproduce local and configured-address query timeouts; preserve Dedicated/Wine exception evidence.
- [x] Find stale monitor root cause: repeated 128 MiB cgroup OOM kills, restart limit, last update 2026-10-23T23:57:34Z.
- [ ] Verify incremental collector under unchanged memory/CPU protections, restore only read-only monitoring reversibly, verify output timestamps and public PID/start identities. Recovery stays disabled.
- [ ] Attribute each oversized log; preserve errors. No live copytruncate, deletion, threshold relaxation or public restart.

### Task 6: Exact-version evidence and missing isolated gates
- [ ] Audit retained final-source hour against hashes and closed evidence, publish sanitized result and distinguish later failed drills.
- [ ] Run available portable regressions and isolated native fault, log/archive, circuit, human/foreign-window and Originalclient/GameSpy checks without touching old failed runtime.
- [ ] Measure resources for PR47; do not start scales that fail reserve.
- [ ] Retain exact blockers and concrete next commands for unavailable WAN/Windows or necessary public maintenance approval. No merge/rollout on failed gates.

Pre-flight interfaces: Task5 consumes PR50 health collector unchanged; Task6 maps its exact hashes to existing native-hour records. Read-only monitor remediation does not qualify or enable public recovery. Existing native-hour PASS is scoped separately from subsequent FAILs and partial cleanup. A dead public query cannot establish no-human state.

Task6 ruling: retained helper-failure cleanup is a reproducible implementation defect: any remaining prefix client incorrectly triggers `wineserver -k` after its server has exited (Wine9 returns1, while `-w` returns0). Two preliminary diagnostic fixtures failed on permissions; the corrected nobody-owned fixture reproduces the empty-stderr exit1. Add exact-live-server detection, retain all actual command failures, and settle Xvfb exec identity before saving. Tests: `tools/test_operations_live_recovery.py` RED then GREEN, full root suite; repeat native fault gates and >=3600s for the new supervisor hash. Health collector stays unchanged and keeps its independently tested monitor provenance.

### Verified checkpoint —24 October,17:50 UTC
- [x] Task5 read-only monitoring repair: same immutable PR50 health collector, unchanged5%/128MiB guards; seven warm probe samples, production fresh writes/complete207-fault scan, no OOM; public game identities preserved.
- [x] Oversized four logs identified at32MiB threshold; crash copies/hash retained. No live maintenance or threshold change.
- [x] Prior final-source3600.002140s/654-sample/96-window hour reverified through closed raw hashes; later two FAILs and residual resources recorded.
- [x] Minimal Wine-server/exec-identity fix committed0ec97b4; SHA83d2bec6507d9de87fa7c42a97af69501f8f77b4608122a6f954dbfae20c1242. Three RED failures,92 final root/59 benchmark tests and555 C++Human-AI checks PASS.
- [ ] New-source native fault/Originalclient/network/hour: BLOCKED by six samples99.5–100% host CPU; no new Retail processes. The old source hour is not transferred. Staged new hour at private26920/26921/:125, not executed.
- [x] PR47 existing low-memory four-bot evidence and eight-client RAM failures reviewed; current CPU also blocks scaling.
- [x] All415 retained source/archive members and12 active pins freshly verified,61DC intact.
- [ ] Public manual maintenance/restoration requires a decision with unknown current human roster. No auto-recovery/reboot/rollout permission inferred.
Full handoff: `docs/reports/2026-10-24-live-reliability-handoff.md`; machine-readable sanitized results alongside it. Next action is the bounded same-Build04 public restoration described there, followed by fresh admission and new-source isolated gates.
