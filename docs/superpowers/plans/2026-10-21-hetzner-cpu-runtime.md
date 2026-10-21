# Hetzner CPU Runtime Implementation Plan

> Execute inline with superpowers:executing-plans. No additional agents.

**Goal:** Restore active bot evidence and measure real Wine null-render costs without quota distortion.
**Architecture:** Isolated loopback/netns Wine copies, unchanged original modules and opt-in candidate DLL; public fleet stopped under current user authorization.
**Tech Stack:** Python 3, Linux procfs/cgroup v2, Wine x86, Xvfb, Retail 1.07.
**Spec:** User master goal supplied 2026-10-21, phases P0-P6.

## Constraints
Hetzner only; preserve qualified DLL and other active agent; no CRC/sync suppression; at most 4 local players/client. Public shutdown expressly authorized when not measured.

## Review Focus
Unreadable root-created INI; capped cgroup; no active ticks; changing maps mid-sample; rendering setting not actually applied.

## Tasks and acceptance
- [x] Inventory process ownership and active measurements. Found no measurement; public bots closed by WM_DELETE_WINDOW, zero players verified before dedicated SIGTERM. Other Codex process preserved.
- [x] Reproduce P0 failure: INI root:root 0600 is unreadable to runtime nobody. Native log explicitly reports Permission denied.
- [x] Correct isolated harness INI ownership, assert readable under runtime uid; forbid saturated/throttled comparisons; require per-slot tick evidence.
- [x] Run isolated P0 smoke in both render modes; CRC/join, ticks, movement and config load must pass. Smoke is not benchmark qualification.
- [ ] If smoke passes, 3 repeats per render variant: 180s warmup + 600s measurement; identical fixed map/settings; capture CPU distributions, throttling, ticks, sync and memory. Reject errors, not conceal them.
- [ ] Examine real headless and build prerequisites on Hetzner; build/run only if ABI-compatible SDK/compiler/import libraries are present. Document exact blockers otherwise.
- [ ] Run appropriate portable harness/source checks; commit source, sanitized report, plan; preserve private runtime logs outside Git. No production deployment without all native gates.

## Rulings and evidence
2026-10-21: Current direct shutdown authorization supersedes attached production keep-running clause only as needed to free benchmark CPU. No production DLL or configuration changed.

## Current handoff
P0 native smoke passed; full P1 runner started on Hetzner only. Private output /srv/tse-cpu-opt-candidates-20261021/hetzner-ab-20261021/qualification-20261020-235444/result.json and /srv/tse-cpu-opt-candidates-20261021/qualification-run.out. Preserve the running measurement. No final CPU saving claimed. SDK pins installed; new builds need authorized Microsoft license acceptance and a functioning compatible toolchain. Public fleet remains intentionally stopped. See docs/reports/2026-10-21-hetzner-cpu-p0-recovery.md.

## 2026-10-21 Microsoft toolchain authorization
Operator explicitly approved license acceptance and installation. Minimal VS2022 x64-host/x86-target tools and Windows SDK 10.0.19041 selected; approximately 950 MB download and 3.59 GB reported installed. Install starts only between completed benchmark samples; private build Wine prefix. Required proof: cl/link invocation, generated PE32 x86 executable, execution under Wine; then GameMP build if prerequisites pass.

## Arena handoffs refreshed before continuation
PR42 f3c9384, PR43 b85df58, PR44 7d9e695 fetched and reviewed at exact heads. All stated portable suites rerun on Hetzner: 9 + 65 Python tests; seven C++ suites including 555 human-AI checks, block smoke and patch/provenance checks pass. PR43 CSV formatter has 22 conversions for 21 arguments; effective +script configuration snapshot and telemetry shutdown need review. PR42/44 patches overlap and do not stack cleanly. No merge/deployment. See docs/reports/2026-10-21-arena-pr42-44-integration-review.md. Microsoft toolchain installation and PE32 x86 compile/link/execute proof now passed; GameMP target include path corrected in a one-translation-unit retry, full DLL build pending.

Corrected full GameMP build queued at the next completed CPU-window boundary via private continue_gamemp_build_between_samples.py; state /srv/tse-cpu-opt-candidates-20261021/gamemp-build-queue.json. It never replaces runtime DLLs, preserves completed samples and resumes the benchmark. License installation is complete; do not ask for that authorization again.
