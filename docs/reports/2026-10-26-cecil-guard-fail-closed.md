# ssam.ai Cecil P1 A/B native admission — 26 October 2026

## Decision
NATIVE A/B NOT STARTED — GUARD BLOCKED. This is an intentional admission refusal, not a failed gameplay test, sync fix, or release qualification. No public process or protected binary was modified. Compare to draft PR #71's controlled source/binary comparability checker.

## Observed release-generation mismatch
The active experimental Build06 generation /srv/tse-experimental-public-20261025/runtime/eight-165601-zof3t2hr reports three pinned roles and eight bots but no expected_names field. The existing Cecil qualification harness originally indexed expected_names before checking public processes; it could not use this result without a KeyError. That field must not be guessed from a GameSpy nickname list because network-slot identities are not authoritative.

The old /srv/tse-public-health-20261021/health.json still reports HEALTHY with zero owned sync warnings and all three simple freshness booleans true, but its last UTC is 2026-10-25T11:33:40Z with no generation binding. It is not a current source-specific health proof. Connected ssam.ai Control read-only health at 2026-10-26T00:11Z reported LIMITED: HEALTH_SOURCE_STALE, HEALTH_GENERATION_UNVERIFIED, SYNC_HISTORY_UNVERIFIED; separate process-generation checking was current. Do not treat this historical snapshot as current acceptance.

## Test-first fix
Isolated worktree /srv/tse-cecil-guard-20261026:
- tools/test_public_generation_guard.py: 15 new tests. Initial RED import missing the new validation functions, then GREEN.
- tools/qualify_bot_sessions.py: fresh read-only public metadata and health checks. Require eight distinct explicit expected names, exactly three owned process roles pinned to one runtime generation, UTC freshness at most 120s, matching health generation, HEALTHY, verified native sync-history coverage, zero owned sync warnings and current telemetry/query/process checks. Enforce exact GameSpy roster cardinality/membership during monitoring: any additional unknown/human player blocks new resource-consuming tests. Fail closed; no automatic discovery, rewriting or process signals.

Full tools/test_*.py suite: 186 tests PASS. No production runtime or native DLL build was performed by this task.

## Same-DLL real command preflight
An ephemeral local four-identity config was prepared outside Git; same candidate DLL SHA256 7dc961c880e0ed68ead13ed4e8299a025be71e05619de36c437c756e964334bf and identical runner/config/ports were selected for controlled Cecil OFF and candidate ON commands. Both real execute invocations ended at the first trust gate:
- CONTROL_OFF: BLOCKED_SAFELY, exit 1, no native test directory created.
- CANDIDATE_ON: BLOCKED_SAFELY, exit 1, no native test directory created.
- Reason: public expected_names missing or incomplete.
- Three protected public game PID startticks and CWDs were identical before and after both probes.
- No original-client combat, native 4-bot OFF/ON runtime, paired CRC/action/state, duration or causality PASS was asserted.

The disk reserve was around 8.8 GiB, MemAvailable around 2.2 GiB, no swap and two vCPUs; historical four-bot private peaks were around 1 GiB RAM and 0.8 of one CPU core. Short CPU observations alone cannot override the missing safety evidence.

## Next integration gate
1. Publish and verify authoritative generation-bound fresh public health/sync coverage and current expected-bot roster from owned process/profile/GUID receipts without relying on names alone to identify humans. Do not fabricate or mark stale files healthy.
2. Enforce exact process identities/roster and human/unknown-player holds, >8 GiB disk and RAM/CPU admission. If these conditions cannot be proven, use a separately isolated host or separately authorized safe shutdown; do not disable guards.
3. With exclusive ownership and original Retail 1.07 binaries unchanged, run ONE pinned Cecil DLL four-bot 150–300s OFF then identical ON. Compare receipts with PR #71; only a verified same-build flag contrast is a suitable A/B input. Never turn off sync kicks.
4. Capture authorized paired native engine action/state/CRC bytes around the first SYNCBAD; investigate only verified causes. One clean 4-bot run is not a 60-minute release. Then run native 1/4/8-bot stability and protected original-client/WAN test before Stable Candidate 1.

## Ownership and safety
This branch changes test-harness safety logic, one new test file, a design, a plan and this report. No server, process, DLL, shared master worktree, runtime config, monitoring service, credential or production branch was changed. No private raw logs, player names, IPs or GUIDs were copied into Git. Draft PR, no auto-merge or deployment.
