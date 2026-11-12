# Native011 repeat: Ursachen der verzögerten ersten Waffenaufnahme

Read-only-Auswertung des abgeschlossenen Fensters `arena011hook2-checked-swap1-trial-1-000025`, 120.041233 s, vier Rollen normal geschlossen, keine beobachteten SYNCBAD/Disconnects. Kein neuer Lauf und keine Codeänderung. Kandidat011 `4184df65d927054470ac37967711236deeec442c4dbf92a9428769458e3ed5db`; keine Aussage zur nativen Wirksamkeit012.

Der vollständige Nenner bleibt **13 Kandidatenleben: 8 mit erster nützlicher Waffe, 3 beendet ohne, 2 zensiert ohne**. Ein weiteres zensiertes Leben hat bereits eine Waffe. Alle 13 wählen beim protokollierten Spawn unmittelbar ein Waffenziel. Die längsten Verzögerungen sind keine einheitliche Health-Prioritätsstörung: Sie enthalten reale Konkurrenz, lange Wege und wenigstens einen unabhängig von12→34 belegten fehlgeschlagenen Endkontakt. Das rechtfertigt keine pauschale Änderung der Waffenfilter oder aller Prioritäten.

Die [JSON-Ergänzung](2026-11-12-native011-acquisition-causes.json) enthält alle 13 Leben, erste Ziele, Auswahl-/Connector-/Endereignisse, beobachtete Wegwechsel und private Logzeilennummern ohne Weltkoordinaten. Grundlage ist der geprüfte [vollständige Fensterbericht](2026-11-12-native011-repeat-window.md); dessen JSON-Hash sowie die Rohdateihashes stehen in der Ergänzung. Identität: Kandidat PhysicalA, locals0/1/2/3 = Globals0/2/3/4 = Entities565/566/567/568; keine Ableitung aus Samplinggruppen.

## Nenner und erste tatsächliche Akquisition

Zeiten sind **native GameClock minus SpawnClock**, keine allgemeine Umrechnung `clientTick × .05` in Wandzeit. Tickangaben unten identifizieren lediglich Logereignisse. Owned-Maskenzuwachs beweist Besitz, nicht abgeschlossene Waffenwahl, Munition oder einen tatsächlich verarbeiteten ersten Spielzustand. Nützlichkeitsmaske `0x3df8`, DoubleColt ausgeschlossen.

| Local / Generation | Erster Zieltyp / Entity | Erste nützliche Aufnahme bzw. Beobachtungsende |
|---|---|---|
| 0 / 5 | Flamer248 | SingleShotgun nebenbei, 3.350 s; Tick261 owned3→11 |
| 1 / 5 | Grenade544 | Grenade, 11.950 s; Tick432 owned3→259 |
| 2 / 5 | Flamer248 | Tod ohne, 53.949 s |
| 3 / 5 | Flamer248 | Rocket, 12.100 s; Tick435 owned3→131 |
| 1 / 6 | Minigun243 | Sniper, 62.901 s; Tick2024 owned3→4099 |
| 0 / 6 | Minigun243 | DoubleShotgun nebenbei, 2.400 s; Tick901 owned3→19 |
| 3 / 6 | Minigun243 | Minigun, 19.850 s; Tick1329 owned3→67 |
| 2 / 6 | Laser267 | Tod ohne, 13.750 s |
| 2 / 7 | Laser267 | IronCannon, 11.251 s; Tick1831 owned7→8199 |
| 3 / 7 | Sniper401 | Rocket nebenbei, 27.102 s; Tick2235 owned3→131 |
| 0 / 7 | Grenade544 | Tod ohne, 20.951 s |
| 1 / 7 | Laser267 | Ohne, bei 7.450 s rechtszensiert |
| 0 / 8 | Minigun243 | Ohne, bei 4.250 s rechtszensiert |

`goal_entity` ist nicht automatisch die aufgenommene Waffe: besonders0/g5,0/g6 und3/g7 erhalten unterwegs einen anderen Waffentyp. Verifizierte Cecil-IDs:7 Minigun,8 Rocket,9 Grenade,11 Flamer,12 Laser,13 Sniper,14 IronCannon; kind1 Health, kind3 Armor.

## Drei abgeschlossene Leben ohne Waffe

**Local2/gen5:** Flamer248 wird aus sechs protokollierten Kandidaten gewählt (Tick194, botA.log283). Die Alternativen sind belegt; die geringste Bewertungszahl gewinnt, nicht die kürzeste reine Pfadlänge. Flamer wird bei360 unpickbar (`render=5`), danach Grenade544 bei400, ebenfalls unpickbar432 genau bei local1s belegter Grenadeaufnahme. Laser267 folgt432; unpickbar558, vorhandener FlightFinish84→86 endet563. Bei564 ist nur noch Minigun243 eligible; Connector ist klar. Route86→95→161→76→43→170→67→68→6→7→8→12→34. Die langen verfügbaren Wege und Konkurrenz liegen vor dem Arrivalproblem. Tick887 liefert beim tatsächlichen Wechsel auf12→34 UP11; echter234-Launch888, zusätzlicher vertikaler Zuwachs889 und anschließender Flug weit am Ziel vorbei. Terminalzeilen904–1338 behalten dieselbe12→34-Kante, später bereits auf Boden; Tod1272. Keine Deadlineverlängerung oder Timeout protokolliert: Minigunfrist73.200 bleibt unverändert. **012 umfasst den konkreten Arrival887-Ausgabefall**, nicht die gesamte vorherige Beschaffungszeit. Siehe [Mechanismus-/Replaybericht012](2026-11-12-bouncer012-arrival-up.md).

**Local2/gen6:** Laser267 wird bei1302 aus drei Kandidaten gewählt, Connector klar (1445–1447). Route94→84→86→176. Terminal1712 (`time=72.100`, eigener Driver-Zeitbereich) zeigt Distanz4.389 zum Endpunkt und Höhe1.787. Eine Sekunde dieses Diagnosezeitbereichs später (1723) steht der Spieler auf statischem Brushsupport338, Geschwindigkeit0, Distanz7.090 zum Ziel; keine Akquisition. Anschließend fällt er unter die Plattform: Terminal1744 Höhe−7.319,1754 Höhe−37.059, danach weiterhin86→176 auf Boden bis Tod1575. Der Laser bleibt als Ziel lesbar; weder unavailable noch Timeout noch Connectorablehnung. Combatübernahme ist bei1540 sichtbar, **nach** dem fehlgeschlagenen Endkontakt. Damit ist ein eigenständiger physischer Endkontakt-/Fortsetzungsfehler belegt, kein12→34-Arrivalfall. Support338 belegt Kontakt, aber kein konkretes Kollisionspolygon oder dessen Kausalität. Der kleinstmögliche weitere Prüfgegenstand wäre diese bereits gespeicherte86→176-Sequenz: wann der Navigator Ankunft erwartet und wann eine auf Boden fortgesetzte Kante ihre physische Erreichbarkeit verliert. Eine neue Radius-/Recoveryregel lässt sich daraus noch nicht eindeutig ableiten.

**Local0/gen7:** Grenade544 bei2070 aus drei Kandidaten, klarer Connector (2232–2234). Weg16→17→3→2;2160 source/hop−1 auf Support9, danach3→14→98→58→0→4. Das ist ein beobachteter Wegwechsel; dessen konkrete Relokations-/Replanursache ist nicht vollständig geloggt. Grenade wird2343 unpickbar. Neuer Laserweg0→58→98→93→84→86; Tod2488. Keine sichtbare Combatbewegungsübernahme in den vorliegenden State-Samples, kein12→34-Arrival und kein Timeout. Kein Beleg für einen Waffenfilterfehler; unvollständiger körperlicher Weg plus Verfügbarkeitswechsel.

## Die drei längsten erfolgreichen Leben

**Local1/gen6, 62.901 s:** Bei766 ist ausschließlich Minigun243 eligible (793–796), Pfadlänge267.969. Der Weg89→157→58→0→1→2→3→14→9→10→11→12→34 schreitet fort, mit einzelnen sichtbaren Combatübernahmen860/900/1080. UP11 bei Arrival1253 gehört zu012; echter234-Launch1254, danach normale Abnahme der vertikalen Geschwindigkeit1255, also **kein allgemeiner Nachweis einer zusätzlichen UP-Impulsfolge**. Minigun wird1329 nachweislich von local3 aufgenommen; eigener Besitz bleibt3. FlightFinish1329–1344, danach Health400 beiHP20 (1345–1351, späterHP45), Armor556 bis1367. Kein belegter gewöhnlicher Health-Vorrang bei voller Gesundheit. Verfügbare Waffenalternativen an diesen beiden gewöhnlichen Auswahlticks sind nicht vollständig geloggt.

Laser267 ist bei1367 der einzige gemeldete mapped Kandidat. Route34→41→100→162→92→84;1520–1620 bleibt92→84 während der Bot bereits auf tieferem Boden steht. Laser wird1638 unpickbar; kein Timeout. Darauf Sniper401: dessen Score318.782 schlägt IronCannon311 knapp319.864, obwohl der reine Pfad264.034 gegenüber158.306 länger ist; das entspricht dem vorhandenen Höhenaufschlag. **Die Auswahl ist belegt, eine günstigere tatsächlich erfolgreiche Alternative nicht.** Weg130→92→93→98→58→0→1→2→3→20→21→19→18→138, Sniperaufnahme2024. Minigunkonkurrenz, spätere Laserroute und Sniperweg werden durch012 nicht pauschal beseitigt.

**Local3/gen7, 27.102 s:** Sniper401 bei1694 aus zwei Kandidaten. Route89→157→58→0→1, danach zurück1→0 und über58→98→93→84→95→161→76. Die genaue Ursache dieses Wegwechsels bleibt offen. Sniper wird2024 unpickbar, zeitgleich mit local1s belegter Sniperaufnahme. Flamer248 folgt2024, unpickbar2117. Grenade544 wird danach gewählt; bei2235 erhält der Spieler unterwegs tatsächlich Rocketbesitz (131). Weder12→34 noch Timeout oder beobachtete Combatübernahme vor dem ersten Erwerb. Konkurrenz ist hier ein echter Verfügbarkeitswechsel und allein kein Bugnachweis.

**Local3/gen6, 19.850 s:** Bei934 nur Minigun243 eligible. Langer, fortschreitender Weg94→95→161→76→43→170→67→68→6→7→8→12→34; Arrival1240 bereits UP0, echter234-Launch und Minigun1329. Keine Combatübernahme in den gespeicherten State-Samples. Dies ist ein erfolgreicher011-Kontrollfall, dessen Arrival012 unverändert lässt.

## Zensierte Leben und Grenzen der Ursachenbehauptung

Local1/gen7 wählt2454 Laser, verliert ihn2490 (`render5`), wählt danach die einzige eligible Minigun. Bei Fensterende läuft noch die Reakquisition über89/90/91/54. Local0/gen8 wählt2518 unmittelbar die einzige eligible Minigun und folgt89→157→58. Nur7.450 beziehungsweise4.250 s Beobachtung: beide sind offene Beschaffungsversuche, keine abgeschlossenen Fehlversuche.

In den vor der ersten Akquisition ausgewerteten Zielen gibt es **keinen protokollierten Timeout und keine abgelehnte ausgewählte Endpoint-Verbindung**. Insbesondere der Minigun-Hit liegt hinter dem Segmentende und wird korrekt als klar gewertet. Kandidatenmeldungen zeigen nur tatsächlich eligible Waffen; nicht gemeldete Alternativen und interne gewöhnliche Visibility-Rejects lassen sich nicht vollständig rekonstruieren. Fehlende Meldungen sind kein Nachweis fehlender Weltwaffen.

Der Quellpfad bestätigt die Abgrenzung: `BotSupplyNative.h`453–464 behandelt erste brauchbare Fernwaffen als urgent;530–535 verwendet die vom Colt unabhängige Maske;539–568 prüft admission/typed need/erreichbare Graphknoten und bewertet Weg plus Höhenaufschlag. Gewöhnliche Auswahl geht dem mapped Fallback voraus (614–649), aber alle ersten Ziele in diesem Fenster sind Waffen. Die existierende Retention lässt ein lebendes Waffenziel bei kurzem Kampf bestehen (1301–1323), während Bewegung unter8 vorübergehend abgibt (1351–1355); Driver1389–1397 lässt urgent Waffen und FlightFinish wieder übernehmen. `nav0/vis1` belegt einzelne solche Ausgaben, keine Dauer oder alleinige Ursache der Gesamtverzögerung. `BotCecilItems.h`67–80 verweigert unpickbare Renderzustände vor Typ-/Maskenentscheidung; die hier geloggten Verfügbarkeitsverluste rechtfertigen kein Entfernen dieser Filter.

Prüfung: Alle13 Nennerleben und8/3/2-Ergebnisse gegen die geprüfte Native-Inventarauswertung abgeglichen; sämtliche13 ersten Ziele sind kind0 am jeweiligen Spawn-Logtick. Besitzmasken gegen die unveränderten Cecil-Referenz-Waffen-IDs geprüft. Keine Tests oder Runtime für dieses reine Berichtsartefakt gestartet. Der getrennte Public-v3-Controllerreview führte ausschließlich28 Offline-Tests aus.
