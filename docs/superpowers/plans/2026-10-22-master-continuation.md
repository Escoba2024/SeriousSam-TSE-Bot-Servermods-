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
