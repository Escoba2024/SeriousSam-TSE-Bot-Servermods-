# Individual sessions and two-server capacity: separate architectures

Verified Hetzner-only source/evidence review, 22 October 2026. PR47 head `b75f14d62f6d8b7705093643ce461e484a8ffc17` was checked in a new detached review worktree; its original worktree was preserved. Its124 Python tests pass again. No planner, profile adapter or lifecycle bridge was reimplemented, and no new individual-client load was started alongside the supervisor hour.

## What PR47 already qualifies

The retained native evidence supports a bounded four-client lifecycle:360s measurement/389.459s with drain, eight joins, seven regular leaves, one own process crash and cooldown/rejoin, two database reopenings, unchanged identities/GUIDs,20Hz per single-player client, no sync/fatal error in complete generations. Opt-in four-color and conservative22-visible/32-decorated-byte names were tested with an original Wine client. These are real bounded observations; they do not qualify eight normal independent sessions, full controller-loss adoption or an active independent remote human PC.

The default identity/session implementation remains inactive for production. Build04 and the eight public bots are retained.

## Measured resource blocker

| Prior isolated architecture/test | Actual result |
|---|---|
| Four individual clients,360s | Private cgroup peak1157.992MiB; host mean65.602%, P9584.397%; limited lifecycle PASS |
| Four individual clients, low-memory graphics,150s | Peak1047.352MiB; cgroup CPU71.923% of one core; limited PASS |
| Eight-client attempt, ordinary graphics | Stopped before client6: MemAvailable970.465MiB, required1068MiB; peak1322.781MiB;20/20 unmounts |
| Eight-client attempt, low-memory graphics | Stopped before client7, six connected: MemAvailable921.137MiB, required1068MiB; peak1389.926MiB;20/20 unmounts |
| Eight grouped bots, two four-player processes, prior PR49 hour | Process RSS maxima server51532KiB, botA187880KiB, botB186300KiB; native final-source capacity remeasurement pending |

Exact prior grouped PSS maxima: server35478KiB, botA122200KiB, botB120593KiB. PSS/RSS exclude other Wine helpers, Xvfb, kernel and page-cache charges; individual-client cgroup peaks include them. They must not be equated. Low-memory four-client peaks differ by110.641MiB (~9.55%) across different durations and lifecycle windows; that is an observed peak difference, not a controlled causal estimate or an eight-client qualification.

No threshold was lowered and no swap added to force a pass. The reported capacity failure is genuine under the tested concurrent public fleet and protected reserve. CPU is also a concern: four individual clients already reached hostP9584.4%, below the desired30% reserve.

## Safe alternatives and hardware envelope

The existing two-four-player-process architecture demonstrably shares process/Wine/render overhead and remains the qualified production choice. Its identities are configurable, but independent per-player joins/leaves within those grouped processes would require a separately verified Retail player-source lifecycle; the current SQLite single-process executor cannot simply be relabeled as that implementation. No unproven ABI change is proposed for production.

For eight independent session clients alongside the protected public fleet, a **4-vCPU/8-GiB test host** is a conservative next qualification target. This is a technical test envelope, not measured capacity or a purchase instruction: eight individual clients plausibly add around2GiB including overhead, the current system already needs its public/OS/services plus protected reserve, and the observed CPU peak makes a RAM-only upgrade insufficient assurance. Repeat startup, representative normal sessions, Originalclient coexistence and>=3600s gates on the actual machine. No infrastructure was ordered.

Two servers with eight **grouped** bots each are a different capacity question. The prior PR49 hour concurrently ran public8 plus private8 at host mean60.70%, P9564.82%, no new throttles; that is useful historical evidence for that exact source. The current new-source hour records current/peak cgroup memory, host available RAM, CPU and both populations. Its final result must establish reserve anew. Even a passing local two-instance hour does not establish second-public-instance WAN/listing,24/7, real reboot, multi-map behavior or sixteen independent session processes.
