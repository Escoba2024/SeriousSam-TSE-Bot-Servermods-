# Deliverable 1: Priorisierter Fehlerbericht (`integration-qa-20261026`)

## Schweregrad-Definitionen

- **BLOCKER:** Verhindert eine valide Gesamtbeurteilung als zusammengeführtes Integrationsartefakt oder verletzt harte Sicherheits-/Prozessgrenzen.
- **P0 (Kritisch / Merge-Stopper):** Führt reproduzierbar zu Bewegungs-Deadlocks, mehrsekündiger Kampfunfähigkeit bei sichtbarem Gegner, komplettem Ausfall von Item-/Waffenentscheidungen unter gültigen Retail-1.07-Spielzuständen, Umgehung reservierter Human-Slots oder direkter Eingabeinjektion.
- **P1 (Hoch):** Erzeugt relevante Fehlentscheidungen, widersprüchliche Mehrfachlogik zwischen PRs, defekte Feature-Flags, Server-übergreifende Leave-Blockaden, Stack-/Sync-Risiken oder gravierende Testlücken (inkl. vakuöser Determinismus-Tests).
- **P2 (Mittel):** Lokale Logik-/Grenzfallfehler mit messbarer Verschlechterung in spezifischen Spielsituationen (Nahkampf-Pinning < 8 m, Waffenbereitschaft außerhalb des Kampfes, Ringpuffer-Off-by-One, falscher Horizont-Parameter).

## Zusammenfassende Prioritätstabelle

| ID | Priorität | Prüfbereich(e) | Betroffene PRs | Kurzbeschreibung | Evidenzstatus |
| :--- | :---: | :--- | :--- | :--- | :--- |
| **`INT-BLOCKER-01`** | **BLOCKER** | Gesamtintegration / Governance | `#67, #57, #63, #50, #58` | Kein zusammengeführter Codex-Integrations-PR vorhanden; PR #67 liefert nur M1/C1/C2 als `.patch`/Offline-Gates (`PARTIAL_DELIVERY`), M4–M8 unintegriert; PR #57 kollidiert mit PR #63 | `[IMPL-VERIFIED]`, `NOT_TESTED_RETAIL` |
| **`QA-01`** | **P0** | (3) Nav/Combat, (8) Reg. ggü. #45 | `#57` (`#69` Naht) | Ungeflaggter `>45°`-Drehstopp bei Zielverfolgung setzt `ObstacleRecovery` in `BotDriver.cpp` endlos zurück (Wand-Oszillation); `exploratory_search_` annulliert sich bei `>35°` selbst | `[IMPL-VERIFIED]`, `[OFFLINE-PROVED]` (`R01`, `R02`), `NOT_TESTED_RETAIL` |
| **`QA-02`** | **P0** | (1) Combat, (3) Nav/Combat, (8) Reg. ggü. #45 | `#57` + `#69` | Ungeflaggtes `escape_active_` macht Bots nach `>=25` Schaden für 100 Ticks (`5,0 s`) blind gegenüber sichtbaren Angreifern; mit PR #69 entsteht ein 3-Wege-Widerspruch (`engaged=1`, `escape=1` -> `owner=kPatrolNavigation`, `fire=0`) | `[IMPL-VERIFIED]`, `[OFFLINE-PROVED]` (`R03`, `R04`, Live-Probe), `NOT_TESTED_RETAIL` |
| **`QA-03`** | **P0** | (3) Nav/Combat, (4) Items | `#54` + `#69` | Rein planares 2D-`NearestNode(x, z)` ignoriert `Y`-Koordinate: Items auf oberen Etagen werden auf Erdgeschoss-Knoten gemappt (`probes_executed=0`), Bot friert unter der Decke ein | `[IMPL-VERIFIED]`, `[OFFLINE-PROVED]` (`R09`, Live-Probe), `NOT_TESTED_RETAIL` |
| **`QA-04`** | **P0** | (4) Items, (1) Combat | `#55` + `#69` | Vier Verstöße gegen Retail-1.07-Waffen-/Item-Regeln: Overheal/Overarmor (`>100`) bricht `ItemPlanner` mit `kInvalidWorld` ab; Colt ohne Munition deaktiviert; Double Shotgun mit 1 Shell erlaubt; geteilter Bullets-Pool & `gam_bInfiniteAmmo=1` ignoriert | `[IMPL-VERIFIED]`, `[OFFLINE-PROVED]` (`R10`, `R11`, `R12`, Live-Probe), `NOT_TESTED_RETAIL` |
| **`QA-05`** | **P0** | (9) Sessions, Security | `#57` + `#68` | Session-Namensnormalisierung bricht bei doppelten `"Serious Sam"`-Standardnamen und Unicode-Spielernamen (`snapshot() -> None`, deaktiviert `reserved_human_slots`); PR #57 übersieht `^aXX/^o/^R`; PR #68 hat defekte doppelt escapte Whitelist-Regex (`'Bot"; Quit(); //'` passiert ungefiltert) | `[IMPL-VERIFIED]`, `[OFFLINE-PROVED]` (`test_qa05a/b/c`, Live-Audit), `NOT_TESTED_RETAIL` |
| **`QA-06`** | **P1** | (9) Sessions | `#57` + `#68` | `JOINING -> LEAVING` bei im Hauptmenü hängendem Client (`alive=True, connected=False`) verharrt dauerhaft in `"wait_leave_ready"`; globales `any(status=="LEAVING")` blockiert Leaves auf **allen** Servern | `[IMPL-VERIFIED]`, `[OFFLINE-PROVED]` (`test_qa06`, Live-Audit), `NOT_TESTED_RETAIL` |
| **`QA-07`** | **P1** | (4) Items, (3) Nav | `#69` (`#55`) | Nicht geprobte Items jenseits `max_cost_probes_per_tick=8` behalten `reachable=true` und euklidische Luftlinie — unpassierbare Items hinter Wänden gewinnen die Utility-Wahl | `[IMPL-VERIFIED]`, `[OFFLINE-PROVED]` (`R14`), `NOT_TESTED_RETAIL` |
| **`QA-08`** | **P1** | (2) Doppelte Logik, (3) Nav | `#69` (`#54`) | Doppelte Patrol-Zustandsmaschine in `NavItemBridgeAgent`: `Remaining() >= 256` nutzt `patrol_agent_` (ignoriert `local_blocked_`), `< 256` nutzt `budgeted_patrol_route_` (verliert `kReposition`) | `[IMPL-VERIFIED]`, `[OFFLINE-PROVED]` (`R15`), `NOT_TESTED_RETAIL` |
| **`QA-09`** | **P1** | (2) Doppelte/widersprüchliche Logik | `#45, #55, #57, #63, #66, #68, #69` | Drei widersprüchliche Waffenscorer (40 m: Item wählt Laser `12`, Combat 2.0 wählt Sniper `13`), Persona-Leck in `PlanRespawn`/`AlertGatePasses`, Kollision PR #57 vs. #63 in `redstation_preset.py`, verlorene Normalisierung in PR #68 `validate_config` | `[IMPL-VERIFIED]`, `[OFFLINE-PROVED]` (`R16`, `test_qa09`, Live-Audit), `NOT_TESTED_RETAIL` |
| **`QA-10`** | **P1** | (7) Feature-Flags, (8) Reg. ggü. #45 | `#57, #66, #69` | Unvollständige Feature-Flags: `bot_bExploratorySearch` & `bot_bCecilP1` nur beim Erst-Attach gelesen, fehlen in `NoteConfigOnce`, kein Setter in `HumanBotPolicy` / `NavItemBridgeAgent`, `validate_config` lehnt `cecil_p1` ab, `startup_script` lässt 4 CVars weg | `[IMPL-VERIFIED]`, `[OFFLINE-PROVED]` (`test_qa10`, Live-Audit), `NOT_TESTED_RETAIL` |
| **`QA-11`** | **P1** | (1) Combat-AI, (8) Reg. ggü. #45 | `#45, #57, #66` | Waffenwechsel-Draw-Unterdrückung in `BotDriver.cpp` blockiert `PLACT_FIRE`, während `HumanBotPolicy` intern `next_shot_tick_` bereits abbucht (Sniper verliert `0,90 s` beim ersten Schuss); 50-ms-Release für Cannon/Grenade `NOT_TESTED_RETAIL` | `[IMPL-VERIFIED]`, `[OFFLINE-PROVED]` (`R05`), `NOT_TESTED_RETAIL` |
| **`QA-12`** | **P1** | (5) Sync, (6) CPU/RAM/Stack | `#54, #62, #63, #65, #68, #69` | `ArenaSim` (`927,34 KiB`) gefährdet 1-MiB-PE-Thread-Stack; uncached `NearestNode` kostet `1,02 ms/Tick` ohne Raycasts; unbudgetierte Item-LOS-Raycasts (`5.120 Rays/s`) & PR #63 `cmd_cmdOnTick` bergen `SYNCLATE`/`SYNCBAD`-Risiko; Arch B übersteigt Hetzner-RAM bei 16 Bots | `[IMPL-VERIFIED]`, `[OFFLINE-PROVED]`, `NOT_TESTED_RETAIL` |
| **`QA-13`** | **P2** | (1) Combat, (3) Nav, (4) Items | `#45, #55, #57, #69` | Vier Detailfehler: (a) `distance<=8.0f` killt `ObstacleRecovery` im Nahkampf; (b) `WeaponSelector` behält leere Waffe außerhalb des Kampfes & `BotDriver` ignoriert Fallback-Waffe bei `target<0`; (c) `RouteMemory::MarkHazard` überspringt Slot `0`; (d) `TimeFactor` nutzt `memory_horizon_s` statt `planning_horizon_s` | `[IMPL-VERIFIED]`, `[OFFLINE-PROVED]` (`R06`, `R07`, `R08`, `R13`), `NOT_TESTED_RETAIL` |
| **`QA-14`** | **P1** | (10) Fehlende/unzureichende Tests | `#45, #57, #69` | Kritische Testblinde Flecken: `extract_block.py` schneidet vor `BotDriver.cpp:990-1200` ab; PR #69 `M02` XORt eine gerade Anzahl identischer Tick-Hashes (`50 × X = 0`, vakuöser Pass!) über ungepacktes Padding (`sizeof=40 > 39`); PR #57 nutzt 6-Zeilen-Regex-Tests statt Integrationstests | `[IMPL-VERIFIED]`, `[OFFLINE-PROVED]` (`R17`), `NOT_TESTED_RETAIL` |

---

## Detaildokumentation aller Befunde

---

### `INT-BLOCKER-01` [BLOCKER] — Kein zusammengeführter Codex-Integrationskandidat vorhanden; PR #67 ist ein partielles Offline-Review-/Patch-Paket

1. **Exakte Datei und Funktion:**
   - PR #67 (`66ab832661809ee2a7be405224d4676c835b6dd8`, Draft): `poc/research/master-integration-20261025/FINAL_REPORT.md`, `M1_LIVE_MCP_AUDIT.md`, `C1_SUPERVISOR_PATCH_PROPOSAL.patch`, `M1_MCP_RECEIPT_PATCH.patch`, `c2_sync_gates.py`
   - PR #57 (`6b84c5d283664bc9e968bb4961abf2dd48731c5b`, Draft): `poc/candidates/integrated-human-cpu-20261021/BotDriver.cpp`, `tools/redstation_preset.py`
   - PR #63 (`1e375d8fe71ea10e3a657c4aaf4da1cbc3ac9127`, Draft): `tools/redstation_preset.py`
   - Unintegrierte Subsystem-Branches: PR #54 (`3f2ba8db...`), PR #55 (`72d464ff...`), PR #62 (`d5fcd066...`), PR #65 (`6227222f...`), PR #66 (`48e110a7...`), PR #68 (`7ec04d03...`), PR #69 (`d0c181c6...`)
2. **Reproduzierbarer Fehlerfall:**
   - Abfrage aller offenen/gemergten PRs (`gh pr list --state all`) sowie Dateivergleich zwischen `main` (`ab0c740`) und PR #67 (`git diff --name-only main..66ab8326...`): PR #67 berührt ausschließlich `docs/reviews/master-integration-20261025/` und `poc/research/master-integration-20261025/`. Weder `poc/botcore/` noch `BotDriver.cpp` noch `tools/` enthalten eine zusammengeführte Integration.
3. **Erwartetes Verhalten:**
   - Ein dedizierter Codex-Integrations-PR führt die ausgewählten Subsysteme hinter dokumentierten Feature-Flags konfliktfrei in `poc/botcore/`, `BotDriver.cpp` und `tools/` zusammen, liefert reproduzierbare End-to-End-Offline-Tests über die echte Integrationsnaht und weist vor einer Produktionsfreigabe native Retail-1.07-Belege auf dem qualifizierten Artefakt nach.
4. **Beobachtetes Verhalten:**
   - PR #67 deklariert selbst `PARTIAL_DELIVERY_WITH_EXPLICIT_NATIVE_BLOCKERS` (nur M1/C1/C2 als Offline-Skripte und ungepatchte `.patch`-Dateien; Arbeitspakete M4–M8 offen).
   - PR #57 und PR #63 modifizieren beide `tools/redstation_preset.py` inkompatibel (`"Alpha-Gaming"` ohne `server_startup` vs. `"ssam.ai"` mit `BOT-`-Präfix, `MOTD`, `ANNOUNCEMENT` und `server_startup`).
   - PR #50 (C1 Supervisor) enthält 5 in PR #67 dokumentierte, aber im Quellbranch unbehobene Fehler (u. a. unterminierter `SYNCBAD`-Scan in `DedicatedServer_107.py`, unregistrierte `SeriousSam.exe` außerhalb der cgroup).
   - PR #58 (C2 Sync-Harness) enthält 7 in PR #67 nachgewiesene Validierungslücken (`OPEN`, `NOT_TESTED_RETAIL`).
5. **Technische Ursache (soweit belegbar):**
   - Parallele Erstellung isolierter Research-PRs in `poc/research/*` und `poc/navigation-lab/*` ohne abschließenden Merge-Durchlauf des Hauptagenten und ohne bereinigte Retail-1.07-Baseline auf dem Zielhost (`54faabf0...` statt `7fc94a39...`).
6. **Konkrete Fix-Empfehlung:**
   - Keinen der offenen Einzel-PRs isoliert als „Gesamtintegration“ mergen. Zuerst in einem dedizierten Integrations-Branch die unten dokumentierten P0-/P1-Defekte beheben, `tools/redstation_preset.py` zwischen PR #57 und PR #63 konsolidieren und die `.patch`-Artefakte aus PR #67 real anwenden und testen (siehe Deliverable 7).
7. **Passender Regressionstest:**
   - `poc/research/integration-qa-20261026/run_live_branch_audit.py` prüft automatisiert die gepinnten Git-Commits auf Divergenz (`pr57` vs. `pr63` `redstation_preset.py`) und Nahtstellenbrüche (`#57 + #54 + #55 + #66 + #69`).

---

### `QA-01` [P0] — Ungeflaggter `>45°`-Drehstopp setzt `ObstacleRecovery` in `BotDriver.cpp` endlos zurück (Wand-Oszillation) & `exploratory_search_` blockiert sich ab `35°` selbst

1. **Exakte Datei und Funktion:**
   - PR #57 (`6b84c5d2...`): `poc/botcore/bot_human.h`, `HumanBotPolicy::Step(...)`, Zeilen `268–278` (Suchmodus `>35°`) und Zeilen `338–340` (Verfolgungsmodus `>45°`, **ungeflaggt**)
   - PR #57 (`6b84c5d2...`): `poc/candidates/integrated-human-cpu-20261021/BotDriver.cpp`, Zeilen `952` und `1106` (`if (humanEscapeForward == 0.0f) bs.bs_navigation.Reset();`)
2. **Reproduzierbarer Fehlerfall:**
   - **Fall A (`R01`):** Bot steht bei `(0, 0)` mit Blickrichtung `-Z`, sieht auf Ticks `1..8` kurz einen Gegner bei `(0, -25)` und läuft auf eine `4 m` breite Säule/Wand bei `z = -1.5` (`x in [-2, +2]`) zu, hinter der der Gegner verdeckt ist (`!target_visible`).
   - **Fall B (`R02`):** Bot befindet sich ohne Ziel (`target_ < 0`) mit `exploratory_search_ = true` im Suchschwenk (`search_rate_deg_s * dt` über `10..30` Ticks).
3. **Erwartetes Verhalten:**
   - **Fall A:** `ObstacleRecovery` dreht den Bot um `>= 60°` seitlich von der Wand weg (`Turn` -> `Advance`) und umgeht das Hindernis wie in PR #45.
   - **Fall B:** Während des explorativen Reisens bleibt die Vorwärtsbewegung aktiv oder dreht innerhalb des erlaubten Kegels konsistent zum Marschziel.
4. **Beobachtetes Verhalten (`[OFFLINE-PROVED]`):**
   - **Fall A (`R01`):** In PR #45 umgeht der Bot die Säule problemlos (`PR45_bypass = 1`). In PR #57 dreht `ObstacleRecovery` das Yaw des Bots seitlich von der Wand weg; sobald die Abweichung zur Luftlinie zum verdeckten Gegner `45°` überschreitet, setzt `bot_human.h:338-340` **ungeflaggt** `cmd.forward = 0.0`. Daraufhin ruft `BotDriver.cpp:952,1106` `bs.bs_navigation.Reset()` auf! Der Bot dreht zurück in die Wand, löst erneut `ObstacleRecovery` aus und bleibt in einer Endlosschleife hängen (`PR57_bypass = 0`, `resets = 8`, maximale Querbewegung `0,15 m` in `240` Ticks = `12 s`). Selbst `bot_bExploratorySearch = 0` und `bot_bCecilP1 = 0` schalten diesen Fehler **nicht** ab!
   - **Fall B (`R02`):** In `30 von 40` deterministischen Suchsegmenten überschreitet die akkumulierte Suchdrehung `35°`, wodurch `bot_human.h:274` die gerade gesetzte Reisegeschwindigkeit `cmd.forward = 0.72` selbst wieder auf `0.0` nullt.
5. **Technische Ursache (soweit belegbar):**
   - `HumanBotPolicy` kennt den aktiven Zustand von `bs.bs_navigation` (`ObstacleRecovery`) nicht und interpretiert die durch `ObstacleRecovery` erzwungene Ausweichdrehung (`>45°` weg vom Ziel-Bearing) als „Bot schaut noch nicht zum Ziel, also anhalten“. `BotDriver.cpp` koppelt `bs_navigation.Reset()` direkt an `decision.forward == 0.0f` statt an die ungefilterte Bewegungsabsicht.
6. **Konkrete Fix-Empfehlung:**
   - In `BotDriver.cpp` `bs.bs_navigation.Reset()` **niemals** ausführen, solange `bs.bs_navigation.IsActive()` wahr ist und der Bot lediglich wegen eines Ausweichmanövers vom Ziel-Bearing abweicht.
   - In `bot_human.h:338-340` den `>45°`-Vorwärtsstopp hinter das Feature-Flag legen **und** ein explizites Flag `bool navigation_override_active` im `WorldView` beachten (wenn `true`, kein Nullen von `cmd.forward`).
   - Im Suchmodus (`bot_human.h:256-278`) den Such-Yaw-Sweep auf `<= 30°` relativ zur Marschrichtung begrenzen statt `cmd.forward` nachträglich hart auf `0.0` zu setzen.
7. **Passender Regressionstest:**
   - `poc/research/integration-qa-20261026/test_combat_nav_regressions.cpp`: `TestR01_ChasingTurnFreezeResetsObstacleRecovery` und `TestR02_ExploratorySearchSelfCancelsForwardAbove35Deg`.

---

### `QA-02` [P0] — Ungeflaggtes 100-Tick-`escape_active_` macht Bots für 5,0 s blind gegenüber sichtbaren Angreifern & erzeugt mit PR #69 einen 3-Wege-Arbitrierungsbruch

1. **Exakte Datei und Funktion:**
   - PR #57 (`6b84c5d2...`): `poc/botcore/bot_human.h`, `HumanBotPolicy::BeginTick(...)` Zeilen `124–134` und `HumanBotPolicy::Step(...)` Zeilen `226–242`
   - PR #69 (`d0c181c6...`): `poc/research/nav-item-bridge/include/bridge_arbitrator.h`, `DeriveThreatAndCombat(...)` Zeilen `250–269` und `ArbitrateCommands(...)` Zeilen `295–355`
2. **Reproduzierbarer Fehlerfall:**
   - Ein Bot läuft mindestens 10 Ticks (`history_count_ >= 2`, da Breadcrumbs bei `tick % 5 == 0` geschrieben werden) ohne aktives Ziel (`target_ == -1`). Auf Tick 11 taucht ein Gegner in `10 m` Entfernung mit freier Sichtlinie (`los = true`) direkt vor ihm auf und verursacht `>= 25 HP` Schaden (z. B. `90 -> 60 HP`, eine einzelne Shotgun-/Rocket-/Sniper-Treffersalve).
3. **Erwartetes Verhalten:**
   - Da der Angreifer in klarem Sichtfeld (`los = true`) steht, erfasst `Perception` ihn sofort im selben Tick; der Bot wählt ihn als `target_`, richtet das Feuer auf ihn oder führt einen kontrollierten Rückzug **mit** Gegenfeuer bzw. korrektem Survival-Routing aus. Bei deaktivierten Zusatzflags (`bot_bExploratorySearch = 0`, `bot_bCecilP1 = 0`) muss exakt das Verhalten von PR #45 erhalten bleiben.
4. **Beobachtetes Verhalten (`[OFFLINE-PROVED]`):**
   - **Isoliert in PR #57 (`R03`):** PR #45 gibt in den folgenden `100` Ticks **`32` Schüsse** auf den sichtbaren Angreifer ab. PR #57 setzt `escape_active_ = true` für `escape_until_ = tick + 100` (`5,0 s`), bricht `Step()` in Zeile `240` vor `ChooseTarget()` mit `cmd.target = -1, cmd.fire = false` ab und gibt **`0` Schüsse** ab — **selbst wenn `exploratory_search = false` und `cecil_p1 = false` gesetzt sind**! (Dies deckt sich kausal mit der Beobachtung in PR #57 `BOT_AI2_VERIFICATION.md` Lauf `AI2-B4`, in dem der Bot über `614 s` `0` eigene Kills erzielte.)
   - **Kombiniert mit PR #69 (`R04` + Live-C++-Probe):** Es entsteht ein **3-Wege-Zustandswiderspruch** über volle `100` Ticks:
     1. `DeriveThreatAndCombat` liest `policy.perception()` (das in `Step()` vor Zeile `226` aktualisiert wurde) und meldet an `ItemPlanner`: **`combat.engaged = true`** -> Item-Verfolgung wird abgebrochen!
     2. `HumanBotPolicy` liefert: **`cmd.escape = true, cmd.target = -1, cmd.fire = false`**.
     3. `ArbitrateCommands` kennt `cmd.escape` nicht, prüft `combat_cmd.target >= 0 && combat_cmd.target_visible` (`false!`), verwirft den Escape-Vektor komplett und übergibt die Steuerung an **`ControllerOwner::kPatrolNavigation` mit `fire = false`** — der Bot patrouilliert wehrlos (`0` Schüsse) auf den sichtbaren Schützen zu!
5. **Technische Ursache (soweit belegbar):**
   - In `BeginTick()` (Zeile `124`) wird `saw_threat` anhand des **Vor-Tick-Ziels** (`target_ >= 0 && perception_.Visible(target_)`) geprüft, **bevor** `Step()` die aktuellen `SenseInput`-Sichtlinien des laufenden Ticks verarbeitet. Und in `Step()` (Zeile `226`) wird `escape_active_` **nicht** abgebrochen, wenn `perception_` nun einen sichtbaren Gegner (`VisibleCount() > 0`) erkennt. Zudem fehlt in Zeile `128` jegliche Feature-Flag-Prüfung, und `ArbitrateCommands` in PR #69 wertet `combat_cmd.escape` nicht aus.
6. **Konkrete Fix-Empfehlung:**
   - In `bot_human.h`:
     1. `escape_active_` zwingend hinter ein explizites Feature-Flag stellen (bei Flag `0` = striktes PR-#45-Verhalten).
     2. Die Auslösung von `escape_active_` erst **nach** `perception_.Observe(...)` und `ChooseTarget(w.tick)` entscheiden — und `escape_active_` sofort beenden (`escape_active_ = false`), sobald ein sichtbarer Gegner (`chosen >= 0 && perception_.Visible(chosen)`) erkannt wird.
   - In `bridge_arbitrator.h` (PR #69): Wenn `combat_cmd.escape` aktiv ist, darf `ArbitrateCommands` niemals auf `kPatrolNavigation` zurückfallen, sondern muss konsistent mit `DeriveThreatAndCombat` entweder `kCombat` (bei sichtbarem Gegner) oder `kSurvivalRetreat` ausführen.
7. **Passender Regressionstest:**
   - `test_combat_nav_regressions.cpp`: `TestR03_BlindEscapeBlocksVisibleCombatFor100Ticks`, `TestR04_BridgeArbitrationFlipsVisibleAmbushToPatrol` sowie Live-Probe #1 in `run_live_branch_audit.py`.

---

### `QA-03` [P0] — Rein planares 2D-`NearestNode(x, z)` verursacht Multi-Floor-Deadlock unter Decken und Galerien

1. **Exakte Datei und Funktion:**
   - PR #54 (`3f2ba8db...`): `poc/navigation-lab/nav_graph.h`, `NavGraph::NearestNode(double x, double z, uint32_t exclude_flags = 0)` Zeilen `161–185`
   - PR #69 (`d0c181c6...`): `poc/research/nav-item-bridge/include/nav_cost_cache.h`, `AnchorNode(...)` / `WorldPathEnricher::Enrich(...)` Zeilen `808–827, 895–915` (`PlanarDistXZ`) sowie `nav_goal_sink.h` Zeilen `177–180, 246, 443, 606`
2. **Reproduzierbarer Fehlerfall:**
   - Zweistöckige Deathmatch-Geometrie (Galerie/Brücke über Erdgeschoss): Erdgeschoss-Knoten `n0 = (10, 0, 10)`, Rampe über `n1..n3` (`44 m` Pfadlänge) hinauf zu Galerie-Knoten `n4 = (10, 8, 10)`. Bot steht unten bei `(10, 0, 10)`, ein Rocket Launcher liegt direkt darüber auf der Galerie bei `(10, 8, 10)`.
3. **Erwartetes Verhalten:**
   - Der Bot wird auf `n0 (Y=0)` geankert, das Item auf `n4 (Y=8)`. `WorldPathEnricher` berechnet die reale Rampendistanz (`~44 m`) per A*, und `NavGraphSink` führt den Bot über `n0 -> n1 -> n2 -> n3 -> n4` auf die obere Etage.
4. **Beobachtetes Verhalten (`[OFFLINE-PROVED]`):**
   - `NearestNode(10.0, 10.0)` akzeptiert gar keinen `y`-Parameter und liefert bei identischem `(x, z)` den zuerst eingefügten Knoten `n0` sowohl für den Bot als auch für das `8 m` höher liegende Item!
   - Da `bot_node == item_node == n0`, führt `Enrich()` **`0` A*-Probes** aus (`probes_executed = 0`) und bewertet die Distanz als `8 m` Luftlinie statt `44 m` Rampenweg.
   - `NavGraphSink` meldet sofort im ersten Tick „letzter Wegpunkt `n0` erreicht“ (`PlanarDistXZ == 0 < 1,25 m`), während die echte 3D-Pickup-Distanz `8,0 m > 1,5 m` beträgt. In unserer Live-Probe gegen PR #54 + PR #69 setzt der Agent `goal_id = 77` mit `intent.forward = 0.00` und bleibt dauerhaft unter der Decke stehen, bis der Stuck-Watchdog greift.
5. **Technische Ursache (soweit belegbar):**
   - `NavGraph` speichert zwar `y` in `NavNode`, ignoriert `y` aber vollständig in `NearestNode` sowie in allen Anker- und Wegpunkterreichungsprüfungen (`PlanarDistXZ` in `nav_cost_cache.h` und `nav_goal_sink.h`). PR #69 enthält keinen einzigen Test mit zwei Knoten auf gleicher `(x, z)`-Position bei unterschiedlichem `y`.
6. **Konkrete Fix-Empfehlung:**
   - `NearestNode3D(double x, double y, double z, double max_step_up_m = 1.6, double max_drop_m = 2.5, double vertical_weight = 4.0)` einführen: Knoten mit `node.y - y > max_step_up_m` (unerreichbar oberhalb ohne Kante) dürfen nicht als direkter Start-Anker gewählt werden; für Ziel-Items muss `|node.y - item.y| <= 1.8 m` gelten.
   - In `NavGraphSink` Wegpunkt-Ankunft nur akzeptieren, wenn zusätzlich `|bot.y - wp.y| <= 1.8 m` erfüllt ist.
7. **Passender Regressionstest:**
   - `test_item_multifloor_regressions.cpp`: `TestR09_MultiFloorPlanarNearestNodeDeadlock` und Live-Probe #2 in `run_live_branch_audit.py`.

---

### `QA-04` [P0] — Vierfache Verletzung der Serious-Sam-TSE-1.07-Item-, Overheal- und Munitionsverträge

1. **Exakte Datei und Funktion:**
   - PR #55 (`72d464ff...`):
     - `poc/research/item-utility/include/item_snapshot.h`, `ValidateWorld(...)` Zeilen `187–190`
     - `poc/research/item-utility/include/item_scoring.h`, `HealthNeed(...)` / `ArmorNeed(...)` / `AmmoNeed(...)` Zeilen `138–165`
     - `poc/research/item-utility/include/item_weapons.h`, `WeaponAmmoTable` / `UsableWeaponMask(...)` Zeilen `40–88`
   - PR #69 (`d0c181c6...`): `poc/research/nav-item-bridge/include/nav_item_bridge.h`, `Step(...)` Zeilen `252–259`
   - PR #45 / PR #57: `poc/candidates/integrated-human-cpu-20261021/BotDriver.cpp` Zeile `912`
2. **Reproduzierbarer Fehlerfall:**
   - **(a) Overheal / Overarmor:** Ein Bot sammelt im Deathmatch eine einzelne TSE Health Pill (`+1 HP` -> `101 / 100 HP`), MegaHealth (`200 / 100 HP`) oder Strong/Super Armor (`101..200 / 100 Armor`) ein — oder steht mit `100 / 100 HP` direkt neben einem MegaHealth (`+100` bis `200 HP`).
   - **(b) Colt-Reserve:** Ein frisch gespawnter Bot besitzt Knife (`1`) und Single Colt (`2`) mit `ammo[2] = 0` (da der TSE-Colt unendliche Reservemunition hat und keinen Munitionspool verbraucht).
   - **(c) Double Shotgun bei 1 Shell:** Ein Bot besitzt Double Shotgun (`4`) und genau `1` Shell (`m_iShells == 1`).
   - **(d) Geteilter Bullets-Pool & Infinite Ammo:** Ein Bot besitzt Tommygun (`6`) und Minigun (`7`) mit `100` Bullets (`m_iBullets = 100 / 500`), oder spielt auf Red Station mit `gam_bInfiniteAmmo = 1` (`tools/redstation_preset.py:6`).
3. **Erwartetes Verhalten:**
   - **(a)** Werte bis `200 HP` und `200 Armor` sind in Serious Sam TSE reguläre Spielzustände; der `ItemPlanner` muss weiterlaufen und Super-Items (`kHealthSuper`, `kArmorSuper`) gegen das Overcap `200` bewerten.
   - **(b)** Single Colt (`2`) und Dual Colts (`3`) sind unabhängig vom Munitionszähler jederzeit schussbereit (`usable`).
   - **(c)** Double Shotgun (`4`) benötigt in Retail TSE (`PlayerWeapons.es`) **mindestens `2` Shells** pro Schuss (`bot_combat.h:10` dokumentiert dies explizit); bei `1` Shell muss auf Single Shotgun (`3`? Index `3` = DualColts, Index `4` = SingleShotgun, Index `5` = DoubleShotgun) gewechselt werden. *(Hinweis zur Indexierung in `botcore`: `4 = Single Shotgun`, `5 = Double Shotgun` benötigt `2` Shells.)*
   - **(d)** Gemeinsame Engine-Pools (`Bullets` für Tommygun + Minigun, `Cells` für Laser + Cannon) müssen über den realen Pool-Maximalwert bewertet werden; bei `gam_bInfiniteAmmo = 1` muss `AmmoNeed == 0` und jede besessene Waffe `usable` sein.
4. **Beobachtetes Verhalten (`[OFFLINE-PROVED]`):**
   - **(a)** `ValidateWorld` weist `health > max_health` (`101 > 100`) und `armor > max_armor` als **`kBadSelf` -> `ItemReason::kInvalidWorld`** zurück! Ein einziger `+1 HP`-Pillen-Pickup schaltet die **gesamte Item-KI** (inkl. Waffen-Pickups!) ab, bis der Bot wieder unter `100` geschossen wird. Und bei `100/100 HP` liefert `HealthNeed` `0.00`, sodass MegaHealth komplett ignoriert wird (`R10` + Live-Probe #3).
   - **(b)** `item_weapons.h` weist Single/Dual Colt ein endliches `ammo_cap = 50` zu; bei `ammo[2] == 0` streicht `UsableWeaponMask` den Colt und zwingt den Bot in unserer Live-Probe auf **`weapon = 1` (Knife!)** (`R11` + Live-Probe #3; selbst `ArenaSim::AddBot` musste als Workaround `b.ammo[2] = 50` faken!).
   - **(c)** `UsableWeaponMask` prüft für Double Shotgun (`5`) nur `ammo[5] > 0` statt `>= 2`; bei `1` Shell wählt der Bot eine nicht feuerbare Waffe (`R11`).
   - **(d)** `AmmoNeed(6)` sättigt bei `100` Bullets (`cap=100` für Tommygun) auf `0.00`, obwohl Minigun erst halb voll ist; `gam_bInfiniteAmmo = 1` existiert im gesamten `itemai`/`navbridge`-Datenmodell nicht (`R12`).
5. **Technische Ursache (soweit belegbar):**
   - PR #55 wurde ohne Abgleich gegen `PlayerWeapons.es` und gegen die in `poc/botcore/bot_combat.h` dokumentierten TSE-Waffenregeln als abstraktes `ammo[15]`-Modell entworfen.
6. **Konkrete Fix-Empfehlung:**
   - In `item_snapshot.h`: `ValidateWorld`-Obergrenze auf `2.0 * max_health` bzw. `200.0` anheben; für `kHealthSuper`/`kArmorSuper` in `HealthNeed`/`ArmorNeed` das Overcap `200.0` ansetzen.
   - In `item_weapons.h`: Für Waffen `1` (Knife), `2` (Colt), `3` (Dual Colts) und `10` (Chainsaw) `requires_ammo = false` setzen; `min_ammo_per_shot` einführen (`2` für Double Shotgun `5`, `1` sonst); ein Feld `bool infinite_ammo` in `SelfState` aufnehmen (`gam_bInfiniteAmmo != 0`).
   - MunitionsPools auf die echten 8 TSE-Pools (`Shells, Bullets, Rockets, Grenades, Napalm, Electricity, IronBalls, SniperBullets`) abbilden.
7. **Passender Regressionstest:**
   - `test_item_multifloor_regressions.cpp`: `TestR10_OverhealAndOverarmorTriggerInvalidWorldAbort`, `TestR11_ColtInfiniteReserveAndDoubleShotgunTwoShell`, `TestR12_SharedBulletsPoolCapMismatchBlocksMinigun` sowie Live-Probe #3 in `run_live_branch_audit.py`.

---

### `QA-05` [P0] — Session-Namensnormalisierung hebelt Human-Slot-Eviction aus & PR #68 enthält eine defekte Whitelist-Regex mit Console-Injection-Risiko

1. **Exakte Datei und Funktion:**
   - PR #57 (`6b84c5d2...`): `tools/bot_sessions.py`, `DECORATION` & `clean_name(...)` Zeilen `24–37`, `Planner.snapshot(...)` Zeilen `243–295`; `tools/bot_session_executor.py` Zeilen `53–56`
   - PR #68 (`7ec04d03...`): `poc/research/session-hybrid-lab/session_hybrid_lab.py`, `clean_name(...)` Zeilen `207–216`, `HybridPlanner.snapshot(...)` Zeilen `438–476`
2. **Reproduzierbarer Fehlerfall:**
   - **Fall A (Standard-Duplikate):** Zwei echte Spieler treten unkonfiguriert mit dem Serious-Sam-Standardnamen `"Serious Sam"` bei (`human_names = ["Serious Sam", "Serious Sam"]`).
   - **Fall B (Nicht-ASCII-Spielername):** Ein einzelner europäischer oder kyrillischer Spieler (z. B. `"Игрок"` oder `"☆☆☆"`) betritt den Server.
   - **Fall C (TSE-Formatcodes & PR-#68-Regex):** Ein Spieler nutzt gültige TSE-Formatcodes wie `^aFF^oBot0^R` (Alpha + Kontrast + Uppercase-Reset), oder in PR #68 wird `clean_name('Bot"; Quit(); //')` aufgerufen.
3. **Erwartetes Verhalten:**
   - Echte menschliche Spieler zählen anhand ihrer belegten Server-Slots zuverlässig gegen `human_capacity = maxplayers - reserved_human_slots`, unabhängig davon, ob zwei Menschen denselben Namen tragen oder kyrillische Zeichen verwenden. Alle gültigen TSE-Formatcodes werden für Namenskollisionsprüfungen entfernt; gefährliche Zeichen (`"`, `;`, `\n`) werden strikt abgelehnt oder entfernt.
4. **Beobachtetes Verhalten (`[OFFLINE-PROVED]`):**
   - **Fall A:** `Planner.snapshot()` verwirft den **gesamten Server-Snapshot mit `return None`**, sobald zwei Menschen denselben bereinigten Namen (`"serious sam"`) haben! Dadurch plant der Session-Controller **keinerlei Bot-Leaves mehr**, und `reserved_human_slots` ist auf dem vollen Server wirkungslos (`test_qa05a` + Live-Audit).
   - **Fall B:** `clean_name("Игрок")` wirft `ValueError("empty visible nickname")`, da alle Nicht-ASCII-Zeichen vor der Alnum-Prüfung gelöscht werden — ein einziger kyrillischer Spieler bringt `snapshot()` zum Absturz bzw. Verwurf (`test_qa05b`).
   - **Fall C:** PR #57 `clean_name("^aFF^oBot0^R")` liefert `"affobot0r"` statt `"bot0"` (übersieht `^a[0-9a-fA-F]{2}`, `^o`/`^O`, `^R`). Noch schwerwiegender: In PR #68 Zeile `212` steht `re.sub(r"[^A-Za-z0-9 ._\\[\\]-]", "", value)` — durch doppelte Backslashes in einem Raw-String parst Python `[^A-Za-z0-9 ._\\[]` gefolgt vom literalen Suffix `\]-`! Dadurch passiert **`clean_name('Bot"; Quit(); //') == 'Bot"; Quit(); //'` komplett ungefiltert** (`test_qa05c` + Live-Audit)!
5. **Technische Ursache (soweit belegbar):**
   - Verwendung derselben strikten Bot-Admissibilitätsfunktion `clean_name` für unkontrollierte externe Human-Query-Namen, Eindeutigkeitszwang auf menschlichen Spielernamen statt Slot-Zählung sowie fehlerhaftes Regex-Escaping in PR #68.
6. **Konkrete Fix-Empfehlung:**
   - Strikte Trennung in zwei Funktionen:
     1. `validate_bot_nickname(name)` (strikte ASCII-Whitelist `r"[^A-Za-z0-9 ._\[\]-]"`, ablehnend bei Verstoß).
     2. `normalize_observed_player_name(raw)` für Server-Queries: vollständige TSE-Tag-Entfernung `re.compile(r"\^(?:c[0-9a-fA-F]{6}|a[0-9a-fA-F]{2}|f[0-9]|[biIoOrRBF])")`, niemals Exception bei Nicht-ASCII/Leerstring (Fallback `<non-ascii-slot-N>`), und **Zählung menschlicher Spieler nach Slot-Anzahl (`len(human_slots)`) statt eindeutiger Namensmenge**.
7. **Passender Regressionstest:**
   - `test_session_and_flags_regressions.py`: `test_qa05a_duplicate_default_serious_sam_names_disable_eviction`, `test_qa05b_unicode_player_name_poisons_snapshot_and_crashes_executor`, `test_qa05c_tse_format_codes_and_pr68_broken_whitelist_regex` sowie `run_live_branch_audit.py`.

---

### `QA-06` [P1] — Im Menü hängender `LEAVING`-Client blockiert dauerhaft sämtliche Bot-Leaves über alle Server hinweg

1. **Exakte Datei und Funktion:**
   - PR #57 (`6b84c5d2...`): `tools/bot_session_runtime.py`, `reconcile(...)` Zeilen `218–227`; `tools/bot_sessions.py`, `Planner.plan(...)` Zeilen `252, 282, 288`
   - PR #68 (`7ec04d03...`): `poc/research/session-hybrid-lab/session_hybrid_lab.py` Zeilen `483, 494`
2. **Reproduzierbarer Fehlerfall:**
   - Ein Bot-Client wird gestartet (`JOINING`), bleibt aber im Serious-Sam-Menü/Verbindungsfehler hängen (`process_alive=True, connected=False`). Das Join-Timeout stuft ihn auf `LEAVING` um. Gleichzeitig betritt auf einem **anderen** Server `srv2` ein menschlicher Spieler den vollen Server und benötigt einen freien Slot.
3. **Erwartetes Verhalten:**
   - Nach Ablauf einer festen `leave_ready_timeout_s`-Frist wird ein nie verbundener `LEAVING`-Client kontrolliert beendet oder in `QUARANTINE` überführt; außerdem darf ein `LEAVING`-Vorgang auf `srv1` niemals Kapazitäts-Evictions auf `srv2` blockieren.
4. **Beobachtetes Verhalten (`[OFFLINE-PROVED]`):**
   - `reconcile()` gibt für `status == "LEAVING"` mit `alive=True, connected=False` zeitlich **unbegrenzt** `"wait_leave_ready"` zurück (da es auf `connected=True` wartet, was ein gescheiterter Connect nie erreicht!).
   - Gleichzeitig prüft `Planner.plan()` global über die gesamte SQLite-Tabelle `any(s["status"] == "LEAVING" for s in active)` ohne Filter auf `s["server"] == server` und verweigert damit **jeden weiteren Leave auf allen Servern** (`test_qa06` + Live-Audit).
5. **Technische Ursache (soweit belegbar):**
   - Fehlender Alters-/Deadline-Abbruch in `reconcile()` für `LEAVING` ohne vorheriges `connected=True` sowie fehlender `server`-Scope bei der Single-Flight-Leave-Sperre.
6. **Konkrete Fix-Empfehlung:**
   - In `reconcile()`: Wenn `status == "LEAVING"` und `not connected` länger als `max_menu_leave_wait_s` (z. B. `15 s`) anhält, bei verifiziertem Einzelprozess-Ownership geordnetes Close/Quarantine auslösen, sodass der Slot aus `ACTIVE` ausscheidet.
   - In `Planner.plan()`: Leave-Drosselung pro `server` (`s["server"] == server`) statt global begrenzen, und Kapazitäts-Evictions (`excess_humans`) Vorrang vor regulärer Rotation einräumen.
7. **Passender Regressionstest:**
   - `test_session_and_flags_regressions.py`: `test_qa06_stuck_menu_leaving_client_deadlocks_all_servers`.

---

### `QA-07` [P1] — Nicht geprobte Items jenseits `max_cost_probes_per_tick = 8` gewinnen über euklidische Luftlinie durch Wände

1. **Exakte Datei und Funktion:**
   - PR #69 (`d0c181c6...`): `poc/research/nav-item-bridge/include/nav_cost_cache.h`, `WorldPathEnricher::Enrich(...)` Zeilen `868–951`
2. **Reproduzierbarer Fehlerfall:**
   - Auf einer Deathmatch-Map existieren `12` sichtbare/bekannte Items (`> 8`, Standardwert auf echten TSE-Maps mit `20..60` Pickups). Die ersten `8` Items im Snapshot-Array verbrauchen `max_cost_probes_per_tick = 8` und erhalten ihre realen A*-Umwegdistanzen (`~32 m`). Item #9 liegt in `5 m` Luftlinie hinter einer Wand mit realem Umweg von `55 m` (oder in einem abgetrennten Bereich).
3. **Erwartetes Verhalten:**
   - Nicht geprobte Kandidaten dürfen nicht mit optimistisch kurzer euklidischer Luftlinie und `reachable = true` geprobte Kandidaten schlagen; das Probing muss nach absteigendem Vorab-Utility-Potenzial bzw. Round-Robin priorisiert werden, und ungeprobte Items müssen konservativ abgewertet oder vor Commit verifiziert werden.
4. **Beobachtetes Verhalten (`[OFFLINE-PROVED]`):**
   - In `R14` behält Item #9 unverändert seine euklidische Position (`5 m`) und `reachable = true` und gewinnt die `ItemPlanner::Step`-Entscheidung (`chosen_idx = 9`) gegenüber allen 8 real geprobten Items! Erst in `NavGraphSink::Submit` stellt sich die reale Umweglänge/Unerreichbarkeit heraus, was zu Ziel-Thrashing bzw. Umweg-Fehlentscheidungen führt.
5. **Technische Ursache (soweit belegbar):**
   - `Enrich()` iteriert linear in Snapshot-Indexreihenfolge `0..count-1` statt nach geschätztem Item-Nutzen und lässt bei erschöpftem Probe-Budget `adapted_items[i]` unverändert auf Roh-Luftlinie + `reachable = true`.
6. **Konkrete Fix-Empfehlung:**
   - Kandidaten vor dem A*-Probing nach oberer Utility-Schranke sortieren, einen Round-Robin-Cursor über Ticks führen und für noch nie im Pfad-Cache verifizierte Items entweder `reachable = false` setzen oder einen konservativen Umwegfaktor (`detour_penalty >= 2.5x`) aufschlagen, bis ein Cache-Eintrag vorliegt.
7. **Passender Regressionstest:**
   - `test_item_multifloor_regressions.cpp`: `TestR14_UnprobedItemsBeyond8CapWinViaEuclideanTrap`.

---

### `QA-08` [P1] — Gespaltene Patrol-Zustandsmaschine in `NavItemBridgeAgent` umgeht `local_blocked_`-Kanten

1. **Exakte Datei und Funktion:**
   - PR #69 (`d0c181c6...`): `poc/research/nav-item-bridge/include/nav_item_bridge.h`, `StepPatrolOrReposition(...)` Zeilen `486–599`
2. **Reproduzierbarer Fehlerfall:**
   - Ein Bot markiert während der Item-Navigation eine blockierte Kante in `local_blocked_`. Auf einem Tick mit `< 8` Item-Probes verbleiben `>= 256` A*-Expansionen im Tick-Budget (`Remaining() == 512 >= 256`); auf einem Tick mit vollen Probes verbleiben `< 256` Expansionen (`Remaining() == 236 < 256`).
3. **Erwartetes Verhalten:**
   - Eine einzige konsistente Patrol-/Reposition-Implementierung respektiert auf jedem Tick sowohl `tick_budget_` als auch `local_blocked_` und erhält den `kReposition`-Modus.
4. **Beobachtetes Verhalten (`[OFFLINE-PROVED]`):**
   - Bei `Remaining() >= 256` delegiert `StepPatrolOrReposition` an `patrol_agent_` (PR #54 `navlab::NavAgent`), das **`local_blocked_` überhaupt nicht kennt** und den Bot direkt wieder in die zuvor als blockiert erkannte Kante routet, ohne `tick_budget_` exakt abzurechnen!
   - Fällt `Remaining()` im nächsten Tick unter `256` (`236`), schaltet `StepPatrolOrReposition` plötzlich auf ein zweites, separates Array `budgeted_patrol_route_` um, das wiederum keinen `kReposition`-Modus unterstützt (`R15`).
5. **Technische Ursache (soweit belegbar):**
   - PR #54 `NavAgent` besitzt keinen Hook für `ConstrainedNavSearch` / `LocalBlockedEdgeTable`; PR #69 baute deshalb einen zweiten Fallback-Router daneben, statt einen einzigen budgetierten Router zu nutzen.
6. **Konkrete Fix-Empfehlung:**
   - `patrol_agent_` entweder um einen optionalen `EdgeFilter`/`ExpansionBudget`-Callback erweitern oder Patrol/Reposition vollständig über `ConstrainedNavSearch` + `local_blocked_` vereinheitlichen und die doppelte `budgeted_patrol_route_`-Zustandsmaschine entfernen.
7. **Passender Regressionstest:**
   - `test_item_multifloor_regressions.cpp`: `TestR15_DualPatrolSplitAndLocalBlockedBypass`.

---

### `QA-09` [P1] — Massive Cross-PR-Duplikation & widersprüchliche Entscheidungslogik (3 Waffenscorer, Persona-Leck, Preset-Kollision, verlorene Config-Normalisierung)

1. **Exakte Datei und Funktion:**
   - **3 Waffenscorer:** `poc/botcore/bot_combat.h:158` (`botcore::ScoreWeapon`), PR #55 `item_weapons.h:105` (`itemai::StandInWeaponScore`), PR #66 `combat2_weapon.h:117` (`combat2::ScoreWeapon2`)
   - **Persona-Orthogonalitätsbruch (`C02`):** PR #66 `combat2_tactics.h:83` (`AlertGatePasses`) und `combat2_tactics.h:274` (`PlanRespawn`)
   - **Preset-Kollision:** PR #57 `tools/redstation_preset.py` vs. PR #63 `tools/redstation_preset.py`
   - **Verlorene Normalisierung:** PR #68 `poc/research/session-hybrid-lab/session_hybrid_lab.py`, `validate_config(...)` Zeilen `288–310`
2. **Reproduzierbarer Fehlerfall:**
   - **Waffenscorer (`R16`):** Bewertung von Laser (`12`) vs. Sniper (`13`) auf `40 m` Distanz.
   - **Persona-Leck (`R16`):** Aufruf von `combat2::PlanRespawn(tier=3, persona=0, seed=42, deaths=1)` vs. `persona=1` bei identischem Skill-Tier `3`.
   - **Config-Normalisierung (`test_qa09`):** Aufruf von `session_hybrid_lab.validate_config` mit `{"nickname": " ^cff00aaAce^r ", "color": "ff00aa"}`.
3. **Erwartetes Verhalten:**
   - Item-Layer und Combat-Layer bewerten Waffen über exakt dieselbe Funktion, sodass der Bot keine Waffe umläuft und einsammelt, die Combat anschließend sofort wieder wegsteckt. Skill-Mechaniken wie Respawn-Reaktionsverzögerung und Wahrnehmungs-Alert-Gates hängen gemäß Vertrag `C02` (`bot_profile.h`) ausschließlich vom Skill-Tier ab, nicht von der Persona. `validate_config` gibt die bereinigten Identitäten zurück.
4. **Beobachtetes Verhalten (`[OFFLINE-PROVED]`):**
   - Auf `40 m` wählt `itemai::StandInWeaponScore` (Kopie des Laser-Bias `F-1` aus `bot_combat.h`) **Laser (`12`: `3.41 > 3.20`)**, während `combat2::ScoreWeapon2` **Sniper (`13`: `5.31 > 2.28`)** wählt (`R16` + Live-Probe #4). Der Bot läuft Umwege für eine Waffe, die Combat verschmäht (und umgekehrt).
   - `PlanRespawn` liefert auf demselben Tier `3` für Aggressor `13` Ticks, für Survivor `19` Ticks (`+300 ms` künstlicher Nachteil allein durch Persona); `AlertGatePasses` ändert ebenfalls die Wahrnehmungsschwelle pro Persona.
   - PR #68 `validate_config` bereinigt eine lokale Kopie `i = dict(raw)`, weist in Zeile `309` aber `c["identities"] = pool` (die **unbereinigte** Rohliste!) zu (`" ^cff00aaAce^r "` bleibt unverändert erhalten!).
   - PR #57 und PR #63 überschreiben `tools/redstation_preset.py` gegenseitig inkompatibel.
5. **Technische Ursache (soweit belegbar):**
   - Fehlende zentrale Header-/Modul-Autorität zwischen den parallelen Arbeitssträngen `#55`, `#57`, `#63`, `#66`, `#68`, `#69`.
6. **Konkrete Fix-Empfehlung:**
   - Einen einzigen kanonischen Waffenscorer in `poc/botcore/bot_combat.h` pflegen und `StandInWeaponScore` in PR #55 per Header-Einbindung ersetzen.
   - In PR #66 Persona-Offsets aus `PlanRespawn` und `AlertGatePasses` entfernen (nur Tier-basiert).
   - In PR #68 Zeile `309` eine `normalized_pool`-Liste aufbauen (`normalized_pool.append(i); c["identities"] = normalized_pool`) bzw. eine einzige Session-Bibliothek in `tools/bot_sessions.py` pflegen.
   - `tools/redstation_preset.py` explizit auf die gewünschte Zielmarke (`ssam.ai` vs. `Alpha-Gaming`) und `gaming_names`-Validierung zusammenführen.
7. **Passender Regressionstest:**
   - `test_item_multifloor_regressions.cpp`: `TestR16_Combat2VsItemScoringDisagreementAndPersonaLeak`; `test_session_and_flags_regressions.py`: `test_qa09_pr68_validate_config_discards_normalized_identities`.

---

### `QA-10` [P1] — Unvollständige und inkonsistente Feature-Flag-Verdrahtung (`BotDriver`, `NavItemBridge`, `Session-Tools`)

1. **Exakte Datei und Funktion:**
   - PR #57 (`6b84c5d2...`): `poc/candidates/integrated-human-cpu-20261021/BotDriver.cpp` Zeilen `1092–1100` (`BotHumanAttach`), Zeilen `1122–1139` (`NoteConfigOnce`), Zeilen `545–560` (`InitBotIntegration`); `poc/botcore/bot_human.h` Zeilen `70–80, 128, 338`; `tools/bot_sessions.py:55–95`; `tools/bot_session_runtime.py:92–103`
   - PR #69 (`d0c181c6...`): `poc/research/nav-item-bridge/include/nav_item_bridge.h` Zeile `46`
   - PR #66 (`48e110a7...`): `poc/research/behavior-improvements/` (keinerlei Shell-CVar in `BotDriver.cpp`)
2. **Reproduzierbarer Fehlerfall:**
   - **Fall A:** Operator ändert zur Laufzeit per Konsole `bot_bExploratorySearch = 0` oder `bot_bCecilP1 = 0`, während Bots bereits attached sind.
   - **Fall B:** Session-Konfiguration übergibt `{"cecil_p1": True}` an `bot_sessions.validate_config(...)` oder generiert das Client-Startskript über `bot_session_runtime.startup_script(ident)`.
   - **Fall C:** Alle neuen Flags werden auf `0` gesetzt (`bot_bExploratorySearch = 0`, `bot_bCecilP1 = 0`), um auf die qualifizierte PR-#45-Baseline zurückzufallen.
3. **Erwartetes Verhalten:**
   - Jedes neue Subsystem besitzt ein eigenes Default-OFF- bzw. sauber dokumentiertes Kill-Switch-CVar, wird im Tick-Loop aktualisiert, im Konfigurationslog (`NoteConfigOnce`) protokolliert, von den Python-Session-Tools durchgereicht und stellt bei `0` bitgenau das PR-#45-Verhalten wieder her.
4. **Beobachtetes Verhalten (`[OFFLINE-PROVED]`):**
   - **Fall A:** `bot_bExploratorySearch` und `bot_bCecilP1` werden nur einmalig in `BotHumanAttach()` gelesen; `HumanBotPolicy` besitzt keinen Setter für Laufzeitänderungen, `NoteConfigOnce` loggt beide CVars nicht, und `NavItemBridgeAgent::Configure` ruft `human_policy_.Configure(&bundle_.bot_profile)` hart mit `(false, false)` auf.
   - **Fall B:** `bot_sessions.validate_config` lehnt `cecil_p1` mit `ValueError` ab; `startup_script(ident)` schreibt nur `bot_bHumanAI` und `bot_iProfile*`, lässt aber `bot_bExploratorySearch`, `bot_bCecilP1`, `bot_bNavAvoidance` und `bot_iSkillTier` komplett weg (`test_qa10` + Live-Audit).
   - **Fall C:** Selbst bei `bot_bExploratorySearch = 0` und `bot_bCecilP1 = 0` bleiben `escape_active_` (`QA-02`) und der `>45°`-Drehstopp (`QA-01`) aktiv — es existiert **kein sauberer Fallback auf PR #45**!
   - Zusätzlich sind Navigation 2.0 (`#54`), Item-Utility (`#55`), Combat 2.0 (`#66`) und Nav-Item-Bridge (`#69`) überhaupt noch nicht über Shell-CVars in `BotDriver.cpp` angebunden.
5. **Technische Ursache (soweit belegbar):**
   - Nachträgliches Hinzufügen einzelner CVars ohne durchgängigen End-to-End-Konfigurationsvertrag zwischen `BotDriver.cpp`, `botcore`, `navbridge` und `tools/bot_session*.py`.
6. **Konkrete Fix-Empfehlung:**
   - Einheitlichen `BotFeatureFlags`-Struct (`human_ai, nav_avoidance, exploratory_search, cecil_p1, nav_v2, item_ai, combat_v2`) in `botcore` definieren, pro Tick aus den `INDEX`-CVars synchronisieren (`policy.SetFlags(flags)`), vollständig in `NoteConfigOnce` ausgeben und bei allen neuen Flags `= 0` **garantiert** den unveränderten PR-#45-Pfad ausführen.
7. **Passender Regressionstest:**
   - `test_session_and_flags_regressions.py`: `test_qa10_session_flag_schema_and_startup_script_disconnect`.

---

### `QA-11` [P1] — Waffenwechsel-Draw-Unterdrückung verbrennt Schusskadenz (`0,90 s` Feuerverlust) & 50-ms-Hold für Ladewaffen ist `NOT_TESTED_RETAIL`

1. **Exakte Datei und Funktion:**
   - PR #45 / PR #57: `poc/botcore/bot_human.h`, `HumanBotPolicy::Step(...)` Zeilen `308–331` (`next_shot_tick_[cmd.weapon]`); `poc/candidates/integrated-human-cpu-20261021/BotDriver.cpp` Zeilen `1054–1070` (`weaponChangePending` unterdrückt `PLACT_FIRE`)
   - PR #66: `poc/research/behavior-improvements/combat2_weapon.h` (übernimmt dieselbe Lücke)
2. **Reproduzierbarer Fehlerfall:**
   - Ein Bot wechselt im Kampf auf Sniper (`13`, Kadenz `36` Ticks = `1,80 s`) oder Rocket Launcher (`8`, Kadenz `16` Ticks = `0,80 s`). Die Waffe benötigt in Retail TSE `18` Ticks (`0,90 s`) Draw-Animation (`weaponChangePending == true`). Bereits auf Tick 2 ist das Ziel im Visier.
3. **Erwartetes Verhalten:**
   - Solange `weaponChangePending` in der Engine das Feuern blockiert (`w.weapon_ready == false`), darf `HumanBotPolicy` den Schuss-Cooldown `next_shot_tick_` nicht vorab abbuchen; sobald die Waffe auf Tick 20 feuerbereit ist, löst der erste Schuss unmittelbar aus. Für Ladewaffen (`Grenade Launcher 9`, `SBC Cannon 14`) muss die Haltedauer von `PLACT_FIRE` zur gewünschten Reichweite passen.
4. **Beobachtetes Verhalten (`[OFFLINE-PROVED]` / `NOT_TESTED_RETAIL`):**
   - `HumanBotPolicy` kennt `weaponChangePending` nicht (`WorldView` enthält kein `weapon_ready`-Feld!), setzt auf Tick 2 `cmd.fire = true` und bucht `next_shot_tick_[13] = 2 + 36 = 38` ab. `BotDriver.cpp:1066` verwirft `cmd.fire` wegen `weaponChangePending` stillschweigend! Wenn die Waffe auf Tick 20 bereit ist, schweigt der Bot weitere **`18` Ticks (`0,90 s`)** bis Tick 38 (`R05`).
   - Zudem pulst `HumanBotPolicy` `cmd.fire = true` nur für **einen einzigen Tick (`50 ms`)** und setzt danach `cmd.fire = false`. Bei `Grenade Launcher (9)` und `Cannon (14)` löst das Loslassen von `PLACT_FIRE` nach `50 ms` den Minimal-Charge-Schuss direkt vor die eigenen Füße aus (Selbstschadenrisiko auf Mitteldistanz; Verhalten in Retail 1.07 ist **`NOT_TESTED_RETAIL`**).
5. **Technische Ursache (soweit belegbar):**
   - Fehlende Rückkopplung des Engine-Waffenstatus (`m_iCurrentWeapon == m_iDesiredWeapon && WeaponReady`) in `botcore::WorldView` sowie fehlende Charge-Hold-Modellierung für `Grenade Launcher` und `Cannon`.
6. **Konkrete Fix-Empfehlung:**
   - `bool weapon_ready` in `WorldView` ergänzen und `next_shot_tick_` nur setzen, wenn `w.weapon_ready == true`.
   - Für `Grenade Launcher (9)` und `Cannon (14)` eine distanzabhängige `fire_hold_ticks`-Dauer (`1..12` Ticks) modellieren und nativ in Retail 1.07 qualifizieren.
7. **Passender Regressionstest:**
   - `test_combat_nav_regressions.cpp`: `TestR05_WeaponSwitchDrawSuppressionBurnsShotCadence`.

---

### `QA-12` [P1] — Stack-Überlaufrisiko (`ArenaSim` `927 KiB`), uncached `NearestNode`-CPU-Kosten, unbudgetierte Item-LOS-Raycasts & Hetzner-RAM-Grenzen

1. **Exakte Datei und Funktion:**
   - PR #69 (`d0c181c6...`): `poc/research/nav-item-bridge/include/arena_sim.h` (`sizeof(ArenaSim) = 949.600 Bytes = 927,34 KiB`), `nav_item_bridge.h` (`sizeof(NavItemBridgeAgent) = 95.080 Bytes = 92,85 KiB`), `nav_cost_cache.h:808–951`
   - PR #54 (`3f2ba8db...`): `poc/navigation-lab/nav_graph.h` (`sizeof(NavGraph) = 173.060 Bytes = 169,00 KiB`, linearer 1024-Knoten-Scan pro `NearestNode`)
   - PR #63 (`1e375d8f...`): `tools/redstation_preset.py:21–29` (`cmd_cmdOnTick` Shell-Ausführung auf jedem Server-Tick)
   - PR #62 (`d5fcd066...`) & PR #65 (`6227222f...`): RAM-/Sync-Risikomodelle
2. **Reproduzierbarer Fehlerfall:**
   - **Stack:** Instanziierung von `ArenaSim` oder `NavGraph` + `NavItemBridgeAgent` als lokale Variable auf einem 32-Bit-Windows-PE-Thread-Stack (`1 MiB = 1.024 KiB` Default-Stackreserve von `SeriousSam.exe` / `DedicatedServer.exe`).
   - **CPU / Sync:** 8 Bots auf einem 1024-Knoten-Graphen mit 32 Items pro Tick (`20 Hz`), zuzüglich naiver `CCastRay`-Sichtlinienprüfungen (`8 Bots × 32 Items = 256 Rays/Tick = 5.120 Rays/s`).
   - **RAM:** Betrieb von Architektur B (isolierte 1-Bot-Wine-Clients) mit 8 bis 16 Bots auf Hetzner CX22 (`3.819 MiB` RAM, `0 MiB` Swap).
3. **Erwartetes Verhalten:**
   - Keine großen KI-Strukturen auf dem Thread-Stack; O(1)/Grid-beschleunigte Knotensuche; striktes globales `CCastRay`-Budget pro Tick (analog zum 2-Ray-Budget für Gegner-LOS in PR #45), sodass das `50 ms`-Server-Tick-Quantum niemals gerissen wird; Einhaltung der `1.068 MiB` freien Host-RAM-Reserve.
4. **Beobachtetes Verhalten (`[OFFLINE-PROVED]` / `NOT_TESTED_RETAIL`):**
   - **Stack (`[OFFLINE-PROVED]`):** `sizeof(ArenaSim) = 927,34 KiB` verursacht auf einem 1-MiB-PE-Stack sofortigen Stack-Overflow (`STATUS_STACK_OVERFLOW`); 16 statische `NavItemBridgeAgent`-Instanzen + 1 `NavGraph` belegen `1.654,63 KiB` (`1,62 MiB`) BSS.
   - **CPU (`[OFFLINE-PROVED]`):** Unser Benchmark über 8 Bots × 1024 Knoten × 32 Items misst allein für die reine C++-Logik (überwiegend wiederholte lineare `NearestNode`-Scans über 1024 Knoten für jedes Item!) **`1.019,51 µs` pro Welt-Tick** (`127,44 µs/Bot-Tick`) — auf 64-Bit-Host-Hardware noch **ohne** einen einzigen Engine-`CCastRay`!
   - **Sync (`[IMPL-VERIFIED]`, `NOT_TESTED_RETAIL`):** Weder PR #55 noch PR #69 besitzen ein Raycast-Budget für `item.visible` (analog `PlanLosQueries` für Spieler). Naive `5.120 CCastRay/s` plus PR #63s `cmd_cmdOnTick`-String-Parser (`20 Hz`) gefährden unmittelbar das `50 ms`-Tick-Budget (`SYNCLATE` / `SYNCBAD`, `FUN_601A2D10`).
   - **RAM (gemäß PR #62 `[T]`/`[P]`):** Auf Hetzner CX22 (`3.819 MiB`, `0 Swap`) liegt Arch A bei `~418,6 MiB` (8 Bots `[T]`), Hybrid C1 bei `~602,8 MiB` `[D]`, Arch B hingegen schon bei `7+1` Clients bei `~1.725,9 MiB` `[T]` (berührt das Sicherheitslimit) und bei 16 Bots bei `~3.566,7 MiB` `[P]` (akute OOM-Gefahr).
5. **Technische Ursache (soweit belegbar):**
   - Große Inline-Arrays in Aggregatklassen, fehlender Spatial-Hash bzw. fehlendes statisches Spawn-Anchor-Caching in `NavGraph` sowie fehlender `PlanItemLosQueries`-Vertrag in `NavItemBridgeAgent`.
6. **Konkrete Fix-Empfehlung:**
   - Statische Item-Spawnpunkte einmalig beim Map-Load auf ihren `anchor_node` abbilden (`O(1)` pro Tick statt `O(N_items * N_nodes)`!).
   - Für `item.visible` entweder kein `CCastRay` verwenden (Items sind an festen Weltkoordinaten über Entitätsstatus `IsActive/Respawn` bzw. Nahbereichs-Distanz erfassbar) oder strikt auf maximal `1..2` gestaffelte Rays pro Bot-Tick deckeln.
   - Große Agenten ausschließlich statisch im BSS oder per einmaliger Initialisierungs-Allokation halten, niemals auf dem Stack (`static_assert(sizeof(...) < ...)`).
   - PR #63s periodische Server-Announcement nicht über `cmd_cmdOnTick` (`20 Hz` Shell-Parser), sondern extern über den Python-RCON/Console-Timer alle `300 s` einspeisen.
7. **Passender Regressionstest:**
   - Siehe Messprotokoll und Größentabelle in Deliverable 4 (`04-cpu-ram-risikobewertung.md`).

---

### `QA-13` [P2] — Vier Detailfehler in Nahkampf-Recovery, Out-of-Combat-Waffenwahl, `RouteMemory` und `TimeFactor`

1. **Exakte Datei und Funktion:**
   - **(a)** PR #45 / PR #57: `poc/candidates/integrated-human-cpu-20261021/BotDriver.cpp` Zeile `1042` (`const BOOL combatHold = target != NULL && decision.distance_m <= (melee ? 1.5 : 8.0) && moveFactor <= 0.0f;` — bzw. in PR #45 sogar ohne `moveFactor <= 0.0f`!)
   - **(b)** PR #45 / PR #57: `poc/botcore/bot_loadout.h` Zeilen `156–167, 204–209` (`WeaponSelector::Update` & `Fallback`) und `BotDriver.cpp` Zeile `1054` (`if (decision.target >= 0) combatWeapon = decision.weapon;`)
   - **(c)** PR #57: `poc/botcore/bot_route.h`, `RouteMemory::MarkHazard(...)` Zeile `131` (`for (int k = 1; k < count_ - 1 && marked < 2; ++k)`)
   - **(d)** PR #55: `poc/research/item-utility/include/item_scoring.h`, `TimeFactor(...)` Zeile `288` (`profile.memory_horizon_s` statt `profile.planning_horizon_s`)
2. **Reproduzierbarer Fehlerfall:**
   - **(a) `R06`:** Bot steht auf `6,5 m` (`<= 8,0 m`) vor einem Gegner und läuft rückwärts/seitlich gegen eine hüfthohe Kiste (`front_dist = 0,6 m`).
   - **(b) `R07`:** Bot verschießt beim tödlichen Treffer seine letzte Tommygun-Kugel (`usable_mask` danach nur noch Knife + Colt), kein Gegner mehr da (`has_target = false`).
   - **(c) `R08`:** `RouteMemory` enthält genau `count_ = 2` Segmente (Slot `0` = Startsegment vor der Klippe, Slot `1` = Absturzsegment); der Bot stirbt durch Umweltschaden (`MarkHazard()`).
   - **(d) `R13`:** Vergleich von `TimeFactor(total_s = 6.0)` zwischen Tier 1 (`planning_horizon_s = 7,5 s`) und Tier 5 (`planning_horizon_s = 16,5 s`) bei gleichem `memory_horizon_s = 14,0 s`.
3. **Erwartetes Verhalten:**
   - **(a)** `ObstacleRecovery` befreit einen im Nahkampf an Geometrie festgekeilten Bot, solange der Bot sich aktiv bewegen will (`|forward| + |strafe| > 0`).
   - **(b)** Sobald die aktive Waffe leer ist, wechselt `WeaponSelector` sofort (auch außerhalb des Kampfes!) auf die beste verfügbare Fernkampfwaffe (z. B. Colt `2`), und `BotDriver.cpp` übernimmt diesen Wechsel auch bei `target < 0`.
   - **(c)** `MarkHazard` markiert auch den ältesten gültigen Ringpuffer-Slot `0` (`k < count_`).
   - **(d)** `TimeFactor` skaliert Reisezeitkosten anhand von `planning_horizon_s`, sodass Tier 5 langfristiger plant als Tier 1.
4. **Beobachtetes Verhalten (`[OFFLINE-PROVED]`):**
   - **(a)** In PR #45 bricht `distance <= 8.0f` `ObstacleRecovery` sofort ab (`buggy_recovery_active = 0`), sodass der Bot an der Kiste festklebt (`R06`).
   - **(b)** `WeaponSelector::Update` setzt bei leerer Waffe außerhalb des Kampfes nur `locked_ = false`, behält aber `current_ = 6` (die **leere** Tommygun!) bei und gibt `6` zurück; selbst wenn `current_ == 0` wäre, scannt `Fallback()` von `1` aufwärts und wählt immer `1` (Knife!), und `BotDriver.cpp:1054` ignoriert `decision.weapon` bei `target < 0` komplett (`R07`).
   - **(c)** Bei `count_ = 2` ist `k < count_ - 1` (`1 < 1`) falsch — Slot `0` wird nie als Gefahrenstelle markiert (`R08`).
   - **(d)** Tier 1 und Tier 5 liefern identische `TimeFactor`-Werte (`0,679 == 0,679`), `planning_horizon_s` ist in `TimeFactor` wirkungslos (`R13`).
5. **Technische Ursache (soweit belegbar):**
   - Jeweils lokale Grenzfall-/Copy-Paste-Fehler an den genannten vier Codezeilen.
6. **Konkrete Fix-Empfehlung:**
   - **(a)** `combatHold` nur setzen, wenn `std::fabs(moveFactor) < 0.05f && std::fabs(decision.strafe) < 0.05f`.
   - **(b)** In `bot_loadout.h:156`: wenn `!WeaponUsable(in.usable_mask, current_)`, sofort `current_ = BestWeapon(in.usable_mask, 15.0, 0.0)` wählen; in `BotDriver.cpp:1054` `combatWeapon = decision.weapon` immer übernehmen, wenn `decision.weapon >= 1`.
   - **(c)** Schleifenbedingung in `bot_route.h:131` auf `k < count_` korrigieren.
   - **(d)** In `item_scoring.h:288` `profile.planning_horizon_s` verwenden (`memory_horizon_s` bleibt ausschließlich für `StalenessFactor` zuständig).
7. **Passender Regressionstest:**
   - `R06`, `R07`, `R08` in `test_combat_nav_regressions.cpp` sowie `R13` in `test_item_multifloor_regressions.cpp`.

---

### `QA-14` [P1] — Schwerwiegende Testblinde Flecken inkl. vakuösem XOR-Determinismus-Test (`50 × X = 0`) und abgeschnittenem `BotDriver`-Extraktor

1. **Exakte Datei und Funktion:**
   - **Blinder Fleck 1 (`BotDriver`-Naht):** `poc/botcore/extract_block.py` Zeilen `1–40` (extrahiert nur den eingebetteten `botcore`-Headerblock aus `BotDriver.cpp`, stoppt **vor** den Adapterzeilen `900–1200`!).
   - **Blinder Fleck 2 (Vakuöser Determinismus-Hash + Padding):** PR #69 (`d0c181c6...`): `poc/research/nav-item-bridge/tests/test_nav_item_bridge.cpp`, Test `M02` Zeilen `529–580` (`sizeof(ArbitrationTrace) == 40`, Summe der Felder `= 39` -> `1 Byte` uninitialisiertes Compiler-Padding in `Fnv1a(&trace, sizeof(trace))`, kombiniert mit `run_hash ^= tick_hash` über **exakt `50` identische Ruheticks**!).
   - **Blinder Fleck 3 (Regex-Snippets statt Integrationstests):** PR #57 (`6b84c5d2...`): `tests/test_bot_ai2.py` (prüft `BotDriver.cpp` lediglich per String-/Regex-Suche auf Textfragmente statt den echten Adapter-Loop auszuführen).
2. **Reproduzierbarer Fehlerfall:**
   - Ausführung von `R17` (`TestR17_VacuousEvenTickXorHashAndPaddingProof`): Eine Sequenz von `50` identischen Zustandsticks wird einmal in Originalreihenfolge und einmal mit mutiertem/invertiertem Zustand gehasht (`run_hash ^= tick_hash` ab Initialwert `FNV_OFFSET_BASIS`).
3. **Erwartetes Verhalten:**
   - Ein Determinismus-Test muss zustands- und reihenfolgesensitiv hashen (laufendes FNV-1a/SHA256-Streaming statt kommutativem XOR) und darf niemals Padding-Bytes via `sizeof(struct)` einbeziehen; der `BotDriver`-Adaptercode (`Zeilen 900–1200`) muss durch ausführbare C++-Tests abgedeckt sein.
4. **Beobachtetes Verhalten (`[OFFLINE-PROVED]`):**
   - Da `X ^ X == 0` für jeden beliebigen 64-Bit-Wert `X` gilt, löschen sich `50` (gerade Anzahl!) identische Tick-Hashes in `M02` exakt gegenseitig aus und liefern immer den nackten Startwert `0xcbf29ce484222325` — **selbst wenn zwei Läufe völlig unterschiedliche konstante Zustände produzieren (`fwd == rev == 0xcbf29ce484222325`, Falsch-Positiv!)** (`R17`). Gleichzeitig liest `Fnv1a(&trace, sizeof(ArbitrationTrace))` ein uninitialisiertes Padding-Byte (`sizeof=40 > 39`), was unter verschiedenen Optimierungsstufen zu UB führt.
   - `make smoke` in `poc/botcore/` übersieht jeden Fehler in `BotDriver.cpp:900–1200` (darunter `QA-01`, `QA-10`, `QA-11`, `QA-13a`, `QA-13b`), weil `extract_block.py` diesen Teil vor dem Kompilieren verwirft!
5. **Technische Ursache (soweit belegbar):**
   - Kommutative/selbstinverse XOR-Aggregation über gerade Tick-Zahlen, Rohspeicher-Hashing über nicht gepackte C++-Structs sowie fehlende testbare Kapselung der `BotDriver`-Übersetzungsschicht.
6. **Konkrete Fix-Empfehlung:**
   - Den `BotDriver`-Entscheidungsadapter (`WorldView`-Aufbau, `ObstacleRecovery`-Kopplung, `weaponChangePending`, `combatHold`, Flag-Sync) in eine eigenständige, Engine-freie Header-Funktion `botcore::AdaptDriverTick(...)` auslagern, sodass `make test` den echten Adapterpfad mitkompiliert.
   - In PR #69 `M02` jedes Feld von `ArbitrationTrace` explizit in einen laufenden FNV-1a-/SHA256-Stream einspeisen (kein XOR, kein `&struct`-Rohspeicher-Hash).
7. **Passender Regressionstest:**
   - `test_item_multifloor_regressions.cpp`: `TestR17_VacuousEvenTickXorHashAndPaddingProof` sowie die gesamte QA-Suite in `poc/research/integration-qa-20261026/`.
