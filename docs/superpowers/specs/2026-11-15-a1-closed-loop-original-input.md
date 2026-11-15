# A1: getrennte Original-Mauseingabe mit gemessener Rückkopplung

Status: **statisch entscheidbar, nicht implementiert und nicht nativ geprüft**.
Claim: ausschließlich diese neue Spezifikation. Bestehende Helfer, eingefrorene
Pakete, Originaldateien, Runtime und frühere FAILs bleiben unverändert.

## Entscheidung und genauer Nutzen

Ein separater normaler Feedbackpfad ist grundsätzlich mit dem First-State-Vertrag
vereinbar. Dieser fordert tatsächliche normale Eingabe/Serveraktion und eine
kausale Original-Fire-/Bullet-/Damagekette; er schreibt keine symmetrische oder
zeitlich konstante Pixel-Gainfunktion vor. Die fehlenden autoritativen
Lebens-/Zustandsordinale und Bullet-/Inflictorbindungen bleiben eigenständige
Blockaden der First-State-Schadensabnahme. Stillstand, Bodenkontakt und Colt sind
nur Bedingungen der vorhandenen Vorbereitungsfixture, keine neuen allgemeinen
Respawn-Gültigkeitsbedingungen.

Empfohlen wird zunächst **genau ein Pitch-Rückkehrfall ohne Schuss**. Er klärt,
ob normale 1-Pixel-Korrekturen anhand tatsächlich verbundener Original-/Server-
Endpunkte die bestehende Rückkehrgrenze von 0,75° erreichen können, obwohl kein
konstanter Gain vorausgesetzt wird. Das ist weder allgemeine Zielerfassung noch
ein Ersatz für `CP.decision`, Kollisionsnachweis oder A1-Freigabe.

Ein direkter vollständiger Aim-Ersatz ist jetzt nicht ausreichend spezifiziert:
`CP.decision` dividiert den geometrischen Fehler durch kalibrierte Gains und
entscheidet über gerundete Pixel, wann kein weiterer Aim-Input erforderlich ist.
Ohne verlässliches Gainmodell darf dieses quantisierte Erfolgsprädikat nicht
einfach weiterbenutzt werden. Eine neue beliebige Winkeltoleranz oder angenommene
Player-Hitbox wäre ebenfalls kein zulässiger Ersatz. Dagegen benötigt die
bestehende 0,75°-Rückkehrdiagnose weder ein solches Aim-Prädikat noch einen Schuss.

## Vorhandene Mechanik und Abgrenzung

Die normalen Eingaben und beobachteten Endpunkte sind vorhanden:

- `x11_endpoint.py:63`: normale begrenzte relative XTest-Motion auf dem eigenen
  PID-/Display-/Fensterpfad; kein Originalgetter und kein Speicherwrite.
- `run_dual.py:36`: tatsächlicher Request, unveränderte 0,1-s-Aktionshülle,
  Deadlineprüfungen und abschließende Release-/Neutralitätsbehandlung.
- `run_dual.py:456`: frisches natives Original-/Serverpaar, höchstens acht echte
  Leseversuche innerhalb 0,2 s; fehlgeschlagene Konsistenzreads bleiben erhalten.
- `CP.observe/act/settled/acknowledge` ab Zeilen 188/277/319/334: Prozess-/Welt-/
  Entity-/Life-/Waffen-/Animatorbindung, frische Before-Press-Frames, tatsächliche
  drei Input-Level und ursprüngliche Viewpoint-Geometrie.
- `CP.acknowledge(..., gain=None)` prüft bereits die einzelne tatsächliche
  Antwort ohne Vorhersagegleichheit mit einem kalibrierten Gain. Die
  Gegenrichtungs-Gainprüfung ist ein separater Orchestrierungsschritt, nicht
  eine Voraussetzung dieses einzelnen ACK-Prädikats.

Der aktuelle Keyboardcontroller selbst ist wegen seiner festen sechs Aktionen
und `KeyboardTransport.look` kein ausführbarer Mousecontroller. Eine spätere
eigene **deaktivierte** Ableitung muss ausdrücklich normale `X11Transport`-/
`Endpoint`-Instanzen verwenden. Keine globale Monkeypatch-Umschaltung, kein
Aufruf des bestehenden Keyboardprogramms mit heimlich anderen Controls.

Unverändert wiederzuverwenden sind die geprüften Observe-/Before-Press-/ACK-
Prüfungen und `action_step`, die normalen Starts/Closes, Modul- und Namespacepins,
FileTransaction und Restorehülle. Die neue Orchestrierung wird separat benannt;
`CP.run_preparation`, seine Gainprüfungen und historischen Status bleiben gleich.
Vier qualifizierte Coredateien bleiben bytegleich; Frida, RECORD und XRes werden
für diesen Fall nicht armiert. Die neue Eingabescope erlaubt ausschließlich
`vanilla/look_vertical/0.1 s`: zuerst +12, danach nur ±1, keine anderen Controls.

## Einziger vorgeschlagener Prüffall

1. Dieselbe private Red-Station-Fixture mit genau zwei eigenen Originalspielern
   und unveränderten Retailkomponenten herstellen; Rolle `botA` ist hier die
   vorhandene Original-Zielrolle, kein KI-Bot. Frische Query-/Slot-/Prozess-/
   Modul-/Namespace-/World-/Life-Bindung wie im eingefrorenen Controller.
   Vorhandenen externen Ein-Bot-Preflight weder ersetzen noch umgehen.
2. Nur die vorhandene MIP-/NoSmooth-Intervention innerhalb der versiegelten
   Transaktion verwenden. **Keine** J/L/I/K-Keyboardprofiländerung. Auf derselben
   vorhandenen Transportverbindung XTestQueryExtension/XSync vor Journalbeginn
   wie geprüft; keine Motion zum Warmup. Öffentliche XNextRequest-Pointer-/
   unsigned-long-ABI wie beim bisherigen Pfad explizit deklarieren.
3. Ein frisches stationäres `CP.live_ready`-Paar gemäß bestehendem Settling
   erfassen. `target_pitch` ist ausschließlich der tatsächliche anfängliche
   Viewpoint-Pitch beider Peers, die innerhalb EPS übereinstimmen müssen.
   Ein neuer Zahlenwinkel, Placement- oder Speicherwrite ist ausgeschlossen.
4. Einmal `look_vertical`, `pixels=+12`, `seconds=0.1` ausgeben. Erst tatsächlichen
   Request, unveränderte Aktions-/Neutralitätsquittung und vollständigen nativen
   ACK erhalten; keine Eingabe bei einem unvollständigen vorherigen ACK.
   Liegt der Detour bereits innerhalb 0,75°, endet der Fall als
   `FAIL_FEEDBACK_NOT_EXERCISED`: ohne mindestens einen tatsächlich bestätigten
   1-Pixel-Korrekturrequest ist dieser Methodenbeleg nicht bestanden. Kein
   zusätzlicher oder größerer Detour zur Herstellung eines günstigen Falls.
5. Danach ausschließlich aus dem jüngsten vollständigen ACK/Settling-Endpunkt
   `error = target_pitch - current_pitch` bestimmen. Wenn auf **beiden** Peers
   `abs(error) <= 0.75` gilt, finale frische Stabilität prüfen und beenden.
   Anderenfalls genau einen normalen Pixel ausgeben:
   `pixels=-1` bei positivem Fehler, sonst `pixels=+1`.
6. Auf jeden einzelnen Pixel wieder den tatsächlichen vollständigen ACK abwarten,
   neu messen und erst dann entscheiden. Der absolute Fehler muss gegenüber dem
   direkt zugehörigen Pre-Emission-Endpunkt um mehr als EPS abnehmen. Kein
   Fortschritt, Gegenbewegung oder ein instabiler Peer bedeutet FAIL, keinen
   automatischen Ersatzimpuls oder erneuten Initial-Detour.
7. Nach dem finalen ACK nochmals das vorhandene Settling mit unveränderten
   Fristen ausführen und die 0,75°-Rückkehr auf beiden tatsächlichen Geometrien
   bestätigen. Anschließend bedingungslos stoppen und normal schließen/restore.
   Keine weitere Aim-, Forward-, Waffen-, Fire- oder Respawnaktion anschließen.

Nur Pitch wird verändert. Yaw-Level, Körper-Yaw/-Pitch/-Bank, Positionen,
Augen-/Zielgeometrie und andere Achsen müssen ihre bestehenden unveränderten
Konsistenzprüfungen bestehen. Direkte Pitchdifferenzen und die bereits bestehende
Wrap-Deltarechnung müssen innerhalb EPS übereinstimmen; ein nicht abgedeckter
Pitch-Wrap ist FAIL und wird nicht als Yaw-Normalisierung versteckt.

## Unveränderte Grenzen und Abbruch

| Grenze | Verbindliche Regel |
| --- | --- |
| Eingaben | Höchstens 48 Aktionen insgesamt: ein +12-Detour und danach nur ±1-Pixel-Korrekturen; höchstens 96 Attemptplätze, keine neue Inputart |
| Aktionszeit | Jede Aktion 0,1 s; Input bis einschließlich Release höchstens 0,35 s |
| Einzel-ACK | Strikt vor `request_finished+2 s`, höchstens 42 Polls mit bisherigen 0,05-s-Abständen |
| Antwort | Vorzeichen/Monotonie wie bisher; `-0.5 <= actual_delta/pixels <= -0.02`, `abs(delta)<=abs(pixels)*0.5`; keine gelockerte per-Request-Grenze |
| Konsistenz | EPS=0,001; alle drei Input-Level und physische Original-/Server-Geometrie müssen tatsächlich passen |
| Stabilität | Bestehende mindestens 0,1 native Spielsekunden je Peer; native Uhren nicht mit Hostzeit gleichsetzen |
| Frische | Tatsächlich angefragtes Paar höchstens 0,2 s alt; echte Readindizes/Predecessors, keine Framewiederverwendung |
| Beobachtungen | Höchstens 1024 Policybeobachtungen und 1024 tatsächliche diagnostische Leseversuche wie bisher |
| Aktive Korrekturphase | Bestehende `AIM_SECONDS=20`, einmalig vor dem Detour gesetzt und niemals je Pixel zurückgesetzt |
| Gesamtvorbereitung | Bestehende 85 s ab dem geerbten gemeinsamen Start; Runnerfenster weiterhin höchstens 90 s |
| Ressourcen | 75 % CPU-Obergrenze, 1,5 GiB verfügbarer RAM, 8 GiB freier Datenträger; vorhandene Host-/Query-/Fehlerprüfungen ohne zusätzliche Samplerate |

Die 48 Aktionen sind ein Maximum, kein Anspruch auf 48 vollständige ACKfristen:
48×2 s allein überschreiten 85 s, mit Aktionszeit erst recht. Vor einem neuen
Input müssen konservativ 0,35+2 s vor der frühesten aktiven Deadline verbleiben;
sonst FAIL **vor** dem Request. Die ACKfrist ist weiterhin
`min(request_finished+2, aktive20sDeadline, gemeinsamerStart+85, Runnerende)`.
Alle ursprünglichen Clockprüfungen vor/nach Reads, Guards und Input bleiben.
Ein verspätet zurückkehrender Read wird als verspäteter FAIL erhalten, niemals
als rechtzeitiger ACK akzeptiert. Release/Neutralisierung und normale Cleanup-
Versuche bleiben auch dann verpflichtend; deren bestehende eigene Timeouts
werden nicht verlängert. Ein 2-s-ACK wird nicht für Budgetzwecke synthetisch
abgeschlossen oder eine neue 85-s-Periode begonnen.

Weder ein Null-Request noch falscher Counter-/Clockbereich, fehlende tatsächliche
Antwort, uncommanded Input, Fokusverlust, Identitäts-/Lifewechsel, ReverseDirection,
Grenzübertritt oder Plateau darf übersprungen werden. Die vorhandene strikte
XNextRequest-Spanne `after-before<=4` bleibt bestehen. Alle Rohattempts bleiben
auch bei einem frühen FAIL im exklusiven privaten Journal erhalten.

## Aussage eines möglichen Ergebnisses

Erlaubte positive Kennzeichnung wäre ausschließlich
`PASS_LIMITED_NATIVE_ACK_PITCH_FEEDBACK_RETURN_ONLY`: tatsächliche normale
1-Pixel-Rückkopplung erreichte in dieser Fixture innerhalb bestehender Grenzen
die bestehende diagnostische Rückkehr. Einzelne gemessene Verhältnisse dürfen
als Rohwerte gespeichert werden, sind aber kein verlässliches Gainmodell.

`qualified`, `a1_pass`, `mouse_gain_fixed`, `input_once_proven`,
`actual_shot_proven`, `foreign_hit_proven` und `first_processed_state_proven`
bleiben False. Keine erfolgreiche symmetrische Kalibrierung, kein allgemeiner
Aim-/Bulletkollisionsbeleg und keine Attribution der unbekannten Mausursache.
Ein Nichterreichen innerhalb der Grenzen bleibt FAIL; keine native Folgeschleife.

Spätere Umsetzung nach Rootentscheidung: zuerst reine Fälle für tatsächliche
asymmetrische ACKs, ±1-Regel, Plateau/Reverse/Identitätswechsel, fehlenden ACK,
Grenzfristen und 48×2-s-Worstcase als RED; dann eigene kleine Orchestrierung plus
deaktivierter Builder. Kein gemeinsamer Helferrefactor. Vor einem einzigen
späteren Root-Nativfall Source-/Pinaudit, normale Restorehülle und getrennte
Ergebniskennung nachweisen. Diese Spezifikation erzeugt oder startet kein Paket.

## Frisch gelesene Quellen und Pins

First-State-Vertrag: `docs/reports/2026-11-12-a1-original-first-state-contract.md`,
Abschnitte 1/3/4/7, insbesondere Zeilen 38/50/113. SHA256:
`877040a0bcdca0f89a8ff6d49fabb85a503f0ead136d93ed0b44b114521e7e01`.

Alle folgenden Dateien wurden für diese Entscheidung unter
`/srv/tse-a1-keyboard-root-frozen-20261115` erneut gelesen/gehasht; keine Runtime-
oder vollständige ABIqualifikation wird aus diesen Quellen abgeleitet.

| Datei | SHA256 |
| --- | --- |
| source-manifest.json | eaa83f51049adcab08b1145fa6b1621996e8594e92c96d9a69df7e3fd5addf4f |
| run_dual.py | 467c556076e74f9053c98bd018860b1c1874b354f054b226c175a24a05c1952a |
| colt_preparation.py | 0ad45ef707fb1d75e4bfee53af82d91b9b482e3e1abcca61f63cc51356070f59 |
| runtime_policy.py | 2bfc0805e6bde12707ba45a5768fac76ce3e62bb1c82f2ce4b40bea4502b9ac2 |
| rotation_diagnostics.py | 35dc92dd7a6f5d7fc1b468698a0d41e12cdc7ceb1033668f1dc0bb810510fad2 |
| x11_endpoint.py | 652147c86c52ce3a49afa7ef39c499df7c7a16a357259b4e09b66b2b8d40cb2b |
| a1_passive_xrecord.py | f93e192c2eedf6f0d467cf9cf659be79dbfe3d588ae223eb8d6aea4586119c95 |

Die historischen Mouse-/Keyboard-FAILs einschließlich der tatsächlichen
Keyboarddaten vom 15.11., 02:27:37 UTC, bleiben erhalten. Der zugehörige reine
geschlossene Reader belegt sechs Einzel-ACKs mit abschließendem Pitchfehler
7,5°; er ist keine Umsetzung oder Abnahme dieses neuen Feedbackfalls.
