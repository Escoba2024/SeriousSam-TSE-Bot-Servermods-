# Deep Technical Research & Architecture Review
## CPU-Optimierung, echtes Headless-Rendering und skalierbare Multiplayer-Bots
### Alpha-Gaming – Serious Sam TSE Classic Retail 1.07

| Feld | Wert |
|---|---|
| Datum | 20.10.2026 |
| Gegenstand | CPU-Ursachenanalyse, Headless-Machbarkeit, Architekturvergleich, Roadmap |
| Bezug | `Escoba2024/SeriousSam-TSE-Bot-Servermods-`, Branch `arena/03664331-serioussam-tse-bot-servermods` |
| Referenzcode | `Croteam-official/Serious-Engine` (SE1 **1.10**), lokal geprüft |
| Retail-Binaries | **nicht** analysiert (in dieser Sitzung kein Zugriff auf Shadow/Hetzner) |
| Status | Technische Bewertung. **Kein** Produktiveingriff, **kein** DLL-Rebuild, **keine** Prozessänderung. |

---

## 0. Belegklassen – Pflichtlektüre vor jeder Entscheidung

Dieser Bericht trennt strikt zwischen Beleg und Vermutung. Jede Aussage trägt eine Klasse:

| Kürzel | Bedeutung |
|---|---|
| **`[B110]`** | Im **SE1-1.10-Quellcode** belegt, mit `Datei:Zeile`. Gilt als *Landkarte*, **nicht** als Beweis für Retail-1.07-Binärverhalten. |
| **`[BR07]`** | An **echten Retail-1.07-Binaries** belegt (vorhandene Ghidra-/Log-Arbeiten dieses Projekts). |
| **`[M]`** | Eigene **Messung** aus Projektberichten (CPU, Laufzeiten, Sync-Logs). |
| **`[H]`** | **Hypothese** – technisch begründet, **nicht** belegt. Muss gemessen werden. |
| **`[O]`** | **Offen** – ohne weitere Untersuchung nicht entscheidbar. |

**Grundregel (entspricht `AGENTS.md`):** SE1 1.10 ≠ Retail 1.07 in ABI, Engine, Binär- und Netzwerkschnittstellen. Jede `[B110]`-Aussage über Retail 1.07 ist eine **Arbeitshypothese**, die an der echten Binary gegenzuprüfen ist. Das betrifft vor allem: Timer-Initialisierung, Symbolnamen (`sam_iMaxFPSActive` u. a.), virtuellen Aufbau von `CGame`, und die Anti-Cheat-Clamps in `RenderScene`.

---

# Teil 1 – Executive Summary

## Die drei Maßnahmen mit dem besten Verhältnis CPU-Einsparung / Aufwand

### 🥇 Maßnahme 1 – Render-Schleife im Bot-Client vollständig abschalten (Null-Renderer)
**Aufwand: sehr gering (1 virtuelle Methode in bereits rebuildbarer `GameMP.dll`). Erwartete Wirkung: sehr hoch.**

`CGame::GameRedrawView()` ist eine **virtuelle Methode, die in `GameMP.dll` implementiert ist** `[B110: Sources/GameMP/Game.h:244, Sources/GameMP/Game.cpp:2091; im Projekt: poc/release/gamemp/Game.cpp:2091]`. Der Retail-`SeriousSam.exe` ruft sie pro Frame aus `DoGame()` auf `[B110: Sources/SeriousSam/SeriousSam.cpp:712]`.

**Es ist damit kein Engine-Patch, kein Binary-Patch und kein Reverse Engineering nötig**, um die komplette Render-Pipeline (Scene-Polygon-Aufbau, Model-Setup, Shadowmaps, Partikel, HUD, llvmpipe-Rasterisierung) zu entfernen. Ihr baut `GameMP.dll` bereits neu.

Detail und Risiken: → Teil 5, **M1**.

---

### 🥈 Maßnahme 2 – MainLoop-Drossel: FPS/Simulations-Loop auf 20–30 Hz begrenzen
**Aufwand: minimal (INI-Wert, optional 10 Zeilen Code in `CGame::GameMainLoop`). Erwartete Wirkung: hoch, Risiko: sehr gering.**

Der entscheidende Beleg: **Die Bot-Aktionsrate und der Netzwerk-Heartbeat hängen nicht an der Framerate.** Sie werden von einem eigenen Windows-Multimedia-Timer mit 50 ms Periode getrieben:

```
timeSetEvent(50 ms, TIME_PERIODIC, CTimer_TimerFunc, ...)     [B110: Sources/Engine/Base/Timer.cpp:253-258]
  → CTimer_TimerFunc_internal()
      → alle CTimerHandler::HandleTimer():
          1. CGame::GameHandleTimer()        [B110: GameMP/Game.cpp:915 AddHandler, 751-753]
               → BotDriver_HandleTimer()     [Projekt: Game.cpp:754]
                   → CPlayerSource::SetAction()   [B110: PlayerSource.cpp:152-161]
          2. CNetworkLibrary::TimerLoop()    [B110: Network.cpp:904 AddHandler, 2032-2083]
               → SendActionsToServer()       [B110: Network.cpp:2007-2018]
                   → CPlayerSource::WriteActionPacket()  [B110: PlayerSource.cpp:172-246]
          3. CSoundLibrary::TimerHandler     [B110: SoundLibrary.cpp:743]
```

Die Frame-Schleife (`DoGame()` → `GameMainLoop()` → `CNetworkLibrary::MainLoop()` → `GameRedrawView()` → `LimitFrameRate()`) ist davon **unabhängig** `[B110: SeriousSam.cpp:666-757, 1190]`.

`CNetworkLibrary::MainLoop()` verarbeitet den Spielstrom mit einer `FOREVER`-Schleife, die **alle verfügbaren Sequenzen** abarbeitet `[B110: SessionState.cpp:1089-1200]`. Eine niedrigere MainLoop-Frequenz bedeutet damit nur *größere Batches*, keinen Simulationsverlust.

**Konsequenz:** Ein FPS-Limit von 10/20/30 FPS senkt die CPU-Last drastisch, **ohne** die Bot-Aktionsrate (20 Hz) oder das Aktions-Sendeintervall zu verändern.

**Warnung:** `sam_iMaxFPSActive` ist im Code mit **500** voreingestellt `[B110: SeriousSam.cpp:47]`. Euer Fleet-Skript setzt ihn auf 60 (`poc/scripts/LocalBotReleaseCore.ps1:30`) – **für das Hetzner-„lowrender“-Profil ist das nicht belegt** `[O]`. Wenn dort der Default 500 aktiv ist, läuft die Render-Schleife ungebremst.

Detail: → Teil 5, **M2**.

---

### 🥉 Maßnahme 3 – `DedicatedServer.exe` als echter Headless-Bot-Host (kein Xvfb, kein GL, kein Sound)
**Aufwand: mittel. Erwartete Wirkung: sehr hoch (Xvfb, llvmpipe, Fenster, Audio entfallen vollständig).**

`DedicatedServer.exe` ist ein Retail-Binary, das die **komplette Welt-Simulation ohne jedes Fenster, ohne Display Mode, ohne GL-Kontext und mit `printf`-Konsole** betreibt `[B110: DedicatedServer.cpp:184 `_bDedicatedServer = TRUE`, Adapter.cpp:77/236/307, Console.cpp:229-231]`. Es ist der einzige Retail-Pfad, der **bewiesen** headless läuft.

Weil `CGame::NewGame()` **ebenfalls virtuell und in `GameMP.dll`** liegt `[B110: GameMP/Game.h:267; Projekt: Game.cpp:1103]`, kann `GameMP.dll` den vom EXE aufgerufenen `NewGame()` (Server-Start) in einen `JoinGame()` (Client-Join) umbiegen – wieder **ohne Binary-Eingriff**.

Detail und Risiken: → Teil 5, **M3**.

---

## Zusätzlicher Befund mit hoher Priorität (betrifft euer Sync-Problem)

**Euer Patch 0007 (`poc/patch/0007-gamemp-ai-render-lock.patch`) serialisiert den 20-Hz-Timer hinter die komplette Frame-Renderzeit.**

Der Patch setzt `CTSingleLock slBotRender(&_pTimer->tm_csHooks, TRUE)` an den **Anfang von `CGame::GameRedrawView()`** und hält ihn für den **gesamten Frame**. Genau dieselbe Critical Section wird aber von `CTimer_TimerFunc()` als **allererstes** genommen, bevor irgendein Handler läuft `[B110: Timer.cpp:118-124]`.

**Folge:** Während jedes gerenderten Frames blockiert der Timer-Thread. Bot-Aktionserzeugung **und** Netzwerk-Heartbeat (`SendActionsToServer`) werden um die volle Frame-Dauer verzögert. Da `net_iExactTimer` per Default **2** ist („execute exactly one pending“ pro Interrupt) `[B110: Network.cpp:149, 2046-2050]`, führt das zu **Takt-Drift der Aktionen** – und der Sync-CRC enthält genau die letzten beiden Aktionen jedes Spielers `[B110: SessionState.cpp:820-828]`.

Das ist eine **begründete, quellcodegestützte Hypothese `[H]`** für `SYNCBAD` – *kein* Beweis. Sie liefert aber eine testbare Vorhersage: **Wenn Rendering verschwindet, verschwindet auch die Rechtfertigung für Patch 0006/0007 – und damit eine konkrete Taktstörungsquelle.**

CPU-Optimierung und Sync-Stabilität sind in dieser Architektur **dasselbe Problem**. → Teil 2.4 und Teil 5 **M4**.

---

# Teil 2 – Technische Ursachenanalyse

## 2.1 Wie die Engine-Basislast tatsächlich verteilt ist `[B110, mit 1.07-Vorbehalt]`

Es gibt **zwei getrennte Taktquellen** pro Client-Prozess:

| Taktquelle | Frequenz | Inhalt | Thread |
|---|---|---|---|
| **Multimedia-Timer** (`timeSetEvent`, 50 ms) | **20 Hz fix** | Bot-Aktionen (`SetAction`), Netzwerk-Heartbeat (`SendActionsToServer`, `Client_Update`, ggf. `ServerLoop`), Sound-Mixing | eigener winmm-Thread |
| **Frame-Schleife** (`DoGame()`) | `sam_iMaxFPSActive` (Default **500**, euer Skript: 60) | `CNetworkLibrary::MainLoop()` (Spielstrom verarbeiten, Prediction, GameAgent-Queries, Broadcast), `GameRedrawView()` (komplettes Rendering), `LimitFrameRate()` | Main-Thread |

Wichtig: Beide laufen über **dieselbe Critical Section** `ga_csNetwork`:
- `CNetworkLibrary::MainLoop()` hält sie über die gesamte Iteration `[B110: Network.cpp:1821]`
- `CNetworkLibrary::TimerLoop()` blockiert darauf bei `net_iExactTimer==2` `[B110: Network.cpp:2047-2050]`
- **`BotDriver_HandleTimer()` hält sie über den gesamten Bot-Tick** `[Projekt: BotDriver.cpp, CTSingleLock slBotWorld(&_pNetwork->ga_csNetwork, TRUE)]`

Und `tm_csHooks` wird von `CTimer_TimerFunc` **und** (durch Patch 0007) von `GameRedrawView` gehalten.

**Daraus folgt eine harte strukturelle Aussage:** Renderzeit, Bot-Tick-Zeit und Netzwerk-Heartbeat sind **serialisiert**. Jede Millisekunde Rendering verzögert den Netzwerk-Takt; jede Millisekunde Bot-Raycasting ebenfalls.

## 2.2 Nachgewiesene Ursachen

| # | Ursache | Beleg |
|---|---|---|
| U1 | Rendering läuft pro Frame vollständig: Prescan (`_pInput->GetInput(TRUE)`, `CreateAction` pro lokalem Spieler), `MakeSplitDrawports`, `RenderGameView` pro Viewer, `PrintStats`, `ConsolePrintLastLines`, `SwapBuffers` | `[B110: GameMP/Game.cpp:2092-2340, SeriousSam.cpp:707-754]` |
| U2 | llvmpipe-Rasterisierung läuft **im Client-Prozess** und zählt damit zur gemessenen Prozess-CPU (Arbeitsthreads inklusive) | `[M]` + Mesa-Architektur |
| U3 | `sam_iMaxFPSActive` Default = **500**; Frame-Schleife ist damit faktisch unbegrenzt | `[B110: SeriousSam.cpp:47]` |
| U4 | `MainLoop()` (Spielstrom + Broadcast + GameAgent) läuft **pro Frame**, d. h. bis zu 500×/s | `[B110: SeriousSam.cpp:686, Network.cpp:1819]` |
| U5 | Der komplette Render-Block wird bei minimiertem Fenster übersprungen (`IsIconic`) und der Limiter nutzt dann `sam_iMaxFPSInactive` (Default **10**) | `[B110: SeriousSam.cpp:707, 250-251]` |
| U6 | Der Dedicated Server betreibt dieselbe Welt-Simulation **ohne** Rendering für **8–16 %** eines Kerns | `[M: eigene Messung 20.10.2026]` |
| U7 | Bot-Tick führt bis zu **76 Raycasts pro Tick** aus (4 Bots × (bis 16 Sichtlinien + 3 Hindernis-Rays)) – unter `ga_csNetwork` | `[Projekt: BotDriver.cpp, BotCombatVisible/BotObstacleDistance]` |
| U8 | Rendering und Raycasting teilen das Brush-Sektor-Scratchflag `BSCF_RAYTESTED = 1<<6` (0x40) | `[B110: Brushes/Brush.h:468, World/WorldRayCasting.cpp:127/580/583]` + `[BR07: AGENTS.md, Patch 0006/0007]` |
| U9 | Die Anti-Cheat-Clamps in `RenderScene()` erzwingen in Multiplayer `gfx_bRenderWorld`, `wld_bRenderShadowMaps`, `wld_bRenderTextures`, `wld_bRenderDetailPolygons` = TRUE | `[B110: Graphics/DrawPort_RenderScene.cpp:721-733]` |

## 2.3 Begründete Hypothesen

| # | Hypothese | Begründung | Prüfschritt |
|---|---|---|---|
| **H1** | **Rendering + Per-Frame-Overhead + Wine/Xvfb sind der größte Einzelposten** (Größenordnung 50–70 Prozentpunkte pro Client-Prozess) | U6 zeigt: reine Welt-Simulation + Netzwerk für 8 Spieler kostet 8–16 %. Ein Bot-Client simuliert dieselbe Welt, plus 4 Spieler-Entitäten, plus Rendering. Bei 70–87 % Messwert bleibt ein Delta von ~55–75 Pp. | M1 + Messung (Teil 6) |
| **H2** | **Die MainLoop-Frequenz allein ist ein signifikanter Posten**, auch ohne Rendering | `MainLoop()` nimmt `ga_csNetwork`, verarbeitet den Strom, `GameAgent_ServerUpdate`, Broadcast-Socket-Poll. Bei 500 Hz ist das 500×/s. Ist `sam_iMaxFPSActive` tatsächlich 500, erklärt das einen Teil der Last auch unabhängig von llvmpipe. | M2 mit variierter Loop-Rate |
| **H3** | **Bot-Raycasting ist kein zu vernachlässigender Posten** | ~76 `CCastRay`/Tick × 20 Hz = ~1520 Rays/s, jeder mit Sektor-Traversierung und Flag-RMW – unter dem globalen Netzwerk-Mutex. | Ray-Zähler instrumentieren, LOS-Cache (M4) |
| **H4** | **Patch 0007 verzögert den 20-Hz-Netzwerk-Takt um die Frame-Zeit und trägt zu `SYNCBAD` bei** | Siehe Teil 1; `net_iExactTimer==2` execute-one-Semantik + `ga_ctTimersPending`-Drift | A/B-Test mit und ohne Rendering, `ser_bReportSyncLate/Early` auf Testserver |
| **H5** | **`LP_NUM_THREADS` (llvmpipe) erhöht die Kontextwechsel-Last auf 2 vCPU** | llvmpipe erzeugt pro Kontext standardmäßig Worker-Threads (Anzahl ~CPU-Kerne). Zwei Clients × N Threads auf 2 vCPU ⇒ Oversubscription. | `LP_NUM_THREADS=1` A/B-Messung |

## 2.4 Offene Fragen

| # | Frage | Warum offen |
|---|---|---|
| O1 | Welche `sam_iMaxFPSActive/Inactive`, `sam_iScreenSizeI/J`, `sam_bPauseOnMinimize` stehen **im Hetzner-lowrender-Profil** in `Scripts/PersistentSymbols.ini`? | Nicht im Repo; `LocalBotReleaseCore.ps1` setzt 60/30/960×540 – Produktionsprofil weicht ab (320×240 laut Angabe). |
| O2 | Existieren `sam_iMaxFPSActive`/`sam_iMaxFPSInactive` in Retail-1.07-`SeriousSam.exe` als Shell-Symbole? | Aus 1.10 belegt; Retail-1.07-Symboltabelle **nicht** geprüft. Prüfbar mit `strings`/Ghidra auf der EXE. |
| O3 | Ist `CGame` in Retail 1.07 so aufgebaut, dass `GameRedrawView`/`GameMainLoop`/`NewGame` von der ModSDK-Fassung aus überschrieben werden können? | Praktisch belegt (`61DC…`-DLL läuft), aber die **vtable-Reihenfolge** ist nicht statisch verifiziert. |
| O4 | Funktioniert das Spiel bei komplett deaktiviertem Rendering stabil (keine Texture/Model-Prepare-Abhängigkeit in Logikpfaden)? | `[H]`: wahrscheinlich ja (Textur-/Model-Daten werden unabhängig vom Renderer geladen; nur der Upload ist rendergetrieben). Muss ein 60-Minuten-Lauf zeigen. |
| O5 | Wie hoch ist der tatsächliche RAM-Verbrauch pro Client-Prozess? | Wird ab ~16 Bots zum Limit (4 GB gesamt). |
| O6 | Verhalten von `IsIconic()` unter Wine/Xvfb ohne Window-Manager | Ohne WM gibt es keine Iconify-Zustände. Mit leichtem WM (z. B. `openbox` in Xvfb) testbar. |

---

# Teil 3 – Architekturvergleich

Bewertungsskala: **–** schlecht · **○** mittel · **+** gut · **++** sehr gut

| Kriterium | **A1** Optimierte Wine-Clients | **A2** Null-Renderer | **A3** Native Headless-Clients (DedicatedServer.exe) | **A4** Server-integrierte Bots | **A5** Protokollkompatible Bot-Clients | **A6** Hybrid (1 Engine, N virtuelle Spieler) |
|---|---|---|---|---|---|---|
| **Prinzip** | Bestehende Clients, minimierte Grafik | `GameMP.dll`: `GameRedrawView()` = no-op | Retail-`DedicatedServer.exe` joint statt hostet | Bots im Dedicated-Server-Prozess | Eigener Netzwerk-Client, nur Protokoll | Eine Engine-Instanz, mehrere lokale Spieler |
| **CPU/4 Bots (Erwartung)** | 40–70 % Kern | 25–45 % Kern | 12–25 % Kern | 8–20 % Kern (für alle Bots) | 2–8 % Kern | ≈ A2/A3, geteilte Welt |
| **Xvfb / GL nötig** | ja | ja (Fenster + Kontext bleiben) | **nein** | nein | nein | ja (außer A3-Variante) |
| **Sound/Input-Last** | ja | ja | **nein** | nein | nein | ja |
| **Entwicklungsaufwand** | **sehr gering** | **gering** | mittel | **hoch** | **sehr hoch** | mittel–hoch |
| **Nötiger Eingriff** | INI/Wine/Mesa | **nur `GameMP.dll`** | **nur `GameMP.dll`** (+ Retail-EXE unverändert) | `Engine.dll`/`GameMP.dll`, tiefe RE | Vollständige Protokoll-Reimplementierung | `GameMP.dll` + Engine-Grenzen |
| **Vanilla-Kompatibilität** | ++ (bewiesen) | ++ (Client unverändert) | ++ (echter Client-Handshake) | ○ (Sync/Ping-Semantik unklar) | ○–(Client-CRC/Deltas nötig) | ++ |
| **Risiko Desync** | wie heute | **sinkt** (Timer nicht mehr blockiert) | **sinkt** | **steigt** (kein echter Remote-Client) | **hoch** (CRC/Deltas/Session-State) | wie A2 |
| **Skalierbarkeit** | ○ | + | ++ | ++ (theoretisch) | ++ (theoretisch) | + |
| **RAM/Prozess** | hoch | hoch | mittel | sehr niedrig | sehr niedrig | mittel |
| **Abhängigkeit von Retail-RE** | keine | keine | keine | **hoch** | **sehr hoch** | gering |
| **Empfehlung** | **sofort** | **sofort** | **als Hauptziel** | verwerfen (vorerst) | verwerfen | als Variante von A2/A3 |

## Begründung der Einzelbewertungen

**A5 – Protokollkompatible Bot-Clients: verwerfen.** Der Client muss nicht „nur Aktionen senden“. Er muss
1. den Join-Handshake inkl. `MSG_REQ_CONNECTPLAYER`/`MSG_REP_CONNECTPLAYER` ausführen `[B110: PlayerSource.cpp:41-113]`,
2. das **State-Delta** verarbeiten (`MSG_REP_STATEDELTA`),
3. den **CRC-Gather** mitliefern (`MSG_REQ_CRCCHECK`, `InitCRCGather`) `[B110: SessionState.cpp:399, Network.cpp:1240-1247]`,
4. den gesamten `MSG_SEQ_ALLACTIONS`-Strom Block für Block in **exakt derselben Reihenfolge** anwenden (`ProcessGameStreamBlock`, Handler ab `SessionState.cpp:1317`),
5. die **komplette deterministische Welt-Simulation** mit `CPlayerEntity::ChecksumForSync` ausführen, weil der 1-Hz-Sync-CRC Sequence, Level, Pause **und die letzten beiden Aktionen jedes aktiven Spielers plus jeden Spieler-Entity-Checksum** umfasst `[B110: SessionState.cpp:792-830, 1880-1913]`.

Das ist **kein** „leichter Netzwerkclient“, sondern eine vollständige Engine-Nachbildung – mit dem zusätzlichen Risiko, dass jede Float-/RNG-/Reihenfolgeabweichung sofort `SYNCBAD` erzeugt. Aufwand und Risiko stehen in keinem Verhältnis. **Verwerfen.**

**A4 – Server-integrierte Bots: zurückstellen, nicht verwerfen.** Der Designbericht (`docs/superpowers/specs/2026-09-30-vanilla-server-bots-design.md`) hat „Pfad B2“ bereits als Fallback mit korrekt benannten Risiken bewertet. Die zusätzliche Erkenntnis aus dieser Analyse: **`SeriousSam.exe` kann selbst im `SSC_DEDICATED`-Modus ohne Rendering hosten** `[B110: GameMP/Game.cpp:2134, SeriousSam.cpp:252]`. Ein Server **mit** lokalen Bot-Spielern (Listen-Server) würde jedoch `gm_CurrentSplitScreenCfg != SSC_DEDICATED` erzwingen und damit Rendering wieder aktivieren. Der Gewinn gegenüber A3 ist damit geringer als er scheint. **Zurückstellen.**

**A6 – Hybrid:** In eurer Architektur ist A6 **bereits realisiert** – 4 lokale Spieler teilen eine Engine-Instanz (`NET_MAXLOCALPLAYERS = 4`) `[B110: Network.h:31]`. Eine Erweiterung auf >4 lokale Spieler erforbert Eingriffe in `gm_lpLocalPlayers[4]`, `NET_MAXLOCALPLAYERS`, Split-Screen-Cfg und die Drawport-Aufteilung. **Nicht priorisieren** – A3 skaliert pro Prozess-Kosten günstiger als das Aufbohren des 4er-Limits.

---

# Teil 4 – Headless-Machbarkeit (Retail TSE 1.07)

## 4.1 Begriffstrennung – was spart wirklich CPU?

| Variante | Fenster | GL-Kontext | Scene-Aufbau | Rasterisierung | SwapBuffers | CPU-Einsparung |
|---|---|---|---|---|---|---|
| **Verstecktes Spielfenster** | ja | ja | ja | ja | ja | **0 %** – rein kosmetisch |
| **Software-Rendering, niedrige Auflösung** | ja | ja | ja | reduziert | ja | gering–mittel (nur Fragmentkosten) |
| **FPS-Limit 10–30** | ja | ja | proportional weniger | proportional weniger | proportional weniger | **hoch** |
| **Null-Renderer** (`GameRedrawView` = no-op) | ja | ja (bleibt) | **nein** | **nein** | ja (1×/Frame) | **sehr hoch** |
| **Vollständig deaktivierte Render-Schleife** (minimiertes Fenster / `IsIconic`) | ja | ja | nein | nein | nein | **sehr hoch** |
| **Echter Headless-Client** (`DedicatedServer.exe`) | **nein** | **nein** | nein | nein | nein | **maximal** |

Euer Auftrag lautet ausdrücklich: keine Vorschläge, die Rendering nur verstecken. Die Tabelle zeigt, wo Einsparung real ist.

## 4.2 Die sieben Einzelfragen (Teil A der Aufgabenstellung)

| # | Frage | Antwort | Klasse |
|---|---|---|---|
| 1 | Kann der OpenGL-Renderer vollständig deaktiviert werden? | **Im laufenden Client nicht ohne Fenster** – `SeriousSam.exe` erzeugt Display Mode + `CViewPort` vor Spielbeginn. Aber: **`GfxLibrary::Init()`/Display-Mode werden von `DedicatedServer.exe` nie aufgerufen** ⇒ dort existiert kein GL-Kontext. | `[B110: Adapter.cpp:77/236/307, DedicatedServer.cpp:182-260]` |
| 2 | Braucht die Serious Engine zwingend einen GL-Kontext? | **Simulation: nein.** `DedicatedServer.exe` beweist das. **Der `SeriousSam.exe`-Prozess: praktisch ja**, weil `StartNewMode()` im EXE vor der Spielschleife läuft. | `[B110]` |
| 3 | Können Render-Aufrufe durch einen Null-Renderer ersetzt werden? | **Ja, in `GameMP.dll`.** `GameRedrawView()` ist virtuell. Das ist der Null-Renderer – ohne Engine-Patch. | `[B110: Game.h:244]` |
| 4 | Können Present/SwapBuffers/Draw-Aufrufe unterdrückt werden? | **Draw-Aufrufe: ja** (M1). **`SwapBuffers` liegt im EXE** (`SeriousSam.cpp:754`) und ist aus `GameMP.dll` nicht direkt entfernbar – aber bei 20–30 Hz vernachlässigbar. Vollständig entfällt es in A3. | `[B110]` |
| 5 | Lässt sich die Render-Schleife von der Simulation trennen? | **Sie ist bereits getrennt** – 20-Hz-Timer (Simulation/Aktionen/Netzwerk) vs. Frame-Schleife (MainLoop + Render). Genau diese Trennung macht FPS-Limiting sicher. | `[B110: Timer.cpp:253-258, Network.cpp:2032]` |
| 6 | Kann Xvfb vollständig entfallen? | **Nur in A3** (`DedicatedServer.exe`). Bei `SeriousSam.exe` nein – Wine braucht ein Display für Fenster/GL. Verkleinerung (z. B. `320x240x16`, MIT-SHM) senkt nur den X-Server-Anteil. | `[B110]` |
| 7 | Abhängigkeiten Rendering ↔ Timing/Physik/Netzwerk? | **Zwei relevante Kopplungen:** (a) `BSCF_RAYTESTED` (0x40) als geteiltes Ray-Scratchflag, das der Renderer per RMW berührt (euer Patch 0006/0007); (b) `tm_csHooks` – der Timer-Thread blockiert, solange `GameRedrawView` sie hält. **Beide verschwinden mit dem Rendering.** | `[B110]` + `[BR07]` |

## 4.3 Zwischenfazit zur Machbarkeit

| Ziel | Machbarkeit | Begründung |
|---|---|---|
| **Null-Renderer (A2)** | **Praktikabel, kurzfristig** | Eine virtuelle Methode in `GameMP.dll`. Kein RE, kein Binary-Patch. |
| **Vollständig Headless (A3)** | **Praktikabel, mittelfristig** | Retail-`DedicatedServer.exe` + `NewGame()`-Override in `GameMP.dll`. |
| **Headless-Patch direkt in `SeriousSam.exe`/`Engine.dll`** | **Nicht empfohlen** | Höheres Risiko, kein Mehrwert gegenüber A3, da A3 den headless Pfad bereits Retail-seitig bereitstellt. |
| **Xvfb-Abschaltung bei `SeriousSam.exe`** | **Nicht ohne Binary-Patch** | Fenster/GL werden im EXE erzeugt. |

---

# Teil 5 – Konkrete Implementierung

Alle Änderungen liegen, soweit nicht anders angegeben, **ausschließlich in `GameMP.dll`** (Quellen: `poc/release/gamemp/`).

## M1 – Null-Renderer (Priorität: P0)

**Funktionsprinzip:** `CGame::GameRedrawView()` wird für Bot-Clients zum No-op. Damit entfallen Prescan, `MakeSplitDrawports`, `RenderGameView` (Welt + Modelle + Schatten + Partikel + HUD), `PrintStats`, `ConsolePrintLastLines` und `SE_PretouchIfNeeded`.

**Betroffene Komponenten:** `GameMP/Game.cpp` (`CGame::GameRedrawView`), Wertepfad `SeriousSam.cpp:712` → vtable.

**Änderung (Pseudocode):**

```cpp
// BotDriver.h
extern INDEX bot_bNullRender;     // default 0

// BotDriver.cpp – BotDriver_Init()
_pShell->DeclareSymbol("user INDEX bot_bNullRender;", &bot_bNullRender);

// Game.cpp
void CGame::GameRedrawView(CDrawPort *pdpDrawPort, ULONG ulFlags)
{
  // BOT-MODUS: komplette Render-Pipeline überspringen.
  // Gründe:
  //  * kein Betrachter benötigt die Ausgabe;
  //  * Renderer + Bot-Raycasts teilen das Sektor-Scratchflag BSCF_RAYTESTED (1<<6);
  //  * der bisherige CTSingleLock auf _pTimer->tm_csHooks (Patch 0007) blockierte
  //    den 20-Hz-Timer für die gesamte Frame-Dauer. Beides entfällt hier.
  if (bot_bNullRender) {
    return;
  }
  ... unveränderter Originalcode ...
}
```

**Erforderliche Nebenänderung:** Der `CTSingleLock slBotRender(&_pTimer->tm_csHooks, TRUE);` aus Patch 0007 darf **nicht** im aktiven Bot-Pfad stehen. Empfehlung: hinter `if (!bot_bNullRender)` schieben, also nur im Render-Pfad halten.

```cpp
void CGame::GameRedrawView(CDrawPort *pdpDrawPort, ULONG ulFlags)
{
  if (bot_bNullRender) return;                       // <-- vor dem Lock!
  CTSingleLock slBotRender(&_pTimer->tm_csHooks, TRUE);
  ...
}
```

**Erwartetes Einsparpotenzial:** `[H]` Größenordnung 40–60 % der Client-Prozesslast (zu messen).

**Aufwand:** ~1–2 Personenstunden Build + native Abnahme.

**Risiken**

| Risiko | Bewertung | Gegenmaßnahme |
|---|---|---|
| Logikpfad liest rendergetriebene Daten (Texture/Model-Prepare) | niedrig–mittel `[H]` | 60-Min-Lauf mit Crash-Watch; Fallback: `pdp->Lock()` behalten und nur `RenderGameView` überspringen |
| HUD-/Statistik-Ausgaben fehlen in Logs | gewollt | Diagnose auf `BotLog`-Pfade umstellen (bereits vorhanden) |
| Thumbnail-Pfad (`_fnmThumb`) wird nie bedient | irrelevant (nur Savegame) | – |
| Retail-1.07-vtable abweichend | niedrig `[O3]` | Da `GameRedrawView` in der produktiven `61DC…`-DLL bereits überschrieben ist, ist der Aufrufpfad praktisch belegt |

**Verifikation**
1. Log-Marker `[BotNullRender] active=1` beim Start.
2. Prozess-CPU vor/nach, identische Map/Spielerzahl (Teil 6).
3. 60-Minuten-Lauf mit Vanilla-Observer: Join, Frags, Respawn, Mapwechsel, `SYNCBAD`-Zähler = 0.
4. Kontrollprobe mit `bot_bNullRender=0` (uninstrumentiert).

---

## M2 – MainLoop-Drossel (Priorität: P0)

**Funktionsprinzip:** Die Frame-Schleife wird auf 20–30 Hz begrenzt. Simulation/Aktionen/Netzwerk laufen unverändert im 20-Hz-Timer.

**Variante 2a – ohne Code (sofort testbar):** In der Client-Startup-INI (analog `poc/scripts/BotStartup.ini`):

```ini
sam_iMaxFPSActive   = 25;   // war vermutlich 500 (Default) oder 60
sam_iMaxFPSInactive = 25;
sam_bPauseOnMinimize = 0;
```

> **Voraussetzung `[O2]`:** Prüfen, dass diese Symbole in Retail-1.07-`SeriousSam.exe` existieren:
> `strings -a Bin/SeriousSam.exe | grep -i 'sam_iMaxFPS'` bzw. Ghidra-Symbolsuche.
> Falls nicht vorhanden ⇒ Variante 2b.

**Variante 2b – in `GameMP.dll` (unabhängig von EXE-Symbolen):**

```cpp
// BotDriver.h
extern INDEX bot_iMainLoopHz;   // 0 = native LimitFrameRate des EXE

// Game.cpp – am ENDE von CGame::GameMainLoop(), NACH _pNetwork->MainLoop()
void CGame::GameMainLoop(void)
{
  ... unveränderter Originalcode bis Zeile 2737 ...

  // BOT-MODUS: Frame-Schleife drosseln.
  // Der 20-Hz-Multimedia-Timer (BotDriver_HandleTimer + CNetworkLibrary::TimerLoop)
  // ist davon NICHT betroffen: Aktionsrate und Sendetakt bleiben 20 Hz.
  if (bot_iMainLoopHz > 0) {
    static CTimerValue tvLast(0I64);
    static BOOL bInit = FALSE;
    CTimerValue tvNow = _pTimer->GetHighPrecisionTimer();
    if (!bInit) { tvLast = tvNow; bInit = TRUE; }
    const TIME tmDelta = (tvNow - tvLast).GetSeconds();
    const TIME tmWanted = 1.0f / (FLOAT)bot_iMainLoopHz;
    if (tmDelta < tmWanted) {
      Sleep((DWORD)((tmWanted - tmDelta) * 1000.0f));
    }
    tvLast = _pTimer->GetHighPrecisionTimer();
  }
}
```

**Wichtig:** Der Sleep steht **nach** `_pNetwork->MainLoop()`, also **außerhalb** von `ga_csNetwork` – er blockiert damit weder den Timer-Thread noch die Stream-Verarbeitung.

**Empfohlene Startwerte:** 25 Hz (Testmatrix: 60 / 30 / 25 / 20 / 10).

**Untere Grenze:** Bei 10 Hz verarbeitet `MainLoop()` im Mittel 2 Sequenzen pro Iteration; `ses_bKeepingUpWithTime` bleibt bis exakt 2 Ticks TRUE `[B110: Network.cpp:1912]`. Bei Jitter können einzelne Iterationen 3 Sequenzen verarbeiten und das Flag kippen (betrifft Demo-Sync/Lerp, **kein** Disconnect-Kriterium). **Mindestempfehlung 20 Hz**, 10 Hz nur als Experiment.

**Risiken:** Bei zu niedriger Rate aktualisiert sich die local-player-Platzierung seltener (Bot sieht leicht veraltete Positionen – KI-Qualität, keine Sync-Relevanz). GameSpy-Query-Antworten werden mit bis zu 50 ms Verzögerung beantwortet (unproblematisch).

**Verifikation:** `MainLoop`-Zähler + gemessene Iterationsrate im Log; Action-Tick-Kontinuität prüfen (`[BotDriver]`-Ticks dürfen nicht springen); `SYNCLATE`/`SYNCEARLY` auf Testserver beobachten.

---

## M3 – `DedicatedServer.exe` als Headless-Bot-Host (Priorität: P1)

**Funktionsprinzip:** Retail-`DedicatedServer.exe` lädt `GameMP.dll` und ruft `CGame::NewGame()` zum Server-Start auf `[B110: DedicatedServer.cpp:159-172]`. Da `NewGame()` virtuell und in `GameMP.dll` liegt, wird es im Bot-Modus zu einem `JoinGame()` umgebogen.

**Betroffene Komponenten:** `GameMP/Game.cpp` (`CGame::NewGame`), `BotDriver.cpp`, `DedicatedServer`-Konfiguration (`Scripts/Dedicated/<cfg>/init.ini`, `1_begin.ini`).

**Änderung (Pseudocode):**

```cpp
// BotDriver.h
extern INDEX    bot_bHeadlessJoin;      // 1 = NewGame() wird zum Join
extern CTString bot_strJoinAddress;     // "127.0.0.1:25600"

// BotDriver_Init()
_pShell->DeclareSymbol("user INDEX bot_bHeadlessJoin;",  &bot_bHeadlessJoin);
_pShell->DeclareSymbol("user CTString bot_strJoinAddress;", &bot_strJoinAddress);

// Game.cpp
BOOL CGame::NewGame(const CTString &strSessionName, const CTFileName &fnWorld,
                    CSessionProperties &sp)
{
  if (bot_bHeadlessJoin && bot_strJoinAddress != "") {
    // DedicatedServer.exe setzt "TCP/IP Server" + 0 lokale Spieler.
    // Für den Bot-Join wird beides überschrieben:
    gm_strNetworkProvider   = "TCP/IP Client";   // statt Server
    gm_StartSplitScreenCfg  = SSC_PLAY4;         // 4 lokale Bot-Spieler
    gm_MenuSplitScreenCfg   = SSC_PLAY4;
    gm_aiStartLocalPlayers[0] = 0;               // Profile 0..3
    gm_aiStartLocalPlayers[1] = 1;
    gm_aiStartLocalPlayers[2] = 2;
    gm_aiStartLocalPlayers[3] = 3;
    BotLog("[BotHeadless] NewGame() -> JoinGame(%s)\n", (const char*)bot_strJoinAddress);
    return JoinGame(CNetworkSession(bot_strJoinAddress));
  }
  ... unveränderter Originalcode ...
}
```

**Konfiguration** (`Scripts/Dedicated/BotClient01/init.ini`):

```ini
ded_iMaxFPS = 25;              // Frame-Schleife des Headless-Hosts
ded_bRestartWhenEmpty = 0;
ded_tmTimeout = -1;
bot_bEnabled = 1;
bot_bAutoCombat = 1;
bot_bObstacleAvoidance = 1;
bot_bHeadlessJoin = 1;
bot_strJoinAddress = "127.0.0.1:25600";
```

**Betroffene Engine-Pfade im Dedicated-Modus (bereits Retail-bewährt):**
- `_bDedicatedServer = TRUE` ⇒ keine Display-Adapter-Enumeration `[B110: Adapter.cpp:77/236/307]` ⇒ **kein Fenster, kein GL**
- Konsole über `printf` `[B110: Console.cpp:229-231]`
- `Load_t()`/`Save_t()` ohne Grafik; `LCDInit()` lädt nur Texture-Daten (kein Upload nötig)
- Reconnect läuft bereits über `BotDriver_HandleReconnect()` aus `CGame::GameMainLoop()` `[Projekt: Game.cpp:2662]` – im Dedicated-Pfad gleichermaßen aktiv

**Erwartetes Einsparpotenzial:** `[H]` Entfall von Xvfb, GL-Kontext, llvmpipe, Fenster, Sound, Input-Prescan. Pro 4-Bot-Prozess Größenordnung 12–25 % eines Kerns statt 70–87 %.

**Aufwand:** 1–2 Tage Implementierung + native Abnahme.

**Risiken**

| Risiko | Bewertung | Gegenmaßnahme |
|---|---|---|
| `InitializeGame()` lädt `Data\DedicatedServer.gms`; Player-Profile/Split-Screen-Cfg müssen gesetzt werden | mittel | Eigene `.gms`-Kopie mit `SSC_PLAY4`; Vorbild `LocalBotReleaseCore.ps1` (binäre `.gms`-Slot-Patches) |
| `_pSound` im Dedicated-Modus nicht initialisiert | niedrig | `JoinSession_t()` ruft `_pSound->Mute()` `[B110: Network.cpp:1233]` – auf Absturz achten; notfalls Sound-Aufrufe in BotDriver kapseln |
| `gm_strNetworkProvider`-String muss exakt dem Retail-Namen entsprechen | mittel | Echten Provider-Namen aus einem funktionierenden Join-Log oder der EXE entnehmen |
| `LoadPlayersAndControls()` erwartet 4 gültige `.plr`-Profile | mittel | Profil-Erzeugung aus dem bestehenden Fleet-Skript wiederverwenden |
| Kein Renderer ⇒ kein `pdp`; Codepfade, die ein Drawport erwarten | mittel | `LoadingHook_t` im Dedicated-Pfad ist printf-basiert `[B110: DedicatedServer.cpp:147-157]`; `GameRedrawView` wird nie aufgerufen |
| Retail-1.07-`DedicatedServer.exe` abweichend | `[O]` | Vorab statisch prüfen (Symbole/`_bDedicatedServer`-Setzstelle), dann isolierter Join-Test |

**Verifikation:** Isolierter Testserver; Preflight; Join mit 4 Bots; Vanilla-Observer; 60-Min-Lauf; Prozessliste zeigt **keinen** X-Server-Kontakt (`lsof`/`strace`-Stichprobe); CPU-Messung gegen A2-Baseline.

---

## M4 – Bot-Tick: Raycast-Kosten und Lock-Dauer reduzieren (Priorität: P1)

**Funktionsprinzip:** Der Bot-Tick hält `ga_csNetwork` über die **komplette** Tick-Arbeit inklusive bis zu ~76 Raycasts `[Projekt: BotDriver.cpp]`. Das verzögert `CNetworkLibrary::TimerLoop()` (Senden) und `MainLoop()`.

**Änderungen**

1. **Sichtlinien-Cache:** LOS pro (Bot, Ziel) nur alle **N Ticks** (z. B. alle 5 ⇒ 4 Hz) neu prüfen; zwischenzeitlich Cache verwenden.
2. **Distanz-Gate:** Ziele jenseits einer Schwelle (z. B. 60 m) ohne LOS-Prüfung verwerfen.
3. **Hindernis-Rays reduzieren:** 3 Rays ⇒ 1 Ray + alternierende Seite pro Tick (Round-Robin).
4. **Kritischen Abschnitt verkürzen:** Daten unter dem Lock **kopieren**, Entscheidung außerhalb rechnen.

```cpp
// Schema (vereinfacht)
struct BotSnapshot { FLOAT3D vPos; FLOAT3D vView; FLOAT fHealth; INDEX iIndex; BOOL bLocal; };

BOOL BotDriver_HandleTimer(CGame *pgame)
{
  // 1) Kurzer Lock: nur Snapshots kopieren
  BotSnapshot aSnap[16]; INDEX ctSnap = 0;
  CPlayerSource *appls[4]; CPlayerAction aDummy[4];
  {
    CTSingleLock sl(&_pNetwork->ga_csNetwork, TRUE);
    // ... Snapshots + Character-Pointer + Waffen/Ammo kopieren ...
  }

  // 2) Ohne Lock: botcore::DecideCombat(), Zielwahl, Waffenwahl (rein)
  //    Raycasts nur noch fuer die tatsaechlich benoetigten Kandidaten,
  //    gecached ueber bot_iLosCacheTicks.

  // 3) Kurzer Lock: Ergebnisse schreiben (SetAction)
  {
    CTSingleLock sl(&_pNetwork->ga_csNetwork, TRUE);
    for (i = 0; i < 4; i++) if (appls[i]) appls[i]->SetAction(pa[i]);
  }
  return TRUE;
}
```

> **Warnung:** Schritt 2 ohne Lock bedeutet, dass `CCastRay` **nicht** mehr unter `ga_csNetwork` läuft – genau die Race, die Patch 0006/0007 adressiert. Diese Umstellung ist damit **erst nach M1 (Rendering aus)** zulässig, oder der Raycast muss unter `tm_csHooks` (kurz) statt `ga_csNetwork` (lang) laufen. **Reihenfolge beachten: M1 vor M4b.**

**Erwartetes Einsparpotenzial:** `[H]` Raycast-Anteil grob −70…−85 %; zusätzlich geringerer Timer-Jitter.

**Verifikation:** Ray-Zähler und Tick-Dauer (`QueryPerformanceCounter`) im Log; `SYNCLATE`/`SYNCEARLY`/`SYNCBAD` auf Testserver.

---

## M5 – Kurzfristige Grafik-/Wine-Optimierungen (Priorität: P1 für A1, P2 nach M1)

| Maßnahme | Wirksamkeit | Begründung / Randbedingung |
|---|---|---|
| `sam_iMaxFPSActive` 500 → 25 | **sehr hoch** | Siehe M2. |
| Fenster minimieren (`IsIconic`) | **sehr hoch**, falls WM verfügbar | Überspringt den kompletten Render-Block inkl. `SwapBuffers` `[B110: SeriousSam.cpp:707]`. Erfordert `sam_bPauseOnMinimize = 0` (bereits im Fleet-Skript) und einen Window-Manager in Xvfb. `[O6]` |
| llvmpipe: `LP_NUM_THREADS=1` (bzw. 2) | mittel | Reduziert Thread-Oversubscription auf 2 vCPU. **A/B messen** – mit 2 Threads kann der Durchsatz auf 2 vCPU besser sein. |
| Xvfb verkleinern: `Xvfb :1 -screen 0 320x240x16 -nolisten tcp` | gering–mittel | Senkt nur den X-Server-Anteil; MIT-SHM aktiv lassen. |
| Wine-Audio auf `null` (`wine reg add "HKCU\Software\Wine\Drivers" /v Audio /d null`) | gering–mittel | Sound-Timer-Handler läuft weiter (20 Hz), aber ohne Gerät. Messen. |
| `WINEDEBUG=-all`, kein `winedbg` | gering | Reduziert Syscall-/Logging-Overhead. |
| `sam_iScreenSizeI/J` verkleinern (z. B. 160×120) | mittel – **nur solange gerendert wird** | Wirkt direkt auf die Fragmentzahl. Clamp in `StartNewMode` prüfen. |
| `sam_iVideoSetup = 0` („speed“) | gering (in MP teils überschrieben) | GLSettings-Skript wird ausgeführt; einige Werte werden in MP zurückgesetzt. |
| `gfx_bRenderWorld`, `wld_bRenderShadowMaps`, `wld_bRenderTextures`, `wld_bRenderDetailPolygons` | **wirkungslos in MP** | Werden in `RenderScene()` bei `_bMultiPlayer` erzwungen `[B110: DrawPort_RenderScene.cpp:721-733]`. **Kosmetisch – nicht darauf verlassen.** |
| `gfx_bRenderModels`, `mdl_bFineQuality`, `mdl_iShadowQuality`, `mdl_fLODMul`, `gap_iTextureFiltering`, `gap_fTextureLODBias` | gering–mittel, **in MP nicht erzwungen** | Reduzieren Geometrie-/Texturaufwand. Nachrangig gegenüber M1/M2. |
| `cli_bPrediction` | bereits aus | Default `FALSE`, `cli_bAutoAdjustSettings = FALSE` `[B110: Network.cpp:122/124]`. **Nicht aktivieren** – Prediction kostet CPU und ist für Bots nicht nötig. |
| CPU-Affinität (`taskset`), `nice` | gering, aber nützlich zur Entkopplung | Clients auf getrennte Kerne pinnern verhindert gegenseitiges Verdrängen des 20-Hz-Timers. Auf 2 vCPU begrenzt wirksam. |
| Diagnoseausgaben reduzieren (`bot_iLogEvery`, `bot_bDiagnostics`) | gering–mittel | `BotLog` → `CPutString` → Konsolenpuffer + Logdatei mit `fflush` pro Zeile `[B110: Console.cpp:220-221]`. Im Dauerbetrieb `bot_iLogEvery` hoch setzen. |

**Ausdrücklich kosmetisch / wirkungslos:** verstecktes Fenster, „unsichtbar“ setzen, reines Wegschieben aus dem Sichtbereich, `gfx_bRenderWorld=0` in Multiplayer.

---

## M6 – Server-Seite (DedicatedServer.exe) mitnehmen (Priorität: P2)

- `ded_iMaxFPS` von **100** auf **25–30** senken (`poc/scripts/dedicated-config/init.ini` setzt derzeit 100). Der Server hat keine Render-Schleife; die Drossel betrifft nur `MainLoop()` (Stromverarbeitung, Broadcast, GameAgent, Client-Handlers). Erwartung `[H]`: spürbare Reduktion der gemessenen 8–16 %.
- `ser_bReportSyncBad = 1` beibehalten (bereits Default `[B110: Network.cpp:97]`); **`ser_iKickOnSyncBad` nicht verändern** – entspricht `AGENTS.md`.

---

# Teil 6 – Performance-Prognose und Benchmark-Plan

## 6.1 Ehrliche Ausgangslage

Es liegen **keine** isolierten Messungen vor, die die Last auf Rendering / Simulation / KI aufteilen. Alle folgenden Zahlen sind damit **Erwartungswerte mit expliziter Unsicherheit**, abgeleitet aus:

1. Eurer Messung: Dedicated Server (volle Welt-Simulation, 8 Spieler, kein Rendering) = **8–16 %** eines Kerns `[M]`
2. Eurer Messung: Bot-Client mit 4 Bots = **70–87 %** `[M]`
3. Quellcode-Struktur (Timer ist unabhängig von der Framerate) `[B110]`

## 6.2 Abgeleitete Untergrenze

Ein Bot-Client muss dieselbe Welt simulieren wie der Server (deterministischer Lockstep). Therefore:

```
Simulations-Untergrenze pro Client-Prozess  ≈  Server-Last        ≈  8–16 %
+ 4 Spieler-Entitäten + BotDriver + Wine-Overhead                  ≈  +5–15 %
---------------------------------------------------------------------------
Theoretische Untergrenze für 4 Bots (headless, ohne Rendering)      ≈ 15–30 %  [H]
```

Daraus folgt die **Einspargrenze** von M1/M2: von 70–87 % auf bestenfalls ~15–30 %. Das ist eine Spanne, **kein** Messwert.

## 6.3 Prognose-Tabelle (ausdrücklich: Prognose, nicht Messung)

| Ziel | Heute (A1) | Nach M1+M2 (A2) | Nach M3 (A3) | Urteil |
|---|---|---|---|---|
| **8 Bots / 2 vCPU** | läuft, zeitweise > 90 % `[M]` | **sehr wahrscheinlich mit Reserve** | **wahrscheinlich mit großer Reserve** | realistisch |
| **16 Bots / 2 vCPU** | nein | möglich, **messpflichtig** | **plausibel** | nach M3 realistisch |
| **24 Bots / 2 vCPU** | nein | unwahrscheinlich | grenzwertig; erfordert M4 + RAM-Prüfung | **ohne Messung nicht zusagen** |
| **32 Bots / 4 vCPU** | nein | möglich | **plausibel** (≈ 8 Prozesse) | realistisch nach M3 |
| **64 Bots / 8 vCPU** | nein | möglich | **plausibel** (≈ 16 Prozesse) | realistisch nach M3, RAM beachten |

## 6.4 Zusätzliche Dimensionen, die die Prognose begrenzen

| Dimension | Bewertung |
|---|---|
| **RAM** | Bei ~250–400 MB pro Wine-Prozess `[H, O5]` sind 16 Prozesse ≈ 4–6 GB ⇒ **4 GB werden ab ~12–16 Bots zum Limit**. Vor Skalierung RSS pro Prozess messen; RAM-Aufstockung einplanen. |
| **Gegner-/Entity-Anzahl** | In Deathmatch gering; in Coop mit vielen Monstern steigen Simulationskosten **auf Server und jedem Client** gleichermaßen. Prognosen gelten nur für die gemessene Map (`DM_LittleTrouble`). |
| **vCPU-Schwankung (Hetzner shared)** | Planung mit **20–30 % Reserve**; keine Auslastung > 70 % Dauerlast einplanen. |
| **Netzwerklast** | Loopback über die öffentliche IP ⇒ zusätzliche Socket-/`iptables`-Kosten pro Paket. Ein Join über `127.0.0.1` (lokaler Server) wäre günstiger, falls derselbe Host. |
| **Reserve für reale Spieler** | Mindestens 1–2 vCPU-Äquivalente bzw. 20 % Headroom reservieren. |
| **Parallele Spielserver** | Jeder weitere Server multipliciert die Server-Last; Bot-Clients sind den Servern frei zuordenbar (Join-Adresse). |

## 6.5 Benchmark-Plan

**Grundregeln**
- Produktiv laufende Prozesse **nicht** ohne Freigabe beenden oder verändern.
- Jede Stufe mit **uninstrumentierter Kontrollprobe**.
- Identische Map (`DM_LittleTrouble`), identische Spielerzahl, identische Bot-INIs, identische Tageszeit-Fenster (vCPU-Schwankung).
- Jede Messung ≥ 15 Minuten, Freigabeläufe ≥ 60 Minuten.
- Vor jedem Start `tools/Test-TSEExternalVanillaPreflight.ps1`.

**Metriken pro Lauf**

| Metrik | Erhebung |
|---|---|
| CPU pro Prozess | `pidstat -u -p <pid> 5` (User + System getrennt; `top`-Werte sind ungenau) |
| CPU pro Prozess inkl. Threads | `pidstat -tu -p <pid> 5` |
| Gesamtsystem | `vmstat 5`, `mpstat -P ALL 5` |
| RAM | `pidstat -r -p <pid> 5`, RSS + PSS |
| Frame-Rate / Loop-Rate | eigener Zähler in `GameMainLoop` (nur Test-DLL) |
| Tick-Trefferquote | Zähler `BotDriver`-Ticks vs. erwartete 20/s |
| Timer-Jitter | `QueryPerformanceCounter` um `CTimer`-Handler (nur Test-DLL) |
| Sync | Serverlog: `SYNCBAD`, `SYNCOK`, `SYNCLATE`, `SYNCEARLY`, Disconnects – Auswertung mit `tools/analyze_sync_log.py` |
| Netzwerk | `ss -u -a -p`, Paketzähler (`iptables -L -n -v -x` oder `nstat`) |
| Join-Tests | Unveränderter Retail-1.07-Vanilla-Client: Join, Sichtbarkeit, Scoreboard, Kick/Rejoin |
| X-/Wine-Last | CPU von `Xvfb`, `wineserver`, `wine-preloader` getrennt erfassen |

**Matrix**

| # | Konfiguration | Zweck |
|---|---|---|
| B0 | Ist-Zustand: 2 Clients × 4 Bots, `sam_iMaxFPSActive` **wie produktiv** | **Baseline** (Wert vorher dokumentieren!) |
| B1 | B0 mit `sam_iMaxFPSActive = 60` | Isoliert Default-500-Effekt |
| B2 | B0 mit `sam_iMaxFPSActive = 30 / 25 / 20 / 10` | FPS-Kurve, Aktionsrate gegenprüfen |
| B3 | B0 mit `LP_NUM_THREADS = 1` | llvmpipe-Thread-Einfluss |
| B4 | **M1**: `bot_bNullRender = 1` bei 25 Hz | Render-Anteil isolieren |
| B5 | M1 + **M2** (`bot_iMainLoopHz`) | Kombinierter Effekt |
| B6 | M1+M2 + **M4** (Ray-Cache, kurze Locks) | KI-/Lock-Anteil |
| B7 | **M3**: `DedicatedServer.exe` Headless-Host, 4 Bots | Headless-Vergleich |
| B8 | M3 skaliert: 8 / 12 / 16 Bots | Skalierungskurve + RAM |
| B9 | Kontrolle: `bot_bEnabled=0`, Vanilla-Observer statt Bots | Referenz „echter Client“ |
| B10 | Freigabelauf der besten Konfiguration, **≥ 60 Minuten**, mit Vanilla-Observer | Abnahme |

**Kritische Gegenprüfungen (dürfen nicht entfallen)**
1. **Aktionsrate:** In B2/B5 muss die `[BotDriver]`-Tick-Frequenz weiterhin 20/s betragen. Fällt sie, ist die Konfiguration **verworfen**.
2. **Sync:** `SYNCBAD`-Zähler muss in jedem Lauf 0 bleiben; `SYNCLATE`/`SYNCEARLY` dokumentieren.
3. **Vanilla-Join:** In jeder Stufe unveränderter Retail-1.07-Client.
4. **Cleanup:** Nach jedem Test Serverpopulation per UDP prüfen; `CloseMainWindow()` vor `Stop-Process -Force` (siehe Bericht vom 17.10.).

---

# Teil 7 – Roadmap

## Phase A – Sofort (kein Code, nur Konfiguration; ~1 Tag)

| # | Maßnahme | Aufwand | Risiko | Erwartung |
|---|---|---|---|---|
| A1 | `sam_iMaxFPSActive/Inactive` im Hetzner-Profil prüfen und auf 25 setzen; Existenz der Symbole in Retail-1.07-EXE verifizieren (`[O2]`, `[O1]`) | 1 h | minimal | hoch |
| A2 | `ded_iMaxFPS` 100 → 25 | 15 min | minimal | gering–mittel |
| A3 | `LP_NUM_THREADS=1` A/B-Messung | 1 h | minimal | mittel |
| A4 | Xvfb auf `320x240x16` verkleinern, Wine-Audio auf `null`, `WINEDEBUG=-all` | 1 h | minimal | gering |
| A5 | `bot_iLogEvery` erhöhen, `bot_bDiagnostics=0` im Dauerbetrieb | 15 min | minimal | gering |
| A6 | **Messbaseline B0–B3** auf isoliertem Testserver | 3–4 h | – | – |

**Gate A:** Baseline dokumentiert; `SYNCBAD = 0`; Aktionsrate 20/s nachgewiesen.

## Phase B – Null-Renderer + Loop-Drossel (~2–3 Tage)

| # | Maßnahme |
|---|---|
| B1 | **M1** implementieren (`bot_bNullRender`), Patch-0007-Lock hinter den Bot-Pfad schieben |
| B2 | **M2b** implementieren (`bot_iMainLoopHz`) – unabhängig von EXE-Symbolen |
| B3 | Neuer DLL-Kandidat eigene SHA256; **bestehende `61DC…`-DLL unangetastet lassen** |
| B4 | Isolierter Testserver, Messreihe B4–B6, Kontrollprobe mit `bot_bNullRender=0` |
| B5 | 60-Minuten-Lauf mit Vanilla-Observer |

**Gate B:** CPU pro 4-Bot-Client dokumentiert; keine Crashs; `SYNCBAD = 0`; Vanilla-Join bestanden; Aktionsrate 20/s.

## Phase C – Headless-Host (~1–2 Wochen)

| # | Maßnahme |
|---|---|
| C1 | Statische Vorprüfung von Retail-`DedicatedServer.exe` (Symbole, `_bDedicatedServer`, `StartGame`-Pfad) |
| C2 | **M3** implementieren (`bot_bHeadlessJoin`) |
| C3 | Eigene `.gms` + 4 Profile; `Scripts/Dedicated/<cfg>/` anlegen |
| C4 | Isolierter Join-Test: 1 Bot → 4 Bots |
| C5 | Messreihe B7–B8 (Skalierung, RAM) |
| C6 | Xvfb-Bedarf dokumentieren (Ziel: entfällt) |

**Gate C:** 4-Bot-Headless-Host stabil ≥ 60 Min; CPU und RSS dokumentiert; kein X-Server-Kontakt.

## Phase D – KI-/Lock-Optimierung (~3–5 Tage, nach Phase B)

| # | Maßnahme |
|---|---|
| D1 | **M4a**: LOS-Cache, Distanz-Gate, Rays reduzieren (wirkt auch heute) |
| D2 | **M4b**: Lock-Verkürzung – **erst nach M1**, wegen `BSCF_RAYTESTED`-Race |
| D3 | Tick-Dauer instrumentieren, Hotspot-Liste |
| D4 | Konsolenausgabe pufferreduziert (`CPutString` mit `fflush` pro Zeile) |

## Phase E – Skalierung & Betrieb (laufend)

| # | Maßnahme |
|---|---|
| E1 | RAM-Profil pro Prozess; ggf. Instanz auf 8 GB heben |
| E2 | Supervisor/Population Manager an die neuen Prozesskosten anpassen |
| E3 | Mehrere Server pro Host: Join-Adressen, Port-Trennung, CPU-Budget je Server |
| E4 | Dauer-Soaks: 6 h / 24 h je Konfiguration |
| E5 | Public-Browser-/333networks-Nachweis separat führen |

## Verworfen / zurückgestellt

| Architektur | Entscheidung |
|---|---|
| A5 Protokollkompatible Bot-Clients | **Verwerfen** – erfordert vollständige deterministische Engine-Nachbildung inkl. State-Delta, CRC-Gather und Sync-CRC |
| A4 Server-integrierte Bots | **Zurückstellen** – hoher RE-Aufwand, A3 erreicht den Großteil des Nutzens ohne `Engine.dll`-Eingriff |
| A6 Hybrid (>4 lokale Spieler je Prozess) | **Nicht priorisieren** – `NET_MAXLOCALPLAYERS = 4` ist engineweit verankert; A3 skaliert kostengünstiger |
| Headless-Patch in `SeriousSam.exe`/`Engine.dll` | **Verwerfen** – A3 stellt den headless Pfad Retail-seitig bereit |

---

# Teil 8 – Abschließende Empfehlung

> **Welche Architektur würdest du als verantwortlicher Engine-Entwickler wählen?**

## Antwort: **A3 – `DedicatedServer.exe` als Headless-Bot-Host, aufbauend auf A2 (Null-Renderer).**

Begründung in der Reihenfolge des Gewichts:

1. **Es ist der einzige Retail-Pfad, der bewiesen ohne Grafik läuft.** `[B110: Adapter.cpp:77/236/307, Console.cpp:229]`. Kein Xvfb, kein GL-Kontext, kein llvmpipe, keine Fenster, kein Audio, kein Input-Prescan. Das ist keine Hoffnung, sondern der Zustand, in dem euer Dedicated Server heute läuft.

2. **Es erfordert kein Reverse Engineering und keinen Binary-Patch.** `CGame::NewGame()` ist virtuell und liegt in `GameMP.dll` `[B110: Game.h:267]`. Euer gesamter `BotDriver`, Reconnect-Handling (`CGame::GameMainLoop` → `BotDriver_HandleReconnect`, `[Projekt: Game.cpp:2662]`) und die `CPlayerSource::SetAction()`-Injektion bleiben unverändert.

3. **Vanilla-Kompatibilität bleibt strukturell erhalten.** Es ist ein echter Join: `JoinSession_t()`, State-Delta, CRC-Gather, `MSG_SEQ_ALLACTIONS`, Sync-Check – derselbe Pfad, den heute eure `SeriousSam.exe`-Clients nutzen `[B110: Network.cpp:1230-1290]`. Der Server sieht einen normalen Client.

4. **Es löst das CPU-Problem und das Timing-Problem gemeinsam.** Ohne Render-Schleife gibt es keine `tm_csHooks`-Blockade des 20-Hz-Timers mehr (Patch 0007 entfällt), keine `BSCF_RAYTESTED`-Race mit dem Renderer (Patch 0006/0007 entfällt) und keine Konkurrenz um `ga_csNetwork` durch 500 Hz `MainLoop()`.

5. **Die Skalierungsziele werden damit plausibel.** Bei ~15–25 % Kernlast pro 4-Bot-Prozess sind 16 Bots auf 2 vCPU und 32–64 Bots auf 4–8 vCPU realistisch – **vorbehaltlich der Messung** und vorbehaltlich des RAMs.

## Der Weg dorthin – in dieser Reihenfolge

```
Heute        → A1/A2 Konfiguration + Baseline (Tag 1)
             → M1 Null-Renderer + M2 Loop-Drossel (Tag 2-3)   ⇒ sofortiger, großer CPU-Gewinn
             → M3 DedicatedServer.exe als Headless-Host (Woche 1-2)
             → M4 KI-/Lock-Optimierung (Woche 2-3)
             → Skalierungsmessung + Soaks (laufend)
```

**M1/M2 sind keine Zwischenlösung, sondern bleiben nützlich:** dieselbe `GameMP.dll` funktioniert in beiden Hosts (`SeriousSam.exe` und `DedicatedServer.exe`). `bot_bNullRender` ist im Headless-Host wirkungslos (kein Aufruf) und schadet nicht; `bot_iMainLoopHz` wirkt in beiden.

## Wichtigste Warnungen

1. **Die qualifizierte DLL `61DC27E0…` bleibt unangetastet.** Jede neue DLL ist ein neuer Kandidat mit eigener vollständiger nativer Abnahme (`AGENTS.md`, `README.md`).
2. **`ser_iKickOnSyncBad` nicht verändern.** Sync-Fehler werden beobachtet, nicht maskiert.
3. **Kein FPS-Limit ohne Aktionsraten-Gegenprüfung freigeben.** Der Quellcode sagt, die Aktionsrate ist unabhängig – die Messung muss es bestätigen.
4. **M4b (Lock-Verkürzung) erst nach M1.** Sonst wird die `BSCF_RAYTESTED`-Race wieder geöffnet.
5. **Bei >12–16 Bots wird RAM zum Limit**, nicht CPU.
6. **Alle `[B110]`-Aussagen sind an Retail 1.07 gegenzuprüfen.** Diese Analyse basiert auf SE1-1.10-Quellcode und euren Binärbefunden – nicht auf einer Retail-1.07-Laufzeitmessung.

---

# Anhang A – Belegverzeichnis

Alle SE1-1.10-Fundstellen (lokal geprüfter Clone von `Croteam-official/Serious-Engine`):

| Behauptung | Fundstelle |
|---|---|
| Tick-Quantum 20 Hz | `Sources/Engine/Base/Timer.cpp:54` |
| Multimedia-Timer 50 ms periodisch | `Sources/Engine/Base/Timer.cpp:253-258` |
| Timer-Handler-Schleife; `tm_csHooks` zuerst | `Sources/Engine/Base/Timer.cpp:92-124` |
| Handler-Registrierung | `Sources/Engine/Base/Timer.cpp:301-312` |
| Netzwerk-Timer-Handler | `Sources/Engine/Network/Network.cpp:899-905, 2030-2083` |
| `SendActionsToServer()` im Timer | `Sources/Engine/Network/Network.cpp:2012-2025, 2072-2076` |
| `net_iExactTimer` Default 2 | `Sources/Engine/Network/Network.cpp:149, 2046-2064` |
| Game-Timer-Handler | `Sources/GameMP/Game.cpp:915` |
| `GameHandleTimer` → BotDriver | Projekt `poc/release/gamemp/Game.cpp:751-754` |
| `CPlayerSource::SetAction()` | `Sources/Engine/Network/PlayerSource.cpp:152-161` |
| `WriteActionPacket()` | `Sources/Engine/Network/PlayerSource.cpp:172-246` |
| `MainLoop()` hält `ga_csNetwork`; läuft pro Frame | `Sources/Engine/Network/Network.cpp:1819-1821` |
| `ProcessGameStream()` arbeitet alle Sequenzen ab | `Sources/Engine/Network/SessionState.cpp:1089-1200` |
| Prediction aus (Defaults) | `Sources/Engine/Network/Network.cpp:122, 124` |
| Sync-CRC-Inhalt | `Sources/Engine/Network/SessionState.cpp:766-830` |
| Sync-Check-Erzeugung, 1 Hz | `Sources/Engine/Network/SessionState.cpp:1880-1913`; `Network.cpp:106` (`ser_tmSyncCheckFrequency = 1.0`) |
| Server-Sync-Handler, Kick bei 10 | `Sources/Engine/Network/Server.cpp:1381-1455`; `Network.cpp:101` |
| `ser_bKickOnSyncLate` / „No valid SYNCCHECK“ | `Sources/Engine/Network/Server.cpp:1127-1135` |
| `DoGame()`; Render-Block; `IsIconic`; `SwapBuffers` | `Sources/SeriousSam/SeriousSam.cpp:666, 707, 712, 754` |
| `LimitFrameRate()`; Defaults 500/10; SSC_DEDICATED-Clamp | `Sources/SeriousSam/SeriousSam.cpp:47-48, 240-259` |
| `sam_iScreenSizeI/J` persistent | `Sources/SeriousSam/SeriousSam.cpp:55-56, 440-441` |
| `GameRedrawView()` virtuell + Inhalt | `Sources/GameMP/Game.h:244`; `Sources/GameMP/Game.cpp:2092-2340` |
| Render-Prescan unter `tm_csHooks` (Original, kurz) | `Sources/GameMP/Game.cpp:2175-2177` |
| `SE_PretouchIfNeeded()` nur bei Bedarf | `Sources/Engine/Engine.cpp:611-616` |
| Anti-Cheat-Clamps in `RenderScene()` | `Sources/Engine/Graphics/DrawPort_RenderScene.cpp:721-733` |
| `BSCF_RAYTESTED = 1<<6`, Nutzung | `Sources/Engine/Brushes/Brush.h:468`; `Sources/Engine/World/WorldRayCasting.cpp:127, 580-583` |
| Renderer schreibt Sektor-Flags (RMW) | `Sources/Engine/Rendering/RendASER.cpp:344` (`BSCF_INVISIBLE`) |
| `DedicatedServer`: `_bDedicatedServer = TRUE` | `Sources/DedicatedServer/DedicatedServer.cpp:184` |
| `DedicatedServer`: `ded_iMaxFPS` Default 100 | `Sources/DedicatedServer/DedicatedServer.cpp:32, 233` |
| `DedicatedServer`: `DoGame()` ohne Rendering | `Sources/DedicatedServer/DedicatedServer.cpp:345-383` |
| `DedicatedServer`: `StartGame()` → `NewGame()` | `Sources/DedicatedServer/DedicatedServer.cpp:159-172` |
| Adapter-Init bei Dedicated übersprungen | `Sources/Engine/Graphics/Adapter.cpp:77, 236, 307` |
| Konsole bei Dedicated via `printf` | `Sources/Engine/Base/Console.cpp:229-231` |
| `NET_MAXLOCALPLAYERS = 4`, `NET_MAXGAMEPLAYERS = 16` | `Sources/Engine/Network/Network.h:30-31` |
| Projekt: BotDriver hält `ga_csNetwork` | `poc/release/gamemp/BotDriver.cpp` (`CTSingleLock slBotWorld(&_pNetwork->ga_csNetwork, TRUE)`) |
| Projekt: Patch 0007 (`tm_csHooks` in `GameRedrawView`) | `poc/patch/0007-gamemp-ai-render-lock.patch`; `poc/release/gamemp/Game.cpp:2091-2097` |
| Projekt: Patch 0006 (Ray unter Netzwerk-Lock) | `poc/patch/0006-gamemp-ai-world-lock.patch` |
| Projekt: Fleet setzt `sam_iMaxFPSActive = 60` | `poc/scripts/LocalBotReleaseCore.ps1:30` |
| Projekt: `ded_iMaxFPS = 100` im Dedicated-Config | `poc/scripts/dedicated-config/init.ini` |
| `[BR07]` Sync-Kick-Mechanismus, Grenzwert 10 | `docs/reports/2026-10-17-retail107-sync-check-investigation.md` |

# Anhang B – Vor jeder Implementierung zu klären

| # | Offene Frage | Klärweg |
|---|---|---|
| O1 | Produktive Werte von `sam_iMaxFPSActive/Inactive`, `sam_iScreenSizeI/J`, `sam_bPauseOnMinimize` im Hetzner-lowrender-Profil | `Scripts/PersistentSymbols.ini` der Bot-Clients lesen (Backup vorher) |
| O2 | Existenz von `sam_iMaxFPSActive` in Retail-1.07-`SeriousSam.exe` | `strings`/Ghidra auf der EXE; ersatzweise M2b nutzen |
| O3 | vtable-Reihenfolge von `CGame` in Retail 1.07 | Praktisch belegt durch laufende `61DC…`-DLL; statisch mit Ghidra auf `GameMP.dll` gegenprüfen |
| O4 | Stabilität ohne Rendering (Model/Texture-Prepare-Abhängigkeiten) | 60-Min-Lauf Phase B |
| O5 | RSS pro Client-Prozess | `pidstat -r` in der Baseline |
| O6 | `IsIconic()` unter Wine/Xvfb | Versuch mit leichtem WM; sonst M1 |
| O7 | Exakter Retail-Name des Netzwerk-Providers für „TCP/IP Client“ | Aus funktionierendem Join-Log oder EXE-Strings entnehmen (für M3) |
| O8 | `StartNewMode()`-Clamps für minimale `sam_iScreenSizeI/J` | `Sources/Engine/Graphics/GfxLibrary.cpp` / `ViewPort.cpp` prüfen, falls Auflösungssenkung genutzt wird |
