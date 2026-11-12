# Names rollout: Dev first, then one public server at a time

## Requirement and observed state

The original request requires Dev/Red Station first and controlled rollout server by server. The reviewed names-only controller currently preflights all six, then closes all twelve clients before its global write/start phase. That global apply is not used. No live names have been changed. The exact full-fleet package/source checks and current read-only preflight have passed. Preserve these guards and the immutable stage rather than bypassing them.

## Existing approved material

- Root names source integrated at e8e1f4c; author commit 6af283724d0faa0a47eda1829bafbc92b22fa7fa.
- Fresh stage: 2,011 files; exactly 51 planned writes and 48 stable profile assignments.
- Reviewed package: 8 sources, 11 dependencies, 2,063 data pins; 102 tests plus three bootstrap regressions and twelve actual-policy replays pass.
- Root frozen package 8b6780542f7bb20e606e28348708e5ce68103b8f8638e303b1d643347a46214d; native read-only preflight passed all six at 08:50 UTC. It is preserved and not applied.
- Delta019 private backup: 45,078,384 bytes, SHA256 0342390c65ae7759d0e6838d6696b4f28eadb3a27364d44d71a4f14b4309ba3b; 11,858 regular files independently restored and rehashed. Google Drive upload and actual complete raw-download equality verified at 08:56 UTC.

## Implementation and acceptance

1. [ ] Preserve old packages/journals. Implement explicit instance-scoped operations under the existing global lock set and full-fleet preflight/collision validation. Keep exactly the approved 51 total payloads and immutable dependency closure.
2. [ ] Use fixed order: development, redstation, yodeller, skulls, trouble, hole. Only the selected instance's two own client generations may be closed or restarted at a time; Dedicated processes remain unchanged.
3. [ ] Journal instance phase, start/stop intent, service invocation, bytes and metadata before every mutation. Bind recovery to the same package, stage, boot, source and exact touched generations. Earlier verified instances determine their expected after-state; untouched instances retain their before-state. Never recapture hashes to mask drift.
4. [ ] Verify each selected instance's eight actual/query names, GUID/profile invariants, new process identities, new client logs and server-log delta before allowing the next instance. Keep global names collision-free throughout mixed before/after stages.
5. [ ] On failure, stop further rollout and safely restore the affected instance from its verified backup. Preserve receipts for earlier accepted instances and explicit partial status. Recovery must not close or rewrite untouched running instances, adopt unproved processes, or report full-fleet success early.
6. [ ] Add meaningful RED/GREEN tests for exact order, no public mutation before Dev verification, mixed-state source validation/collision, partial failure and interrupted recovery, exact affected-instance rollback, and full final 48-name verification. Retain existing guards/tests; no gameplay/DLL/server changes.
7. [ ] Independently review and freeze a new disabled package; Root alone performs native preflight and deployment. Verify fresh actual fleet activity and update name-dependent identity/monitoring records.

Milestone A and B remain unaccepted/unstarted respectively. This names-only rollout is not a combat/nav release qualification.
