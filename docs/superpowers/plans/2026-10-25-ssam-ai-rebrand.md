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
- [ ] Update separate website source (header, title, metadata, page copy, demo server names), build/test, create isolated PR.
- [ ] Update deployed read-only MCP UI display labels, preserve stable MCP protocol identifiers, run test/build/handshake, verify tunnel health.
- [ ] Update installed read-only ChatGPT plugin display instructions where permitted by package ownership; preserve read-only safety.
- [ ] Inventory live server name/config and change display name only with safety checks (never start/stop gameplay to rebrand).
- [ ] Verify ssam.ai domain ownership/registrar and brand rights before configuring DNS, email, SSL or publishing a site.
- [ ] Rename GitHub repository slugs only after audits of remote URLs, workflows and active agent branches; GitHub redirects alone are not sufficient.
- [ ] Confirm final branding in runtime/website/ChatGPT and document any blockers honestly.

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
