# Weapon220: zulässige Zwischenankunft erneuert den Fortschrittsbeleg

Der echte SDK107-Reproducer zeigt eine konkrete Livenesslücke: Wiederholte zulässige Rückwechsel über einen erreichten Nachbarknoten lassen den10s-NoProgressbeleg immer neu beginnen, obwohl dasselbe Erstwaffenziel unverändert bleibt. **4181 Checks, ein gezielter RED**, keine Produktionsänderung. Die primäre physische Ursache im geschlossenen032-Nativfall bleibt UNKNOWN; keine Pickup-/Connector-/A4-/Verbesserungsfreigabe.

## Enger nativer Bezug, ohne erneuten Rawdurchlauf

Verwendet wurden ausschließlich die vorhandenen032-Ableitungen `long-no-useful-focus.json` und `source-custody-final.json`, ursprüngliche LittleTrouble-Navmetadaten und Produktionsquellen. Der betroffene eigene Bot A0/global0, Generation39, hatte44,239227s beobachtetes Leben ohne Usefulbesitz. Weapon220 ist im Teilversuch tick10489–10889 unverändert an Goal27 gebunden: Source-Deadline544,450 bei Beginn524,450, Ende `timeout`. Diese Sourcezeiten werden nicht mit nativen Spielsekunden fusioniert.

20 gedrosselte SourceStates während dieses Versuchs zeigen keine Ziel27-Ankunft, sondern zunächst55→60, danach wiederholt60→59 und62→60. Originale lokale Punkte:

| Slot | Position | Radius | Bedeutung |
|---|---|---:|---|
|27|(-68,75;4,5;-0,25)|2|Waffenziel220|
|59|(-65,5;4,5;18,75)|2|gewöhnlicher Zwischenpunkt|
|60|(-55,25;0,5;19,25)|1|gewöhnlicher Zwischenpunkt|
|62|(-61,25;0,5;22,75)|1,5|gewöhnlicher Nachbar, Link nach60|

Alle vier haben Flags0 und keinen Lock. Tick10680/10760 zeigen anhand der gedruckten Positionen eine robuste ursprüngliche62-Radiusankunft bei weiterhin nicht erreichtem59. Das kann `CecilNavigator::Update` legitim als Relocation behandeln; die feste Deadline wird dabei nicht verlängert. `BotCecilRebudgetWeapon` schließt gemappte Waffen ausdrücklich aus.

Das beweist noch keine lückenlose native Transit-Uhr oder Kollisionsursache: `hop_clock` ist der separate Checkpointzustand, nicht `itemTransitSince`. `floor=2` bedeutet geprüfte Ausweichbewegung, nicht verworfene Endbewegung; `rays` ist16 minus Restbudget und `liquid` enthält den PlayerState. Referenz187 belegt allein weder eine bewegliche Plattform noch eine bestimmte Klasse. Keine Terminalzeile in diesem Teilversuch ist mit den beobachteten `hop!=goal` vereinbar, beweist bei1Hz aber nicht das Fehlen jedes kurzen Connectoraufrufs. Pickup-Receiver/ACK fehlen weiterhin.

## Echter Source-RED

Die neue Fixture in `test_cecil_native_bridge.py` ruft reale BotSupplyTick→ChooseGoal/Nearest→Navigator.Update→SafeMotion→HopCheckpoint/ItemTransit auf. Initial wird Source60 tatsächlich belegt; danach werden weder Anchor62 noch Source/Hop manuell gesetzt. Die feste gewöhnliche induzierte Teilgraphik27/59/60/61/62 verwendet ursprüngliche Koordinaten/Radien und vorhandene gerichtete Kanten. Ausgelassene globale Routen, synthetische frei/passierbar-Casts, statischer WorldBase-Support und interpolierte Positionen sind ausdrücklich Testbedingungen, keine native Physiksimulation.

Die geskriptete3s-Schleife ergibt7×60→59 und7×62→60. Der erste beste Abstand zu Goal27 beträgt23,116461m bei1,05s und wird danach nicht mehr verbessert. Trotzdem wird `itemTransitSince` bei1,40/2,95/4,40/…/19,40s neu gesetzt. Bei19,95s ist Ziel220 unverändert und seine lokale Transit-Uhr nur0,55s alt. Der gewünschte Schutz gegen das volle20s-Zirkulieren schlägt fehl. Radius-/Ray-/Lifetime-/Inventarkontrollen und der positive echte59→27-Routenfortschritt bestehen; die bisherigen4175 Checks bestehen ebenfalls.

```sh
TMPDIR=/dev/shm nice -n 15 python3 -B poc/candidates/redstation-supply-20261107/test_cecil_native_bridge.py --sdk-player /srv/tse-sdk-20261021/Sources/EntitiesMP/Player.es
```

Der normale SDK-Lauf lief mit unverändertem Produktionsheader und Windows-`far`-Makro. Kein ASan-/MSVC-/Retail-/Nativeversuch in diesem Auftrag. Im ersten vollständigen RED-Log steht eine reine Einrückungswarnung bei zwei benachbarten Fixture-`if`s; anschließend nur in zwei Zeilen getrennt, keine Produktions-/Testsemantikänderung. Private Quittung enthält die genaue Log-/Sourcezuordnung.

## Engster nächster Fixentwurf – noch nicht umgesetzt

Einen bereits beobachteten gerichteten Abschnitt innerhalb **derselben** World/Map/Spieler/Generation/Item/Goal/Attempt/Deadline nicht allein wegen einer erlaubten Nachbar-Relocation mit neuer NoProgress-Allowance versehen. Ein begrenzter gespeicherter Beleg müsste dieselbe erneut besuchte Kante samt bisher bester Distanz erkennen; echtes neues gerichtetes Vorankommen und neue≥0,75m-Bestdistanz bleiben relevant. Bloß die Source/Hop-Gleichheit aus der bestehenden `same`-Bedingung zu entfernen wäre falsch: Distanzen zu verschiedenen Hops sind nicht vergleichbar.

Vor Gameplaycode entscheidet Root über den engen Episodenvertrag. Gegenfälle müssen echte neue Kanten-/Zielankunft, legitim längere Umwege, neue Need-/Goal-/Life-/Map-/Gravitykontexte, physische Locks, Spezialkanten, fehlende CurrentPoint-/Owner-/Acceptedbelege, Budgetlücken und feste Enddeadline schützen. Keine Verlängerung, kein synthetisches Reached/Acquisition/Floor und keine Radius-/Pit-/CD-Lockerung. Der bewiesene SDK-Mechanismus begründet einen gezielten Fixversuch, erklärt aber nicht rückwirkend alle langen nativen Waffenlücken oder die erste blockierte Bewegungsrichtung.

Falls die erste physische Ablehnung kausal benötigt wird, fehlt genau ihr bereits berechneter `SCecilProbe` auch bei akzeptiertem Escape2, plus derselbe Update-`relocated/reached/source/hop`-Kontext. Der bisherige MotionProbe-Logger schreibt nur bei Safety0. Das ist eine benannte Messgrenze, kein Vorschlag für eine weitere ungerichtete600s-Wiederholung.
