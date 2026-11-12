# Public012, MITTEL, Swap0: vollständig beobachtete Lebensverläufe

Das abgeschlossene Original-Retail-1.07-Fenster `arena012public-v4-checked-swap0-trial-1-003511` zeigt häufiger nützlichen Waffenbesitz beim Kandidaten, aber keinen Fragvorsprung. Es ist **ein begrenzt bestandenes Vergleichsfenster**, keine A3-, Karten-, Langzeit- oder Releasefreigabe. Dauer: 240,058 s. Der unveränderte Originalserver und Vanilla liefen mit acht eigenen Bots. Frida war in diesem Fenster nicht aktiv.

Die Zuordnung stammt erneut aus den tatsächlichen Attach-Zeilen: Legacy `botA`/7fc94a39, HumanAI0, lokale Spieler 0–3 → globale Slots **0, 2, 3, 4**, Entity-IDs 565–568. Kandidat `botB`/e0495577, HumanAI1/Supply1/MITTEL, lokale Spieler 0–3 → Slots **5–8**, IDs 569–572. Vanilla belegt Slot1. Die frühere inerte 048-Bootstrapinstanz wurde vor den gemessenen Kohorten geschlossen und gehört nicht zum Vergleich.

| Beobachtung | Legacy7fc | Kandidat012 |
|---|---:|---:|
| Leben mit mindestens einer lebenden Inventarprobe | 38 | 23 |
| Beobachteter Tod / am Fensterende zensiert | 34 / 4 | 19 / 4 |
| Nützlicher Waffenbesitz im Leben | 7 | 19 |
| Abgeschlossene Leben ohne solchen Besitz | 27 | 2 |
| Zensierte Leben ohne solchen Besitz | 4 | 2 |
| Nützliche Waffe tatsächlich als `current` beobachtet | 5 | 19 |
| Nützliche aktuelle/besessene Waffe mit `fire_requested` | 2 | 15 |
| Erstbesitz-Median, **nur erfolgreiche Leben** | 3,050 s | 9,800 s |
| Spätester Erstbesitz, nur erfolgreiche Leben | 40,202 s | 31,401 s |
| Letzter Query-Fragdelta | **+26** | **+20** |

Nützlich bedeutet exakt Besitzmaske `0x3df8`; Colt/Doppelcolt und Chainsaw zählen nicht. Die bedingten Mediane sind wegen der sehr unterschiedlichen Ausfallanteile kein Vergleich aller Lebenszeiten. Alle ersten lebenden Proben beginnen mit Besitz3. Die vier ersten Legacy-Leben endeten ohne nützliche Waffe; beim Kandidaten wurde Erstbesitz nach 3,400/3,850/2,300/10,350 s beobachtet. Minigunbesitz wurde in keiner der beiden Gruppen beobachtet. Der [JSON-Nachweis](2026-11-12-native-public012-swap0-analysis.json) enthält jedes Leben mit Entity, Spawnclock, Quellzeilen, Tod oder Zensierung, Erwerbs-, Current- und Fire-Request-Belegen.

Der letzte Query liegt bei 238,686 s, also vor Fensterende. Lokale Fragdeltas sind Legacy `[7,7,6,6]`, Kandidat `[6,2,5,7]`, Vanilla0. Drei Kandidatenslots zeigen mindestens eine Abnahme des Scores. Scoreänderungen werden nicht als vollständige Kill-/Suizidrekonstruktion ausgegeben. `fire_requested` und Cecils `shots` sind Eingabeanforderungen, keine gezählten Projektile, Treffer oder zugeordneten Schadensereignisse.

## Erwerb, Bewegung und verbleibende Fehler

Die Kandidatenlogs enthalten exakt 23 `CecilSpawn`- und 19 `CecilDeath`-Ereignisse. Chronologische Zuordnung pro lokalem Spieler stimmt mit allen nativen Leben überein; die Existenz des ersten nützlichen `CecilPickup` stimmt in jedem Leben mit dem Inventar überein. Legacy hat keine vergleichbaren Cecil-Lebensereignisse; dort bleibt das Originalserver-Inventar die Quelle.

Die beiden abgeschlossenen Kandidatenleben ohne nützliche Waffe sind local0/Leben4 (10,601 s) und local3/Leben4 (4,050 s). Die erfolglos zensierten Leben sind local0/Leben7 (3,850 s) und local3/Leben8 (11,051 s). Local1/Leben3 benötigt 31,401 s bis zum ersten nützlichen Besitz. Damit ist ein allgemeines Gate für schnellen Waffenerwerb nicht erfüllt.

Local1/Entity570/Generation8 lebt ab nativer Spawnclock104,052 s bis zum Fensterende, insgesamt 136,658 s beobachtet. Nützlicher Besitz erscheint nach 12,201 s, ein beobachteter Fire-Request mit nützlicher aktueller Waffe erst nach 126,758 s. Die Zustandszeilen zeigen große räumliche Bewegung, vielfach ohne sichtbares Ziel und mit Knife als aktueller Waffe; dies ist keine dauerhafte Standposition. Trotzdem bleibt Waffenziel245, Weapon9/Anchor12, von DriverTick2754 bis3654 erfolglos erhalten: **45 nominale Sekunden bis Timeout** (`botB.log`:2428,3264). Ein zweiter Versuch läuft4493–4733, weitere12 s (3893,4093). Insgesamt gibt es fünf protokollierte Goal-Timeouts; alle sind im JSON enthalten. Die genaue Ursache des erfolglosen Terminal-/Routenverlaufs ist damit noch nicht abschließend bestimmt.

Die 120 Approach-Zeilen betreffen dieselbe Generation8: Tick2751 erreicht Node8 und wählt Hop12. RawUP1 wird an2751/2754/2758/2763 zu FinalUP0; letzterer Zustand liegt bei `(-46,966,24,005,63,052)` auf Support193. Tick2764 meldet Radiusankunft an12 mit Velocity `(53,053,73,174,-77,274)` und anschließend hoher Flugkurve bis Y111,407. Das Ziel selbst liegt anNode12, daher bleibt `out_hop=12`; diese Episode ist kein Nachweis einer erfolgreichen12→34-Minigunroute. Ziel245 ist Weapon9, nicht Minigun. Es gibt in diesem Fenster keinen Hook234-Beleg. Quellzeilen2425–2666 erlauben eine konkrete Folgeanalyse, aber keine Behauptung eines gemessenen nativen Bounceraufrufs.

Drei `CecilFlightFinish`-Episoden auf86→176 enden mit `reason=context`: local1 771→773/Deadline49,100; local3 1658→1682/97,755; local3 2831→2837/151,531. Anfangs-/Enddeadline sind jeweils unverändert. Die angrenzenden Zustände zeigen Besitz2051; die zweite Episode fällt bis nahe Bodenniveau, die dritte zeigt danach176→95. Kein Ereignis meldet `arrived`; kein pauschaler Flugfix-PASS. Zustände vor/nach jedem Ereignis stehen im JSON.

Als beschreibende Bewegungsgröße wurde die längste Folge lebender Proben innerhalb1 m um die erste Position, ohne Probenlücke über0,5 s, berechnet: Legacy maximal15,251 s, Kandidat1,900 s. Das ist kein automatischer Stuck-Test: Routenschleifen, Fehlflüge und erfolgloser Erwerb können bei großer Bewegung bestehen. Die beobachteten Polylinien summieren sich auf3580,97 bzw.12742,47 Einheiten; Teleports und Abtastung begrenzen ihre Interpretation als tatsächlichen Laufweg.

## Start, Identität und Abschluss

Der vollständige gespeicherte Inventarstrom wurde unabhängig nochmals durch die eingefrorene Initial-Policy geführt. Raw-first, first-neutral und leeres Pending-Fehlerarchiv stimmen byteinhaltlich mit dem daraus rekonstruierten Ergebnis überein. Alle neun neutralen Positionen einschließlich Yaw entsprechen **exakt** der unveränderten Referenz SHA256`073f4d9a…`. Gemeinsame positive Spawnclock/GameTick:0,9000001549720764; HP100, Armor0, Owned3, Current/Wanted2, Velocity0, Support0, Buttons0, Render3, Physics`0x40000284`.

Nur Slot8 wird früher in Phase`0x40000287` erfasst: elapsed0,080056 s, Y12,107500; erste neutrale Probe elapsed0,117352 s, Y12,032500, exakt Referenz. Die rohe erste Probe bleibt erhalten. Es wird **kein erster Simulationszustand** behauptet. Die Initial-Policy wählt die erste neutrale Probe unabhängig von ihrer Position und verwirft beobachtete Zwischenabweichungen dauerhaft. Alle neun Proben und beide Phasen sind im JSON dokumentiert.

Beide Kohortenkonfigurationen wurden aus den archivierten kanonischen Quellen mit dem eingefrorenen Policycode erneut erzeugt und exakt verglichen. Alle Inventarproben tragen dieselbe Originalserver-Prozessidentität und dieselben Originalkomponentenhashs; die finalen Rollenidentitäten passen zu ihren tatsächlichen Launch-/Close-Receipts. Das eigene Normal-Close ist für alle vier Rollen mit je vier stabilen Identitätsprüfungen attestiert. Die vier archivierten `*-closed.log`-Dateien wurden unabhängig auf Länge/SHA und SYNCBAD, Syncdisconnect, CRC-Fehler, Crash, InvalidAction und Joinfehler geprüft: keine Treffer, keine finalen Fehlergründe. Die vollständigen Loghashs stehen im JSON. Dies ist eine Nachprüfung der erhaltenen Belege, kein erneuter Prozesszugriff.

## Messgrenzen

5898 gültige doppelt gelesene Inventarproben,126 wegen Veränderung verworfene Proben; die Reads bleiben nicht atomar. Gesamte Readerzeit24,923 s, maximale Einzelprobe10,365 ms; diese Summe ist keine kausale Overheadmessung. Gleiche native Ticks wurden für Bewegungs-/Verlustgrößen zusammengeführt, Lebensidentitäten nie vermischt. Erwerbszeiten sind erste beobachtete Besitzzeiten, nicht genaue Pickup-Ereignisse. Nicht beobachtete Zwischenaktionen oder extrem kurze Leben können nicht ausgeschlossen werden.

Summen positiver beobachteter HP-Abnahmen, auf0 begrenzt und ohne Spawnclock-Proben: Legacy3457,36/Kandidat2085,00; Armor-Abnahmen0/275. Dies sind beobachtete Zustandsverlust-Untergrenzen, **keine zugeordneten ausgeteilten Schadenssummen**, keine exakten Damage-Aufrufe und kein First-Tick-Schadensnachweis.

Die irreführend benannte `CecilState liquid`-Spalte enthält laut `BotDriver.cpp` tatsächlich `m_pstState`:0STAND,1CROUCH,2SWIM,3DIVE,4FALL. Ein Wert4 ist kein Wasser-/Gefahrenbeweis. Keine aus diesem Fenster abgeleitete Flüssigkeits- oder Hazards-Abnahme.

Reproduktion dieser reinen Dateianalyse: private Skripte `/srv/tse-nav-public012-review-20261112/{analyze,enrich,finalize}.py`; `python3 .../finalize.py`. Die Skripthashs und Eingabedateihashs stehen im JSON. Rohlogs, Prozessadressen, GUIDs, Konfigurationsinhalte und Retaildateien bleiben privat. Kein Runtime-Aufruf wurde für diese Auswertung ausgeführt.
