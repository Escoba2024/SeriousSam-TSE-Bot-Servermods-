# ssam.ai – Unabhängiger technischer Audit (LM Arena Agent)

**Datum:** 2026-11-01 (Europe/Berlin / UTC)
**Autor:** Unabhängiger Audit-Agent (Arena.ai Agent Mode), keine Implementierung, nur Analyse und Doku
**Scope:** Primär-Repository `Escoba2024/SeriousSam-TSE-Bot-Servermods-`, Referenz `DreamyCecil/CecilBotMod`, `DreamyCecil/SE1-ModSDK`, `Croteam-official/Serious-Engine` (1.10-Referenz)
**Begleitdokument:** [2026-11-01-lmarena-codex-handoff.md](2026-11-01-lmarena-codex-handoff.md) (umsetzbares Backlog für Codex)

Kennzeichnungen: **TESTED** = in dieser Audit-Sitzung selbst reproduziert oder in einem veröffentlichten, hashbelegten Native-Lauf nachgewiesen. **NOT_TESTED** = nicht im Audit oder in keinem veröffentlichten Lauf geprüft. **BLOCKED** = technische Blockade dokumentiert. **HYPOTHESE** = klar gelabelte Vermutung, kein Nachweis.

---

## 1. Executive Summary

1. **Der Hauptzielzustand „acht stabile Bots auf Red Station" ist nicht nachgewiesen und derzeit BLOCKED.** Die einzige 8-Bot-Stunden-Abnahme (3600 s, 2×4, Zero SYNCBAD) existiert für **Yodeller** (integrierte DLL `7fc94a39…`, 21.10., Wine/Hetzner) und für **Fortress** (qualifizierte 61DC-DLL, 12.10., Shadow). Auf Red Station liegt nur 1-Bot-/2-Bot-Evidenz von 150–300 s vor (PR #82, Build03 `a62a19e7…`). Der öffentliche Server wurde am 26.10.2026 auf ausdrückliche Nutzeranweisung heruntergefahren (M1-M4-Goal-Ledger, PR #74). Die 8-Bot-Abnahme am Zielhost ist am RAM-Guard gescheitert (1.039,3 MiB verfügbar vs. 1.068 MiB benötigt, PR #80 / Issue #79).

2. **Die Ursache von „Too many bad syncs" bleibt offen.** Der Retail-Kick-Mechanismus (Handler `FUN_601A2D10`, Schwellwert 10, Disconnect) ist per Ghidra-Dekompilation der unveränderten Engine.dll (`B79BF8…`) **TESTED/geprüft**. Die bisher einzigen nativ belegten Fehlerszenarien (10.10., alte Kandidaten: 1→10 SYNCBAD + Disconnect) und der 26.10. Cecil-P1-Vierbot-Versuch (5 SYNCBAD in 97,93 s) konnten nicht reproduziert werden; derselbe DLL-Hash lief 152,43 s Vier-Bot mit 0 SYNCBAD. Die vom 17.10.-Bericht angeordnete **Isolation des ersten divergenten Ticks** (CRC + Actions beider Seiten) ist bis heute nicht durchgeführt bzw. nicht veröffentlicht. Neue, mit Quellbeleg untermauerte Hypothese dieses Audits: **Haltezeit des `ga_csNetwork`-World-Locks im Bot-Timer** (4 lokale Bots × LOS-Ray-Budget ohne globale Obergrenze pro Tick) verzögert die eigene Client-Simulation und ist ein belastbarer SYNCBAD-Kandidat (Abschnitt 5.4).

3. **Die größte konkrete Chance für M3 (Navigation) liegt vor der Tür und ist im aktuellen Plan ungenutzt:** CecilBotMod liefert mit `Cecil/Navmeshes/RedStation_5AF1A276.nav` **193 echte Wegpunkte für Red Station** (Format vollständig analysiert und in diesem Audit geparst). Der aktuelle M3-Plan (PR #91) enthält dagegen nur eine **12-Knoten-Platzhalter-Datei** mit `MEASURE_REQUIRED`. Das Konvertieren und nativ verifizieren der Cecil-Navmesh-Punkte ersetzt den Großteil der manuellen Vermessung (Abschnitt 8, Befund N-1).

4. **Die AI-Schicht (Human-Bot-Policy) ist der technisch reifste Teil des Projekts.** 555 deterministische Offline-Checks + 5 Stufen + 6 Persönlichkeiten, im Audit selbst reproduziert (`make test/smoke/bench`, alle PASS). Im produktiven Build ist allerdings **Strafen deaktiviert** (`bot_fStrafeScale=0`), es wird **kein Zielfernrohr** gezogen (keine `PLACT_SNIPER_USE`-Actions), und **Item-Suche ist offline, aber nicht integriert** (PR #55). Gegen CecilBot ist das Zieldesign prinzipiell überlegen (korrelierter Fehler statt 0,5-s-Random); gegen Cecil fehlen Navigation, Pit-Avoidance und Items (Abschnitt 7).

5. **M1-Reliability-Infrastruktur ist ausgebaut, aber nicht qualifiziert:** Pair-Sync-Producer (PR #74), Hypothesen-Toolkit (PR #65, 92 Tests), Forensik-Toolkit (PR #58, 29 Tests), Supervisor-Werkzeuge (`fleet_supervisor.py`) existieren, sind aber (a) auf ältere Kandidaten source-pinned, (b) nicht produktiv aktiviert, (c) durch den RAM-Blocker und die suspendierten 60/60/120-Minuten-Gates nicht abgenommen (Abschnitte 10, 11).

**Priorisierte Empfehlung (Kurzform):** (1) RAM-Vorcondition beheben (Issue #79) → (2) ersten divergenten SYNCBAD-Tick auf dem aktuellen Kandidaten isolieren (T-01) → (3) Red-Station-Navgraph aus der Cecil-Navmesh erzeugen und nativ verifizieren (T-03) → (4) globalen Ray/Lock-Budget-Schutz einführen (T-04) → (5) 8-Bot-Red-Station-3600-s-Abnahme als M1+M2+M3-Gesamtgate (T-05). Details im Handoff.

**Zweite Durchsicht (01.11.2026, 19:00 UTC) — drei Änderungen zum obigen Stand:** (a) **PR #39** (`agent/bot-ai-cecil-20261020` @ `1433bc9`, Draft) enthält bereits einen strikten BNMV-v6-Converter **und 9 konvertierte Navmeshes** — inkl. RedStation (193 node/879 arc/1 locked; im Audit bytegenau gegen Cecils `PathPoint.cpp` verifiziert, 12.245/12.245 Bytes) → T-03 wird zu **Validierungs- und Integrationsaufgabe** (kein Neuparser). (b) BNMV-v6 **speichert die Kanten** pro Punkt (Nachbarlisten + Polygon-UBYTE); die erste Durchsicht hatte dies unvollständig als „Kanten nicht in der Datei" klassifiziert — korrigiert in §8.1. (c) **Neuer Befund A-10 (P1):** Im Projekt laufen **drei parallele Kampf-Policy-Linien** (Human-AI/`bot_human.h`, Cecil P1/PR #57, Cecil-Taktik-AI/PR #39) plus PR #66-Research; Issue #93 verlangt „keine doppelten Policy-Owner" → neue Aufgabe **T-14 (Policy-Konvergenz, Entscheidungsdoku)** ergänzt das Backlog.

---

## 2. Untersuchte Repository-Revision

| Artefakt | Revision | Zeitstempel |
|---|---|---|
| Primär-Repo `main` (Checkout-Basis) | `ab0c7400353a108f8461bb82280c539fdfe81499` | 2026-10-25 17:04:06 +0100 |
| Audit-Ausführung (Sandbox) | – | 2026-11-01, ~18:20–19:00 UTC |
| CecilBotMod (Referenz-Klon) | `953b477e53fdc5a5d84c8ae8d759c84fdf6c973c` (branch `master`) | 2026-04-16 09:13:31 +0300 |
| SE1-ModSDK includes (Referenz-Klon) | `595a833b5a30493162b74d642bc6814a38b32eb5` | – |
| Serious-Engine 1.10 (Croteam, Referenz-Klon) | `main` bei Auditzeit | – |
| GitHub-Remote-Daten | PRs bis #95, Issues bis #94, Stand 2026-10-31/11-01 | – |
| **Nachschau 01.11. (zweite Durchsicht)** | PR #39-Branch `agent/bot-ai-cecil-20261020` @ `1433bc9` (BNMV-v6-Converter + 9 konvertierte Navmeshes), Issue #92-Kommentar 01.11. 13:50 UTC (Live-Flottenzustand), Issue #93 (Cecil-first-Auftrag mit Verweis auf PR #39) | 2026-11-01, ~19:00 UTC |

**Hinweis zur Historie:** Der lokale Checkout enthält exakt **einen** Commit auf `main` (`ab0c740`, „docs(deploy): record ssam.ai IP deployment, QA and rollback release"). Die Commit-Historie ist also im Audit-Checkout nicht vollständig; der aktuelle Entwicklungsstand wurde daher zusätzlich aus GitHub-PRs/-Issues (Stand bis 2026-11-01) und deren Branch-Heads (insb. `agent/publication/20261031-m2m3-redstation` @ `dc64cc6`, `agent/chat/20261026-m1-m4-integration`, `agent/lead/20261030-m2-final` @ #82) rekonstruiert. Alle Zitate aus Agenten-Branches sind als solche gekennzeichnet.

**Geprüfte Artefakte (Auswahl, alle im Repo vorhanden):** `AGENTS.md`, `README.md`, `docs/coordination/*` (inkl. PR-74-Ledger), `docs/reports/2026-10-12-shadow-development-status.md`, `2026-10-17-retail107-sync-check-investigation.md`, `2026-10-20-bot-ai-profiles-and-perception.md`, `2026-10-21-human-cpu-final.md`, `2026-10-21-integrated-runtime-results.json`, `poc/release/gamemp/*` (13 Dateien), `poc/candidates/integrated-human-cpu-20261021/*`, `poc/botcore/*` (inkl. 7 Test-Suiten), `poc/patch/0001–0009`, `poc/scripts/*` (Fleet/Release), `tools/*` (Sync-Analyse, GameSpy-Query, Telemetrie).

**Eigen ausgeführte, isolierte Tests (keine Produktion, kein Retail, kein Netzwerk):**
- `cd poc/botcore && make test` → **alle Suiten PASS**, u. a. `HUMAN AI PASS: 555 checks, 0 failures` (reproduziert, g++13, Linux).
- `make smoke` → `INTEGRATION BLOCK PASS` (reproduziert).
- `make bench` → 0,55–0,61 µs/Bot/Tick (reproduziert; Report-Werte 0,38–0,48 µs, andere CPU).
- `python3 verify_patch.py` → `PATCH VERIFY PASS` (reproduziert).
- CecilBotMod-Klon + Binär-Parsing der 9 Navmesh-Dateien (Python, ohne Engine).
- Statische Quellanalyse aller obigen Pfade; keine Datei verändert.

---

## 3. Tatsächlich verifizierter Entwicklungsstand

### 3.1 Qualifizierte/aktive Kandidaten (Hash-Evidenz aus den Berichten)

| Kandidat | SHA256 | Status |
|---|---|---|
| 61DC-Referenz (12.10.) | `61DC27E0E7B80BADCF9AE705C30FCA88EDD3935737715DFFFF59E90C26F1FEF9` | Lokal qualifiziert: 8-Bot-KI-Stunde auf **Fortress** (3697,29 s, 480 aktive Bot-Minuten, 69 Brush-Advances ≥ 2 m, 0 SYNCBAD). Bytegenauer Quellabgleich in `poc/release/gamemp/` (13 Dateien, `tools/Verify-SourceProvenance.py`). |
| Build04 integriert (21.10.) | `7fc94a39c3f5d9516f262d9e4d04a5cf38e6eb5ae3482976c32c952a99d30835` | Wine/MSVC-Build, Quellen `poc/candidates/integrated-human-cpu-20261021/`. 8-Bot-Stunde auf **Yodeller** mit Original-Client (3600 s, 12×5-Min-Fenster aktiv, 0 SYNCBAD, 3 CRC-OK), 600-s-öffentlicher Smoke, 4 externe WAN-UDP-Queries. War bis 26.10. produktiv auf 91.99.75.33:25600. |
| M2 Build03 (30.10.) | `a62a19e75251f69207966bb8965c019d8c7e76458099e6eb86bfddc4cb1ee5dd` | PR #82: native M2-Evidenz auf **RedStation** (1 Bot 300 s, 2 Bots 300 s, 2 Bots 150 s aggressor): echte Colt-Schäden/Kills, Respawn-Zyklen, Munitionsverbrauch, keine beobachteten Sync-/CRC-Fehler. |
| Cecil P1 (25.10., PR #57) | `7dc961c8…` (Teilhash im 26.10.-Ledger) | **Nicht qualifiziert:** historischer 4-Bot-Lauf FAIL (97,93 s, 5 SYNCBAD); neuer 4-Bot-Lauf mit anderer Harness 152,43 s, 0 SYNCBAD (Nicht-Reproduzierbarkeit, M1-M4-Ledger). |
| Ground-Lookahead (11.–12.10.) | `53982F05…` | FAIL/ungeklärt: native Sync-Fehler beim aktivierten 600-s-Retry; aus der qualifizierten Quelle ferngehalten (AGENTS.md). |
| M2/M3 Offline (31.10., PR #91) | Quellbaum `dc64cc6` | Offline-only: `bot_navigation_v2.h` (A*, Item-Utility, Pit-Logik), `bot_driver_policy_bridge.h`, 613 Checks/0 Fehler, ASan/UBSan. `redstation.nav.example` = **Platzhalter** (12 Knoten, `MEASURE_REQUIRED`). |
| Cecil-Taktik (20.10., PR #39) | `C65CB29BB17D9BE85CBC597D95C55E7ABE2A9D67C159ADE2735C096FDC6396D1` (experimentell) | Opt-in-TaktikAI (`bot_bTacticalAI`), BNMV-v6-Converter + 9 konvertierte Cecil-Navmeshes (inkl. RedStation 193/879), 75-s-native-8-Bot-Fleet-Smoke auf Shadow PASS (0 SYNCBAD-Marker), Windows-Build OK. **Nicht qualifiziert:** 60-Minuten-/CRC-/CPU-/RAM-Gates offen, kein aktives Pathfinding, Abgrundsicherheit der Seitwärtsbewegung offen. Zweite, neben der Human-AI laufende Policy-Linie (Befund A-10). |

### 3.2 Produktions-/Betriebszustand (wichtig für alle Schlussfolgerungen)

- **Öffentlicher Server: offline.** M1-M4-Goal-Ledger (PR #74, 26.10.): „Public gameserver explicitly disabled by user"; PIDs 399158/399232/399305 beendet, Ports 25600/25601 nach Signalen frei. Das README (Abschnitt „Aktuelle Integration – 21.10.2026") bezeichnet 91.99.75.33:25600 weiterhin als „Öffentlich aktiv" — dieser Abschnitt ist als **datierter Snapshot vom 21./25.10.** zu lesen (siehe Befund D-1).
- **Live-Zustand am 01.11.2026 13:50 UTC (Issue #92, read-only-Live-Diagnose des Folgeagenten):** `ssam-tse-live.service` **aktiv** als *server-only*-Launcher (Map Yodeller, **0 Spieler**), die alten Bot-Units `tse-play-20261030-bota/botb.service` im Zustand **failed**. Das bestätigt den Zustand „Server läuft, keine Bots" — es spielt aktuell **keine** 8-Bot-Session; „aktiver Betrieb" ist nur im Sinne des 21.-25.10.-Snapshots korrekt.
- **Unpublished-Backlog:** Laut Issue #92 existiert lokal (Hetzner/OpenCode-Host) ein Branch `agent/chat/20261101-m2m3-live-diagnostics` (Commit `e5aa3af7`, Basis `62fc6cf`) mit `tools/operations/inspect_live_fleet.py` (15 Unit-Tests, TDD RED→GREEN, read-only) und **52 Commits vor `origin/main`, die noch nicht gepusht sind** — GitHub-Authentifizierung auf dem Host ist blockiert (`could not read Username`, `GIT_TERMINAL_PROMPT=0`). Bis zum Push sind diese Stände für andere Agenten (und Audits) nicht sichtbar — bei Abgleich immer Issue #92 und lokale Inventur mitprüfen.
- **Native Langzeitabnahmen der M1-M4-Kandidaten sind suspendiert** („1/4/8-bot 60/60/120 min gates: SUSPENDED — Do not run without explicit authorization", PR #91-Handoff).
- **RAM-Blocker:** Der M1-Zielhost (Ubuntu, 2 vCPU, ~3,7 GiB RAM, kein Swap) kann 8 private Bot-Clients nicht mehr admettre: Lauf mit 6 Bots, Stopp vor Client 7 bei 1.039,3 MiB verfügbar vs. 1.068 MiB benötigt (PR #80). Issue #79 offen.
- **Geschützte Artefakte:** 61DC-DLL unverändert; 415-Datei-Rollback-Archiv SHA256-verifiziert (Ledger 26.10.); Retail-Originale hashgepinnt.

### 3.3 Was „funktioniert" heißt (Grenzen)

„BESTANDEN"-Angaben in den Berichten sind **Scope-qualifiziert** (Map, DLL-Hash, Umgebung, Dauer). Der Audit bestätigt diese Trennung in den Dokumenten überwiegend als sauber; die einzige dokumentarische Unschärfe ist die README-Produktivangabe (D-1). Keine der „BESTANDEN"-Angaben ist als generelle Runtime-Kompatibilität zu lesen — zutreffend so in den Berichten gekennzeichnet.

---

## 4. Architektur-Review

### 4.1 Bestätigte Grundarchitektur (TESTED, Quellabgleich)

- Bots sind **reine Client-Instanzen**: `CGame::GameHandleTimer()` → `BotDriver_HandleTimer(this)` (`poc/release/gamemp/Game.cpp:752-754`). Pro Tick (20 Hz) und pro lokalem Slot 0..3 wird ein `CPlayerAction` komponiert und über `CPlayerSource::SetAction(pa)` in den regulären Netzwerkpfad übergeben (`poc/candidates/integrated-human-cpu-20261021/BotDriver.cpp`, Abschnitt „3) compose the action"). **Keine** Server-/Entity-/Engine-Modifikation; Server und menschliche Clients unverändert. ✅
- Konventionen korrekt umgesetzt: `pa_vTranslation(3) = -moveFactor` (Vollgas = `-plr_fSpeedForward`), **absolute, nie auf 360 gewickelte** Heading-Winkel (Delta-Berechnung in `CPlayerEntity::ApplyAction`), Fire = Bit 0, Waffenwahl über Select-Group-Pulse am Rising-Edge (`bot_weapon_input.h::CombatWeaponInput::Poll`, Gruppen-Tabelle 1..8, `groups[15]={0,1,2,2,3,3,4,4,5,5,1,6,7,6,8}`).
- 2 Clients × 4 lokale Spieler für 8 Bots; `bot_iRosterOffset=0/4` teilt das 8-Bot-Roster.
- **World-Lock:** Die gesamte Player-Loop (Entity-Zugriffe, alle `CCastRay`s, `SetAction`) läuft unter `CTSINGLELock slBotWorld(&_pNetwork->ga_csNetwork, TRUE)`; Renderer-Sektorflag-RMW (0x40) wird über `tm_csHooks` gegen den Bot-Timer gesperrt (`Game.cpp` `GameRedrawView`, Kommentar: „Renderer sector-flag RMW also touches the ray scratch flag (0x40)"). Dies sind die Fixes aus Patches 0006/0007 — mit nativem Beleg (gemeinsamer Ray-Sektorstapel, konkurrierende Sektorflag-Schreibzugriffe, `docs/reports/2026-10-12-shadow-development-status.md`).
- **Reconnect:** `BotDriver_HandleReconnect` (Main-Thread-Stack, nicht Timer-Thread) mit Exponential-Backoff 2→10 s (`bot_reconnect.h`); nur „finished + disconnected" armt den Reconnect; Abbruch über ESC/WM_CLOSE/WM_QUIT. Offline getestet (`test_bot_reconnect` PASS, im Audit reproduziert).
- **Telemetrie:** `BotTelemetry.csv` (21 Felder, Watchdog-Thread schreibt weiter, wenn der Timer-Thread hängt — bewusste Deadlock-Diagnosefähigkeit), NullRender-Option (Renderframe-Skip bei `gm_bGameOn`, im produktiven Build04 aktiv, Draws=0 belegt).

**Bewertung:** Die Architektur ist schlank, korrekt getrennt (enginefreie `poc/botcore`-Regeln + dünne GameMP-Integration) und durch die Lock-Fixes auf einem soliden Fundament. Zwei strukturelle Schwachstellen: (a) der World-Lock-Hold ist nicht global budgetiert (Befund S-2), (b) die globale `ctl_pvPlayerControls` wird um die Komposition herum gezeroed (Befund S-4, P3).

### 4.2 Schichtmodell und Testbarkeit

`bot_profile → bot_perception → bot_aim → bot_loadout → bot_human` (Orchestrierung) ist vollständig enginefrei und unit-testbar; die Integration liest nur replizierte Player-Zustände (Position/Augenpunkt, `en_vCurrentTranslationAbsolute`, Health, Waffen) — **keine Server-Omniscenz**, kein Chat, keine Denktexte. Diese Eigenschaft ist korrekt: Client-seitige Bots dürfen nur beobachten, was der Client erhält.

---

## 5. Netzwerk-Synchronisation (SYNCBAD / „Too many bad syncs")

### 5.1 Geprüfte Mechanik (TESTED/verifiziert, 17.10.-Bericht + Ghidra)

- Retail 1.07 (unveränderte `Engine.dll`, SHA256 `B79BF8BB…`): Handler `FUN_601A2D10` (Case `0x13`, `CNetworkMessage::Read(...,0x10)`); vergleicht zwei Felder (1.10-Referenz: `sc_iLevel` und `sc_ulCRC` für denselben Tick), setzt den Counter bei Gleichheit auf 0, inkrementiert bei Abweichung, loggt `SYNCBAD` (optional) und **disconnectet bei Zähler ≥ 10** (`DAT_602A7EB4`, initialisiert in `CNetworkLibrary::Init`; im Binär 0a 00 00 00). Konfigsymbole `ser_iKickOnSyncBad`, `ser_bReportSyncBad/OK/Late/Early` in der Retail-DLL vorhanden.
- Sync-Check-Takt ~1 s (1.10-Referenz `Network.cpp` 95–107); in den Fehlläufen 10 SYNCBADs über ~9 s (Tick 83,40→92,40 bzw. 23,50→37,15).
- **Keine Empfehlung, `ser_iKickOnSyncBad` zu senken** — ausdrücklich abgelehnt (richtig; der Check ist der einzige Schutz vor Simulation-Divergenz).

### 5.2 Evidenzlage: was passiert, was nicht

| Lauf | Kandidat | Umgebung | Ergebnis |
|---|---|---|---|
| `eight-hour` / `eight-combat-only` (10.10.) | frühere Kandidaten (≠ 61DC) | Shadow lokal | **FAIL**: je 10× SYNCBAD + Disconnect (Log-Zeilen belegt, `tools/analyze_sync_log.py` auf beiden Originalen verifiziert). |
| 61DC-KI-Stunde (12.10.) | 61DC | Shadow lokal, Fortress | **PASS** (Scope): 3697,29 s, 0 SYNCBAD, 6 CRC-Akzeptanzen. |
| Hetzner-Kontrollen (16.–17.10.) | 61DC/1-Bot + Vanilla | Wine/Hetzner | PASS_LIMITED (2-Client-Kontrollen, 3600+ s, 0 Disconnects). |
| Build04-8-Bot-Stunde (21.10.) | `7fc94a39` | Wine/Hetzner, Yodeller | **PASS** (Scope): 3600 s, 0 SYNCBAD, 3 CRC-OK, 6430 SYNCOK. |
| M2-RedStation (30.10.) | `a62a19e7` | Wine, RedStation | 1-Bot 300 s, 2-Bot 300 s, 2-Bot 150 s: keine beobachteten Sync-Fehler (kurze Läufe). |
| Cecil-Taktik 8-Bot-Smoke (20.10.) | `C65CB29B…` | Shadow, nativ (Map im PR nicht genannt) | 75 s, 2×4 Bots, taktische KI aktiv: 8 Joins, CRC-OK, **keine beobachteten SYNCBAD-Marker** (kurzer Smoke, keine Abnahmedauer). |
| Cecil-P1 4-Bot (25.10./26.10.) | `7dc961c8` | Wine/Hetzner, privat | **FAIL** 97,93 s, 5 SYNCBAD; **nicht reproduziert**: gleicher DLL/Settings, neue Harness `qualify_bot_sessions.py`, 152,43 s, 0 SYNCBAD (Ledger + Repeatability-Review). |
| Ground-Lookahead (11.–12.10.) | `53982F05` | Shadow | **FAIL**: Sync-Fehler nur in aktiver Variante; dezaktivierte/probe-only-Kontrollen clean. |

**Interpretation (Audit):** SYNCBAD tritt in diesem Projekt **intermittierend** auf und ist an konkrete Kandidaten/Umgaben gebunden; die qualifizierten Kandidaten überleben lange Läufe. Der 26.10.-Vergleich (gleiche DLL, unterschiedliche Harness → einmal 5 SYNCBAD, einmal 0) ist das wichtigste neue Datenpunkt-Paar: Es deutet auf einen **Harness-/Timing-sensitiven Trigger** hin (z. B. Prozessstart-Reihenfolge, Poll-Raten, CPU-Last während des Laufs), oder auf einen Rest-Race, der nur unter bestimmter Scheduling-Bedingung schießt. **Root Cause: offen.**

### 5.3 Bestätigte, bereits behobene Mechanismen

1. **Geteilter Ray-Sektorstapel / Sektorflag-RMW** zwischen Timer-Thread (Bot-Rays) und Renderer/Simulation — nativ nachgewiesen, behoben durch `ga_csNetwork`-Hold (0006) + `tm_csHooks`-Render-Lock (0007). Danach: lange Läufe clean. **Diese Mechanik-Klasse ist die einzige mit echtem Native-Beleg.**

### 5.4 Offene Ursachen — priorisiert, mit Diagnoseverfahren

> Alle drei sind **HYPOTHESEN**; keine ist bewiesen. Die Reihenfolge folgt dem Produkt aus Plausibilität (Quellbeleg) und Prüfbarkeit.

**H1 (höchste Priorität): Client-eigene Simulation durch World-Lock-Hold verzögert → Sync-Check vergleicht versetzten Zustand.**
- Quellbeleg: `BotDriver_HandleTimer` hält `ga_csNetwork` für die komplette 4-Player-Loop; darin: bis zu 16 LOS-Rays/Player (Legacy-Vollscan) oder 4–8 (Human-AI-Budget) × 4 Player = bis zu ~32–64 `CCastRay::Cast` pro Tick pro Client, plus `GetPlayerEntity`-Lookup, Weapon-Lesung, `SetAction`. Der eigene Client-Simulationspfad (Network-Thread) braucht denselben Lock.
- Wirkung: Hält der Timer-Thread lange, simulierte der Client im Check-Zeitpunkt nicht bis zum vom Server geforderten Tick — der zurückgemeldete CRC-Paarwert weicht ab, obwohl die Simulation später konvergiert. Vanilla-Humans halten diesen Lock nie so lange; das erklärt, warum der Fehler bot-spezifisch ist und lastabhängig (CPU-saturierter Wine-Host) auftritt.
- Bestehende Messung: `BotTelemetry.csv` führt `lock_ms_max/lock_ms_last` — **wurde aber nicht als Sync-Proxy ausgewertet/veröffentlicht**.
- Diagnose (konkret): (a) In einem 8-Bot-Wine-Lauf `lock_ms_max`-Histogramm pro Prozess erstellen und gegen die erste SYNCBAD-Folge korrelieren (Pair-Producer aus PR #74 liefern die CRC-Seiten). (b) Gegenprobe: globalen Ray-Budget-Limiter (T-04) auf 12 Rays/Tick pro Client setzen und denselben Lauf wiederholen; sinkt `lock_ms_max`-p99 und verschwinden die SYNCBADs, ist H1 bestätigt. (c) Kontrolle: `bot_iScanInterval=4` (Legacy) bzw. `max_los_per_tick`-Reduktion als A/B.

**H2: Tick-Phasen-/Frequenzdrift des Bot-Timers (WinMM/Wine) vs. Server-20-Hz.**
- Beleg: Actions werden deterministisch im Timer-Takt erzeugt (`pa_llCreated` wird von `SetAction` gestempelt); der Server wendet Actions an Eintreff-Ticks an. Systematischer 20-Hz-Drift oder Jitter des WinMM-Timers unter Wine (Xvfb, CPU-Steal) verschiebt die Tick-Zuordnung einzelner Actions um ±1 — das CRC prüft Level+Tick-Paar.
- Diagnose: `BotTelemetry` liefert `tick_ms_max/tick_ms_avg` pro Sekunde — Histogramm über einen Lauf: Erwartung p99 ≤ 60 ms (50 ms Nenn); Clustering von `tick_ms_max`-Spitzen mit SYNCBAD-Folgen würde H2 stützen. Zusätzlich `sam_iMaxFPSActive`/Timer-Quantum im Log prüfen (bereits in `bot_bDiag`-Herzschlag).
- Abgrenzung: Reine Netzwerk-Latenz ist laut 17.10.-Bericht **nicht** als CRC-Fehlerursache bewiesen (und im LAN-Fall vernachlässigbar) — bleibt als Teil-Hypothese nur für WAN-Läufe.

**H3: Restlicher, nicht unter dem World-Lock geschützter Welt-/Entity-Zugriff im Timer-Pfad.**
- Beleg: Die 10.10.-Fehlläufe traten **vor** 0006/0007 auf; seit 61DC keine langen-Failure mehr — aber der Cecil-P1-Build (25.10., enthält neue Codepfade: `bot_route.h`, Interception, veränderte Aim-/Loadout-Pfade) scheiterte einmalig. Ein neuer Pfad könnte einen ungeschützten Zugriff (oder eine längere Lock-Hold) eingeführt haben.
- Diagnose: (a) Pair-Capture (T-01) auf dem Cecil-P1-Äquivalent des aktuellen Kandidaten; (b) Code-Audit aller `CCastRay`/`CEntity::Get*Entity`/`m_penWeapons`-Zugriffe außerhalb `CTSINGLELock(slBotWorld, ...)` (Audit-Fund: im aktuellen `BotDriver.cpp` sind alle im Lock; `BotDriver_HandleReconnect` läuft bewusst ohne Lock, aber nur im Disconnect-Zustand — akzeptabel); (c) ASan/UBSan-Debug-Build des GameMP-x86 (offline) + ein nativer 1-Bot-Debug-Lauf mit `bot_iLogEvery=1`.

**Nicht empfohlene Pseudo-Fixes** (wiederholt): `ser_iKickOnSyncBad=0`, Locks weglassen „weil es ja läuft", Ground-Lookahead reaktivieren, bevor die erste-Divergenz-Tick-Analyse vorliegt.

### 5.5 Bestehende Sync-Werkzeuge (Status)

`tools/analyze_sync_log.py` (loggenbasiert, im Audit gelesen, funktional), PR #58 (Forensik-Toolkit, 29 Tests, offline), PR #65 (Hypothesen-Registry + Verdict-Engine, 92 Tests, offline), PR #74 (`native_sync_handler_probe.py` — nur Handler-Zählung nativ qualifiziert; **interne Instruktionen-Hooks scheiterten** mit Wine-Pagefault bei `0x601a2d57` und sind verboten; `native_sync_snapshot.py` + Pair-Producer: 4-Bot-Läufe mit action/CRC-Paaren, 0 SYNCBAD, aber nur 152–360 s). **Fehlt: die eine, entscheidende Messung — CRC + Actions beider Seiten am ersten abweichenden Tick im Fehlfall.**

---

## 6. CecilBot-Vergleich (Architektur & Verhalten)

### 6.1 Architektur-Unterschied (entscheidend)

| Aspekt | CecilBotMod (`953b477`) | ssam.ai |
|---|---|---|
| Bot-Art | **Server-Entity** `CPlayerBot : CPlayer` (`Sources/Bots/Classes/PlayerBot.es:38`), `BotApplyAction`-Override | Reine Netzwerk-Clients, `CPlayerSource::SetAction`-Pfaden |
| Netzwerk | Binary-Patches auf `CMessageDispatcher::ReceiveFromClient*` und `CSessionState::ProcessGameStreamBlock` (`NetworkPatch/ServerIntegration.cpp:57-80`), eigenes Paket `MSG_CECIL_SANDBOX=49`, Stream-Block an **alle** Sessions | Kein Netzwerk-Patch, kein neues Paket, Vanilla-Strom |
| Weltzugriff | Serverseitig **omniskient**: `ClosestEnemy` iteriert alle Welt-Entities und liest sogar **die Zielzuweisung anderer Bots** (`penTargetEnemy == pen` in `BotFunctions.cpp:224-320`) | Nur replizierte Player-Zustände + eigene Health (bewusst, `bot_perception.h`) |
| Navigation | `_pNavmesh` (pro Map `.nav`), A*-Nächster-Punkt-Logik, „important points" (Items/Schalter/Marker), `PPF_JUMP/CROUCH/WALK/UNREACHABLE`-Flags | Reaktive 3-Strahlen-ObstacleRecovery (qualifiziert); globaler Nav = offline-only (PR #91) |
| Lizenz | GPL-2.0 | GPL-2.0-only (kompatibel); `THIRD-PARTY-NOTICES.md` nennt CecilBotMod bereits als Referenz |

**Folgerung (bestätigt die 20.10.-Analyse):** Eine Ganztübernahme ist mit der Vorgabe „Server/Entities unverändert" **unvereinbar** (Kategorie 4 in der Übernahmetabelle). Übernehmbar sind: Algorithmen, Parameterordnungen und **Daten** (Navmesh-Punkte), nicht die Entität/Netzwerk-Patches.

### 6.2 Verhaltens-Vergleich (funktion für funktion)

| Funktion | Cecil (Quellstelle) | ssam.ai (Quellstelle) | Bewertung |
|---|---|---|---|
| Zielwahl | `ClosestEnemy` mit 4 Prioritäten (sichtbar, niedriger HP, nah, zielt-auf-mich) + `fTargetCD` 1–3 s (`BotFunctions.cpp:224-320`, `BotSettings.cpp`) | Legacy: nächster sichtbarer, kein Gedächtnis (`bot_combat.h::DecideCombat`); Human-AI: Hysterese 1,35×/1,4×, Reaktionszeit, Gedächtnis `memory_s` (`bot_human.h::ChooseTarget`) | ssam Human-AI **überlegen** (prinzipieller, testbar); Legacy schwächer als Cecil. „Zielt-auf-mich" nicht portierbar (keine replizierten Target-Infos) — korrekt weggelassen. |
| Zielen | Zufalls-Winkel `±fAccuracyAngle/2` (Easy 10°, Hard 2°), alle 0,5 s neu (`BotMovement.cpp:289-307`), `fShootAngle` 15° als Feuer-Toleranz | OU-Prozess (korrelierter Bias, τ 0,24–0,55 s), mechanisches Overshoot-Modell (schwache Bremse), `settle_s` + `fire_tol_deg` 1,5–5° (`bot_aim.h`) | ssam **überlegen** (Drift statt Frame-Jitter; jede Fehlpriorität mechanisch erklärbar). Cecils 0,5-s-Refresh ist grober. |
| Vorhalten | `fPrediction` 0,1/0,2/0,5 + `FRnd()*fPredictRnd`, skaliert mit `(1 - bw_fAccuracy)` (`BotMovement.cpp:272-275`) | `prediction_gain` 0,05–0,9 × `distance/proj_speed` (`bot_human.h::Step`, `WeaponProfile.proj_speed`) | Vergleichbar; ssam deterministischer, stufenkalibriert. |
| Drehung | `fRotationSpeed = Clamp(dist/400, min, max)`, Limit 20–30°/s (`BotMovement.cpp:311-330`) | Rate/Beschleunigungs-Limits 110–340°/s, 320–1300°/s² pro Stufe (`bot_profile.h`) | ssam differenzierter (5 Stufen vs. 4 Presets). |
| Bewegung/Nav | Navmesh + important points + Pit-Avoidance (`CheckPit` via `WouldFallInNextPosition`, `BotMovement.cpp:341-397`) + Jump/Crouch + Health-skaliertes Strafen + 2–4 s Richtungswechsel | Vorwärts/Rückwärts, 3-Strahlen-Recovery (2 m Advance, Stuck-Detektor), **Strafe inaktiv** (`bot_fStrafeScale=0`), keine globale Nav, keine Pit-Avoidance (Ground-Lookahead FAIL) | **Cecil deutlich vorn** — die größte Verhaltenslücke (Befunde N-1, A-3, A-4). |
| Waffenwahl | Distanzband-Tabelle `dmg × accuracy` (14 Waffen, `_abwDeathmatchWeapons`, `BotWeapons.cpp`), `fWeaponCD` 3–5 s, `bw_fStrafe` pro Waffe, Frequency (Grenade 1,0 s) | Legacy: feste Bänder <10/≤30/>30 m (`botcore_ai.h::SelectWeapon`); Human-AI: Utility-Score (dps×accuracy×rangefit×Selbstschaden-Penalty) + Hysterese `switch_margin` + Dwell (`bot_loadout.h`) | ssam Human-AI **vergleichbar/besser** (Selbstschaden-Term, Hysterese); Cecils Grenade-Cadence (1-s-Frequenz) fehlt in ssam — kleine Lücke. |
| Items | `BotItems.cpp`: Typ-Distanzen (Waffe 16 m, Health 32 m, Rüstung 16 m, Munition 16 m), Sicht-Barriere, `m_ulPickedMask`, Cooldown 5 s, „coop: immer Items" | **Offline**: PR #55 `item-utility` (inkl. Cecil-Analyse) — nicht in Kandidat integriert; PR #91 NavV2 hat `kFetchItem`-Modus | **Lücke** (Befund A-5): auf Red Station bleiben Bots ohne Item-Verhalten sichtbar unter menschenähnlichen Spielern. |
| Tod/Respawn | `fRespawnDelay` 0–3 s pro Preset | Nativ: Fire-Press/Release-Puls (4-Tick-Flanke), Respawn im Originalspiel belegt (21.10./30.10.); **Defekt**: fehlende Player-Entity unterdrückt Fire (PR #95, Befund A-1) | Vergleichbar; ssam hat den Randfall-Defekt. |
| Sniper-Zielfernrohr | `UseWeaponScope`: `PLACT_SNIPER_USE | PLACT_SNIPER_ZOOMIN` bei Sicht, Zoom-out bei Sichtverlust (`BotWeapons.cpp`) | **Existiert nicht** — keine Scope-Actions in BotDriver | **Lücke** (Befund A-6): „Distanzschütze"-Persona mit Sniper (Index 13) schießt ohne Fadenkreuz-Zoom. |
| Gedanken/Chat | `SBotThoughts` (Textzeilen, `^c`-Farbcodes) | Bewusst weggelassen (keine Chattexte) | Korrekt gegenüber der Vorgabe. |

### 6.3 Lizenz

CecilBotMod ist GPL-2.0; das ssam.ai-GameMP ist bereits GPL-2.0-only → **Verwendung von Algorithmusideen: frei; Übernahme von Code/Dateien:** erlaubt, aber dann sind GPL-Verbindungs- und Hinweispflichten zu erfüllen (Attribution in `THIRD-PARTY-NOTICES.md`, Lizenzdatei erhalten). **Navmesh-Dateien** (`Cecil/Navmeshes/*.nav`) sind Daten; bei Übernahme als Referenzbasis für den eigenen Red-Station-Graphen gehört eine Quellenangabe dazu (T-03/T-12). Retail-1.07-Kompatibilität von CecilBotMod selbst ist aus dem Repository-Code nicht beweisbar (Server-Patches gegen 1.07-ABI, `Patcher/patcher.cpp`); das ist für uns nebensächlich, weil wir nur Ideen/Daten übernehmen.

---

## 7. KI- und Kampf-Analyse

### 7.1 Bestätigte Qualität (TESTED/offline + Scope-qualifizierte Native)

- 555 deterministische Human-AI-Checks reproduziert (Audit); Monotonie aller Stufen, Orthogonalität Persona×Skill, Ray-Budget, Hysterese, Gedächtnis, Overshoot-Mechanik — alle nachweislich.
- Native: 8-Bot-Yodeller-Stunde (21.10.) mit echten Fire-Actions/Kill-Score in allen 5-Min-Fenstern; M2-RedStation-Läufe (30.10.) mit Colt-Kills, Respawn-Zyklen, Munitionsabfall (Clip 6→4→3→1) — **Scope: je ≤ 2 Bots, ≤ 300 s**.
- CPU: Entscheidungsanteil 0,38–0,61 µs/Bot/Tick (Benchmark, Audit reproduziert) — vernachlässigbar; dominante Last ist Rendering/Wine (gelöst durch NullRender, Draws=0 belegt).

### 7.2 Schwachstellen (mit Quellenbeleg)

**A-1 (P1): Respawn-Feuerflanke bei fehlender Player-Entity.** `BotDriver.cpp` (alle Varianten): `if (localInput==NULL) { BotTelemetry_NoEntity(); ...; continue; }` — es wird **keine** Action emittiert, also kein Respawn-Puls, solange der `CPlayerSource` existiert, die Entity aber (Spectator-/Tot-Transition) fehlt. PR #95 (Draft) dokumentiert genau diesen Defekt und einen Guard-Fix; Build + native Smoke ausstehend. (Im Audit im Quelltext bestätigt.)

**A-2 (P2): Strafen inaktiv im Produktivbuild.** `bot_fStrafeScale` Default 0 (Report 21.10.: „StrafeScale bleibt 0"); die Persona-`strafe_bias`-Parameter (0,40–0,95) wirken also **nicht**. Sichtbare Folge: Bots stehen in der Distanzbandbreite und schieben nur vor/zurück — deutlich weniger „menschlich" als Cecil-Bots (die ständig strafing laufen, Richtungswechsel alle 2–4 s). Risiko bei Aktivierung: neu nativ verifizieren (0008-Highlight im 20.10.-Bericht: Strafe „nicht nativ verifiziert").

**A-3 (P1): Keine globale Navigation → Bewegungsmuster sind auf Red Station nicht überzeugend.** Ohne NavGraph: Bots ohne sichtbares Ziel drehen sich (Scan-Rate 40–70°/s) oder laufen in den 3-Strahlen-Recovery-Modus; sie verlassen nie systematisch ihre Map-Region, nutzen keine Gänge/Brücken/Katwalks. Auf Fortress/Yodeller (offene Maps) unsichtbar; auf Red Station (mehrstockig, Gänge) sichtbar. Cecil löst das mit Navmesh + important points. → T-03.

**A-4 (P2): Pit-/Abgrundsicherheit fehlt (Ground-Lookahead blockiert).** Cecils `CheckPit` (`WouldFallInNextPosition` mit temporärer `en_vNextPosition`/`en_fStepDnHeight`) ist der bewährte Mechanismus. Der ssam.ai-Versuch (Ground-Lookahead) **scheiterte nativ an Sync** (53982F05) und ist daher korrekt eingefroren. Alternative ohne Simulationseingriff: Pit-Kanten in den NavGraph kennzeichnen (aus der Cecil-Navmesh ableitbar oder per einmaliger Messung) und dort nicht hin pathfinden (T-03/T-08).

**A-5 (P2): Item-Suche nicht integriert.** Offline vorhanden (PR #55, inkl. Cecil-Item-Analyse), kein Candidate-Integration. Auf Red Station sind Health/Armor/Ammo/Weapon-Pickups zentrale Verhaltensanreize; ohne Item-Logik sammeln 8 Bots nichts, während ein Mensch immer wieder Pickups aufsucht. → T-08.

**A-6 (P2): Kein Sniper-Zoom.** Kein `PLACT_SNIPER_USE`/`PLACT_SNIPER_ZOOMIN` in BotDriver (im Audit via Suchlauf bestätigt: keine Treffer). Cecil nutzt Scope systematisch. Geringes Risiko (Vanilla-Action-Bits), sichtbarer Gewinn für Sniper-Waffen (Index 13) und Long-Range-Kampf. → T-09.

**A-7 (P3): Grenade-Kadenz fehlt.** Cecils `bw_fSpecial/Frequency` (Grenade 1,0 s) = kontrolliertes Abfeuern; ssam feuert bei erlaubtem Ziel den Fire-Button durch (engine-seitige Kadenz). Klein, aber für Wurf-/Raketenwaffen relevant. Optional in T-09/T-07 mitabdecken.

**A-10 (P1, neue Durchsicht): Drei parallele Kampf-Policy-Linien drohen zu doppelten Policy-Ownern zu werden.** Neben der produktiv integrierten **Human-AI** (`bot_human.h`, 555 Checks, Build04/M2-Kandidaten) laufen (a) **Cecil P1** (PR #57: Interception/`bot_route.h`, Fire-Cadence, Respawn; ein negativer Datenpunkt: 5 SYNCBAD in einem 4-Bot-Lauf, nicht reproduziert) und (b) die **Cecil-Taktik-AI** (PR #39: `bot_bTacticalAI`, eigenständige Taktik nach Cecil, experimenteller Build `C65CB29B…`, 75-s-Smoke clean), dazu PR #66 (`combat2`-Research). Issue #93 (Nutzerauftrag 31.10., „Cecil-first") verlangt ausdrücklich: *„Keine doppelten Policy-Owner oder redundanten Kontrollpfade"* und Wiederverwendung der Bestehenden. Risiko: parallele Kalibrierung, geteilte Integrationspunkte am selben `BotDriver.cpp`-Block, widersprüchliche A/B-Baselines (welche Policy ist die Kontrollgruppe?) und verzweigter Sync-Flächenwachstum. Empfehlung: **ein** Policy-Owner (Empfehlung: Human-AI, weil produktiv integriert und am besten getestet), die anderen Linien nur als **Selektionsquelle** (Cecil-P1-Feuerrhythmus, PR #39-Taktikmodule, PR #66-Waffencurves) per Review in den Owner einfließen; die Policy-Entscheidung dokumentiert in `docs/decisions/`. → T-14.

**A-8 (P3): `world.max_health = 100.0` hart in der Integration gesetzt** (`BotDriver.cpp` Human-AI-Block). In TSE-Deathmatch korrekt (Health-Cap 100, Rüstung separat) — nur bei künftigen Coop-/Mod-Maps zu prüfen. Keine Aktion.

**A-9 (Info): Legacy-Pfad** (`bot_bHumanAI=0`) bleibt bewusst erhalten (bitgleicher Fallback zum qualifizierten Kandidaten) — gut für A/B-Tests und Rollback.

### 7.3 Entscheidungsfrequenz/Stabilität

20-Hz-Tick, Entscheidungen pro Tick, aber Hysteresen (Ziel 1,35×/1,4×, Waffe Dwell + Margin) verhindern Flackern — offline belegt. CPU/Memory: 46,1 MiB/Bot prozessgeteilt (21.10.), 0,55–0,61 µs/Tick Policy — keine Effizienzprobleme; Raycasts dominieren (→ T-04).

---

## 8. Navigation & Red-Station-Bewertung

### 8.1 Befund N-1 (P1, wichtigster Navigation-Fund): CecilBotMod enthält eine echte Red-Station-Navmesh — und PR #39 hat sie bereits konvertiert

- Datei: `Cecil/Navmeshes/RedStation_5AF1A276.nav` (12.245 Bytes) im CecilBotMod-Repo. **Im Audit bytegenau geparst (Python):** Magic `BNMV`, Version 6, `nextPointID=195`, **193 Punkte, 879 gerichtete Kanten, 1 gesperrter Punkt, 0 Polygone**, Parser verzehrt exakt 12.245/12.245 Bytes. Format pro Punkt (gegen Cecil `PathPoint.cpp::WritePoint/ReadPoint` verifiziert): `BPPH` + idx + FLOAT3D + range + flags + important + next + [lockEntity + CPlacement3D, wenn ≠ −1] + **Kanzahl + Nachbarn (gerichtet)** + Polygon-UBYTE (+`PPO1`/`PPO2`-Daten, hier 0). Beispielhafter Punkt: (-51,25; 1,0; -37,75), range 2,0.
- **Korrektur zur ersten Durchsicht:** Die Kanten **sind** in BNMV-v6 pro Punkt gespeichert (Nachbarlisten); Cecils Raycast-Pfad (`CastPathPointRay`) dient der Laufzeit-Prüfung/Erweiterung, nicht dem primären Kantenbezug. Ein Kanten-Build via Raycasting ist damit nur noch Fallback.
- **Schon vorhanden im Projekt (PR #39, Branch `agent/bot-ai-cecil-20261020` @ `1433bc9`, Draft, 20.10.):** strikter `convert_cecil_navmesh.py` (BNMV-v6, validiert, polygon-fähig) und **alle 9 Cecil-Navmeshes bereits konvertiert**, u. a. `poc/experiments/tactical-ai/maps/RedStation_5AF1A276.waypoints` (193 `node` + 879 `arc` + 1 `# locked`, Header: „Door locks, jump/crouch flags and pit safety require runtime validation before any automatic path following"). Dazu `test_bot_nav_graph.cpp` und 5/5 Konvertertests (im PR belegt). **Konsequenz für T-03: Nicht neu erfinden — PR #39-Converter/-Daten als Basis übernehmen** und den verbleibenden Teil (native Validierung + aktive Pathfinding-Anbindung) fertigstellen. (Issue #93 weist dies explizit als „zwingend prüfen und wiederverwenden" aus.)
- **Wichtig zum Dateinamen:** `SaveNavmesh` baut den Namen aus `fnWorld.FileName()` + `fnWorld.GetHash()` (`Navmesh.cpp:88-96`). `CTString::GetHash()` ist eine **Name-String-Hash** (`_rotl(key,4)+toupper(c)`, `CTString.cpp:285-294` in der 1.10-Referenz; 1.07-Äquivalent) — **kein Dateiinhalt-Hash** (im Audit gegen diverse Kandidaten geprüft; exakter 1.07-Wert für „RedStation" nicht reproduziert → 1.07-Implementierung unterscheidet sich leicht, unkritisch). Folgerung: Der Name bindet an **Dateinamen/Pfad**, nicht an die Map-Inhalte.
- **Konsequenz für Validität:** Die 193 Punkte sind nur dann exakt, wenn Cecils `RedStation.wld` bytegleich mit dem Retail-1.07-`RedStation.wld` des Projekts ist (beide Retail 1.07 → sehr wahrscheinlich, aber **nicht beweisbar**, weil Cecils `.wld` nicht im Repo liegt). Nativ-Verifizierung bleibt Teil von T-03 (Walk-Test: jeder Punkt begehbar, jede Kante passierbar, Lock-Punkt als Türkandidat identifizieren).
- **Passung in die bestehende Architektur:** `WaypointGraph` (botcore_ai.h:147) fasst 256 Knoten × 8 Kanten/Knoten → 193 Punkte passen; **nach Kanten-Import** den Kantenbesatz pro Knoten prüfen (PR #39-Daten: max. Grad zu ermitteln; bei > 8 `kMaxEdgesPerNode` erhöhen oder längste Kanten prunen). `bot_navigation_v2.h` (PR #91) hat bereits A* + `kFetchItem`/`kRetreat`/`kAvoidPit`-Modi und 30 Checks — es fehlt also **nur die echte Graphdatenbasis (vorhanden in PR #39) + die native Anbindung + die Validierung**.
- **PR #39-Kontext (zweite Durchsicht):** Der PR enthält neben Konverter/Daten auch eine **Cecil-inspirierte taktische AI** (opt-in `bot_bTacticalAI`, experimentaler Build `C65CB29BB17D…`, 75-s-native-8-Bot-Fleet-Smoke auf Shadow PASS ohne SYNCBAD-Marker; 60-Minuten-Gates offen). Damit existieren im Projekt **drei parallele Kampf-Policy-Linien** (Human-AI/`bot_human.h` im produktiven Kandidaten, Cecil P1/PR #57, Taktik-AI/PR #39) plus PR #66-Research — siehe neuen Befund A-10 (Policy-Konvergenz).

### 8.2 Bestehender Navigation-Status

- **Qualifiziert (TESTED, Scope):** Reaktive ObstacleRecovery (3 Strahlen front/left/right, Stuck-Detektor, ≤40-Tick-Advance, Reset bei >64 m Teleport) — 69 Brush-Advances ≥ 2 m in der 61DC-Stunde.
- **Offline (PR #91):** `bot_navigation_v2.h` (A* über WaypointGraph, Item-Desirability, Pit-Modus), `bot_driver_policy_bridge.h` (21 Checks), `redstation.nav.example` (**Platzhalter**, 12 Knoten, `MEASURE_REQUIRED`).
- **Blockiert:** Ground-Lookahead/Synchrone Pit-Prüfung (Sync-FAIL, korrekt eingefroren).
- **Red-Station-spezifisch (TESTED, Scope):** Nur 1-Bot/2-Bot × 150–300 s M2-Kampfläufe (PR #82). **Kein** 8-Bot-Red-Station-Lauf, **keine** Nav-Abnahme, **keine** Spawn-/Item-/Hazard-Analyse der Map existiert in veröffentlichten Berichten. Aussagen wie „Bots verhalten sich auf Red Station überzeugend" sind derzeit **nicht** belegbar.

### 8.3 Was eine 8-Bot-Red-Station-Session braucht (Audit-Synthetik)

1. Echter NavGraph (T-03) → Bots verteilen sich, nutzen Gänge/Katwalks, erreichen Pickups.
2. Item-Logik (T-08) → wiederkehrende Bewegungsmotive.
3. Strafe + Scope (T-07/T-09) → kampfunterstützende Bewegungsvielfalt.
4. RAM + Supervisor (T-02/T-11) → 3600 s ohne Operator.
5. Gate-Spezifikation T-05 (12×5-Min-Fenster, alle 8 aktiv, 0 SYNCBAD, ≥ 1 CRC-OK, Vanilla-Observer-Join, Telemetrie-Komplett).

---

## 9. Multi-Bot-Reliability (M4)

### 9.1 Bestanden (Scope-qualifiziert)

- Phase-1 Reconnects (kontrollierte Reconnects/Mapwechsel, 12.10.-Status), Phase-3 Recovery-Stunde (3700,64 s, 480 aktive Bot-Minuten, Recovery-DLL `24053920…`), 3 Karten + fehlgeschlagene Joins + Hard-Exit als kurze Szenarien.
- Fleet-Start/Stop (`Start-BotFleet.ps1`: gestaffelter Start, Status-Datei, Rollback bei Teilschaden, PID-basiert ohne Namens-Lookup), Identitäts-Sidecars (PLC4-Profile + GUIDs, `Get-FleetIdentities`), Query-Readiness (vollständige eindeutige Namenslisten + konsistente Spielerzahlen, nicht nur Slotcount).
- Reconnect-Policy offline getestet (`bot_reconnect.h`, Backoff 2→10 s, nur finished+disconnected armt).
- Observer-Abbruch: `CloseMainWindow` vor Force (17.10.-Report; „Ghost"-Slot nach `Stop-Process -Force` dokumentiert).

### 9.2 Offene Lücken

**R-1 (P2): Supervisor nicht für aktuellen Kandidaten qualifiziert, nicht aktiv.** `tools/operations/fleet_supervisor.py` + `fleet_health.py` (PR #74) existieren; der Supervisor ist laut Ledger „source-pinned" auf den historischen `7fc94a39…`-Manifest und „has NO native reliability admission"; kein Service installiert/gestartet. Kein Nachweis von Crash→Restart→Rejoin-Zyklus, kein Host-Reboot-Test, kein Log-Rotation-Verfahren für `BotTelemetry.csv`/Game-Logs im Dauerbetrieb. → T-11 (nach T-01/T-05).

**R-2 (P0-RAM, siehe 3.2):** 8-Bot-Abnahme am Zielhost blockiert (Issue #79). Das ist die härteste Produktionsbedingung für M4. → T-02.

**R-3 (P2): Dynamische Population nicht abgenommen.** `PopulationCore.ps1`/`PopulationManager`-Regeln offline getestet (Human-Slot-Reserve, Bot-Erkennung per Namenspräfix); „dauerhafter, race-freier Population-Supervisor" laut 12.10.-Status nicht umgesetzt/abgenommen. Namensklassifikation per Präfix ist **nicht fälschungssicher** (ein Mensch kann „TSE_Bot…" heißen) — im Report korrekt als Grenze gekennzeichnet; für den M4-Goal („Bots bleiben 8") zunächst vertretbar.

**R-4 (P3): Ressourcen-Limits für 24/7.** `BotTelemetry.csv` wächst unbegrenzt (1 Zeile/s/Prozess ≈ 8640 Zeilen/Tag — vertretbar, aber keine Rotation definiert); Game-Logs des Dedicated Servers ebenfalls. RAM 46,1 MiB/Bot stabil über 1 h gemessen; 24/7-Leckfreiheit **nicht** behauptet (zutreffend). → T-13.

---

## 10. Meilenstein-Bewertung (M1–M4)

Legende: ✅ = mit Scope-Nachweis, ⚠️ = implementiert, nicht nativ verifiziert, ✖ = fehlt/blockiert.

### M1 – Synchronisation & Zuverlässigkeit

| Kategorie | Inhalt |
|---|---|
| ✅ Verifiziert | Retail-Kick-Mechanismus + Schwellwert 10 (Ghidra, 17.10.); World-/Render-Lock-Fixes 0006/0007 mit langläufigem Beleg (61DC-Stunde, Build04-Stunde, je 0 SYNCBAD); Pair-Sync-Producer (4-Bot, 152–360 s, action/CRC-Paare, 0 SYNCBAD, PR #74); Log-Decode-Optimierung (CPU-Ratio 0,068, PR #80); Offline-Sync-Tools (29+92 Tests). |
| ⚠️ Implementiert, nicht verifiziert | Supervisor-Werkzeuge (pinned, nicht aktiv); 60/60/120-Minuten-Gates (suspendiert); Cecil-P1-Kandidat (einmal 5 SYNCBAD, einmal 0). |
| ✖ Offene Probleme | **Root Cause offen** (Abschnitt 5.4, H1–H3); RAM-Blocker (Issue #79); erste-Divergenz-Tick-Isolation nie durchgeführt; interner Instrumentierungs-Weg blockiert (Wine-Pagefault, interne Patches verboten). |
| Tests & Grenzen | Offline: 147 (PR #74), 92 (PR #65), 29 (PR #58), 291 Tools. Native: nur ≤ 360-s-Läufe mit 0 SYNCBAD; **kein** Fehlfall mit Paardaten erfasst. |
| Nächste Schritte | T-01 (erste Divergenz isolieren, inkl. A/B gegen H1), T-02 (RAM), danach Gates 60/60/120 auf dem aktuellen Kandidaten. |
| Risiken | Neue Codepfade (PR #91-Nav, Item, Strafe, Scope) erhöhen die Sync-Oberfläche → jedes Feature braucht eigene Native-Sync-A/B (0 vs. 1, gleiche DLL sonst, `analyze_sync_log.py` auf dem Serverlog). |

### M2 – Bot-AI & Kampf-Intelligenz

| Kategorie | Inhalt |
|---|---|
| ✅ Verifiziert | 555 Offline-Checks (Audit-reproduziert); 5 Stufen/6 Personas im nativen Build (8-Roster im Lauf belegt, 21.10.); native Kampf-/Respawn-Evidenz (Colt-Kills, Respawn, Munitionsabfall) auf RedStation 1–2 Bots ≤300 s (PR #82); 8-Bot-Kampfstunde Yodeller (3600 s, alle 12 Fenster aktiv, 0 SYNCBAD, 21.10.); CPU-Abnahme (A/B/C-Fenster, NullRender −78,7% Client-CPU). |
| ⚠️ Implementiert, nicht verifiziert | Strafe (Scale=0), Item-Utility (offline), Sniper-Logik (fehlt), PR #95-Fix (Draft), M2-M3-Bridge (offline), Cecil-P1-Interception (`bot_route.h`) — letztere mit negativem Datenpunkt (5 SYNCBAD einmalig). |
| ✖ Offene Probleme | Kein 8-Bot-Kampflauf auf Red Station; keine Langzeit-Verhaltensdiversitätsmessung (z. B. Zeitanteile: kämpfen/laufen/items); Grenade-Kadenz; Respawn-Randfall (A-1). |
| Tests & Grenzen | Offline sehr stark; native Kampfbelege nur kurze 1–2-Bot-Läufe auf Red Station; Scorelisten sind keine statistische Rangfolgenstudie (im Report zutreffend so gelabelt). |
| Nächste Schritte | T-06 (PR #95 finalisieren), T-05 (8-Bot-Red-Station-Gate), T-07/T-09 (Strafe/Scope), T-08 (Items). |
| Risiken | Jede neue Verhaltensschicht muss die 20-Hz-Action-Pipeline deterministisch lassen (keine serverseitigen Effekte); A/B-Gates verpflichtend. |

### M3 – Navigation & Bewegung

| Kategorie | Inhalt |
|---|---|
| ✅ Verifiziert | Reaktive ObstacleRecovery (69 Brush-Advances ≥2 m, 61DC-Stunde); NavV2-A* + Bridge offline (30+21 Checks, PR #91); Reconnect/Mapwechsel-Nav-Reset. |
| ⚠️ Implementiert, nicht verifiziert | NavV2-native Anbindung (fehlt komplett), `redstation.nav.example` (Platzhalter), Pit-Modus (ohne echte Daten). |
| ✖ Offene Probleme | **Keine echten Red-Station-Wegpunkte** (T-03 schließt das via Cecil-Navmesh); Pit-Avoidance blockiert durch Ground-Lookahead-Vorgeschichte; kein Walk-/Edge-Verfahren. |
| Tests & Grenzen | Offline vollständig; native Nav-Abnahme auf Red Station: **nicht existent**. |
| Nächste Schritte | T-03 (Navmesh-Port + nativer Walk-Test), danach NavV2-Anbindung + 8-Bot-Abdeckungsmetrik (Anteil Map-Regionen, die ≥1 Bot in 60 s besucht). |
| Risiken | Falsche Waypoints (andere `.wld`-Revision) → Bots laufen in Wände/Abgründe → Stuck-Events; deshalb nur nach nativem Walk-Test aktivieren; Fallback = bestehende Reaktive Recovery (bitgleich erhalten). |

### M4 – Dynamische Sessions & Reconnects

| Kategorie | Inhalt |
|---|---|
| ✅ Verifiziert | Reconnect-Policy (offline + Phase-1/3 native Läufe); Fleet-Start/Stop mit Rollback (offline getestet, Phase-3 nativ genutzt); Ghost-Slot-Kenntnis + CloseMainWindow-Regel. |
| ⚠️ Implementiert, nicht verifiziert | Supervisor (pinned), Health-Check (GameSpy-Query vorhanden), Population-Regeln (offline), Session-Hybrid-Prototyp (PR #68, offline). |
| ✖ Offene Probleme | Kein Crash→Restart→Rejoin-Nachweis; kein Reboot-Test; keine dynamische Population nativ; RAM-Blocker; öffentliche Serverliste/333networks für die aktuelle Zielkonfiguration nicht abgenommen. |
| Tests & Grenzen | `Test-Fleet*.Tests.ps1` (12+ Suiten) offline; native M4-Lauf **nicht dokumentiert** (nur die M1-M4-suspendierten Gates). |
| Nächste Schritte | T-11 (Supervisor binden + Recovery-Tests), T-02 (RAM), T-05 (Gate als M4-Nachweis mitbetrachten). |
| Risiken | Supervisor-Fehlstarts (Join-Burst) → Server-Slot-Flapping; deshalb gestaffelter Start (besteht) + Health-Gate vor Restart (besteht offline) beibehalten. |

---

## 11. Priorisierte Befunde (Gesamtliste)

| ID | Schw. | Problem | Ort (Datei/Funktion) | Beleg | Ursache | Lösung (Kurz) | Vorteil | Sync-/Kompat-Risiko | Schritte (Kurz) | Verifikation (Kurz) | Konfidenz |
|---|---|---|---|---|---|---|---|---|---|---|---|
| S-1 | **P0** | 8-Bot-Red-Station-Nachweis fehlt; Native-Gates suspendiert; Server offline; RAM-Blocker | Hetzner-Host, Issue #79, PR #80, M1-M4-Ledger | PR #80 (1.039,3 vs 1.068 MiB), Ledger 26.10 (Shutdown) | Ressourcen + Prozesssteuerung, kein Code | T-02 + T-05 (Gate-Spec) | Ermöglicht das Hauptziel | keiner | RAM-Condition; Gate-Spec; Lauf | Gate-Report (12 Fenster, 0 SYNCBAD, CRC) | Hoch (Datenlage) |
| S-2 | **P1** | SYNCBAD-Root-Cause offen; erste-Divergenz-Tick nie isoliert | `FUN_601A2D10` (Retail), `BotDriver.cpp` | 17.10.-Bericht; 26.10.-Ledger (5 SYNCBAD vs 0) | offen; H1: Lock-Hold (s. u.), H2: Timer-Drift, H3: Restzugriff | T-01 (Paar-Isolation) + T-04 (Budget/SLO) | Verhindert sporadische Disconnects der 8-Bot-Flotte | niedrig (nur Diagnose + Budget) | Pair-Capture-Loop; A/B mit/ohne Budget | JSON: erster Tick + CRC-Paar + Actions | Mittel (Hypothese H1: Mittel-Hoch) |
| S-3 | **P1** | `ga_csNetwork`-Hold unbudgetiert (≤ 64 Rays/Tick/Client, 4 Player) | `BotDriver_HandleTimer` (`CTSINGLELock slBotWorld`), Legacy-Scan 16×4, Human-AI 4–8×4 | Quelltext (Audit); `lock_ms_max`-Feld existiert, ungenutzt | Architektur: Lock-Hold ∝ Ray-Anzahl | Globales Ray-Budget/Tick + p99-SLO-Alert | Kürzere Simulation-Latenz; weniger Sync-Druck; CPU | **gering–mittel** (Änderung der LOS-Frequenz kann AI-Verhalten leicht ändern → A/B) | Budget-Variable, Round-Robin, Telemetrie-Alert | `lock_ms_max`-Histogramm vor/nach; 4-Bot-Sync-A/B | Hoch (Mechanik), Mittel (Wirkung) |
| N-1 | **P1** | Echte Red-Station-Waypoints **existieren bereits konvertiert** (PR #39: 193 Punkte/879 Kanten), aber nicht validiert und nicht im aktiven Pathfinding; PR #91 nutzt noch den 12-Knoten-Platzhalter | PR #39 `poc/experiments/tactical-ai/{convert_cecil_navmesh.py,maps/RedStation_5AF1A276.waypoints}`; `poc/botcore/redstation.nav.example` | Audit-Parsing bytegenau (12.245/12.245 Bytes, 193/879/1 lock, gegen `PathPoint.cpp` verifiziert); PR #39 (5/5 Konvertertests); Issue #93 (Wiederverwendung angeordnet) | Daten vorhanden; native Validierung + Anbindung fehlen | PR #39-Daten übernehmen → nativer Walk-Test → aktive Pathfinding-Anbindung | M3 ohne neue Messkampagne abschließbar; echte Kartennutzung | niedrig (Read-Only-Daten + A*; Walk-Test isoliert) | T-03 | Walk-Test: 0 Stuck/Edge-Defekte; 8-Bot-Abdeckung | Hoch (Daten + Format + Konverter belegt) |
| A-1 | **P1** | Respawn-Fire unterdrückt bei fehlender Player-Entity | `BotDriver.cpp` (`localInput==NULL → continue`) | Quelltext (Audit); PR #95 (Draft, Fix+Helfer) | Code-Defekt (bekannt) | PR #95 finalisieren (Build+Smoke) | Zuverlässige Respawn-Kette | **niedrig** (mehr Fire-Edges → native Verifikation nötig) | T-06 | Kill/Death/Respawn-Sequenz in Retail-Lauf | Hoch (Defekt belegt) |
| A-2 | P2 | Strafe inaktiv (`bot_fStrafeScale=0`) | `BotDriver.cpp`, `bot_profile.h` (strafe_bias) | Report 21.10. | bewusst deaktiviert (nicht nativ verifiziert) | A/B aktivieren (0,3–0,5) | Bewegungsmenschlichkeit | mittel (neue Lateral-Actions) | T-07 | 4-Bot-Sync-A/B + Verhaltens-Telemetrie | Hoch (Zustand), Mittel (Effekt) |
| A-5 | P2 | Item-Logik offline, nicht integriert | PR #55 `poc/research/item-utility/` | PR #55 (offline, getestet) | Integrationsarbeit offen | T-08: NavV2-`kFetchItem` + Item-Utility anbinden | Pickups werden aufgesammelt (Matchrealismus) | mittel (mehr Bewegung + Waffenwechsel) | T-08 | Item-Events in 8-Bot-Lauf; Sync-A/B | Hoch (Zustand) |
| A-6 | P2 | Kein Sniper-Zoom | `BotDriver.cpp` (keine `PLACT_SNIPER_*`) | Suchlauf im Audit; Cecil `UseWeaponScope` | Feature-Fehlende | T-09: Scope-Bits bei Sniper+Sicht | Long-Range-Kampf funktional | gering (Vanilla-Bits) | T-09 | Scope-Telemetrie; Sync-A/B | Hoch |
| R-1 | P2 | Supervisor unpinned/aktiv + ohne Recovery-Nachweis | `tools/operations/fleet_supervisor.py` | PR #74, Ledger („no native reliability admission") | Qualifikation fehlt | T-11 nach T-01/T-05 | 24/7-Betrieb | niedrig (nur Operations) | T-11 | Kill-Test: Restart+Rejoin ≤ N s; Reboot-Test | Hoch |
| F-1 | P2 | Namenskonventionen inkonsistent (Roster `BOT-*` vs Fleet-Präfix `TSE_Bot`); 100-Namen-DB nicht in diesem Repo; Farbcodes (`^b/^i/^f/^c`) nicht nativ visuell abgenommen | `fleet-config.sample.json` (`botNamePrefix:"TSE_Bot"`), `bot_profile.h` (`BOT-Rookie-Rush` …), `PopulationCore.ps1` (Präfix-Klassifikation) | Quelltext (Audit) | Dokumentations-/Integrationslücke | T-10: versionierte Roster→Charakter-Name-Map + Präfix-Einigung + visuelle Abnahme | Supervisor-Klassifikation korrekt; Präsentation | keiner | T-10 | Ingame-Screenshot-Akzeptanz (Original-Client); Query-Name-Gleichheit | Hoch (Lücke), Namen-DB selbst: **nicht geprüft** (liegt außerhalb dieses Repos) |
| D-1 | P3 | README-Produktivangabe veraltet (Server 26.10. auf Nutzerbefehl offline; README sagt „Öffentlich aktiv") | `README.md` („Aktuelle Integration – 21.10.2026"), M1-M4-Ledger | Dokumentenvergleich (Audit) | Doku-Synchronisation | T-12: Status-Abschnitt aktualisieren (historisch vs aktuell) | Vermeidet Fehleinschätzung durch andere Agenten | keiner | T-12 | README-Durchsicht | Hoch |
| S-4 | P3 | `ctl_pvPlayerControls`-Zeroing um `ctl_ComposeActionPacket` (globale Puffer, Race-Fenster vs. Render-Prescan) | `BotDriver.cpp` (Abschnitt 3) | Quelltext (Audit) | Shared-Buffer-Design (Vanilla) | dokumentieren; nur bei Mixed-Human/Bot-Client relevant | Vermeidet Input-Glitches in Mixed-Szenarien | keiner | (nur Doku) | – | Mittel |
| R-4 | P3 | Keine Log-Rotation/Größenlimits für 24/7 | `BotTelemetry.csv`, Game-Logs | Architektur (Audit) | fehlende Betriebsvorschrift | T-13 | Disk-Sicherheit | keiner | T-13 | 7-Tage-Lauf ohne Disk-Fill | Hoch |
| A-7 | P3 | Grenade-Kadenz fehlt (Cecil `bw_fSpecial/Frequency`) | `BotDriver.cpp` Fire-Pfad | Cecil-Quellvergleich (Audit) | Feature-Fehlende | optional in T-09/T-07 | Wurfverhalten realistischer | gering | – | – | Mittel |
| A-10 | **P1** | Drei parallele Kampf-Policy-Linien (Human-AI, Cecil P1/PR #57, Taktik-AI/PR #39) + PR #66-Research; Doppel-Owner-Risiko, widersprüchliche A/B-Baselines | `poc/botcore/bot_human.h`, PR #57 `bot_route.h`, PR #39 `BotDriver-tactics.patch`, PR #66 `combat2_*` | Zweite Durchsicht (Audit): PR-Inventory; Issue #93 (Verbot doppelter Policy-Owner) | Koordinationsrisiko durch parallele Agenten | T-14: Ein Policy-Owner (Empfehlung: Human-AI) + Selektions-Reviews der anderen Linien | Eindeutige Baselines, kein paralleler Sync-Flächenwachstum | keiner (Entscheidungsdoku) | T-14 | Entscheidungsdoku + Owner-Mapping in `docs/decisions/` | Hoch (Bestand belegt) |

---

## 12. Konkrete Engineering-Empfehlungen (in Abhängigkeitsreihenfolge)

1. **T-02 RAM-Vorcondition (P0, Issue #79):** ≥ 8 GiB freie Reserve am Zielhost wiederherstellen (Memory-Eaters identifizieren, evtl. Bot-Flotte auf größeres Image/Host migrieren; Wine-Xvfb-Overhead prüfen). Ohne dies ist keine 8-Bot-Native-Abnahme möglich — alles Native hängt an dieser Bedingung.
2. **T-01 Erste-Divergenz-Tick-Isolation (P0):** Den Pair-Producer von PR #74 auf den **aktuellen** integrierten Kandidaten ausrollen und als Loop-Funktion betreiben: 10× 150-s 4-Bot-Läufe, (a) aktuelle Harness, (b) alte Harness-Konfiguration (Reproduktion des 26.10.-Fehlszenarios), (c) mit/ohne T-04-Budget. Jede SYNCBAD-Folge muss in einem Capture-Run landen; Auswertung: erster abweichender Tick, CRC-Paar, letzte N Actions beider Seiten (Paar-Produzent liefert bereits action inputs + CRC transitions). Zusätzlich `lock_ms_max`/`tick_ms_max`-Histogramme (H1/H2-Diskriminator).
3. **T-03 Red-Station-NavGraph (P1) — auf PR #39-Basis, nicht neu erfinden:** (i) PR #39-Converter `poc/experiments/tactical-ai/convert_cecil_navmesh.py` + konvertierte `maps/RedStation_5AF1A276.waypoints` (193 node/879 arc/1 locked) übernehmen (Format im Audit bytegenau gegen `PathPoint.cpp` verifiziert, inkl. Polygon-UBYTE und Lock-Placement); (ii) `WaypointGraph`-Kantenbesatz prüfen (max. Grad ermitteln; > 8 → prunen/`kMaxEdgesPerNode`); (iii) **nativer Walk-Test** (ein Bot, `bot_iLogEvery=5`: jeder Knoten aufgesucht, pro Kante Stuck-Events gezählt; Lock-Punkt als Türkandidat markieren; Abgründigkeit per Y-Verlauf prüfen) — Raycast-Kanten-Build nur als Fallback für fehlende Kanten; (iv) bei ≥ 95 % passierbarer Kanten: Daten-Import in `poc/botcore/redstation.nav` (Platzhalter ersetzen), Attribution CecilBotMod (T-12); (v) Anbindung an aktives Pathfinding (NavV2 `bot_navigation_v2.h` aus PR #91).
4. **T-04 Globales Ray-/Lock-Budget (P1):** `bot_iGlobalLosPerTick` (Default 16, 0=unlimited) in BotDriver: Round-Robin über 4 Player, Vorrang bestehender Targets (Human-AI `SortKey` kennt dies bereits). Telemetrie: `lock_ms_max` pro Sekunde (existiert) + neue Zählung `rays_global`; Alert im Log bei p99 > 5 ms. Sync-A/B vor/nach (4 Bots, 600 s, `analyze_sync_log.py`).
5. **T-05 8-Bot-Red-Station-Gate (P1, nach 1–4):** 3600 s, 2×4, Fragmatch, RedStation, Vanilla-Observer-Join; Gates: alle 8 in jedem 5-Min-Fenster aktiv (Bewegung+Fire), 0 SYNCBAD, ≥ 1 CRC-OK, ≤ N Stuck-Events/Nav-Events (T-03-Metrik), Telemetrie-Komplett, regulärer Shutdown, 415-Datei-Rollback-Prüfung. Dieses Gate ist **gleichzeitig** M1-Dauer-Nachweis, M2-8-Bot-Kampfnachweis auf der Zielmap und M3-Nav-Nachweis.
6. **T-06 PR #95 finalisieren (P1):** MSVC-x86-Build des Guarded-Fire-Fixes, 1-Bot native Smoke (gezielte Tötung des Bots, Spectator-Transition, Respawn innerhalb der Engine-Kadenz), danach in den Gate-Kandidaten.
7. **T-07/T-09 Strafe + Scope (P2):** jeweils isolierte A/B-Läufe (gleiche DLL sonst, 4 Bots, 600 s, Sync-Log + Verhaltens-Telemetrie); Werte konservativ starten (Strafe 0,3–0,5; Scope nur bei Sniper+Target).
8. **T-08 Items (P2):** PR #55 `item-utility` + NavV2 `kFetchItem` in den Kandidaten bringen (enginefreie Schicht bereits getestet); Red-Station-Item-Positionsliste aus Walk-Test (Knoten mit Item-Kommentar); A/B mit Item-Event-Zählung.
9. **T-11 Supervisor (P2):** nach T-05: Kandidaten-binden, Crash-Test (eigene Bot-Prozesse killen: Restart+Rejoin ≤ 60 s), Reboot-Test, Health-Gate (GameSpy-Query) vor jedem Start; danach als Dienst (keine produktiven Prozesse ohne Freigabe berühren).
10. **T-10 Namen (P2):** versionierte Roster→Charakter-Name-Zuordnung (im Repo, z. B. `poc/scripts/roster-names.json`), einheitliches Präfix-Verfahren für die Populations-Klassifikation, **einmalige** visuelle Abnahme von Farbcodes im Original-Client (Screenshot-Akzeptanz). Die 100-Namen-DB selbst liegt außerhalb dieses Repos — nicht erfinden; Lücke dokumentieren (F-1).
11. **T-12/T-13 Doku & Betrieb (P3):** README-Status aktualisieren; Nav-Daten-Attribution; Log-Rotation (BotTelemetry + Game-Logs, 7 Tage).
12. **T-14 Policy-Konvergenz (P1, keine Code-Änderung):** Entscheidung „ein Policy-Owner" (Empfehlung: Human-AI `bot_human.h`) + Mapping, welche Module aus Cecil P1 (Feuerrhythmus/Interception-Tests) und PR #39 (Taktik, Navdaten) selektiv in den Owner übernommen werden; Ergebnis in `docs/decisions/` (Erfüllt Issue #93 „keine doppelten Policy-Owner").

**Abgelehnte/abweisende Alternativen (mit Begründung):**
- `ser_iKickOnSyncBad` senken/deaktivieren: verwässert den einzigen Divergenzschutz — explizit abgelehnt (konsistent mit AGENTS.md).
- Ground-Lookahead reaktivieren: ungeklärter Sync-FAIL; Pit-Sicherheit statisch über NavGraph (T-03) lösen.
- CecilBotMod als Ganzes portieren: unvereinbar mit „Server/Entities unverändert" (Architektur, Abschnitt 6.1).
- Navmesh-Datei blind übernehmen **ohne** nativen Walk-Test: `.nav`-Name bindet nicht an Dateiinhalt (Abschnitt 8.1); Falschdaten erzeugen Stuck-Bots.
- 16/32-Bot-Skalierung jetzt planen: keine Kapazitätsabnahme (21.10.-Report: „16 Bots wären mindestens vier Botprozesse … keine Kapazitätsfreigabe").

---

## 13. Verifikationsanforderungen (Definition of Done je Befund)

- Jeder Sync-relevante Change: Native A/B (0/1) auf **derselben** sonst unveränderten DLL, 4 Bots, ≥ 600 s, Server-`SYNCBAD`-Log via `tools/analyze_sync_log.py` = 0, mindestens 1 `SYNCOK`/CRC-Ok, Telemetrie-Komplett.
- Jeder AI/Nav-Change: Offline-Suite (botcore `make test`) grün + ein nativer Verhaltenslauf mit Telemetrie-Auswertung (Feuer-/Zielwechsel-/Item-/Nav-Events) — **Scope-angabe** (Map, Botzahl, Dauer, DLL-Hash) im Report.
- 8-Bot-Gates: wie T-05 spezifiziert; **keine** Addierung mehrerer Läufe als ein Gate.
- Dokumentation: `TESTED`/`NOT_TESTED`/`BLOCKED` pro Behauptung; keine Runtime-Angabe aus statischer Analyse; keine privaten Rohlogs/Hashes-Fehlbelege.

## 14. Verbleibende Unbekannte

1. Exakte 1.07-`CTString::GetHash`-Implementierung (für den Nav-Dateinamen; unkritisch, aber für deterministische Namensfindung relevant). *Geklärt in der zweiten Durchsicht:* BNMV-v6 speichert die Kanten pro Punkt (Nachbarlisten) — ein Raycast-Kanten-Build ist nur Fallback.
2. Bytegleichheit von Cecils `RedStation.wld` mit dem Retail-1.07-Original (nur nativ prüfbar; Walk-Test in T-03).
3. SYNCBAD-Root-Cause (H1–H3 offen; kein Capture-Run mit Paardaten im Fehlfall existiert).
4. Ob die 26.10.-Vierbot-FAIL-Harness (`qualify_bot_sessions.py`-Alte) den Fehler deterministisch triggert (Reproduktionsrate unbekannt).
5. Langzeit-RAM-Stabilität (≥ 24 h) unter Wine (nur 1-h-Daten).
6. 333networks/öffentliche Browser-Sichtbarkeit der **aktuellen** Zielkonfiguration (letzte Abnahme bezog sich auf den später abgeschalteten Betrieb; 01.11.-Live-Diagnose: server-only, 0 Spieler).
7. Inhalte der 100-Namen-DB und des ssam.ai-Webauftritts (außerhalb dieses Repos; nicht auditiert).
8. Cecil-P1-`bot_route.h`-Interception: ob die einmaligen 5 SYNCBAD kausal damit zusammenhängen (kein Pair-Capture vorhanden).
9. **Inhalt des 52-Commits-unpublished-Backlogs** (Issue #92, Stand 01.11.): was in `agent/chat/20261101-m2m3-live-diagnostics` und verwandten lokalen Worktrees bereits implementiert ist (u. a. `inspect_live_fleet.py`), ist vor dem Push aus GitHub nicht vollständig überprüfbar — mögliche Duplikate mit T-01/T-11-Werkzeugen erst nach Push klären.

## 15. Empfohlene nächste Aktionen für Codex (Priorität)

1. **T-02** (RAM) als erste harte Vorbedingung klären — ohne sie läuft nichts Natives. Parallel **T-14** (Policy-Konvergenz-Entscheidung) offline erledigen — sie ist die Voraussetzung dafür, dass T-05/T-07/T-08 auf einer eindeutigen Basis laufen.
2. **T-01 + T-04 parallel**: Diagnostics-Loop (erste Divergenz) und Lock-Budget sind unabhängig voneinander umsetzbar; T-04 liefert zusätzlich den H1-Diskriminator.
3. **T-03** auf **PR #39-Basis** vorantreiben (Converter/Daten existieren bereits): Kantenbesatz prüfen (offline), Walk-Test-Plan fassen, danach nativer ~30-min-Walk-Test auf kurz verifiziertem Testserver-Slot; `redstation.nav.example`-Platzhalter durch echte Daten ersetzen.
4. Danach **T-05** als integratives Gate; **T-06** dazwischen einarbeiten (klein, reduziert Respawn-Risiko im Gate).
5. Die offenen Draft-PRs (**#39, #74, #80, #82, #91, #95**) als Basis statt als parallele Neuarbeit verwenden — das Handoff-Backlog (begleitend) ist explizit auf Nicht-Duplizierung mit diesen PRs geprüft. Vor jeder neuen Werkzeugarbeit zusätzlich das 52-Commits-unpublished-Backlog (Issue #92) nach Push abgleichen.

---

*Ende des Audit-Reports. Alle Befunde sind mit Datei-/Quellenangaben im Repository belegt; nicht belegbare Aussagen sind als HYPOTHESE oder „außerhalb dieses Repos" markiert. Keine Spielprozesse wurden gestartet, keine DLLs verändert, kein Produktivserver berührt.*
