# ssam.ai – Codex-Handoff: priorisiertes Implementierungs-Backlog (LM Arena Audit)

**Datum:** 2026-11-01 · **Quelle:** [2026-11-01-lmarena-independent-review.md](2026-11-01-lmarena-independent-review.md) (Befund-IDs verweisen dort auf Kapitel)
**Status:** Nur Dokumentation/Planung. Keine Quelle wurde geändert; keine Runtime angestoßen.
**Regel:** Aufgaben, die von offenen PRs bereits abgedeckt sind, werden hier **nicht** dupliziert, sondern referenziert: PR #39 (BNMV-v6-Converter + 9 konvertierte Cecil-Navmeshes + Taktik-AI), PR #74 (Pair-Sync-Producer, Supervisor-Werkzeuge), PR #91 (NavV2 + Bridge, offline), PR #95 (Respawn-Fix, Draft), PR #55 (Item-Utility, offline), PR #57 (Cecil P1), PR #58/#65 (Sync-Tools, offline), PR #82 (M2-Evidenz).

**Definition of Done (gilt für alle Tasks):**
- Offline: `cd poc/botcore && make test && make smoke && make bench` grün; neue Regeln erhalten eigene unit Tests.
- Native (falls Bestandteil): A/B 0/1 auf derselben sonst unveränderten DLL, ≥ 4 Bots, ≥ 600 s, `tools/analyze_sync_log.py` → 0 SYNCBAD, ≥ 1 CRC-OK, Telemetrie-Komplett, Scope-Angabe (Map/Botzahl/Dauer/DLL-Hash/Umgebung) im Report.
- Report-Kennzeichnung: `TESTED` / `NOT_TESTED` / `BLOCKED`; keine Addierung mehrerer Läufe als ein Gate.

**Abhängigkeitsgraph (Kurzform):**
`T-02` → (alle nativen Gates) ; `T-01` + `T-04` (parallel) → `T-05` ; `T-03` → `T-05` ; `T-06` → `T-05` ; `T-05` → `T-11` ; `T-07/T-08/T-09` → (optional in `T-05`-Kandidaten, sonst eigener A/B) ; `T-10/T-12/T-13` unabhängig ; `T-14` offline und unabhängig (aber vor `T-05`/`T-07`/`T-08` als Basis-Entscheidung erledigen).

**Zweite Durchsicht (01.11.2026):** T-03 wurde auf **PR #39-Basis** umgeschrieben (Converter + konvertierte RedStation-Daten existieren bereits; Rest = Validierung + Integration). Neue Aufgabe **T-14** (Policy-Konvergenz) ergänzt das Backlog.

**Dritter Stand (01.11.2026, 19:14 UTC — PR #96-Kommentar des Umsetzungsteams, self-reported, NICHT audit-verifiziert):** T-01–T-13 werden als umgesetzt/nachgewiesen gemeldet (405 Python-Tests PASS, BotCore test/smoke/san/bench PASS, Retail-Win32-Build PASS, private DLL `dd9ae785…` `qualified=false`, nicht installiert). Konsequenzen für dieses Backlog:
- **T-02 → definitiv BLOCKED_PHYSICAL_RAM** (Host: 7,57 GiB gesamt / ~5,8 GiB frei; „≥ 8 GiB Reserve" unerreichbar). Neue Priorität 1: **Kapazitäts-Entscheidung** (Host-Upgrade, Flotten-Split auf zweite Maschine oder Xvfb/Overhead-Reduktion) — erst danach T-05.
- **T-05:** Live-8-Bot-Red-Station-Point-in-Time-Run existiert (0 SYNCBAD in inspizierten Logs, 45-s-Bewegung/Feuer/Tod/Respawn dokumentiert) — **kein** 3600-s-Originalclient-/CRC-Gate; bleibt als Abnahme offen.
- **T-03:** Umsetzung meldet eigenen BNMV-v6-Parser + 193 Cecil-/236 gemessene Live-Knoten. **Nach Push prüfen:** (a) wurde PR #39-Converter wiederverwendet oder ein Duplikat geschrieben (Issue #93: keine redundanten Kontrollpfade)? (b) Merge-Kriterium Cecil↔Live-Messung dokumentieren? (c) Walk-/Kantenvalidierung (offen) wie hier spezifiziert.
- **T-14 (neue Aufgabe, nach Umsetzungslauf ergänzt):** noch offen; zudem klären, welche **Policy-Linie** der Live-8-Bot-Run nutzte (A/B-Baseline für T-05).
- **Verifizierungs-Basis:** Zweig `agent/chat/20261101-lmarena-integrated` + 5 lokale Commits (`3238592`, `7cf62b9`, `78d44ec`, `dffce98`, `f4a6beb`) liegen **nicht** im Remote (Push-Blocker auf Ubuntu) → alles darüber steht hier unter Vorbehalt „self-reported".

---

## T-01 · P0 · Isolation des ersten divergenten SYNCBAD-Ticks (M1-Root-Cause)

- **Ziel:** Ersten Fehlfall mit Paardaten (CRC beider Seiten + Actions am ersten abweichenden Tick) zu erfassen und die Hypothesen H1 (Lock-Hold), H2 (Timer-Drift), H3 (Restzugriff) zu diskriminieren — die vom 17.10.-Bericht angeordnete, bis heute offene Maßnahme.
- **Relevante Dateien:** `tools/native_sync_snapshot.py`, `tools/native_sync_handler_probe.py`, `tools/m1_recovery_gate.py` (PR #74, als Basis — nicht ersetzen), `poc/research/sync-hypothesis-validation/` (PR #65), `tools/analyze_sync_log.py`, `BotTelemetry.csv`-Schema (`poc/candidates/integrated-human-cpu-20261021/BotDriver.cpp`).
- **Vorgeschlagene Umsetzung:**
  1. Pair-Producer auf den **aktuellen** integrierten Kandidaten ausrollen (Manifest-Update, source-pinned wie in PR #74 — kein Kandidaten-Mix).
  2. Laufmatrix als wiederholbarer Job (je 150 s, 4 Bots, gleicher Map/Server/Konfiguration):
     - (a) aktuelle Harness, (b) alte Harness-Konfiguration vom 26.10.-Fehlfall (`qualify_bot_sessions.py`-Differenz als Parameter dokumentieren), (c) mit/ohne T-04-Budget. 10 Wiederholungen je Zelle; alle Runs archvivieren (Log+Telemetrie+Hashes).
  3. Bei jeder SYNCBAD-Folge: automatisierter Report = erster abweichender Tick, Server-CRC vs. Client-CRC, letzte N Actions pro Player (aus dem Pair-Capture), `lock_ms_max`/`tick_ms_max`-Fenster der letzten 60 s beider Prozesse.
  4. H1/H2-Diskriminator: `lock_ms_max`-p99 und `tick_ms_max`-Histogramm über alle Runs korrelieren mit SYNCBAD-Auftritten (einfaches Python-Script auf BotTelemetry.csv + Serverlog).
- **Abhängigkeiten:** T-02 (RAM für 4-Bot-Läufe auf dem Zielhost; alternativ separater isolierter Host), T-04 (nur für Zelle (c)).
- **Akzeptanzkriterien:** ≥ 1 SYNCBAD-Folge mit vollständigem Paar-Report **oder** 10/10 reproduzierbar clean mit dokumentiertem Fehlszenario-Parameter (dann: Fehlszenario als deterministischer Trigger identifiziert). Kein Fehlfall darf „ohne Daten" enden (fail-closed: fehlendes Log → `sync_scan_complete=false`, existiert bereits in PR #74 — beibehalten).
- **Empfohlene Tests:** Bestehende PR #74/65/58-Suiten (keine Duplikate); neu: Unit-Test des Report-Generators (Synthese-Log → erwartetes JSON).
- **Komplexität:** MEDIUM (Werkzeuge existieren; Arbeit = Ausrollung + Laufmatrix + Korrelation).

## T-02 · P0 · RAM-Vorcondition am Zielhost (Issue #79)

- **Ziel:** ≥ 8 GiB sichere Speicherreserve wiederherstellen, damit 8 private Bot-Clients + Server + Observer wieder admissible sind (PR #80: Stopp vor Client 7 bei 1.039,3 MiB frei vs. 1.068 MiB benötigt).
- **Relevante Dateien:** Issue #79, PR #80 (Diagnose), `docs/reports/2026-10-21-hetzner-capacity.md` (Kapazitätshochrechnung), `poc/scripts/fleet-config.sample.json`, `tools/operations/fleet_health.py` (PR #74, RAM-Guard).
- **Vorgeschlagene Umsetzung:** (1) Inventur laufender Prozesse/dienste auf dem Host (nur eigenes Eigentum anfassen — fremde Ressourcen bleiben unangetastet, AGENTS.md); (2) Optionen: größerer Host/verlagerte Flotte, Wine-Xvfb-Overhead reduzieren (eigener minimaler Display-Server, NullRender bereits aktiv), Bot-Flotte auf zweite Maschine (dann: WAN-Latenz in die Sync-Hypothesen einrechnen); (3) Entscheidung + Kapazitätsnachweis (Preflight: `min(RAM_frei) ≥ 8 GiB` im Health-Gate).
- **Abhängigkeiten:** keine (Vorbedingung für alle nativen Gates).
- **Akzeptanzkriterien:** Preflight-Messung mit ≥ 8 GiB freier Reserve **nach** Start der 8 Bot-Prozesse + Server; dokumentiert in einem neuen `docs/reports/2026-11-xx-ram-capacity.md` (bereinigt, ohne private Logs).
- **Empfohlene Tests:** `tools/operations/fleet_health.py`-RAM-Gate gegen die neue Konfiguration; 8-Prozess-Start ohne Guard-Abbruch.
- **Komplexität:** MEDIUM (Operations, kein Code — falls Host-Migration nötig: MEDIUM–HIGH).

## T-03 · P1 · Red-Station-NavGraph: Validierung und Integration der bereits konvertierten PR #39-Daten (M3-Kern)

- **Ziel:** Die 193 echten Red-Station-Waypoints in den **aktiven** NavGraph überführen und nativ verifizieren. **Basis = PR #39** (`agent/bot-ai-cecil-20261020` @ `1433bc9`): dort existieren bereits (a) ein strikter, getesteter BNMV-v6-Converter (`poc/experiments/tactical-ai/convert_cecil_navmesh.py`, 5/5 Tests über alle 9 Cecil-Navmeshes; im Audit zusätzlich bytegenau gegen Cecils `PathPoint.cpp`-Serialisierung verifiziert: `BPPH`+idx+FLOAT3D+range+flags+important+next+[lockEntity+CPlacement3D]+**Kanzahl+Nachbarn**+Polygon-UBYTE) und (b) die konvertierte RedStation-Graphdatei `poc/experiments/tactical-ai/maps/RedStation_5AF1A276.waypoints` (**193 node / 879 gerichtete arc / 1 locked**). **Neuparser ist ausdrücklich NICHT zu schreiben.** Rest des M3-Kerns: Kantenbesatz prüfen, nativer Walk-Test, Anbindung an aktives Pathfinding, Platzhalter ersetzen. Issue #93 ordnet die Wiederverwendung an („keine doppelten Policy-Owner oder redundanten Kontrollpfade").
- **Relevante Dateien:** PR #39: `poc/experiments/tactical-ai/{convert_cecil_navmesh.py,maps/RedStation_5AF1A276.waypoints,test_bot_nav_graph.cpp}`, `docs/plans/2026-10-20-cecilbot-tactical-ai.md`; neu: `poc/botcore/redstation.nav` (aus PR #39-Daten, ersetzt `redstation.nav.example`); Konsumenten: `poc/botcore/botcore_ai.h` (`WaypointGraph`, kMaxNodes=256, kMaxEdgesPerNode=8), `poc/botcore/bot_navigation_v2.h` (PR #91, A* + `kFetchItem`/`kRetreat`/`kAvoidPit` — als Konsument nutzen), `THIRD-PARTY-NOTICES.md` (Attribution).
- **Vorgeschlagene Umsetzung:**
  1. **Übernahme PR #39** (Entscheidung + Dokumentation): die vier Dateien/Dateibäume (Converter, RedStation-`.waypoints`, Nav-Graph-Test, ggf. `bot_navigation.h`) in den Arbeitszweig einbringen (cherry-pick oder saubere Re-Commit der Dateisubmenge; PR #39 bleibt als Draft bestehen, Taktik-AI-Anteil wird unter T-14 entschieden — hier rein die **Datenebene** übernehmen).
  2. **Offline-Kantenanalyse:** Maximalgrad der 879 gerichteten Kanten über 193 Knoten ermitteln; bei > 8 ausgehenden Kanten: längste Kanten prunen (Abstandsschwelle, deterministisch, getestet) oder `kMaxEdgesPerNode` erhöhen — eine Entscheidung, dokumentiert. `redstation.nav` aus den PR #39-Daten erzeugen (Syntax `node <x> <y> <z>` + `arc <a> <b>`), Lock-Punkt als `# locked`/Türkandidat markieren.
  3. **Nativer Walk-Test (zwingend, kein Formalismus):** isolierter Retail-Testserver (Preflight-Regeln wie T-01, **kein** Produktivserver), 1 Bot: jeder der 193 Knoten aufgesucht (≥ 2 s Stand, kein Stuck/Reset), pro Kante passierbar/Stuck-Events gezählt, Y-Verlauf gegen Abgründe prüfen (> 2 m Sprung = Fehlkante → prunen), Lock-Punkt als Tür verifizieren. Raycast-Kanten-Build (`CCastRay` + `BPOF_PASSABLE`, Cecils `CastPathPointRay`-Äquivalent) nur als **Fallback für fehlende Kanten** — v6 trägt bereits 879 Kanten.
  4. **Integration in aktives Pathfinding** (derzeit in PR #39 explizit noch offen): `bot_navigation_v2.h` (PR #91) lädt den echten Graphen statt Platzhalter; `kAvoidPit`/`kRetreat`/`kFetchItem`-Modi laufen auf echten Daten; BotDriver-Policy-Bridge (PR #91) als Anbindungspunkt, ohne Human-AI-Logik zu ändern (Policy-Owner-Regel T-14 beachten).
  5. **Daten-Kommit** mit Quellenangabe (CecilBotMod, GPL-2.0, Datei-Hash der `.nav`) in `THIRD-PARTY-NOTICES.md` (→ T-12); `redstation.nav.example`-Platzhalter aus PR #91 ersetzen (oder als Fallback mit Hinweis markieren).
- **Wichtige Einschränkung (im Audit belegt):** Der Dateinamen-Hash (`5AF1A276`) ist ein **Name-String-Hash**, kein Dateiinhalt-Hash → die Punkte gelten nur für bytegleiche `.wld`. Der Walk-Test ist deshalb zwingend.
- **Abhängigkeiten:** PR #39 (Datenbasis), PR #91 (NavV2/Bridge als Konsument); isolierte Retail-Testumgebung + kurzes Runtime-Leasing (1 Bot genügt, keine T-02-Größe nötig).
- **Akzeptanzkriterien:** `redstation.nav` im Repo mit 193 Knoten/879 Kanten (oder begründet prunten), Walk-Test-Report `TESTED` (1 Bot, RedStation, ≥ 600 s, Stuck-Events ≤ 2, 0 SYNCBAD, Abdeckungs-Protokoll je Knoten), Erreichbarkeitstest grün (jeder Knoten von jedem Knoten), 8-Bot-Red-Station-Nutznachweis anschließend über T-05.
- **Empfohlene Tests:** PR #39-Tests beibehalten (Converter 5/5, `test_bot_nav_graph.cpp`); neu: Loader-Unit-Test (echte Datei → erwarteter Graph inkl. Lock-Markierung), Erreichbarkeitstest, nativer Walk-Test wie oben.
- **Komplexität:** MEDIUM (Übernahme + Kantenanalyse LOW; nativer Walk MEDIUM; Integration MEDIUM; **kein** neuer Parser, **kein** neuer AI-Code).

## T-04 · P1 · Globales Ray-/World-Lock-Budget pro Tick (M1-Schutz + H1-Diskriminator)

- **Ziel:** Die `ga_csNetwork`-Hold-Zeit im Bot-Timer begrenzen: heute sind bis zu 16 (Legacy) bzw. 4–8 (Human-AI) LOS-Rays **pro Player** möglich → bis zu ~32–64 Rays/Tick/Client; der eigene Client-Simulationstakt wird dadurch verlangsamt (Sync-Druck, H1 im Audit).
- **Relevante Dateien:** `poc/candidates/integrated-human-cpu-20261021/BotDriver.cpp` (Loop + `CTSINGLELock slBotWorld`; Human-AI-Block `PlanLosQueries`; Legacy-Scan `bot_iMaxLosRays`), `poc/botcore/bot_human.h` (`SortKey`/Budget), `poc/botcore/test_botdriver_block.cpp` (Smoke), `BotTelemetry.csv` (`lock_ms_max` existiert).
- **Vorgeschlagene Umsetzung:**
  1. Neue Konsole-Variable `bot_iGlobalLosPerTick` (Default 16; 0 = unlimited = heute).
  2. Round-Robin-Verteilung über die 4 Player-Slots, **Vorrang** für Slots mit bestehendem Track (Human-AI: `perception_.Track()!=NULL`; Legacy: `bs_iCombatTarget`); Rest an nächste Slots; nicht verteilte Slots behalten ihren Track-Status, aber ohne frischen Ray (keine Wandvision — die `planned_`-Gate-Logik in `bot_human.h` muss unverändert funktionieren).
  3. Telemetrie: Zähler `rays_global` pro Tick + bestehende `lock_ms_max`; Log-Zeile (opt-in, `bot_iLogEvery`) bei p99(lock_ms) > 5 ms.
  4. Enginefreie Regel in `bot_human.h`/neue Mini-Schicht mit Unit-Test (Budget-Verteilung deterministisch, Track-Vorrang).
- **Abhängigkeiten:** keine für offline Teil; Sync-A/B ist eigenständiger Lauf (4 Bots, 600 s, 0/1, T-01-Laufmatrix optional mitnutzen).
- **Akzeptanzkriterien:** Unit-Tests grün; nativer A/B: `lock_ms_max`-p99 sinkt messbar (Ziel ≥ 30 %), 0 SYNCBAD in beiden Zellen, AI-Verhaltensmetriken (Zielwechsel/Sek, Feueranteil) ändern sich ≤ 10 % (sonst Parameter nachkalibrieren).
- **Empfohlene Tests:** `make test` (neue Budget-Tests), `make smoke`, 4-Bot-Sync-A/B, `make bench` (Ray-Zahl im Benchmark-Output prüfen).
- **Komplexität:** LOW–MEDIUM.

## T-05 · P1 · 8-Bot-Red-Station-Abnahme (integratives Gate M1+M2+M3)

- **Ziel:** Der Hauptprojektziel-Zustand: 8 Bots (2×4), Fragmatch, **RedStation**, 3600 s, Vanilla-Observer, ohne Operator-Eingriff.
- **Relevante Dateien:** Gate-Spezifikation neu `poc/REDSTATION-GATE.md`; `tools/analyze_sync_log.py`, `tools/gamespy_query.py`, `poc/scripts/` (Fleet-Start/Stop), `docs/reports/2026-10-21-human-cpu-final.md` (als Format-Vorlage), `poc/PHASE-3-ABNAHME.md` (Methodik-Vorlage).
- **Vorgeschlagene Umsetzung:**
  1. Kandidaten-Bindung: aktueller integrierter Kandidat + T-03-Graph + T-04-Budget + T-06-Fix (alles source-pinned, Manifest wie in PR #74/80).
  2. Gates (alle aus Telemetrie + Query + Serverlog, nicht aus Namen/Laufzeit):
     - alle 8 Bots in **jedem** 12×5-Min-Fenster aktiv (Bewegung ≥ Schwelle **und** ≥ 1 Combat-Fire-Action),
     - 0 SYNCBAD, ≥ 1 CRC-OK, 0 fehlerhafte Disconnects,
     - Nav-Metriken (T-03): ≤ 2 Stuck-Events/Bot, ≥ 4 verschiedene Map-Regionen je Bot (Knoten-Cluster-Zählung),
     - Telemetrie-Komplett (keine Lücken > 2 s), regulärer Shutdown, 415-Datei-Rollback-Prüfung danach.
  3. Vanilla-Observer: Beitritt aus der Query-Liste, ≥ 300 s, normales Spiel, regulärer Abbruch per `CloseMainWindow` (17.10.-Regel).
  4. Bericht `docs/reports/2026-11-xx-redstation-eight-bot-gate.md` (bereinigt; Scope klar: Wine/Host-Klasse, kein Windows-Spieler-PC-Ersatz).
- **Abhängigkeiten:** T-02, T-03, T-04, T-06 (alle abgeschlossen oder explizit begründet ausgenommen).
- **Akzeptanzkriterien:** alle Gates bestanden in **einem** Lauf; kein Teil-PASS aus mehreren Läufe addiert.
- **Empfohlene Tests:** das Gate selbst + Wiederholbarkeit: 2. Lauf zu einem späteren Zeitpunkt (Reproduzierbarkeit) als optionaler Best-Case.
- **Komplexität:** HIGH (Koordination + Runtime; Code selbst gering).

## T-06 · P1 · PR #95 finalisieren (Respawn-Fire-Edge bei fehlender Entity)

- **Ziel:** Den dokumentierten Defekt schließen: `localInput==NULL` unterdrückt **alle** Fire-Actions (inkl. Respawn-Puls) für noch existierende `CPlayerSource` (Quellbeleg: `BotDriver.cpp`, alle Kandidaten-Varianten). PR #95 (Draft) enthält Guarded-Fire-Fix + enginefreie Helfer + Test.
- **Relevante Dateien:** PR #95-Branch (`agent/chat/20261031-respawn-missing-entity`), `poc/candidates/integrated-human-cpu-20261021/BotDriver.cpp` (Ziel), `poc/botcore/` (Helfer-Tests).
- **Vorgeschlagene Umsetzung:** PR #95 gegen den aktuellen Kandidaten abgleichen (der PR vermerkt: jüngerer lokaler Stand `ssam-m2m3-native-20261031` hat weitere V2/Respawn-Änderungen — **erst abgleichen, dann integrieren**, nichts überschreiben); MSVC-x86-Build; 1-Bot native Smoke: Bot gezielt töten, Spectator-/Entity-Transition beobachten, Respawn innerhalb der Engine-Kadenz, Kill-Credit korrekt.
- **Abhängigkeiten:** MSVC/Build-Umgebung (RDC-/Wine-Buildpfad wie Build04); vor T-05 in den Kandidaten.
- **Akzeptanzkriterien:** Helfer-Tests PASS (C++11), Build0x-DLL mit Hash im Report, native Smoke `TESTED` (Kill→Death→Respawn-Sequenz im Log), kein SYNCBAD im Smoke.
- **Empfohlene Tests:** PR #95-eigene Helfer-Suite + `make test` + 1-Bot-Retail-Smoke (3× wiederholt).
- **Komplexität:** LOW (Code fertig; nur Abgleich + Build + Smoke).

## T-07 · P2 · Strafen aktivieren und nativ verifizieren

- **Ziel:** `bot_fStrafeScale` ≠ 0 — die Persona-`strafe_bias`-Parameter (0,40–0,95) wirken im Produktivbuild heute nicht (21.10.-Report: „StrafeScale bleibt 0"); sichtbare Bewegungsvielfalt steigt (Vergleich Cecil: ständiges Strafen, Richtungswechsel 2–4 s).
- **Relevante Dateien:** `poc/candidates/integrated-human-cpu-20261021/BotDriver.cpp` (`pa_vTranslation(1) = Clamp(humanStrafe*bot_fStrafeScale,...)` — Pfad existiert, nur deaktiviert), `poc/botcore/bot_human.h` (`MoveIntent`, `strafe_sign_`-Flip-Logik), `poc/scripts/Phase1HumanAI.ini`.
- **Vorgeschlagene Umsetzung:** A/B-Lauf (4 Bots, 600 s, gleiche DLL sonst): `bot_fStrafeScale=0` vs. `0,4` (Startwert; konservativ). Metriken: SYNCBAD (muss 0 bleiben), Lateral-Action-Anteil, Stuck-Events, Kill-/Tode-Verhältnis. Bei Problemen: Scale stufenweise (0,2/0,3) oder nur für Personas mit `strafe_bias ≥ 0,6` (Profile-Extension, optional).
- **Abhängigkeiten:** T-04 (gleiche Laufmatrix mitnutzen); kein T-05-Abhängiger.
- **Akzeptanzkriterien:** A/B-Report: 0 SYNCBAD in beiden Zellen; Lateral-Anteil > 5 % der Actions in der aktivierten Zelle; keine Stuck-Steigerung > 20 %.
- **Empfohlene Tests:** `make test` unverändert (Policy-Logik bleibt), nativer A/B, Telemetrie-Auswertung.
- **Komplexität:** LOW.

## T-08 · P2 · Item-Suche integrieren (Red-Station-Matchrealismus)

- **Ziel:** Bots sammeln Health/Armor/Ammo/Weapon-Pickups auf — heute passiert das nicht (Cecil-Bots tun es standardmäßig; ssam.ai: offline vorhanden, nicht integriert).
- **Relevante Dateien:** PR #55 `poc/research/item-utility/` (`item_planner.h`, `item_scoring.h`, Cecil-Analyse-Doku), PR #91 `bot_navigation_v2.h` (`kFetchItem`-Modus), T-03-Graph (Item-Positionen als Knoten-Annotation), `BotDriver.cpp` (Anbindungspunkt: `NavWorld`/`NavCommand`-Feed).
- **Vorgeschlagene Umsetzung:** (1) Item-Utility-Schicht 1:1 aus PR #55 in `poc/botcore` übernehmen (enginefrei, bereits getestet) oder als Kopie mit Lizenzhinweis; (2) Item-Positionen für Red Station aus dem T-03-Walk-Test ermitteln (Knoten-Kommentar `# health x y z`); (3) Anbindung: Bot ohne Ziel + Item im Umkreis 16 m (Waffe) bzw. Health<50 + Health-Item < 32 m → `kFetchItem`; (4) Hysteresis: Item-Ziel wird nicht pro Tick neu gewählt (Cooldown 5 s, wie Cecil `fItemSearchCD`); (5) A/B-Lauf (4 Bots, 600 s): Item-Event-Zählung + Sync.
- **Abhängigkeiten:** T-03 (Positionen), PR #55-Review (offline-Tests müssen im Kandidaten-Zweig grün laufen).
- **Akzeptanzkriterien:** Item-Events > 0/Bot im A/B-Lauf; 0 SYNCBAD; kein Stuck-Anstieg (Item-Gegehe nicht in Wände); `make test` grün inkl. neuer Adapter-Tests.
- **Empfohlene Tests:** PR #55-Suite, `test_bot_navigation_v2.cpp` (kFetchItem-Szenarien), nativer A/B.
- **Komplexität:** MEDIUM.

## T-09 · P2 · Sniper-Zielfernrohr (Scope) für Langstrecke

- **Ziel:** Cecils bewährtes Verhalten portieren: bei Sniper-Waffe (Index 13) + sichtbarerm Ziel → `PLACT_SNIPER_USE | PLACT_SNIPER_ZOOMIN`; Sichtverlust → Zoom-out (`PLACT_SNIPER_USE`). Heutiger Stand: keine Scope-Actions (Suchlauf im Audit: keine Treffer).
- **Relevante Dateien:** `poc/candidates/integrated-human-cpu-20261021/BotDriver.cpp` (Fire-/Button-Sektion, `pa_ulButtons`), Cecil-Referenz `BotWeapons.cpp::UseWeaponScope` (Vorbild), `poc/botcore/bot_loadout.h` (WeaponAt(13)), `poc/botcore/test_botdriver_block.cpp` (Smoke-Erweiterung).
- **Vorgeschlagene Umsetzung:** Enginefreie Regel `ScopePolicy` in `botcore` (Zustand: none/zooming/zoomed; Übergänge an `target_visible` + `current_weapon==13` gekoppelt; Cooldown für Button-Edge wie `CombatWeaponInput`); Anbindung: Buttons OR-en in `pa_ulButtons` (nur Human-AI-Pfad). A/B (4 Bots, 600 s): Scope-Telemetrie (Zoom-in/Out-Events), SYNCBAD, Sniper-Trefferquote (Score-Proxy).
- **Abhängigkeiten:** keine hart; T-05-Kandidat optional.
- **Akzeptanzkriterien:** Unit-Tests (Edge-Semantik, kein Button-Strom pro Tick), A/B: 0 SYNCBAD, Zoom-Events nur bei Sniper+Sicht.
- **Empfohlene Tests:** `make test`/`smoke`, nativer A/B.
- **Komplexität:** LOW.

## T-10 · P2 · Spielernamen: Roster-Mapping, Präfix-Einheit, Farbcod-Abnahme

- **Ziel:** (a) Versionierte, nachvollziehbare Zuordnung Roster-Slot → Charakter-Name im Repo (heute: implizit über die private BotClient-Installation); (b) Präfix-Konvention vereinheitlichen — Roster-Labels `BOT-*` vs. Fleet-Klassifikation `botNamePrefix:"TSE_Bot"` (`fleet-config.sample.json`) — sonst klassifiziert der Populations-Supervisor inkonsistent; (c) **einmalige** visuelle Abnahme: Do Serious-Sam-Farbcodes (`^b`, `^i`, `^f`, `^cRRGGBB`) im Original-Client (HUD/Killfeed/Scoreboard) korrekt rendern? (NOT_TESTED, keine Veröffentlichung mit Gegenbeweis gefunden).
- **Relevante Dateien:** neu `poc/scripts/roster-names.json` (oder in `bot_profile.h` als dokumentiertes Default), `poc/scripts/fleet-config.sample.json`, `poc/scripts/PopulationCore.ps1` (`Get-PlayerClassification`), `poc/botcore/bot_profile.h` (`DefaultRoster`), Cecil-Referenz für Code-Syntax (`BotMovement.cpp` `^caf3f3f…`).
- **Vorgeschlagene Umsetzung:** (a) JSON mit 8 Roster-Namen + 100-Namen-Pool-Referenz **falls** der Pool in einem anderen ssam.ai-Repo liegt: nur Verweis, **nicht** kopieren/erfinden; (b) Ein Präfix für Beides wählen (Empfehlung: Names in Query unverändert lesbar, Präfix-Bot-Erkennung über Sidecar statt Namenspräfix — die PLC4-Sidecars existieren bereits und sind fälschungssicherer; Präfix nur Fallback); (c) ein 10-minütiger Original-Client-Lauf mit einem farbigen Namen → Screenshot-Akzeptanz im Report.
- **Abhängigkeiten:** (c) braucht kurzen Testserver-Slot; (a/b) offline.
- **Akzeptanzkriterien:** `roster-names.json` im Repo + Konsistenz-Test (Name ↔ Sidecar ↔ Query-Name); Präfix-Entscheidung in `docs/decisions/` dokumentiert; Screenshot-Abnahme `TESTED` oder explizit `BLOCKED` mit Grund.
- **Empfohlene Tests:** `Test-FleetIdentitySidecars.Tests.ps1` (erweitern), JSON-Schema-Test, visueller Lauf.
- **Komplexität:** LOW.

## T-11 · P2 · Supervisor: Kandidaten-Bindung + Recovery-Nachweis + Aktivierung

- **Ziel:** Aus den PR #74-Werkzeugen (`fleet_supervisor.py`, `fleet_health.py`) einen **kandidatengebundenen** Supervisor machen und nativ qualifizieren — heute: pinned auf historisches `7fc94a39…`-Manifest, „no native reliability admission", nicht aktiviert (Ledger 26.10.).
- **Relevante Dateien:** PR #74 `tools/operations/*`, `poc/scripts/Start-BotFleet.ps1`/`Stop-BotFleet.ps1`, `PopulationCore.ps1`, `docs/reports/2026-10-21-hetzner-operations.md` (Betriebsregeln).
- **Vorgeschlagene Umsetzung:** (1) Manifest auf T-05-Kandidaten umbinden (Hash-pinned); (2) Health-Loop: GameSpy-Query (25601) + Prozessbelegung + RAM-Guard; (3) Recovery-Tests (isoliert, eigene Instanzen): Bot-Prozess killen → Supervisor startet Ersatz → Rejoin → 8 Bots wieder in ≤ 60 s; Server-Neustart → alle Rejoin; (4) Restart-Limits (≤ N/Std, sonst Alarm + Stop, kein Join-Burst: bestehende Stagger beibehalten); (5) erst nach bestandenen Tests: als Dienst auf dem Zielhost (nur mit expliziter Freigabe; Produktivprozesse ohne Freigabe nicht berühren).
- **Abhängigkeiten:** T-02, T-05 (Kandidat + Gates).
- **Akzeptanzkriterien:** 3/3 Recovery-Szenarien bestanden (`TESTED`), keine Slot-Flapping (> 2 Disconnects/Stunde außerhalb der Tests), Log-Audit trail pro Aktion.
- **Empfohlene Tests:** PR #74-Suite, neue Recovery-Integrationstests (isolierte Instanzen), 24-h-Betrieb (optional, `NOT_TESTED`-markiert bis dann).
- **Komplexität:** MEDIUM.

## T-12 · P3 · Doku-Synchronisation (README-Produktivstatus, Daten-Attribution)

- **Ziel:** (a) README: Abschnitt „Aktuelle Integration – 21.10.2026" klar als **historischer Snapshot** markieren und aktuellen Betriebsstatus ergänzen (Server seit 26.10. auf Nutzeranweisung offline; nächste Gate-Sequenz = T-05) — verhindert Fehleinschätzungen durch nachfolgende Agenten (Befund D-1). (b) Bei T-03: `THIRD-PARTY-NOTICES.md` um die Cecil-Navmesh-Quelle ergänzen (Datei-Hash, GPL-2.0, „Daten, keine Code-Übernahme"). (c) Datumsinkonsistenz im P0-Kandidaten-Abschnitt prüfen („ursprünglich 22.10.2026 bezeichnet" vs. Verzeichnis `p0-nullrender-20261022`) — harmonisieren oder erklären.
- **Relevante Dateien:** `README.md`, `THIRD-PARTY-NOTICES.md`, `poc/candidates/p0-nullrender-20261022/README.md`.
- **Vorgeschlagene Umsetzung:** Redline-Änderungen nur, keine Umstrukturierung; jede Statusänderung mit Datum + Beleg (Ledger-PR #74).
- **Abhängigkeiten:** (b) auf T-03.
- **Akzeptanzkriterien:** Doku-Review: kein Statement „produktiv aktiv" ohne Datums-Scope; Attribution vollständig.
- **Empfohlene Tests:** keine automatischen; Peer-Review.
- **Komplexität:** LOW.

## T-13 · P3 · Log-Rotation & Telemetrie-Limits für 24/7

- **Ziel:** `BotTelemetry.csv` (1 Zeile/s/Prozess) und Dedicated-Server-Logs wachsen unbegrenzt; für Dauerbetrieb braucht es Rotation/Limits (Befund R-4).
- **Relevante Dateien:** `poc/candidates/integrated-human-cpu-20261021/BotDriver.cpp` (`BotTelemetry_Start`), `poc/scripts/` (Fleet-Stop), `docs/reports/2026-10-12-shadow-development-status.md` (Punkt 6: „2-/6-/24-Stunden-Soaks, Logrotation … offen").
- **Vorgeschlagene Umsetzung:** Option A (empfohlen, keine Engine-Änderung): Supervisor-/Fleet-Level-Rotation (Datei-Size-Check, Rename `BotTelemetry-YYYYMMDD-HH.csv`, Max 7 Tage, danach Lösch-Kandidaten mit Hash-Liste); Option B (Client-seitig, nur falls nötig): Neustart-Zwang bei > 250 MB. Beides im Supervisor (T-11) verankern.
- **Abhängigkeiten:** T-11.
- **Akzeptanzkriterien:** 7-Tage-Simulation (beschleunigt) + 1 realer 24-h-Lauf: Disk-Nutzung < 500 MB/Tag gesamt, keine verwaisten Files, Telemetrie-Komplett bleibt (Lücken-Check im Auditor).
- **Empfohlene Tests:** Unit-Test der Rotationslogik, 24-h-Lauf (optional als `NOT_TESTED` bis erledigt).
- **Komplexität:** LOW.

## T-14 · P1 · Policy-Konvergenz: ein Policy-Owner für alle Kampflogik (neuer Befund A-10, zweite Durchsicht)

- **Ziel:** Die drei parallelen Kampf-Policy-Linien — (1) **Human-AI** `bot_human.h` (im produktiven Kandidaten Build04 integriert, 555 Checks), (2) **Cecil P1** (PR #57: `bot_route.h`-Interception, Fire-Cadence, Respawn; ein negativer Datenpunkt: 5 SYNCBAD in einem 4-Bot-Lauf, nicht reproduziert), (3) **Cecil-Taktik-AI** (PR #39: `bot_bTacticalAI`, opt-in, experimenteller Build `C65CB29B…`) — plus PR #66-Research in **einen** Policy-Owner konvergieren, damit keine doppelten Policy-Owner/redundanten Kontrollpfade entstehen (Issue #93, explizite Nutzeranforderung).
- **Relevante Dateien:** `poc/botcore/bot_human.h`, PR #74-Branch `poc/candidates/integrated-human-cpu-20261021/BotDriver.cpp` (Human-AI-Policy-Block, `7fc94a…`-Basis), PR #57 `poc/botcore/bot_route.h` + `poc/release/gamemp/BotDriver.cpp`-Diff, PR #39 `poc/experiments/tactical-ai/BotDriver-tactics.patch` + `bot_navigation.h`, PR #66 `poc/research/combat2/`; neu: `docs/decisions/2026-11-xx-policy-owner.md`.
- **Vorgeschlagene Umsetzung:**
  1. **Inventur:** Funktion-Matrix je Linie (Zielen, Feuern, Items, Navigation, Respawn, Kommunikation) — vorhanden/fehlt/inkompatibel (Anschluss an Issue #93-Matrix).
  2. **Owner-Entscheidung:** Empfehlung: **Human-AI als einziger Policy-Owner** (Begründung: produktiv integriert, am besten getestet, korreliertes Zielmodell). Cecil P1 und PR #39-Taktik werden **Selektionsquellen**: pro Modul ein Review (übernehmen/abstimmen/verwerfen) — z. B. Fire-Cadence aus Cecil P1 (A-8), ggf. Taktikmodule aus PR #39; PR #39-**Navdaten** fließen unabhängig davon über T-03 ein (Daten ≠ Policy).
  3. **Verzichtsliste:** Parallel produktive Policy-Branches werden eingestellt; `bot_bTacticalAI`-Pfad und `bot_route.h`-Pfad bleiben entweder deaktiviert oder werden in den Owner merged — keine beiden im selben Build aktiv.
  4. **Dokumentation:** Entscheidung + Matrix + Mapping (welches Modul aus welcher Quelle) in `docs/decisions/`; A/B-Baseline-Definition für T-05 (Kontrollgruppe = Owner ohne neue Module).
- **Abhängigkeiten:** keine (offline, rein Entscheidung); Ergebnis ist Vorbedingung für T-05/T-07/T-08, damit deren Baselines eindeutig sind.
- **Akzeptanzkriterien:** Entscheidungsdoku im Repo (TESTED = im Peer-Review verabschiedet), keine zwei aktiven Policy-Pfade im M3-Kandidaten-Build, A/B-Baseline in T-05-Plan eindeutig benannt.
- **Empfohlene Tests:** keine Code-Tests (Entscheidungsdoku); ggf. Smoke-Test, dass `bot_bTacticalAI=FALSE`-Default und Human-AI-Block den einzigen aktiven Pfad bilden.
- **Komplexität:** LOW (Dokumentation/Entscheidung; die eigentliche Merging-Arbeit erfolgt bei den jeweiligen Modulen in T-07/T-08 oder T-03).

---

## Reihenfolge-Vorschlag (1–2 Wochen, 1 Hauptagent + optional 1 Subagent für T-03 offline)

| Woche | Hauptagent | Subagent (optional) |
|---|---|---|
| 1 | T-02 (RAM) → T-01-Laufmatrix starten | T-14 (Policy-Entscheidungsdoku) + T-03 Übernahme PR #39 + Kantenanalyse (offline) |
| 2 | T-04 → T-06 (Build+Smoke) → T-03 nativer Walk (kurzer Slot) | T-07/T-09-Offline-Vorbereitung (A/B-Profile nach T-14-Baseline, Tests) |
| 3 | **T-05 8-Bot-Red-Station-Gate** | Gate-Monitoring (nur Leserecht) |
| 4 | T-11 (Supervisor), T-08, T-10, T-12/T-13 | – |

**Koordinationsregeln (aus AGENTS.md, wiederholt):** Isolierte Worktree/Branch pro Writer; keine Überschneidung auf Dateien; laufende Prozesse/Worktrees vor Delegation inventarisieren; fremde Runtime unangetastet; alle native Tests nur nach Preflight und dokumentierter Exklusivität; keine Produktiv-Änderungen ohne Freigabe; Ergebnisse mit Diffs/Build-Outputs/Reproduzierbarkeit an den Hauptagenten; fehlende Retail-Tests als `NOT_TESTED` ausweisen.

**Erfolgskriterium des Backlogs:** Nach T-05 liegt ein einzelner, hashbelegter 3600-s-Lauf vor, in dem 8 Bots auf Red Station aktiv kämpfen, navigieren, (optional) Items sammeln, 0 SYNCBAD auftreten und ein Vanilla-Client normal spielt — und die SYNCBAD-Hypothese (T-01) ist dadurch entweder bestätigt, widerlegt oder als nächster eng gefasster Fall definiert.
