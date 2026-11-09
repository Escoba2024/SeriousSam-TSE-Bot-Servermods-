# Cecil continuation and qualified live rollout — 09.11.2026

The user explicitly requested continuation of the latest Cecil integration, bot logic and waypoint work, followed by rollout to the live servers. This supplies the separate production-rollout authorization required by the earlier development-first decision. The development-first order, frozen acceptance criteria, player protection and per-instance rollback remain applicable.

## Observed starting state

- Clean publication branch `codex/20261107-cecil-release`, HEAD `ccc469a`; draft PR #99 already exists. Continue this branch; do not publish the inherited development branch containing private historical data.
- Five production instances on ports 25600/10/20/30/40 each report eight players and retain BotClient hash `7fc94a39c3f5d9516f262d9e4d04a5cf38e6eb5ae3482976c32c952a99d30835`.
- Development 25650 was still Yodeller with eight bots, both running build010 hash `224ee607072982a521bdab36250554039f9e606a4db755fdd42716fb0f031475` from 07.11. Both client logs contain zero recognized sync/fatal/invalid-action errors. The server log contains 55 SYNCBAD events attributed to external/unclassified connections, zero matching either known local BotClient address. This is log attribution, not evidence of complete sync correctness or a completed duration gate.
- The prior 600-second Yodeller observation completed, all eight score deltas positive, 129 observed deaths, no monitor errors; it remains a short functional observation. Current log continuity does not replace the required monitored final-hash gates.
- Direct local shell execution and existing native MSVC/Wine toolchain are available on the actual Hetzner host. RDC discovery also reports the Ubuntu device online and both Windows devices offline. Windows original-Retail gameplay acceptance is currently unverified; no remote GUI success is inferred.
- Disk reserve 73 GiB and approximately 3.3 GiB available memory at initial inventory. No new dependencies, Ghidra or Frida sessions started.

## Execution and review

Use the existing full-integration plan and its fixed one/four/eight-bot duration and behavior criteria. Independent read-only code review established unsuitable-prefix item starvation and retention of an earlier move/fire action after invalid-action rejection. Both require failing regression tests, targeted corrections and a new native candidate; build010 results cannot qualify that new hash.

A separate isolated qualification-tool worktree addresses missing start/end telemetry coverage and contaminated populations. Only the main agent controls native builds and runtime. No unrelated service/process is stopped and no qualified historical DLL is overwritten. Private logs, profiles, NAV payloads, binaries, and rollback archives remain outside tracked source.
