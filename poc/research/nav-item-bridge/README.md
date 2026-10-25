# `nav-item-bridge` — Enginefreier Adapter zwischen Navigation 2.0, Item-Utility und Combat-KI

> **Hinweis zur Einordnung:** Dieser Prototyp ist eine reine **Offline-Forschungs- und Integrationsschicht** (`poc/research/nav-item-bridge/**`). Ein Offline-`PASS` ersetzt **keine** native Retail-Abnahme in Serious Sam: The Second Encounter Classic 1.07 (`GameMP.dll` / Live-MP-Qualifikation).

## Zielsetzung & Verantwortungs-Trennung

`nav-item-bridge` verbindet die bestehenden Prototypen aus:
- **`poc/botcore/*.h`** (`main`, `ab0c740`) — Wahrnehmung (`Perception`), menschliches Zielen (`HumanAim`), Waffenwahl (`Loadout`), Kampfsteuerung (`HumanBotPolicy`) und reaktive Wand-Befreiung (`ObstacleRecovery`),
- **PR #54 (`poc/navigation-lab`, `3f2ba8db`)** — Waypoint-Graph (`navlab::NavGraph`), deterministische A*-Pfadsuche (`navlab::NavAStar`) und Patrouillen-/Repositions-Agent (`navlab::NavAgent`),
- **PR #55 (`poc/research/item-utility`, `72d464ff`)** — zustandsbasierte Item-Bewertung (`itemai::EvaluateItem`), Hysterese-/Abort-Planer (`itemai::ItemPlanner`) und abstrakte Ziel-Senke (`itemai::NavigationSink`),

ohne eine zweite Kampf-KI, ohne duplizierte Pfadsuche und ohne Änderungen an schreibgeschützten Upstream-Verzeichnissen.

| Schicht | Beantwortet ausschließlich | Darf **nicht** entscheiden |
|---|---|---|
| **Combat-KI (`botcore::HumanBotPolicy`)** | **WANN** Kampf Vorrang hat + Zielen (`yaw/pitch`), Feuerfreigabe (`fire`) & Waffenindex (`weapon`) | Welches Item langfristig angesteuert wird oder wie Mehrraum-Routen geplant werden |
| **Item-Utility (`itemai::ItemPlanner`)** | **WELCHES** Ziel sich lohnt + Hysterese, Cooldowns, Unreachable-Blacklist & Schadens-/Kampf-Abbruch | Direkte Lenkwinkel, Waypoint-Fortschritt oder Abzugsteuerung |
| **Navigation 2.0 (`NavGraphSink` + `navlab::NavAgent` + `ObstacleRecovery`)** | **WIE** der Bot sein aktives Item-Ziel bzw. seine Patrouillen-/Ausweichroute erreicht | Eigenmächtige Item-Priorisierung oder Feuerbefehle |

---

## Verzeichnisstruktur

```text
poc/research/nav-item-bridge/
├── Makefile                              # Targets: all, test, smoke, bench, compat, check-noalloc, clean
├── README.md                             # Kurzüberblick & Reproduktionskommandos
├── include/
│   ├── upstream_seams.h                  # Read-only-Include-Resolver (botcore + PR #54 + PR #55)
│   ├── nav_cost_cache.h                  # Tick-Budget, LocalBlockedEdgeTable, ConstrainedNavSearch, PathCostCache, WorldPathEnricher
│   ├── nav_goal_sink.h                   # Konkrete itemai::NavigationSink auf const navlab::NavGraph
│   ├── bridge_arbitrator.h               # Strikte 3-Schichten-Arbitrierung + erklärbarer ArbitrationTrace
│   ├── nav_item_bridge.h                 # Pro-Bot-Fassade NavItemBridgeAgent + 5x6-Profil-Orthogonalität
│   ├── arena_sim.h                       # Deterministischer 20-Hz-Mehrbot-Simulator (Wände, LOS, Pickups, Kampf)
│   └── upstream/
│       ├── navlab_mirror.h               # Guard-kompatibler Fallback-Spiegel von PR #54 (solange noch nicht auf main)
│       └── itemai_mirror.h               # Guard-kompatibler Fallback-Spiegel von PR #55 (solange noch nicht auf main)
├── tests/
│   ├── compat_tu.cpp                     # C++14 / C++17 / C++20 Syntax- & Warnungs-Gate (-Wall -Wextra -Werror)
│   ├── test_seams_and_contracts.cpp      # 9 Seam-, Orthogonalitäts-, Cache-, Fail-Closed- & 1000-Tick-Fuzz-Checks
│   ├── test_scenarios_matrix.cpp         # Alle 12 Pflicht-Szenarien (inkl. --summary Markdown-Ausgabe)
│   └── test_multibot_competition.cpp     # 8-Bot-Konkurrenz, const-NavGraph-Unveränderlichkeit, Reihenfolge-Invarianz
└── benches/
    └── bench_nav_item_bridge.cpp         # sizeof-Speicherbilanz, P50/P95/P99-Latenz & globaler operator-new-Trap
```

---

## Schnellstart & Prüfkommandos

Alle Befehle werden aus `poc/research/nav-item-bridge` ausgeführt:

```bash
cd poc/research/nav-item-bridge

# 1. Alle 24 automatisierten Tests (Seams + 12 Pflicht-Szenarien + Multi-Bot)
make test

# 2. Kompakte Szenario-Matrix als Markdown-Tabelle
make smoke

# 3. CPU-/Speicher-Benchmark inkl. Laufzeit-Nachweis von 0 Heap-Allokationen
make bench

# 4. Sprachstandard-Kompatibilität (C++14, C++17, C++20 mit -Wall -Wextra -Werror)
make compat

# 5. Statischer No-Alloc- & No-STL-Container-Check über alle Header
make check-noalloc

# 6. Aufräumen aller Build-Artefakte
make clean
```

Wenn PR #54 (`poc/navigation-lab`) und PR #55 (`poc/research/item-utility`) lokal ausgecheckt oder auf `main` gemerged sind, bindet `upstream_seams.h` deren Original-Header automatisch direkt ein. Mit `-DNAV_ITEM_BRIDGE_REQUIRE_UPSTREAM` lässt sich zusätzlich zur Compile-Zeit erzwingen, dass keinerlei Fallback-Spiegel genutzt wird.

---

## Weiterführende Dokumentation

- [`docs/research/nav-item-bridge/2026-10-25-architektur-und-schnittstellenanalyse.md`](../../../docs/research/nav-item-bridge/2026-10-25-architektur-und-schnittstellenanalyse.md)
- [`docs/research/nav-item-bridge/2026-10-25-test-und-benchmark-report.md`](../../../docs/research/nav-item-bridge/2026-10-25-test-und-benchmark-report.md)
- [`docs/research/nav-item-bridge/2026-10-25-codex-c4-integrationsplan.md`](../../../docs/research/nav-item-bridge/2026-10-25-codex-c4-integrationsplan.md)
