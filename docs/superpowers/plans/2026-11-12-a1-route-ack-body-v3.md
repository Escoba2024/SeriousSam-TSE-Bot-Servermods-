# A1 Route V3: ACK-Gain und bestehende Körperkonsistenz

Datum: 2026-11-12
Owner: /root/review_names_transaction
Status: **READY_FOR_INDEPENDENT_ROOT_REVIEW**, private Ausführung deaktiviert.
Basis: 4d51a57c41cec2189a49b70f38f3301c664c984c
Privater Nachfolger: /srv/tse-a1-route-after-rotation-completion-v3-20261112

## Ziel und belegte Ursache

Root autorisierte die eng begrenzte Korrektur nach der Read-only-Analyse des tatsächlichen 104429-FAIL. ACK −6° / 12 px = −0.5 liegt im unveränderten zulässigen Bereich. Die tatsächliche Körperantwort −6.0000457763671875° ergibt einen Roh-Gain von −0.5000038146972656; die frühere Bereichsprüfung wies ihn vor der bestehenden EPS-Konsistenzprüfung ab. Drei Float32-Winkelschritte liegen innerhalb EPS 0.001°.

Der alte FAIL bleibt erhalten. Warum das normale +12-px-Signal jetzt −6° statt früher −3° bewirkte, bleibt ungeklärt; kein Exactly-once-Nachweis.

## Umfang und unveränderte Grenzen

Nur RD.run_calibration verwendet nach bestätigtem, zulässigem ACK die bestehende EPS-Prüfung der Körperantwort und stellt erst danach den ACK-Gain bereit. Rohwinkel, Körperdelta und Roh-Gain bleiben unverändert und werden ausdrücklich belegt. Roh-Gain-Gegenrichtungsdifferenz maximal 0.05 und Körperrückkehr maximal 0.75° bleiben bestehen.

ACK-Bereich [−0.5, −0.02], EPS 0.001°, lokale Fristen 2 s, globale 85/90 s, Route 45 s, Flug 8 s, Auswahl 3 s und maximal 48 Aktionen bleiben gleich. Keine Eingabe-Wiederholung, kein nativer Start oder Build, keine Änderung an Originalquellen, Route, Transport, Read-Retry, Normal-Close oder Restore. run_dual.py ändert ausschließlich zwei V3-Bezeichner. Alte Pakete bleiben unverändert.

## Aufgaben und Abnahme

- [x] Neues deaktiviertes V3-Paket und eigener Claim; Inventur aller 115 V2-Dateien vor und nach der Arbeit.
- [x] RED mit allen 15 tatsächlichen 104429-Policy-Paaren und beiden Eingabequittungen in realem RD; ursprüngliche Ablehnung reproduziert.
- [x] Gegenfälle innerhalb/außerhalb des vorhandenen EPS (65/66 Float32-Schritte mit beiden Vorzeichen), falsche Körperrichtung, unzulässiges/falsch gerichtetes ACK und unveränderter Roh-Gain-Gegenrichtungsgrenze.
- [x] Minimale Korrektur; GREEN mit exakt erhaltenem Körper-Rohwert und bereitgestelltem ACK-Gain −0.5.
- [x] Replay endet absichtlich vor einer unbewiesenen linken Eingabe; keine native Abschlussbehauptung.
- [x] Vollständige relevante private Regression: 155 Tests PASS in 0.817 s; sechs neue Tests gezielt PASS in 0.025 s.
- [x] Closure und normalisierte Deltas geprüft: 48 Runtime-, 43 eigene und 82 Evidenz-Pins; 19 eigene Runtime-Dateien bytegleich, 27 externe Runtime-Pins unverändert; alte 115 V2-Dateien sowie originale FAIL-Quellen/Raw-Belege unverändert.
- [x] Manifest, Testquittung und Abschlussbericht eingefroren; ausschließlich neue V3-Dokumentation für Repository-Commit.
- [ ] Root: unabhängiges Review, separate eingefrorene Kopie und aktuelle Fixture-/Originalpins prüfen.
- [ ] Root: nach READY höchstens ein neuer begrenzter nativer Versuch; vollständige Kalibrierung, Route/Feuer, Rohdaten, Normal-Close, Logs und Restore bewerten.

## Persistente Ergebnisse

Bericht: docs/reports/2026-11-12-a1-route-ack-body-v3.md
Manifest-SHA256: 8aa93b6db274fe78af30c23caa2b2e7fb946345468fa96788745c5911a53bb87
Normalisierter Delta-SHA256: 52eec0d46eaa333884c25b3c4c90d3d773019d9264ab3dd7abab73855b819275
Testquittung-SHA256: 4209315e10b2fce8a2cfb03c89f0ba5679fce9174a221f096fe52f224fbe7b99

Die getrennte Ursachenanalyse bleibt unter /srv/tse-milestone-a-continuation-evidence-20261112/a1-route-v2-native-104429-analysis/ANALYSIS.md erhalten. Alle Schuss-/Treffer-/Erstzustands-/Qualifikationsbehauptungen bleiben false. Root besitzt alle späteren nativen Entscheidungen.
