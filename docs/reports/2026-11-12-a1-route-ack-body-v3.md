# A1 Route V3: ACK-Gain und bestehende Körperkonsistenz

Datum: 2026-11-12
Status: **READY_FOR_INDEPENDENT_ROOT_REVIEW** — privates Paket deaktiviert, kein nativer V3-Lauf.
Verantwortlich: /root/review_names_transaction
Repository-Basis: 4d51a57c41cec2189a49b70f38f3301c664c984c
Privates Paket: /srv/tse-a1-route-after-rotation-completion-v3-20261112

## Belegte Ursache und weiterhin offene Faktoränderung

Der tatsächliche Lauf /srv/tse-milestone-a-evidence-20261111/a1-route-after-rotation-completion-v2-20261112-104429 bleibt unverändert FAIL. Er endete nach LookRight und Forward innerhalb der Kalibrierung; Route und Feuer wurden nicht erreicht.

| Messgröße | Unveränderter Rohwert |
|---|---:|
| Körper-Yaw vor Look/Forward | −135.0000457763672° |
| Körper-Yaw nach Forward und Ruhe | −141.00009155273438° |
| Körper-Delta | −6.0000457763671875° |
| Körper-Roh-Gain bei +12 px | −0.5000038146972656°/px |
| Bestätigtes kumulatives ACK-Delta | −6° |
| Bestätigter ACK-Gain | −0.5°/px |
| Körper minus ACK | −0.0000457763671875° |
| Bereits vorhandenes EPS | 0.001° |

Der frühere Aufruf von calibration_gain wies den Körper-Roh-Gain knapp unter −0.5 ab, bevor die bereits bestehende Körper-/ACK-Konsistenzprüfung mit EPS greifen konnte. Der Unterschied beträgt genau drei Float32-Winkelschritte bei dieser Größenordnung. Der erfolgreiche Diagnose-Lauf 090901 hatte fünf solche Schritte, lag mit seinem Gain nahe −0.25 jedoch nicht an der Bereichsgrenze.

Die Read-only-Analyse prüfte die Zuordnung aller 15 Policy-Paare zu den vollständigen Raw-Paaren und Versuchseinträgen sowie Prozess-/Lebens-/Weltbindung und Eingabezeiten. Die letzten Look-/Forward-Baselines begannen rund 9.257/8.954 ms vor der tatsächlichen Anfrage und endeten jeweils rund 0.26 ms davor. Die Daten passen zur gleichen Look-Aktion; sie belegen keinen alten oder vertauschten Callback-Zustand.

**Warum +12 px im Lauf 104429 −6° statt der früher beobachteten −3° erzeugten, ist weiterhin ungeklärt.** Diese Faktoränderung wird durch die numerische Korrektur weder erklärt noch als genau einmal verarbeitete Eingabe qualifiziert.

Persistente Analyse:

- /srv/tse-milestone-a-continuation-evidence-20261112/a1-route-v2-native-104429-analysis/ANALYSIS.md
- SHA256: 685efe1c5f78a8d526279b4607e67554a71b92d98ea725b07db01d49163f8d41
- Daneben: analysis.json, failed-timeline.jsonl und passed-timeline.jsonl.

## Eng begrenzte Änderung

Nur RD.run_calibration erhält eine Verhaltensänderung. Nach dem unverändert zulässigen, bestätigten ACK bleiben valid, gleiche Lebens-/Weltkennung und exakt 12 px vorgeschrieben. Die Körperantwort muss weiterhin die vorhandene EPS-Prüfung gegen das ACK bestehen. Erst danach wird der bereits zulässige ACK-Gain als calibration.yaw_degrees_per_pixel bereitgestellt; gain_basis ist ausdrücklich acknowledged_action.

Die Körperwinkel in den Paaren bleiben unverändert. Zusätzlich werden body_delta_yaw_deg_raw, body_gain_deg_per_pixel_raw und body_yaw_degrees_per_pixel_raw ohne Rundung oder Begrenzung gespeichert. Auch ein später abgewiesener Körperwert bleibt im Beleg erhalten. Die ursprüngliche Begrenzung der Differenz beider Körper-Roh-Gains auf 0.05 wird weiterhin anhand der Rohwerte geprüft. Die bestehenden ACK-Gegenrichtungs- und Körperrückkehrprüfungen bleiben erhalten.

Der ACK-Bereich bleibt einschließlich seiner Grenzen [−0.5, −0.02], EPS bleibt 0.001°. Kein Zeitbudget, Retry oder Aktionslimit wird erweitert: lokale ACK-/Ruhefrist 2 s, globale 85/90 s, Route 45 s, Flug 8 s, Auswahl 3 s, maximal 48 Aktionen. Identität, Doppelreads, Transient-Allowlist, Rohbelege, Eingabegrenze aus V2, Normal-Close und Restore sind unverändert.

run_dual.py ändert ausschließlich zwei Bezeichner für V3-Unit/Evidenz. preparation_policy.py, shooter_policy.py einschließlich Route und legacy calibration_gain sowie x11_endpoint.py bleiben bytegleich zu V2. Die ursprüngliche Route fährt vorwärts und berechnet keine Drehungen aus einem Maus-Gain; ihre Freigabe benötigt weiterhin die gerade bestandene RD-Kalibrierung. Ein Verbraucher erhält den bestätigten ACK-Gain, nicht den außerhalb des zulässigen Bereichs liegenden Körper-Rohwert.

## RED/GREEN und Aussagegrenzen des Replays

Sechs neue Tests verwenden tatsächliche RD-Funktionen. Der native Replay enthält exakt die 15 Policy-Paare und zwei Eingabequittungen aus 104429. Er reproduzierte vor der Änderung die ursprüngliche Ablehnung. Nach der Änderung wird die erste Körperantwort angenommen: Roh-Delta −6.0000457763671875°, Roh-Gain −0.5000038146972656°/px, bereitgestellter ACK-Gain −0.5°/px.

Der Replay stoppt absichtlich **vor der nächsten linken Eingabe**, für die dieses native Fenster keine Daten enthält. Er behauptet keine vollständige native Kalibrierung, Route oder Schussabgabe.

Die Gegenfälle prüfen:

- 65 Float32-Winkelschritte innerhalb des vorhandenen EPS gegen 66 Schritte außerhalb, jeweils mit beiden Vorzeichen.
- Falsche Körperrichtung trotz zulässigem ACK.
- ACK außerhalb des bestehenden Gainbereichs oder in falscher Richtung; Ablehnung vor Forward.
- Unveränderten Rohwert-Erhalt und zulässigen ACK als bereitgestellten Gain.
- Den unveränderten maximalen Unterschied von 0.05 zwischen den Körper-Roh-Gains beider Impulse.

Gezielter GREEN-Lauf: 6 Tests in 0.025 s. Vollständige relevante private Regression: **155 Tests bestanden in 0.817 s**. Enthalten sind alle 149 bisherigen Tests für Controller, tatsächlichen Endpoint/Transport, abgelaufene Fristen, Read-Retry, Route und Lifecycle sowie die sechs neuen Fälle. Kein C++-Build und kein nativer Start.

Testquittung: evidence/route-v3-test-receipt.json. RED-/GREEN-/Gesamtlogs und das Ergebnis des begrenzten exakten Replays liegen unter evidence/route-v3-*. Die Testquittung bindet das vollständige Suite-Log und die native Replay-Datei per SHA256.

## Eingefrorene Pins

Alle Pfade in der Tabelle sind relativ zum privaten V3-Paket.

| Datei | SHA256 |
|---|---|
| source-manifest.json | 8aa93b6db274fe78af30c23caa2b2e7fb946345468fa96788745c5911a53bb87 |
| run_dual.py | 532678f4505e6c3138cdeb36c86e2e70678483ad04d4b068255d70c9376d979f |
| rotation_diagnostics.py | 35dc92dd7a6f5d7fc1b468698a0d41e12cdc7ceb1033668f1dc0bb810510fad2 |
| evidence/route-v3-normalized-delta.json | 52eec0d46eaa333884c25b3c4c90d3d773019d9264ab3dd7abab73855b819275 |
| evidence/route-v3-test-receipt.json | 4209315e10b2fce8a2cfb03c89f0ba5679fce9174a221f096fe52f224fbe7b99 |
| evidence/route-v3-native-104429-replay.json | 9abb01b7c5f17f0261361be1c12a09f77c8c4142677b8327ac2ee8c59f42c9ca |
| evidence/route-v3-private-offline-suite.log | ba041f52520628897ebb73057fe9331cff6f47e0ce4c402becdf9bc3af95c4bc |
| evidence/route-v3-exact-replay-result.json | 55aff4580df807894d3bb85f68714f73942c56fe4d800231cf7bd9d91dec6a87 |

Das Manifest enthält 48 Runtime-Pins, 43 eigene Datei-Pins und 82 Evidenz-Pins. Von 21 eigenen Runtime-Dateien sind 19 bytegleich; RD enthält ausschließlich die dokumentierten Korrekturhunks, der Controller ausschließlich V3-Bezeichner. Alle 27 externen Runtime-Pins bleiben gleich. Der normalisierte Controller ist exakt V2; 34 gemeinsame Controllerfunktionen sind AST-identisch. Die neun inneren RD-Funktionen bleiben AST-identisch.

Alle 115 Dateien des V2-Pakets sind unverändert. Dessen Manifest bleibt 6ea34a1fa6a11c86c9b25db554535a509fabcccb8b18ba6347603b12fd210ee8. Die gespeicherten SHA256-Werte der tatsächlichen FAIL-Quellen und Raw-Belege wurden erneut gegen die Originaldateien geprüft. Ältere Pakete und Belege wurden nicht bearbeitet.

## Handoff und offene Abnahme

RUNTIME_REVIEWED im Controller und runtime_reviewed im Manifest bleiben false; runtime_performed bleibt false. Nur neue V3-Dokumentation geht in diesen Repository-Commit. Die privaten Runtime-Quellen bleiben separat über obige Pins festgelegt.

Root übernimmt die unabhängige Prüfung, erstellt bei READY eine eigene eingefrorene Kopie und führt höchstens einen neuen begrenzten nativen Nachfolger aus. Davor sind aktuelle Fixture- und Originalabhängigkeiten erneut zu prüfen; abweichende Pins benötigen eine Erklärung. Eine erfolgreiche Offline-Regression ist keine A1-Abnahme.

Der nächste native Lauf muss erst die vollständige aktuelle Kalibrierung bestehen, dann die normale Original-Pickup-Route und den begrenzten normalen Feuer-Hold erreichen. Reale Schuss-, Fremdtreffer- und erster Zustands-Treffer-Belege sind damit weiterhin nicht erbracht. Alle entsprechenden Qualifikationsbehauptungen bleiben false.
