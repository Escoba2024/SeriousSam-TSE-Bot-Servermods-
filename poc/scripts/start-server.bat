@echo off
rem ============================================================
rem start-server.bat - Vanilla TSE 1.07 Dedicated Server (Phase 0)
rem Vorher: scripts\dedicated-config\ nach <SERVER>\Scripts\Dedicated\BotTest\ kopieren
rem         und Map/Session-Name dort anpassen!
rem ============================================================
setlocal
set "SERVER_DIR=C:\Games\TSE-Server"
set "CONFIG=BotTest"

cd /d "%SERVER_DIR%\Bin" || exit /b 1
if not exist SeriousSam.exe (
  echo FEHLER: SeriousSam.exe nicht gefunden in %SERVER_DIR% - SERVER_DIR anpassen!
  pause
  exit /b 1
)

if exist DedicatedServer.exe (
  echo Starte DedicatedServer.exe (Konfiguration: %CONFIG%) ...
  echo Log: %SERVER_DIR%\Dedicated_%CONFIG%.log
  start "" DedicatedServer.exe %CONFIG%
) else (
  echo Keine DedicatedServer.exe gefunden.
  echo Fallback: Server ueber das Menue starten:
  echo   SeriousSam.exe -^> Multiplayer -^> New Game -^> Split-Screen: "Dedicated"
  echo   -^> Deathmatch + Map + MaxPlayers setzen -^> Start
  start "" SeriousSam.exe
)
endlocal
