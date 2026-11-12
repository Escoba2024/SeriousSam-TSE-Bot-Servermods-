# A1 V5: Jede Route-Beobachtung an die jüngste geprüfte Basis binden

**Ergebnis: READY für unabhängigen Re-Review, NOT_RUN.** Beide Ausführungsgates bleiben false. Keine neue native Route, kein Pickup-, Schuss-, Damage- oder First-State-Nachweis. Das native 111716-Resultat bleibt FAIL; der unabhängige V4-Review bleibt als BLOCKED/P1 erhalten.

## Auftrag und Isolation

V5 korrigiert den bestätigten P1 aus dem unabhängigen Review, SHA256 bfe3dee9a8ee83b41805ebf5f17bcee60a4dfb5857b41f97285df840e197dcf6. Das neue private Paket liegt unter /srv/tse-a1-flight-transition-v5-20261112. Die vorhandene isolierte Branch codex/20261112-a1-flight-transition-v4 erhält auf c209e73a13d3435d0b09d5fee5e7be1981e4cfa4 ausschließlich drei neue V5-Dokumente. Root-Worktree, V4, Reviews, Originaldaten, Dienste und Produktion bleiben unverändert.

## Belegte Ursache und tatsächlicher Fix

Der echte PP-Pfad speicherte route-after-input, führte die neuere Probe jedoch nicht der Route zu. Die drei vollständigen Reviewer-Gegenfälle wurden unverändert vor der Korrektur ausgeführt: Support 0, außerhalb des Original-Node 12-Radius und außerhalb des Approachkorridors, jeweils neuerer Same-Tick-Frame 62. Alle drei akzeptierten danach Flug über den älteren günstigen Frame 61. Die eigene Wiederholung des Reviewer-Skripts und die darauf aufgebauten fehlschlagenden Regressionsfälle sind erhalten.

PP verarbeitet die After-Input-Probe nun sofort passiv. Die unveränderte Route prüft einen Kandidaten. Im Approach wird nur dessen jüngster Anker bzw. seine Invalidierung übernommen; Entscheidungstick und Fortschritt bleiben bis zur nächsten frischen Entscheidungsprobe erhalten. Dadurch entsteht weder eine zusätzliche Eingabe noch eine künstliche Rhythmusänderung durch Konsumieren des Entscheidungsticks. Ein bereits beobachteter zulässiger Flugübergang wird vollständig übernommen. Die ausgeführte Aktion wird nicht mit einer neuen Aktion verglichen; die bisherigen Vergleiche der noch nicht begonnenen pending Aktion bleiben bestehen.

Die ausdrücklich auf denselben Lesepfad begrenzte Prüfung belegte zusätzlich action_step → periodic → sample. Ein vollständiger Speichertest mit echten Controller-, Endpoint-, Paar- und Samplingfunktionen las während des letzten normalen Forward drei neuere vollständige Support 0-Proben. Danach verwendete PP noch immer den alten Anker. Die letzten Eingabe-/Lesebelege dieses Gegenfalls sind synthetisch und so gekennzeichnet; sie sind keine Behauptung über native Zwischenzustände.

V5 ergänzt deshalb in native_roles einen aus der tatsächlichen Erfolgsreihenfolge abgeleiteten Marker: letzter vollständiger Paarindex sowie Index und exakte Zeiten seines unmittelbaren Vorgängers. Der zurückgegebene Paargegenstand muss das tatsächliche letzte Listenelement sein. Der native PP-Aufruf verlangt den Vertrag ausdrücklich. Form, int-Typen, bestehende 1024-Grenze, streng steigende Indizes, Zeitreihenfolge und exakter Vorgänger bei direkter Folge werden geprüft. Fehlende oder manipulierte Marker bleiben fatal und der rohe Frame bleibt im Fehlerreceipt.

Ist seit der letzten PP-Probe ein vollständiger erfolgreicher Read ungeprüft geblieben, erhält das Receipt seine Sequenzlücke mit Anzahl und beiden Zeitmarkern. Der ältere Approachanker wird verworfen. Kein Rohzustand wird nachträglich qualifiziert. Die danach frisch und vollständig geprüfte PP-Probe darf wieder regulär die aktuelle Basis bilden. Bereits belegte Flugzeiten werden nicht zurückgesetzt. Fehlgeschlagene/partielle Rohversuche werden weiterhin unverändert erhalten und zählen nicht als vollständige Erfolge.

Historische Fixtures bleiben über das reine PP-Test-API ohne neue Metadaten abspielbar. Der native Controller verwendet zwingend require_successful_read_sequence=True; dies ist durch tatsächliche Aufrufverdrahtung getestet. Nach einem erhaltenen Marker ist auch im Testmodus kein Wechsel auf unmarkierte Frames zulässig.

## Unveränderte Grenzen und konkreter Float-Befund

shooter_policy.py bleibt vollständig bytegleich zu V4: Originalgeometrie, Node 12/34, Support, Geschwindigkeiten, gleiche Life/World und strikt positive Host-/Ticklücke unter 0.5 s bleiben bestehen. RD, frische Doppelreads, ACK, View-Ruhe, ursprüngliche Requestgrenze nach allen langsamen Guards, unabhängiges Release, Hostbudget, Locks, Originalmodule, Normal Close und Restore bleiben unverändert.

Die volle Regression zeigte einen konkreten numerischen Fristfall: Flightstart 5.819999999999998 plus 8 ergibt Deadline 13.819999999999997, während die Subtraktion 7.999999999999999 ergibt. Der bisherige Subtraktionsvergleich akzeptierte diesen exakt an der absoluten Deadline liegenden Testzustand. Die Korrektur lautet ausschließlich value + reserve < flight_started + 8. Kein Epsilon, keine größere Frist. Der bestehende 8-/8.01-s-Test ist unverändert wieder grün; RED und Rohwerte sind erhalten.

85 s gemeinsame Policy, 90 s Controllerfenster, Route 45, Flight 8, Auswahl 3, 48 Aktionen,0.2 s Frische und die bisherigen Readgrenzen werden nicht erweitert. Die Safe-Up-/Cleanupfunktionen erhalten keinen neuen Deadlinewächter.

## Tatsächliche Verifikation

| Prüfung | Ergebnis |
| --- | --- |
| Drei vollständige unabhängige PP-Ankergegenfälle | RED tatsächlich reproduziert → GREEN |
| Tatsächlicher periodic/sample-Gegenpfad | RED mit 3 erfolgreichen Zwischenreads → GREEN |
| Neue Regressionen | 13 Methoden; Sequenzfälschungen und Rohsupportvarianten als Unterfälle |
| Bestehende Fälle | 174 enthalten; nur der Metadatenadapter eines Wiring-Tests ergänzt |
| Vollständige relevante private Suite | 187 Tests in 1.958 s, OK |
| Gezielte Route-/Historien-/Controllerfälle | 32 Tests vor der finalen Frist-/Adapterkorrektur grün; alle im finalen Vollsuitebeleg enthalten |
| Originale erfolgreiche Paarfolge 111716 | 203 vollständige Paare aus 213 Versuchen gegen 9 Quellpins geprüft |
| Strikter V5-Replay mit diesen Originalmarkern | 66 exakte Rollenframes, 27 exakte RD-Paare, 16 exakte Originalreceipts |
| Nicht von PP geprüfte Erfolgsfolgen im Originalreplay | 21 Lücken erhalten; 12 Approachanker verworfen und durch frische PP-Proben regulär ersetzt |
| Letzter Übergang | Raw 211 bleibt Bodenbasis; Raw 212 löst die unveränderte Rücknahme von Versuch 17 vor Request aus |
| Request-/Releasebeleg | 0 neue Down-Requests, 1 sicheres Up, keine gehaltene Taste |
| Native Aktionen oder Builds | Keine |

Der strikte Replay endet absichtlich an Raw 212. Alle tatsächlichen Paar-/Rollenwerte und deren Lesezeiten bleiben exakt. Policy-requested_at stammt wie bisher aus der deterministischen Testuhr; diese zusätzliche Python-Aufrufzeit wird nicht als historischer nativer Zeitpunkt ausgegeben. Ein erster zu weit gefasster Metadaten-Gleichheitsassert samt Diagnose ist erhalten. Kein späterer nativer Flug-, Pickup- oder Feuerzustand wird erfunden.

Der erste Vollsuitebeleg bleibt erhalten: Er zeigte die echte Float-Grenze sowie den noch nicht retargeteten Manifestpfad und fehlenden neuen Testadapter. Der aktuelle Beleg ist ausschließlich flight-v5-private-offline-suite.log und dessen gepinnte Quittung. Kein Test wurde zur Akzeptanz einer größeren Grenze abgeschwächt.

## Delta, Closure und Erhaltung

Genau 2 von 21 eigenen Runtime-Dateien ändern sich: preparation_policy.py und run_dual.py. 19 bleiben bytegleich. 33 Controllerfunktionen, 9 PP-Funktionen und alle 16 Shooterfunktionen sind AST-identisch. Neue PP-Helfer sind nur passive Ankerpflege und Prüfung der Erfolgsreihenfolge. Im Controller ändern sich native_roles, der strikte PP-Aufruf und zwei V5-Bezeichner; action_step, bounded_step, sample, periodic sowie Close/Restore bleiben unverändert.

Nach ausschließlich den benannten Rücknormalisierungen entsprechen beide gesamten Runtime-ASTs exakt dem V4-Parent. Der einzige angepasste alte Test normalisiert nach Entfernen seines tatsächlichen Metadatenadapters ebenfalls exakt auf V4. Alle übrigen alten Tests sind bytegleich.

Finale Closure: **48 Runtimepins, 46 eigene Dateien, 125 Evidenzdateien**, keine Abweichung. Alle 27 externen Runtime-Abhängigkeiten und 12 aktuellen Fixturepins wurden unverändert gegen die tatsächlichen Dateien geprüft. 141 V4-Dateien, 15 unabhängige Reviewdateien und 9 native Quelldateien sind unverändert. Der transitive Close-Wrapper-/graceful-helper-Vertrag und die Prüfung vor nativen Imports bleiben erhalten.

## Finale Pins

| Gegenstand im privaten V5-Paket | SHA256 |
| --- | --- |
| source-manifest.json | 24f05828986e5111c0dd25c10c98b250103c9c5959ab54d5975b122f0087cf1d |
| run_dual.py | 4b8165837af331e34ee47f8b10377919de1ad814065a8b34d5e28080534d9a58 |
| preparation_policy.py | 66e473adb63a9f69a7e3b0f84d18d6004a147af44e4256c78a7660904024a98d |
| shooter_policy.py | 3b78751e5448fd53c67f3c3bfa67163734b86b1ff1da85861b2ebd2b25c3ad0f |
| evidence/flight-v5-normalized-delta.json | dbfb19f5fe268722d03a2efed6b83249fff6ed142b79a1f123ded5121467aa31 |
| evidence/flight-v5-test-receipt.json | f7ba1a999c3ccbbe69dae88108b57f6c53617df2720e990513275fb6cd8b4970 |
| evidence/flight-v5-strict-exact-replay-result.json | e639482a04bdaa51d0b289d1ddb4f3a4814759fd18d77dcf5d6ec67a279cc095 |

Die reproduzierbaren Scripts, vollständigen Diffs, RED/GREEN-Logs, strikte Replayableitung, Normalisierung und Parent-/Review-Pins liegen ausschließlich im privaten Paket. Der komplette Laufzeitcode und die unveränderten Retaildaten gehören nicht in den öffentlichen Dokumentationscommit.

## Übergabe und nächste echte A1-Abnahme

Root übernimmt unabhängigen Re-Review, Integration, separate Root-Kopie, neue eigene Pfad-/Selfpins und einen späteren begrenzten nativen Versuch. Beide Gates dieses Autorenpakets bleiben false. Eine erfolgreiche 85/90 s-Preparation wäre erst die normale Waffenbeschaffung und begrenzte Fire-Kontrolle, noch keine A1-Abnahme.

Als nächste getrennte Arbeit ist normales Ausrichten auf den tatsächlich eigenen zweiten Spieler anhand frischer Positionen und neu bestandener ACK-Kalibrierung erforderlich. Die reale Sicht-/Schusslinie, Original-Fire-/Bullet-Provenienz und normale fremde Damage-Aufrufe müssen belegt werden. Aktuelle Inputreceipts beweisen Request/Release; Waffenbesitz, fire_requested oder spätere HP allein ordnen keinen ersten verarbeiteten Lebenszustand zu.

Wiederverwendbar sind der geprüfte run_dual-Lifecycle, PP, RD, der gepinnte InventoryReader und X11-Endpoint sowie die nativen 090901-/111716-Rohbelege und die vorhandenen Root-Close-/Restorequittungen. Die vorhandene Zwei-Spieler-Anpassung /srv/tse-combat-a1-damage-dual-v2-draft-20261112 bietet den Damage-v2-Beobachter, den strikten Drei-Prozess-Hostvertrag und dual_evidence.final_reasons. Sie enthält keinen nativen Controller und ist nicht runtimefreigegeben. Die ursprüngliche Neun-Spieler-Version /srv/tse-nav-damage-v2-draft-20261111 und deren historische Belege dürfen nicht still in einen Zwei-Spieler-Beleg umgedeutet werden. /srv/tse-combat-a1-lifecycle-draft-20261112 bleibt eine unqualifizierte Integrationskandidatin.

Ein instrumentiertes Folgefenster benötigt eigenständigen Review und vergleichbare uninstrumentierte Kontrolle. Erforderlich sind vollständige Originalbyte-/Main-TLS-/CurrentTick-/Lebens-/Weltbindung, bekannter fremder Inflictor, DMT_BULLET 4, gleicher positiver Spawnclock und tatsächlicher Vorher-/Nachher-HP-Verlust, vollständiger Nenner/Coverage sowie fehlerfreies Stop/Drain/Unload/Detach/Originalbyte-Restore. Unbekannte Inflictoren, Überlappungen, Drops und spätere Fehler bleiben ablehnend.

Für den ordinalen ersten verarbeiteten Respawnzustand fehlt weiterhin die native lückenlose Bindung von InitializePlayer-Abschluss bis zur definierten ersten abgeschlossenen Serververarbeitung desselben Lebens. INITIALIZED/APPLIEDACTION und CurrentTick==SpawnClock allein liefern diese Reihenfolge nicht. Wiederholte reale Gelegenheiten können anschließend mit normalem Feuer/Respawn und tatsächlich beobachteten Spawnpositionen untersucht werden; getrennte Bot-/Originalclient-, Mapwechsel- und Neustartabnahmen bleiben erforderlich. Die aktuelle historische Rolle botA ist dabei ein Originalclient, kein AI-Botnachweis. Keine direkten Engine-Damage-Aufrufe, Teleports oder Spielzustandswrites. Alle weitergehenden Claims bleiben false.
