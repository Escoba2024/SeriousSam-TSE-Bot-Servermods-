# Native011: Wiederholung mit tatsächlichen Bouncer-Kontakten

**Beide gebundenen Anfahrten sind jetzt tatsächlich ausgeübt.** Drei vollständige
Actionepisoden zeigen die Unterdrückung des normalen UP vor der Ankunft an12:
zweimal8→12 und einmal11→12. Der Originalserver-Hook belegt vier reale Aufrufe
von Bouncer234, alle durch011-Kandidaten. Einer dieser vier Spieler erwirbt in
diesem Leben tatsächlich die Minigun. Das ist ein begrenzter Anfahrts- und
Kontaktbeleg, keine allgemeine Waffen-/Flug-/Milestone-A-Abnahme.

Privates Fenster `arena011hook2-checked-swap1-trial-1-000025`:
120,041233 Sekunden, Swap1/MITTEL/Diagnostik aktiv, unveränderter011-Kandidat
`4184df65d927054470ac37967711236deeec442c4dbf92a9428769458e3ed5db`.
Die tatsächlichen Attach-Zuordnungen sind erneut Kandidat/botA Locals0..3 →
globale Slots0/2/3/4 → Entities565..568; Alt048/botB → Slots5..8 → Entities569..572.
Vanilla563/Slot1 gehört keiner Botkohorte an. Das
[bereinigte JSON](2026-11-12-native011-repeat-window.json) enthält sämtliche
26 beobachteten Botleben, Quellzeilen, Originaluhren und Hashes.

## Action → Originalaufruf → Aufnahme

| Kandidat Local / Entity / Generation | Geprüfte Anfahrt | Raw-UP1 → Final-UP0 vor Ankunft | Ankunft12→34 | Exakt passender Post-Hook-Actiontick | Minigun im selben Leben |
|---|---|---|---|---|---|
| 2 / 567 / 5 | 8→12 | 874,878,882 | 887, Final-UP11 | 888 | nein |
| 3 / 568 / 6 | 8→12 | 1227,1232,1237 | 1240, Final-UP0 | 1240 | ja, Tick1329/owned67 |
| 1 / 566 / 6 | 11→12 | 1245,1249 | 1253, Final-UP11 | 1254 | nein |
| 0 / 565 / 6 | keine passende Actionepisode | nicht belegt | nicht exakt belegt | keiner | nein |

Die drei Episoden umfassen je120 Actionzeilen. Die jeweiligen positiven
UP-Anforderungen vor der Ankunft werden ausnahmslos auf Final-UP0 reduziert,
auch bei fehlender Supportreferenz und unverändertem Zustand0. Die Raw-Capture-
Werte und die Navigator-Ankunft bleiben erhalten. Ankunft auf die Folgekante
12→34 liegt außerhalb dieser Unterdrückung und gibt teilweise wieder UP11 aus.

Die Hookfolge ist567,568,566,565. Die ersten drei Hook-Positionen und
Post-Hook-Velocities stimmen komponentenweise innerhalb0,0001 mit den genannten
Actionticks überein. Für alle vier registrierten eigenen Entities ist die
Originaländerung von Velocity und Support protokolliert:

| Entity | Vorher-Support | Vy vorher → nach Originalaufruf |
|---|---:|---:|
| 567 | 193 | 0 → 73,184364 |
| 568 | 193 | 0 → 73,181099 |
| 566 | 193 | 0 → 72,391014 |
| 565 | 234 | −11,252808 → 63,671909 |

Support ist danach jeweils null. Entity565/Local0 hat kurz davor Source13/Hop12
am Tick1460 und danach keinen aktiven Item-Flug am1480. Ohne entsprechende
Actionepisode lässt sich dieser vierte Kontakt keiner erfolgreichen gebundenen
8→12-/11→12-Anfahrt zuschreiben. Seine Minigunaufnahme bleibt aus.

Bei568 ist die gesamte relevante Erfolgskette vorhanden: unterdrücktes UP,
Ankunft/echter234-Aufruf am1240, danach Minigunbesitz `owned=67` am1329, also
89 nominale Actionticks/4,45 s später. Die serverseitige Inventory-Lesung
bestätigt Minigunbesitz beim Game-Tick57,799404, Spawnclock37,949707.

**Offener Anschlussbefund:** Bei567 wird am Ankunftstick887 bereits12→34
gewählt und Final-UP11 ausgegeben. Der Hook setzt Vy am888 auf73,184364;
am889 protokolliert die Action bereits85,984360, eine zusätzliche Änderung
von+12,799996. Danach erreicht der Flug etwaY149 und weit entfernte Positionen;
es gibt keine Minigunaufnahme, und das Leben endet ohne Fernwaffe.
Bei566 ist trotz Final-UP11 am1253 der anschließende Verlauf anders:
Vy72,391014 am1254 und70,891014 am1255. Ein pauschaler Schluss, jeder UP-Puls
am Bouncer erhöhe die Launchgeschwindigkeit gleichartig, wäre damit falsch.
Die konkrete Ursache des unterschiedlichen Nach-Hook-Verlaufs ist noch nicht
vollständig nachgewiesen; dieser Bericht schlägt keine pauschale Radius- oder
Sprungänderung vor.

## Waffen, Leben und Frags

| Messgröße | Kandidat011 | Alt048 |
|---|---:|---:|
| Beobachtete Leben | 13 | 13 |
| Mit beobachtetem Tod beendet | 10 | 9 |
| Rechtszensiert am Fensterende | 3 | 4 |
| Mit Fernwaffenbesitz `owned & 0x3df8` | 8 | 10 |
| Beendet ohne Fernwaffe | 3 | 1 |
| Zensiert ohne Fernwaffe | 2 | 2 |
| Leben mit Minigun-Bit64 | 1 | 0 |
| Erfolgsfälle: Median erste Aufnahme | 11,975 s | 9,625 s |
| Erfolgsfälle: maximale erste Aufnahme | 62,90 s | 18,60 s |
| Query-Frags: Beginn → letzte Query | 0 → 7 | 0 → 6 |

Der Kandidat hat somit keinen allgemeinen Rapid-Weapon-Nachweis. Insbesondere
567/Generation5 endet nach etwa53,95 s ohne Fernwaffe trotz tatsächlichem
Bouncerkontakt;567/Generation6 nach13,75 s und565/Generation7 nach20,95 s
bleiben ebenfalls ohne Fernwaffe. Local1/566/Generation6 braucht62,90 nominale
Sekunden bis zur ersten solchen Waffe (Sniper, Tick2024), obwohl der234-Aufruf
bereits am1254 nachgewiesen ist. Doppelcolt zählt nicht zur Fernwaffenmaske.
Alle fehlgeschlagenen und rechtszensierten Leben bleiben im Nenner.

Zwei begrenzte Flugabschlüsse sind protokolliert: Local2/567/Generation5
84→86, Tick558→563, `arrived`, unveränderte Deadline45,869; sowie
Local1/566/Generation6 12→34, Tick1329→1344, `context`, unveränderte
Deadline83,300. Der zweite Beginn fällt mit der Minigunaufnahme des anderen
Spielers568 zusammen. Kein Kandidaten-GoalEnd `timeout` erscheint im Fenster;
048 hat fünf gewöhnliche Weapon0-Itemtimeouts nach jeweils12 nominalen Sekunden.
Der konkrete Kontextabbruch am1344 wird durch den Endgrund allein nicht erklärt.

## Grenzen und finale Integrität

Alle vier Rollen normal geschlossen, Fehlerliste leer, keine Sync-BADs oder
Sync-Disconnects. Die vier nach Close archivierten Rollenlogs wurden erneut
gegen ihre berichteten SHA256/Größen geprüft und auf Fehler durchsucht.
Hook:39 Gesamtaufrufe,4 passende234,35 andere Pads,0 unbekannte Spieler,
0 Faults und0 Drops; alle vier passenden Records erhalten. Die tatsächliche
Listenerüberdeckung umfasst das gesamte120039,100-ms-Messfenster; Detach und
vollständige Originalbody-Wiederherstellung sind bestätigt.

Inventory ist wiederholt gelesen, nicht atomar. Pickup-Driver-Ticks und
Originalserver-Spawnuhren sind getrennte Zeitbasen. Keine First-State-Damage-
Aussage, kein schadensursächlicher Nachweis aus Frags und keine Stunden-/Release-
Abnahme. Der Lauf ist ein instrumentierter Diagnosevergleich mit048, kein
angerechneter öffentlicher7fc-Vergleich. Das erste011-Fenster ohne Anfahrtsbeleg
bleibt [separat dokumentiert](2026-11-12-native011-first-window.md).

Private Reproduktion: zuerst `repeat_enrich.py`, dann `repeat_actions.py` unter
`/srv/tse-nav-011-review-20261112/`; Skripthashes und Eingabedateihashes stehen
im JSON. Die Auswertung prüft alle Lebensnenner gegen Spawn-/Death-/Pickup-
Logs, beide Kohortenzuordnungen, alle drei UP-Episoden und die exakte
Position-/Velocitykorrelation der ersten drei Hook-Records. Keine Runtimeänderung.
