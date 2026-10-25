# ssam.ai autonomous continuation — 25 October 2026

M1's demonstrated stale/ENOENT/nickname defects have an implemented read-only
repair deployed to the existing MCP endpoint. Confirmed human/bot identity is
still blocked by missing authoritative server-side GUID/session bindings.
M2/M3 now have independently reviewed, reproduced offline tools/patches; neither
has new native acceptance. M4–M8 remain behind their stated P0/native gates.

## Fresh inventory and protected work

Main fetched at `ab0c740`; existing local main `fdfc46e` was not reset. Initial
nine worktrees were inspected. Dirty files in the AI2 and 22October master
worktrees and dirty app `servers.json` were preserved. Other Codex sessions
remain active; no existing work was interrupted or branch force-pushed.

The active public generation is `/srv/tse-experimental-public-20261025/runtime/eight-165601-zof3t2hr`,
not the old README/registry generation. Its own HANDOFF labels it an experimental
Build06 user test. Dedicated399158/start65294584; clients399232/399305; cgroup
`tse-integration-399143`. No ownership of these foreign game processes was
assumed. No process signal, runtime script edit, map switch, DLL replacement,
firewall change, game restart or memory instrumentation occurred here.

All12 active role binary hashes were freshly verified. Server original
Dedicated9596f53c, Engineb79bf8bb, Entities7f595f2a, GameMP1c41da35 retain their
known full pins. Both bot DLLs are Build06
`54faabf01d205c034055fa03c5b4316ce12a4907c824462ad85f797b3e7845e8`.
All415 protected backup source files and415 tar-member contents passed SHA256;
archive `d7b3650d55a21fc88614d5b969e126ac1cfcc52585262a1ef139eb0be1632b7d`
remains unchanged. Protected61DC is among those verified files.

Host: Ubuntu Hetzner ubuntu-4gb-nbg1-2,2vCPU,3819MiB/no swap. At19:21:16UTC,
a fresh5s sample was51.224% busy,2163224KiB MemAvailable,9459818496bytes disk
available. This is a short observation, not an extra-fleet capacity PASS or a
repetition of the historical99.5–100% CPU blocker. Live cgroup was about570MiB,
uncapped CPU/memory. Existing foreign cgroups/test residues remain untouched.

A direct UDP query to the public IP from this host independently confirmed
GameSpy10/16,Red Station,1.07,port25600 and infiniteammo=0. This is independent
of MCP parsing but **not an independent WAN vantage point**. The requested
infinite-ammo behavior therefore remains a demonstrated unresolved mismatch.

## M1 implementation, review and deployment

Before: ten GameSpy slots were all reported human; health said HEALTHY with
11:33UTC data; logs/statistics failed ENOENT on an unmounted old generation.

A separate app worktree `/srv/ssam-monitor-fix-20261025`, branch
`fix/20261025-runtime-monitoring`, contains source commits `a447ec3`, `b7bda00`,
`091f251`, `193e07b`. The app repository has no configured Git remote. Its full
reviewable delta from `9976cd3` is preserved in
[`tools/monitoring/0001-generation-aware-readonly-mcp.patch`](../../tools/monitoring/0001-generation-aware-readonly-mcp.patch).
No account plugin/package identity or audience changed.

The private receipt pins result bytes, PID/start/CWD/UID/cgroup,12 binaries,
eight native profiles and GUID-sidecar hashes. Current process/query ownership
and recent complete local-slot action telemetry are checked per request.
Receipt creation: `tools/monitoring/create_runtime_receipt.py`; no receipt,
GUID, profile, native raw log or binary is published. Duplicate/unproven names
remain unknown. A matching unique local roster name is explicitly an
**association**, not a confirmed network-slot identity. The app exposes separate
association counts and labels; it never equates an unmatched nickname with a
human. This preserves protection against a human taking an old bot name.

GameSpy fragments must come from the expected loopback port, have a complete
packet sequence and consistent fields. Query ownership checks the compatible
bind address plus inode; conflicting eligible binds fail closed. Missing logs
produce explicit unavailable backend/UI states while live rankings remain
independent. Statistics label associated-roster scores, not verified bot scores.
Health returns fresh process/query/telemetry observations with LIMITED coverage;
old health timestamps, missing generation binding and unverified sync-history
coverage remain visible alerts. Historical zero counters are not inherited.

Independent review caught unavailable-history UI, UDP bind-address validation,
and the nickname-versus-network-identity gap. Each was addressed with a failing
regression followed by GREEN. Other regressions cover stale/future timestamps,
PID reuse, binary/GUID changes, partial/stale telemetry, missing query inode,
missing logs and packet reordering. `npm run check`:20/20 tests, TypeScript and
single-file UI build PASS. Existing dependency PURE-comment bundler warnings
remain nonfatal. Real stdio MCP handshake/tool/resource test:1 PASS,7 tools,
10 slots and live8-entry associated roster ranking. The stdio test now explicitly
passes its registry environment; earlier attempts without that forwarding were
retained as failed preflight, not counted as PASS.

Release `/srv/ssam-monitor-release-20261025-b7bda00` holds the verified compiled
code. Private registry/receipt/backups/rollback record are under
`/srv/tse-monitor-evidence-20261025`. Existing source/dirty registry were not
overwritten. Only the read-only app service was restarted; its existing loopback
MCP/tunnel identity, filesystem protection, memory/task limits and admin-tool
absence remain. No game operation is exposed.

The actual service preflight found EACCES on `/proc/<nobody-pid>/cwd` under its
old capability set. A transient service reproduced it. Process-observation
permissions now add CAP_SYS_PTRACE together with read-only `/proc` and explicit
denial of `@debug`, `process_vm_readv`, `process_vm_writev`, `process_madvise`.
Do not rely on `@debug` alone: actual systemd expansion lacked the process_vm
calls. Owned helper tests proved ptrace and zero-vector process_vm calls return
EPERM and `/proc/self/mem` cannot open for writing. No game memory was read or
written. Configuration example is included in the app patch.

Initial connected calls during service restarts timed out; later connected
status/health calls returned fresh LIMITED, verified processes/query/telemetry,
10 identity-unknown slots and8 roster associations. These are read-only API
proofs, not new native join/combat/sync-hour acceptance. Full current-generation
sync history is still **UNVERIFIED**; the old collector is not silently relabeled.

Rollback: remove only
`/etc/systemd/system/alpha-gaming-control.service.d/20261025-monitoring.conf`,
run `systemctl daemon-reload`, restart `alpha-gaming-control.service`. Original
service and registry are backed up privately and remain unchanged. Keep receipt
pinned to this generation; any generation/profile/hash/PID change fails closed
until separately reviewed. Do not auto-discover/rebind an arbitrary live process.

## C1 / M3

C1 isolated worktree `/srv/tse-c1-reliability-20261025`, branch
`agent/c1/20261025-reliability-audit`, commit `5061ea0`; integrated scoped output
as `64334d9`. Exclusively new research/report paths, no runtime modules changed.
Five demonstrated defects: state read before controller lock; unregistered native
role after exec/save crash permits duplicate start; hardlink writer overlooked;
archive budget omits manifest; partial SYNCBAD tail counted as completely scanned.

Lead reran actual imported-code audit against pinned PR50 source: baseline5FAIL/
6PASS; patched11PASS; inherited91PASS/1 explicit Wine-CLI SKIP. The integration
runner now discovers inherited tests from its selected source root, so it is
usable from main without pretending PR50 runtime modules are merged. C2 independently
reviewed the patch: no new Important/Critical findings. Archive budget covers the
committed end state; temporary compression/manifest files need extra headroom.
/proc inventories remain snapshots and require exclusive resource ownership.

[`C1 handoff`](reliability-audit-20261025/HANDOFF.md) contains exact module and
patch SHA256, commands and native gates. Neither the old hour nor those fixture
tests qualify new supervisor hashes. No productive auto-restart/systemd recovery
was enabled. Native helper/Xvfb loss, recovery/adoption, human/foreign holds,
closed logs and final-source>=3600s remain **NOT_TESTED here**.

## C2 / M2

C2 worktree `/srv/tse-c2-sync-20261025`, branch
`agent/c2/20261025-native-sync-gates`, commit `3712192`; scoped integration
`82a994d`. Lead repeated37/37 synthetic tests and pinned PR58's29 original tests
plus seven adversarial findings. C1 independent read-only review found no
Important/Critical issue within the sealed offline contract.

The strict gate validates complete session/connection/level/sequence/tick windows,
all required byte lengths, artifacts and hashes before comparing CRC/action/state.
It never derives engine ticks from BotDriver wallclock/20Hz counters and always
reports retail_runtime=NOT_TESTED. PR58 accepts some missing/error/duplicate/
unmatched evidence and must not be used directly as native acceptance.

[`C2 report`](native-sync-gates/2026-10-25-c2-capture-compare.md) and tool README
contain the native N0–N7 matrix. Root cause is **OPEN**: no qualified native
producer/Retail binding and paired authorized divergent captures are available.
The current public remote slots are not consenting capture clients. Historical
kick/counter evidence does not identify a divergent action/state field or prove
Ground-Lookahead caused other generations. Kick verification was never disabled.

## PR integration matrix and downstream gates

| PRs | Dependency / disposition |
|---|---|
|45|Merged qualified Build04 baseline; protect exact evidence|
|46→49→50|Draft stack main→reliability→hardening→follow-up; no blind merge; C1 new patch requires its own native qualification|
|47→51|Independent sessions then RedStation stack; eight single-client/hour and drain qualification incomplete; preserve current grouped architecture|
|57|Based on51; Cecil opt-in source overlaps active AI2 BotDriver/botcore ownership; no concurrent integration or rollout|
|63|Based on51; redstation_preset overlaps active AI2 work; MOTD HUD/300s delivery remain unqualified|
|54|Navigation laboratory/transfer analysis; no native graph/world adapter acceptance|
|55|Independent item-utility research; no verified native item source/adapter|
|56|Independent RAM/session model; estimates/synthetic scheduler do not qualify hybrid native leave/rejoin|
|58|Sync research reviewed; seven additional fail-closed findings; use strict separate gate, no root-cause claim|
|62|Offline behavior simulator; synthetic quality signals are not Retail combat/latency measurements|

PR metadata were refreshed through GitHub; their existing branches were not
modified or merged. Incoming research is read/reviewed separately. No historical
name list or stale main README is treated as current live runtime state.

M4/M5: wait for P0 and controlled own-candidate native baseline/A-B gates; do not
combine all flags. M6: resource and lifecycle gates still required. M7: requested
infiniteammo disagrees with query;300s/HUD and power-up removal have no new PASS.
M8: no second server, no16bots/no24x7 qualification and no hardware order.

## Reproduce and resume

```sh
python3 -m unittest discover -s tools -p 'test_*.py'  #43 PASS on main-based branch
python3 -B poc/research/reliability-audit-20261025/run_audit.py --source-root /srv/tse-c1-reliability-20261025
python3 -B -m unittest discover -s poc/research/native-sync-gates/tests -v
python3 -B poc/research/native-sync-gates/review_pr58.py
cd /srv/ssam-monitor-fix-20261025
ALPHA_SERVERS_CONFIG=/srv/tse-monitor-evidence-20261025/servers.json npm run check
ALPHA_SERVERS_CONFIG=/srv/tse-monitor-evidence-20261025/servers.json npm run test:integration
```

Next concrete dependencies: obtain authoritative server/client GUID/session
bindings in an owned isolated reproduction; qualify the native capture producer
against pinned Retail functions and an uninstrumented control; acquire complete
paired divergent captures. Keep unknown public slots protected. Then qualify
the final supervisor patch on independent loopback resources with fresh reserve/
ownership preflight and full native fault/hour matrix. A Windows/WAN counterpart
and source-specific capture evidence cannot be replaced by these offline tests.

Publication uses a new main-based branch/PR; no existing PR head or main is
updated. Shell HTTPS push lacks credentials; connected GitHub publication is used.
A publication receipt records local and remote tree equality and final PR URL.
