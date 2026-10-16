# Unabhängiger Cloud-Review: PR #7 und PR #3

Stand: 17.10.2026 (Europe/Berlin). Ausschließlich Code-/Cloud-Regression; keine Shadow-/Hetzner-Verbindung, keine Spielprozesse, keine neue DLL oder native Spielabnahme.

Fortsetzung nach diesem ursprünglichen Reviewstand: [portable Publication-Prüfung](2026-10-17-cloud-publication-portability.md), Test-/Runner-Commit `711f8fd`. Dort sind vier der sieben Linux-Fehler tatsächlich portiert, der CLI-/UDP-Test separat ausführbar und die drei verbleibenden Windows-Abhängigkeiten ausdrücklich ausgewiesen. Die untenstehenden 18 PASS / 7 FAIL / 2 SKIP bleiben der historische Lauf von `d67bc6b`.

## Geprüfte Identitäten und Quellen

| Referenz | Neu gelesener Commit | Bedeutung |
|---|---|---|
| main zu Arbeitsbeginn | `f4a1a336e271e21bc01df430847bf3fda08b122d` | ursprüngliche Basis |
| PR #3 | `11b57e74c8f990e631822dc6b1472a6a1918c7ea` | Population-Supervisor, Draft gegen main |
| PR #7 | `f56bbcdb403ffd6b8cfa85d585bc62e399a9f284` | Recovery, gegen PR-3-Branch |
| PR #8 | `9f9398ae91796cebfba667d4b8b6fcd204e90e45` | vorhandener Watchdog-Draft gegen PR #7 |
| main bei erneuter Prüfung | `4ca47d31294ac1fac1b4ecb5516c53a6f857e22b` | parallel ergänzt: AGENTS.md und MCP-Richtlinie; kein Supervisor-Codewechsel |
| geprüfter Fix | `d67bc6b362d159329070d05acde80159c906df9f` | eigener Branch `codex/cloud-supervisor-review-20261017`, Basis PR #7 |

Alle Remote-Branches und Pull-Refs wurden ausdrücklich neu abgerufen. Der vorhandene Cloud-Checkout war nur für main konfiguriert; ein einfaches `fetch --all` hätte die weiteren Branches nicht erfasst. Frischer separater Clone, sauberer Ausgangsbaum, kein AGENTS.md im geprüften PR-7-Baum. Die während der Arbeit neu auf main erschienenen [Agentenanweisungen](https://github.com/Escoba2024/SeriousSam-TSE-Bot-Servermods-/blob/4ca47d31294ac1fac1b4ecb5516c53a6f857e22b/AGENTS.md) und [MCP-Richtlinie](https://github.com/Escoba2024/SeriousSam-TSE-Bot-Servermods-/blob/4ca47d31294ac1fac1b4ecb5516c53a6f857e22b/docs/decisions/2026-10-17-tse-ai-tools-mcp-policy.md) wurden anschließend gelesen; diese Dateien sind auf der gestapelten PR-Basis noch nicht enthalten. Sie werden durch diesen PR nicht kopiert oder überschrieben.

Verbindliche externe Quellen gelesen: GitHub Issues [#4](https://github.com/Escoba2024/SeriousSam-TSE-Bot-Servermods-/issues/4), [#5](https://github.com/Escoba2024/SeriousSam-TSE-Bot-Servermods-/issues/5), [#6](https://github.com/Escoba2024/SeriousSam-TSE-Bot-Servermods-/issues/6), deren Kommentare und offene PRs samt Gesprächen; Drive [Projektprotokoll](https://docs.google.com/document/d/1odDCeRJhTrWP1xs9ksHKGwqMZPW3zdVSJ5Odr6Urkb0/edit), [Handoff](https://docs.google.com/document/d/1C26GfC2E1GHyJnBmbYOXNJ7G7wgMeE3FmqaMbu2UzW8/edit), [Roadmap](https://docs.google.com/document/d/17iFDR1NxSgkwPDnEql1pFDw9qpUIErUPDFC_J5SDdzo/edit), [Hetzner-Masterplan](https://docs.google.com/document/d/1J4g28WZ-On2uot1bnxCi2-D0hmDL91GMkaZI63rhaZ0/edit), [KI-Reviewboard](https://docs.google.com/document/d/1iFauUGivTuxhI1uwE8C2F8gY2HyvoN2xTFPBXSm0pNo/edit) sowie [Notion-Projekt](https://app.notion.com/p/3fb90f11bec881a5b22df0b40e6c9ef2).

Quellenkonflikt: Notion und ältere Dokumentköpfe nennen externe Erreichbarkeit noch offen. Neuere datierte Drive-Nachträge dokumentieren M1 und begrenzte M3-Kontrollen bereits bestanden. Diese historischen Fremdbelege werden nicht erneut implementiert und nicht als hier selbst beobachtet ausgegeben. Lowrender-Abschluss/Vanilla-Gegenprobe und Linux-4/8 bleiben nach dem gelesenen Stand offen. Keine Live-Aussage über den heutigen Runtime-Zustand.

## Befunde und minimale Korrekturen

**F1 – P2 / wichtig: frische Readiness verliert gegen Timeout.** `Invoke-PopulationLoop` las zunächst eine vollständige neue Query, prüfte dann jedoch die alte Pending-Deadline vor `IsReady`. Beispiel: Frist 45, Querybeginn 44, Rückkehr 46 mit erfolgreicher Readiness. Die bereits wieder bereite Gruppe wurde trotzdem gestoppt. Gilt für initialen Join in PR #3 und für nachträgliche Recovery in PR #7. RED: `Fresh ready sample lost to expired deadline`. Korrektur: gültige aktuelle Readiness zuerst auswerten; sie hebt Pending auf. Unsichere, ungültige oder weiter nicht bereite Antworten verlängern die Frist nicht. Es gibt keine harte Echtzeitgarantie: Polling und synchrone Query-/Stop-Dauer kommen weiterhin hinzu.

Regression: `Test-PopulationDeadlineBoundary.Tests.ps1`, neun Szenarien: initialer und späterer Erfolg bei überquerter Deadline, zwei getrennte Ausfälle mit eigenständigen 45-s-Fristen, fortgesetzter Verlust, Queryexception, ungültiges Sample, Queryausfall nach Ready, ObserveOnly mit/ohne bestehendes Pending. GREEN; kein zusätzlicher Start und nur abschließender Cleanup bei erfolgreicher Recovery.

**F2 – P2 / wichtig: UDP-Parser ignoriert nicht geparste Bytes.** `Get-PopulationFields` suchte passende Feldpaare irgendwo im String. So wurden `garbage` vor einer ansonsten gültigen Antwort und ein abgeschnittener nachfolgender Schlüssel wie `\player_1` hinter einem vorhandenen final/queryid akzeptiert. Ein final-Feld allein beweist bei solcher Framing-Beschädigung keine vollständige Antwort. RED: `Malformed UDP framing accepted`. Korrektur: die konsumierten Feldpaare müssen den kompletten Eingabestring abdecken; vorhandene Versions-/Mod-/Zähler-/Endmarker-/Duplikatprüfung bleibt erhalten.

Regression: `Test-PopulationQueryFraming.Tests.ps1`, 14 Parserprüfungen plus Loop-Szenario. Beschädigte Antworten werden verworfen und setzen die Zwei-Sample-Startfreigabe zurück. Vollständige Antworten, leere Mod-Kennung, Spielername `final` und final ohne queryid bleiben zulässig. GREEN. Kein behaupteter Schutz gegen absichtlich gefälschte UDP-Antworten oder Botnamen.

**F3 – P2 / Testportabilität: Windows-Annahmen verhindern vollständigen Cloud-Lauf.** Neun vorhandene PowerShell-Suiten scheitern unverändert unter Linux. Die für dieses Paket zentralen Recovery-/Controller-Tests wurden ausschließlich beim Testprozessstart portiert: `WindowStyle=Hidden` nur auf Windows. Ihre Assertions bleiben erhalten. Keine Änderung am nativen Prozessadapter. Die übrigen sieben Windows-/Pfad-Abhängigkeiten bleiben sichtbar FAIL; kein Umschreiben zu PASS oder stilles SKIP.

## Reviewmatrix PR #7 / PR #3

| Bereich | Ergebnis / Grenze |
|---|---|
| ReadinessLost / spätere Recovery | PR #7 behebt unbegrenztes Warten nach Disconnect; F1 ergänzt die Deadline-Grenze. Ein Ereignis/eine Frist pro Ausfall; erneute Frist erst nach zwischenzeitlichem Ready. |
| Weiterlaufender Client nach Disconnect | Echte PowerShell-Kinder plus Retail-Format-Fixture: fehlender UDP-Slot und Log-only-Disconnect führen je zu zwei Starts; kurzzeitige Wiederherstellung bleibt bei einem. Keine Spielausführung. |
| Nur UDP unsicher | Keine neue Startfreigabe. Bei bereits Pending bleibt der begrenzte Timeout aktiv; ein zuvor bereiter Client erhält allein durch Queryexception keine neue ReadinessLost-Frist. |
| Human-Reserve / Vierergruppen | Gesamte gemeldete Population zählt, keine Präfixklassifikation. Cap = min(Target, Max−Reserve). 8→9 stoppt eine eigene Vierergruppe; drei freie Plätze werden nicht mit vier Bots gefüllt. Modell: 22 Checks PASS. |
| Gleichzeitige Human-Joins | Kein atomarer Slot-Reservierungsmechanismus im Server. Zwei stabile Samples schließen spätere gleichzeitige externe Joins nicht aus. Native Race-Abnahme bleibt offen; keine Garantie beliebiger Human-Bursts. |
| Locks | Sortierte exklusive Installationslocks, auch bei anderen State-Verzeichnissen; Teilfehler geben gehaltene Handles frei. Controller-Suite prüft Konkurrenz und Wiederaufnahme nach Freigabe. Kein Windows-Junction-/SMB-/Crash-Lock-Test aus Linux ableitbar. |
| PID-Reuse / Ownership | Statisch: exakter EXE-Pfad + UTC-Startticks + gepinnter Handle; Stop prüft zusätzlich Eltern-PID. Kein PID-/Prozessnamen-/Prozessbaum-Kill. Frischer PID-Lookup wird vor Stop gepinnt. Windows-CIM-Pfad hier nicht vollständig ausführbar. |
| State beschädigt / Wiederaufnahme | Cleanup verwendet In-Memory-Record, nicht erneut die State-Datei. Unlesbare/inkonsistente Start-Receipts lösen Rollback aus. Aktiver Neustart übernimmt keine alte State-Datei und verweigert einen bereits laufenden Client. Windows-Adapterprüfung weiterhin erforderlich. |
| ObserveOnly | Keine Start-/Stop-Aufrufe, kein finaler Prozesscleanup, keine Installationslocks. Eigener neuer Evidence-Ordner wird dennoch geschrieben; „read-only“ bezieht sich auf die Runtime. |
| Stop / Restart / Cooldown / Rollback | Bestehende Kontrollsuite: 18 Checks PASS, inklusive Logfehler-Cleanup, Startfehler, Query-Gates, Namenssperre und zehn Sekunden ab Stop-Ende. Windows-Stop-/CIM-Suiten bleiben hier FAIL. |
| Orphan / Watchdog | PR #3/#7 besitzen keinen externen Guardian. Hard-Exit-Orphan ist dokumentierter nativer Fremdbefund. PR #8 ergänzt separat ein opt-in Guardian-Konzept mit gehaltenen Handles, Owner-ID, Protokollsequenzen und Installationslocks. Dieser Review ersetzt weder dessen vollständigen finalen Review noch native Hard-Exit-Abnahme. Nicht doppelt implementiert. |

## Tatsächlich ausgeführte Prüfungen

Debian GNU/Linux 13, Python 3.12.14, lokal unter `work/` entpackte PowerShell 7.5.4, keine Retail-Dateien/Windows-CIM/GPU. PowerShell-Download aus offizieller GitHub-Releasequelle, keine Produktabhängigkeit geändert.

| Lauf | PASS | FAIL | SKIP / blockiert |
|---|---:|---:|---:|
| Unverändertes PR-7-Checkout: PowerShell inkl. ShadowRuntimeLog | 14 Suiten | 9 Suiten | 2 native/private Suiten |
| Finaler Fix: derselbe PowerShell-Scope + zwei neue Suiten | 18 Suiten | 7 Suiten | 2 native/private Suiten |
| Python-Publication-Fixtures unverändert, vorher/nachher | 44 Tests (25+9+10) | 0 | 0 |
| Source-Provenance, vorher/nachher | 13 veröffentlichte Hashes + Original-Captures | 0 | 0 |
| `test_auto_combat_evidence.py` ohne private Argumente | 0 | Aufruf scheitert mit IndexError | keine Fixture ausgeführt; echte Evidence + DLL fehlen |

Der reguläre `tools/Test-Publication.ps1` wurde ebenfalls unverändert gestartet und brach bei `Test-FleetAndPopulation.Tests.ps1` ab. Deshalb wurden sämtliche zugelassenen Suiten danach einzeln in eigenen pwsh-Prozessen ausgeführt; der Runner-Abbruch verdeckt keine weiteren Fehler. Der Gesamtstatus dieses Linux-Scopes ist **nicht vollständig grün**.

Verbleibende FAIL, jeweils im unveränderten Baseline- und Final-Lauf:

- `Test-FleetAndPopulation.Tests.ps1`: Windows-Beispielpfad wird auf Linux als nicht absolut abgelehnt.
- `Test-FleetLaunchFailure.Tests.ps1`, `Test-FleetProcessControl.Tests.ps1`, `Test-FleetStopCurrent.Tests.ps1`, `Test-FleetStopExitCode.Tests.ps1`: `Start-Process -WindowStyle` auf Linux nicht unterstützt.
- `Test-LocalReleasePreparation.Tests.ps1`: Windows-Pfadseparator-/Containment-Annahme (`Startup path escapes its isolated bot client`).
- `Test-PopulationSupervisorAdapter.Tests.ps1`: erste CLI-/Loopback-UDP- und Identitäts-/Joinformatprüfungen durchlaufen, danach Abbruch an `-WindowStyle`; späterer CIM-Teil nicht geprüft. Kein PASS für die ganze Suite.

Explizit ausgelassen: `Test-RetailCleanup.Tests.ps1` (echte Retail-Session nötig), `Test-LocalReleasePackage.Tests.ps1` (private SDK-Artefakte nötig). Der zusätzliche Auto-Combat-Aufruf ist kein Quellcode-Regressionsbefund. Bereinigte Einzelstatus: [JSON](2026-10-17-cloud-supervisor-review.json).

Unabhängiger separater Reviewer prüfte `f56bbcd..d67bc6b` und vollständigen Supervisor/Core: keine wichtigen Befunde; dieselben fünf relevanten Suiten eigenständig PASS. Die sieben Windows-/Pfad-Fails und native Grenzen wurden bestätigt. Das ist Code-Review, keine neue Retail-Qualifikation.

## Reproduzierbare Kommandos

```bash
git fetch origin '+refs/heads/*:refs/remotes/origin/*' '+refs/pull/*/head:refs/remotes/origin/pr/*'
git clone --no-hardlinks /path/to/fetched-repository work/review
git -C work/review remote set-url origin https://github.com/Escoba2024/SeriousSam-TSE-Bot-Servermods-.git
git -C work/review fetch origin '+refs/heads/*:refs/remotes/origin/*'
git -C work/review switch -c codex/cloud-supervisor-review-20261017 origin/codex/supervisor-readiness-recovery-20261016
# Baseline auf f56bbcd; anschließend Fix d67bc6b aus dem eigenen Branch prüfen.
pwsh -NoProfile -File tools/Test-Publication.ps1 -Evidence /new/private/evidence/publication -Python python3
```

Der Publication-Aufruf ist unter Windows mit allen Voraussetzungen das bevorzugte Gesamtgate. Für die vollständige Linux-Fehlerinventur jede `poc/scripts/*.Tests.ps1` separat mit `pwsh -NoProfile -File <suite>` starten, außer den beiden oben ausdrücklich ausgelassenen Suiten. `Test-LocalReleasePreparation.Tests.ps1` benötigt zusätzlich `-Evidence <new-private-directory>`. Danach:

```bash
pwsh -NoProfile -File tools/Test-ShadowRuntimeLog.ps1
pwsh -NoProfile -File poc/scripts/Test-PopulationDeadlineBoundary.Tests.ps1
pwsh -NoProfile -File poc/scripts/Test-PopulationQueryFraming.Tests.ps1
pwsh -NoProfile -File poc/scripts/Test-PopulationReadinessRecovery.Tests.ps1
pwsh -NoProfile -File poc/scripts/Test-PopulationSupervisorControl.Tests.ps1
pwsh -NoProfile -File poc/scripts/Test-PopulationSupervisor.Tests.ps1
python3 -B poc/scripts/test_fleet_ai_evidence.py
python3 -B poc/scripts/test_obstacle_evidence.py
python3 -B poc/scripts/test_local_release_smoke.py
python3 -B tools/Verify-SourceProvenance.py
git diff f56bbcdb403ffd6b8cfa85d585bc62e399a9f284..HEAD --check
```

RED/GREEN lässt sich ohne Produktdateien zu überschreiben reproduzieren: neue Tests in ein separates Archiv/Checkout von `f56bbcd` kopieren; beide scheitern dort. Mit `d67bc6b` bestehen beide. Private Rohlogs/temporäre Prozess- und Testidentitäten wurden nicht veröffentlicht. Nach dem Lauf waren keine eigenen pwsh-Kinder mehr vorhanden; es wurden zu keiner Zeit Spiele gestartet.

## Merge-Empfehlung und Übergabe

- **PR #7 unverändert: Änderungen anfordern (F1/F2).** Sein enger Recovery-Ansatz ist sinnvoll; dieser Fix-PR wird auf #7 gestapelt. F2 liegt bereits in der PR-3-Basis, F1 dort für initiale Joins.
- **PR #3: Draft beibehalten.** Korrekturen übernehmen und Windows-Gesamtgate sowie native Race-/Ownership-/Cleanup-Matrix schließen. Kein pauschaler Population-/24/7-PASS.
- **PR #8: Draft beibehalten.** Bestehende Watchdog-Arbeit respektieren; gemeinsame Supervisor-Korrekturen anschließend regulär integrieren. Vollständiger finaler Watchdog-Review und natives Gate bleiben separat.
- **Eigener Fix-PR:** eng geprüfter Codevorschlag, unabhängiger Review ohne wichtige Befunde und relevante Cloud-Regressionen PASS. Vor Merge Windows-Publication aus frischem Checkout ausführen; keine bedingungslose Mergefreigabe aus einem insgesamt roten Linux-Lauf.

Nächstes konkretes Runtime-Arbeitspaket: **isolierte Supervisor-Grenzprüfung des Fix-Commits**, nicht M1/M3 neu implementieren. Zuerst Windows-Publication mit Python und den neuen Tests; dann ein vorbereiteter 61DC-BotClient an eigenem isoliertem Dedicated: (1) Readiness unmittelbar vor Deadline wiederherstellen, (2) dauerhaft getrennter weiterlaufender Client → begrenzter Stop, ≥10 s Cooldown, genau ein Ersatz, (3) Query-only-Ausfall und ObserveOnly ohne zusätzliche Prozesssteuerung, (4) parallele Human-Joins/Reserve und kontrollierter Stop mit unverändertem Human-/Observer-Prozess. Commit, DLL-/Startup-Hash, monotone Zeiten, unabhängige Prozess- und vollständige UDP-Evidence, Cleanup/Originalhashes protokollieren. Für PR #8 Hard-Exit separat abnehmen.

M4 bleibt an der Quellverfügbarkeit und Runtime-Prerequisites begrenzt; siehe [portable Vorbereitung und Auditmatrix](../../poc/HETZNER-M4-CLOUD-PREFLIGHT.md). Kein Runtime-Agent soll fehlende Prerequisite-Nachweise aus diesem Cloud-Bericht erzeugen oder bestehende aktive Sessions unterbrechen.
