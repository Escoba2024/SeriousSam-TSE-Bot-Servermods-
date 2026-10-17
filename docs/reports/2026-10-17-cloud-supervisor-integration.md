# Gemeinsamer Cloud-Integrationsnachweis und Runtime-Übergabe

17.10.2026. Isolierter Branch `codex/cloud-supervisor-integration-20261017`, PR-Basis **PR #10**. Gemeinsamer Code-/Test-Commit: `e475213ee138e22c84db7ed41c3b38d0126a97b8`.

## Zusammengeführter Stand

Vor Beginn alle Remote-Branches und Pull-Refs neu abgerufen und GitHub-PR-Metadaten geprüft:

| Quelle | geprüfter SHA |
|---|---|
| main | `39662e3757154540c1220fef0ebfcba67f5291eb` |
| PR #7, gemeinsame Vorbasis | `f56bbcdb403ffd6b8cfa85d585bc62e399a9f284` |
| PR #8, Watchdog | `9f9398ae91796cebfba667d4b8b6fcd204e90e45` |
| PR #10, Deadline/UDP/Cloud-Portierungen | `9d77adf99bb13fb3bf0ec981e3bf3288a3104680` |
| PR #11, Capture-Fix einschließlich PR #8 | `c7bb2cc407524ada82310540331707c092df8969` |

PR #11 wurde lokal zunächst ohne Commit auf PR #10 angewendet. Keine Textkonflikte. Die gemeinsame `PopulationSupervisor.ps1` wurde semantisch geprüft: frische gültige Readiness wird weiter vor dem Deadline-Timeout verarbeitet; Guardian-Start/Stop-Zweige bleiben erhalten und kehren vor direkter Prozesssteuerung zurück. UDP-Core entspricht exakt PR #10; Guardian, Launcher und Controller-CLI entsprechen exakt PR #11. Beide PR-HEADs sind Eltern des Integrationscommits. Kein Remote-Merge, kein Umschreiben der Quell-PRs, kein Merge nach main.

## Konkret belegte Integrationslücke

Der unveränderte PR-10-Publication-Runner entdeckte nach Integration zwei zusätzliche Windows-Prozesssuiten. Beide liefen unter Linux in `Start-Process -WindowStyle Hidden` auf Fehler: `Test-PopulationHardExitBoundary.Tests.ps1` und `Test-PopulationWatchdogProcess.Tests.ps1`. Der Runner erfasste beide FAILs und lieferte Exit 1; die übrigen Checks wurden ausgeführt.

Nur die explizite Windows-Klassifizierung des Runners wurde um diese zwei Namen erweitert. Unter Windows bleiben ihre Aufrufe unverändert. Keine Testassertion und kein Produktionsschutz wurde entfernt. Die zusätzlichen SKIPs bedeuten offene Windows-Integration. Insbesondere wird das in PR #11 dokumentierte Linux/.NET-Startzeitproblem nicht durch Toleranzen umgangen. `Test-PortableRegression.ps1` aus PR #8 bleibt unverändert und ist hier kein qualifizierter Linux-Einstieg; für diesen gemeinsamen Cloud-Umfang wurde `Test-Publication.ps1` verwendet.

## Ausgeführte Prüfungen

Debian 13, PowerShell 7.5.4, Python 3.12.14. Nur synthetische Fixtures, PowerShell-Hilfsprozesse und lokale UDP-Fixtures; keine Spielprozesse.

| Prüfung | tatsächliches Ergebnis |
|---|---|
| Gemeinsamer Stand, Runner unverändert | 26 PS PASS / 2 FAIL / 5 SKIP; Python 44 PASS; Provenance/Quellhashes 13 PASS; Exit 1 |
| Gemeinsamer Stand, zwei Windows-Klassifizierungen ergänzt | 26 PS PASS / 0 FAIL / 7 SKIP; Python 44 PASS; Provenance/Quellhashes 13 PASS; Exit 0 |
| Negativprobe `-Python /usr/bin/false` | 26 PS PASS / 7 SKIP; drei Python-Aufrufe und Provenance-Verifier FAIL/Exit 1; Hashprüfung weiter 13 PASS; Runner Exit 1 |
| Frischer Clone von `e475213` | 26 PS PASS / 0 FAIL / 7 SKIP; Python 44 PASS; Provenance/Quellhashes 13 PASS; Exit 0; Working Tree sauber |
| PowerShell-Syntaxprüfung der Skripte in `poc/scripts` und `tools` | PASS |
| Diff-/Schutzprüfung | `git diff --check` PASS; keine Änderung in `poc/patch` oder `poc/release` gegenüber PR #7 |

Der unabhängige Reviewer fand keine umsetzbaren Befunde und führte selbst aus: Deadline 9 Szenarien PASS, UDP 14 Parserprüfungen plus Start-Gate PASS, Safety 4770 Checks PASS, Capture 9 echte Hilfsprozessszenarien PASS. Er bestätigte den Erhalt beider Integrationszweige und die unveränderte Windows-Ausführung der zwei zusätzlich klassifizierten Suiten. Kein Windows-/Mailbox-/Retail-PASS durch diesen Reviewer.

Die sieben Linux-SKIPs sind fünf Windows-Suiten (`FleetProcessControl`, `LocalReleasePreparation`, `PopulationSupervisorAdapter`, `PopulationHardExitBoundary`, `PopulationWatchdogProcess`) und zwei native/private Gates (`RetailCleanup`, `LocalReleasePackage`). Die neue Capture-Suite läuft unter Linux tatsächlich und wird nicht ausgelassen. Vollständige bereinigte Statuszeilen stehen in [JSON](2026-10-17-cloud-supervisor-integration.json); private Logs und Prozessidentitäten bleiben außerhalb des Repository.

Reproduktion des Cloud-Umfangs:

```bash
git fetch origin '+refs/heads/*:refs/remotes/origin/*' '+refs/pull/*/head:refs/remotes/origin/pr/*'
git switch --detach e475213ee138e22c84db7ed41c3b38d0126a97b8
pwsh -NoProfile -File tools/Test-Publication.ps1 -Evidence /new/private/evidence -Python python3
# Erwartete Negativprobe auf Linux, separater Evidence-Pfad:
pwsh -NoProfile -File tools/Test-Publication.ps1 -Evidence /new/private/failure-evidence -Python /usr/bin/false
```

## Nächstes konkretes Runtime-Arbeitspaket

**W1: Gemeinsamen Stand auf isoliertem Windows qualifizieren.** Ein frisches Checkout von `e475213ee138e22c84db7ed41c3b38d0126a97b8` verwenden, bestehende Runtime dabei unangetastet lassen. Den Publication-Runner mit vorhandenem echtem Python und neuem privatem Evidence-Verzeichnis starten:

```powershell
pwsh -NoProfile -File tools/Test-Publication.ps1 -Evidence C:/TSE-QA/evidence/new-run -Python python
# Kompatibilitätsproben zusätzlich in Windows PowerShell 5.1:
powershell -NoProfile -File poc/scripts/Test-PopulationWatchdogCapture.Tests.ps1
powershell -NoProfile -File poc/scripts/Test-PopulationWatchdog.Tests.ps1
powershell -NoProfile -File poc/scripts/Test-PopulationWatchdogProcess.Tests.ps1
```

Gate: keine FAILs, insbesondere keine Windows-Plattform-SKIPs; nur die beiden expliziten native/private Gates dürfen beim regulären Publication-Aufruf fehlen. Der vollständige Guardian→Controller-Mailbox-Pfad muss Start/Stop/Start, Controller-Live-Hold, Hard-Exit vor/nach Launch-Bestätigung, persistenzbedingte Fehler, Lockkonkurrenz und unveränderten unabhängigen Kontrollprozess belegen. Capture-Fehler mit später lesbaren Metadaten und dauerhaft unlesbare Identität getrennt ausweisen. Dauerhaft unbewiesene Identität bleibt eine gemeldete Cleanup-Verweigerung.

**W2: Begrenzte native Grenzprüfung nach W1.** Ausschließlich separate qualifizierte Testinstallation, unveränderte 61DC-DLL und vor/nachher Hashschutz. Höchstens ein eigener Vier-Bot-Client; Human-/Observer-/Dedicated-Prozesse bleiben erhalten. Native normale Beendigung und erzwungenen Stop unterscheiden. Relevante Fälle:

- Readiness erstmals kurz vor/nach der 45-Sekunden-Grenze, einschließlich einer UDP-Abfrage, die die Grenze überschreitet; gültige frische Readiness verhindert falschen Timeout.
- Nach erfolgreichem Join Readiness-Verlust bei weiterlebendem Client sowie spätere Recovery; nur kurzzeitiger UDP-Verlust führt nicht zum sofortigen doppelten Gruppenstart.
- Unvollständige UDP-Antworten lösen keinen Start aus; gleichzeitig beitretende Menschen und reservierte Slots werden mit unabhängigen Statusbelegen erfasst. Keine atomare Einzelplatzgarantie aus dem Cloud-Modell ableiten.
- Controller-Hard-Exit während Join und nach Readiness: ausschließlich eigener Client bereinigt, Locks nach Cleanup frei, veraltete State-Dateien nicht adoptiert; ObserveOnly bleibt ohne Prozesssteuerung.

Zeitpunkte und Exitcodes mit monotoner Laufzeit, tatsächlichen Start-/Stop-Ereignissen sowie unabhängigen 1-Hz-UDP-Belegen dokumentieren. Bei Sync-Kick, Slotverlust, fremdem Prozesseingriff, unbewiesener Identität oder fehlgeschlagenem Cleanup keine Freigabe; private Evidenz behalten und nur bereinigte Zusammenfassung mit getesteten SHAs veröffentlichen. Dies ist ein Testauftrag, keine Aussage über bereits bestandene native Fälle.

**M4 bleibt separat:** Für 4-/8-Bot-Harness-Audit zuerst bestehende bereinigte private Skripte sowie Lowrender-/Vanilla-Voraussetzungen bereitstellen. Kein neuer Cloud-Harness, kein M1-/M3-Neubau und kein nativer Skalierungstest durch dieses Paket.

## Mergeempfehlung und Grenzen

Der gemeinsame Kandidat macht die bereits geprüften Korrekturen gemeinsam auscheckbar. Er bleibt **Draft**, bis W1 und die relevanten nativen Gates bestanden und unabhängig bewertet sind. PR #3/#7/#8 sowie #10/#11 werden durch diesen Cloud-PASS nicht automatisch freigegeben. Die Quell-PRs bleiben offen; bei später geändertem HEAD Ergebnisse nicht übertragen, sondern betroffenen Umfang neu prüfen.

Aktuelle main-AGENTS-/MCP-Vorgaben beachtet. Kein Zugriff auf aktive Shadow-/Hetzner-Runtime, keine Spiel-/Retail-Binaries, privaten GUIDs, Credentials oder Rohlogs veröffentlicht, keine DLL geändert oder neu qualifiziert. Die ausgewählte Linux-Publication meldet ausdrücklich `windowsPortableCoverageComplete=false` und `nativeRuntimeStarted=false`.
