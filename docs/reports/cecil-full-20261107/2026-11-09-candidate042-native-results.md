# Normal042: Supply-Messwerte erfüllt, zwei Skulls-Stillstände bleiben

Normal042 ist nicht für den Rollout qualifiziert. Quelle `7a0a5c89cf069bde47fa82dcabf0bfc5232bb874`, Tree `ff11d698de322a56166edd6660bed98ac45862bb`, DLL `6eb4eb8043f45ce7b2f721886452bc6cf1f26aa6c24e3c760c6ac29ba89adf37`. Alle15 MSVC-Übersetzungseinheiten und der Link bestehen; [bereinigtes Buildmanifest](build042.json). Main hat den finalen zusammengeführten Stand mit770 SDK-ASan/UBSan-Prüfungen erneut geprüft. Unabhängige vollständige Quellreviews bestätigen die Änderung. Portable Prüfungen und Windows-x86-Build ergeben keine native Freigabe.

## Begrenzte Bewegungsänderung

Ein tatsächlich angenommener Ground-Stall prüft nun acht gravitationstangente Weltrichtungen einschließlich Vorwärtsrichtungen. Die physische Richtungsidentität bleibt trotz veränderter Zielausrichtung erhalten. Definitiv blockierte Richtungen werden übersprungen, unbekannte oder budgetbedingt verschobene Ergebnisse später erneut geprüft. Nach einem vollständigen erfolglosen Durchlauf darf ein neuer Durchlauf beginnen; kein dauerhaft gesättigtes Tried-Mask verhindert alle weiteren Versuche. Bei deaktiviertem Strafe existieren ausdrücklich nur die zwei körperbezogenen Vorwärts-/Rückwärtsrichtungen. Eine geänderte Schwerkraft bindet ausschließlich den Richtungsrahmen neu; der tatsächliche Positionsstillstand und Cooldown bleiben erhalten.

Jede neue oder fortgesetzte Richtung benötigt aktuelle Supportautorisierung und frische bestehende Wand-/Bodenstrahlen. Der0,3-Bewegungsbetrag,0,6s-Hold,1,6s-Cooldown,16-Raybudget, kurze NULL-Fußprüfung, allgemeine Neigungsgrenze, enge aktuelle Kontaktfläche, Original-NAV-Radien/Locks und feste Ziel-Fristen bleiben unverändert. Es wird keine physisch freie Richtung oder garantierte NAV-Rückkehr behauptet.

## Vollständiger Skulls-Lauf: FAIL

Acht Bots werden600,005982249s mit596 Statusabfragen beobachtet. Telemetrie deckt das volle Fenster ab, Szenario und Population bleiben korrekt, alle acht haben positive Scoreentwicklung, neue Monitor-/Sync-/CRC-/Fatalfehler werden nicht erkannt. Das unveränderte10s-Stillstandsgate ist dennoch verletzt:

| Slot | Maximaler unbegründeter Stillstand |
| --- | ---: |
| BotA:0 |36,321s |
| BotA:1 |5,033s |
| BotA:2 |10,083s |
| BotA:3 |6,045s |
| BotB:0 |1,007s |
| BotB:1 |3,024s |
| BotB:2 |5,042s |
| BotB:3 |7,054s |

BotA:0 steht am Ende im selben lebenden Kontext mit Anchor242, Goal/Hop-1 und neutralen finalen Achsen. Der originale Skulls-Knoten242 ist UNREACHABLE mit Radius2m, ohne ausgehende Verbindungen oder Next-Link. Der aktuelle Quellpfad akzeptiert diesen geometrischen Anchor, findet dort aber kein anderes erreichbares Ziel und kehrt neutral zurück; der Offgraph-Watchdog verlangt Anchor<0. Das ist ein eigener Navigationsübergang, keine Wiederholung der früheren erschöpften Fünfrichtungsmaske. BotA:2 zeigt getrennt10,083s bei der bereits bekannten NULL-/Seitenwandlage im bereits zuvor erfassten Kontaktbereich. Die vollständige unabhängige Kontext-/Ursachenprüfung wird getrennt fortgeführt; kein fehlender Boden wird als sicherer Kontakt ausgegeben.

Alle drei eigenen Spielprozesse schließen normal; Rohlogs und Zeitreihen sind erhalten. Main-FAIL-Verdict-SHA256 `1e17b41bf8d3a899730b111662f6c2796fcce33967dd61e111487851151c0048`. Keine weiteren042-Karten oder formalen3600/3600/7200s-Fenster wurden nach diesem Fehler gestartet.

Der neu exakt an042 gebundene private Feature-Indexer besteht16 reine Tests und liest erst nach normalem Cleanup die vollständigen frischen Logs. Er zählt39+23 gesundheitskorrelierte Todes-/Respawnfolgen, insgesamt62, unter derselben Entity und nächster Generation. Der Indexer begrenzt BotA auf die tatsächlich überwachten Ticks200–12180 und BotB auf20–12000. Ein weiterer BotA-Todesfall hat seine Gesundheitsprobe im Fenster, aber den Spawn erst im normalen Cleanup-Nachlauf und bleibt deshalb im Messfenster rechtszensiert; der vollständige Rohlogreview erkennt einschließlich dieses Nachlaufs63 Paare. Kein Nachlauf verlängert das Zeitgate. Das sind keine100 Todesfälle und keine vollständige Respawn-/Featurefreigabe. Er erkennt geordnete Waffenketten für Doppel-Colt/Rocket/Grenade, noch keine Flamer-/Cannon-Kette auf Skulls. Logs, Flags oder eine Escape-Meldung allein belegen keinen physisch erfolgreichen Wegpunktübergang.

## Versorgung v15

Alle zehn frischen Einzelbotfälle und alle elf zugehörigen Spielprozesse sind normal beendet. Der vollständige numerische Auditor erfasst589 korrekte Ein-Bot-Abfragen, zehn unterschiedliche Prozess-/Kernelstart-Kontexte und10/10 Erwerbsnachweise in der prospektiv festen ersten Zehnerzielmenge. Die zehn festen Initialleben benötigen8,35/3,25/2,65/2,45/5,00/3,95/3,15/3,95/9,90/10,15s bis zur ersten sinnvollen Waffenaufnahme: Median3,95s, Nearest-Rank-P9510,15s. Die15s-/30s-Grenzen bleiben unverändert.

Die tatsächliche Ziel-Entity544 ist Grenade9,248 Flamer11 und311 Cannon14. Main liest passende einzelne neue Besitzbits und denselben nativen Zielendtick im lebenden lokalen Kontext. `goal_picked=0` wird nicht zum Erfolg umgedeutet; kein ReceiveItem-Hook oder allgemeiner2,5m-Pickupradius wird behauptet. Alle späteren Zielstarts und zensierten Versuche bleiben erhalten. Mindestbeobachtung60s, Drain520s, die bereits native einmalige Relocation-Frist, feste Initialleben und vollständige normale Abschlussmetadaten bleiben unverändert. Main und unabhängiger vollständiger Rohreview bestätigen ausschließlich das begrenzte Supply-Gate. Privater Supply-Verdict-SHA256 `6550a9245438cb74ef3a48a3948e93f552cc03bd42e40a26d4ecde6c96d9995a`; unabhängiger Review `09d0d9f7f4f5594b081cc27c9f1570434c34527d2daa047b162187eb304d9bd4`. Von sämtlichen26 erhaltenen Starts sind25 korroboriert; Rang12 in Fall5 bleibt ein echter Grenade-Timeout und gehört nicht zur festen ersten Zehnerkohorte. Es gibt keine rechtszensierten Waffenziele. Bot-Exitstatus1 bleibt ausdrücklich erhalten. Gesamtstatus weiterhin `qualified=false`, Skulls FAIL.

## Getrennte041b-Diagnose abgeschlossen

Die ausschließlich diagnostische DLL `6ccee386a76fb60d8f8c58e1c11390fef301149cfe9cc5e45a541784e0f6b636` aus Quelle `af87dfb2480d03d1e2420da5c49eba21efd94f7f` verwendet eine zusätzliche begrenzte physische Abfrage innerhalb der tatsächlich nativen StepDn-Höhe1,5m. Der optionale Lauf endet nach705,389973s/625 Statusabfragen ausdrücklich administrativ. `observation_completed=false`/`KeyboardInterrupt()` und normaler Cleanup aller drei Prozesse bleiben erhalten; niemals ein bestandenes Zeitgate.

Bei einem tatsächlich reproduzierten NULL-Stillstand nahe der früheren Skulls-Fehlerstelle liefern23 gepaarte kurze Fußstrahlen und StepDn1,5m-Strahlen jeweils keinen Treffer. Das zeitweise native Standpolygon ist vertikal mit Support0; der tatsächliche Owner-Klassentyp wurde nicht geloggt. Eine allgemeine Vertiefung der kurzen Supportprüfung ist daraus nicht begründet. Später löst sichtbarer Kampf die Lage mit etwa8m Abstieg im selben Leben und anschließendem Tod; das ist kein autonomer Recovery-/NAV-Wirknachweis. Kompakter privater Diagnosebericht-SHA256 `cc22d7ef537e57685731a6c743a472e8b09f78efc42baa58019f4bc1a169b503`.

## Weiterhin offen

Native vollständige Waffen-/Sonderaktionen einschließlich USE-Effekt, Crouch/Jump/Teleport und Schwerkraft, alle fünf Karten, aktueller Original-Retail-Gameplaytest,3600/3600/7200s, gemessener CPU-/RSS-Vergleich, Rotation und kontrollierter Wiederanlauf bleiben offen. Frühere041-Retail-/Supply-Teilbelege qualifizieren042 nicht. Die Transfermatrix bleibt ausdrücklich039-Snapshot, historische FAILs bleiben erhalten. Alle sechs öffentlichen Instanzen sind am09.11.2026 um21:27:44UTC mit jeweils acht eigenen Bots und den bisherigen DLLs bestätigt; keine042-DLL ist öffentlich ausgerollt. Der autorisierte vollständige Rollout samt gemeinsamer900s-Flottenprüfung bleibt Aufgabe nach bestandener Kandidatenqualifikation.
