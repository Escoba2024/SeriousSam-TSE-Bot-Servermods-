# Native008: early normal jump before Bouncer234 contact

The completed120.006-second private crossover provides two per-action instances of the same failed8→12 approach. All four roles closed normally; errors=[], zero observed SYNCBAD/disconnects. The original-function hook covered the complete gameplay window, with30 total invocations,29 other-pad invocations, one matched Bouncer234 call, no drops/faults/unmatched players, successful detach and restored original body. These are bounded diagnostic observations, not general A or release acceptance. Build008 SHA256 is `07113052dac65df7143f8418e5e2c3ef1c9f1ebd5acc96b6fba55c4166bffb4b`.

## Exact failed action chains

| Candidate life | Initial8→12 action | Next action | Airborne radius arrival |
|---|---|---|---|
| local3/gen5 | tick945: requested up1, final composed up11, support54, vertical translation2.614 | tick946: support0, vertical translation17.238 | tick959: reachedHop12=true, outputHop34, support0,4.636 above node12 |
| local1/gen7 | tick2528: requested up1, final composed up11, support54, vertical translation2.614 | tick2529: support0, vertical translation17.238 | tick2542: reachedHop12=true, outputHop34, support0,4.701 above node12 |

Both initial actions have NAV ownership and SafeMotion result1. This is an actual ordinary jump command and subsequent physical departure from the supporting ramp. It is not a missed Bouncer launch: neither player's entity has a Bouncer234 call under the complete retained hook coverage. At the airborne arrival, requested yaw turns9 degrees toward the remote destination and forward command reverses, while westward native translation remains approximately17.55. The bot passes above the pad and reaches pad height beyond its west geometry bound. No radius/contact equivalence is assumed.

The immediately preceding actions958/2541 still have source8/hop12 and reachedHop=false. Actions959/2542 satisfy the original shifted sphere but are outside the original sphere centered on node12. This exactly identifies the observed navigation transition without changing its semantics. The [sanitized event JSON](2026-11-11-native008-bouncer-actions.json) retains action ticks, source log lines and relative positions. Client action time is not server time: local3's initial command position matches native37.899708; local1's initial command is bracketed by native117.002541–117.102547. Do not interpret client126.4 as elapsed time in this120-second window.

The separate candidate local2/gen6 has the sole matched Bouncer234 call with support234 before, cleared support and strong upward translation after, followed by Minigun bit64 acquisition at tick1116 (259→323). Its earlier11→12 approach is outside the early-action capture scope; this is a successful native launch/pickup control, not a complete matched approach experiment.

## Portable replay and minimal proposal

`approach008Transitions()` in the real bridge suite replays both exact pre-transition and transition positions, translated by node12's origin. It reproduces initial8→12 JUMP from target Override42, the preceding not-reached action, and the next airborne12→34 switch. It simulates no engine motion and does not prove a counterfactual landing. The complete ASan/UBSan bridge suite passes1594 checks with zero failures.

Proposed for review only: suppress the ordinary positive Up output on the actual directed8→12 approach while it still has normal support. Bind this exception to successfully validated original RedStation world/NAV contents (world CRCff3776e0, NAV content CRCe4571656; Cecil path hash5af1a276 is separate), current map generation, and the exact unchanged directed edge/node metadata. Publish that binding only through the existing validated loader and clear it on map change/failure. Preserve the authored flags, radii, navigator state, jump cooldown, goal deadlines and all movement safety checks. Do not affect11→12,12→34, unrelated jump edges, other maps, or liquid/action-specific vertical movement. Keep raw requested up visible separately from final composed up in diagnostics. No synthetic launch, contact, position or velocity operation is proposed.

This is the smallest first change justified by the observed premature normal jump. It is not yet implemented. The unchanged radius might still cause steering before actual contact during the new grounded approach; the next isolated native discriminator must observe that behavior before proposing any additional arrival rule. No contact or successful pickup is guaranteed by this portable replay.
