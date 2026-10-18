# D1 Dispatcher integrations — design (2026-10-18)

**Authority:** Owner approval in chat; A00 source-only GRANTED in Issue #18 comment 6245262914 through 08:45 Europe/Berlin. No runtime lease.

## Scope and architecture

Build independent stdlib Python interfaces under `tools/dispatcher_integrations/`. D0 remains the only worker/state-machine owner and must opt into these modules after a separate review. Do not modify `tools/notion_bridge/**`, systemd, D0 SQLite, root policy, or another agent's worktree. The source-only adapters must work with injected fake HTTPS transports; this PR makes no production network calls.

* `api_transport.py`: strict HTTPS host pinning, caller-supplied credential, no redirects, no token serialization/logging, ETag/304, bounded durable retry/cooldown after 429/limited 403/5xx, fail-closed after configured retry budget. A 401/ordinary 403 is an authorization failure, not quota.
* `github_adapter.py`: typed read-only GitHub issue retrieval, owner/manifest/local-grant verification, exact immutable identity including GitHub issue number/revision/base SHA/manifest digest, safe status-event encoding. No uncontrolled issue-comment POST.
* `notion_adapter.py`: typed read-only Notion page retrieval (only with operator-provisioned Notion token), schema/parent validation, status mapping, source revision checks. Notion is a *signal* only, never authorization; changing Notion status cannot start jobs or mark GitHub integration DONE.
* `contracts.py`: shared acceptance/replay and status reconciliation contracts. `REVIEW_READY` denotes a published testable PR, never `DONE`.

## Explicitly blocked operations

No direct Notion E2E without an operator-provisioned server token. No GitHub owner-approval bypass through Notion. No live POST, model subprocess, worker injection, server change, or merge. A later D0 integration grant is required to use these modules in the live worker.

## Security and testing

Use TDD and synthetic in-memory/disk fixtures only. Test 401/403/429, retry headers and persist-after-restart, ETag/304, redirects/foreign hosts, transport errors, leaked token prevention, stale/foreign/closed/edit-mutated issues, expired grants, duplicate and replay events, Notion status drift and cross-source failures. Confirm exact file scope, full isolated suite on Windows, Linux re-run when possible. No PASS claims from documentation alone.
