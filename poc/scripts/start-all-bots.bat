@echo off
rem ============================================================
rem start-all-bots.bat - Phase 3: mehrere Bot-Client-Prozesse starten
rem Voraussetzung pro Bot-Client N:
rem   C:\Games\TSE-BotClient-N\  (eigene Installation, getauschte GameMP.dll,
rem   Scripts\BotStartup.ini, eigenes Spielerprofil/eigener Name im Menue gesetzt)
rem Grenzen: 4 Bots pro Prozess (NET_MAXLOCALPLAYERS), 16 Spieler gesamt
rem (NET_MAXGAMEPLAYERS) - Bots + echte Spieler zusammen!
rem ============================================================
setlocal EnableDelayedExpansion
set "BASE=C:\Games"
set "SERVER_IP=127.0.0.1"
set "SERVER_PORT=25600"
set "DELAY=5"

for %%I in (1 2 3 4) do (
  if exist "!BASE!\TSE-BotClient-%%I\Bin\SeriousSam.exe" (
    if exist "!BASE!\TSE-BotClient-%%I\Scripts\BotStartup.ini" (
      echo Starte Bot-Client %%I ...
      start "" /D "!BASE!\TSE-BotClient-%%I\Bin" "!BASE!\TSE-BotClient-%%I\Bin\SeriousSam.exe" +connect %SERVER_IP%:%SERVER_PORT% +quickjoin +script Scripts\BotStartup.ini
      timeout /t %DELAY% /nobreak >nul
    ) else (
      echo UEBERSPRUNGEN: TSE-BotClient-%%I hat keine Scripts\BotStartup.ini
    )
  ) else (
    echo UEBERSPRUNGEN: !BASE!\TSE-BotClient-%%I nicht gefunden
  )
)

echo.
echo Alle gefundenen Bot-Clients gestartet (gestaffelt, %DELAY% s Abstand).
echo Beobachten: Server-Log + Scoreboard; Ressourcenlast im Task-Manager pruefen.
pause
