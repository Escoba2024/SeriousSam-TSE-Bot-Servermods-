# D1 dispatcher integration adapter contracts

This directory is a **source-only, standalone** component. It is not imported
by D0's running `tools/notion_bridge/development_dispatch.py`, nor has it been
deployed or granted a production service, GitHub write or Notion secret.

## Ownership and responsibility

* `api_transport.HTTPSClient`: HTTPS GET only to pinned `api.github.com` or
  `api.notion.com`; injected token provider, opener and clock; no redirects;
  persistent per-API cooldown, HTTP 429/limited 403/5xx handling, bounded
  failures, safe 401/ordinary 403, 304/ETag optimization. Auth token is never
  written into cooldown state. The transport uses one request per poll (no busy
  retry loop). It does not send status POST.
* `github_adapter.GitHubAdapter.fetch_approved_issue`: only the configured
  owner/repository's issue, `TSE_DEV_JOB_V1` manifest with exact schema, pinned
  revision/base, hash-matched local administrator grant, expiry under 4 hours,
  fixed scoped tests and valid paths. Returns immutable `ApprovedJob`.
* `contracts.DeliveryLedger.record_once`: a durable, local candidate-receipt
  reservation. Replays are deduplicated; modified identities under the same
  job ID are rejected; a failed/stale lock is fail-closed. **Call only after D0
  has durably accepted a job**, never before, or a crash might suppress a job
  that was not actually persisted to worker SQLite.
* `contracts.status_event`: encodes an approval-bound **preview only**. No
  external status write. `REVIEW_READY` requires source SHA and nonempty
  evidence; `DONE` is never generated and remains D0's integration gate.
* `notion_adapter.NotionAdapter.fetch_candidate`: read-only Notion page
  verification with exact data source, stable page ID and timestamp.
  `observe_status` cannot mint a grant, enqueue a job, or set D0 to `DONE`.
  Notion status `Erledigt` is mapped to `NOTION_REPORTED_COMPLETE`.

## Security and integration order for D0

1. Merge/review as a **separate** source candidate; the A00/D0 team must
   explicitly decide what to consume. D1 did not alter D0's worker.
2. A server administrator independently provisions scoped credentials through
   protected service configuration (never copy ChatGPT Notion connector tokens,
   never expose auth in model subprocess `env`). Direct Notion E2E remains
   BLOCKED until that happens. An authenticated live GitHub integration check
   also requires a separate deployment/test grant.
3. Instantiate distinct clients with distinct protected state paths, e.g. D0's
   designated root-owned data directory. The caller must supply an exclusive
   worker lock and policy-synchronized scheduling. The module does not
   implement shared-worker locks or D0's central database transitions.
4. Notion `Wartet` merely requests a reconciliation. Re-fetch the GitHub
   owner-authored issue, validate its exact manifest digest against D0's
   root-owned grant, then recheck cancellation/expiry immediately before D0
   accepts it. A Notion-only status is **never** an execution instruction.
5. Only D0 may write GitHub status events, reconcile them to Notion and set
   `DONE` after verified integration; D1's `status_event` is a data schema
   proposal requiring D0 review, not an asserted authoritative server receipt.
6. Protect state files from untrusted local writers; the adapters validate
   content but are not a substitute for OS ownership and sandbox policy.

## Offline reproduction

From repository root (Python 3.10+ stdlib):

```shell
python -B -m unittest discover -s tools/dispatcher_integrations -p "test_*.py" -v
```

Tests use fake HTTPS transports and temporary files; there are no external API
calls, service restarts, Codex worker launches, Git pushes or game processes.
Successful offline tests **do not** qualify live authenticated Notion or
Hetzner systemd integration.

## Known constraints

* No authentic Notion API token is currently provisioned to CX23 as of D0's
  last owner Handoff; this is a tested fail-closed branch, not a live PASS.
* GitHub/Notion account credentials, live POST and status reconciliation need
  D0/administrator-controlled provisioning and a new runtime/write grant.
* API rate budget is persisted per client state path; callers must use a
  consistent root-owned path (not ephemeral scratch on every poll).
* D0's deployment has its own quota and SQLite state machine; any future
  module wiring must test those together rather than claiming unit tests as
  an end-to-end dispatcher acceptance.
