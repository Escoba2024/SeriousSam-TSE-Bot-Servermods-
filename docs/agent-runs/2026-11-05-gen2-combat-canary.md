# 2026-11-05 – SSAM.AI Gen2 Combat: Build und fehlgeschlagener Live-Canary

**Ergebnis:** Neue Colt-Combat-Logik implementiert und portabel sowie nativ kompiliert, aber **kein bestandener neuer Live-Gameplay-Test**. BotB-Canary musste nach einem Join-/Identitätskonflikt abgebrochen werden. Der vorab funktionierende Gen2-Bestand läuft nach automatischem Rollback wieder mit acht Bots.

## Ausgangslage (21:32–21:50 UTC)
- Retail-1.07-Dedicated-Server online, Map Red Station. Zwei 4-Spieler-Wine-Bot-Client-Dienste.
- Aktive Gen2-DLL A/B: SHA256 `7fc94a39c3f5d9516f262d9e4d04a5cf38e6eb5ae3482976c32c952a99d30835`.
- Gen2-Referenzbuild `/srv/tse-integrated-build-20261021-04/manifest.json`, öffentliches acht-Bot-600-s-Smoke-Dokument mit Bewegungs-/Schussbelegen vorhanden. Keine vollständige M1-Dauerabnahme.
- Ursprünglich ein neunter Spieler `oogabooga` in GameSpy sichtbar; bei Canary-Preflight nur acht mit den echten Bot-Client-Logs exakt abgeglichenen Namen.

## Änderung
- `poc/botcore/bot_combat.h` plus Release-Header: Colt-Fire nur bis 18 m, Annäherung bis 3 m statt standardmäßig 8 m. Gezielte Regressionstests im `test_bot_combat.cpp`.
- Vier bestandene C++-Tests: `test_bot_combat` 0 Fehler, `test_botcore_ai` PASS, `test_bot_human_ai` 555 Checks 0 Fehler, `test_bot_navigation` PASS.
- MSVC/Wine x86-Release aus exakt gepinntem Gen2-Quellstand, 38 Source-Hashes mit der Live-Referenz verglichen. Alle bis auf `bot_combat.h` identisch.
- Kandidat `e8152fae2c62dc2da81a0c0ad7fcf7ebeec431da63de69f0c1d2a748c3498a55`, `/srv/tse-gen2-combat-20261105/build-003/manifest.json`, `build_ok=true`, `qualified=false`. Früherer experimenteller Build-002 mit zwei zusätzlichen Header-Abweichungen bewusst **nicht** eingesetzt.

## Canary / Rollback (21:53–21:57 UTC)
- Backups beider aktuellen Bot-Client-DLLs mit SHA verifiziert. Nur BotB gestoppt und mit Kandidat neu gestartet; der Dedicated Server und BotA blieben aktiv.
- BotB zeigte im echten SeriousSam-Log `Cannot add player because: Player character '...' already exists in this session.` Nach 110 s waren die neuen vier BotB-Spieler nicht verifiziert. Kein Gameplay-PASS; Kandidat nicht auf BotA übertragen.
- Der automatisierte Recovery-Pfad stellte die ursprüngliche Gen2-DLL für BotB aus geprüftem Backup wieder her und startete den Dienst. Recovery-Receipt: `ORIGINAL_RESTORED`.
- Nach Wiederverbindung: GameSpy erneut acht identifizierbare Bots (u. a. BotB `MentalMarmot`, `VoidStrafe`, `ChromeRitual`, `N1GHTM4RE`), Scores von BotB stiegen zwischen 21:56:31Z und 21:57:09Z; Logs zeigen Bewegung/Zielerkennung/Kampf.
- A/B-DLL-Hashes wieder `7fc94a39...952a99d30835`, alle drei Dienste `active`. Letzte 1 MiB Clientlogs ohne SYNCBAD/Access violation/Fatal Error. Keine Dauerstabilität damit belegt.

## Offen / nächste Umsetzung
1. Untersuchen, warum beim Restart des Bot-Clients eine neu rotierte Spieleridentität als bereits vorhanden abgewiesen wird (Session-/GUID-Restzustand möglich, nicht nachgewiesen).
2. Gameplay-Test des neuen Kandidaten mit sicheren nativen Laufzeitbedingungen. Der vorhandene isolierte Runner blockiert parallel laufende Game/Wine-Prozesse; Schutzsperren nicht umgehen.
3. Erst nach erfolgreichem Join, belegter Spielaktivität und Sync-Smoke kontrolliertes Deployment auf A+B, bei Fehler automatischer Rückfall.
4. Keine Retail-Binaries, IP-Rohlogs oder privaten Spielerprofile ins Git-Repository hochladen.
