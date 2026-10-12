@echo off
rem ============================================================
rem hash-inventur.bat [Zielordner] - SHA-256-Inventur einer TSE-Installation
rem Zweck: Nachweis, dass EntitiesMP.dll / Engine.dll / SeriousSam.exe / .gro
rem        in allen Installationen (Server, Bot-Client, Observer) identisch sind.
rem Ausgabe: tse-hash-inventur.txt neben dem Zielordner
rem ============================================================
setlocal
set "TARGET=%~1"
if "%TARGET%"=="" set "TARGET=C:\Games\TSE-Server"

if not exist "%TARGET%\Bin\SeriousSam.exe" (
  echo FEHLER: %TARGET% enthaelt keine SeriousSam.exe - Pfad als Argument uebergeben!
  echo Aufruf: hash-inventur.bat C:\Games\TSE-Server
  pause
  exit /b 1
)

for %%D in ("%TARGET%") do set "PARENT=%%~dpD"
set "OUT=%PARENT%tse-hash-inventur-%~n1.txt"

echo TSE-1.07 Hash-Inventur>"%OUT%"
echo Ziel : %TARGET%>>"%OUT%"
echo Datum: %DATE% %TIME%>>"%OUT%"
echo.>>"%OUT%"
echo --- Kern-Dateien --->>"%OUT%"
for %%F in (SeriousSam.exe DedicatedServer.exe Engine.dll EntitiesMP.dll GameMP.dll GameGUIMP.dll) do (
  if exist "%TARGET%\Bin\%%F" (
    echo [%%F]>>"%OUT%"
    certutil -hashfile "%TARGET%\Bin\%%F" SHA256>>"%OUT%"
  ) else (
    echo [%%F] NICHT VORHANDEN>>"%OUT%"
  )
)
echo.>>"%OUT%"
echo --- GRO-Dateien (Spieldaten, CRC-relevant) --->>"%OUT%"
for %%F in ("%TARGET%\*.gro") do (
  echo [%%~nxF]>>"%OUT%"
  certutil -hashfile "%%F" SHA256>>"%OUT%"
)
echo.>>"%OUT%"
echo --- Version --->>"%OUT%"
if exist "%TARGET%\Data\Var\Sam_Version.var" (
  type "%TARGET%\Data\Var\Sam_Version.var">>"%OUT%"
)
echo.
echo Fertig: %OUT%
echo Datei im Projektordner (Drive: "Serious Sam TSE Projekt") ablegen.
notepad "%OUT%"
endlocal
