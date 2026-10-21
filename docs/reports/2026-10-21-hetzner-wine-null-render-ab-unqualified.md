# Hetzner-only Wine Null-Render A/B – unqualified CPU results
Date: 2026-10-21 (Europe/Berlin). Host: `ubuntu-4gb-nbg1-2` (2 vCPU, ~4 GB RAM). This report supersedes any implication that the previously measured Shadow GPU-enabled CPU gains apply to Hetzner.

## Isolation and provenance
- **All runtime work in this experiment happened on the Hetzner server.** No Shadow machine was accessed for this run. Existing original public 8-bot processes (DedicatedServer PID 98806, SeriousSam PID 98938/98940) remained running and were not restarted or modified.
- Separately copied runtime `/srv/tse-cpu-opt-candidates-20261021/hetzner-ab-20261021/` (~2.2 GB) with **independent Wine prefixes**, dedicated in an **isolated Linux network namespace**, local UDP port `26860`, separate Xvfb display `:116`, no external/public port. Map: **Yodeller**.
- Experimental candidate `GameMP.dll` SHA-256 `4F74146EB4E8B640E1D5A080D61D311C6965F1BFB071160F0753C370929C54FB`; public fleet unchanged `61DC27E0E7B80BADCF9AE705C30FCA88EDD3935737715DFFFF59E90C26F1FEF9` (both botA and botB).
- The only intentional A/B difference is `bot_bNullRender=0` (render enabled) versus `bot_bNullRender=1` (early GameMP return). Both scripts request `sam_iMaxFPSActive=20` and inactive 10; flags not independently verified at runtime.
- Test processes were started at niceness +17 with a **shared Linux cgroup CPU cap of 45,000/100,000 µs** (45% of one CPU for BOTH dedicated server and bot client) to protect production. Global host load was already ~3 on two logical CPUs. Mesa **llvmpipe** confirmed in test client's OpenGL context.
- Logs and JSON telemetry are **private to the Hetzner staging directory**, not published. The exact process-state checks after tests showed all three original public PIDs alive and public SHA-256 hashes unchanged.

## Measured results – NOT a valid CPU saving claim

| Variant | Client CPU, 18s | Memory RSS | CRC | Players joined | BotDriver local/ticks in log | Bad sync signatures |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| Render enabled | 35.56% of one core | 247184 KiB | OK | 4 | 0 / none | 0 in inspected logs |
| Null render | 35.56% of one core | 246548 KiB | OK | 4 | 0 / none | 0 in inspected logs |

**Interpretation:** The shared cgroup was severely CPU throttled (`nr_throttled=2528` of `nr_periods=3146` after the A/B). Identical 35.56% client CPU with server consuming the rest of a 45% core cap does **not** mean renderer saves 0%; it means this method cannot distinguish CPU demand at saturation. Furthermore, although four named players joined and CRC passed, no new BotDriver tick/position log signatures appeared in either 18s sample. Therefore neither variant passed the **active-bot/simulation** acceptance requirement. The absence of `SYNCBAD` during short runs is insufficient sync qualification.

The prior Shadow single-bot 12s measurements were **4.4% vs 1.7% of a core** on native Windows/NVIDIA GPU, and are **not** Hetzner CPU results. No confirmed percentage savings or scale-up capacity is currently available for Hetzner.

## Next Hetzner-only gates
1. Diagnose why the **isolated** four-join Wine runtime produced no BotDriver tick evidence; verify shell `bot_bEnabled`, native action timer, and server side motion before comparing CPU.
2. Use a lower-load isolated setup (e.g. a single local bot), with verified action logs and controlled CPU quotas that do not saturate either variant. Record per-PID process CPU, system CPU, cgroup throttling, FPS and RSS. Do not weaken public runtime safeguards.
3. Profile render/callback and timer locks (the `tm_csHooks` render scope is suspicious) with measurements, not assumptions.
4. Verify original unmodified Retail 1.07 human joins, external movement/kill/sync and 60-minute clean stability.
5. Keep public fleet on accepted hash `61DC...` and leave draft PR unmerged until qualified. New source builds going forward must use a supported Hetzner-only toolchain; do not depend on Shadow. If no compatible Retail 1.07 build toolchain is available on Hetzner, document that as a real blocker.

## Safety and execution artifacts
Staging folder: `/srv/tse-cpu-opt-candidates-20261021/hetzner-ab-20261021`
Runner: `ab_runner.py` (staging only).
Metrics: `result-hetzner.json`.
Test cgroup: `/sys/fs/cgroup/tse-null-render-ab-20261021` (empty after the run).
The public server remained unchanged. No candidate was deployed.
