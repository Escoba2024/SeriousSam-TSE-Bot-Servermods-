# Native009 repeat UP on the bound Red Station approach

Native009 applied the intended first-action suppression, but a subsequent ordinary UP pulse escaped during a brief loss of reference on the same8→12 edge. The completed120.0395-second diagnostic had four normally closed roles, no reported errors or bad-sync/disconnect messages. The original-server hook observed46 calls, all on other pads, and zero calls for234 over its entire120037.5ms gameplay window overlap. There were no dropped records, faults or unmatched players; detach and original function-body restoration completed. This is evidence of an unsuccessful approach, not a Bouncer or milestone acceptance.

The [sanitized receipt](2026-11-11-native009-bouncer-repeat-up.json) retains the exact15 action samples and private artifact hashes. The gameplay candidate009 SHA256 was `0146cfeef95b532d7050672963d58d4542ac21ad2a8a957c5810db46970d74eb`; the earlier inert bootstrap used048. In botA local2/generation5:

| Tick | Actual context | Requested UP / final action Y |
|---|---|---|
|1368|Source8→hop12, STAND, support54|1 / 0:009 suppression applied|
|1373|Same edge, STAND, support0, y24.123377, vertical velocity−1.886465|1 / 11:repeat pulse escaped|
|1374|Support193, y24.007467, vertical velocity−2.318191|0 / 0|
|1375|Support0, y24.722467, vertical velocity14.299999|0 / 0:actual ordinary upward departure|
|1378|Same edge, STAND, support0|1 / 11:another repeat pulse|
|1381|Existing radius arrival advances12→34 at y27.437468, support0|0 / 0|

Client action generation and server processing are different observation points. The record does not prove a particular action packet's processing instruction or the exact moment of support acquisition. It does prove that the previous rule allowed positive ordinary UP during the same STAND approach, and that contact/upward departure followed. No234 call occurred. The correction removes these requests; it does not remove any Engine support test.

## Original1.07 cross-check

Original `EntitiesMP.dll` SHA256 `7f595f2a7fc96a978b3467983e8f17c70d827f17a5f4ee887f9c7a1f20b1d350` at preferred base60310000:

- `603ffbf9..603ffc37` checks reference+11c, resets or increments fall time+3c8, and rearms player JUMPALLOWED bit4 when requested UP is below0.1. A missing reference does not immediately imply FALL; the following fall-time comparison selects the state.
- `6040031b..60400347` suppresses positive UP when JUMPALLOWED is absent and calls imported SetDesiredTranslation through IAT6048b5a8 (PE import table independently resolved to Engine.dll `?SetDesiredTranslation@CMovableEntity@@QAEXABV?$Vector@M$02@@@Z`). This block does not require a current reference.

Original `Engine.dll` SHA256 `b79bf8bb3927fe4f8f252e141d721ae5c738df02218f0ecc12da5c1afbcb534f`, SetDesiredTranslation export RVA157f60/preferredVA60217f60 through60217fa6, copies the three requested components into entity+ec without a support test and enrolls the mover. This proves that absence of reference at action generation is not a general guarantee that an ordinary UP request will be discarded. It does not imply that the physical jump implementation lacks its own contact rules. SDK Player.es3989–4030 and4226–4231 corroborates the inspected original instructions; SDK semantics alone are not substituted for Retail evidence.

## Bounded010 change and replay

The existing exact world path/worldCRCff3776e0/NAVCRCe4571656/metadata/serial binding remains unchanged. So do the actual source8/hop12, flags42, live identity, default gravity, valid frame/velocity, STAND/CROUCH and unblocked-edge requirements. The only extension permits the same positive-UP suppression when the reference is null. A present reference still must be an undeleted, immovable brush in the same world. FALL, SWIM, DIVE, other maps and edges11→12/12→34 remain unchanged. No support, velocity, placement, deadline, radius, topology or navigator state is written; no casts, lookups, selection or RNG are added. Raw capture still occurs before output suppression. This grants no new ground or air movement authority.

The real navigator Update → RawCapture → approach-helper replay uses all15 recorded positions/velocities/references with Retail FLOAT timestamp multiplication. It is a replay of observed inputs, not a physics simulator or prediction of010 positions. The general portable timer stub is double, so this focused replay explicitly supplies original FLOAT times to avoid shifting the recurring pulse tick. With009 code, five behavioral checks fail: both unsupported repeat pulses under diagnostics off/on and the direct passive-output check. After the focused conditional change, the replay also retains the original high-radius arrival and identical goal/deadline/RNG, flags and later edge. Existing real BotSupplyTick first-transition, lifecycle/binding, invalid reference, other-edge and jump-clock regressions remain included; unsupported FALL/liquid counterexamples were added.

Native010 effect remains open. An unchanged radius decision could still turn before actual pad contact; no speculative radius correction is included. There is no new general A-PASS or first-state damage proof.

Verification: `python3 poc/candidates/redstation-supply-20261107/test_cecil_native_bridge.py --sanitize --sdk-player /srv/tse-sdk-20261021/Sources/EntitiesMP/Player.es` passed 1779 checks with zero failures under ASan/UBSan. The final corrected regression against009 produced exactly five behavioral failures; initial timer/anchor fixture mistakes were corrected before these final receipts. Independent read-only review found no Important/Critical issue. Windows build and native010 remain Root-owned pending gates.
