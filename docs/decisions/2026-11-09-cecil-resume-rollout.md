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


## Height preference and bounded off-graph reacquisition

Build015 retains native navigation during the RedStation launch, unlike014, but its first upper-weapon attempt still ended without acquisition. The first useful pickup took18.7s in that trial. Urgent mapped-item ranking now adds a3x height-difference preference consistent with Cecil's ordinary vertical weighting, expressed in the current gravity frame. This changes only candidate preference, not graph topology/search costs, node radii, jump cadence or physical route deadlines.

The015 Hole observation failed the fixed10s idle limit: water poses had no ordinary anchor within12m/3m-height and a grounded low pose had no same-floor node. Explicit neutral ownership exposed this coverage gap instead of hiding it behind uncontrolled Human wandering. Add slow owned reacquisition toward up to three physically visible original nodes within32m; ground candidates have at most8m height difference and require the actual native support reference. Swimming uses normal3D input. Ordinary anchor criteria remain unchanged and no recovery target is claimed as an acquired graph node. Uncommitted airborne movement remains neutral.

A target attempt has a fixed6s deadline and6s backoff. New targets clear stale escape state; requested, held and replacement horizontal actions are capped at0.3 before their exact probes. Ground recovery always requires wall and floor support even when ordinary bAvoidPits is disabled, without any current-point exemption; water retains its native3D checks. Locks refresh outside ordinary anchor coverage. Budget exhaustion defers with owned neutral action. All are new candidate behavior requiring full native qualification; historical ground-feature failures and015 idle failures remain failures.


## Retained item need is separate from acquisition admission

Build016's fixed ten-spawn supply series met first-useful-pickup timing (median3.40s/P958.40s), but only3/10 first actual weapon goals had matching ownership gains. It failed the frozen9/10 requirement. A source-identical behavior control with rejection-only telemetry (private diagnostic017 overlay) established an actual cannon cancellation when weighted acquisition distance crossed16m although the typed item remained available. This does not establish the cause of both earlier flamer cancellations. All failures remain in their predeclared cohorts.

Share strict typed/pickable/generation/per-kind need/allowed/usable rules between acquisition and retention. Retention does not repeat initial radius/ranking, visibility or enemy-distance admission; live native item decoding, directed path validation, close-threat action arbitration and the existing twelve-second deadline remain. New selection retains the original weighted distance, visibility, reachability, priority and enemy-distance behavior. Mapped-weapon capability/deadline handling is unchanged. This is a deliberate correction to acquisition/continuation coupling, not wider search or enemy knowledge.

The actual native bridge regression failed with the old expression and passes with the shared retention helper. Final offline verification:187 actual bridge checks with ASan/UBSan and pinned SDK USE32,62 motion checks and all Cecil C++ suites including new item-retention cases, actual Driver action guards, native item fake-SDK contract,166 tool tests. These are portable evidence, not native final-hash qualification. The diagnostic DLL is not a release candidate. Build018 requires a new published source/hash and all affected native gates.

The limited Build016 Yodeller300s window had full coverage,41 deaths, no recognized native errors and maximum unexplained stillness3.017s. One bot's net score delta was0, so the stricter all-eight-positive helper stopped the pipeline. Its failed score check is preserved. Own clients and server closed normally and all cgroups drained; no duration gate started. No inference that a zero net score alone proves inactive combat.


Independent review found that retaining an urgent weapon across a close threat could leave inactive movement ownership set and suppress Human fire. A second failing actual bridge regression reproduces this. The close non-health threat return now yields action ownership while retaining goal/deadline; urgent health keeps the existing exception. Both regressions and the187-check sanitized bridge pass, with no additional blocker reported in the focused re-review.


## Score trajectory and mapped continuation correction

A new read-only analyzer reports each expected bot's observed first/last/min/max scores and positive/negative changes alongside unchanged net deltas. Missing observations remainOPEN and break change comparisons; invalid scores reject the evidence. Eight new tests plus existing suites total174 passing tool tests. The prior substring assertion prohibiting any occurrence ofpos was corrected to prohibit the actual JSON coordinate key, sincepositive_change_count contains the same substring.

Before starting Build018 map tests, the private protocol was versioned to require positive observed score development per bot, plus unchanged movement/fire/coverage/sync criteria. The earlier endpoint-profit assertion misclassified a directly corroborated kill followed by suicide as no score development. The original frozen criterion asks for hit/score development, not strictly positive net profit; no duration, population, safety or quality threshold is reduced. Preserve the018 protocol and all earlier helper failures.

Build018's second single-bot trial exposed the same admission/continuation coupling in the distinct mapped fallback: selected flamer248, then incidental shotgun ownership3→11 while the flamer goal remained active, immediate cancellation; subsequent ordinary selection collected that flamer. The old mapped retained-goal predicate includes!HasRanged, so another useful gun necessarily cancels a still-needed target. Split mappedNeeded from mappedEligible: only new fallback acquisition requires missing usable allowed ranged capability; continuation checks the specific typed ranged weapon's current need. Retain actual availability, generation, allowed mask, selected-weapon usability, close-threat cancellation and the same fixed20–45s deadline. No renewal, scan widening or graph change.

A failing actual bridge regression now distinguishes incidental different-weapon gain from selected-weapon gain. The former keeps the original goal/deadline, the latter clears it. Sanitized bridge188 checks pass; focused independent review reports no remaining blocker. Build018's original prospective cases continue unchanged and all remain evidence; Build019 requires a new native hash and complete affected qualification.

One inactive staging helper assumedbotB existed in one-bot copies and stopped after staging SupplybotA. The declared018 runner was already started before its new protocol filename was generated. All criteria/cases had already been fixed by the pre-start runner and published qualification/inherited016 protocol. The late metadata generation is recorded explicitly in protocol018; no trial is dropped or replaced, and no prospective filename timestamp is invented. Subsequent staging inventories actual roles and validates the complete plan before mutation.
