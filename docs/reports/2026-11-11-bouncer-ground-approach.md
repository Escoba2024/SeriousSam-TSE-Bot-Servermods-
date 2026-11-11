# Bound the observed Red Station8→12 ordinary jump

Historical009 implementation report. The completed009 observation and narrowly extended010 condition are documented in [the repeat-UP follow-up](2026-11-11-native009-bouncer-repeat-up.md).

Native008 recorded two actual grounded8→12 actions with requested up1 and composed up11, followed immediately by loss of support and upward translation17.238. Both later advanced through the shifted-radius arrival high above Bouncer234 and missed its contact. The exact evidence and portable transition replay are in [the008 report](2026-11-11-native008-bouncer-actions.md).

This change suppresses only positive ordinary `move.up` on the actual navigator-selected source8/hop12. Raw diagnostics are captured first. The target flags42, radius4, directed topology, navigator state and jump cooldown remain untouched. No synthetic arrival, launch, velocity, support, entity write, selector, ray, lookup or simulation RNG is introduced. Existing Driver ownership and final movement safety checks remain in place.

The exception requires the existing loader to have successfully validated the exact original world path `Levels\LevelsMP\Deathmatch\RedStation.wld`, world content CRC`ff3776e0` and NAV content CRC`e4571656`. Cecil path hash`5af1a276` is not substituted for either content CRC. The bound graph must have193 points and exact original IDs, coordinates, radii, flags, important/next/lock metadata and complete link lists for8 and12. The loader revokes the binding under its hooks lock before reloading and publishes it under that lock only after existing file/parse checks succeed. Failed/disabled loads leave it revoked. StopGame's existing Ready=false or serial increment immediately makes the prior record unusable; the loader replaces it on the next serial/map/enable transition.

At use time the exception additionally requires current Ready/enabled flags and matching map serial, unchanged node metadata, a valid active unstuck/unrelocated8→12 edge, unlocked endpoints, live matching player identity, finite valid body/position/view/gravity/velocity, default downward gravity, ground state STAND or CROUCH, and an already present undeleted static brush reference in the same world. Missing support, airborne/liquid state, a moving/model/foreign/deleted support or invalid context retains the original action. This consumes existing support evidence; it grants no ground authority from proximity or an absent reference.

The sole mutation is `move.up=0`.11→12,12→34, unrelated jump outputs, other maps and airborne movement remain unchanged. Native effect is not yet known: unchanged radius arrival may still turn the bot before actual pad contact. That is a separate next-run discriminator, not an implemented additional fix or a claimed successful pickup.

## Verification

The focused real bridge replay of both008 first-transition positions produced two RED failures with the bounded helper still a no-op, then passed after the single Up assignment. Tests cover both supported first transitions, preserved raw requested jump, flags/radius/goal/deadline/RNG, missing/deleted/moving/foreign/model support, ground/air/liquid/invalid player contexts, changed serial/Ready/enable, invalid metadata/links/bounds, rejected world path/content CRCs, failed/disabled publication,11→12 and12→34 unchanged, diagnostics on/off parity and identical subsequent navigator jump cooldown. The observer and existing bridge regressions are included. No runtime has been started for this candidate by this agent.

Validation: `python3 poc/candidates/redstation-supply-20261107/test_cecil_native_bridge.py --sanitize` passed1676 checks with zero failures under ASan/UBSan. Root still owns Windows build, independent review and native009 qualification.
