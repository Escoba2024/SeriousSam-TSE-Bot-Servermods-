# TSE 1.07: Zentrale Agentenkoordination (A00–A09)

**Stand: 17.10.2026.** Dieses Dokument ergänzt `AGENTS.md` und die [verbindliche Toolpolicy](../decisions/2026-10-17-tse-ai-tools-mcp-policy.md). Bei Widersprüchen gelten die konservativeren Schutz-/Abnahmeregeln. **Agenten laufen nicht durch das bloße Anlegen dieser Dateien an und können andere Chat-Sessions nicht automatisch steuern.** Jeder aktive Agent muss die Regeln selbst übernehmen. Vor PR-Merge gelten diese Regeln als zur Übernahme vorgeschlagene Koordination.

## Ziele / Quelle der Wahrheit

- **Code, Branches, Pull Requests, technische Belege:** GitHub.
- **Live-Belegung, Schreibreservierung, Blocker, Übergaben:** GitHub-Koordinationsissue (in `STATUS.md` zu verlinken). Kein zweites konkurrierendes Notion-/Drive-Lockregister.
- **Gemeinsames Runtime-Labor:** Shadow und Hetzner, physisch getrennt von Git-Workspaces. Nur nach exklusiver Freigabe.
- **Notion / Drive:** lesbare Spiegel des Status, nicht operative Autorität oder Ersatz für GitHub-Belege.
- A00 verwaltet die Integrationswarteschlange; A00 bearbeitet **keinen** Supervisor-, DLL- oder Runtime-Code.

## Maximal zehn Slots – eine zuständige Schreibinstanz pro Modul

| Slot | Verantwortungsbereich | Exklusiver Standardscope (Schreiben) | Bestehende Arbeit / Grenze |
|---|---|---|---|
| **A00** | Koordination, PR-Triage, Integrations-Gates | `docs/coordination/**`, Koordinationsissue, Review-/Integrationsentscheidungen | Kein Gameplay-/Produktions-/Supervisor-Code |
| **A01** | Population-Supervisor, Readiness, UDP-Supervisor-Gates | `poc/scripts/PopulationSupervisor*.ps1`, `Manage-BotPopulation.ps1`; ausschließlich **ein** aktiver Supervisor-Integrationszweig | PR #3/#7/#10/#12/#13 bilden eine **sequenzierte Familie**; nicht parallel auf denselben Dateien schreiben |
| **A02** | Watchdog / Guardian / Prozessidentität | `poc/scripts/PopulationWatchdog.ps1`, `Watch-BotPopulation.ps1`, watchdog-spezifische neue Tests | PR #8/#11 sind Vorstufen von #12; `PopulationSupervisor.ps1` nur nach Übergabe an A01 |
| **A03** | Unabhängige portable QA, CI und Sicherheitstests | neue eigenständige Regressionen unter `tools/` / `poc/scripts/Test-*\` nach Freigabe; Review-Berichte mit eindeutigen Namen | Keine parallelen Änderungen an bereits von A01/A02 belegten Testdateien; PR #14 betrifft Fleet-Auditor |
| **A04** | Retail-Sync-Root-Cause und CRC-Analyse | neue `docs/reports/*sync*` (eigene IDs), `tools/analyze_sync_log.py` und eigene Parser-Tests nach Claim | PR #16; Original-Retail-DLLs nur lesen, 61DC-Kandidat bleibt geschützt |
| **A05** | Shadow native Retail-Abnahme, Join, Windows-Harness | neue Runtime-Berichte / Harness-Scope `poc/scripts/Test-RetailJoin*.ps1` nach Claim | PR #15/#17; **keine** Änderungen am laufenden Shadow-Test ohne Runtime-Lease |
| **A06** | Hetzner / Wine / öffentliche UDP-/333networks-Listung | eigene WAN-/Wine-Testberichte, `poc/HETZNER-*` nach Claim | Hetzner-Instanz und produktiver Port sind **exklusiv**; keine fremden Playerslots entfernen |
| **A07** | Bot-AI, Navigation, Combat | eigene `poc/release/gamemp/**`-Quellen und Botcore nach eigener Branch-/Runtime-Abnahme | keine Überschreibung der bekannten qualifizierten 61DC-DLL, keine unbelegte 1.07↔1.10-Annahme |
| **A08** | REA / GhidraMCP / Frida, reproduzierbare Binärdiagnose | neue Toolchain-/Analyseberichte, **eigene lokale Analyseprojekte** | REA, `ghidra_tse`, Frida nur isoliert; A04/A07 erhalten Findings statt gemeinsam in der DLL zu schreiben |
| **A09** | Alpha-Gaming-Webseite und Design | **separate** Repositories `AlphaWebBolt`, `alphawebgemini` bzw. separater Web-Ziel-Branch | Website heißt Alpha-Gaming; `#SamIsBack`/`#newSam` nur Kampagnen. Keine TSE-Runtime-Dateien |

**Wichtig:** Slots A01–A09 sind **vorgesehene Rollen**, keine Behauptung, dass neun Agenten verbunden, gestartet oder persönlich zugewiesen sind. Existierende PRs zeigen Arbeitsprodukte, nicht den Live-Status eines Chat-/Codex-Prozesses.

## Harte Kollisionsregeln

1. **Niemals** zwei Agenten im selben Git-Worktree. **Nie** das gemeinsam genutzte Shadow-Root-Checkout als Schreibworkspace eines neuen Agenten. Zulässiger Pfad: `C:\Users\Shadow\Documents\SeriousSam-TSE-Worktrees\agent-Axx-<ticket>`. Vor Anlage `git worktree list --porcelain`, `git status --short` und vorhandene Verzeichnisse prüfen; keine bestehenden Worktrees automatisch zurücksetzen/löschen.
2. Jede Arbeit besitzt ein Ticket/Issue, eine **eindeutige** Branch `agent/Axx/<ticket>-<kurzname>`, explizite Dateipfade und Akzeptanzkriterien. Alte `codex/*`-Branches bleiben unverändert, bis ihre Arbeit kontrolliert übernommen wird.
3. Ein Modul wird nur von **einem aktiven Writer** verändert. Für gemeinsam berührte Dateien (v.a. `PopulationSupervisor.ps1`, `tools/Test-Publication.ps1`, `poc/POPULATION-SUPERVISOR.md`) braucht es vorherige A00-Freigabe und serialisierte Übergabe. Dateieigentum ist eine **Schreibreservierung**, nicht das Verbot von Read-only-Review.
4. Vor schreibender Arbeit den Koordinationsissue lesen. `CLAIM` mit Slot/Ticket/Branch/Worktree/Dateien/Ressourcen/Laufzeit posten; **erst nach A00-`GRANTED`** beginnen. Kein eigener `GRANTED`-Kommentar; bei fehlender Antwort nur Read-only-Analyse.
5. Lease gilt maximal **4 Stunden**, Erneuerung vor Ablauf; `RELEASE` nach Handoff. Abgelaufene Lease autorisiert **keine** automatische Übernahme: A00 muss erst Prozessstatus, offenen Git-Status und Laufzeitbesitz prüfen. Bei unsicherem Zustand **BLOCKED / no write**.
6. **Runtime-Locks**: `SHADOW_RETAIL`, `SHADOW_GAME_FILES`, `HETZNER_RUNTIME`, `GHIDRA_TSE_PROJECT`, `RELEASE_MERGE`. Exklusiv pro konkreter Installation/Instanz, auch wenn Git-Dateipfade verschieden sind. Selbst eine bestehende Git-Lease erlaubt **nicht** automatisch Runtime-Zugriff.
7. **Passiver Review** ohne Schreib-/Runtimezugriff darf parallel laufen; Findings gehen ins eigene Ticket/PR-Kommentar. Falsche Belege/Schlüssel/Spielerprofile/Prozesslogs nicht öffentlich veröffentlichen.
8. Kein Agent führt selbstständig Merge, Force-Push, Rebase fremder Branches, laufende Prozesskills oder Bot-/Server-Deploy auf gemeinsam genutzten Instanzen aus. A00 prüft Merge-Gates; Runtime-Besitzer stimmt Test-/Deployzeitpunkt ab.
9. Statuswerte: `FREE` / `CLAIM_REQUESTED` / `GRANTED` / `RUNNING` / `BLOCKED` / `REVIEW` / `RELEASED`. Im Zweifel `UNKNOWN`, nie „frei“ aus fehlendem Signal ableiten.
10. Jede Übergabe nennt Commit-SHA, Branch, tatsächliche Tests, SKIPs, veränderte Dateien, Laufzeitfolgen, offenen Blocker und Folgeticket. Kein „PASS“ ohne zugehörige nachprüfbare Ebene.

## Integrationsreihenfolge und Konfliktzonen

**Roter Bereich Supervisor:** `#3 → #7 → #10` sowie `#8 → #11`, beide in **#12** zusammengeführt; **#13** erweitert #12 um Lock-Marker-Schutz. Diese Pfeile sind Abhängigkeits-/Reviewhinweise und **keine Aussage, dass ein PR gemergt wurde**. A00 bestimmt einen finalen gemeinsamen Kandidaten und vergleicht Merge-Base/Diffs, statt alle Vorstufen nacheinander in `main` zu mergen. Windows-/PS5.1- und native W1/W2-Gates bleiben offen.

**Getrennte QA-/Native-Familien:** #14 Fleet-UDP-Evidenz, #15 RetailJoin-Restore, #16 Sync-Parser und #17 Vanilla-Preflight. Bei Überlappung (`tools/Test-Publication.ps1` in #12/#15) läuft Zusammenführung **nacheinander** mit erneuten Tests.

**Entscheidungs-Gates:** (1) portable Tests und Versionsprovenienz, (2) sicherer Windows/PS5.1-Test, (3) isolierte echte Retail-1.07-Join-/Action-/Sync-Probe, (4) unabhängiger externer UDP-/Browser-Test, (5) lange Soak-/Skalierungsprüfung – jede Ebene gesondert dokumentieren. Keine 24/7-/16-Bot-Freigabe durch reine CI.

## Einweisung eines weiteren Agenten

1. `AGENTS.md`, Toolpolicy, dieses Dokument, `STATUS.md` und das Koordinationsissue lesen.
2. Slot **beantragen**, nicht eigenmächtig als frei behandeln; `CLAIM` posten und A00-`GRANTED` abwarten.
3. Eigenes Ticket/Branch/Worktree anlegen, bestehende Branches/aktive Prozesse unangetastet lassen.
4. Nur freigegebene Pfade/Ressourcen bearbeiten; bei unerwarteter Überschneidung **STOP / BLOCKED / A00 kontaktieren**.
5. Änderungsstand mit Tests/Handoff dokumentieren, PR eröffnen, `RELEASE` posten.

**Technische Einschränkung:** GitHub-Issue-Kommentare sind kein transaktionssicherer verteilter Mutex. Exklusivität entsteht hier durch **eine** entscheidungsbefugte A00-Instanz, konsequente Übernahme der Regeln und OS-seitige Prozess-/Dateisperren für konkrete Runtime-Proben. Bei unklarer oder fehlender A00-Freigabe keine Schreib-/Runtime-Aktion. Branch-Protection/Required Checks müssen separat in den Repository-Einstellungen aktiviert werden.
