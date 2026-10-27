# M1 duration continuation and monitor cost correction, 27 October 2026

Status: IN_PROGRESS, NOT RELEASE QUALIFIED. Public runtime remains user-disabled.

## Confirmed evidence
Prior immutable idle-r2 matrix: one bot3700.687s and four bots3762.257s uninterrupted full population accepted against their original source policy. Eight bots ran3748.102s elapsed,3582.551s full population, before host CPU protection stopped the test. Last CPU samples87.538/86.996/86.465% exceed unchanged85% three-sample limit. Available RAM minimum1049.7MiB; disk minimum8.155GiB. Native game CPU declined over the run while monitoring cycles grew. Cleanup census is clean; recovery was correctly blocked, not executed.

A short private preserved-log cProfile measured approximately0.16CPU s per matcher pass and0.13s for repeated full-text reads. Source-only benchmark replayed unchanged private logs using alternating original and candidate matcher calls, seven pairs: median new/original CPU ratio0.58955 (~41.05% lower matcher CPU). This measures the log matcher, not overall server savings or native duration acceptance. No raw logs or private identities are published.

## Change and review
Collapse case variants to eight conservative shared literals. Keep original regex as the final match authority, full text each call, Identifier negative-lookahead, unknown-pattern/flag fallback and actual Match object unchanged. Two helper copies remain byte-identical. No cache, offsets, missing log omission, game DLL/config/observer change or guard relaxation.

A more aggressive seven-anchor prototype was rejected: routine joystick 'error' and bot 'symbols' forced expensive original regex searches. An unpaired absolute-time comparison was inconclusive; alternating paired reference/candidate replay controls short-term CPU-speed variation. Retain failed benchmark receipts privately. Independent read-only reviewer found no blocking issues; added actual shared-anchor delegation and routine-message regressions following its minor test-quality observation.

Verification: performance72tests normal and optimized; tools242tests; recovery profile19tests optimized. Check final logged totals before relying on this report. New native matrix is REQUIRED before release; the old1/4 passes are not relabeled as new-producer qualification.

## Safe continuation
Same published source tree as PR75 head4e959ad was recovered from its byte-identical older local history. Work now on agent/chat/20261027-m1-monitor-cost. Private idle-r3 matrix has fresh roots, exact policy/source pins and unchanged1/3600,4/3600,8/7200 admission. Original failed receipts remain intact. Existing canonical recovery qualifier is rebound to the exact reviewed r3 controller; fault execution retains its separately pinned historical source policy and identical game candidate.

Originals/backups remain protected. Package-download cache only was cleared, increasing free disk to8.58GiB. No retail binary, worktree, test log or backup removed. No public server activation or merge. M1-only scope; existing M2-M4 offline candidates remain unqualified.
