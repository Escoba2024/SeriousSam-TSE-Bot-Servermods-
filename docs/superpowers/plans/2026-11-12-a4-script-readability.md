# A4 round-script readability correction

> For agentic workers: use superpowers:executing-plans task by task and verify before completion.

## Goal and boundaries

Explain and correct the observed 1/1/1 round-script execution while preserving the failed native result. Work only in `codex/20261112-a4-script-readability`, base `5a44b29374883d78d6da9b7f2e027dc615b2ff90`, and the new private package `/srv/tse-a4-readability-completion-20261112`. Root alone owns native execution, freeze and integration. No live fixture changes, game starts, compiles, guard relaxation or broad resource tests.

Reviewed parent: `/srv/tse-milestone-a-continuation-evidence-20261112/a4-build015-lowrender-wait-review`, manifest SHA-256 `1c558d9801b474a3fc6b05beef4f630572552e7e017ee87112dc5e637e654129`. Parent package and old trial `a4-reset015-lowrender-20261112-082738` remain unchanged and FAIL.

## Architecture and acceptance

Seven intended scripts are materialized after the existing complete transaction snapshot/seal, with exact bytes, mode 0644 and owner/group 65534. Retain actual staged bytes, metadata and a bounded read-only check executed with that UID/GID. Preserve exact transaction restoration, including preexisting metadata and deletion of newly created files.

Validate actual complete server-log begin records in the order 1, 2, 3; 1, 1, 1 must reject. Phase readiness/completion must require the corresponding executed round. Add expected session time limits 1, 1, 0 only if the offset is independently grounded in the existing 156-byte original layout; retain source/hash/offset evidence. Keep every current protocol, identity, host, pause, observer, 300-second, transition and final active-time bound.

## Tasks

- [x] Reproduce the old materialization with umask 0077 in tempfile directories; use a real UID/GID-65534 reader and retain exact outcome/metadata.
- [x] Write RED permission/receipt/restore and observed-round-sequence regressions against actual controller boundaries.
- [x] Implement the smallest explicit readable materialization and ordered native observation guards; prove GREEN.
- [x] Derive the time-limit offset from pinned source/Original evidence; implement and test 1/1/0 validation only if established.
- [x] Run the small private suite, normalize changes, verify all preserved bounds and parent files, and keep both runtime gates false.
- [x] Write sanitized report, update this plan, commit isolated repository documentation and deliver pinned private package/Root run plan.

## Ledger

- Initial state: clean isolated worktree and claim verified; repository AGENTS.md unchanged from the previously read base.
- Root Python currently has umask 0077. Existing controller uses write_text for all seven round files without chmod/chown.
- Archived native server log contains complete 1_begin records at lines 83, 344 and 597, with only 1_end records. No 2/3 begin execution was observed.
- Existing Original Retail disassembly report documents the missing-next-begin fallback; official 1.10 source remains corroboration, not assumed Retail ABI identity.
- A separate disabled private copy was created; original files are hash-recorded for preservation verification.

## Completed verification and handoff

- Actual UID/GID-65534 reader reproduced EACCES for all four new round-2/3 files under the old staging loop and umask 0077; the three existing files remained readable.
- New materialization records exact staged bytes/metadata, enforces 0644 and UID/GID 65534, and requires a bounded actual read. Permission failures retain receipts before propagation. Full snapshot/restore regressions pass, including preexisting binary content and differing metadata.
- Complete observed begin records must form 1/2/3, with exact count at phase boundaries. The archived 1/1/1 log is rejected by both the validator and actual controller log/finish boundaries.
- Original Retail CheckGameEnd load at RVA 0xEE86A, bytes 8b4030, and verified GetSessionProperties/CurrentTick imports plus the 60.0 constant establish signed minutes at session offset 0x30. Actual archived phase-3 value 1 rejects; expected phase values are 1/1/0.
- RED logs precede both implementations. Final private suite: 113/113 tests, 0.523 seconds. Existing phase-finish fixture now supplies real valid execution records and the real validator; no prior assertion removed.
- Normalized delta: 23 unchanged controller function ASTs, seven unchanged shared files, original reset policy retained as an exact byte prefix, and all prior runtime bounds preserved. Parent and old native failure evidence remain unchanged.
- Sanitized report: `docs/reports/2026-11-12-a4-script-readability.md`. Implementation and detailed evidence remain in the disabled private package; final pins and commit are recorded by its manifest/final-package receipt.
- No live fixture changes, native starts or compiles. Native acceptance is pending Root review, separate freeze and bounded execution. Previous trials remain FAIL.
