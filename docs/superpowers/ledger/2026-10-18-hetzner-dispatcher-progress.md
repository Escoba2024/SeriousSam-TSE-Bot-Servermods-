# SDD ledger — plan: docs/superpowers/plans/2026-10-18-hetzner-dispatcher-acceptance.md

**2026-10-18 · verification session:** New independent owner-scoped plan branch. Existing A03 production branch `38ab237851d166bc02115d8e9fca21c45dd8d3a8` and model worktrees were not altered during inventory.

## Verified starting evidence
- Production host `ubuntu-4gb-nbg1-2`, installation SHA `38ab237851d166bc02115d8e9fca21c45dd8d3a8`, tracked worktree clean.
- `tse-notion-bridge.timer` active, currently about 60 seconds between invocations; service `ExecMainStatus=0`; journal displays two jobs as `REVIEW_READY` repeatedly without new attempts.
- Job #32 / PR #34: `4012d3e6d6f4df5b53da86f76036b534af7f58c6`, 74 tests in persisted job log, one attempt.
- Job #33 / PR #35: `a6415ea41677f1b74ec1903f9e944ecc4ce7dbfc`, 82 tests in persisted job log, one attempt; dispatched in the same invocation after #32.
- Persistent events 1–12: #32 transitioned to `REVIEW_READY` before #33's first `RUNNING`. SQLite records both exactly once. Never label as merged `DONE`.
- Real reboot from boot `b100e7ca-5a99-4812-86f6-a1fa709d516f` to `a3cc2ce3-7581-4bcb-b397-2c910ab0a8ad`, current boot 2026-10-18 02:24:47 UTC. `acceptance-after-reboot.json` confirms unchanged jobs and attempts.
- `acceptance-faults.json`: controlled worker SIGKILL produced `BLOCKED` and recovery inspection lock; real local Git failure/backoff/retry fixture passed. This is a controlled fault fixture, not an unrelated production crash.
- New live defect: GitHub unauthenticated API call from same VPS returned HTTP 403; `X-RateLimit-Limit: 60`, `Remaining: 0`, `Used: 60`. Current source_errors for both terminal jobs `GITHUB_SOURCE_UNAVAILABLE`; completed-job repeat polling consumes quota.

## Task progress
- Task 1: evidence gathered; publish/verify this ledger then mark complete.
- Task 2: NOT STARTED. First write RED tests for unnecessary GitHub API consumption and persistent 403 cooldown.
- Task 3: NOT STARTED.
- Task 4: NOT STARTED; production left unchanged.
- Task 5: NOT STARTED.

## Boundaries / residual limitations
- No Notion API token on VPS: `BLOCKED_SERVER_TOKEN_MISSING`. Optional Notion mirror not part of GitHub-only dispatcher acceptance.
- GitHub issues #32/#33 grants are time-bounded and their completed work should not be re-run. New development jobs need distinct owner-approved manifests and root policy grants.
- PRs #31/#34/#35 are Draft, not merged; tests are for dispatcher infrastructure, not native TSE game/runtime.
