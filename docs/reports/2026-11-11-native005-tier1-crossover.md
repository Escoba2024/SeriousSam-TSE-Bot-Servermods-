# Native005: erster vollständiger Vergleich mit vertauschten Startpositionen

**Kein allgemeines A-PASS.** Der Flugabschluss ist nativ nachgewiesen, aber ein
sichtbarer Gegner unterbricht ihn weiterhin mit anschließendem Sprungpunkt-Zyklus.
Schnelle Waffenaufnahme und die vollständige Vergleichsserie bleiben offen.

Die bereinigten Einzelleben, Flugereignisse, Quellprüfsummen und Methoden stehen in
[der JSON-Auswertung](2026-11-11-native005-tier1-crossover.json). Private Rohlogs,
Spielernamen, Speicheradressen, Konfigurationen und Weltkoordinaten sind nicht
enthalten. Ausgewertet wurden die abgeschlossenen privaten Läufe
`arena005-checked-swap0-trial-1-210634` und
`arena005-checked-swap1-trial-1-211315`, jeweils Tier1.

## Tatsächlicher Startvergleich

Alle acht physischen Slots haben in beiden Läufen exakt dieselben CecilSpawn-XYZ
und dieselben ersten gültigen nativen XYZ. Jeder Slot startet mit Inventarmaske 3.
Die DLL-/Policy-Zuordnung wurde wirklich zwischen BotA und BotB getauscht;
der Kandidat hat SHA256
`35c950832d8ce4c48e0363ab33ba1a517d4a87e95bb320ca5aa686c59f2bfc35`.

Vor Freigabe waren alle neun Spieler ungespawnt. Die PRNG-Zustände waren gleich.
Innerhalb jedes Laufs beträgt die Streuung der acht serverseitigen Spawnuhren 0.
Die absoluten Spawnuhren unterscheiden sich allerdings: ungefähr 0,95 s bzw. 0,90 s;
die Pause lag bei 0,75 s bzw. 0,70 s. Damit sind Startorte und gemeinsamer Start innerhalb
jedes Laufs belegt, keine identischen absoluten Uhren zwischen den Läufen.
Ein anfänglich transienter Spawnwert 0 bei bereits positiver Gesundheit wurde aus
der gültigen Spawnuhrenmessung ausgeschlossen. Die Speicherlesungen sind nicht atomar.

## Alle Leben und Inventaraufnahmen

Fernkampfbesitz bedeutet `owned & 0x3df8 != 0`. Alle Erstaufnahmen sind durch
CecilPickup belegt. Das misst Inventarbesitz, nicht zusätzlich die aktuelle
Munition oder eine abgeschlossene Waffenwechselanimation. Median und Maximum
beziehen sich ausschließlich auf erfolgreiche Aufnahmen; Todesfälle und
zensierte Leben dürfen bei einem Leistungsvergleich nicht verschwinden.

| Lauf / Policy | Leben | Aufnahme | Tod ohne Aufnahme | Fensterende ohne Aufnahme | Median / Maximum der Aufnahmen |
|---|---:|---:|---:|---:|---:|
| Swap0 / Alt048 |24|11|11|2|12,20 /22,20s|
| Swap0 / Neu005 |22|17|3|2|10,15 /63,00s|
| Swap1 / Neu005 |17|12|2|3|13,05 /50,60s|
| Swap1 / Alt048 |19|15|4|0|10,15 /43,55s|

Neu005 verliert Leben ohne Aufnahme nach 15,5/45,3/15,5 s im ersten und 4,45/11,4 s
im zweiten Lauf. Weitere Leben sind rechtszensiert bei mindestens 16,7/7,5 s bzw.
33,5/9,5/0,3s. Besonders lange erfolgreiche Aufnahmen:63,0/39,5/33,4s in Swap0
und 50,6s in Swap1. Diese Befunde verhindern eine Abnahme der schnellen Waffenaufnahme.

## Flugabschluss und verbleibender Fehler

Swap0 enthält acht Begin/End-Paare: zweimal `arrived`, sechsmal `context`, jeweils
0,05–1,10s, mit unveränderter Kante und Frist. Der stärkste Nachweis ist local2/gen11:
Bei Tick 4275 nimmt ein anderer Bot Laser267 auf; der betroffene Bot bleibt bei
Inventarmaske 3, beendet86→176 bei 4297 mit `arrived` und nimmt bei 4412 eine andere
Fernkampfwaffe auf. In den folgenden verfügbaren 30 s-Stichproben erscheint keine
neue source−1/hop86-Akquisition. Dies ist ein begrenzter positiver Nachweis.

Swap1 enthält zwei weitere Paare, beide `context`. Beim relevanten Fehlerfall
local2/gen7 verschwindet Laser267 bei 3772 während84→86. Die Frist bleibt 204,955 s.
Bei 3773 wechselt das Kampfziel von keinem Ziel zu einem neu gewählten Spieler;
bei 3774 endet der Flugabschluss. Danach sind sechs source−1/hop86-Akquisitionen,
wiederholte vertikale Bewegung am Sprungpunkt sowie neutrale `floor=0`-Aktionen
belegt. Der Bot verlässt den Bereich später über84→93 und erhält erst bei 4634
seine erste Fernkampfwaffe:50,6s nach Spawn 3622.

Die notwendige falsche Bedingung lässt sich aus Log und Kandidatenquellcode ableiten:
`ChooseCecilTarget` kann nach target−1 einen neuen Spieler nur über `Selectable`
mit frischer Sicht wählen. Beim noch gültigen Flugabschluss ist `goalEntity=0`;
USE und wichtige Interaktion sind ausgeschlossen. Der Driver gewährt bei diesem
sichtbaren Gegner deshalb keine NAV-Bewegungszuständigkeit. `BotCecilSafeMotion`
löscht `flightAccepted` und kann es ohne diese Zuständigkeit nicht erneuern.
Im nächsten Tick scheitert folglich `BotCecilFlightFresh` an `flightAccepted>=0`.
Dies ist eine quellcodegestützte Ableitung, kein direkt protokollierter Feldwert.
Der exakte Physikzustand und weitere eventuell falsche Bedingungen bei 3774 sind
nicht geloggt. Node84 hat Flags10, Node86 und176 haben Flags0. Der Abbruch erfolgt
also noch auf84→86; ein fehlendes JUMP-Flag des Folgeschritts erklärt ihn nicht.

## Frags, Todesursachen und beobachtete Gesundheit

Letzte minus erste gültige Statusabfrage: Swap0 Alt 9/Neu 32 Frags,
Swap1 Neu 22/Alt 6. Die originalen Server-Tötungsmeldungen erklären diese Werte:
Neu erzielt über beide Läufe 59 Kills, davon 28 gegen die andere Policy, 21 gegen
die eigene Policy und 10 gegen den Observer. Alt erzielt 17, davon 6 gegen die
andere Policy, 6 gegen die eigene Policy und 5 gegen den Observer. Selbsttötungen
und weitere Todmeldungen reduzieren die jeweiligen Fragwerte. Fragmatch enthält
keine Teams; gleiche Policy ist lediglich eine Auswertungskategorie.

Summierte beobachtete serverseitige Gesundheitsabnahmen, bei negativer HP auf 0
begrenzt und nur innerhalb derselben Entity-/Spawnidentität: Swap0 Alt 2062,0 /
Neu 1691,0; Swap1 Neu 1385,59 /Alt 1635,74 HP. Diese nicht atomaren Stichproben
enthalten weder vollständige Schadensereignisse noch Rüstung und ordnen keinem
Angreifer Schaden zu. Daraus folgt insbesondere kein First-Tick-Schadensnachweis.

Beide Fenster liefen 240,089 s bzw.240,008s, mit je 100 gültigen Neun-Spieler-Abfragen,
0 BAD-Syncs,0 Disconnects und regulärem Ende aller vier Prozesse. Dies belegt
nur diese isolierten Fenster. Eine vollständige Serie von mindestens drei
Vergleichen, weitere Karten und die übrigen A-Gates bleiben offen.
