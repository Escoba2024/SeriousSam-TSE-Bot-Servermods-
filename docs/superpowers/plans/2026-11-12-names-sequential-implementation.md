# Sequential names rollout implementation plan

**Goal:** Enforce Development first, then Red Station, Yodeller, Skulls, Little Trouble and Hole, with exactly one affected instance at a time.

**Architecture:** A dedicated sequential controller reuses reviewed file/process/log guards. Full 48-assignment/51-write stage validation and the complete global lock set remain mandatory. The journal records the fixed completed prefix, one selected instance, exact current generations, original backups and immutable stage/source identity. Current inputs must equal known before/after payloads; no recapture changes those expectations.

**Authority:** Implementation and temporary offline tests only. Root owns independent review, integration and all native operations. Preserve previous packages, stage files and journals.

## Tasks and acceptance

- [x] RED: reproduce all-clients-first behavior and specify fixed-order acceptance with no public close before Dev verification.
- [x] Implement selected-instance close/write/start boundaries and fresh eight-name verification plus global mixed-state collision/source checks.
- [x] Preserve earlier accepted instances on failure; rollback only the affected instance and explicitly report partial state.
- [x] Bind interrupted recovery/resume to the same boot/source/stage, durable invocation records and completed prefix. Never adopt an unproved generation.
- [x] Verify full 48-name final state with all exact started generations and log gates before global success.
- [x] Run focused and complete offline suites; prepare a new disabled immutable package and exact handoff; commit distributable source/tests/docs.

Recovery first restores an interrupted affected instance and halts. Explicit resume starts only from a verified quiescent boundary and rechecks the entire mixed state. Old global packages remain immutable and are not used for this rollout.

Focused evidence: 20/20 sequential tests passed in 61.979 seconds. Full current 122-test suite and private package validation are paused during root native measurement; no additional stage scans during that window.

Final verification: complete current nine-module suite 123/123 PASS, 193.285 seconds, exit 0. Three private bootstrap boundary tests PASS; disabled package closure 9 sources / 11 dependencies / 2063 data pins validated. Independent root review found no critical/important findings at the tested controller/backend hashes. Runtime gate false; root retains all native authority.
