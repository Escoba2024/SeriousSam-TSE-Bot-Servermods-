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
- [x] Windows MSBuild Release_TSE107 produced new candidate `GameMP.dll` (SHA256 `4F74146E...`, 225280 bytes); shadow native smoke and private Hetzner transfer hash verified. No replacement of accepted DLL.
- [x] Preliminary native Shadow one-bot 12s samples: null render 1.7% one core vs render enabled 4.4% at the same FPS20 on map DM_LittleTrouble; see report. **Not** Wine/8-bot benchmark.
- [ ] Required isolated Hetzner Wine 4/8-bot A/B and 10-minute CPU/95p workload profile.
- [x] Isolated Windows dedicated CRC OK, native bot join and tick/movement continuity in both A/B variants; brief local logs show no bad-sync signs.
- [ ] Unmodified human observer join, full combat and 60-minute sync/latency acceptance on new DLL.
- [ ] Only after native acceptance, decide whether to deploy with explicit backup, rollback and CPU headroom. No current production deployment authorization is inferred from a passing static test.

## Known limits

Static source checks cannot prove ABI compatibility, `IsIconic` behavior, frame-pacing correctness, `SwapBuffers` overhead, rendering independence of native 1.07, or multiplayer sync. Compare with the independent eight-bot baseline report. Do not use fake sync/bad-CRC suppression. Existing live Codex sync-agent works separately in `/srv/tse-main-agent-20261019` and must not be interrupted.

## Evidence 2026-10-21

See `docs/reports/2026-10-21-null-render-native-smoke-ab.md`. Shadow game-server and client test processes stopped after testing. The protected public eight-bot Wine fleet remains unchanged and is not yet qualified with this new DLL.
