# Lokales Bot-Release für Serious Sam TSE 1.07

Dieses Paket stellt automatische Deathmatch-Bots in zwei getrennten BotClient-Prozessen mit jeweils vier lokalen Spielern bereit. Der Bot verwendet den nativen Action-Composer und die normalen Netzwerkaktionen. Sichtprüfung, Waffenwahl, native Respawn-Eingaben und begrenzte reaktive Hinderniserholung laufen im BotClient-GameMP.

Der freizugebende DLL-Kandidat hat SHA256 `61DC27E0E7B80BADCF9AE705C30FCA88EDD3935737715DFFFF59E90C26F1FEF9`. Die öffentliche Konsolidierung steht in `docs/reports/2026-10-12-shadow-development-status.md`; die genaue lokale Abnahme steht unter `.codex/evidence/shadow-20261010/local-release/report.md`. Nur ein dort mit `passed: true` belegter Lauf zählt als Abnahme. Frühere Stundenläufe anderer DLLs werden nicht übertragen.

## Betrieb vorbereiten

Es werden die vorhandenen fünf getrennten 1.07-Kopien unter `.codex/retail` verwendet: Server, Observer, Human und zwei BotClients. Steam-Installation, Server, Observer und Human behalten ihre originalen Binärdateien. Die BotClient-Kopien müssen echte getrennte Installationen mit eigenen `Players`, `Data`, `Scripts` und Logs sein. Die maximale lokale Spielerzahl ist vier pro Prozess; acht Bots benötigen zwei Prozesse.

Die folgenden Befehle werden aus dem Repository ausgeführt. Der unveränderte Dedicated Server muss bereits auf `127.0.0.1:25600` laufen. Ein Server mit mindestens neun freien Gesamtplätzen erlaubt zusätzlich einen menschlichen Client; das lokale Prüfprofil verwendet 16 Plätze.

```powershell
$repo = (Get-Location).Path
Set-Location -LiteralPath $repo
$run = New-Item -ItemType Directory -Path '.codex\local-bot-run-001'
$config = Get-Content -LiteralPath 'poc\scripts\local-release-fleet.sample.json' -Raw | ConvertFrom-Json
$config.processes[0].clientDir = Join-Path $repo '.codex\retail\TSE-BotClient'
$config.processes[1].clientDir = Join-Path $repo '.codex\retail\TSE-BotClient2'
$configPath = Join-Path $run.FullName 'fleet.json'
$config | ConvertTo-Json -Depth 5 | Set-Content -LiteralPath $configPath
$dll = Join-Path $repo '.codex\shadow-20261010-release-render-lock\Sources\Bin\vs2022.Release_TSE107\GameMP.dll'
& 'poc\scripts\Initialize-LocalBotRelease.ps1' -Config $configPath -Dll $dll -Backup (Join-Path $run.FullName 'backup')
& 'poc\scripts\Start-BotFleet.ps1' -Config $configPath -State (Join-Path $run.FullName 'fleet-state.json')
```

Die Vorbereitung prüft den nativen Marker `Data\Var\Sam_Version.var` mit Wert `v1.07` sowie native `GAMEV012`- und `PLC4`-Formate, erzeugt acht verschiedene Profil-/Sidecar-GUIDs, stellt Fensterbetrieb und begrenzte Bildraten ein und sichert jeden geänderten Dateizustand vor dem Schreiben. Sie ersetzt ausschließlich das BotClient-GameMP und dessen lokale Einstellungen/Profile. Bereits laufende BotClients und vorhandene Backup-Verzeichnisse werden zurückgewiesen. Die Statusdatei des Starters dokumentiert Prozesse; der Starter allein bestätigt keinen erfolgreichen Beitritt oder CRC.

`LocalBotRelease.ini` aktiviert AutoCombat und Hinderniserholung, schließt lokale Mitspieler als Kampfziele aus, protokolliert nur einmal pro Sekunde und schaltet vollständige Snapshot-Diagnostik aus. Gegner des zweiten BotClient-Prozesses und menschliche Gegner können als Ziele gewählt werden. Das ausführliche Abnahmeprofil `Phase1ObstacleAvoidance.ini` erlaubt lokale Testgegner und schreibt jeden 20-Hz-Tick.

## Beenden und Originalzustand zurücknehmen

```powershell
& 'poc\scripts\Stop-BotFleet.ps1' -State (Join-Path $run.FullName 'fleet-state.json') -GracefulWaitSeconds 5
& 'poc\scripts\Restore-LocalBotRelease.ps1' -Backup (Join-Path $run.FullName 'backup')
```

Die Rücknahme prüft sämtliche Backup-Hashes und Zielpfade vor dem ersten Schreiben. Sie stellt ursprüngliche Dateien bytegenau wieder her und entfernt einzeln die Dateien, die vor der Vorbereitung fehlten. Engine, Entities und Client-EXE werden zusätzlich gegen ihre vor der Vorbereitung gelesenen Hashes geprüft. Backup und Stop-Nachweis bleiben erhalten. Ein neuer Start verwendet ein neues Run-Verzeichnis.

## Quellbuild und erneute native Prüfung

Die vollständigen dreizehn geänderten GameMP-Quelldateien liegen in `poc/release/gamemp`. Dazu gehört `LoadingHook.cpp` mit dem Abbruch eines ausstehenden Reconnects bei Escape. Vor den datierten Lizenzhinweisen zur Veröffentlichung wurden alle 32 kompilierten Game-Quelldateien des Kandidaten mit dem vollständigen neuen Quellbuild bytegenau verglichen. `docs/reports/2026-10-12-source-verification.json` enthält Original- und Veröffentlichungs-Hashes; das Entfernen ausschließlich des dort dokumentierten Hinweisblocks ergibt die originalen 13 erfassten Dateien. Der Build benötigt den getrennt bezogenen SE1-ModSDK-Stand `aa7869c2c2c4db0562281814d0ac3784e6b9d6f0`, das saubere Includes-Unterprojekt `94ff8cd0e63941f8601294350b616472f772ed51`, unveränderte Entities-Header, VS2022 Build Tools v143 x86 und Windows SDK 10.0.19041.0. Veränderte oder zusätzliche Dateien in den Header-/Importbibliothek-Eingaben werden vor dem Anlegen des Buildverzeichnisses zurückgewiesen.

```powershell
git clone 'https://github.com/DreamyCecil/SE1-ModSDK.git' '.codex\SE1-ModSDK'
git -C '.codex\SE1-ModSDK' checkout --detach aa7869c2c2c4db0562281814d0ac3784e6b9d6f0
git -C '.codex\SE1-ModSDK' submodule update --init --recursive
& 'poc\scripts\Build-LocalBotRelease.ps1' -Sdk '.codex\SE1-ModSDK' -BuildDir '.codex\my-release-build'
```

Die Clone-Befehle dienen einer frischen Umgebung. Die bereits vorhandene geprüfte `.codex/SE1-ModSDK`-Kopie dieses PCs bleibt erhalten. Includes ist ein Unterprojekt desselben Upstream-Repositories auf dessen Includes-Stand; es wird durch den festgelegten SDK-Gitlink auf den genannten Commit gesetzt.

Der Build verwendet die erfassten Änderungen einschließlich `StdAfx.h`, Retail-Allocator und Importbibliothek-Anpassung. Er baut ausschließlich GameMP für `Release_TSE107|Win32`; er baut und verteilt keine Retail-Engine, Entities oder Spieldaten. Der historische Vergleichsbuild vor den Veröffentlichungshinweisen entstand aus bytegleichen Originalquellen und besitzt einen anderen DLL-Hash; auch die PE-Sektionen `.text`, `.rdata` und `.reloc` unterscheiden sich. Eine ausschließlich auf Metadaten beschränkte Abweichung oder ein byteidentischer Binärbuild wird daher nicht behauptet. Eine selbst gebaute DLL ist ein eigener nativer Prüfkandidat. Für die obigen Betriebsbefehle wird der tatsächlich abgenommene DLL-Hash verwendet.

Das ursprüngliche Hindernis-GameMP bleibt erhalten. Patch `0006` sichert Timer-Entityzugriffe und komplette Ray-Lebenszeiten mit der nativen World-/Network-Sperre; Patch `0007` schützt den Renderdurchlauf mit der Timer-Hooks-Sperre. Damit werden sowohl der gemeinsame Ray-Sektorstapel als auch konkurrierende Schreibzugriffe auf dessen Sektorflags ausgeschlossen. Die Reihenfolge bleibt Hooks1000 vor Network2000; Thumbnail- und Prescan-Sperren sind rekursiv.

Die native Abnahme läuft stets einzeln mit Sicherungs- und Rücknahmehülle:

```powershell
& 'tools\run-shadow-fleet.ps1' -Evidence '.codex\evidence\my-release-hour' -Seconds 3700 -SyncMinutes 0 -Lifecycle -Dll $dll -StartupSource 'poc\scripts\Phase1ObstacleAvoidance.ini'
& 'python' -B 'poc\scripts\Test-FleetAIEvidence.py' '.codex\evidence\my-release-hour' --dll $dll --startup 'poc\scripts\Phase1ObstacleAvoidance.ini' --minutes 60 --output '.codex\evidence\my-release-hour\acceptance-audit.json'
```

Der eigenständige Auditor liest die Logs mit begrenztem Speicher, prüft den letzten nativen Player-Source-Abschnitt jedes Prozesses und ordnet versetzte lokale Tickzähler dem gemeinsamen Snapshot-Zeitpunkt zu. Er verlangt je Bot 60 vollständige Fenster mit 1200 zusammengehörigen Navigation-, Combat-, Driver- und replizierten Snapshot-Datensätzen, begrenzte Aktionen, reale Wand-Ausweichfortschritte und lebende Kampfeingaben. Außerdem prüft er acht Namen/GUIDs, kontinuierliche Serverantworten, Originalversion/Modstatus, CRC, den menschlichen Beitritts-/Austrittsablauf, Prozessersatz sowie Rücknahme und Crashdiagnostik. Bewegungs-, Ziel-, Todes-, Hold- und Fire-Werte werden pro Fenster ausgewiesen. Legitime Pausen ohne sichtbaren Gegner werden nicht durch erzwungenes Feuern kaschiert.

Query- und CPU/RAM-Dateien müssen unabhängig mindestens 3600 Sekunden umfassen, ohne mehr als 60 Sekunden zwischen Samples. Die CPU-Zahl im Audit ist Prozent eines logischen CPU-Kerns; sie ist kein bereits durch die Anzahl der Host-Kerne geteilter Taskmanager-Prozentwert. Die Laufzeit im nativen `result.json` kann die anschließende Logauswertung enthalten. Deshalb zählt für die echte Stundenmessung zusätzlich die Zeitspanne der Serverabfragen.

Das exakte sparsame Betriebsprofil wird anschließend separat geprüft:

```powershell
& 'tools\run-shadow-fleet.ps1' -Evidence '.codex\evidence\my-production-smoke' -Seconds 180 -SyncMinutes 0 -Lifecycle -NativeJoinOnly -Dll $dll -StartupSource 'poc\scripts\LocalBotRelease.ini'
& 'python' -B 'poc\scripts\Test-LocalReleaseSmoke.py' '.codex\evidence\my-production-smoke' --dll $dll --startup 'poc\scripts\LocalBotRelease.ini' --output '.codex\evidence\my-production-smoke\production-audit.json'
```

`NativeJoinOnly` bezeichnet ausschließlich das Weglassen des alten Snapshot-Prüfers im Runner. Native Version, acht reale Namen/Profile, CRC, Lifecycle, Runtime-Fehler, Ressourcen, Stop und Restore werden weiter geprüft. Der nachgeschaltete Smoke-Auditor verlangt bytegleich `LocalBotRelease.ini`, vollständige regelmäßige Combat-/Navigation-/Driver-Samples alle 20 Ticks und prüft zusätzlich sämtliche protokollierten Ereigniszeilen. Er weist lokale Kampfziele und ungültige Eingaben zurück und verlangt echte Bewegung sowie lebende Kampfbereitschaft aller acht Bots. Dieser kurze Nachweis ersetzt keinen vollständigen 20-Hz-Stundenlauf und keine Wand-Erfolgsprüfung pro Bot.

`Package-LocalBotRelease.ps1` erstellt nach der vollständigen lokalen Abnahme ein Quell-ZIP. Es verlangt aktuelle erfolgreiche Abnahme- und Originalerhaltungsbelege, gleicht alle dreizehn erfassten GameMP-Quellen und den vollständigen eindeutigen 32-Dateien-Quellvergleich ab und verifiziert jeden ZIP-Eintrag gegen SHA256. `SOURCE-MANIFEST.json` nennt Quellen und SDK-Stände; Retail-DLLs, EXEs, SDK-Importbibliotheken, Spieldaten, Rohlogs und Backup-Dateien werden nicht eingepackt.

## Umfang

Dieses Release ist auf lokale Stockmap-Deathmatch-Prüfungen ausgelegt. Hinderniserholung ist eine begrenzte Reaktion mit drei kurzen Kollisionsstrahlen. Globale Wegfindung, Item-Routen, Bodenerkennung und Abgrundsicherung, Coop, Internetbetrieb und 24/7-Dauerbetrieb benötigen weitere Entwicklung beziehungsweise eigene native Abnahmen. Insbesondere kann ein Bot auf Stockmaps an einem Abgrund sterben; native Respawn-Eingaben ersetzen keine Bodennavigation.

Die GPLv2-Lizenz und die Attributionen von Croteam/DreamyCecil bleiben in den Quelldateien und `poc/release/LICENSE` erhalten. Das Quellpaket enthält keine kommerziellen Spieldaten oder originalen Retail-Binärdateien. Der veröffentlichte Quellstand und die Abnahmegrenzen stehen in `docs/reports/2026-10-12-shadow-development-status.md`. Rohlogs und lokale Qualifikationsarchive bleiben privat.
