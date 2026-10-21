# Guarded Hetzner operations design — 2026-10-21

## Intent and scope
User authorizes executing PR46 without routine approval pauses: reclaim >=8 GiB safely, implement and isolate-test monitoring/log limits/recovery, then measure two eight-bot instances. Public eight remain online, original files and rollback remain intact. No engine/DLL change, new agents, installs or paid capacity.

## Selected architecture
Use a separate Python operations module with a persisted, validated instance manifest and an exclusive flock. Existing qualified launcher and stop tool remain unchanged. Their prepare-only path creates private overlays and profiles; the new controller owns only a separate loopback port/display/cgroup. Production is read-only until all acceptance gates pass.

A generic Restart=always wrapper around the old launcher was rejected because it can duplicate retained processes and cannot reconcile overlay ownership after controller death. Editing the qualified launcher was rejected to keep engine qualification provenance and existing production behavior intact.

## Health and recovery contract
Manifest pins candidate SHA, original binary SHA, boot ID, process PID/start ticks/CWD/command/cgroup, display, ports and exact lower/upper/work mounts. Validate all configuration before any mutation. Current boot processes with mismatching identities, unknown mount or any foreign port owner block every action. Missing processes are distinct from PID reuse. Each query must be a fresh, complete native GameSpy exchange; validate version, expected roster, maxplayers and telemetry freshness, ticks/actions and draw count. Humans produce an explicit hold on disruptive recovery. Unknown query is never interpreted as an empty server. External-client SYNCBAD is an alert, never an automatic server restart; owned-client SYNCBAD blocks qualification and scale. Keep private peer details out of public reports.

Per-instance flock survives launch and polling, preventing duplicate controllers. A stopped controller leaves the healthy game running. A new controller adopts only exactly reconciled processes and mounts. When an owned client exits, restart only that client after fresh roster/ownership verification; preserve the original server and humans. Restart the whole isolated fleet only after confirmed owned server death, free ports and a recent no-human snapshot. Bound retries with backoff and a persisted circuit breaker. Boot simulation re-mounts only exact owned overlays when all previous processes are absent and ports free; actual host reboot remains unscheduled.

## Log safety
Never copytruncate live Wine handles: observed flags are not O_APPEND, so truncation can create holes or overwrite fresh data. Archive and hash only closed generation files before controlled own-process restart, with gzip verification. Bound controller output via systemd journal options. Operational log threshold holds disruptive restarts when humans/uncertain query are present, raises disk/log alerts and prevents starting additional load. Preserve original qualification evidence and rollback archives; retention never targets historical evidence. If a safe continuous size cap is impossible without disrupting humans, document the exact guard and defer disruptive maintenance.

## Isolated acceptance
Unit fixtures exercise PID absence/reuse, wrong CWD/cgroup, foreign port/mount, bad manifest, stale query/telemetry, low disk, missing DNS, humans, circuit breaker and no double start. Native isolated lifecycle exercises prepare/start/adopt, own client failure/recovery, safe stop, manifest reload, mount replay and boot simulation. Unchanged lower hashes verified before/after. A controlled active-bot hour is required before production recovery activation. Independent WAN/native public-browser proof for existing release is preserved; new unlisted loopback service has no external-public qualification. No production reboot for testing.

## Scale gate
Disk >=8 GiB, measured initial CPU reserve >30%, memory reserve, unique ports, and no concurrent benchmark. Public service stays protected; starting two additional isolated eight-bot fleets would place 24 bots on the host. Do not treat a two-instance result as isolated when it includes public humans. Measure bounded additional load and abort self-owned tests if host reserve or native sync/telemetry gates fail. If reserve cannot support the requested independent 2x8 test beside production, report the measured host constraint, keep production at eight, and do not order resources.
