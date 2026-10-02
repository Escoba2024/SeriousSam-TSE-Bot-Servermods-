# Runbook: Pfad-D-PoC bauen und testen
## Vanilla-kompatible Bots für Serious Sam: TSE 1.07

> Begleitdokument zu `VERIFIKATION.md` (dort: alle Begründungen und Quellenangaben).
> Ziel: 1 Bot auf einem **unmodifizierten** TSE-1.07-Dedicated-Server, sichtbar und
> spielbar für **unmodifizierte** Vanilla-Clients.

## 🔧 Execution-Kit (Ergänzung 30.09.2026)

Zu diesem Runbook gehören jetzt ausführbare Hilfsmittel (alle in `scripts/` bzw. PoC-Ordner):

- **`PHASE-0-CHECKLISTE.md`** – Checkliste Testbasis & Binary-Inventur (Phase 0/0A der Design-Spec)
- **`TESTPROTOKOLL-PHASE-0A.md` / `TESTPROTOKOLL-PHASE-1.md`** – ausfüllbare Testprotokolle mit Gates
- **`PHASE-2-3-ANLEITUNG.md`** – 2–4 Bots pro Client (Split-Screen) + mehrere Bot-Client-Prozesse
- **`scripts/`** – `start-server.bat`, `start-observer.bat`, `start-bot-client.bat`, `start-all-bots.bat`, `hash-inventur.bat`, `BotStartup.ini`, `dedicated-config/` (siehe `scripts/README.md`)
- **`REPO-README.md`** – fertige README für das GitHub-Repo (Struktur, Lizenz, Quickstart)

**Besserer Server-Start (falls `DedicatedServer.exe` in der Installation vorhanden):** `DedicatedServer.exe <config>` liest `Scripts\Dedicated\<config>\init.ini` + `<Runde>_begin.ini` und läuft als echter Konsolen-Server ohne Rendering (loggt automatisch nach `Dedicated_<config>.log`). Wichtig dabei: `ded_bRestartWhenEmpty = 0` setzen (Default TRUE = Runden-Reset bei Leerstand) und Spielmodus per `gam_iStartMode = 2` (Fragmatch) – Vorlagen liegen in `scripts/dedicated-config/`. Die `DedicatedServer.exe` lädt ebenfalls die GameMP.dll per `LoadLibrary`/`GAME_Create` – **auf dem Server muss das die Originale bleiben.**

---

## Voraussetzungen

- Windows-PC (Build **und** Test; Serious Sam Classic ist ein Windows-Spiel)
- Serious Sam: The Second Encounter **1.07**, legal erworben (Steam: „Serious Sam Classic: The Second Encounter" ist 1.07; GOG-Retail ebenso)
- Historischer 1.07-Build: MSVC 6.0 SP6 / v60. Lokal geprüft: VS Build Tools 2022
  v143 **mit RetailAllocator.cpp**; ein unbereinigter v143-Build crasht beim Join.
- ~2 GB freier Platz

## Lokal geprüfter Windows-Buildpfad (01.10.2026)

Aktuelle Beweise und offene Gates stehen in `../CODEX_WINDOWS_POC_REPORT.md`.
Die drei vorhandenen Retail-Kopien liegen unter `.codex/retail/`; EXE und DLLs
liegen jeweils in **Bin/**. Die alten generischen BAT-Vorlagen weiter unten
müssen für diese Ordnerstruktur angepasst werden.

```powershell
# Neue Zielordner wählen; alte Artefakte werden nicht überschrieben.
.\poc\scripts\Build-RetailGameMP.ps1 -Sdk .codex\SE1-ModSDK -BuildDir .codex\my-sdk-build
.\poc\scripts\Test-RetailJoin.ps1 -Dll .codex\my-sdk-build\Sources\Bin\vs2022.Release_TSE107\GameMP.dll -Evidence .codex\evidence\my-sdk-test -Seconds 30
# Erst nach erfolgreichem SDK-Kontrolltest, mit eigenem Bot-Spielerprofil:
.\poc\scripts\Build-RetailGameMP.ps1 -Sdk .codex\SE1-ModSDK -BuildDir .codex\my-bot-build -Bot
.\poc\scripts\Test-RetailJoin.ps1 -Dll .codex\my-bot-build\Sources\Bin\vs2022.Release_TSE107\GameMP.dll -Evidence .codex\evidence\my-bot-test -Seconds 45 -Startup Scripts\BotStartup.ini -Observer
```

Das Runtime-Skript startet und beendet seine eigenen Prozesse und sichert Logs.
Es setzt vorhandene `.codex/retail/TSE-{Server,BotClient,Observer}`-Kopien und
die bestehende BotTest-Konfiguration voraus. Es lässt die getestete GameMP im
BotClient installiert. Eigene Spielerprofile vorher einrichten; Server und
Observer behalten originale Binaries. CRC-/Join-Erfolg ersetzt keinen
60-Minuten-Test und keine Prüfung von Schaden, Respawn oder Mapwechsel.

---

## Schritt 1 – Referenz-Repos holen

```bat
git clone --recursive https://github.com/DreamyCecil/SE1-ModSDK.git
:: Nur als Lese-Referenz (nicht zum Bauen des Bot-Clients nötig):
git clone --depth 1 https://github.com/Croteam-official/Serious-Engine.git
```

Das ModSDK klonen **mit** `--recursive` – die Engine-Header/Libs für 1.07 liegen im
Submodule `Sources/Includes` (Branch `includes`, dort `Engine107/` mit fertigen
`Engine.lib`, `EntitiesV.lib` usw.).

## Schritt 2 – BotDriver einbauen

Der PoC-Patch liegt in `tse-bot-poc/patch/`:

1. **`gamemp/BotDriver.h`, `gamemp/BotDriver.cpp` und `botcore/botcore.h`** nach `SE1-ModSDK\Sources\Game\` kopieren. Der aktuell getestete Pfad verwendet v143; der gemeinsame Botcore-Header setzt moderne C++-Standardbibliothek voraus.
2. **Drei Einfügungen** in `SE1-ModSDK\Sources\Game\Game.cpp` (identische Ankerstellen wie im Diff `0001-gamemp-botdriver-poc.patch` gegen Croteam 1.10; im ModSDK liegt `GameHandleTimer` bei Zeile ~747, `CreateAction`/`SetAction` bei ~793/795):
   - `#include "BotDriver.h"` zu den Includes (nach `#include "LCDDrawing.h"`)
   - An den Kopf von `CGame::GameHandleTimer()`:
     ```cpp
     // [BotDriver] if enabled, synthesize the actions of all local players and
     // bypass the normal input path (works without input focus and with menus on)
     if (BotDriver_HandleTimer(this)) {
       return;
     }
     ```
   - In `CGame::InitInternal()` **vor** dem Block „// load persistent symbols":
     ```cpp
     // [BotDriver] declare bot console symbols (before persistent symbols and
     // the startup script are executed, so scripts can set them)
     BotDriver_Init();
     ```
3. `BotDriver.cpp` + `BotDriver.h` zum Projekt `Game` hinzufügen (in der Solution
   Rechtsklick → Add → Existing Item; wer mag, trägt sie analog im Diff in die
   `.vcxproj` ein).

> Wichtig: **Nur das `Game`-Projekt bauen.** `EntitiesMP`/`EntitiesTSE` NICHT anfassen
> und keine Entities neu kompilieren – die EntitiesMP.dll des Bot-Clients muss
> byte-identisch mit der des Servers bleiben (CRC-Check, s. VERIFIKATION.md 1.1).

## Schritt 3 – Bot-Client zusammenstellen

1. Installationsordner von TSE 1.07 **vollständig kopieren** (z. B. `TSE-BotClient\`).
2. Die gebaute **`GameMP.dll`** (Release!) aus Schritt 2 in `TSE-BotClient\` über
   die vorhandene kopieren (Backup der Original-DLL nicht vergessen).
3. Alles andere bleibt unangetastet: `SeriousSam.exe`, `Engine.dll`,
   `EntitiesMP.dll`, alle `.gro`-Dateien.
4. Bot-Aktivierung anlegen: Datei `TSE-BotClient\Scripts\BotStartup.ini`
   (Vorlage liegt in `scripts/BotStartup.ini`):
   ```ini
   bot_bEnabled = 1;
   bot_fYawSpeed = 45;
   bot_fFirePeriod = 1.0;
   bot_iFireTicks = 3;
   bot_iLogEvery = 40;
   ```

> Kein Mods-Ordner, kein `+game` – sonst meldet der Client einen Mod-Namen und der
> Vanilla-Server weist ihn ab (Mod-Check im Handshake, VERIFIKATION.md 1.2).

## Schritt 4 – Vanilla-Dedicated-Server (1.07) starten

Auf dem Server-PC (darf derselbe sein, für saubere Tests lieber ein zweiter):

1. Frische, unmodifizierte TSE-1.07-Installation.
2. **Bevorzugt:** `DedicatedServer.exe` mit Konfiguration starten – Vorlagen in
   `scripts/dedicated-config/` nach `<Server>\Scripts\Dedicated\BotTest\` kopieren,
   anpassen (Map, Session-Name), dann `DedicatedServer.exe BotTest`
   (oder `scripts/start-server.bat`). Log: `Dedicated_BotTest.log`.
   - **`ded_bRestartWhenEmpty = 0`** setzen (Default TRUE = Runden-Reset bei Leerstand)
   - Spielmodus Deathmatch: `gam_iStartMode = 2`
3. **Fallback ohne DedicatedServer.exe:** Multiplayer → New Game → Split-Screen-Auswahl
   auf **„Dedicated"** stellen (`SSC_DEDICATED`, die Konsole klappt dann automatisch
   runter), Deathmatch + Map (z. B. `DM_LittleTrouble`) wählen, Start.
4. Ports freigeben: UDP **25600** (Game) und 25601 (Query); `gam_ctMaxPlayers`
   nach Bedarf (max. 16, `NET_MAXGAMEPLAYERS`).

## Schritt 5 – Bot-Client starten (vollautomatischer Join)

```bat
TSE-BotClient\SeriousSam.exe +connect <server-ip>:25600 +quickjoin +script Scripts\BotStartup.ini
```

- `+connect` + `+quickjoin` = Vanilla-Autojoin ohne Menü (`JoinNetworkGame()`).
- `+script` aktiviert die Bots nach der Initialisierung.
- Der Client kann danach **ungefokussiert/minimiert** bleiben – der BotDriver
  erzeugt Aktionen unabhängig vom Input-Zustand (Headless-light).

## Schritt 6 – Mit Vanilla-Client verifizieren

Dritter PC (oder derselbe): normale, unmodifizierte TSE-1.07-Installation, per
Serverbrowser (333networks) oder Direktconnect joinen und durchtesten
(Details: `TESTPROTOKOLL-PHASE-1.md`):

| Prüfung | Erwartung |
|---|---|
| Join des Bot-Clients klappt | Server-Log: „Adding player …", CRC check OK |
| Scoreboard/Spielerliste | Bot erscheint als normaler Spieler mit Namen |
| Bewegung | Bot läuft vorwärts, dreht langsam |
| Schießen/Respawn | Feuer-Pulse; nach Tod automatisch Respawn (Fire=Rebirth) |
| Schaden/Frags | Bot nimmt Schaden, kann sterben, kann (später) fraggen |
| Mapwechsel | Auto-Reconnect des Bot-Clients (`gam_strJoinAddress`) |
| 60+ min | kein Desync/Kick |
| Serverbrowser | Spielerzahl zählt den Bot mit |

Konsolen-Log des Bot-Clients zeigt alle 2 s: `[BotDriver] bot0 tick=… pos=(…) heading=… fire=…`
– Position muss sich mit voller Laufgeschwindigkeit ändern.

## Troubleshooting (Disconnect-Meldungen dekodieren)

| Meldung | Ursache | Fix |
|---|---|---|
| „Wrong CRC check." | `Player.ecl`/EntitiesMP.dll/Daten weichen ab | EntitiesMP.dll + Daten des Bot-Clients durch Originale ersetzen; nur GameMP.dll tauschen |
| „This server runs version X.Y, your version is A.B" | Engine-Versionen mischen (z. B. 1.10-Build) | Bot-Client = 1.07-Installation + nur GameMP.dll-Swap |
| „MOD:<name>\\<url>" | Bot-Client hat einen Mod aktiv | kein `+game`, kein Mods-Ordner; DLL direkt ins Hauptverzeichnis |
| „Server full!" | alle Slots belegt / `ctWantedLocalPlayers` zu groß | `gam_ctMaxPlayers` erhöhen oder Bot-Anzahl reduzieren |

## Nächste Ausbaustufen

1. **2–4 Bots pro Client:** siehe `PHASE-2-3-ANLEITUNG.md` (Split-Screen-Konfiguration;
   BotDriver bedient bereits alle 4 Slots)
2. **Mehr als 4 Bots:** weitere Bot-Client-Prozesse – `scripts/start-all-bots.bat`
   (bis 16 Spieler gesamt)
3. **Echte KI:** State-Feedback steht bereit (`GetLocalPlayerEntity` → Position/Heading
   pro Tick). Navigations-Layer außerhalb der synchronisierten Welt bauen
   (Waypoints/NavMesh aus Level-Geometrie, Raycasts clientseitig), CecilBotMod-KI-Logik
   als Referenz portieren. Die botcore/ ist der Platz, um Entscheidungs-Logik ohne
   Engine zu entwickeln und zu testen.
4. **Slot-Management:** Bots freigeben, wenn echte Spieler joinen (Phase 5, Population
   Manager – z. B. via RCon `net_strAdminPassword` oder Bot-Client-Logik, die
   `GetPlayersCount()` beobachtet).
5. **Headless:** Rendering deaktivieren (Engine-Eingriff – erst angehen, wenn Pfad D
   auf echter Hardware stabil läuft).

## Phase-1-Diagnose (01.10.2026)

Phase 1 bleibt **NOCH OFFEN**. Laufzeitdaten ersetzen keine Observer-Sichtprüfung.
`bot_bDiagnostics=1` aktiviert nur lesende Snapshots aller vorhandenen Spieler:
Entityposition/Yaw, Gesundheit, angewendete Buttons und nativen Player-Query-Fragwert.
`bot_iTestTarget=-1` ist Standard und behält das ursprüngliche PoC-Verhalten.
Mit `bot_iTestTarget=0` wird genau dieser Spieler mit Colt-Actions anvisiert;
alle vier Sekunden folgt ein fester Sprungpuls. Der native Action-Composer
wandelt normierte Achsen in Retail-Geschwindigkeiten um. Es gibt keine
Navigation, Zielsuche oder direkte Schadens-/Entity-Manipulation. Hindernisse
können den Test blockieren. Der Observer muss zuerst als Spielerindex 0 joinen.

```powershell
# Neues Build-/Evidence-Ziel verwenden; Originalinstallation nicht anfassen.
.\poc\scripts\Build-RetailGameMP.ps1 -Sdk .codex\SE1-ModSDK -BuildDir .codex\phase1-next-build -Bot
Copy-Item poc\scripts\Phase1Diagnostics.ini .codex\retail\TSE-BotClient\Scripts\Phase1Diagnostics.ini
Copy-Item poc\scripts\Phase1Combat.ini .codex\retail\TSE-BotClient\Scripts\Phase1Combat.ini
.\poc\scripts\Test-RetailJoin.ps1 -Dll .codex\phase1-next-build\Sources\Bin\vs2022.Release_TSE107\GameMP.dll -Evidence .codex\evidence\phase1-next-combat -Seconds 180 -Startup Scripts\Phase1Combat.ini -Observer -VisibleClients
.\poc\scripts\Test-Phase1Telemetry.ps1 -BotLog .codex\evidence\phase1-next-combat\SeriousSam.log -Output .codex\evidence\phase1-next-combat\telemetry.json
.\poc\scripts\Test-Phase1Telemetry.Tests.ps1
```

`-VisibleClients` startet nur die Clients mit `WindowStyle Normal`; Default bleibt
Hidden. Der Test beendet weiterhin seine Prozesse hart: **kein Shutdown-Gate**.
`Test-Phase1Telemetry.ps1 -QueryServer` liest während einer aktiven Session die
native localhost-UDP-25601-Statusantwort zusätzlich ein. Ein laufender Log kann
währenddessen unvollständige Zeilen enthalten; finale Auswertung nach Laufende.
Interleaved/unvollständige Snapshotzeilen werden verworfen und gezählt, nicht
repariert oder als Evidenz akzeptiert. Keine Gesamtabnahme aus diesem JSON ableiten.

Die Computer-Use-Aufnahme schlug hier auch mit sichtbaren 960x540-Fenstern mit
Capture-Timeout fehl. Ohne geprüfte GUI bleiben sichtbare Bewegung/Rotation,
Schusswirkung, Scoreboard und Jitter/Teleports offen. Die beiden automatischen
Kampfversuche zeigten Gesundheit 100 und Frags 0 bei beiden Spielern. Nächster
Schritt: freie Schusslinie tatsächlich herstellen und Schaden/Death/Respawn
beobachten; erst danach Reconnect/Mapwechsel/Shutdown/10-,30-,60-Minuten-Sync.


## Retail-Pruefung 02.10.2026

Aktueller Gate-Stand und Hashes oben im Phase-1-Protokoll.
`bot_bTestThirdPerson=1` ist eine native View-Taste fuer Spectator-QA;
Standard FALSE. Phase1Visual.ini nutzt sie, Phase1Respawn.ini nutzt Yaw5
auf Fortress fuer normale Umwelttode/Respawns.

`-CaptureObserver -CaptureFps 30`: native 960x540-TGAs.
`-AllowReconnect`: nur Retail-Exit1 mit nativem Quit und vollstaendigen
Renderer-Cleanupmarkern; gleiche Bot-/Observer-CLI neu starten, Logs und
Slotstatus archivieren. Ein Crash gilt nicht als erfolgreicher Join.
`-ExpectedShutdown`: Observer erforderlich, AllowReconnect ausgeschlossen;
Server0/Bot1/Observer1 und beide Quitmarker. Default-Hardcleanup beweist kein Shutdown.

`Test-Phase1Telemetry.ps1 -QueryServer`: Status und Player-Frags separat vom Server.
`-SyncMinutes N`: mindestens N*1200 einzigartige monotone Tick-Snapshots und
jede Minute Positionen, Yaw, angewendetes Fireon/off. Lebende Prozesse reichen nicht.
Soaks: Fortress ohne Timelimit, normaler Vanilla-Spectator ohne lokalen Spieler,
beide Testkopien Fensterbetrieb, PauseOnMinimize0, FPS60/30. Praeferenz ueber
normales Join-Menue oder gesicherte GAMEV012-Datei setzen und danach restaurieren.
Originalinstallation unveraendert. Lokale Sequenz und Backups: .codex/run-native-soaks.ps1.
Regressionen: Test-RetailJoinState.Tests.ps1, Test-Phase1Telemetry.Tests.ps1.
NativeJoin615s plus finale Telemetry -SyncMinutes10; analog1815/3615s fuer30/60.
10 Minuten BESTÄTIGT; 30 Minuten läuft aktuell; 60 Minuten + 60-Minuten-Wiederholung offen. Keine Gesamtabnahme.
