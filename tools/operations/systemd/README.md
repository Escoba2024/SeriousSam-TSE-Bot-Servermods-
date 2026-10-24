# Read-only public health monitor

`tse-public-health-monitor.service` is the exact staged monitor configuration
for the immutable four-source bundle under
`/srv/tse-ops-monitor-release-20261022/b5a6cba`. It is installed as
`tse-public-health.service`, not as a second concurrent writer. This service
always executes `monitor`; it cannot invoke game recovery through its command.
The original unit and source pin file must remain available for rollback.

Deployment gates:

1. Require exact-source native qualification and original-client/safety results.
   Validate public PID/start/CWD identities, game hashes, fresh roster and disk.
2. Check all four release hashes and verify the staged unit with
   `systemd-analyze verify`. Preserve old unit, pins and last health output.
3. Stop only the old **monitor** unit. Install the new source-pin manifest as
   `/etc/tse-public-health-20261022.sha256`, replace the monitor unit,
   daemon-reload and start. Never signal the public game or Wine processes.
4. Wait for the bounded historical sync scan to finish. Verify expected roster,
   zero owned faults, retained external historical count, fresh telemetry/query,
   current memory/CPU fields, bounded service memory and unchanged public PIDs.
   Existing historical warnings and log limits must remain visible.
5. If these checks fail: stop the new monitor, restore the exact saved old unit,
   daemon-reload, check original `/etc/tse-public-health-20261021.sha256` and start
   the old monitor. Preserve both sets of evidence. Do not restart games.

The root-owned deployment bundle contains `tools/operations/fleet_health.py`,
`fleet_supervisor.py`, `tools/qualify_integrated_wine.py` and
`tools/bot_telemetry.py`; hashes in the installed manifest bind the paths.
`CPUQuota=5%` is a service budget, not a game CPU limit. Read-only quota probes
have qualified the incremental warm scan; a first incomplete scan stays blocked.
No boot/recovery, host reboot or 24/7 qualification follows from this service.

## Incident repair24 October2026

The unit is now the actual deployed read-only monitor: immutable `b5a6cba`
bundle, original CPUQuota5% and MemoryMax128M. A separate probe preserved207
historical faults and stayed below34MiB with zero OOM. Existing failed whole-log
monitor was replaced; public game processes were not signalled. This narrow
read-only outage repair bypasses only the healthy-roster migration precondition
above. It grants no recovery/reboot/rollout permission. The output's timestamp
and failure booleans now reflect the present Dedicated exception/query outage.
See `docs/decisions/2026-10-24-readonly-monitor-incident-repair.md` and the
24October incident handoff for exact pins, preserved configuration rollback
and its known old-reader OOM limitation. The newer private supervisor fix
`83d2bec...` is not in this production bundle and lacks new native qualification.
