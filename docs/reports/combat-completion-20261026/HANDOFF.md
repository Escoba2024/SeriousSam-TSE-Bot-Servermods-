# Combat completion handoff ·26 October2026

Scoped source candidate completion from63638893b40ee6b8c095a634213eb5cf2656ffbe on branch agent/chat/20261026-combat-completion, worktree /srv/tse-combat-completion-20261026. No source work in other checkouts, runtime operations, Windows/Wine builds, deployment, push or merge.

## Confirmed fixes

- QA02: BeginTick can activate history retreat before this tick's observations. Step previously returned for100ticks even after accepted fresh LOS. Step now cancels active history retreat on fresh Perception::Visible before its early return. ChooseTarget and aim still impose normal reaction/LOS gates; raw actor coordinates alone do not cancel retreat.
- QA01: the unflagged45degree target-bearing stop reset native recovery during hidden-target detours. This turn hold now applies only to exploratory movement without active recovery. The existing NotifyNavigation callback records recovery ownership; Reset clears it. Both remembered- and visible-target detours preserve movement intent. Existing final hazard/injury movement gates remain authoritative.

Neither change adds a competing combat/respawn/target controller. PR66 weapon/lead/strafe defaults remain false; profiles and skill/persona tables are unchanged. The original PR57, PR66 and QA PR62 source pins and module extraction are unchanged.

## Reproducible portable evidence

Command: `nice -n 19 python3 poc/candidates/combat-master-20261026/verify.py`.

| Gate | Result |
|---|---|
| Actual HumanBotPolicy + ObstacleRecovery regression suite |29414 assertions,0 failures|
| Existing composed policy suite |1243 assertions,0 failures|
| Existing default-off compatibility corpus |21600 complete rows identical to PR57|
| Inherited PR57 test executables |10/10 PASS|
| Real driver-block portable smoke |PASS; engine stubs only|
| Exact native disabled-recovery reset branch |PASS; real policy/recovery; original branch RED exit3|
| Botcore/GameMP source mode parity + refusal to overwrite |PASS|
| Native build/Retail1.07/sync/gameplay |NOT_TESTED|

Initialized-fixture original-source RED and independent mutation results are recorded in RED_MUTATIONS.json. Original history-retreat cases produce100 retreat ticks and0 shots; independent removal of either repair fails the regression executable with exit1. Corrected fresh-visible ambush produces0 retreat ticks, first target at tick25 after reveal21,32 policy fire commands. Delayed reveal26 produces5 retreat ticks, first target30,32 fire commands. Reaction is preserved. Occluded and outside-FOV controls retain100 retreat ticks and0 shots.

The wall fixture uses native weapon/distance hold thresholds and no-target movement fallback. The default hidden-target fixture crosses behind the pillar with0 recovery resets. Exploratory mode clears the pillar laterally with0 resets, then chooses new travel after its target memory expires; it does not guarantee pursuit of expired observations.40 independent seeds exercise actual exploratory travel with bounded turning and resumed motion. This distinction is explicit in tests and VERIFICATION.json.

All three candidate fixture sources now value-initialize every SenseInput, correcting the fresh reviewer's undefined-input finding. The complete suite and independent RED controls were rerun after that correction. The compatibility corpus deliberately excludes corrected scenarios. Byte identity on that corpus does not claim global PR57 equivalence; the regression fixtures pin the intentional behavior differences.

PR72 audit pin7df2867e1ad7a6101b95a54031d7583265977f72 was fetched read-only through GitHub tools. Its R02 search mirror assumes an obsolete heading/speed sequence. Actual pinned PR57 uses RouteMemory::Travel; the completion tests call that production path directly. No QA mirror or post-policy replacement simulator is used for combat decisions.

## Integration seam

Materialize an absent output directory via:

`python3 poc/candidates/combat-master-20261026/apply.py --gamemp NEW_OUTPUT`

Pass its flat overlay to the parent's existing builder `--source-overlay`. bot_human.h is patched before materialization; BotDriver.cpp uses the updated driver.patch, including NotifyNavigation(false) when recovery is disabled or inapplicable. No new translation unit, linker input, public callback or CVar is introduced by this completion. NotifyNavigation must continue to report each final recovery decision (including false when recovery ends or is disabled), as RouteMemory already expects. Keep bot_human.h, combat_master_support.h, combat2_weapon.h and combat2_selected.h alongside BotDriver.cpp. SOURCE_MANIFEST.json retains exact input/local/output SHA256. The newly added regression file is compiled by verify.py and is not a native source input.

## Remaining work and evidence boundaries

Parent must review/cherry-pick the commit and conduct any native build, artifact hash, isolated1/4/8bot joins, instrument-free sync and gameplay tests. Source acceptance does not qualify a Retail DLL and does not explain existing PR57 four-bot SYNCBAD. The protected61DC DLL and original source checkout/untracked compare_qa62.py remain untouched.

PR72 QA11 pre-draw shot-cadence charging and QA13 close-target adapter navigation gating are not repaired by this scoped QA01/QA02 patch. Real driver-block smoke ends before parts of the native movement tail (QA14); the added exact reset-branch executable covers the disabled-recovery notification seam, while other tail logic is outside that smoke; closed-loop tests therefore name exactly which real policy/recovery contract they exercise and do not claim complete native adapter coverage. PR69 arbitration is not imported here; the parent must ensure its chosen owner honors accepted fresh combat and final movement safety. Observation-age measurement, projectile/cannon behavior, strafe self-motion/evasion and native gunplay remain unqualified as in the original C1 handoff.

Fresh independent review identified and corrected undefined fixture inputs and stale recovery state when obstacle avoidance is disabled. The final complete portable suite passed after both corrections. The independent RED mutation controls fail with319/307/12 assertions respectively (original / without cancellation / restored unflagged turn stop), and the old exact native reset branch fails with exit3.
