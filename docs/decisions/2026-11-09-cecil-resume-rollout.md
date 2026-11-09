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


## Prospective supply failure and mapped acquisition correction

Build013 completed limited300-second Hole, Little Trouble and Yodeller functional observations; these are not duration qualification. Its fixed ten-spawn single-bot RedStation series failed: one first-pickup latency lower bound is50.75s and one60s observation has no pickup. Nine observed pickups have a median lower bound29.45s, already above15s; failed/censored observations are retained. The original16m/eye-LOS item search combined with random patrol cannot reliably equip an unarmed bot. Both incomplete013 one/four-bot duration gates were explicitly aborted and their own private runtime closed normally.

Add a distinct mapped-weapon acquisition fallback after ordinary search and before patrol, only without an allowed usable collected ranged weapon (IDs4–14 except melee10), independently of enemy-distance sentinel values. Use original graph WeaponItem references, fresh typed eligibility, directed reachability and complete approach/route/connector cost. Validate a bounded same-floor node-to-item connector; repeat the existing final connector checks on arrival. Preserve original preset search distances and all enemy/fire visibility rules. Defer on exhausted ray budget, use a fixed20–45s route deadline without scan renewal, and clear on threat, new capability, unavailable item, failed route or lifecycle reset. Local eye/nearest-anchor rejections must not masquerade as evidence against a distinct mapped route; actual mapped connector/path/timeout failures retain global backoff.

Add exact read-only native Spawn/Death telemetry to remove one-second lifecycle timing ambiguity. Complete raw-log auditing remains separate from native acceptance. This behavior correction requires build014 and all new affected gates. Run its prospective ten-spawn supply series before starting long-duration gates, so another known supply failure does not consume hours of qualification. Frozen thresholds and final fleet requirements are unchanged.


## Ballistic edge ownership correction

The first build014 native supply trial selected the mapped upper RedStation laser immediately. Its directed84→86 jump-pad edge lost navigation control during flight: no acquisition node existed within the nearest-node height/radius limits, and the scheduled scan overwrote the anchor with−1. The Driver then resumed full-forward Human scanning at70deg/s, missing the upper node repeatedly. This is supported by preserved native action/position sequences and the pinned original graph; it is stronger evidence than an assumed jump-pulse or arrival-radius defect. The first mapped goal timed out and a subsequent goal ended without its selected weapon acquisition. These failures remain in the prospective cohort.

Preserve the previous acquisition anchor only while the same-goal navigator still has a valid committed directed edge. Existing graph/lifecycle resets, locks, suffix validation and deadlines continue to invalidate it. Add explicit movement ownership for neutral navigation so missing/invalid routes, rejected connectors and USE-release frames cannot silently hand no-target movement back to Human wandering. Preserve visible-target combat arbitration. No ranking, graph topology, arrival radius or jump cadence changes are justified by this finding.

Regression tests first reproduce airborne loss and unowned neutral output; extracted actual Driver arbitration rejects the old active-only condition. Build015 must repeat the frozen prospective supply scenario before any new long-duration gates. Build014 is not qualified and its failed observations are preserved.
