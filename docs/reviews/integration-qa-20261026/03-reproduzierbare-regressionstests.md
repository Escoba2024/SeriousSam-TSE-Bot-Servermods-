# Deliverable 3: Reproduzierbare Regressionstests & Ausführungsprotokoll (`integration-qa-20261026`)

> **Wichtige Einordnung:** Alle in diesem Dokument aufgeführten Tests sind **deterministische Offline-Tests (`[OFFLINE-PROVED]`)**. Sie beweisen Logik-, Vertrags-, Speicherlayout- und Nahtstellenverhalten im Quellcode, ersetzen aber **keinen** nativen Laufzeitnachweis in `SeriousSam.exe` / `DedicatedServer.exe` (`NOT_TESTED_RETAIL`).

---

## 1. Ausführungsprotokoll der bestehenden Offline-Testsuiten im Repository

Alle bestehenden Offline-Tests der relevanten Branches wurden isoliert (Read-Only-Extraktion per `git archive`) ausgeführt:

| Branch / PR | Commit-SHA | Ausgeführter Befehl | Ergebnis | QA-Bewertung der Aussagekraft |
| :--- | :--- | :--- | :--- | :--- |
| **`main` (PR #45)** | `ab0c7400...` | `make -C poc/botcore test && make -C poc/botcore smoke BOTDRIVER=../candidates/integrated-human-cpu-20261021/BotDriver.cpp` | **PASS** (`16/16` Unit + Smoke) | Prüft nur `botcore`-Headerblock; `extract_block.py` verwirft `BotDriver.cpp:900–1200` (`QA-14`) |
| **PR #54 (Nav 2.0)** | `3f2ba8db...` | `make -C poc/navigation-lab test` | **PASS** (`22/22` Checks) | Kein Multi-Floor-Test auf gleicher `(x, z)`-Koordinate (`QA-03` unentdeckt) |
| **PR #55 (Items)** | `72d464ff...` | `make -C poc/research/item-utility test` | **PASS** (`35/35` Checks) | Testet `health <= 100` & fiktive `ammo[15]`-Caps; TSE-Overheal (`101..200`), Colt `@0` und Double Shotgun `@1` fehlen (`QA-04`) |
| **PR #57 (Cecil-P1 + AI2 + Sessions)** | `6b84c5d2...` | `make -C poc/botcore test && make -C poc/botcore smoke ... && python3 -m unittest discover -s tests` | **PASS** (`24/24` C++ + `60/60` Python) | `test_bot_ai2.py` prüft `BotDriver.cpp` nur per Regex; kein gekoppelter `HumanBotPolicy + ObstacleRecovery`-Loop (`QA-01`), kein Ambush-in-LOS-Test (`QA-02`), kein Duplikat-`"Serious Sam"`-Test (`QA-05`) |
| **PR #58 (Sync C2)** | `df7108ba...` | `python3 -m unittest discover` in `poc/research/sync-harness*` | **PASS** (`12/12` Python) | Synthetische Mocks; 7 reale Gate-Schwächen durch PR #67 C2 belegt |
| **PR #63 (`ssam.ai` Preset)** | `1e375d8f...` | `python3 -m unittest tests/test_redstation_preset.py` | **PASS** (`10/10` Python) | Kollidiert direkt mit `tools/redstation_preset.py` aus PR #57; `cmd_cmdOnTick` `20 Hz` ist `NOT_TESTED_RETAIL` |
| **PR #65 (MP-Sync)** | `6227222f...` | `python3 -m unittest` in `poc/research/mp-sync-20261026/` | **PASS** (`14/14` Python) | Rein analytisches Offline-Modell (`H1/F11/F12` sind Hypothesen, `NOT_TESTED_RETAIL`) |
| **PR #66 (Combat 2.0)** | `48e110a7...` | `make -C poc/research/behavior-improvements test` | **PASS** (`29/29` Checks) | Isoliert gegen eigene Header getestet; Divergenz zu PR #55 `StandInWeaponScore` und `C02`-Persona-Leck ungetestet (`QA-09`) |
| **PR #67 (Master Partial)** | `66ab8326...` | `python3 -m unittest discover` in `poc/research/master-integration-20261025/` | **PASS** (`23/23` Python) | Deckt nur M1/C1/C2 offline ab; M4–M8 nicht vorhanden (`INT-BLOCKER-01`) |
| **PR #68 (Session C1 Lab)** | `7ec04d03...` | `python3 -m unittest` in `poc/research/session-hybrid-lab/` | **PASS** (`21/21` Python) | Übersieht kaputte Whitelist-Regex `r"[^A-Za-z0-9 ._\\[\\]-]"` (`QA-05c`) und verlorenes `i` in `validate_config` (`QA-09`) |
| **PR #69 (Nav-Item-Bridge)** | `d0c181c6...` | `make -C poc/research/nav-item-bridge test` | **PASS** (`18/18` Szenarien) | Nutzt lokale Fallback-Mocks statt PR #57; Test `M02` ist vakuös (`50 × X = 0` XOR + Struct-Padding, `QA-14`); Multi-Floor (`QA-03`) & Probe-Cap-Trap (`QA-07`) fehlen |

---

## 2. Neue reproduzierbare QA-Regressionssuite (`poc/research/integration-qa-20261026/`)

Zur lückenlosen, jederzeit wiederholbaren Reproduktion aller identifizierten Fehler wurde unter `poc/research/integration-qa-20261026/` eine eigenständige, warnungsfreie (`-std=c++17 -O2 -Wall -Wextra -Werror`) C++17- und Python-Testsuite erstellt.

### 2.1 Dateistruktur

| Datei | Zweck | Abgedeckte Befunde |
| :--- | :--- | :--- |
| `Makefile` | Targets `make test` (Standalone auf `main`), `make test-live` (inkl. Live-Git-Extraktion aller Kandidaten-Commits) und `make clean` | Alle (`QA-01..QA-14`) |
| `test_combat_nav_regressions.cpp` | 8 deterministische C++17-Tests gegen `poc/botcore/` für Combat-, Navigations- und `BotDriver`-Adapterfehler (`R01..R08`) | `QA-01`, `QA-02`, `QA-11`, `QA-13a/b/c` |
| `test_item_multifloor_regressions.cpp` | 9 deterministische C++17-Tests für Multi-Floor-Ankerung, TSE-Overheal/Munition, Probe-Cap-Falle, Patrol-Split, Scorer-Divergenz & XOR-Padding-Beweis (`R09..R17`) | `QA-03`, `QA-04`, `QA-07`, `QA-08`, `QA-09`, `QA-13d`, `QA-14` |
| `test_session_and_flags_regressions.py` | 6 `unittest`-Fälle für Session-Eviction, TSE-Formatcodes, defekte PR-#68-Whitelist-Regex, Menü-Leave-Deadlock, verlorene Normalisierung & CVar-Lücken | `QA-05`, `QA-06`, `QA-09`, `QA-10` |
| `run_live_branch_audit.py` | Extrahiert die gepinnten Commits von `#54, #55, #57, #63, #66, #67, #68, #69` Read-Only in ein Temp-Verzeichnis, importiert die echten Python-Module und kompiliert eine C++17-Cross-PR-Probe mit `-DNAV_ITEM_BRIDGE_REQUIRE_UPSTREAM` direkt gegen die echten Header | `INT-BLOCKER-01`, `QA-02`, `QA-03`, `QA-04`, `QA-05`, `QA-06`, `QA-09`, `QA-10` |
| `README.md` | Bedienungsanleitung, Befund-Mapping und `NOT_TESTED_RETAIL`-Hinweis | Dokumentation |

### 2.2 Verifiziertes Ausführungsprotokoll (`make -C poc/research/integration-qa-20261026 test-live`)

Ausgeführt in dieser Sandbox mit Exit-Code `0`:

```text
=== integration-qa-20261026: Combat, Navigation & Seam Regressions ===
[PASS] R01_ChasingTurnFreezeResetsObstacleRecovery (QA-01)  | PR45_bypass=1 PR57_bypass=0(resets=8,max_x=0.15m) Fix_bypass=1
[PASS] R02_ExploratorySearchSelfCancelsForwardAbove35Deg (QA-01b) | cancelled_segments=30/40 (>35 deg self-zeroes forward=0.72)
[PASS] R03_BlindEscapeBlocksVisibleCombatFor100Ticks (QA-02a) | PR45_shots=32 vs PR57_blind_ticks=100 PR57_shots_in_first_100t=0(total=0)
[PASS] R04_BridgeArbitrationFlipsVisibleAmbushToPatrol (QA-02b) | world_los=1 pr57_target=-1 -> bridge_engaged=0 owner=patrol fire=0
[PASS] R05_WeaponSwitchDrawSuppressionBurnsShotCadence (QA-11) | draw_ready_t=20 buggy_first_shot_t=38 fixed_first_shot_t=20 lost=18 ticks(0.90s)
[PASS] R06_CloseCombatUnder8mResetsObstacleRecovery (QA-13a) | pinned_at_6.5m: buggy_recovery_active=0 fixed_recovery_active=1
[PASS] R07_NoTargetKeepsEmptyWeaponAndDropsReadiness (QA-13b) | fight_wpn=6 -> empty_post_fight_sel=6(unusable!) driver@no_target=1 fixed=2
[PASS] R08_RouteMemoryMarkHazardOffByOne (QA-13c)           | oldest_slot0_hazard: buggy=0 (skipped!) fixed=1
=== SUMMARY: 8 passed, 0 failed (NOT_TESTED_RETAIL) ===

=== integration-qa-20261026: Item, Multi-Floor & Cross-PR Regressions ===
[PASS] R09_MultiFloorPlanarNearestNodeDeadlock (QA-03)        | buggy_nodes=(0,0)->eff=8m(deadlock=1) fixed_nodes=(0,4)->ramp_A*
[PASS] R10_OverhealAndOverarmorTriggerInvalidWorldAbort (QA-04a) | mega_need@100hp=0.00 valid@101hp=0 valid@200armor=0 fixed_valid=1
[PASS] R11_ColtInfiniteReserveAndDoubleShotgunTwoShell (QA-04b/c) | Retail(Colt=1,DShot@1sh=0) vs PR55_69(Colt=0,DShot@1sh=1)
[PASS] R12_SharedBulletsPoolCapMismatchBlocksMinigun (QA-04d) | 100_bullets: PR55_AmmoNeed(6)=0.00(minigun_fill=0.50) Fixed_PoolNeed=0.80
[PASS] R13_TimeFactorUsesMemoryHorizonNotPlanningHorizon (QA-13d) | buggy(T1=0.679 == T5=0.679) vs fixed(T1=0.450 != T5=0.725)
[PASS] R14_UnprobedItemsBeyond8CapWinViaEuclideanTrap (QA-07) | probes_used=8/8 -> item9(walled_5m) reachable=1 chosen_idx=9(expect_trap=9)
[PASS] R15_DualPatrolSplitAndLocalBlockedBypass (QA-08)       | tick1_rem=236(<256:budgeted_patrol) tick2_rem=512(>=256:patrol_agent_no_local_block)
[PASS] R16_Combat2VsItemScoringDisagreementAndPersonaLeak (QA-09) | 40m_best: ItemLayer=12(Laser=3.41>Sniper=3.20) vs Combat2=13(Sniper=5.31>Laser=2.28) | Respawn(T3): agg=13!=surv=19
[PASS] R17_VacuousEvenTickXorHashAndPaddingProof (QA-14)      | sizeof=40>fields=39(pad=1) 50x_XOR: fwd=0xcbf29ce484222325 == rev=0xcbf29ce484222325 (FALSE PASS!)
=== SUMMARY: 9 passed, 0 failed (NOT_TESTED_RETAIL) ===

Ran 6 tests in 0.001s — OK (test_session_and_flags_regressions.py)

[LIVE-PASS] QA-02 PR57(unflagged!)+PR69 3-way split (engaged=1,escape=1->owner=patrol,shots=0): 100/100 ticks
[LIVE-PASS] QA-03 Multi-floor ceiling deadlock: astar_probes=0 goal=77 fwd=0.00
[LIVE-PASS] QA-04 Overheal 101HP->invalid-world & Colt@0->weapon=1(Knife!)
[LIVE-PASS] QA-09 Scorer split (Item:12 vs C2:13) & Respawn persona leak (13!=19)
[LIVE-CPP-SUMMARY] 4/4 live cross-PR C++ checks reproduced
"status": "LIVE_CROSS_PR_REPRODUCTION_OK"
```

---

## 3. Wie der Codex-Hauptagent diese Suite als Gate nutzt

1. Vor Beginn des Integrations-PRs demonstrieren `R01..R17`, `test_session_and_flags_regressions.py` und `run_live_branch_audit.py` sowohl den jeweiligen **Ist-Fehler** als auch die **Soll-Invariante nach dem Fix**.
2. Im echten Integrations-Branch übernimmt der Codex-Hauptagent die **Fix-Assertions** (`Fix_bypass == 1`, `fixed_shots >= 25`, `NearestNode3D == n4`, `fixed_valid == 1`, `clean_tse_visible_name_fixed`, `AdaptDriverTick` im `make test`-Ziel von `poc/botcore/`) direkt als verpflichtendes CI-/Pre-Merge-Gate.
