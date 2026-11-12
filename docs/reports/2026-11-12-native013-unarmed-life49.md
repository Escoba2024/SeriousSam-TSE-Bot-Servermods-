# Native013: 49.151 Sekunden ohne nützlichen Waffenbesitz

**Belegte Teilursache ist wiederholter Zielverlust durch konkurrierende Pickups, nicht ein festhängender Waffenwechsel oder eine nachgewiesene bessere übersehene Alternative.** Kein Gameplayfix aus dieser Auswertung. Privates Fenster `arena013brush3p-i0-swap1-trial-1-015034`, botA local0/Slot0/entity565/Generation6; serverseitige Lebensuhr31.449806, Tod nach49.150513 s. [Vollständige Lebensnenner und Quellenhashs](2026-11-12-native013-flight-control-analysis.json) bleiben maßgeblich.

| Driver-Ticks | Dauer | Tatsächliche Auswahl und Verlauf | Ende / Quellzeile botA.log |
|---|---:|---|---|
|797–1039|12.10 s|Minigun243, Ziel34;93→98→58→0→1→2→3→14→9→10; beweglicher Liftabschnitt2→3 sichtbar an Höhe3.423→7.235→11.049|243 render5/unavailable1096–1097; local2 nimmt Minigun im selben Tick1039 auf,1102 |
|1039–1099|3.00 s|Kein Item, Reacquire9; x≈−51, z−15.685→−27.932, Höhe14.696→13.076|Neues Ziel1099,1236 |
|1099–1336|11.85 s|Napalm544, Ziel175;9→14→98→58→0→4→5→102→112; zwei beobachtete NAV0-Zustände1260/1280, danach Fortschritt|544 render5/unavailable1501–1502; local3 nimmt Napalm ebenfalls1336 auf,1511 |
|1336–1358|1.10 s|Health549, Ziel174; eigenes HP60→85|549 render5/unavailable1534–1535; eigener Healthanstieg, keine Fremdzuweisung |
|1358–1521|8.15 s|Laser267, Ziel176;174→112→102→5→4→0→58→98→93|267 render5/unavailable1683–1684; local2 nimmt Laser1521 auf,1693 |
|1521–1660|6.95 s|Cannon311, Ziel71;98→93→84→95, tatsächlicher FALL-Anflug|311 render5/unavailable1812–1813; local2 nimmt Cannon1660 auf,1819 |
|1660–1670|.50 s|Begrenztes altes84→95-Finish, Deadline114.823 unverändert|`arrived`,1831; keine neue86→176-Fortsetzung |
|1670–1691|1.05 s|Reacquire160 nach dem Flug|Neues Ziel1691,1861 |
|1691–1779|4.40 s|Sniper401, Ziel138;95→161→76; HP85→65→45→5|Tod1779,1923–1924; vorher1775 nur DoubleColt3→7,1918 |

Die Driver-Intervalle summieren sich auf49.10 s; die erste native Todesbeobachtung ist49.150513 s nach Spawn. Driverzeit und serverseitige Lebensuhr sind getrennte Messungen. 49 einsekündige CecilStates:47NAV1,2NAV0,11mit Sichtkontakt;47SafeMotion1,2SafeMotion2. Der aus diesen Positionen gebildete Polygonzug ist etwa553.34 m lang, ohne Anspruch auf exakte Weglänge. Keine lange Same-Hop-Schleife, kein `CecilItemTransitEnd` und kein Itemtimeout in diesem Leben. Der gewöhnliche Fortschrittswatchdog soll einen solchen weiterlaufenden Versuch nicht allein wegen hoher Gesamtdauer abbrechen.

## Welche Alternativen sind tatsächlich belegt?

Die bestehenden Diagnosebatches erfassen die **nach sämtlichen Filtern verbleibenden gemappten Waffen**. Sie sind weder eine vollständige Weltinventur noch ein Beweis physischer Erreichbarkeit der gesamten Route. Ausgeschlossene Items und deren einzelne Filtergründe sind hier nicht vollständig protokolliert.

| Tick | Eligible / emittiert | Beobachtete Kandidaten: Item, Graphdistanz, Score, erster besonderer Abschnitt | Gewählt / Connector |
|---:|---:|---|---|
|797|1/1|243:240.553,389.450,1→2 (Lockkontext; Flagunion0)|243, clear1 |
|1099|2/2|248:153.561,238.969,98→91/Flag2;544:147.358,215.576,kein besonderer Abschnitt|544, clear1 |
|1358|1/1|267:183.857,314.392,93→84/Flag10|267, clear1 |
|1521|1/1|311:196.580,310.134,93→84/Flag10|311, clear1 |
|1691|2/2|243:197.136,343.938,8→12/Flag42;401:238.557,241.850,kein besonderer Abschnitt|401, clear1 |

Quellenzeilen814–816,1232–1235,1536–1538,1685–1687,1857–1860. Bei243 liegt der gemessene Brushhit hinter dem Connectorende (Länge1.258371, Hitdistanz1.309612);013 behandelt ihn korrekt als clear. Die konkrete frühere Connectorblockade reproduziert sich hier nicht.

An beiden Entscheidungen mit mehr als einem Kandidaten gewinnt bereits die vorhandene Alternative ohne besonderen Abschnitt und mit geringerem Gesamtscore. Es gibt deshalb **keinen belegten Anlass**, pauschal besondere Routen zu deaktivieren, Fristen zu verkürzen, Sichtfilter zu entfernen oder eine Radiusänderung vorzunehmen. Bei späteren Retentionsphasen ist nicht vollständig erfasst, welche zunächst ausgeschlossenen oder inzwischen respawnten Waffen erreichbar gewesen wären. Ebenso ist aus den verbleibenden Kandidatenzahlen nicht beweisbar, ob Ausschluss durch aktuelle Verfügbarkeit, frühere Ablehnung, Locks oder andere bestehende Filter erfolgte.

Die vier tatsächlichen Waffenverluste und weiteren Wege sind als Konkurrenz-/Umwegfolge belegt. Das angemessene nächste Discriminandum ist eine **konkrete, zum jeweiligen Entscheidungszeitpunkt nach allen bisherigen Sicherheitsfiltern zugelassene kürzere Alternative** oder eine nachgewiesene unnötige Reacquire-/Rückwegphase; kein hypothetisches globales Tuning. Es wurde weder neue Telemetrie noch Code oder Runtime verändert.
