# Architektur- und Schnittstellenanalyse: `nav-item-bridge` (Navigation 2.0 × Item-Utility × Combat-KI)

- **Datum:** 2026-10-25
- **Projekt:** `ssam.ai` (`Escoba2024/SeriousSam-TSE-Bot-Servermods-`)
- **Basis-Commit (`main`):** `ab0c7400353a108f8461bb82280c539fdfe81499`
- **Referenzierte Vorarbeiten (strikt read-only):**
  - `poc/botcore/*.h` + `poc/candidates/integrated-human-cpu-20261021/BotDriver.cpp` (bestehende 20-Hz-Kampf-, Wahrnehmungs-, Waffen- und Wandbefreiungsschicht)
  - **PR #54** (`3f2ba8dbf0df341b35cb157efd152fa93d1d7fd7`, `poc/navigation-lab/*`) — Navigation 2.0 (`NavGraph`, `NavAStar`, `NavAgent`)
  - **PR #55** (`72d464ff501d90ec4b69c2a131a50a06323e1909`, `poc/research/item-utility/*`) — Item-Utility (`ItemPlanner`, `EvaluateItem`, `NavigationSink`, `botcore_adapter.h`)
  - **PR #57** (`6b84c5d283664bc9e968bb4961abf2dd48731c5b`) — Human-AI-P1-Referenz (Koordinaten- und Kadenzkonventionen)
- **Status:** Offline-Integrationsprototyp (`PASS`, 24/24 Testsuiten grün, 0 Heap-Allokationen). **Kein Ersatz für eine native Retail-Abnahme in `GameMP.dll`.**

---

## 1. Schnittstellen-Inspektion der bestehenden Schichten (Aufgabe 1)

Vor dem Entwurf der Brücke wurden sämtliche Header und Aufrufpfade in `poc/botcore`, PR #54, PR #55 und `BotDriver.cpp` geprüft. Dabei zeigten sich vier präzise Anschlussstellen und drei reale Integrationslücken, die `nav-item-bridge` ohne Änderung an den Quellmodulen schließt:

### 1.1 Gemeinsame Koordinaten- und Zeitkonventionen
Alle drei Systeme teilen bereits dasselbe rechtshändige Serious-Sam-TSE-Koordinatensystem und denselben 20-Hz-Takt (`dt = 0.05 s`):
- **Achsen:** `+X` rechts, `+Y` oben, `-Z` vorwärts bei `yaw_deg = 0°`.
- **Yaw-Formel:** `yaw_deg = atan2(-dx, -dz) * 180.0 / pi` (identisch in `botcore::AimAt`, `navlab::NavAgent::SteerTowards` und `NavGraphSink::SteerTowards`).
- **Heading-Akkumulation:** Unwrapped `bs_aHeading += yaw_delta_deg` in `BotDriver.cpp`.

### 1.2 Identifizierte Schnittstellenlücken zwischen PR #54, PR #55 und `botcore`

1. **Abstrakte Ziel-Senke ohne Graph-Anbindung:**
   PR #55 definiert `itemai::NavigationSink` (`Submit`, `Cancel`, `Poll`) sowie `RecordingNavigationSink` für Offline-Attrappen, besitzt aber keine Implementierung auf `navlab::NavGraph` / `navlab::NavAStar`. Umgekehrt kennt `navlab::NavAgent` aus PR #54 nur `kPatrol`, `kPursue`, `kReposition` und `kScan`, jedoch kein explizites Item-Ziel mit `arrive_radius_m`, `expires_tick`, `max_speed_frac` und 2-Strike-`kStalled`-Eskalation.
2. **Euklidische Distanzfalle in `itemai::EvaluateItem`:**
   PR #55 berechnet `travel_s = Distance(w.self.eye, it.pos) / speed` aus der Luftlinie. Liegt ein Medkit `4 m` Luftlinie hinter einer massiven Wand, erfordert aber `62 m` Korridor-Umweg, überschätzt die Luftlinie den Nutzen massiv gegenüber einem offen erreichbaren Medkit in `14 m` Entfernung. Ebenso fehlt ohne Graph-Abfrage eine Erkennung abgetrennter Graph-Inseln (`reachable = false`).
3. **Konflikt zwischen `botcore::ObstacleRecovery` und Waypoint-Navigation (zentraler Befund):**
   `botcore::ObstacleRecovery` (`poc/botcore/bot_navigation.h`) wurde ursprünglich für kartenlose Bots entworfen: Nach dem Wegdrehen von einer Wand erzwingt `NavigationPhase::Advance` **40 Ticks (`2,0 s` ≈ `24 m`)** geradlinigen Blindflug. In Verbindung mit einem Waypoint-Graphen schiebt diese starre 40-Tick-Phase den Bot nach einer A*-Neuplanung bis zu `20 m` aus dem Navigationsnetz heraus (`off-mesh`), sodass anschließende `NearestNode`-Abfragen fehlschlagen.

---

## 2. Gemeinsame Adapter-Architektur & strikte Verantwortungstrennung (Aufgabe 2)

Die Brücke kapselt den kompletten Zustand eines einzelnen Bots in `navbridge::NavItemBridgeAgent` (`include/nav_item_bridge.h`). Alle Komponenten kommunizieren ausschließlich über wohldefinierte Wert-Structs:

```text
                       BridgeTickInput (20 Hz, pro Bot)
                                     │
         ┌───────────────────────────┼───────────────────────────┐
         ▼                           ▼                           ▼
┌─────────────────────┐   ┌─────────────────────┐   ┌─────────────────────────┐
│ 1. COMBAT-KI        │   │ 2. PFADKOSTEN-CACHE │   │ const navlab::NavGraph  │
│ HumanBotPolicy      │──▶│ WorldPathEnricher   │◀──│ (1x pro Map, read-only, │
│ WANN kämpfen?       │   │ + PathCostCache     │   │  0 mutierbarer State)   │
│ Aim / Fire / Weapon │   └──────────┬──────────┘   └────────────┬────────────┘
└─────────┬───────────┘              │                           │
          │ ThreatState +            ▼                           │
          │ CombatContext ┌─────────────────────┐                │
          └──────────────▶│ 3. ITEM-UTILITY     │                │
                          │ ItemPlanner         │                │
                          │ WELCHES Ziel lohnt? │                │
                          └──────────┬──────────┘                │
                                     │ NavGoal / Cancel / Poll   │
                                     ▼                           │
                          ┌─────────────────────┐                │
                          │ 4. NAVIGATION 2.0   │◀───────────────┘
                          │ NavGraphSink (Goal) │
                          │ NavAgent (Patrol)   │
                          │ ObstacleRecovery    │
                          │ WIE ans Ziel kommen?│
                          └──────────┬──────────┘
                                     ▼
                          ┌─────────────────────┐
                          │ 5. ARBITRIERUNG     │
                          │ ArbitrateCommands() │
                          │ -> BotDriverIntent  │
                          │ -> ArbitrationTrace │
                          └─────────────────────┘
```

### Harte Invarianten der Schichten-Trennung
- **Waffenhoheit:** `BotDriverIntent::weapon` stammt **immer** aus `HumanBotPolicy` (`bot_loadout.h`), niemals aus Navigation oder Item-Planer.
- **Feuerdisziplin (`fire`-Hygiene):** Sobald Navigation (`kItemNavigation`, `kPatrolNavigation`), Überlebens-Rückzug (`kSurvivalRetreat`) oder `kObstacleRecovery` die Blickrichtung (`yaw_delta_deg`) steuert, erzwingt `ArbitrateCommands` strikt `intent.fire = false`. Ein Bot feuert niemals blind in Richtung eines Waypoints oder einer Wand.
- **Null Rückkopplung in fremde Interna:** Weder `HumanBotPolicy` noch `ItemPlanner` noch `NavGraph` werden verändert oder über verdeckte globale Variablen gekoppelt.

---

## 3. Zielübersetzung (`NavGoal` → Navigation 2.0) (Aufgabe 3)

`navbridge::NavGraphSink` (`include/nav_goal_sink.h`) implementiert `itemai::NavigationSink` vollständig:

1. **`Submit(const NavGoal& goal)`:**
   - Löst über `TrueItemTable` die exakte 3D-Weltposition `true_pos_` des Items auf (unabhängig von einer etwaigen Pfadkosten-Projektion in `adapted_world_`).
   - Ist dasselbe `goal_id` am selben Ort bereits aktiv (`kAccepted` / `kInProgress`), erfolgt ein **idempotentes Update** von Ablaufzeit (`expires_tick`), Priorität und Geschwindigkeitsfaktor ohne unnötige A*-Neusuche.
   - Andernfalls werden Start- und Ziel-Ankerknoten via `graph.NearestNode(..., max_anchor_dist_m)` bestimmt und eine budgetierte Suche über `ConstrainedNavSearch` gestartet.
   - Bei unverbundenem Zielknoten oder fehlendem Anker liefert `Submit` sofort `NavStatus::kUnreachable`.
2. **`Poll(int goal_id, NavFeedback* out)`:**
   - Prüft in fester Reihenfolge: (a) Teleport-/Respawn-Sprung `> 8 m` → Replan, (b) 3D-Ankunft `Distance(bot_pos_, true_pos_) <= arrive_radius_m` → `NavStatus::kArrived`, (c) Zeitüberschreitung `goal.Expired(tick)` → `NavStatus::kExpired`, (d) Epoch-Wechsel des Graphen oder der lokalen Kanten-Sperrtabelle → sofortiger Replan, (e) Fortsetzung budgetbegrenzter Teilrouten (`partial_route_`), (f) Auslieferung eines anstehenden `NavStatus::kStalled`-Signals.
3. **`StepGoalMove(...)` (Endanflug-Garantie):**
   - Verfolgt Zwischen-Waypoints mit Segment-Projektion (verhindert Umkreisen bei hohem Tempo) und schaltet auf dem letzten Routenabschnitt innerhalb von `2,2 × arrive_radius_m` direkt auf die exakte Item-Position `true_pos_` um, sodass der Pickup-Radius (`1,5 m`) zuverlässig getroffen wird.
   - Respektiert `goal.max_speed_frac` sowie `goal.allow_jump` (`kEdgeJump` → `jump_hint`).

---

## 4. Erreichbarkeit und echte Graph-Pfadkosten (Aufgabe 4)

Da `poc/research/item-utility` read-only ist und `itemai::EvaluateItem` intern `Distance(w.self.eye, it.pos)` liest, reichert `WorldPathEnricher` (`include/nav_cost_cache.h`) einen lokalen `ItemSnapshot`-Puffer vor `ItemPlanner::Step` kostengetreu an:

- **`PathCostCache` (128 Einträge, 2-Wege-satzassoziativ):**
  Speichert pro `(start_node, goal_node, combined_epoch)` das Tupel `{reachable, second_node, cost_from_second_m, total_graph_cost_m}`.
  Solange sich der Bot in derselben Start-Zelle bewegt, entsteht **kein einziger erneuter A*-Aufruf** (`0` Expansionen, `~86–95 %` Cache-Trefferquote im Dauerbetrieb), während sich die Restdistanz
  `d_eff = PlanarDistXZ(bot, second_node) + cost_from_second_m + PlanarDistXZ(goal_node, item_pos)`
  dennoch jeden Tick kontinuierlich und glatt aktualisiert.
- **Pfadkosten-Projektion (`ProjectAlongRay`):**
  Ist ein Item erreichbar und `d_eff > d_euclid`, wird `adapted_items[i].pos` entlang des Richtungsstrahls vom Bot-Auge auf den Abstand `d_eff` projiziert; gleichzeitig merkt sich `TrueItemTable` die unveränderte Originalposition `true_pos` für `NavGraphSink` und Telemetrie. Damit bewertet `ItemPlanner` die **reale A*-Reisezeit** (inkl. gesperrter Türen `kEdgeBlocked` und lokaler Kanten-Sperren), ohne dass PR #55 modifiziert werden muss.
- **Fail-Closed-Durchreichung:**
  Enthält `raw_world` ungültige Eingaben (`NaN`, `Inf`, doppelte IDs, ungültige Waffenindizes), gibt `WorldPathEnricher` die Rohdaten unverändert weiter, sodass `itemai::ValidateWorld` deterministisch mit `ItemReason::kInvalidWorld` abbricht.

---

## 5. Prioritätswechsel, Hysterese und Zielkonflikte (Aufgabe 5)

Prioritätsentscheidungen folgen einer klaren, zyklenfreien Hierarchie in `ArbitrateCommands` (`include/bridge_arbitrator.h`):

1. **`kDeadIdle` (`!alive || !deathmatch`):** Null-Bewegung, kein Feuer, Zustands-Reset beim Tod.
2. **`kSurvivalRetreat` (`visible_combat && item_dec.has_goal && item_dec.suppress_combat && goal_move.active`):** Kritische Überlebenssuche (`health_frac < 0.35` auf Health/Armor, sofern kein Nahkampf-`ThreatAbort` greift) übersteuert das offene Duell; `fire = false`, Flucht entlang der A*-Route zum Medkit.
3. **`kCombat` (`visible_combat`):** Sichtbarer Gegner hat Vorrang vor opportunistischer Item-Suche (`kVisibleEnemyCombatLeads` bzw. `kCombatPreemptedItemGoal`). `HumanBotPolicy` steuert Zielen, Feuern und Strafe-Distanzband.
4. **`kItemNavigation` (`item_dec.has_goal && goal_move.active`):** Kein sichtbarer Gegner; `NavGraphSink` führt den Bot auf dem A*-Pfad zum gewählten Item. Hysterese (`commit_margin` + Mindest-Bindungsdauer `min_commit_s` in `ItemPlanner`) verhindert Ziel-Flattern bei fast gleichwertigen Items (`M03_HysteresisPreventsGoalThrashing`: `0` Wechsel).
5. **`kPatrolNavigation` (`has_waypoint_graph && patrol_cmd.active`, sonst `kMaplessScan`):** Kein aktives Item-Ziel; `navlab::NavAgent` übernimmt `kReposition` zum zuletzt gesehenen Gegner (`kRememberedEnemyReposition`) oder `kPatrol` (`kPatrolExplore`). Ohne Waypoint-Graph greift nahtlos die bestehende Scan-Drehung (`kMaplessScan`).
6. **Unterlagerte reaktive Wand-Befreiung (`kObstacleRecovery`):** Greift nur bei unmittelbarem Wandkontakt (`front < 1.2 m` / physischer Stillstand) ein und gibt die Steuerung nach maximal 6 freien `Advance`-Ticks (`~3,5 m`) sofort wieder an A* zurück.

---

## 6. Unerreichbare Items & Vermeidung von Re-Search-Stürmen (Aufgabe 6)

Unerreichbare Ziele werden zweistufig abgefangen:
1. **Vorab-Erkennung im `WorldPathEnricher`:** Liegt ein Item zu weit abseits jedes Waypoints (`NearestNode == -1`, `off_mesh_unreachable`) oder auf einer abgetrennten Graph-Komponente (`NavSearchStatus::kUnreachable`, z. B. erhöhte Plattform ohne Sprung-/Lift-Kante), speichert `PathCostCache::StoreUnreachable` das negative Ergebnis für `unreachable_cache_ttl_ticks` (Standard: `200` Ticks = `10 s`) und setzt `adapted_items[i].reachable = false`. In Folge-Ticks entstehen **0 erneute A*-Probes** (`S06`: `t2_reprobes = 0`).
2. **Langzeit-Blacklist im `ItemPlanner`:** Meldet `NavGraphSink` während einer laufenden Zielansteuerung `NavStatus::kUnreachable` (etwa nach dynamischer Türschließung via `BumpGraphEpoch`), sperrt `ItemPlanner::FinishGoal` das Item für `consumable_blacklist_s + 30 s` in seiner internen Blacklist.

---

## 7. Kopplung von Stuck-Recovery und Item-Suche (Aufgabe 7)

Ein reales Problem bei reiner `(x, z)`-Positionsüberwachung ist das **seitliche Wand-Gleiten**: Wenn `ObstacleRecovery` um 90° abdreht und parallel an einer unkartierten Barriere entlangläuft, legt der Bot mehr als `1 m` zurück, ohne dem Ziel näherzukommen. `NavGraphSink::StepGoalMove` kombiniert daher **drei Detektoren**:
1. Klassisches planares Stuck-Fenster (`d < stuck_min_dist` über `stuck_window`),
2. Ziel-Fortschritts-Überwachung (`rem_now` sinkt über `stall_win` Ticks nicht um mindestens `0,75 m`),
3. Direkte Front-Blockade (`front_obstacle_m < 1.2 m` bei `>= 12` Ticks ohne Fortschritt).

**Zweistufige Reaktion beim Auslösen (`S08`):**
- **Fall A — Alternativroute existiert (`S08A`):** `BlockCurrentSegment` trägt die blockierte Kante lokal in `LocalBlockedEdgeTable` ein (pro Bot, mit TTL, **ohne** den gemeinsamen `const NavGraph` zu verändern), setzt `ObstacleRecovery` zurück und plant sofort auf die freie Umgehungsroute um (`detour_pickup_t = 172`).
- **Fall B — Einziger Korridor vollständig versperrt (`S08B`):** Lässt das probeweise Sperren der Kante überhaupt keinen Pfad mehr übrig, nimmt `NavGraphSink` die Sperre für den ersten Versuch zurück und sendet `NavStatus::kStalled` (Strike 1), damit `ObstacleRecovery` eine echte Befreiungschance an einer bloßen Mauerkante erhält. Scheitert auch der zweite Anlauf, sendet `NavGraphSink` den zweiten `NavStatus::kStalled` (Strike 2): `ItemPlanner` bricht das Ziel regulär mit `ItemReason::kStalled` ab, setzt Cooldowns, und `NavGraphSink::Cancel` verankert die Sackgassen-Sperre in `LocalBlockedEdgeTable`.

---

## 8. Abbruch bei Gegnerkontakt und Beschuss/Schaden (Aufgabe 8)

`DeriveThreatAndCombat` (`include/bridge_arbitrator.h`) übersetzt den Zustand von `HumanBotPolicy` und `DamageTracker` in `itemai::ThreatState` und `itemai::CombatContext`:
- **Sichtbarer Gegner im Kampfband (`<= 1,5 × preferred_range_m`):** `combat_priority >= 0.88` überschreitet `combat_lock_priority` aller sechs Persönlichkeiten → gesunde Bots brechen opportunistische Item-Wege sofort mit `ItemReason::kCombatLock` ab (`S04`), `NavGraphSink::Cancel` räumt die Route ab, und `ControllerOwner::kCombat` übernimmt Zielen & Feuern.
- **Poke-Distanz (`> 1,5 × preferred_range_m`):** Die Prioritätsformel skaliert über Aggression und Caution (`Aggressor ~ 0,70` vs. `Survivor ~ 0,83`), sodass vorsichtige Persönlichkeiten eher auf Distanz sichern, während Aggressoren früher in den Kampf gehen.
- **Beschuss / Schaden während der Navigation (`S05`):**
  - Verliert ein Bot auf einem opportunistischen Item-Weg innerhalb von `damage_window_s` mehr als `abort_damage_frac` seiner Maximal-HP (`S05A`), bricht `ItemPlanner` die exponierte Route mit `ItemReason::kDamageAbort` ab (`under_fire = true`), während `HumanBotPolicy::NotifyDamage` das Schadens-Aufmerksamkeitsfenster aktiviert.
  - Ist der Bot dagegen kritisch verwundet (`health_frac < 0.35`, `S05B`) und ein erreichbares Medkit in Reichweite, setzt `ItemPlanner` `suppress_combat = true` → `ControllerOwner::kSurvivalRetreat` priorisiert den Rückzug zum Medkit über das Feuergefecht.

---

## 9. Persönlichkeit (6 Personas) & Skill-Stufen (Tiers 1–5) (Aufgabe 9)

`BuildBridgeProfile` (`include/nav_item_bridge.h`) erzeugt aus `(tier, persona, base_seed, slot)` konsistent:
- `botcore::BotProfile` (Kampf, Wahrnehmung, Aim, Waffenpräferenz),
- `itemai::ItemProfile` (Planungshorizont `2,5..13,0 s`, Disziplin, Risiko-Bewusstsein vs. Gewichtungen `w_health`, `w_weapon`, `w_armor`, `w_strategic`),
- `navlab::NavPersonality` (`turn_rate_deg_s` strikt aus `bp.skill.turn_rate_deg_s`; `walk_factor`, `explore_bias`, `deadend_aversion` strikt aus `bp.personality`).

**Bewiesene 3-Schichten-Orthogonalität (`C02_SkillOrthogonalAcross3Layers`):**
Über alle `5 Tiers × 6 × 6 = 180` Paare verändert ein Wechsel der Persönlichkeit bei festem Tier **keinen einzigen mechanischen Skill-Parameter** (weder Aim/Reaktion in `botcore`, noch `ItemSkillBlock` in `itemai`, noch die maximale Drehgeschwindigkeit `turn_rate_deg_s` in `navlab`). Gleichzeitig treffen `Aggressor` (wählt Waffen-Upgrade `1002`) und `Survivor` (wählt Medkit `1001`) bei identischer Weltlage und identischem Tier reproduzierbar unterschiedliche strategische Entscheidungen (`S10`).

---

## 10. Mehrbot-Konkurrenz ohne geteilten mutierbaren Zustand (Aufgabe 10)

- **100 % zustandsfreie gemeinsame Kartendaten:** Alle Bots erhalten ausschließlich `const navlab::NavGraph&`. Lokale Kanten-Sperren (`LocalBlockedEdgeTable`), Pfadkosten-Caches (`PathCostCache`), A*-Arbeitsfelder (`ConstrainedNavSearch`) und Zielzustände liegen vollständig privat in der jeweiligen `NavItemBridgeAgent`-Instanz.
- **Byteweise Unveränderlichkeit & Reihenfolge-Invarianz:**
  - `M01_EightBotContentionAndGraphImmutability` prüft per 64-Bit-FNV-1a-Speicherhash über `sizeof(navlab::NavGraph)`, dass sich kein einziges Byte des Graphen nach `600` Ticks mit `8` kämpfenden und sammelnden Bots verändert.
  - `M02_SlotStepOrderIndependence` beweist, dass die Auswertungsreihenfolge (`Agent A` vor `Agent B` vs. `Agent B` vor `Agent A`) bit-identische `BotDriverIntent`-Ströme erzeugt.
- **Saubere Ziel-Invalidierung bei Konkurrenz (`S09`):** Laufen zwei Bots auf dasselbe MegaHealth (`id=901`) zu, nimmt der nähere Bot 0 das Item auf (`respawn_s = 25 s`). Im unmittelbar nächsten Tick erkennt Bot 1 über den regulären Welt-Snapshot, dass `respawn_s` seinen Warte-Horizont übersteigt, verwirft `901` ohne Leerlauf-Campen und schwenkt sofort auf das sekundäre Medkit (`id=902`) um.
