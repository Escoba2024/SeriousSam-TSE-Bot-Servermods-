# TECHNICAL_HANDOFF – P0 BotDriver-Diagnose + gültiger Null-Render-A/B (2026-10-21)

Von: unabhängiger Review-Agent (`arena/e39db2a9-serioussam-tse-bot-servermods`).
An: Hauptagent (Hetzner-Workspace). Kontext: [Unabhängiges Review](../research/2026-10-21-independent-review-cpu-optimization.md).
Dieser Handoff ist eine Spezifikation – **keine** Freigabe für Produktionsprozesse.
Alle Änderungen nur in isolierten Kopien (eigene Ports/Displays/Wine-Präfixe).

## 1. Kritischster aktueller Fehler

Der isolierte Hetzner-Wine-A/B (PR #40) ist **doppelt konfundiert**: (a) geteilter
45-%-Kern-Cap, ~80 % der Perioden gedrosselt (`nr_throttled=2528/3146`) – 35,56 %
Client + ~10 % Server = Cap-Sättigung, das Messverfahren kann Nachfrage nicht
trennen; (b) in **beiden** Varianten fehlt jeder BotDriver-Nachweis – die
wahrscheinlichste Einzelursache ist, dass die A/B-Skripte `bot_bEnabled=1` (und
damit wahrscheinlich auch `bot_bNullRender=1`) nie zur Anwendung brachten; beide
Clients renderten also identisch. Der A/B beweist weder „keine Ersparnis" noch
„BotDriver defekt".

## 2. Wahrscheinlichste technische Ursache

H1 (hoch): Skriptanwendung unbestätigt. Begründung im Review §2.3: Join/CRC läuft
über `+connect`/`+quickjoin` unabhängig vom Skript; die Baseline mit
`HetznerFleet.ini` zeigte Attach-Zeilen unter identischem Wine-Stack; der Ledger
gibt selbst an, Flags nie runtime-verifiziert zu haben. H2 (gleichzeitig wahr):
Messdesign (Cap/18 s). Schwache Hypothesen: „Skript zu früh" (SE1.10-Init-Reihenfolge:
`InitializeGame()` → BotDriver_Init → **danach** `+script`-Include) und
„Log-Pufferung" (CPutString flushet pro Zeile, 1.10-Referenz).

## 3. Erforderliche Diagnoseinstrumentierung

Patch anwenden: `poc/patch/0008-gamemp-botdriver-diagnostics.patch` (nur
`poc/release/gamemp/BotDriver.cpp`, opt-in, Default aus).
- `[BotDiag] init: bot symbols declared` – beweist, dass genau dieser DLL-Kandidat geladen ist und Init lief.
- `[BotDiag] call=N gameon=E enabled=B locals=M1M2M3M4 fpsActive=.. fpsInactive=.. snd=..` – Herzschlag alle `bot_iDiagEvery` Timer-Calls (Default 100 = 5 s), **vor** jeder Sperre/jedem Gate; beweist WinMM-Timer-Leben (auch im Menü) und die effektiven Konfigurationswerte.
- `CShell::GetINDEX` gibt bei fehlendem Symbol −666 zurück (Release) – nie fatal.
Neue Shell-Symbole: `bot_bDiag`, `bot_iDiagEvery`. Zusätzlich extern greppen:
`Command line script:` (EXE-Log) und Shell-Fehlerzeilen direkt danach.

## 4. Betroffene Quellcodefunktionen

`BotDriver.cpp`: `BotDriver_Init()`, `BotDriver_HandleTimer()` (Instrumentierung);
Referenzpfade (unverändert): `CGame::GameHandleTimer` (Game.cpp:752-754),
`CGameTimerHandler::HandleTimer` (Game.cpp:746-750), `CGame::GameMainLoop`
(Game.cpp:2632 ff.), `CGame::GameRedrawView` (Guard in PR #40), Engine:
`CTimer_TimerFunc` (tm_csHooks → Handler, SE1.10 Timer.cpp:74-121),
`CNetworkLibrary::TimerLoop`/`MainLoop`, `CPlayerSource::SetAction`.

## 5. Konkreter Patch

1. `git apply poc/patch/0008-gamemp-botdriver-diagnostics.patch` → MSBuild
   Release_TSE107 x86 (Windows-Runner-Toolchain v143, README-Pins) → neuer
   Kandidaten-DLL mit eigener SHA256; **nie** die qualifizierte `61DC…` ersetzen.
2. Optional danach: `poc/patch/0009-gamemp-bot-ai-throttle.patch` (KI-Drossel,
   Defaults = aktuelles Verhalten; Betriebsprofil z. B. `bot_iScanInterval=4;
   bot_fTargetRange=60; bot_iMaxLosRays=4; bot_iObstacleInterval=2;`).
3. A/B-Client-Skript (isoliert) minimal:
   `bot_bEnabled=1; bot_bDiag=1; bot_bAutoCombat=1; bot_bObstacleAvoidance=1;
   bot_bNullRender=0|1; sam_iMaxFPSActive=20; sam_iMaxFPSInactive=20;
   sam_bPauseOnMinimize=0; snd_iFormat=0; bot_iLogEvery=40;`
   (bei 0009 zusätzlich das Drosselprofil).

## 6. Erwartetes Testverhalten

Nach Start (auch noch im Menü): `[BotDiag] init` gefolgt von Herzschlägen ≈5 s.
Nach Join: `gameon=1`, `locals=1111`, Attach-Zeilen, alle `bot_iLogEvery`-Ticks
Position-/Combat-Zeilen; Serverlog zeigt Bewegung/Frags der 4 Spieler. Bleibt ein
Marker aus → Entscheidungsbaum im Review §2.2 (Zustände 1–5) ergibt die Ursache,
**ohne** weitere CPU-Messung.

## 7. Regressionsrisiken

- Neuer DLL-Kandidat = neuer ungeprüfter Kandidat: volle Gate-Kette (Vanilla-Observer-Join, 60-min-Sync beidseitige Logs, sauberes `CloseMainWindow`-Ende, SHA256-Protokoll).
- `snd_iFormat=0` nur auf Bot-Clients; niemals auf menschlichen Instanzen.
- Minimiertes Fenster (späterer Schritt): `sam_bPauseOnMinimize` betrifft MP laut 1.10-Quelle nicht, trotzdem setzen; prüfen, dass unter Wine **ohne** WM `IsIconic` greift (CPU-Delta im Heartbeat sichtbar; sonst Foreign-Methodik verwerfen).
- Keine geteilten Cgroup-Caps mehr; `ser_iKickOnSyncBad` niemals anfassen.
- 0009 ändert KI-Verhalten nur bei gesetztem Profil; Defaults bitidentisch halten und Phase-1-Combat-Abnahme nach Aktivierung wiederholen.

## 8. Messbare Erfolgskriterien

- Diagnose: alle fünf Marker (init, Herzschlag, enabled=1, locals=1111, Ticks/Position) in ≥2 aufeinanderfolgenden Läufen.
- Gültiges A/B (≥120 s nach 60 s Warmup, `pidstat -u -h 1`, **inkl.** wineserver/Xvfb ausgewiesen, `nr_throttled` ~0): Null-Render/ikonisch vs. Render zeigen einen **reproduzierbaren** Median-Unterschied pro PID; Zielhypothese ≥30 % Client-CPU-Ersparnis [wird erst hierdurch belegt oder verworfen].
- Sync: 60 min ohne SYNCBAD-/Disconnect-Neuheit; UDP-Population konstant; sauberes Prozessende ohne Geist-Spieler.
- Erst danach: 4-Bot-Instanz auf 2 vCPU mit Ziel <50 % Gesamtauslastung [Hypothese].

## 9. Nächster Entwicklungsschritt

1. 0008 bauen + Marker-Lauf (30 min).
2. gültiges A/B nach §9 der Review (2 h).
3. ikonisch-Experiment (§3.2 Review: `bot_bMinimizeWindow`-Spec, 3 Zeilen, separater Kandidat) – erst wenn 1–2 grün.
4. parallel, separater Worktree: DedicatedServer.exe `+connect`-Client-Test (30 min, Review §4.1).
5. Ergebnis zurück in `docs/reports/…` mit denselben Evidenzstandards wie bisher; PR #40 bleibt Draft, bis 1–3 belegt sind.
