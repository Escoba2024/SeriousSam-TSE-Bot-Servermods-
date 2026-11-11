# Normal041: Skulls verletzt weiterhin das Stillstandsgate

Normal041 ist nicht für den Rollout qualifiziert. Quelle `74b5e16ca52b3dfb78c0758ddaa6087a837fd9d3`, Tree `5cfe4e0df7dc264921c6926cca1804b7a023cf35`, DLL `9ffb50081a06116c97474cd3d9aaadf75e8fbf9d5b64545bf5e70001bf8c1020`. Alle15 MSVC-Einheiten und der Link bestehen; [bereinigtes Buildmanifest](build041.json). Main hat743 zusammengeführte SDK-ASan/UBSan-Prüfungen und die Driver-/Item-/Originaltabellenprüfungen ausgeführt; zwei unabhängige Reviews bestätigen den zusammengeführten Stand. Das ersetzt keine native Gesamtfreigabe.

## Eng begrenzte Änderungen

Die allgemeine Boden-Neigungsprüfung bleibt unverändert. Nur ein tatsächlich beobachteter Ground-Stall oder dessen gehaltene Bewegung kann eine engere Kontaktprüfung verwenden: genau das bereits native Standpolygon, derselbe aktuelle statische WorldBase-Owner, nicht beweglich oder passierbar, finite normalisierte Fläche mit positiver gravitationsbezogener Unterstützung und ein tatsächlicher Treffer innerhalb nativer StepUp-/StepDn-Grenzen. Unbekannte NULL-Unterstützung wird dadurch nicht freigegeben.

Fehlt geometrisch jeder ungesperrte Originalpunkt innerhalb32m und8m gravitationsbezogener Höhe, darf die bestehende Wiederannäherung weiter entfernte Originalpunkte als Hinweise prüfen. Ein fehlgeschlagener LOS-Test, ein Tried-Bit oder ein Retry-Timer erzeugt diese geometrische Abwesenheit nicht. Maximal drei LOS-Tests, Reserve für zwei finale Sicherheitsstrahlen, Originalradien, Locks, feste6s-Versuche und Ziel-Fristen bleiben unverändert. Nach den bisherigen drei Escape-Richtungen folgen zwei einmalige Seitwärts-/Rückwärtsdiagonalen für einen tatsächlichen Ground-Stall, entsprechend der Original-Cecil-NoPosChange-Bewegung. Jede ausgegebene Bewegung bleibt im0,3-Limit und braucht frische Wand-/Bodenprüfung.

## Vollständiger Skulls-Lauf: FAIL

Acht Bots sind600,008519155s beobachtet, mit vollständiger Telemetrieabdeckung, korrektem Szenario, null neuen Monitor-/Sync-/CRC-/Fatalfehlern und positiver Scoreentwicklung aller acht.64 Todesfälle sind über tatsächliche nichtpositive Gesundheit und anschließenden Spawn derselben Entity mit nächster Generation unabhängig korreliert; das allein erfüllt noch nicht die globale100-Todesfälle-Anforderung.

| Slot | Maximaler unbegründeter Stillstand |
| --- | ---: |
| BotA:0 |16,145s |
| BotA:1 |5,028s |
| BotA:2 |2,027s |
| BotA:3 |1,010s |
| BotB:0 |0s |
| BotB:1 |3,034s |
| BotB:2 |2,020s |
| BotB:3 |1,011s |

BotA:0 verletzt die unveränderte10s-Grenze im Fenster531,518–547,663s. Derselbe lebende Ground-Zustand ohne sichtbaren Gegner hat zu diesen Messpunkten keine Referenz, keinen gewöhnlichen Anchor/Goal/Hop und neutrale finale Bewegungsachsen. Der kurze bestehende Supportstrahl meldet keinen Treffer; tatsächliche tragende Kontaktgeometrie ist dadurch weder bewiesen noch ausgeschlossen. Die interne Translationsvariable darf nicht mit gemessener Ortsänderung gleichgesetzt werden. Ein weiterer enger nativer Kontakt-/Strahlvergleich wird getrennt diagnostiziert; keine allgemeine Boden- oder Referenzgrenze wird auf Verdacht erweitert.

Ein anderer beobachteter Ground-Recovery-Fall zeigt nach einem zunächst erfolglosen Seitversuch die Gegenrichtung und mehrere Meter reale Bewegung im selben Leben. Ohne bestätigten Folgepfad wird das nicht als erfolgreiche NAV-Wiederaufnahme ausgegeben. Einzelbeobachtung und wesentlich kürzerer maximaler Stillstand als bei040 begründen keine kausale oder allgemeine Erfolgsbehauptung.

Alle drei eigenen Skulls-Prozesse sind normal geschlossen und die Rohbelege erhalten. Privater Main-Verdict-SHA256 `d64285d58bc63871af6552b8503dd8aa56d623e62e867dca7fbe0c0c67c290c9`; unabhängiger Review `2159871f2681ab189ef99a4bc628f08aeac6228471e2c58b810584e885714ba1`. Keine weiteren041-Karten oder formalen3600/3600/7200s-Gates wurden nach diesem Fehler gestartet.

## Getrennte Kontaktdiagnose

041diag, Quelle `267e624367f698f9b1af8ec73cd529d3a8bc8279`, DLL `11517d865a3d200f40e3411c441299e86150d532a8563f9422e9bdcb7610e9fd`, ergänzt ausschließlich begrenzte passive Kontaktprotokolle: keine zusätzliche Engineabfrage, kein anderer Bewegungsinput oder Boden-Schwellwert.752 SDK-ASan/UBSan-Prüfungen und der eigene Windows-x86-Build bestehen. Der erste vollständige600,296s-Versuch zeigt36 andere eingefrorene Kontaktkontexte, aber keinen NULL-Stillstand. Daraus folgt kein Ursachen- oder Qualifikationsnachweis.

Der getrennte Wiederholungsversuch reproduziert lebende lang anhaltende Stillstände mit tatsächlichem Wechsel zwischen nativem Standpolygon/Referenz und NULL bei unveränderter Position. Auf einer positiven Schräge liegt die ebene Bodenprojektion etwa0,292m unter dem Fuß-Bezugspunkt; der bestehende Strahl endet bereits0,05m darunter. Ein zweiter Kontext zeigt ein vertikales Standpolygon und beweist daher keinen Boden. Der Formatter liest den tatsächlichen Standzeiger in beiden Zweigen direkt; NULL ist hier kein ausgelassenes Logfeld. Nach fünf bereits freigegebenen, physisch erfolglosen Ausweichrichtungen kann der unveränderte Tried-Zustand weitere Versuche im selben Stillstand verhindern. Bodenmessung und dieser separate Liveness-Pfad bleiben getrennte Befunde; keine allgemeine Erweiterung erhält allein daraus eine Freigabe.

Nach546,002896s und480 korrekten Statusabfragen beendet Main den optional bis1800s vorgesehenen Diagnoseversuch ausdrücklich administrativ nach ausreichender Reproduktion. `observation_completed=false` und `KeyboardInterrupt()` bleiben erhalten. Alle drei eigenen Prozesse schließen über den normalen Cleanup, ohne Force oder Cleanupfehler. Das ist ein unvollständiger Diagnoselauf, niemals ein bestandenes Zeitgate. Eine weitere ausschließlich messende Abfrage innerhalb der nativen StepDn-Grenze wird vorbereitet; deren Ergebnis und Wirkung sind noch unbekannt. [Binäranalyse und Werkzeugentscheidung](../../decisions/2026-11-09-retail107-contact-query-analysis.md) halten die Retail1.07-Grenzen fest.

## Versorgung und weitere Gates

Die neue v14-Versorgung ist vollständig und normal beendet: zehn frische Einzelbot-Beitritte,597 gültige Ein-Bot-Abfragen und26 tatsächliche Waffenzielstarts. Die festgelegten ersten zehn Ziele sind sämtlich über typisierte ausgewählte Item-Entity, passenden neu erworbenen Besitz, denselben nativen Zielendtick und lokalen Bewegungs-/Pickupkontext korroboriert: **10/10**. Main und zwei unabhängige vollständige Rohlogprüfungen bestätigen ausschließlich dieses begrenzte Supply-Gate. `goal_picked=0` ist kein Erfolgssensor; ein direktes ReceiveItem-Ereignis und ein allgemeiner geometrischer Pickup-Radius werden nicht behauptet.

Alle zehn festen Initialleben bleiben erhalten:8,40/3,15/5,60/3,15/4,85/3,45/9,85/3,80/3,50/3,45s bis zum ersten sinnvollen Pickup, Median **3,65s**, Nearest-Rank-P95 **9,85s**. Die unveränderten15s-/30s-Grenzen sind erfüllt. Beiläufige Shotgun-Erwerbe werden für die initiale Latenz gezählt und nicht fälschlich dem ausgewählten Flamerziel zugeschrieben. Spätere Leben ersetzen keinen fehlenden Erstfall. Originale Map-/NAV-CRC und unveränderte minimale60s-/Drain520s-Regeln sind nachgewiesen.

Sämtliche26 Starts bleiben sichtbar. Ein späterer Cannon-Versuch auf Rang23 in Fall9 liegt außerhalb der festen ersten zehn und bleibt am normalen Fallende rechtszensiert; er zählt weder als Erfolg noch als verschwiegener Fehlschlag. Der Fall3-Cannonabschluss bei70,7s liegt innerhalb der bereits vorher nativ protokollierten einmaligen Relocation-Frist72,027s; die nach mindestens60s fortgesetzte Beobachtung erweitert keine KI-Deadline.

Alle elf eigenen Prozesse sind normal geschlossen. Tatsächliche Server- und Bot-Kernelstartticks, elf getrennte systemd-Invocation-Identitäten und die zehn bereits abgefragten Population0-Antworten sind jetzt persistiert. WM_CLOSE erzeugt bei den Botprozessen terminalen Status1; der Server hat Status0. Diese Rohwerte bleiben erhalten, kein Force-Cleanup und kein erfundener Exitstatus0. Beim Cannon beträgt der größte beobachtete Abstand zur Item-Platzierung4,117m, davon etwa1,215m horizontal/3,934m vertikal; der Flugkontext erklärt die unterschiedlichen Bezugspunkte, beweist aber keinen exakten Kollisionsradius.

Begrenzter privater Supply-Verdict-SHA256 `2faa6be94decd01999dd0d092f2728a7b6aae304abde250fac67f199d5af6f3f`; unabhängige Rohprüfungen `801f3baedd6486fb3e071f869f1f385d1a8f03c68c3b10eeabaf23baf4c3875d` und `c75189752f5231b6754d5a18416b2c40287a49219a3a7137843c377ee703264d`. Der Verdict bleibt `qualified=false` für den Gesamtkandidaten; Skulls ist weiterhin FAIL.

Ein separater originaler Retail/Wine-Client beobachtet120,198s auf Red Station mit100 gültigen Zwei-Spieler-Abfragen. Gerenderte Welt, zwei tatsächliche Bot-Kills gegen den unveränderten Client und damit mindestens ein zwischenzeitlicher normaler Wiedereinstieg sind sichtbar. Alle zwölf gewöhnlichen Inputaufrufe sind abgeschlossen; einzelne Bewegungs-/Jumpwirkungen lassen sich aus diesen drei Screenshots wegen Tod/Respawn nicht kausal abgrenzen. Alle Originalhashes bleiben erhalten und alle vier eigenen Spiel-/Displayprozesse sind normal geschlossen. Dies ist ein begrenzter Join-/Combat-Interop-Nachweis, keine vollständige Gameplay-, Windows-, WAN- oder Gesamtfreigabe. Der getrennte gezielte041b-Lauf beobachtet120,184725s mit107/107 korrekten Zwei-Spieler-Abfragen. Unmittelbar vor und nach der einzigen dreisekündigen Vorwärtseingabe zeigen beide tatsächlich geprüften Bilder100 Gesundheit, dieselbe Colt-Perspektive und unveränderte0/0-Spielstände, aber deutlich unterschiedliche HUD-Positionen. Keine Todes-/Killfeed-Ereignisse, Gegenrichtung oder andere Aktion liegt in der Bildklammer. Main und unabhängiger Bild-/Rohlogreview bestätigen begrenzte tatsächliche Bewegung im selben Leben. Der Inputwrapper dauert3,594s, die gesamte Bildklammer3,827s; daraus wird weder exakte Geschwindigkeit noch ein Treffer oder Sprung abgeleitet. Auch hier bleiben alle Originaldateien unverändert und alle vier eigenen Prozesse schließen normal. Privater begrenzter Retail-Gameplay-Verdict `3f1ddae5618e078aa27f9ee0d7c5bc8c2ad73a2a13864021362f323b025b67ce`, unabhängiger Review `3fe495e7e4f65adf354ea739b03d7e7b9f88ab11bedeb28f20ee83c651e9dfaa`. Der eingefrorene Harness-Rohstatus bleibt unverändert; die Bildadjudikation steht getrennt im Verdict. Skulls bleibt FAIL, keine Gesamtfreigabe.

Alle neun Original-NAV-Dateien bestehen auf dem041-Quellstand erneut den byteidentischen Rundlauf und221.682 SDK-ASan/UBSan-Parser-/Suchprüfungen, einschließlich aller Red-Station-Paare mit unveränderten193 Punkten/879 gerichteten Kanten. Keine privaten NAV-Inhalte werden veröffentlicht.

Finale Feature-/Waffen-/Sonderaktions-/Retail-/Karten-/Stunden-/Ressourcen-/Recovery-Gates und der autorisierte gestaffelte Rollout aller sechs Instanzen samt900s-Flottenprüfung bleiben offen. Die öffentlichen fünf Produktionsinstanzen und der bisherige Entwicklungsstand bleiben unverändert. Die bestehende Transfermatrix bleibt ausdrücklich ein039-Snapshot; historische039-/040-FAILs und Teilnachweise bleiben erhalten. Keine diagnostische DLL erhält Qualifikationszeit.
