# A00 Koordinationsboard – Snapshot vom 17.10.2026

**Status:** Initiale GitHub-Inventur; GitHub-Issue für Live-Claims ist noch mit einer konkreten URL zu verlinken. Diese Datei ist ein **Snapshot**, keine Live-Synchronisierung. Nichts hiervon bestätigt, dass fremde Chats/Agenten die Regeln bereits übernommen haben.

## Aktive Slots

| Slot | Agent / Aktivität | Arbeitsrecht |
|---|---|---|
| A00 | Koordination durch ChatGPT in separatem Branch `coord/a00-agent-orchestration-20261017` | Nur Governance-Dokumentation; **keine Merge- oder Runtime-Freigabe** |
| A01 | **NICHT ZUGEWIESEN**; Supervisor-PRs vorhanden | Kein Claim/GRANTED |
| A02 | **NICHT ZUGEWIESEN**; Watchdog-PRs vorhanden | Kein Claim/GRANTED |
| A03 | **NICHT ZUGEWIESEN**; QA-/Fleet-PR vorhanden | Kein Claim/GRANTED |
| A04 | **NICHT ZUGEWIESEN**; Sync-Parser-PR vorhanden | Kein Claim/GRANTED |
| A05 | **NICHT ZUGEWIESEN**; Windows-/Vanilla-PRs vorhanden | Kein Claim/GRANTED |
| A06 | **NICHT ZUGEWIESEN**; Hetzner-Issue #6 vorhanden | Kein Claim/GRANTED |
| A07 | **NICHT ZUGEWIESEN**; Bot-AI-Branch vorhanden | Kein Claim/GRANTED |
| A08 | **NICHT ZUGEWIESEN**; Toolchain-Issue #9 vorhanden | Kein Claim/GRANTED |
| A09 | **NICHT ZUGEWIESEN**; Website-Repositories bestehen | Kein Claim/GRANTED |

## GitHub-Bestand bei Inventur

16 Branches; 11 offene PRs: #3, #7, #8, #10, #11, #12, #13, #14, #15, #16, #17. Diese **nicht** als 11 separate aktive Chat-Agenten interpretieren.

**Konfliktfamilie Supervisor:** #3 / #7 / #8 / #10 / #11 / #12 / #13. **Vorrang bei Integration:** gemeinsamer Kandidat #12, dann #13 nach Review; Eltern-PRs sind keine unabhängigen zusätzlichen Merges. Windows-Gates offen.

**Kontrollierbare parallele Workstreams:** #14 Fleet-UDP; #15 RetailJoin-Harness; #16 Sync-Parser; #17 Vanilla-Preflight; Toolchain #9; WAN/Hetzner #6; Bot-AI; Alpha-Gaming-Web. #15 und #12 ändern beide `tools/Test-Publication.ps1`: seriell prüfen.

## Shadow-Workspace-Inventur (nur beobachtet, nicht beansprucht)

Gemeinsames Root: `C:\Users\Shadow\Documents\SeriousSam-TSE-Bot-Servermods-` (`main` @ `55f1d25e08caed7667494321a0a9a9dcd193bf9a`) – untracked `error.log`, **nicht** anfassen.

Bereits vorhanden unter `C:\Users\Shadow\Documents\SeriousSam-TSE-Worktrees\`:
- `chatgpt-sync-log-regressions-20261017`
- `chatgpt-syncdump-compare-20261017`
- `chatgpt-vanilla-preflight-framing-20261017`
- `population-supervisor-20261014`
- `portable-qa-watchdog-20261017`
- `rdc-retail-harness-restore-20261017`
- `supervisor-readiness-recovery-20261016`

Die Existenz eines Worktrees ist kein Nachweis, dass er inaktiv oder sauber ist. Keine `git worktree prune`, `git reset --hard`, automatische `checkout`-Wechsel oder gemeinsame Cache-/Runtime-Schreibzugriffe.

## Unmittelbare P0/P1-Abhängigkeiten

1. **P0:** Bisherige native DLL und etwaige laufende Shadow-/Hetzner-/Codex-Sessions schützen.
2. **P0:** Supervisor-PR-Familie entflechten; #12 + #13 nur nach W1 Windows/PS5.1 und W2 begrenzten Retail-Tests beurteilen.
3. **P0:** Sync-Ursache `Too many bad syncs` isolieren, keine bloße Kick-Flag-Maskierung.
4. **P1:** #15/#17 Restore-/Preflight-Guards in isolierter Testumgebung prüfen.
5. **P1:** Öffentlichen Browser-/WAN-Nachweis strikt vom Direkt-IP-Join unterscheiden.
6. **P2:** Bot-AI, Skalierung und Alpha-Gaming-Webseite auf getrennten Quellzweigen ohne Einfluss auf Retail-Baseline.

**Live-Fragen und Freigaben gehören in das Koordinationsissue; diese Datei nur bei nachweisbarer neuer Inventur aktualisieren.**
