# Build022: geschlossenes Red-Station-Fenster

Build022 lief am14.11.2026 isoliert 600,0348175 Sekunden auf Red Station/Hard2
mit acht DEMON-Bots, Original-Dedicated und unverändertem Originalbeobachter
mit derselben20FPS-Konfiguration wie die drei älteren Nav20-Arme. Die DLL
28028e448e514cae8589b078d06533c8934a4a12ca7ab52aaead77e1590ab8fc
wurde in beiden tatsächlichen Botprozessen geprüft. Quelle621e92f;
Rootfreeze3c45ca2d, Manifest/47Quellen/28Overlays separat verifiziert.

Ergebnis: **PASS_LIMITED_A4_OBSERVATION_FUNCTIONAL_REVIEW_REQUIRED**.
Alle vier Rollen normal beendet; Root640Dateien und vier archivierte Schlusslogs
unabhängig geprüft. Keine neuen BAD-/Disconnect-/CRC-/Crash-/InvalidAction-/
Joinfehler. ResultSHA
ee217919c0462288ec1c77f61241f09b279fbaeabac166ee2f0e75b51af69bb3.
Öffentliche Runtime und Dev wurden nicht geändert.

| Beobachtung | Build022 | vorheriger020-Arm |
|---|---:|---:|
| serverseitige Nicht-Suizid-Kills |170|159|
| Leben mit Usefulbesitz / beobachtet |92/193|84/180|
| tatsächliche Useful-Inventargewinne |118|112|
| an Sourcewachstum gebundene FIRE-Beobachtungen |3379|3468|
| links-/rechtszensierte Leben |121/8|105/8|
| längster beobachteter lebender Abschnitt ohne Useful |45,589s|45,739s|
| maximale bestehende1m-Stationaritätsmetrik |10,000s|2,449s|

Das sind einzelne Matches ganzer Kandidaten, keine direkten Duelle und kein
statistisch belegter Rang. Die0,15s kürzere längste Unbewaffnetheit ist kein
zuverlässiger Beschaffungsfortschritt. Alle acht Slots zeigen Bewegung,
Waffengewinne und gebundenes FIRE; daraus folgt kein Erfolg in jedem Leben.
Die kanonische Lebensauswertung nutzt unveränderte V3-Provenienz und native
Spawnclocks; eine mehrdeutige postmortale HP-Reihenfolge wird nicht als neues
Leben oder Waffenaufnahme gewertet. Keine SourceTick/20-Interpolation.

## Offene konkrete Befunde

Der Healthconnector wird im Spiel vorgeschlagen und außerhalb der Navsphäre
fortgesetzt. Ein Proposalflag allein beweist weder akzeptierten Input noch
Heilung; die detaillierte Zuordnung wird separat geprüft.

Das lange späte Leben betrifft NativeSlot0, Spawn547,189941 bis zur letzten
lebenden Beobachtung592,778809, ausschließlich Owned3/7. Es ist über die
bestehende Source-/Nativebindung Generation27 zugeordnet. Alle47periodischen
Sourcezustände dieser Generation haben Healthproposal0. Nicht als Regression
des Healthfixes erklären; mehrere Waffenunavailable-Enden bleiben ohne
native Begründung. Die vorhandene Diagnostics1-Quelle wird auf einen engen
Diagnoseweg geprüft, bevor weitere Gameplayänderungen vorgenommen werden.

Die frühe Stillstandsphase ist ein anderes Leben. Ihre Quelle deutet auf ein
zehnsekündiges Avoidintervall am aktuellen Ausgangsanker nach einer erfolglosen
Importantinteraktion. Der inzwischen gewöhnliche Zielweg bleibt bei gesperrtem
Sourceanker neutral. Das ist eine Hypothese mit Source-/Nativebelegen; ein
SDK107-Reproducer am realen Code soll sie bestätigen. Keine Locklockerung
und kein Fix vor Reproduktion.

CPUmax56,359%, RAMmin2628714496B, Diskmin8825348096B. Während Gameplay lag
die größte Hostmesslücke bei1,159s; die46,521s-Lücke während des Starts bleibt
erhalten, daher kein vollständiger Ressourcen-PASS. Formale Stunden, Reset,
übrige Karten, A1 und Drei-Stufen-Abnahme bleiben offen. Build022 ist nicht
freigegeben und wird nicht auf Public oder Dev übernommen.
