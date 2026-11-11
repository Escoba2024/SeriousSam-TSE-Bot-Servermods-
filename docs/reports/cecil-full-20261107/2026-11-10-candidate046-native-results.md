# Normal046: Supply und Hole scheitern, Skulls-Routen bleiben offen

Normal046 ist nicht insgesamt qualifiziert. Quelle `c298cf241b514b28f6d28e815bb5718a5a1d3d6c`, Tree `dba553b039a8a4dd10de27168f37671a1da48d84`, DLL `b148ae2e9ccfb337a6311bd81c4cdedafb9eac5d48bbb31126673eec51554816`. Der korrekte Supply-Builder kompiliert 15 MSVC-Einheiten und linkt PE32/x86. Alle 28 Overlay-Dateien und 47 gesamten Build-Eingaben sind geprüft; gegenüber 045 ändern sich ausschließlich Supply-Header und NAV-Suchhelper. Driver und rein lesender Waffenobserver bleiben unverändert. [Bereinigtes Buildmanifest](build046.json), SHA256 `fadab0b4fff2b94cdd2a6a533d5c76e32a433c66f8b98c516a820faa48515b8c`; privates Originalmanifest `7dc5af8b2dd5ddd636ad2077fffdeb0f0ae153bc49156d56d312a5d6c027d170`.

## Änderung und tatsächlich geprüfter Umfang

Die passive Hop-Fortschrittshistorie übersteht NULL- oder andere gültige Brush-Referenzen derselben Welt. Eine solche Beobachtung erteilt keine Bewegungs- oder Checkpoint-Freigabe: Aktuell gültiger statischer WorldBase-Kontakt und eine im selben Tick erfolgreiche gewöhnliche Nearest-/LOS-Erfassung bleiben dafür nötig. Der bestehende Unterschied zwischen passiver Beobachtung und aktueller Freigabe wird ausdrücklich erhalten.

Nach zwei tatsächlich akzeptierten erfolglosen Checkpoints derselben gewöhnlichen Patrouillenkante kann ein fester sechssekündiger Alternativversuch beginnen. Monotoner Bestgewinn von mindestens 0,75 m setzt die Fehlversuchszählung zurück; der reale 0,764778-m-Gegenfall darf nicht als fehlender Fortschritt gelten. Hinweise bleiben innerhalb 32 m euklidischer Distanz und 8 m Höhe. Die vorbereitete gerichtete Elternkette muss ihren tatsächlichen Suchstart erreichen und die gescheiterte Kante vermeiden. Höchstens drei LOS-Prüfungen und ein neuer Kandidatensuchlauf pro Tick teilen das vorhandene 16-Strahlenbudget mit der abschließenden Sicherheit.

Hint, echte Ankererfassung und Originalradius-Ankunft sind getrennt. Jede Alternativbewegung verlangt aktuellen statischen Kontakt sowie frische Wand- und zwingende Bodenprüfung, auch bei gewöhnlicher Pit-Policy0. Horizontale Norm höchstens 0,3, Up=0, Strafe-Vorgabe und feste Frist bleiben verbindlich. Weder Originalgraph noch Radien, Locks, Spezialpunktregeln oder Itemfristen werden erweitert. Die [Entscheidung zum begrenzten Alternativversuch](../../decisions/2026-11-10-cecil-repeated-patrol-edge-recovery.md) beschreibt diese bewusste Adapterregel, keine vollständige Originalmod-Parität.

Die finale SDK107-Bridge besteht mit 1086/0 unter ASan/UBSan; neun portable C++-Prüfungen, Driver-/Item-/Originalexport-Verträge und der unveränderte Waffenobserver bestehen. Nach tatsächlicher Bindung aller 30 privaten Vorlagen bestehen unabhängig 158 reine Harness-/Auswerterprüfungen: Safe34+Funktionsguards3, Supply33, Retail20, Matched18, Rotation6, Featureindex16 und Waffenreader28. Das sind keine zusätzlichen nativen Läufe oder Ressourcenmessungen.

Zwei Vorbereitungsgrenzen bleiben nachvollziehbar: Eine frühe 977-Prüfungen-Fixture löste keine echten Checkpoints aus und bleibt **INCONCLUSIVE**; erst der positive Kontrollfall mit tatsächlich zwei Checkpoints und Originalquellpunkt-Neuannäherung liefert den gültigen RED979/1. Eine private vorbereitende Assertion verwechselte zunächst 28 Overlay- mit 47 gesamten Build-Eingaben und brach vor Build, Pinbindung und Runtime ab. Der folgende korrekte Build prüft beide Mengen getrennt; der Binder verknüpft die Overlay-Hashes ausdrücklich mit dem veröffentlichten Source-Tree. Keiner dieser Vorgänge wird als nativer Erfolg oder verschwiegener nativer Versuch gezählt.

## Vollständige native Fenster

| Prüfung | Tatsächlicher Umfang | Ergebnis |
| --- | --- | --- |
| Supplyv19 | Zehn feste Erstziele und zehn feste Initialleben; 594 korrekte Ein-Bot-Abfragen, elf normale Abschlüsse | Erstziele 10/10, Median 9,9 s, **P95 30,5 s > unverändert 30 s: FAIL**. |
| Skulls | 600,008063 s, 595 Statusabfragen, volle Abdeckung, positive Scoreänderungen aller acht, maxquiet 6,052235 s, keine erkannten Monitorfehler, drei normale Abschlüsse | Numerische Grenzen erfüllt; tatsächliche 152-s-/32-s-Routenlücken halten die funktionale Freigabe **OPEN**. Session Exit0 ist kein Gesamt-PASS. |
| Hole | 600,011153 s, 595 Statusabfragen, volle Abdeckung, positive Scoreänderungen aller acht, keine erkannten Monitorfehler, drei normale Abschlüsse | **FAIL**: unbegründeter Stillstand 31,291447 s > 10 s und Aktivität 32,1 s nach Spawn > 5 s. Der unveränderte Validator beendet die Session mit Exit1. |
| Original-Retail046, übrige drei Karten, formale Stunden, Ressourcen, Rotation, Recovery und All6 | Nicht durchgeführt | Keine Übertragung historischer Erfolge; insbesondere bleibt der Retail-/Stunden-Guard wegen fehlendem Supply-PASS geschlossen. |

Der allgemeine Monitorstatus allein ist kein Funktionszertifikat. Seine separaten 600-s-Fenster erfüllen keine 7200-s-Stundenprüfung; Scoreentwicklung oder Positionsänderung ersetzt keine wirksame Wegpunktfortsetzung.

## Versorgung: richtige Erwerbe, aber tatsächlicher Latenzfehler

Die zehn festen Initialleben ergeben 8,35 / 3,90 / 5,20 / 10,15 / 30,50 / 9,90 / 12,00 / 9,90 / 26,75 / 3,95 s. Median 9,9 s besteht die unveränderte 15-s-Grenze, P95 30,5 s überschreitet die unveränderte 30-s-Grenze. Der fünfte Fall wird nicht gerundet, ausgefiltert, durch einen späteren Spawn ersetzt oder mit einer neuen Schwelle gerettet.

Alle zehn chronologisch ersten ausgewählten Waffenversuche sind im jeweiligen Leben anhand gewählter typisierter Entity, passendem Besitzbit und angrenzendem nativen GoalEnd korreliert. Das beweist keine universelle Pickupreichweite und keinen exakt instrumentierten ReceiveItem-Aufruf. Alle 26 Waffenstarts bleiben erhalten: 25 korroborierte Erwerbe und ein tatsächlicher Nichtkohorten-Timeout, Rang13/Fall5/Laser267. Insgesamt liegen 34 Goalstarts vor. Es gibt keinen ersatzweise ausgelassenen rechtszensierten Waffenversuch; vorläufige Reconcile-Markierungen der ersten neun Fälle bleiben als Zwischenstände erhalten, der vollständige Zehner-Replay ist nicht inkonklusiv.

Zehn unterschiedliche PID-/Start-Epochen und feste Initialleben, elf normale Unit-Abschlüsse, zehn tatsächliche Leerslotantworten und 17 unveränderte Original-/Konfigurationspins sind geprüft. Die unveränderten Kriterien verlangen mindestens 9/10 Erstzielerfolge **und** passende Initialleben-Latenzen; 10/10 Erwerbe heben den P95-Fehler nicht auf. Main und unabhängiger vollständiger Review bestätigen denselben NONPASS. Es existiert kein Supply046-PASS-Zertifikat.

Main-Verdict-SHA256 `77f5e64be7ac5b5d1c4242423ecb5dbb6147ea9157260abbca039c3254d44ab3`; unabhängiger Review `d5cf786ab1e5b2ab0bcb097de973617819a5527281bf9c838423f3ca8f052919`; numerischer Audit `c36fa03cac5455c54f1e4aae3867934eedeb0c128580bb58ff316347e390ac49`.

## Skulls: begrenzte Checkpoint-Fortsetzung und offene Routen

Vier Checkpoints haben getrennt bewertete Folgen. Zwei zeigen im selben Ziel-/Lebenskontext autonome deutliche Höhenbewegung vor späterem Combat. Ein weiterer wird von regulärem Zielwechsel begleitet und belegt daher nicht das Erreichen des alten Ziels. Der späte vierte zeigt nach Source-Neuannäherung echte nachfolgende Hop-/Ankerfortsetzung im selben Zielkontext vor Combat. Aus diesen Kontrollfluss- und Positionsfolgen wird weder eine bestimmte Transportentity noch vollständige Zielerreichung abgeleitet. In Skulls gibt es **keinen** `CecilPatrolRecovery`-Event; diese Karte liefert keinen nativen Erfolg für die neue zweite Komponente.

BotB:2 bleibt im gemessenen Fenster 152 s auf demselben Goal/Hop. Rund 427,83 m aufsummierter Sampleweg werden nicht zu wirksamer Hop-Fortsetzung; Schusszähler und fehlende Gegnersicht bleiben konstant. Alle 153 erfassten Zustände sind STAND. Ob ein unprotokollierter Zwischenzustand, eine STUCK-Phase oder ein anderer aktueller Guard die Historie löscht, ist nicht aus diesen 1-Hz-Proben bewiesen. Die Klassen der wechselnden Referenzen werden nicht geraten.

BotB:3 bleibt 32 s in einem weiteren gleichen Hop-Kontext. Acht tatsächliche FALL-Proben unterbrechen die STAND-Abschnitte; jeder beobachtete STAND-Abschnitt ist höchstens 3 s lang. Damit kann die auf STAND/CROUCH begrenzte durchgehende Fünf-Sekunden-Historie diesen Kontext nicht erhalten. Späterer Combat und Zielwechsel sind kein autonomer Heilungsnachweis. Beide Routen bleiben offen, ohne daraus einen erfundenen Zehn-Sekunden-Stillstandsfehler zu machen.

Die tatsächlichen nativen Monitorgrenzen sind BotA Tick200..12160 und BotB Tick20..11980. Der zusätzliche B2-Rohlogpunkt bei Tick12000 gehört zum Nachlauf und verlängert den gemessenen Kontext nicht auf 153 s. 64 strenge Health-Death→Folgegeneration-Respawnpaare sind im Fenster belegt, 35A+29B; maximal 1,9 s Death→Spawn und 0,9 s bis beobachteter Aktivität nach Spawn.

Main-Verdict-SHA256 `cbc4bbe1079a6c5f52696d817409fe9d4b44436f3f83263337ddcb8f350fa40c`; unabhängiger vollständiger Review `b015b623a03c33b1670b25bfbcb54a337233aea1c18321f1d0683357aa21c32a`.

## Hole: echte Grenzverletzungen trotz begrenzter Alternativerfolge

Das vollständige Fenster scheitert bei BotB:2 an 31,291447 s unbegründetem Stillstand. Im selben Leben liegt der native Spawn bei Tick2198, die erste später belegte Aktivität bei Tick2840: **32,1 s nach Spawn**, deutlich über der unveränderten Fünf-Sekunden-Grenze. Der erste kleine Positionsversatz nach Combat genügt noch nicht; erst die spätere große Positionsänderung überschreitet das bestehende Aktivitätsmaß. Sie wird weder als autonome NAV-Recovery noch als identifizierter Teleporter gewertet.

Die Zustandsproben zeigen akzeptierte Bewegungsanforderungen bei unveränderter tatsächlicher Position. Das beweist keine native Anwendung dieser Eingabe. Der protokollierte Waffen-Wartezustand ist ein weiterer korrelierter Lebenszyklushinweis; eine Kamera-, Event- oder Kollisionsursache ist damit nicht bewiesen. Das erste betroffene Goal endet bei Tick2408 als **unavailable**, nicht als Timeout. Ein späteres Ziel endet ebenfalls unavailable. Aus diesen 046-Daten wird kein spekulativer FIRE-/USE-Fix oder Engine-Zustandseingriff abgeleitet.

Zusätzlich bleiben zwei tatsächlich bewegte, aber ineffektive gleiche Hop-Kontexte von 88 s und 200 s offen. Sie sind nicht die Ursache des numerischen Stillstands-Fails und werden nicht durch kurze Ausweichbewegungen als gelöst bezeichnet.

Die zweite Komponente wird hier tatsächlich ausgeübt: 13 Patrol-Tags enthalten fünf Eintritte. Main korroboriert zwei gewöhnliche Erwerbe von Originalpunkt52 mit echter physischer Folge und anschließender gewöhnlicher Navigation im selben Zielkontext. Drei weitere Versuche scheitern ausdrücklich an ausgeschöpften Kandidaten. Hinweise oder geloggte Erwerbe allein sind kein Zielerfolg; weder vollständige Zielerreichung noch ein direkter nativer Einzel-Floor-Receipt wird behauptet. Alle drei Fehlschläge bleiben erhalten.

Hole liefert 87 strenge Health-Paare im gemessenen Fenster, 46A+41B; keine unvollständigen Paare, maximal 1,9 s Death→Spawn. Gemeinsam mit Skulls sind das 151 unterschiedliche **046**-Paare. Die getrennte Bedingung Aktivität spätestens 5 s **nach Spawn** scheitert trotzdem an dem 32,1-s-Fall. Daher kein Respawn-Gesamt-PASS allein wegen der überschrittenen Anzahl100. Die nativen Hole-Monitorgrenzen sind BotA Tick200..12160 und BotB Tick40..12000; Nachlauf wird nicht zur Reparatur verwendet.

Main-Verdict-SHA256 `132887da95f38cb5bac5803f7cdb2cd4c4dbfae80cd69cb9cba2401d01b75368`; Main-Rohindex `09896fc0d38b029a71b61180f760414ef9461b09cab5f49f1e6f64cb39119c59`; unabhängiger vollständiger Review `7d6ac55f774ab9ae9e13d5462b118c96f739bf651c78185b42a6b96d027ce14c`.

## Messgrenzen, Integrität und Fortsetzung

Die Pflichtwaffen3/8/9/11/14, vollständige Sonderaktionen und CD plus native Animation sind nicht insgesamt abgenommen. Waffenwahl, tatsächlicher Gruppenimpuls, native Wanted-Annahme und vollständiger bekannter Familienexit müssen für jede echte unzensierte Kette getrennt gebunden werden. Unterschiedliche Timerdomänen werden nicht gleichgesetzt. Die vorgeschlagene algebraische Herausrechnung der gesamten Familienverweildauer ist ausdrücklich **keine Akzeptanzformel**; sie würde nicht bewiesene Warte-/Schedulerzeit als Animationsdauer gutschreiben. Frühere Policy-Opportunity bleibt offen. Historische045-Observerketten erhalten keinen046-Kredit.

Die private, hashgebundene Auswertung bindet vollständige Rohbytes, Kandidaten-/Prozess-/Map-/Lebensidentitäten und die tatsächlichen Fenster. Zur Offline-Reproduktion mit selbst bereitgestellten autorisierten Daten, ohne einen Spielprozess zu starten:

```sh
python3 tools/analyze_cecil_qualification.py "$EVIDENCE_DIR"
python3 tools/audit_cecil_native_log.py "$LOG" --epoch "$EPOCH_JSON" --useful-weapon-mask 0x3df8
python3 poc/candidates/redstation-supply-20261107/test_cecil_native_bridge.py --sanitize --sdk-player "$SDK107/Sources/EntitiesMP/Player.es"
python3 poc/candidates/redstation-supply-20261107/test_cecil_action_native.py --sdk-player "$SDK107/Sources/EntitiesMP/Player.es"
python3 poc/candidates/redstation-supply-20261107/test_cecil_items_native.py
python3 poc/candidates/redstation-supply-20261107/test_cecil_rules_exports.py "$PINNED_ANALYSIS_EXPORTS"
python3 poc/candidates/redstation-supply-20261107/test_cecil_weapon_observer.py
```

Der allgemeine Rohlog-Indexer ersetzt nicht den versionierten vollständigen Supply-Replay oder die manuelle geometrische Beurteilung. Main führt Build, Runtime und native Verdikte; die unabhängigen Reviews sind über ihre Hashes getrennt gebunden. Die Dokumentvorbereitung ersetzt keinen unabhängigen Main-Review. Main hat die sechs finalen Dateien einschließlich aller 41 Bereiche, 109 Quellanker, Build-/Native-Bindungen und unveränderten historischen Anhänge geprüft. Die Veröffentlichung führt Main getrennt aus.

Main protokolliert nach Hole um 01:07:20 UTC 289 aktuelle unveränderte Pins, normale Abschlüsse beider Kartenfenster und geleerte eigene Prozess-/Cgroup-Ressourcen. Postrun-SHA256 `8325c63cbd45a74ea480883763a5a0cea78dffd554fd92f523a70cae453880b2`. Quieszenz ist keine funktionale Freigabe. Ein separater öffentlicher Bestandssnapshot um 01:20:06 UTC zeigt sechs bisherige Instanzen mit je acht eigenen Bots und keinem zusätzlichen Spieler; dort wurde keine046-DLL installiert. Snapshot-SHA256 `705badb3af0967330e4b548b41df8a5f6e2e74bd193c7b7112d8764ea61baf94`.

Der getrennte passive 047-Teilpatch `096f7988ff68581461d3b3748e482b9250e75ec6` besteht portabel mit 1242/0 sowie neun C++- und vier Adapterprüfungen. Ein separat entwickelter rein lesender Player-Observer dient weiterer Messung, nicht der Heilung eines angenommenen Kamerafehlers. Einzelne Compiler-/Offlineprüfungen sind kein fertiger047-Kandidatenbuild oder Native-Nachweis. Kein046-Lauf wird einem047-Kandidaten angerechnet.

Die [41-Bereiche-Matrix](transfer-status.json) bindet den tatsächlichen046-Quellstand und die begrenzten nativen Fehler, während 045-/039-Historien erhalten bleiben. Original-Cecil-GPL-Attribution und die CPOL-/Patcher-Architekturgrenze bleiben getrennt; keine originalen NAV-/Retail-Daten, privaten Rohlogs oder Binärdateien werden veröffentlicht. [Alle045-Befunde](2026-11-09-candidate045-native-results.md) und frühere Fehler bleiben bestehen. All6+900s, reguläre Integration und alle fehlenden finalen Gates bleiben offen; es gibt keine046-Gesamtfreigabe.
