# Candidate013 DEMON: gekreuzter nativer Schadensvergleich

Die beiden abgeschlossenen 120-s-Fenster zeigen mehr nützlichen Waffenbesitz und insgesamt mehr Frags für Candidate013. Der erste Lauf bleibt bei der gesamten begrenzten HP-Schadenssumme ungünstiger. Diese zwei instrumentierten Fenster ergeben **keine A3-Gesamtfreigabe, Tierüberlegenheit oder Erstzustandsabnahme**. Alle 93 beobachteten Leben, einschließlich fehlgeschlagener und rechtszensierter Waffenaufnahmen, stehen im [bereinigten JSON](2026-11-12-native-public013-demon-damage-pair.json).

## Identität, Start und Abschluss

- Swap0: `arena013public-damage-checked-swap0-trial-3-033544`, 120.051825 s; Public7fc/HumanAI0 auf botA (Slots 0/2/3/4), Candidate013/DEMON auf botB (5/6/7/8).
- Swap1: `arena013public-damage-checked-swap1-trial-3-034421`, 120.105414 s; Candidate013 auf botA, Public7fc auf botB. Vanilla ist Slot 1. Die tatsächlichen Attach-/Entity-Zuordnungen wurden gegen Serverinventar und Schadensregistry geprüft.
- In beiden Läufen entsprechen alle neun **ersten phasenqualifizierten neutralen** Beobachtungen exakt derselben unveränderten Positionsreferenz. Raw-First-, Neutral- und Pending-Belege wurden erneut durch die unveränderte Initialpolicy abgespielt; keine Pendingfehler. Kanonische Kohortkonfigurationen wurden bytegenau reproduziert; vier tatsächliche DEMON-Profile pro Lauf haben dieselben lokalen Seeds.
- Beide Fenster: vier normale Prozessabschlüsse, unveränderte PID/Start-Identitäten bis Cleanup, vollständige Wiederherstellung, nach Close archivierte Logs mit geprüften SHA256/Bytezahlen und ohne Sync-/Crash-/InvalidAction-Befund. Vollständige Hookabdeckung, keine verlorenen/ungeklärten Opferaufrufe, keine verschachtelten oder fremden Threads; originale Getter-/Damage-Körper wiederhergestellt.
- Die vorangegangenen Initialphasen-FAILs `033230` und `033953` bleiben FAIL und sind ausgeschlossen. Swap1 verschiebt lediglich den bestehenden vollständig geprüften Trace-Drain hinter den Inventarbatch; Referenz, Qualifier und Hookregeln bleiben gleich. Daraus folgt keine nachträgliche Kausalerklärung für die verpassten Phasen.

## Vollständige Lebensnenner

Nützlich bedeutet Besitzmaske `0x3df8`, also ohne Colt/Double-Colt und Nahkampfwaffen. Besitz, tatsächlich ausgewählte Waffe und FIRE-Anforderung werden getrennt gezählt.

| Lauf / Kohorte | Leben | Tod / rechtszensiert | Nützlich besessen / ausgewählt / FIRE angefordert | Ohne Aufnahme gestorben / zensiert | Query-Fragdelta |
|---|---:|---:|---:|---:|---:|
| Swap0 Public | 27 | 24 / 3 | 5 / 3 / 0 | 20 / 2 | +18 |
| Swap0 Candidate | 18 | 14 / 4 | 13 / 12 / 11 | 5 / 0 | +19 |
| Swap1 Public | 28 | 24 / 4 | 3 / 0 / 0 | 21 / 4 | +8 |
| Swap1 Candidate | 18 | 14 / 4 | 13 / 13 / 13 | 3 / 2 | +25 |
| Paar Public | 55 | 48 / 7 | 8 / 3 / 0 | 41 / 6 | +26 |
| Paar Candidate | 36 | 28 / 8 | 26 / 25 / 24 | 8 / 2 | +44 |

Dazu kommen zwei Vanilla-Leben, beide ohne nützliche Waffe gestorben; keine reinen Leichenepochen. Alle Candidate-Spawn-, Todes- und nützlichen Pickup-Ereignisse stimmen pro tatsächlicher Entity/Generation mit den Inventarleben überein. Die erfolgreichen Aufnahmen des Kandidaten liegen im Paar bei Median 8.525 s, Maximum 22.601 s; dieser ausschließlich erfolgreiche Nenner verschweigt die zehn Leben ohne beobachtete Aufnahme nicht. Publics Erfolgsmedian 1.300 s betrifft nur acht von 55 Leben und ist daher kein Nachweis schnellerer allgemeiner Versorgung.

Konkrete offene Erwerbsfälle: Swap0 local0/entity569/generation6 stirbt nach 29.350 s ohne nützliche Waffe (Inventarzeilen 489–1102; CecilSpawn 643), local1/entity570/generation7 nach 27.150 s (669–1242; Spawn 811). Swap0 local1/generation9 erhält erst nach 21.401 s eine nützliche Waffe und zeigt bis zum rechtszensierten Lebensende keine nützliche Auswahl/FIRE-Anforderung. Swap1 local0/entity565/generation9 nimmt nach 22.601 s auf, wählt nach 24.551 s und fordert nach 24.802 s FIRE an; seine folgende generation10 bleibt 20.901 s ohne Aufnahme rechtszensiert. Swap1 local2/entity567/generation10 bleibt 15.301 s ohne Aufnahme rechtszensiert. Diese Fälle sind keine verschwundenen oder automatisch erfolgreichen Versuche.

## Tatsächlicher Schaden und unabhängige Todesfolgen

503 originale Damage-Aufrufe werden vollständig partitioniert: 288 lebende bekannte andere Spieler, 187 bereits tote Opfer, 15 Selbstschäden, 13 ohne bekannte Spielerattribution, null außerhalb/über der Fenstergrenze. Nur die erste Gruppe geht in Kohortschäden ein. Begrenzter HP-Verlust ist pro Aufruf `min(positive HP vorher, beobachtete HP-Abnahme)`; Roh-Overkill und Armor bleiben getrennt.

| Lauf / Angreifer | Aufrufe | Roher HP-Verlust | Begrenzter HP-Verlust | Armor-Verlust | Tödliche Aufrufe |
|---|---:|---:|---:|---:|---:|
| Swap0 Public | 72 | 2715.361 | 2394.602 | 25 | 18 |
| Swap0 Candidate | 71 | 9293.899 | 1760.117 | 0 | 20 |
| Swap1 Public | 40 | 1575.000 | 1417.872 | 25 | 8 |
| Swap1 Candidate | 105 | 3030.000 | 2548.000 | 50 | 28 |

„Anderer Spieler“ umfasst im Free-for-all auch dieselbe DLL-Kohorte. Deshalb ist die volle Paarmatrix erforderlich:

| Angreifer → Opfer | Aufrufe | Begrenzter HP-Verlust | Tödlich |
|---|---:|---:|---:|
| Public → Public | 70 | 2406.289 | 16 |
| Public → Candidate | 42 | 1406.185 | 10 |
| Candidate → Public | 115 | 2644.351 | 32 |
| Candidate → Candidate | 59 | 1463.766 | 14 |
| Candidate → Vanilla | 2 | 200.000 | 2 |

Alle 74 tödlichen fremden Aufrufe stimmen paarweise mit den tatsächlichen Killmeldungen des Originalservers im Messfenster überein (38/36 je Lauf). Die abschließenden Closed-Logs werden für Sicherheit, nicht für zusätzliche Messfensterkills verwendet. Frags +44/+26 sind Nettowerte; Selbst-/Umwelttode dürfen nicht als fremde Kills umetikettiert werden. Kein akzeptierter HP-Abfall wurde exakt am Spawn-Tick beobachtet; insbesondere ist dies kein A1-Erstzustandsbeweis.

## Bewegung, Flug und Beobachtungsgrenzen

Pro Lauf existieren nur 46 BotHuman-Diagnosezeilen. An den gleichgetaktet vorhandenen Human-/FinalAction-Paaren gibt es keinen Human-FIRE→Final-No-FIRE-Fall; daraus folgt keine Aussage über alle 20-Hz-Aktionen. FinalAction-FIRE-Zähler steigen bei Candidate im Swap0 um 109/148/343/560, im Swap1 um 233/371/189/125; das sind Aktionen, keine gezählten Schüsse. Die protokollierten Zustände enthalten STAND/FALL, keine SWIM-/DIVE-Ausübung.

Längste beobachtete Verweilzeit innerhalb eines Meters, mit Abbruch bei >0.5-s-Samplinglücke: Candidate maximal 1.95 s/1.35 s je Lauf, Public 7.15 s/9.30 s. Dies schließt weiträumige Routenschleifen nicht aus. Pro-Leben-Bewegungsnenner und Lücken stehen im JSON. Candidate-GoalEnd: Swap0 unavailable33/death9/timeout3/connector2; Swap1 unavailable31/death7/connector4. Keine pauschale Routeneffizienzfreigabe.

Flugfinish: Swap0 local1 Tick328→331 und local0 1315→1318, jeweils 86→176 und `arrived` bei unveränderter Deadline. Swap1 local0 981→985 und local1 1935→1937 ebenfalls 86→176/arrived; local3 1975→1976 auf 12→34 endet `context`. Kein `continue`-Ereignis dieses Paares. Dies sind Navigatorereignisse und kein zusätzlicher physischer Bouncer-/Landungsnachweis.

## Kosten und Reproduzierbarkeit

Controller-CPU 26.144/25.613 s, maximaler RSS 166996/167772 KiB. Inventar: 2467/2472 gültige Batches, 68/75 als verändert verworfen; gesamte Leserzeit 10.880/11.153 s, längster Einzelread 14.974/11.679 ms. Größte Hauptlooplücke 227.514/222.971 ms. Gemessene Host-CPU maximal 58.163/59.121 %, minimal verfügbare RAM 1.791/1.872 GiB; keine aufgezeichnete Budgetverletzung. Host-Gesamtlücken von 46.414/46.890 s betreffen auch Startup; größte Gameplay-Budgetlücken sind 1.767/1.725 s. Keine kontinuierliche Grenzgarantie zwischen Stichproben und keine kausale Instrumentierungskostenmessung.

Private Analyseskripte: `/srv/tse-nav-a3-demon-pair-audit-20261112/{analyze.py,behavior.py,publish_pair.py}`; alle Läufe unter CPUQuota25 %. Das JSON enthält vollständige bereinigte Lebens-/Bewegungstabellen, pro Fenster die volle Schadensmatrix, Quell-/Rohartefakt-Hashes und Nachweiszeilen. Private Rohlogs, Namen, GUIDs, Pointer und Retaildaten sind nicht Bestandteil dieses Berichts.
