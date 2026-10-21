# Retail 1.07 Null-Render CPU Candidate – Shadow Native Smoke and A/B

**Date:** 2026-10-21 Europe/Berlin. **Status:** Native smoke PASS (one bot); Hetzner 8-bot Wine acceptance NOT RUN. The existing public server was not modified.

## Binary provenance

- Source: branch `agent/cpu-opt/20261021-null-render`, changed `poc/release/gamemp/Game.cpp` by one opt-in `bot_bNullRender` guard and one shell declaration; opt-in config separate.
- Build environment: Shadow Windows, Visual Studio 2022 Build Tools, Release_TSE107 Win32, existing 1.07 SDK-derived GameMP project cloned into `native-nullrender-build`.
- MSBuild: exit 0, generated `GameMP.dll`, 225,280 bytes, SHA-256 `4F74146EB4E8B640E1D5A080D61D311C6965F1BFB071160F0753C370929C54FB`.
- MSBuild emitted warning C4474 in unchanged `Controls.cpp` and MSB8029 for build-path placement. No build error.
- Protected current Hetzner eight-bot DLL: SHA-256 `61DC27E0E7B80BADCF9AE705C30FCA88EDD3935737715DFFFF59E90C26F1FEF9`.
- New DLL was transferred privately to `/srv/tse-cpu-opt-candidates-20261021/GameMP-4F74146E.dll` and verified by exact SHA-256. It was **not** installed in any live Wine runtime.

## Isolated Windows smoke

Shadow isolated copied server/client runtime, unmodified Retail 1.07 dedicated server, native client, map `DM_LittleTrouble.wld`, loopback UDP 25600, no GameSpy heartbeat. Single local bot `TSE_Bot_Client_1`. Original player/application state and public Hetzner processes untouched.

| Variant | `bot_bNullRender` | FPS cap | Observed CPU on Shadow | Protocol/logs |
| --- | ---: | ---: | ---: | --- |
| Null render | 1 | 20 FPS | ~1.7% of one logical CPU (12s sample) | Server CRC OK; joined; BotDriver active through tick >=1180 with position changes |
| Render enabled | 0 | 20 FPS | ~4.4% of one logical CPU (12s sample) | Server CRC OK; joined (after isolated server restart); BotDriver active through tick >=620 with position changes |

Percentage differences from these 12s samples are preliminary, **not** production savings or a confidence interval. This is Windows on an NVIDIA RTX 2000 Ada GPU, *not* software OpenGL under Hetzner Wine/llvmpipe. Both runs share code/binary/config except render-enable flag; server was restarted between runs because the first player's name remained occupied after process stop. No `SYNCBAD`/bad-sync signatures appeared in the inspected local logs during these brief runs. A 60-minute sync/CRC and human-join acceptance for this new binary has not been performed.

Original full logs are retained only in the private isolated Shadow runtime `SeriousSam-TSE-CPUOpt-20261021/smoke`, not published. Both Shadow test processes were stopped after testing; port not used for production.

## Remaining mandatory gates

1. Independently confirm `bot_bNullRender` and `sam_iMaxFPSActive` are recognized under Retail 1.07/Wine.
2. On an isolated Hetzner Wine prefix/port/display, compare stable four-bot clients with identical workload and CPU telemetry. Do not compete with a saturated public service or overwrite its DLL.
3. Verify server-side correct bot actions and human unmodified Retail 1.07 joins, CRC, no dropped network ticks, and 60-minute stable sync/combat.
4. Prove headroom for eight bots and optionally later scale-up. The current implementation bypasses GameMP game rendering but does **not** remove the game's Win32/OpenGL/Xvfb context or outer SwapBuffers/mainloop; it is not yet full headless.
5. Only after reproducible acceptance and rollback preparation, consider deployment to public eight-bot fleet.

This is a new unqualified candidate, not a replacement for the verified original DLL.