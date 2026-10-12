@echo off
rem ============================================================
rem start-bot-client.bat - Bot-Client Phase 1 (1 Bot-Spieler)
rem Voraussetzungen:
rem   - unveraenderte TSE-1.07-Installation in BOT_DIR
rem   - NUR GameMP.dll gegen Bot-Build getauscht (Backup!),
rem     alle anderen Dateien byte-identisch zum Server (Hash-Check!)
rem   - Scripts\BotStartup.ini vorhanden (bot_bEnabled = 1)
rem ============================================================
setlocal
set "BOT_DIR=C:\Games\TSE-BotClient"
set "SERVER_IP=127.0.0.1"
set "SERVER_PORT=25600"

cd /d "%BOT_DIR%\Bin" || exit /b 1
if not exist SeriousSam.exe (
  echo FEHLER: SeriousSam.exe nicht gefunden in %BOT_DIR% - BOT_DIR anpassen!
  pause
  exit /b 1
)
if not exist "%BOT_DIR%\Scripts\BotStartup.ini" (
  echo FEHLER: Scripts\BotStartup.ini fehlt in %BOT_DIR%!
  pause
  exit /b 1
)

echo Hinweis: GameMP.dll muss der Bot-Build sein (siehe RUNBOOK.md Schritt 3).

echo Starte Bot-Client, verbinde mit %SERVER_IP%:%SERVER_PORT% ...
echo Der Bot bewegt sich vorwaerts, dreht langsam und feuert periodisch.
start "" SeriousSam.exe +connect %SERVER_IP%:%SERVER_PORT% +quickjoin +script Scripts\BotStartup.ini
endlocal
