# A4 – begrenzte passive Actionbeobachtung der Waffenversorgung

## Status

Die Source-Erweiterung ist offline geprüft und zur unabhängigen Rootprüfung bereit. Es wurde keine Gameplaykorrektur vorgenommen. Die Ursachen der beiden Bewegungsverzögerungen aus dem Build016-Lauf 104821 bleiben bis zum neuen nativen Beleg offen.

Basis ist baec731b9e17adf0f43f22168d49a09a3d536bf7. Die Arbeit liegt ausschließlich im Worktree /srv/tse-milestone-a-a4-passive-supply-observer-20261112, Branch codex/20261112-a4-passive-supply-observer. Die vorherige Analyse /srv/tse-a4-supply-causal-analysis-20261112 und alle ursprünglichen FAILs bleiben erhalten.

## Enger Produktionsdiff

BotSupplyNative.h erhält genau 100 additive Zeilen. BotDriver.cpp, die vorhandenen Tests und die eigentliche Navigations-, Waffen-, Safety-, Input- und Rotationslogik bleiben bytegleich. Der neue Capture wird unmittelbar nach dem vorhandenen Approach-Capture mit dem schon berechneten Navigatorergebnis aufgerufen. Der neue Final-Beobachter liegt im bereits vorhandenen Final-Hook, den der Driver nach SetAction aufruft.

Es gibt keine zusätzliche Navigation, Casts, Welt-Entity-Suche oder RNG-Nutzung. Die Prüfung der vorhandenen veröffentlichten RedStation-Bindung liest nur deren Zustand: ursprünglicher Weltpfad, World-CRC ff3776e0, NAV-CRC e4571656 und vorhandene Metadatenprüfung werden weiterhin ausschließlich vom bisherigen Loader abgesichert.

Der bestehende Schalter bleibt standardmäßig aus. Das genaue Opt-in für ein später von Root geprüftes Testfenster lautet:

```text
bot_bDiagnostics = 1;
```

bot_bEnabled und bot_bSupplyNavigation müssen im bereits geprüften Testaufbau aktiv sein. Die Erweiterung fügt keinen neuen Gameplay- oder Freigabeschalter hinzu.

## Zulassung, Identitäten und feste Grenzen

| Klasse | Tatsächlich beobachteter Zustand |
|---|---|
| north68_6 | Bereits gewählte Kante mit SourceSlot 68 und Zielhop 6; der tatsächliche Reached-/Austrittsübergang wird noch mit seiner finalen Action erfasst. |
| source87 | Noch ungebundene Quellpunktannäherung: SourceSlot kleiner 0, Anchor 87 und Hop 87; eine bereits gebundene Kante nach 87 gehört nicht dazu. |

Zusätzlich verlangt der Beobachter ein gemapptes Waffenziel, keine Follow-/Important-Interaktion, gültige Welt-/Entity-/Life-Identität und keine Nutzwaffenbits aus 0x3df8 in owned oder usable. Bereits vorhandene, lediglich leergeschossene Nutzwaffen eröffnen dieses Fenster ebenfalls nicht.

Das Kontingent liegt in eigenem statischem Diagnosezustand außerhalb von SSupplyState. Pro Klasse, Slot und Mapepoche werden maximal 200 tatsächliche Actions innerhalb von weniger als 10 Sekunden seit dem ersten Capture ausgegeben. Zwei Klassen und vier lokale Slots ergeben maximal 1600 neue Zeilen pro Viererprozess und Mapepoche. Bestehende andere Diagnosetags sind davon unverändert.

Tod, ClearGoal, Goalwechsel, vollständiger Supply-Reset sowie Diagnose-Aus/Ein erneuern das Kontingent nicht. Ein zulässiger neuer Goal auf derselben beobachteten Annäherung behält Startzeit und Zähler. Lebens-/Entity-/Weltbruch, rückläufige Tick-/Capturezeit, fehlende frische Capture-Zuordnung, Fristablauf oder Ende der Klasse schließen das laufende Fenster. Nur ein höherer, gültig veröffentlichter Mapserial eröffnet eine neue Epoche. Ein alter Serial kann keine ältere Epoche wieder öffnen.

## Inhalt und Aussagegrenzen einer Zeile

Der neue Tag lautet CecilSupplyDiagWindow. Jede ausgegebene Zeile gehört genau zu einem frischen Capture und dem folgenden vorhandenen Final-Hook mit identischem Tick/Zeitwert. Sie enthält:

- Lokalen Slot, Klasse, Mapserial, Entity, Generation, Tick, Driverzeit, Samplezähler und Alter des festen Fensters.
- Erfasstes Ziel, tatsächlichen vorherigen Source/Hop, Reached, Navigatorergebnis, Anchor, Flags, Aktiv-/Arrived-/Stuck-/Relocated-Zustände und ursprüngliche Bewegungs-/Drehwünsche.
- Bestehende owned-/usable-Masken sowie Goal-Anfang und Deadline.
- Finale Navigationsübernahme, Sichtbarkeit, Safety-Ergebnis, danach tatsächlich vorhandenes Ziel/Source/Hop sowie die an SetAction übergebene Translation, Rotation und Buttons.
- Aktuelle Position, Geschwindigkeit, Schwerkraft, Support-ID/-Typ/-Physik, PlayerState sowie Körper-, View- und LastRotation-Winkel.
- Den bereits vorhandenen SCecilProbe-Zustand: Anfrage, Safety-Yaw, erste/letzte Ursache, Ursachenmaske, Wall-/Floor-Zähler, Kontaktfelder, Normale sowie vorhandene Start-/Endpunkte.

SCecilProbe bleibt seine bisherige aggregierte Ablage. Es entsteht keine vollständige Liste einzelner Casts; erste/letzte Ursache und Geometriefelder dürfen nicht nachträglich beliebig miteinander gleichgesetzt werden.

Die Driverzeit ist Tick × TickQuantum, keine neue serverseitige Quittung. SetAction belegt eine übergebene Clientaction; ihre serverseitige Verarbeitung oder Wirkung ist damit noch nicht nachgewiesen. Position/View/Velocity gehören zur vorhandenen Clientbeobachtung am Ausgabezeitpunkt. Nachfolgende Zeilen und die bestehende phasengebundene Inventar-/Registry-Erfassung müssen separat zugeordnet werden.

Floatfelder nutzen begrenzte %.9g-Ausgaben. Dadurch kann der neue Datensatz den unveränderten 2048-Byte-BotLog auch bei großen endlichen beobachteten Werten vollständig einschließlich Zeilenende erreichen. Das Format hat bei den verwendeten Integer-/Floattypen einen konservativen numerischen Höchstbedarf von 1869 Zeichen unter Win32 bzw. 1988 unter LP64; der reale Loggerpfad wird zusätzlich mit großen endlichen Payloadwerten geprüft. Es gibt keine zusätzliche Abschlusszeile außerhalb des 200er-Budgets.

## Reproduzierbare Prüfungen

Der neue Test importiert den unveränderten bestehenden Bridge-Harness. Er führt die Produktionsfunktionen BotSupplyTick, BotCecilSafeMotion und den bestehenden Final-Hook mit SDK-förmigen World-/Physics-Stubs aus. Die synthetischen Routekoordinaten testen die Beobachterklassen; sie sind keine Behauptung über originale Flugphysik. Die vorhandenen Action-Guards werden gesondert aus dem tatsächlichen Driver geprüft.

| Prüfung | PID | Ergebnis |
|---|---:|---|
| SDK107-Baseline vor Produktionsänderung |1192516|2687 Checks, 0 Fehler|
| Aktivierungs-RED gegen unveränderte Produktion |1192635|6 Checks, 2 echte Assertionfehler|
| Identitäts-/Quota-RED |1192792|50 Checks, 24 echte Assertionfehler|
| Probe-Payload und vollständige Logzeile, RED |1193134|66 Checks, 2 echte Assertionfehler|
| Rückläufige Zeit bei steigenden Ticks, RED |1193365|68 Checks, 2 echte Assertionfehler|
| Abschließender neuer Beobachter, SDK107 + ASan/UBSan |1193660|68 Checks, 0 Fehler, Exit0, 35,48 s|
| Abschließende bestehende Bridge, SDK107 + ASan/UBSan |1193718|2687 Checks, 0 Fehler, Exit0, 31,70 s|
| Tatsächliche Driver-Action-Guards mit SDK107 |1193697|PASS, Exit0, 1,09 s|

Die Beobachterfälle prüfen unter anderem wirkliche neue Goal-IDs, unveränderte Grenzen bei Reset/Tod/Aus-/Ein, die frische Final-Zuordnung, beide Klassen und alle vier lokalen Slots. Vier jeweils 240 Actions lange OFF/ON-Vergleiche decken freie und vollständig blockierte Safety für beide Klassen ab. Dabei bleiben sämtliche Bewegungsfelder, finale Actions, Safety, RNG- sowie Cast-/Lookup-Ergebnisse gleich.

Die vollständigen Originalausgaben liegen in /srv/tse-a4-passive-supply-observer-evidence-20261112. Ausschließlich die FINAL-Receipts und der folgende Manifeststand sind die abschließende Prüfung. Zwischenläufe bleiben erhalten. Eine zusätzliche Extremzeit-Fixture mit TickQuantum 1e280 erzeugte tatsächlich keine zulässige Navigatoraction (0 Zeilen, Source -1); ihre Assertion war ungeeignet und wird ausdrücklich nicht als Produktions-RED gewertet. fixture-correction.json enthält diese Einordnung und die unveränderten Ausgaben. Dort ist auch ein sofort beendeter Aufruf mit falsch geschriebenem SDK-Pfad dokumentiert; dabei starteten weder Compiler noch native Prozesse.

Die ausführbaren Offlineprüfungen lauten:

```bash
python3 /srv/tse-milestone-a-a4-passive-supply-observer-20261112/poc/candidates/redstation-supply-20261107/test_supply_observer_native.py --sanitize --sdk-player /srv/tse-sdk-20261021/Sources/EntitiesMP/Player.es
python3 /srv/tse-milestone-a-a4-passive-supply-observer-20261112/poc/candidates/redstation-supply-20261107/test_cecil_native_bridge.py --sanitize --sdk-player /srv/tse-sdk-20261021/Sources/EntitiesMP/Player.es
python3 /srv/tse-milestone-a-a4-passive-supply-observer-20261112/poc/candidates/redstation-supply-20261107/test_cecil_action_native.py --sdk-player /srv/tse-sdk-20261021/Sources/EntitiesMP/Player.es
```

## Pins und Root-Übergabe

| Datei | SHA-256 |
|---|---|
| BotSupplyNative.h |ad54eef28d087654dd7ad5107f547091f1cda5b7ed2f03e06e9ec40593064bd1|
| Neuer test_supply_observer_native.py |c48a41b2cab7e3c6f781025dc5337a4e6eea2c61f66d467ed4216c6f32a0c6ae|
| Unveränderter BotDriver.cpp |b377dbcf222e6f35d09d2c570b8a768e3977d277cf4e830878c6f0ac2c2d4265|
| source-manifest.json im privaten Belegverzeichnis |bb346c82882f4abfd70ab3c30c068f45123dd07a4ac606d2608c1af85537d69f|
| RUNPLAN-disabled.json im privaten Belegverzeichnis |8d64f06924f7b716705797a378bd4d5a837d76fc7add9a59e2afb4c3def87bee|

Der Manifest enthält zwölf konkret geprüfte Source-/Harness-/SDK-Pins. Der Git-Commit bindet den übrigen unveränderten Repository-Stand. Dies ist kein Runtime-Closure-Manifest und keine DLL-Qualifikation.

Root besitzt weiterhin allein Integration, Build und Runtime. Für die neuen Zeilen ist eine neue, separat gepinnte DLL erforderlich. Es wurde kein ausführbarer nativer Controller erstellt oder freigegeben. runtime_reviewed, native_start_enabled und native_qualified stehen in Manifest und Runplan auf false.

Nach unabhängiger Annahme des Source-Diffs sieht der minimale native Plan genau ein neues, eindeutig benanntes Fenster des bestehenden begrenzten A4-Protokolls vor. Der 300-s-Rahmen sowie Runtime-Lock, CPU-/RAM-/Diskgrenzen, geordnete Runden, Transition-/Close-Guards, frühe Inventar-/Epochbindung und exakte Wiederherstellung bleiben bestehen. Es gibt keine automatische Wiederholung oder Fristverlängerung. Die acht ursprünglichen Bot-/Pickup-/Fire-Abnahmen bleiben unverändert.

Die Auswertung ordnet die neuen Zeilen nach Prozess, Slot, Mapserial, Entity, Generation und Tick zu. Erst tatsächlich vorhandene Requests, Reached-/Safety-Daten, final übergebene Actions und folgende Bewegungszustände dürfen eine Ursachenhypothese stützen. Tritt eine Klasse nicht auf oder endet das Fenster zu früh, lautet der Befund NOT_OBSERVED. Daraus entstehen weder ein Pickup-/Fire-PASS noch eine nachträgliche Aufwertung des alten 104821-FAILs.
