# Windows/Retail TSE 1.07 Pfad-D-PoC – erster Laufzeitlauf

> Aktueller Stand 01.10.2026: Der unten dokumentierte ursprüngliche Crash wurde
> mit einer GameMP-seitigen Allocator-Anbindung behoben. SDK-Kontrollbuild und
> Bot-Build bestehen jetzt reale CRC-/Join-Tests. Details und Grenzen im angehängten
> Abschnitt „ABI-/CRT-Fortsetzung“. Der erste Lauf bleibt als historische Evidenz erhalten.

Stand: 01.10.2026. Start-Commit: `264611c34b7f01be6371ec3301e5da670852c5b9` (`main`). Kein Push oder Commit.

## Dateien und Testumgebung

- Die vorbereiteten PoC-Dateien wurden nach `poc/` übernommen: Dokumente, `botcore/`, `patch/`, `scripts/`. Bestehende Repo-Dokumente blieben erhalten. In `poc/scripts/dedicated-config/1_begin.ini` wurde nur der Map-Pfad auf den im Retail-GRO vorhandenen, korrekt escapten Pfad `Levels\\LevelsMP\\Deathmatch\\DM_LittleTrouble.wld` korrigiert.
- Lokale, über `.git/info/exclude` ausgeblendete Arbeitsdateien liegen unter `.codex/`: `SE1-ModSDK/` (Commit `aa7869c2c2c4db0562281814d0ac3784e6b9d6f0`, Submodule mit 1.07-Headern und Import-Libs), `retail/` mit `TSE-Server`, `TSE-BotClient`, `TSE-Observer`, Build-Logs und `evidence/`.
- Die ursprüngliche Steam-Installation wurde nicht verändert. `CODEX_TASK.txt`, `_codex_windows_poc_task.md` und `.worktrees/` sind fremde, unberührte untracked Dateien.
- Installiert: Visual Studio Build Tools 2022 `17.14.41`, nur `Microsoft.VisualStudio.Component.VC.Tools.x86.x64` und `Microsoft.VisualStudio.Component.Windows10SDK.19041`. Kein IDE-Workload.

## Exakte Befehle

PowerShell, Repo als Arbeitsverzeichnis; `$src` ist `C:\Program Files (x86)\Steam\steamapps\common\Serious Sam Classic The Second Encounter`:

```powershell
& 'C:\Program Files\Git\cmd\git.exe' clone --depth 1 --recurse-submodules --shallow-submodules https://github.com/DreamyCecil/SE1-ModSDK.git .codex\SE1-ModSDK
winget install --id Microsoft.VisualStudio.2022.BuildTools --exact --source winget --accept-package-agreements --accept-source-agreements --silent --override "--quiet --wait --norestart --add Microsoft.VisualStudio.Component.VC.Tools.x86.x64 --add Microsoft.VisualStudio.Component.Windows10SDK.19041"
foreach ($n in 'TSE-Server','TSE-BotClient','TSE-Observer') { robocopy $src ".codex\retail\$n" /E /R:1 /W:1 /NFL /NDL /NJH /NJS /NP }
```

Das lokale SDK-Game-Projekt wurde ausschließlich für den Test angepasst: `BotDriver.{h,cpp}` aus `poc/patch/gamemp/` nach `Sources/Game/`; die drei Einfügungen aus dem Patch in `Game.cpp`; `BotDriver.cpp` im Game-Projekt; `StdAfx.h` verweist auf die vorhandene 1.07-Datei `EntitiesV/Player.h`; der 1.07-Include-Pfad erhielt `Engine107/EntitiesV/`; `Engine107/EntitiesV.lib` wurde als `Engine107/EntitiesMP.lib` kopiert. `dumpbin /headers` zeigt, dass diese mitgelieferte Import-Lib auf `ENTITIESMP.dll` verweist. Kein Entity-Code wurde gebaut.

```powershell
# botcore, Arbeitsverzeichnis poc\botcore, nach Bereitstellung von vcvarsall:
call "C:\Program Files (x86)\Microsoft Visual Studio\2022\BuildTools\VC\Auxiliary\Build\vcvarsall.bat" x86
cl /nologo /EHsc /std:c++17 /O2 /Febotcore_test.exe test_botcore.cpp
botcore_test.exe

# GameMP, PowerShell im Repo:
$sdk = (Resolve-Path '.codex\SE1-ModSDK\Sources').Path + '\'
$ms = 'C:\Program Files (x86)\Microsoft Visual Studio\2022\BuildTools\MSBuild\Current\Bin\MSBuild.exe'
& $ms (Join-Path $sdk 'Game\Game.vcxproj') /t:Rebuild /p:Configuration=Release_TSE107 /p:Platform=Win32 /p:PlatformToolset=v143 /p:UseOfMfc=false "/p:SolutionDir=$sdk" /p:WindowsTargetPlatformVersion=10.0.19041.0 /m:2 /v:minimal

# Laufzeitstarts (jeweils WorkingDirectory = jeweiliger Bin-Ordner):
DedicatedServer.exe BotTest
SeriousSam.exe +connect 127.0.0.1:25600 +quickjoin
SeriousSam.exe +connect 127.0.0.1:25600 +quickjoin +script Scripts\BotStartup.ini
```

`botcore_test.exe` meldete vor und nach dem GameMP-Build `ALL CHECKS PASSED` (1200 Ticks, 2700° Heading, 180 Fire-Ticks). Der Game-Build war erfolgreich. Zwischenfehler (fehlender Include-Pfad und `EntitiesMP.lib`) wurden behoben und neu gebaut; Tests wurden nicht deaktiviert. Die generierten botcore-Testdateien wurden danach entfernt.

## Hashes, PE und Abhängigkeiten

SHA-256 (vor dem Tausch waren alle drei Kopien identisch):

| Datei | Server | Bot-Client | Observer |
|---|---|---|---|
| `Bin/GameMP.dll` vorher | `1C41DA35B3FC47378C407B770E1BD1DCC2B7E6BF676C140586BC6035461D4208` | derselbe | derselbe |
| `Bin/GameMP.dll` final | derselbe | `DB3DC0BCB249DE9644D4AD4E30723F2F62DF43397E4426CDB614E92317264AB6` | derselbe |
| `Bin/EntitiesMP.dll` vorher und final | `7F595F2A7FC96A978B3467983E8F17C70D827F17A5F4EE887F9C7A1F20B1D350` | derselbe | derselbe |

`dumpbin /headers`: `14C machine (x86)`. `dumpbin /exports`: `GAME_Create = _GAME_Create`. Relevante `dumpbin /dependents`: `Engine.dll`, `ENTITIESMP.dll`, `VCRUNTIME140.dll` plus Windows/UCRT-APIs. Der lokal mit v143 aus **unverändertem** SDK-Game-Code gebaute Kontroll-Build hatte SHA-256 `CEC7A0C28C66C8B454DDFFE60D1CBBAE451D3B062887AE5867FFA09D64B38189`.

## BESTÄTIGT

- Der unveränderte Dedicated Server lud seine originale `GameMP.dll`, startete `Levels\LevelsMP\Deathmatch\DM_LittleTrouble.wld` und lauschte auf UDP 25600. Log: `.codex/evidence/server-Dedicated_BotTest.log`.
- Der unveränderte Observer jointe. Client-Log: `joined`; Server-Log: `CRC check OK` und Spieler `joined`.
- Der finale Bot-Build ist eine echte x86-PE-DLL mit `GAME_Create`; der Bot-Client lud sie und führte `Scripts\BotStartup.ini` aus. Sein Log endet nach `Command line connection: '127.0.0.1:25600'`. Log: `.codex/evidence/botclient-final-SeriousSam.log`.
- Beim Bot-Client-Start beendet sich `SeriousSam.exe` reproduzierbar mit `0xC0000005` (`-1073741819`); Windows Application Error 1000 vom 01.10.2026, 16:46:23: Fehlermodul `ntdll.dll`, Offset `0x00087d5c`, Bericht `db6ef379-fd4d-497f-9755-d0677b3ecca1`. Der Server protokolliert dabei keinen Bot-Join und keinen Bot-CRC-Check.
- Derselbe Crash trat mit `bot_bEnabled = 0` und auch mit einer **ohne BotDriver** aus dem SDK mit v143 gebauten `GameMP.dll` auf. Ein zweiter Client mit **originaler** Retail-`GameMP.dll` erreichte dagegen den Server und bestand den CRC-Check; dessen Join wurde erst wegen eines identischen kopierten Spielernamens abgewiesen. Damit ist ein zweiter lokaler Client/Port allein nicht die Crash-Ursache.

## TECHNISCHE SCHLUSSFOLGERUNG

Der GameMP-only-Injektionspfad ist kompiliert, und die DLL wird vom Retail-Client geladen. Der mit MSVC v143 erzeugte SDK-Game-Build ist aber beim Verbindungsaufbau nicht laufzeitkompatibel mit dieser Retail-1.07-Installation. Da bereits der unveränderte SDK-Game-Build gleich crasht, gibt es aktuell keinen Beleg für einen BotDriver-Fehler. Die genaue ABI/CRT-Ursache ist ohne passenden Legacy-Buildpfad oder Crash-Stack nicht nachgewiesen. Das SDK-Projekt deklariert für `Release_TSE107|Win32` ursprünglich `PlatformToolset=v60`; dieses proprietäre Legacy-Toolset ist hier nicht vorhanden.

## OFFEN

- **R-001 CRC-Verhalten:** offen für den GameMP-Swap; der Bot-Client erreicht die CRC-Challenge nicht. `CRC check OK` gilt nur für die beiden Vanilla-Clients.
- **R-002 Retail-Build/Load/Join:** Build und Laden beobachtet; Join scheitert vor der CRC-Phase an `0xC0000005`. Gate bleibt offen.
- **R-003 Bewegung/Feuer/Sync:** keine Runtime-Beobachtung; Gate bleibt offen.
- Nach Behebung des Crashes benötigt der Bot-Client eine eigene Spieleridentität, weil die kopierte Retail-Spielerdatei denselben Namen wie der Observer trägt. Das ist ein separater, belegter Join-Blocker.

**Kleinster nächster Schritt:** Ein zum Retail-1.07-GameMP-ABI passendes Legacy-Toolset bzw. einen nachweislich kompatiblen GameMP-Buildpfad bereitstellen und zuerst die unveränderte SDK-Game-DLL gegen denselben Server joinen lassen. Danach den BotDriver-Build mit eigenem Spielerprofil erneut testen. Die Original-Installation und die beiden Vanilla-Binaries bleiben dafür unverändert.

---

## ABI-/CRT-Fortsetzung – 01.10.2026

Gearbeitet wurde im vorhandenen Projekt `C:\Users\info\Documents\SeriousSam-TSE-Bot-Servermods-`,
weil der neue Desktop-Worktree `5557` nur den alten getrackten Stand enthält.
Vorhandenes SDK, PoC, Retail-Kopien und Belege wurden weiterverwendet. Keine Commits,
kein Push, keine Installation einer weiteren Toolchain. Neue Evidenz:
`.codex/evidence/abi-20261001/`. Alte Logs wurden vor jedem Lauf gesichert.

### BESTÄTIGT: Crashposition und minimale Änderung

1. Neuer Kontrollbuild aus dem **getrackten** SDK-Commit
   `aa7869c2c2c4db0562281814d0ac3784e6b9d6f0`, ohne BotDriver. Die Game-Spiellogik
   (`Game.cpp` und weitere `.cpp`) blieb unverändert. Wie im ersten Lauf musste
   `StdAfx.h` den vorhandenen Retail-Header `EntitiesV/Player.h` verwenden;
   Include-/Import-Library-Pfade wurden angepasst. Das ist kein byte-identischer
   Original-SDK-Build, sondern ein Kontrollbuild mit unveränderter Spiellogik.
2. Der Kontrolllauf `baseline/` crasht nach ungefähr fünf Sekunden mit
   `0xC0000005` / Exitcode `-1073741819`, ohne CRC-Challenge oder Join.
3. Die neue `.RPT` nennt die GameMP-Section-Offets `0001:0001B292`,
   `0001:0000F577`, `0001:0001265E`. Die passende Map und Disassembly zeigen:
   `JoinGame` → `StartProviderFromName` → sized `operator delete` → UCRT-Freigabe
   → `ntdll.dll`. Bei `10010572` steht der Delete-Aufruf; die Rückkehradresse
   `10010577` entspricht exakt dem Stack. Der Aufruf löscht einen 12-Byte-
   `CNetworkProvider` aus der von Engine erzeugten Providerliste.
4. Retail-Engine und Retail-GameMP importieren `MSVCRT.dll`; der moderne
   Kontrollbuild verwendet `VCRUNTIME140.dll` und die UCRT-Heap-API. Die
   Destruktoren des Providers und seiner CTString werden aus Engine importiert;
   die anschließende Objektfreigabe erfolgt im unbereinigten Build über UCRT.
5. **Einzige funktionale Korrektur:** `poc/patch/gamemp/RetailAllocator.cpp`
   verbindet globale skalare/Array-`new` und `delete` einschließlich sized delete
   mit den existierenden `Engine.dll`-Exporten `AllocMemory`/`FreeMemory`.
   Null-Freigaben bleiben erlaubt; Nullgrößen erhalten mindestens ein Byte;
   Größen oberhalb `LONG_MAX` werden abgewiesen. Keine Änderung der Providerlogik,
   der Entities oder der Engine. Das kleine Zusatzobjekt wird ohne PCH gebaut.
6. Mit dieser Anbindung besteht der SDK-Kontrollbuild CRC und Join und bleibt
   30 Sekunden am Leben. Ein zweiter sauber erzeugter SDK-Build besteht denselben
   Test erneut. Der vorhandene BotDriver wurde **erst danach** integriert.

Die Crashursache ist damit für diesen Joinpfad auf die falsche CRT-Zuordnung der
Objektfreigabe eingegrenzt und durch den Vorher-/Nachher-Runtime-Test behoben.
Eine allgemeine Gleichheit aller MSVC-6-/MSVC-2022-ABIs wird daraus nicht behauptet.

### Toolchain, Flags und Buildpfad

- Vorhandene VS Build Tools 2022 `17.14.41`, MSBuild `17.14.60+43b635718`.
- Compiler `19.44.35229` für x86, Tool-Verzeichnis `14.44.35207`, Toolset `v143`.
- Konfiguration `Release_TSE107|Win32`, `UseOfMfc=false`, Windows SDK `10.0.19041.0`.
- SDK-Ursprung deklariert `v60`. Die [Projekt-Buildanleitung](https://github.com/DreamyCecil/SE1-ModSDK/wiki/Building)
  nennt MSVC 6.0 SP6, VS 2010 und Daffodil für historische 1.07-Builds.
  MSVC 6.0 ist nicht vorhanden und wurde nicht aus fremden Archiven beschafft.
  Der beobachtete Joinblocker ließ sich mit den vorhandenen Werkzeugen beheben;
  für diesen Meilenstein war deshalb kein Legacy-Compiler nötig.
- Wesentliche Compileroptionen: `/O2 /Ob1 /Oi /Ot /Oy- /GF /EHsc /MD /GS /Gy-`
  `/fp:precise /Zc:wchar_t /Zc:forScope /Zc:inline /Gd /TP /Zi /W3`,
  `NDEBUG`, `_USE_32BIT_TIME_T`, `SE1_VER=SE1_107`, `SE1_GAME=SS_TSE`.
  SDK-Dateien nutzen `/YuStdAfx.h`, StdAfx.cpp `/Yc`; RetailAllocator.cpp keinen PCH.
- Linker: `/DLL /MACHINE:X86 /INCREMENTAL:NO /DEBUG /MAP /DYNAMICBASE /NXCOMPAT`
  `/SAFESEH`, vorhandene Engine107-/Entities-Importlibs und Windows-Libs.
- Vollständige tatsächliche Compiler-/Linkerargumente inklusive aller Makros:
  `Sources/Obj/vs2022.Release_TSE107/Game/Game.tlog/CL.command.1.tlog`
  und `link.command.1.tlog` in jedem neuen Buildordner.
- Vorbestehende SDK-Warnung `Controls.cpp:226`, C4474 (zusätzliches sscanf-Argument),
  bleibt dokumentiert; nicht Teil dieser Korrektur. Die ersten Vorbereitungsläufe
  scheiterten am fehlenden EntitiesTSE-Includepfad bzw. Postbuild-Zielordner;
  beide sind im ausführbaren Buildskript berücksichtigt.

Reproduzierbarer **Buildablauf**, keine Zusicherung identischer Bytes
(PE-Zeitstempel und PDB-Pfade unterscheiden Builds):

```powershell
# Aus dem Projekt-Hauptordner; BuildDir und Evidence müssen jeweils neu sein.
.\poc\scripts\Build-RetailGameMP.ps1 -Sdk .codex\SE1-ModSDK -BuildDir .codex\abi-sdk-repeat
.\poc\scripts\Test-RetailJoin.ps1 -Dll .codex\abi-sdk-repeat\Sources\Bin\vs2022.Release_TSE107\GameMP.dll -Evidence .codex\evidence\abi-20261001\sdk-repeat -Seconds 30

# Erst nach bestandenem Kontrolltest:
.\poc\scripts\Build-RetailGameMP.ps1 -Sdk .codex\SE1-ModSDK -BuildDir .codex\abi-bot-final -Bot
.\poc\scripts\Test-RetailJoin.ps1 -Dll .codex\abi-bot-final\Sources\Bin\vs2022.Release_TSE107\GameMP.dll -Evidence .codex\evidence\abi-20261001\bot-observer -Seconds 45 -Startup Scripts\BotStartup.ini -Observer
```

`Build-RetailGameMP.ps1` archiviert die getrackten SDK-Game-/Projektdateien nach
einem neuen lokalen Ziel; vorhandene Änderungen im SDK bleiben erhalten.
Includes und EntitiesTSE-Header werden über Junctions gelesen, kein Entities-
Projekt gebaut. Es ergänzt nur Header-/Library-Pfade, Map-Ausgabe, Allocator und
optional die drei vorhandenen BotDriver-Hooks. Ausgabe: GameMP.dll/.lib/.exp/
.map/.pdb, Buildlog, Buildbefehl und SDK-Commit. Das Runtime-Skript tauscht nur
die BotClient-GameMP, startet die vorhandene Vanilla-Serverkonfiguration und
prüft echte Logs/Prozesszustände. Es sichert vorherige Logs/DLL, beendet am Ende
nur selbst gestartete Testprozesse und schreibt `result.json`; Tests dauern ab
Clientstart, die reale Spielzeit nach dem Laden ist etwas kürzer.

### PE-/Importvergleich

| Merkmal | Retail GameMP | moderner Kontrollbuild / Korrektur |
|---|---|---|
| Maschine | x86 (`14C`) | x86 (`14C`) |
| Linker-Indiz | 6.00 | 14.44 |
| SectionAlignment | `0x1000` | `0x1000` |
| FileAlignment | `0x1000` | `0x200` |
| Runtime | MSVCRT.dll | VCRUNTIME140.dll, Windows/UCRT |
| Game-Factory | GAME_Create | GAME_Create = _GAME_Create |
| Engine/Entities | Engine.dll / ENTITIESMP.dll | dieselben Retail-DLLs |
| Objektallokation | Legacy-CRT | nach Korrektur Engine AllocMemory/FreeMemory |

Vollständige Header, Imports, Exports und Sections: `pe-retail.txt`,
`pe-sdk-v143.txt`, `pe-engine.txt`; korrigierte PE-Daten in `allocator/pe.txt`
und abschließender PE-Inventur. Keine Packings-/Calling-Convention-Änderung
vorgenommen; `/Gd` bleibt cdecl für freie Funktionen. Identische PE-Alignments
beweisen keine identischen C++-Layouts.

### Artefakte und SHA-256

| Build | SHA-256 GameMP.dll | Evidenz |
|---|---|---|
| Neuer Kontrollbuild ohne Anbindung | `8A45F41D303E791789B48EB248AB51F49CBCB4CE5BD530555C408A2666CF1DBB` | `baseline/`, GameMP.* im Evidenz-Hauptordner |
| SDK + Allocator, erster Erfolg | `6F39AA046464AFF9054834F03C909A3F1EA7BDF8A3DCDEE6D1333654304F633D` | `allocator/` |
| SDK + Allocator, Wiederholung | `275C30256CEE6A17983E37634242E518D49C483E7DDE85350F283A6145C0ABA0` | `.codex/abi-sdk-repeat/`, `sdk-repeat/` |
| Bot + Allocator, erster Erfolg | `81F7FA921C57C181AA8D3DCF4D9BDCB9692A67B719A90030B38CE306054D54E9` | `.codex/abi-bot-build/`, `bot/` |
| Bot + Allocator, gemeinsamer Observer-Test | `55017E1180025577673DF4966701CD5DA694CF312AFA446C7585E240B5C3CB58` | `.codex/abi-bot-final/`, `bot-observer/` |

### Spieleridentität

Nur `TSE-BotClient/Players/Player0.plr` und `.plr.guid` wurden nach dem SDK-Gate
angepasst: eigener Name `TSE_Bot_PoC`, neue GUID. Vorherige Dateien vollständig in
`profile-before/` gesichert. Das bestehende PLC4-Format wurde vor dem Schreiben
auf Kennung, Stringlängen und Dateigröße geprüft; Team und 32 Appearance-Bytes
beibehalten. Das entspricht der [Croteam-Serialisierung](https://github.com/Croteam-official/Serious-Engine/blob/master/Sources/Engine/Entities/PlayerCharacter.cpp).
Der echte Runtime-Join prüft, dass Retail die Datei tatsächlich liest. Observer-
Profil und originale Steam-Installation wurden nicht verändert.

### BESTÄTIGT: Runtime

- SDK-Kontrollbuild: zweimal 30 Sekunden Prozesslauf, jeweils geladene DLL,
  CRC-Challenge, `CRC check OK`, Server-Spielerjoin und Client-`joined`/`done.`.
- Bot-Build: 30 Sekunden mit aktiver BotStartup.ini, eigene Identität,
  `CRC check OK`, `TSE_Bot_PoC joined`, BotDriver-Ticks und veränderte lokale
  Entitypositionen. Das belegt lokale Bewegung; sichtbare Rotation, Schüsse und
  Schaden sind damit noch nicht separat bewiesen.
- Details des gemeinsamen Observer-Tests stehen in `bot-observer/result.json`,
  `Dedicated_BotTest.log`, `SeriousSam.log` und `observer-SeriousSam.log`.
- Dieser gemeinsame Test lief 45,19 Sekunden ab Bot-Clientstart: Bot und Observer
  blieben am Leben, die Bot-DLL wurde als geladen erkannt, zwei CRC-Prüfungen
  wurden akzeptiert. Serverlog und Observerlog enthalten `TSE_Bot_PoC joined`.
  Botlog reicht bis Tick 800 mit wechselnden Positionen. Kein Crashbericht
  erzeugt. Das ist ein Netzwerkteilnehmer-Nachweis im Observerlog, noch keine
  visuelle Scoreboard-/Gameplay-Abnahme.
- Isolierter Botcore nach Korrektur erneut `ALL CHECKS PASSED`: 1200 Ticks,
  2700 Grad Heading, 180 Fire-Ticks; `.codex/evidence/abi-20261001/botcore.log`.
- Server/Observer behalten originale GameMP mit SHA-256
  `1C41DA35B3FC47378C407B770E1BD1DCC2B7E6BF676C140586BC6035461D4208`.
  EntitiesMP bleibt in allen drei Installationen beim zuvor dokumentierten
  `7F595F2A7FC96A978B3467983E8F17C70D827F17A5F4EE887F9C7A1F20B1D350`.
- Abschließende Inventur: `final-binary-hashes.json`; Engine.dll, SeriousSam.exe
  und DedicatedServer.exe ebenfalls in allen Kopien identisch. PowerShell-
  Syntaxprüfung beider neuer Skripte ohne Fehler. Alle Testprozesse beendet;
  kein UDP-25600-Endpunkt nach Testende vorhanden. Im BotClient bleibt der
  geprüfte finale Bot-Build installiert, ursprüngliche DLLs sind gesichert.

### TECHNISCHE SCHLUSSFOLGERUNG

Ein mit v143 erzeugter GameMP-Build kann den Retail-1.07-Joinpfad durchlaufen,
wenn die Objektallokation an die unveränderte Engine gekoppelt wird. Der erste
Crash war kein Beweis für eine generelle Inkompatibilität moderner Compiler.
Das DLL-übergreifende CRT-Risiko entspricht der
[Microsoft-Dokumentation](https://learn.microsoft.com/cpp/c-runtime-library/potential-errors-passing-crt-objects-across-dll-boundaries).
Die erfolgreichen Builds beweisen CRC-/Join-Kompatibilität für die getestete
Little-Trouble-Session, keine vollständige ABI-Zertifizierung aller Spielpfade.

### OFFEN / NOCH ZU TESTEN

- Andere ABI-Grenzen: insbesondere modulübergreifende Exception-/RTTI-Pfade,
  weitere Objektlayouts und Ressourcenlebenszeiten beim sauberen Beenden.
- Visueller Observer-Nachweis von Bewegung/Rotation/Feuer und Scoreboard.
- Schaden, Frag/Death, Respawn, Mapwechsel, Reconnect, 60 Minuten Synchronität.
- Vollständiges Phase-1-Gate bleibt offen; keine Mehrbot-/KI-Weiterentwicklung.
- Die Testprozesse werden zum Ende beendet; der Test beweist noch keinen
  fehlerfreien regulären Spiel-Shutdown. Keine zusätzliche Crash-RPT in den
  erfolgreichen kurzen Tests beobachtet.

**Nächster kleinster Schritt:** Mit dem gesicherten Bot-Build die normale
Spielerrepräsentation und Aktionen am Vanilla-Observer visuell prüfen, danach
gezielt Schaden/Tod/Respawn und erst anschließend Mapwechsel/Reconnect und
60-Minuten-Synchronität abnehmen. Vorhandene Belege bleiben erhalten.

---

## Phase-1-Fortsetzung – 01.10.2026, 18:04–18:32 Europe/Berlin

**Phase 1: NOCH OFFEN.** Keine Arbeit an Phase 2, Navigation, KI oder mehreren Bots.
Hauptprojekt weiterverwendet; Desktop-Worktree 195b enthaelt den lokalen PoC nicht.
Keine Installation, kein Commit/Push. Vorhandene untracked Dateien und historische
Evidenz erhalten; `.codex/` bleibt lokal ausgeschlossen.

### BESTÄTIGT

- Bewährte Ausgangs-DLL live SHA256
  `55017E1180025577673DF4966701CD5DA694CF312AFA446C7585E240B5C3CB58`.
- Native Vanilla-Serverstatusabfrage (UDP 25601, `\status\`) nennt `gamever=1.07`,
  leeren `activemod`, `numplayers=2`, `player_1=TSE_Bot_PoC`, `frags_1=0`.
  Das beweist Spielername/realen Slot, kein sichtbares Scoreboard.
- Diagnose-Lauf: 120.21 Sekunden mit zwei CRC OK und Vanilla Observer.
  2150 gültige Bot-Snapshots, 1005 verschiedene Positionen, 161 Yaw-Werte;
  329 angewendete Fire-on- und 1821 Fire-off-Samples. 37 beschädigte/interleaved
  Snapshotzeilen werden transparent verworfen, nicht rekonstruiert.
- Zwei gezielte Kampfversuche liefen je 180 Sekunden ohne selbstständigen Crash
  oder protokollierten SyncKick. **Kein positiver Kampfnachweis:** beide Spieler
  durchgehend health 100 und frags 0 in den gültigen Snapshots; Observer blieb
  stationär. Native Serverabfrage im zweiten Kampfversuch ebenfalls beide frags 0.
- Finaler Build mit unverändertem `BotStartup.ini`, ohne Diagnose/Zielmodus:
  60.16 Sekunden, CRC/Join/Bot-Übernahme/Positionen und Vanilla Observer PASS.
- Keine neuen passenden Application-Error-1000/WER-1001-Ereignisse und keine
  neuen Retail-RPT-Dateien im geprüften Zeitfenster. **Kein Shutdown-Nachweis:**
  Testskript beendet Prozesse weiterhin hart. `exitCode=null` in erfolgreichen
  result.json beschreibt den lebenden Prozess vor Cleanup, keinen sauberen Exit.
- Server/Observer-GameMP weiterhin
  `1C41DA35B3FC47378C407B770E1BD1DCC2B7E6BF676C140586BC6035461D4208`.
  EntitiesMP in allen drei Kopien weiterhin
  `7F595F2A7FC96A978B3467983E8F17C70D827F17A5F4EE887F9C7A1F20B1D350`.
  Engine/EXEs untereinander identisch. Keine Steam-Datei verändert.
- Temporäre Anzeigeeinstellungen beider Kopien vollständig aus Backup
  wiederhergestellt und per SHA256 verglichen. Keine Testprozesse oder
  UDP-25600/25601-Endpunkte nach Abschluss.

### GEÄNDERT

- `poc/patch/gamemp/BotDriver.cpp`: abschaltbare, nur lesende Spieler-Snapshots;
  fester Zielindex `bot_iTestTarget` (Default -1). Zieltest nach 20 Sekunden
  Standardbewegung, begrenzte Yaw/Pitch-Korrektur und Colt-Auswahl ausschließlich
  über `CPlayerAction`/`SetAction`. Kein direkter Schaden/Entityeingriff,
  keine Navigation/Zielsuche. Standardstartup behält ursprüngliches Verhalten.
- `poc/botcore/botcore.h`, `test_botcore.cpp`: gemeinsam verwendete einfache
  Zielwinkel-/Winkeldelta-Funktionen; Checks für Achsenkonvention, Pitch,
  ±180°-Übergang und Tick-Drehlimit. Vorhandene 1200-Tick-Tests erhalten.
- `poc/scripts/Build-RetailGameMP.ps1`: gemeinsamen Botcore-Header im Bot-Build
  kopieren. Dieser Pfad benötigt moderne C++-Standardbibliothek/v143;
  keine neue Aussage zur v60-Baubarkeit.
- `Test-RetailJoin.ps1`: optional `-VisibleClients`; nur Client-WindowStyle.
- `Phase1Diagnostics.ini`, `Phase1Combat.ini`: reproduzierbare Diagnose-/Zieltests.
- `Test-Phase1Telemetry.ps1`, `.Tests.ps1`: Auswertung gültiger Snapshots,
  verworfene Zeilen zählen, vorhandene Evidence-Ausgaben schützen, optional
  aktiven lokalen Vanilla-Status einlesen. Keine automatische Gate-PASS-Aussage.
- Runbook, Skript-README, Phase-1-Protokoll und lokaler Projektstand aktualisiert.
  RetailAllocator unverändert.

### TESTS / BUILDS

| Lauf | Ergebnis |
|---|---|
| botcore-before | ALL CHECKS PASSED; 1200 Ticks, 2700 Grad, 180 Fire-Ticks |
| visual-first, 180.17 s | CRC/Join/Prozesse PASS, visuelle Abnahme offen |
| visual-windowed, 79.96 s | Absichtlich beendet; result FAIL/Exit -1, kein spontaner Crash |
| visual-visible, 331.92 s | Absichtlich beendet; result FAIL/Exit -1, kein spontaner Crash |
| diagnostics, 120.21 s | CRC/Join/Prozesse/Snapshot-Telemetrie PASS |
| combat-fixed-target, 180.07 s | CRC/Join/Prozesse PASS; Kampfziel nicht erreicht |
| combat-warmup, 180.29 s | CRC/Join/Prozesse PASS; Kampfziel nicht erreicht |
| default-regression, 60.16 s | Finaler Build mit originalem BotStartup: CRC/Join/Observer/Bewegung PASS |
| Erweiterte Botcore-Checks | RED: neue Aim-Funktionen fehlen; danach GREEN, bestehende Checks erhalten |
| Telemetrie-Regression | ALL TELEMETRY CHECKS PASSED: Health/Frags/Fire, beschädigte Zeile, Ausgabeschutz |
| PowerShell-Syntax | Alle vier Build-/Test-/Auswertungsskripte PASS |

Build-/Runtimebefehle entsprechen dem Runbook. Verwendete lokale Buildziele und Hashes:

| Buildziel `.codex/` | SHA256 GameMP.dll |
|---|---|
| phase1-diagnostics-build | `A3D45A43CDAB0D3AFDA38CB57B60ABBD306D7A38FF0B924C8DDB0AB232599688` |
| phase1-combat-build | `332EE305C9B021F896CF4A8A88014DF3E1C0273A12A6F75B89A29F7586E11FE2` |
| phase1-combat-warmup-build | `E2090990D1CD4FB5B2FB73E1F6AB88FC72B744197C8935A5B2B361266D5BA8DA` (durch finalen Logfix vor Runtime ersetzt) |
| phase1-combat-final-build | `791F68B5F5F01610B9BB9E713B042643F701217539094C5DC97ACFEB92098F32` |

Der finale Build bleibt im isolierten BotClient installiert. Der bewährte
Ausgangsbuild bleibt unter `.codex/abi-bot-final/` und in den Backups erhalten.

### EVIDENZ

`.codex/evidence/phase1-20261001/`:
- Pro Lauf `result.json`, `Dedicated_BotTest.log`, `SeriousSam.log`,
  `observer-SeriousSam.log`, DLL-/Vorlog-Backup. Abgebrochene Läufe mit `run-note.txt`.
- `diagnostics/telemetry.json`; `combat-fixed-target/telemetry.json`;
  `combat-warmup/telemetry.json` und `telemetry-live.json` mit nativer Serverantwort.
- `visual-visible/server-query.txt`; `visual-capture-note.md` mit echten Capture-/Inputfehlern.
- `botcore-before/`, `combat-core/{red,green,warmup-green,final-green}.log`;
  `telemetry-tests.log`; `syntax-check.log`; `BotDriver.diff` gegen gesicherte Ausgangsquelle.
- `final-binary-hashes.json`, `final-process-status.json`, `application-errors.json`,
  `new-rpt-files.json`, `display-config-before/`.
- Buildkommando/Buildlog/SDK-Commit und DLL/PDB/Map unter den jeweiligen Buildzielen.

### TECHNISCHE SCHLUSSFOLGERUNG

Aktuelle Snapshotdaten erweitern den Action-Nachweis um tatsächlich angewendete
Fire-Buttons und Entity-Yaw. Sie beweisen weder sichtbare Schüsse noch Treffer
oder den konsistenten Health-Zustand von Server und Observer. Stagnierende
Zieltestpositionen legen geometrische Blockierung nahe; die genaue Ursache der
fehlenden Treffer ist ohne zuverlässige Schusslinienprüfung nicht bewiesen.
Keine prophylaktische ABI-/Allocator-Änderung erforderlich oder vorgenommen.

### NOCH OFFEN / GATE-STATUS

**Phase 1: NOCH OFFEN.**
- Gate A: sichtbares Scoreboard/Player-Menü; Observer-Sicht auf Bewegung,
  passende Richtung, Rotation/Actions, Fire/Projektile/Hitscanwirkung;
  Teleports, periodische Resets und starke Jitter-/Desync-Bewegung ausschließen.
  Windows Computer Use liefert auch mit sichtbaren 960x540-Fenstern Capture-
  Timeouts; F11 ohne Bilddatei, Bereichsklick ohne verfügbare Koordinatengeometrie.
  Diese visuellen Punkte benötigen eine funktionierende GUI-/menschliche Abnahme.
- Gate B: Schaden beider Richtungen, konsistenter Health-Zustand,
  Frag/Scoreboardzählung, Death-Synchronisation, mehrere Respawns und danach
  gültiger Player mit Bewegung/Rotation/Fire. Beide automatischen Versuche ohne Treffer.
- Gate C: sauberer Disconnect/Slotfreigabe/Observer-Leave/Reconnect/CRC/Actions;
  mindestens zwei Mapwechsel samt Verbindungs-/Actionverhalten.
- Gate D: regulärer Shutdown aller drei Prozesse und Heap-/Allocator-Freigaben.
- Gate E: 10/30/60 Minuten aktive Actions mit Vanilla Observer und Server;
  60-Minuten-Wiederholung. Nicht gestartet: laut Auftrag erst nach Kampfzyklus.

**Kleinster nächster Schritt:** freie Schusslinie zwischen genau diesem Bot und
Vanilla Observer tatsächlich herstellen und einen realen Schaden/Frag plus
mehrere Death-/Respawn-Zyklen belegen. Danach Session- und Soak-Gates in Reihenfolge.

## Fortsetzung 01.10.2026: native Aufnahmen und echter Kampf

Phase 1: NOCH OFFEN. Die bisher fehlende Schusswirkung hatte einen reproduzierten Eingabefehler: `input-speed-diagnosis/SeriousSam.log` meldet `[BotInput] forward=-666.00 up=-666.00`. Die Geschwindigkeitssymbole sind im normalen Entities-Code nicht deklariert. Engine GetFLOAT liefert bei fehlendem/falschem Symbol -666. Damit wurde aus vorwaerts eine volle Rueckwaertsbewegung; der vorgeschlagene Jump wurde zur Duckbewegung. Die vorherige Hypothese ausschliesslicher Wandblockierung war unvollstaendig. Keine neue ABI-/Allocatorursache.

Korrektur in BotDriver.cpp: normierte Achsen und Rotationsdeltas an den vorhandenen exportierten `ctl_ComposeActionPacket` geben; shared Control-Buffer um den Aufruf sichern/leeren/wiederherstellen; normale Fire- und Weapon-Bits anschliessend setzen; weiterhin `CPlayerSource::SetAction`. Der native Composer liefert Retail-Geschwindigkeiten und pflegt lokale SharpTurning-Eingabeakkumulatoren. Keine direkte Placement-/Health-/World-Schreibstelle, keine EntitiesMP-Aenderung. Zielmodus benutzt angewendete Rotationsakkumulatoren, festen Colt und vier Jump-Ticks je 80 Ticks; Standardmodus weiter periodische Bewegung/Rotation/Fire. Kein Warmup mehr. Botcore-Speedreferenz anhand native Retail-Actions auf 10 korrigiert (alter Wert 320 war unbelegt).

Native Aufnahmen: GameMPs vorhandenes `dem_iAnimFrame` speichert TGAs auch dann, wenn Windows.Graphics.Capture keine Bilder liefert. `Test-RetailJoin.ps1 -Observer -CaptureObserver` sichert beide PersistentSymbols.ini, setzt temporaer Window 960x540/FPS 10 bzw. 5/PauseOnMinimize 0, archiviert neue Observer-TGAs unter Evidence/observer-screenshots und stellt die Originale im finally wieder her. Nicht fuer Stunden-Soaks verwenden (etwa 15 MB/s). Native GameMP-Aufnahmen enthalten keine nachgelagerten Konsolen-/Menueoverlays. Preflight blockiert nur eigene isolierte Spielprozesse und belegte UDP-Testports; eine unabhaengige Steam-Instanz wird nicht geschlossen.

Build: `.\poc\scripts\Build-RetailGameMP.ps1 -Sdk .codex\SE1-ModSDK -BuildDir .codex\phase1-native-final-build -Bot`. SHA256: AA0D07C11D00CF92C4908AA7C0C547AC8E96B32685737469701ACF7F87A37984. Build zuvor F985EE468B1B6653389EF3D61D92647926BF86EC2E82FC7CCC9C1AF37B620175; der finale Build korrigiert nur die enginefreie Default-Speedreferenz 320 -> 10.

Alle neuen Belege: `.codex/evidence/phase1-continue-20261001/`.

| Lauf | Dauer / Ergebnis | Aussage |
|---|---|---|
| native-capture | Observer-Join User break, Bot nicht gestartet | Fehlversuch erhalten; kein Botcrashnachweis |
| native-capture-repeat | 20.08 s PASS, 193 TGAs | Native HUD/Spielernamen sichtbar |
| weapon-diagnostics | 60.19 s PASS | Colt/Ammo/Fire/Ray-Diagnose, noch kein Schaden |
| local-input-combat | 90.06 s PASS | Lokaler Eingabespiegel getestet; Capture-Regex traf nicht, Fullscreen statt Window; Originale trotzdem restauriert |
| hole-combat | 90.16 s PASS | Alte Eingabefehler noch vorhanden; kein Schaden |
| skulls-combat | 90.15 s PASS | Angewendete Zielrotation stabil; kein Schaden |
| kunta-combat | 180.23 s PASS | Kein Schaden; UI-W/Control-Eingaben ohne Gameplay-Actions |
| capture-script-regression | 30.18 s PASS, 303 TGAs | Neue Capture-/Archivierungsfunktion und Konfigrestaurierung |
| arena-stage-combat | 120.21 s PASS | Boden-Staging traf nicht; Rueckwaertssymptom fuehrte zur Geschwindigkeitsdiagnose |
| input-speed-diagnosis | 20.16 s PASS | Beide Shell-Reads -666 live bestaetigt |
| native-composer-combat | 120.06 s PASS, 1202 TGAs | Observer health 100 -> 80 -> 60 -> 40 -> 20 -> 0; Bot frags 0 -> 1, Health 100; nativer Observerlog bestaetigt Kill |
| native-keyboard-combat | 180.18 s PASS | Kill wiederholt; alternative Vanilla-Keyboardkonfiguration erzeugt keinen Respawn; restauriert |
| hole-native-respawn | 180.20 s PASS | Finale DLL, Standard-Diagnosemodus: Bewegung/Rotation/Fire laufen; Bot health100, kein Lava-/Respawnnachweis |
| observer-fire-key-combat | 180.15 s PASS | Finale DLL killt Observer; temporaere G-Feuerbindung auch bei 400 kurzen Tastendruecken ohne angewendete Observer-Fire-Actions; Controls aus Backup restauriert |

PASS in der Tabelle bedeutet CRC/Join/Prozessleben mit unveraendertem Server und Observer, nicht Phase-1-Abnahme und nicht regulären Shutdown. Alle alten Builds und Fehlversuche erhalten. Native PNG-Belege fuer Health40 und Health0/Scoreboard1: `native-composer-combat/frame-250.png`, `frame-300.png`, `observer-death.png`. Serverlog nimmt zwei CRCs an; Observerlog meldet den Kill; Health/Frags aus replizierten Bot-Snapshots stimmen mit Observer-HUD ueberein. Eine kontinuierliche serverseitige Healthmessung ist damit nicht bewiesen. Botmodell am linken Bildrand in frame-300 sichtbar, vollstaendige Observer-Bewegungs-/Rotations-/Jitterabnahme noch offen.

Checks: Jump-Test zunaechst Compilerfehler (TestJump fehlte), danach PASS. Speedreferenz-Check zunaechst FAIL fuer320, nach Korrektur PASS. Botcore 1200 Ticks/2700 Grad/180 Fire-Ticks ALL CHECKS PASSED. Telemetrie ALL TELEMETRY CHECKS PASSED. Syntax aller vier PowerShell-Skripte PASS. DLL-Builds erfolgreich. Laufzeitdaten und verworfene Snapshotzeilen in jeweiliger telemetry.json. Keine eigene neue Testnavigation, keine Mehrbots.

Offen: Bot-Schaden/Tod und mehrere Bot-Respawns mit Actions danach; vollstaendige visuelle Abnahme; Disconnect/Reconnect/Slotfreigabe; zwei Mapwechsel; regulaerer Shutdown; 10/30/60-Minuten-Sync und 60-Minuten-Wiederholung. Stockmaps als getrennte Starts ersetzen keinen Mapwechsel derselben Session. Die normale UI-Eingabe fuer Vanilla-Observer-Respawn/Zurueckschiessen ist derzeit der konkrete Blocker. Native Aufnahmen funktionieren; wiederholte kurze sky-Tastendruecke liefern keine beobachteten Gameplay-Actions. F1-Eingabeversuch brachte einen lokalen Testchat-Echo statt Konfigaenderung; wurde nicht als gelungener Konsolenbefehl gewertet.

Naechster Schritt: unveraenderten Vanilla-Observer manuell respawnen und Bot mehrfach erschiessen; Log-/TGA-Erfassung vorhanden. Danach C/D/E in der vorgegebenen Reihenfolge. Phase 2 bleibt bis dahin gesperrt. Kein Phase-1-complete behaupten.

## Fortsetzung 02.10.2026: vier native Bot-Respawns
Cleanup-Race-Test korrigiert: gemeinsam mutierbares Hashtable statt script-scope Flag. Echter Lauf cleanup-race-regression30.19s PASS, simulierte Stop-Process-Ausnahme nach Terminierung tatsaechlich injiziert; alle Prozesse/Ports entfernt, beide Konfigurationen byte-identisch restauriert,300TGAs+3Logs archiviert. Fuenf PS-Syntaxchecks und Telemetriechecks PASS. Standalone Botcorecheck PASS; Testkommentar klaert, dass er keinen nativen Composer ausfuehrt.
Neue Evidenz: .codex/evidence/phase1-20261002. Hole-straight90.13s und Hole-native-combat90.23s CRC/Join PASS, health100; keine Death-/Respawnabnahme daraus.
Fortress-slow-turn180.09s PASS mit finaler AA0D07C-DLL, Vanilla-Observer/Server/Entities. Normale Fragmatch-Stockmap Fortress, TestTarget-1, YawSpeed5. Bothealth Minimum-15.5; vier Todesuebergaenge bei Ticks629/1712/2060/2420, vier Respawns health100 bei664/1744/2104/2464. Observer meldet viermal passed away. Nach jedem Respawn161-388 Positionen und45-153 Fire-on-Samples, jeweils Fire-off vorhanden. Native Frags0->-4 bei Umwelttoden. cycles.json und telemetry.json enthalten Details. Keine direkte Health-/Entity-/World-Manipulation. Reproduzierbares Profil poc/scripts/Phase1Respawn.ini.
Konsolenrootcause geklaert: SDK Console.cpp verlangt im laufenden Spiel / vor Befehlen, sonst Chat. Native Tasten mit Shift+7 erreichen jetzt nachweislich Shellparser; zwei Variablenabfragen scheitern wegen deutscher Zeichentasten (Unterstrich als - bzw. '). Kein erfolgreicher Variablenwechsel behauptet; die -666 Parserausgabe ist kein neuer Speedread im BotDriver.
Little-trouble-wide-fov60.07s PASS,602TGAs: kein Bot im Sichtfeld und kein Schaden. FOV150 wird in normalem Fragmatch durch natives Player.es auf90 gesetzt; Einstellung byte-identisch restauriert. Kein FOV-/Modellgate daraus ableiten. Skulls-native-visual90 laeuft fuer sichtbare Spielerrepraesentation.
Phase1 weiterhin OFFEN: gesamte visuelle Bewegung/Rotation/Jitter-Abnahme und vollstaendige serverseitige Schadenskonsistenz noch nicht belegt; danach C/D/E. Kein Phase2, kein Commit/Push bisher. Manual-combat-ready vom Vortag ist abgeschlossen, nicht mehr aktiv.

Neuester Stand: Fortress-Zyklen durch unabhaengigen Reviewer gegen Rohlog bestaetigt, keine neuen relevanten Codebefunde. Skulls-native-visual90.26s PASS,902TGAs, Beobachterblick aus einem anderen Raum; contact.png zeigt noch kein Botmodell, keine Gate-A-Freigabe. Kunta-native-combat120 prueft erstmals den korrigierten nativen Composer auf dieser Stockmap; laeuft. Kurze manuelle Observer-Kameraausrichtung angefragt, weil automatisierte Eingaben keine Gameplay-Actions liefern. C/D/E weiterhin nach den offenen vorherigen Abnahmen.

## Gesicherter Zwischenstand 02.10.2026
Kunta-native-combat120.07s: CRC/Join/Prozessleben PASS,1200TGAs; health100 bei beiden Spielern, geometrisch getrennte Ebenen. contact.png zeigt kein Botmodell. Damit keine weitere visuelle Freigabe.
Alle eigenen Testprozesse und UDP25600/25601 beendet; Bot-/Observer-Displayconfigs und Servermap aus Backups byte-identisch restauriert. Finale DLL weiterhin AA0D07C11D00CF92C4908AA7C0C547AC8E96B32685737469701ACF7F87A37984. Reviewer ohne neue relevante Befunde.
Phase1 NOCH OFFEN. Neu belegt: vier normale Umwelt-Deaths/Respawns mit Actions danach. Noch offen: sichtbare Botbewegung/-rotation und Jitterpruefung, volle Schadenskonsistenz; danach Reconnect, zwei Mapwechsel, regulaerer Shutdown,10/30/60min-Sync. Phase2 nicht begonnen. Benoetigter naechster Schritt: Vanilla-Observer manuell zum Bot ausrichten; automatisierte Tastendruecke erzeugen keine beobachteten Gameplay-Actions. Die Anfrage dazu bleibt ohne Antwort.
Der Quell-/Test-/Dokustand wird als wertvoller Zwischencheckpoint gesichert; Retailkopien, DLLs und TGAs bleiben lokal ausgeschlossen.
