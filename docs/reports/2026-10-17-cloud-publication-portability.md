# Cloud-Fortsetzung: portable Publication-Prüfung

17.10.2026, Europe/Berlin. Folgeschritt zu [Supervisor-Review / PR #10](2026-10-17-cloud-supervisor-review.md). Basis `b92f0bc67ae507c059e747436daf3d9087b6ce6a`, Test-/Runner-Commit `711f8fd57f4cc0771137d72b1bd69d256902e3e1`. Alle Remote-Branches und PR-Refs erneut gelesen; main unverändert `4ca47d31294ac1fac1b4ecb5516c53a6f857e22b`, PR #7 weiterhin `f56bbcdb403ffd6b8cfa85d585bc62e399a9f284`. Keine neuen PR-10-Kommentare beim Start. Aktuelle main-Agenten-/MCP-Vorgaben weiter beachtet.

## Konkrete Änderungen

Vier der zuvor sieben roten Linux-Suiten wurden mit ihren ursprünglichen Assertions portiert:

- `Test-FleetAndPopulation.Tests.ps1`: echte absolute temporäre Pfade statt `C:`-Fixtures; Dateioperationen mit plattformtauglichen Separatoren. Negative Alias-/Duplikat-/Profil-/GUID-/State- und PID-Reuse-Prüfungen bleiben erhalten.
- `Test-FleetLaunchFailure.Tests.ps1`: synthetische Fixture-Dateien an den richtigen Pfaden; echte PowerShell-Kinder statt OS-abhängiger Fensteroption auf Linux. Launchfehler, State-Schreibfehler und kombinierter Fehler müssen weiterhin alle eigenen Kinder bereinigen und den unabhängigen Kontrollprozess erhalten.
- `Test-FleetStopCurrent.Tests.ps1` und `Test-FleetStopExitCode.Tests.ps1`: `WindowStyle=Hidden` nur auf Windows. Wirklich gestoppter eigener Konsolenprozess, unveränderter Prozess bei veralteter Startzeit und tatsächlicher Exitcode werden weiter geprüft. Erzwungener Konsolenstop bleibt ausdrücklich kein nativer regulärer Spiel-Shutdown.

Die CLI-/Loopback-UDP-/Readiness- und Identitätsprüfungen wurden unverändert aus `Test-PopulationSupervisorAdapter.Tests.ps1` nach `Test-PopulationQueryAdapter.Tests.ps1` verschoben. Der ursprüngliche Dateiname enthält weiterhin den echten Windows-CIM-Cleanup-Test einschließlich disk-unabhängigem Stop. Keine Assertion entfernt und kein Windows-CIM durch einen Linux-Mock ersetzt. Die portable Suite wird nun als eigener vollständiger Test ausgeführt und bereinigt ihre synthetischen Dateien.

`tools/Test-Publication.ps1` führt die verfügbaren Checks bis zum Ende aus und schreibt alle PASS/FAIL/SKIP einschließlich Exitcode beziehungsweise Startfehler in `result.json`. Eine fehlgeschlagene Prüfung ergibt am Ende einen Fehlerexit. Unter Linux werden nur die drei nachweislich Windows-abhängigen Suiten explizit ausgelassen; auf Windows werden sie weiterhin ausgeführt. Die bestehenden beiden native/private Ausschlüsse bleiben erhalten. Die Summary kennzeichnet den ausgewählten Scope und `windowsPortableCoverageComplete=false` unter Linux; ein portabler PASS ist keine vollständige Windows-Abnahme.

Der Runner verwendet den ersten ausführbaren Python-Treffer im PATH. Ein Zwischenlauf hatte mehrere `Get-Command`-Treffer zusammen als Pfad interpretiert und die vier Python-/Provenance-Aufrufe korrekt als FAIL erfasst; die Auswahl ist in `711f8fd` korrigiert. Testanzahlen werden aus tatsächlich erfolgreichen unittest-Ausgaben gelesen, statt stets 44 zu behaupten.

Keine Änderung an Supervisor/Core, nativen Prozess-/CIM-Adaptern, Release-Staging, Botcode oder qualifizierter DLL gegenüber `b92f0bc`. Keine Spielprozesse oder aktive Shadow-/Hetzner-Runtime verwendet. Synthetische Binärformat-Fixtures sind keine Retail-Dateien und bleiben privat/temporär.

## Tatsächliche Ergebnisse

Umgebung weiterhin Debian 13, PowerShell 7.5.4, Python 3.12.14.

| Prüfung | Ergebnis |
|---|---|
| Vier unveränderte Suiten auf `b92f0bc` | 4 FAIL, bekannte Pfad-/WindowStyle-Ursachen reproduziert |
| Dieselben vier Suiten nach Fixture-Korrektur | 4 PASS, echte PowerShell-Kinder und unveränderte Assertions |
| Getrennte CLI-/UDP-/Readiness-Suite | PASS, echte Loopback-UDP-Anfragen, vollständiger ObserveOnly-Aufruf und Startzeit-/Readiness-Prüfungen |
| Regulärer Publication-Aufruf, `711f8fd` | **23 PowerShell-Suiten PASS, 0 FAIL, 5 SKIP**, **44 Python-Fixtures PASS**, **13 veröffentlichte Quellen + Original-Captures PASS**; Exit 0 |
| Neuer separater Clone von `711f8fd` | gleicher Publication-Umfang und Ergebnisse, Exit 0; sauberer Baum |
| Absichtlicher Python-Exit 1 über `/usr/bin/false` | alle 23 PS-Suiten beendet; drei Python-Suiten und Provenance-Verifier jeweils FAIL/Exit 1, Hashprüfung weiter ausgeführt; `passed=false`, Runner Exit 1 |
| Schon vorhandener Evidence-Ordner | vor allen Tests abgelehnt; vorhandene `result.json` hashgleich, Exit 1 |
| PowerShell-Syntaxprüfung | alle Testdateien und Runner ohne Parsefehler |
| Unabhängiger separater Reviewer | keine umsetzbaren Befunde; Assertionserhalt, positive/negative Ergebnisse und Startfehler-Behandlung geprüft |

Die fünf expliziten SKIPs:

1. `Test-FleetProcessControl.Tests.ps1`: Windows-CIM und ntdll Suspend/Resume fehlen auf Linux.
2. `Test-LocalReleasePreparation.Tests.ps1`: Windows-Pfadsemantik des bestehenden Release-Stagings; nicht als Linux-Staging erweitert.
3. `Test-PopulationSupervisorAdapter.Tests.ps1`: echte Windows-CIM-Ownership-/Cleanup-Integration; portable Teile laufen separat.
4. `Test-LocalReleasePackage.Tests.ps1`: qualifizierte private SDK-Artefakte fehlen, bisheriger Ausschluss.
5. `Test-RetailCleanup.Tests.ps1`: echte Retail-Session erforderlich, bisheriger Ausschluss.

Die ursprünglichen sieben FAILs werden damit nicht nachträglich umgedeutet: vier wurden tatsächlich repariert und neu bestanden; die übrigen drei sind weiterhin unerprobte Windows-Integration und werden im ausgewählten Linux-Scope ausdrücklich SKIP. Die zusätzliche portable Suite erklärt den Anstieg von 18 auf 23 PASS. [Bereinigte Einzelergebnisse](2026-10-17-cloud-publication-portability.json); keine privaten Rohlogs veröffentlicht.

## Reproduktion

```bash
git fetch origin '+refs/heads/*:refs/remotes/origin/*' '+refs/pull/*/head:refs/remotes/origin/pr/*'
# Eigenen Branch/Commit in einem frischen Checkout verwenden.
git switch codex/cloud-supervisor-review-20261017
pwsh -NoProfile -File tools/Test-Publication.ps1 -Evidence /new/private/evidence -Python python3
```

Auf Windows denselben Runner mit vorhandenem Python ausführen: die drei Windows-Suiten werden dort nicht übersprungen. Die beiden native/private Suiten bleiben eigenständige Gates; `-IncludeLocalPackageFixtures` nur mit tatsächlich vorhandenen privaten Paketvoraussetzungen setzen. Keine Spieldateien aus Cloud-Tests ableiten oder veröffentlichen.

Negativprobe auf Linux, ausschließlich Tests:

```bash
pwsh -NoProfile -File tools/Test-Publication.ps1 -Evidence '/new/private/failure evidence' -Python /usr/bin/false
# Erwartet: vier dokumentierte fehlgeschlagene Python-/Provenance-Aufrufe,
# verbleibende Prüfungen dennoch erfasst, result.json mit passed=false, Exit ungleich 0.
```

## Verbleibende Gates

PR #10 bleibt Draft für Windows-Publication und den bereits beschriebenen gezielten nativen Deadline-/Recovery-/Human-Race-Test. Der unabhängige Reviewer hat Windows/PowerShell-5.1-Kompatibilität statisch geprüft; ausgeführt wurde Windows hier nicht. PR #3/#7/#8 werden nicht automatisch gemergt oder umgeschrieben.

M4 bleibt unverändert an den fehlenden bereinigten privaten Linux-Harnessquellen und echten Lowrender-/Vanilla-Prerequisite-Belegen begrenzt. Dieses Paket erweitert die Cloud-Regression und ersetzt keine M1-/M3-/M4-Runtime-Abnahme. Nächster Runtime-Schritt bleibt die begrenzte Windows-/Supervisor-Grenzprüfung; für M4 zuerst vorhandene Harnessquellen zur Prüfung bereitstellen.
