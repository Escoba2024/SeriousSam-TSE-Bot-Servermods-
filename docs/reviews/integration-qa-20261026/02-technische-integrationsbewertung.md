# Deliverable 2: Technische Integrationsbewertung (`integration-qa-20261026`)

## 1. GitHub-Status & Identifikation des tatsächlichen Codex-Integrationsstands

### 1.1 Vollständige PR-Bestandsaufnahme (Stand 2026-10-25)

| PR | Commit-SHA (40 Zeichen) | Branch | GitHub-Status | Tatsächlicher technischer Inhalt | Retail-1.07-Status |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **#45** | `ed10b29e8d93dc4561a39ef9b9f8e60ac0466544` (`main` `ab0c740`) | `agent/integration/20261021-human-cpu` | **MERGED** | Qualifizierte Baseline `botcore` + `BotDriver.cpp` (`GameMP.dll` SHA256 `7fc94a39...`, 8 Profile, 2-Ray-LOS-Budget, `ObstacleRecovery`) | `[RETAIL-EVIDENCE-DOC]` (Baseline) |
| **#50** | `b5dafb87e4352d28b22db28621b37efe1acb2ac6` | `agent/lead/20261022-phase-completion` | OPEN (Draft) | C1 Supervisor-Kandidat (enthält 5 in PR #67 belegte Sicherheits-/Sync-Fehler, u. a. unterminierten `SYNCBAD`-Scan) | `NOT_TESTED_RETAIL` (fehlerhaft) |
| **#54** | `3f2ba8dbf0df341b35cb157efd152fa93d1d7fd7` | `arena/8317e1d6-...` | OPEN | **Navigation 2.0** (`poc/navigation-lab/`): `NavGraph`, A*, `NavAgent`, Patrol/Reposition — isoliertes Lab ohne `BotDriver`-Integration | `NOT_TESTED_RETAIL` |
| **#55** | `72d464ff501d90ec4b69c2a131a50a06323e1909` | `arena/232e8a37-...` | OPEN | **Item-Utility** (`poc/research/item-utility/`): `ItemPlanner`, `ItemScoring`, `ItemWeapons` — isoliertes Lab ohne `BotDriver`-Integration | `NOT_TESTED_RETAIL` |
| **#57** | `6b84c5d283664bc9e968bb4961abf2dd48731c5b` | `agent/chat/20261025-cecil-p1` | OPEN (Draft) | **Codex Cecil-P1 + Bot-AI2 + Session-Tools**: ändert `poc/botcore/`, `BotDriver.cpp` (DLL `7dc961c8...`) & `tools/bot_session*.py`, `tools/redstation_preset.py`; **keine** Integration von `#54/#55/#66/#69` | `[RETAIL-EVIDENCE-DOC]` nur **1 Bot / 131,87 s**; `4/8/16` Bots = `NOT_TESTED_RETAIL` |
| **#58** | `df7108ba04cafb120c6a035503fa2f9732a83b0f` | `arena/c2418556-...` | OPEN | C2 Sync-Harness-Entwurf (weist 7 in PR #67 belegte Prüflücken auf) | `NOT_TESTED_RETAIL` |
| **#62** | `d5fcd066c28764a6ba7fb6808364304f3ccd74e7` | `arena/ed539689-...` | OPEN | **Session-Memory-Architekturvergleich** (`docs/reviews/session-memory-20261026/`): reine Dokumentations-/Modellanalyse `[T]/[D]/[P]` | Dokumentations-PR (`NOT_TESTED_RETAIL` für C1/16p) |
| **#63** | `1e375d8fe71ea10e3a657c4aaf4da1cbc3ac9127` | `agent/chat/20261025-ssam-server-experience` | OPEN (Draft) | **Codex `ssam.ai` Red Station Preset**: ändert `tools/redstation_preset.py` (`BOT-`-Präfix, `MOTD`, `ANNOUNCEMENT`, `cmd_cmdOnTick` `20 Hz`) — **direkter Dateikonflikt mit PR #57** | `NOT_TESTED_RETAIL` |
| **#65** | `6227222f3c91d248246eb3dbd139b7d03c6a4cc3` | `arena/2a42754c-...` | OPEN | **Multiplayer-Sync-Audit & Hypothesen (`H1/F11/F12`)** (`poc/research/mp-sync-20261026/`): Offline-Rechnungen & Hypothesen | `NOT_TESTED_RETAIL` |
| **#66** | `48e110a7aa7b818cf7bab5979f6aae629932a2dc` | `arena/501f5d01-...` | OPEN | **Combat 2.0 Kandidat** (`poc/research/behavior-improvements/`): `ScoreWeapon2`, `SelectStrafeStyle`, `PlanRespawn`, `AlertGatePasses` — isoliert, nicht in `botcore` integriert | `NOT_TESTED_RETAIL` |
| **#67** | `66ab832661809ee2a7be405224d4676c835b6dd8` | `agent/lead/20261025-master-integration` | OPEN (Draft) | **Codex Master-Integration (Partial)**: deklariert `PARTIAL_DELIVERY_WITH_EXPLICIT_NATIVE_BLOCKERS`; enthält **nur** M1/C1/C2 als Offline-Tools & `.patch`-Dateien; **M4–M8 fehlen komplett** | `NOT_TESTED_RETAIL` |
| **#68** | `7ec04d0304c4db606ebe223c5800386f9f3e69e2` | `arena/20261025-session-hybrid-c1-lab` | OPEN | **Session-Hybrid-Lab (C1)** (`poc/research/session-hybrid-lab/`): isolierte Kopie/Weiterentwicklung von `bot_sessions.py` | `NOT_TESTED_RETAIL` |
| **#69** | `d0c181c638c6e82fd0187c3a29ad5fc8bf6d1869` | `arena/d1ba932d-...` | OPEN | **Nav-Item-Bridge** (`poc/research/nav-item-bridge/`): Header-Brücke für PR #45 `botcore` + PR #54 + PR #55 (`ArenaSim`), aber **ohne** PR #57, **ohne** PR #66 und **ohne** `BotDriver.cpp`-Einbau | `NOT_TESTED_RETAIL` |

### 1.2 Feststellung zum fehlenden Gesamt-Integrations-PR (`INT-BLOCKER-01`)

- **Befund (`[IMPL-VERIFIED]`):** Es existiert im gesamten Repository **kein PR**, der die Subsysteme `#54, #55, #57, #62, #63, #65, #66, #68, #69` tatsächlich integriert.
- **PR #67** ist ein ehrlicher Status- und Vorbereitungs-Draft des Codex-Lead-Agenten (`PARTIAL_DELIVERY_WITH_EXPLICIT_NATIVE_BLOCKERS`), der dokumentiert, dass auf dem Hetzner-Server noch ein veralteter Build06 (`54faabf0...`) lief und dass vor einer echten Integration zunächst Receipt-Validierung (M1), Supervisor-Härtung (C1) und Sync-Gates (C2) repariert werden müssen. Selbst in M1 und C1 legt PR #67 lediglich `.patch`-Dateien unter `poc/research/master-integration-20261025/` ab, ohne die Zielskripte zu patchen.
- **Konsequenz für dieses QA-Review:** Keiner der Forschungs-PRs darf als fertige Integration missverstanden werden. Um dem Codex-Hauptagenten dennoch maximal belastbare Evidenz für den kommenden echten Integrationslauf zu liefern, haben wir sowohl jeden Einzel-PR als auch die **reale C++17-Kompilation der kombinierten Header (`#57 + #54 + #55 + #66 + #69` mit `-DNAV_ITEM_BRIDGE_REQUIRE_UPSTREAM`)** geprüft und dabei gravierende Nahtstellenfehler aufgedeckt.

---

## 2. Systematische Bewertung der 10 Prüfbereiche

### Prüfbereich 1: Fehlerhafte Combat-AI-Integration
- **Ungeflaggtes `escape_active_`-Blindfenster (`QA-02`, P0):** In PR #57 `bot_human.h:128,226–242` zwingt jeder Schadensimpuls `>= 25 HP` ohne Vor-Tick-Ziel den Bot für `100` Ticks (`5,0 s`) in `cmd.target = -1, cmd.fire = false` — selbst wenn der Angreifer `10 m` frontal im klaren Sichtfeld steht (`R03`: `0` Schüsse statt `32` Schüsse in PR #45).
- **Kollision mit PR #69 Arbitrierung (`QA-02`, P0):** In Kombination mit PR #69 meldet `DeriveThreatAndCombat` `combat.engaged = true` (bricht Item-Routing ab), während `ArbitrateCommands` `cmd.escape` ignoriert und auf `kPatrolNavigation` (`fire = false`) schaltet (`Live-Probe #1`: `100/100` Ticks im sichtbaren Feindfeuer im Patrol-Modus ohne Gegenwehr).
- **Waffenwechsel-Kadenzverlust (`QA-11`, P1):** `BotDriver.cpp:1066` unterdrückt `PLACT_FIRE` während `weaponChangePending`, aber `HumanBotPolicy` bucht `next_shot_tick_` bereits im ersten Draw-Tick ab (`R05`: `0,90 s` Feuerverlust bei Sniper).
- **Ladewaffen Cannon/Grenade (`QA-11`, `NOT_TESTED_RETAIL`):** Einzeltick-Feuerpuls (`50 ms`) lässt Ladewaffen sofort auf Minimalreichweite los.
- **Combat 2.0 (`#66`) unverbunden:** `combat2_weapon.h` und `combat2_tactics.h` sind in weder `poc/botcore/` noch `BotDriver.cpp` noch `NavItemBridgeAgent` eingebunden.

### Prüfbereich 2: Doppelte oder widersprüchliche Bot-Logik
Unsere Cross-PR-Analyse belegt fünf massive Duplikationsachsen (`QA-08`, `QA-09`):
1. **Drei konkurrierende Waffenscorer:**
   - `botcore::ScoreWeapon` (`poc/botcore/bot_combat.h:158`) — enthält bekannten Laser-Bias (`F-1`).
   - `itemai::StandInWeaponScore` (PR #55 `item_weapons.h:105`) — kopiert den Laser-Bias; bewertet auf `40 m` Laser (`3.41`) höher als Sniper (`3.20`).
   - `combat2::ScoreWeapon2` (PR #66 `combat2_weapon.h:117`) — korrigiert die Distanzbänder und bewertet auf `40 m` Sniper (`5.31`) weit höher als Laser (`2.28`).
   - **Folge (`R16`):** Item-KI und Combat-KI arbeiten gegeneinander (Bot sammelt Laser statt Sniper, Combat wechselt sofort weg).
2. **Fünf konkurrierende Such-/Explorationsschleifen:** PR #45 konstanter Yaw-Sweep (`bot_human.h:263`), PR #57 `exploratory_search_` + `RouteMemory` (`bot_human.h:268`), PR #66 `SelectRoamTurn` (`combat2_tactics.h`), PR #54 `NavAgent` (`nav_agent.h`) und PR #69 `budgeted_patrol_route_` (`nav_item_bridge.h:510`).
3. **Zwei Patrol-Router innerhalb derselben Klasse (`QA-08`):** `NavItemBridgeAgent::StepPatrolOrReposition` schaltet je nach `tick_budget_.Remaining() >= 256` zwischen `patrol_agent_` (ignoriert `local_blocked_`) und `budgeted_patrol_route_` (ignoriert `kReposition`) hin und her (`R15`).
4. **Bruch des Persona-Orthogonalitätsvertrags `C02` (`QA-09`):** PR #66 verknüpft `persona` mit Wahrnehmungsschwellen (`AlertGatePasses`) und Respawn-Verzögerung (`PlanRespawn`: `13` vs. `19` Ticks auf demselben Tier `3`, `R16`), obwohl `bot_profile.h` vorschreibt, dass Reaktions-/Skill-Stärke ausschließlich über `tier` gesteuert wird.
5. **Drei konkurrierende Session-/Preset-Implementierungen:** PR #57 `tools/bot_sessions.py`, PR #68 `session_hybrid_lab.py` (verwirft in `validate_config` Zeile `309` das normalisierte Dict `i`!) sowie die direkte Dateikollision `tools/redstation_preset.py` zwischen PR #57 (`Alpha-Gaming`) und PR #63 (`ssam.ai`).

### Prüfbereich 3: Konflikte zwischen Navigation und Combat
- **Wand-Oszillation durch `>45°`-Drehstopp (`QA-01`, P0):** `ObstacleRecovery` dreht den Bot seitlich von einer Wand weg; `bot_human.h:338` setzt `cmd.forward = 0.0`, sobald der Winkel zum verdeckten Gegner `>45°` wird; `BotDriver.cpp:952,1106` ruft wegen `humanEscapeForward == 0.0f` sofort `bs.bs_navigation.Reset()` auf (`R01`: `8` Resets, `0,15 m` Querfortschritt, kein Passieren der `4 m`-Säule).
- **Selbstblockade im Suchmodus (`QA-01b`, P0):** `bot_human.h:274` nullt `cmd.forward = 0.72` in `30/40` Suchsegmenten selbst, sobald der eigene Suchschwenk `35°` überschreitet (`R02`).
- **Nahkampf-Pinning unter `8 m` (`QA-13a`, P2):** `combatHold` deaktiviert in PR #45 `ObstacleRecovery` pauschal bei `distance <= 8.0f`, selbst wenn der Bot an einer Kiste festhängt (`R06`).
- **Multi-Floor-Decken-Deadlock (`QA-03`, P0):** Planares `NearestNode(x, z)` mappt obere Etagen auf Erdgeschoss-Knoten (`R09`, `Live-Probe #2`).

### Prüfbereich 4: Falsche Item-Entscheidungen
- **Overheal-/Overarmor-Totalausfall (`QA-04a`, P0):** `101 HP` (eine einzige `+1 HP`-Pille über `100`) lässt `ValidateWorld` fehlschlagen (`kInvalidWorld`) und schaltet **alle** Item-Entscheidungen inkl. Waffen-Pickups ab; bei `100/100 HP` ist `HealthNeed == 0`, sodass MegaHealth ignoriert wird (`R10`, `Live-Probe #3`).
- **Falsche TSE-Waffen-/Munitionsregeln (`QA-04b/c/d`, P0):** Colt wird bei `ammo == 0` als unbenutzbar gestrichen (`weapon = 1` Knife!), Double Shotgun wird fehlerhaft mit `1` Shell erlaubt (`PlayerWeapons.es` verlangt `2`), geteilter Bullets-Pool (`Tommygun`/`Minigun`) und `gam_bInfiniteAmmo = 1` (`tools/redstation_preset.py:6`) fehlen (`R11`, `R12`).
- **Euklidische Wand-Falle ab 9 Items (`QA-07`, P1):** Ab dem 9. Item bleiben Kandidaten wegen `max_cost_probes_per_tick = 8` auf euklidischer Luftlinie mit `reachable = true` und schlagen geprobte Wege durch Wände hindurch (`R14`).
- **Falscher Horizont-Parameter (`QA-13d`, P2):** `TimeFactor` liest `memory_horizon_s` statt `planning_horizon_s` (`R13`).

### Prüfbereich 5: Multiplayer-Sync-Risiken
*(Detailliert in Deliverable 5 `05-multiplayer-sync-risikobewertung.md`)*
- Der 36-Byte-`CPlayerAction`-Pfad bleibt in PR #57 strukturell ABI-konform (`[IMPL-VERIFIED]`), **aber** Server-Tick-Überziehungen (`> 50 ms`) erzeugen in Retail 1.07 `SYNCLATE`/`SYNCBAD` (`FUN_601A2D10`, Schwelle `0x602A7EB4`).
- Weder PR #55 noch PR #69 budgetieren `CCastRay` für Item-Sichtlinien (`8 Bots × 32 Items × 20 Hz = 5.120 Rays/s`).
- PR #63 hängt per `cmd_cmdOnTick` einen String-Befehl in den `20 Hz`-Haupttick des Dedicated Servers (`NOT_TESTED_RETAIL`).
- PR #50 hat einen unterminierten `SYNCBAD`-Logscan (PR #67 C1), PR #58 sieben Sync-Gate-Lücken (PR #67 C2).

### Prüfbereich 6: Speicher- und CPU-Probleme
*(Detailliert in Deliverable 4 `04-cpu-ram-risikobewertung.md`)*
- `sizeof(ArenaSim) = 927,34 KiB` sprengt einen 1-MiB-32-Bit-Windows-PE-Stack bei lokaler Allokation sofort; `16 × NavItemBridgeAgent + NavGraph = 1,62 MiB` BSS.
- Uncached `NearestNode` über 1024 Knoten kostet für 8 Bots × 32 Items bereits offline `1.019,51 µs/Welt-Tick` ohne Engine-Raycasts.
- Architektur B sprengt auf Hetzner CX22 (`3.819 MiB` RAM, `0 Swap`) bei 16 Bots (`~3.566,7 MiB` `[P]`) die verfügbare Host-Kapazität.

### Prüfbereich 7: Unvollständige Feature-Flags
- `QA-10` (P1): `bot_bExploratorySearch` und `bot_bCecilP1` werden nur einmalig in `BotHumanAttach()` gelesen, fehlen in `NoteConfigOnce`, besitzen keinen Setter in `HumanBotPolicy` oder `NavItemBridgeAgent`, werden von `bot_sessions.validate_config` abgelehnt und in `startup_script` ausgelassen.
- Noch kritischer: Die beiden P0-Änderungen in PR #57 (`>45°`-Drehstopp `QA-01` und `100`-Tick-`escape_active_` `QA-02`) sind in `bot_human.h` **überhaupt nicht hinter einem Flag geschützt**!

### Prüfbereich 8: Regressionen gegenüber PR #45
Gegenüber der gemergten Baseline PR #45 (`ab0c740`, DLL `7fc94a39...`) führt PR #57 **selbst bei deaktivierten neuen Flags (`bot_bExploratorySearch = 0, bot_bCecilP1 = 0`)** zwei direkte P0-Verhaltensregressionen ein:
1. **`R01` (`QA-01`):** PR #45 umgeht die `4 m`-Säule bei der Verfolgung eines kurz gesehenen Gegners fehlerfrei (`PR45_bypass = 1`); PR #57 bleibt mit `8` `ObstacleRecovery`-Resets und `0,15 m` Querbewegung vor der Wand hängen (`PR57_bypass = 0`).
2. **`R03` (`QA-02`):** PR #45 erwidert bei einem Hinterhalt aus `10 m` in klarem Sichtfeld sofort das Feuer (`32` Schüsse in `100` Ticks); PR #57 stellt den Bot für volle `100` Ticks (`5,0 s`) blind (`0` Schüsse).

### Prüfbereich 9: Fehlerhafte Session-Verwaltung
- **`QA-05` (P0):** Zwei menschliche Spieler mit Standardnamen `"Serious Sam"` oder ein einziger Spieler mit kyrillischem Namen (`"Игрок"`) lassen `Planner.snapshot()` `None` zurückgeben bzw. werfen `ValueError`, wodurch keine Bots mehr für Menschen Platz machen (`reserved_human_slots` ausgehebelt). PR #57 übersieht `^aXX/^o/^R`; PR #68 lässt durch die defekte Raw-Regex `r"[^A-Za-z0-9 ._\\[\\]-]"` sogar `'Bot"; Quit(); //'` ungefiltert durch.
- **`QA-06` (P1):** Ein im Menü hängender `LEAVING`-Client (`alive=True, connected=False`) bleibt dauerhaft in `"wait_leave_ready"` stecken und blockiert über das globale `any(s["status"] == "LEAVING")` Bot-Leaves auf **allen** Servern.

### Prüfbereich 10: Fehlende oder unzureichende Tests
- **`QA-14` (P1):**
  1. `poc/botcore/extract_block.py` schneidet vor `BotDriver.cpp:900–1200` ab — der gesamte C++-Adapter-Code war in `make smoke` blind!
  2. PR #69 Test `M02` XORt `50` identische Ruheticks (`X ^ X = 0`) über ungepacktes Struct-Padding (`sizeof=40 > 39`) und besteht selbst bei komplett unterschiedlichem Zustand (`R17`).
  3. PR #57 `tests/test_bot_ai2.py` prüft `BotDriver.cpp` nur per Regex-Textsuche.
  4. Keiner der offenen PRs enthielt Multi-Floor-Tests auf identischem `(x, z)`, Overheal-Tests (`101..200 HP`), Duplikat-`"Serious Sam"`-Tests oder Cross-PR-Kompilationsproben (`#57 + #54 + #55 + #66 + #69`). Alle diese Lücken sind nun durch `poc/research/integration-qa-20261026/` geschlossen.
