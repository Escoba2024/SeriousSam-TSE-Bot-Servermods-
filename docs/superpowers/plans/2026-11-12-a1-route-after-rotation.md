# Execution plan: A1 route after proven rotation
Date: 2026-11-12
Base: 1a9ab5e35331fe9bfa74de414ffef7c0aca3091c
Branch: codex/20261112-a1-route-after-rotation
Worktree: /srv/tse-milestone-a-a1-route-completion-20261112
Private successor: /srv/tse-a1-route-after-rotation-completion-20261112
Claim: /srv/tse-milestone-a-continuation-evidence-20261112/a1-route-claim.json

## Scope and ownership
Offline implementation only. Root owns review, native execution and integration. No changes to old packages, fixture or production. No subagents: Root plus two workers is the agreed cap.
Use writing-plans, executing-plans, test-driven-development and verification-before-completion. The fixed Root scope supplies design approval; no additional permission loop is needed.

## Tasks
1. [done] Read actual090901 native role mapping/inventory, existing route, RD, controller and Damage/lifecycle reports. Confirm botA original spawn matches Route.
2. [done] Create isolated worktree/claim and persist specification.
3. [done] Copy V3 to a separate disabled successor; record exact old-package inventory and preservation digest.
4. [done] Add deterministic real-policy and controller-seam tests. Save initial RED output.
5. [done] Implement pure shared-budget orchestration and minimal controller fresh-role/wiring changes. Keep RD, Route and lifecycle helpers unchanged.
6. [done] Focused GREEN tests including expired success/deadline, life/process, stale read, exhaustion, no further input and failed receipt retention. Run full small private suite once when host scheduling permits.
7. [done] Freeze source/runtime/evidence pins and normalized delta. Verify all old bytes and unchanged lifecycle ASTs. Save report, test logs and next-hit-proof limitations.
8. [done] Final documentation and exact package/manifest/test handoff prepared for Root; independent Root review/native freeze remains pending.

## Verification gates
No native starts/builds; disabled gate checked before resource access.
85s policy/90s native input, Route45s/Flight8s/actions48 unchanged.
Unchanged RD.run_calibration exactly once before original Route.
Fresh read for every input and pre-emission; no input retry.
All raw attempts/failed frames retained.
Original source preservation, complete dependency closure, normal-close/restore behavior unchanged.
False shot/hit/first-state/qualification claims unless future actual native evidence proves them.

## Decisions
No Fire/Bullet hook in this bounded step. Existing passive fire_requested is not a shot witness.
Route's legacy late-pickup success ordering is guarded externally before calling unchanged Route.next.
Native tests remain NOT_RUN; passing deterministic tests only establishes preparation readiness.

## Progress log
2026-11-12: inspected actual V3 window; botA exact expected spawn/heading in all35 valid snapshots. Created worktree and claim. Root reports A4 closed/restored and permits normal small offline tests while Names suite runs.

2026-11-12 final: 138/138 private tests PASS in0.685s;22new real-policy/controller cases;82parent files preserved,32controller functions AST-identical,17runtime files byte-identical. New manifest a902c0133fb31f6f4703e3626b5ebe2521567169c00fb89e1f3c68ea8bdd5bb8;48runtime/41own/56evidence pins;bothgatesfalse. Root clarified next separate step: normal aim toward own second player and passive Original shot/Damage/lifecycle proof; hook draft remains candidate only. No new native work or scope expansion.
