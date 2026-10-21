# CPU measurement protocol for TSE 1.07 bots on Hetzner

**Date:** 2026-10-22 · **Status:** protocol + implemented tooling.
**Supersedes the method** of the 2026-10-21 Wine A/B, which ran under a shared
45 %-of-one-core cgroup cap and produced no active-bot evidence.

This document defines when a CPU number may be used in a saving claim. The
tools enforce it; the operator does not have to remember it.

## 1. Preconditions (hard)

| Gate | Why | Enforced by |
| --- | --- | --- |
| Isolated client copy, own Wine prefix, own UDP port, own Xvfb display | production must keep running | `hetzner_preflight.sh` (port free, path marker, version marker) |
| No cgroup CPU quota below the expected demand, or no quota at all | a capped run measures the cap | `hetzner_preflight.sh` + `tse_cpu_profile.py analyze` |
| Bot driver proven active for the whole window | an idle client is not a bot client | `bot_telemetry.py` → `ACTIVE_OK` |
| Same map, mode, bot count, KI profile, FPS settings, binary | otherwise the difference is not the optimisation | profiles differ in one line (`test_p0_candidate_source.py`) |
| Host headroom reported with every repetition | the 2-vCPU host also serves production | sampler (`host.busy`, `load1`) |
| Server population stable during the window | proves the workload existed | `gamespy_query.py` |

Any failed precondition turns the window into `NOT_QUALIFIED`. The numbers are
kept, but they must not appear in a "saving" column.

## 2. What is actually being measured

`tse_cpu_profile.py sample` reads, every 0.5 s:

- `/proc/<pid>/stat` (process `utime`+`stime`) → **fraction of one core**;
- `/proc/<pid>/task/*/stat` + `comm` → CPU split into **main**, **llvmpipe**
  and **other** threads (this is how the software renderer becomes visible);
- `VmRSS`;
- the process cgroup's `cpu.stat` (`nr_periods`, `nr_throttled`,
  `throttled_usec`) and `cpu.max` / `cfs_quota_us`;
- host `/proc/stat` (busy fraction) and `/proc/loadavg`.

`tse_cpu_profile.py analyze` reduces this to medians/p95 per role
(`client`/`server`), the thread-group shares and a validity verdict.

Cost categories from the task, and what can honestly be separated today:

| Category | Separable? | How |
| --- | --- | --- |
| A. World simulation | partly | main-thread CPU when the bot driver is inactive vs active at the same map |
| B. Rendering (engine scene graph) | partly | `render_skip_d ≈ frames_d` in the null variant removes the GameMP view rendering; the residual main-thread cost is not the scene |
| C. Wine/OpenGL/llvmpipe | yes (share) | `thread_cpu.llvmpipe` from the per-thread sampler |
| D. Bot KI | yes, as a difference | same client, same map, `bot_bEnabled=0` vs `1`, identical render mode |
| E. Network | no | needs runtime instrumentation; the existing profile only shows it inside the main thread |
| F. Engine main loop | yes (rate) | `frames_d` per second |
| G. Lock waits | yes | `lock_ms_max` and `lock_ms_last` from the candidate; `stall_s` shows a blocked timer |

Category E is a real gap. Do not present a main-thread number as
"simulation" if the network path is inside it.

## 3. Run protocol

1. **Warmup:** 300 s, excluded from analysis (`--warmup 300`). Loading, texture
   upload and the first joins are not steady state.
2. **Measurement:** 600 s per repetition.
3. **Repetitions:** 3 per variant, **alternated** A/B/A/B/A/B. Do not run all
   A first and all B later: production load, llvmpipe thermal behaviour and
   page cache drift would be attributed to the variant.
4. **Restart the client between repetitions** (fresh process, fresh
   `BotTelemetry.csv`). Keep the server running.
5. **Identical workload:** four bots per client, same map (`Yodeller`),
   Deathmatch, same KI profile, same FPS cap. The two client profiles differ
   only in `bot_bNullRender`.
6. **One binary.** Both variants use the same candidate DLL; only the startup
   script differs. A rebuilt DLL would add a second variable.
7. Record `nproc`, `load1/load5`, `MemAvailable`, cgroup path and quota with
   every repetition (the harness writes them into `evidence.json`).

## 4. Qualification of a saving

For each repetition the analyser produces the client's median core usage.
`compare` then requires **all** of the following:

- every repetition is `valid` (no throttling, host < 90 % busy, not at machine
  capacity, processes alive, ≥ 10 samples);
- at least **3 repetitions per variant**;
- **non-overlapping spread**: `max(candidate) < min(baseline)`;
- a positive median difference.

Only then is the result labelled `QUALIFIED_MEASUREMENT`. This is deliberately
conservative: with three repetitions it is the cheapest way to avoid declaring
noise as a saving. A 5 % difference inside a 10 % run-to-run spread is not
evidence.

`QUALIFIED_MEASUREMENT` still says nothing about gameplay, CRC or sync. Those
gates are separate and mandatory.

## 5. Bot scaling: do not divide by four

A four-bot client's CPU consists of

```
C(4) = fixed_client_cost + 4 × incremental_bot_cost
```

`C(4)/4` therefore includes a quarter of the fixed client overhead (Wine, GL
context, engine main loop, network). The incremental cost must be measured:

```
incremental_bot_cost ≈ (C(4) − C(1)) / 3
fixed_client_cost    ≈ C(1) − incremental_bot_cost
```

Measure 1, 2 and 4 bots on the same client, map and profile. Two caveats:

- With rendering enabled, a split-screen client renders one viewport per local
  player, so `C(4) − C(1)` also contains three extra viewports. That is a real
  cost of the current architecture, but it is **not** bot AI.
- With `bot_bNullRender=1` the viewport cost disappears, so the same
  difference then approximates simulation + AI + network.

Do not extrapolate beyond measured counts (4 → 8 → 12 → 16) without
measurement; server-side cost grows with participant count and the 2-vCPU host
has no headroom for guesses.

## 6. Host contention

The production fleet runs on the same two vCPUs. That does not invalidate an
A/B, but it limits the claim:

- Alternate A/B windows (see §3) so both variants see similar contention.
- Report `host.busy` and `load1` with every repetition.
- A run where the host is > 90 % busy is marked invalid unless the operator
  explicitly records `--allow-busy-host`; then the result is a *comparison
  under contention*, never an absolute capacity statement.
- Absolute capacity ("how many bots fit") requires a quiet host or a second,
  authorised test instance. Neither is assumed here.

## 7. Commands

```bash
# preflight (read-only)
tools/benchmarks/hetzner_preflight.sh --runtime <client> --dll <GameMP.dll> \
    --port 26860 --max-load 3

# one repetition (never starts or stops a process)
tools/benchmarks/measure_window.sh --label ab-A-rep1 --out evidence/ab-A-rep1 \
    --pid <client>:client --pid <server>:server \
    --duration 600 --warmup 300 --interval 0.5 \
    --telemetry <client>/Bin/BotTelemetry.csv --expect-bots 4 \
    --expect-nullrender 0 --require-cwd /srv/tse-cpu-opt-candidates-20261022 \
    --server <isolated-server>:26860 --expect-players 5 --expect-prefix <prefix>

# repeat for ab-B (expect-nullrender 1), then
python3 tools/benchmarks/tse_cpu_profile.py compare \
    --baseline evidence/ab-A-rep1/cpu-analysis.json \
    --baseline evidence/ab-A-rep2/cpu-analysis.json \
    --baseline evidence/ab-A-rep3/cpu-analysis.json \
    --candidate evidence/ab-B-rep1/cpu-analysis.json \
    --candidate evidence/ab-B-rep2/cpu-analysis.json \
    --candidate evidence/ab-B-rep3/cpu-analysis.json \
    --out evidence/ab-verdict.json
```

## 8. Acceptance gates that remain outside this protocol

A measured CPU difference does not qualify a candidate. The native gates from
`AGENTS.md` stay in force: vanilla 1.07 client joins and sees the bots, CRC
passes, 60 minutes without new `SYNCBAD`, combat/kills/respawn, map change,
reconnect, clean disconnect without ghosts, and `ser_iKickOnSyncBad` unchanged.
