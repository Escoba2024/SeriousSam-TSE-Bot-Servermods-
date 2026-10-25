# Test- und Benchmark-Report: `nav-item-bridge`

- **Datum:** 2026-10-25
- **Verzeichnis:** `poc/research/nav-item-bridge/`
- **Compiler & Flags:** `g++ -std=c++17 -O2 -Wall -Wextra -Wpedantic -Werror` (Benchmarks mit `-O3 -DNDEBUG`; Sprachstandard-Gate über `-std=c++14`, `-std=c++17`, `-std=c++20`)
- **Gesamtergebnis Offline-Suite:** **PASS** (`24 / 24` automatisierte Prüffälle grün: `9` Seam-/Vertrags-Checks + `12` Pflicht-Szenarien + `3` Mehrbot-Konkurrenz-Checks; `0` Heap-Allokationen; `0` Budget-Überschreitungen)
- **Wichtige Abgrenzung:** Alle Ergebnisse in diesem Bericht sind **enginefreie Offline-Nachweise** auf synthetischen Testkarten. Ein Offline-`PASS` ist **keine** Retail-Abnahme in `GameMP.dll` / Serious Sam TSE Classic 1.07.

---

## 1. Übersicht der ausführbaren Prüfkommandos

| Gate | Kommando (aus `poc/research/nav-item-bridge`) | Geprüfte Eigenschaft | Status |
|---|---|---|---|
| Gesamt-Testsuite | `make test` | Alle 24 Tests (`test_seams_and_contracts`, `test_scenarios_matrix`, `test_multibot_competition`) | **PASS** (`24/24`) |
| Kompakte Szenario-Matrix | `make smoke` | Markdown-Zusammenfassung der 12 Pflicht-Szenarien + Mehrbot-Kurzlauf | **PASS** |
| CPU- & Speicher-Benchmark | `make bench` | `sizeof`-Speicherbilanz, P50/P95/P99-Tick-Latenz, `operator new` Laufzeit-Falle | **PASS** (`0` Allocs) |
| C++-Standard-Gate | `make compat` | Warnungsfreie Übersetzung unter `-std=c++14`, `-std=c++17`, `-std=c++20` | **PASS** |
| Statisches No-Alloc-Gate | `make check-noalloc` | Keine Heap-/STL-Container-Tokens (`new`, `delete`, `malloc`, `vector`, …) in `include/**` | **PASS** (`8/8` Header) |
| Upstream-Kreuzprüfung | `make UPSTREAM_FLAGS="... -DNAV_ITEM_BRIDGE_REQUIRE_UPSTREAM" test compat` | Bit-identischer Lauf direkt gegen extrahierte Original-Header aus PR #54 (`3f2ba8db`) & PR #55 (`72d464ff`) | **PASS** |

---

## 2. Dokumentation aller 12 Pflicht-Szenarien (`test_scenarios_matrix`)

Gemeinsames Reproduktionskommando für alle 12 Szenarien:
```bash
cd poc/research/nav-item-bridge && make build/test_scenarios_matrix && ./build/test_scenarios_matrix
```

### Szenario 01 — Wenig HP + erreichbares Medkit (`S01 LowHpReachableMedkit`)
- **Erwartung:** Ein verwundeter Bot (`22/100 HP`) in einem L-förmigen Korridor (`(0,0) -> (0,-12) -> (10,-12)` mit Sicht-/Bewegungswand dazwischen) ignoriert nachrangige Munition (`id=102`), wählt sofort das erreichbare `+50 HP`-Medkit (`id=101`), übergibt die Steuerung an `ControllerOwner::kItemNavigation`, umläuft die Korridorecke per A* und sammelt das Medkit bis auf `72 HP` ein.
- **Ergebnis:** **PASS** — `goal=101 owner=item-nav pickup_tick=51 hp=22->72`.
- **Testkommando:** `cd poc/research/nav-item-bridge && ./build/test_scenarios_matrix`
- **Warum der Test sinnvoll ist:** Prüft den grundlegenden End-to-End-Durchstich `Selbstzustand -> Item-Nutzen -> NavGoal -> A*-Mehrknoten-Steuerung -> physischer Pickup -> Zielabschluss`.

### Szenario 02 — Leere Munition + erreichbares Ammo-Item (`S02 EmptyAmmoReachableAmmo`)
- **Erwartung:** Ein voll geheilter Bot (`100 HP`), der Rocket Launcher (`Waffe 8`) und Colt besitzt, aber auf allen Munitionswaffen `0` Schuss hat (`ammo_starved`), erkennt den Munitionsnotstand, wählt das `16 m` entfernte Raketen-Ammo-Pack (`id=201`), navigiert über den Graphen dorthin und stellt seine Feuerbereitschaft (`rockets = 5`) wieder her.
- **Ergebnis:** **PASS** — `ammo_starved->goal=201 pickup_tick=30 rockets=0->5`.
- **Testkommando:** `cd poc/research/nav-item-bridge && ./build/test_scenarios_matrix`
- **Warum der Test sinnvoll ist:** Stellt sicher, dass `UsableWeaponMask` und Munitionsknappheit zwischen `botcore` und `ItemPlanner` konsistent gekoppelt sind und Bots nicht dauerhaft mit leerer Waffe herumlaufen.

### Szenario 03 — Waffe statt unnötigem Health-Item (`S03 WeaponInsteadOfFullHealth`)
- **Erwartung:** Ein Bot mit `100/100 HP` und `80/100 Armor` (nur Messer + Einzel-Colt) lässt ein unmittelbar neben ihm liegendes Medkit (`id=301` in `3,5 m` Abstand) unberührt (`HealthNeed == 0`), wählt stattdessen den `18 m` entfernten Rocket Launcher (`id=302`) und rüstet sich damit aus.
- **Ergebnis:** **PASS** — `first_goal=302 (skipped 3.5m Medkit 301=0) acquired_RL=1`.
- **Testkommando:** `cd poc/research/nav-item-bridge && ./build/test_scenarios_matrix`
- **Warum der Test sinnvoll ist:** Verhindert das klassische Bot-Fehlverhalten, reine Nähe über tatsächlichen Bedarf zu stellen und nutzlose Heil-Items vor wichtigen Waffen-Upgrades anzusteuern.

### Szenario 04 — Gegnerkontakt während Item-Suche (`S04 EnemyContactDuringItemSearch`)
- **Erwartung:** Während ein gesunder, mit Tommygun ausgerüsteter Bot (`95 HP`) aktiv auf ein Rüstungs-Item (`id=401`) zuläuft, tritt ein Gegner in `~10 m` Sichtlinie auf. Die Kampfpriorität steigt über `combat_lock_priority`, `ItemPlanner` bricht die Suche mit `ItemReason::kCombatLock` ab, `NavGraphSink` wird geleert (`sink_idle=1`), und `ControllerOwner::kCombat` übernimmt Zielen & Feuern ohne Navigations-Störeinfluss.
- **Ergebnis:** **PASS** — `pre_nav=1 abort=1 owner=combat(31 ticks) shots=1 sink_idle=1`.
- **Testkommando:** `cd poc/research/nav-item-bridge && ./build/test_scenarios_matrix`
- **Warum der Test sinnvoll ist:** Beweist die harte Vorrangregel der Combat-KI bei Feindkontakt und die saubere Rückgabe der Steuerung (`fire`- und `yaw`-Hoheit).

### Szenario 05 — Beschuss / Schaden während Navigation (`S05 IncomingFireDamageDuringNav`)
- **Erwartung:** Zweiteiliger Nachweis:
  - **5A (Opportunistischer Abbruch):** Ein gesunder Bot (`90 HP`) auf dem Weg zu regulärer Munition erleidet schweren Treffer-Schaden (`-38 HP` → `under_fire=true`), woraufhin `ItemPlanner` den exponierten Lauf sofort mit `ItemReason::kDamageAbort` abbricht.
  - **5B (Überlebens-Rückzug):** Ein kritisch verwundeter Bot (`18 HP`) unter Gegnersicht (`24 m`) und Streifschuss hält dank `suppress_combat = true` Kurs auf das rettende `+50 HP`-Medkit (`ControllerOwner::kSurvivalRetreat`, `fire=false`) und heilt sich auf `66 HP`.
- **Ergebnis:** **PASS** — `5A_dmg_abort=1(under_fire=1) 5B_survival_retreat_ticks=11 healed_hp=66`.
- **Testkommando:** `cd poc/research/nav-item-bridge && ./build/test_scenarios_matrix`
- **Warum der Test sinnvoll ist:** Prüft beide Seiten der Schadensreaktion: kein stures Weiterlaufen in eine Todeszone für unwichtige Items, aber auch kein selbstmörderisches Stehenbleiben bei kritischen HP neben einem rettenden Medkit.

### Szenario 06 — Item außerhalb erreichbaren Graphen (`S06 UnreachableIslandItem`)
- **Erwartung:** Ein hochwertiger Rocket Launcher (`id=601`) liegt nur `7 m` horizontal entfernt auf einem abgetrennten Insel-Waypoint ohne Verbindungskante, während eine Tommygun (`id=602`) in `20 m` auf dem verbundenen Hallenboden liegt. `WorldPathEnricher` erkennt `601` im ersten Tick als `kUnreachable`, speichert dies im `PathCostCache` (`0` Re-Probes im Folgetick) und führt den Bot direkt zu `602`.
- **Ergebnis:** **PASS** — `rejected_island=601(unreach=1,t2_reprobes=0) picked_reachable=602(1)`.
- **Testkommando:** `cd poc/research/nav-item-bridge && ./build/test_scenarios_matrix`
- **Warum der Test sinnvoll ist:** Verhindert sowohl Endlosläufe gegen Wände/Vorsprünge unter unerreichbaren Plattform-Items als auch teure A*-Re-Search-Stürme in jedem Tick.

### Szenario 07 — Hindernis und Alternativroute (`S07 ObstacleAndAlternativeRoute`)
- **Erwartung:** Der direkte `24 m`-Korridor zur `+100`-Rüstung (`id=701`) ist durch ein geschlossenes Tor (`kEdgeBlocked` + physische Wand) versperrt; über den Westflügel existiert eine `48 m` lange Umgehungsroute. `ConstrainedNavSearch` umgeht die gesperrte Kante, projiziert die reale Umweglänge in die Nutzenbewertung und führt den Bot kollisionsfrei über `x < -7.5` zum Ziel.
- **Ergebnis:** **PASS** — `bypassed_blocked_gate=1(min_x<-7.5) pickup_tick=143 armor=100`.
- **Testkommando:** `cd poc/research/nav-item-bridge && ./build/test_scenarios_matrix`
- **Warum der Test sinnvoll ist:** Nachweis, dass statische/dynamische Graph-Sperren sowohl in der Pfadkostenbewertung als auch in der tatsächlichen Routenführung berücksichtigt werden.

### Szenario 08 — Stuck und Neuplanung (`S08 DynamicStuckAndReplan`)
- **Erwartung:** Zweiteiliger Härtetest:
  - **8A (Unkartierte Barriere mit Ausweichroute):** Die kürzere Ostroute (`28 m`) ist im Graphen als offen eingetragen, physisch jedoch durch eine Sackgassen-Mauer blockiert. Der Bot läuft zuerst nach Osten (`x > 2.0`), erkennt die Blockade, sperrt das Segment lokal in `LocalBlockedEdgeTable`, bricht den 40-Tick-Blindlauf von `ObstacleRecovery` sauber ab, plant per A* auf die freie Westroute um und sammelt den Rocket Launcher ein.
  - **8B (Komplettblockade ohne Ausweichroute):** Ist die einzige Verbindung physisch zugemauert, eskaliert `NavGraphSink` nach zwei erfolglosen Befreiungsversuchen auf `NavStatus::kStalled`, worauf `ItemPlanner` kontrolliert mit `ItemReason::kStalled` abbricht.
- **Ergebnis:** **PASS** — `8A_east_trap=1 replan=1 detour_pickup_t=172 | 8B_stalled_abort=1`.
- **Testkommando:** `cd poc/research/nav-item-bridge && ./build/test_scenarios_matrix`
- **Warum der Test sinnvoll ist:** Deckt Imperfektionen realer Waypoint-Netze (bewegliche Türen, Props, fehlende Sperrflags) ab und hat im Entwurf den kritischen 24-m-Off-Mesh-Konflikt von `botcore::ObstacleRecovery` aufgedeckt und gelöst.

### Szenario 09 — Zwei Bots mit demselben Ziel (`S09 TwoBotsSameGoalCompetition`)
- **Erwartung:** Zwei verwundete Bots (`35 HP`) steuern gleichzeitig dasselbe zentrale MegaHealth (`id=901`) an; Bot 0 startet näher (`9 m`) als Bot 1 (`15 m`), während nahe Bot 1 ein sekundäres Medkit (`id=902`) liegt. Bot 0 sammelt `901` zuerst ein; Bot 1 erkennt sofort im Folgetick das aufgenommene Item (`respawn_s = 25 s`), schwenkt ohne Stehenbleiben auf `902` um und sammelt dieses ein.
- **Ergebnis:** **PASS** — `both_init_goal=901(1) winner_901=bot0 bot1_rerouted_902=1 winner_902=bot1`.
- **Testkommando:** `cd poc/research/nav-item-bridge && ./build/test_scenarios_matrix`
- **Warum der Test sinnvoll ist:** Prüft saubere Konkurrenzauflösung über reguläre Welt-Snapshots ohne geteilten mutierbaren Zustand und ohne Geister-Campen auf leeren Spawnpunkten.

### Szenario 10 — Persönlichkeitsabhängige Zielentscheidung (`S10 PersonalityDependentDecision`)
- **Erwartung:** Identischer Weltzustand, identische Position `(0,0)`, identischer Skill-Tier (`Tier 4`), `45 HP`, Tommygun vorhanden; symmetrisch in je `14 m` Entfernung liegen links ein `+55 HP`-Medkit (`id=1001`) und rechts eine Lasergun (`id=1002`). Der `Aggressor` (`persona=0`) entscheidet sich für das Waffen-Upgrade (`1002`), der `Survivor` (`persona=1`) für das Medkit (`1001`), während alle mechanischen Skill-Werte über alle drei Schichten hinweg bit-identisch bleiben.
- **Ergebnis:** **PASS** — `Tier4 Aggressor->1002(Weapon) Survivor->1001(Health) skill_orthogonal=1`.
- **Testkommando:** `cd poc/research/nav-item-bridge && ./build/test_scenarios_matrix`
- **Warum der Test sinnvoll ist:** Belegt sichtbare taktische Vielfalt der sechs Persönlichkeiten bei strikter Wahrung der `botcore`-Regel „Persönlichkeit verändert niemals mechanisches Können“.

### Szenario 11 — Budgetgrenzen bei großen Graphen (`S11 LargeGraphBudgetCap`)
- **Erwartung:** Auf einem maximal ausgebauten `32 × 32 = 1.024`-Knoten-Graphen mit Hindernis-Pfeilern und `24` verteilten Items unter engem Expansionslimit (`max_expansions_per_tick = 96`) überschreitet der Agent in keinem einzigen von `400` Ticks das Limit (`violations == 0`), setzt Teilrouten (`partial_route_`) inkrementell über Folgeticks fort und sammelt erfolgreich mehrere Ziele ein.
- **Ergebnis:** **PASS** — `nodes=1024 ticks=400 max_exp=96/96 violations=0 pickups=5`.
- **Testkommando:** `cd poc/research/nav-item-bridge && ./build/test_scenarios_matrix`
- **Warum der Test sinnvoll ist:** Schützt den 20-Hz-Spieltakt auf großen Serious-Sam-Kathedralen-/Hofkarten zuverlässig vor A*-Latenzausreißern.

### Szenario 12 — Deterministischer Replay-Lauf mit gleichen Seeds (`S12 DeterministicReplay`)
- **Erwartung:** Zwei unabhängige Komplettläufe (`600` Ticks × `4` Bots, Kampf aktiv, dynamisches Öffnen/Schließen eines Tors bei Tick 120/260, `6` respawnende Items) mit Seed `0xC0DECAFE` liefern über alle Positionen, Winkel, `BotDriverIntent`-Kommandos, `ControllerOwner`-Zustände und Ziel-IDs denselben 64-Bit-FNV-1a-Zustandshash, während ein Kontrolllauf mit Seed `0xDEADBEEF` sauber abweicht.
- **Ergebnis:** **PASS** — `600t x 4bots hashA=0xd9b0cf1aa2b0b01c == hashB=0xd9b0cf1aa2b0b01c (!= hashC) pickups=8`.
- **Testkommando:** `cd poc/research/nav-item-bridge && ./build/test_scenarios_matrix`
- **Warum der Test sinnvoll ist:** Determinismus ist Grundvoraussetzung für reproduzierbares Debugging, Regressionstests und Multiplayer-Stabilität ohne undefiniertes Verhalten.

---

## 3. Ergänzende Seam-, Vertrags- und Mehrbot-Tests (`12` weitere Checks)

### 3.1 `test_seams_and_contracts` (`9/9 PASS`)
Kommando: `cd poc/research/nav-item-bridge && ./build/test_seams_and_contracts`
- `C01_BuildAll30Profiles`: Alle `5 × 6 = 30` Profile valide konstruierbar.
- `C02_SkillOrthogonalAcross3Layers`: Alle `180` `(tier, persona_a, persona_b)`-Kombinationen bit-orthogonal in Combat, Item-Utility und Navigation.
- `C03_InvalidProfileBoundsRejected`: Ungültige Tiers (`0`, `6`) und Personas (`-1`, `6`) werden fail-closed abgewiesen.
- `C04_CoordinateAndYawParity`: Exakte Übereinstimmung von `botcore::AimAt`, `NavGraphSink`-Steuerung und Kinematik (`+X -> -90°`, `-Z -> 0°`).
- `C05_TrueGraphCostBeatsEuclideanTrapAndCaches`: Bot vermeidet `4 m`-Luftlinien-Falle hinter U-Wand (`62 m` Pfad), wählt offenen `14 m`-Korridor und erzielt im Folgetick `100 %` Cache-Hits (`0` Probes).
- `C06_MalformedWorldFailsClosed`: `NaN`-Koordinaten & doppelte Item-IDs führen deterministisch zu `ItemReason::kInvalidWorld` bei endlichen Ausgabewerten.
- `C07_EmptyGraphFallsBackToMaplessScan`: Leerer Graph (`0` Knoten) fällt absturzfrei auf `kMaplessScan` zurück.
- `C08_DeathAndRespawnStateHygiene`: Tod & Respawn löschen aktive Ziele, Schadens-Timer und lokale Sperren rückstandsfrei.
- `C09_Fuzz1000TicksFiniteBoundedAndFireSafe`: `1.000` randomisierte Stress-Ticks ohne `NaN`/`Inf`, ohne Budgetverletzung (`max_exp = 33/80`) und mit `0` Fehlschüssen außerhalb von `kCombat`.

### 3.2 `test_multibot_competition` (`3/3 PASS`)
Kommando: `cd poc/research/nav-item-bridge && ./build/test_multibot_competition`
- `M01_EightBotContentionAndGraphImmutability`: `8` Bots über `600` Ticks in einer 4-Raum-Deathmatch-Arena — `const NavGraph`-Speicherhash vor und nach dem Lauf identisch (`graph_immutable=1`), exakte Pickup-Erhaltung (`7 == 7`), `6/8` aktive Sammler.
- `M02_SlotStepOrderIndependence`: Vertauschen der `Step`-Reihenfolge zweier Agenten liefert bit-identische `BotDriverIntent`-Hashes (`0xcbf29ce484222325`).
- `M03_HysteresisPreventsGoalThrashing`: Bei zwei fast identischen Medkits auf entgegengesetzten Diagonalen entstehen `0` Ziel-Oszillationen (`switches=0`).

### 3.3 Direkte Kreuzverifikation gegen Original-Header aus PR #54 & PR #55
Mit extrahierten Originaldateien aus PR #54 (`3f2ba8dbf0df341b35cb157efd152fa93d1d7fd7`) und PR #55 (`72d464ff501d90ec4b69c2a131a50a06323e1909`) unter `-DNAV_ITEM_BRIDGE_REQUIRE_UPSTREAM` liefen sämtliche `24` Tests sowie `make compat` fehlerfrei durch und lieferten **exakt denselben Replay-Hash `0xd9b0cf1aa2b0b01c`** wie der Standalone-Lauf.

---

## 4. CPU- und Speicher-Benchmark (`bench_nav_item_bridge`, Aufgabe 11)

Kommando: `cd poc/research/nav-item-bridge && make bench`

### 4.1 Statischer Speicherbedarf (`sizeof`, 0 Byte dynamischer Heap)

| Struktur / Komponente | Größe (Bytes) | Größe (KiB) | Kardinalität in `GameMP.dll` |
|---|---:|---:|---|
| `const navlab::NavGraph` (`1.024` Nodes × `8` Edges) | `173.060 B` | `169,00 KiB` | **1× pro geladener Karte** (geteilt, read-only) |
| `botcore::HumanBotPolicy` (Combat-KI) | `2.408 B` | `2,35 KiB` | 1× pro Bot |
| `itemai::ItemPlanner` (Item-Utility) | `12.096 B` | `11,81 KiB` | 1× pro Bot |
| `navbridge::PathCostCache` (128 Einträge) | `1.800 B` | `1,76 KiB` | 1× pro Bot |
| `navbridge::NavGraphSink` (Goal-Navigation) | `632 B` | `0,62 KiB` | 1× pro Bot |
| `navlab::NavAgent` (Patrol / Reposition) | `21.904 B` | `21,39 KiB` | 1× pro Bot |
| `navbridge::ConstrainedNavSearch` (A*-Puffer) | `40.976 B` | `40,02 KiB` | 1× pro Bot |
| **Gesamter `NavItemBridgeAgent` (1 Bot)** | **`89.896 B`** | **`87,79 KiB`** | Komplett inkl. aller Caches & Puffer |
| **8 Bots + 1 geteilter `NavGraph`** | **`892.228 B`** | **`871,32 KiB`** | Typisches 8-Bot-Deathmatch (`< 0,9 MiB`) |
| **16 Bots + 1 geteilter `NavGraph`** | **`1.611.396 B`** | **`1.573,63 KiB`** | Voller 16-Slot-Server (`~1,54 MiB`) |

### 4.2 20-Hz-Laufzeitverhalten (`50.000 µs` = `100 %` Frame-Budget)

*Hinweis: Gemessen wurde konservativ der komplette Arena-Tick inkl. Sichtlinien- & Fühler-Raycasts, Wahrnehmung, Pfadkosten-Anreicherung, Item-Scoring, A*-Suche, Wand-Befreiung und Arbitrierung unter aktivem globalem `operator new`-Trap.*

| Workload | Nodes | Items | Bots | Mean Server-Tick | P50 | P95 | P99 | Mean pro Bot | Ø Exp/Bot | Max/Cap | Cache-Hit-% | Heap-Allocs |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| `A_Small_64n_16i_1b` | 64 | 16 | 1 | `3,60 µs` | `3,23 µs` | `6,75 µs` | `9,86 µs` | `3,60 µs` | `5,62` | `113 / 192` | `95,1 %` | **`0`** |
| `B_RetailDM_256n_32i_8b` | 256 | 32 | 8 | `115,43 µs` | `114,33 µs` | `144,09 µs` | `168,12 µs` | `14,43 µs` | `21,70` | `192 / 192` | `88,4 %` | **`0`** |
| `C_Cathedral_1024n_64i_8b` | 1024 | 64 | 8 | `711,52 µs` | `716,77 µs` | `825,96 µs` | `992,28 µs` | `88,94 µs` | `31,49` | `192 / 192` | `86,2 %` | **`0`** |

- **Typischer 8-Bot-Deathmatch-Server (`256` Knoten, `32` Items):** `P99 = 168,12 µs` → **nur `0,34 %`** des `50 ms`-Budgets bei 20 Hz (`~14,4 µs` pro Bot).
- **Maximalausbau (`1.024` Knoten, `64` Items, `8` Bots):** `P99 = 992,28 µs` (`< 1,0 ms`) → **unter `2,0 %`** des `50 ms`-Budgets bei **0 Heap-Allokationen** und **0 Budget-Überschreitungen**.
