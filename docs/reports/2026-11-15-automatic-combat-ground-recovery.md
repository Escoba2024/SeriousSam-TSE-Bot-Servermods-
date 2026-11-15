# Separate automatic combat ground recovery: offline result

The source mechanism is implemented and portably verified. Ordinary automatic
visible combat can now opt into the existing bounded ground-progress recovery
without acquiring Supply/Nav ownership. This is unbuilt source, not a Retail
escape, Sync result or causal explanation of the native026 Skulls episode.

`BotDriver.cpp:1550` passes the actual final ownership and the production request
helper separately. `BotSupplyNative.h:2209` admits automatic human-policy visible
combat only when Supply is inactive, forward/strafe are finite and nonneutral,
and up is exactly zero. The new SafeMotion argument defaults false. Ordinary
nonstalled combat retains its normal speed.

`BotSupplyNative.h:1013` records combat-only metadata after the existing validated
support branch, without an extra cast. The pin binds player/world/map, entity and
generation, validated reference+ID, StandOn, gravity and the same native tick.
Each SupplyTick invalidates it. Fresh validation at2220 denies missing, negative
map, changed, dead, stale, nonfinite or unknown identities; a retained reference
is resolved through the current world before dereference and its current ID is
checked. Support, movement and observation remain three separately required
same-tick stamps. Observation alone is not support authority.

SafeMotion at2312 keeps the existing recoveryContext and all physical checks.
Only an actual2s stationary episode or its still-eligible fixed escape obtains
the existing0.3 recovery bound. The0.25s observation gap,0.25m progress threshold,
0.6s hold, ordinary0.5 floor-normal policy, exact native-contact exception,
ray/strafe/pit/cooldown/deadline bounds remain unchanged. Context or owner changes
reset the combat episode. Combat cannot mark Nav hints Tried/rejected, alter goal
selection or claim FlightAccepted; rejectOriginal is explicitly useReacquire-gated.

The only productive addition inside Reacquire is explicitly identified and
inverted separately from passive diagnostics by the historical source proof.
Its restored body still hashes to
`88950482f46137a5af41a6214451221855be8aa5c4c41ac25f443ddea06493df`;
the deliberate height-guard mutation is still rejected. `cecil_motion.h` is
byte-identical to the baseline
`a32870d3a4d47c95f927e25d1b3bb881de8297f9245dedb632c56069cda88e09`.

## Actual focused verification

- Initial behavioral RED:3544 checks,2 failures: missing automatic-combat escape
  and missing actual Driver request helper. Existing ownership checks remained.
- First normal GREEN:3659 checks,0 failures; retained as its own checkpoint.
- Review RED:4 focused checks,3 failures for negative map serial already before
  actual Capture and independently inside Fresh. Combat-only correction:4/0.
- Final full relevant normal Bridge:3663 checks,0 failures,7.267s. This includes
 122 new assertions beyond the previous3541-check reproducer baseline. Cases cover
  actual trigger combinations, normal speed, caps/budgets, death/entity/generation/
  map/world/reference/contact/gravity changes, stale/nonfinite stamps, no intent,
  direction hold, owner changes and exact Nav/flight nonauthority.
- The existing ActionNative caller regression ran once with its unchanged
  ASan/UBSan default under Root's explicit exception:PASS1.171s. It compiles the
  actual final Driver call and production request helper with the necessary
  ten-argument stub. No Bridge sanitizer or parent repeat series was run.

Commands are the existing `test_cecil_native_bridge.py` with `--support-dir` and
the pinned SDK107 `--sdk-player`, and `test_cecil_action_native.py` with the
actual `--driver` and same SDK. The focused map runner changes only the fixture's
test-main selection and compiles the same production extraction; no new CLI.
Private0600 logs, runner, exact commands/hashes and source pins are retained under
`/srv/tse-automatic-combat-recovery-evidence-20261115/offline-final-receipt.json`.

Root alone reviews/integrates and may build a new candidate. No Retail DLL,
Original process, live configuration, diagnostic patch, RNG or navigation-core
change was made. Native effectiveness, performance and Sync remain untested.
