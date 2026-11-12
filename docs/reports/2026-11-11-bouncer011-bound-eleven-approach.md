# 011: positive UP nur auf der zusätzlich belegten11→12-Anfahrt unterdrücken

Der abgeschlossene010-Lauf zeigt bei local2/g7 die wirkliche erste11→12-Aktion: Tick1025 mit Roh-UP1/finaler Action-UP11 auf Support194, danach Aufstieg ohne234-Aufruf und zu hohe12→34-Ankunft. Der [native010-Bericht](2026-11-11-native010-bouncer-outcomes.md) trennt diesen Fehlanflug von den späteren erfolgreichen234-Launches derselben beziehungsweise einer anderen Entity.

Die vorhandene010-Regel für8→12 wird ausschließlich auf die gerichtete11→12-Kante erweitert. Die globale Bindung prüft zusätzlich die originale Punkt11-ID, Position, Radius2, Flags0, fehlende Important-/Next-/Lock-Referenzen und die vollständige geordnete Linkliste `[10,13,12,89,189,94]`. Die bestehenden Weltpfad-/WeltCRC-/NavCRC-/193Punkte-/Loaderlock-/Ready-/Serial-Prüfungen bleiben erhalten. Der native NAV wurde privat erneut gelesen: SHA256 `70e2839587b0f14c024ef978579133e84eed594a3cbbd0fa1f1db98d99aa37c6`, CRC32 `e4571656`,12245Bytes,193Punkte. Die WeltCRC bleibt `ff3776e0`; der NAV-Dateisuffix ist weiterhin lediglich Pfadhash.

Der tatsächliche committed Navigator-Source muss8 oder11 sein, der aktuelle Hop12. Blockierung wird für den tatsächlichen Source und Ziel12 geprüft; eine Blockierung des unbenutzten Knotens8 sperrt keine gültige11→12-Anfahrt. Quelle und Vektorlänge werden vor dem Zugriff geprüft. Der bestehende Kontext bleibt lebender gültiger Spieler in STAND/CROUCH, normale Gravitation und gültige endliche Bewegung. Eine vorhandene Referenz muss weiterhin eine statische gültige Brush derselben Welt sein; eine fehlende Referenz folgt der bereits in010 eingeführten engen Regel.

Die einzige Bewegungskorrektur bleibt `move.up=0` für zuvor positiveUP. Rohdiagnostik wird vorher erfasst. Kein zusätzlicher Ray, Entity-Lookup, RNG-Zugriff oder Entity-/Velocity-/Support-Write. Kein Reset oder Umbau von Navigator, Sprungclock, Radius, Flags, Ziel, Deadline, Flugfortsetzung oder Ankunft. FALL/SWIM/DIVE,12→34 und andere Anfahrtskanten bleiben ausgeschlossen. Die globale Konfigurationsbindung ist passiv; Lebens-/Botzustand bleibt separat.

## Reproduzierbare Prüfung

Die echte010-Zustandsfolge1025–1035 wird als aufgezeichnete Eingabe in den ursprünglichen Navigator/RawCapture/Helper-Pfad gespielt. Sie ist ausdrücklich keine Physiksimulation oder Vorhersage des neuen nativen Fluges. Die beiden bisherigen positivenUP-Pulse auf11→12 werden bei vorhandener beziehungsweise fehlender Referenz entfernt; spätere12→34-Ausgaben, übrige Bewegungswerte, Navigatorübergänge, originale Deadline, Generation, RNG sowie Entity-/Support-/Velocityzustand bleiben unverändert. Diagnose an/aus wird separat geprüft.

Zusätzlich geprüft: echter `BotSupplyTick`-Übergang an11, unveränderte13→12-Alternative trotz desselben markierten Ziels,11-Metadaten-/Linkreihenfolgefehler, Blockierung von11 oder12, Serial/Ready-Verlust, bewegliche/fremde Referenz und ausgeschlossene FALL-/Wasserzustände. Das echteTick-Fixture wurde als gemapptes Minigunziel mit passender ursprünglicher Startzeit/Deadline aufgebaut; ein zuerst versehentlich als gewöhnliches altes12s-Ziel angelegter Fall endete korrekt im Timeout und wurde als Fixturefehler korrigiert. Diese Korrektur verändert keine Produktivquelle.

Erste gezielte RED-Prüfung gegen unveränderte integrierte010-Quelle:1915Checks/7 erwartete Fehler. Danach GREEN1915/0. Erweiterter finaler normaler SDK107-Test:1918Checks/0. Der finale Testsatz wurde zusätzlich in einer temporären Kopie gegen den unveränderten010-Header geprüft, ohne den eigenen überprüfbaren Quellstand zurückzuändern. Finaler Gegencheck gegen unveränderten010-Header:1918Checks/11 erwartete Fehler; finaler011-Header:1918Checks/0 unter SDK107 und ASan/UBSan. Der Driver-Actiontest bestand ebenfalls mit ASan/UBSan.

```
python3 poc/candidates/redstation-supply-20261107/test_cecil_native_bridge.py --sanitize --sdk-player /srv/tse-sdk-20261021/Sources/EntitiesMP/Player.es
python3 poc/candidates/redstation-supply-20261107/test_cecil_action_native.py --sdk-player /srv/tse-sdk-20261021/Sources/EntitiesMP/Player.es
```

Der tatsächliche Driver-Actiontest mit SDK107 und ASan/UBSan ist bestanden. Windows-Build, neue native11→12-Wirksamkeit, vollständiger Tiervergleich und Produktionsfreigabe bleiben Root vorbehalten und sind hier nicht behauptet. Ausgangsbasis ist die integrierte010-Quelle `b2f46e1725be49151ac062a565723afff2248c6a`; vor dem Fix waren die Candidatequellen dazu identisch. Unabhängige Berichtsarbeit wurde beim lokalen Merge erhalten.

Die unabhängige Quellprüfung fand keinen wichtigen/kritischen Produktivbefund. Das zusätzliche Diagnosefixture leitet seine finale Action jetzt aus dem tatsächlich korrigierten `move.up*11` ab und prüft explizit Roh-UP1/finale-UP0. Die neue Behauptung scheiterte mit dem vorher hartkodierten finalen11-Wert als1918Checks/1 Fehler, bevor ausschließlich dieses Testargument korrigiert wurde.

Auch der abschließende, unabhängig überprüfte Testsatz mit dieser abgeleiteten finalen Action besteht unter SDK107 und ASan/UBSan mit1918Checks/0 Fehlern.
