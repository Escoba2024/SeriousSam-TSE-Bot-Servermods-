# Bestehende Community-Notice im nächsten Kandidaten erhalten

Am 11.11.2026 um 21:14 UTC wurden neben dieser Entwicklung neue Notice-DLLs in allen sechs BotA-Prozessen festgestellt. Die vorhandene separate Aufgabe unter `/srv/tse-community-notices-20261111.C5Bofl` dokumentiert deren Rollout zwischen 21:02 und 21:12 UTC. Diese Änderungen stammen nicht aus dem Milestone-A-Kandidaten.

Die nächste A-Quelldatei übernimmt die exakt drei Änderungen der dortigen `Game.cpp`: standardmäßig deaktiviertes `bot_bCommunityNotice`, Registrierung des Schalters und Versand der vorhandenen Discord-Mitteilung über normales Client-Chat nach 20 Sekunden und anschließend alle 300 Sekunden. Der Bytevergleich nach Entfernung dieser drei Ergänzungen ergibt exakt die bisherige A-Quelldatei. SHA256 der übernommenen Datei: `aec5da416dd0cf09098680d4533045887b1327120124a7a479bb8e44adf78056`. Keine BotDriver- oder Navänderungen werden aus dieser fremden Aufgabe übernommen.

Dies erhält eine bereits separat ausgerollte Betriebsfunktion; die ereignisbezogenen individuellen Chat-Sitzungen aus Meilenstein B sind weiterhin nicht implementiert. Ein späterer A-Rollout muss BotA=1 und BotB=0 aus der jeweiligen vorhandenen Konfiguration erhalten. Kandidat 005 enthält diesen Schalter noch nicht und darf daher die aktive BotA-Notice-DLL nicht ersetzen. Die neue Quelldatei benötigt einen eigenen Build und native Prüfung.

Die aktuelle Live-Prüfung liest auf allen sechs Servern den tatsächlichen Sessionwert für Spawn-Unverwundbarkeit 0. Die Notice-Sicherung enthielt diesen Wert schon vor deren Rollout; daraus lässt sich nicht ableiten, wer die vorherigen eigenen Rücksetzungen von Hole und Dev auf 3 erneut geändert hat. Das bleibt unaufgeklärt. Fremde Runtime-Dateien wurden bei dieser Quellenübernahme nicht verändert.


### 23:14 UTC — neuer Dev-Syncbefund und korrigierte Live-Identität

Frische23:11:40-Flottenprüfung: alle6×8 eigene Bots, Dev zusätzlich1UNKNOWN. Dev aktuellerServerlog10BAD/1SyncDisconnect; fünf Publics0/0. Dev-Belege unverändert privat unter dev-sync-observation-2313 gespeichert (Logs mit SHA, Snapshot/PID/start/CWD, tatsächliche Mapping-Inodes/DLLs). Keine instrumentierte oder mutierende Maßnahme am externen Spieler. Weder Spawn0 noch Powerupserver noch neue009-Ursache daraus bewiesen. BestehenderDevserverfe4a77, beideBots048; kein009 produktiv.

Korrektur: die tatsächlich gehashten aktuellen BotA-DLLs sind öffentlich7fc undDev048, genau wie in den maschinenlesbaren22:38/22:59-Snapshots. Frühere Prosa mit Notice407fc/58017 als zu diesen späteren Zeitpunkten aktiv war widersprüchlich und ist zurückgenommen. Der separate21:02–21:12-Notice-Rollout ist ein historischerBeleg, sein späterer Zustand/Wechselverursacher unbekannt. Noticequellarbeit/Backups bleiben erhalten, keine eigenmächtige Wiederaktivierung. HauptberichtheaderundTabelle korrigiert; neueDeploys nur nach frischerIst-Prüfung und exklusivemZugriff.
