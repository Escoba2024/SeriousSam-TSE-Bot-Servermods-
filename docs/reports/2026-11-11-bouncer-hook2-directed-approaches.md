# Second Bouncer trace: four failed approaches and two successful launches

Read-only analysis after final cleanup of all four roles in `arena007hook2-checked-swap1-trial-1-222849`. This is the completed120-second SWAP1 diagnostic, not a release qualification. The companion JSON includes source hashes and sanitized observations. No process access or code/runtime changes were made during this analysis.

**Candidate007 demonstrably launches from Bouncer234 twice, but four other observed approaches advance toward34 without a234 function call and fall to a lower level.** The difference is associated with the incoming route: successful candidate approaches use9→10→11→12, failed ones use6→7→8→12. This establishes a real directed approach failure, not its exact implementation cause.

The final measured botA launch is candidate007 (`ce15842a…`); the earlier botA bootstrap launch was old048 and must not be mistaken for its measurement binary. BotB is old048 (`ec820d04…`). Actual Cecil entity IDs and native inventory bind botA locals0–3 to565–568/global slots0/2/3/4, botB569–572 to slots5–8. Vanilla is remaining563/slot1. Sampling-group names are not used as cohort evidence.

| Candidate local / generation | First sampled source12 tick | Incoming route | Observed result |
|---|---:|---|---|
| 3 / 5 |1040|7→8→12|No234 call; falls below destination level|
| 2 / 5 |1300|7→8→12|No234 call; falls below destination level|
| 0 / 6 |1380|7→8→12|No234 call; falls below destination level|
| 0 / 7 |1720|10→11→12|Actual launch; Minigun acquired|
| 2 / 6 |1720|7→8→12|No234 call; falls below destination level|
| 1 / 6 |1760|10→11→12|Actual launch; rival takes Minigun during flight; bounded finish continues|

These six are observed source12 episodes in six lives, not a denominator of every conceivable pad approach or every player life. The hook covers the full measured window, reports44 total function calls,42 to other pads, two matched234 calls, zero unmatched players/faults/drops. Other-pad calls are counted rather than individually recorded; do not attribute their identities from these counters.

## Actual launches and item contention

Event1 is565/local0/gen7 at75.699079 seconds into the window. Before support is234; velocity approximately(−1.72,−11.39,2.59) changes to(68.48,61.73,−74.01), support clears. The bot retains source12/hop34 through the flight and acquires Minigun bit64 at Cecil1797, owned3→67 (`botA.log:1544`). Subsequent native inventory confirms67 (`inventory.jsonl:1503`); the next Cecil state uses anchor34/source34. This is an actual candidate route and pickup success.

Event2 is566/local1/gen6 at78.043079 seconds,2.344 seconds later. Support234 becomes null and velocity changes from(0.41,−11.55,10.34) to(72.62,63.78,−68.26). This bot already acquired a Grenade while approaching. Local0's Minigun acquisition coincides with local1 goal243 becoming unavailable at1797 (`botA.log:1551`). Local1 immediately begins `CecilFlightFinish` on12→34 (`:1552`), retains goal_entity0 and navigation ownership in samples1800/1820/1840, and ends at1846 with reason=context and unchanged deadline111.222 (`:1638`). It subsequently has normal support in the destination area; native83.350487 still shows the same life,67.25HP and owned259 (`inventory.jsonl:1575`). It does not gain Minigun during this finish. That is observed item contention plus a successful physical finish, not a failed Bouncer start. The context end alone does not identify which internal guard fired.

## Failed route, with and without the polling gap

Local2/gen6 is the requested simultaneous failure control. It has source8/hop12 at1700, source12/hop34 at1720, then continues falling at1740/1760 and reaches the lower level at1780 (`botA.log:1459,1473,1491,1510,1537`). The same Minigun goal stays valid throughout this failure until the other bot picks it up at1797. No234 call belongs to567 anywhere in the complete hook. Thus neither a recorded launch followed by bad flight nor an unavailable-item reset explains this particular initial miss.

The inventory has a3.55-second gap exactly across this approach: native72.899849→76.450066 (`inventory.jsonl:1414–1415`). The Cecil transition at1700→1720 lies inside it. Later server samples show support null and a path already beyond the pad before descending. These observations cannot locate the exact arrival decision, jump input or first missed collision tick.

The earlier local3/gen5 failure supplies a denser physical comparison. Native40.599667 still has support and ramp velocity approximately(−17.15,2.61,0.01);40.749664 is airborne, then41.349655–41.599651 crosses the horizontal area bounded by the two successful contact positions while substantially higher. At41.499653 the player's origin is about4.7 units above those contact origins, moving(−17.55,−5.26,−0.17), support null. By41.849648 it has travelled past that area before descending to approximately contact height. No234 event occurs. A later upward velocity change is not a234 launch and its exact cause is not recorded. Cecil1020 still targets12;1040 has advanced to34 (`:966,980`). The sequence supports a physical overflight during the8→12 approach, while the nav state advances, rather than rejection inside JumpFromBouncer's support guard: the matched function was never entered for this attempt.

The static pad brush bounds and this trajectory are not a full model-brush collision-volume calculation. The current evidence does not isolate whether arrival handling, jump timing, movement speed, or their interaction causes the miss. Successful fast approaches from the other direction also prevent a blanket inference that candidate speed alone is defective. Do not remove flags, shrink radius, inject a launch, or change physics from this trace alone.

The narrow remaining measurement is the actual per-action8→12 arrival/advance condition and final jump/movement output around one of these reproducible failed approaches, with uninterrupted native position/velocity/support sampling. Reproduce that precise decision trace in a portable regression before selecting a gameplay fix. The observed FlightFinish success should remain a separate preservation regression.

Final receipt reports full120092ms listener overlap, clean detach and original-body restoration, no observed SYNCBAD/disconnects across all four roles, and all four closed. Coverage supports the bounded absence-of-call finding; it is not long-duration sync or zero-cost instrumentation proof.
