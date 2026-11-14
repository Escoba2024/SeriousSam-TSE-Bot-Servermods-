# Flottenabgleich mit unabhängigem zweiten Auftrag

Eine reine Leseprüfung am14.11.2026 um18:37:20UTC band die tatsächlich geladenen Botmodule an die laufenden Prozesse und fragte alle sechs Instanzen ab. Sie fand je acht eigene Bots, mit einem zusätzlichen Teilnehmer auf Red Station:

| Server | Port | Map | Bot-DLL |
|---|---:|---|---|
|Dev|25650|Red Station|Cecil048 ec820d04|
|Red Station|25600|Red Station|Gen2 7fc94a39|
|Yodeller|25610|Yodeller|Build018 6db89204|
|Skulls|25620|We Got Skulls'n'Bones Too|Build018 6db89204|
|Little Trouble|25630|Little Trouble|Build018 6db89204|
|Hole|25640|Hole|Build018 6db89204|

Das weicht vom historisch belegten eigenen Rückstelllauf17:12 ab. Ursache der Dateiveränderung ist ein zweiter, unabhängiger Projektauftrag: dessen `scope.txt` nennt ausdrücklich Build018 auf den fünf öffentlichen Servern und schließt Dev aus. `owner.json` nennt tatsächlich gehaltene Deployment-/Flotten-/Instanzlocks. Per-Instanz-Ergebnisse und Dateizeiten belegen den Publicrollout17:57–18:05 sowie einen nachfolgenden Namensrefresh bis18:19. Es wurden ausschließlich gemeinsame Projektbelege gelesen, keine fremden Chat-/Sitzungsinternas. Fremde Prozesse und neuere Identitätsdaten blieben unangetastet.

Der dortige Abschlussaudit18:09 meldet für Red zuvor zehn neue BAD-Syncs und einen Disconnect, danach Rückroll auf Gen2 und90,117s begrenztes Nachbeobachtungsfenster ohne weitere Syncereignisse. Diese fremden Projektbelege sind keine von uns wiederholte Fehlerursachenanalyse und keine Langzeitfreigabe. Die vier anderen018-Instanzen haben dort je90s begrenzte Aktivitätsbelege; deren Zähler werden nicht mit unseren früheren Fenstern addiert. Der eigene18:37-Audit bestätigt Module und Belegung, kein neues volles Aktivitäts-/Regel-/Namens-/GUID-Gate.

Der Nutzer wurde über die widersprüchlichen Liveaufträge informiert und hat ausdrücklich entschieden: **aktuellen Stand behalten; isoliert weiterentwickeln**. Damit keine erneute Rückstellung durch diesen Auftrag. Das vorher angezeigte Buildstatusbild bleibt hinsichtlich seiner Livezeile auf dem früheren17:16-Stand und ist überholt; die Entwicklungsaussagen zu018/019/020 bleiben davon getrennt.

Die fremden Botstarts/Namensjobs überlappen unseren geschlossenen18:11–18:16-Navigationslauf und bilden zusätzliche Hostlast. Eine genaue CPU-Spikezuordnung ist nicht belegt. Vor weiteren nativen Fenstern sind aktuelle fremde Jobs und gemeinsame technische Sperren erneut zu prüfen. A ist nicht abgeschlossen, B nicht begonnen.

Private Belege:
- RootEV/fleet-module-status-20261114-1837-private.json: eigener frischer Modul-/Queryaudit.
- /srv/tse-public-build018-20261114-1855: scope/owner/build-final-audit/red-sync-rollback-ended und Namensabschluss des unabhängigen Auftrags.
- /srv/tse-cecil-full-20261107/.codex/evidence/restart-fleet-20261111-public-build018-20261114-1855: dessen instanzbezogene Ergebnisse.

Keine Spieleridentitäten oder privaten Rohlogs werden mit diesem Bericht veröffentlicht.
