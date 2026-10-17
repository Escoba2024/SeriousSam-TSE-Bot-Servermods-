# Cloud-Fortsetzung: Integrität gespeicherter UDP-Belege

17.10.2026. Branch `codex/cloud-query-evidence-validation-20261017`, Basis PR #13 `c43d14382c2fc4bf5b80e3f26ee957193c971db9`. Geprüfter Code-/Test-Commit: `86556fc9a81fc5b69735a6d30ae2e59944771005`.

Vor Beginn alle Remote-Branches und PR-Refs neu abgerufen. main weiterhin `39662e3757154540c1220fef0ebfcba67f5291eb`. Das Paket ändert nur den vorhandenen Python-Flottenauditor und seine synthetischen Tests, keine Harness-/Controller-/DLL-/Release-Quellen. Aktuelle main-AGENTS-/MCP-Vorgaben beachtet; keine aktive Shadow-/Hetzner-Runtime, Spielprozesse, privaten Rohlogs oder Retail-Dateien verwendet.

Beim abschließenden Abruf main `375b995d0e3e3f0cf31da4f427b4cc1a062f0a9c`: neue AGENTS-Vorgaben, [Retail-1.07-Sync-Bericht](https://github.com/Escoba2024/SeriousSam-TSE-Bot-Servermods-/blob/375b995d0e3e3f0cf31da4f427b4cc1a062f0a9c/docs/reports/2026-10-17-retail107-sync-check-investigation.md) und lesender `tools/analyze_sync_log.py` vollständig gelesen. Sie ändern weder diesen Auditor noch PR #13. Keine Übernahme nach diesem Branch und kein neuer Cloud-Nachweis der dort extern dokumentierten nativen Läufe. Die dort genannten fehlgeschlagenen Sync-Läufe bleiben von separat bestandenen Stunden getrennt; Ursache der CRC-Divergenz offen. Vor weiteren nativen Proben insbesondere die dokumentierte fehlende automatische DLL-Wiederherstellung in `Test-RetailJoin.ps1` beachten; separate Testinstallation oder ausdrücklich gesicherten Restore-Pfad verwenden. Qualifizierte 61DC-DLL unangetastet lassen, Sync-Kick-Grenze nicht zur Scheinfreigabe deaktivieren. Der neue Sync-Parser wurde in diesem Paket gelesen, aber nicht eigenständig qualifiziert.

## F6 – P2: beschädigte Queries zählen als vollständiger Fleetbeleg

`audit_queries` in `Test-FleetAIEvidence.py` suchte einzelne Statusfelder und Spielernamen mit Regex an beliebigen Stellen im Text. Die Suche prüfte weder vollständiges Framing noch den final-Marker und zählte Namen ohne eindeutige numerische Spielerindizes. Somit konnten acht erwartete eindeutige Namen selbst dann einen vollständigen Steady-Beleg ergeben, wenn zwei unterschiedliche Namen denselben Spielerindex hatten.

Auf unverändertem PR #13 synthetisch reproduziert: korrekte drei Samples mit 120 Sekunden Spanne akzeptiert; danach wurden auch dieselben Samples mit Fremdpräfix, abgeschnittenem angehängtem Feld, fehlendem final oder doppeltem Spielerindex akzeptiert. Das ist ein falsches positives Ergebnis der gespeicherten Query-Auswertung, kein Nachweis eines solchen Fehlers in einer bestimmten nativen Abnahme.

## Minimale Korrektur

`query_fields` liest die Feldpaare strukturiert. Sie müssen den gesamten Eingabestring abdecken; doppelte Schlüssel und ein fehlender oder nichtleerer final-Wert führen zu FAIL. `audit_queries` verwendet diese Prüfung für Status und Spielerantwort. Spielerindizes werden anschließend numerisch auf Eindeutigkeit und Bereich 0–15 geprüft.

Vorhandene Versions-/Mod-/Identitäts-/Zähler-/Dauer-/Abstands-/Lifecycle-Prüfungen bleiben erhalten. `queryid` ist weiterhin optional. Ein Spieler namens `final` bleibt zulässig, weil Werte nicht als Protokollschlüssel interpretiert werden. Die vorhandene explizite `eight-bots`-Startup-Ausnahme für eine noch partielle Spielerliste bleibt getrennt von Steady-Messungen; eine solche Liste ohne Übergangslabel wird abgewiesen.

Nur synthetische Positivfixtures wurden um echte Abschlussmarker ergänzt. Fehlende Marker in tatsächlichen gespeicherten Antworten dürfen nicht nachträglich ergänzt werden, um ein PASS zu erhalten. Die vorhandenen Retail-Collector-Quellen speichern die Rohantwort von `Invoke-FleetQuery`; ihre native Ausführung und vorhandene private Captures wurden hier nicht geprüft.

## Regressionen und unabhängige Prüfung

Sechs zusätzliche Testmethoden prüfen:

- Fremdpräfix, abgeschnittenes Feld und einzelnes Schluss-Backslash in beiden Antworttypen.
- Fehlenden und nichtleeren final-Marker in beiden Antworttypen.
- Doppelte Statusfelder und doppelte Spielerfelder bei weiterhin acht eindeutigen Namen.
- Aliasindizes (`0`/`00`) und Index 16.
- Gültige Antworten ohne queryid und einen Spieler namens final.
- Markierten partiellen Startup-Übergang gegenüber derselben unvollständigen Steady-Liste.

Die neue Suite gegen den alten Auditor ergab **31 Tests, 14 fehlgeschlagene negative Subtests, Exit 1**. Nach Korrektur bestehen alle 31 Tests. Ein unabhängiger Reviewer fand keine umsetzbaren Befunde, bestätigte den Assertionserhalt und führte die 31 Tests sowie `git diff --check` selbst aus. Keine neue Python-Versionsanforderung erkennbar; ausgeführt wurde Python 3.12.14.

| Ausgeführter Scope | Ergebnis |
|---|---|
| Neue Query-Regressionen gegen Baseline | FAIL / Exit 1, beschädigte Replies akzeptiert |
| Korrigierter Flottenauditor | 31 Python-Tests PASS |
| Gemeinsamer Publication-Lauf nach Fix | 27 PS PASS / 0 FAIL / 7 SKIP; 50 Python-Tests (31+9+10) PASS; 13 Provenance-/Quellhashprüfungen PASS; Exit 0 |
| Frischer separater Clone von `86556fc` | 27 PS PASS / 0 FAIL / 7 SKIP; 50 Python-Tests PASS; 13 Provenance-/Quellhashprüfungen PASS; Exit 0; Working Tree sauber |
| Source-Scope / Schutz | Controller, Guardian, Runner, `poc/patch` und `poc/release` gegenüber PR #13 unverändert |

Die 27 PS-Suiten und sieben Windows/native/private SKIPs bleiben unverändert. Die sechs zusätzlichen Python-Methoden erklären den Anstieg von 44 auf 50. Der Runner ermittelt diese Anzahl aus den tatsächlichen unittest-Ausgaben. Seine bereits geprüfte Negativprobe wurde ohne Runneränderung nicht erneut ausgeführt. [Bereinigte Einzelstatus](2026-10-17-cloud-query-evidence-review.json).

Reproduktion im Checkout des geprüften Commits:

```bash
python3 -B poc/scripts/test_fleet_ai_evidence.py
pwsh -NoProfile -File tools/Test-Publication.ps1 -Evidence /new/private/evidence -Python python3
```

## M4-Grenzen und nächstes Runtime-Paket

Dies ist eine gezielte Korrektur des vorhandenen Auditors. Kein neuer Linux-Harness und keine erneute Implementierung bestandener M1-/M3-Abnahmen. Ohne Auswertung der tatsächlichen privaten Evidenz wird keine historische Abnahme nachträglich als PASS oder FAIL eingestuft.

Der Auditor bleibt für seinen dokumentierten Windows-2×4-Scope ausgelegt: Query-/Ressourcenabstand bis 60 Sekunden, feste Prozessrollen und PID-basierte Ressourcenserie. Das ist kein unabhängiger 1-Hz-M4-Nachweis. Prozess-Startidentität, Host-Steal/PSS, vollständige monotone Wall-/Tick-Zuordnung und 20-Hz-Drift-SLOs werden durch diesen Patch nicht ergänzt. Die bestehenden Sync-/Logprüfungen bleiben unverändert. Vorhandene private 4-/8-Harnessquellen und Lowrender-/Vanilla-Voraussetzungen bleiben die Vorleistung aus [M4-Preflight](../../poc/HETZNER-M4-CLOUD-PREFLIGHT.md).

Für den nächsten gemeinsamen W1/W2-Test jetzt `86556fc9a81fc5b69735a6d30ae2e59944771005` verwenden; enthält auch die bisherigen Deadline-/UDP-/Guardian-/Capture-/Lock-Korrekturen. Unter Windows mit vorhandenem Python den Publication-Runner ausführen, danach die offenen Windows/PowerShell-5.1-/Mailbox-/Lock-/Hard-Exit-Gates und begrenzten nativen Recovery-/Human-Race-/Cleanup-Prüfungen aus den [Integrations-](2026-10-17-cloud-supervisor-integration.md) und [Lock-Berichten](2026-10-17-cloud-lock-marker-review.md) abschließen. Vollständigen Query-Ausfall weiterhin getrennt prüfen; keine pauschale 45-Sekunden-Garantie.

Vor einer neuen nativen Auswertung prüfen, dass gespeicherte Rohantworten ihren tatsächlichen final-Marker enthalten. Den korrigierten Auditor gegen die echte private Evidenz anwenden und nur bereinigte Ergebnisse samt Eingabe-/Code-SHAs veröffentlichen. Kein PASS aus synthetischen Fixtures auf native Spielstunden übertragen. Der neue PR bleibt Draft; keine Remote-Merges, keine neue DLL-Qualifikation und kein Zugriff durch Cloud auf aktive Runtime.
