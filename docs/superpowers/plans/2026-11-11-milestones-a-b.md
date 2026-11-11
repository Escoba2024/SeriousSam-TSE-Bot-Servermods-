# SSAM.AI milestones A then B — execution ledger

Authority: user attachment `SSAM_AI_CODEX_ANWEISUNG_2026-11-11.md`, preserved privately at `/srv/tse-milestone-a-evidence-20261111/request.md`. Execution is explicitly authorized, including isolated worktrees, commits, pushes, backups and controlled restarts. No routine approval checkpoint. Main agent owns integration/runtime; two agents own combat/navigation analysis and bounded fixes in separate worktrees. B must not start before all A gates pass.

Worktree: `/srv/tse-milestone-a-20261111`, branch `codex/20261111-milestone-a`, base `4d04ab4ad190a0f6cd078d96f5416e0eea9e1da0`. Existing writers/worktrees preserved. Private evidence and archives stay outside Git. Never publish Retail binaries, player GUIDs, raw logs or credentials.

## Task 1 — inventory, exclusive access and restorable baseline [AUDITED; SEE EXECUTION UPDATE]

- Inspect actual systemd units/process maps, current queries on game-port+1, active DLL hashes, configs, nav, rosters and build provenance. Save private before/after JSON manifests.
- Preserve all relevant tracked and untracked source work, active runtime files, startup scripts, systemd units/timers, monitoring configuration and toolchain provenance. Verify archive listing, SHA256 and restore into a separate directory. Preserve at least 8 GiB disk free.
- Acquire existing fleet/runtime deployment locks before any shared-runtime mutation; never unlock another process's resources. Local inventory is read-only.
- Verify Git origin access and existing Drive folder `14HBTUlfJvyE821KnoHJhNGZ__4Ge2-y2`; verify upload/readback or record concrete blocker.
- Current discovery: actual Dev SERVER DLL is now `fe4a77bd…`, active since 18:24 UTC, from authorized power-up work. Dev CLIENT remains `ec820d04…`; public CLIENT `7fc94a39…`. Preserve the selective Damage/Invisibility filter on Dev. Shadow and other Windows desktop are offline.

## Task 2 — A1 effective spawn protection [PARTIAL; ACCEPTANCE OPEN]

- Trace `Scripts/PersistentSymbols.ini`, `Scripts/Dedicated_startup.ini`, `Scripts/Dedicated/BotTest/init.ini`, `1_begin.ini`, all rotations and restart templates for each runtime. Check native session field assignment in `Game.cpp`/`SessionProperties.cpp`.
- Set effective server `gam_tmSpawnInvulnerability=0` at the session boundary and templates; preserve respawn delay, HP, ammo, blood and gibs. No target spawn grace found in Cecil048, so no speculative entity changes.
- Gate: repeated immediate post-respawn damage/death for bots and available Vanilla client, plus map switch/restart. Config zero alone is not PASS.

## Task 3 — A2 exact name-pool expansion [PARTIAL; ACCEPTANCE OPEN]

- Existing source pool: `/srv/tse-ai2-namecap-20261025/poc/scripts/GamingNicknames.json`; actual active subsets/IDs in live `roster100.json` and `bot-roster.json`/PLC4 files. Preserve original pool exactly.
- Add `poc/scripts/GamingNicknames.json`, `GamingNicknames.additions.json`, metadata and `tools/gaming_names.py` with tests. New visible names exactly 250; normalized format-stripped casefold uniqueness against original and active aliases; fixed seed 20261111.
- Ground decoration in actual parser/evidence. Use safe ASCII, bounded visible/raw bytes, reject command/quote/backslash/control syntax, reset decorations. At most 25 blink names; unsupported formats get plain fallback. Stable internal ID and names separate; allocation deterministic and collision-free across fleet.
- Gate: validator negative cases + full pool pass, native representative format rendering and external query. No render PASS from source inspection.

## Task 4 — A3 bounded arena improvements [PARTIAL; ACCEPTANCE OPEN]

- Source: `poc/candidates/redstation-supply-20261107/{BotDriver.cpp,bot_profile.h,bot_human.h,bot_loadout.h,cecil_rules.h}` (build048 overlay pins verified against source). Preserve per-local-player isolation and sibling opponents.
- Three explicit tiers MITTEL/STARK/DEMON, deterministic legacy migration; avoid Cecil Configure overwriting tier aim settings. Shared tactical capabilities, few ordered parameters. Short-range Colts policy, reachable weapon acquisition, fire/supply arbitration, tracking and movement without damage/state manipulation.
- Tests in existing `test_cecil_human.cpp`, `test_cecil_rules.cpp`, `test_cecil_motion.cpp`, plus focused regression cases before implementation. Build with `tools/build_supply_gamemp.py` and pin entire overlay/manifest/DLL.
- Gate: at least three reproducible old/new native comparisons with exchanged starts; weapon acquisition, valid weapon use, damage/hits, stuck, deaths/frags and current event evidence. Human difficulty judgment remains separate.

## Task 5 — A4 nine-map matrix and whitelist [AUDITED; SEE EXECUTION UPDATE]

- Verify Cecil itch/GitHub/wiki/nav catalog and actual `Scripts/Cecil/maps.txt`, nav hashes/CRC/world content. World-path suffix hash is not integrity CRC.
- Matrix for Desert Temple, Little Trouble, Lost Tomb, Fortress, Hole, Compound, Red Station, Skulls, Yodeller. Record load vs movement/item/height/teleport/jump/hazard/map-reset evidence independently.
- Inspect private build048 evidence as well as older tracked reports; never inherit old candidate acceptance. Hole/Fortress liquid/lava routes require explicit evidence. Desert Temple remains excluded without installed world and binding.
- Whitelist only actually accepted maps; repair or temporarily use accepted Red Station, without pretending file load is functional acceptance. Record coop gap; no coop port or removal of mode guards.

## Task 6 — A5 backup, Dev gate and sequential rollout [PENDING; DEPENDS 1–5]

- Commit and push distributable source/config/nav metadata/names/reports; confirm remote SHA. Upload private restore archives to existing Drive project and verify size/checksum or download. Isolated restore test before deployment.
- Hold exclusive deployment lock; Dev first, then public servers sequentially. Verify PID/start identity, mapped DLL inode/hash, config/nav/map, eight actual active bots, fresh kill/damage/respawn evidence, Vanilla sync, resource budget and no new restart/error loop. Roll back a failing instance and stop rollout.
- Budget baseline: >=8 GiB disk free; measured RAM/CPU/tick headroom. Existing stability gates (3600/3600/7200 s where applicable) remain pending until actually satisfied.
- Completion requires every A criterion on all discovered live instances; `qualified=false` cannot silently become approved.

## Task 7 — B1/B2/B acceptance [NOT STARTED; HARD DEPENDENCY A COMPLETE]

- Only after A: Dev Red Station individual session controller; prefer measured solo support, otherwise prove independently controllable slots. Persistent stable IDs, six states, exclusive lock, idempotence/backoff/jitter, actual query/log joins/leaves, replacement-before-leave at minimum eight, no humans removed.
- Local event chat pool DE/EN, RU only after encoding test; separate flags. 5–12% event probability, per-bot 3–8 min, <=3/server/60s, >=10s gap, 1–4s delay, no duplicate within30min or recursive bot conversations.
- Native three different bot cycles and rejection/full/crash/controller-restart cases; prove siblings unaffected, all registries/queries agree, budgets (25% CPU reserve,1.5GiB available RAM,8GiB disk) hold. Public stays A throughout. Backup B then staged rollout only with full Dev acceptance.

## Review focus / stop conditions

Unknown player classification; stale inode-vs-path identity; partial UDP responses; false name uniqueness after formatting; incomplete archive/symlink restoration; Cecil preset overriding difficulty; item navigation suppressing valid combat; accepting stale build evidence. External access failures are recorded with actual attempted operation. Continue independent work; never promote a failed/incomplete gate.

## Handoff

Execution status, rollback and next steps are maintained in `docs/reports/2026-11-11-milestone-a-progress.md`.

## Execution update 2026-11-11 19:15 UTC

Inventory and file-restore completed. Task2 PARTIAL: public five load zero; Dev rolled back after three actual sync kicks. Task3 portable implementation/tests complete, native rendering/deployment open. Task4 bounded implementation/build complete, requested gameplay/comparison gates open. Task5 nine-map audit complete, no candidate whitelist. Task6 before backups verified; final source publication and after backup completed with remote verification, Drive roundtrip and isolated file restore. No new DLL promotion. Task7 not begun. See full report and HANDOFF for receipts and current exact scope.

## Autonomous continuation 2026-11-11 19:22 UTC

Goal remains all A then all B. Previous turn made concrete code/runtime/backup progress; no completion claim. Current inventory refreshed (18 native fleet processes, original DLLs, five public zero configs, Dev3 after rollback). Windows RDC still offline. Own isolated Wine original-client probe created with private namespace/display/roots; actual exported session getter disassembled and read-only observed. All250 names now pass the original Engine decoder and LengthNaked in a new native executable run (not merely old parser examples); native visible rendering/query still open. Two agents fixing observed A3 trigger/aim and A4 item-route-cycle defects in separate worktrees. B remains gated.

### Continuation evidence / rulings

- A3 RED/GREEN: pre-turn aim trigger suppressed aligned moving-target shots; final-residual settle and ordered response gain implemented, with hard bounds unchanged. Ordinary item pursuit no longer suppresses feasible combat; urgent acquisition remains.
- A4 RED/GREEN: retained old048 Hole44s/Skulls25s bounded same-hop cycles are FAIL evidence, not merely missing verdicts. Extended mapped/relocated item transit now ends after10s without0.75m best-distance gain, preserving fixed deadline and existing30s rejection expiry; fresh typed/needed/reachable selection follows. Independent code review found no material issue; native rerun still required.
- Main replayed1372bridgechecks and183tools tests; build002 succeeded, qualifiedfalse. Two isolated native320s spawn3/0 field controls precede denser comparison. No goal narrowing to the completed subset and no B implementation.
- Ruling: Windows RDC offline does not block all Retail functional work; use licensed unchanged original client under Wine with private namespace/normal input and explicit Wine evidence scope. No Windows/GPU/WAN acceptance inferred.


### Native acquisition regression / Build003

Ruling: do not finish three Build002 trials just to satisfy a count after its shared Supply regression is demonstrated. Trial2 completed diagnostically; finalcandidate must receive three actualmatched comparisons. Retention fix77d8339 preserves mapped route identity across temporary closecombat; all safety/deadline gates retained. Build0030ae31bb... now owns fresh native sequence; firstwindow livehandle33276. A2representativeGUI/localGameSpy passed180s with originalclient; keep WAN/physicalWindows scope separate. A1exactfirststate/human/restart/mapchange still open despite provenordinarycannonkill0.30s afteroldbotspawn.


### Continuation20:46UTC

Hole configuration rolledback after9BAD/max8/noDisconnect; Devremains3. Fourpublicconfigs0, Hole/Dev3, alloldDLLs. Fresh20:39queries6×8ownbots/noextras/current18logs0BAD/0disconnect;27.36GiBdisk/2.40GiBavailableRAM. No newreleasepromotion.

Build004 diagnostic-only43908fa08d7cb40c058fd03d455797feae8b40c9be4cf94667aa9ee179b14310, source7e96f03,1406SDK107sanitizedbridgechecks plus183tooltests.120soff/on controlsclosednormally/noSync. Realmetadata explains globalweaponrespawn/render5 andinvertedrawGameSpyweaponsstay value; no filterremoval. A separate26sjump-padloop aftercommittednavigationcancellation is nowreproduced inlogs; boundedTDDfixassignednavagent, independentreviewcombatagent.

NormalPausefromownbootstrapwindow frozeoriginalserver whilecohortsjoin. Twoearly15.6sswappedDLLprobesmatchall8actualpositions/owned3 andseed; each8spawnclockspread0. Testmechanicsproven, nofullcomparisonacceptanceyet. Versionedsourcesnapshots/hashes underpoc/experiments/milestone-a-20261111, privateevidencearchived. Nextreusableharnessmustfinalizeaftercleanup; helperTDDassignedcombatagent. FullA1firststate/restart/mapchange, final3tiercomparisons, mappedfunctional/hourgates, Dev+fleetrolloutstillopen. Bnotstarted.

Build004 privatearchive uploaded/rereadSHA62b2b0350656e0b14a0529bcd6cd934eeb543bbd0c6ac5cb32aa2ad86a65cc1f,4554807bytes,163regularfilesseparatelyrestored,2linksindexed. EarlyPauseprobeswerecompletedlater andnotinthatarchive; nextsnapshotmustincludethem. Remote d6a80b4 tree equalslocal7236b7b; newerlocaldiagnostic/probesourcesneednextpublication.


## Current execution update — 21:44 UTC

The earlier fleet inventory and live handles are historical. Fresh21:24 reading confirms all six servers with eight own bots, no extra slots, effective session Spawn0, and current logs0BAD/0Disconnect. A separate completed community-notice task changed all BotA DLLs; preserve it. Existing foreign notice source was byte-verified and incorporated default-off into006+. Dev and Hole had previously been restored by this task to3 after external sync failures; later return to0 is observed, authorship unknown. No A-candidate DLL is live.

A2 native format work is now demonstrated: all250 additions through the actual original Engine parser, plus five format categories rendered in an original Wine client and independently queried. Live fleet allocation remains pending.

A3/A4:005 completed two crossed240s windows. Actual first positions/inventories match for8/8 physical slots and DLL roles exchanged. Frags improve in both roles against Dev048; first useful weapon is still delayed50–63s in some lives. Full life denominators and failed/censored cases are recorded; no acceptance.006 diagnostic controls completed60/240s with normal cleanup and0sync errors. Actual connector hit behind target yields bounded segment fix e1a6bcb. Actual visible-target handoff aborting orphaned flight yields separate ownership fix297c1bc. Main1563 integrated SDK107 ASan/UBSan checks plus actual Driver/item adapter checks passed;207tools tests passed. Independent reviews found no material defects. Build007 ce15842a36fee25d56fb1ffcb0f0a45878c254d9b0c5b95b129ce7708abf4b7f is built, unqualified and isolated only. First native smoke includes the guarded all-player original-engine inventory observer; its runtime success and costs still require evidence.

Backups: full original baseline and dedicated fixture remain verified; latest005/006 progress archive14,827,716bytes, SHA47da01c1a112b355f9992bc441748b5431e1b66d938d65e14e79a4909a4bcdc3 uploaded, actually downloaded identically and580regular files written/rehashed separately. It includes both Git histories and the complete foreign notice task. It predates297c1bc/Build007; next delta must include those and new observations. Latest verified remote77fa03bc6a882c2a6d4c94143939009226c9bd31 has the exact3fe9ec6 tree; newer local source/report commits need publication.

Next sequence: finish007 smoke and actual supply/movement regression test; diagnose remaining long first-weapon paths from actual choices, then run final three tier comparisons against actual public7fc with proven equal starts. A safe normal-console bootstrap prototype for7fc's staggered respawn is prepared but not natively qualified. Complete first-state damage/Vanilla/mapreset/restart, map functional gates and required stability windows, Dev acceptance, backed-up staged A rollout. B remains entirely unstarted until all A gates pass.
