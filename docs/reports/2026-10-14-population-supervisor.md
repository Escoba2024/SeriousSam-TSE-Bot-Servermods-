# Population-Supervisor – 14.10.2026

Der kontinuierliche Population-Supervisor erweitert die vorhandenen Fleet-Werkzeuge um konservative Steuerung ganzer vorbereiteter BotClient-Prozessgruppen. GameMP, Engine, Entities und Navigation wurden nicht geändert. Der bisher qualifizierte DLL-Kandidat bleibt `61DC27E0E7B80BADCF9AE705C30FCA88EDD3935737715DFFFF59E90C26F1FEF9`.

## Verhalten

Gesamtbelegung ersetzt eine unsichere Human/Bot-Namensklassifikation. Die Obergrenze beträgt `min(TargetPopulation, MaxPlayers - ReservedHumanSlots)`, mindestens null. Zwei Vierergruppen und Ziel acht reagieren auf einen zusätzlichen Menschen mit Stop einer eigenen Gruppe; nach dessen Austritt kann die Gruppe wieder starten. Bis zu drei Plätze bleiben wegen der Gruppengröße frei. Gleichzeitige fremde Beitritte sind weiterhin eine Race-Grenze.

Starts warten auf zwei konsistente UDP-Beobachtungen und die Bereitschaft bereits gestarteter Gruppen. Native Join-Zeilen, eigene genaue BotDriver-Slots, Servernamen und Prozessidentität bilden den Bereitschaftsnachweis. Fehler/Sync-Verlust nach dem letzten Join sperren ihn. Join-Deadline 45 Sekunden, Wiederstartverzögerung zehn Sekunden nach abgeschlossenem Stop, zusätzliche Sperre bei noch gemeldeten alten Gruppennamen.

## Portable Prüfung

22 PowerShell-Prüfsuiten, 44 bestehende Python-Fixture-Fälle und die Provenance aller 13 veröffentlichten GameMP-Quellen bestanden. Die Supervisor-Modellprüfung enthält 22 Fälle. Controllerfälle umfassen echte PowerShell-Kindprozesse, Join-Timeout, Fehler-Cleanup, Startsperren und Wiederstartverzögerung. Der echte CLI-/UDP-Adapter wurde gegen einen lokalen UDP-Testserver geprüft, einschließlich exklusiver Client-Locks und exakter Startzeitprüfung.

Die unabhängige Prüfung identifizierte zwei zusätzliche Fehler, beide durch RED/GREEN-Regression behoben: Ein Spielername `final` konnte zuvor einen fehlenden UDP-Abschlussmarker verdecken; das Abschlussfeld muss jetzt tatsächlich als leeres Protokollfeld geparst sein. Außerdem durfte ein späterer State-Dateifehler keinen eigenen Prozess zurücklassen; Stop und Cleanup arbeiten jetzt unabhängig von der Datei mit der gehaltenen, erneut geprüften Prozessidentität. Der Start-State wird vor Übernahme auf den eigenen aktuellen Client geprüft.

Der Abgleich mit originalen Retail-Logs zeigte außerdem, dass `CRC check OK` ein Servermarker ist. Client-Bereitschaft verwendet den tatsächlichen indented `joined`-Marker und anschließende genaue BotDriver-Zeilen. Ein echter Regressionstest reproduzierte zuerst die Ablehnung dieses Retail-Formats und bestand nach der Korrektur.

## Native Probe

BESTANDEN mit dem endgültigen Skriptstand: 101,6624029 Sekunden begrenzter lokaler Lifecycle mit unverändertem Dedicated Server, Vanilla-Observer und der bestehenden qualifizierten DLL. Drei eigene Gruppenstarts und ein durch Human-Beitritt ausgelöster Gruppenstop; fünf unabhängige native CRC-Akzeptierungen; kein Join-Timeout. Die unabhängige Auswertung bestätigt alle fünf vollständigen Status-/Spieler-Stufen und deren exakte erwartete Namen/Indizes:

| Stufe | Nachweis |
|---|---|
| 8 | Zwei eigene Vierergruppen automatisch gestartet |
| 9 | Zusätzlicher Vanilla-Human beigetreten |
| 5 | Supervisor stoppt eine eigene Vierergruppe; Human bleibt aktiv |
| 4 | Human kontrolliert ausgetreten |
| 8 | Supervisor ergänzt die fehlende Vierergruppe nach Cooldown |

84 gültige Beobachtungen und eine wegen inkonsistenter Statusantwort zurückgehaltene Query; kein Start aufgrund dieser unsicheren Query. Skript-SHA256, genaue Messdaten und Qualifikationsgrenzen stehen in der [bereinigten Abnahmezusammenfassung](2026-10-14-population-supervisor.json). Der dort genannte Testcommit bezeichnet die lokale Codehistorie; die Skripthashes binden den Nachweis an den veröffentlichten Inhalt.

Rücknahme bestanden: alle 817 Dateizustände der Bestandsaufnahme vor der heutigen Probe wiederhergestellt; alle 30 erfassten Executables/Bibliotheken erhalten; null eigene Spieleprozesse/Testports und keine Crash-/Cleanupbefunde. Zwei BotClient-GameMP-DLLs waren bereits vor der Probe auf 61DC vorbereitet und bleiben so erhalten; die übrigen 28 Binaries stimmen auch mit der älteren Originalbasis überein. Die alte pauschale Originalbinary-Prüfung scheitert an diesen zwei schon vorbereiteten Dateien und wird ausdrücklich nicht als neuer bestandener Nachweis übernommen. Maßgeblich ist die heutige gesicherte Startinventur. Kleine freigegebene Supervisor-Lockdateien im Installationswurzelordner bleiben entsprechend dem Runbook erhalten.

Dies ist eine kurze Gruppen-Lifecycle-Abnahme auf Fortress. Sie belegt keine neue KI-Stunde und keinen regulären Shutdown für sämtliche Prozesse: Fenster-Exit/harte Fallbacks werden als eigene Controller-Receipts erfasst, der Harness verwendet kontrollierten Teardown.

## Offene Qualifikation und Fortsetzung

Die Population-Manager-Gesamtphase bleibt TEILWEISE: keine exakte individuelle Slotsteuerung, keine beweisbare Human-Identität, keine Garantie gegen beliebige Join-Races und kein externer Watchdog bei hartem Controllerausfall. Zwölf/sechzehn Bots, mehrere Server und 24-Stunden-/24/7-Betrieb sind offen. Öffentliche 333networks-/Vanilla-Browser-Abnahme und externe UDP-Erreichbarkeit des Shadow-Cloudsystems bleiben unabhängig davon offen.

Die bestehenden Phase-1-/Vier-Bot-/Acht-Bot- und KI-Stundenabnahmen behalten ihren bisherigen Umfang. Globale Navigation, Itemplanung, Abgrundsicherheit und weitere Waffenfamilien bleiben offen. Der gescheiterte Ground-Lookahead-Kandidat ist weiterhin ausgeschlossen.

Nächste Prioritäten: weitere begrenzte Population-Recovery-/Query-Ausfall-/Controllerabbruch-Proben, danach Skalierung und längerer Betrieb; öffentliche Browserprüfung benötigt einen nachweislich von außen erreichbaren UDP-Endpunkt. [Bedienung und Cleanup](../../poc/POPULATION-SUPERVISOR.md) ermöglichen die Fortsetzung ohne neue Projekterklärung.
