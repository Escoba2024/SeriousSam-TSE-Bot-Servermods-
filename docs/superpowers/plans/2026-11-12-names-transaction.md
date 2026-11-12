# Names-only transaction completion plan

> For agentic workers: execute inline with superpowers:executing-plans; root owns independent review and all native operations.

**Goal:** Finish an offline-tested, fail-closed names-only transaction and recovery implementation.
**Architecture:** Preserve existing 48-slot assignments and byte planner. Extract the private controller into a configurable generic backend, with a disabled private entry point and frozen dependency closure.
**Tech Stack:** Python 3 standard library, Linux flock/fsync, caller-supplied systemd/native adapter.
**Spec:** Existing A2 request and private prepared transaction; public scope is 48 stable identities and exactly 51 name-only writes. Runtime authorization remains separate.

## Global constraints

No live operations by the implementation agent. No DLL or Dedicated-server mutation. Preserve old worktrees. No private paths, GUIDs or raw evidence in distributable files. Unknown players remain untouched.

## Review focus

- Interrupted start: accept only journaled native generation or exact durable service invocation; never infer ownership from a new PID.
- Journal/storage failure: do not hide either exception; fail before unjournaled mutation, retain recoverable state.
- Recovery replay: validate exact backup/path/state scope; retain every closed log, including failing candidates.
- Red startup: bypass rotation during rollback restart, verify old identities, then restore original launchers.
- Stage/dependency drift: independently regenerate 51 payloads, validate complete manifest and exact lock order.

## Task 1: transaction and durable filesystem boundary

- [x] Copy existing WIP unchanged; add regression tests for journal failure and path/metadata behavior, observe RED.
- [x] Implement minimal durable journaling/rollback changes, observe GREEN.

## Task 2: guarded backend and recovery

- [x] Extract configurable backend and preserve known behavior; tests use real temporary files and simulated external service primitives only.
- [x] RED then GREEN: interrupted identity capture, changed invocation/PID, malformed recovery scope, archive replay/failure and Red rollback.
- [x] Validate exact staged payloads, source closure and fixed locks with boundary tests.

## Task 3: verification and root handoff

- [x] Run focused suites; document the corrected fixture error and the final full-suite rerun deferred for the root native resource window.
- [x] Commit generic source/tests/docs. Prepare disabled private entry, full dependency hashes and precise review/recovery instructions.
- [x] Report commit and limits to root for independent review; no runtime claim.

## Final ruling

The root agent requested no heavy compile/IO work while the native comparison ran. The final 64-test low-IO batch and the last backend guard regression passed. The current full 80-test replay is explicitly left to root after that window; no native acceptance is claimed.

## Bounded independent-review fixes

- [x] Reproduce and fix same-name replacement-generation acceptance in both final verification methods.
- [x] Reproduce and fix missing complete new-client log-error gating; retain the existing rollback path.
- [x] Persist exact Dedicated prefix/inode/generation baselines; retain historical events, reject new sync events, cross-boundary markers, rewrites, truncation and rotation.
- [x] Preserve closed-log acceptance classes via one shared scanner with byte-boundary tests.
- [x] Add the missing original graceful helper to the private bootstrap closure and validate its wrapper pin before the first stop.
- [x] Run the complete current focused suite after the native window: 89/89 passed in 125.552 seconds. Offline private closure regression and package check passed; runtime gate remains false.

The initial full-suite deferral above is now resolved. No native action was executed by this worker.
