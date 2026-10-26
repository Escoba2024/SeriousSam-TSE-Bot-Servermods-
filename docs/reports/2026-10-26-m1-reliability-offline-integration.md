# SSAM.AI M1 – Reliability source integration (26 Oct 2026)

**Status: OFFLINE_TESTED_ONLY, NATIVE_NOT_TESTED, NOT_DEPLOYED.**

Source checkout: /srv/tse-c1-reliability-20261025 (independent isolated C1 audit, no edits made to it).
Integration worktree: /srv/tse-m1-m4-integration-20261026.
The user ordered the public server stopped; no Wine test, systemd unit, runtime mount,
live game process, port 25600/25601, cgroup, or external player was modified.

## Exact source provenance

Imported these previously audited PR50-derived modules into tools/operations,
then applied `poc/research/reliability-audit-20261025/0001-close-controller-archive-and-sync-gaps.patch`
with `git apply --check` and `git apply` (no fuzzy hunks).

| Artifact | Original SHA256 | Integrated SHA256 |
|---|---|---|
| fleet_health.py | 152d2b71865d0649f977016701267ed17a086eb15a506c4113173a28f45e1800 | ef99e37d4754c60ad3acf0eb484a529e56b80115c6734ba21252c68c1f4fd030 |
| fleet_supervisor.py | 83d2bec6507d9de87fa7c42a97af69501f8f77b4608122a6f954dbfae20c1242 | c0c1a99853f373ff052f33252ccab12f436537a3f96be85c1fccfbea62a3f87b |
| correction patch | n/a | 9268f2a11bc4cd52589061af4094376a673d688cd9952278345b49e51ef31ba4 |

Tests were imported from that reference repository into tools/test_fleet_operations.py,
tools/test_operations_completion.py, tools/test_operations_live_recovery.py,
tools/test_operations_review.py, and the isolated offline audit in
poc/research/reliability-audit-20261025/test_reliability_audit.py.

## Reproduced defects and regression status

11 direct audit cases against baseline code: **5 FAIL**, 6 PASS.
Same 11 cases against exact patched source: **11 PASS**.

The five RED→GREEN cases prevent:
1. reading an obsolete controller generation before acquiring the supervisor lock;
2. silently adopting an unregistered native role in the same cgroup after exec/save failure;
3. log archive unlink while a hardlinked open writer still exists;
4. a compressed archive plus manifest exceeding its budget before removing the input;
5. marking a trailing, unterminated SYNCBAD record fully scanned.

The combined integration tools suite with
`test_operations_live_recovery.LiveRecoveryTests.test_native_absent_server_wait_with_remaining_process`
explicitly skipped because it invokes native Wine: **130 run, 0 failures, 0 errors, 1 skipped**.
The separate audit suite: **11 run, all OK**.
These are synthetic/portable regression tests, NOT a live M1/restart/hour validation.

## Important integration boundary

The imported supervisor is **not enabled** or installed as a systemd service;
systemd templates were deliberately not imported. The inherited module
`fleet_health.py` pins the *older* DLL SHA256
`7fc94a39c3f5d9516f262d9e4d04a5cf38e6eb5ae3482976c32c952a99d30835`
and `fleet_supervisor.py` pins a historical build-manifest path and proof
for that version. Current Cecil P1 candidate is
`7dc961c880e0ed68ead13ed4e8299a025be71e05619de36c437c756e964334bf`.
Do NOT bypass or retarget the source-pin/receipt validation to start P1:
it has no M1 60/60/120-min, sync, independent vanilla and full
reliability evidence. A valid source import is not acceptance.

## Required later gates

- Source-level integration review of the proposed hardened operations modules.
- Candidate- and generation-bound native preflight, health/identity/roster
  authentication, Linux PID epoch/cgroup/UDP ownership and proper rollback.
- Exactly isolated native supervisor crash/restart/circuit/log/archive probes,
  additional game generation healthy for >=60 minutes, human-slot protection.
- Restore public deployment only under verified safe condition and user release rules.
- Resolve native CRC/action/state first-divergence diagnosis; never repeat
  unsafe Frida interior CMP hooks from the earlier experiment.

Current releases remain unchanged. M1 Reliability is **IN_PROGRESS**
and M1 overall **IN_PROGRESS**. M2/M3/M4 are not released.

## Follow-up: missing server SYNC log must fail closed

During integration a **sixth** reliability defect was reproduced against the
already audited C1-patched source. If the server's
`server/Dedicated_BotTest.log` was absent, `fleet_health.collect`
seeded `complete=True, owned=0`, allowing `assess` to treat missing
SYNC evidence as a completed zero-error scan. This violates fail-closed
supervision and can incorrectly authorize recovery.

TDD reproduction: `tools/test_m1_missing_sync_log.py`, using a fully
synthetic result.json, valid stub GameSpy response and no actual processes.
RED: `AssertionError: True is not false: missing file was silently
admitted as zero bad syncs`. Minimal patch: initialize missing-log
`complete=False`, leaving the existing scanner behavior unchanged for
real files. GREEN: focused one-test PASS and full offline suite **131 run,
0 failures/errors, 1 deliberately skipped native Wine test**. The 11
original imported C1 regressions continue to PASS.

This is an integration-specific additive fix, not part of the original
C1 patch SHA above. Post-fix `tools/operations/fleet_health.py` SHA256:
`c666370adfcd4bae3df75f073474ca730302a3b93beaaf492b05e00a2e3c42bd`. The original C1-patch SHA stays in the table
as provenance, not as the integrated post-fix file hash.

Consequence: missing server log holds automatic recovery until complete,
owned-generation sync evidence exists; this trades availability for
safety. Neither native incident recovery nor production deployment is
qualified by this offline reproduction.
