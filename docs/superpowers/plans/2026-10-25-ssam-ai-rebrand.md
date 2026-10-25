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
- [x] Website ssam.ai rebranding, new SVG logo/favicon, correct public image assets, package name, README and portable visual smoke tests; website PR #1 merged (squash commit `72e39f4`).
- [x] Update deployed read-only MCP UI display labels, preserve stable MCP protocol identifiers, run unit/build/branding handshake, verify tunnel health (HTTP 200). Legacy online-only integration test fails at live.online when game server offline.
- [x] Update separate owned skill plugin to 0.1.1 as ssam.ai Control (read-back verified); App-backed plugin's original ChatGPT listing title requires separate App configuration.
- [x] Update MCP human-readable registry name only to `ssam.ai | Red Station | 8 Human Bots`, preserve all other registry fields. The actual GameSpy broadcast session name still needs to be verified at the next safe game start.
- [ ] Verify ssam.ai domain ownership/registrar and brand rights before configuring DNS, email, SSL or publishing a site.
- [ ] Rename GitHub repository slugs only after audits of remote URLs, workflows and active agent branches; GitHub redirects alone are not sufficient.
- [x] Validate website on isolated Hetzner workspace: `npm ci`, TypeScript, Vite build, browser smoke at 390 px + desktop, 0 browser JS errors. Source image blobs verified in GitHub tree; binary preview images missing in isolated local mirror.
- [x] Document remaining external blockers and retain all live compatibility identifiers.
- [ ] Verify next live GameSpy broadcast name after an authorized game start; game server is currently offline.
- [ ] Rename repository slugs (`SeriousSam-TSE-Bot-Servermods-`, `Alpha-Gaming-Website`) after external dependency audit and GitHub repository-Settings rename access; connected GitHub tools have no repository-rename action.
- [ ] Rename original App-backed ChatGPT listing title in App configuration UI; Plugin Creator explicitly does not allow App-backed presentation edits. Separate ssam.ai Control skill plugin already displays new name.
- [ ] Register and prove control of domain ssam.ai, then assess IP/legal rights before any DNS, HTTPS or public website deployment.

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

## Continuation / verification (2026-10-25)

- Website React rebranding PR [#1](https://github.com/Escoba2024/Alpha-Gaming-Website/pull/1) **MERGED**, squash commit `72e39f4d4456d816f88bcff04941947b96444b8c`.
- Verified isolated Hetzner checkouts: 297 npm packages installed; `npm run typecheck` exit 0, `npm run build` exit 0, 1943 Vite modules built. Final build contains SVG favicon. `grep` found no remaining Alpha-Gaming public-facing strings in source, index and npm manifests.
- Portable Playwright smoke PASS: Chrome Headless Shell, 390×844 mobile viewport (scrollWidth 390), desktop home, mobile navigation, server modal, bot page, preview-only payments disabled and /admin locked; zero browser errors.
- The validation mirror intentionally lacks original binary images; Github `main` tree was checked for `public/images/{battlefield.jpg,bot-tech.jpg,kleer-vignette.png,sam-vignette.png}` and `public/brand/ssam-icon.svg`. Its tracked `dist/` legacy build was removed.
- Registry via read-only MCP confirmed `ssam.ai | Red Station | 8 Human Bots`, game query **offline**, so public GameSpy announcement is **not verified**. Health telemetry timestamp predates check, do not mistake cached health for live players.
- The website is *not* deployed; no domain registration/ownership by owner. Repo slug and App-backed title admin changes cannot be performed with the presently connected write actions. Do not bypass credential controls or rename active systemd service identifiers for a cosmetic goal.

## Live-Website Deployment über Hetzner-IP (25.10.2026, 16:03 UTC)

- [x] Öffentliche IP `http://91.99.75.33/` vor Änderung geprüft: HTTP 200 und Alpha-Gaming-Titel, Auslieferung aus `/var/www/alpha-gaming/releases/agent6-20261018-fef0259`.
- [x] GitHub Website PR #1 bereits gemergt; dazu passende isolierte Vite-Quelldateien geprüft. Alle vier Bilder anhand Git-Blob-SHA exakt gegen die vorhandene bisherige Live-Version geprüft und im neuen Build aufgenommen.
- [x] `npm run typecheck` und `npm run build` erfolgreich (1.943 Module); finaler Build ohne alten Alpha-Gaming-Markentext, SVG-Logo und vier Bilder enthalten.
- [x] Staging `npm run preview -- --port 8765` auf localhost: mobile/desktop Playwright-Smoketest erfolgreich, inklusive Navigation, Serverdetails, Bots, deaktivierten Zahlungen und gesperrtem Adminbereich, null JS-Fehler. Alle geprüften statischen Ressourcen HTTP 200.
- [x] Neue Release-Stufe angelegt: `/var/www/alpha-gaming/releases/ssam-ai-20261025-72e39f4` (lesbare Dateiberechtigungen), alte Nginx-Konfiguration unverändert, `nginx -t` PASS.
- [x] Atomare Umschaltung von `/var/www/alpha-gaming/current` auf neues Release, ursprüngliches Release weiterhin unter `/var/www/alpha-gaming/releases/agent6-20261018-fef0259` erhalten. Rückfallzeiger `/root/ssam-ai-backups/site-before-ssam-20261025.txt` und Build-SHA256 in `/root/ssam-ai-backups/ssam-site-release-20261025.sha256`.
- [x] **Live-Abnahme nach Umschaltung:** HTTP 200, Dokumenttitel `SSAM.AI`, Favicon und 4/4 Bilder HTTP 200; Live-Playwright Desktop/Mobile-Smoke PASS, 390px viewport ohne horizontales Überlaufen, null JS-Laufzeitfehler, `X-Robots-Tag: noindex, nofollow` gesetzt.
- [ ] Domain `ssam.ai` bleibt unregistriert/nicht im Besitz des Eigentümers. Öffentliches Branding über die vorhandene **HTTP-IP** ist ein Preview ohne TLS/Custom-Domain; kein Zahlungssystem aktiviert. Vor kommerzieller Veröffentlichung Rechte-/Lizenzlage, Datenschutz und Rechtstexte prüfen.
- [ ] GitHub-Repository-Slugs und älteren App-backed ChatGPT-Eintrag separat über Settings umbenennen; tatsächlichen GameSpy-Servernamen erst bei sicherem GameServer-Start prüfen.
