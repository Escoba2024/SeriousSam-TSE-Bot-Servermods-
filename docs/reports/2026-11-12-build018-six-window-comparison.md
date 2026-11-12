# Build018: sechs abgeschlossene Vergleiche gegen die öffentliche Alt-DLL

Stand: 12.11.2026 21:21:28 MEZ. Die Uhrzeit bezeichnet den letzten vollständig ausgewerteten A3-Abschluss.

Die neue KI erzielt in jedem der sechs begrenzten Vergleiche mehr direkte Abschüsse gegen die alte KI als umgekehrt. Die gemeinsame Auswertung umfasst MITTEL, STARK und DEMON mit jeweils vertauschten Startpositionen. Dies ist ein belegter Fortschritt gegenüber der Alt-DLL. Build018 hat weiterhin keine Gesamtfreigabe für Dev oder die öffentliche Flotte. Insbesondere ist STARK in dieser Stichprobe nicht eindeutig stärker als MITTEL.

## Artefakt und Vergleichsgrenze

Gameplay-Quelle: Commit 1802fb3f0720b53feb032abfe2c2a83407bfea6e. DLL: SHA256 6db89204e33dc7d76ecdfed68055d2b75bde4950475793a57101fd0cefcb8e4a, 428544 Byte. Der zugehörige Quellbaum wurde als e53d6c601a80f627047c7a3aa6b3b36b81983b8a tatsächlich von GitHub zurückgeholt. Die späteren Berichte benötigen eine eigene Veröffentlichung.

Jeder abgeschlossene Vergleich beobachtet 120 Sekunden, vier alte und vier neue Bots sowie den unveränderten Vanilla-Teilnehmer. Alle neun neutralen Anfangszustände passen streng zur gleichen Referenz. Diese Anfangserfassung beweist keinen allerersten gültigen Respawnzustand. Es gab keine Spielzustandsschreibzugriffe durch den Schadensbeobachter.

## Ergebnisse

| Stufe | Startverteilung | Direkte Abschüsse neu → alt | Direkte Abschüsse alt → neu | Gesamtfrags neu / alt | Leben mit nützlicher Zusatzwaffe neu / alt |
| --- | --- | ---: | ---: | ---: | --- |
| MITTEL | normal | 20 | 5 | 27 / 14 | 12 von 15 / 4 von 32 |
| MITTEL | vertauscht | 11 | 7 | 22 / 19 | 13 von 21 / 1 von 27 |
| STARK | normal, separate Ressourcenfolgeprobe | 19 | 7 | 23 / 13 | 14 von 17 / 3 von 28 |
| STARK | vertauscht | 12 | 6 | 17 / 17 | 11 von 14 / 3 von 29 |
| DEMON | normal | 27 | 4 | 32 / 9 | 10 von 14 / 3 von 35 |
| DEMON | vertauscht | 20 | 4 | 27 / 15 | 11 von 19 / 2 von 35 |

Direkt zwischen den verglichenen Gruppen ergeben sich MITTEL 31:12, STARK 31:13 und DEMON 47:8. Abschüsse innerhalb derselben Gruppe und gegen den stationären Vanilla-Teilnehmer sind darin nicht enthalten. Die Gesamtfrags werden zusätzlich berichtet; sie enthalten diese anderen FFA-Abschüsse und ersetzen den direkten Vergleich nicht.

Die vorhandene Inventarmaske 0x3df8 definiert hier die nützliche Zusatzwaffe. Ihr Besitz wurde in 71 von 100 beobachteten neuen Leben und 16 von 186 alten Leben gesehen. Ein Leben ohne diese Zusatzwaffe wird nicht als buchstäblich waffenlos bezeichnet. Die neuen Leben umfassen 77 beobachtete Todesfälle und 23 am Fensterende rechtszensierte Leben; die alten 167 Todesfälle und 19 rechtszensierte Leben. 22 neue beziehungsweise 155 alte abgeschlossene Leben enden ohne beobachteten Besitz einer solchen Zusatzwaffe. Erfolgslatenzen werden nicht als vollständige Lebensnenner ausgegeben. Fire-Anforderungen sind weiterhin von tatsächlichen Treffern und Abschüssen getrennt.

## Vollständigkeit der geschlossenen Belege

Alle sechs vollständigen Schadensströme wurden mit dem unveränderten strengen Analyzer geprüft. Die 1490 erfassten Damage-Ereignisse sind vollständig nach Kategorien aufgeteilt; Fremdschaden, Leichentreffer, Eigenschaden und nicht zuordenbare Fälle bleiben unterscheidbar. Für jedes Fenster stimmen die ursprünglichen Server-Abschusspaare genau mit den zugeordneten tödlichen Schadensereignissen überein. Die Originalfunktionen sind wiederhergestellt und der Beobachter ist getrennt.

Die vier Rollen wurden nach jedem Fenster normal geschlossen. Root prüfte jeweils 640 wiederhergestellte Dateihashes, die vier ruhenden Labverzeichnisse, die beiden entfernten X-Displays und die akzeptierten abgeschlossenen Logs unabhängig nach. Die tatsächlichen Build018-, Quell-, Result- und Analyzerpins stehen in der maschinenlesbaren Begleitdatei und den privaten Rohbelegen.

## Ressourcenfehler und geänderte Betriebsbedingung

Zwei frühere STARK-Versuche bleiben FAIL. Die erste Messung unterschritt die unveränderte 1,5-GiB-MemAvailable-Grenze um 12435456 Byte, die zweite trotz ausgeschlossener paralleler Testprozesse um 1302528 Byte. Diese abgebrochenen Messungen zählen nicht als vollständige Vergleichsläufe.

Root pausierte anschließend ausschließlich die beiden bisherigen Dev-Botdienste durch die bereits geprüfte normale Close-Hülle. Vorher waren acht eigene Dev-Bots, null unbekannte Teilnehmer und die bisherigen geladenen DLLs verifiziert. Ein eigener Wächter hält die Deployment-/Dev-Sperren und stellt die Originaldienste bei explizitem Abschluss, Ausnahme, Signal oder spätestens nach 35 Minuten wieder her. Gemessener RAM-Gewinn: 364425216 Byte. Der Dev-Server und die fünf öffentlichen Instanzen wurden nicht ersetzt.

Die vollständigen STARK- und DEMON-Fenster fanden unter dieser ausdrücklich dokumentierten Bedingung statt. Die niedrigsten gemessenen verfügbaren RAM-Werte lagen zwischen 1850441728 und 1941581824 Byte. Die unveränderten CPU-, RAM-, Disk- und Spielregeln wurden nicht gelockert. Das ist keine Dauerlastabnahme und kein kausaler Instrumentierungs-Overheadnachweis.

## Offene Abnahmen und Fortsetzung

- Die Paarungen stützen die Verbesserung gegen die alte KI; STARK > MITTEL ist nicht belegt. DEMON erzielt in diesen Fenstern die deutlich besseren direkten Ergebnisse. Keine Aussage über menschliches Spielniveau.
- Die fest eingegrenzte A4-Prüfung mit 480-Sekunden-Grenze, Red → Red → Red und 24 unveränderten Slotphasen wurde nach der A3-Auswertung separat gestartet. Ihr Abschluss ist nicht Teil dieser A3-Quittung.
- A1: Der typisierte Original-Shell-Startvergleich ist nativ angenommen. Der spätere V3-Lauf bricht vor Fire bei wechselndem Yaw-Gain ab. Die einfache isolierte X11-Probe bestätigt 24 von 24 angeforderte Pixeldeltas; die Ursache innerhalb Wine/Originalspiel ist noch offen.
- Ein lokal vorbereiteter Prescan-Vergleich wurde nach dem Ausfall der lokalen Arbeitsumgebung nicht nativ gestartet. Seine weitere Sicherung, unabhängige Prüfung und erneute Quellbindung sind vor einer Freigabe erforderlich.
- Die Originalanforderungen an A1, vollständige Karten-/Navigationsabnahme, 3600/3600/7200-Sekunden-Läufe, separate Wiederherstellung und Dev-zuerst-Rollout bleiben offen. A2 ist abgeschlossen, B unbegonnen.
- Delta021 ist tatsächlich vollständig wiederhergestellt und über Drive zurückgeprüft. Dieser spätere Stand braucht Delta022; ein lokaler Umgebungsausfall ist kein Nachweis einer neuen Drive-Sicherung.

[Maschinenlesbare Ergebnisse](milestone-a-20261112/build018-six-window-comparison.json).
