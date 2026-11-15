# Geschlossener A1-NoFire-Lauf005628: Pitchgain bleibt FAIL

Der Lauf scheiterte unverändert an `opposite pitch gain does not reproduce`.
Horizontal wurde diesmal je ein Engine-Cursorread beobachtet; bei negativem Pitch
wurde derselbe Versatz zweimal gelesen. Die neue aktuelle XRes-Zuordnung bindet
die Query-/Warp-Verbindung dieses Laufs an den eigenen Originalprozess. Sie
beweist weder die Ursache der Doppelverarbeitung noch eine historische Zuordnung
der früheren Verbindung U. Keine Implementierung, Runtime oder Grenzänderung.

Isolierter Audit-WT ab Rootfff0b2a; Claim ausschließlich neuer reiner Reader und
dieser bereinigte Bericht. Root allein integriert. Keine Controller-, Adapter-,
Gameplay-, Input-, Gain-, EPS-, FPS- oder Fristenänderung.

## Reproduzierbare vollständige Archivprüfung

Evidenz `/srv/tse-milestone-a-evidence-20261111/a1-xres-lifecycle-root-20261115-005628`,
ResultSHA256 `3e4398c98b2518b4dc44882243d4218d4f3f4678b8a1d36f0c34accaf6035e35`.
Tatsächlicher eingefrorener Sourceparent
`/srv/tse-a1-xres-lifecycle-root-frozen-20261115`, Manifest
`e9cb52a1135ea3046570fdaaac6e2f37ac2117535b8d4c312239f39d7cbec90c`.
Archivierte Controller-/CP-/Rotations-/Policyquellen sind bytegleich zum Parent;
benutzte reine Decoder und Evidenzquellen wurden gegen dessen Pins geprüft.

Der neue `tools/audit_a1_xres_closed_005628.py` ruft nur die gepinnten reinen
Decoder/Auditoren auf. Kein Controller-/Workerimport, Display, Prozessstart oder
Nativeaufruf. Tatsächlich erfolgreich replayt:

- Alle310RECORD-Rows,175124Byte, exakt abgeleitete Felder/Callbackserials,
  keine offenen Queryantworten. Bestehender Emissions-/Phasenauditor unverändert
  gegen alle6Phasen und8tatsächlichen Einzelrequests ausgeführt.
- Neue Lifecycle-/XResauswertung identisch zum geschlossenen Ergebnis:
  2Snapshots/28PIDqueries,2+28Arrays vollständig frei,3aktuelle Originalbasen,
  1lifecycleveränderte Base,238Original-Query/Warp-Rows.
- Alle278JS-Records bilden139vollständige benachbarte Input-/Actionpaare auf
  genau einem beobachteten Inputthread.134neutrale und5nichtneutrale Cursorreads.
  Yaw-Rawaction entspricht überall minus EngineX und dem lokalen Akkumulator-
  zuwachs; Compose-/Return-Reihenfolge stimmt. Alle139Cursor-/Recenterquittungen
  erfolgreich. Inputprofile und vollständige Guards sind privat erhalten.
- Alle59native Rotationspaare mit tatsächlicher PID/Start-/Entity-/World-/Life-
  Bindung und fortschreitenden eigenen Gameticks. Pitchvorzustände und beide
  ACK-Endpunkte bleiben an ihre echten CP-Quittungen gebunden.

Die4Core-`unsupported`-Rows sind dieselben4vom bestehenden Adapter typisierten
Nichtcursor-XTEST-Keyevents: zwei normale Forward-Down/Up-Paare. Weder zu
Cursorrecords umetikettiert noch als verloren/malformed entfernt. Legacyzählung
234unattributedQuery+4Warp bleibt in ihrer ursprünglichen Window-Resource-
Semantik erhalten; die separate neue XResauswertung bindet diese238Rows an die
aktuelle Original-PID. Die12nicht als Original klassifizierten Requestrows sind
die6Queryrequest/-reply-Paare der eigenen Controllerverbindung, keine belegten
fremden Spieler.17Start-/17Died-Rows derselben temporären Base bleiben UNKNOWN.

Privater vollständiger Replaybeleg einschließlich allerRawrows/139Paare/59nativen
Paare/2Snapshots/8Requests und Quellen-/Artefaktpins:
`/srv/tse-cecil-rollout-evidence-20261114/a1-xres-lifecycle-closed-audit-005628.json`,
1949641Byte, SHA256
`7b7a56d3a96a2a8b91669482f5fc3864ceb539fb65430ca8c19e856fedb147d5`.
Er enthält eigene Prozess-/Ressourcenidentitäten und bleibt privat.

```sh
cd /srv/tse-a1-xres-closed-data-audit-20261115
python3 -B tools/audit_a1_xres_closed_005628.py --output /srv/tse-cecil-rollout-evidence-20261114/a1-xres-lifecycle-closed-audit-005628-REPLAY.json
```

Ausgabe exklusiv0600, vorhandene Dateien werden nicht überschrieben. Ein anderer
Ausgabepfad verändert den Receiptinhalt nicht. Keine Native-/Testsuiteausführung
durch den Reader; dies ist eine geschlossene Daten-/Quellenprüfung.

## Tatsächliche Inputfolge und ACKs

| Phase | Normaler Request | Xclient-Sequenzintervall | Nichtneutrale Originalreads | Tatsächliche Antwort |
| --- | --- | --- | --- | --- |
| 0 | X+12 | 32→33 | ID55: rawX+12,EngineX+3 | Actionyaw−3°, kumulativerACK−3° |
| 1 | Forward Down/Up | 46→47 /50→51 | kein Cursorversatz | Bodyyaw−3,0000763° gegenüber vorher |
| 2 | X−12 | 64→65 | ID139: rawX−12,EngineX−3 | Actionyaw+3°, kumulativerACK+3° |
| 3 | Forward Down/Up | 77→78 /81→82 | kein Cursorversatz | Bodyyaw+2,9999695° gegenüber vorher |
| 4 | Y+12 | 95→96 | ID223: rawY+12,EngineY−3 | nativerPitchACK−3°/Gain−0,25 |
| 5 | Y−12 | 108→109 | IDs257/259: jeweils rawY−12,EngineY+3 | nativerPitchACK+6°/Gain−0,5 |

Jede dieser8Emissionsintervalle umfasst exakt einen echten passenden XTEST-
WireRequest auf derselben eigenen Controllerverbindung. Kein zusätzlicher
Controller-XTEST-Request. Beide horizontalen angefragten Actiongains sind−0,25;
Bodygains−0,25000636/−0,24999746, Rückkehrfehler0,000106812°. Das ist ein
begrenzter Befund dieses Laufs, keine Widerlegung früherer horizontaler FAILs.

Pitch: Der letzte echte native Zustand vor Y+12 hatte empfangenen/lokalen und
Viewpointpitch0°. Der ACK-Endpunkt zeigt server-/clientseitig−3°. Vor Y−12 lagen
diese Werte bei−3°, nachher und am ACK-Endpunkt bei+3°: tatsächlicher Zuwachs+6°.
Die an beiden nativen Endpunkten separat erfasste Körperplatzierung dreht dabei
den Pitch nicht; hier belegt ist die Original-Viewpointrotation. Die gültigen
ACK-Endpunkte wurden nach der vorhandenen Stabilitätshaltezeit akzeptiert. Die
anschließende unveränderte0,05-Gainvergleichsgrenze scheitert an0,25Differenz;
Rückkehr-/Aim-/Firepfad wird danach nicht erreicht.

JS zeigt bei257/259 im Abstand47ms zweimal GetCursorPos(400,301) bei Center
(400,313), jeweils nachfolgend SetCursorPos(400,313) mit erfolgreichem Return.
EngineY ist jeweils+3. Alle übrigen EngineYreads sind0 bis auf ID223mit−3.
Dies lokalisiert den zusätzlichen vertikalen Verbrauch spätestens am Original-
GetInput-Ausgang. Direkter JS-`raw_action_pitch`/Pitch-Composewert fehlt im
vorhandenen Trace; er wird nicht aus Yawfeldern erfunden. Die tatsächliche native
Pitchantwort passt zu den zwei+3-Eingangswerten, doch eine direkte per-Aufruf-
Pitch-Composebindung ist damit nicht gemessen.

## Exakte Wirefolge beim negativen Pitch und ihre Grenze

Die Query-/Warp-Verbindung ist in beiden tatsächlichen Snapshots an dieselbe
eigene Original-PID/Startgeneration und denselben PIDnamespace gebunden; keine
Lifecyclegrenze dieser Base im vollständigen RECORDstream. Dies benennt die
Verbindung, nicht automatisch den konkreten aufrufenden Thread oder JS-Record.

| Callback | Tatsächlicher Wirevorgang | Eigene Verbindungssequenz | Ergebnis |
| --- | --- | --- | --- |
| 286 | Controller XTEST Y−12 | 108 | genau ein Request |
| 287/288 | Device/DeliveredMotion | 0/283 | Root(400,301) |
| 289/290 | Original QueryPointerrequest/-reply | 390 | sameScreen,Root und Window(400,301) |
| 291 | Original WarpPointerrequest | 392 | Root→Root,Ziel(400,313) |
| 292/293 | Device/DeliveredMotion | 0/392 | Root(400,313) |
| 294/295 | Original Queryrequest/-reply | 395 | Root und Window(400,313) |
| 296/297 | Original Queryrequest/-reply | 396 | Root und Window(400,313) |
| 302/303 | Original Queryrequest/-reply | 397 | Root und Window(400,313) |
| 304/305 | Original Queryrequest/-reply | 398 | Root und Window(400,313) |
| 306/307 | Original Queryrequest/-reply | 399 | Root und Window(400,313) |
| 308/309 | Original Queryrequest/-reply | 400 | Root und Window(400,313) |

Query390→Warp392 liegen innerhalb derselben Xserveruhr50ms auseinander. Es gibt
hier genau einen Queryreply mit301und einen tatsächlichen Warp zum Center;
danach ausschließlich sechs Centerreplies. WarpPointer hat keinen eigenen
Protokollreply. Device-/DeliveredMotion und spätere Queryreplies belegen hier
die tatsächliche Centerposition; ein USER32Return allein wäre schwächer.

**Keine erzwungene Zuordnung des Wirewarps zwischen JS257 und259:** Der JS-Trace
trägt keine Xclient-Requestsequence und beide Reads befinden sich im selben
späteren Hostdrain-Batch. Xserverzeit, JS-Date.now, Gameclock und die Host-/Recorder-
Receiptzeiten sind keine austauschbare Ausführungsuhr. Weder der erste noch der
zweite SetCursorPos-Return ist damit direkt an Warp392 gebunden.

Die Nullhypothese eines tatsächlich beobachteten alten Xserverreply **nach** dem
realen Warp wird von diesen Rawdaten nicht gestützt: die vollständigen späteren
Replies sind Center. Ein alter Wine-Cursorcache, eine verzögerte/zusammengefasste
Recenteranfrage oder ein anderer Übergang zwischen USER32 und X11 bleibt ohne
genaue Aufruf-/Requestbindung offen. Auch eine Aufnahme vor dem Wirewarp kann
nicht durch bequemes Uhrmatching ausgeschlossen werden. Keine Ursachenbehauptung,
Fixempfehlung oder Toleranzlockerung aus bloßer zeitlicher Nähe.

## Abschlussgrenze

Collector278Records/0Faults/0Drops, passiverRecorder310/310freed/0Drops,
Originalbyteprüfung/Unload/Detach und normale eigene Prozessschlüsse sind in der
geschlossenen Evidenz erhalten. Root meldete unabhängig664Dateien+9Absenzen+
3ClosedlogsRestorePASS; dieser Reader wiederholt keine Live-/Restoreoperation.
Kein Schuss, kein Schaden-/Respawnschutzbeleg, kein `input_once` und kein A1-PASS.
