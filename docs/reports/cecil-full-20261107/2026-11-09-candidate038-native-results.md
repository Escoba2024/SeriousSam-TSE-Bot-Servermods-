# Normal038: Versorgung und Respawns belegt, Skulls-Verhaltensgate fehlgeschlagen

Normal038 ist **nicht für den Rollout qualifiziert**. Der vollständige Skulls-Test überschreitet die unveränderte Stillstandsgrenze. Alle privaten Spielprozesse wurden normal beendet; die öffentlichen Instanzen bleiben unverändert.

Quelle: `e2804ac2d0cabdc082a3bb881ef0557cd0f66bfc`, Tree `9eecbbb40cd3213fd1f29758010380118fa1f5cf`. Normale PE32-x86-DLL: `eacc13bd22221f758c151875857fab48012eb2637ffa89abb24346b2af52ec1b`. [Buildmanifest](build038.json). Keine diagnostische Overlay-DLL wurde als038-Abnahme ausgegeben.

## Vollständige beobachtete Kurzfenster

| Szenario | Beobachtet | Maximaler unbegründeter Stillstand | Ergebnis |
| --- | ---: | ---: | --- |
| Hole,8 Bots | 600,009 s | 2,025 s | Begrenzte Beobachtung bestanden |
| Little Trouble,8 Bots | 600,008 s | 9,067 s | Begrenzte Beobachtung bestanden |
| Yodeller,8 Bots | 600,007 s | 3,020 s | Begrenzte Beobachtung bestanden |
| Skulls,8 Bots | 600,008 s | 271,191 s | **Fehlgeschlagen** |
| Zusätzliche Red-Station-Liftregression,4 Bots | 600,003 s | 1,013 s | Begrenzte Beobachtung bestanden |

Alle genannten Fenster haben vollständige Monitorabdeckung, keine neuen Monitorfehler und beobachteten positiven Scorezuwachs bei jedem eigenen Bot. Diese Eigenschaften heben die Skulls-Regression nicht auf. Der geplante fünfte Acht-Bot-Kurzlauf auf Red Station wurde nach dem Fehler nicht gestartet. Kein 3600-/3600-/7200-s-Gate wurde mit038 begonnen oder abgeschlossen.

## Prospektive Versorgung: vollständige neue Beobachtung statt zensierter Endpunkte

Der ursprüngliche v10-Lauf mit zehn festen60-s-Beitritten bleibt ohne Freigabe: acht korroborierte Erwerbe, ein echter Cannon-Fehlversuch und ein administrativ zensiertes Flamer-Ziel. Dieses Ziel begann bei57,25 s; seine unveränderte native12-s-Deadline lag erst bei69,25 s. Die Beendigung des eigenen Messprozesses um60 s belegt weder Erfolg noch nativen Timeout.

Für einen neuen Lauf wurde vor dem ersten Start ein eigenständiges v11-Protokoll deklariert. Jeder der zehn frischen Beitritte dauert mindestens60 s. Ein noch offenes Ziel aus der globalen First-10-Kohorte wird bis zum tatsächlichen nativen Ende und einer späteren vollständigen State-Barriere beobachtet. Wiederholte Zielwahlen und neue Starts im selben Tick zählen einzeln. Die vollständigen nach normalem Schließen erhaltenen Rohlogs werden erneut ausgewertet; administrative Grenzen gelten niemals als nativer Erfolg oder Timeout. Längere vorangehende Beitritte verändern die Server-/Itemphase, weshalb dies ausdrücklich ein neues Szenario ist.

Alle zehn v11-Beitritte sind beendet: zehn getrennte, chronologische PID-/Start-Epochen,595 gültige Statusabfragen mit genau einem erwarteten Bot und der unveränderten Red-Station-Karte. Die ersten zehn tatsächlichen Waffenziele haben neun durch ausgewählte Entity, passenden Waffenbit-Zuwachs und räumliche Nähe korroborierte Erwerbe. Rang 5 in Fall 2 bleibt ein echter Cannon-Fehlversuch mit `unreachable_hold`; er wird weder entfernt noch ersetzt.

Die zehn festen **initialen** Leben ergeben Latenzen von8,90/3,35/2,45/3,45/3,80/10,20/2,60/4,90/3,95/3,45 s. Median3,625 s und Nearest-Rank-P9510,20 s erfüllen die unveränderten15-/30-s-Grenzen. Spätere Respawns ersetzen kein fehlgeschlagenes initiales Leben.

Der eingefrorene Ledger erzeugt eine zu breite Warnung: `begin_case` markiert jeden noch offenen Waffenversuch beim nächsten Fallbeginn, obwohl sein Abschlussfilter bereits korrekt auf die ersten zehn beschränkt ist. Der einzige derartige Versuch ist Cannon311 in Fall 5, **globaler Rang 13**, Starttick1042. Alle ursprünglichen ersten zehn Ziele waren zuvor bis Fall 4/Tick 672 ausdrücklich beendet. Die eigene und eine unabhängige vollständige Rekonstruktion bestätigen diese Abgrenzung und alle übrigen Rohlog-, Lebenszyklus- und Erwerbsbelege.

Die automatischen NONPASS-/INCONCLUSIVE-Dateien, der fehlerhafte eingefrorene Ledger und sämtliche Rohlogs bleiben unverändert. Eine getrennte, ausdrücklich dokumentierte Scope-Bewertung bestätigt ausschließlich das Einzelbot-Versorgungsgate. Sie qualifiziert weder Skulls noch die Gesamtversion. Es wurden keine Messschwellen oder Kohorten nachträglich geändert.

## Respawns, Waffen und Lift

Auf Hole sind118 vollständige, unterschiedliche Folgen aus vorheriger positiver Gesundheit, nativem Todesereignis, nichtpositiver Gesundheit, Spawn derselben Entity mit nächster Generation und erneuter Aktivität bestätigt. Alle acht Bots tragen bei. Maximal Tod→Spawn1,90 s, Spawn→Aktivität1,15 s und Tod→Aktivität2,90 s. Aktivität bedeutet gemessene Bewegung über0,25 m oder sichtbaren Kampf mit tatsächlichem finalem Feuerinput.

Ein 119. Todesereignis liegt am Ende des Monitorfensters. Sein Spawn und seine Bewegung sind im normalen erhaltenen Nachlauf sichtbar, werden aber nicht in118 mitgezählt. Der unabhängige Auswerter wurde vom Hauptagenten erneut ausgeführt; Hashes und alle Zeit-/Identitätsbedingungen stimmen. Der Nachweis schließt das100-Todesfälle-Featuregate, keine Langzeitqualifikation.

Double-Colt, Rocket, Grenade und Cannon haben innerhalb ihrer jeweiligen038-Lebenszyklen tatsächliche Besitzänderung→geloggte Auswahl→aktuelle und gewünschte Waffe→finalen Feuerinput. Für Flamer sind Besitzänderung und kurzzeitig aktuelle Waffe belegt; eine entsprechende vollständige Auswahl-/Feuerfolge bleibt offen. Nahdistanz-Suppression, getrennte CD-/Animationszeiten sowie die übrigen Sonderaktionen werden nicht aus unvollständigen Beispielen als bestanden erklärt. Feuerinputs sind keine Trefferbelege.

Ein unabhängig geprüfter Liftfall zeigt den038-Fix im normalen nativen Lauf: aktuelle echte MovingBrush-Referenz, neu geschlossener Lock, beibehaltene gerichtete Anfahrt, tatsächliche Ankunft innerhalb des ursprünglichen Radius und anschließender Aufstieg zur oberen Etage. Danach unterbricht sichtbarer Kampf die ursprüngliche Route. Dies ist ein begrenzter Einzelfallnachweis, keine Behauptung vollständiger Lift-/Zielparität.

## Skulls: fehlende Offgraph-Fortschrittsprüfung

BotB:1 steht von106,851 bis378,042 s unverändert ohne sichtbaren Gegner. Dieselbe lebende Entity/Generation bleibt auf festem Boden; Schwerkraft, Medium und Referenz sind stabil. Die finale Ausgabe wechselt zwischen sechs Sekunden freigegebener langsamer Reacquisition und sechs Sekunden neutraler Kandidatenpause. Ziel237 liegt23,84 m entfernt und2,56 m tiefer, ohne Sonderflag, Lock oder Teleport. Freie Strahlen werden als Bewegungsfreigabe verwendet; eine tatsächliche Positionsänderung findet nicht statt.

BotB:2 zeigt denselben fehlenden Fortschritt für12,120 s. BotA:2 steht15,119 s neutral: Der nächste Originalknoten liegt36,17 m entfernt und damit außerhalb des unveränderten32-m-Bereichs. Dieser Fall kann nicht allein durch einen Watchdog für positive Zielbewegung behoben werden.

Die konkrete kollidierende Body-/Step-Geometrie ist aus diesen normalen Logs nicht bewiesen. Belegt ist das Fehlen einer Fortschrittsreaktion: freie Prüfstrahlen und wiederholte Ziel-Cooldowns ersetzen keine gemessene Bewegung. Im gepinnten Original existiert zusätzlich `NoPosChange` in `Sources/Bots/Logic/BotMovement.cpp:25` und das positionsbasierte Ausweichen ab560; `Sources/Bots/BotStructure.cpp:327` aktualisiert den Bewegungszustand bei tatsächlicher Positionsänderung.

Der nächste Kandidat erhält eine eng begrenzte Wiederherstellung dieses Mechanismus. Voraussetzung ist ein belegter aktueller Ground-Kontext und tatsächlich angenommene Offgraph-Supply-Steuerung. Vorhandene begrenzte Escape-Richtungen müssen weiterhin Wand und Boden prüfen. Graphdaten,32-m-Grenze, Ankunftsradien, Flags, Itemdeadlines, Physik-/Netzwerkgrenzen und Raybudget bleiben erhalten. Auch neutrale echte No-Candidate-Situationen werden ausdrücklich von unbekanntem Support, Budgetmangel und ungültigen Daten unterschieden. Eine sichere freie Escape-Richtung wird nicht vor ihrer nativen Prüfung behauptet.

Private Rohlogs, Original-NAV-Daten, Retail-Binaries und Profile werden nicht veröffentlicht. Die vollständigen finalen Versorgung-, Karten-, Waffen-/Sonderaktions-, Retail-, Langzeit-, Ressourcen- und Wiederanlaufnachweise sind nach der Verhaltensänderung passend neu zu erbringen. Erst danach folgt der autorisierte gestaffelte Rollout auf alle sechs Server und die gemeinsame15-Minuten-Flottenprüfung.
