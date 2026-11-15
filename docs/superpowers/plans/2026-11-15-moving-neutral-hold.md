# Moving neutral hold: narrow source reproducer and correction

Claim: only BotSupplyNative.h, the existing test_cecil_native_bridge.py and new
own plan/report. Preserve the preceding029 audit and every old test. Root alone
integrates/builds/runs. No Retail, live, fixture or extra observer change.

1. Add an actual BotSupplyTick fixture establishing the original267→112 edge
   and W9 attempt with the original points/radii/flags. Show real fixture pose
   changes with neutral Navigator wishes, then observe the unchanged2s goal
   rejection. This must be an authentic RED before production changes.
2. Preserve complete stationary parent and negative cases: velocity/intent or
   FALL alone do not establish movement; frozen pose still rejects at2s;
   deadline expires identically; actor/life/world/nav/source/hop/goal/attempt
   changes invalidate position evidence. Keep old support/lock/safety/ray tests.
3. Use only actual positions and existing scalar context. The relevant existing
   Navigator progress distance is0.75m (cecil_motion.h:87), stricter than the
   independent0.25m ground-stall metric. No new arbitrary distance or relaxed
   hold/goal deadline. Reuse the existing0.25s freshness bound only if necessary
   for contiguous positional evidence; a gap must not itself renew the timer.
4. After RED, implement the minimum passive progress bookkeeping at the current
   neutral-wish hold branch. It may reset the false stationary timer only on
   genuine same-domain displacement; never grant movement/support/arrival,
   extend the goal deadline, change topology or add Engine/clock/RNG/ray calls.
5. Run the relevant full actual SDK107 bridge with ASan/UBSan once after GREEN,
   and only necessary targeted source regressions. Retain actual outputs/hashes,
   whole source diff and limitations; commit reviewable changes and stop jobs.

Status: completed offline; Root review/integration and any Windows/native test
remain separate. Initial compiler failure is retained as a fixture-compatibility
failure, not behavioral RED. The corrected fixture reproduced3748checks/1failure
against the unchanged parent. First correction:3933/0 normal. Final expanded
production-used guards:3968/0 in one full ASan/UBSan bridge run. No other bridge
repeats, Windows builds, Retail or live actions.

The0.25s observation gap is the unchanged CecilGroundProgress bound
(cecil_motion.h:27); new credit also requires consecutive Source ticks, equal
dt and exact gravity. Position distance uses all three world components, as
CecilNavigator::Update:87 does; no gravity-plane projection. Identity/context
recapture never changes holdSince. The parent heldNode/new-hold initialization
remains unchanged. ClearGoal/ClearAvoidance invalidate passive history; skipped
Source ticks cannot accrue unobserved progress.

Measured sparse poses are fixture anchors; synthetic20Hz intermediate positions
are not a native replay. The reduced graph retains actual267→112 coordinates,
radii/flags and direction, then connects112 directly to the same item goal0.
It does not reproduce the complete native path/collision/launcher topology.
The exact old full-header inverse and exact old-test inverse both pass; details
and actual logs are in /srv/tse-moving-neutral-hold-evidence-20261115.
