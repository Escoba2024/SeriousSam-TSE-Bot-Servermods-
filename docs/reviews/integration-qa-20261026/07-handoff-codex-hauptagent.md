# Deliverable 7: Konkretes Handoff für den Codex-Hauptagenten (`integration-qa-20261026`)

## 1. Sofortige Leitplanken (Merge-Stopps)

1. **Kein Direkt-Merge von PR #57 (`6b84c5d2...`) nach `main`:** Enthält zwei **ungeflaggte P0-Regressionen** gegenüber PR #45 (`QA-01` Wand-Oszillation durch `>45°`-Drehstopp + `bs_navigation.Reset()`, `QA-02` `100`-Tick-Blindheit gegenüber sichtbaren Angreifern) sowie den Session-Eviction-Bypass bei doppelten `"Serious Sam"`- oder Nicht-ASCII-Namen (`QA-05`).
2. **Kein Direkt-Merge von PR #63 (`1e375d8f...`) ohne Konfliktauflösung:** Überschreibt `tools/redstation_preset.py` inkompatibel zu PR #57 und führt mit `cmd_cmdOnTick` einen `20 Hz`-Shell-Parser-Hook im Dedicated Server ein (`NOT_TESTED_RETAIL`).
3. **Keine unveränderte Übernahme von PR #54, #55, #66, #68, #69 in Produktionspfade:**
   - PR #54 + #69 scheitern auf mehrstöckigen Maps (`QA-03`: 2D-`NearestNode`),
   - PR #55 + #69 scheitern an TSE-Overheal (`101..200 HP` -> `kInvalidWorld`), Colt `@0` und Double Shotgun `@1` (`QA-04`),
   - PR #68 enthält in Zeile `212` die defekte Raw-Regex `r"[^A-Za-z0-9 ._\\[\\]-]"` (`'Bot"; Quit(); //'` passiert ungefiltert, `QA-05c`) und verwirft in Zeile `309` die normalisierten Identitäten (`QA-09`),
   - PR #67 (`66ab8326...`) ist nur ein partielles Vorbereitungs-Paket (M1/C1/C2 als `.patch`/Offline-Gates; M4–M8 fehlen komplett, `INT-BLOCKER-01`).

---

## 2. Verbindlicher 6-Phasen-Integrationsplan für den echten Codex-Integrations-PR

### Phase 0: Infrastruktur-, Receipt- & Supervisor-Basis scharfschalten (PR #67 M1/C1/C2 real anwenden)
1. `M1_MCP_RECEIPT_PATCH.patch` und `C1_SUPERVISOR_PATCH_PROPOSAL.patch` aus PR #67 nicht nur als `.patch` ablegen, sondern im Integrations-Branch real auf den Supervisor (`DedicatedServer_107.py` etc.) anwenden und per Test verifizieren (insb. terminierter `SYNCBAD`-Scan + cgroup-Bindung von `SeriousSam.exe`).
2. Auf dem Zielserver (`46.225.231.211`) den unsauberen Build06 (`54faabf0...`) durch ein frisches Overlay auf Basis der qualifizierten PR-#45-Baseline (`7fc94a39...`) ersetzen, bevor irgendein neuer Kandidat gemessen wird.
3. `c2_sync_gates.py` aus PR #67 als verbindliches Auswertungs-Gate für alle künftigen Retail-Läufe verdrahten.

### Phase 1: `poc/botcore/` & `BotDriver.cpp` reparieren + testbaren Adapter extrahieren (`QA-01, QA-02, QA-09, QA-10, QA-11, QA-13, QA-14`)
1. **Einheitlicher Feature-Flag-Vertrag (`QA-10`):**
   - `struct BotFeatureFlags { bool human_ai; bool nav_avoidance; bool exploratory_search; bool cecil_p1; bool combat_v2; bool nav_item_bridge; };`
   - Pro Tick in `BotDriver.cpp` über `policy.SetFlags(flags)` aktualisieren (nicht nur einmalig in `BotHumanAttach()`!) und vollständig in `NoteConfigOnce` protokollieren.
   - **Harte Invariante:** Sind `exploratory_search == 0, cecil_p1 == 0, combat_v2 == 0, nav_item_bridge == 0`, muss sich `HumanBotPolicy` bitgenau wie PR #45 verhalten!
2. **Fix `QA-01` (Nav/Combat-Oszillation):**
   - Den `>45°`-Drehstopp (`bot_human.h:338–340`) hinter Flag legen **und** deaktivieren, sobald `w.navigation_override_active == true` ist.
   - In `BotDriver.cpp:952,1106` `bs.bs_navigation.Reset()` **niemals** auslösen, während `bs.bs_navigation.IsActive()` ein Hindernis umgeht.
   - Im Suchmodus (`bot_human.h:256–278`) den Yaw-Sweep auf `<= 30°` begrenzen statt `cmd.forward` ab `35°` auf `0.0` zu setzen.
3. **Fix `QA-02` (100-Tick-Blindfenster):**
   - `escape_active_` erst **nach** `perception_.Observe(...)` und `ChooseTarget()` bewerten, hinter ein eigenes Flag stellen und **sofort abbrechen**, sobald `perception_.VisibleCount() > 0` einen sichtbaren Angreifer meldet.
4. **Fix `QA-09` (Einziger Waffenscorer + `C02`-Orthogonalität):**
   - Die bereinigten Distanzbänder aus PR #66 (`ScoreWeapon2`, Behebung des Laser-Bias `F-1`) direkt als optional geflaggten Modus in `botcore::ScoreWeapon` integrieren; `StandInWeaponScore` in PR #55 ersatzlos streichen und auf `botcore::ScoreWeapon` verweisen.
   - Aus `PlanRespawn` und `AlertGatePasses` (PR #66) alle `persona`-Abhängigkeiten entfernen (`C02`: Reaktionszeit ist rein `tier`-abhängig).
5. **Fix `QA-11` & `QA-13a/b/c`:**
   - `bool weapon_ready` (`!weaponChangePending`) in `WorldView` übergeben; `next_shot_tick_` erst setzen, wenn `w.weapon_ready == true`.
   - `combatHold` nur setzen, wenn der Bot tatsächlich stehenbleiben will (`|moveFactor| < 0.05 && |strafe| < 0.05`).
   - `WeaponSelector::Update` bei leerer `current_`-Waffe auch außerhalb des Kampfes sofort neu wählen lassen und `decision.weapon` in `BotDriver.cpp` auch bei `target < 0` übernehmen.
   - `RouteMemory::MarkHazard` auf `k < count_` korrigieren.
6. **Fix `QA-14` (`BotDriver`-Testbarkeit):**
   - Die Entscheidungslogik aus `BotDriver.cpp:900–1120` in eine Engine-freie Header-Funktion `botcore::AdaptDriverTick(...)` ziehen, damit `make -C poc/botcore test` den echten Adapterpfad mitprüft.

### Phase 2: 3D-Navigation, TSE-Item-Vertrag & CPU/Stack-sichere Bridge zusammenführen (`QA-03, QA-04, QA-07, QA-08, QA-12, QA-13d`)
1. **3D-Ankerung (`QA-03`):**
   - `NavGraph::NearestNode3D(x, y, z, max_step_up_m=1.6, max_drop_m=2.5, vertical_weight=4.0)` implementieren und in `nav_cost_cache.h` sowie `nav_goal_sink.h` durchgängig verwenden; Wegpunkt-Ankunft zusätzlich an `|bot.y - wp.y| <= 1.8 m` binden.
2. **TSE-1.07-konforme Item-/Waffenregeln (`QA-04`, `QA-13d`):**
   - `ValidateWorld` bis `200 HP` / `200 Armor` (`2.0 * max`) öffnen; `kHealthSuper`/`kArmorSuper` gegen `200` bewerten.
   - Knife (`1`), Single Colt (`2`), Dual Colts (`3`) und Chainsaw (`10`) ohne Munitionsbedarf schussbereit halten; Double Shotgun (`5`) erst ab `>= 2` Shells erlauben.
   - Die 8 realen TSE-Munitionspools (`Shells, Bullets, Rockets, Grenades, Napalm, Electricity, IronBalls, SniperBullets`) sowie `bool infinite_ammo` (`gam_bInfiniteAmmo != 0`) abbilden.
   - `TimeFactor` in `item_scoring.h:288` auf `profile.planning_horizon_s` umstellen.
3. **Bridge-Härtung & CPU/Stack-Disziplin (`QA-02b, QA-07, QA-08, QA-12, QA-14`):**
   - In `ArbitrateCommands` `combat_cmd.escape` explizit behandeln (kein stiller Rückfall auf `kPatrolNavigation` bei `combat.engaged == true`).
   - In `WorldPathEnricher::Enrich`: statische Item-Spawnpunkte einmalig beim Map-Load auf ihren `anchor_node` cachen (`O(1)` statt `270.336` Knotenscans/Tick!); Kandidaten nach Vorab-Utility sortieren und ungeprobte Items konservativ abwerten statt mit Roh-Luftlinie gewinnen zu lassen.
   - Einen einzigen Patrol-/Reposition-Router verwenden, der `local_blocked_` und `tick_budget_` immer beachtet.
   - **Hartes Item-LOS-Raybudget:** Maximal `0..2` gestaffelte `CCastRay`-Aufrufe pro Bot-Tick für Items (oder reine Entitäts-/Wegpunkt-Sichtbarkeit).
   - `ConstrainedNavSearch` als einzelnes statisches Scratch-Objekt teilen; keine Allokation von `NavGraph`/`ArenaSim` auf dem 1-MiB-PE-Stack; Test `M02` auf feldweises Streaming-FNV-1a ohne XOR und ohne Struct-Padding umstellen.

### Phase 3: Session-Management & `redstation_preset.py` konsolidieren (`QA-05, QA-06, QA-09, QA-10`)
1. **Einzige kanonische Session-Bibliothek in `tools/bot_sessions.py`:** Keine divergente Kopie in `session_hybrid_lab.py` weiterpflegen; falls Hybrid-C1-Konzepte übernommen werden, Zeile `212` (`r"[^A-Za-z0-9 ._\[\]-]"`, **einfaches** Backslash-Escaping!) und Zeile `309` (`normalized_pool` statt `pool`) zwingend korrigieren.
2. **Robuste Human-Slot-Zählung (`QA-05`):**
   - Vollständige TSE-Dekorations-Regex `r"\^(?:c[0-9a-fA-F]{6}|a[0-9a-fA-F]{2}|f[0-9]|[biIoOrRBF])"`.
   - `Planner.snapshot()` darf bei doppelten Human-Namen (`"Serious Sam"`) oder kyrillischen/Unicode-Spielernamen **niemals** `None` liefern oder `ValueError` werfen; `human_count` muss über die **Anzahl menschlicher Spieler-Slots** gezählt werden, damit `reserved_human_slots` jederzeit greift.
3. **Bounded Menu-Leave & Server-lokale Leave-Sperre (`QA-06`):**
   - In `bot_session_runtime.reconcile()` ein `max_menu_leave_wait_s`-Timeout für `LEAVING` bei `connected=False` einführen; in `Planner.plan()` `any(s["status"] == "LEAVING" and s["server"] == server)` serverlokal filtern.
4. **Auflösung des Konflikts `tools/redstation_preset.py` (PR #57 vs. PR #63) & CVar-Weitergabe (`QA-10`):**
   - Ziel-Branding (`ssam.ai` vs. `Alpha-Gaming`) und `BOT-`-Präfix mit `gaming_names.validate_native` in **einer** Datei zusammenführen.
   - Den `20 Hz`-`cmd_cmdOnTick`-Hook aus PR #63 durch einen externen `300 s`-Timer im Python-Controller ersetzen.
   - Alle aktiven `bot_b*`-CVars in `bot_sessions.validate_config` und `bot_session_runtime.startup_script` synchron führen.
   - Auf Hetzner CX22 (`3.819 MiB`, `0 Swap`) unter Architektur B `max_bots <= 6` erzwingen (keine `16` Wine-Clients!).

---

## 3. Verpflichtende Abnahme-Checkliste vor Öffnung des Integrations-PRs

- [ ] **Check 1 (Offline-Regressionsgate):** `make -C poc/botcore test`, alle Subsystem-Tests **und** die QA-Suite in `poc/research/integration-qa-20261026/` bestätigen, dass alle Soll-Invarianten (`Fix_*`) erfüllt sind (`0` Warnungen unter `-Wall -Wextra -Werror`).
- [ ] **Check 2 (PR-#45-Äquivalenzbeweis):** Mit allen neuen Feature-Flags auf `0` liefert der integrierte Build über `1.000` Ticks identische Entscheidungen wie PR #45 (`R01` umgeht die Wand, `R03` feuert `32` Schüsse statt `0`).
- [ ] **Check 3 (Keine Duplikate/Konflikte):** Genau 1 Waffenscorer, 1 Patrol-Router, 1 Session-Modul, 1 konfliktfreies `tools/redstation_preset.py`.
- [ ] **Check 4 (Native Retail-1.07-Qualifikation gemäß Deliverable 6):** Erst **nach** Vorliegen kryptografisch validierter `M1`/`C2`-Receipts für `4` und `8+` Slots inkl. echtem Vanilla-1.07-Human-Client (`0 SYNCBAD`, `0 CRC`, `MemAvailable >= 1.068 MiB`) darf `NOT_TESTED_RETAIL` für die geprüfte Konfiguration aufgehoben werden.
