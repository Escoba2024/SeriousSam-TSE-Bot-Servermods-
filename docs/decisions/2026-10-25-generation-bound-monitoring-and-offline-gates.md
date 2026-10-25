# Decision: generation-bound read-only monitoring,25 October2026

The active public runtime is the separately documented experimental AI2 Build06
user run, not the retired RedStation generation. Its original12 binary pins and
process identities are preserved. Read-only MCP registry/health/log lookup is
repaired through a separately staged app release and private receipt; no game
control or automatic supervisor recovery is enabled.

A local verified profile/GUID/process/telemetry roster plus matching GameSpy name
is an association only. Without authoritative server-side GUID/session evidence,
all network slots remain identity-unknown. Unknown slots retain human protection.
Stale health and incomplete sync history must remain explicit LIMITED alerts.

The service's process observation permission is bounded by read-only /proc and
explicit denied debug/process_vm/process_madvise syscalls, tested with owned
helpers; no game hook or memory access occurred. Original app source/dirty registry
are preserved, with a single removable drop-in for rollback.

C1/C2 outputs are integrated only as independent research tests/patches. They are
not source-specific native acceptance. PR46/49/50 and downstream feature/native
rollout gates remain open. PR58's existing tests omit seven demonstrated failure
cases; its COMPARABLE/complete output alone cannot accept native sync evidence.

Evidence, exact boundaries and next steps:
[master handoff](../reports/2026-10-25-master-handoff.md).
