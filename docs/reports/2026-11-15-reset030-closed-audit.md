# Reset030 – geschlossener FAIL unverändert

Der Lauf `a4-reset030-v3-root-20261115-110253` bleibt FAIL (Result `dc38ebb2f86fb3364ae5bd64bf77a47c7f1aebb3df1f200b4e58f4903c97ce7a`). Drei Phasen/24 Slotphasen und zwei normale Red→Red-Kartenresets wurden in425.421824s beobachtet; die strikten Aktivitätskriterien scheitern weiterhin an Phase1 A:1 (Useful-Gain und Useful-FIRE) sowie Phase2 A:2 (Useful-FIRE). Keine Kriterienänderung, Nativewiederholung oder A4-Abnahme.

Alle bestehenden ResetV3-Envelope-/Attempt-/Source-Life-/Decimal-Prüfungen wurden reproduziert.6347 tatsächliche Readversuche:6160 erfolgreiche Reads, davon3 getrennte Smokeproben und6157 Gameplayreads;187 verworfen (157 state changed/30 tick changed).4185 vorab kanonisch festgelegte Botgruppenproben,1972 getrennt validierte Overlapproben. Die260 frühen Übergangsproben sind bereits streng gebundene Gameplayreads, keine zusätzlichen Reads und kein alternativer Pickupstream.

| Phase | Versuche/verworfen | Native Leben | links/rechts zensiert | beobachteter Tod | Usefulbesitz/Gains | Server-Killlogzeilen |
|---|---:|---:|---:|---:|---:|---:|
|0|2307/70|43|27/8|35|17/25|35|
|1|1939/57|50|37/8|42|21/24|43|
|2|2101/60|44|37/8|36|17/23|37|

137 kanonische native Leben,101 links-/24 rechtszensiert und ein Leben mit erneut positiver Probe nach erstem beobachteten Tod (Phase0, separat mehrdeutig). Die qualifizierte Lebenszusammenfassung zählt daraus keinen zusätzlichen Pickup/Lebenszeitgewinn. Legacy-Aktivitätszähler des ganzen überlappenden Streams und kanonische Lebensnenner bleiben nebeneinander erhalten; sie sind keine austauschbaren Nenner. Server-Killlogzeilen sind weder vollständige Damagecalls noch ein Vergleichssieg.

## Alle24 Slotphasen

Leben/Besitz/Gains aus dem kanonischen Stream, Flag aus unveränderter V3 mit Same-Life-Sourcecountergrowth. Jeder Slot ist tatsächlich lokal/global zugeordnet; globale Slots wechseln über Kartenwechsel. Flag ist kein Weaponcall-/Hit-/Bewegungs-ACK.

|Phase|lokal|global|Leben|Usefulbesitz|Gains|Useful-FIREflag+Sourcegrowth|
|---|---|---:|---:|---:|---:|---:|
|0|botA:0|0|8|2|2|45|
|0|botA:1|2|7|1|3|3|
|0|botA:2|3|5|3|5|54|
|0|botA:3|4|3|2|3|172|
|0|botB:0|5|5|3|5|70|
|0|botB:1|6|4|3|4|124|
|0|botB:2|7|5|1|1|76|
|0|botB:3|8|6|2|2|21|
|1|botA:0|4|5|3|4|270|
|1|botA:1|5|5|0|0|0|
|1|botA:2|6|6|2|2|16|
|1|botA:3|7|4|2|3|178|
|1|botB:0|0|10|4|3|78|
|1|botB:1|1|6|4|6|36|
|1|botB:2|2|8|2|2|4|
|1|botB:3|3|6|4|4|74|
|2|botA:0|0|9|4|3|146|
|2|botA:1|2|6|2|2|24|
|2|botA:2|4|7|1|1|0|
|2|botA:3|6|1|1|3|93|
|2|botB:0|1|5|2|3|12|
|2|botB:1|3|7|3|3|85|
|2|botB:2|5|5|3|7|21|
|2|botB:3|7|4|1|1|75|

## Phase1 A:1/global5: tatsächlich kein beobachteter Usefulbesitz

Alle612 gültigen kanonischen Aliveproben haben owned3 (Knife1/Colt2), keine Usefulwaffe; fünf beobachtete native Leben. Vier enden mit beobachtetem Tod, das letzte bleibt rechtszensiert; die ersten drei sind linkszensiert.21 tatsächliche sampled FIREbits liegen ausschließlich bei currentColt2. Damit ist weder allgemeines Nichtfeuern noch bloß ein verpasster Useful-Pickupübergang bewiesen: im beobachteten Nenner fehlt auch Usefulbesitz. Leben/Erstprobe/Ende bleiben exakt native Floatzeiten, ohne SourceTick/20-Umrechnung.

|Spawnclock|Alive-Probenzeitraum|Distanz der Endpunkte / beobachtete Chords*|World-Y-Range|Tod|Knife/Colt-Proben|Colt-FIREproben|
|---:|---|---:|---|---:|---:|---:|
|6.700007439|7.650011063–31.849800110|70.457 /359.519|−5.996…43.843|31.999797821|74/68|6|
|33.499774933|33.549774170–55.199443817|92.486 /313.018|−2.988…40.801|55.349441528|111/17|0|
|57.099414825|57.249412537–58.949386597|22.739 /28.538|0.190…4.230|59.249382019|6/6|1|
|60.699359894|60.699359894–109.052055359|129.957 /693.606|−5.997…45.009|109.202064514|133/143|14|
|110.702156067|110.702156067–120.002723694|37.227 /167.712|0.007…35.282|offen|40/14|0|

*Nur direkte beobachtete Positionschords bei unveränderter0.5s-Gapregel; keine interpolierte tatsächliche Weglänge oder kontinuierliche Geschwindigkeit. Das48.353s-Alivefenster des vierten Lebens enthält echte große Positions-/Höhenänderungen, keinen belegten durchgehenden Stillstand. Seine größte Beobachtungslücke ist0.600037s und bleibt eine Lücke. Aktueller/wanted-Nenner und alle Positionsendpunkte stehen privat.

Kontinuierliche FIREdauer ist unbekannt. Die sampled Colt-Flagruns haben nur Endpunktspannen: erstes Leben0/0.299995/0.249996s, drittes0s, viertes0/0.850052/1.000061s; einzelne Proben und diese Spannen dürfen nicht als kontinuierlich gehaltene Feuerzeit integriert werden. Desired/Wanted ist ebenfalls kein bestätigter Waffenwechsel.

## Phase2 A:2/global4: später echter Gain, noch kein Useful-FIREbeleg

Sieben native Leben, sechs beobachtete Tode, letztes Leben rechtszensiert. Dort steigt owned3→67 erstmals bei Tick134.6536102294922 (Spawn116.10248565673828). Zehn darauf folgende gültige Proben besitzen die Usefulwaffe, bleiben aber currentKnife1; erst die letzte bei136.50372314453125 zeigt wanted7/current1. Das sind1.850113s zwischen erster Besitzprobe und letzter Probe, kein bestätigter abgeschlossener Wechsel. Alle655 Aliveproben dieses Slotphase haben current1 oder2; zehn sampled FIREbits, aber kein aktuelles Useful-FIREbit. Source-Firewünsche/-Counterzuwachs und normale Coltaktivität sind separat vorhanden. Kein Beweis, dass nach dem Beobachtungsende nicht geschossen worden wäre; die Gateanforderung ist im tatsächlichen Fenster dennoch nicht erfüllt.

## Reset-/Configbelege und verbleibende Lücke

Unveränderte V3 bestätigt alle drei getrennten Prozess-/Registry-/Welt-/Logoffset-Epochen und zwei Resetübergänge; Nativezeiten sind innerhalb jeder Epoche monoton. Das ist kein Nachweis eines stabilen Mapkontexts bei jedem einzelnen Pickeraufruf. Der neue begrenzte Scan von `botA-closed.log` findet genau drei ready1-CecilLoad-Zeilen181/2177/4254: RedStation,193Nodes, mapCRCff3776e0, navCRCe4571656. Beide Botgruppen haben je Phase die passenden CecilLoad-Belege; die Rollenzuordnung wird erneut aus tatsächlichen lokalen/globalen Sourcezeilen geprüft. Keine neue Navdatei-/Fixture-Leseprobe erforderlich.

Archivierte Profile: acht DEMON/tier3/duelist; Cohortconfig-Hashes A032748b1… und B9f2dfea8….2031 Sessionhealthzeilen (768/605/658) zeigen effektiven Spawnwert0 für Server/Bots/Original und innerhalb jeder Phase genau einen gemeinsamen Sessionhash. Die dritte native Phase reicht beobachtet von4.149997711 bis136.503723145; der bestehende Controller verlangt unverändert≥120 Wall- und Gamezeit. Die reine Beobachtung des Originalclients ersetzt keinen First-State-Schadensbeleg.

Diag0 liefert keine Candidate-/Selection-Custody oder DriverFinalzeile. Die Source-State-GOAL/HOP-Folgen und Knife/Colt-Wechsel sind archiviert, aber Item-Erreichbarkeit, Konkurrenzclaim, endgültige SafeMotion-/Arbitrationsentscheidung und tatsächliches Waffenfunktions-ACK fehlen für diese Episoden. Ein Supplyabbruch durch Combat, alter Claim-/Mapkontext oder Timerfehler ist damit nicht kausal belegt. Keine neue Diagnosefunktion oder Verhaltenskorrektur wurde eingebaut.

## Auditverfahren und eigener Readerfehler

Ein begrenzter Inventar-/Attempt-/Sourcepass mit Resolve+O_NOATIME+NOFOLLOW, keine Rawduplikate, kein alter Skulls-Replay. Der erste Auditreader schloss die `early-botA/B`-Hülle fälschlich aus; unveränderte V3 stoppte korrekt an fehlenden erfolgreichen Serials. Fehlreader und Fehlerliste bleiben privat erhalten. Im erhaltenen Offline-RAM wurden genau260 Proben aus dem separat erstmals gelesenen `early-inventory-raw.jsonl` ergänzt, Sourcecontroller schreibt denselben gebundenen Sample in beide Archive. Phase0 wurde nicht wiederholt, Phase1/2 im RAM fortgesetzt; Inventory und Sessionhealth wurden nie vollständig erneut gelesen. Die korrigierte Readerquelle behandelt frühe Hüllen direkt als ihren tatsächlichen gebundenen Gameplaygroup. Der alte Satz im ersten audit-receipt, frühe Reads seien nicht in kanonischen Leben enthalten, ist falsch und wird durch `final-facts-and-processing-erratum.json` ersetzt. Alle reproduzierten V3-Slotbefunde entsprechen exakt den archivierten Ergebnissen; das Native-FAIL bleibt unverändert.

Neue Quelle: `tools/audit_reset030_closed.py`; Reproduktion nur bei begründetem Bedarf mit `--output <frisches privates Verzeichnis>`. Wegen Root-Kompression muss zuvor die Originalarchivierung verlustfrei bereitgestellt sein; dieser Auftrag fordert keinen weiteren Replay. Private Belege unter `/srv/tse-reset030-closed-audit-evidence-20261115`, insgesamt unter3MiB. Keine Tests/Builds/Native-/Liveänderung. Rootrestore643Dateien/5Absenzen/beide NS/4normale Logs ist ein separat von Root geprüfter Nachweis und wurde nicht nachträglich ersetzt.

Beim ersten normalen Pythonimport entstanden acht gewöhnliche Cachedateien im eigenen deaktivierten Paket, keine geänderten Quellbytes oder Originalfixturedateien. Diese Metadatenabweichung ist Root gemeldet; nichts wurde gelöscht. Der reproduzierende Reader deaktiviert Bytecodewrites vor Imports und prüft die eingefrorenen Helferbytes sowie den qualifizierten Lebenshelper vor deren Verwendung. Diese Vorbereitungskorrektur wurde nicht zum Anlass eines weiteren Raw-Replays genommen. Der letzte Ergänzungsschritt verarbeitete ausschließlich vorhandenen RAM und den einmalig neu gelesenen geschlossenen BotA-Log; der Offline-Pythonprozess ist beendet und alle Handles sind frei.
