# Kandidat013: native Flugfortsetzung und vollständige Lebensnenner

**Die neue versiegelte Fortsetzung wurde einmal nativ ausgeübt; eine erfolgreiche Ankunft ist damit nicht bewiesen.** In beiden120-s-Fenstern bleiben lange Leben ohne nützlichen Waffenbesitz. Keine A3-/A4-Gesamtfreigabe und kein Vergleich gegen die öffentliche7fc-Baseline.

Private Quellfenster: `arena013brush3p-i0-swap1-trial-1-015034` (120.098864 s) und `arena013brush3p-i1-swap1-trial-1-015357` (120.100496 s). Kandidat013 `3a8d84c9c04e4839ee08d5d8ec879c37f25265df267c03e966ec869754a81f93`, Quelle `5ce974c296240be4ece76386654ecd7e666d1aa4`; Gegenkohorte048 `ec820d0461313c41fec2b477f57109310d3c71a77b4423955ac69f3807566530`. Tatsächliche Attach-Zuordnung beider Fenster: KandidatbotA locals0–3 auf Slots0/2/3/4, IDs565–568;048botB auf5/6/7/8, IDs569–572; eigener Vanilla Slot1. Keine Zuordnung aus Gruppennamen angenommen.

[JSON-Beleg](2026-11-12-native013-flight-control-analysis.json) enthält alle56 beobachteten Botleben, Lebensuhr/Generation, Tod/Zensierung, Erwerb/aktuelle Waffe/Feueranforderung, Quellzeilen und Hashs, tatsächliche Slotzuordnung, Frags, Flugereignisse und Ressourcen. Rohrecords, Adressen und Prozessidentitäten bleiben privat.

## Vollständige Nenner

| Fenster/Kohorte | Leben: tot + zensiert | Nützlicher Besitz / aktuelle Waffe / Feueranforderung | Ohne Besitz: tot + zensiert | Erwerbsmedian / Maximum nur erfolgreicher Leben | Minigun-Leben | Fragdelta |
|---|---:|---:|---:|---:|---:|---:|
| i0 Kandidat013 |18:14+4|12/12/8|4+2|11.125 /30.550 s|1|+6 |
| i0 Vergleich048 |13:9+4|6/6/5|4+3|6.200 /45.651 s|0|+16 |
| i1 Kandidat013 |14:10+4|8/7/6|5+1|9.375 /19.050 s|1|+10 |
| i1 Vergleich048 |11:7+4|9/9/5|1+1|10.850 /14.201 s|0|+6 |

Nützliche Waffenmaske `0x3df8` schließt DoubleColt und Nahkampf aus. Feueranforderung erfordert beobachteten Besitz und eine passende tatsächlich aktuelle Waffe; sie beweist weder abgegebenes Projektil noch Treffer oder Schützenattribution. Erfolgsmediane lassen erfolglose Leben aus und dürfen deshalb nicht allein zum Vergleich dienen. Query-Endpunkte liegen bei119.344 beziehungsweise119.200 s. Die zwei Fenster unterscheiden sich im tatsächlichen Spielverlauf; keine kausale Effektgröße aus den Fragdeltas.

Längste Kandidatenfehler: i0 local0/gen6 stirbt nach49.151 s ohne nützlichen Erwerb; local0/gen7 endet nach39.252 s unbewaffnet zensiert. i1 local3/gen6 stirbt nach56.949 s ohne irgendeinen Pickup; local2/gen9 nach38.752 s ohne nützliche Waffe. Auch die kurzen erfolglosen Leben bleiben im Nenner. Maximale beobachtete1-m-Residenz2.200/2.100 s beim Kandidaten beweist keine Freiheit von bewegten Routenschleifen.

## Neue Fortsetzung: positiv ausgeübt, Flugausgang weiterhin verfehlt

In i1 nimmt Kandidatlocal2/entity567/gen7 bei Tick599 Laser267 auf (owned3→2051, botA.log:629); dessen eigenes86→176-Finish endet601 `arrived`. Gleichzeitig verliert local3/entity568/gen6 dasselbe Item (635), ohne Erwerb. Der bereits akzeptierte84→86-Flug beginnt599 zu enden (636), wird646 exakt einmal auf86→176 fortgesetzt (697) und endet664 `context` (711). Alle drei Marker behalten **Deadline48.834**. Bis zum Ende erscheint kein neues Itemziel; erst665 folgt Health358 (712). Dies belegt den vorgesehenen begrenzten Zustandsübergang, keine neue Item-/Fristautorität.

Dichte serverseitige Inventarproben zeigen die Grenze:

| Inventarzeile | Serverclock | Position XYZ | vertikale Translation |
|---:|---:|---|---:|
|571|20.499973|(1.073435,35.547119,12.013534)|+36.375 |
|574|20.649971|(1.027171,40.553371,11.807956)|+31.875 |
|583|20.999966|(−.358717,49.609619,11.854935)|+21.375 |
|601|21.749954|(−.358717,56.640869,11.854935)|−1.125 |
|625|22.749939|(−.358717,39.765869,11.854935)|−31.125 |
|628|22.899937|(.142030,34.647118,11.861542)|−35.625 |
|642|23.499928|(−6.485388,7.422103,12.043379)|−53.625 |
|645|23.599926|(−7.567216,1.834599,12.034890)|−56.625 |
|650|23.849922|(−7.760668,−.032817,11.797603)|+14.300 |

Die beiden ersten Proben liegen außerhalb des originalen Node86-Radius1, dessen Zentrum(0,38,12) ist. Der genaue erste Höhenkreuzungsframe fehlt; daraus folgt keine Berechtigung zu einer Radiusänderung. Horizontale Translation wird oberhalb des Knotens null, dann fällt der Spieler. Der Continue bei Driver646 liegt im absteigenden Zeitintervall, nicht auf der ersten Steigphase. Schon Driver660/server23.499928 ist die Höhe7.422 weit unter dem geometrischen Ausgang176 auf37.25. **Driverzeit Tick/20, serverseitiger GameTick und Wallclock sind verschiedene Uhren.** Die Tabelle verbindet tatsächliche Positionsproben mit Logzuständen, nicht einen erfundenen synchronen Frame.

HP40, gleiche Lebensuhr und Nullreferenz bleiben in den aufgeführten Proben erhalten. Der genaue End664-Frame ist nicht erfasst. Ground-/PlayerStatewechsel ist angesichts der folgenden positiven Translation plausibel, aber die konkret fehlgeschlagene `FlightFresh`-Unterbedingung bleibt unbekannt. Tod und Fristablauf erklären diesen Fall nicht. Keine heuristische Korrektur wird daraus abgeleitet.

Originale JumpFromBouncer-Aufrufe für denselben Spieler und bekannte Brush136 sind als Record9 bei18.324870 s und Record12 bei23.340870 s relativ zum Messfenster erhalten; vertikale Translation wechselt jeweils−10.554→58.875 beziehungsweise−5.235→52.800. Das sind echte Funktionsaufrufe mit geprüften Argumenten, keine aus NAV-Flags abgeleitete Klassenbehauptung. Der zweite Aufruf liegt nach dem ersten Flug; die Fortsetzung hat wiederholten Kontakt und späteres Reakquirieren nicht allgemein gelöst. Das gesamte Leben endet ohne nützlichen Erwerb.

## Weitere Flug-/Erwerbsfälle und Zeitgrenzen

In i0 gibt es im Messlog acht Flugmarker: local3/gen6 86→176 bei592–594 `arrived` nach tatsächlichem Laser-Pickup; local2/gen7 dieselbe Kante1521–1524 ebenfalls nach Laser-Pickup; local2/gen6 12→34 bei1039–1041 `context` nach Minigun-Pickup; local0/gen6 84→95 bei1660–1670 `arrived` nach fremdbedingter Item-Unverfügbarkeit. **Kein Continue in i0.**

Die geschlossenen i0-Logs haben zwölf Marker: vier zusätzliche12→34-Marker bei2644–2714 liegen erst im Cleanup-Tail. Sie werden nicht den120-s-Lebens-/Erwerbsdaten zugeschlagen. Geschlossene Logs bleiben dennoch für Sync-/Crash-/Cleanup-Prüfung maßgeblich.

In i1 erreicht local1/gen7 tatsächlich Minigunbesitz bei1314, zunächst3→67; erste native Beobachtung nach19.050 s dieses Lebens. Der originale234-Aufruf ist Record21 bei50.340870 s, mit vertikaler Translation0→73.176788 und danach Minigunaufnahme. Das12→34-Finish1314–1316 endet `context`. Minigunbesitz und tatsächlicher Funktionsaufruf sind belegt; daraus folgt keine automatische Qualifikation aller Anflugvarianten. i0 local2/gen6 bekommt die Minigun nach30.550 s; i0 besitzt keine Hookdaten und deshalb keinen nachgewiesenen originalen234-Aufruf.

Der lange erfolglose i0-local0/gen6-Versuch durchläuft243→544→Health549→267→311→401. Die ersten fünf Ziele enden `unavailable`, das letzte mit Tod1779. Pickup1775 ergibt nur DoubleColtmask7. Kein Item-Timeout wird in diesem Leben gemeldet. Dies ist eine eigene konkrete Folgeursache für weitere Analyse tatsächlicher Auswahl-/Connector-/Routenbelege, kein Beweis, dass eine alternative Waffe währenddessen erreichbar war. i1 enthält einen Kandidaten-Timeout für Item310/local3 bei1958 sowie einen048-Timeout Item78/local0 bei2317.

## Vollständigkeit und Beobachtungskosten

Beide Resultate sind fehlerfrei, alle vier Rollen normal geschlossen; archivierte geschlossene Logs wurden anhand Hash/Bytes/Identität geprüft und auf Sync-/Crash-/InvalidAction-Fehler untersucht. i1:45 Gesamtaufrufe=45 passende=45 empfangene,44 innerhalb des eigentlichen Messfensters und einer75 ms davor. Argumentcounts73:9,129:21,136:10,234:1,274:3,517:1. Registry46, null unbekannte Spieler/Argumente, Faults, Drops oder Detachfehler;125000-ms-TTL,120098.339-ms-vollständige Fensterüberdeckung,123-Byte-Originalkörper restauriert. Alle45 zeigen eine Translationsänderung; das macht nicht jeden Aufruf zu einem erfolgreichen Navigationsflug.

| Messgröße | i0 | i1 |
|---|---:|---:|
| Server CPU-Zeit |4.16 s|4.58 s |
| Kandidat CPU-Zeit |4.41 s|4.17 s |
|048 CPU-Zeit |4.44 s|4.18 s |
| Vanilla CPU-Zeit |75.95 s|74.77 s |
| Inventar gültig / verworfene Änderung |3022/86|2935/71 |
| Inventar Lesezeit gesamt / Maximum |12.236897/.013698 s|12.470903/.013053 s |
| Hooksetup |entfällt|.305909 s |

RSS-Endpunkte und vollständige Usagewerte stehen im JSON. Der Server startet mit unterschiedlich großem RSS (51.09 versus105.87 MB); es handelt sich weder um Peakmessung noch um einen kausal isolierten Hookkostenvergleich. Unterschiedliche Spielverläufe und Vorfensterinput bleiben enthalten. Die sieben reinen Hookanalyse-Negativtests wurden erneut bestanden; sie qualifizieren nur die Analyse, nicht den nativen Kandidaten. JSON-Nenner und Zeilen wurden gegen die erhaltenen Rohdateien geprüft. Keine Runtime durch den Auswerter.
