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
