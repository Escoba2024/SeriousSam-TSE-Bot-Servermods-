# A1: doppelt beobachteter Rechtsversatz erklärt die ungleichen Gains

**FAIL unverändert; reine Evidenz-/Quellenanalyse.** Basis `6956cfd`.
Keine Codeänderung, kein Generator, Test, Build, Hook, Input oder nativer Lauf.
Privates Fenster:
`/srv/tse-milestone-a-evidence-20261111/a1-release-deadline-20261114-144306`.

| Archiv | SHA256 |
|---|---|
| result.json | `51e8e0e5ed32177606a71e6c1ca17e82812c5ba047581bf81525fef5652cc772` |
| original-input-trace.jsonl | `89004d146871c5ac9e875adbe4ebbc4f8f625181a48a5ac01c14cb1d6c247ec0` |
| rotation-pairs.jsonl | `8b305093d54a77b1aab2cab6809c1f6217e39f25e661a431e2088146d759f559` |
| rotation-read-attempts.jsonl | `d7c5f6388e5aa7bd8e442577004b88fa5e1aed61578fa8083d03ccc0b62ac280` |

Die drei archivierten Controller-/RD-/CP-Quellen stimmen mit dem eingefrorenen
Rootpaket `/srv/tse-a1-release-deadline-root-frozen-20261114` überein.
Den unabhängigen Restore664+8+3 und den vollständigen normalen Cleanup hat
Root separat geprüft; dieser Bericht beansprucht keine eigene Wiederholung.

## Tatsächliche Anfragen und Originalverarbeitung

Alle drei Anfragen haben erfolgreiche Emissions-/Releasequittungen, je eine
tatsächlich begonnene Held-Beobachtung und keine Timingfehler:

| Anfrage | XTest-Start, monotonic | Input bis Release |
|---|---:|---:|
| look_right +12 px | 1293814.019944395 | 137,449451 ms |
| forward | 1293814.862353134 | 159,541141 ms |
| look_left −12 px | 1293816.028402944 | 144,256554 ms |

Das Journal enthält 12 Hüllen und **140 echte Payloadrecords:70 GetInput und
70 Action**, Sequenzen1–140 ohne Lücke, genau einen Timerthread und eine
Action je Input. Abschluss:70 vollständige Paare,0Faults,0Drops. 67 Inputs
lesen Cursorzentrum400/313 und Engine-X/Y0. Die übrigen drei sind:

| Originalinput | Cursor/Zentrum X | raw_dx | Engine-X | Action | raw_action_yaw | lokaler Akkumulator |
|---|---:|---:|---:|---|---:|---|
| 37 | 412/400 | +12 | +3 | 38, input_id37 | −3° | 0→−3° |
| 39,50 ms später | 412/400 | +12 | +3 | 40, input_id39 | −3° | −3→−6° |
| 119 | 388/400 | −12 | −3 | 120, input_id119 | +3° | −6→−3° |

Input37 und39 protokollieren beide getrennte erfolgreiche GetCursorPos-
Rückgaben sowie SetCursorPos auf400/313 mit Erfolg. Vorher Input35 und
nachher Input41 lesen wieder400/313 und0. Das sind frische eigene Records:
der JS-Code erzeugt pro GetInput einen neuen Record, weist doppelte Cursor-
oder Recenter-Sites desselben Records zurück und bindet dessen Action über
input_id. Zwei unveränderte +12-Cursorwerte verursachen damit tatsächlich
zwei einzelne −3-Grad-Actions; keine einzelne Engineumrechnung mit Gain−0,5.

Der Harness protokolliert je Richtung genau eine bestätigte Motion-Anfrage.
Der gepinnte `X11Transport.look` enthält genau einen Aufruf der vorbereiteten
XTest-C-Funktion, danach XSync, ohne Wiederholung. Diese Belege zählen keine
serverseitigen X11-/Wine-Geräte- oder Motionevents.

## ACK und physische Gegenprüfung

Die RD-Grenze schlägt korrekt an:

- Rechts: frische Vorprobe mit Action0 und Body−135,0000457763672°;
  danach drei ACK-Proben mit kumulativ−6°, schließlich bestätigter ACK−6°
  bei Server-/Clienttick11,2000246. Nach dem bestehenden Forward und
  Settle beträgt der Body−141,00009155273438°, also Delta−6,0000457763671875°.
  Tatsächlicher Action-Gain−6/12=−0,5; roher Body-Gain−0,5000038146972656.
- Links: frische Vorprobe mit kumulativ−6°; danach drei ACK-Proben mit
  kumulativ−3° und relativer Änderung+3°, bestätigt bei Tick13,3000326.
  Tatsächlicher Action-Gain+3/(−12)=−0,25. Die bestehende Differenzgrenze0,05
  scheitert an0,25. Der zweite Forward-/Settle-/Bodyreturn-Schritt wurde
  folgerichtig nicht mehr ausgeführt. Ein fertiger zweiter Body-Gain fehlt.

Alle ausgewählten Paare bleiben in derselben geprüften Entity/Life/World-
Zuordnung je Prozess, Spawnclock0,25. Die einseitige Verdopplung besteht
bereits in den Original-Input-/Actionrecords und wird anschließend durch
ACK und den ersten Bodydelta bestätigt. Ein reiner Snapshot-
Assoziationsfehler erklärt diese übereinstimmenden Belege nicht.

## Eingegrenzte Ursache und fehlender Beleg

Alle70 Inputrecords zeigen unverändert acceleration0, sensitivity0,25,
prescan0, precision0 und filter0. Die ausgeführten Lifetimeguards verlangen
zusätzlich Profil0, relative1, invert0 und per-axis/global smoothing0.
Die vorhandene passive Controlsprobe stimmt damit überein. Ein Wechsel des
Original-Accelerations-/Absolut-/Smoothingprofils ist nicht belegt. Das
protokollierte Axisfeld `absolute` ist ein akkumuliertes Lesefeld und kein
Nachweis eines absoluten Eingabemodus; der relative-Modusguard bleibt1.

Der konkrete Fehler liegt spätestens beim **erneuten Cursorversatz+12 im
zweiten GetInput nach bereits erfolgreich gemeldetem Recenter**. Woher er
kommt, bleibt UNKNOWN. Die Archive enthalten keine X11-Motion-/Geräte-
Eventfolge und keine unabhängige X-Serverposition unmittelbar nach dem
Original-SetCursorPos. Dessen erfolgreicher Rückgabewert beweist keine
dauerhafte Rückstellung bis zum nächsten GetCursorPos. Wiederholte/verspätete
Events, Cursorcache-/Recenterverarbeitung oder ein weiterer Beweger lassen
sich damit nicht gegeneinander entscheiden. Keine davon wird als Ursache
behauptet; insbesondere kein bewiesener Frida- oder Winefehler.

Die Releasekorrektur hat in diesem Fenster alle drei Eingaben unter dem
unveränderten harten Limit beendet. Sie hat die Gain-Abnahme nicht bestanden.
Der nächste Rootplan müsste die fehlende Ereignis-/Cursorgrenze gezielt
beobachten und OwnProcess/OwnDisplay, bounded Queue/TTL, uninstrumentierte
Kontrolle, Originalbytes und normalen Cleanup erhalten. Hier werden weder
neue Hooks noch Profiländerungen oder Wiederholungen implementiert.

Kein Fire, Schaden, Respawnschutz-, A1- oder Flottenabschluss wird abgeleitet.
