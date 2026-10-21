# Measurement tooling (P0/P1) – read-only

Everything here observes a running experiment. Nothing starts, stops, reniches
or signals a game process. The only writes are the evidence files you pass on
the command line.

| Tool | Purpose | Exit codes |
| --- | --- | --- |
| `hetzner_preflight.sh` | GO/NO-GO for an isolated runtime: path marker, version marker, binaries, cgroup quota/throttle counters, host headroom, free port | 0 GO, 9 NO-GO, 2 usage |
| `measure_window.sh` | one warmup+measurement window: CPU sampler + bot telemetry + server population, writes `evidence.json`/`summary.md` | 0 QUALIFIED_WINDOW, 6 CPU invalid, 3 bots inactive, 4 stalled, 8 population, 2 usage |
| `tse_cpu_profile.py` | `sample` procfs/cgroup, `analyze` per-role medians + validity, `compare` ≥3 repetitions | 0 ok/valid/QUALIFIED, 6 invalid, 7 unqualified, 2 usage |
| `bot_telemetry.py` (in `tools/`) | parse the candidate CSV and decide ACTIVE/INACTIVE/STALLED/ACTION_STARVED | 0 ACTIVE_OK, 3 INACTIVE, 4 STALLED, 5 NO_DATA, 2 usage |
| `gamespy_query.py` (in `tools/`) | read-only GameSpy v3 population/scores | 0 ok, 8 expectation/timeout, 2 usage |

## Order of operations

```bash
# 0. build and record the candidate hash (see poc/candidates/.../README.md)

# 1. never sample production: create/choose an isolated runtime below
#    /srv/tse-cpu-opt-candidates-<date>/ and let the preflight check it
tools/benchmarks/hetzner_preflight.sh \
    --runtime /srv/tse-cpu-opt-candidates-20261022/hetzner-ab/client \
    --dll     /srv/tse-cpu-opt-candidates-20261022/hetzner-ab/client/Bin/GameMP.dll \
    --port 26860 --max-load 3

# 2. start the isolated client with the diagnostic profile, then:
tools/benchmarks/measure_window.sh --label p0-diag --out evidence/p0-diag \
    --duration 120 --warmup 30 --interval 0.5 \
    --pid <client-pid>:client --pid <server-pid>:server \
    --telemetry <client>/Bin/BotTelemetry.csv --expect-bots 4 \
    --expect-nullrender 0 \
    --require-cwd /srv/tse-cpu-opt-candidates-20261022 \
    --server <server>:26860 --expect-players 5 --expect-prefix <prefix>

# 3. only if that is QUALIFIED_WINDOW and the telemetry says ACTIVE_OK:
#    3x variant A, 3x variant B (alternating), then
python3 tools/benchmarks/tse_cpu_profile.py compare \
    --baseline evidence/ab-A-rep1/cpu-analysis.json ... \
    --candidate evidence/ab-B-rep1/cpu-analysis.json ...
```

## What counts as a valid window

`tse_cpu_profile.py analyze` marks a repetition **invalid** when any of these
is true (numbers, not impressions):

- cgroup throttled > 1 % of periods or > 2 % of wall time;
- host CPU busy > 90 % median (override only with `--allow-busy-host`, and then
  the result is a *comparison under contention*, not a capacity claim);
- a sampled process is ≥ 90 % of the whole machine;
- fewer than 10 samples after warmup, or a process disappears.

`compare` additionally requires ≥ 3 valid repetitions per variant and a
non-overlapping spread (`max(candidate) < min(baseline)`).

## Known limits

- The sampler measures the **Linux process**, i.e. the whole Wine process. The
  per-thread split attributes llvmpipe by thread name; everything else is
  "other" and cannot be separated into engine/AI/network without runtime
  instrumentation.
- `bot_telemetry.py` proves the action pipeline, not gameplay, sync or CRC.
- A `QUALIFIED_WINDOW` is a measurement verdict only. The native acceptance
  gates (vanilla join, CRC, 60 min, map change, reconnect, clean disconnect)
  remain mandatory and are not automated here.
