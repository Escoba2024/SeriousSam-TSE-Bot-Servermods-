@echo off
rem ============================================================
rem start-observer.bat - unveraenderter Vanilla-Beobachter-Client (Phase 0A/1)
rem Der Client bleibt komplett unmodifiziert (Referenzinstallation)!
rem ============================================================
setlocal
set "OBS_DIR=C:\Games\TSE-Observer"
set "SERVER_IP=127.0.0.1"
set "SERVER_PORT=25600"

cd /d "%OBS_DIR%\Bin" || exit /b 1
if not exist SeriousSam.exe (
  echo FEHLER: SeriousSam.exe nicht gefunden in %OBS_DIR% - OBS_DIR anpassen!
  pause
  exit /b 1
)

echo Starte Beobachter-Client, verbinde mit %SERVER_IP%:%SERVER_PORT% ...
start "" SeriousSam.exe +connect %SERVER_IP%:%SERVER_PORT% +quickjoin
endlocal
