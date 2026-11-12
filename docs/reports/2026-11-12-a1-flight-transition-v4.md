# A1 V4: gebundener Approach→Flight-Übergang

Datum: 2026-11-12
Status: **READY_FOR_INDEPENDENT_ROOT_REVIEW**
Owner: /root/review_names_transaction
Repository-Basis: c5e36ed55f4ad3ecf7b2130161ab251eaa8b25b7
Privates Paket: /srv/tse-a1-flight-transition-v4-20261112

## Ergebnis und Abnahmegrenze

Die belegte Engstelle aus dem tatsächlichen Lauf 111716 ist in einem neuen deaktivierten Paket korrigiert. Der exakte Offline-Replay erreicht mit denselben 27 RD-Paaren, 66 Rollenframes und 16 vorhandenen Eingabequittungen nun den passiven Flugzustand. Der pending 17. Forward wird über den tatsächlichen Controller-/Endpoint-/Transportpfad vor XTest zurückgehalten. Das Originalfenster bleibt FAIL.

**174/174 private Tests bestanden in 1,251 s:** alle 155 bisherigen Tests unverändert sowie 19 neue. Keine Builds, nativen Starts, produktiven Änderungen oder Root-Worktree-Writes. Beide Runtime-Gates bleiben false. Nach Raw 212 existiert kein weiterer nativer Zustand; der Replay stoppt dort ausdrücklich. Ein tatsächlicher Pickup-, Feuer-, Treffer- oder Erstzustandsnachweis bleibt offen.

## Ursache und konservative Korrektur

Im geschlossenen V3-Fenster zeigte Raw 211 noch eine gestützte gültige Approach-Pose innerhalb des unveränderten Radius von Originalknoten 12. Raw 212 begann 0,386162096 s später; der native Tick war rund 0,4 s weiter. Support war0 und die drei bekannten Flug-Geschwindigkeitsbedingungen waren erfüllt, während x bereits jenseits der bisherigen x<−35-Erkennung lag. Die folgende Approachprüfung scheiterte konkret an z, nicht an Heading. Es gibt keinen aufgezeichneten Zwischenzustand oder Nachweis einer bestimmten Bouncer-Eventidentität.

Die ursprüngliche direkte Flugsignatur und der Approachkorridor bleiben bestehen. Eine spätere Beobachtung außerhalb dieser x-Zone benötigt zusätzlich den unmittelbar vorherigen tatsächlich beobachteten Approachzustand:

- unveränderte Lebens-/Weltidentität, positiver Support und Position im vorhandenen Original-Node 12-Radius 4;
- positiver Host- und Native-Tick-Abstand, beide strikt kleiner als 0,5 s;
- aktueller Support 0, unverändert vx>20/vy>10/vz<−20 und unverändertes Heading;
- Positionsfortschritt innerhalb der ursprünglichen Kante 12→34, ohne am Ziel vorbeizuspringen.

Der zusätzliche Deckel von 0,5 s ist ein neuer zusätzlicher Belegschutz. Kein vorhandenes Budget wird angehoben. Jede neuere Approach-Probe ersetzt oder verwirft den Anker auch bei gleichem nativen Tick. Eine ältere günstigere Probe kann ihn nicht ersetzen.

Bei diesem verspätet beobachteten Übergang beginnt Flight8 bereits am Lesebeginn der letzten Bodenprobe. Die Beobachtungslücke wird vollständig mitgezählt. Beide Rohzustände und das bekannte Zeitintervall werden in flight_transition erhalten. Ein exakter physikalischer Flugstart oder eine Bouncer-ID wird nicht erfunden.

## Kein Forward nach dem beobachteten Zustandswechsel

Die neue Prüfung entscheidet ausschließlich über die bereits geplante Aktion. Erkennt sie flight, wird der pending Forward zurückgenommen. Jede andere Änderung von Aktion, Dauer, Korridor, Besitz, Leben oder Prozess bleibt fatal.

Ist der Übergang schon vor dem Endpointaufruf sichtbar, wird step nicht mehr aufgerufen. Wird er erst nach allen langsamen Endpoint-/Transportguards erkannt, reicht eine typisierte RouteFlightBeforeInput-Rücknahme vom letzten PP-Callback bis zum Controller. Der Controller akzeptiert sie ausschließlich vor Requestbeginn für einen einzelnen zulässigen botA-Forward. Derselbe Exceptiontyp aus einem anderen Ursprung oder nach Requestbeginn bleibt FAIL.

Bei der Rücknahme sind held_started sowie Request-start/finish null und request_confirmed false. Sichere Key-up-/Releaseprüfung läuft unverändert weiter. Cleanup-/Clockfehler können nicht als erfolgreiche Rücknahme erscheinen. PP akzeptiert die neue Quittung nur bei zuvor selbst festgestelltem Flugübergang, bestätigter Freigabe und konsistenten Zeiten.

Der Versuch bleibt in actions und input_phase_timings; input_receipts enthält ausschließlich positive tatsächliche Eingabequittungen. Timingindizes zählen Versuche, damit eine Rücknahme keinen späteren Index dupliziert. Die Rücknahme wird nicht als Inputretry ausgeführt. Anschließend gelten die bestehenden passiven Flug-/Pickupprüfungen.

## Reproduzierbare Verifikation

Der private Testbeleg enthält unveränderte Daten aus 111716 und SHA-Pins der Originalquellen. Zunächst reproduzierten die reine Route und der vollständige PP→bounded_step→action_step→Endpoint/Transport-Replay exakt outside reviewed approach corridor/heading. XTest ist in diesen Tests ausschließlich ein Speicherersatz; kein Display-/Prozess-/Inputbackend wird geöffnet.

Die 19 neuen Tests decken insbesondere ab:

- den vollständigen tatsächlichen Replay bis zur verfügbaren Datengrenze sowie beide Rücknahmepunkte;
- zu große/negative Host- und Native-Tick-Abstände, alte günstige Anker trotz neuerer Same-Tick-Probe und falsche Launchgeometrie;
- Lebens-/Welt-/Prozesswechsel, veraltete Frames, falschen Support und falsche Geschwindigkeitsrichtung;
- unverändert fatale andere pending-action Änderungen;
- Cancellation aus falschem Ursprung oder nach bereits begonnenem Request, fehlerhafte Freigabe und nicht angeforderte Quittungen;
- abgelaufeneFristen von 85/45/8 s einschließlich eines ausdrücklich synthetischen, zu spät erfolgreichen Pickupzustands.

Der Same-Tick-Ankergegenfall wurde zusätzlich separat RED→GREEN nachgewiesen. Gezielter finaler Lauf:19 Tests in 0,456 s. Vollständige relevante Regression:174 Tests in 1,251 s. Die Abschlussverdrahtung und der bestehende Cleanup-/Finalizerpfad wurden geprüft; die sichere Rücknahme wird nicht als positiver Input gezählt. Der Replay behauptet keine vollständige native Kalibrierungs-/Route-Abnahme des neuen Pakets.

## Umfang und Erhaltung

Verhaltensänderungen betreffen ausschließlich shooter_policy.Route, die Orchestrierung in preparation_policy und action_step/bounded_step im Controller. Der Controller erhält zusätzlich zwei eigene V4-Unit-/Evidenzbezeichner.

RD einschließlich ACK-/EPS-Korrektur, Endpoint/Transport und Freigabe, Originalplan, legacy calibration_gain/run_program, Reader, Transaktion, Normal-Close, Restore, Hostbudgets, Prozess-/Modul-/Welt-/Profilbindungen und Lockverfahren bleiben unverändert. ACK-Bereich, EPS, Reader-Retry/Freshness, lokale Prüfungen von 2 s, globale 85/90 s, Route 45 s, Flight 8 s, Auswahl 3 s und Aktionen 48 werden nicht erweitert.

Alle 126 Dateien des V3-Parentpakets und die tatsächlichen nativen Quelldateien wurden vor/nach der Arbeit unverändert geprüft. 18 von 21 eigenen Runtime-Dateien sind bytegleich; alle 27 externen Runtime-Pins und 12 aktuellen Fixture-Pins stimmen unverändert mit den tatsächlichen Dateien überein. Außerhalb der ausdrücklich geänderten Bereiche normalisieren alle drei Runtime-Quellen exakt auf den Parent-AST. Unverändert sind 13 Shooter-, 8 PP- und 31 Controllerfunktionen. Private Raw-Belege und Runtimequellen werden nicht in diesen Dokumentationscommit aufgenommen.

## Finale Pins

Alle relativen Dateinamen beziehen sich auf das private V4-Paket.

| Datei | SHA256 |
|---|---|
| source-manifest.json | 330c5c3b972bb6e83d3f573f1105b4ee3077559a8edc3b20865967d811339e71 |
| run_dual.py | ba4fe5305dd65a1c05fa5d8a2846ab5ba1429c2106fe6ba43030e029a39ab3f6 |
| shooter_policy.py | 3b78751e5448fd53c67f3c3bfa67163734b86b1ff1da85861b2ebd2b25c3ad0f |
| preparation_policy.py | 025217ae6ad38ebdcc2c63427fb16f31dd4bd1cb6f6d65d5af6c03e143d6772d |
| evidence/flight-v4-normalized-delta.json | ec58c4d82fa06f9eda9f11575982cc8e490df1e4ec6549914e8d6d09a6763f61 |
| evidence/flight-v4-test-receipt.json | c0fc478c5690fbd451933c29e8f5865d678dd06b64714cfe79b224a998da759d |
| evidence/flight-v4-exact-replay-result.json | 5d66833b98a178aa9806c1c941316192edfd9e0d85914af4a05ea0116042eb64 |
| evidence/flight-v4-native-111716-test-fixture.json | 1b0d6580cf1844b3916fbeefc2abba21edfc25084866a339b91c0c9986469af0 |

Manifestumfang: **48 Runtime-Pins, 44 eigene Datei-Pins, 96 Evidenz-Pins**. Die drei vollständigen Runtime-Diffs liegen separat unter evidence/flight-v4-*.py.diff. Alle eigenen Dateien und Evidenzpins wurden nach dem Freeze nochmals gegen das Manifest geprüft.

## Handoff und verbleibende Grenzen

Root übernimmt das unabhängige Review, Integration/Sicherung und gegebenenfalls eine separat eingefrorene native Kopie. Vor einem tatsächlichen Lauf sind aktuelle Fixture-/Originalpins und technische Exklusivität erneut zu prüfen. Dieses Paket wird nicht in-place aktiviert.

Die aktuelle Korrektur belegt sichere Verarbeitung des bekannten Übergangs. Ein anderes physikalisches Muster, eine längere Beobachtungslücke oder abweichende Originalgeometrie wird weiterhin konservativ abgewiesen. Der weitere tatsächliche Flug, Pickup und normale Kontrollschuss sind noch zu beobachten. Erst danach folgen normales Ausrichten auf den eigenen zweiten Spieler und passive Original-Schuss-/Damage-/Lifecyclebelege. A1 ist damit nicht abgenommen; B bleibt unbegonnen.
