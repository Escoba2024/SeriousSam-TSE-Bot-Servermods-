# ssam.ai — Agent 2 Ausführungsplan M2+M3 (Red-Station Kampf/Navigation)

> **Agent:** einmaliger zweiter OpenCode-Entwicklungsagent (Task `79587cd6930dcf09db7c5eee`)  
> **Modell:** `opencode-go/kimi-k2.7-code`  
> **Issue:** GitHub #90, Master #88  
> **Worktree:** `/home/opencode-tse/workspaces/ssam-m2m3-agent2-20261030`  
> **Branch:** `agent/opencode/20261030-m2m3-agent2`  
> **Basis-HEAD:** `5c8df7108430286a59786ad55fbb75762bf9e489` (M2 Human AI2 Stand)  
> **Start (UTC):** 2026-10-30T18:23:00Z  
> **Scope:** Offline-Entwicklung M1–M4. **Kein Deployment, kein Live-Test, kein Merge.**  
> **Native Gates:** 1/4/8 Bot 60/60/120 min ausdrücklich **AUSGESETZT**, nicht durchführen.

---

## 1. Ausgangslage (belegt)

### 1.1 Repository / Worktrees

| Worktree / Branch | HEAD | Status | Schutz |
|---|---|---|---|
| `tse-base` / `main` | `ab0c740` | sauber, unverändert | NICHT schreiben |
| `ssam-dashboard-20261030` | `27cf46a` | Task `871abf…` exit0, nicht anfassen | NICHT schreiben |
| `ssam-finalization-20261030` | `6b2d27c` | unverändert erhalten | NICHT schreiben |
| `ssam-m1-agent-20261030` | `b406805` | M1 lokal | NICHT schreiben |
| `ssam-m2-agent-20261030` | `5c8df71` | M2 lokal | NICHT schreiben |
| `ssam-m3-integration-20261030` | `ab0c740` | Reset zu main, 157 gelöschte Dateien | NICHT schreiben |
| `ssam-mcp-integration-20261030` | `b095e00` | MCP Staging | NICHT schreiben |
| **Dieser Worktree** | `5c8df71` | **aktueller Arbeitsbranch** | schreibend erlaubt |

### 1.2 GitHub-Issues / PRs

| # | Titel | Stand laut Webfetch (2026-10-30) |
|---|---|---|
| #88 | MASTER: TSE Classic 1.07 finalisieren M1–M4 | offen, persistenter Gesamtauftrag |
| #90 | Einmaliger Folgeagent M1–M4 | **STARTED** mit Task `79587cd…`, PID 18172/18173 |
| #80 | M1: reduce duplicate log decoding | Draft, RAM-blocked, 6-Bot-Grenze |
| #81 | M2 Human AI2: reviewed combat integration | Draft, CODE_COMPLETE / NATIVE_QA_PENDING |
| #82 | M2: native combat and respawn evidence | Draft, IN_PROGRESS / NATIVE_QA_PENDING |

### 1.3 Codebasis im aktuellen Worktree

Alle folgenden Dateien liegen unter `poc/botcore/` bzw. `poc/ai-integration/gamemp/`.

| Komponente | Datei | Stand |
|---|---|---|
| Profile (5 Skills / 6 Personas) | `bot_profile.h` | implementiert, 555 Checks |
| Perception | `bot_perception.h` | implementiert, FOV/LOS-Budget |
| Aim | `bot_aim.h` | implementiert, OU-Bias, Trigger-Discipline |
| Waffen-Utility | `bot_loadout.h` | implementiert, Hysterese |
| Human-KI | `bot_human.h` | implementiert, `HumanBotPolicy` |
| Reactive Hinderniserholung | `bot_navigation.h` | implementiert, **keine globale Navigation** |
| Wegpunkt-Graph | `botcore_ai.h` | vorhanden, **ungenutzt** |
| Legacy Combat | `bot_combat.h` | vorhanden |
| Reconnect | `bot_reconnect.h` | vorhanden |
| BotDriver-Integration | `poc/ai-integration/gamemp/BotDriver.cpp` | M2-Stand, `bot_bHumanAI` Pfad |

### 1.4 Offline-Teststatus (lokal verifiziert)

Kommando: `cd poc/botcore && make clean && make test && make smoke && make bench`

| Suite | Ergebnis | Anmerkung |
|---|---|---|
| `test_botcore` | PASS | |
| `test_botcore_ai` | PASS | |
| `test_bot_reconnect` | PASS | |
| `test_bot_combat` | PASS (0 failures) | |
| `test_bot_weapon_input` | PASS (0 failures) | |
| `test_bot_navigation` | PASS (0 failures) | nur Hinderniserholung |
| `test_bot_human_ai` | PASS (555 checks) | |
| `test_botdriver_block` | PASS | Integration-Block Smoke |
| `bench_bot_human` | PASS | ≤0.62 µs/tick |

---

## 2. Ziele und Reihenfolge

### 2.1 M2+M3 — Human AI2 + Navigation 2.0 (Fokus Red Station)

**Ziel:** Die bestehende `HumanBotPolicy` um eine **enginefreie globale Navigations- und Item-Utility-Schicht** erweitern, ohne die qualifizierten Kampf-/Ziel-/Respawn-Pfade zu duplizieren oder zu beschädigen.

Konkrete Deliverables:

1. **A*-Wegfindung** auf dem bestehenden `WaypointGraph` (`botcore_ai.h`).
2. **Abgrundschutz** (`PitAvoidance`): einfacher ray-basierter Boden-Check, der vor Abgründen abbremst/umlenkt.
3. **Hindernisintegration**: Verbindung von `ObstacleRecovery` mit der globalen Pfadplanung (Pfeil auf nächsten Wegpunkt → lokale Hinderniserholung bei Blockade).
4. **Item-Utility-Schicht** (`ItemUtility`): Bewertung von Health-/Armor-/Waffen-Pickups basierend auf Bedarf, Distanz und Gefahr.
5. **Navigations-Policy** (`bot_navigation_v2.h`): Entscheidung "kampfen / zu Wegpunkt laufen / Item holen / sicherer Rückzug".
6. **Integration in `HumanBotPolicy`**: wenn kein sichtbares Ziel, Rückzug nötig oder Controller-Persona aktiv → Navigation aktivieren.
7. **Offline-Regressionstests** mit deterministischen Szenarien, ASan/UBSan-kompatibel.
8. **Red-Station-Beispielgraph** als dokumentiertes Format (`.nav`-Textdatei), **keine erfundenen Koordinaten** — Platzhalter für spätere native Vermessung.
9. **Dokumentation**: CecilBotMod-Konzepte berücksichtigt, aber kein Cecil-Code kopiert.

**Nicht im Scope:**
- Native Retail-Tests (nicht autorisiert, ausgesetzt).
- DLL-Build / MSVC-Build (ohne SDK/Windows nicht reproduzierbar).
- Echte Map-Geometrie / Navmesh-Generierung.

### 2.2 M4 — Dynamische Sessions

**Ziel:** Join/Leave/Reconnect/Session-Zeitfenster mit bestehenden Schnittstellen (`bot_reconnect.h`, `PresenceSchedule`) integrieren und offline qualifizieren.

Konkrete Deliverables:
1. Session-State-Maschine (`BotSessionState`): `Offline → Joining → Active → Leaving → Offline`.
2. Deterministische Join/Leave-Delays über `PresenceSchedule`.
3. Reconnect-Backoffs erweitern: exponentieller Backoff, Max-Retries, Reset nach Erfolg.
4. Mixed-human-safety: Population-Controller prüft menschliche Slots.
5. Offline-Tests für Session-Lebenszyklus.

### 2.3 M1 — Sync-/CRC-Schutz, Supervisor, Recovery

**Ziel:** Guards und Supervisor verbessern, ohne Abnahme vorzutäuschen.

Konkrete Deliverables:
1. Logging-Guards für `SYNCBAD` / `Too many bad syncs` / CRC-Fehler.
2. Restart-Backoff-Policy (keine Dauerrestart-Schleifen).
3. Ressourcen-Gates (RAM/Disk) als reine Policy-Funktion.
4. Dokumentation, dass 1/4/8-Bot-Gates ausgesetzt bleiben.

---

## 3. Status-Ledger

| ID | Meilenstein | Thema | Status | Begründung |
|---|---|---|---|---|
| A | M2 | Human AI2 Code | `OFFLINE_PASS` | 555 Checks + Smoke + Bench passen |
| B | M2 | Native Retail QA | `NATIVE_PENDING` | Nur autorisiert bei exklusivem Lease |
| C | M3 | A* Pathfinding | `OFFLINE_PASS` | `AStarPathfinder` in `bot_navigation_v2.h`, 30 Checks |
| D | M3 | Abgrundschutz | `OFFLINE_PASS` | `PitAvoidance` in `bot_navigation_v2.h`, ASan/UBSan clean |
| E | M3 | Item-Utility | `OFFLINE_PASS` | `ItemUtility` in `bot_navigation_v2.h`, need-based scoring |
| F | M3 | Navigations-Policy | `OFFLINE_PASS` | `NavigationPlanner` + `BotDriverPolicy`, 7+21 Checks |
| G | M3 | Red-Station-Beispiel | `OFFLINE_PASS` | `redstation.nav.example` mit `MEASURE_REQUIRED`-Markern |
| H | M3 | Offline-Regression | `OFFLINE_PASS` | `make test` + `make smoke` + `make bench` + ASan/UBSan |
| I | M4 | Session-State-Maschine | `NOT_STARTED` | Folgeschritt (nach Kapazität) |
| J | M1 | Sync-/Supervisor-Guards | `NOT_STARTED` | Folgeschritt (nach Kapazität) |
| K | Gesamt | Native 1/4/8 60/60/120 min | `SUSPENDED` | Ausdrücklich ausgesetzt |

---

## 4. Risiken und Blocker

| Risiko | Wahrscheinlichkeit | Auswirkung | Mitigation |
|---|---|---|---|
| Navigation 2.0 verändert deterministische Human-AI-Ergebnisse | mittel | Regression in 555 Checks | Strikte Trennung: Navigation nur aktiv ohne Ziel / bei Rückzug; alte Pfade unverändert lassen |
| Doppelte Policy-/Target-/Respawn-Owner | mittel | Architekturfehler | Eindeutige Ownership: `HumanBotPolicy` besitzt Targeting; `NavigationV2` besitzt Weg/Item; Adapter entscheidet Modus |
| Fehlende echte Red-Station-Koordinaten | hoch | Kein map-spezifischer Beweis | Format liefern, Koordinaten als `MEASURE_REQUIRED` markieren |
| Kein Windows/MSVC-SDK verfügbar | hoch | Kein DLL-Build in dieser Session | Reine enginefreie C++-Arbeit; Build bleibt `NOT_TESTED` |
| Unzureichende RAM für native Tests | hoch | Testabbruch | Keine nativen Tests starten |
| Verwechslung mit M2/M3/MCP-Worktrees | mittel | Fremde Arbeit überschreiben | Vor jedem Schreibzugriff Worktree/Branch prüfen; nur in diesem Branch committen |

---

## 5. Nächste Aktionen

M2/M3 Red Station ist **offline vollständig**. Folgeschritte (nur nach expliziter Kapazitäts-/Autorisierungsprüfung):

1. **M4-A1**: `BotSessionState` in `bot_reconnect.h`/`bot_session.h` entwerfen: `Offline → Joining → Active → Leaving → Offline`.
2. **M4-A2**: `PresenceSchedule` für deterministische Join/Leave-Delays erweitern und unit-testen.
3. **M4-A3**: Reconnect-Backoff-Policy erweitern (exponentieller Backoff, Max-Retries, Reset nach Erfolg).
4. **M4-A4**: Mixed-human-safety prüfen (Population-Controller, menschliche Slots).
5. **M1-A5**: Logging-Guards für `SYNCBAD` / `Too many bad syncs` / CRC-Fehler ergänzen.
6. **M1-A6**: Restart-Backoff-Policy und Ressourcen-Gates (RAM/Disk) als reine Policy-Funktionen.
7. **Build/Native**: MSVC/DLL-Build und Retail-Abnahme bleiben **ohne SDK/exklusives Lease `NOT_TESTED`**.

---

## 6. Handoff-Informationen

- **Branch:** `agent/opencode/20261030-m2m3-agent2`
- **Basis:** `agent/opencode/20261030-m2` @ `5c8df71`
- **Arbeitsverzeichnis:** `/home/opencode-tse/workspaces/ssam-m2m3-agent2-20261030`
- **Vor dem nächsten Schreibzugriff:** Git-Setup-Lock `/tmp/opencode/ssam-agent2-20261030-setup.lock` verwenden (atomar mit `set -o noclobber`).
- **Nicht verändern:** `tse-base`, Dashboard-, Finalization-, M1/M2/M3/MCP-Worktrees.
- **Native Tests:** Nur nach expliziter autorisierter Freigabe und exklusivem Runtime-Lease.
- **Merge/Push:** Nicht ohne separate Autorisierung und Credentials-Prüfung.

---

## 7. Änderungshistorie

| Zeit (UTC) | SHA | Kommentar |
|---|---|---|
| 2026-10-30T18:23:00Z | `5c8df71` | Worktree/Branch angelegt, Plan initial erstellt. |
| 2026-10-31T00:50:00Z | `TBD` | Fortsetzung Task `79587cd6930dcf09db7c5eee`: `test_bot_driver_policy.cpp` repariert, `bot_driver_policy_bridge.h` + Test angelegt, `redstation.nav.example` erweitert, alle C++/Python-Tests + ASan/UBSan passen. |
