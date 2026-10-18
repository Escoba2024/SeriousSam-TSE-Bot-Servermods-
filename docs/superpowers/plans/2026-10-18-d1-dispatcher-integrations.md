# D1 Dispatcher Integrations Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox syntax for tracking.

**Goal:** Provide tested standalone HTTPS, GitHub and Notion adapters plus strict authority/status contracts without touching D0's worker.

**Architecture:** Pluggable HTTP opener and clock; durable adapter-specific cooldown; immutable owner-granted identity. Notion is read-only candidate metadata, GitHub+root policy remains execution authority.

**Tech Stack:** Python 3.13 standard library, unittest, git worktree.

**Spec:** `docs/superpowers/specs/2026-10-18-d1-dispatcher-integrations-design.md`

## Global Constraints
- A00 source-only GRANTED #18 comment 6245262914; scope exactly `tools/dispatcher_integrations/**` and listed D1 documents.
- No changes to `tools/notion_bridge/**`, D0 SQLite or production services.
- No live production POST, Notion secrets, D0 worktree, merge or force push.

## Review Focus
1. Host/path confusion or HTTP redirects must never forward a token to a foreign host.
2. 401/ordinary 403 must be authorization errors rather than indefinitely retried quota.
3. A restart during API cooldown must not retry before the recorded deadline.
4. A GitHub owner edit or replay must not become a new authorized development job.
5. A Notion `Erledigt` value must not imply D0 `DONE`.

---

### Task 1: Durable hardened HTTP transport
**Files:** `tools/dispatcher_integrations/api_transport.py`, `test_api_transport.py`
- [x] Write test for pinned host, 401, 403, 429, ETag/304, transient 5xx, redirects and persisted retry (RED).
- [x] Implement HTTPS-only client, injected opener, durable cooldown, bounded retries, no secret logging (GREEN).
- [x] Run `py -3 -B -m unittest discover -s tools/dispatcher_integrations -p test_*.py -v`; commit.

### Task 2: Approved GitHub issue and immutable job identity
**Files:** `contracts.py`, `github_adapter.py`, `test_authority.py`
- [x] Write tests for owner/issue/policy/digest/base/expiry, foreign/stale/closed, replay and status event invariants (RED).
- [x] Implement scoped read interface and immutable idempotency record. Never send status POST (GREEN).
- [x] Run isolated unittest suite and commit.

### Task 3: Read-only Notion schema and safe reconciliation
**Files:** `notion_adapter.py`, `test_notion_adapter.py`
- [x] Write tests for missing token, parent/schema errors, status drift, stale update, missing value and cross-source authorization (RED).
- [x] Implement Notion page retrieval and candidate-only reconciliation (GREEN).
- [x] Run suite, negative cases and commit.

### Task 4: Review and Handoff
**Files:** `docs/reports/2026-10-18-d1-dispatcher-integrations-handoff.md`, `docs/superpowers/ledger/2026-10-18-d1-dispatcher-integrations.md`
- [ ] Verify exact changed paths, full Python suite, `git diff --check`, fresh SHA and clean state.
- [ ] Commit and push own branch only; create Draft PR targeting A00's current API-budget branch, avoid integrating into D0 worker.
- [ ] Record tests, commits, PR URL, limits and integration requirements for D0. Post Handoff in #18.
