# A1: tatsächlicher Input und Host-Zeitüberschreitung

Status: **FAIL unverändert; reine Diagnose und prospektiver Designvorschlag**.
Keine Runtime, kein Build, kein Hook-/Input-/ACK-/Grenzwertwechsel und kein Retry
wurden durch diesen Bericht ausgeführt. Arbeitsbasis: `cb35182d80b371a48859b01f3dbd9e4d6ab5f884`.

## Belegbindung

Privates abgeschlossenes Fenster:
`/srv/tse-milestone-a-evidence-20261111/a1-exact-coverage-20261114-141819`.

| Datei | SHA256 |
|---|---|
| result.json | `f66266f97f9eadf008f42aa557e1a3aa2c25778d7c6ed9a04efbb76a0392bf74` |
| original-input-trace.jsonl | `14723bb913ef940d785a9479de98ea1a60ab683c89332ce87328ca217ea107b4` |
| rotation-read-attempts.jsonl | `ee50478497cd17c5a9b77ebc8a3cd3019241220b8327dea244fa19341bbd0d5f` |
| rotation-pairs.jsonl | `76dd26e20845ca08bbf6f3268bbe5a350c1f9a5428c89f51decaab00b7e864c2` |
| queries.jsonl | `a22165ddd1696622053c0cd7e053faa089b1ec77d9d3ac69defe92f018e47b99` |
| controller-source.py | `8db8f4212e3ed191fd5cbfa30cd1a333570436d8753976333001f88edc08f26e` |

Die Quellen wurden in der eingefrorenen Kopie
`/srv/tse-a1-exact-coverage-root-frozen-20261114` gelesen.
Die wiederhergestellten Dateien/Metadaten, drei normal geschlossenen Rollen,
Originalbytes, Unload/Detach und beendeten Worker hat Root separat geprüft;
dieser Bericht beansprucht dafür keine eigene vollständige Restoreprüfung.

## Tatsächliche Eingaben und native Verarbeitung

Alle drei XTest-Anfragen sind mit `request_confirmed=true` archiviert.

| Anfrage | Input bis vollständige Freigabe | Ergebnis des action_step |
|---|---:|---|
| look_right, +12 Pixel | 135,253074 ms | PASS |
| forward, 100 ms angefordert | 161,843464 ms | PASS |
| look_left, −12 Pixel | 352,432804 ms | FAIL |

Das Journal enthält 13 Hüllen, darin **138 tatsächliche Payloadrecords**:
69 GetInput- und 69 passend verknüpfte Actionrecords, fortlaufende Sequenzen
1–138, keine Faults oder verworfenen Records. Zwei GetInput-Records haben einen
von null verschiedenen horizontalen Cursorwert. Die Summe der beiden raw_dx
ist null. Die Hüllenzahl ist keine Zahl nativer Aufrufe.

Der erste Mausimpuls erscheint als Input 37 mit raw_dx=+12 und engine_x=+3;
Action 38 referenziert Input 37 und hat raw_action_yaw=−3. Der vorhandene
Kalibrierablauf erkannte den echten ACK von −3 Grad und Gain −0,25 Grad/Pixel.
Nach dem vorgesehenen Forward-/Settle-Schritt änderte sich der gemessene
Bodywinkel um −3,0000762939453125 Grad.

Auch der dritte Impuls wurde tatsächlich verarbeitet: Input 123 hat
raw_dx=−12 und engine_x=−3; Action 124 referenziert Input 123 und hat
raw_action_yaw=+3, wodurch die kumulative Actionrotation auf null zurückkehrt.
Die späteren Original-Paarreads zeigen die passende Änderung der server- und
clientseitigen Actionfelder im selben Leben. Wegen der vorherigen Exception
erreichte der Ablauf für diese Richtung jedoch keinen abgeschlossenen
ACK-Hold-/Gain-/Bodyreturn-Nachweis. Dafür wird kein PASS abgeleitet.
Integer-Wanduhrwerte des JS und Host-Monotonzeiten erlauben keine zusätzliche
submillisekundengenaue Kausalzuordnung; die Records sind über IDs und Werte gebunden.

## Konkreter Fehlerpfad

`run_dual.py:81–89` prüft das geplante Ende erst nach `observe()`.
Die unveränderte harte Grenze ist Anfragedauer + 250 ms, hier 350 ms.

| Ereignis des dritten Inputs | Monotonzeit | Nach tatsächlichem XTest-Start |
|---|---:|---:|
| XTest-Start | 1292330.807703282 | 0 ms |
| erste Held-Beobachtung: Paarread fertig | 1292330.877068950 | 69,365668 ms |
| nächster periodischer Hostblock: interner Zeitstempel | 1292330.952126106 | 144,422824 ms |
| Drain-Request | 1292331.032862955 | 225,159673 ms |
| Drain fertig | 1292331.082270079 | 274,566797 ms |
| Querypfad fertig | 1292331.145241146 | 337,537864 ms |
| letzter Readversuch fertig | 1292331.159688389 | 351,985107 ms |
| finally: Releasebeginn | 1292331.160134653 | 352,431371 ms |
| finally: Release fertig | 1292331.160136086 | 352,432804 ms |

Der nächste `observe()`-Block wurde damit begonnen, obwohl der geplante
100-ms-Zeitraum bereits beendet war. Danach scheiterte zu Recht
`bounded('observation')`; der unveränderte abschließende Check meldete zusätzlich
`input through release host overrun`. Die Vorbereitung vor XTest dauerte
398,729293 ms und gehört nicht zum gemessenen Input-bis-Release-Zeitraum.

Die archivierten Teilintervalle erlauben keine Einzelprozess-CPU-Attribution.
Vom internen Host-Zeitstempel bis zum Drain-Request vergingen 80,736849 ms
für den kombinierten Ressourcen-/Save-/Log-/Identitäts-/Modul-/Display-/Fokuspfad.
Der Drain selbst dauerte 49,407124 ms und lag innerhalb seiner eigenen Frist.
Bis zum Ende des anschließenden Querypfads vergingen weitere 62,971067 ms;
das enthält den geerbten Transport-/Subprozess-/UDP-/Validierungspfad und ist
keine isolierte Netzwerklatenz. Der letzte Readversuch dauerte 14,351579 ms.
Alle neun Frida-IPC-Aufrufe blieben innerhalb ihrer jeweiligen Budgets.
Host-CPU-Maximum 69,976 % unterschreitet 75 %, schließt aber kurzzeitige
Schedulingkosten nicht aus. Es ist kein Frida-Timeout und kein bewiesener
einzelner Verursacher der Gesamtdauer.

## Engster prospektiver Korrekturvertrag

Noch nicht implementiert oder nativ geprüft:

1. Das geplante Ende unmittelbar vor und nach den bestehenden strikten
   Held-Guards prüfen. Bei Fälligkeit keinen weiteren teuren Observer zulassen,
   sondern den vorhandenen Capture-/`before_release`-Pfad und danach
   `finally`/Release erreichen. Identitäts-/Fokus-/Clockprüfungen dürfen dadurch
   nicht abgeschwächt werden; die konkrete Reihenfolge muss im Root-Plan feststehen.
2. Harte 350-ms-Grenze, Clockmonotonie, Capturefehler, Releasefehler und
   Sticky-FAIL bleiben unverändert. Ein noch rechtzeitig gestarteter Observer,
   der die harte Grenze überschreitet, bleibt FAIL. Das gilt ebenso für zu
   langsame Guards oder Captureoperationen.
3. Keine erfundene Held-Beobachtung: null tatsächlich ausgeführte Beobachtungen
   müssen explizit erkennbar bleiben. Eine bestätigte Emission allein ist kein
   ACK-, Body-, Gain- oder A1-Nachweis.
4. Der existierende erfolgreiche `CP.act`-Pfad ruft nach Release bereits
   `observe(stage+'-after-input')` auf. Ein noch fälliger Host-/Log-/Guard-/Drain-/
   Queryzyklus kann dort unter unveränderter Periodik stattfinden. Keine
   zusätzlichen Reads, keine veränderten Samplingfristen und keine neuen Inputs.
   Anschließende echte native ACK-/Body-/Gain-Belege bleiben erforderlich.

Vor Umsetzung sind fokussierte RED/GREEN-Fälle nötig: bereits vor Guards
fälliges Ende; Guards überschreiten 100 ms, aber nicht 350 ms; Guards über
350 ms; rechtzeitig begonnener langsamer Observer über 350 ms; langsames oder
fehlschlagendes Capture; rückwärtslaufende Uhr; Releasefehler; garantiertes
Release bei jedem Fehler; ehrlicher Fall ohne Held-Beobachtung sowie der
unveränderte nachfolgende periodische und native ACK-Ablauf.

Der historische Lauf bleibt FAIL. Dieser Befund beweist keine vollständige
Kalibrierung, Schadensfreigabe, A1-Abnahme oder allgemeine Runtimequalifikation.
