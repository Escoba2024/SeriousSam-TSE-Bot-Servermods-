# A4 Build019: Ressourcenabbruch und unabhängige Nachprüfung

Der isolierte Lauf `a4-reset019-extended-20261114-085029` bleibt **FAIL**: Die gemessene Host-CPU erreichte 75,510204 % bei unveränderter Obergrenze 75 %. Der Lauf dauerte vom 14.11.2026 08:50:29 bis 08:51:56 UTC; kein Kartenrundenabschluss wurde protokolliert. Daraus folgt weder ein bestandener noch ein fehlgeschlagener 24-Slotphasen-Waffentest. Build019-DLL: `671df77a06eb9df8822032418e4d9ae2550f5581a2bf89c3e45b83c0f32472be`.

Die leichte, unabhängige Nachprüfung bestätigte:

- **648 Restore-Einträge**: 643 vorhandene Dateien, eine ursprüngliche Abwesenheit, vier während des Laufs erzeugte Rundenskripte anschließend entfernt. Beide privaten Backupbestände enthalten für alle 643 Dateien passende SHA256; der unveränderliche Anfangssnapshot des nachfolgenden Quiet-Laufs bestätigt dieselben Datei-Hashes und dieselben Modi/UID/GID. Eine Abwesenheit ist explizit erfasst; die vier weiteren folgen aus dem vollständigen `server/Scripts`-Treesnapshot. Keine Abweichung. Mtime wird nicht behauptet.
- Alle vier alten Spielprozess-PIDs sind inzwischen abwesend. Der Controller verzeichnet vier regulär geschlossene Rollen und `restored=true`, keine Restorefehler. Weil die Labinstallation bereits wieder verwendet wird, wird keine heutige allgemeine Prozess-, Display- oder Sperrenfreiheit behauptet.
- Vier geschlossene Rollenlogs stimmen nach erneutem Hash-/Größenvergleich exakt mit dem Resultat überein; die Observerkopie ist identisch mit dem Vanilla-Log. Der vorhandene Logklassifikator meldet darin keine Sync-, CRC-, Crash-, Invalid-Action- oder Joinfehler. Das kurze Fenster ersetzt keine Stabilitätsabnahme.
- 26 Ressourcenstichproben: mindestens 2.858.459.136 Byte verfügbarer RAM und 11.913.420.800 Byte freier Datenträger. Die CPU-Grenzüberschreitung bleibt entscheidend; größte Messlücke im Spiel 1,138077 Sekunden, während des Startablaufs 47,212909 Sekunden.

Der Hauptagent beobachtete gleichzeitig eine eigene fremde Agentensuite (`python3 -m unittest discover -s tools -p test_*.py`) mit 69,8 % Prozess-CPU und 75 Sekunden Laufzeit. Eigentum und anschließendes Ende wurden bestätigt. Eine separate zeitgestempelte Prozessmessdatei wurde nicht gespeichert: Das stützt eine geänderte Lastbedingung, beweist aber keine vollständige kausale Zuordnung der Hostlast zu diesem Prozess. Die `/proc/stat`-basierte Grenzüberschreitung selbst ist erhalten.

Zusätzlich wurde ausschließlich statisch der getrennte Quiet-Freeze geprüft: Launcher bytegenau nur Ausführungsgate und eindeutiger Unit-/Evidenznamensraum verändert, AST lesbar, 14 eigene Abhängigkeiten hashgenau, 51 externe Pins unverändert. Manifest: `917fab112b3094a5793d7a6a7cecbf81a13167aa23e145dfde564e912415f974`. Während des laufenden Vergleichs wurden externe große Dateien nicht erneut vollständig gehasht. Keine Kriterienänderung und keine Runtime-Abnahme aus dieser Prüfung.

Die [bereinigte Quittung](milestone-a-20261114/build019-a4-resource-failure.json) enthält Ressourcenzeitachse, genaue Beleg-SHAs, Loghashes und Prüfgrenzen. Diese Agentenarbeit startete keine Tests, Builds, native Prozesse oder Wiederholung und änderte keine Runtime.
