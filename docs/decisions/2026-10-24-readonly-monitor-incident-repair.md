# Read-only monitor restoration during a public outage — 24 October 2026

Verified on authorized Hetzner only. The public runtime is stalled after an unhandled Wine-hosted Dedicated exception, while its old monitor stopped at128MiB cgroup OOM/start-limit. Requiring a healthy public roster before restoring read-only telemetry prevents that telemetry from describing an outage.

Decision: restore only `tse-public-health.service` using the immutable existing PR50 `b5a6cba` bundle, validated in an isolated service-shaped probe. Keep CPUQuota5%, MemoryMax128M, hardening, output path and the `monitor` action. Pin all four source files. No public game process signal, DLL/config update, recovery, reboot or rollout. New private supervisor source83d2bec is not deployed.

Proof: seven complete warm probe samples,207 historical external faults retained, query failure and unknown population explicit, peak33,984,512bytes, no OOM; service syntax and source-pin checks passed. Production monitor resumes current writes and completes its bounded scan. Original public identities and12 binary pins remain intact. See [incident report](../reports/2026-10-24-live-reliability-handoff.md).

This narrow exception supersedes only the old healthy-roster precondition for read-only incident telemetry restoration. All disruptive maintenance and native production qualification gates remain. Configuration rollback material is preserved privately; the known OOM old reader is not represented as a healthy operational fallback. No new independent WAN/Windows, native-hour or24/7 acceptance follows.
