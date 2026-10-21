# Null render, presentation bypass and the headless BotHost: what the code allows

**Date:** 2026-10-22 · **Status:** source-level analysis of the 1.07 GameMP
source in this repository plus the PR #40 change. No runtime claim.

Terminology first, because the three levels get mixed up in the reports:

| Level | What stops | Still required |
| --- | --- | --- |
| **1. Render skip** | the scene/view drawing inside GameMP | GL context, drawports, `SwapBuffers`, Xvfb, all engine frame work |
| **2. Presentation bypass** | the whole `CGame::GameRedrawView` body for bot frames | context creation, outer loop, `SwapBuffers` of the (unchanged) framebuffer, Xvfb |
| **3. Context-free headless** | GL/X11/Xvfb entirely | engine must run with a null rasteriser (`GAT_NONE`) and no drawport |

The PR #40 switch and the P0 candidate implement **level 2**. Level 3 is not
implemented and its feasibility is not proven.

## 1. What the bypass removes (verified by reading the source)

`CGame::GameRedrawView()` (`Game.cpp:2091`) does, in this order:

1. takes `tm_csHooks` (the lock that can stall the 20 Hz timer);
2. handles thumbnail rendering (`_fnmThumb`), including a recursive call;
3. `SE_PretouchIfNeeded()`;
4. builds split-screen drawports (`MakeSplitDrawports`);
5. prescans input and calls `CControls::CreateAction(..., TRUE)` for local
   players **inside `tm_csHooks`**;
6. collects local and observer viewers, calls `CEntity::RenderGameView()` per
   viewport (world, models, particles, HUD), fills empty drawports;
7. draws messages/stats/console lines, demo OSD, profile accumulation;
8. `_pSound->UpdateSounds()`, `_pGfx->gl_bAllowProbing = FALSE`, screenshots.

The candidate returns before step 1 when
`bot_bNullRender && gm_bGameOn && !_pNetwork->IsServer() && _fnmThumb==""`.
So all eight steps disappear for bot frames, and the timer can no longer be
blocked by rendering on this path.

## 2. What remains (and why this is not headless)

Still executed by the retail EXE around the GameMP callback:

- `SeriousSam.exe` main loop, message pump, window handling under Xvfb;
- `_pGfx` frame begin/end and the viewport `SwapBuffers()` (a copy/blit of the
  back buffer; with no drawing it still touches the X server and the llvmpipe
  framebuffer);
- GL context creation, extension probing, texture/font loading at level load;
- `CGame::GameMainLoop()` → `_pNetwork->MainLoop()` (simulation, input packets);
- the engine timer and its hook list (`_pTimer->HandleTimer`).

None of these are measured yet. The candidate's `frames`, `renderskip`
and the sampler's `thread_cpu.llvmpipe` are the instruments that will show how
much of the remaining CPU sits in llvmpipe/SwapBuffers versus the game loop.

### The busy-loop risk

`sam_iMaxFPSActive` is an **EXE-owned** symbol: it does not appear anywhere in
the GameMP source. The FPS limiter therefore lives outside the code changed
here, and its behaviour when the render callback returns immediately is not
known. Two outcomes are possible:

- the limiter still sleeps between frames → the bypass saves the renderer cost;
- the limiter only throttles inside the render path → the null client spins at
  maximum frame rate and burns *more* CPU than before.

That is not speculation about 1.07 internals; it is a gap in the available
source. Hence `bot_iNullRenderFps` (default 0) and the frame counter. If a run
shows `frames_per_s >> 20` together with high CPU in the null variant, enable
pacing and re-measure. Never enable pacing "just in case": it changes the
workload and would need its own A/B.

## 3. Level 3: what a `GAT_NONE` BotHost would have to solve

Concrete blockers found in the GameMP source that a context-free build must
handle (each one is a code change, not a configuration flag):

| Blocker | Evidence | Consequence |
| --- | --- | --- |
| `LCDInit()` loads eight menu textures with `SetData_t` and `Force(TEX_CONSTANT)` | `Game.cpp` `CGame::LCDInit` | fails or wastes memory without a rasteriser |
| `LoadingHook_t` locks a drawport and calls `SwapBuffers` | `LoadingHook.cpp` | loading path must be skipped or rewritten |
| `GameRedrawView` uses `CDrawPort::Lock`, `Fill`, `GrabScreen`, `SetFont`, `PutText` | `Game.cpp:2091+` | already bypassed by level 2 |
| `CGame::ComputerRender` / `ConsoleRender` assume a drawport | `Game.cpp` | must stay off (`gm_csComputerState=CS_OFF`) |
| `CGame::InitInternal` calls `CAM_Init()`, `LCDInit()`, control loading | `Game.cpp:1015+` | split into headless-safe and visual parts |
| Sound system init and `UpdateSounds` | `Game.cpp` | audio device must be optional |
| `_pGfx->gl_*` statistics and `SE_PretouchIfNeeded` | `Game.cpp` | need a stub rasteriser, not just "no draw calls" |

Those are GameMP-side items. The unknown, larger part is `Engine.dll`:

- whether `_pGfx` can be created with `GAT_NONE` in 1.07 and which subsystems
  still call into it (`CEntity::RenderGameView`, `CWorld::Render`, console
  rendering, font handling);
- whether `Engine.dll`'s network/CRC path has any dependency on the graphics
  object or on the window (the dedicated server suggests "not for
  simulation", but the dedicated server is not a client);
- whether a client can run without a `CViewPort`/`CDrawPort` at all, i.e.
  whether the EXE's main loop requires one.

Because 1.07 is not the public 1.10 source, none of these can be answered by
reading the SDK; they need 1.07 disassembly or an experiment.

## 4. Variant A: dedicated BotHost.exe

Sketch: a small EXE that initialises the engine like `DedicatedServer.exe`,
then joins a remote session as a normal client and runs our GameMP with the
bot driver.

Checkpoints that must be proven in this order (each is a stop/go gate):

1. Engine/Entities/GameMP load and `GAME_Create` returns a working `CGame`
   with `_bDedicatedServer` semantics understood (the dedicated path skips
   persistent symbols, `Game.cpp:1018`).
2. `_pNetwork->StartProvider`/`StartPeerToPeer` is **not** required for a
   client; `CGame::JoinGame(CNetworkSession)` must be reachable.
3. Local player sources (`gm_lpLocalPlayers`) are created and `pls_Index`
   matches the server slot after the CRC handshake.
4. The timer handler is registered and `gm_bGameOn` becomes TRUE
   (`Game.cpp:908`, `Game.cpp:752`).
5. `SetAction` packets appear at the server (`MSG_SEQ_ALLACTIONS`).
6. A vanilla 1.07 client sees the bot move (external gate).

Known risks: class layouts/ABI of 1.07 `Engine.dll` (the project already
carries a `RetailAllocator.cpp` for a reason), export/import differences, and
the fact that the EXE's main loop is not part of the repository. Every one of
these can invalidate the approach late. That is why the ladder below is
ordered by cost.

## 5. Variant B: DedicatedServer.exe as client host

Hypothesis: use the existing dedicated binary with a modified GameMP that
joins instead of hosting.

What speaks for it: it already runs without a visible window and without a
human input path.

What speaks against it, concretely:

- `CGame::InitInternal` branches on `_bDedicatedServer`; the dedicated path is
  not a client path with a flag flipped, it skips client-side pieces.
- `DedicatedServer.exe` starts a provider/session; turning that into a client
  join replaces the EXE's own control flow, which is not in the repository.
- `CGame::GameRedrawView` is not called on the dedicated path, so a null
  renderer would be irrelevant — but so would any code that depends on the
  render callback for pacing.

Verdict: **research hypothesis, not a plan.** The cheapest decisive experiment
is not on the dedicated binary but on an isolated normal client: prove that the
P0 telemetry reports `ACTIVE_OK` with `bot_bNullRender=1` and no GL draw, then
measure how much CPU remains outside llvmpipe. If the remainder is small, level
3 buys little and should not be attempted. If the remainder is large, the
headless work is justified — and only then is Variant A worth its cost.

## 6. Ordered ladder (each step has a stop condition)

1. **Level 2 at 20 Hz** — P0 telemetry proves ticks/actions; render skip counted.
   Stop if the timer stalls or actions < 18/s.
2. **Residual cost split** — sampler shows llvmpipe vs main thread with the
   bypass active. If llvmpipe is still a large share, the bypass is incomplete
   (SwapBuffers/context), and level 3 is the only next step.
3. **Frame pacing check** — if `frames_per_s >> 20`, measure `bot_iNullRenderFps`
   as its own variant (A/B, same protocol).
4. **Context-free prototype** — first without network: can 1.07 GameMP run at
   all with `GAT_NONE`? This is the single most informative experiment and the
   one most likely to fail early (cheap to find out with a disposable copy).
5. **Headless join** — only after 4, with 1 bot, then 4.
6. **Vanilla + 60 min + reconnect** — mandatory before any deployment.

No step may be skipped, and none of steps 3–6 is started before the CPU
evidence of step 1–2 exists.

## 7. Claims

- Implemented: level-2 bypass, optional pacing, proof counters.
- Not implemented: `GAT_NONE`, window/context-free startup, BotHost, dedicated
  client mode.
- Not measured: any CPU saving, llvmpipe residual share, frame rate under the
  bypass.
- Therefore: no statement in this document may be used as a performance claim.
