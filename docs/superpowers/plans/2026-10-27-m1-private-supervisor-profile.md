# M1 private supervisor candidate profile implementation plan

> Use superpowers:executing-plans; parent owns all native operations and integration.

**Goal:** Opt-in immutable candidate profile for the existing operations supervisor, retaining the legacy default.
**Architecture:** Verify exact accepted r3 matrix and pins before loading a frozen instance profile. Existing Runtime, health, ownership, retry and archive paths consume instance-bound roles, artifacts and settings. Prepared overlays copy qualified configuration; a separate loopback namespace is mandatory and master advertising is disabled.
**Tech Stack:** Python3, existing operations modules, native receipt acceptance.
**Spec:** M1 autonomous completion and parent task of27October; docs/reports/2026-10-26-m1-reliability-offline-integration.md.

## Global constraints
No native processes, ports, mounts, iptables, Codex, builds, heavy tests or active policy changes by this worker. Native matrix owns resources. No public activation; source-only code is NOT native qualification. Existing legacy constants and default API remain unchanged.

## Review Focus
- Unaccepted/malformed/drifted duration receipts must never admit candidate.
- Instance profile must never mutate legacy module globals.
- Eight separate1LP clients and original observer must not become two4LP clients.
- Profile prepared-settings mismatch or host namespace must block action.
- Unknown players, stale telemetry and PID/generation mismatch must retain existing HOLD behavior.

## Task1: immutable profile and admission
Files tools/operations/private_candidate_profile.py; new tools/test_private_candidate_profile.py.
Consumes exact r3 policy/matrix/build/config/source pins; produces frozen role/settings profile only after direct receipt validation.
- [x] RED focused purePython tests for absent profile, matrixnotaccepted, topology/config/path rejection.
- [x] Implement bounded metadata/pin loader and accepted-config reference derivation.
- [x] GREEN focused short tests; no fabricatednative gate.

## Task2: existing runtime/health opt-in
Files tools/operations/fleet_supervisor.py, fleet_health.py; new tools/test_private_supervisor_profile.py.
Consumes Task1 profile; produces instance-bound role/artifact/settings handling with strict networknamespace admission. Legacy functions remain unchanged by default.
- [x] RED tests for profile role/localplayer/roster and defaultlegacy preservation.
- [x] Implement profile branches using existing Runtime methods; no secondcontroller.
- [x] GREEN focused purePython tests; document unexecuted native/fullsuite gates.

## Ledger
Pre-flight: Task2 consumes frozen role/settings profile fromTask1; no other writer in own worktree. Basea18e898. Parent explicitly authorizes no intermediate approval. Fullsuite/native deferred while matrix runs.

- Task1 complete:6initial missing-profile failures RED→GREEN; exactinventory, nativeprofile and preparation guards each separately RED→GREEN. Full actualacceptedloader/native admission remains unexecuted while matrix is active.
- Task2 complete: role/recovery contract3FAIL+1TypeError RED→GREEN; private ghost nickname escalation RED→GREEN. No globalcandidate/roster/build mutations.
- Ruling: profile admission reuses exact accepted1/4/8 receipts and their complete policy inventory; it never treats old8partial runtime as accepted. If wrong, acceptance fails closed rather than relabeling history.
- Ruling: private nickname stillpresent means WAIT_GHOSTS indefinitely, never forced fleet restart. This avoids evicting an unproven occupant at the cost of availability until genuine absence.
- Ruling: keep the legacy default unchanged; opt-in profile explicitly changes master policy to isolated loopback/no advertising and uses the qualified8x1LP plus owned original observer topology. No public operating qualification is claimed.
- Parent review/fullsuite/native gates remain external to this worker; no extra agent spawned. Parent requested commit and handoff now, then reviews and integrates independently.

- Parent precommit review: read-only health/monitor profile plumbing gap reproduced (2FAIL/1error), corrected with config-bound forwarding and private-result no-profile rejection. Final focused set25PASS normal and optimized; broadsuite/native remain deferred. Source integrity rechecks occur before every launch/action via ownership and verify_settings.

- Parent postcommit Important cleanup finding: wronglegacy prefix-source mapping skipped9privateprefixes inRuntime.stop. Focused actualcontrolflow RED1/10→GREEN10/10; profile.source nowusedconditionally; final26focusedPASS normal/-O. Broad/nativequalification deferred.
