# Original Pitch Feedback Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:executing-plans and test-driven-development. Root performs the independent integration/freeze review and is the only native executor; no delegation.

**Goal:** Prepare one disabled, bounded normal Mouse-Pitch feedback diagnostic, preserving every historical calibration FAIL.

**Architecture:** New pure policy reuses the frozen Mouseparent's actual Observe/Act/Settled/ACK closures with exact AST provenance. A separate builder copies that full parent into a fresh disabled package and wires only normal X11Transport/Endpoint plus bounded in-memory emission journaling; no shared helper or Core modification.

**Tech Stack:** Python standard library; existing pure Colt geometry and normal XTest transport. Tests supply synthetic frames/fake C functions only, never native calls.

**Spec:** `docs/superpowers/specs/2026-11-15-a1-closed-loop-original-input.md`.

## Global Constraints

- Claim only NEW `tools/a1_pitch_feedback.py`, `test_a1_pitch_feedback.py`, `prepare_a1_pitch_feedback.py`, `test_prepare_a1_pitch_feedback.py`, own plan/report/private evidence. Existing helpers and four Core files unchanged.
- Parent `/srv/tse-a1-xres-lifecycle-root-frozen-20261115`, manifest `e9cb52a1135ea3046570fdaaac6e2f37ac2117535b8d4c312239f39d7cbec90c`. No KeyboardTransport or keyboard profile mapping.
- First +12 vertical pixels, then only ±1 vertical pixel chosen from actual connected Original/server pitch; vanilla only, each 0.1 s, no Fire/Forward/aim/respawn or extra detour.
- At least one ACKed 1-pixel correction; final return within existing 0.75° on both actual peers. No gain symmetry or fixed gain prediction; per-request existing [-0.5,-0.02] bound, EPS .001 and physical/source ACK unchanged.
- Maximum48 actions/96 attempts/1024 observations and raw reads; paired freshness .2 s/eight acquisition attempts; through-release .35 s; ACK2 s/42 polls/.05 s; native stability .1 s; active20/shared85/runner90 seconds.
- Reserve2.35 seconds before earliest deadline before any input; preserve clocks and hard deadlines after slow reads. No 48×2s minimum opportunity or time reset.
- All instrumentation gates and main gate False; no Frida/RECORD/XRes arm, no Native/runtime/display/compiler/install. Stop all tests/builders on Root STATICONLY.
- Every attempted native emission retained privately0600/O_EXCL even on rejection; sticky failures, normal closes, complete restore and actual metadatasource pins required. All qualification/shot/FirstState/exactly-once/gain claims False.

## Review Focus

- Sparse native samples must not become repeated or synthetic ACKs; retain failed read attempts and genuine successful indices.
- A late read after a deadline must FAIL even if its angle is favorable; all active/global/runner clocks share the original start.
- A zero-sized detour within .75 must not falsely qualify unexercised 1-pixel feedback.
- Metadata failures must remain FAIL and retained; no successful phase may stand in for missing actual native emission metadata.
- Copied nested helpers must retain exact semantics; no old CP.run_preparation dispatch or dynamic monkeypatching.

## Task 1: Pure feedback policy and actual ACK invariants

**Files:** Create `tools/a1_pitch_feedback.py`, `tools/test_a1_pitch_feedback.py`.

**Interfaces:** `FeedbackScope.admit(role,control,seconds,pixels)` enforces fixed initial +12 then ±1 and48 actions. `run(read_roles,step,clock,sleep,receipt,*,started,runner_deadline)` returns a limited feedback-return receipt or raises with sticky FAIL. `journal_complete(report,verdict)` validates actual phase/emission evidence and normal cleanup without conferring A1 qualification.

- [x] Write model tests for asymmetric initial +12 response followed by actual1-pixel return, unchanged peer/geometry, no fixed opposite impulse and no Fire.
- [x] Execute the named new class only, preserve its actual missing-policy RED output0600; do not import or run an existing parent test class as a suite.
- [x] Implement the smallest pure policy, reusing unchanged Observe/Act/Settled/ACK closures (record exact parent hashes and AST comparisons); own orchestration and clock/reservation checks are explicit.
- [x] Targeted RED→GREEN for plateau/reverse/new identity/stale or missing ACK, malformed/reused frames, .2/.35/2/20/85/90 deadlines, late favorable reads,48/96 limits, no actual correction and failed raw metadata.
- [x] Run `python3 -m unittest -v test_a1_pitch_feedback.FeedbackPolicyTests` from tools, compare outputs with expected PASS, preserve real logs/hashes. Commit new policy/tests plus plan status.

Expected: synthetic valid case returns only `PASS_LIMITED_NATIVE_ACK_PITCH_FEEDBACK_RETURN_ONLY`; all malformed/deadline cases stop without further inputs, no native side effects.

## Task 2: Disabled Mouseparent controller, journals and pins

**Files:** Create `tools/prepare_a1_pitch_feedback.py`, `tools/test_prepare_a1_pitch_feedback.py`; own report.

**Interfaces:** `transform(parent_text)` yields a strictly gated new controller; `prepare(fresh_destination)` validates original parent, copies it, wires normal mouse feedback and writes fresh manifest/diff/handoff. Journaling uses existing strict reserve/record methods, preserves all attempted calls0600 and validates real phase/counter/timing metadata through Task1 journal_complete().

- [x] Write tests that fail on missing builder: fresh destination, all false gates/manifests, normal transport/no keyboard mapping, no worker/recorder/old CP preparation entry, unchanged action/reader/identity/close/restore ASTs and four Core bytes.
- [x] Run targeted builder class RED, preserve output. Implement narrow copy/retarget; never overwrite an old package. Explicit native-counter ABI declarations are metadata only; XTestQueryExtension/XSync stay outside active input journaling, no warmup input.
- [x] Test actual fake-C emission flow: accepted/rejected attempts, pre-counter/reservation failure with no new motion,96→97 refusal, cleanup persistence and sticky errors. Test journal_complete() rejects missing/cross-phase calls/counters/release timing/ACKs/restore.
- [x] Run only the two named new test classes; generate one fresh disabled package, verify every runtime/diagnostic/collector pin, four Core bytes and inherited ASTs. Record exact source hashes, not native qualification.
- [x] Commit builder/tests/report and final plan status. Deliver root-reviewable full diff, package and private immutable RED/GREEN receipts; all jobs stopped before Root native work.

Expected: disabled package generation and pure/fake-C tests PASS; native/runtime flags remain False. Root decides integration/freeze and exactly one later native diagnostic after review/backup.

## Initial rulings and coordination

- Root explicitly permits only focused tests and forbids broad discovery, native calls, builds and extra agents; this overrides generic skill setup/suite/delegation suggestions.
- Existing test fixture `test_colt_preparation.py` is private in the frozen Mouseparent, not a public tools file; use only its synthetic fixture class with its exact source hash, never its parent suite or runtime entry.
- Task2 consumes Task1 run/complete interfaces and independent actual journal rows. No metadata-only success is allowed to qualify the pure model or vice versa.

## Offline completion — 15 November 2026

- Plan732329c preceded production. Pure policy a088c82; journal/strict nonwrapped pitch correction5946794; disabled builder and focused fake-C evidence d1d4bca.
- Actual RED logs: missing policy12 failures; missing journal3 failures; Root-discovered360° alias2 failures; missing builder2 failures. All retained0600, with hashes in the private author receipt.
- Final only-new focused run24/24PASS2.234s. This includes exact copied helper ASTs, unchanged controller reader/identity/action/close/restore ASTs, false main/six instrumentation gates and collector manifest, all package pins and Core byte equality. No native/API/input execution took place.
- Fresh final `/srv/tse-a1-pitch-feedback-final-disabled-20261115`, manifest `b03ce4cd17b428a7175939cb3ec57be53bcfcdb008376c1125908b45ec5abe3d`,106 runtime/88 diagnostic/14 collector pins. Earlier disabled checkpoint remains untouched.
- Private receipt `/srv/tse-a1-pitch-feedback-evidence-20261115/offline-final-receipt.json`, SHA256 `faddeed5aba1c8f4754d16495cd2bdc34a0414594b008c0079c6b2790119c408`.
- Root source/freeze review and any subsequent native diagnostic are PENDING; gain, A1, Fire, exactly-once and FirstState remain UNPROVEN. No automatic runtime or retry is scheduled by this worker.
- Initial Task1 wrong-CWD invocation produced import failure (tool transcript only). It is not counted as a source RED; corrected tools-CWD runs are separately logged. No unsuccessful historical native result was changed.
