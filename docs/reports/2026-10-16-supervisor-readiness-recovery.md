# Supervisor: Bereitschaft nach einem Disconnect wiederherstellen

Ausgangspunkt: Supervisor-Branch `11b57e74c8f990e631822dc6b1472a6a1918c7ea` / PR #3. Ein bereits erfolgreich beigetretener Client konnte später die Verbindung verlieren und trotzdem als Prozess weiterlaufen. `Test-PopulationNativeReady` erkannte den Fehler korrekt, doch die zuvor gelöschte Join-Deadline wurde nicht erneut gesetzt. Der Controller blockierte weitere Starts unbegrenzt, ohne die getrennte Gruppe zu ersetzen.

Die Korrektur setzt bei späterem Bereitschaftsverlust erneut die bestehende 45-Sekunden-Frist, einmal pro zusammenhängendem Ausfall. Wiederhergestellte Bereitschaft hebt sie auf. Bei Ablauf greift der vorhandene identitätsgeprüfte Stop mit anschließendem Cooldown. `ObserveOnly` steuert keine Prozesse und setzt keine neue Frist. Ereignis: `ReadinessLost`. Keine Änderungen an GameMP, Engine, Entities oder qualifizierter DLL.

## Prüfung am 16.10.2026

- Neuer Regressionstest mit echten PowerShell-Kindprozessen und tatsächlichem Retail-Join-/BotDriver-/Disconnect-Logformat: vor der Änderung reproduzierbar FAIL (`Disconnected live client was not recovered within bounded readiness timeout`).
- Nach der Änderung PASS: dauerhaft getrennter, noch laufender Client wird innerhalb der Frist ersetzt (zwei Starts); kurzer Bereitschaftsverlust wird aufgehoben (ein Start).
- Voller portabler PowerShell-Scope: 23 Suiten PASS auf Shadow/PowerShell 7.6.6, einschließlich CLI-/UDP-/Prozessidentitätsadapter und neuer Regression. Wie im bestehenden Test-Publication-Runner bleiben RetailCleanup (benötigt eigenen Spieltest) und lokale Paketfixtures (benötigen qualifizierte SDK-Artefakte) ausgenommen.
- Unveränderte Python-Fixtures aus frisch extrahiertem Git-Archiv von `11b57e7` separat auf Linux: 25 + 9 + 10 = 44 Tests PASS. Verify-SourceProvenance: alle 13 veröffentlichten Quellen und exakte Original-Captures PASS.
- Der bestehende kombinierte Runner wurde wegen fehlender Python-Laufzeit auf Shadow nicht als ein einzelner Aufruf ausgeführt. Die beiden Teile wurden getrennt geprüft. Kein neuer nativer Supervisor-Spiel-Lifecycle oder 24/7-Test aus dieser Regression ableiten.

Private Rohbelege: Shadow `.codex/evidence/supervisor-readiness-recovery-20261016/full-regression/`. Neue echte Spieleläufe zur unabhängigen Wine-Sync-Untersuchung sind getrennte Tests, keine Supervisor-Abnahme. Merge und weitere native Recovery-/Race-/Controllerausfall-Prüfungen bleiben eigene Gates.


## Ergänzung: native Recovery und Query-Ausfall, 21:21 UTC

Die gezielte native Abnahme bestand mit einem echten vorbereiteten Retail-1.07-Windows-BotClient, der qualifizierten 61DC-GameMP-DLL und einem getrennten unveränderten Retail-Dedicated unter Ubuntu 24.04.4 / Wine 9. Der Dedicated verwendete den isoliert geprüften nativen mitgelieferten CRT-Override. Produktionsskript-SHA256: `9E4271614334780C179A8B550B8E96B78A64865B86189AE5DFBCBB06A536CCB8` aus Commit `056db9c6ae585c37232d9afa7855accc5e625236`.

Eine ausschließlich auf Quelladresse und beide Ports dieses Testservers begrenzte 90-Sekunden-Netzsperre erzeugte 30 `QueryUncertain`-Ereignisse. Während dieses Intervalls startete keine zusätzliche Gruppe; nach Freigabe blieb der bisherige Client verbunden. Anschließend wurde nur der Spielport für 330 Sekunden gesperrt, während die echte UDP-Abfrage weiter erreichbar blieb. Nach dem nativen Verbindungsverlust lief der Clientprozess weiter. `ReadinessLost` wurde erkannt, nach 45,9429686 Sekunden griff `JoinTimeout` mit identitätsgeprüftem Stop. Alle vier folgenden Wiederstartverzögerungen lagen zwischen 10,6869 und 10,7607 Sekunden. Solange die Sperre wirkte, blieben neue Join-Versuche ebenfalls begrenzt. Nach Freigabe gelangen nativer Join, serverseitige CRC-Akzeptierung, BotDriver-Bereitschaft und die vollständige exakte UDP-Spielerliste erneut.

Fünf Starts, vier Timeouts; im unabhängigen Prozessmonitor maximal ein eigener Client gleichzeitig. Abschließende Stop-Anforderung, normaler Controller-Abschluss und kein eigener Recovery-Client mehr aktiv bestätigt. Die temporären Netzsperren wurden entfernt; die übrigen unabhängigen Kontrollläufe liefen weiter. Stop-Receipts heißen `window-exit-unverified`; daraus wird keine allgemeine reguläre Shutdown-Abnahme abgeleitet. Ein vorangegangener Prozesspausenversuch ohne nachgewiesenen UDP-Ausfall zählt ausdrücklich nicht als Recovery-Abnahme.

Private Rohbelege: `hetzner-supervisor-native-recovery-20261016/native-recovery-verified.json`, Controller-Ereignisse, Generations-State/Stop-Receipts, native Logs und genaue Netzsperren-Zeitpunkte. Veröffentlicht werden ausschließlich bereinigte Befunde, keine Retail-Dateien, Profile, privaten Identitäten oder Zugangsdaten.

## Ergänzung: harter Controllerabbruch, 21:23 UTC

Der separate echte Native-Test bestätigte die dokumentierte Grenze: Ein nativ bereiter Spielclient blieb nach hartem Abbruch seines Controllers aktiv. Ein neuer Controller verweigerte mit `Client already running; never adopt it.` die Übernahme; kein zweiter eigener Client entstand. Der Prüfharness hielt Prozesshandle, Executable-Pfad, Startzeit und ursprüngliche Elternkette fest und bereinigte den verbliebenen Client anschließend. Ergebnis `PASS_LIMITED_FAIL_CLOSED_ORPHAN_CONFIRMED`; privater Beleg `hard-exit-result.json`.

Das ist ein Nachweis der sicheren Neustartverweigerung und zugleich des weiterhin offenen externen Watchdogs. Es ist kein Nachweis selbsttätiger Orphan-Recovery. Ein erster Harness-Lauf scheiterte an einer während des Joins inkonsistenten UDP-Spielerliste und wurde mit bestätigtem eigenen Cleanup beendet. Nach begrenzter Behandlung solcher unsicheren Readiness-Abfragen bestand die Wiederholung; Produktionscode wurde dafür nicht geändert.

Geltungsbereich insgesamt: ein echter Client und begrenzte Recovery-/Query-/Hard-Exit-Fälle. Beliebige gleichzeitige Join-Races, exakte Einzelslotsteuerung, externer Watchdog, 12/16-Bot-Skalierung und 24-Stunden-/24/7-Betrieb bleiben offen. PR #7 ist ein gezielter Fix gegen den Entwicklungszweig von PR #3; daraus folgt keine vollständige Freigabe des Population Managers oder Änderung von main.
