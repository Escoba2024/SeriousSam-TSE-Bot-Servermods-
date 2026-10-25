# ssam.ai Rebranding Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Rebrand the existing Alpha-Gaming TSE project to **ssam.ai** across public text, website and administration UI without disturbing game services, evidence or external integrations.

**Architecture:** Separate display identity from stable internal identifiers. Make user-facing changes through isolated repository branches; preserve historical references, runtime paths, tunnel IDs and systemd unit names until explicitly tested migration is available.

**Tech Stack:** GitHub, React/TypeScript/Vite, Node.js MCP App, systemd, Wine/TSE 1.07.

**Spec:** Owner instruction on 2026-10-25: replace Alpha-Gaming with ssam.ai project-wide.

## Acceptance criteria

- [x] Inspect live Hetzner project and concurrent worktrees before changes.
- [x] Create isolated GitHub branding branch in TSE repository.
- [x] Set ssam.ai as the primary TSE repository display identity and retain existing technical documentation.
- [x] Update website source (header, title, metadata, page copy, demo server names) in private Website PR #1 (draft); **website build and visual test pending**.
- [x] Update deployed read-only MCP UI display labels, preserve stable MCP protocol identifiers, run unit/build/branding handshake, verify tunnel health (HTTP 200). Legacy online-only integration test fails at live.online when game server offline.
- [x] Update separate owned skill plugin to 0.1.1 as ssam.ai Control (read-back verified); App-backed plugin's original ChatGPT listing title requires separate App configuration.
- [x] Update MCP human-readable registry name only to `ssam.ai | Red Station | 8 Human Bots`, preserve all other registry fields. The actual GameSpy broadcast session name still needs to be verified at the next safe game start.
- [ ] Verify ssam.ai domain ownership/registrar and brand rights before configuring DNS, email, SSL or publishing a site.
- [ ] Rename GitHub repository slugs only after audits of remote URLs, workflows and active agent branches; GitHub redirects alone are not sufficient.
- [ ] Verify final production website build and GameSpy broadcast, update App-backed listing, rename repos after dependency audit, and document final blockers.

## Decision record

1. **ssam.ai** is the human-facing product and community brand. **ssam.ai Control** is the admin/read-only dashboard name. `#SamIsBack` and `#newSam` are unchanged.
2. Historic reports, evidence paths, binary hashes, commit history and third-party notices must not be rewritten. Internal IDs such as `alpha-gaming-control.service`, `tse-public-1`, UI resource URI, private tunnel, and installation paths are compatibility identifiers until separately validated.
3. Do not touch the running TSE GameServer, Wine clients, bot DLLs, active LMArena/Codex worktrees, firewall, ports or storage cleanup.
4. The Domain already has Cloudflare nameservers visible publicly, **but ownership is unverified**. Do not claim the domain is available or belongs to this owner.
5. No claim of completed website deployment or brand/legal rights until actually verified.

## Workstream ownership

- TSE repository: `branding/ssam-ai-20261025` branch, docs only.
- Website: same branch name in separate private repo; keep production/demo distinction and licensing notice.
- Hetzner MCP: standalone local repo at `/srv/alpha-gaming-control-mcp`, only UI labels and operational human-readable name. Keep the service names and credentials untouched.

## Handoff

All uncompleted checkbox items must be reconciled against actual output and evidence in the final rebranding status report. No unrelated engineering changes in branding commits.

## Verified actions (2026-10-25)

- TSE branding GitHub PR [#59](https://github.com/Escoba2024/SeriousSam-TSE-Bot-Servermods-/pull/59); branch `branding/ssam-ai-20261025`, no merge or runtime change.
- Website brand changed in 15 tracked files; private repo PR [#1](https://github.com/Escoba2024/Alpha-Gaming-Website/pull/1) is a draft until npm/TypeScript/Vite and visual tests. Legacy image asset and git/build paths still exist intentionally.
- Ubuntu standalone MCP local commit `fcb1177` with new UI text, title, tool titles and offline-safe test: 6/6 backend tests PASS, TypeScript/Vite build PASS, 1/1 offline-safe MCP branding/read-only test PASS. Previous `test:integration` failed solely at `live.online === true` while TSE server offline.
- MCP and tunnel systemd descriptions show ssam.ai Control; after coordinated tunnel restart, `127.0.0.1:3977/healthz` = HTTP 200 and `127.0.0.1:3979/readyz` = HTTP 200.
- Human-readable registry name changed **without** changing server ID or other JSON fields. The runtime `servers.json` had pre-existing uncommitted changes; original was backed up and not committed.
- Owned ChatGPT skill plugin updated and read back as version 0.1.1 with `ssam.ai Control` displayName and read-only guard intact. The separate App-backed plugin still reports original App-side name, which is not editable via Plugin Creator source update.
- Domain `ssam.ai` has public Cloudflare NS records; this does **not** prove domain ownership. No DNS or public website deployment performed.
- Technical unit names, paths and GitHub repo slugs remain unchanged for compatibility until verified migration.
