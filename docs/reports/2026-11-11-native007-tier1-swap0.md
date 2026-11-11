# Native007: erster abgeschlossener Tier1-Vergleich

Der isolierte Red-Station-Lauf `arena007-checked-swap0-trial-1-214804` endet nach
240,097 Sekunden mit allen vier Prozessen normal geschlossen, 0 BAD,
0 Disconnects und 100/100 Statusabfragen mit neun Spielern. Neuer Kandidat:
`ce15842a36fee25d56fb1ffcb0f0a45878c254d9b0c5b95b129ce7708abf4b7f`;
Gegner ist Dev048, **nicht** der öffentliche Legacy7fc. Diagnostik war aktiv.
Das Controllerergebnis bleibt ausdrücklich begrenzt und unqualifiziert.

Vor Freigabe waren alle neun Spieler ungespawnt; die acht Bots haben innerhalb
dieses Fensters dieselbe ursprüngliche Server-Spawnuhr. Eine vertauschte
007-Gegenprobe liegt hier noch nicht vor.

| Kohorte | Alle Leben | Fernkampfwaffe aufgenommen | Gestorben ohne | Am Ende ohne, rechtszensiert | Frags |
|---|---:|---:|---:|---:|---:|
| Alt048 | 34 | 23 | 8 | 3 | +12 |
| Neu007 | 19 | 13 | 5 | 1 | +37 |

Maske `0x3df8` schließt Colt, Double-Colt und Chainsaw aus. Sämtliche
Erstaufnahmen sind durch `CecilPickup` belegt. Der unabhängige originale
Server-Inventarreader bestätigt exakt dieselben 53 Leben und 23/13 Erwerbe:
4371 gültige Gruppenmessungen, 81 als verändert verworfene Messungen.
Lesekosten insgesamt 17,161 Sekunden, maximal 12,90 ms je Gruppenversuch;
keine daraus abgeleitete uninstrumentierte Performance-Abnahme.

Clienttick-Differenz mal 0,05 ist nicht immer identisch mit vergangener nativer
Serverzeit. Die JSON-Datei enthält beide getrennt; native Zeiten sind der
Zeitpunkt der ersten beobachteten Aufnahme und können diese verspätet erfassen.
Unter erfolgreichen Leben liegt der native Median bei alt 11,30 s und neu
7,05 s, das Maximum bei alt 31,45 s und neu 58,10 s. Diese Kennwerte schließen
fehlgeschlagene und zensierte Leben aus; die Tabelle enthält deren volle Nenner.

Die vier neuen Erstleben erhalten eine Fernkampfwaffe nach beobachteten nativen
3,20/2,85/2,35/9,95 s. Später bleiben drei erfolgreiche neue Leben lange ohne:
42,50/58,10/36,00 s. Neu local3/gen8 ist am Ende seit mindestens **83,40 s** ohne
Fernkampfwaffe. Besitz allein beweist weder Munitionsbereitschaft noch einen
Schuss oder Schaden. Erste Beobachtungen einer ausgewählten Fernkampfwaffe mit
nativem `has_ammo` stehen deshalb separat in JSON.

Die Frags stammen aus erster bis letzter Query, zuletzt bei 238,725 s. Die
Servermeldungen zählen neu 37 Kills: 23 gegen alte Bots, elf gegen dieselbe
Kohorte und drei gegen den Observer. Alt zählt 14 Kills, einen Selbstkill und
einen nicht zugeordneten „passed away“-Tod; das entspricht +12. Kohorten sind
Analysekategorien, keine Teams. Beobachtete HP-Abnahmen sind keine vollständige
Schadens-/Rüstungsbilanz und keine Angreiferzuordnung.

## Gezielte Fixbelege und verbleibende Grenzen

**Connector:** 28 protokollierte Entscheidungen, darunter sieben tatsächliche
Treffer hinter dem Segmentende am Minigun-Anker34: Länge 1,258371,
Trefferdistanz 1,309612, `hit=373`, `render=4`, `polygon=8192`, jeweils
`valid=1 clear=1`. Damit ist der konkrete zuvor falsch verworfene Treffer jetzt
als frei beobachtet. Es gibt keinen nichtleeren Within-Segment-Treffer in diesen
28 Zeilen; dessen native Blockierung wurde hier nicht eigens ausgeübt.

**Flugabschluss:** genau ein Ereignis, neu local0/gen9: tick4717 beginnt
86→176 mit unveränderter Frist245,048; tick4719 endet mit `arrived`.
Bei Beginn erfolgen eigene Laseraufnahme und neue Gegnerwahl, zuvor war das
Combat-Ziel leer. Tick4720 zeigt sichtbaren Gegner und nach Abschluss NAV0.
Die sechs verfügbaren Folgesamples über etwa fünf weitere Clienttick-Sekunden
zeigen keine erneute Node86-Akquisition. Es gibt während der zwei Abschlussticks
keine eigene `CecilState`-Zeile; einzelne finale NAV-Ausgaben sind daher nicht
direkt protokolliert. Belegt ist gültige Fortsetzung bis Ankunft bei sichtbarem
Gegner am Beginn, **nicht** Konkurrentenverlust oder ein erst späterer
Sichtwechsel. Die bereits erfolgte eigene Aufnahme wurde nicht durch den
Flugabschluss verursacht.

**Weitere Route offen:** local3/gen7 wählt bei541 als einziges zulässiges Ziel
Minigun243. Connector frei, aber wiederholte44→43-Versuche und später12→34
führen bis Timeout1328 nicht zur Aufnahme; erst Cannon311 bei1390. Das lange
local0/gen7-Leben enthält ebenfalls Minigun-Timeout3064 und danach Snipererwerb.
Das letzte local3/gen8-Leben verliert Sniper401 an einen anderen Erwerber,
lässt Minigun243 auslaufen, verliert Laser267 und verfolgt schließlich248.
Dies sind konkrete weitere Navigations-/Erwerbsbefunde, keine Begründung für
ungeprüfte Frist-, Physik- oder Topologieänderungen.

[Sanitisierte vollständige Daten](2026-11-11-native007-tier1-swap0.json) enthalten
alle Leben, Zensierungen, Einzelereignisse und SHA256 der privaten Quellen.
Schnelle Waffenaufnahme, drei vollständige Gegenproben, First-Tick-Schaden und
Gesamtabnahme A bleiben offen. Kein allgemeines A-PASS.
