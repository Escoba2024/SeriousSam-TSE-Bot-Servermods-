# Hetzner CPU P0 Recovery — 21.10.2026

## Scope and actual result
The public eight-bot fleet was intentionally stopped under the operator's current instruction to free the 2-vCPU host for uncontaminated CPU qualification. No active measurement was found before shutdown. Before closing, UDP showed exactly the eight expected HetznerFleetA/B players and no external player. Both clients exited via WM_DELETE_WINDOW; their logs reported stopping game and renderer cleanup. A fresh UDP query returned zero players. The empty dedicated was then terminated with SIGTERM. Public UDP 25600/25601 listeners are absent. The unrelated existing Codex session was preserved.

Production GameMP.dll hashes remain 61DC27E0E7B80BADCF9AE705C30FCA88EDD3935737715DFFFF59E90C26F1FEF9 in both clients. No production DLL or INI was changed. Restart remains possible from the existing launch scripts; do not restart during the private measurement.

## Root cause and minimal fix
The previous A/B runner created HetznerCPUBenchmark.ini as root:root mode 0600 and then ran Wine as uid/gid 65534. The native client log explicitly recorded Cannot load script file / Permission denied. The bots therefore joined using persisted local player settings without enabling BotDriver or the requested render switch. Those old CPU comparisons test neither active bots nor the intended rendering setting.

A real uid-65534 read reproduced PermissionError before the fix. The corrected script is atomically created with runtime ownership and mode 0600; the runner verifies readability as nobody before launch. No timer or lock change was needed for this cause.

## Actual corrected native smoke
Two isolated network-namespace Wine runs, unchanged Retail server, four local bots, candidate DLL SHA256 4F74146EB4E8B640E1D5A080D61D311C6965F1BFB071160F0753C370929C54FB, Xvfb :116, Mesa llvmpipe. Private test cgroup cpu.max was max 100000.

| Gate | Render on | Null render |
|---|---:|---:|
| CRC OK | 1 | 1 |
| Joined local players | 4 | 4 |
| All four local slots logged ticks | yes | yes |
| Tick maximum per slot | 1180 | 1180 |
| Bot0 tick delta / 18s sample | 360 | 360 |
| Observed action rate | about 20 Hz | about 20 Hz |
| Unique logged positions per slot | 43 / 37 / 35 / 40 | 39 / 34 / 34 / 39 |
| fire=1 log markers | 20 | 7 |
| Kill log markers | 8 | 7 |
| Observed CRC/sync error markers | 0 | 0 |
| Short client CPU, percent of one core | 113.94 | 26.50 |

**CPU values NOT QUALIFIED.** These are 18-second diagnostic windows, no repeated ten-minute samples. Portable compilation overlapped the smoke. They are not a reproducible savings claim, capacity estimate, AI equivalence test or 60-minute synchronization acceptance. Full multiplayer/vanilla observer, map transition, reconnect and clean-disconnect acceptance are still pending.

## P1 run now in progress
Versioned tools/benchmarks/run_hetzner_wine_ab.py executes three runs per mode with alternating order, waits for CRC/join and bot readiness, warms up 180 seconds after readiness, then measures 600 seconds. Same fixed Yodeller map and client settings; no scheduled map change during the measurement. Expected wall duration approximately 80 minutes. Only this dedicated test server and four bots are permitted while the public fleet is stopped.

The runner rejects unreadable scripts, missing local slots, rate outside 19–21 Hz, no observed motion, tick resets, SYNCBAD/CRC failures, new cgroup throttling and host saturation. It records client mean/median/p95/peak CPU, server CPU, total test-cgroup CPU, host utilization/steal, thread CPU, RSS and per-slot action rates. Incremental and final JSON plus logs remain private on Hetzner. Even a successful CPU A/B is explicitly not a full production release.

## Reproducible tests
- Real native permission repro: unreadable before correction; runtime-readable nobody:600 script and active bots afterwards.
- Python benchmark source and evidence guards: 13 tests passed (9 evidence/permission regressions + 4 existing null-render source guards).
- Six portable C++ botcore test executables: all passed. No GameMP rebuild claimed.
- Python fixture correction during development: no-motion fixture originally replaced overlapping substrings; changed to a complete position regex. Final tests pass; no fixture result is native runtime evidence.

## Build prerequisites and stop condition
The pinned SE1-ModSDK was retrieved directly on Hetzner: aa7869c2c2c4db0562281814d0ac3784e6b9d6f0 with Includes 94ff8cd0e63941f8601294350b616472f772ed51. SDK header/import-library absence is resolved.

No installed MSVC-compatible compiler or Windows SDK was found. Existing g++ alone cannot be claimed ABI-compatible with Retail MSVC C++ modules. msvc-wine source was prepared and its upstream Visual Studio 2022 manifest inspected without accepting terms or installing Microsoft software. Minimal x86 selection: approximately 922 MB download and 3.68 GB reported installed bytes; temporary unpacking headroom must be rechecked against about 6 GiB free before installation. Exact JSON proposal remains private.

Microsoft's installer explicitly requires acceptance of https://go.microsoft.com/fwlink/?LinkId=2179911 . That license acceptance has not been authorized or performed. New GameMP/BotHost builds and subsequent native acceptance remain blocked pending that specific authorization and successful toolchain setup. No Shadow use, no new agents, no paid resources, no automatic production deployment or merge.

## Optimization status
| Optimization | Status | CPU before | CPU after | Savings | Conditions | Action rate | Sync | Vanilla join | Production |
|---|---|---|---|---|---|---|---|---|---|
| Benchmark script ownership | P0 native smoke passed | not an optimization metric | not applicable | not applicable | isolated 4-bot smoke | about 20 Hz | no short-run errors | pending | no change |
| GameMP null render | CPU A/B RUNNING; NOT QUALIFIED | diagnostic 113.94% | diagnostic 26.50% | NOT QUALIFIED | 18s smoke only; full repeats pending | about 20 Hz in smoke | 60min pending | observer pending | not released |
| FPS20/30/40 and Mesa thread tuning | pending | not measured comparatively | not measured comparatively | NOT QUALIFIED | separate one-variable tests required | pending | pending | pending | not released |
| Native headless BotHost, no Xvfb/GL | build prerequisite blocked | not measured | not measured | NOT QUALIFIED | Microsoft toolchain/license pending | pending | pending | pending | not released |
| AI caching/raycast changes and capacity | pending | not isolated | not isolated | NOT QUALIFIED | after timing/render gates | pending | pending | pending | not released |
