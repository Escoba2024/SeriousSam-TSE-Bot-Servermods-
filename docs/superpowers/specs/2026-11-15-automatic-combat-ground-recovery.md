# Automatic combat ground recovery

The source reproducer demonstrates that ordinary visible combat can retain this
bot's own movement while Supply's ground-position watchdog is gated off. This
feature closes that narrow position-time recovery gap. It does not establish the
cause of the native026 episode or change any historical result.

Claim: `BotSupplyNative.h`, `BotDriver.cpp`, existing native Bridge test and the
action-contract test's strictly necessary new-call compatibility, this new spec,
own new plan/report/private evidence. No `cecil_motion.h`, diagnostics, casts,
RNG, native builds, runtime, live changes or delegation.

## Separate authority

Append a default-false `combatRecoveryRequested` argument to final SafeMotion;
`useReacquire` keeps its existing meaning. A small production helper evaluates
the actual Driver request: automatic AND humanMode AND visible target AND not
supplyActive AND finite nonneutral forward/strafe AND exactly zero up. It is
tested directly; the actual Driver call is checked, not replaced with a test-only
predicate. Manual, invisible, neutral, nonfinite and vertical requests cannot opt in.

Combat recovery must remain in the existing offgraph/no-goal recoveryContext,
same-tick fresh ground observation, movement and support stamps, current grounded
life/world/map/gravity/contact identity, budgets and physics. Because existing
stamps are only times, retain a small combat-only same-tick metadata pin at their
existing Reacquire production site. It binds player/world/map/entity/generation,
reference and its identity, StandOn and gravity. No additional cast or allocation.
Invalidate it at every SupplyTick/reset/death; a changed/missing pin authorizes
nothing. Existing Nav/default-false contexts do not require this new pin.

## Movement and ownership

Before a real stall/eligible active escape, keep the ordinary combat request's
speed and ordinary collision safety. Only actual2s stationary time or a still
authorized existing escape can enable the existing0.3 bounded recovery. Preserve
0.25s maximum observation gap,0.25m progress threshold, fixed0.6s escape hold and
existing sweep/cooldown/deadline/ray/strafe/pit rules. Fresh casts still decide
every emitted action. The0.5 ordinary floor normal and the exact current-contact
exception are unchanged. Invalid/no-intent input cannot renew a held escape.

Combat cannot acquire/change NAV goals, mark hint Tried/rejected, clear or extend
hint backoffs, accept flight, or inherit Nav-only traversal authority. Gate the
existing `rejectOriginal` hint mutation explicitly on `useReacquire`. Every
FlightAccepted call still receives `useReacquire`-derived authority. Owner/context
changes reset shared stationary observation/held recovery rather than inheriting
a2s combat stall into another ownership domain. Existing false-default behavior
and tests remain unchanged.

## Evidence

First real RED: default implementation accepts the new optional argument through
a test compatibility overload but cannot escape under actual ordinary visible
combat ownership. Then smallest implementation and one normal full relevant
Bridge GREEN run. Add focused opposite controls for trigger/caps/budget/life/map/
reference/contact/no-intent/direction hold/owner flips/fresh stamps, preserving old
false-default assertions. No ASan without a new memory issue. Portable approvals
are not physical escape or native qualification. Root alone reviews/builds/freezes
and decides a later native case.
