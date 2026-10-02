# scripts/ – Start- und Hilfsskripte (Windows)

Alle Pfade/IPs sind am Anfang jedes Skripts konfigurierbar (`set`-Zeilen). Skripte vor dem ersten Start an die eigene Installation anpassen.

| Datei | Zweck | Phase |
|---|---|---|
| `BotStartup.ini` | Aktiviert den BotDriver im Bot-Client. Ablage: `<Bot-Client>\Scripts\BotStartup.ini` | 1+ |
| `dedicated-config/` | Konfiguration für `DedicatedServer.exe` (init.ini, 1_begin.ini, 1_end.ini). Ablage: `<Server>\Scripts\Dedicated\BotTest\` | 0 |
| `start-server.bat` | Startet den Vanilla-Dedicated-Server ( DedicatedServer.exe, sonst Menü-Fallback) | 0 |
| `start-observer.bat` | Startet den unveränderten Beobachter-Client und verbindet ihn per `+connect +quickjoin` | 0A |
| `start-bot-client.bat` | Startet den Bot-Client ( `+connect +quickjoin +script Scripts\BotStartup.ini`) | 1 |
| `start-all-bots.bat` | Startet mehrere Bot-Client-Installationen gestaffelt (`TSE-BotClient-1..4`) | 3 |
| `hash-inventur.bat` | SHA-256-Inventur einer Installation (EXE/DLLs/GROs + Version) für den Identitäts-Nachweis | 0 |

## Reihenfolge (erste Inbetriebnahme)

1. `hash-inventur.bat` für **alle drei** Installationen → Ergebnisse vergleichen (EntitiesMP/Engine/EXE/GRO müssen identisch sein)
2. `dedicated-config/` in den Server kopieren, anpassen → `start-server.bat`
3. `start-observer.bat` → Phase-0A-Tests (`TESTPROTOKOLL-PHASE-0A.md`)
4. Bot-Client vorbereiten (GameMP-Tausch laut `RUNBOOK.md`) → `start-bot-client.bat` → `TESTPROTOKOLL-PHASE-1.md`
5. Bei Erfolg: `start-all-bots.bat` (Phase 3, `PHASE-2-3-ANLEITUNG.md`)

## Hinweise

- **Auf dem Server wird niemals eine Datei getauscht** – auch nicht GameMP.dll.
- Der Bot-Client bleibt eine 1.07-Installation; 1.10-Binaries sind als Drop-in verboten (Versions-Handshake).
- `DedicatedServer.exe` loggt automatisch nach `Dedicated_<config>.log`; beim Menü-Fallback `+logfile` verwenden.
- Bei Disconnect-Meldungen: Tabelle in `TESTPROTOKOLL-PHASE-1.md` („Troubleshooting-Schnellreferenz").

## Phase-1-Diagnosewerkzeuge (01.10.2026)

- `Build-RetailGameMP.ps1`: reproduzierbarer v143-Retail-GameMP-Build; kopiert bei `-Bot` auch den gemeinsamen Botcore-Header.
- `Test-RetailJoin.ps1`: isolierter Retail-Lauf; optional `-Observer -VisibleClients -CaptureObserver`. Native TGAs unter Evidence/observer-screenshots; Fensterkonfiguration wird gesichert und wiederhergestellt. Kurze Capture-Läufe verwenden (etwa 15 MB/s), keine Capture-Aufnahme beim Soak. Cleanup bleibt hart und beweist keinen regulären Shutdown.
- `Phase1Diagnostics.ini`: nur lesende Spieler-Snapshots, ohne Zieltest.
- `Phase1Combat.ini`: fester Zielspieler 0 mit Colt und festem Sprungpuls, nativer Action-Composer; keine Navigation, keine direkte Entity-/Schadensmanipulation.
- `Test-Phase1Telemetry.ps1 -BotLog <Log> -Output <neue JSON>`: Snapshot-Auswertung mit Anzahl verworfener beschädigter Zeilen. `-QueryServer` liest zusätzlich den aktiven lokalen Vanilla-Serverstatus.
- `Test-Phase1Telemetry.Tests.ps1`: Checks für Health-/Frag-/Fire-Auswertung, beschädigte Zeilen und Schutz vorhandener Evidenz.
- `Test-RetailCleanup.Tests.ps1 -Dll <DLL> -Evidence <neuer Ordner>`: echter 30-s-Retail-Lauf mit simuliertem Stop-Process-Fehler; prüft unabhängiges Cleanup, Config-Restaurierung und archivierte Aufnahmen.
- `Phase1Respawn.ini`: langsame Standardbewegung (5 Grad/s) für den Stockmap-Test auf `Fortress.wld` im normalen Fragmatch. Vier Bot-Tode und native Respawns wurden in 180 s belegt; Spawnvariation kann das Ergebnis ändern. Nur die isolierte Server-Mapkonfiguration temporär ändern und anschließend restaurieren.

Die Test-INI-Dateien nur im isolierten BotClient verwenden. Gameplay-Gates bleiben
bis zur tatsächlichen Schadens-/Respawn- und Observer-Abnahme offen; siehe Runbook.
