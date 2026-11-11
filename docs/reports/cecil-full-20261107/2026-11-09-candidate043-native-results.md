# Normal043: Skulls-Messgrenzen und Supply bestanden, Luft-NAV-Lücke offen

Normal043 ist noch nicht insgesamt für den Rollout qualifiziert. Quelle `4fd46626cd9a5c6762c2339154e28951b2bfdd36`, Tree `f92f9d8642c490daa82fd0bc5b45a841924465c8`, DLL `81f9b73bfdb29ce31110c0170f4c0fceb82cb985315056124d2da39571a16ebe`.15 MSVC-Einheiten/Link und802 finale SDK-ASan/UBSan-Prüfungen bestehen. Main und unabhängiger vollständiger Quellreview bestätigen genau die zwei geänderten Dateien. Neun C++-Suiten, Driver-/Item-/Originaltabellenprüfungen,34 reine Safe- und33 Supply-Harnessprüfungen bestehen ebenfalls. [Bereinigtes Buildmanifest](build043.json); reine Prüfungen ersetzen keine native Abnahme.

## Bewegungsfreigabe ist kein Bodennachweis

Der tatsächliche Positionswatchdog beobachtet jetzt auch einen angenommenen Navigationsanker ohne gültiges Folgepfadziel. Der originale isolierte UNREACHABLE-Knoten wird weder entfernt noch mit erfundenen Kanten versehen. Gültige Ziel-/Lock-/UNREACHABLE-Wartekontexte und USE behalten ihre eigenen Regeln.

Eine separate aktuelle Bewegungsfreigabe nach Cecil-Standard `bAvoidPits=0` erlaubt erst bei echtem Stillstand beziehungsweise während des ursprünglichen eigenen Holds den bestehenden0,3-Weltsweep mit frischer physischer Wandprüfung. Unbekannter NULL-Support bleibt ausdrücklich unbekannt. Diese Freigabe autorisiert weder Kontaktboden-Ausnahmen, ferne Originalhinweise noch einen NAV-Anker. Opt-in-Abgrundvermeidung verlangt weiterhin aktuelle Supportautorisierung und Bodenprüfung; die gewöhnliche Reacquisition vor einem Stillstand behält ihre bisherige Bodenpflicht. Welt-/Frame-/Lebens-/Owner-/Zeit-/Graph-Prüfungen,0,6s-Hold,1,6s-Cooldown,16-Raybudget, Original-NAVs/Locks/Radien und feste Ziel-Fristen bleiben erhalten. Es gibt keine tiefere Probe, neue Engine-API, Speicher-/Physicsänderung oder zusätzlichen Jump-Input.

Die neuen begrenzten Recovery-Metadaten trennen `support_authorized`, `pit_avoidance` und `floor_required`. `support_authorized=0` zusammen mit `floor_required=0` bei Originalpolicy0 ist kein Bodenbeweis.

## Skulls600: quantitative Grenzen erfüllt

Der vollständige neue Acht-Bot-Lauf endet nach600,006398371s mit596 korrekten Statusabfragen, vollständiger Telemetrieabdeckung, unverändertem Szenario, positiver Scoreentwicklung aller acht und keinen neu erkannten Monitor-/Sync-/CRC-/Fatalfehlern. Alle drei eigenen Prozesse schließen normal, Rohbelege bleiben erhalten.

| Slot | Maximaler unbegründeter Stillstand |
| --- | ---: |
| BotA:0 |2,014s |
| BotA:1 |1,005s |
| BotA:2 |2,026s |
| BotA:3 |2,022s |
| BotB:0 |2,023s |
| BotB:1 |1,016s |
| BotB:2 |2,009s |
| BotB:3 |6,055s |

Die unveränderte10s-Grenze ist damit eingehalten. Main-Featureindex zählt innerhalb der tatsächlichen Monitorfenster40+30 gesundheitskorrelierte Todes-/Folgegeneration-Respawns, insgesamt70; das sind keine100 Todesfälle. Geordnete Pickup-/Auswahl-/Current-/Inputketten auf Skulls sind für Doppel-Colt/Rocket/Grenade beobachtet, für Flamer/Cannon dort noch offen. Privater Main-Verdict-SHA256 `b01d25972a9b5e478060156334900421da097033a7f7f0be8b2ab939d3957d83`.

### Eigenständige funktionale Lücke im Flugzustand

Ein tatsächlicher BotB:0-Recovery-Fall zeigt bei335,05s unbekannten Support, Standardpolicy0 und eine ausgegebene wandgeprüfte Ausweichrichtung. Bis336s folgt reale seitliche Positionsänderung im selben Leben. Danach zeigen21 Messpunkte bei336–356s wiederholte Höhenzyklen, angenommene Supply-Ownership, neutrale Achsen und keinen Anchor/Goal/Hop.19 davon haben nativen FALL-Zustand, zwei kurze STAND-Proben liegen bei348/356s; einzelne gecachte Reacquisition-Hinweise bleiben erhalten, bilden aber keinen gültigen Folgepfad. Erst sichtbarer Combat übernimmt357s die Bewegung;359s ist wieder ein gültiger NAV-Pfad im selben Leben vorhanden, später auch eine weitere Bodenannäherung mit Navigation.

Die anfängliche Rückkehr ist damit durch Combat mitbestimmt und kein autonomer Supply-Luft-Recovery-Nachweis. Der Lauf belegt auch keinen permanenten Loop und keinen neuen10s-Stillstandsfehler: tatsächliche Höhenänderung bleibt tatsächliche Bewegung. Die quantitative Prüfung wird nicht nachträglich zu FAIL umgedeutet. Der konkrete Quellpfad verwirft bei fehlender Referenz den nativen FALL-Zustand bereits vor Originalhint-/LOS-/Bewegungswahl; der Ground-Watchdog setzt wegen realer Höhenänderung seinen Stillstand zurück. Eine eng getrennte frische Luft-Bewegungsfreigabe mit wirklichem Originalhint und physischer Wandprüfung wird daher vor vollständiger Funktionsqualifikation separat entwickelt. Original-Cecil-Bewegung ist grundsätzlich nicht auf STAND/CROUCH beschränkt. Neue Laufzeitnachweise bleiben nach jeder Verhaltensänderung erforderlich.

## Versorgungv16: begrenztes Supply-Gate bestanden

Zehn frische eigene Einzelbotfälle und alle elf Prozesse sind normal abgeschlossen.589 gültige Ein-Bot-Abfragen und zehn unverwechselbare PID-/Kernelstart-Kontexte sind erhalten. Die prospektiv festen ersten zehn Waffenziele sind nach Main und unabhängigem vollständigem Rohreview sämtlich korroboriert:10/10. Typisierte ausgewählte Entity, einzig passendes neues Waffenbit, derselbe native Zielendtick und der lokale lebende Bewegungs-/Pickupkontext stimmen überein. Darunter sind diesmal ausdrücklich auch die tatsächlichen WaffenIDs13,5 und12; keine Grenade-/Rocket-Verwechslung.

Die zehn festen Initialleben benötigen9,55/10,15/20,50/2,45/4,05/4,85/3,90/4,05/9,90/19,80s: Median7,20s/P9520,50s. Die15s-/30s-Grenzen bleiben unverändert. Der20,5s-Laserfall liegt innerhalb seiner bereits nativ protokollierten Mapped-Frist; er wird weder als gewöhnlicher12s-Versuch fehlklassifiziert noch nachträglich verlängert. Alle25 tatsächlichen Waffenzielstarts bleiben erhalten:24 korroboriert, späterer Flamer auf Rang25 in Fall10 ohne beobachtetes Ende rechtszensiert außerhalb der festen ersten zehn. Kein solcher Nachlauf ersetzt einen Kohortenfall oder wird zum Erfolg umgedeutet.

Alle614 nativen Zustandsproben zeigen keinen sichtbaren Gegner, alle zehn Initialleben bleiben ohne Tod oder Ersatzspawn erhalten, elf normale Abschlüsse/zehn tatsächliche Leerslotantworten/17 unveränderte Original-/Konfigpins sind geprüft. Bot-Exitstatus1 bleibt ausdrücklich erhalten. Kein `goal_picked`-Alleinbeweis, ReceiveItem-Hook oder allgemeiner Pickupradius. Privater begrenzter Supply-Verdict-SHA256 `7bcd2380745c02f16ca747234886004bd83feab54d9cf6931fe730081c6b6ad3`; unabhängiger Rohreview `2837ca23fe65463e6ce7773a6883bf4fe4e21b06e4bbe1e5551ac16560c8d83f`. Gesamtkandidat weiterhin `qualified=false`.

## Zusätzlichen Main-Prüffehler transparent erhalten

Der reguläre Stager prüft alle289 vorherigen Gate8-Dateipins vor der gesicherten DLL-Ersetzung; der reguläre Run-Window-Start prüft anschließend Manifest, Originalserver, installierte Kandidaten-DLL, Root-/Unitbelegung und Isolation. Eine zusätzliche Main-Prüfung vergleicht irrtümlich noch die zwei Vorgänger-DLL-Hashes, schlägt vor eigener Protokolldatei fehl, und Main stoppt seine folgenden Startaufrufe an dieser Stelle versehentlich nicht.

Die ausdrücklich erst nach Start durchgeführte vollständige Reconciliation und unabhängige Prozess-/Kernelstart-/Mapped-device/inode-Prüfung bestätigen exakt die beiden beabsichtigten42→43-DLL-Ersetzungen und287 unveränderte weitere Dateien. Dies ist kein rückwirkender zusätzlicher Preflight. Der eigenständige Fehler und seine Nachprüfung bleiben getrennt protokolliert; es wird kein nie erzeugtes043-Anfangs-Preflightdokument behauptet. Unabhängiger Poststart-Review-SHA256 `ca967b12b2f53fe0cd03e4deffc67dbe2721de9349dae229af6698001d79d55a`.

Nach normalem vollständigem Abschluss bestätigt eine neue echte Root-/Unit-/Prozessquieszenz alle289 aktuellen Dateipins. Dieser ausdrücklich als POST_RUN gekennzeichnete Snapshot dient ausschließlich der Prüfung vor einer künftigen Kandidateninstallation, nicht der rückwirkenden Abnahme von043.

## Weitere Abnahme offen

Keine weiteren043-Karten, formalen3600/3600/7200s-Fenster, Ressourcen-/Rotations-/Recovery- oder öffentlichen Rolloutläufe wurden gestartet. Der gezielte aktuelle Original-Retail/Wine-Harness ist nur vorbereitet und mit20 reinen Checks und tatsächlich geladener Helper-/Manifestbindung geprüft; kein043-Retail-Gameplayresultat wird daraus behauptet. Alle übrigen Waffen-/Sonderaktions-/Karten-/100er-Respawn-/Stunden-/CPU-/RSS-/Recovery-Gates, der vollständige autorisierte All6-Rollout samt900s-Flottenprüfung und reguläre Integration bleiben offen. Frühere DLL-Zeit zählt nicht für den nächsten Kandidaten. Die Transfermatrix bleibt ausdrücklich039-Snapshot, alle historischen Fehler bleiben erhalten. Die sechs öffentlichen Instanzen bleiben auf den bisherigen DLLs; keine043-DLL ist dort installiert.
