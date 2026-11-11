# Original Retail pause and matched-start design

This is a read-only investigation plus a passive observer tool. No input was sent, no process was launched or changed, and no native memory was written by this task. The parent separately owns the isolated runtime trials.

## Existing comparison limitation

The build003 observation `arena003-trial-1-195642` starts its shared sampling window with the old cohort already7.85–8.00 seconds into its lives; the new cohort has0–0.10 seconds of spawn age and one pending spawn. Build004 diagnostic-off `arena004-diag0-trial-1-202055` has the same problem: old8.10–8.25 seconds, new0–0.15 seconds. Fixed join order and bot profile seed did not reproduce the same starting markers between these runs. Their scores cannot establish matched or exchanged starts.

The SDK reference `Sources/EntitiesMP/Player.es:GetDeathmatchStartMarker` ranks markers by distances from current players, chooses using IRnd among the farthest half, and skips recently used markers. This explains why movement during joining matters; it is not a blanket Retail ABI equivalence claim. The bot profile seed affects the bot policy, not the native spawn PRNG.

## Original binary proof

Engine SHA256: `b79bf8bb3927fe4f8f252e141d721ae5c738df02218f0ecc12da5c1afbcb534f`, preferred image base `0x600c0000`.

- Export `TogglePause`, RVA `0x0dab40` / VA `0x6019ab40`: `8b412033c98b90ac00000085d20f94c18988ac000000c3`. It toggles the requested flag at session+`0xac`, with session read from network+`0x20`.
- Export `IsPaused`, RVA `0x0dab60` / VA `0x6019ab60`, normal-path bytes: `85c97413a1b8d62c6085c0750a8b41208b80a8000000c3`. It reads actual pause at session+`0xa8`; a separate global/disconnected fallback can return true. The helper therefore labels raw actual/request flags explicitly.
- Export `_pNetwork` is RVA `0x20d6a4`. Last processed game tick is session+`0x4c`, already used by the existing hash-pinned session observer.
- Original persistent shell symbol `ser_bClientsMayPause` is registered to `0x602a7ec0`; handler `0x601a37ac` tests it before accepting the nonprivileged client pause path. It is initially0 in the private server configuration.
- Original `IsWaitingForPlayers`, RVA `0x0dacd0`, checks session wait-all flag+`0xc0` and compares actual player count with maximum+`0xbc`. Normal `gam_bWaitAllPlayers` / `gam_ctMaxPlayers` are configuration candidates; this investigation did not run a wait-all prototype.

Original SeriousSam.exe SHA256: `9f8f9a0b8fd718616036ed2c3584904e2dfd58e49515bf4c8ecc45175d02cc53`. At `0x435a9a` it checks WM_KEYDOWN `0x100`, then VK_PAUSE `0x13`, and calls imported TogglePause at `0x435ab1` through IAT `0x47907c`. Local libX11 `XStringToKeysym("Pause")` returns `0xff13`; no display/input event was needed to verify this mapping. Thus the existing PID-verified normal-input helper can support Pause without injecting code or calling engine exports.

Actual native IRnd at `0x601c2510` calls Rnd at `0x601a42e0`, which updates session PRNG state+`0x7c`. Exported ResetRND at `0x601a4300` initializes `0x87654321` and advances32 PRNG steps. No normal configurable shell seed setter was found in the original Engine/GameMP/executable declarations. ResetRND is a C++ method, not a demonstrated shell setting; do not call it or write its state as a workaround. Deterministic initialization does not prove identical intervening RNG consumption.

## Completed parent-owned pause prototype

Independent examination of retained `arena004-barrier-diag1-trial-1-202841` records a30.011-second limited observation. The parent used normal Vanilla Pause with private `ser_bClientsMayPause=1`, joined both cohorts while paused, then resumed normally. Its result records a fixed barrier tick16.000041961669922 and nine entities before release.

All eight bots have the same original-server spawned_tick16.20003890991211, giving measured cohort spawn-clock spread0.000 seconds. The observer is an older life. All eight initial CecilSpawn positions are retained. Different local action ticks195 versus34 are client-local counters and do not imply different server spawn ages.

There is an initial raw-observation gap from game tick16.05 to19.60 because `lastcontrol=-100` immediately invokes three blocking observer-input operations after the first sample. Defer observer input for12 seconds (`lastcontrol=0`) and collect uninterrupted dense samples for the first1–2 seconds after release. The initial paused bots have health0 and have not spawned: equal pre-release entity count does not yet prove matched positions. Use the first actual spawn events and server spawned_tick after release.

## Minimal crossover protocol

1. Keep map, original server, physical role directories, private player profiles, join order, roster size, observer setup and pause sequence fixed. Record hashes for all shared session/config inputs. Apply normal pause before either measured cohort joins; verify actual pause and frozen state, not merely the requested bit.
2. Join all measured clients while paused. Start dense observation before normal release; defer observer inputs. Require actual eight-bot spawn-clock equality/bounded spread, alive transitions, starting ownership/health and complete first-spawn positions. Record each bot's physical role/local slot and its actual initial marker/placement, rather than using its later moved position.
3. For the paired leg, swap old and candidate DLLs plus their required policy configuration between the two physical role directories. Preserve the physical role order and identity slots. Keep the candidate tier fixed within that pair. This tests exchanging cohorts across the same physical starts rather than altering join order.
4. Accept the pair as exchanged starts only when the actual initial positions for each physical role/slot match between legs, within a predefined measurement tolerance and equivalent observation age. The DLL cohort must then occupy the other cohort's first-leg positions. Predeclare this gate before reading the scores; mismatches are unmatched diagnostic runs, not accepted comparisons. Record observer initial position/state as well.
5. Obtain at least three qualifying paired comparisons for the release candidate. Report acquisition including failed/censored lives, actual weapons, damage/kill events, deaths, stuck episodes and within-window frag changes. Different candidate builds or a mismatched start pair cannot silently substitute for required candidate comparisons.

If repeated barrier starts still differ, compare the passive PRNG state and bootstrap actions before release to identify the divergence. Neutral bootstrap input and a repeatable pause/release sequence may remove it; that needs native observation. The proposed normal-config bootstrap uses old048 with AutoCombat/Human/Supply disabled and no Vanilla fire until the pause barrier, then restores measured cohort settings before their joins. Actual all-peer pre-release PRNG equality must be observed across legs, never imposed. Normal gameplay repositioning with a full state gate is an alternative, but no such positioning control was implemented here. Do not claim seed control or matching solely from a constant configuration value. Save/load, teleporting, seed writes and forced world mutation are not part of this proposal.

## Passive helper

`tools/probe_retail_pause.py --pid PID --root OWN_INSTALLATION` outputs only `actual_pause`, `requested_pause`, `game_tick` and current `random_seed`. It opens process memory read-only, verifies the original Engine hash, mapping identity and the TogglePause/IsPaused/Rnd/ResetRND instruction sequences, and checks process/session identity again after reading. It reads PRNG state at session+`0x7c` without modifying or advancing it. Rnd RVA`0xe42e0` is pinned by its complete17-byte function, ResetRND RVA`0xe4300` by its complete64-byte function. It neither calls the exports nor sends input. Sampling is not atomic; the caller must require repeated stable samples and player-state evidence. Reading file access time does not invalidate the identity check.

Verification performed here: Python compilation, original binary hash/instruction-pin comparison, invalid-PID refusal and wrong-process-directory refusal. No native process was read by the new helper during this subtask; its end-to-end use remains a parent-owned runtime check. The parent's separate existing observer supplied the pause prototype evidence above.


## Parent native use and actual crossover

The parent invoked the pinned observer on an authorized isolated server, verifying pause0/request0 and finite tick38.249702, followed by real pause1/request1 on server and allthree clients. No export was called or memory written. Two neutral-bootstrap30sprototype legs then swapped candidate004 andold048 across physical roles while retaining directories/GUIDs/joinorder. All8initialCecilSpawnpositions matched exactly by physical role+local slot; all8server spawn clocks had spread0.0 ineachleg; firstalive observedowned masks also matched, including one early DoubleColt. Full sanitized evidence: `milestone-a-20261111/native-start-crossover-prototype.json`. Raw pre-release RNG differs by one call; these are equal observed starts, not full identical simulation replays. Neither shortpilot closes the three longercandidatecombatcomparisons.

A further normal-input prototype paused via the PID-verified bootstrap bot window before starting Vanilla. This worked despite nullrender: server clock0.6500001 stayedfrozen acrossjoins, all9players remainedunspawned before release, thenordinarybotactions spawned them. This eliminates pre-barrier itemconsumption; a crossed counterpart is pending. Normalclose cleanup completed; no forcedexit or productionresource change.


### Early common-start counterpart completed

The early bootstrap-Pause15.6s pair also matches all8positions and allfirstaliveownedmask3, with actual pre-release seed2306364401 inbothlegs, all9players unspawned before release, and eachleg's8bot spawnclockspread0. Absolute spawnclocks differ(.8500001 versus1.0000001), not an identical-clock replay. NoBAD/disconnect/error, all4roles normally closed. Sanitized record `milestone-a-20261111/native-early-start-crossover.json`. A transient non-atomic row health100/spawn0 was independently identified; subsequent repeated coherent samples support the spread result, not the transient.

Independent review found a general historical harness limitation: windowPASS is assigned beforefinally, whose cleanup errors do not themselves make exitnonzero. Allreviewed artifacts separately satisfy errors=[] and all4closed, so those actual cleanup conclusions stand. The versioned snapshots are archival, notfinalacceptanceharness; the next reusableharness must finalize status only after all expected roles have valid identities and completed normal cleanup.
