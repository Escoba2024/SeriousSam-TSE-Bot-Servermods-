# Native multi-Brush control and instrumented analysis, 2026-11-12

Retained files only; no runtime calls, memory reads, instrumentation or gameplay edits by this analysis. Both windows have final PASS_LIMITED receipts, four normal closes, accepted archived post-close logs, no reported sync/error patterns, matching launched/closed process identities, and original-server inventory identities. This is candidate 012 against 048, NOT the public 7fc comparison or A3 acceptance.

- Control: arena012brush3-i0-swap1-trial-1-010000, 120.031139775 seconds.
- Instrumented: arena012brush3p-i1-swap1-trial-1-010721, 120.041193138 seconds.
- Actual botA slots 0/2/3/4 are candidate 012 e0495577…; botB slots 5/6/7/8 are 048 ec820d04…; Vanilla slot 1. Attach identities, rather than physicalA group labels, determine cohorts.
- INI files for each physical cohort are byte-identical between these two windows. Gameplay trajectories and initial observations are not an exact matched-state controlled comparison.

## All observed lives

Useful weapon mask 0x3df8 excludes Colt/doubleColt/chainsaw. Counts include failed completed lives and right-censored lives; medians are success-only and never substitute for that denominator. Acquisition means first observed native owned bit, current means actual selected useful weapon, fire means observed request while current useful, not a hit or confirmed ammunition discharge. The accompanying compact [JSON](2026-11-12-native-brush-v3-control-analysis.json) preserves all 45 observed bot lives, exact cohort denominators and source hashes; raw inventory/function records remain private.

| Window/cohort | Lives | Death/censored | Useful owned/current/fire | Dead/censored without useful | Success median/max seconds | Minigun lives | Last query frag delta |
|---|---:|---:|---:|---:|---:|---:|---:|
| i0 candidate 012 |10|7/3|7/7/4|2/1|12.050/85.351|1|+5|
| i0 old048 |10|6/4|8/8/6|1/1|8.525/40.450|0|+9|
| i1 candidate 012 |12|8/4|8/8/6|3/1|9.150/23.100|1|+15|
| i1 old048 |13|10/3|11/10/3|1/1|10.400/37.049|0|+1|

Initial alive lives have an explicit left-window observation gap (approximately 0.50–0.55 seconds after spawn). Samples use two equal reads, not atomic snapshots; no transient unsampled life or first-state completeness claim. Last queries were at 119.748/i0 and 118.275/i1 seconds, before close. One-meter residence maxima around 2.2–2.6 seconds do not measure repeated route cycles or establish unstuck behavior.

Control candidate local 3/gen6 needed 85.351 seconds for its first useful Laser ownership. It tried goal 248→544→267, lost 267 at 663, next mapped goal 243 appeared at 1186, lost 243 at 1557, then 556 and 267. Pickup 1899 was followed by bounded 86→176 finishing and arrived 1901. This is multiple attempts and an unowned-goal gap, not evidence of one 10-second watchdog failure.

## Actual original function calls

The instrumented receipt has 31 total calls = 31 received records, zero unknown arguments/players/faults/drops/detach errors, full 120038.996 ms window coverage, successful detach and 123-byte restoration. The frozen registry contains 46 known Brushes. Thirty calls are inside the gameplay window; the first is 0.103 seconds before it and remains in the total denominator.

Argument Brush counts: 73×6,129×8,136×11,234×2,274×3,517×1. Each retained call changed actual current translation; render type 4 does not prove a Bouncer class, and this analysis does not label every call a successful route launch. Support identity is only membership in the frozen registry; unknown support pointers remain opaque.

The calls with argument 234 are candidate entity 566/local 1 at 41.593 seconds and old048 entity 572/local 3 at 47.247 seconds. Candidate entity 566/gen6 subsequently owns Minigun, first useful acquisition at life age 23.100 seconds. The function event, ownership sample, and complete path success are separate claims.

The material candidate 567/gen8 failure is detailed below. Three calls with argument 136 occur in that life and the window ends with no useful weapon. FlightFinish arrival at 86 does not terminate the physical upward flight. Candidate 012 therefore retains a concrete functional failure despite clean instrumentation/cleanup.

Other i1 bounded flight episodes, shown as local/generation, begin→end tick, edge and end reason: local 2/gen6, 678→685, 86→176, context; local 3/gen6, 1559→1574, 86→176, context; local 0/gen7, 2445→2447, 86→176, arrived; local 2/gen8, 2445→2474, 84→86, arrived. Each preserves its logged original deadline. The sampled surrounding states do not identify the exact failed context predicate on the two context endpoints.

## Observed cost, not causal overhead

| Role | CPU seconds i0/i1 | RSS start→end i0 bytes | RSS start→end i1 bytes |
|---|---:|---:|---:|
| Server |4.18/4.34|51359744→51752960|105656320→106180608|
| Candidate |4.32/4.04|189157376→189157376|189198336→189329408|
|048 |4.40/3.93|189308928→189440000|188907520→189038592|
| Vanilla |64.96/78.18|191254528→214323200|191922176→211083264|

Usage brackets include the initial normal observer input; RSS is endpoint observation, not peak. Different trajectories, frags and Vanilla CPU preclude exact causal instrumentation overhead. Reader i0: 3006 valid/87 torn discarded, 12.3166 seconds total, max 13.595ms. Reader i1: 2938 valid/68 torn discarded, 12.4543 seconds total, max 11.386ms. Hook setup 0.32256 seconds. No timeout/performance acceptance follows from these values.

Seven focused offline hook-analysis tests pass, including unknown opaque support, known registry mismatch, wrong argument/function, incomplete denominator/fault/detach, nonfinite/expired evidence, outside-window total retention and velocity change versus launch distinction. They validate analysis boundaries, not the game.

## Phase boundary: observed cause and bounded scope

Exact original NAV CRC `e4571656` / SHA `70e2839587b0f14c024ef978579133e84eed594a3cbbd0fa1f1db98d99aa37c6` has node 84 with JUMP|OVERRIDE flags 10, ordinary node 86 at height 38 with radius 1 and direct link 176, and ordinary node 176 with stable ID 178 and important entity 267. World content CRC `ff3776e0` and path hash `5af1a276` are distinct bindings.

In instrumented botA.log, local 2/entity 567/generation 8 retains 84→86 before loss (lines 2213/tick 2420 and 2231/tick 2440). Lines 2243–2244 record item 267 unavailable and bounded finish beginning 2445 with deadline 140.518. Line 2253/tick 2460 still has goal 176, goalEntity0, source 84→86, FALL and NAV ownership. Line 2267 ends at 2474 with arrived; line 2272 selects Minigun243 at 2475 with new deadline 168.750. Lines 2282/tick 2480 and 2299/tick 2500 show uncommitted source−1/hop86 at heights 48.285 and 60.310, horizontal neutral movement; later lines 2313/tick 2520 and 2344/tick 2560 show reacquisition and renewed elevation.

Original function event 27 for 567 at 110.047 seconds changes vertical velocity −11.241→53.175. Event 29 at 112.445 seconds changes −25.782→60.776. Both precede the radius endpoint. Inventory lines 2784/2785 bracket that endpoint at native clocks 114.652397/114.752403, heights 36.988/40.591, upward velocities 38.276/35.276, both with null support. Nearby CecilWeaponObserve lines2265/2273 tie driver ticks2471/2476 to native clocks114.552391/114.802406. The exact tick2474 callback position was not sampled; interpolation is not treated as a snapshot. Event 31 at 116.500 seconds again invokes the same original function with known Brush 136, changing vertical velocity −2.529→64.806. This proves an endpoint during upward flight and a later repeated contact, not a causal explanation of all three contacts.

In candidate 012 source, BotCecilFlightFresh pins identity/context/deadline and accepted movement; FlightEdge pins the current directed edge. FlightPlan stores only that edge. Finishing checks AtNode86 before normal navigator Update and clears on arrival, while ordinary live-item planning can carry special provenance across an actually reached successor. The selected future path exists only as a mutable navigator search tree: its root is current source for initial search or current hop for suffix refresh; timer/lock/arrival updates can replace it. A graph link alone cannot justify arbitrary flight extension.

The resulting narrowly authorized implementation is documented separately in [Preselected RedStation flight exit](2026-11-12-sealed-flight-exit.md): one actual pre-loss selected successor, accepted before sealing, unchanged identity/gravity/original deadline/locks, actual reached 86, exact ordinary Update output 86→176 or neutral cancellation, consumed once. It adds no search for new authority, Frida dependency, fake support, radius/topology change or new item/important action. Its portable tests do not establish native efficacy. Earlier repeated 136 contacts and other 86→176 misses with live items remain separate failures.

## Ordinary transit watchdog: corrected call interpretation

Candidate 012 BotSupplyNative.h line1556 calls its argument accepted, but Driver→SafeMotion→HopCheckpoint→ItemTransitFailed passes useReacquire, meaning Driver supplyActive. SafeMotion invokes the checkpoint at 1750 before final wall/escape/neutral selection. Consequently final SafeMotion return 0 or return 2 alone does not reset this clock; neutral return 1 also occurs after the watchdog.

Actual reset predicates include loss of NAV ownership/current-point observation, invalid frame, offgraph-air path, nonordinary nodes/interactions/locks, changed identity/attempt/edge/gravity, observation gap>.25 seconds and other explicit eligibility failures. A meaningful .75-unit distance gain resets the passive no-progress clock. These are existing conditions, not evidence that a final rejection causes resets.

The separately retained STARK local 1/gen8 source 0→1 trajectory has NAV 0 at 1900, then many NAV 1/floor 2 samples 1920–2100. The first is actual loss of ownership; accepted escape return 2 does not imply reset. Printed hop_clock values belong to a separate checkpoint, not itemTransitSince, and cannot reconstruct this ten-second timer. Source 5→4 appears 2120. No ItemTransitEnd event occurs in STARK or either V3 window. The control 85.351-second life spans multiple targets and a no-goal interval; it does not prove one uninterrupted ordinary-edge timer failure. Terminal 86→176 remains excluded from this ordinary-transit question. No deadline relaxation or rejection fix is justified by these logs.

## Verification and interpretation

The compact export checks every cohort's life/death/acquisition/failure denominator and rejects pointer/process/session identifiers. Closed archives were checked against final receipt SHA/length and sync/crash/invalid-action patterns; launch/normal-close identity equality was checked privately. Seven focused analyzer tests passed. These checks qualify retained-file analysis, not an A3/A4/full-map release.
