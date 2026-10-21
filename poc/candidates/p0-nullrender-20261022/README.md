# P0 candidate: evidence telemetry + null renderer (2026-10-22)

**Status: NOT BUILT, NOT RUN, NOT QUALIFIED.** This directory contains source
that has only been checked statically and compiled as isolated C++ with Win32
stubs. It has never been built with MSVC, never loaded by 1.07 and never
measured on Hetzner.

It exists because the 2026-10-21 A/B could not answer its own question: four
players joined, but there was no proof of a single bot tick, and the CPU number
was produced under a 45 %-of-one-core cgroup cap that both variants hit
(35.56 % each). See
`docs/reports/2026-10-22-p0-bot-tick-diagnosis.md`.

## Provenance

| Item | Value |
| --- | --- |
| Base | `poc/release/gamemp/` at commit `30a6747` — the source of the qualified DLL |
| `Game.cpp` base SHA-256 | `01dfa59857df4953d3a89096cd8049b9ba022f81e388c0dfc52b4826909474b6` |
| `BotDriver.cpp` base SHA-256 | `b5d3290391b2504cce96529155b4072361fed0319a80ad1695707e36a9165c64` |
| `BotDriver.h` base SHA-256 | `82c8282d1426177031cdaa3f140fd084c2ddcf51cb74bfd694e49af90e8d0a3d` |
| Overlay files | `Game.cpp`, `BotDriver.cpp`, new `BotTelemetry.h` |
| `BotDriver.h` | **unchanged** (the overlay does not need it) |
| `apply.sh` | verifies the three hashes, copies the release tree, overlays the files |

`poc/release/gamemp/` is never modified. The qualified DLL `61DC27E0…F1FEF9`
and the public fleet are untouched.

## What the overlay changes

1. **Evidence layer** (`BotDriver.cpp`, `BotTelemetry.h`, one config call and
   one frame counter in `Game.cpp`)
   - a watchdog thread writes `BotTelemetry.csv` next to the executable
     (or to `$TSE_BOT_TELEMETRY`), one row per second, using raw `WriteFile`
     so a CRT shutdown cannot crash it during disconnect;
   - `BotDriver_HandleTimer()` counts **every** invocation before any
     early-out, with explicit `disabled` / `gameoff` / `nolocal` counters;
   - `SetAction()` calls, `GameMainLoop()` frames and missing player entities
     are counted separately;
   - the `ga_csNetwork` wait is measured with `QueryPerformanceCounter`;
   - `#build`, `#exe` and `#config` lines identify the binary and the switches
     that the startup script actually produced;
   - `stall_s` grows while the driver is enabled and in game but no timer
     invocation arrives — the deadlock discriminator.

2. **Null-render layer** (`Game.cpp`, opt-in, default off)
   - `if (bot_bNullRender && gm_bGameOn && !_pNetwork->IsServer() && _fnmThumb=="") return;`
     at the very top of `CGame::GameRedrawView()`, i.e. **before**
     `CTSingleLock slBotRender(&_pTimer->tm_csHooks, …)` is taken;
   - skipped/drawn frames are counted, so the switch is provable;
   - optional pacing (`bot_iNullRenderFps`, default 0 = native engine pacing).

Both layers live in one binary so that the A/B differs only in one startup
line (`bot_bNullRender`), not in a rebuild.

## Build

```bash
poc/candidates/p0-nullrender-20261022/apply.sh /srv/tse-cpu-opt-candidates-20261022/gamemp-p0
msbuild /srv/tse-cpu-opt-candidates-20261022/gamemp-p0/Game.vcxproj \
    /p:Configuration=Release_TSE107 /p:Platform=Win32
sha256sum /srv/.../Bin/GameMP.dll
```

- The result is a **new, unqualified** candidate. Record its SHA-256.
- Never overwrite `61DC…` in a runtime that serves players.
- If the build fails, stop and report the compiler error — do not "fix" the
  release tree.

`BotTelemetry.h` is a header; no `.vcxproj` change is required because the
implementation lives in `BotDriver.cpp`, which is already in the project.

## Switches

| Switch | Default | Meaning |
| --- | --- | --- |
| `bot_iTelemetry` | **1** | 0 = no per-second rows (manifest/state lines only) |
| `bot_bTelemetryConsole` | 0 | 1 = one `[BotP0]` summary line every 5 s |
| `bot_bNullRender` | 0 | 1 = skip `GameRedrawView` for non-server, non-thumbnail frames |
| `bot_iNullRenderFps` | 0 | >0 = pace skipped frames to this FPS (opt-in, not validated) |
| `bot_iLogEvery` | 40 | existing per-bot console log interval |

Telemetry defaults to **on** in this diagnostic build on purpose: the failure
mode to avoid is a run that produces no evidence. Set `bot_iTelemetry=0` for a
behavioural control.

If `bot_bNullRender=1` is set without `bot_bEnabled=1`, the build logs a
warning and records `#config,bot_enabled=0`; that combination cannot produce
bot evidence.

## Reading the result

```bash
python3 tools/bot_telemetry.py <client>/Bin/BotTelemetry.csv --warmup 30 \
    --expect-bots 4 --expect-nullrender 1 --json analysis.json
```

Exit codes: 0 `ACTIVE_OK`, 3 `INACTIVE` (disabled / game off / no local
players), 4 `STALLED` (timer stopped or actions starved), 5 `NO_DATA`.
The tool proves the action pipeline; it says nothing about gameplay, sync or
CPU.

## Known limits and risks

- **Not headless.** The GL context, Xvfb, `SwapBuffers`, the EXE main loop and
  the engine timer all remain. This removes the GameMP view rendering, nothing
  else.
- **Busy-loop risk.** `sam_iMaxFPSActive` is an EXE symbol that does not exist
  in GameMP. If the outer loop only throttles inside the render callback, the
  null variant may spin at maximum frame rate. `frames` in the CSV makes this
  visible; `bot_iNullRenderFps` is the opt-in countermeasure. Do not enable it
  "just in case" — it changes the workload and needs its own A/B.
- **`#config` is written after the startup script** but a `PersistentSymbols`
  reload later could change values; the per-second `enabled`/`gameon` columns
  show the runtime state regardless.
- **Thread safety.** The watchdog touches only atomics, a critical section and
  `WriteFile`; it never calls engine code or takes an engine lock. State
  events are written from the timer thread under the same critical section
  (held for one line).
- **Telemetry overhead** is one QPC pair per tick (20/s), a few atomics and one
  write per second. It is not free, so a CPU comparison must use the same
  binary and the same `bot_iTelemetry` value in both variants.
- **No MSVC build has been done.** The only compile check is `g++ -fsyntax-only`
  of the telemetry block against Win32 stubs (see
  `tools/benchmarks/test_p0_candidate_source.py`).

## Rollback

Copy the previous `GameMP.dll` back and delete `BotTelemetry.csv`. No
persistent shell symbols are written and nothing else on disk changes.
