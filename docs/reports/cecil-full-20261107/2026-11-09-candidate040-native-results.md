# Normal040: Versorgung begrenzt bestanden, Skulls fehlgeschlagen

Normal040 ist **nicht für den Rollout qualifiziert**. Die neue vollständige Einzelbot-Versorgung besteht ihr unverändertes Teilgate; der vollständige Acht-Bot-Skulls-Lauf scheitert am Stillstandsgate. Keine weiteren Karten oder formalen Stundenfenster wurden für040 begonnen. Die sechs öffentlichen Instanzen bleiben unverändert.

Quelle `0c48a4f9f92d993ea1c5a5a9fed82d5acea08db1`, Tree `7cb63a29e1a072511c101f68c2362a7f92f71724`, normale PE32-x86-DLL `4925d3f38c43795730d5d73d9cffd73681f92200820d51e0fe994cd6651f84c5`. [Bereinigtes Buildmanifest](build040.json). Alle15 MSVC-Übersetzungseinheiten und der Link bestehen. Die zusammengeführte SDK107-Bridge besteht633 ASan/UBSan-Prüfungen; die Korrekturen wurden durch Main und unabhängig geprüft. Build, portable Prüfungen und Teilgate ersetzen keine native Gesamtqualifikation.

040 trennt die passive Beobachtung einer unveränderten Offgraph-Position von der aktuellen physischen Freigabe einer Escape-Bewegung. Fehlende Referenz oder ein verschobener Supportcast löschen nicht mehr allein die Positionsbeobachtung; jede tatsächlich ausgegebene Recovery-Bewegung braucht weiterhin aktuellen Support und geprüfte Wand-/Bodenstrahlen. Zusätzlich kann der eng begrenzte Grounded-Replan einen nach einem Flug am Boden verbliebenen, hoch liegenden Routenursprung auf den bereits gefundenen ursprünglichen Bodenknoten zurücksetzen. Ziel, Deadline und globale Locks werden dabei nicht erneuert. Die nativen Ergebnisse unten bestimmen die verbleibenden Grenzen dieser Änderungen.

## Vollständige Versorgungskohorte v13

Zehn aufeinanderfolgende frische Einzelbot-Beitritte auf unverändertem Red Station sind abgeschlossen: zehn unterschiedliche Bot-PID-/Kernel-Startepochen,592 gültige Abfragen mit genau einem eigenen Bot, ursprüngliche Map-CRC `ff3776e0` und NAV-CRC `e4571656`. Alle33 tatsächlichen Waffenzielstarts bleiben erhalten. Die ersten zehn bilden die feste chronologische Erwerbskohorte; kein Versuch wurde entfernt, ersetzt oder nachträglich auf einen späteren Erfolg umgestellt. Es gelten unverändert mindestens60s je Fall, Drain eines offenen First-10-Versuchs bis zum nativen Ende samt späterer vollständiger State-Barriere und eine administrative Obergrenze520s. Die finale vollständige Rohlog-Reconciliation ist nicht zensiert.

**10/10** erste gewählte, typisiert aufnehmbare Waffenziele haben korroborierte Erwerbe. Der Nachweis verbindet ausgewählte Item-Entity und Waffentyp, neu gesetztes passendes Inventarbit, lokales Annähern, genau einen Bot und `GoalEnd unavailable` im selben Tick. Letzteres allein ist kein Erfolg; auch der bei diesen Respawnitems protokollierte Wert `goal_picked=0` wird nicht als Erwerbsbeweis verwendet. Main und zwei unabhängige Reviews bestätigen die Kohorte.

Die zehn festen initialen Leben ergeben9,65/3,95/10,15/11,35/5,15/5,20/18,00/9,95/5,90/9,90s bis zum ersten sinnvollen Waffenpickup. Median **9,775s** und Nearest-Rank-P95 **18,00s** erfüllen die unveränderten15s-/30s-Grenzen. Ein späteres Respawnleben ersetzt keinen Fall. Im zweiten Fall zählt der tatsächlich zuerst erworbene beiläufige Shotgun-Pickup zur Initiallatenz; das spätere ausgewählte Flamerziel wird gesondert über sein eigenes Waffenbit nachgewiesen.

Der Cannon-Erwerb in Fall1 erhält neu das Bit8192. Beobachtet sind der ursprüngliche Anchor-Hinweis63, nachfolgende Hops68/69/71 sowie dazwischen Anchor72 im Flug. Daraus wird keine lückenlos unbeobachtete Anchorfolge rekonstruiert. Beim Pickup beträgt der Abstand vom Player-Fuß zur protokollierten Item-Platzierung etwa4,053m, davon nur0,901m horizontal und3,952m vertikal. Beim Flamer in Fall2 sind es4,407m, davon2,917m horizontal und3,304m vertikal; benachbarte Zustände zeigen die Flug-/Fallbewegung. Diese Platzierungsabstände sind kein gemessener Pickup-Radius. Es wird keine neue2,5m-Grenze eingeführt und kein exaktes Collision-/ReceiveItem-Ereignis behauptet; die Zuordnung beruht auf den kombinierten nativen Belegen.

Der echte begrenzte Supply-Nachweis bleibt ausdrücklich `qualified=false` für den Gesamtkandidaten. SHA256 seines privaten Verdicts: `436442c66ca8c8ef91ad699e59b3f3ef2a6a8008453fbba797b47ad1f50ab560`.

## Vollständiger Skulls-Lauf

Acht Bots sind **600,006024632s** mit vollständiger Fensterabdeckung beobachtet. Alle acht erhöhen ihren Score;52 Todesereignisse und keine neuen Monitor-/Sync-/CRC-/Fatalfehler sind erfasst. Sechs Slots überschreiten trotzdem die unveränderte Grenze10s für unbegründeten Stillstand:

| Slot | Längster unbegründeter Stillstand |
| --- | ---: |
| BotA:0 |158,354s |
| BotA:2 |46,379s |
| BotA:3 |84,746s |
| BotB:1 |39,340s |
| BotB:2 |228,921s |
| BotB:3 |100,853s |

Damit ist das Verhaltensgate **fehlgeschlagen**. Aus freigegebenen Eingaben, freien Strahlen oder kurzen Escapes wird keine erfolgreiche körperliche Bewegung oder NAV-Wiederaufnahme abgeleitet. Alle drei eigenen normalen Prozesse sind anschließend normal geschlossen, die Rohlogs erhalten. Andere Karten und die formalen3600-/3600-/7200s-Läufe wurden nach dem bekannten Fehler nicht gestartet.

## Bindung und Grenzen der Belege

Die Supply-Bots sind über ihre zehn gespeicherten PID-/Kernel-Starttick-Paare gebunden. Die Serveridentität wurde zur Laufzeit geprüft; sein Kernel-Starttick ist in den ursprünglichen Runnerartefakten nicht persistiert. Ergänzend liegen systemd-PID-/Startzeit-/Invocation-Daten und die normalen Abschlusslogs vor. Der erfolgreiche Population0-/Cgroup-Drain wird vom eingefrorenen Runner erzwungen und durch die aufeinanderfolgenden Starts und fehlerfreien Cleanup-Ergebnisse gestützt; einzelne Population0-Antworten sind nicht separat gespeichert.

Die zehn Bot-Units melden nach normalem WM_CLOSE, Spielende und Renderer-Cleanup Exitstatus1; der Server meldet Exitstatus0. Daraus wird weder ein nicht beobachteter Sync-/Fatalfehler noch ein Bot-Exitstatus0 erfunden. Kein Force-Cleanup wurde verwendet. Die normale Beendigung und die Rohlog-Fehlerprüfung sind getrennte Aussagen.

Private Artefakte einschließlich vollständiger Builddaten, Protokoll, Verdict, beider unabhängiger Reviews, Rohlogs, Monitorzeitreihe und Cleanup sind in einem privaten Hashindex gebunden. SHA256 des Aggregatbelegs: `32a6238a15e5bbb5a06bb78f9e5b23df930fdf0d8f33bdc7ced1e26f385e4c07`. Private Pfade, Rohlogs, Profile, Retail-Binaries und originale NAV-Inhalte werden nicht veröffentlicht.

## Separate Folgemessung und offene Gates

Die getrennte private Diagnose aus `a5a9fd973dae6805a11654b87ed39f28a8a6ea42`, DLL `a050d1b0e2f93db2a7621bf6d1b20f6cd3846653d4abe6bada80272757ec796d`, ist nach **600,002959462s** mit536 gültigen Abfragen und normalem Cleanup aller drei eigenen Prozesse abgeschlossen. Sie protokolliert aktuelle native Standpolygon-/Kollisionsmetadaten und bereits vorhandene Cast-Ergebnisse: keine zusätzlichen Diagnose-Rays oder Engine-/World-Abfragen, keine geänderten Aktionen oder Supportschwellen. Die getrennte SDK-Bridge besteht643 ASan/UBSan-Prüfungen. Loggingkosten und vollständige Laufzeitgleichheit sind damit nicht gemessen; diese Diagnose erhält keine Qualifikationszeit.

Bei einem einzelnen reproduzierten A3-Stillstand stimmen18 abgelehnte Bodenstrahlen exakt mit dem aktuellen nativen Standpolygon und dessen WorldBase-Owner überein. Die normalisierte Flächennormale `(0,9175556;0,3976075;0)` unterschreitet die zusätzliche allgemeine0,5-Supportschwelle. Eine protokollierte Strahldistanz2,4784336m ab1m über dem Fuß ergibt1,4784336m Höhenabfall, innerhalb der nativen StepDn-Höhe1,5m; StepUp ist1m. Die Kollisionsmetadaten zeigen Handle-Radius und -Höhe jeweils0,5m. Die aus diesen Messwerten abgeleitete Kugel-/Ebenengeometrie erklärt, warum ein kurzer Strahl unter dem Platzierungsfuß keinen Boden findet, während die Kollisionskugel noch auf derselben Fläche steht. Dies belegt diese konkrete Sensor-/Kontaktabweichung, nicht die Ursachen sämtlicher Stillstände aus Normal040.

Der beobachtete A3 löst sich später mit sichtbarem Gegner und Human-Bewegungsbesitz; das wird nicht als erfolgreiche Ground-Recovery gezählt. Ein anderer Abschnitt ohne nahen Originalknoten zeigt zusätzlich, dass alle296 Originalpunkte außerhalb32m liegen; die nächsten liegen etwa51,7–55,1m entfernt. Auch dieser Bot erhält später nach Kampfbewegung wieder einen NAV-Pfad. Weder permanentes Versagen noch eine erfolgreiche bisherige Recovery wird daraus behauptet. Der finale unabhängige private Diagnosebeleg hat SHA256 `10e2222a2297420163b0b963f428c55339da984b65cd4cec505b3300abf6c204`. Eng begrenzte Korrekturen werden separat geprüft; ihre native Wirkung ist noch offen.

Der bestehende [41-Bereiche-Transferstatus](transfer-status.md) bleibt ausdrücklich ein **039-Snapshot**; seine Matrix wird durch diese040-Ergebnisse weder umbenannt noch auf040 umgebunden. [039-Skulls- und Versorgungsfehler](2026-11-09-candidate039-native-results.md) bleiben unverändert dokumentiert. Weitere finale Features, Karten, Waffen-/Sonderaktionsnachweise, Original-Retail-Gameplay,3600/3600/7200s, vergleichbare CPU-/RSS-Messung, Recovery und gestaffelter Rollout aller sechs Instanzen samt gemeinsamer900s-Flottenprüfung bleiben offen. Jede weitere Verhaltens-DLL benötigt neue Nachweise; kein040-Teilgate wird automatisch übertragen.
