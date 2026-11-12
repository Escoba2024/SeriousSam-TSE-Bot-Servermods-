# A1 Input Diagnostics Implementation Plan

> **For agentic workers:** Use superpowers:executing-plans task by task.

**Goal:** Preserve failed calibration evidence and distinguish requested, locally consumed, server-received and body/view rotation in an opt-in passive diagnostic.

**Architecture:** Keep the default inventory path unchanged; add explicit optional scalar fields and guards. A separately pinned, disabled private controller consumes paired samples and ends with review required after the calibration pair.

**Tech Stack:** Python 3.12, unittest, existing read-only Retail reader and guarded X11 controller.

**Spec:** docs/superpowers/specs/2026-11-12-a1-input-diagnostics.md

## Global Constraints

- Isolated branch codex/20261112-a1-input-diagnostics; base b6b776dd.
- No runtime, builds, hooks, memory writes or modifications outside the claimed worktree/new private draft.
- Gain/return tolerances and host/identity/restore gates unchanged.
- Runtime review gate false; shot/hit/first-state claims false.

## Review Focus

- Nonfinite or changing diagnostic fields must fail the full two-pass read.
- Default mode must retain exact read sequence and decoded bytes.
- Stale or mismatched client/server acknowledgements must not become calibration success.
- Smoothing may produce multiple partial increments; unexplained extra or reversed response must stop.
- Failed input/settling must retain bounded receipts before exception propagation.

### Task 1: Native failure receipt and optional reader

Files: tools/retail_inventory_readonly.py; tools/test_retail_inventory_rotation.py; private test_calibration_failure_receipt.py.

- [x] Reproduce old empty failure receipt (RED) from native endpoint angles.
- [x] Add reader mode/negative/default compatibility tests and observe RED.
- [x] Implement optional rotation_diagnostics=False API, fingerprints and finite scalar decode.
- [x] Run reader tests, preserve RED/GREEN logs.

### Task 2: Private input diagnostic and controller wiring

Files: private rotation_diagnostics.py, shooter_policy.py, run_dual.py and tests; disabled source-manifest.json.

- [x] Add failure-receipt, no-ack, delayed-server, view-rest, extra-input, smoothing and lifecycle tests; observe RED.
- [x] Implement bounded paired observations and record all evidence before validation/failure.
- [x] Wire own Vanilla reader and actual emission times into existing guarded lifecycle; retain cleanup/restore.
- [x] Run private suite and inspect normalized lifecycle diff.

### Task 3: Verification and handoff

- [x] Run offline tools unittest suite when Root native window is free, excluding the g++-invoking test_arena_combat.py under the no-compile scope.
- [x] Re-pin private package, test disabled gate, validate dependency hashes.
- [x] Write sanitized report and Root run plan; commit claimed repo files.

## Execution ledger

- Setup: clean isolated worktree and base verified; Root owns native runtime.
- Ruling: cloud skill helper scripts are not installed on the remote device; this persistent plan is the task ledger instead.
- Ruling: diagnostic draft ends after the input pair with review required; unknown consumption never promotes route/fire.
- Pre-flight: private paired observer consumes the reader optional fields; default callers keep unchanged schema/read sequence.

- RED: native 045050 angles reproduce the old empty failure receipt; the same original rejection now retains all endpoints.
- RED/GREEN: reader opt-in guards/finite values/two-pass drift and exact default golden; 32 reader tests passed.
- RED/GREEN: fresh paired input acknowledgements, both client/server view rest, counter mismatch, pre-emission drift and partial failure receipts. Actual controller sampling body tested offline.
- Verification: final private suite 95/95; repository Python suite 262/262 with compiler module explicitly excluded. Initial broad run used the wrong working directory and failed one import; corrected invocation passed, both logs retained.
- Integrity: seven optional Retail byteguards checked against the exact original DLL; six lifecycle/transport files byte-identical and 17 critical controller functions AST-identical to the frozen parent.
- Package: /srv/tse-a1-input-diagnostics-completion-20261112; 46 runtime pins, 37 own source/config/test pins; both runtime review gates false. No runtime performed.
- Handoff: docs/reports/2026-11-12-a1-input-diagnostics.md and the private README provide findings and the Root-only run plan. Root must independently review/freeze before any native use. A1 acceptance and the input factor-two cause remain open.
