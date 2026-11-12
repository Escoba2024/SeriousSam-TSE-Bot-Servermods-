# Build017: drei Red-Station-Runden und dichter Supply-Beobachter

## Tatsächliches Ergebnis

**FAIL bleibt bestehen.** Das separat geprüfte Testpaket durchlief Red Station → Red Station → Red Station und beobachtete 246,391839 Sekunden. Beide Kartenneustarts wurden erkannt. Die vorhandenen fünf Aktivitätsfelder sind in 21 von 24 Bot-/Phasen-Kombinationen vollständig; drei Kombinationen erfüllen die Waffen-/Feuerkriterien nicht.

| Phase | Betroffener lokaler Bot | Fehlende bestehende Kriterien |
| --- | --- | --- |
| 0 | botA:2 | beobachteter nützlicher Waffenpickup; natives Fernwaffenfeuer |
| 1 | botB:2 | Fire-Aktionszeile; beobachteter nützlicher Waffenpickup; natives Fernwaffenfeuer |
| 2 | botA:2 | Fire-Aktionszeile; beobachteter nützlicher Waffenpickup; natives Fernwaffenfeuer |

Das ist keine Kartenfreigabe. Die drei fehlgeschlagenen Kombinationen hatten vier, zwei beziehungsweise fünf beobachtete Leben mit drei, einem beziehungsweise vier HP-Todesereignissen. Diese vollständigen Nenner bleiben erhalten. Konkurrenz, kurze Leben und ein möglicher Navigationsdefekt werden anhand der tatsächlichen Aufzeichnung getrennt untersucht.

## Neue Beobachtung

Die nachgehashten geschlossenen Botlogs enthalten **437 dichte Diagnosezeilen in sieben Fenstern**, sämtlich für north68_6. Für source87 wurde in diesem Lauf kein solches Fenster erfasst. Die erste Root-Auswertung zählt und bindet diese Zeilen; sie behauptet noch keine Ursache und keine erfolgreiche source87-Route.

Die Zeilen enthalten ursprüngliche Navigation, angeforderte und endgültige Aktion, Position, Geschwindigkeit, Support, Probeergebnis und Rotation. Damit kann ein konkreter Bewegungsfehler gegen echte Zielwechsel und Konkurrenzereignisse geprüft werden. Die bisherigen FAILs werden nicht nachträglich in PASS umbenannt.

## Ressourcen, Abschluss und Wiederherstellung

Höchster gemessener Host-CPU-Intervallwert: **60,2978 %**. MemAvailable fiel nicht unter **2.101.719.040 Bytes**, freier Datenträgerspeicher nicht unter **15.108.591.616 Bytes**. Die maximale Start-/Lebenszyklus-Messlücke betrug 47,2887 Sekunden, die maximale Gameplay-Lücke 2,3667 Sekunden. Daher bleibt budget_pass_claim=false; das ist kein Langzeit-Ressourcennachweis.

Der Wrapper endete mit Exit 1 nach 310,18 Sekunden einschließlich Aufbau und Cleanup. Alle vier Rollen wurden normal geschlossen, sämtliche Schlusslogs akzeptiert. Root prüfte anschließend unter exklusiver Lab-Sperre alle vier Wurzeln auf Prozessfreiheit, beide Testdisplays auf Abwesenheit und unabhängig **643 Dateihashes sowie fünf fehlende Pfade**. Die gesamte Wiederherstellung ist bestätigt.

## Provenienz und nächste Arbeit

Build017 stammt aus b35397f024b8a8722a01178a08c06d3d40802f65; DLL-SHA256 a5a379aadfd0cc376ad15a8368dd6814518e3f2da1fde22fdde9bd86f02abc5d. Der unabhängige Controllerreview bestätigte 122 Source- und 65 Runtimepins, alle geerbten Protokolle und die vorhandene 130-Test-Quittung. Root aktivierte ausschließlich eine eigene Kopie für dieses eine Fenster; das Autorenpaket bleibt deaktiviert.

Die geschlossene Aufzeichnung wird jetzt gezielt kausal ausgewertet. Es ist keine spekulative Änderung an Original-Navflags, Ankunftsradien, Zeitgrenzen oder Abnahmekriterien beschlossen. A1, vollständige aktuelle A3-Vergleiche, A4-Kartenfreigaben, die 1/4/8-Bot-Langzeitprüfungen und der Kandidatenrollout bleiben offen. B ist unbegonnen.

## Nachweise

[a4-build017-native-supply-observer.json](milestone-a-20261112/a4-build017-native-supply-observer.json) enthält die öffentliche strukturierte Quittung. Private Originale: Fenster a4-reset017-supply-observer-20261112-154453, Root-Freeze, Controllerreview, Root-Postflight und die erste Zeilenzählung. Ergebnis-SHA256: 7fa65885a2bf3e5a877d53cb09801aad3b4d7874df633fd0a31925cbe799813b.
