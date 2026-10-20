# Hetzner CPU and Headless Optimization Investigation Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Reduce CPU usage per four-bot TSE Retail 1.07 Wine client while maintaining unchanged server/client vanilla compatibility, BotDriver behavior, and network synchronization.

**Architecture:** Establish a repeatable no-modification baseline first. Apply reversible graphics/FPS experiments only to isolated runtime copies, then evaluate a separate null-renderer/headless candidate against exactly the same multiplayer gates; do not change public production Wine processes.

**Tech Stack:** Ubuntu 24.04, Wine, Xvfb, Mesa llvmpipe, TSE Retail 1.07, native `GameMP.dll` / BotDriver, Linux `pidstat` or `top`, native UDP queries, Windows vanilla observer, Python post-processing.

**Spec / evidence:** [2026-10-21 eight-bot performance baseline](../../reports/2026-10-21-hetzner-eight-bot-cpu-headless-baseline.md); existing `AGENTS.md` and qualified native runtime reports remain controlling.

## Global constraints

- Never modify live public server/clients, their game binaries, DLLs, logs, ports or Wine prefixes to run experiments.
- No Git modifications in another active Codex agent's checkout or another agent's branch; own branch/worktree only.
- Retail 1.07 cannot assume ABI/CRC/network compatibility from Serious Engine 1.10 source.
- Preserve the original dedicated server and unmodified human observer.
- Any rebuilt DLL becomes a **new unqualified candidate**.
- Do not use `ser_iKickOnSyncBad=0` to hide desync.
- Exclude game binaries, private raw logs, secrets and individual player data from public commits.
- Baseline and each candidate must have independent evidence and clear pass/fail gates.

## Review focus

1. Low render FPS may throttle native update/action timing; explicitly compare input ticks and server game progression.
2. Disabling draw calls may still require context/GL state initialization; measure actual CPU, not window visibility.
3. One-client/four-bot average is not incremental per-bot cost; benchmark 1, 2, 4, and 8 bots separately.
4. Software-renderer CPU can vary with simultaneous human observers and map complexity; same map/workload is mandatory.
5. Existing sync crashes from non-qualified candidates must not be dismissed by short join tests.

## Tasks and completion criteria

### Task 1 — Record an immutable live baseline (read-only)

**Files**
- Create: `docs/reports/YYYY-MM-DD-hetzner-cpu-measurements.md`
- Optional sanitized measurements: `docs/evidence/hetzner-cpu-*.csv`

- [ ] Record runtime IDs, Wine/Xvfb/Mesa versions, map name, server identity, player count and command-line configuration. No private logs.
- [ ] Acquire 5-10 minutes of CPU and RSS samples per dedicated/client/wineserver; store time stamps and sampling intervals.
- [ ] Record independent UDP population and native sync/CRC/driver heartbeats during same window.
- [ ] **Verification:** CPU sample files can be reprocessed; server population stable; no process writes/stops; clearly mark gaps.

### Task 2 — Isolated graphics/FPS comparison

**Files**
- Create: `tools/benchmarks/tse_cpu_profile.py` (parser / aggregate, if necessary)
- Test: `tools/benchmarks/test_tse_cpu_profile.py`
- Create: `docs/reports/YYYY-MM-DD-low-render-ab.md`

- [ ] Write regression tests for per-process percent-to-CPU-core normalization, missing samples, and shared client overhead; verify expected tests fail before implementation.
- [ ] Implement minimal parser and run unit tests to completion.
- [ ] Provision an independent Wine-prefix/runtime copy with separate server ports and Xvfb display; record immutable hashes. Do not reuse production `BotTest` ports.
- [ ] Compare current rendering, minimum graphics, and bounded 10/20/30 FPS with identical 1/4/8-bot workload; confirm graphics flags or caps are real, not ignored.
- [ ] Record median, p95 CPU, RAM, tick continuity, player population, and sync outcomes for each condition.
- [ ] **Verification:** positive or negative CPU effect quantified, with confidence limits and native 1.07 regression gate. Stop/revert any candidate at first genuine sync failure.

### Task 3 — Null-renderer technical feasibility (design before patch)

**Files**
- Create: `docs/research/YYYY-MM-DD-tse107-null-renderer-feasibility.md`
- Create: `docs/superpowers/specs/YYYY-MM-DD-tse107-null-renderer-design.md` only if implementation is selected

- [ ] Inspect Croteam 1.10 main-loop and renderer dependencies, then verify relevant entrypoints with *owned and authorized* Retail 1.07 binaries (Ghidra/REA as needed).
- [ ] Distinguish skipping presentation, skipping scene-draw, preserving context without draw calls, and removing GL/Xvfb startup entirely.
- [ ] Map engine/timer/network/physics/input dependencies and concrete failure points.
- [ ] Compare patch versus clean-room client based on implementation risk, CPU potential and long-term maintainability.
- [ ] **Verification:** function-level evidence plus a bounded prototype test plan; no compatibility or saving claims without actual 1.07 measurements.

### Task 4 — Protected candidate evaluation

**Files**
- Create: `docs/reports/YYYY-MM-DD-headless-retail107-acceptance.md`

- [ ] Build candidate with proven binary provenance and separate signature/hash; never overwrite qualified `61DC...` runtime DLL.
- [ ] Compare against control under identical CPU, bot-count, map and server configurations.
- [ ] Verify human vanilla observer join, CRC, 20 Hz synthetic inputs, visible movement/combat, no sync anomalies, no player ghosts.
- [ ] Execute 60-minute stability gate and independent network/server-side log evaluation before describing headless runtime as qualified.
- [ ] **Verification:** accepted only with actual CPU reduction, stable join/sync/combat, clean shutdown and reproducible evidence. Reject/revert if any required gate fails.

### Task 5 — Resource-capacity and operating economics

**Files**
- Create: `docs/reports/YYYY-MM-DD-hetzner-bot-density-capacity.md`

- [ ] Run only approved 4/8/12/... bot tests in isolated instances; do not infer capacity by linear extrapolation.
- [ ] Record CPU saturation, p95 delays, active population, bot decision latency, map and concurrent human effects.
- [ ] Calculate safe headroom for 2/4/8 vCPU profiles from actual validated data.
- [ ] **Verification:** report maximum *measured stable* density and separate hypothetical estimates; do not claim production 24/7 until watched for 24h.

## Progress ledger

- 2026-10-21: **Planning/documentation only.** Verified two software-rendered four-bot Wine clients and a 2-vCPU resource bottleneck in a short live snapshot. No optimization implemented, no candidate acceptance or increased bot capacity established.
- Tasks 1-5: **NOT STARTED**. Complete each only with reproduced evidence and a separate isolated execution workspace.
- Ownership: next assigned implementation agent, with non-conflicting branch/worktree and explicit separation from the live Codex session.
- Next action: Task 1 sampling/read-only, then Task 2 controlled A/B. Do not substitute a new architecture before these measurements.

## Handoff

Production and parallel Codex processes must remain running and unmodified. Integration needs a code review, isolated test evidence, and a deliberate merge decision; publishing this plan itself is not a runtime authorization.
