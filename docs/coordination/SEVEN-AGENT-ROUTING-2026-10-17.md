# A00 – Sieben-Agenten-Routing und Kollisionsregister (17.10.2026)

**Status: Koordinationsvorschlag / PENDING_CLAIM, nicht GRANTED.** Maßgeblich sind [AGENTS.md](../../AGENTS.md), [README.md](README.md), [HANDOFF.md](HANDOFF.md), [INTEGRATION-GATES.md](INTEGRATION-GATES.md) und [Issue #18](https://github.com/Escoba2024/SeriousSam-TSE-Bot-Servermods-/issues/18). Dieses Dokument ergänzt die ältere funktionale Slot-Matrix; es ändert ohne bestätigte CLAIMs keine alten Rechte und startet keine fremden Agenten.

## Wichtige ID-Übersetzung (Namenskollision vermeiden)

Die sieben Chat-Rollen aus dem Auftrag sind **nicht identisch** mit den historischen A01–A09-Slotnummern. Insbesondere **Agent A5 (Audit)** ist **nicht** der bisherige A05-Slot (native Shadow-Tests).

| Bezeichnung im Chat | Historischer funktionaler Slot | Exklusiver Aufgabenfokus | Vorgemerkter Schreibbereich; formale Lease steht aus | Quellen |
|---|---|---|---|---|
| A00 | A00 | Zentralsteuerung, CLAIM/GRANT, Merge-/Konfliktentscheidungen | `docs/coordination/**`; Issue #18 | #18 / #19 |
| A1 (Engine) | A08 (Binärdiagnose); Codeänderungen getrennt nach A07-Claim | GameMP 1.07/1.10 ABI, CRC, Join/Sync; verifizierte Ghidra/REA-Befunde | **Nur neue** eindeutige `docs/reports/*abi*` / `*gamemp*` nach Claim; `poc/release/gamemp/**` **nicht** automatisch freigegeben | #9, vorhandener Sync-Bericht |
| A2 (Native) | A05 | Windows-PS5.1-/Retail-Harness, Restore, reproduzierbare Native-Gates | `poc/scripts/Test-RetailJoin.ps1`, `poc/scripts/Test-RetailJoinState.Tests.ps1`, neue eigene Native-Berichte; **kein** `tools/Test-Publication.ps1` | #15 / #5 |
| A3 (UDP) | A03 (QA/UDP); mit A05 für Preflight abzustimmen | Vanilla-/GameSpy-UDP-Framing, Preflight, Fleet-Evidenz | `tools/Test-TSEExternalVanillaPreflight*.ps1`, `poc/scripts/Test-FleetAIEvidence.py`, `poc/scripts/test_fleet_ai_evidence.py`, neue eigene UDP-Berichte | #17 / #14 |
| A4 (Sync) | A04 | SYNCBAD/CRC-Dumps, aligned Vergleich, Parser-/Fixture-Regressionen | `tools/analyze_sync_log.py`, `tools/test_analyze_sync_log.py`, `tools/compare_sync_dumps.py`, `tools/test_compare_sync_dumps.py`, eindeutige Sync-Berichte | #16 / #21 |
| WEB | A09 | Alpha-Gaming-Website, Darstellung/Design getrennt vom Retail-Bot-Code | ausschließlich `Escoba2024/AlphaWebBolt`, `Escoba2024/alphawebgemini` oder separater freizugebender Web-Zielbranch; **keine** TSE-Kernpfade | Web-Repos |
| A5 (Audit) | **eigene Auditrolle aus #20**; **nicht** A05 | Remote-/Local-Push-Nachweise, SHAs, Handoffs, Notion-/Drive-Spiegel | `docs/audits/**`, `docs/process/agent-handoff-contract.md`; **keine** `docs/coordination/**`-Writes | #20 / #22 |

Die Tabelle ordnet Arbeit **eindeutig zu** (vorgemerkte Ziel-Claims), ist aber **keine** nachträgliche `GRANTED`-Freigabe für bestehende Chatprozesse. Jeder Bearbeiter muss für konkrete Pfade/Branch/Worktree/Ticket einen aktuellen `CLAIM` nach `HANDOFF.md` selbst im Issue #18 veröffentlichen. A00 prüft Konflikte und vergibt dann eine auf maximal vier Stunden begrenzte Lease. Für alte `codex/*`-Branches bleibt der tatsächliche Eigentümer bis zur Bestätigung **UNKNOWN**.

## PR-Inventur und Merge-Verantwortung

- **Gemergt:** #19 / `eeb40426f77d223d9f0f07489598ed2cdeac8ec7`, ausschließlich Koordinationsregeln.
- **13 offene PRs zum Inventurzeitpunkt:** #3, #7, #8, #10, #11, #12, #13, #14, #15, #16, #17, #21, #22.
- **Gestapelte Supervisor-Familie:** #3 → #7 → #10; #7 → #8 → #11; Integration beider Zweige in #12; #13 basiert auf #12; **#14 basiert auf #13**, enthält ausschließlich Fleet-Auditor-Diff relativ zu #13. Vorstufen nicht unabhängig nacheinander in main mergen.
- **A00 ist einziger Merge-/Release-Entscheider** (Gate/Sequenz), **kein Supervisor-Codeautor**. Technische Codeintegration ist **UNASSIGNED / BLOCKED** bis zum separaten CLAIM eines geeigneten Supervisor-Eigentümers (historisch A01); A3 darf nur UDP-Scope ändern, A2 nur Native-Harness. Keine implizite Erweiterung der neuen Rollen.
- **Harter Konflikt:** `tools/Test-Publication.ps1` in #10/#12 **und** #15. Pfad `UNASSIGNED_CONFLICT_HOLD`. Gezielte serielle Integration in eigenem Worktree mit Eigentümerfreigabe und Windows/portable Regressionen; A00 entscheidet Merge erst danach.
- **Eigenständige Review-Spuren:** A4 #16/#21 (disjunkte Python-Dateien), A3 #17 (Preflight), A5 #22 (Dokumentationsaudit); #14 ist trotz eigenem Diff **gestapelt**. Kein Runtime-PASS durch synthetische Fixtures.

## Physische Ressourcen: einzeln und fail-closed

| Resource | Aktuelle Autorisierung | Vorgesehener einziger künftiger Owner | Freigabebedingung |
|---|---|---|---|
| `SHADOW_RETAIL` | **UNKNOWN/BLOCKED; keine GRANTED-Lease** | A2 | Eigentümer bisheriger Prozesse, exklusive isolierte Installation, SHA/Prozessbelegung, CLAIM |
| `SHADOW_GAME_FILES` | **UNKNOWN/BLOCKED** | A2 | Backup und exklusive Sicherung/Restore, keine produktive DLL ersetzen |
| `HETZNER_RUNTIME` | **UNKNOWN/BLOCKED** | A2 nur für abgestimmte Native-/WAN-Tests; bestehender Betreiber aus #6 hat Vorrang bis Übergabe | Host-/Port-/Fremdspieler-Belegung, Testkopie, aktiver Betreiber/HANDOFF/RELEASE verifiziert; A3 nur passives Protokollreview |
| `GHIDRA_TSE_PROJECT` | **UNKNOWN/BLOCKED** | A1 | isoliertes eigenes Projekt, korrekte `ghidra_tse`-Instanz, keine Konflikte mit anderen Analysen |
| `RELEASE_MERGE` | **A00 entscheidet allein; kein Merge-Gate erteilt** | A00 | dokumentiertes `READY_FOR_MERGE`, alle relevanten Gates |

Shadow-Read-only-Befund bei erneuter Inventur: **9 Worktrees** inkl. eigenem A00-Worktree; `main` lokal bei `d765fd2a5af3c17cbfe3036752ecb4ea5d986e93` und `error.log` untracked. Mindestens `codex.exe` PID **2304**, Sandbox-Service und PowerShell-Prozesse sichtbar. Das belegt **weder** laufende TSE-Tests **noch** freie Runtime. Kein Prozess wurde beendet/umkonfiguriert. Kein Hetzner-Remote-State überprüft. Kein fingierter Spieler-/PID-/Lease-Owner.

## Priorisierte Tickets und nächste überprüfbare Übergaben

1. **P0 / A00:** Rollen-/Pfad-Routing im #18 veröffentlicht; offene CLAIMs und alten Supervisor-Owner abgleichen. Ohne Handshake bleibt `NO_WRITE`.
2. **P0 / A1 + A4:** Ursache der divergierenden CRCs/SYNCCHECK-Snapshots eingrenzen: erst identischer Level/Sequence/Tick, erster abweichender State/Action-Wert; statisches Ghidra ist nicht native Root-Cause.
3. **P0 / A2:** #15 Restore-Gates gegen isolierte Windows/PS5.1-Kopie prüfen; #12/#13 fachlich read-only Windows-Gates planen. Keine produktive Runtime ohne Leases.
4. **P1 / A3:** #17 fail-closed UDP-Preflight reviewen; #14 im Stack #13 prüfen; keine Anpassung des Publication-Runners.
5. **P1 / A5:** #16/#17/#21/#22 und diese Koordination in Audit-Inventur aufnehmen; lokale SHA/upstream-Vergleiche nur nach legitimer read-only-Übernahme, Notion/Drive als Spiegel.
6. **P2 / WEB:** Alpha-Gaming-Branding in separaten Repos, keine `#SamIsBack`-/`#newSam`-Umbenennung der Marke; Frontend-Build/QA als eigener Handoff.
7. **P0 / A00 Integration:** Supervisor #12 + #13 + #14 als **einen** Kandidaten beurteilen, #15-Runnerverschmelzung explizit konfliktbehandeln; Windows-/Retail-/WAN-Gates vor finalem Merge entsprechend `INTEGRATION-GATES.md`. Wenn kein Code-Integrator mit Claim vorliegt: **BLOCKED**, nicht selbst Fachcode verändern.

**Meilenstein M-A00-7ROUTE:** sieben Rollen abgegrenzt, Kollisions- und Ressourcenentscheidungen dokumentiert, PR-Familie inventarisiert. **Nicht erreicht:** tatsächliche externe Agenten-Handoffs/Leases, technische PR-Integration, neuer Native-Retail-60m-/WAN-/Browser-PASS. Dieses Dokument ist ohne die Veröffentlichung in Issue #18 keine operative GRANTED-Lease.
