# A1: vorbereitete XTest-Verbindung, Gain-FAIL weiterhin belegt

Geschlossenes Fenster`a1-xtest-preparation-20261114-222350`:
**FAIL unverändert**, ausschließlich Archiv-/Quellenanalyse ab`d8fbd270`.
Kein Fix, Testlauf, Build, Input, Hook oder neuer Runtimeversuch. Root hat
normalen Dreierclose, Originalbytes/Recorder-/Workerende und664Dateien+
8Abwesenheiten+3geschlossene Logs separat geprüft. Dieser Autor beansprucht
keine Wiederholung dieser unabhängigen Restoreprüfung.

## Was die Metadatenvorbereitung tatsächlich erreicht hat

Prearm-Receipt: XTestQueryExtension auf bestehender Transportverbindung,
Return1/Version2.2 und erfolgreicher XSync vor Recorderarm. Alle vier späteren
echten Aufrufe haben Return1 und exakt einen Sequenzplatz. Der alte
`b-a>4`-Fehler tritt in diesem Fenster nicht mehr auf. Dies ist ein begrenzter
Erfolgsbeleg für die Vorbereitung, keine A1-/Gain-/InputOnce-Abnahme.

| Tatsächlicher Aufruf | Counter vor→nach | Parentmonotonic Start→Ende | RECORD-Serial |
|---|---|---|---:|
|RelativeMotion +12/0|32→33|1321459.729568741→1321459.729596973|40|
|Forward-Key25 down|46→47|1321460.631508762→1321460.631532257|78|
|Forward-Key25 up|50→51|1321460.781023339→1321460.781047485|85|
|RelativeMotion −12/0|64→65|1321461.815391308→1321461.815414523|130|

Alle drei vorhandenen Controllerphasen sind PASS/released, mit je einer
Held-Beobachtung: rechts131.603ms, forward165.562ms, links149.011ms von
Input bis Release, unter dem unveränderten350ms-Limit. Vier Attemptrows sind
ACCEPTED; gültige Liste und tatsächliche Wireaufrufe stimmen überein.
Keine weitere Controller-Mausanfrage ist im gedeckten Trace vorhanden.

## Vollständige Original-Input-/Actionbindung

13Journalhüllen enthalten162Payloadrecords:81GetInput und81Action, Sequenzen
1..162 ohne Lücke, genau ein beobachteter Timerthread, je eine Action mit
passender input_id. Abschluss81Paare,0Faults/Drop/InFlight/Gamewrites.
78Inputs haben Cursor400/313 und Engine-X/Y0. Nur diese drei sind nicht null:

| Input→Action | JS-Entryms | CursorX/Zentrum | raw_dx→EngineX | Rawyaw vor Compose | Akkumulator danach |
|---|---:|---|---|---:|---|
|55→56|1794695061738|412/400|+12→+3|−3°|0→−3°|
|57→58|1794695061787|412/400|+12→+3|−3°|−3→−6°|
|139→140|1794695063839|388/400|−12→−3|+3°|−6→−3°|

Alle drei GetCursorPos-Aufrufe melden Erfolg, ebenso die jeweils anschließend
beobachteten SetCursorPos-Aufrufe auf400/313. Die beiden rechten Inputentries
liegen innerhalb derselben JS-Uhr49ms auseinander. Der erste Recenterreturn
steht bei1794695061739, der zweite Cursorread bei1794695061788. Das belegt die
wiederholte Win32-Cursorlesung, keine eindeutige Zuordnung zu einem X-Warp.

Der passive Midpoint liest Rawyaw vor `ctl_ComposeActionPacket`; der jeweilige
Actionreturn liest danach die tatsächliche lokale Akkumulation. Alle81Paare
erfüllen `Rawyaw = -EngineX` und die gemessene Akkumulatordifferenz entspricht
genau Rawyaw. Es ist daher erneut keine einzelne Umrechnung mit Gain−0.5:
zweimal+12Rawinput erzeugt zweimal−3°. Links erzeugt einmal−12 genau+3°.
Die empirischen Einzelread-Verhältnisse sind jeweils−0.25. Die bestehende
Abnahme verwendet die angefragten12Pixel pro Impuls; deren Denominator wird
hier ausdrücklich nicht geändert, um die Verdopplung zu verbergen.

81Profilreads zeigen acceleration0, sensitivity0.25, prescan0, precision0,
filter0. Die vorhandene effektive Controlsprobe belegt Profil0, relative1,
invert0 und global/per-axis/effective smoothing0; sie sind zwei gleiche
Speicherlesungen, keine atomare Gesamtaufnahme. Ein Profil-/Smoothingwechsel
ist nicht belegt. Das akkumulierte Feld `absolute` ist kein Nachweis eines
absoluten Eingabemodus.

## ACK, Body und konkrete Ablehnungsstelle

Rechts bestätigen drei frische Speicherpaare bei Serverticks11.6500263,
11.7000265 und11.8000269 kumulativ−6°; Originalclient ebenso−6°.
Bestätigter relativer Delta−6°/angefragte12 ergibt Gain−0.5.
Nach dem regulären Forward/Settle beträgt der Body bei Tick12.8000307
−141.00009155273438° statt vorher−135.0000457763672°:
Delta−6.0000457763671875°, roher Bodygain−0.5000038146972656.

Links bestätigen die drei Paare bei13.8000345/13.8500347/13.9000349 den
kumulativen Übergang−6→−3°, also Delta+3°/(−12)=−0.25.
Die unveränderte Gain-Differenzgrenze0.05 scheitert korrekt an0.25
(`rotation_diagnostics.py:213–215`). Vor dem zweiten Forward/Body-Settle
endet der Ablauf: ein zweiter Bodyendpunkt fehlt und wird nicht ergänzt.
Alle29archivierten physischen Paare bleiben je Prozess in derselben geprüften
Entity/World/Life/Prozessstart-Zuordnung, Originalspawnclock0.25. Die Verdopplung
besteht bereits vor ACK in echten Input-/Compose-/Actionrecords; ein bloßer
Snapshot-Assoziationsfehler erklärt die konsistenten Belege nicht.

## RECORD: gedeckter Coreausschnitt und offene Verbindungszuordnung

152Records/43816Bytes, Startserial1 und Endserial152;152Callbacks/freed152,
keine malformed/drop, normaler Recorderexit0. Unveränderter Coreparser wurde
auf sämtlichen Wirebytes erneut ausgeführt: alle abgeleiteten Felder exakt,
keine offenen Queryantworten. Der unveränderte A1-Auditor reproduziert die
archivierte partielle Auswertung vollständig, einschließlich vier Emissionen
und drei Phasen. Dies ist ein Archivreplay, keine neue native Abnahme.

| Quellenalias | Belegte Records | Grenze |
|---|---|---|
|C: Controllertransport|2RelativeMotion,2Key-FakeInput,3Querypaare|über tatsächlichen Ressourcenlookup und Emissionsintervalle gebunden|
|W: Originalfenster-Resourceowner|2DeliveredMotion,0Queries,0Warps|Fenster-/Ressourcenbindung, keine Gleichsetzung aller Verbindungen eines Prozesses|
|U: weitere X-Verbindung|65Querypaare,2Warps,2DeliveredMotion|kein belegter Ressourcen-/Socket-/PIDlookup für diese Verbindung|
|Device/Control|4DeviceMotion, Start, End|originating_client bleibt None|

130unattributed Queryrecords sind65Paare von U; davon64Antworten400/313,
eine412/313. Die drei Controllerantworten sind400/313. Kein Queryantwortbeleg
für388 ist vorhanden; der linke Gerätemove388 ist dennoch direkt beobachtet.

Ausgewählte RECORD-Folge, **ausschließlich X-Serverzeit in Millisekunden**:

| Serial | X-Serverms | Tatsächlich beobachtet |
|---:|---:|---|
|40–42|1321459728|C-FakeInput+12, Device412/313, Delivered412/313 an W|
|43–44|1321459743|U-Query mit tatsächlicher Antwort412/313|
|45–47|1321459793|U-Warp auf400/313, danach Device400/313 und Delivered an U|
|78|1321460630|C-KeyPress25|
|85|1321460780|C-KeyRelease25|
|130–132|1321461814|C-FakeInput−12, Device388/313, Delivered388/313 an W|
|133–135|1321461847|U-Warp auf400/313, danach Device400/313 und Delivered an U|

Damit enthält der gedeckte Corestream genau einen positiven und einen negativen
Controller-Move sowie die zwei Zentrierbewegungen. Keinen zweiten Device412-
Record als Erklärung der doppelten Original-Lesung. Der erste Warp folgt hier
65Serverms nach dem rechten FakeInput, der zweite33Serverms nach dem linken.
Dies sind Differenzen innerhalb derselben X-Serveruhr, keine Frida-/Gamezeit.

**Beide Warps bleiben prozessseitig UNKNOWN.** U ist weder C noch W. Mehrere
X-Verbindungen desselben Wineprozesses sind möglich; verschiedene Clientbases
beweisen weder denselben noch einen fremden Prozess. Ziel Rootfenster/400/313,
nahe Zeiten und ähnliche Cursorfolgen ersetzen keinen Ressourcen-/PIDbeleg.
Keiner der drei erfolgreichen Original-SetCursorPos-Aufrufe wird daher einem
bestimmten der nur zwei Wirewarps zugeordnet. Der Request allein ist kein
Positionsbeweis; die nachfolgenden tatsächlichen Devicepositionen sind separat.

Der immutable Coreparser klassifiziert die beiden36Byte-XTEST-Requests mit
Eventtyp2/3 als `unsupported`, weil er nur relative Maus-FakeInputs typisiert.
Sein Nativezähler bleibt **unknown2**. Der A1-Adapter erkennt zusätzlich aus
Header/Major132/minor2/Typ2oder3/Keycode25/device0 die beiden normalen gebundenen
Forward-Keyrequests. Das ergibt **adapter_typed_noncursor_xtest2**, aber
**method_decoder_unsupported2**, nicht Coreunknown0. Die Keyrequest-Paddingbytes
werden nicht als weitere Mausbewegung interpretiert. `unparsed_selected_records0`
gilt nur für diesen ausgewählten Corefilter, nicht für XI2, Win32-Queues oder
einen vollständig erklärten Cursorcache.

## Uhren und weiterhin fehlende kausale Grenze

Parentemissionen und Phasen verwenden Parentmonotonic; die Recorderdatei nennt
zusätzlich ihre eigene Callbackreceipt-Monotonic. Diese Receipt ist eine spätere
Beobachtung, keine exakte Serverausführungszeit. Originalrecords verwenden
Frida-Date.now-Epochms; Hostdrains halten nur Batch-Reihenfolge/-Empfangsgrenzen.
Server-/Clientgameticks stammen aus jeweils eigenen nativen Speicherproben.
Keine dieser Uhren wird hier stillschweigend gleichgesetzt oder interpoliert.

Die neuen Belege begrenzen das Problem auf einmal beobachtete gedeckte Core-
Bewegung412 gegenüber zweimal tatsächlichem GetCursorPos412 und nachfolgender
Rawaction. Sie beweisen weder einen vollständigen XI2-Verlauf noch eine genaue
Original-Recenter→Wire-Zuordnung oder einen konkreten Wine-/Cache-/Fridafehler.
Ein dauerhafter Recentererfolg folgt nicht allein aus SetCursorPos-Return1.
Die Abnahme bleibt wegen tatsächlich ungleicher angefragter Inputwirkung rot.
Kein neuer Fix oder Nativeplan wird aus diesem Audit implementiert.

## Reproduzierbare Pins und private vollständige Quittung

| Archiv/Quelle | SHA256 |
|---|---|
|result.json|`957d68ce2f306d89dc0839ffd1abcd7d613c92b16aed64f459f91fb4ea72a446`|
|original-input-trace.jsonl|`5f3c0ae29de7ed841a72585d33c185ceb719e5424282f0cde6e415ace0e83541`|
|rotation-pairs.jsonl|`a97c0051834ac6158d46d7778a785deb7e2f1d1b704aaad8bb93b76512ac00ad`|
|record-raw.jsonl|`2507870424b2410e7f751d9a1f46e41dbfa4ffa42a8b94fc293db017160ce2ef`|
|controller-emissions.json|`62a7e974dcadd6a748a834df6a032c285e55339a247e2259c9c8f5f4b7c29be6`|
|Rootmanifest|`71b9c896e068e473d0fd8317871b0fa3ccc5f4a43828c87e8b1b09619c60170a`|
|Controller/archivierte Quelle|`4f5e1fa7a61d81dc02c0f5e6c1cc64c5744ae82c1be6943b3dcb61f01e809528`|
|rotation_diagnostics.py|`35dc92dd7a6f5d7fc1b468698a0d41e12cdc7ceb1033668f1dc0bb810510fad2`|
|Original-JS|`11c264e1e879bc8c186f9af1817a469d7c2eac22245fe03def54502480104a9c`|
|Originalguards|`3d2b237a787869fee27b02ac22a84f5bdf4e3528e8e2fee2981f05d3e8d7e9d1`|
|Coreparser|`ca4de66b67603924d00fb0acb4cf381f46877a76fc4e798784309649c52b27cf`|
|A1-Passivauditor|`21ebccbe5425b43108d79036b5179c071b6a3f8be3b6a549fef65c5985ad57c0`|

Archivierte Controller-/RD-/CP-/Manifestdateien bytegleich zum tatsächlichen
Rootfreeze. Quellenstellen: JS181–227 Cursor/Recenter,238–275 Action/Compose;
Core81–85 Keyunsupported; Passivauditor11–13 zusätzliche Keytypisierung.

Vollständige private0600Quittung mit allen152Rawrecords,81Input/Action-Paaren,
29physischen Paaren,17ACK-/Bodybeobachtungen, allen vier Calls/Attempts und
allen drei Phasen:
`/srv/tse-cecil-rollout-evidence-20261114/a1-xtest-preparation-closed-diagnosis-final.json`,
SHA`f23372ba5cbbffe52ed0229817512828fdfa5cf9edd65a310b4bc931b387b646`.
Der private Reproducer
`a1-xtest-preparation-closed-audit-private.py` im selben Verzeichnis hat SHA
`6eb98a31d1d5572a8cc9b92750d3dd8c2ec073bf5c9a6da97bae10299515e42d`.
Er führt nur Archiv-/Quellenchecks und pure Parser aus, keine Runtimefunktionen.
Ein anfänglicher Analysepfadfehler für eine nicht dort liegende Bindingsdatei
erzeugte keine Quittung; der finale Reproducer verwendet ausschließlich die
tatsächlich vorhandenen obigen Quellen. Keine Retaildateien/Spieleridentitäten
oder privaten Rohdaten werden mit diesem bereinigten Bericht veröffentlicht.
