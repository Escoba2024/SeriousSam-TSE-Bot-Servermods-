# Unabhängiges technisches Review – CPU-Optimierung / Null-Renderer / BotDriver (2026-10-21)

Autor: Unabhängiger Senior C++-/RE-/Performance-Review-Agent (Arena-Branch
`arena/e39db2a9-serioussam-tse-bot-servermods`). Dieses Dokument ist **Analyse und
Spezifikation** – keine Freigabe, kein Laufzeitnachweis, keine Änderung produktiver
Prozesse.

---

## 0. Prüfkontext und Quellenlage

**In dieser Sitzung tatsächlich geprüft (belegt):**

| Quelle | Umfang |
|---|---|
| `poc/release/gamemp/` (13 Dateien) | Vollständig gelesen: BotDriver.cpp/h, Game.cpp, botcore*.h, bot_combat.h, LoadingHook.cpp-Anwesenheit |
| Exakter Vanilla-Vergleich | `DreamyCecil/SE1-ModSDK` @ `aa7869c2c2c4db0562281814d0ac3784e6b9d6f0` (exakt der im README gepinnte Commit) geklont; `Sources/Game/Game.cpp` vs. Projekt-`Game.cpp`: **16 Zeilen Differenz** (ohne CR) – die Integration ist minimalinvasiv nachvollziehbar |
| SE-1.10-Referenzengine | `Croteam-official/Serious-Engine` geklont; Timer-/Network-/Console-/SeriousSam-Hauptloop am Originalcode verifiziert (Datei:Zeile unten) |
| PR #40 | Kompletter Diff via `gh pr diff 40` geprüft (Null-Renderer-Guard, Hetzner-A/B-Bericht, Ledger, Profil, statischer Test) |
| Berichte | 2026-10-21 Acht-Bot-Baseline, 2026-10-17 Lowrender-Vanilla-Control, AGENTS.md, Research-Assessments (Gemini/Perplexity), Coordination-Status |

**Nicht verfügbar (fehlender Prüfkontext, wird nicht als gelesen behandelt):** die im
Auftrag genannten fünf Deep-Research-Dokumente („Alpha-Gaming Bot-CPU –
Forschungsbericht…", `lmarena.txt`, `GRok.txt`, „Serious Sam Bot Optimization.md",
„Serious Sam TSE 1.07 – Bot-CPU-Optimierung Architektur-Review.md") sowie die
ChatGPT-Master-Roadmap und die privaten A/B-Rohlogs (`ab_runner.py`,
`result-hetzner.json`, HetznerFleet.ini der A/B-Läufe). Alle Aussagen dazu bleiben
rekonstruiert und müssen gegen die Originale geprüft werden.

**Beweisklassen (durchgehend verwendet):**
- **[Fakt]** direkt aus Repository-/SDK-/SE1.10-Quelle oder PR-Diff belegt.
- **[Referenz-Annahme]** aus SE-1.10-Quelle belegt, für Retail 1.07 **nicht** binär verifiziert (AGENTS.md: 1.10 ≠ 1.07).
- **[Hypothese]** plausibel, unbewiesen; nur durch Messung zu entscheiden.
- **[Riskant]** Architekturänderung mit Sync-/ABI-Risiko.
- **[Ausführbar]** konkret mit vorhandenen Mitteln umsetzbar.

---

## 1. Verifiziertes Faktengerüst: Wer läuft wo, wie oft?

### 1.1 Threads und Takte eines Bot-Clients [Fakt/Referenz-Annahme]

SE1 verwendet **keinen** zentralen Game-Thread; drei aktive Einheiten pro Client:

1. **WinMM-Timer-Thread (≈20 Hz).** `CTimer` startet `timeSetEvent(50 ms, 0,
   CTimer_TimerFunc, 0, TIME_PERIODIC)` (SE1.10 `Engine/Base/Timer.cpp:237-267`).
   Der Callback nimmt `tm_csHooks` und ruft **alle** Handler
   (`Timer.cpp:74-121`). `TickQuantum = 1/20 s` (`Timer.cpp:54`).
   Registriert sind (in Add-Reihenfolge):
   a) `CNetworkTimerHandler::HandleTimer` → `CTSTREAM_BEGIN` → `_pNetwork->TimerLoop()`
      (SE1.10 `Network/Network.cpp:659-668`): Client sendet `SendActionsToServer()`
      (MSG_ACTION, `WriteActionPacket` pro lokalem Spieler) + `_cmiComm.Client_Update()`;
      Server zusätzlich `ServerLoop()`.
   b) `CGameTimerHandler::HandleTimer` → `_pGame->GameHandleTimer()` (SDK
      `Game.cpp:746-750`): **Hier sitzt `BotDriver_HandleTimer(this)`** (Projekt
      `Game.cpp:754`) – bei `bot_bEnabled=1` erzeugt BotDriver pro lokalem Spieler
      eine `CPlayerAction` und ruft `SetAction()`; der Vanilla-Eingabepfad wird
      übersprungen. Reihenfolge pro Tick: **erst Senden der Aktionen des Vor-Ticks,
      dann Erzeugen neuer Aktionen.**
2. **Hauptthread (FPS-Loop).** `while(_bRunning){ PeekMessage-Pump; DoGame();
   LimitFrameRate(); }` (SE1.10 `SeriousSam.cpp:855-1190`). `DoGame()` ruft
   `_pGame->GameMainLoop()` (→ `_pNetwork->MainLoop()` → `ga_csNetwork` →
   `SessionStateLoop` + `ProcessGameStream` = **Weltzustands-Update des Clients**)
   und danach **jeden Frame** den Renderblock:
   `if(!IsIconic(_hwndMain) && pdp->Lock()) { GameRedrawView(...); ComputerRender(pdp);
   ... ConsoleRender(pdp); ... SwapBuffers(); }` (`SeriousSam.cpp:707-755`).
   `LimitFrameRate()` drosselt auf `sam_iMaxFPSActive`; **bei minimiertem Fenster
   (`IsIconic`) auf `sam_iMaxFPSInactive`** (`SeriousSam.cpp:244-262`).
3. **Wine/Nebenläufiges:** wineserver, Xvfb (separater Prozess!), Mesa-Threads,
   Sound-Mixer (falls aktiv) – kosten CPU **außerhalb** der SeriousSam.exe-PID.

Konsequenzen:
- `GameMainLoop`/Welt-Sync läuft **frametaktgetrieben im Hauptthread**, nicht im Timer.
  `sam_iMaxFPSInactive` bestimmt damit auch die Prozessfrequenz von `ProcessGameStream`
  und damit die Aktualität der lokalen Welt (die BotDriver für Zielung liest).
- Der WinMM-Timer hält `tm_csHooks` während aller Handler; das Projekt-`GameRedrawView`
  belegt `tm_csHooks` **framespannend** (Projekt `Game.cpp:2091-2098`). Folie [Fakt]:
  im Rendermodus wird der 20-Hz-Takt framesynchronisiert (Jitter), kein Deadlock
  (Lock-Ordnung überall `tm_csHooks` → `ga_csNetwork`). Der PR-40-Early-Return liegt
  **vor** diesem Lock und umgeht es im Null-Render-Modus [Fakt].
- `CPlayerSource::SetAction` ist Single-Slot „latest wins" mit `pa_llCreated`-Stempel
  (SE1.10 `PlayerSource.cpp`); Aktionen werden erst im nächsten `TimerLoop` gesendet.

### 1.2 Skript-/Init-Reihenfolge [Referenz-Annahme, 1.10; 1.07 zu verifizieren]

`Init()`: `ParseCommandLine` (speichert nur `cmd_strScript`) → `SE_InitEngine` →
`InitializeGame()` (= `_pGame->Initialize` → `InitInternal` → **`BotDriver_Init`
deklariert alle bot_*-Symbole**) → **erst danach** `include "<cmd_strScript>"`
(SE1.10 `SeriousSam.cpp:395-505`). Ein `+script` kann Bot-Variablen also setzen;
ein „Skript zu früh" ist als Erklärung für fehlende `bot_bEnabled` **schwach**.
Das EXE-Log enthält zudem die Zeile `Command line script: '<pfad>'` und Shell-Fehler
pro Zeile – ein einfacher externer Prüfpunkt.

### 1.3 Konsolen-/Log-Verhalten [Referenz-Annahme]

`CPutString` → `CConsole::PutString`: `fprintf(con_fLog,…)` **plus `fflush` pro Aufruf**
(SE1.10 `Console.cpp:208-231`). Logzeilen erscheinen daher zeitnah; **fehlende
BotDriver-Zeilen belegen sehr wahrscheinlich fehlende Aufrufe**, nicht Pufferung.
`BotLog` formatiert lokal und nutzt den synchronisierten Konsolenschreiber [Fakt,
BotDriver.cpp:22-31].

---

## 2. P0 – Warum fehlt der BotDriver-Tick-Nachweis im isolierten A/B?

### 2.1 Befundlage [Fakt, PR #40]

- Beide Varianten (Render an / `bot_bNullRender=1`): **exakt 35,56 %** Client-CPU in
  18 s; CRC OK; 4 Spieler gejoint; **null** BotDriver-Attach-/Tick-Zeilen.
- Cgroup: 45 % **eines** Kerns **geteilt** zwischen DedicatedServer und Client;
  `nr_throttled=2528` von `nr_periods=3146` (~80 % der Perioden gedrosselt).
- 35,56 % + ~10 % Server ≈ 45 % Cap: **beide Varianten forderten mehr CPU, als
  verfügbar war.** Das Experiment misst die Deckelung, nicht die Nachfrage.
- Beide Skripte setzten laut Ledger `sam_iMaxFPSActive=20` usw.; Ledger räumt ein:
  „flags not independently verified at runtime".

### 2.2 Entscheidungsbaum (Fünf-Zustands-Diagnose)

Prüfwerkzeuge: Klientenlog (Client! nicht Serverlog), Markierungen
`[BotDiag]`/`[BotDriver]` (Patch 0008), EXE-Logzeilen `Command line script:` und
Shell-Fehler, `bot_bDiag=1` im Skript.

```
START: Klientenlog nach Join (>=60 s, NICHT gedrosselt) lesen
│
├─ (1) "[BotDiag] init: bot symbols declared" fehlt?
│      → Falsche/alte GameMP.dll geladen (Kopie/Pfad-Priorität) oder InitInternal
│        lief nie. → DLL-SHA256 im Runtime-Bin-Verzeichnis prüfen; Engine-Log auf
│        Game-Init-Fehler prüfen. [Zustand 2f: falsche DLL]
│
├─ (2) init vorhanden, aber KEIN "[BotDiag] call=…" Herzschlag (auch im Menü nicht)?
│      → WinMM-Timer tot oder GameHandleTimer wird nie gerufen.
│      → Engine-Startlog: „Cannot initialize multimedia timer" / 3-Versuch-Check;
│        cgroup-Throttling des WinMM-Threads; Wine-mm-Timer-Besonderheit.
│        [Zustand 1: Timer wird nicht aufgerufen]
│
├─ (3) Herzschlag da, `enabled=0`?
│      → Skript nicht angewendet (nicht ausgeführt/inkludiert oder falsche Datei)
│        ODER bot_bEnabled-Zuweisung fehlt. EXE-Log auf „Command line script:"
│        und Shell-Fehler prüfen. [Zustand 2: Timer ok, BotDriver aus]
│
├─ (4) Herzschlag da, `enabled=1`, `gameon=1`, aber `locals=0000`?
│      → Join erzeugte keine lokalen Spielerquellen in DIESEM Prozess
│        (Split-Screen-Konfig/das Join-Skript des A/B-Laufs!). Baseline-Fleet
│        joinete 4 Spieler pro Client via Skript; A/B-Skripte neu. – Ggf. sind die
│        4 Server-Spieler anders zustande gekommen (mehrere Joins, andere Clients).
│        [Zustand 3: BotDriver läuft, findet keine Quellen]
│
├─ (5) Herzschlag da, locals>0, aber keine „is now bot-driven"-Zeile?
│      → gm_bGameOn-Flattern oder Tick-Zähler-Problem → [BotDiag] gameon-Verlauf
│        auswerten. [Zustand 3b]
│
├─ (6) „is now bot-driven" da, aber keine Tick/Position-Zeilen alle bot_iLogEvery?
│      → SetAction-Aktionen ankommen nicht: next hop Serverlog (Spielerbewegung,
│        MSG_ACTION-Frequenz), Sync-Warnungen. [Zustand 4: Aktionen verloren]
│
└─ (7) Alles vorhanden?
       → Messung/Inspektion war falsch (falsche Logdatei, zu kurzes Fenster,
         gedrosselt). [Zustand 5: funktionierte, Nachweis fehlte]
```

### 2.3 Hypothesenranking (mit Begründung)

| # | Hypothese | Plausibilität | Begründung |
|---|---|---|---|
| H1 | **A/B-Skripte setzten die Bot-Variablen nicht** (Script lief nicht / fehlte `bot_bEnabled=1`); `bot_bNullRender` griff damit ebenfalls in Variante B nicht → **beide Varianten renderten normal** | **Hoch** | Erklärte mit EINER Ursache beide Anomalien (identische 35,56 % **und** null Bot-Zeilen). Join/CRC funktioniert unabhängig davon über `+connect`/`+quickjoin`. Ledger bestätigt: Flags nie runtime-verifiziert. Der 8-Bot-Baselinelauf mit `HetznerFleet.ini` zeigte Attach-Zeilen – Mechanismus funktioniert unter Wine grundsätzlich. |
| H2 | Messmethode invalide (geteilter 45-%-Cap, ~80 % gedrosselte Perioden, 18 s) | **Hoch** (für die CPU-Seite) | 35,56+~10 ≈ Cap-Sättigung; identische Werte sind die Kap-Artefakt-Erklärung, falls H1 nicht greift. Auch bei H1 gleichzeitig wahr. |
| H3 | WinMM-Timer durch Throttling lahmgelegt | Niedrig | Throttling verlangsamt Ticks, eliminiert sie aber nicht; in 18 s blieben immer noch Hunderte Calls; Herzschlag würde das zeigen. |
| H4 | Log-Pufferung/inspezierte falsche Datei | Niedrig–Mittel | `CPutString` flushed pro Zeile (1.10-Referenz); Baseline zeigte Attach-Zeilen im Klientenlog unter identischem Wine-Stack. Restrisiko: falsche Datei im Kopier-Runtime inspiziert. |
| H5 | Falsche GameMP.dll in der Kopie geladen (z. B. originale 61DC statt 4F74) | Niedrig–Mittel | Erklärt fehlenden Null-Render-Effekt, aber **nicht** fehlende BotDriver-Zeilen (61DC hat BotDriver!). Nur gemeinsam mit H1 vollständig. |

**Schlussfolgerung P0:** Der A/B-Vergleich beweist weder „Null-Renderer bringt nichts"
noch „BotDriver defekt". Er ist wegen (H1+H2) **doppelt konfundiert**. Vor jedem erneuten
CPU-Vergleich: Patch 0008 + nicht gedrosselte, per-PID gemessene Läufe ≥60 s
(s. §9 Benchmark-Strategie).

### 2.4 Sekundärbefund (Rendermodus)

Das framespannende `tm_csHooks`-Lock des Projekts in `GameRedrawView` (Schutz des
Ray-Scratch-Flags gegen Renderer-Sektorflags) verlängert die Sperrzeit des
Timer-Kontexts auf die Framedauer. Bei llvmpipe-Frametimes im Zweistellen-
Millisekundenbereich erzeugt das Tick-Jitter für BotDriver/Netzwerk. Der PR-40-Guard
liegt davor und umgeht es im Null-Render-Modus – das ist ein **zusätzlicher,
bisher undokumentierter Stabilitätsvorteil** des Null-Renderers. Kein Deadlock-Risiko
erkennbar (Lock-Ordnung konsistent hooks→network).

---

## 3. P1 – Rendering eliminieren (Stufen A/B/C)

### 3.1 Was läuft trotz PR-40-Early-Return noch? [Fakt/Referenz-Annahme]

Pro Frame zusätzlich zu `GameRedrawView`-Skip:
- `ComputerRender(pdp)` + `ConsoleRender(pdp)` (Früh-Ausstieg bei Computer off / Konsole zu – Aufwand klein, aber DrawPort-Locks bleiben);
- **`pvpViewPort->SwapBuffers()`** – auf llvmpipe ein CPU-Blit/GL-Flush pro Frame;
- Nachrichtenpumpe, `GameMainLoop` (Welt-Sync), `LimitFrameRate`-Sleep;
- GL-Kontext/Xvfb bleibt komplett initialisiert.

### 3.2 Der übersehene Vanilla-Hebel: minimiertes Fenster (STUFE A+)

**[Referenz-Annahme, SE1.10:** `DoGame` überspringt bei `IsIconic(_hwndMain)` den
**gesamten** Renderblock inkl. SwapBuffers (`SeriousSam.cpp:707`), und
`LimitFrameRate` fällt auf `sam_iMaxFPSInactive` (`:251`)**]**. Multiplayer-Clients
pausieren beim Minimieren **nicht**: `sam_bPauseOnMinimize` wirkt nur in
`GM_SINGLE_PLAYER` (`SeriousSam.cpp:882`).

Konfiguration (ohne eine Zeile Engine-Code):
```
sam_iMaxFPSActive=20; sam_iMaxFPSInactive=20;   // MainLoop-Rate halten
sam_bPauseOnMinimize=0;                          // defensiv (MP ohnehin unberührt)
snd_iFormat=0;                                   // kein Audiokontext/Mixer
```
+ Fenster minimieren. Da unter Xvfb **ohne Window-Manager** ICCCM-Iconify von
xdotool unzuverlässig ist, ist der robuste Weg ein Mini-Feature **in BotDriver**
(opt-in, 3 Zeilen, imselben DLL-Kandidaten wie 0008):
```cpp
// im ersten BotDriver-Tick (oder BotDriver_Init), nur wenn bot_bMinimizeWindow=1:
HWND hwnd = FindWindowA("SeriousSam", NULL);      // Fensterklasse = APPLICATION_NAME
if (hwnd != NULL) ShowWindow(hwnd, SW_MINIMIZE);  // Wine setzt IsIconic intern
```
**Verifizierungsbedarf [Hypothese]:** (a) setzt Wine ohne WM `IsIconic()` korrekt
(erwartet ja – Win32-interner Zustand), (b) verhält sich Retail-1.07-EXE wie 1.10
(IsIconic-Guards). Beides ist mit einem 5-Minuten-Lauf + `bot_bDiag`-Heartbeat
(CPU-Delta) und/oder Fensterlistung prüfbar. Wenn ikonisch funktioniert, macht dies
den GameMP-Null-Renderer zur zweiten Verteidigungslinie und entfernt zusätzlich
SwapBuffers – **der größte Erwartungswert pro Risiko**.

### 3.3 STUFE B (Engine-Loop-Reduktion)

Mit ikonischem Fenster + `sam_iMaxFPSInactive=20` verbleiben: Nachrichtenpumpe,
`GameMainLoop`/`ProcessGameStream` (erforderlich!), 20-Hz-Timer (erforderlich),
Wine-Grundlast. `sam_iMaxFPSInactive<10` senkt die Welt-Aktualität (Bot-Zielung
nutzt lokale Welt!) – **nicht** unter 10 gehen [Hypothese, Test über
BotCombat-Positionsgüte]. Eine Absenkung des `tm_csHooks`-Locks auf die reine
Prescan-Phase (statt framespannend) wäre im Rendermodus möglich, berührt aber das
Scratch-Flag-Argument des Projekts → **nicht** anfassen, solange Null-Render/
ikonisch verfügbar ist.

### 3.4 STUFE C (echtes Headless) → §4 (P2).

### 3.5 Beantwortung der Detailfragen (Auftrag §6)

- **Läuft nach Early-Return noch Renderarbeit?** Ja: ComputerRender/ConsoleRender/
  SwapBuffers/2D-Block im EXE + GL-Grundbetrieb (§3.1).
- **Kann die Engine 20-Hz-Simulation ohne Renderframes?** Ja – Simulation ist
  renderunabhängig (Timer + `MainLoop`); der DedicatedServer beweist das serverseitig
  mit GAT_NONE [Referenz-Annahme].
- **Netzwerk-erforderliche Loop-Teile:** WinMM-Tick (`TimerLoop` Aktionen senden),
  `GameMainLoop`→`MainLoop` (Stream anwenden), Nachrichtenpumpe (Window-Subsystem
  des Retail-EXE). Entbehrlich: gesamter visueller Block + Sound + Prescan.
- **GL-Init vermeidbar?** Mit Retail-EXE nein (Viewport-Kontext beim Start). Ohne GL
  nur via BotHost (P2) oder DedicatedServer.exe-als-Client-Experiment (§4 Option B).

---

## 4. P2 – Echter Headless-BotHost (Entwurf)

### 4.1 Option B zuerst testen: DedicatedServer.exe als Client [Ausführbar, 30 min]

`DedicatedServer.exe` ist dieselbe Engine mit Dedicated-Flag (kein GL-Viewport,
GAT_NONE, `_bDedicatedServer=TRUE`). Unbekannt ist, ob der **Client-Rolle-Pfad**
(`+connect` als Join, `SendActionsToServer`, Prediction) im Dedicated-EXE erreichbar
ist. Experiment: isolierte Kopie, `DedicatedServer.exe +connect <ip:port> +quickjoin
+script Scripts\BotStartup.ini` (bot_bEnabled=1), ein Bot. **Wenn** er joint und
`[BotDriver]`-Zeilen + serverseitige Bewegung zeigen: fertiger near-headless
4-Bot-Client mit vorhandenen Binaries (GameMP 61DC unverändert!). Wenn nicht:
kein weiterer Aufwand in Option B. Risiken: Dedicated-EXE könnte Client-Pfaden
fehlerhaft initialisieren (Session-Props, `sso_ctLocalPlayers`) → Sync-Fehler;
streng isoliert testen, SYNCBAD-Kriterien anlegen.

### 4.2 Option A: eigener BotHost.exe (Design)

Prinzip [Fakt-Bausteine]: Die gesamte Simulation liegt in Engine.dll/EntitiesMP/
GameMP.dll (retail). Der EXE ist Verkleidung: Init-Reihenfolge, Shell-Symbole,
Nachrichtenpumpe, Viewport. Ein BotHost ohne Viewport erzeugt **nie** einen
GL-Kontext.

Minimaler PoC (Win32, x86, MSVC-ABI, linkt SDK-Importlibs von Game/Engine):
1. `SE_InitEngine("SeriousSam")` (erzeugt `_pTimer` inkl. WinMM-Tick, `_pNetwork`,
   `_pShell`, Konsole+Log; **keinen** Viewport, **keinen** Gfx-Kontext).
2. EXE-seitige `sam_*`-Symboldeklarationen nach SE1.10-`SeriousSam.cpp:440-460`
   übernehmen (nur die von Game.dll gelesenen).
3. `_pGame->Init(...)` (Game.dll registriert seinen Timer-Handler selbst →
   `GameHandleTimer`+BotDriver laufen automatisch).
4. Skript inkludieren (`bot_bEnabled=1`, `+connect`-Adresse), `JoinGame(CNetworkSession(addr))`.
5. Loop: `PumpMessages(); _pGame->GameMainLoop(); Sleep(10..50);` (≈20 Hz; exakte
   Rate wie §3.3 wählen). Kein `_pSound->SetFormat`, kein `_pGfx`-Viewport.

Offene Risiken [Riskant]: undokumentierte EXE-seitige Erwartungen von Game.dll 1.07
(Reihenfolge/fehlerhafte Symbolzugriffe → FatalError); Importlib-ABI (MSVC-mangled
C++-Exports, §7); CRC/Join-Verhalten identisch zu Client (erwartet, da Engine-Pfad
identisch – aber nur Test zählt); Wartungszweig‐Drift gegenüber Retail-EXE-Verhalten
(z. B. Fenster-/Eingabespezifika im Vanilla-Pfad, die BotDriver umgeht).

**PoC-Gate-Kette:** 1 Host/1 Bot/1 Dedicated → Join+CRC+20-Hz-Actions 10 min →
4 Bots/Host 60 min SYNCBAD-frei → CPU-Vergleich ggü. ikonischem Vanilla-Client.
**Entscheidungsempfehlung:** Option-B-Experiment sofort; BotHost erst danach und nur,
wenn Option B scheitert **und** der ikonische Client nach §3 nicht unter ~10–15 %
Kern/Client kommt (sonst lohnt der Aufwand nicht).

---

## 5. P3 – Bot-KI-Kosten (Code-Level-Befunde)

Kostenquellen pro Tick und Bot [Fakt, BotDriver.cpp]:
- AutoCombat-Scan: für Index 0..15 `GetPlayerEntity`+`BotCombatIsLocal` (4-Loop)+Snapshot
  + **`BotCombatVisible` = je ein `CCastRay`** pro gültigem Kandidaten. Worst case
  15 Rays/Bot/Tick = bis ~1200 Rays/s pro 4-Bot-Client.
- Obstacle-Avoidance: **3 Rays/Tick** (front/left/right), wenn lebendig+bewegend → +240 Rays/s.
- Alles innerhalb **einer** `ga_csNetwork`-Sperre über den gesamten 4-Bot-Tick
  inkl. `BotLog`-Aufrufe (Konsolenlock verschachtelt) → verlängert die Sperrdauer
  ggü. `ProcessGameStream` (Hauptthread) → Jitter.
- `SelectTarget` wählt den **nächsten** sichtbaren Kandidaten (bot_combat.h) →
  nearest-first-Verifikation ist verhaltensäquivalent zur Vollprüfung bei
  ausreichendem Ray-Budget.

**Patch 0009 (liegt bei, Defaults = aktuelles Verhalten):**
`bot_iScanInterval` (Vollscan nur alle N Ticks; dazwischen nur Cached-Target-Verify
mit 1 Ray, 20-Hz-Aim bleibt), `bot_fTargetRange` (Distanzfilter), `bot_iMaxLosRays`
(Ray-Budget, nearest-first nach Distanzsortierung), `bot_iObstacleInterval`
(Seiten-Rays gedrosselt). Empfohlene Betriebseinstellung (Hypothese, zu messen):
`4 / 60 / 4 / 2` → Rays von bis zu ~1440/s auf ~50–120/s je Client (−90 %) bei
praktisch gleicher Zielqualität (nächster sichtbarer bleibt nächster).

Weitere (später, als Spec): `BotLog` aus der `ga_csNetwork`-Sperre herausziehen
(Sammelpuffer, Flush nach Unlock); `BotCombatIsLocal`-Ergebnis pro Tick cachen
(Mikro). 20-Hz-`SetAction` bleibt in jedem Fall unberührt – nur Denk-/Suchfrequenz
sinkt. Sync-Risiko: keins bekannts (rein clientseitige Entscheidungen; gleiche
`SetAction`-Semantik), Verhalten ändert sich leicht (KI-Qualität) → Phase-1-
Combat-Abnahme wiederholen.

---

## 6. P4 – Analytisches CPU-Kostenmodell (Hypothesen!)

**Belegte Messpunkte:** Client 70–87 % Kern (4 Bots, llvmpipe, Baseline 21.10.);
Dedicated 8–16 %; native Windows-Smoke (PR40, 12 s): Render 4,4 % vs. Null-Render
1,7 % (−61 %, 1 Bot, **nicht** Wine). Hetzner-A/B: invalide (§2).

**Modell (je 4-Bot-Client, 2-vCPU-Hetzner, Hypothesenbreiten aus den Messpunkten):**

| Anteil | Bereich | Bemerkung |
|---|---|---|
| Wine/EXE/Timer/Wine-Grundlast | 5–15 % | mm-Timer-Thread, Pumpe, wineserver-Proxy |
| Welt-Sync/ProcessGameStream | 10–25 % | mapabhängig, 20 Hz |
| Rendering (llvmpipe 320x240) | 30–60 % | Baseline deutet auf Dominanz; native Smoke −61 % als untere Grenze |
| BotDriver-KI (Rays, Scan, Log) | 5–20 % | §5, stark map-/kandidatenabhängig |
| DedicatedServer (pro Instanz) | 8–16 % | belegt; wächst mit Teilnehmern/Aktionen |

**Szenarien (explizit Hypothesen, kein Ersatz für Messung):** Mit ikonischem
Null-Render + KI-Drossel (§3+§5) plausibel 25–45 % Kern je 4-Bot-Client →
8 Bots ≈ 0,5–0,9 Kern + Server 0,1–0,2 → **8 Bots auf 2 vCPU stabil möglich**,
12–16 Bots eher 4 vCPU. Ohne Rendering-Eliminierung ist 2 vCPU bei 8 Bots
(belegte 85–92 % Auslastung) bereits am Limit. **Kapazitätszahl final nur aus
Messung nach §9.**

---

## 7. Hetzner-only Build-Architektur

| Weg | Bewertung |
|---|---|
| **MinGW-w64** | **Verwerfen.** Retail-Engine-DLLs exportieren MSVC-mangl*te* C++-Symbole (Klassen, `_pGame`-Interface); Itanium-Mangling/ABI von GCC ist inkompatibel. Behauptung „buildet einfach" wäre unbelegt. |
| **Clang-cl Cross (Linux→i686-pc-windows-msvc, lld-link)** | Realistisch [Hypothese, zu qualifizieren]: MSVC-ABI/Mangling korrekt abbildbar; Windows-SDK-Header/Libs nötig; Importlibs für Retail-DLLs aus Exports generierbar (gendef/llvm-dlltool). Qualifikation nur über volle Runtime-Gates (Join/CRC/60 min). |
| **MSVC BuildTools unter Wine / Wine+MSBuild** | Nicht als Primärweg: Installer/Paketgröße/Abstürze unter Wine historisch brüchig; Wartungsrisiko. |
| **Empfehlung: GitHub-gehostete Windows-Runner** | „Hetzner-only" ist das falsche Ziel – das **Ziel** ist „Shadow-unabhängig". `windows-latest` + VS2022/v143 baut genau die bereits qualifizierte Toolchain (README-Pins); Artefakt (DLL, SHA256) wird nach Hetzner transferiert und dort nur **getestet**. Kein ABI-Risiko, kein neuer Kandidaten-Typ. Clang-cl-cross bleibt Fallback. |

---

## 8. Unabhängiges Review – Antworten auf die 12 Fragen (kurz)

1. **GameRedrawView bester Ansatzpunkt?** Für GameMP-only: ja, aber unvollständig –
   er verlässt nicht den Renderblock des EXE (SwapBuffers!). Besser: IsIconic-Pfad
   (§3.2) **plus** Guard als Rückfallebene.
2. **CPU vor GameRedrawView?** Ja: `GameMainLoop` läuft davor im selben Frame;
   Timer-Thread unabhängig; Prescan-Input innerhalb der Funktion entfällt durch den Guard.
3. **Äußerer Loop weiter teuer?** Ja – SwapBuffers + 2D + Pumpe bei bis zu
   `sam_iMaxFPSActive`; ohne ikonisch kein großer Gewinn.
4. **GL-Init vermeidbar?** Mit Retail-EXE nein; nur BotHost/Dedicated-Experiment (§4).
5. **GAT_NONE mit Client-Modus kompatibel?** Simulationstechnisch ja (Dedicated
   beweist GAT_NONE-Sessions), aber der Retail-Client-EXE erzeugt trotzdem einen
   GL-Kontext; Kompatibilität des Join-Pfades unter Dedicated-EXE = §4.1-Test.
6. **BotHost realistisch?** Ja, aber mittelgroßes Projekt mit ABI-/Init-Risiken;
   erst nach Option B und §3-Messung entscheiden (§4.2).
7. **Einfacherer Weg im Retail-Client?** Ja: **minimiertes Fenster** + FPS/Sound-
   Skript (§3.2) – null Binary-Änderung wenn extern iconifizierbar; sonst 3 Zeilen
   in BotDriver.
8. **Größte Wirkung / geringstes Risiko:** (1) A/B-Validität herstellen (0008,
   Messfix) – null Risiko; (2) ikonisch+snd_iFormat=0; (3) Null-Render-Guard (PR40);
   (4) KI-Drossel 0009 (Defaults aus); (5) Option B Dedicated-as-Client; (6) BotHost.
9. **Lockstep-Risiken?** TSE-MP ist server-autoritativ mit Action-Stream + CRC-Sync
   (SYNCBAD-Grenze 10, belegt im Sync-Bericht). Renderentfernung berührt die
   Simulation nicht; Risiko steckt in **Taktarmut** (`sam_iMaxFPSInactive` zu niedrig →
   Stream-Verzug), mm-Timer-Hunger unter Cgroup-Caps und Clients, die bei
   Mapwechsel/Reconnect in Menü-Zuständen rendern (Guardbedingungen beachten).
   `ser_iKickOnSyncBad` nie abschalten.
10. **Aus Research verwerfen/zurückstellen:** Gemini-Server-Loopback (bereits korrekt
    verworfen – kein nativer Einspeisepunkt); „Protocol-only-Bots" (zurückstellen auf
    unbestimmte Zeit); jede 1.10-ABI-Übernahme; „Xvfb allein entfernen spart CPU"
    (nur mit GL-Entfernung); große BotHost-Vorabinvestition vor Messung.
11. **Übersehene CPU-Quellen:** **wineserver** (separater Prozess, in per-PID-Werten
    unsichtbar!), Xvfb-Prozess, Audio-Bridge/Mixer (`snd_iFormat=0`), das framespannende
    `tm_csHooks`-Lock (Jitter, §2.4), Logvolumen (`bot_iLogEvery=20` × 8 Bots →
    Konsole+Datei-I/O), `REALTIME/TIME_CRITICAL`-Priorität des WinMM-Threads unter
    Cgroup-Konkurrenz.
12. **Wiederverwendbare Engine-Funktionalität:** DedicatedServer.exe (GAT_NONE-Pfad),
    `SSC_DEDICATED`-Zweig in `DoGame`, `net_iExactTimer`, Demo-Client-Pfad
    (Sitzung ohne Fenster), PersistenteSymbols-Bootstrapping, vorhandene
    `BotDriver`-Reconnect-Transaktion.

---

## 9. Benchmark- und Teststrategie (gültiges A/B)

1. **Vorbedingung:** `bot_bDiag=1` (Patch 0008) im Klientenlog bestätigt: init +
   Herzschlag + `enabled=1` + `locals=1111` + Attach-Zeilen. Ohne diese fünf Marker
   wird **keine** CPU-Zahl gemessen.
2. **Keine geteilten Caps.** Entweder gar kein cgroup-Limit (isolierte Kopie, eigene
   Ports/Displays, Produktionslast <50 %) oder ≥2 Kerne pro Instanz. `nr_throttled`
   nebenbei mitschreiben; >0 % throttle → Lauf verwerfen.
3. **Messung:** `pidstat -p <server>,<clientA>,<clientB>,<wineserver*>,<Xvfb> -u -h 1`
   über ≥120 s nach 60 s Warmup; Median+p95 pro PID; CPU-Summe **inklusive**
   wineserver/Xvfb getrennt ausweisen. Zwei Clients phasenversetzt auf derselben Map.
4. **Matrix (nur nach Schritt 1):** ikonisch+NullRender vs. ikonisch ohne Guard vs.
   Render an (je 4 Bots); danach KI-Drossel ein/aus. Gleiche Map/Population/Wine-Stack.
5. **Abnahme pro Kandidat** (aus Plan/AGENTS übernommen): Vanilla-Observer-Join +
   UDP-Population, 60-min-Sync (beide Logs, SYNCBAD-Zähler), sauberes
   `CloseMainWindow`-Ende, DLL-SHA256 dokumentiert, qualifizierte 61DC unberührt.

## 10. Priorisierte Entscheidung

| Rang | Maßnahme | Erwartung | Risiko | Abhängig |
|---|---|---|---|---|
| 1 | Patch 0008 + validierter A/B-Lauf (§9) | Klarheit P0 | ~0 | – |
| 2 | `bot_bDiag`-geführt: ikonisch+Skript (§3.2) | ggf. −30–60 % je Client [Hyp.] | niedrig | 1 |
| 3 | PR-40-Guard behalten (Merge nach Qualifikation) | −SwapBuffers-Rest+Jitterfrei | niedrig | 1–2 |
| 4 | Patch 0009 mit Betriebsprofil | Rays −~90 % [Hyp.] | niedrig | 1 |
| 5 | Option B: DedicatedServer als Client | Headless ohne Neubau | mittel | 1 |
| 6 | GitHub-Runner-Build-Kette | Shadow-freie Builds | niedrig | – |
| 7 | BotHost.exe (STUFE C) | echtes Headless | hoch | 2–5 negativ getestet |

Unabhängig parallelisierbar: 1+6; 4 nach 1; 5 parallel zu 2/3 auf separater Instanz.
