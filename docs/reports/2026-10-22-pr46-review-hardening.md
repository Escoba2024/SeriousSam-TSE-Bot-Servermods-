# Alpha-Gaming PR46: independent failure-closed review, 22 October 2026

## Scope and provenance
Verified Ubuntu host ubuntu-4gb-nbg1-2. Worktree: /srv/tse-reliability-qa-20261022, branch agent/ops/20261022-pr46-review-hardening. Starting tree d6d29115 (PR #46). The original reliability worktree has one modified design document plus three untracked artifacts; NONE were touched. No production runtime code, systemd unit, port, Wine process, game binary or backup was changed.

## Review findings and implementation
Ported pre-existing locally verified review-candidate fixes (NOT a new GameMP.dll):
* Reject clock rollback/future timestamps in recovery retry budget.
* Fail closed if unknown Retail X window owns a private display before teardown.
* Archive closed generations even if readers hold open handles; reject active writers.
* Validate bounded, configurable private log limits and include Wine/Xvfb logs.
* Incrementally scan sync records, detect inode/rotation/partial lines; hold recovery while incomplete.
* Check exact local player count in telemetry, cgroup CPU throttling/OOM and source bounds.
These are safeguards for isolated private operations. Production recovery remains disabled.

## Reproducible tests
Private evidence (not committed): /srv/tse-reliability-qa-evidence-20261022.
RED baseline: python3 -m unittest discover -s tools -p test_operations_review.py -v ; 8/8 newly introduced tests failed as expected.
GREEN: python3 -m unittest discover -s tools -p 'test_*operations*.py' -v ; 34/34 PASS.
Suite: python3 -m unittest discover -s tools -p 'test_*.py' -q ; 77/77 PASS.
Python compilation: PASS. git diff --check: PASS. No new native Retail run for this modified source.

## Existing native evidence: explicitly separate from this patch
2026-10-21 private evidence native-qualification.json records 3600.0037s elapsed, 652 samples, 8 active bots, both local telemetry at 20 Hz/80 actions/s, owned sync 0 per related public health, six 10-minute windows, host busy mean 63.13%, P95 67.92%, no new throttles, no host reboot. Status PASS_ISOLATED_LIFECYCLE_AND_60MIN for ORIGINAL supervisor SHA256 32a3de50fc585ee618502b6a3a50137cfd60db6ab20f75abf28fcd325bef8e16 and ORIGINAL health SHA256 a8401eda2205ae177de6422a44ee70ded87ce0d8145874f3a0a75dcfa762f674. It does NOT constitute a native test or release approval for this changed review branch.

## Protected public state
Public UDP 25600/25601 and original live PIDs 124818, 124882, 124950 still present at review. /etc/tse-public-health-20261021.sha256 check PASS; read-only systemd monitor remains online. Free disk approximately 15 GiB; available RAM 2344 MiB. Current health warns transient QUERY_UNCERTAIN, historically 56 EXTERNAL_CLIENT_SYNC, and LOG_LIMIT_MAINTENANCE_HOLD; owned sync 0. Human presence/extra ninth player was transiently observed. Do not infer bot faults from external-client sync warnings.

## Decision and handoff
Code: OFFLINE TESTED, NOT NATIVELY REQUALIFIED. Service: READ-ONLY PUBLIC MONITOR, NOT AUTO-RECOVERY. Public 8 bots: STILL ACTIVE at audit time. PR46 merge/release: OPEN. PR47 eight-separate-client hour remains BLOCKED by host RAM safety gate. New independent original-client gameplay and public second-server rollout: OPEN. No protected backup or original DLL modified.

Next: Review this branch against PR46; safely test the new code in separate private runtime for at least 3600s and prove all safeguards, then integrate via qualified PR and plan a reversible monitor migration. Production activation remains gated.

## Native follow-up, 2026-10-22, 09:20 UTC (new supervisor source)
One-bot isolated Retail 1.07 smoke: PASS_LIMITED_NATIVE_RECOVERY. Own bot PID 172945 was gracefully signalled by guarded pidfd; ghost-safe supervisor recycled its OWN private fleet and relaunched owned bot PID 173227. Original one-bot game port 26840 / query 26841 / display :126. Native query and fresh telemetry became HEALTHY before and after recovery. Private controller exited; all private overlays were unmounted, own query ports/display cleaned. Production PID and start-tick checks passed before/after. Private evidence: /srv/tse-reliability-qa-evidence-20261022/native-smoke-report.json. This is a LIMITED one-bot native failure/recovery acceptance, not the eight-bot hour.

Eight-bot native requalification started on own ports 26860/26861, display :127, using immutable new source hashes: supervisor 8c6c863aab2fc198012c9b39e4d65c917d3442eb555424164ca8c2c8b6f86893 and health 8752560b8aa49b6eb12d99804072f13c6dd8558a67db9c597e0da26bb8ce0c8f. The first orchestrator attempt failed in the TEST HARNESS prior to lifecycle (newline included in saved config path), NOT a game failure; it safely stopped private roles and unmounted. Raw failed evidence was retained in soak attempt1 archives. Corrected orchestrator R2 started in systemd unit tse-pr46-native-qa-r2-20261022.service; native double-start protection passed by 09:20:41 UTC. Complete R2 hour verdict PENDING at this update, no PASS claim yet. Live public source-pin hashes unchanged.

Important: The earlier 2026-10-21 hour remains a PASS for the OLD code, while this new hour is pending. No automatic production recovery deployed or enabled.
