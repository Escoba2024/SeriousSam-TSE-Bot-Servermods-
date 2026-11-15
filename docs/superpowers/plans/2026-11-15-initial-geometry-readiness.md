# Initial geometry readiness implementation plan

> **For agentic workers:** Use superpowers:executing-plans and superpowers:test-driven-development. Root owns integration and every runtime action.

**Goal:** Before the first valid geometry pair only, discard exactly a bound client null-animator error as PENDING within the existing .2 s / 8-attempt acquisition. No accepted null snapshot.

**Architecture:** A new pure classifier and exact-whole-source Runner transform; no reader/core changes. Derive only from the existing client EvidenceError and read_rotation_pair FAIL receipt plus already pinned mapping/identities. Server and client pointers occupy different address spaces and are never equated. New condition explicitly changes initial readiness/retry behavior. No cause of null startup state is asserted.

**Claim:** tools/first_state_initial_geometry_patch.py, tools/test_first_state_initial_geometry_patch.py, this plan and a new report; private /srv/tse-initial-geometry-readiness-evidence-20261115. No package/Frozen/Root/runtime writes.

## Contract

- Exact parent: QJS10 V3 disabled run_dual.py; preserve entire inverse.
- Only EvidenceError at client snapshot, receipt FAIL + complete server_snapshot, no vanilla_snapshot/pair. Same server PID/start as records. Server roster exactly mapping with pinned entity_ids; selected slot belongs to this roster. Error raw animator exactly zero; all parsed slot/id/pointers/tick canonical and finite. Error tick is a separate client game clock, never compared as equal to server game clock.
- Validate existing client-reader identity equals its recorded pin, without another read. Invalid/misaligned nonzero animator, bad slot/entity/server identity, missing receipt or any other failure remain fatal.
- Exception only while rotation_samples is empty, never after the first valid pair. Raw failed receipt retained in existing finally journal. Explicit pending counter/status; ordinary successful frame processing unchanged.
- read_rotation_pair and native_rotation_pair are byte-identical, including .2/8 bounds, freshness, clock/deadline assertions. First MethodWindow requires native_roles() success as before.
- No snapshotguard/EPS/90s/input/worker/ABI/queue/TTL changes. Old V2/V3 failures remain failures.

## Tasks

- [x] Task 1: Extract actual nested sample/native_rotation_pair/read_rotation_pair ASTs for portable fixture tests. Observe old zero path fatal; desired initial zero→valid fails RED. Test persistent-zero deadline/attempt bounds, post-valid zero and adversarial bindings.
- [x] Task 2: Implement smallest pure classifier and exact Runner transform; GREEN targeted tests. Keep native_rotation_pair and read_rotation_pair exact.
- [x] Task 3: Verify full inverse/pins and no other source changes; report command/log hashes and clear new-condition metadata requirements. Commit Source-only; Root builds any V4 package separately.

**Verification ruling:** Only the directly relevant portable fixtures are authorized; no broad project discovery/suite, Native or package generation. Parent source is read with explicit resolve + O_NOATIME/NOFOLLOW. Test fake clocks/readers invoke real extracted functions, never a display/process.

## Completion / rulings

All three source-only tasks complete. Actual Parent RED: one assertion fails because the bound zero remains fatal. Final 12 targeted tests PASS. A first constructed GREEN attempt had an incorrect whitespace anchor and 17 errors; retained, corrected before any package/runtime application. Additional real RED proves a pending label must retain the original raw-read FAIL status, then GREEN.

Root confirmed: existing state/tick-changed consistency discards remain as parent even after successful pairs; the no-new-exception rule applies to the newly admitted null/pointer/binding path. No blanket alteration of old consistency behavior.

No package generated. Root's future V4 must pin the new helper and explicitly record readiness_or_retry_changed=True/new condition; inherited V3 error-context metadata describes that earlier transform only and must not be mistaken for the new admission condition. Any native execution remains Root-owned after independent review.
