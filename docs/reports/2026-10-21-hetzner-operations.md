# Hetzner: Betrieb und Rückfall, 21.10.2026

## Nachgewiesene Architektur

Ein unveränderter Retail-1.07-Dedicated-Server, zwei BotClient-Prozesse mit je vier lokalen Spielern. Bot-GameMP Build04, HumanAI=1, NullRender=1, 20Hz, RosterOffset 0/4, Telemetrie=1, LogEvery=200, Diagnostik reduziert, StrafeScale=0. Yodeller/Fragmatch, acht Bots, 16 Slots. Native Netzwerk-/Physik-/Sync-Pfade bleiben aktiv. Originalclients benötigen keine Modifikation.

Jede Rolle und jedes Wine-Präfix verwendet einen eigenen Overlayfs-Mount. Originalinstallation, Spielebinaries und vorherige 61DC-DLL bleiben im Lower-Verzeichnis erhalten. Der explizite öffentliche Modus verlangt ein erfolgreiches gleiches DLL-Stundenergebnis; nur ein erfolgreicher zusätzlicher 600s-Smoke lässt die eigenen Prozesse laufen. Öffentliche Population muss alle acht Botnamen enthalten und darf weitere Menschen aufnehmen. Die originale Engine verwendet fest master.gamespy.com. Dieser heute nicht mehr auflösbare Name wird gemäß offizieller HOSTS-Anleitung auf die aktuell DNS-geprüfte Adresse von master.333networks.com umgeleitet (am Testtag 81.205.81.173). Ein neuer Patch-Override ist in Original-Retail nicht verfügbar. Der Harness prüft die tatsächliche Legacy-Namensauflösung vor jedem öffentlichen Start. ser_bReportSyncBad=1, ser_bReportSyncOK=1; Kickgrenzwert bleibt 10.

## Start und Status

Arbeitsbaum: `/srv/tse-integration-20261021`. Kein zweiter Start neben einer laufenden Flotte. Vorher aktuelle Prozessidentitäten, Belegung von 25600/25601, freien Speicher und laufende Benchmarks prüfen. Der Harness prüft eigene Runtime-Sperre, freie Ports, originale Binärhashes und die gleichartige Stundenabnahme erneut.

```sh
python3 /srv/tse-integration-20261021/tools/qualify_integrated_wine.py \
  --runtime /srv/tse-integration-public-20261021 \
  --template /srv/tse-wine-runtime-20261020/public-eight-20261020-2140 \
  --vanilla /srv/tse-wine-runtime-20261020/install/vanilla \
  --build-manifest /srv/tse-integrated-build-20261021-04/manifest.json \
  --stage eight --duration 600 --port 25600 --display :118 \
  --public-address 91.99.75.33 \
  --acceptance-report /srv/tse-integration-runtime-20261021/eight-100513/result.json
```

Vor dem tatsächlichen Start kann derselbe Aufruf mit `--prepare-only` ausschließlich Kopien/Mounts/Hashes prüfen und anschließend ausräumen; das ist kein Laufzeit-PASS. Tatsächlicher Start erhält ein eindeutiges `eight-<UTC>-<Zufall>`-Verzeichnis. `result.json` enthält Status, Prozessidentitäten, Display, cgroup und Mountliste. Erfolgszustand: `PASS_PUBLIC_SMOKE` mit `left_running=true`; zusätzlich UDP-Query auf 25601 und frische Masterliste prüfen. Niemals einfach das lexikografisch letzte Ergebnis als Produktion annehmen: spätere Preflights haben ebenfalls eigene Verzeichnisse.

Private Rohdaten und Spielebinaries verbleiben auf dem Host. Rohlogs regelmäßig nach geprüftem Archivierungsverfahren rotieren; keine unkontrollierte Löschung fremder Evidenz. Der Host hatte vor dem Start etwa 1,8GiB frei, daher vorhandene Installationen nicht vollständig duplizieren. Kein neuer Dienst oder Kostenauftrag.

## Kontrollierter Stop und Rückfall

Zusätzliche eigene Originalobserver zuerst per WM_CLOSE beenden; fremden Spielern keine Slots entziehen. Für ein tatsächlich reteniertes qualifiziertes Ergebnis:

```sh
python3 /srv/tse-integration-20261021/tools/stop_integrated_public_wine.py \
  --result /ABSOLUTER/AKTUELLER/LAUF/result.json
```

Das Werkzeug prüft PID, Linux-Startzeit und CWD vor jedem Signal, registrierte Spielprogramme und Displaybelegung. Zuerst WM_CLOSE, begrenztes TERM/KILL nur für eigene Prozesse, prefix-spezifischer wineserver-Abschluss, anschließend ausschließlich eigene Overlay-Mounts. Die ursprüngliche Installation braucht keine DLL-Rückkopie, weil sie unverändert bleibt. Ein eigener abgebrochener öffentlicher Versuch hat das normale Cleanup einschließlich aller sechs Unmounts tatsächlich durchlaufen.

Zusätzliche Sicherung: `/srv/tse-public-backup-20261021/previous-runtime.tar` und `manifest.json`. 415 Dateien einschließlich vollständiger alter GameMP-DLLs, Skripte/Konfigurationen, Profile, Logs und Launcher wurden archiviert, in ein separates Verzeichnis extrahiert und bytegenau per SHA256 geprüft. Große unveränderte Spielearchive verbleiben im erhaltenen Lower-Bestand. Geschützte Bot-DLL muss `61dc27e0e7b80badcf9ae705c30fca88edd3935737715dffff59e90c26f1fef9` ergeben. Vor Wiederverwendung alter Launcher deren Display :102, Prefixe und tatsächliche Legacy-Master-Namensauflösung prüfen; geerbte neuere Mastervariablen in der Testvorlage sind keine belegte Retail-Konfiguration. Alte DLL ausschließlich mit ihren bekannten HetznerFleet-Symbolen starten, nicht mit unbekannten neuen Human-/NullRender-Flags.

Archiv ausschließlich in ein neues eigenes Prüf-/Rückfallverzeichnis extrahieren, niemals blind über einen laufenden Server. Ein Rückfall erhält eigene Overlay-Kopien, originale 61DC-DLL, bekannte Profile und die geprüfte öffentliche Legacy-Master-Namensauflösung. Hashes/Ports/Population/Query/Originalbeitritt und frische Masterliste nach jedem Neustart erneut prüfen. Es wird keine neue öffentliche 61DC-Stundenabnahme behauptet.

## Kapazität und offene Arbeiten

Acht aktive Bots sind mit zwei Viererprozessen gemessen. Zusätzliche Botprozesse und mehrere Instanzen erst isoliert qualifizieren. 16 Slots schließen acht weitere Bots plus menschliche Teilnehmer in derselben Instanz aus. Dynamische Population, Supervisor/automatischer Reboot-Neustart, 24/7, Mehrkarten- und 16+-Bot-Betrieb bleiben offen. Ohne qualifizierten Supervisor bedeutet ein Hostneustart einen manuellen kontrollierten Neustart mit den oben genannten Gates.

## Legacy-Master-DNS und dessen Rücknahme

Offizielle Grundlage: https://333networks.com/instructions/hosts und https://333networks.com/instructions/serioussam/s. Keine Engine-/Dedicated-/Originalclient-Binary gepatcht, kein Zusatzprogramm installiert. Originale `/etc/hosts` liegt als `hosts.before` im privaten Sicherungsverzeichnis; `legacy-master-resolution.json` enthält Originalhash, exakt hinzugefügte markierte Zeile und Ziel. Zur Rücknahme ausschließlich die eigene Zeile mit Marker `alpha-gaming-retail107-20261021` nach Gegenprüfung entfernen; spätere fremde Hosts-Änderungen erhalten. Danach ist die Legacy-Masterverbindung erwartbar wieder ohne Auflösung. Für Spieler-PCs mit unverändertem alten Retail kann entsprechend eine eigene HOSTS-Einrichtung notwendig sein; dies ist keine Änderung der Spielbinaries.
