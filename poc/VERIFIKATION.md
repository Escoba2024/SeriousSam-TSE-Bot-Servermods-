# Pfad D – PoC: Quellcode-Verifikation & Implementierung
## Vanilla-kompatible Bots für Serious Sam: The Second Encounter v1.07

**Status:** Der Bericht wurde anhand des echten Croteam-Sourcecode (Serious Engine v1.10, Commit `b408e88a16fd01aa1cfd0e0a999c86c2c1437c9e`) Punkt für Punkt nachgeprüft. Kernthesen bestätigt, **zwei entscheidende neue Befunde** (CRC-Check und Versions-Handshake) liefern die noch fehlenden harten Garantien für Pfad D – und töten die Alternativen endgültig. Der PoC-Patch für Pfad D ist **implementiert** (GameMP-only) und die Action-Generierungs-Logik wurde isoliert getestet (`botcore/`, alle Checks bestanden).

---

## 1. Die drei entscheidenden Befunde

### 1.1 Der Server CRC-prüft EntitiesMP.dll – aber NICHT GameMP.dll ⭐

Beim Join läuft folgender Austausch:

```
Client → Server : MSG_REQ_CRCLIST          (SessionState.cpp:391-396)
Server → Client : MSG_REQ_CRCCHECK         (Dateiliste = ga_pubCRCList)
Client → Server : MSG_REP_CRCCHECK         (CRC über genau diese Dateien)
Server         : CRC != ga_ulCRC → Disconnect "Wrong CRC check."
                                               (Server.cpp:1551-1567)
```

Was landet in der Liste? Beim Serverstart wird `InitCRCGather()` aufgerufen:

| Fundstelle | Was wird geprüft |
|---|---|
| `Engine/Network/Network.cpp:2472-2477` | explizit `Classes\Player.ecl` **plus** alles beim Level-Load Gesammelte |
| `Engine/Entities/EntityClass.cpp:344-352` (`CEntityClass::AddToCRCTable`) | die `.ecl`-Datei **und die Entity-Class-DLL** (`ec_fnmClassDLL` = **EntitiesMP.dll**) |
| `Engine/Base/Serial.cpp:159` (`CSerial::AddToCRCTable`) | geladene Datendateien (Texturen, Modelle, Sounds, Welt …) |

**Konsequenzen:**
- **Pfad A (serverseitige PlayerBot-Entity / modifizierte EntitiesMP) ist für Vanilla-Server endgültig tot.** Nicht nur „Clients brauchen den Mod" – der Server *disconnectet* jeden Client, dessen EntitiesMP.dll nicht **byte-identisch** ist. Schon ein neu kompiliertes, funktional identisches EntitiesMP.dll fällt durch.
- **GameMP.dll wird nirgends CRC-geprüft.** Auch SeriousSam.exe/Engine.dll nicht. Ein Bot-Client mit getauschter GameMP.dll besteht den CRC-Check, solange EntitiesMP.dll und die Spieldaten Vanilla bleiben.
- Das bestätigt Pfad D als einzigem sauberen Weg und präzisiert Berichts-Abschnitt 17 (dort als „unbekannt" geführt).

### 1.2 Der Versions-Handshake schließt 1.10-Builds auf 1.07-Servern aus ⭐

Der Client sendet beim Session-Connect `'VTAG' + _SE_BUILD_MAJOR + _SE_BUILD_MINOR` (`Engine/Network/SessionState.cpp:317-318`). Der Server vergleicht **exakt** und trennt bei Abweichung:

```cpp
// Engine/Network/Server.cpp:866-885
if (iTag=='VTAG') { nm>>iMajor>>iMinor; } else { iMajor=109; iMinor=1; }
if (iMajor!=_SE_BUILD_MAJOR || iMinor!=_SE_BUILD_MINOR) {
  // disconnect: "This server runs version %d.%d, your version is %d.%d."
}
```

Der 1.10-Source meldet `10000.10` (`Engine/CurrentVersion.h:17-18`, Kommentar: *„minor versions that are data-compatibile, but are not netgame-compatibile"*).

**Konsequenz:** Ein aus dem öffentlichen 1.10-Source gebauter Client kann **niemals** einen Vanilla-1.07-Server joinen. Der Bericht vermutete das („Bit-Kompatibilität nicht belegt") – es ist jetzt per Source **bewiesen**. Der Bot-Client muss also:
- **Variante 1 (empfohlen):** Vanilla-1.07-Installation + **nur getauschte GameMP.dll** (bot-fähig, aus SE1-ModSDK gebaut, 1.07-Target). Version im Handshake meldet die **unveränderte Engine.dll** → 1.07 ✔. Mod-Name bleibt leer ✔.
- **Variante 2:** Full-Rebuild aus 1.07-Target-Quellen (SE1-ModSDK) – riskanter (mehr Binaries weichen ab), für den PoC unnötig.

Zusätzlich geprüft und relevant: Der Handshake vergleicht auch den **Mod-Namen** (`Server.cpp:888-897`). Ein Bot-Client, der seine DLL als „Mod" aktiviert (`+game`/Mods-Ordner), wird von einem Vanilla-Server abgelehnt. **Direkter DLL-Swap im Hauptverzeichnis löst das Problem** (kein Mod-Name).

### 1.3 Der EXE lädt GameMP.dll per LoadLibrary + einzelner Factory-Funktion ⭐

```cpp
// SeriousSam/SeriousSam.cpp:371-391 (InitializeGame)
#define GAMEDLL (_fnmApplicationExe.FileDir()+"Game"+_strModExt+".dll")  // → GameMP.dll
HMODULE hGame = LoadLibraryA(fnmExpanded);
CGame* (*GAME_Create)(void) = GetProcAddress(hGame, "GAME_Create");
_pGame = GAME_Create();
```

Der Export ist minimal (`extern "C" __declspec(dllexport) CGame *GAME_Create(void)`, `GameMP/Game.cpp:62`). Ein DLL-Swap ist mechanisch trivial und berührt weder Mod-Name noch CRC noch Version. Genau das ist die Architektur des PoC.

---

## 2. Verifikation der Berichts-Behauptungen (Auszug mit Fundstellen)

Alle Zeilenangaben: Croteam-Source v1.10, Commit `b408e88a`, **vor** Anwendung des PoC-Patches.

| # | Berichts-Behauptung | Befund | Fundstelle (Source) |
|---|---|---|---|
| 1 | `CPlayerAction`: `pa_vTranslation`, `pa_aRotation`, `pa_aViewRotation`, `pa_ulButtons`, `pa_llCreated` | ✅ exakt (Kommentar: *„order is important for compression… do not reorder"*) | `Engine/Network/NetworkMessage.h:274-286` |
| 2 | `PLACT_FIRE` etc. existieren | ✅ Bit 0 = Fire, 14 weitere Flags (RELOAD, WEAPON_NEXT, USE, …) | `EntitiesMP/Player.es:259-273` |
| 3 | Pipeline: Controls → `CreateAction` → `SetAction` auf `CPlayerSource` (GameMP) | ✅ Aufrufkette steht **komplett in GameMP**, jede Tick: `ctrls.CreateAction(...)` → `lp_pplsPlayerSource->SetAction(paAction)` | `GameMP/Game.cpp:760` (`CGame::GameHandleTimer`), `:806-808`, `:438-461` (`CControls::CreateAction`) |
| 4 | `CPlayerSource`: `pls_paAction`, `SetAction`, `WriteActionPacket`, `Start_t` | ✅ alles public | `Engine/Network/PlayerSource.h:31-58` |
| 5 | `CPlayerBuffer` puffert, Server aggregiert zu `MSG_SEQ_ALLACTIONS` | ✅ `CPlayerBuffer::CreateActionPacket`, vom Server pro Tick gebündelt | `Engine/Network/PlayerBuffer.cpp:102`, `Engine/Network/Server.cpp:798`, `NetworkMessage.h:78` |
| 6 | `CPlayerTarget::ApplyActionPacket` → `CPlayerEntity::ApplyAction` | ✅ MainLoop wendet pro Spieler an | `Engine/Network/SessionState.cpp:947-950`, `Engine/Network/PlayerTarget.cpp:128,166`, `EntitiesMP/Player.es:3614` |
| 7 | Lokale Spieler hardcodiert max. 4 (`gm_lpLocalPlayers[4]`) | ✅ plus `NET_MAXLOCALPLAYERS 4` | `GameMP/Game.h:216`, `Engine/Network/Network.h:31` |
| 8 | Join mit N lokalen Spielern (`AddPlayer_t` pro Spieler) | ✅ `JoinGame` → `JoinSession_t(session, ctLocalPlayers)` → `AddPlayers()` → `AddPlayer_t` je Spieler; Server zählt jeden gegen `ses_ctMaxPlayers` („Server full!") | `GameMP/Game.cpp:1173-1191`, `Engine/Network/Network.cpp:2200`, `Engine/Network/Server.cpp:946-966` |
| 9 | „bis typisch 16–32 Spieler, abhängig von SessionProperties" | ⚠️ **Korrektur:** Engine-Cap ist **16** (`NET_MAXGAMEPLAYERS 16`), 4 pro Client, `NET_MAXGAMECOMPUTERS` Clients | `Engine/Network/Network.h:29-31` |
| 10 | `GetPlayersCount` / `GetPlayerEntity` / `GetMyPlayerIndex` | ✅ `CSessionState::GetPlayersCount` (SessionState.cpp:2130), statisches `CEntity::GetPlayerEntity` (Entity.h:522), `GetMyPlayerIndex` als PlayerEntity-Export | `Engine/Classes/PlayerEntity.es:50`, `EntitiesMP/Player.es:478-483` |
| 11 | Demo-System = Netzwerk-System | ✅ `StartDemoPlay_t` liest denselben Session-State-Stream | `Engine/Network/Network.cpp:1327+` |
| 12 | 1.10 = modifizierte 1.07-Basis | ✅ README: „source code for Serious Engine v.1.10 … modified to run correctly under the recent version of Windows" | Repo `README.md:4,26` |
| 13 | CecilBotMod: `PlayerBot.es`, NavMesh-Entity, braucht modifizierte EntitiesMP+GameMP | ✅ `Classes/PlayerBot.ecl`, `Classes/NavMeshGenerator.ecl`, fertige `.nav`-Dateien im Repo | github.com/DreamyCecil/CecilBotMod |
| 14 | SE1-ModSDK unterstützt TSE 1.07 | ✅ README listet TSE 1.05/1.07/1.10; `includes`-Branch liefert fertige **Engine107**-Libs (`Engine.lib`, `EntitiesV.lib`, …); warnt selbst: jede Entity-Abweichung → Desync gegen Vanilla | github.com/DreamyCecil/SE1-ModSDK (+ Branch `includes`) |
| 15 | 333networks zählt echte Slots | ✅ (kein Code nötig; Slots sind echte `CPlayerTarget`s) | – |

---

## 3. Implementierungs-kritische Semantik (aus dem Source abgeleitet)

Diese Details stehen so **nicht** im Bericht, sind aber für einen korrekten Bot zwingend:

1. **`pa_vTranslation` ist eine Geschwindigkeit, kein Richtungsvektor.** Voll vorwärts = `pa_vTranslation(3) = -plr_fSpeedForward` (**z < 0 = vorwärts!**). Buttons setzen exakt diesen Wert (`Player.es:502`).
2. **`pa_aRotation`/`pa_aViewRotation` sind absolut akkumulierte Winkel** (relativ zur Spawn-Blickrichtung), keine Deltas: `ctl_ComposeActionPacket` akkumuliert in `penThis->m_aLocalRotation` und schreibt den Akkumulator ins Paket (`Player.es:491,525`). Der Konsument (`ApplyAction`, `Player.es:3633-3646`) bildet selbst das Delta zum vorherigen Paket. **Folge: niemals auf ±180° wrappen** – sonst dreht der Spieler einmal komplett um 360°. Vanilla akkumuliert ebenfalls unbegrenzt (Reset nur bei Entity-Neuschöpfung, `Player.es:1130`).
3. **Anti-Abuse-Clamps:** `ApplyAction` klemmt Translation auf `±plr_fSpeedForward/Backward/Side/Up` und begrenzt Diagonalgeschwindigkeit (`Player.es:3662-3688`). Der Bot darf also gar nicht schneller als Vanilla-Sprint sein.
4. **20 Hz:** `CTimer::TickQuantum = 1/20.0` (`Engine/Base/Timer.cpp:54`). `GameHandleTimer` läuft pro Tick – der Bot generiert also 20 Aktionen/s, exakt wie ein Mensch.
5. **`pa_llCreated`** wird von `CPlayerSource::SetAction` selbst gestempelt (`PlayerSource.cpp:155-162`) – der Bot muss sich um den Zeitstempel nicht kümmern.
6. **Fire nach Tod = Respawn:** ist der Spieler tot, führt `PLACT_FIRE` über `DeathActions` zum Rebirth (`Player.es:3736`) – der periodisch feuernde PoC-Bot respawnt also automatisch.
7. **Ping wird mitgeschickt:** `WriteActionPacket` packt 10 Bit selbst-ermittelten Ping dazu (`PlayerSource.cpp:198-201`) – irrelevant für den Bot, aber gut zu wissen.
8. **`GameHandleTimer` hat einen zweiten Zweig ohne Input** (Menu an / DirectInput aus → Aktionen werden genullt, `Game.cpp:817-842`). **Headless-Folgerung:** Der Bot muss seine Aktionen VOR der Input-Verzweigung injizieren, sonst wird er bei Fokusverlust/öffnender Konsole stillgestellt. Der Patch macht genau das.

---

## 4. Der implementierte PoC-Patch (Pfad D, 1 Bot – faktisch 1–4)

### Dateien (in `tse-bot-poc/patch/`)

| Datei | Inhalt |
|---|---|
| `0001-gamemp-botdriver-poc.patch` | Unified Diff gegen Croteam 1.10 @ `b408e88a`: 3 Einfügungen in `Game.cpp`, 2 in `GameMP.vcxproj` |
| `gamemp/BotDriver.h`, `gamemp/BotDriver.cpp` | Neues, in sich geschlossenes GameMP-Modul (~150 Zeilen) |

Die identische Struktur existiert im SE1-ModSDK (`Sources/Game/Game.cpp`, `GameHandleTimer` bei ModSDK-Zeile 747, `CreateAction`/`SetAction` bei 793/795) – der Patch überträgt sich 1:1 (nur Zeilennummern verschieben).

### Injektionspunkte (minimal-invasiv, GameMP-only)

1. **`CGame::GameHandleTimer()` – Kopf:** `if (BotDriver_HandleTimer(this)) return;`
   Erzeugt pro lokalem Spieler eine synthetische `CPlayerAction` und übergibt sie an `CPlayerSource::SetAction()` – **derselbe Aufruf wie im Vanilla-Pfad**. Läuft damit unabhängig von Input-Fokus und Menü-Zustand (Headless-fähig).
2. **`CGame::InitInternal()`:** `BotDriver_Init();` **vor** dem Laden der persistenten Symbole und `Scripts/Game_startup.ini` – damit lassen sich Bot-Variablen per Skript/Konsole setzen.

### Verhalten (PoC, ohne KI)

- Dauerhaft vorwärts mit `bot_fMoveFactor × plr_fSpeedForward`: normierte Achsen werden vom exportierten `ctl_ComposeActionPacket` in native Geschwindigkeiten umgewandelt. Die früheren Shell-Abfragen waren falsch: nicht deklarierte Symbole lieferten im Retail-Test `-666`, was rückwärts statt vorwärts bewegte. Der native Composer pflegt zugleich die lokalen Blickwinkelakkumulatoren.
- Heading dreht mit `bot_fYawSpeed` °/s (absolut akkuminiert, nie gewrappt)
- Feuerpuls: alle `bot_fFirePeriod` s für `bot_iFireTicks` Ticks `PLACT_FIRE` (Bit 0) → triggert auch Respawn nach Tod
- Status-Log alle `bot_iLogEvery` Ticks mit **echter Welt-Position** (`_pNetwork->GetLocalPlayerEntity(ppls)` → `CEntity::en_plPlacement`, public: `Engine/Entities/Entity.h:185`) – das ist zugleich das State-Feedback für die spätere Navigations-KI
- Alles deterministisch (kein RNG) → reproduzierbares Debugging, keine Desync-Überraschungen durch die Action-Quelle

### Aktivierung (ohne einen einzigen Klick im Menü)

```
SeriousSam.exe +connect <server-ip>:25600 +quickjoin +script Scripts\BotStartup.ini
```
- `+connect`/`+quickjoin` sind Vanilla (`SeriousSam/CmdLine.cpp:123-131`, `SeriousSam.cpp:556-566` → `JoinNetworkGame()`, `MenuStarters.cpp`)
- `+script` führt nach der Initialisierung Shell-Kommandos aus (`SeriousSam.cpp:501-504`) → `BotStartup.ini` enthält `bot_bEnabled 1;`
- Alternativ/zusätzlich: `bot_bEnabled 1;` in `Scripts/Game_startup.ini` (wird von GameMP ausgeführt, `Game.cpp:1024`)
- Auto-Reconnect bei Server-Restart/Mapchange gibt es gratis: `CGame::GameMainLoop` → `JoinGame(CNetworkSession(gam_strJoinAddress))` (`Game.cpp:2669-2672`)

### Was der Patch NICHT anfasst
SeriousSam.exe, Engine.dll, EntitiesMP.dll, Spieldaten (.gro/.ecl/.wld) – alles bleibt byte-identisch → CRC-Check ✔, Versions-Check ✔, Mod-Check ✔.

---

## 5. Botcore-Test (in der Sandbox ausgeführt)

`tse-bot-poc/botcore/` enthält eine engine-freie Kopie der Tick-Logik + Testharness (g++, C++17). **Ergebnis: `ALL CHECKS PASSED`** (Ausgabe in `botcore/test_output.txt`):

- Heading-Delta pro Tick = exakt `yawSpeed × TickQuantum` (1200 Ticks = 60 s → 2700°, keine Sprünge/Wraps)
- Translation = `-plr_fSpeedForward` (z < 0, Vorwärts-Konvention)
- Fire-Duty-Cycle = 3/20 Ticks = 15 %
- Simulierte `ApplyAction`-Deltas summieren sich korrekt zur Heading-Änderung

Das validiert die Semantik des Generators; kompiliert wurde **nicht** gegen die echte Engine (dafür fehlt hier die Windows/MSVC-Umgebung – siehe Runbook).

---

## 6. Was auf echter Hardware zu verifizieren bleibt

| # | Test | Erwartung laut Source |
|---|---|---|
| 1 | Bot-Client (Vanilla-1.07-Install + getauschte GameMP.dll) joint Vanilla-Dedicated 1.07 | Join OK (Version=1.07 via Engine.dll, Mod leer, CRC: EntitiesMP/Daten identisch) |
| 2 | Vanilla-Client sieht Bot | Normaler Spieler: Scoreboard, Bewegung, Schießen, Schaden, Frags, Respawn |
| 3 | CRC-Mismatch-Negativtest: fremde `Player.ecl` in den Class-Ordner legen | Server trennt mit „Wrong CRC check." (Server.cpp:1557) |
| 4 | 60 min Sync-Stabilität + Mapwechsel | Auto-Reconnect via `gam_strJoinAddress` |
| 5 | 2–4 Bots pro Client (Split-Screen-Konfiguration SSC_PLAY2..4) | `JoinSession_t(…, ctLocalPlayers)` nimmt bis 4; Server bucht je Spieler einen Slot |
| 6 | Mehrere Bot-Client-Prozesse | Bis `NET_MAXGAMEPLAYERS 16` Spieler gesamt |
| 7 | Serverbrowser (333networks) | Zählt echte Slots |
| 8 | Desync-Verhalten bei `cli_bEmulateDesync`-artigen Störungen | Sync-Check via `MSG_SYNCCHECK` (SessionState.cpp:1880+) |

Offene Punkte (nicht per Source belegbar): tatsächliches Laufzeitverhalten des ModSDK-Game-Builds gegen die Vanilla-1.07-EXE (ABI-Kompatibilität der `GAME_Create`-Schnittstelle ist gegeben, aber unbewiesen im Praxistest), Langzeit-Stabilität headless/ungefokussiert, Timing-Drift über Stunden.

---

## 7. Aktualisierte Antworten (nur wo der Befund vom Bericht abweicht/erweitert)

- **Frage 17/18 (1.07↔1.10):** Nicht mehr „unbekannt" – **1.10-Builds können 1.07-Server prinzipiell nicht joinen** (exakter Major/Minor-Vergleich im Handshake). 1.10-Source bleibt Referenz für Logik/Portierung, niemals als Bot-Client-Basis.
- **Pfad-A-Bewertung:** Verschärft von „Clients brauchen Mod" auf „Server **kicked** Clients mit abweichender EntitiesMP.dll (CRC)".
- **Pfad-B-Bewertung (Synthetic Clients im Server):** zusätzlich erschwert – ein solcher Server wäre selbst kein Vanilla-Binary mehr (Version/CRC-Checks serverseitig geändert). Weiterhin nur mit klassischem Patch-Hook-Framework denkbar.
- **Neu:** Es existiert ein **dritter, trivialer Vanilla-Kompatibilitätsmechanismus** (LoadLibrary/GAME_Create-Swap), der Pfad D auf „nur GameMP.dll ersetzen" reduziert – kein Mod-Ordner, kein Mod-Name, kein Client-Download für echte Spieler.

---

## 8. Fundstellen-Index (alle Zitate)

**Engine (Croteam 1.10 @ b408e88a):**
`Network/NetworkMessage.h:74-108` (Message-IDs, u. a. `MSG_SEQ_ALLACTIONS:78`), `:274-286` (CPlayerAction) · `Network/PlayerSource.h:31-58`, `Network/PlayerSource.cpp:155-162,172-215` · `Network/PlayerBuffer.cpp:102` · `Network/PlayerTarget.cpp:128,166` · `Network/Server.cpp:798, 855-975, 1536-1568` · `Network/SessionState.cpp:193-230, 306-340, 391-405, 947-950, 1880-1915, 2130` · `Network/Network.cpp:183-195, 1173-1295, 2200-2225, 2472-2500` · `Network/Network.h:29-31, 111-113, 277` · `Entities/EntityClass.cpp:344-352` · `Entities/Entity.h:175-185, 520-522` · `Entities/PlayerCharacter.h:47` · `Base/Serial.cpp:159` · `Base/CRCTable.cpp` · `Base/CRC.cpp` · `Base/Timer.cpp:54` · `Base/Shell.h:58` · `Classes/PlayerEntity.es:50` · `CurrentVersion.h:17-18`

**EntitiesMP:** `Player.es:259-273` (PLACT_*), `:446-585` (ctl_ComposeActionPacket), `:806` (plr_fSpeedForward), `:1130` (m_aLocalRotation-Init), `:3614-3760` (ApplyAction), `:3722-3730` (DeathActions/Rebirth)

**GameMP:** `Game.h:186-190` (SSC_*), `:216` (gm_lpLocalPlayers[4]) · `Game.cpp:62` (GAME_Create), `:438-461` (CControls::CreateAction), `:756-845` (GameHandleTimer), `:854+` (InitInternal), `:1105-1167` (NewGame), `:1173-1200` (JoinGame), `:1734` (AddPlayers), `:2638` (GameMainLoop), `:2669-2672` (Auto-Reconnect)

**SeriousSam (EXE):** `CmdLine.cpp:108-140` · `SeriousSam.cpp:371-391` (InitializeGame/LoadLibrary), `:480-540` (Init-Reihenfolge, +script), `:556-566` (+connect) · `GUI/Menus/MenuStarters.cpp:275` (StartNetworkGame, SSC_DEDICATED → Konsole)

**Extern:** `github.com/Croteam-official/Serious-Engine` (README) · `github.com/DreamyCecil/SE1-ModSDK` (README; Branch `includes` → `Engine107/`) · `github.com/DreamyCecil/CecilBotMod` (PlayerBot.ecl, NavMeshGenerator.ecl)
