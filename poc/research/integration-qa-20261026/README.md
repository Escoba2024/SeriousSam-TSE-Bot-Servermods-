# Reproduzierbare Integrations-QA-Regressionstests (2026-10-26)

Unabhängige Offline-Regressions- und Integrationsnaht-Suite für den QA-Audit der
PRs `#45, #54, #55, #57, #62, #65, #66, #67, #68, #69` (Serious Sam TSE Classic 1.07).

> **Wichtige Evidenzgrenze:** Alle Tests in diesem Verzeichnis sind reine
> Offline-Vertrags-, Simulations- und Integrationsnaht-Tests auf Linux (`g++`
> C++17 + Python 3 Standardbibliothek). Keine Engine-Ausführung, kein Wine,
> keine Veränderung an `main` oder fremden Branches. Nativer Retail-1.07-Status
> sämtlicher hier geprüfter Kandidatenpfade: **`NOT_TESTED_RETAIL`**.

## Ausführen

```bash
# 1. Eigenständige C++17- + Python-Regressionssuite (läuft auf jedem Checkout):
make -C poc/research/integration-qa-20261026 test

# 2. Zusätzlich Live-Cross-PR-Prüfung direkt gegen die gepinnten Git-Commits
#    (#54, #55, #57, #63, #66, #67, #68, #69), sofern per git fetch vorhanden:
make -C poc/research/integration-qa-20261026 test-live

# 3. Artefakte bereinigen (keine Binaries im Git-Baum):
make -C poc/research/integration-qa-20261026 clean
```

## Abgedeckte Defekte & Integrationsnähte

| Test / Datei | Geprüfte QA-IDs | Inhalt |
|---|---|---|
| `test_combat_nav_regressions.cpp` (`R01..R08`) | `QA-01`, `QA-02`, `QA-11`, `QA-13` | Geschlossener Regelkreis `HumanBotPolicy` ↔ `BotDriver` ↔ `ObstacleRecovery` (`>45°` Chasing-Freeze-Schleife), `BotExploratorySearch` `>35°`-Selbstblockade, 100-Tick-Blind-Escape (`escape_active_`) vor `Observe()`, Nahtbruch PR #57 + PR #69 (`kPatrol` trotz sichtbarem Angreifer), Kadenzverlust während Waffen-Draw, `distance <= 8m` Recovery-Reset, verworfene Fallback-Waffe ohne Ziel, `RouteMemory::MarkHazard` Off-by-one. |
| `test_item_multifloor_regressions.cpp` (`R09..R17`) | `QA-03`, `QA-04`, `QA-07`, `QA-08`, `QA-09`, `QA-13`, `QA-14` | 2D-XZ-`NearestNode` Multi-Floor-Deadlock unter Decken/Galerien, TSE Overheal/Overarmor (`>100 HP/Armor` → `ValidationError::kBadSelf` + MegaHealth `utility=0`), Colt-Endlosreserve & Double-Shotgun-2-Shell-Regel, geteilter `m_iBullets`-Pool (`Tommygun`/`Minigun`), `TimeFactor`-Horizontfehler, ungeprobte Items `>8` als Luftlinien-Falle, gespaltene Patrol-FSM (`256`-Budgetgrenze + ignoriertes `local_blocked_`), Waffen-Scorer-Divergenz PR #55 vs. PR #66 + `PlanRespawn`-Persona-Leak, selbstauslöschender geradzahliger XOR-Hash + Struct-Padding in PR #69 `M02`. |
| `test_session_and_flags_regressions.py` (6 Tests) | `QA-05`, `QA-06`, `QA-09`, `QA-10` | Doppelte Vanilla-Standardnamen (`"Serious Sam"`), Nicht-ASCII-Spielernamen und TSE-Formatcodes (`^b`, `^i`, `^f`) hebeln `human_capacity`-Eviction aus; globaler `LEAVING`-Deadlock bei Menü-Hänger (`wait_leave_ready`); verworfene Normalisierung in PR #68 `validate_config`; abgelehntes `cecil_p1` & fehlende CVars in `startup_script`. |
| `run_live_branch_audit.py` | `QA-02`, `QA-03`, `QA-04`, `QA-05`, `QA-06`, `QA-09`, `QA-10` | Extrahiert die unveränderten PR-Commits temporär (`tempfile`), importiert die echten Python-Module und kompiliert einen C++17-Seam-Test direkt gegen die echten Header aus PR `#54, #55, #57, #66, #69`. |

Vollständige Berichte siehe [`docs/reviews/integration-qa-20261026/`](../../../docs/reviews/integration-qa-20261026/).
