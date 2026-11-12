# Native012: getrennte Ursachen der langsamen Waffenaufnahme

Read-only-Auswertung des bereits abgeschlossenen Fensters `arena012hook2-checked-swap1-trial-1-001915`. Grundlage ist Roots private vollständige Lebensauswertung `native012-root-analysis/result.json`; ihr Hash und die Rohdateihashes stehen in der [sanitisierten Ergänzung mit allen 13 Leben](2026-11-12-native012-acquisition-causes.json). Identitäten wieder aus BotCombat/globaler Slotzuordnung: KandidatA locals0/1/2/3 = Globals0/2/3/4 =565/566/567/568. Kein neuer Lauf, kein Quellfix.

**13 Leben, 10 erste nützliche Waffenaufnahmen, 1 Tod ohne, 2 bei Fensterende ohne.** Insgesamt9Tode und4zensierteLeben. Alle13erstenZiele sind Waffen am jeweiligen Spawn-Logtick. Zeiten unten stammen aus originalem Native-GameClock minus SpawnClock. Ereignisticks und `CecilSupplyDiagTerminal.time` ordnen nur die jeweiligen Logs; sie sind keine allgemeine Wandzeitmessung. Besitz ist nicht gleich nachgewiesene kampfbereite Auswahl oder erfolgreicher Schuss. Der Vergleich mit [011](2026-11-12-native011-acquisition-causes.md) ist eine Ursachenabgrenzung, kein kontrollierter Leistungsnachweis.

| Local / Generation | Erste nützliche Aufnahme oder offenes Ende |
|---|---|
| 0 / 6 | 2.550 s |
| 1 / 6 | 12.150 s |
| 2 / 6 | 8.500 s |
| 3 / 6 | **77.600 s**, Laser1758 |
| 0 / 7 | **43.949 s**, Minigun1413 |
| 2 / 7 | 11.550 s |
| 1 / 7 | 11.700 s |
| 2 / 8 | **32.401 s**, Tod ohne |
| 1 / 8 | **17.551 s**, DoubleShotgun1973 nebenbei |
| 2 / 9 | 10.201 s |
| 3 / 7 | 7.700 s |
| 1 / 9 | Ohne bei15.301 s rechtszensiert |
| 0 / 8 | Ohne bei12.101 s rechtszensiert |

## Längstes Leben: Local3/gen6, 77.600 s

Erstes Flamerziel248 bei206 (botA.log318–320, sechs eligible Kandidaten), verloren375 nach belegter Aufnahme durch local2. Grenade544 bei415, verloren449 bei local1s Aufnahme. Laser267 folgt449; sein Connector ist klar. Route46→47→48→49→97→94→84→86→176. Terminal738 (`time37.200`) liegt nur4.282Einheiten vom Endpunkt und1.642darüber, bereits mit negativer Vertikalgeschwindigkeit. Keine Waffenaufnahme; Terminal748 liegt27.608unter dem Ziel,756/794 bereits ungefähr37darunter auf Boden. **Der erste physische Laserkontakt scheitert wie im unabhängigen011-Fall2/gen6.** Ein exakt gleiches Kollisionspolygon oder dieselbe unmittelbare Ursache ist damit nicht bewiesen.

Laser wird845 unpickbar, zeitgleich mit local2/gen7s echter Laseraufnahme. Das nächste Ziel ist Minigun243, aber dieser Bot erreicht deren Route12→34 vor der ersten Akquisition nie. Tick860–1400 bleibt er in der räumlichen Umgebung des Laseranflugs: source−1/hop86, wiederholt anchor−1 und reacquire84/86/176, teils keine Knotenauswahl. Physisch wiederholen sich starke Auf-/Abbewegungen. Die zahlreichen MotionProbe-Zeilen901–1289 zeigen oft vollständig neutrale gewünschte Bewegung und keine ausgeführten Wand-/Bodenrays in genau diesen Ausgaben; andere Takte enthalten begrenzte Reakquisitionsbewegung. Das ist ein belegter langer **Reakquisitionszyklus**, keine Schlussfolgerung allein aus einem fehlenden Goal-Log. Die Zuordnung seiner einzelnen vertikalen Impulse zu einem bestimmten anderen Bouncer ist durch den auf234gefilterten Hook nicht erfasst.

Minigunfrist85.572 bleibt bestehen; sie wird nicht wiederholt verlängert. Bei1413 nimmt local0/gen7 die Minigun tatsächlich auf, weshalb auch dieses Ziel unpickbar wird.1413/1433 melden null eligible mapped Waffen. Bei1453 wird der wieder verfügbare Laser erneut gewählt; nun über95→84 mit einzelnen sichtbaren Combatübernahmen, dann84→86→176. Endlich1758 owned3→2051; FlightFinish beginnt nach dem tatsächlichen Besitzwechsel. Kein Timeout und kein12→34-Arrivalfall in dieser Vorgeschichte. **012s Arrival-UP-Unterdrückung erklärt oder behebt diesen77.600sFall nicht.**

Der enge weitere Diagnosegegenstand ist bereits durch die vorhandenen Daten begrenzt: Zusammenhang zwischen fehlgeschlagenem86→176-Endkontakt, Zielwechsel bei vorhandener erneuter Luftbewegung und danach fehlendem committed source trotz wiederholter Ankerversuche. Ohne Lifecycle-Replay folgt daraus weder zusätzliche Luftsteuerung noch eine bestimmte neue Recovery-/Radiusregel.

## Separater erfolgreicher Minigunfall: Local0/gen7, 43.949 s

Laser267 bei534, Route16→152→14→98→93→84→86; sichtbare Combatbewegungsübernahmen700/740. Laser wird845 von local2/gen7 aufgenommen; FlightFinish845–859. Ab860 einzige eligible Waffe Minigun243, klarer Connector. Weg84→95→161→76→43→170→67→68→6, anschließend sichtbarer Rückgang zu67→68 und erneuter Versuch68→6, dann6→7→8→12→34. Die Ursache des früheren68→6-Rückgangs ist nicht vollständig protokolliert; der Wegverlust selbst ist sichtbar. Es gibt keine neue Minigun-Deadline und keinen Timeout.

Ein echter234-Launch gehört genau diesem Leben, anschließend Minigun1413. Arrival1324 hat bereits rawUP0; **der neue012-Fall für positives UP beim Umschalten wird hier nicht positiv ausgeübt**. Der Erfolg ist deshalb kein Wirksamkeitsnachweis der neuen positiven Arrival-Unterdrückung. Der lange Abschnitt davor umfasst Laser-Konkurrenz und körperlichen Weg, nicht die erfolgreiche letzte Flugsekunde allein.

## Tod ohne und drittlängster Erwerb

**Local2/gen8,32.401 s ohne:** Grenade544 bei1270 wird1327 von local1/gen7 aufgenommen; Minigun243 bei1327 wird1413 von local0/gen7 aufgenommen.1413/1433 null eligible mapped Kandidaten. Laser1453 über165→84; mehrfach nav0/vis1 bei1520/1540/1580/1600/1620/1680, danach84→86. Laser1758 von local3/gen6 aufgenommen, FlightFinish bis1785. IronCannon311 bei1786, Weg86→95→161→76, Tod1917. Dieses Leben liefert sowohl reale Konkurrenz als auch einzelne nachgewiesene Combatübernahmen. Ihre kontinuierliche Dauer ist nicht gemessen; sie beweisen keine pauschal falsche Priorität. Kein12→34-Anflug, kein beobachteter Timeout oder ausgewählter Connector-Reject.

**Local1/gen8,17.551 s:** Laser1622 über83→87→88→160→84, unpickbar1758 bei local3s Aufnahme. Anschließend Reakquisition, Flamer248 ab1820. Tatsächliche erste nützliche Waffe ist eine unterwegs aufgenommene DoubleShotgun1973 (owned3→19), nicht der Flamer im Goal-Feld. Keine sichtbare Combatbewegungsübernahme in den gespeicherten State-Samples vor dem Erwerb; kein12→34-Arrival.

**Zensierte Leben:** Local1/gen9 verliert erst Grenade544 und verfolgt dann Laser über90/54/53/52/51→50; Local0/gen8 verfolgt Laser über63/68/6/27/95/84→86. Beide bleiben offene Beschaffungen. Ihre15.301/12.101s sind keine abgeschlossenen Fehlversuche.

## Beweisgrenzen

Ausgewählte Endpoint-Connectoren sind in den analysierten Vor-Erwerb-Ereignissen klar, protokollierte Goal-Timeouts fehlen. Das sagt nichts über alle internen gewöhnlichen Visibility-Rejects oder nicht geloggte Weltalternativen aus. Alle genannten verlorenen Ziele sind wirklich `render5`; die konkurrierenden Besitzwechsel werden getrennt belegt. Natürliche Konkurrenz ist kein Fehlerbeweis.

Der zusätzliche native012-Lauf bestätigt insbesondere, dass das schnelle Ausrüsten nicht allein durch den Arrivalfix erledigt ist. Er übt den neuen positiven Arrivalfall aber auch nicht aus und widerlegt diesen engen Fix deshalb nicht. Die wiederholte Laser-Endkontakt-/Reakquisitionssequenz liegt außerhalb seines Geltungsbereichs. Ein neuer Gameplayauftrag oder Fix wird aus diesem Bericht nicht vorweggenommen.

Validierung:13Leben/10Aufnahmen/1Todohne/2zensiertohne gegen Roots vollständige Native-Auswertung abgeglichen; alle13erstenGoalzeilen sind Waffen am Spawn-Logtick. Die Ergänzung stoppt die kompakten zensierten Routensamples konservativ beiTick2600; die Lebensnenner übernehmen weiterhin die gesamten nativen Schlussproben. Keine Runtime oder Quelländerung durch diese Analyse.
