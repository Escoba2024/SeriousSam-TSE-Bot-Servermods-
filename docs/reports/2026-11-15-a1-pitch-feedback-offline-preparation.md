# Separate Original pitch feedback diagnostic — offline preparation

Status: disabled and awaiting Root source/freeze review. No native input, display,
Frida, build, installation or live action was executed by this worker. Historical
Mouse and Keyboard FAILs remain unchanged. A1/FirstState damage is still open.

The separate policy requests one normal +12 vertical-pixel detour, then chooses
only a −1 or +1 vertical-pixel correction from the latest actual paired Original
and server endpoint. It neither predicts a constant gain nor calls the existing
CP preparation/symmetric calibration. It requires an actual detour outside the
existing0.75° return boundary, at least one ACKed correction, strict actual progress
and fresh settled return on both peers. No Fire/Forward/respawn or second detour
is available. The only possible success is
`PASS_LIMITED_NATIVE_ACK_PITCH_FEEDBACK_RETURN_ONLY`; all qualification, gain,
exactly-once, shot and first-processed-state claims remain false.

## Sources and exact derivation

Parent: `/srv/tse-a1-xres-lifecycle-root-frozen-20261115`, manifest
`e9cb52a1135ea3046570fdaaac6e2f37ac2117535b8d4c312239f39d7cbec90c`.
This is the actual normal-Mouse parent, not the Keyboard transport/profile.

- `colt_preparation.py`, SHA256
  `0ad45ef707fb1d75e4bfee53af82d91b9b482e3e1abcca61f63cc51356070f59`:
  nested `observe` at188, `act` at277, `settled` at319 and `acknowledge` at334
  are copied with identical AST. Top-level geometry/live-state/baseline helpers
  are imported unchanged. No shared source is edited or globally monkeypatched.
- New orchestration retains the per-request actual ACK interval−0.5..−0.02,
  EPS0.001, opposite-axis/physical geometry checks,0.1s native stability,
  freshness0.2s/eight acquisition attempts, ACK2s/42 polls and0.05s polling.
  Direct pitch differences additionally require ordinary absolute agreement;
  they cannot use the inherited yaw-wrapping `same()` helper.
- A fixed20s active deadline shares the existing85s preparation and90s runner
  clocks. Each input reserves2.35s before the earliest deadline. Input0.1s,
  through-release0.35s,48 actions,96 native attempts and1024 observations/raw
  reads retain their bounds. Late favorable reads remain recorded failures.
- Generated controller preserves exact AST for normal `action_step`, paired
  reader/acquisition, own process/module identity, periodic resource/query
  guards, normal role/display close, archive and transaction restore functions.
  It retains the normal `X11Transport`/`Endpoint` and sealed Mouse/NoSmooth
  installation; it introduces no Keyboard mapping.
- Before journaling it retains the qualified same-transport
  `XTestQueryExtension`2.2 plus `XSync`, with explicit existing XNextRequest ABI.
  No warmup motion, resource getter or additional input is introduced.
- Actual attempt reserve/record methods and `XtstProxy` are reused unchanged.
  Every reserved/partial/rejected/accepted call remains in memory until normal
  cleanup writes separate0600/O_EXCL attempt/emission files. The unchanged
  counter guard rejects intervals larger than4. A journal error cannot qualify
  the result; the completion check binds each real call to its actual phase,
  pixels, counter interval, timing, ACK, normal closes and restore.

## TDD and verification

Only the new classes ran; the synthetic parent fixture was imported without
running its suite. Tests make no Xlib/native calls. Real captured RED outputs:
12 missing-policy failures,3 missing-journal failures,2 direct360°-alias failures,
and2 missing-builder failures. Root's alias finding was reproduced: the previous
new `same()` checks accepted wrapped360° differences and continued until another
gate failed. Only the two new direct-pitch checks changed to absolute comparison;
the copied CP ACK AST remains identical.

Final24/24 focused cases passed in2.234s. They cover asymmetric endpoint response,
real1-pixel return opportunity, plateau/reversal/missing ACK, identity/stale/reused
frames, extra-axis changes, late favorable reads, active/global/runner deadlines,
hold/reservation/action/attempt limits, actual fake-C invocation and first-counter
failures, primary exception preservation, rejected-row persistence and O_EXCL,
completion evidence mutations, builder gates, pins, immutable Core and inherited
controller ASTs. No native capability is inferred from these models.

One early command ran from the wrong directory and produced a test import error.
It is preserved in the tool transcript and excluded from RED/GREEN counts;
correct tools-directory outputs are separate private files.

Reproduce offline from `tools/`:

```sh
python3 -B -m unittest -v test_a1_pitch_feedback.FeedbackPolicyTests test_a1_pitch_feedback.FeedbackJournalTests test_prepare_a1_pitch_feedback.FeedbackPackageTests
```

## Disabled package and handoff

Final package `/srv/tse-a1-pitch-feedback-final-disabled-20261115`:

- Manifest `b03ce4cd17b428a7175939cb3ec57be53bcfcdb008376c1125908b45ec5abe3d`.
- Controller `d703e3467cbd10cb8f1ab72c93aedf5fcf75b48741a9477bd4585a8471e7b5f7`.
- All106 runtime,88 diagnostic and14 collector pins freshly match. Four Core
  files are byte-identical. Main plus all six instrumentation code gates are
  false; collector manifest `runtime_reviewed` is also false.
- `pitch-feedback-source.diff` and `PITCH-FEEDBACK-HANDOFF.json` accompany the
  full package. The earlier disabled checkpoint was preserved unchanged.

Private evidence directory `/srv/tse-a1-pitch-feedback-evidence-20261115` contains
real RED/GREEN logs, parent/fixture/source/AST/Core pins and author receipt
`offline-final-receipt.json`, SHA256
`faddeed5aba1c8f4754d16495cd2bdc34a0414594b008c0079c6b2790119c408`.
Final focused log SHA256
`b097236c8e4101bdce1f54a40fb811c91fccf494ff575a7fdb3ddce715e94841`.
This is author offline verification, not independent review or runtime evidence.

Root alone integrates, reviews/freezes and executes any subsequent single native
case after normal backup/preflight. Nothing is scheduled by this worker. A return
within0.75° would establish only bounded pitch-feedback usability at actual paired
endpoints; it cannot establish repeatable gain, exactly-once input, general aiming,
bullet collision or first-state damage.
