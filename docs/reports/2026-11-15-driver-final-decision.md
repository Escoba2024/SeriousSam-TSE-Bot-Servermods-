# Passive Driver final-decision source checkpoint

Status: portable source tests passed; no Windows build or Retail execution.
This closes only the diagnostic source task. It does not explain a particular
027 life, qualify navigation/recovery, or prove movement, firing, pickup or ACK.

Base fce7f1c80264bacd5d445ad0c3d5b83999c3b3c9 contains built028's passive
contention Header. `BotSupplyNative.h` remains byte-identical, SHA256
72cea9c22d1a781bac8e1b733f63c22368f4cee8e0f3c3677067e571af8040bd.
The full Driver inverse restores
ebb2c4cc694ebdc1ee8f9e2e1aa88a2cb587afae5adc649bfcae84ff244c6c55.
The initial source slice is47d81bf; the subsequent four-fact correction is
separately committed with its own RED/GREEN evidence. The initial report
commit contains no code change.

The new production-used pure header `driver_final_decision.h` holds one stack
scalar receipt. A new CecilDriverFinalV1 row follows the existing SetAction
only when diagnostics and supply navigation are enabled and the same existing
local tick modulo20 opportunity is reached. The old CecilState output and
Diag0 logging cadence are untouched. Early rejection/continue paths do not
reach the row and remain unobserved here, with their old rejection logs intact.

The row binds an invocation within an externally pinned process/log epoch using
local/tick/actor/entry-generation. Entry/exit generation or recorded actor
disagreement yields life_link0=UNKNOWN. Life_link1 means only those source
identities agree through submission, not alive/native-first-state proof.
`baseline_map_pin` is the cached rotation baseline; `map_known=0` is always
literal. No new current-map read was added, and generation equality never
establishes map stability. Existing Candidate.entity remains the ITEM ID;
unmatched selection calls must not be joined to another tick's final row.

All captures are copies of existing values/evaluations. The weapons-presence
pass-through remains at the old lazy pointer condition. Wanted/current and
combat-recovery pass-throughs return the same typed argument once, in the same
argument position; they do not add another Getter/Poll/Resolve/helper call or
prescribe a new inter-argument order. The complete original boolean expression
is recovered by the exact inverse. No new rays, entity queries, atomic serial
reads, RNG, visibility tests or clocks were introduced.

## Compact version1 schema

- Identity: local/tick/actor, entry+exit generation, exit actor, baseline map
  pin, literal map-known0, source-life link (0 UNKNOWN,1 agreeing source pins).
- pre_supply: actual pre-supply decision bits and cached target INDEX. Defined
  pre bits0/1/2/3/5/6/7 mean automatic/humanMode/combatDeathmatch/targetVisible/
  combatHold/testAimReady/humanFire, copied BEFORE the supply block. Other pre
  bit positions are undefined, not a final-fire claim. Target is cached
  bs_iCombatTarget in automatic mode, otherwise configured bot_iTestTarget;
  it is not a fresh target-entity lookup or existence proof.
- Supply tuple: block entered, native ready result, supply call observed,
  complete proposal available, proposal bitmask,
  itemKind, flags, buttons, forward/strafe/up/yaw-delta/pitch-delta. Bitmask0..7:
  active, ownsMovement, itemGoal, urgent, followGoal, useControl, flightGoal,
  activeFlight. Valid means copied, not physically authorized.
- wp: old short-circuit weapon-pointer read evaluated, actual nonnull result.
  post_mode bits0..9, copied after SetAction: automatic, humanMode, combatDeathmatch, targetVisible,
  supplyActive, combatHold, testAimReady, humanFire, bFire, cecilUseControl.
- arb: post-supply-arbitration forward/strafe/up and cumulative requested
  heading/pitch followed by actual cecilFlags, before later strafe
  scaling/clamps/safety.
- weapon: selection Poll called, travelKnife, pre-resolve combat weapon,
  final weapon, selection-Poll wanted, fire-Poll called, its current/wanted,
  selection-Poll actual lastButtons argument, combatSelect and final
  cecilButtons. LastButtons uses the same single-evaluation pass-through as
  wanted/current; no second field read. Knife1/Colt2 retain actual enum meanings.
- safe: called, actual useReacquire/combatRecoveryRequested, return status,
  actual existing source-local now, entry forward/strafe/up/finalYaw/maxStrafe,
  then returned forward/strafe/up. Called0 makes the remaining values unknown;
  no old state.probe is copied as fresh evidence.
- submitted/action/rot/view/buttons: exact action argument after composer and
  SetAction. This is source submission, not internal created-time, network ACK,
  Engine action, damage or successful recovery. All three view axes are kept.

All28 floating fields use %.17g. An independent token-width calculation gives
1394 bytes including NUL; compiled negative IEEE Double-max, unsigned-max,
signed-min and all-presence flags produce1207 bytes before NUL, below2048.
Neighboring Double-values have a genuine RED under %.9g then GREEN under %.17g.
Caller only logs complete positive-length output smaller than the2048 buffer.
There is at most one NEW row per admitted20-tick opportunity; no extra Diag0
log. Stack initialization, formatting and log I/O have real unmeasured native
cost. No hard600s total bytes/rate or zero-overhead claim is made.

## Verification and limits

Reproduction from the repository root:

```sh
PYTHONPATH=tools python3 -m unittest tools.test_driver_final_decision tools.test_driver_final_wiring tools.test_driver_final_source tools.test_contention_diag_source -v
python3 poc/candidates/redstation-supply-20261107/test_cecil_action_native.py --sdk-player /path/to/qualified-sdk/Sources/EntitiesMP/Player.es
```

Nine focused Python tests PASS0.335s after the four-fact correction. The wiring test compiles actual extracted
Driver supply, selection-Poll, fire-Poll, SafeMotion-call and post-SetAction
fragments with SDK-shaped stubs. Seven conditions run with diag0 and diag1:
visible ordinary fight, no-visible supply, urgent weapon, traversal, not-ready,
missing weapons and reset-inside-supply. Each pair compares28 action/state/call
values exactly; ready/supply/Getter/Poll/Resolve/Travel/Safety counts are asserted.
These portable stubs are not an ABI/retail simulation qualification.

Twelve explicitly enumerated changed fragments reconstruct the ENTIRE Driver028
byte string; no diagnostic-line stripping or whitespace normalization. Eight
initial Driver mutations, plus four missing-fact mutations, including urgency, SafeMotion ownership, final buttons, Poll,
diagnostic gate, truncation guard and life reset, fail verification. The .5
ordinary-normal Header mutation also fails the unchanged Header pin. Existing
contention inverse and its seven negative cases remain, and its formats remain
bounded1742/1898 including NUL. The old unchanged-Driver assertion now uses the
exact full inverse instead of accepting a newly changed Driver hash.

Before Root's four-fact review correction, the existing action-native test ran
once with its unchanged ASan/UBSan default: PASS; SDK Player.es SHA256
85c92933fa5b0cc726be7b42a3bc82d4c95b255507ec8b1fffe2666fcf3888af.
Its only fixture addition is the actual pure header and a neutral receipt;
previous behavioral conditions/assertions remain unchanged. No bridge repeat.

Actual RED/GREEN logs are private. The initial wiring GREEN attempt failed
because its fixture omitted Settings definition and cecilFloorStatus; this
compile failure is retained, with only those fixture defects corrected. The
old direct-Driver-hash RED is retained. No failed native result was reclassified.

Root's review found four missing metadata facts in the initial source: actual
Poll lastButtons, post-arbitration flags, pre-supply mode/cached target, and
block-entered versus not-ready distinction. A new targeted test produced four
actual missing-binding failures and the pure-header fixture failed for missing
fields before the minimal correction. Current tests compile the actual new
pre-supply statements, assert the original lastButtons reaching Poll once,
compare pre-mode versus post-state and assert block/ready/called distinctions.
The prior receipt/report and passing pre-fix ASan evidence are not relabeled as
final-code verification. No bridge or ASan repeat was made for scalar metadata.

No new runtime/controller package was generated or enabled. Master switch and
diagnostics defaults remain false; Root alone may build and qualify a new
candidate. The existing source-overlay builder already includes ordinary .h
files, so the new pure header follows the established source closure.
