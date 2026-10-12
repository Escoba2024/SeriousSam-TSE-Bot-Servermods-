# Publikationsprüfung – 12.10.2026

Der Auftrag synchronisiert vorhandene Entwicklung. Es wurden keine neuen Bot-Funktionen und keine weiteren nativen Spieleläufe gestartet. Erneut geprüft wurden kurze Regressionen, die Source-Provenance, die Release-Reproduktion und der erhaltene lokale Runtime-Zustand.

| Prüfung | Ergebnis |
|---|---|
| Vollständige private Sicherung | PASS: 59.092 Dateien; 7.188.641.366 unkomprimierte Bytes; jeder ZIP-Eintrag mit SHA256 rückgelesen. ZIP-SHA256 `03AB0E29FA61058A994CB9106AD8D03490E8A1302BB2DEFA9496CB15BE459DA2`. Git-Bundle mit vollständiger Historie geprüft. Junctions wurden nicht verfolgt; ihre realen SDK-Ziele sind im Quellbackup enthalten. |
| Sechs C++-Kernsuiten | PASS: botcore, botcore_ai, Reconnect, Combat, native WeaponInput und ObstacleRecovery. Default `make test` umfasst jetzt alle sechs vorhandenen Suiten. |
| Extrahierter Game-Reconnect-Integrationstest | PASS: reale veröffentlichte Game-/BotDriver-/LoadingHook-Blöcke kompiliert; fehlgeschlagener Join, Backoff, Stop/Targetwechsel, Escape/Close/Quit und Exception-Recovery geprüft. Die ältere Testumgebung wurde um die atomare Windows-Grenze des bereits bestehenden Reset-Hooks ergänzt. |
| Python-Fixtures | PASS: 25 Fleet-AI + 9 Obstacle + 10 Sparse-Smoke + 6 Combat = 50 Fälle. Combat-Fixtures verwenden zusätzlich private akzeptierte Altbelege. |
| PowerShell-Regressionen lokal | PASS: 20 Suiten einschließlich 15 Fleet-Suiten, Vorbereitung/Rücknahme, Telemetrie, Join-State, Runtime-Log und Paket-Negativfälle. |
| Paket-Negativfälle | PASS: sechs Fälle für fehlgeschlagene/veraltete Abnahme, doppelte erfasste Quellen, fehlende/doppelte/geänderte kompilierte Eingaben. Original-/Veröffentlichungs-Hashes und exakter Lizenzhinweisblock werden vor Archivschreiben geprüft. |
| Separater frischer Git-Checkout | PASS: 19 portable PowerShell-Suiten, 44 portable Python-Fixtures, 13 veröffentlichte Quellen plus exakt rekonstruierte Original-Hashes. Der lokale Pakettest mit ursprünglichem Kandidaten-SDK und die Combat-Altbelege sind zusätzliche lokale Prüfungen, keine versteckten Voraussetzungen der portablen Suiten. |
| Source-only GameMP-Rebuild aus separatem Checkout | PASS: gepinnter SDK/Includes-Stand, VS2022/v143/Win32/SDK10.0.19041.0; Build-DLL SHA256 `90CD86BF7FE53BF9C401B4C0869A85D2DE2A6722BAD66220F0EF5E70BC951713`. Dieser neue Build besitzt keine eigene native Abnahme. Qualifiziert bleibt die unveränderte 61DC-DLL. |
| Git-Blob-/Checkout-Hashes | PASS: alle 13 Provenance-Dateien und beide exakten QA-/Production-INIs. `.gitattributes` verhindert Checkout-bedingte Änderungen ihrer Bytes. |
| Runtime-Erhaltung | PASS: 30 Originalbinaries, 815 globale Dateizustände und ältere qualifizierte DLLs unverändert; keine eigenen Spielprozesse oder belegten Testports. Die drei ursprünglich schmutzigen Dateien sind im geprüften Backup erhalten. Der Makefile wurde für die Testziel-Vervollständigung absichtlich geändert; die beiden Telemetrie-Dateien blieben bytegleich. |
| Veröffentlichungsscope | Keine `.codex`-/Ground-/Scratch-Dateien, Retail-Binaries/Assets, Profile/GUIDs, SDK-Importbibliotheken oder Archive im Git-Dateibaum. Bereinigte Berichte enthalten keine privaten Runtime-Identitäten. GPL-Hinweise/Attribution erhalten; datierte Hinweise und Original-/Veröffentlichungs-Hashes erfasst. |

## Portable Regressionen

Aus dem Repository in PowerShell 7 mit Python 3:

```powershell
pwsh -NoProfile -File tools/Test-Publication.ps1 -Evidence .codex/verification-001 -Python python
python -B tools/Verify-SourceProvenance.py
```

Bei GNU Make und einem C++17-Compiler: `make -C poc/botcore test`. Alternativ in einem x86 Native Tools Terminal von VS2022:

```powershell
$out = (New-Item -ItemType Directory .codex/cpp-001).FullName
foreach ($test in 'test_botcore','test_botcore_ai','test_bot_reconnect','test_bot_combat','test_bot_weapon_input','test_bot_navigation') {
    cl /nologo /std:c++17 /EHsc /O2 /D_CRT_SECURE_NO_WARNINGS /Fo"$out/$test.obj" /Fe"$out/$test.exe" "poc/botcore/$test.cpp"
    if ($LASTEXITCODE) { throw "Build failed: $test" }
    & "$out/$test.exe"
    if ($LASTEXITCODE) { throw "Test failed: $test" }
}
python -B poc/scripts/Test-BotReconnectIntegration.py poc/release/gamemp/Game.cpp poc/release/gamemp/BotDriver.cpp "$out/reconnect.cpp" poc/release/gamemp
cl /nologo /std:c++17 /EHsc /O2 /Ipoc/release/gamemp /Fo"$out/reconnect.obj" /Fe"$out/reconnect.exe" "$out/reconnect.cpp"
if ($LASTEXITCODE) { throw 'Reconnect harness build failed' }
& "$out/reconnect.exe"
if ($LASTEXITCODE) { throw 'Reconnect harness failed' }
```

## Veröffentlichungskorrekturen und Grenzen

Vorhandene Sicherungshüllen/Auditoren wurden aus dem privaten `.codex`-Arbeitsordner in `tools/` erfasst; die ursprünglichen lokalen Kopien bleiben erhalten. Dokumente, Regressionen und Packager benutzen die öffentlichen Pfade. Der Packager hat eine explizite Dokumentauswahl, sodass lokal vorhandene unqualifizierte Ground-Pläne nicht versehentlich ins qualifizierte Paket geraten. Seine privaten Abnahme-JSONs können lokale Pfade enthalten; für Git wurden ausschließlich bereinigte Zusammenfassungen übernommen.

Ältere BAT-Vorlagen verwenden jetzt die tatsächlichen `Bin`-Verzeichnisse. Sie benötigen manuell angepasste Installationspfade und sind kein Runtime-Abnahmebeleg. Für das aktuelle Release gelten die geprüften PowerShell-Werkzeuge. Herkunfts- und Patchdateien behalten ihre notwendigen upstreambedingten Bytes; dokumentierte Whitespace-Attribute schützen diese Quellen, während die übrigen Änderungen normal durch `git diff --check` geprüft werden.

Die unabhängige Veröffentlichungsprüfung umfasst Quellen, Geheimnis-/Dateiscope, Lizenz-/Provenance-Hinweise, Dokumentkonsistenz und Reproduzierbarkeit. Ein bestandener frischer Build oder Unit-Test überträgt keine native Abnahme auf die neu gebaute DLL. Historische lokale Stunden und aktuelle 61DC-KI-Stunde bleiben getrennte Belege. Ground, globale Navigation, öffentlicher Browser, größere Skalierung und 24/7 bleiben offen.
