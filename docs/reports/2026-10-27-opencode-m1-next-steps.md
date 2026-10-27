# M1 next steps after user deferral of the eight-bot run

Status: OFFLINE_REGRESSIONS_VERIFIED; native M1 remains IN_PROGRESS. The eight-bot duration gate is DEFERRED_BY_USER as requested on 27 October 2026, not PASS.

## Result and scope
The existing supervisor core qualifier and its original eleven source/metadata checks from worker commit 19b35912d1741d63668b3fef070335fe84ea2460 were brought into this isolated branch. The core qualifier remains byte-identical to that reviewed source. Default invocation starts nothing; explicit native execution still requires accepted pinned duration and canonical recovery evidence. No runtime admission, production Runtime, candidate DLL, source policy, threshold or public service was changed.

Nine additional offline regression tests exercise the EXISTING Runtime implementation: actual constructor lock rejects a duplicate before process actions; unknown roster blocks recovery and log maintenance; stale/future queries block recovery; expired no-human evidence blocks server recovery; reopened restart history enforces backoff and three-per-hour circuit; log maintenance uses the existing stop/restart path or stops without restart when its budget is exhausted; an incomplete sync scan blocks maintenance.

These tests use temporary state/lock files, fixture health.collect inputs and mocked lifecycle methods. They prove offline control-flow contracts only. No real unknown original guest, native fault/rejoin, runtime archive maintenance or following-generation hour was measured. Native phases remain NOT_TESTED. No fixture grants PASS_NATIVE or M1 completion.

## Parent review correction
OpenCode's initial extension added parallel roster/freshness/verdict/maintenance helpers. Parent review rejected these: freshness parsing could accept future timestamps, the duplicate probe did not test the existing Runtime constructor, and direct archive invocation bypassed the existing maintenance decision path. Those additions were removed; their private snapshot is retained outside Git. The final patch reuses the existing production decisions directly, with no additional production policy.

## Verification
Base: 7fe0b95a11341f594272beca0f9cf8f04150db69, same tree as canonical local e71b168b4606ccc2909e32ba9100591b76363c36 before these changes.

- python3 -m unittest tools.test_existing_supervisor_qualification -v: 20 run, 20 PASS, exit 0.
- python3 -O -m unittest tools.test_existing_supervisor_qualification tools.test_private_supervisor_profile: 33 run, 33 PASS, exit 0.
- Full tools discovery as opencode-tse: 288 run, 284 PASS, 1 FAIL, 2 ERROR, 1 SKIP, exit 1.
- Remaining FAIL: test_reader_handles_do_not_block_verified_archiving.
- Remaining ERROR: test_archive_restores_exact_bytes_and_budget_fail_closed; test_runtime_wrapper_rejects_actual_source_inventory_drift.
- The archive cases cannot enumerate protected /proc handles as UID1001; the source-inventory fixture cannot create its required /srv temporary path. These pre-existing environment failures were retained rather than weakening guards or adding skips. The full suite is not green.
- Existing root/Wine CLI case skipped by its own eligibility check. No native games were run.
- git diff --check: exit 0 (untracked additions additionally checked by compilation/import and the above tests).
- Core source byte comparison against reviewed worker input: identical.

## Remaining acceptance
8 bots >=7200 continuous seconds: DEFERRED_BY_USER.
1/4-bot idle-r3 receipts remain historical accepted duration receipts (3701.053s / 3762.538s); not relabeled.
Canonical native recovery and actual supervisor phases: BLOCKED by unchanged accepted-matrix admission and current resource/privilege prerequisites.
Current free disk remains below the 8GiB minimum. No deletion, reserve reduction, extra costs, rights escalation or public startup was performed.
Independent whole-M1 native acceptance remains OPEN. Offline code review is a separate check.

## Independent read-only source review
No blocking findings. Core SHA256 9ecfd94c621e11289a980eed2a4f79eb2136136ac89576fcba23a00d6ba59651 matches worker input; original eleven test ASTs unchanged. Nine new tests exercise existing Runtime paths without native games. Reviewer suggested isolating empty UDP ownership in the expired-evidence negative test; this was applied and 33 focused tests then passed, exit0. JSON state reopen is an offline fixture, not native persistence acceptance.
