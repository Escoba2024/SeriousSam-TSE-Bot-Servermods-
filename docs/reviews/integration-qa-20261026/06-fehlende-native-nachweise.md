# Deliverable 6: Liste fehlender nativer Nachweise (`NOT_TESTED_RETAIL`-Matrix)

> **Grundsatz:** Keine Offline-Simulation (`ArenaSim`, `unittest`, synthetische Kinematik) beweist reales Spielverhalten, echte BSP-Kollisionen, echte Waffen-State-Machines (`PlayerWeapons.es`), echtes Wine-/PE-Speicherverhalten oder echte Mehrspieler-Synchronität in **Serious Sam Classic: TSE Retail 1.07**. Alle nicht nativ gegen ein kryptografisch gepinntes `GameMP.dll`-Artefakt nachgewiesenen Punkte sind nachfolgend explizit als **`NOT_TESTED_RETAIL`** gekennzeichnet.

---

## 1. Vollständige Nachweismatrix nach Funktionsbereich

| Nr. | Komponente / Funktion | Quell-PR(s) | Verifizierte Implementierung | Offline-Test | Nativer Retail-1.07-Nachweis | Status |
| :--- | :--- | :--- | :---: | :---: | :--- | :--- |
| **N-01** | **Gemeinsames Integrations-Binary (`GameMP.dll`)** aus `#54 + #55 + #57 + #66 + #69` | Alle | Nein *(existiert noch nicht, `INT-BLOCKER-01`)* | Nur Header-Kompilation in QA-Probe | Keiner | **`NOT_TESTED_RETAIL`** |
| **N-02** | **Navigation 2.0 (`NavGraph`, A*, `NavAgent`, Patrol/Reposition)** in echten `.wld`-Deathmatch-Maps | `#54` | Ja (`poc/navigation-lab/`) | Ja (`22` Lab-Tests + QA `R09, R15`) | Keiner; auch kein `.wld`-Wegpunkt-Generator/Exporter im Runtime-Pfad | **`NOT_TESTED_RETAIL`** |
| **N-03** | **Multi-Floor-/Rampen-/Aufzug-/Jumppad-Navigation** (z. B. Red Station, Little Trouble, Hole) | `#54`, `#69` | Fehlerhaft (`QA-03`: 2D-`NearestNode`) | Reproduziert Fehler (`R09`) | Keiner | **`NOT_TESTED_RETAIL`** |
| **N-04** | **Item-Utility (`ItemPlanner`, Overheal, Rüstung, Munition, Waffenwert)** gegen echte `CItem`-Entitäten in `wo_cenEntities` | `#55` | Fehlerhaft (`QA-04a–d`) | Reproduziert Fehler (`R10–R13`) | Keiner; kein `CItem`-Snapshot-Extraktor in `BotDriver.cpp` vorhanden | **`NOT_TESTED_RETAIL`** |
| **N-05** | **Nav-Item-Bridge (`NavItemBridgeAgent`, `ArbitrateCommands`, `WorldPathEnricher`)** im echten Server-/Client-Tick | `#69` | Teilweise (`QA-02, QA-03, QA-07, QA-08`) | Ja (`18` Lab-Tests + QA-Probes) | Keiner (nur gegen `ArenaSim` gelaufen) | **`NOT_TESTED_RETAIL`** |
| **N-06** | **Combat 2.0 (`ScoreWeapon2`, `SelectStrafeStyle`, `PlanRespawn`, `AlertGatePasses`)** | `#66` | Isolierte Header (`QA-09`) | Ja (`29` Lab-Tests + QA `R16`) | Keiner (nicht in `GameMP.dll` kompiliert) | **`NOT_TESTED_RETAIL`** |
| **N-07** | **PR #57 Bot-AI2 & Cecil-P1 (`DLL 7dc961c8...`) mit `4`, `8` und `16` Bots** | `#57` | Ja (`QA-01`, `QA-02` P0-Fehler enthalten!) | Teilweise + QA `R01–R08` | **Nur `1` Bot über `131,87 s` dokumentiert**; `4`, `8` und `16` Bots komplett ungetestet | **`NOT_TESTED_RETAIL`** *(für `>= 2` Bots & Langzeit)* |
| **N-08** | **Vanilla-1.07-Human-Client + Bots gemeinsam im selben Match (`>= 30 min`, `0 SYNCBAD`, `0 CRC`)** | `#57`, `#63`, `#65`, `#67` | Nicht integriert | Nur Offline-Gate-Regeln (`c2_sync_gates.py`) | Keiner für irgendeinen Post-PR-#45-Kandidaten | **`NOT_TESTED_RETAIL`** |
| **N-09** | **Ladewaffen (`Grenade Launcher 9`, `SBC Cannon 14`) unter 1-Tick-Feuerpuls (`50 ms` `PLACT_FIRE`)** | `#45`, `#57`, `#66` | Ja (`QA-11`) | Nein (benötigt `PlayerWeapons.es` State-Machine) | Keine Messung von Wurfweite, Selbstschaden oder tatsächlicher Feuerauslösung | **`NOT_TESTED_RETAIL`** |
| **N-10** | **Sniper Rifle (`13`) Zoom-/Hipfire-Streuung, Munitionsverbrauch & Draw-Verzögerung** | `#45`, `#57`, `#66` | Kadenzfehler belegt (`QA-11`) | `R05` (`0,90 s` Verlust) | Reale Trefferrate & `PlayerWeapons.es`-Interaktion ungetestet | **`NOT_TESTED_RETAIL`** |
| **N-11** | **Double Shotgun (`5`) bei `1` verbleibender Shell & Single/Dual Colt bei `0` Bullets** | `#55`, `#69` | Fehlerhaft (`QA-04b/c`) | `R11` + Live-Probe #3 | Kein nativer Lauf mit Item-/Bridge-Maske | **`NOT_TESTED_RETAIL`** |
| **N-12** | **Session-Runtime (`bot_sessions.py`, `bot_session_runtime.py`, `bot_session_executor.py`) mit echten Wine-Clients (`PLC4`-Profil-Overlay, `WM_DELETE_WINDOW`, Join/Leave-Zyklus)** | `#57`, `#68` | Fehlerhaft (`QA-05`, `QA-06`) | Nur SQLite-/Mock-Tests | PR-#57-Modulkommentar bestätigt explizit: *„offline adapter primitives ... must be requalified before an on-disk overlay is ever written“* | **`NOT_TESTED_RETAIL`** |
| **N-13** | **Farb- und Dekorationscodes in nativen `.plr`-Spielerprofilen (`^cRRGGBB`, `BOT-^c...^r`)** | `#57`, `#63`, `#68` | Divergent (`QA-05`, `QA-09`) | Nur String-Tests | In `bot_sessions.py:30` explizit vermerkt: *„colors remain gated until native verification“* | **`NOT_TESTED_RETAIL`** |
| **N-14** | **PR #63 `ssam.ai` Red Station Preset inkl. `cmd_cmdOnTick` (`20 Hz` Shell-Ausführung), `MOTD` & `Say(...)`-Intervall** | `#63` | Ja (`tools/redstation_preset.py`) | Nur String-Generierung (`10` Tests) | Weder Chat-Ausgabe noch `20 Hz`-Server-Tick-Overhead nativ gemessen | **`NOT_TESTED_RETAIL`** |
| **N-15** | **Gehärteter Supervisor (PR #50 + PR #67 `C1_SUPERVISOR_PATCH_PROPOSAL.patch`) & MCP-Receipt-Prüfung (`M1_MCP_RECEIPT_PATCH.patch`)** | `#50`, `#67` | Liegt nur als `.patch` vor! | Nur Offline-Validator | Nicht auf Zielhost eingespielt, kein Live-Lauf auf sauberem `7fc94a39...`-Build | **`NOT_TESTED_RETAIL`** |
| **N-16** | **Hybrid-Session-Architektur `C1` (`~602,8 MiB` Modell) & 16-Bot-Skalierung auf Hetzner CX22 (`3.819 MiB`, `0 Swap`)** | `#62`, `#68` | Nur Konzept + Offline-Planner | Offline-Modell | Keinerlei nativer Mehrprozess- oder 16-Slot-Lasttest | **`NOT_TESTED_RETAIL`** |
| **N-17** | **Sync-Hypothesen `H1`, `F11`, `F12` aus PR #65** | `#65` | Reine Analyse | Analytische Skripte | Explizit unbewiesene Hypothesen | **`NOT_TESTED_RETAIL`** |

---

## 2. Mindestanforderungen für den Abbau von `NOT_TESTED_RETAIL` vor Produktionsfreigabe

Ein Punkt darf erst dann von `NOT_TESTED_RETAIL` auf `QUALIFIED_RETAIL_107` hochgestuft werden, wenn **alle** folgenden Nachweise kryptografisch gebunden (`M1`-Receipt-Schema aus PR #67) vorliegen:

1. **Sauberer Zielzustand:** Verifizierter `GameMP.dll`-SHA256-Hash (kein schmutziges Overlay wie `54faabf0...`), dokumentierte `PersistentSymbols.ini` und exakt protokollierte `NoteConfigOnce`-Zeile im Serverlog.
2. **Echte Mehrspieler-Staffelung:** Abgestufte native Läufe auf `RedStation.wld` **und** mindestens einer zweiten mehrstöckigen Deathmatch-Map mit:
   - `4 Bots` (`>= 15 min`),
   - `8 Bots` (`>= 30 min`),
   - Zielkapazität (`z. B. 8–12 Bots + >= 1 echter Vanilla-1.07-Human-Client` über `>= 30 min`, inkl. aktivem Human-Join/Leave zur Prüfung von `reserved_human_slots`).
3. **Harte Null-Fehler-Kriterien (`c2_sync_gates.py`):**
   - `0` `SYNCBAD`-Einträge,
   - `0` Paket-/CRC-Disconnects des Vanilla-1.07-Clients,
   - dokumentierte p95/p99-Tick-Dauer `< 50 ms` (`SYNCLATE`-Quote innerhalb definierter Schwelle),
   - Host-RAM-Minimum durchgehend `>= 1.068 MiB MemAvailable` (`0` OOM-Events),
   - reale Gameplay-Telemetrie: nicht-triviale Bot-Kills (`> 0`, kein 100-Tick-Blindfenster wie in `AI2-B4`), verifizierte Item-Pickups pro Minute und endliche Stuck-Recovery-Rate ohne Wand-Oszillation.
