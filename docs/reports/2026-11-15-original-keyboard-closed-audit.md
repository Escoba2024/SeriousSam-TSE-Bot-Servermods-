# Geschlossener Original-Keyboardfall: sechs Einzel-ACKs, Gesamtabnahme fehlgeschlagen

Claim dieses Audits: ausschließlich dieser neue Bericht und ein separater
privater Datei-Reader. Keine vorhandene Quelle, Runtime, Profile, Grenzwerte oder
Originaldatei wurde geändert. Keine Tests, Displays, Hooks, APIs für native
Prozesse, Eingaben oder Wiederholungsläufe wurden gestartet.

Der tatsächliche NoFire-Fall `a1-keyboard-root-20261115-022737` bleibt **FAIL**:
`opposite keyboard pitch did not return`. Result-SHA256:
`f8c132577541c97bfb257dbfba7a46882dd9c290cf8a28299ffa87dbf581ba5e`.
Sechs bestätigte Einzelaktionen ersetzen die fehlgeschlagene geometrische
Rückkehrprüfung nicht. Mauskalibrierung, Schaden und A1 sind dadurch nicht
abgenommen.

## Tatsächlich gebundene Eingaben

Die vollständigen Rohjournale stimmen mit den eingebetteten Result-Daten und
deren gespeicherten Hashes überein: zwölf Native-Keycalls, zwölf akzeptierte
Attempts, zwölf passende Keymaps sowie sechs Releasequittungen. Jeder Aufruf
ist `XTestFakeKeyEvent`, hat Return 1 und verbraucht genau eine Xlib-Sequenznummer.
Alle fünf eigenen Tasten sind vor dem nächsten Impuls neutral; jeder Down-Bitmap
zeigt ausschließlich die beauftragte Taste, jeder Up-Bitmap ist neutral.
Jeder tatsächliche Up ist einmal ausgeführt, durch XSync bestätigt und mit einer
Nullbitmap quittiert; keine Releasequittung enthält einen Fehler.

Das sind XTest-/Keymapbelege auf derselben Controllerverbindung. RECORD und
Frida wurden nicht armiert. Es gibt deshalb keine aufgezeichnete Wirefolge,
keine exakte Xserver-Haltedauer und keinen Beleg einer bestimmten Anzahl von
Original-GetInput-/CreateAction-Aufrufen.

Alle Phasen verlangten 100 ms. Die folgenden tatsächlichen Controllerzeiten
stammen unverändert aus `input_phase_timings`; jede Eingabe einschließlich
Release blieb unter der unveränderten 350-ms-Grenze.

| Phase | Taste / Wirkung | Host-Hold ms | Release ms | Input bis Release ms | Bestätigte Winkelwirkung |
| --- | --- | ---: | ---: | ---: | --- |
| 0 | J / yaw_left | 138,142 | 18,514 | 156,656 | +45° kumulativer Yaw |
| 1 | W / Forward | 128,917 | 18,513 | 147,430 | Körper-Yaw +44,999969° |
| 2 | L / yaw_right | 131,548 | 21,030 | 152,578 | −45,000000224° kumulativer Yaw |
| 3 | W / Forward | 137,374 | 20,535 | 157,908 | Körper-Yaw −45,000076° |
| 4 | I / pitch_up | 138,135 | 19,654 | 157,789 | Pitch +30° |
| 5 | K / pitch_down | 131,255 | 16,967 | 148,222 | Pitch −22,5° |

Die fünf Tastencodes und zwölf Counterpaare sind privat vollständig erhalten. Es gibt
keinen belegten Vorzeichen- oder Aufrufzählfehler. Insbesondere ist der zweite
Pitchimpuls tatsächlich negativ; er ist lediglich um 7,5° kleiner als der erste.

## Wo die Pitchabweichung bereits sichtbar ist

Die drei ausdrücklich verwendeten Pitch-Level sind serverseitiges
`last_action_pitch_deg`, Original-`local_action_pitch_deg` und
Original-`last_action_pitch_deg`. An den bestätigten Endpunkten stimmen sie
jeweils überein:

| Native-Paar | Zustand | Drei Pitch-Level | Server-/Original-Viewpoint-Pitch |
| --- | --- | --- | --- |
| 34 | vor Up | 0 / 0 / 0° | 0 / 0° |
| 38 | bestätigter Up | 30 / 30 / 30° | 30 / 30° |
| 39 | vor Down | 30 / 30 / 30° | 30 / 30° |
| 44 | bestätigter Down | 7,5 / 7,5 / 7,5° | 7,5 / 7,5° |

Damit liegt die ungleiche Winkeländerung bereits im lokalen kumulativen
Original-Input vor; sie entsteht nicht erst in der Auswertung eines einzelnen
serverseitigen Endpunkts. Körper-Pitch und Bank bleiben in diesen Frames 0°;
die unveränderte reine Colt-Geometrie liest den tatsächlichen Viewpoint-Pitch.
Die direkte Rechnung `7,5−0 = 7,5°` stimmt mit der vorhandenen Wrap-Auswertung
überein. Ein Yaw-Wrap- oder Pitch-Vorzeichenfehler erklärt diesen Fall nicht.

Die Zwischenbeobachtungen begrenzen die Aussage genauer. Beim Up zeigt Paar 35
während des Host-Hold-Intervalls `0 / 7,5 / 0°`; das erste Paar nach vollständig
beendetem Release (36) zeigt `22,5 / 30 / 22,5°`, danach Paar 37 drei Mal 30°.
Beim Down zeigt Paar 40 während des Holds `30 / 22,5 / 30°`, das erste Paar nach
Release (41) `15 / 7,5 / 15°`, danach Paar 42 drei Mal 7,5°.

Zwischen den tatsächlichen Reads bestehen Lücken. Dass ein Wert erstmals nach
Release beobachtet wird, belegt keinen nach Release erneut ausgeführten Input.
Die gespeicherten Buttonraten sind H=300 und P=150, und die beobachteten lokalen
Zwischenwerte enthalten 7,5°-Schritte. Ohne Callbacktrace darf daraus keine
genaue Framezahl oder Ursache der zusätzlichen 7,5° abgeleitet werden. Die
Host-Holds unterscheiden sich um rund 6,88 ms; deren Lage relativ zu den
Original-Eingabezyklen ist nicht aufgezeichnet. Dieses Audit empfiehlt deshalb
keinen Timing-, Gain-, FPS- oder Toleranzfix.

Yaw und Körpergeometrie bestehen ihre vorhandenen Einzelprüfungen: Nach den
zwei normalen Forwardimpulsen beträgt der Körper-Yaw-Rückkehrfehler
0,0001068115234375°. Pitch bleibt dagegen 7,5° vom Anfang entfernt und verletzt
die unveränderte Rückkehrgrenze von 0,75°. Das Programm endet dort korrekt als
FAIL, obwohl `actions_admitted/attempted/released/acked/completed` jeweils 6
Einzelaktionen zählen. `keyboard_evidence_complete`, `generic_trial_accepted`
und `qualified` bleiben False. Auch `diagnostic_only` bleibt im Result False,
weil die Exception vor dem nachfolgenden Finalisierungsupdate eintritt; dieses
Flag wird nicht umetikettiert.

## Denominatoren und Grenzen

Es gibt 45 erfolgreiche Native-Paare aus 46 tatsächlichen Readversuchen und 39
Policy-Beobachtungen. Alle verwendeten Frames sind über den exakten
Successful-Read-Index, Host-Readbereich, beide Prozessgenerationen, lokale
Rollen und unveränderte Entity-/World-/Life-Schlüssel an die ursprünglichen
Rohreads gebunden. Der größte tatsächliche Paired-Readbereich beträgt 19,493 ms.
Native Spielzeiten werden je Peer separat erhalten; sie werden nicht mit der
Host-Uhr gleichgesetzt.

Readversuch 31 scheitert mit `state changed during read`. Er liegt etwa 280 ms
nach dem abgeschlossenen zweiten Forwardrelease und endet etwa 429 ms vor dem
Pitch-Up-Press. Er hat keine gespeicherten Teil-Snapshots. Er wird weder als
gültiger Frame gezählt noch durch Interpolation ergänzt. Die 45 erfolgreichen
Frames behalten ihre echten Indizes; ein fehlgeschlagener Read wird nicht als
zusätzlicher günstiger ACK gezählt.

Die drei eigenen Rollen sind laut ihren Abschlussquittungen normal geschlossen;
die archivierten Logs sind akzeptiert und die aufgezeichnete Transaktion meldet
`restored=True`. Der zusätzliche vollständige Root-Datei-/Metadatenvergleich ist
ein separater Root-Nachweis und wird hier nicht als eigene Wiederholungsprüfung
ausgegeben. Ebenso bleibt der innere Ressourcenbeleg mit sieben Samples und
27,531 s größter Samplinglücke `budget_pass_claim=False`; er ersetzt nicht den
separaten äußeren Root-Ressourcennachweis.

## Reproduktion und Pins

Der private Reader wertet ausschließlich vorhandene Dateien und bereits
gepinnten reinen Geometriecode aus. Er startet keinen Controller und schreibt
seinen Output exklusiv mit Mode 0600. Reproduktion in eine neue Ausgabedatei:

```
python3 -B /srv/tse-a1-keyboard-closed-audit-evidence-20261115/audit_closed_keyboard.py --output /srv/NEW-PRIVATE-CLOSED-KEYBOARD-AUDIT.json
```

| Artefakt | SHA256 |
| --- | --- |
| Root-/Capture-Manifest | eaa83f51049adcab08b1145fa6b1621996e8594e92c96d9a69df7e3fd5addf4f |
| tatsächlicher Controller | 467c556076e74f9053c98bd018860b1c1874b354f054b226c175a24a05c1952a |
| a1_keyboard_input.py | b8f1ec83ea86a50c57dd66bbca8b18bc4c3ddab9a9b32f239a4bceb5fc34f514 |
| a1_keyboard_geometry.py | 48a9c444c298f6070461951ad88a9e7899e0131751ffb22837caac364d62adf7 |
| colt_preparation.py | 0ad45ef707fb1d75e4bfee53af82d91b9b482e3e1abcca61f63cc51356070f59 |
| privater audit_closed_keyboard.py | 13ce97d521f2f834b8690abc0ec669fdc43f59216ef42f5214f94bb0c3c3dc96 |
| closed-keyboard-audit-final.json | 5078d455c808c4c60998433e0e981341bc48e2bc7b1d332465cee49163700858 |

Die vollständige private Quittung liegt im selben privaten Auditverzeichnis.
Sie enthält alle 12 Calls/Attempts/Bitmaps, sechs Releases/Phasen, alle 45
Native-Paare, alle 39 Policy-Beobachtungen, den verworfenen Read sowie Hashes der
Originalarchive und acht verwendeten Quelldateien. Keine Rohidentitäten werden
in diesem öffentlichen Bericht veröffentlicht.
