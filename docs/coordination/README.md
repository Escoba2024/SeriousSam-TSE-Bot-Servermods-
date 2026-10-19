# TSE 1.07: Zentrale Agentenkoordination (A00–A09)

**Arbeitsmodus aktualisiert am 19.10.2026.** Dieses Dokument ergänzt `AGENTS.md` und die [Toolpolicy](../decisions/2026-10-17-tse-ai-tools-mcp-policy.md). Die frühere manuelle A00-CLAIM/GRANTED-Pflicht ist ausdrücklich aufgehoben. Unverändert gelten technische Kollisionssicherheit, Tests, Versionsnachweise und Schutz fremder laufender Prozesse. Die Dateien starten oder steuern keine anderen Chats automatisch.

## Ziele / Quelle der Wahrheit

- **Code, Branches, Pull Requests, technische Belege:** GitHub.
- **Transparenz über laufende Arbeiten, Konflikte und Übergaben:** [GitHub-Issue #18](https://github.com/Escoba2024/SeriousSam-TSE-Bot-Servermods-/issues/18). Das Issue ist ein Informationsboard, **kein Freigabe- oder Lock-Server**. GitHub-Kommentare sind keine atomaren Sperren.
- **Gemeinsames Runtime-Labor:** Shadow und Hetzner. Gemeinsame Installation/Port/Prozess nur bei technisch nachgewiesener exklusiver Belegung; bevorzugt separate isolierte Testkopien. Keine manuelle A00-Freigabe nötig.
- **Notion / Drive:** lesbare Spiegel des Status, nicht operative Autorität oder Ersatz für GitHub-Belege.
- A00 hilft bei Konflikten und Integrationsreihenfolge, blockiert aber keine unabhängigen Arbeiten. Keine zusätzliche Dispatcher- oder Agenteninstanz erforderlich.

## Maximal zehn Slots – eine zuständige Schreibinstanz pro Modul

| Slot | Verantwortungsbereich | Exklusiver Standardscope (Schreiben) | Bestehende Arbeit / Grenze |
|---|---|---|---|
| **A00** | Koordination, Konflikthinweise, Integration | `docs/coordination/**`, Koordinationsissue, Review- und Integrationshinweise | Kein Gameplay-/Produktions-/Supervisor-Code |
| **A01** | Population-Supervisor, Readiness, UDP-Supervisor-Gates | `poc/scripts/PopulationSupervisor*.ps1`, `Manage-BotPopulation.ps1`; ausschließlich **ein** aktiver Supervisor-Integrationszweig | PR #3/#7/#10/#12/#13 bilden eine **sequenzierte Familie**; nicht parallel auf denselben Dateien schreiben |
| **A02** | Watchdog / Guardian / Prozessidentität | `poc/scripts/PopulationWatchdog.ps1`, `Watch-BotPopulation.ps1`, watchdog-spezifische neue Tests | PR #8/#11 sind Vorstufen von #12; `PopulationSupervisor.ps1` nur nach Übergabe an A01 |
| **A03** | Unabhängige portable QA, CI und Sicherheitstests | neue eigenständige Regressionen unter `tools/` / `poc/scripts/Test-*` im eigenen isolierten Zweig; Review-Berichte mit eindeutigen Namen | Keine parallelen Änderungen an bereits von A01/A02 belegten Testdateien; PR #14 betrifft Fleet-Auditor |
| **A04** | Retail-Sync-Root-Cause und CRC-Analyse | neue `docs/reports/*sync*` (eigene IDs), `tools/analyze_sync_log.py` und eigene Parser-Tests mit eigenem Scope | PR #16; Original-Retail-DLLs nur lesen, 61DC-Kandidat bleibt geschützt |
| **A05** | Shadow native Retail-Abnahme, Join, Windows-Harness | neue Runtime-Berichte / Harness-Scope `poc/scripts/Test-RetailJoin*.ps1` nach Eigenprüfung | PR #15/#17; **keine** Änderungen am laufenden Shadow-Test ohne Runtime-Lease |
| **A06** | Hetzner / Wine / öffentliche UDP-/333networks-Listung | eigene WAN-/Wine-Testberichte, `poc/HETZNER-*` # nach Eigenprüfung | Hetzner-Instanz und produktiver Port sind **exklusiv**; keine fremden Playerslots entfernen |
| **A07** | Bot-AI, Navigation, Combat | eigene `poc/release/gamemp/**`-Quellen und Botcore nach eigener Branch-/Runtime-Abnahme | keine Überschreibung der bekannten qualifizierten 61DC-DLL, keine unbelegte 1.07↔1.10-Annahme |
| **A08** | REA / GhidraMCP / Frida, reproduzierbare Binärdiagnose | neue Toolchain-/Analyseberichte, **eigene lokale Analyseprojekte** | REA, `ghidra_tse`, Frida nur isoliert; A04/A07 erhalten Findings statt gemeinsam in der DLL zu schreiben |
| **A09** | Alpha-Gaming-Webseite und Design | **separate** Repositories `AlphaWebBolt`, `alphawebgemini` bzw. separater Web-Ziel-Branch | Website heißt Alpha-Gaming; `#SamIsBack`/`#newSam` nur Kampagnen. Keine TSE-Runtime-Dateien |

**Wichtig:** Slots A01–A09 sind **vorgesehene Rollen**, keine Behauptung, dass neun Agenten verbunden, gestartet oder persönlich zugewiesen sind. Existierende PRs zeigen Arbeitsprodukte, nicht den Live-Status eines Chat-/Codex-Prozesses.

## Autonomer Arbeitsbeginn – keine Genehmigungswarteschlange

1. **Code, Offline-QA, Berichte und statische Analysen starten sofort** in einem eigenen Branch/Worktree. Bestehende Worktrees, Status, aktive Prozesse und Pfadüberschneidungen zuvor lesend prüfen. `CLAIM`, `GRANTED`, Ablauf/Erneuerung einer Code-Lease und A00-Antwort sind **keine Voraussetzungen**.
2. Ein Agent dokumentiert seinen konkreten Scope und das Ergebnis spätestens bei PR/Handoff. Für längere oder parallele Arbeiten ist ein kurzer `STARTED`-Eintrag in Issue #18 hilfreich, aber optional. Ein Ticket ist sinnvoll, jedoch keine Startblockade für kleine unabhängige Arbeit.
3. **Niemals zwei Writer im selben Worktree oder gleichzeitig an derselben gemeinsam genutzten Datei.** Neuen Worktree außerhalb des Shadow-Root-Checkouts anlegen; vorher `git worktree list --porcelain`, `git status --short` und existierende Verzeichnisse prüfen. Bestehende `codex/*`-Branches nicht überschreiben. Kollision: zunächst auf separaten Teilbereich ausweichen oder seriell integrieren, statt auf eine A00-Freigabe zu warten.
4. **Runtime nur bei technischer Exklusivität:** Vor Zugriff auf `SHADOW_RETAIL`, `SHADOW_GAME_FILES`, `HETZNER_RUNTIME`, `GHIDRA_TSE_PROJECT` oder gemeinsam genutzte Ports/Dateien Prozesse, Eigentümer und tatsächliche Instanz identifizieren. Wo ein verlässlicher atomarer Lock/Owner-Nachweis verfügbar ist, diesen nutzen; ein GitHub-Kommentar allein reicht nicht. Ist die exklusive Kontrolle nicht belegbar, **nur diese gemeinsame Ressource meiden**, eine eigene isolierte Kopie bzw. Offline-Test verwenden und übrige Arbeit fortsetzen. Keine abgelaufene Text-Lease als Freigabe interpretieren.
5. **Eigenständig testen und integrieren** ist bei konfliktfreier Änderung, nachvollziehbarem Review und bestandenen dafür relevanten Tests möglich, soweit Repository-Schutzregeln und tatsächliche Berechtigungen es erlauben. A00-Zustimmung ist nicht notwendig. Gestapelte Supervisor-PRs und überlappende Dateien werden seriell zusammengeführt, keine blinden Mehrfach-Merges.
6. **Unveränderte Schutzregeln:** keine fremden Prozesse stoppen, keine unbestätigten produktiven Deployments, keinen Force-Push/Rebase fremder Branches, keine qualifizierte Retail-`GameMP.dll` austauschen, keine fremden Spieler oder privaten Rohlogs beeinflussen. Plattform-/MCP-Berechtigungen und gegebenenfalls nötige Sicherheits-, Kosten- oder Veröffentlichungsfreigaben bleiben bestehen.
7. **Handoff statt Blockade:** Änderungen, Commit/Branch, Tests mit PASS/FAIL/SKIP, Umgebung, Ressourcen-Folgen, offene Probleme und PR dokumentieren. Die Stufen portable/Windows/native Retail/WAN/Soak sind **Testevidenz**, keine separaten A00-Genehmigungsstufen. Fehlende Nachweise ehrlich als `NOT_TESTED` kennzeichnen.

A00 fungiert als **nicht blockierende Koordination**. Ein inaktiver, nicht erreichbarer oder nicht gestarteter A00 verhindert keine sichere isolierte Arbeit. Diese Regeln wirken bei anderen bereits laufenden Agentensitzungen erst, nachdem sie die aktualisierten Projektanweisungen eingelesen haben.

## Integrationsreihenfolge und Konfliktzonen

**Roter Bereich Supervisor:** `#3 → #7 → #10` sowie `#8 → #11`, beide in **#12** zusammengeführt; **#13** erweitert #12 um Lock-Marker-Schutz. Diese Pfeile sind Abhängigkeits-/Reviewhinweise und **keine Aussage, dass ein PR gemergt wurde**. A00 bestimmt einen finalen gemeinsamen Kandidaten und vergleicht Merge-Base/Diffs, statt alle Vorstufen nacheinander in `main` zu mergen. Windows-/PS5.1- und native W1/W2-Gates bleiben offen.

**Getrennte QA-/Native-Familien:** #14 Fleet-UDP-Evidenz, #15 RetailJoin-Restore, #16 Sync-Parser und #17 Vanilla-Preflight. Bei Überlappung (`tools/Test-Publication.ps1` in #12/#15) läuft Zusammenführung **nacheinander** mit erneuten Tests.

**Entscheidungs-Gates:** (1) portable Tests und Versionsprovenienz, (2) sicherer Windows/PS5.1-Test, (3) isolierte echte Retail-1.07-Join-/Action-/Sync-Probe, (4) unabhängiger externer UDP-/Browser-Test, (5) lange Soak-/Skalierungsprüfung – jede Ebene gesondert dokumentieren. Keine 24/7-/16-Bot-Freigabe durch reine CI.

## Einstieg eines weiteren Agenten

1. `AGENTS.md`, diese Koordination und laufende Worktrees/Branches prüfen.
2. Eigenen Scope, Branch und Worktree nutzen; ohne `GRANTED` direkt mit konfliktfreien Code-/Offline-Arbeiten beginnen.
3. Bei belegten gemeinsamen Laufzeitressourcen isolierte Kopien oder Offline-Arbeit vorziehen. Niemals bei unbekanntem Besitz in fremde Prozesse/Dateien eingreifen.
4. Ergebnis, Tests, PR und Handoff dokumentieren. A00 nur für reale Konflikte oder schwierige Integration einbeziehen, **nicht** als Pflicht-Freigabestufe.

**Einschränkung:** GitHub-Kommentare sind keine transaktionssicheren Locks. Wo technische Exklusivität nötig ist, muss sie am jeweiligen Host/Prozess überprüft und durchgesetzt werden. Die Änderung der Projektregeln deaktiviert keine Plattform-Approvals oder GitHub-Branch-Protection.
