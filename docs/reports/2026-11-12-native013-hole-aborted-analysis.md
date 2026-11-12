# Native013 Hole: abgebrochenes Funktionsfenster

Das Fenster `a4-013-hole-20261112-020110` bleibt **FAIL**: Die Host-CPU überschritt mit 79,856 % die Grenze von 75 %. Die letzte Inventarprobe liegt bei 394,592 s; angefordert waren 600 s. Daraus folgt weder eine Gameplay-/Syncursache noch eine 600-s-Kartenabnahme. Alle vier Rollen schlossen normal, die nach Close archivierten Logs wurden akzeptiert und die ursprünglichen Dateien vollständig restauriert. `active-evidence.json` fehlt beim Abort; die Auswertung benutzt die erhaltenen Inventar-, State-, Ereignis- und Abschlussbelege.

Alle acht Bots verwendeten Kandidat013 `3a8d84c9…a81f93`, tatsächlich migriertes Profil DEMON/tier3. BotA belegt Slots 0/2/3/4, BotB 5/6/7/8; Vanilla ist Slot1. Beide Clientlogs bestätigen Hole, 139 Knoten, WorldCRC `582bd040`, NavCRC `d7cac057`. Bereinigte Nenner, Einzel-Leben, Flüssigkeitsepisoden und Abschluss-Hashes stehen in der [JSON-Auswertung](2026-11-12-native013-hole-aborted-analysis.json). Private Rohdaten bleiben außerhalb des Repository.

## Lebens- und Waffennenner

| Kohorte | Lebend beobachtete Leben | Beobachteter Tod / rechtszensiert | Nützlicher Besitz / aktuelle Waffe / Feueranforderung | Tod / zensiert ohne nützlichen Besitz |
|---|---:|---:|---:|---:|
| BotA | 61 | 57 / 4 | 44 / 42 / 42 | 17 / 0 |
| BotB | 66 | 62 / 4 | 50 / 49 / 49 | 14 / 2 |
| Gesamt | 127 | 119 / 8 | 94 / 91 / 91 | 31 / 2 |

Weitere drei positive Spawnclock-Epochen der Slots 0/2/5 enthalten ausschließlich nichtpositive HP und werden separat erhalten: insgesamt 130 beobachtete positive Epochen, davon 127 mit wenigstens einer lebenden Probe. Sie werden weder als erfolgreiches Leben noch als nachgewiesener Nichtspawn gewertet. Drei spätere Cleanup-Spawns in den geschlossenen Clientlogs liegen außerhalb der Inventarabdeckung.

Nützlich bedeutet Besitzmaske `0x3df8`; Double Colt und Nahkampf zählen nicht. Feueranforderung bei passender aktueller besessener Waffe beweist weder Treffer noch Schützenattribution. Unter den 94 erfolgreichen Erwerbsleben beträgt der Median 2,400 s, das Maximum 38,750 s. Diese erfolgsbedingten Werte ersetzen die 33 fehlgeschlagenen oder zensierten Erwerbe nicht. 9139 Inventarproben waren gültig, 311 zerrissene Proben wurden verworfen; maximale beobachtete Lücke 0,245 s. Die Messung bleibt nicht atomar.

## Passive Transitabbrüche und anschließender Erwerb

Drei `ItemTransitEnd`-Ereignisse belegen den begrenzten Abbruch eines Itemversuchs. Sie beweisen keine allgemeine Befreiung aus derselben Kante:

- BotA local1/entity708/generation13: Kante 0→1, Item688 bei Tick4470 nach genau 10 s ohne Hopfortschritt abgebrochen (botA-closed.log:4105). Tick4471 wählt Item673; auch dessen Route benutzt zunächst 0→1. Nach dessen Verlust folgt Minigun418, erneut 0→1, erneut Abbruch nach 10 s bei4817 (Zeile4392). Danach DoubleShotgun442, später Flamethrower661; tatsächlicher Pickup bei4946 (Zeile4502, Besitz3→131). Native Erwerbszeit 34,652 s nach Spawn, nützliche aktuelle Waffe erst60,651 s, Feueranforderung60,851 s; Tod nach62,551 s. Dies ist ein erfolgreicher später Erwerb mit langem unbewaffnetem Vorlauf, kein schneller Beschaffungsnachweis. Die Gründe der späteren Waffenwahl sind hier nicht isoliert.
- BotB local3/entity714/generation7: Kante51→50, Item419 bei1077 nach10 s abgebrochen (botB-closed.log:1141). Nachfolgende Auswahl673,688,450; bis zum Tod nach39,649 s kein nützlicher Besitz.

Bei BotA local1/generation13 liegen 37 periodische States mit 0→1 zwischen4260 und5220 (48 s), verteilt über wechselnde Ziele und später auch waffenbesitzende Bewegung. Das ist kein Beleg eines 48 s unverändert stehenden einzelnen Versuchs. Weitere wiederkehrende 0→1-Strecken enthalten Patrol-/Important-Ziele ohne ItemEntity; der Itemwatchdog ist dafür kein allgemeiner Patrolnachweis. Keine neue globale Timeout- oder Bewegungsregel wird aus diesen Daten abgeleitet.

## Flüssigkeitszustände: Ausstieg und offener langer Verlauf

Originalzustände sind 0 STAND, 1 CROUCH, 2 SWIM, 3 DIVE, 4 FALL. Das geloggte `floor` ist dagegen das SafeMotion-Ergebnis (0/1/2), keine Boden- oder Flüssigkeitsklasse. Aufeinanderfolgende beobachtete SWIM/DIVE-States derselben Lebensgeneration bilden 46 Episoden: 30 enden mit einem beobachteten STAND/CROUCH desselben Lebens, fünf mit FALL, zehn mit Tod vor beobachtetem Ausstieg, eine ist rechtszensiert. Abgetasteter Zustandswechsel beweist keine dauerhafte trockene Position.

Der längste Verlauf betrifft BotB local2/entity713/generation8: 36 DIVE-States von Tick880 bis1580, also35 s (botB-closed.log:1020–1558), danach Tod bei1600 (1593/1595). HP bleiben in diesen States20 und fallen beim Tod auf−330. Eine konkrete Todesursache, insbesondere Ertrinken, ist nicht belegt. Nützlicher Napalmbesitz besteht bereits0,600 s nach Spawn, aktuelle Waffe1,100 s, erste nützliche Feueranforderung26,350 s.

Der Verlauf ist kein durchgehender Pitch-/Leveling-Lock: 22/36 States haben NAV-Besitz, 13/36 `level_swim=1`. Ticks880–980 führen mit UP−0,21…−0,29 unter Healthziel460 tiefer (Y23,148→16,983);1000–1080 liegt UP+0,23…+0,30 vor.1120–1300 folgen NAV-Zielwechsel und UP bis+0,99.1320–1540 ist überwiegend sichtbarer Kampf mit NAV0/UP0; Schusszähler63→192.1560 hat NAV1/UP+0,02,1580 wieder sichtbaren Kampf NAV0/UP0 und `level_swim=1`, mit endlichem Blick-/Kompositionspitch. Die Schwerkraft bleibt(0,−1,0); eine konkrete Colliderklasse oder fehlerhafte Rayantwort ist aus diesen Logs nicht belegt.

Ein Gegenbeispiel ist BotB local3/entity714/generation8: DIVE1340–1620 über14 s, dann STAND1640 desselben Lebens; davor bereits Napalmbesitz und Feueranforderung. Das belegt einen beobachteten Ausstieg unter derselben Implementierung, ohne den35-s-Verlauf zu erklären oder alle Flüssigkeitsfälle zu qualifizieren.

## Offene Grenzen

Kein Mapreset, keine 600-s-Abnahme, keine vollständige Erstzustands- oder Schadensattribution. CPU-Abbruch bleibt separat vom beobachteten Erwerbs-/Navigationsverhalten. Die nächste Ursachenprüfung sollte die wiederkehrende 0→1-Routenwahl und den langen DIVE-Verlauf mit tatsächlicher Bewegungsbesitz-/Zielchronologie unterscheiden; pauschales Entfernen von Sicherheit, Pitchregeln oder Radien ist durch dieses Fenster nicht gerechtfertigt.
