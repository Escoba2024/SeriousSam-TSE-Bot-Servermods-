# A1 Route V2: final normal-input request boundary
Date: 2026-11-12
Owner: /root/review_names_transaction
Status: IMPLEMENTATION COMPLETE; disabled V2 frozen for independent Root review.
Worktree: /srv/tse-milestone-a-a1-route-completion-20261112
Base documentation commit: 8ee03167e73749eea79bc41f4a9fada474fa867f
New private package: /srv/tse-a1-route-after-rotation-completion-v2-20261112

## Verified defect
The V1 policy callback executes before Endpoint.down and X11Transport.event/look perform additional process/display/focus guards. A0.30s final guard accepts an input based on an older-than0.2s observation; a2s guard can send at85.8s after the85s deadline. The recorded emission started timestamp is before those guards. Independent review:/srv/tse-a1-route-review-names-worker-20261112/REVIEW.md SHA04166f76e5ec53e1c7084a646b88178e8068437488f4be97c2d1e27a3447f6d8.

## Design
Thread one optional normal-request submission callback through Endpoint.down and X11Transport.event/look. Transport executes all existing guards and resolves its native XTest function/arguments first. Only then does the controller submission callback run the final policy state/pending/budget checks, stamp the actual request start and call that resolved XTest function immediately. Record native request return separately from later XSync/transport completion.
Keep normal key/button release on the existing direct request path; no new policy/deadline callback applies to up. No input retry, threshold increase, native calls during development, or changes to RD/Route/policy behavior. Preserve original package bytes and create fresh own/runtime/evidence pins for V2.

## Tasks and acceptance
1. [done] Copy parent package and record all parent files; execute independent reproduction read-only.
2. [done] Add failing regressions executing real action_step, Endpoint.down and X11Transport event/look with a fake C-library/clock and delayed guards.
3. [done] Minimal separate source hunks in controller request dispatch/timing and endpoint/transport forwarding. Adapt only necessary memory-fixture request signatures.
4. [done] Prove fresh checks after last guards; reject stale data, changed pending state and expired global/action budgets before any down/motion request. Check key, button, relative-motion requests and true request timestamps.
5. [done] Prove native rejection/post-request failure/deadline expiry still independently release previously pressed keys/buttons. Never route safe up through the new policy guard.
6. [done] Full small offline suite, exact normalized delta/closures and preservation. Update byte-identical claims to actual changed runtime files/functions.
7. [done] Commit report/plan and hand exact disabled V2 pins to Root. Independent review and native work remain Root-owned.

## Limits
All V1 substantive bounds remain: shared85s/controller90s, Route45s, flight8s, selection3s, actions48, V3 pair retries8/.2s. Gatesfalse. No new A1 experiment or first-state/hit claim.

## Completion evidence
149/149 private tests PASS in0.751s. Eleven new actual Endpoint/transport tests and independent before/after reproductions retained. V1all98files and V3all82files preserved. Only action_step plus Endpoint.down/X11Transport.look/event change behavior;19own runtime files and27external pins unchanged. Manifest6ea34a1fa6a11c86c9b25db554535a509fabcccb8b18ba6347603b12fd210ee8;48runtime/42own/72evidencepins. Bothgatesfalse. Root independent review and any native execution remain pending.
