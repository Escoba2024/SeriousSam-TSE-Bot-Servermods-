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

## Task progress — accepted checkpoint, 2026-10-18 03:14:24 UTC
- Task 1: complete — SHA-pin/boot/SQLite/journal and exact PR #34/#35 commits verified against live server and GitHub; baseline source clean.
- Task 2: complete — RED baseline regressions individually reproduced on CX23: `test_terminal_jobs_do_not_refetch_or_relaunch` failed with terminal job fetched; `test_github_403_rate_limit_is_persisted_and_avoids_refetch` failed missing persistent cooldown. GREEN implementation in `a839ececab2e6ddb09087f94b84865afcde99d65`. The new pending-job sequential execution regression from the original 86-test suite still passes. HTTP 403 reset logic was tested by a synthetic HTTPError, not by deliberate exhaustion after deploying.
- Task 3: complete — RED `test_systemd_timer_respects_unauthenticated_rate_budget` expected 300s but observed 60s; GREEN timer set to `OnUnitInactiveSec=300s`.
- Task 4: complete — isolated Linux candidate tree and immutable GitHub release tree tested as `tsecontrol`; 89/89 PASS in 3.790s (candidate) and 4.469s (release), `git diff --check` clean after normalizing transferred CRLF. Root-only backup of old unit/timer and SQLite state: `/opt/tse-agent-control/backups/20261018-goal-a00-api/`. Stopped only own timer; verified no active own worker before deployment; root-owned release created at `/opt/tse-agent-control/releases/a00-api-budget-20261018` with clean HEAD `a839ece...`. Repointed only own service unit to that independent release directory and installed 300s timer, `systemd-analyze verify` PASS. Original production Git checkout remains clean and pinned to `38ab237...`. New service 2026-10-18 03:12:47 UTC Exit 0, `Result=success`; repeat manual run 03:14:24 UTC Exit 0. Both job attempts stay at 1, both states `REVIEW_READY`, `source_errors={}`. Timer enabled/active, list-timers next trigger 03:17:47 UTC. One API header probe after original rate reset returned 55/60 remaining. No new model, merge, game runtime or foreign process action.
- Task 5: complete — Draft PR #36 published with exact scoped implementation and RED/GREEN evidence. See GitHub issue #18 Handoff for operational resumption. Independent external code-review agent unavailable here; Final review: self-review (no subagent tool), PR diff and exact changed paths inspected. No Critical/Important findings in this bounded diff; no asserted independent approval.

## New commits and publication
- Plan `2701a34`, baseline ledger `f5e9704`, failing regressions `bcb359d` and `108bc91`, GREEN fix `a839ece`.
- Branch `agent/A00/18-dispatcher-api-budget-20261018`, review candidate [PR #36](https://github.com/Escoba2024/SeriousSam-TSE-Bot-Servermods-/pull/36). No merge requested or performed.
- Two actual development acceptance outputs remain [PR #34](https://github.com/Escoba2024/SeriousSam-TSE-Bot-Servermods-/pull/34) and [PR #35](https://github.com/Escoba2024/SeriousSam-TSE-Bot-Servermods-/pull/35), not integrated into main. Their recorded `REVIEW_READY` is correct and must not be relabeled `DONE` without separate integration acceptance.

## Rulings
- Ruling: keep terminal jobs immutable and skip live issue re-fetch — existing published commits and SQLite authorization digest provide completed acceptance, while each future distinct job requires fresh owner-granted manifest and exact administrator policy; if historical issue is edited after completion the old result remains archival, not implicitly revoked.
- Ruling: 5-minute baseline polling plus SQLite cooldown — avoids unauthenticated API exhaustion without introducing token sharing or a second worker. If many simultaneously pending jobs exhaust 60/hour, the worker fail-closes until reset; throughput is bounded intentionally.
- Ruling: deploy via independent immutable root-owned release checkout and switch only the dedicated systemd unit — preserves A03 source worktree and existing job worktrees; it adds an alternate release directory and requires that path in the service unit. Restore original unit/timer from root-only backup on failed rollout.
- Ruling: do not repeat a full VPS reboot solely for this source-level patch — real before/after reboot preservation already exists for this dispatcher family, while a second reboot could disrupt unrelated VPS workloads. The new release itself passed full test suite, service restart and repeat polling, but a fresh full machine reboot against `a839ece` was not performed.

## Resume / future work
1. Current dispatcher service is `tse-notion-bridge.service`; enabled active timer `tse-notion-bridge.timer`. Installed root-owned source SHA `a839ece` under `/opt/tse-agent-control/releases/a00-api-budget-20261018`. Old clean source remains under `/opt/tse-agent-control/notion-bridge`.
2. Persistent database and job logs under `/var/lib/tse-agent-control/development`; progress tracked here and in issue #18. Inspect `systemctl status`, `journalctl -u tse-notion-bridge.service`, CLI `--status`, and both PRs before new work.
3. New tasks require separate, exact owner-signed GitHub manifest and root-held grant; do not reuse #32/#33 IDs, expired grants, job worktrees or published branches. A failed model mid-execution intentionally requires recovery inspection before relaunch; pre-model fetch and failed Git publication support bounded retries.
4. Notion server API token still absent (`BLOCKED_SERVER_TOKEN_MISSING`): optional connector mirror not provisioned, do not copy credentials to solve it. Game native/24-7-bot correctness not established by this dispatcher acceptance.

## Boundaries / residual limitations
- No Notion API token on VPS: `BLOCKED_SERVER_TOKEN_MISSING`. Optional Notion mirror not part of GitHub-only dispatcher acceptance.
- GitHub issues #32/#33 grants are time-bounded and their completed work should not be re-run. New development jobs need distinct owner-approved manifests and root policy grants.
- PRs #31/#34/#35 are Draft, not merged; tests are for dispatcher infrastructure, not native TSE game/runtime.


## Focused persistence regression added after first production verification
- 2026-10-18 additional assertion in `test_github_403_rate_limit_is_persisted_and_avoids_refetch`: open a second independent SQLite connection after persisting HTTP 403 cooldown, advance clock beyond the GitHub reset, verify owner-authorized pending job is fetched exactly once and reaches `REVIEW_READY`. Full Linux `tsecontrol` test suite `Ran 89 tests in 4.463s — OK`, `git diff --check` exit 0, isolated candidate only.
- Additional test-only commit `a0d69133b164682326cb9275e665b92ec5c669a0` pushed normally to Draft PR #36 (source implementation unchanged). GitHub content blob `tools/notion_bridge/development_dispatch.py` SHA `01d467457a417e030d6ac62c86ace2d6b81e2477` identical at deployed source commit `a839ece` and PR #36 HEAD `a0d6913`. Production release path and service unchanged; test-only commit does not require repointing the production unit.
- No external independent reviewer was invoked. Human merge/release approval for the Draft PR stack remains separate from this completed dispatcher infrastructure acceptance.

## Task 6 completed: deployed-release full CX23 reboot acceptance — 2026-10-18 03:33–03:35 UTC

**Authority / ruling:** The project owner explicitly required demonstrated server-restart resilience and requested completion in this session. A regular reboot was done once after verifying `tse-notion-bridge.service` had `MainPID=0`, both jobs were already `REVIEW_READY`, no active Codex process or logged-in interactive users, exact release SHA `a839ececab2e6ddb09087f94b84865afcde99d65`, existing rollback copy. Nginx was the only nonstandard active application service; its brief interruption was a known cost of the owner's requested real reboot test. No SIGKILL, merge, production game or foreign worker modification. Shell call `systemd-run --unit=goal-a00-reboot --on-active=3s /usr/bin/systemctl reboot` scheduled exactly one reboot.

**Private reproducible evidence files on CX23:**
- `/var/lib/tse-agent-control/development/acceptance-goal-a00-before-reboot.json`; recorded 2026-10-18T03:33:01Z, SHA256 `6ae3a2f73a135a6afc94cf6f9f72970c654df1b7691435d038a91d6b5585a05c`.
- `/var/lib/tse-agent-control/development/acceptance-goal-a00-after-reboot.json`; recorded 2026-10-18T03:34:09Z, SHA256 `fd35b99ff870037ccba0354874c6b94a82ef19c5f815fb84c6959c6f7d7bb2ea`.
- `/var/lib/tse-agent-control/development/acceptance-goal-a00-reboot-comparison.json`, locally generated independent comparison with `passed=true`, 15 checks true, exit 0.
- Actual Linux boot ID changed **`a3cc2ce3-7581-4bcb-b397-2c910ab0a8ad` → `e2fdd025-c547-450d-bd5d-cab0f846e649`**. Trusted SSH host key remained unchanged; connection recovered without host-key bypass.
- Exactly two SQLite jobs and 12 transition events identical before/after reboot. Jobs: `dispatch-review-output`, `REVIEW_READY`, attempts=1, commit `4012d3e6d6f4df5b53da86f76036b534af7f58c6`; `dispatch-fetch-recovery`, `REVIEW_READY`, attempts=1, commit `a6415ea41677f1b74ec1903f9e944ecc4ce7dbfc`.
- Immutable release Git HEAD `a839ececab2e6ddb09087f94b84865afcde99d65`, clean status, deployed source SHA256 identical before/after; owner source_errors `{}`. Both `tse-notion-bridge.timer` and Nginx `active`, timer `enabled` after reboot.
- Real automatic timer fired at **03:34:22Z**, `Result=success`, `ExecMainStatus=0`; additional manual `systemctl start tse-notion-bridge.service` at **03:34:28Z**, exit 0. Journal reported both `REVIEW_READY` after both invocations; no new Codex model process. 300-second next timer trigger 03:39:28Z observed.
- Actual post-reboot full suite as `tsecontrol` against immutable release: `python3 -B -m unittest discover -s tools/notion_bridge -p test_*.py -v`, **89 tests / OK, 4.514s, exit 0**; `git diff --check` exit 0 and release checkout clean. Log: `/var/lib/tse-agent-control/goal-api-a00/test-after-reboot.log`.

**Task result:** Full restart, persistence and deduplication gates now PASS on the deployed API-budget release, not merely the old baseline.

## Task 7 / integration boundary
- GitHub-only owner-granted development dispatcher technical acceptance: **PASSED**. Two real sequential published code jobs, 74/82 tests in per-job checkouts, no duplicate attempts, process SIGKILL fail-closed controlled fixture, Git fetch recovery, live two-boot retention, new-release reboot, active persisted timer, published PRs #34/#35 and infrastructure PR #36.
- No merge into main: job `REVIEW_READY` is correct and *not* `DONE`; semantic review/merge remains an external explicit release gate, not part of this infrastructure acceptance.
- Optional direct Notion data-source ingestion: **BLOCKED_SERVER_TOKEN_MISSING**. Server's connector credential was not present and may not be copied from ChatGPT, so direct Notion E2E was not asserted. Separate D1 agent has submitted Claim in Issue #18, currently status requested; A00 coordination still required.
- Project game runtime/WAN/native Retail-1.07 functionality is **not** qualified by dispatcher software results; these are independent future gates.
- Handoff published to Issue #18 with these fresh claims; no new code or production processes necessary for this checkpoint.
