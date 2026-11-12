# Native011: erstes abgeschlossenes Diagnosefenster

**Die Änderungen an 8→12 und 11→12 sind in diesem Fenster nicht nachgewiesen.**
Beim Kandidaten gibt es weder Approach-Actionzeilen noch periodische States mit
Source8/11/12 oder Hop12. Der passive Originalserver-Hook erfasste keinen Aufruf
für Bouncer234. Es gibt folglich keine tatsächliche Raw-UP/Final-UP-Kette für
diese beiden Kandidatenanfahrten auszuwerten und keinen Minigun-Erfolg.

Privates Artefakt: `arena011hook2-checked-swap1-trial-1-235412`,
120,027503 Sekunden, Swap1/MITTEL/Diagnostik aktiv. Kandidat011:
`4184df65d927054470ac37967711236deeec442c4dbf92a9428769458e3ed5db`.
Gegenkohorte048:
`ec820d0461313c41fec2b477f57109310d3c71a77b4423955ac69f3807566530`.
Server und Vanilla verwenden originales GameMP. Dies ist ein isolierter
Diagnoselauf; kein qualifizierter Release und kein angerechneter öffentlicher
A3-Vergleich. Das vollständige bereinigte Datenblatt mit Quellzeilen und Hashes
steht in [der JSON-Auswertung](2026-11-12-native011-first-window.json).

## Identitäten, Waffen und Lebensnenner

Die Zuordnung stammt aus den tatsächlichen Attach-Zeilen, nicht aus den
irreführenden Inventory-Gruppennamen `physicalA`/`physicalB`:

| DLL/Rolle | Local0 | Local1 | Local2 | Local3 |
|---|---|---|---|---|
| 011/botA: globaler Slot / Entity | 0 / 565 | 2 / 566 | 3 / 567 | 4 / 568 |
| 048/botB: globaler Slot / Entity | 5 / 569 | 6 / 570 | 7 / 571 | 8 / 572 |

Slot1/Entity563 ist Vanilla und gehört nicht zur Kandidatenkohorte. Alle
Inventory-Gruppen wurden anhand dieser tatsächlichen Slots zusammengeführt.
Spawn-/Death-/Pickup-Ereignisse der Fensterlogs wurden pro Local/Generation mit
den serverseitigen Inventory-Leben `(Entity, spawned_tick)` gegengeprüft.
Die Inventarlesungen sind doppelte gleiche Reads, keine atomaren Ereignisse.

| Messgröße | Kandidat011 | Alt048 |
|---|---:|---:|
| Beobachtete Botleben | 10 | 10 |
| Mit beobachtetem Tod beendet | 6 | 6 |
| Am Fensterende rechtszensiert | 4 | 4 |
| Leben mit erworbener Fernwaffe, Maske `0x3df8` | 7 | 8 |
| Beendet ohne solche Waffe | 3 | 1 |
| Zensiert ohne solche Waffe | 0 | 1 |
| Leben mit Minigun-Bit64 | 0 | 0 |
| Median nur erfolgreicher Pickup-Zeiten | 11,95 s | 8,175 s |
| Maximum nur erfolgreicher Pickup-Zeiten | 39,65 s | 33,15 s |
| Query-Frags, Beginn → letzte Query | 0 → 1 | 0 → 10 |

Die Maske schließt Colt, Doppelcolt und Chainsaw aus. Sie belegt Besitz, keine
ununterbrochene Munitionsverfügbarkeit. Die erfolgreichen Pickup-Zeiten sind
Differenzen der lokalen Driver-Ticks × 50 ms; das JSON enthält zusätzlich die
originalen Server-Spawnuhren und ersten Inventory-Nachweise. Beide Uhren dürfen
nicht als identische absolute Zeitbasis behandelt werden. Die erste
Inventory-Beobachtung liegt nach dem Erstspawn; es gibt keinen First-State-Beleg.

Die drei erfolglosen abgeschlossenen Kandidatenleben sind:

| Local / Entity / Generation | Spawn-/Death-Driver-Tick | Serverseitig beobachtete Lebensdauer |
|---|---|---:|
| 0 / 565 / 6 | 216 → 1166 | 47,55 s |
| 3 / 568 / 6 | 216 → 832 | 30,80 s |
| 2 / 567 / 7 | 1174 → 1426 | 12,60 s |

Alt048 Local1/570/Generation6 starb nach etwa6,00 s ohne Fernwaffe;
Local0/569/Generation8 blieb am Fensterende nach15,25 s ohne solche Waffe
rechtszensiert. Die Nenner enthalten diese Fehlschläge ausdrücklich. Die
Rapid-Weapon-Anforderung bleibt offen. Die letzte der59 gültigen Queries liegt
bei119,137419 s; ihre Frags sind keine vollständige Schadens- oder Killursachen-
Attribution. Aus Gesundheitsdifferenzen folgt hier keine First-Tick-Damage-Aussage.

## Tatsächliche Kanten- und Flugbelege

Die sichtbare 8→12-Anfahrt gehört zur **alten048**: botB Local2/Entity571/
Generation6, Tick1180, Source8/Hop12, Position(-42,721;28,428;63,075), UP0.
Ab Tick1220 bis zum letzten Fenster-State2440 verbleibt diese alte Navigation
in den periodischen States auf Source12/Hop34. Die Quelle8/11/12- bzw.
Hop12-Auswahl umfasst63 alte States, aber keine neuen Approach-Actionzeilen.
Bei dieser Baseline gibt es daher keinen exakten Arrival- oder Final-Jump-Tick.
Kein Pad234-Aufruf und keine Minigun-Aufnahme wurden nachgewiesen. Dies ist
kein Beleg für Wirksamkeit oder Versagen der nicht ausgeübten011-Anfahrtsregel.

Drei tatsächliche Kandidaten-Flugabschlüsse sind vorhanden:

| Local / Entity / Generation | Kante | Begin → Ende | Endegrund | Unveränderte ursprüngliche Deadline |
|---|---|---|---|---:|
| 0 / 565 / 6 | 84→86 | 613 → 654 | arrived | 49,096 |
| 3 / 568 / 6 | 84→86 | 613 → 633 | context | 48,052 |
| 2 / 567 / 8 | 86→176 | 1630 → 1633 | arrived | 93,100 |

Bei Local0 bleibt nach Verlust des Itemziels am Tick613 die NAV-Bewegung auch
mit sichtbarem Gegner am Tick620 erhalten. Trotzdem endet dieses gesamte Leben
später ohne Fernwaffe. Bei Local3 zeigen die States620/640 den Wechsel von
Flug-NAV ohne Support zu Kampfbewegung ohne Support; die konkrete am633
verworfene Kontextbedingung ist in diesen periodischen States nicht aufgelöst.
Das darf nicht ohne weitere Belege einer bestimmten Guardbedingung zugeschrieben
werden. Local3 stirbt ebenfalls ohne Fernwaffe.

Local2 nimmt beim Tick1630 Laser267 auf (`owned=2051`), beginnt danach den
begrenzten86→176-Abschluss und beendet ihn am1633 mit `arrived`. Am1640 sind
Laser als Current/Wanted12, sichtbarer Gegner, Support338 und normale
Kampfbewegung bei NAV0 protokolliert. Diese einzelne Kette ist belegt; sie ist
keine allgemeine Zusage für alle Flug-/Waffenziele. Bei keinem der drei Paare
wird die protokollierte Deadline verlängert; keines endet mit Deadlinegrund.

Drei andere Kandidaten-Itemziele enden mit normalem `timeout`: Entity293
(Tick885→1125),349 (1357→1597),287 (2174→2414), jeweils12 nominale Sekunden.
Alle haben Weapon0. Bei048 betrifft dies Entity358 (1926→2166), ebenfalls12 s.
Diese Zeitlimits sind keine Minigun-Flugzeitlimits.

## Abschließende Log- und Hookprüfung

Alle vier Rollen wurden normal geschlossen. Der Controller meldet keine
Fehler, keine Sync-BADs oder Sync-Disconnects. Die neuen `*-closed.log` wurden
nach dem Schließen archiviert; deren Größen und SHA256 wurden unabhängig mit
dem Ergebnis verglichen und die Fehlermuster erneut geprüft: keine Treffer.
BotA enthält nach dem Messfenster einen zusätzlichen Spawn und Tod; diese
Schließphase wurde in der Fehlerprüfung berücksichtigt, aber nicht in die
zehn beobachteten Gameplay-Leben eingerechnet.

Hook:33 Gesamtaufrufe, alle33 andere Pads,0 passende234-Aufrufe,0 unbekannte
Spieler,0 Drops,0 Faults. `frida-bouncer.jsonl` ist entsprechend leer. Die
beobachtete Listener-Laufzeit überdeckt das gesamte120025,032-ms-Messfenster;
Detach und Wiederherstellung des vollständigen Originalfunktionskörpers sind
bestätigt. Diese Abdeckung ist keine erfolgreiche Padnutzung.

Reproduzierbare private Auswertung: `python3
/srv/tse-nav-011-review-20261112/enrich.py`; beide Analyseskripthashes stehen im
JSON. Die Auswertung prüft unter anderem gleiche Lebenszahlen zwischen
CecilSpawn und Inventory, Tod-/Pickup-Konsistenz sowie vollständige
Post-Close-Dateihashes. Es wurden keine Prozesse oder Runtime-Dateien verändert.
