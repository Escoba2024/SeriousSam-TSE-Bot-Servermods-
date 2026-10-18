# D1 dispatcher integration HANDOFF — 2026-10-18

**Role:** D1, source-only independent adapter development, A00 GRANTED Issue #18 comment 6245262914 (lease until 08:45 Europe/Berlin). **No runtime / production credential / service grant.**

## Baseline and protection

- Branch: `agent/D1/18-dispatcher-integrations-20261018`.
- Base SHA: `add3518a7acb489c93adae309fa593080c31ab16` (A00 API-budget PR #36).
- Separate local seed: `C:/Users/info/Documents/Codex/2026-10-18/hetzner-dispatcher/d1-seed`.
- Separate worktree: `C:/Users/info/Documents/Codex/2026-10-18/hetzner-dispatcher/agent-D1-18-integrations`.
- D0 checkout: `C:/Users/info/Documents/Codex/2026-10-18/hetzner-dispatcher/repo`, original preflight `M tools/notion_bridge/README.md` not touched.
- All changes limited to `tools/dispatcher_integrations/**` and the expressly granted D1 plan/spec/ledger/report files.
- **No changes:** central D0 worker, D0 SQLite, `tools/notion_bridge/**`, systemd, server, Codex, ChatGPT connector credentials, TSE game/runtime, any other agent branch/worktree.

## Implementation

1. Pinned HTTPS-only GET transport (`api_transport.py`) with injected credential provider, pinned GitHub/Notion host, no redirect following, limited payload, ETag 304, persistent cooldown for GitHub 403 (rate 0), 429 and 5xx/transport failure, bounded total retries, 401 and ordinary 403 fail closed.
2. GitHub source adapter and immutable contracts: exact author `Escoba2024`, issue identity/state, `TSE_DEV_JOB_V1`, manifest SHA-256, root-owned grant, max four-hour expiry, pinned base/source scope/test command. Atomic local receipt ledger rejects duplicates and changed identities after restart; call **only after durable D0 acceptance**.
3. Notion adapter: read-only exact page+data-source+edited-time+status validation, no Notion-to-execution escalation; Notion `Erledigt` never implies D0 `DONE`.
4. Approval-bound status **preview only** for D0 to review. `REVIEW_READY` requires a pinned commit SHA and evidence; `DONE` cannot be generated. No HTTP POST.

## Reproducible tests

**Environment:** Windows `DESKTOP-64MTHJ3`, Python 3.13.3, isolated D1 worktree, synthetic HTTPS and temp files, no network/API credentials or game server.

`py -3 -B -m unittest discover -s tools/dispatcher_integrations -p test_*.py -v`: **36/36 PASS**, exit 0. Test history includes observed RED errors for missing transport, GitHub/Notion modules, HTTP-date Retry-After/304 reset and package import before corresponding GREEN fixes. Independent cross-adapter fake requests enforce no POST and no Notion-only authorization.

`git diff --cached --check`: exit 0 on scoped individual commits. Final pre-push `git diff --check`, exact branch diff and `py_compile` to be recorded at finish.

**Not run:** real GitHub authenticated request from CX23; direct real Notion API; Linux/server integration; systemd; HTTP POST; D0 worker import/production wiring. The D0 main Linux suite and live systemd acceptance in Issue #18 concern D0's existing release, **not this branch**.

## For D0 (integrator)

- Review `tools/dispatcher_integrations/README.md` and tests, then adopt the modules only under D0's independent file/runtime/source approval.
- Keep D0 root-owned owner-grant and SQLite state machine authoritative. Notion page `Wartet` is only candidate metadata; reread the matching owner-authored GitHub issue and root policy immediately before worker acceptance.
- Store token/state under restricted service user; never pass tokens to model sandbox or publicly log. Provision actual Notion server API token separately; user has not granted copying ChatGPT connector secrets.
- Cross-process exclusive locks / durable dispatcher acceptance / live GitHub status publishing are **D0's integration responsibility**. D1 intentionally has no worker or live status POST.
- Preserve D0's already verified two `REVIEW_READY` jobs #32/#33 and PRs #34/#35. Do not re-execute those jobs, merge, deploy, or mark `DONE`.

## Publication
- Source commits: `91f6aad565185a616799e3d9c0412a9319c2189e`, `f176fec86468e7c3bf362b3e8f69dcac6c51c559`, `97c3a9f71cde10b2c235d6eabaeb4e619dfa383f`.
- Final documentation commit / remote HEAD / PR link are recorded in GitHub Issue #18 HANDOFF after publication.
- **Result:** source adapters and offline contract integration tests prepared. Live API authentication and complete Notion→D0→GitHub status E2E remain BLOCKED by credentials and separate D0 integration authorization.
