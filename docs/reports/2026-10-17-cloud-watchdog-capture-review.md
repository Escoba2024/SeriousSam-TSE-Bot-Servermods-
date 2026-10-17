# Unabhängige Cloud-Fortsetzung: Watchdog-Identitätserfassung

17.10.2026, Europe/Berlin. Neuer isolierter Branch `codex/cloud-watchdog-capture-20261017`, **Basis PR #8**, nicht PR #10 oder main. PR-8-HEAD erneut abgerufen: `9f9398ae91796cebfba667d4b8b6fcd204e90e45`. Fix: `fb90287206a662983770d9b4790af917004e15dc`.

Alle Remote-Branches und Pull-Refs vor Beginn neu gelesen. main war dabei `39662e3`; aktuelle AGENTS-/MCP-Vorgaben gelesen. Kein Aufruf von Shadow/Hetzner, Ghidra/Frida oder aktiver Runtime. PR #10 und dessen aktuelle Cloud-Portierungen bleiben separat; keine ungeprüfte Zusammenführung, keine Force-Pushes, keine Änderungen an qualifizierter GameMP-DLL, Botcode, Retail-Dateien, Credentials oder privaten Rohlogs.

## F4 – P2 / wichtig: temporärer Capture-Fehler hinterlässt dauerhaft unvollständigen Besitzdatensatz

Der bisherige Watchdog speicherte nach `Start-Process` zunächst den tatsächlichen Prozess mit `StartedUtc=null`, bevor `New-PopulationWatchdogIdentity` die vollständigen Metadaten erfasst. Scheitert die Erfassung, bleibt dieser vorläufige Record erhalten. Selbst wenn die Metadaten beim späteren Cleanup wieder lesbar sind, vergleicht der Stop die echte Startzeit weiterhin mit dem fehlenden Wert. Der eigene Prozess wird nicht gestoppt; `cleanupPassed=false`, ein neuer Guardian verweigert später den schon laufenden Client.

Reproduziert mit einem **echten PowerShell-Kindprozess** auf unverändertem PR-8-Code: erster Startzeit-Lesezugriff künstlich fehlerhaft, danach lesbar; Original-Cleanup ergibt false und der Kindprozess bleibt aktiv. Anschließender Test-Teardown beendet ausschließlich den eigenen gehaltenen Prozess. Das ist ein Code-/Hilfsprozessnachweis, kein nativer Spiel- oder vollständiger Controller-/Mailbox-Test.

## Minimale Korrektur

- `Register-PopulationWatchdogChild` kapselt die bestehende Registrierung des wirklich gestarteten Kindes. Der vorläufige Record bleibt vor Metadaten-/Datei-/Antwortfehlern im Speicher erhalten.
- `CapturePending=true` wird erst nach tatsächlich verfügbarem, nichtnull Handle gesetzt. Fehlendes erfolgreiches Pinning ist keine Wiedererfassungsberechtigung.
- Beim autorisierten Stop beziehungsweise Cleanup eines bestätigten Controller-Exits darf dieser markierte Record seine Identität am **selben gehaltenen Prozessobjekt** erneut erfassen. Owner und PID werden davor geprüft; vollständiger EXE-/Startzeitvergleich erfolgt weiterhin vor Kill.
- Dauerhaft unlesbare Metadaten, falscher Owner/PID/EXE, gescheitertes Pinning und ein fehlender Zeitstempel ohne Pending-Markierung bleiben Stop-Verweigerungen mit Fehlerstatus. Keine Adoption aus Dateien, kein neuer PID-Lookup, kein Namens-/Baum-Kill und keine Toleranz im Startzeitvergleich.

Der Controller-Live-Guard in `Invoke-PopulationOrphanCleanup` bleibt unverändert: keine Wiedererfassung oder Prozesssteuerung allein wegen eines laufenden Controllers. Ein ausdrücklicher gültiger Stop-Auftrag des Controllers ist davon wie bisher getrennt.

## Regression und Review

`Test-PopulationWatchdogCapture.Tests.ps1` startet pro Fall eigene echte PowerShell-Hilfsprozesse als Controller, Client und unabhängige Kontrolle. Metadaten-Proxies injizieren Fehler, während Handle-, Exit-, Kill- und Wait-Aufrufe die echten gehaltenen Objekte verwenden. PowerShells `Process.Path`-Typdatenproperty lässt sich am tatsächlichen Objekt nicht direkt überschreiben; deshalb ist diese Proxy-Grenze explizit. Keine Betriebssystemprozess-IDs erfunden oder an fremde Prozesse gerichtete Stop-Aufrufe.

Neun Szenarien: normaler Capture, einmalig fehlgeschlagene Startzeit, nach dem bisherigen 500-ms-Fenster verfügbarer Pfad, dauerhaft unlesbarer Pfad, falscher Owner, falsche PID, falsche EXE, gescheitertes Pinning und unmarkiert fehlender Startzeitstempel. In jedem Fall bleibt der Client bei lebendem Controller unangetastet und der unabhängige Prozess erhalten. Erfolgreicher Cleanup ist idempotent; verweigerter Cleanup wird nicht als Erfolg ausgegeben. Finaler Test-Teardown nutzt ausschließlich seine tatsächlichen Launchobjekte.

Die neue Registrierungsfunktion fehlte zunächst (RED). Zusätzlich wurde die entscheidende Verhaltensregression geprüft: In einer **separaten Scratch-Kopie** nur den Retry entfernen, Registrierung beibehalten → `Recoverable capture failure orphaned real child: TransientStartTime`, Exit 1. Vollständiger Fix → neun Szenarien PASS. Der direkte Baseline-Reproducer oben belegt den ursprünglichen Defekt unabhängig von der neuen Hilfsfunktion.

Unabhängiger separater Reviewer für `9f9398a..fb90287`: keine umsetzbaren Befunde; neue neun Szenarien und bestehende 35 Ownership-Checks eigenständig PASS. Windows/PowerShell 5.1 und vollständige Mailbox-Integration wurden auch vom Reviewer nicht ausgeführt.

## Tatsächlich ausgeführte Matrix

Debian 13, PowerShell 7.5.4, Python 3.12.14. Jede entdeckte zugelassene PowerShell-Suite wurde in einem eigenen Prozess ausgeführt; Fehler wurden weiter inventarisiert. Der Sammelprozess ist kein grünes Gesamtergebnis.

| Scope | PASS | FAIL | SKIP |
|---|---:|---:|---:|
| Unverändertes PR-8-Archiv `9f9398a`, inklusive ShadowRuntimeLog | 16 PS-Suiten | 11 PS-Suiten | 2 |
| Fix `fb90287`, inklusive neuer Capture-Suite | 17 PS-Suiten | dieselben 11 PS-Suiten | 2 |
| Frischer separater Clone von `fb90287` | 17 PS-Suiten | dieselben 11 PS-Suiten | 2 |
| Bestehende Watchdog-Ownership-Suite | 35 Checks | 0 | 0 |
| Bestehende Safety-Boundaries-Suite | 4770 Checks | 0 | 0 |
| Neue Capture-Suite | 9 Prozessszenarien | 0 | 0 |
| Unveränderte Python-Fixtures | 44 (25+9+10) | 0 | 0 |
| Source-Provenance | 13 Quellen + Original-Captures | 0 | 0 |

Alle elf FAILs treten bereits ohne diesen Fix auf:

- `Test-FleetAndPopulation.Tests.ps1`: Windows-Pfadfixture unter Linux nicht absolut.
- `Test-FleetLaunchFailure.Tests.ps1`, `Test-FleetProcessControl.Tests.ps1`, `Test-FleetStopCurrent.Tests.ps1`, `Test-FleetStopExitCode.Tests.ps1`, `Test-PopulationHardExitBoundary.Tests.ps1`, `Test-PopulationReadinessRecovery.Tests.ps1`, `Test-PopulationSupervisorAdapter.Tests.ps1`, `Test-PopulationWatchdogProcess.Tests.ps1`: Windows-only `-WindowStyle` verhindert die unveränderte Ausführung.
- `Test-PopulationSupervisorControl.Tests.ps1`: derselbe unterdrückte WindowStyle-Startfehler führt zur Assertion `Start/resume after cooldown failed`.
- `Test-LocalReleasePreparation.Tests.ps1`: Windows-Staging-/Pfadsemantik.

SKIP: RetailCleanup braucht eine echte Retail-Session; LocalReleasePackage braucht private qualifizierte SDK-Artefakte. Die zusätzliche private Auto-Combat-Evidence-Suite wurde mangels ihrer privaten Argumente nicht ausgeführt. [Bereinigte Einzelstatus](2026-10-17-cloud-watchdog-capture-review.json).

Der engere portable Scope in **PR #10** besitzt andere Basis und zusätzliche Portierungen; dessen 23 PASS / 5 SKIP sind nicht das Ergebnis dieses Watchdog-Branches. Die dortigen Deadline-/UDP-Korrekturen wurden hier nicht dupliziert. PR #8 erbt diese weiterhin offenen gemeinsamen Befunde bis zur regulären Integration.

## Linux-Transportgrenze, nicht gelockert

Eine zunächst versuchte vollständige Hilfsprozess-/Mailbox-Probe scheiterte unter Linux schon am unveränderten `Test-PopulationWatchdogPeer`. Eine isolierte Gegenprüfung zeigte gleiche reale PID und gleichen EXE-Pfad, aber unterschiedliche Startzeit-Ticks desselben Prozesses in zwei .NET-Prozessen (in der Probe 7143 Ticks / 0,7143 ms). Daher wurde kein kompletter Watchdog-Transport-PASS behauptet. Das ist ein konkreter Linux/.NET-Portabilitätsbefund dieses Windows-orientierten Transportes, kein hier behobener Retail-Fehler und kein Grund, PID-Reuse-Guards zu lockern.

Vollständiger Watchdog-Start/Stop, normale Beendigung, Hard-Exit, Protokoll-/Datei-Races und fehlgeschlagene Metadaten im gesamten Guardian→Controller-Pfad bleiben auf Windows unabhängig zu prüfen. Ein dauerhaft unlesbares eigenes Kind bleibt absichtlich ein dokumentierter Fail-closed-Orphan; es wird nicht unbekannt beendet.

## Reproduktion und nächstes Runtime-Paket

```powershell
pwsh -NoProfile -File poc/scripts/Test-PopulationWatchdogCapture.Tests.ps1
pwsh -NoProfile -File poc/scripts/Test-PopulationWatchdog.Tests.ps1
pwsh -NoProfile -File poc/scripts/Test-PopulationSafetyBoundaries.Tests.ps1
python -B poc/scripts/test_fleet_ai_evidence.py
python -B poc/scripts/test_obstacle_evidence.py
python -B poc/scripts/test_local_release_smoke.py
python -B tools/Verify-SourceProvenance.py
```

Für die breite Inventur jede `poc/scripts/*.Tests.ps1` separat ausführen, außer den zwei expliziten native/private SKIPs; LocalReleasePreparation benötigt zusätzlich `-Evidence <neuer privater Ordner>`. Danach `tools/Test-ShadowRuntimeLog.ps1`. Auf Linux bestehen die oben genannten elf Suiten unverändert nicht; auf Windows sind sie echte offene Prüfungen. Kein grünes Publication-Gesamtgate für diesen Branch behauptet.

Nächstes Runtime-Arbeitspaket für PR #8: frisches isoliertes Windows-Checkout dieses Fixes, neue Capture-Suite (auch PowerShell 5.1), bestehende Ownership-/WatchdogProcess-/HardExit-/Safety-Suiten und gemeinsame PR-10-Fixes geordnet prüfen. Danach begrenzter nativer Guardian-Lauf mit unveränderter 61DC-DLL: Start/Join und Hard-Exit, höchstens ein eigener Client, kein Stop bei bloß lebendem Controller, erhaltene Human-/Observer-/Dedicated-Prozesse, Hashschutz und exakter Cleanup. Transiente Capture-Fehler vor Bestätigung und echte dauerhaft unlesbare Identität als getrennte FAIL-/Recovery-Grenzen ausweisen.

**Mergeempfehlung:** PR #8 unverändert wegen F4 nicht bedingungslos freigeben. Eigener enger Fix-PR bleibt Draft bis Windows-/Integrationsgate. PR #10 und native Gates nicht überspringen. M4-Harnessquellen/Lowrender-Prerequisites weiterhin separat offen; keine neue M1-/M3-Implementierung oder Spielausführung.
