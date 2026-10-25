# Intelligente Bot-Navigation 2.0 – Offline-Prototyp, Messergebnisse und Integrationsplan

**Datum:** 25.10.2026
**Auftrag:** ALPHA-GAMING-Entwicklungsauftrag „Intelligente Bot-Navigation 2.0" (Phasen 1–4)
**Rolle:** unabhängiger Senior-C++-Entwickler (Game-AI / Navigation / A*)
**Branch:** `arena/8317e1d6-serioussam-tse-bot-servermods` (PR #54, eigenständig, kein Auto-Merge)
**Base:** `main` @ `107d28a276c4fe4428cc3c8bf5bbd876e1a85351`; Vorgänger-Commit auf dem Branch: `2241cc5` (CecilBotMod-Transferanalyse, `docs/audits/2026-10-25-cecilbotmod-ki-transferanalyse.md`)
**Cecil-Referenz:** `github.com/DreamyCecil/CecilBotMod` @ `953b477` (nur Algorithmen-Ideen, GPLv2 respektiert, kein Quelltext kopiert)
**Schreibbereich:** ausschließlich `poc/navigation-lab/**` und `docs/research/**`; `poc/botcore/**` read-only includiert, unverändert.

---

## 1. Zusammenfassung

Der Prototyp **`poc/navigation-lab/`** ist fertig, offline getestet und benchmarkt:

- **4 Testsuiten, 4746 bestandene Assertions, 0 Fehler** (`make test`), davon 307 Checks im Seam-Test direkt gegen die existierenden botcore-Header (read-only).
- **Gemessene** Tick-Kosten (steady_clock, keine Schätzwerte): **0,35–0,87 µs pro Tick und Agent**; 16 Bots auf einer 1024-Node-Karte kosten zusammen **13,9 µs/Tick = 0,028 % eines CPU-Kerns** bei 20 Hz.
- **Null Heap-Allokationen** — statisch bewiesen (`make check-noalloc`) und zur Laufzeit erzwungen (`operator new`-Trap im Benchmark bricht bei jeder Allokation ab; Ergebnis: 0 Allokationen).
- **Determinismus** bitgleich getestet (gleiche Seeds → gleiche Positionen/Telemetrie über zwei unabhängige Läufe, 4 Bots parallel).
- Header kompatibel zu **C++11/14/17** (`make compat`), `g++ -Wall -Wextra`-warnungsfrei.
- Integrationsnähte zu botcore (Waypoint-Dateiformat, Persönlichkeiten, `BotCommand`-Merge) sind im Seam-Test **ausgeführt bewiesen**, nicht nur behauptet.

Größte während der Entwicklung gefundene und behobene Fehlerklasse: **Steuerungs-Limit-Cycles** (Orbit um Wegpunkte bei Turn-Rate > Ankunftsradius, Routen-Komplettverbrauch bei Gegenkurs, Replan-Oszillation bei unerreichbaren Zielen). Alle drei sind durch Tests dauerhaft abgesichert (Abschnitt 5).

**Kein Retail-Anspruch:** Alles Folgende ist Offline-Nachweis. Native Abnahme (BotDriver-Integration, SYNCBAD-Beobachtung) steht aus und ist bewusst als eigener, gatebarer Schritt geplant (Abschnitte 7–9).

---

## 2. Befund: vorhandene Navigation (Phase 1)

Aus dem Read-only-Audit der botcore-Header (`poc/botcore/botcore_ai.h`, `bot_navigation.h`, `bot_human.h`) und der CecilBotMod-Transferanalyse (`2241cc5`):

| Komponente (botcore) | Befund | Konsequenz für Navigation 2.0 |
|---|---|---|
| `WaypointGraph` (`botcore_ai.h:147`) | 256 Nodes, 8 Kanten/Node, BFS-`NextHop` (kürzeste **Hop**-Anzahl, keine Kosten), keine Kanten-Flags, kein Blocking zur Laufzeit, keine Alternativenrouten | Graph bleibt als Dateiformat-/Lade-Naht erhalten; Routing übernimmt der budgetierte A* mit Kosten, Flags und Teilrouten |
| `StuckDetector` (`botcore_ai.h:265`) | Fensterbasierte Fortschrittsprüfung; Semantik gut | 1:1-Semantik in `NavAgent` nachgebildet (`stuck_window`, `stuck_min_dist`) und mit Avoid-Bias + Sofort-Replan kombiniert |
| `bot_navigation.h` | Phasenmodell (Approach/Reposition/…) ohne durchgehende Routen-Verwaltung | FSM Patrol/Pursue/Reposition/Scan übernimmt die Phasen mit explizitem Zustands- und Telemetrie-Vertrag |
| `BotCommand` (`bot_human.h:47`) | `target`, `target_visible`, `yaw_delta_deg`, `forward`, … | Merge-Regel: Combat führt bei Ziel; Navigation füllt sonst (im Seam-Test ausgeführt) |
| Human-KI / `PersonalityParams` (`bot_profile.h:99`) | 6 Standard-Personas (Aggression, Caution, …) | `NavPersonalityFromTraits()`-Bridge; alle 6 Personas im Seam-Test gegen Nav-Invarianten geprüft |
| CecilBotMod (`Navmesh.cpp`) | A* mit Allokation pro Aufruf + lineare Open-List (O(n²)); serverseitige Bot-Entities + Netzwerk-Detours | **Nicht** portierbar (GPLv2 + Architektur); heap-freier A* mit binärem Heap + Budget stattdessen neu gebaut |

Historische Sync-Problematik: „Too many bad syncs" ist real und analysiert — siehe Abschnitt 7.

---

## 3. Architektur des Prototyps

```
nav_graph.h   Waypoint-Graph (statisch: 1024 Nodes, 12 Kanten/Node, 173 KB)
              Flags: Kanten blocked/jump/danger; Nodes important/dead-end/spawn
              Scripts-kompatibler Parser („node x y z", „edge a b", „block a b")
nav_astar.h   A*: binärer Heap, Generation-Stamps (keine Array-Resets), Budget
              (Default 256 Expansionen), deterministisches Tie-Break,
              per-Edge-Kostenvarianz (Seed) für Routenvielfalt;
              Teilrouten: Budget→tiefster Node, unerreichbar→zielnächster Node
nav_agent.h   FSM: Patrol (besuchsgewichtetes Ziel-Scoring) / Pursue (grob;
              Feinbewegung bleibt beim Combat-Layer) / Reposition (Route zur
              letzten bekannten Zielposition) / Scan; Stuck-Detektor,
              Teleport-Guard (>8 m/Tick), Repath-Cooldown, Turn-in-place >60°,
              Segmentprojektions-Vorrücken, Avoid-Bias nach Stuck (5 s)
nav_maps.h    Synthetische Karten (Korridor/Grid+Wände/Ring/Dead-Ends/
              disjunkt/Spirale) — ausschließlich für öffentliche Tests
```

Designentscheidungen mit direktem Realwelt-Bezug:

1. **Budget statt Vollsuche:** Jede Suche ist hart auf `max_expand` begrenzt (CPU-Deckel pro Tick). Bei Budget-Ende liefert A* die Route zum **tiefsten expandierten Node** — der Bot läuft den erkundeten Gang weiter und plant vom neuen Standpunkt neu (in `TestBudgetedSearchMakesProgress` auf der 256-Node-Spirale bewiesen: Fortschritt >5 m, `expanded_last_search ≤ 256` in jedem Tick).
2. **Routenvielfalt deterministisch:** Per-Edge-Kosten-Jitter ±12 % (Hash aus Kanten-Indices + Bot-Seed) — gleiche Seeds liefern bitgleich dieselbe Route, verschiedene Seeds nachweislich verschiedene Ring-Seiten (`test_nav_astar.cpp`).
3. **Segmentprojektions-Vorrücken:** Ein Wegpunkt gilt als passiert, wenn die Projektion des Bots auf das Segment `prev→cur` über `cur` hinausliegt (t>1) **oder** der Radius trifft. Facing-basierte Regeln scheitern doppelt (Gegenkurs-Routen, Achs-Gitter) — beide Fehlmodi sind als Regressionstests fixiert.
4. **Turn-in-place über 60°:** Verhindert Bogenlaufen bei großen Heading-Fehlern (Drift aus Korridoren + Orbit-Einfang, wenn Turn-Radius > Ankunftsradius).
5. **Unerreichbare Ziele memoisiert:** Nach `kUnreachable` keine Re-Search-Sturm mehr; der Bot fährt die Teilroute zum zielnächsten Punkt und scannt dort (Test: exakt **1** Suche in 400 Ticks).

---

## 4. Reproduzierbare Tests (Phase 3)

`cd poc/navigation-lab && make test` (g++ -std=c++17 -O2 -Wall -Wextra, keine Drittabhängigkeiten):

| Suite | Checks | Abdeckung (Kartendaten 100 % synthetisch) |
|---|---|---|
| `test_nav_graph` | **1084** | Basics, NearestNode-Grenzen, Blocking/Toggling, Dead-End-Flagging, Parser (inkl. Kommentar-/Fehlerzeilen), Kapazitätsgrenzen |
| `test_nav_astar` | **83** | erreichbar/unerreichbar (disjunkte Karten), blockierte Pässe + Alternativroute, Ring/Zyklen + Alternativrouten über Seeds, Budget-Grenze (Spirale, ≤10 Expansionen), Zielwechsel-Wiederverwendung, Determinismus über Instanzen |
| `test_nav_agent` | **3272** | Ende-zu-Ende mit kinematischem Simulator (20 Hz, 10 m/s): Patrol-Abdeckung, unerreichbar→Scan, Pursue-Grobsteuerung, Zielwechsel mid-route, Stuck→Recovery→Ankunft, Teleport-Guard, Budget-Fortschritt, Persönlichkeitswirkung auf Zielwahl, **4-Bot-Determinismus**, Persona-Bridge, toter Agent |
| `test_nav_seam` | **307** | botcore read-only: identische Waypoint-Datei → `WaypointGraph`+`NavGraph`, **144/144 Reachability-Paare äquivalent** (BFS vs. A*), alle **6 Standard-Personas** → gültige `NavPersonality` + lebende FSM, `BotCommand`/`NavCommand`-Merge deterministisch |

Zusätzliche Gates: `make check-noalloc` (Heap-Primitive in Headern → Build-Fehler; Kommentare vorgängig vom Präprozessor entfernt, damit Prosa nicht triggt) und `make compat` (C++11/14/17).

---

## 5. Gemessene Benchmarks (Phase 3, `make bench`)

**Methode:** `std::chrono::steady_clock` um jeden `NavAgent::Step` bzw. um die Tick-Schleife; 1200 Ticks (60 s Sim-Zeit) pro Konfiguration; Workload = Patrol + deterministische Reposition-Phasen (Ziel alle 300 Ticks für 100 Ticks „zuletzt bekannt"); kinematische Simulation 10 m/s. Worst-Case-Suche separat: Ecke-zu-Ecke, 1000–2000 Iterationen. **Host:** 2× Intel(R) Xeon(R) @ 2,60 GHz (Sandbox). Alle Werte unten sind Ausgabe des Laufs vom 25.10.2026, keine Schätzung.

### Tick-Kosten (steady state)

| Karte | Bots | µs/Tick/Agent | µs/Tick (alle) | % Kern @20 Hz | worst Step | Suchen | Exp./Suche |
|---|---|---|---|---|---|---|---|
| grid16 (256 Nodes) | 1 | 0,510 | 0,510 | 0,0010 % | 133,1 µs* | 13 | 34,4 |
| grid16 | 4 | 0,345 | 1,381 | 0,0028 % | 30,5 µs | 48 | 46,9 |
| grid16 | 8 | 0,373 | 2,986 | 0,0060 % | 88,1 µs | 94 | 50,0 |
| grid16 | 16 | 0,366 | 5,855 | 0,0117 % | 72,4 µs | 186 | 54,9 |
| grid32 (1024 Nodes) | 1 | 0,856 | 0,856 | 0,0017 % | 39,1 µs | 11 | 102,1 |
| grid32 | 4 | 0,873 | 3,490 | 0,0070 % | 49,9 µs | 39 | 115,9 |
| grid32 | 8 | 0,870 | 6,961 | 0,0139 % | 80,8 µs | 73 | 135,3 |
| grid32 | 16 | **0,866** | **13,858** | **0,0277 %** | 67,0 µs | 143 | 141,1 |

\* First-Touch-Rauschen (Page Faults) im 1-Bot-Lauf; die Such-Mikromessung (unten) zeigt die wahre Worst-Case-Größenordnung.

**Einordnung:** Selbst 16 Bots auf der größten Karte verbrauchen **<0,03 %** eines Kerns im 20-Hz-Budget (50 ms/Tick). Der vorhandene botcore-Bench liegt bei 0,44–0,51 µs/Tick für die Human-KI — die Navigation 2.0 bleibt in derselben Größenordnung und ist additiv unkritisch.

### Worst-Case einzelne A*-Suche (Ecke zu Ecke)

| Karte | Budget | mean | max | gefunden | Expansionen |
|---|---|---|---|---|---|
| grid16 (256) | 256 | 8,30 µs | 45,9 µs | 2000/2000 | 227/Suche |
| grid16 (256) | 1024 | 8,00 µs | 30,6 µs | 2000/2000 | 227/Suche |
| grid32 (1024) | 256 | 8,27 µs | 30,8 µs | **0/1000** | 256/Suche (Budget) |
| grid32 (1024) | 1024 | 72,43 µs | 136,2 µs | 1000/1000 | 963/Suche |

**Ehrlicher Befund:** Auf einer vollen 1024-Node-Karte erreicht Budget 256 die Diagonale **nicht** — der Agent kompensiert per Teilroute + inkrementellem Replan (bewiesen im Spiral-Test; steady-state-Expansionen bleiben ≤141/Suche). Reale Waypoint-Karten der botcore-Generation haben ≤256 Nodes (`WaypointGraph::kMaxNodes`), liegen also komplett im Budget. Für größere Zukunfts-Karten: Budget erhöhen (72 µs worst case sind im 50-ms-Tick immer noch trivial) oder hierarchische Cluster-Routen (Abschnitt 9).

### Speicher

| Objekt | Größe |
|---|---|
| `NavGraph` (statisch, pro Karte) | 173.060 B (169 KB) |
| `NavAStar` (statisch, pro Agent) | 20.488 B |
| `NavAgent` (statisch, pro Agent) | 21.904 B |
| 16 Agenten + 1 Karte (worst case statisch) | **511,3 KB** |
| belegt @1024 Nodes, 4 Kanten/Node | 24 KB Nodes + 48 KB Kanten |

### Heap

`operator new` war im Messabschnitt scharf geschaltet (Abbruch bei Allokation): **0 Allokationen** über alle 8 Konfigurationen. `make check-noalloc` belegt zusätzlich statisch, dass keine Heap-Primitive in den Headern stehen.

---

## 6. Integrationsplan (Phase 4)

### 6.1 Komponenten-Zuordnung (botcore bleibt Eigentümer)

| navigation-lab | Andockpunkt | Änderungsumfang |
|---|---|---|
| `NavGraph` + Parser | lädt dieselben per-Map-Waypoint-Dateien wie `WaypointGraph::ParseLine` (Format im Seam-Test auf Äquivalenz geprüft) | BotDriver: eine zusätzliche Load-Zeile pro Karte |
| `NavAgent::Step` | BotDriver-Tick, **vor** der Human-KI: erzeugt `NavCommand` | ein Block `if (nav_enabled)` |
| `NavCommand` → `BotCommand` | Merge-Regel aus `test_nav_seam.cpp`: Combat mit Ziel führt unverändert; ohne Ziel setzt Navigation `yaw_delta_deg`/`forward` | ~10 Zeilen |
| `NavCommand.stuck` | triggert bestehenden `ObstacleRecovery`-Pfad | 1 Zeile |
| `NavPersonalityFromTraits(PersonalityParams…)` | pro Bot aus vorhandenem Profil, kein neues Tuning-System | 1 Zeile |

**Kampf vs. kontaktfreie Navigation:** Pursue ist bewusst **Grobsteuerung** (Kurs halten auf sichtbares Ziel, halbe Geschwindigkeit, kein Routing) — Zielauswahl, Waffenkadenz, Ausweichbewegung und Respawn-Verzögerung bleiben vollständig bei der Human-KI/dem parallelen ChatGPT-Arbeitspaket. Reposition/Patrol/Scan sind die kontaktfreien Modi. Damit gibt es keine Überschneidung mit den fremden Arbeitsgebieten.

### 6.2 Per-Map-Waypoint-Dateien

Bestehendes Scripts-Format bleibt Quelle der Wahrheit (`node`/`edge`/Kommentare). Navigation 2.0 liest dieselben Dateien; neu sind nur **optionale** Erweiterungen (`block a b [0|1]`, Node-/Kanten-Flags), die von `WaypointGraph::ParseLine` ignoriert werden müssten, falls beide Parser dieselbe Datei lesen — daher: NavGraph liest die Datei, `WaypointGraph` bleibt für Legacy-Pfade unverändert. Vorschlag: pro Karte eine `<map>.nav`-Datei neben der bestehenden Waypoint-Datei, aus derselben Export-Pipeline.

### 6.3 „Too many bad syncs" — Analyse für die Navigation

Belegter Stand aus `docs/reports/2026-10-17-retail107-sync-check-investigation.md` (main):

- Handler `FUN_601A2D10` vergleicht zwei State-Wertepaare; Abweichung → `SYNCBAD` + Zähler++, Übereinstimmung → `SYNCOK` + Reset auf 0; **Retail-Schwelle = 10** (`DAT_602A7EB4 = 0a 00 00 00`), danach Disconnect mit `Too many bad syncs`.
- Nachweislich betroffene Läufe: alte DLL-Kandidaten (je 10 `SYNCBAD` in Folge → Disconnect) und der **Ground-Lookahead-Versuch** (Floor-Ray-Feature) — die qualifizierte `61DC27E0…`-DLL bestand dagegen die lokale Acht-Bot-Stunde.
- 1.10-Referenz prüft u. a. Sequence, Level, Pause, Player-Actions, Player-Entitys im Sync-CRC (`SessionState.cpp:765–812`); welche Felder bei Retail 1.07 divergieren, ist **offen**.

Konsequenzen für Navigation 2.0 (konkret, nicht spekulativ):

1. **Determinismus ist Pflicht, nicht Kür:** `NavAgent` ist eine reine Funktion von (Graph, Input, Seed) — keine Zeitquellen, kein versteckter Zufall. Server- und Bot-Client-Instanz mit gleichem Seed liefern bitgleiche Kommandos (getestet). Divergente Navigation wäre eine eigene SYNCBAD-Quelle.
2. **Kein Engine-State in der Nav-Entscheidung:** Alles, was der Agent liest, kommt aus dem Waypoint-Graph und den vom Driver übergebenen Input-Feldern. Floor-Rays/Physik-Queries sind **bewusst nicht** enthalten — der Ground-Lookahead-FAIL ist der empirische Beleg, dass solche Features Sync-Risiko tragen.
3. **Glatte Bewegung reduziert Korrekturbedarf:** Rate-limited Steering (240°/s), kein Rückwärtslaufen, Turn-in-place statt Bogenlaufen, Teleport-Guard (Route wird bei Sprüngen >8 m/Tick verworfen statt dagegenzulenken). Das ersetzt **keine** native Abnahme, minimiert aber Positions-Korrektur-Spikes.
4. **Abnahmeprotokoll übernehmen:** Integration erst nach dem Prüfplan des Sync-Reports (separate private Kopien, `ser_bReportSyncBad`-Beobachtung, **kein** Herunterregeln von `ser_iKickOnSyncBad`, kontrollierte A/B-Stufen Vanilla→1 Bot→Navigation-aktiv). Navigation ist dabei eine eigene Stufe: gleiche DLL-Basis, Nav-Block an/aus.

### 6.4 Langfristig: clientseitige Navmesh

Der Waypoint-Graph ist die korrekte erste Stufe (deckt Selbstständigkeit, Patrol, Verfolgung, Dead-End-Vermeidung ab). Eine clientseitige Navmesh (Cecil-Stil) wäre Stufe 2 — sie erfordert aber Engine-Zugriff (Kollisions-/Floor-Queries) und fällt damit unter dieselbe Sync-Risikoklasse wie Ground-Lookahead. Empfehlung: erst nach bestandener Native-Abnahme von Stufe 1 und nur mit dem obigen A/B-Protokoll; die `NavAgent`-FSM ist graphquellen-agnostisch designed (Interface `NearestNode`/`Plan`), eine Navmesh könnte später als `NavGraph`-Produzent dienen, ohne die FSM zu ändern.

---

## 7. Gruben-/Abgrund-Vermeidung — separater, gatebarer Vorschlag

**Nicht** Teil dieses Prototyps, wie gefordert nur als Vorschlag:

- **Daten:** Waypoint-Kanten-Flag `kEdgeDanger` existiert bereits und ist getestet (A* umgeht flagged Kanten; Parser versteht `edge a b <flags>`). Rein datenbasierte Pit-Vermeidung (Kartenautor markiert Kanten) ist damit **ohne jeden Engine-Zugriff** sofort verfügbar und sync-neutral.
- **Sensorisch:** Floor-Ray-Lookahead wäre die automatische Variante — **gatepflichtig**, weil (a) Ground-Lookahead bereits einen „Too many bad syncs"-FAIL produzierte, (b) Floor-Rays Engine-State lesen, der server-/client-seitig divergieren kann.
- **Sicherer Testpfad:** isolierte Offline-Stufe (Strahl gegen synthetische Höhendaten im Lab, deterministisch) → native Stufe nur mit A/B-Protokoll (6.3, Punkt 4), einzelne Karte, ein Bot, `ser_bReportSyncBad`-Monitoring, Abbruchkriterium: 1 SYNCBAD → Feature aus.

---

## 8. Blocker und offene Punkte

1. **Kein Retail-/Engine-Zugriff in dieser Umgebung** — alle Ergebnisse sind Offline-Nachweise. Native Abnahme (BotDriver-Patch + Sync-Protokoll) ist der nächste notwendige Schritt und liegt außerhalb dieses Auftragsrahmens.
2. **Budget vs. Kartengröße:** >256-Node-Karten brauchen höheres Budget (gemessen unkritisch) oder Cluster-Hierarchie — Designentscheidung vor der ersten großen Map.
3. **Waypoint-Datenqualität:** Navigation 2.0 kann schlechte Karten nicht heilen (feinde Kanten → Teilrouten/Scan). Export-Pipeline/Validierungswerkzeug wäre ein eigenes kleines Arbeitspaket.
4. **`WaypointGraph`-Kanten sind nicht öffentlich lesbar** (private Arrays) — die Kopplung läuft deshalb korrekt über das **Dateiformat**, nicht über Graph-Konversion. Für eine spätere Direkt-Konversion bräuchte botcore einen Edge-Iterator (fremder Schreibbereich — nicht angefasst).

## 9. Konkreter nächster Implementierungsschritt

**Ein Bot, eine Karte, Nav-Block im BotDriver hinter Flag:**

1. `navigation-lab`-Header in den BotDriver-Build aufnehmen (header-only, kein Makefile-Umbau).
2. Im Tick: `NavAgentInput` aus vorhandenem Bot-State füllen (Position, Yaw, `BotCommand.target`/`target_visible` + letzte bekannte Zielposition aus der Perception), `NavCommand` per Merge-Regel (6.1) in `BotCommand` übernehmen; `NavCommand.stuck` → `ObstacleRecovery`.
3. Flag `bot_bNav2` (Default **aus**); A/B-Abnahme nach 6.3-Protokoll auf separater Installation: Vanilla → 1 Bot Nav-aus → 1 Bot Nav-an → 8 Bots Nav-an, je Stufe mit SYNCBAD-Monitoring.
4. Erst danach: Item-/Objective-Flags (`kNodeImportant` ist vorbereitet), Pit-Flag-Rollout (7), Kartenvalidierung.

## 10. Regelkonformität (Parallelarbeit)

- GitHub-/AGENTS.md-Stand vor Arbeitsbeginn geprüft: `main` @ `107d28a` unverändert; offene Fremd-PRs (#39–#51, `agent/*`/andere `arena/*`) unberührt; kein A00-Dispatcher, kein geteilter Queue.
- Ausschließlich zugewiesener Schreibbereich: `poc/navigation-lab/**`, `docs/research/**`. Fremde Arbeitsgebiete (Zielpriorisierung, Waffenkadenz, Respawn-Delay, Human-KI-Kampfverhalten) nicht berührt — Pursue liefert nur Grobsteuerung.
- Kein Produktionsserver, keine geschützten Binaries, keine privaten Logs/Credentials; nur synthetische Kartendaten veröffentlicht.
- Offline-Tests klar von nativer Retail-Abnahme getrennt (Abschnitte 1, 6.3, 8).
- PR #54 bleibt eigenständig, kein Auto-Merge.
