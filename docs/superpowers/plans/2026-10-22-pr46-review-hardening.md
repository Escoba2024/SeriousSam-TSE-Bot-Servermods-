# PR46 Reliability – independent review hardening, 2026-10-22

Owner: isolated Hetzner-only review worktree /srv/tse-reliability-qa-20261022.
Base: d6d29115e807826f8d4ca802359b535b31362fcd (PR #46).
Do not modify live service source /srv/tse-reliability-20261021, its /etc SHA pin, original files, or the public eight-bot service.

## Execution checklist
- [x] Audit host/worktrees, historical PR46 evidence, active service and identity-gated public processes.
- [x] Preserve four uncommitted changes in original PR46 worktree.
- [x] Replay eight independent operations-review tests in RED state: 8 failures against baseline.
- [x] Apply existing review-candidate corrections in this isolated branch; 34 targeted tests PASS.
- [x] Execute full available tools/test_*.py suite: 77 tests PASS.
- [x] Confirm /etc production source-pin hashes PASS and public three Linux PIDs unchanged.
- [x] Publish source-only hardening in separate branch; no runtime rollout.
- [ ] Integrate review branch with PR46 via reviewed merge; ensure live pinned monitor migration remains deliberate and reversible.
- [ ] Repeat full native 3600-second lifecycle with NEW source hashes (prior PASS used old source hashes).
- [ ] Independently reproduce foreign-window hold, adversarial corruption cases and 60-minute recovery after merge.
- [ ] Validate external master/GameSpy and active original-client observer for integrated candidate.
- [ ] Complete log maintenance/runbook, host-boot rehearsal if safely schedulable; actual reboot NOT_TESTED.
- [ ] Only after explicit native production safety gates, evaluate monitor/recovery activation; do NOT disrupt public players.
- [ ] Following PR46 approval, coordinate PR47 RAM-capacity blocker; then independently assess two-server rollout.

Stop criteria: qualified gates or documented constraint; protected public service unchanged.

## Native execution checkpoint, 2026-10-22 09:20 UTC
- [x] Native isolated one-bot real-failure/ghost-aware recovery with the new reviewed source: PASS_LIMITED, owned cleanup PASS, public PIDs/startticks unchanged.
- [x] New private eight-bot runtime prepared on 26860/26861, display :127.
- [x] Harness-only config newline failure preserved and fixed without changing operational supervisor code; cleanup confirmed.
- [x] R2 independent qualifier launched under tse-pr46-native-qa-r2-20261022.service; first double-start guard PASS.
- [ ] R2 genuine eight-bot 3600-second result, per-bot activity, CPU/RAM/Sync, cleanup, and original source hash verification still PENDING.
- [ ] Only after clean native acceptance revisit PR46 integration and deployment gates. Production unchanged.
Private output: /srv/tse-reliability-qa-evidence-20261022/soak/orchestrator-status.json, native-qualification.json, qualifier-stdout.log. First failed harness attempt retained separately.
