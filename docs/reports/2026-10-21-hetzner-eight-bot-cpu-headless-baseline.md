# Hetzner: Eight-Bot Runtime and CPU/Headless Baseline (2026-10-21)

> Status: **LIVE-SNAPSHOT / PERFORMANCE HYPOTHESES**, not a native 60-minute or 24-hour acceptance test. This report records read-only observations; no runtime or binary was changed.

## Scope and provenance

- Project: Alpha-Gaming / Serious Sam The Second Encounter Classic **Retail 1.07** (vanilla multiplayer compatibility remains mandatory).
- Host inspected over Remote Desktop Commander: Hetzner `ubuntu-4gb-nbg1-2`, Ubuntu, **2 vCPU**, **3819 MiB** physical RAM, no swap.
- Target public game endpoint: `91.99.75.33:25600`; port 25601 was also observed bound by the dedicated process at the initial inspection.
- Check times: 2026-10-20 ~21:42-21:43 UTC and 2026-10-20 ~22:04 UTC, corresponding to 2026-10-20 23:42-23:43 and 2026-10-21 00:04 Europe/Berlin.
- Runtime examined: `/srv/tse-wine-runtime-20261020/public-eight-20261020-2140/` (separate from source checkout `/srv/tse`).
- **No raw log, retail binary, secret, identifying player data, or private profile is included in Git.** Statements below are summarized measurements.

## Verified configuration

- One Wine-hosted `DedicatedServer.exe BotTest`.
- Two Wine-hosted `SeriousSam.exe` processes, each started with `+connect 91.99.75.33:25600 +quickjoin +script Scripts\\HetznerFleet.ini`.
- Both client logs explicitly show `BotDriver` attaching to **four local players each** (`HetznerFleetA_1..4` / `HetznerFleetB_1..4`): eight bot-controlled player identities in the observed session. This is a log-level and process-level observation, not a fresh independent 60-minute population audit.
- Xvfb virtual screen `:102`, **640x480x24**; Serious Sam window **320x240**.
- **OpenGL context exists** and reports `Mesa llvmpipe (LLVM 20.1.2, 256 bits), OpenGL 4.5 Compatibility Profile, Mesa 25.2.8`. Accordingly, these clients are *displayless* but **not render-free/headless**: graphics are software-rendered on CPU.
- `HetznerFleet.ini` has auto-combat, obstacle avoidance and BotDriver enabled. The clients still execute native game/network simulation.

## Measured resource utilization

At 2026-10-20 ~21:43 UTC, two successive `top -b` snapshots across approximately three seconds showed:

| Process or host | Observed sample | Meaning |
| --- | ---: | --- |
| First `SeriousSam.exe` | 70.0% -> 75.1% | % of one Linux logical CPU |
| Second `SeriousSam.exe` | 70.0% -> 87.0% | % of one Linux logical CPU |
| `DedicatedServer.exe` | 10.0% -> 16.3% | % of one Linux logical CPU |
| Host CPU idle | 14.3% -> 7.6% | Server-wide sample; busy ~85.7-92.4% |
| RAM used | ~1480 MiB | At sampling time |
| RAM available | ~2340 MiB | Linux `MemAvailable`, not raw free memory |
| Swap | 0 | No configured swap |

Later, after the game process PIDs changed, cumulative process percentages were around 63.8% and 61.2% for the bot clients and 8.3% for Dedicated. These are *not* equivalent to a controlled A/B benchmark. CPU measured **per bot** cannot be isolated from the shared renderer/engine-client overhead with these readings alone. A simple division by four gives ~18-22% of one core *per bot including its quarter of its client overhead*, not a measured incremental bot cost.

**Current bottleneck:** likely CPU capacity from full game-client/llvmpipe work; memory headroom is comparatively large. The fraction specifically attributable to rendering, networking, world simulation, BotDriver and Wine is **not yet profiled**. These observations do not prove an exact maximum bot capacity.

## Runtime and release boundaries

- The running public eight-bot configuration is distinct from previously qualified **local/Shadow** one-hour candidates. Do not inherit the earlier qualified `61DC27E0...` DLL acceptance without hash/provenance comparison.
- Previous `Too many bad syncs` episodes affect other test variants; no generic fix is demonstrated. Never suppress `ser_iKickOnSyncBad` to fake acceptance.
- Public server-browser visibility has been **reported by the operator**, but no independent browser-query proof is included in this snapshot.
- Direct join, CRC acceptance, actual native action continuity, 60-minute stability, external human join/reconnect, process recovery, and 24-hour fleet uptime require separate evidence for this exact current deployment.
- Other agents and a live Codex process use separate workspaces; **do not modify production Wine processes or other worktrees while testing optimization hypotheses**.

## Optimization candidates (not yet implemented or benchmarked)

1. **Controlled low-render baseline:** establish synchronized per-process CPU, system CPU, RSS, FPS, 20-Hz game-action continuity and server query telemetry. On a cloned isolated bot runtime, compare existing settings with lower graphics detail and bounded render FPS (e.g., 10/20/30 FPS), while preserving engine/network tick behavior.
2. **Non-render path / null renderer:** inspect engine startup and `SwapBuffers` / OpenGL calls; test a separate binary candidate that bypasses render work without disabling required gameplay/physics/network input. Removing Xvfb **alone** is not a CPU optimization if a software GL context is still created.
3. **Standalone headless game-client architecture:** longer-term candidate retaining synchronized client state and multiplayer protocol without drawing frames. Higher development/ABI/sync risk. Retail 1.07 engine is not the public Serious Engine 1.10; do not assume drop-in binary compatibility.
4. **Bot logic cost and scaling:** profile line-of-sight raycasts, navigation, target evaluation, logging and per-client shared overhead separately. Measure CPU as bot count rises; server cost can grow nonlinearly with participants.
5. **Alternative protocol-only or server-integrated bots:** research only, with explicit CRC/state-sync proof and strict vanilla 1.07 compatibility. No deployment until qualified.

No CPU-saving percentage, 12/16+ bot capability, or fully headless client is claimed as achieved.

## Acceptance gates for optimization work

- A: Read-only baseline with repeatable `pidstat`/`top`, sample interval and workload/players recorded.
- B: Isolated A/B on the same map, player population, client configuration and Wine stack, measuring effective CPU per client and total system capacity.
- C: Verify `GameHandleTimer` / `CPlayerAction` continues to emit bounded actions despite FPS changes or renderer removal.
- D: Native Retail 1.07 vanilla observer join and CRC; independent UDP query and player population evidence.
- E: 60-minute joined/combat/sync test; check both client AND server logs, no new `SYNCBAD` or disconnect regressions.
- F: Multi-server restart/recovery, external browser and 24-hour operation only after B-E.

See the [CPU/headless investigation plan](../superpowers/plans/2026-10-21-headless-cpu-optimization-investigation.md). **This publication is documentation only**; it does not authorize a production experiment.
