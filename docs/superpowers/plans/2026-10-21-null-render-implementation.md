# Retail 1.07 CPU Optimization – Isolated Implementation Ledger

Date: 2026-10-21 (Europe/Berlin). Workspace: `/srv/tse-cpu-opt-20261021`, branch `agent/cpu-opt/20261021-null-render`.

## Goal and safety

Remove the expensive client game-render call from opt-in four-bot client instances, and cap the host render/main-loop frequency, preserving unchanged Retail 1.07 server, human clients, simulation, world state and `CPlayerAction` network path. No changes to the public eight-bot instance unless a separately built DLL and configuration pass native gates.

## Implemented design

- `Game.cpp`: new `bot_bNullRender` shell `INDEX` (default FALSE, settable only by an explicit client script), returning from `GameRedrawView` before taking `tm_csHooks` when `gm_bGameOn`, not a server, and no thumbnail pending.
- Existing fallback full render path preserved for menu, unmodified clients and server.
- `poc/profiles/HetznerNullRender.ini`: explicit experimental opt-in and `sam_iMaxFPSActive=20`, `sam_iMaxFPSInactive=10`, `sam_bPauseOnMinimize=0` to avoid a hot empty main loop. The variable names and behavior must be verified on original 1.07 and Wine.
- No direct `Engine.dll`, `EntitiesMP.dll`, `SeriousSam.exe`, dedicated server or protocol modifications. Xvfb/OpenGL context may remain required by the EXE; this is **null-game-render** not proven fully headless.

## Acceptance and progress

- [x] Read-only inspection: current production 2x SeriousSam.exe + dedicated, all preserved, not modified; existing project reference reviewed.
- [x] Isolated Git clone/branch established against `main` 30a6747.
- [x] Reversible opt-in null-render source and profile authored.
- [x] Static guard tests (4/4) and `git diff --check` passed 2026-10-21.
- [ ] Build **new** Retail 1.07 `GameMP.dll` with complete source and dependencies in isolated Windows SDK build tree; record SHA256 and build log. No replacement of accepted DLL.
- [ ] A/B baseline vs 20 FPS alone vs null render at same map and client population in isolated Wine prefix and distinct ports/display; record per-process median/p95 CPU and memory, timer/input continuity and sync.
- [ ] Unmodified human Retail 1.07 join, CRC, visible combat/kill confirmation, 60-minute clean sync/latency test on the new DLL.
- [ ] Only after native acceptance, decide whether to deploy with explicit backup, rollback and CPU headroom. No current production deployment authorization is inferred from a passing static test.

## Known limits

Static source checks cannot prove ABI compatibility, `IsIconic` behavior, frame-pacing correctness, `SwapBuffers` overhead, rendering independence of native 1.07, or multiplayer sync. Compare with the independent eight-bot baseline report. Do not use fake sync/bad-CRC suppression. Existing live Codex sync-agent works separately in `/srv/tse-main-agent-20261019` and must not be interrupted.
