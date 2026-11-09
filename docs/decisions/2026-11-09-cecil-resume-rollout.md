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


## Qualification scheduling and available native client

The user confirmed no Windows machine is currently available and requested continued execution using the available paths. A separate owned original-Retail installation and Wine prefix on the actual Hetzner host are therefore used for real join/rendered gameplay with ordinary PID-verified keyboard/mouse input. The read-only Linux preflight preserves the Windows preflight's four-original-component, process-occupancy and fresh exact-single-bot requirements; any synthetic process root or status fixture forbids a launch. This is real Retail/Wine evidence, not Windows, an independent WAN host, or GPU-hardware acceptance.

The fixed 3600/3600/7200-second final-hash gates may run concurrently on isolated development copies: one and four bots on strictly loopback-bound, nonadvertising ports25700 and25710; the eight-bot test remains on the public development instance. Each copy retains original Dedicated/Engine/Entities and the same final BotClient DLL, RedStation/nav/settings, exact expected populations, separately owned Wine prefixes, services and observation series. Copies are prepared from the verified development source; production stays at eight bots per instance. No frozen duration/behavior limit changes. All controlled scenarios reject extra participants or observation gaps. Simultaneous load includes the extra test processes and is identified in resource comparisons. Only the main agent operates them, and all temporary resources require normal cleanup.


## Observed isolation correction and external visitor

Retail did not open a GameSpy query socket with heartbeat disabled. The first empty isolated server was shut down with SIGINT (native stopping-game/renderer-cleanup log; no clients had started). The qualification copies instead use systemd PrivateNetwork=yes with only loopback, no route, and shared namespaces only between each owned server and its own clients/observer. The GameSpy feature can then serve private status replies without any ability to contact a public master. The copies' ports are absent from the host namespace. Initial transient-service startup checks needed to wait for native exec/cwd/namespace readiness; these setup failures are preserved as setup evidence, not BotClient failures or successful gates.

An external visitor joined the public development Hole instance after its eight bots joined. Its controlled functional observer correctly failed with unexpected population9. No visitor identity is published, no session is removed, and no public map/service change is attempted while occupied. Further controlled eight-bot map and duration tests move to another isolated development copy on port25720 inside its own network namespace, with the same final DLL/config/assets. Production remains unchanged. The public development instance retains eight playing candidate bots. The real original-Retail/Wine join/movement/fire/normal-exit check completed before this visitor arrived, with original hashes preserved and the server population restored to one bot.


## Navigation regression requires a new candidate

The isolated build012 Hole observation had complete telemetry and no monitor errors, but three slots had nonpositive score deltas. Investigation found an independently reproducible route-commitment defect: timer expiry reacquired a nearest anchor already completed on a long edge, sending the bot backwards. Displacement in either direction kept resetting the stuck timer. This is consistent with the observed repeated Hole hops, not proof that it explains every native behavior.

The regression first failed on both first-edge and subsequent-edge travel. The corrected navigator retains the committed source/destination and source flags until actual arrival or explicit goal, lock, recovery or relocation invalidation. Periodic and unrelated-lock checks validate the remaining suffix from the destination. Newly blocked destinations, unreached acquisition anchors, teleport exits and destination OVERRIDE remain covered. All affected final-hash gates must restart after a new native build.

The incomplete build012 one/four-bot monitors were aborted explicitly as NOT_QUALIFIED. Their private clients and the eight-bot Hole clients were closed normally through their own verified windows; slots drained, then owned dedicated servers exited through SIGINT and service cgroups emptied. Logs and partial observations are preserved. Production and the occupied public development instance were untouched.
