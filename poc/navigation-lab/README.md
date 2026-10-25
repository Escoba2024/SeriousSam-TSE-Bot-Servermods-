# navigation-lab — Intelligente Bot-Navigation 2.0 (Offline-Prototyp)

Eigenständiger, engine-freier Prototyp für die nächste Bot-Navigationsstufe:
Waypoint-Graph, budgetierter A*, deterministische Routenwahl, Agent-FSM
(Patrol/Pursue/Reposition/Scan) mit Persönlichkeiten, Stuck-Erkennung und
Repath-Cooldown. **Nur synthetische Kartendaten.** Kein Retail-Zugriff, keine
Änderung an `poc/botcore/**` (Headers werden im Seam-Test read-only includiert).

Kontext, Messergebnisse und Integrationsplan:
[`docs/research/2026-10-25-bot-navigation-2-prototype.md`](../../docs/research/2026-10-25-bot-navigation-2-prototype.md)

## Bauen & Testen

```sh
make test           # alle vier Testsuiten (graph, astar, agent, seam)
make bench          # gemessene CPU/RAM-Benchmarks (1/4/8/16 Bots)
make smoke          # Kurzlauf: graph + astar
make check-noalloc  # Build-Gate: keine Heap-Primitive in den Headern
make compat         # Header-Kompatibilität C++11/C++14/C++17
```

Toolchain: `g++ -std=c++17 -O2 -Wall -Wextra` (wie `poc/botcore`), kein
CMake, keine Drittabhängigkeiten.

## Dateien

| Datei               | Inhalt                                                                 |
|---------------------|------------------------------------------------------------------------|
| `nav_graph.h`       | Waypoint-Graph: feste Kapazität (1024 Nodes, 12 Kanten/Node), Kanten-Flags (blocked/jump/danger), Node-Flags (important/dead-end/spawn), Scripts-kompatibler Parser, `NearestNode`, Blocking. Null Heap. |
| `nav_astar.h`       | A* mit binärem Heap, Expansion-Budget (Default 256), Generation-Stamps (keine Resets), deterministisches Tie-Break (f↑, g↓, Index↑), optionale per-Edge-Kostenvarianz pro Bot-Seed für Routenvielfalt; bei Budget/Unreachable Teilroute (tiefster bzw. zielnächster Node). |
| `nav_agent.h`       | Agent-FSM: Patrol (besuchsbasiertes Ziel-Scoring), Pursue (grobe Verfolgung; Feinbewegung bleibt beim Combat-Layer), Reposition (Route zur letzten bekannten Zielposition), Scan (Umschauen am Ankunfspunkt). Stuck-Detektor (botcore-Semantik), Teleport-Guard, Repath-Cooldown, Rate-limited Steering (Turn-in-place über 60°), Wegpunkt-Vorrücken per Segmentprojektion (verhindert Orbit-Limit-Cycles). `NavPersonalityFromTraits()` brückt botcore-Persona-Werte. |
| `nav_maps.h`        | Synthetische Kartenbauer: Korridor, Grid (mit Wänden), Ring, Dead-End-Karte, zwei disjunkte Grids, Spirale. Nur für öffentliche Tests/Benchmarks. |
| `test_nav_graph.cpp`| Basics, Blocking/Toggles, Parser, Kapazitätsgrenzen.                   |
| `test_nav_astar.cpp`| Erreichbar/unerreichbar, Blockaden+Alternativrouten, Zyklen/Ring, Budget, Zielwechsel, Determinismus über Instanzen. |
| `test_nav_agent.cpp`| Ende-zu-Ende mit kinematischem Simulator (20 Hz, 10 m/s): Patrol, unerreichbares Ziel→Scan, Pursue, Zielwechsel, Stuck→Recovery, Teleport-Guard, Budget-Fortschritt (Spirale), Persönlichkeitswirkung, 4-Bot-Determinismus, Persona-Bridge, toter Agent. |
| `test_nav_seam.cpp` | Integrationsnaht zu `poc/botcore` (read-only): gleiche Waypoint-Datei → `WaypointGraph` + `NavGraph` (Reachability-Äquivalenz auf allen Paaren), alle 6 Standard-Personas → `NavPersonality`, `BotCommand`/`NavCommand`-Merge-Regel. |
| `bench_nav.cpp`     | Gemessene Benchmarks (steady_clock, keine Schätzwerte), inkl. `operator new`-Trap: jede Heap-Allokation im Messabschnitt bricht ab. |
| `compat_tu.cpp`     | Compile-only-TU für `make compat`.                                     |

## Design-Regeln

1. **Null Allokationen** — alles statisch; `check-noalloc` + Runtime-Trap.
2. **Determinismus** — gleiche Eingaben/Seeds → bitgleiche Ausgaben
   (getestet); keine Zeit-, keine versteckten Zufallsquellen.
3. **Budgets** — jede Suche hat ein Expansions-Limit; Teilrouten statt
   Hängern; Such-Telemetrie (`searches_total`, `expansions_total`) für CPU-Nachweise.
4. **20-Hz-Tauglichkeit** — O(1)-Arbeit pro Tick außerhalb von (budgetierten)
   Replans; gemessen: 0,35–0,87 µs/Tick/Agent.
5. **Kampf bleibt beim Combat-Layer** — Navigation liefert im Pursue-Modus nur
   Grobsteuerung; die Human-KI behält Zielwahl/Kadenz/Ausweichen.
