# A1 Route V3 / 111716: abgeschlossene Read-only-Ursachenanalyse

Datum: 2026-11-12

**Ergebnis: Gesamt-FAIL bestätigt. Die vollständige Kalibrierung wurde erfasst; die Route wurde vor dem 17. XTest-Request sicher abgebrochen.** Es wurde kein neuer nativer Versuch gestartet und keine Paket-, Repository- oder Runtime-Datei geändert. Geschrieben wurden ausschließlich diese neuen Analyseartefakte.

Native Quelle: /srv/tse-milestone-a-evidence-20261111/a1-route-after-rotation-completion-v3-20261112-111716

## Kalibrierung und rohe Gegenrotation

RD meldet CAPTURED_REVIEW_REQUIRED nach 3.516190215014 s mit 27 Beobachtungen. Alle 27 Paare stimmen exakt mit rotation-pairs.jsonl und den zugehörigen Rohversuchen überein.

| Wert | Rechts, +12 px | Links, −12 px |
|---|---:|---:|
| Bestätigtes ACK-Delta | −3° | +3° |
| Zulässiger ACK-Gain | −0.25°/px | −0.25°/px |
| Tatsächliches Körperdelta | −3.0000762939453125° | +2.999969482421875° |
| Körper-Roh-Gain | −0.25000635782877606°/px | −0.2499974568684896°/px |
| Körper minus ACK | −0.0000762939453125° | −0.000030517578125° |

Die Körper-Yaws sind nacheinander −135.0000457763672°, −138.0001220703125° und −135.00015258789062°. Der rohe Rückkehrfehler beträgt 0.0001068115234375°. Nach beiden Forward-/Ruhephasen sind die relativen Blickwinkel auf Server und Vanilla wieder 0; nach der Gegenrotation sind auch die kumulativen Last-/Local-Aktionswerte wieder 0.

Die vier Kalibrier-Requests sind bestätigt und ihre Abschlussquittungen PASS. Die letzten frischen Baselines endeten 0.273–0.394 ms vor den jeweiligen XTest-Anfragen. Die vollständigen exakten Zeiten stehen in analysis.json. Es gibt keine vertauschte Lebens-/Prozessbindung.

ACK-Gains, Körper-Roh-Gains und Rückkehrfehler sind numerisch identisch mit dem erfolgreichen Diagnosefenster 090901. Dieser neue Lauf verwendet wieder −0.25 und prüft daher den zuvor problematischen nativen −0.5-Grenzfall nicht erneut. Die Ursache der früheren Faktoränderung bleibt ungeklärt; ein Exactly-once-Nachweis folgt daraus nicht.

## Erste abgewiesene Routepose

Die Route begann bei Monotonic 1108664.332391231 am unveränderten Originalspawn. Sie blieb bis zum Fehler in phase=approach; flight_started ist null. Die projizierten Knoten sind [63, 68, 6, 7, 8]. Projektion ist kein Beweis des späteren vollständigen Flug-/Pickup-Pfades.

| Messung | Letzte akzeptierte Prüfung | Erste abgewiesene Prüfung |
|---|---:|---:|
| Policy-Beobachtung, Index ab 0 | 64 / route-before-input | 65 / route-pre-emission |
| Rohversuch, Index ab 0 | 211 | 212 |
| Raw-Pair-Index ab 0 | 201 | 202 |
| Lesebeginn, Monotonic | 1108677.689223620 | 1108678.075385716 |
| Leseende, Monotonic | 1108677.697372755 | 1108678.086637101 |
| Nativer Tick | 25.549896240234375 | 25.94989013671875 |
| x | −47.44542694091797 | −28.811553955078125 |
| y | 24.00680923461914 | 46.90065002441406 |
| z | 63.0 | 38.5413932800293 |
| Yaw | 90.00000762939453° | 90.00000762939453° |
| Geschwindigkeit x | −10.0 | 51.8955078125 |
| Geschwindigkeit y | 0.0 | 60.35626983642578 |
| Geschwindigkeit z | 0.0000028212998586241156 | −66.33743286132812 |
| Support-Pointer | vorhanden | 0 |

Die privaten Entity-, Welt-, Lebens- und Prozessbindungen bleiben durchgehend identisch. Alle66 Rollenframes stimmen exakt mit den archivierten Server-Snapshots der jeweiligen Rohversuche überein. Die vollständigen Werte bleiben in der privaten Analyse.

Zwischen diesen zwei Lesebeginnen liegen 0.386162095936 s; zwischen dem vorherigen Leseende und nächsten Beginn 0.378012961010 s. Der native Tick steigt um 0.399993896484 s. Es existiert kein weiterer Rohversuch dazwischen. Die letzte Probe selbst benötigt nur 0.011251384858 s und ist frisch; es handelt sich nicht um eine wiederverwendete alte Probe. Nach der Pre-emission-Leseanforderung liegen 0.121432620101 s vor dem eigentlichen Lesebeginn, innerhalb der bestehenden vorgeschalteten Guards.

## Exakt entscheidender Guard

shooter_policy.Route.next erkennt den Übergang nach flight nur, wenn gleichzeitig x < −35, vx > 20, vy > 10 und vz < −20 gelten. Beim letzten Zustand sind alle drei Geschwindigkeitsbedingungen wahr, aber x < −35 ist falsch. Daher bleibt der Ablauf im Approachzweig.

Die folgende Korridorprüfung verlangt −55 ≤ x ≤ 74, −1 ≤ y ≤ 60, |z−63| ≤ 3 und maximal 2° Heading-Abweichung. **Ausschließlich z verletzt diese Prüfung:** |38.5413932800293−63| = 24.458606719970703 > 3. x, y und Heading liegen innerhalb ihrer Grenzen. Die Fehlermeldung outside reviewed approach corridor/heading ist somit konkret ein z-Korridorfehler nach verfehlter Flugerkennung, kein Headingfehler.

Ein reiner In-Memory-Replay der tatsächlich archivierten, unveränderten Route.next reproduziert mit den aufgenommenen Policy-Frames genau diesen einen Fehler bei Beobachtung 65. Alle vorherigen 39 Entscheidung-/Vorabprüfungen stimmen mit den pending Actions überein. Für die Replay-Zeit wird das aufgezeichnete Paarende verwendet; der genaue interne Aufrufzeitpunkt wurde nicht separat geloggt. Die entscheidenden räumlichen Prädikate sind hiervon unabhängig. Der tatsächliche letzte Guard liegt zwischen Monotonic 1108678.086637101 und 1108678.087030275, rund 13.754 s nach Routenbeginn, nicht an einer 45-s-Frist.

In keinem gespeicherten botA-Rohzustand ist die vollständige x-gebundene Flugstartsignatur erfüllt. Die hohe räumliche Geschwindigkeit und support=0 beim letzten Read sind mit bereits begonnener Flug-/Bouncerbewegung vereinbar. Der genaue physikalische Übergang und eine bestimmte Bouncer-Eventidentität wurden im Beobachtungszwischenraum nicht erfasst. Deshalb wird keine neue Flugphase nachträglich als nachgewiesen eingesetzt und keine Korridorgrenze erweitert.

## Versuch 17 wurde vor dem Request abgewiesen

Es gibt 17 versuchte Aktionen, davon 16 bestätigte und freigegebene Eingabequittungen: vier Kalibriereingaben und zwölf botA-Forward-Holds. Versuch 17 wäre der dreizehnte botA-Forward-Hold für 0.1 s gewesen.

preparation_policy.act führt den pending-Route-Guard erneut im finalen Pre-emission-Callback aus. Der Callback scheitert in der kopierten Route.next. In controller.action_step ruft submit zuerst diesen Callback auf; erst danach würden Requestzeit, held_started und die XTest-Funktion folgen.

Die echte Quittung bestätigt den Abbruch:

- failed_phase = preparation; status = FAIL.
- held_started, emissions[0].started und emissions[0].finished sind null.
- request_confirmed ist false; für Versuch 17 fehlt eine positive Eingabequittung.
- Die sichere Release-/Cleanup-Phase lief von 1108678.087039669 bis 1108678.113500381 weiter.

Es wurde kein neuer Down-Request für Versuch 17 ausgeführt. Das bedeutet nicht, dass keinerlei Cleanup-Key-up-Anfrage stattfand: Die vorhandene sichere Freigabe bleibt unabhängig aktiv. Die Flugbewegung im letzten Zustand kann daher nicht durch einen Down-Request des 17. Versuchs erklärt werden.

## Integrität, Grenzen und Cleanup-Quittung

213 Rohversuche enthalten 203 vollständige Paare und zehn erhaltene transiente state-changed-Ablehnungen. Alle vollständigen Paare, RD-Beobachtungen und Rollenframes wurden zugeordnet; die letzten zwei entscheidenden Versuche sind beide vollständig und erfolgreich gelesen.

Der result.json-Beleg meldet alle drei Rollen und beide Displays geschlossen, ClosedLogs akzeptiert sowie 673 Restorepfade erfolgreich verifiziert. Diese Analyse prüft die geschlossenen Belege; Root prüft parallel aktuelle Restorepfade und Quieszenz. Hier wurde keine zusätzliche Liveprüfung durchgeführt.

Gesamtstatus bleibt FAIL. pickup_observed und normal_fire_control_completed sind false. Waffenbeschaffung, tatsächlicher Schuss, Fremdtreffer und erster Zustands-Treffer sind nicht nachgewiesen. Es wird weder eine Korrektur implementiert noch ein weiterer Versuch empfohlen oder gestartet.

## Artefakte und Quellpins

analysis.json enthält genaue Rohwerte, Bindungen, Prädikate, Quittungen und den reinen Policy-Replay. calibration-timeline.jsonl, route-timeline.jsonl und raw-route-tail.jsonl referenzieren die exakten Raw-Pair-/Attempt-Indizes. source-pins.json bindet sämtliche ausgewerteten Quelldateien; ihre Bytes wurden nach Erstellung dieser Analyse erneut unverändert bestätigt.

| Native Quelle | SHA256 |
|---|---|
| result.json | 2ce98da90855a5b1328d1a5367158f285ee7d1825e95b2e0146e6a9110fc51bc |
| source-manifest.json | 3aac5eadf62a9b6064319d92528ad2fda02cf733d234892dd0a991fbb3aacab7 |
| rotation-pairs.jsonl | b891a8e27d12b67a34c13ae3ba9eee57ad0fd4ad963503c93d0510cefb6bed75 |
| rotation-read-attempts.jsonl | 70e1e0aeb6469cdad06de37d6992d1b3fc7d37cd22503e0c4ac5cdc93facc999 |
| rotation_diagnostics.py | 35dc92dd7a6f5d7fc1b468698a0d41e12cdc7ceb1033668f1dc0bb810510fad2 |
| preparation_policy.py | 57aa07c533cf3c61be81dde36064d2de97cf3689eded71f27393ca7730541c83 |
| shooter_policy.py | 8324d25575dc020e2b95257715ea7ff4c9e54b6535d1a078a7506db4a4b23276 |

Die V2-104429-FAIL-Datei bleibt bei SHA256 4c6da53723ed39bab7549b40a9a85561161fcd99918f54022c1bee99c844c055. Kein älterer Beleg wurde geändert.

## Unabhängige Root-Abschlussprüfung

Root hat anschließend den exklusiven Lablock erworben, alle664 vorhandenen Dateien direkt gegen die Restore-SHAs geprüft und die erneute Abwesenheit der neun temporären Pfade bestätigt. Die vier Labwurzeln sind frei von eigenen Spiel-/Wine-Prozessen; beide Testdisplays sind abwesend. Diese aktuelle Prüfung ist im [kompakten Nativebeleg](milestone-a-20261112/a1-route-v3-native.json) festgehalten. Die unveränderte vollständige Analyse liegt privat unter `/srv/tse-a1-route-v3-native-111716-analysis-20261112/`.
