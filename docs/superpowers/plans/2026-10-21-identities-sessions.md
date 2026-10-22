# Alpha-Gaming Identities and Sessions Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Persistente glaubwürdige Botidentitäten und unabhängig geplante, sicher abgegrenzte Sitzungen für Retail 1.07.
**Architecture:** Vorhandene Human-KI nutzen; SQLite-basierter reiner Planer erzeugt idempotente Lebenszyklusabsichten. Runtime erst nach kollisionsfreier nativer Qualifikation anbinden.
**Tech Stack:** Python-Standardbibliothek/sqlite3, vorhandenes C++17/MSVC/Wine/Retail.
**Spec:** docs/superpowers/specs/2026-10-21-identities-sessions-design.md

## Global Constraints
- Hetzner ausschließlich; Worktree /srv/tse-identities-20261021, Branch agent/identities/20261021-sessions.
- Basis fdfc46e, vorhandene und öffentliche Build04-Flotte unverändert.
- PR #46 besitzt aktive Zuverlässigkeitsarbeit; fremde Runtime/Dateien niemals ändern.
- Keine Farben-/Längen-/Gameplay-/Stundenabnahme ohne neuen echten Beleg.
- Keine zusätzlichen Dienste/Dependencies, keine LLMs im Spielbetrieb.
- Benutzerauftrag ersetzt routinemäßige Skill-Freigabeschritte; Umsetzung inline.

## Review Focus
- Zwei Controller dürfen dieselbe Identität nicht doppelt starten.
- Fehler/unklare Antworten dürfen keine Humans verdrängen.
- Persistenz darf laufende JOINING/LEAVING-Absichten nicht wiederholen.
- Sichtbare Namen mit Farben und Groß-/Kleinschreibung kollidieren.
- Crash darf weder eine geplante Pause abkürzen noch Admin-Off aufheben.

### Task 1: Bestandsprüfung und Integration abgrenzen
**Files:** Entwurf, dieser Plan, docs/reports/2026-10-21-identities-sessions-handoff.md
**Interfaces:** main/PR45, Draft PR46, /proc, GameSpy/Health.
- [x] GitHub, Worktrees, Prozesse, Ports, aktuelle Health und fremde native Qualifikation lesen.
- [x] Eigenen Worktree erstellen, vorhandene Profile/Schnittstellen untersuchen.
- [x] Konflikt Supervisor vs. Sitzungsende explizit dokumentieren.
- [x] Ausgangstests im eigenen Worktree protokollieren.

### Task 2: Identitäten und Sitzungsplaner (TDD)
**Files:** tools/bot_sessions.py, tools/test_bot_sessions.py, poc/scripts/BotSessions.example.json
**Interfaces:** Planner(db, config), plan(server, snapshot, now), record(id, event, now); keine Runtime-Signale.
- [x] Tests für Namen, GUID/Seed-Stabilität und getrennte reproduzierbare Ströme schreiben; RED protokollieren.
- [x] Minimale SQLite-Implementierung und gewichtete Bänder.
- [x] Zustands-/Restart-/Human-/Rate-/Doppelcontroller-/Admin-Tests RED/GREEN.
- [ ] Ganze vorhandene Python-/C++-Regressionen außerhalb fremder Lastmessungen; Ergebnisse dokumentieren.
- [x] Portablen Kern samt Konfigurationsbeispiel und expliziter Nichtaktivierung committen.

### Task 3: Retail-Lebenszyklus und Farbsyntax
**Files:** eigener späterer Runtime-Adapter nach belegter Schnittstelle, zugehörige Tests/Runbook.
**Interfaces:** Task2-Intents; PR46-Supervisor abgestimmter Sollzustand. Keine parallele Änderung am aktiven Supervisor.
- [x] Nach Ende fremder Qualifikation Ressourcen/Prozesse/Ports erneut prüfen.
- [x] Einzelverbindungs-Smoke ohne neue DLL; Plain-Nickname und isolierte Query verifiziert. Farb-HUD/Limit noch offen.
- [x] Echte individuelle Join/Quit/Rückkehr mit stabiler GUID am selben isolierten Server nachgewiesen; Crash-vs-geplant im produktiven Controller noch offen.
- [ ] Produktions-Supervisor erst nach Integration an session desired-state binden; keine doppelte Wiederherstellung.
- [ ] Poolfarbe erst nach Native-Gate aktivierbar machen.

#### Fortsetzung 21.10., Task 3a: portabler Adaptervertrag
**Files:** `tools/bot_session_runtime.py`, `tools/test_bot_session_runtime.py`.
**Consumes:** `Planner.identities()/states()` und unveränderte PLC4-Vorlage.
**Produces:** `profile_bytes(template, identity) -> bytes`,
`startup_script(identity) -> str`, `ControllerLock(database)` als Contextmanager,
`reconcile(state, observation) -> str` ohne Prozessnebenwirkungen.
- [x] RED/GREEN: PLC4-Name/GUID ändern, Team/Appearance bytegenau erhalten; beschädigte
  Längen, gefährliche Namen und Farben verweigern. Wiederkehr identisch.
- [x] RED/GREEN: Profil/Seed müssen die vorhandenen BotDriver-Symbole erreichen.
- [x] RED/GREEN: zweiter Controller auf derselben DB (auch Symlink) gesperrt;
  Freigabe nach Contextende/Prozessende. Kein zeitbasiertes Lock-Stehlen.
- [x] RED/GREEN: Join nur mit bestätigtem Prozess UND Verbindung; Ghosts/unklarer
  Prozess blockieren; geplanter Leave erzeugt keinen Wiederanlauf;
  Exit/Disconnect bleiben bis bestätigter Abwesenheit in Quarantäne.
- [x] GREEN: `python3 -m unittest discover -s tools -p 'test_*.py'`.
- [x] Commit/Push mit präzisem Umfang; echte Ausführung bleibt separates Gate.

#### Fortsetzung, Task 3b: isolierter Einzelverbindungsnachweis
Erst nach belegtem Ende der PR46-Messung: private Overlay-/Wine-Prefix-/Port-
und cgroup-Umgebung, immutable Build04. Eine Identität per Prozess, Profile
aus SQLite statt zufälliger Neuerzeugung. Regulärer WM_DELETE_WINDOW-Pfad,
Prozessende UND vollständige Query-Abwesenheit, danach gleicher GUID-Hash
bei Rückkehr. Keine Verwendung des fixen PR46-Wiederanlaufs. Farben bleiben
gesperrt bis HUD/Scoreboard/Kill/Query/Vanilla-Darstellung einzeln geprüft.

### Task 4: Verhalten, Kapazität und Abnahme
**Files:** gezielte vorhandene Human-KI-Erweiterungen, Tests, Berichte.
- [ ] Fehlende Ressourceninteressen und zeitlich zusammenhängende Orientierungspausen gezielt anbinden.
- [ ] Neue DLL falls nötig separat MSVC-bauen, Hash und 1/4/8-Gates.
- [ ] Isoliert acht, danach 2x8 mit Baseline und >=60 min gemeinsamer Stabilität.
- [ ] Normale Sessions und beschleunigte Zustandswechsel getrennt messen.
- [ ] Profile unter gleichen Bedingungen beobachten; Messungen von subjektiven Urteilen trennen.
- [ ] Eigene Ressourcen schließen, Hash-/Restore-Nachweis.

### Task 5: Review, PR und Handoff
- [x] Review, Konfigurations-/Aktivierungs-/Rollback-Anleitung und präzise offene Gates.
- [x] Eigenen Branch pushen und PR erstellen. Bei externem Blocker ausdrücklich Draft/Teilstand.
- [x] Handoff mit SHA, Tests, Produktionsstatus, belegtem Blocker und kleinstem nächsten Schritt aktualisieren.

## Ausführungsstand / Handoff
Portabler Kern 8467149: 72 Python-Tests (29 neu) OK, unabhängiger Review ohne belegten blockierenden Kernfehler. Echte gleichzeitige Controller und 200 virtuelle Sitzungen mit normalen Zeitbändern geprüft; keine reale Stundenabnahme. Task3/4 BLOCKED_NATIVE_ACTIVE_PR46_QUALIFICATION: fremder MEASURING_3600-Lauf und kollidierende Supervisor-Lebenszyklusarbeit. Keine Runtime-Anbindung oder Gameplay-Erweiterung fertig behauptet. Vollständiger Befund, private Belegorte und kleinster nächster Schritt: docs/reports/2026-10-21-identities-sessions-handoff.md. PR bleibt Draft, Produktion unverändert.

Draft-PR: https://github.com/Escoba2024/SeriousSam-TSE-Bot-Servermods-/pull/47. Veröffentlichung über verbundenen GitHub-Connector nach fehlgeschlagener HTTPS-Push-Anmeldung; veröffentlichter Implementierungsbaum b1bcf596beeacdceecbe8f109c64efb011a881d3 entspricht exakt dem geprüften lokalen f9d8a40. Lokale Beleggeschichte unter agent/identities/20261021-sessions-local-proof erhalten. Kein Merge, keine Aktivierung. Task3/4 weiterhin offen.

### Fortsetzung 21.10. 17:54 UTC – Umsetzung Task 3a (chat/RDC Hetzner)
- Neuer ausschließlich portabler Adapter: `tools/bot_session_runtime.py`; 17 neue Tests in `tools/test_bot_session_runtime.py`.
- Read-only echte PLC4-Vorlagenstruktur von `install/vanilla/Players/Player0.plr` gegenüber dessen .guid-Sidecar geprüft; ausschließlich Nickname-Länge/ASCII-Name/GUID werden im Ergebnis verändert; restliche Team-/Appearance-Bytes gleich. Die aktive Retail-Kopie wird NICHT geschrieben.
- Derselbe UUIDv5 und BotDriver-Seed bleiben bei Wiederkehr identisch; `bot_iProfile0`, `bot_iProfileSeed` und `bot_iRosterOffset` sind im integrierten BotDriver-Quelltext vorhanden und offline geprüft. Farbwert wird NICHT in einen nativen Namen umgesetzt.
- Pro DB kanonisches `flock` inkl. Symlink-Gleichheit, verweigerter Hardlink-DB/Lock-Symlink und Prozess-Exit-Freigabe; `claim_launch(identity,epoch)` persistiert eine einmalig beanspruchte JOINING-Epoch transaktional in SQLite. Kein automatischer Retry eines unklaren Starts.
- `reconcile` ist ohne Prozessseitenwirkungen; verlangt explizite gleiche Identität/Epoch, belegte Eigentümerschaft, frische Query und klare Ghost-/Fremdprozessgrenzen. Ohne Native-Probe nie Starten, Töten oder `Planner.record` ausführen.
- **89/89** komplette `python3 -m unittest discover -s tools -p 'test_*.py'` PASS (3.634 s), davon 17 neue Runtime-Adapter-Tests. Keine zusätzliche CPU-/C++-/Wine-/Native-Qualifikation, solange PR46 `MEASURING_3600` läuft.
- Diese Umsetzung vervollständigt ausschließlich den portablen Task3a-Vertrag; Task3b/4 und Gesamtziel weiterhin offen.

### Follow-up 18:00 UTC – separate-process contention and full planner-adapter lifecycle
- Zwei zusätzliche Tests: echter zweiter OS-Prozess bleibt während gehaltener Kernel-Sperre ausgeschlossen; kompletter **simulierter** Pfad Intent → durable Launch-Claim → Join-Ack → geplantes Leave → bestätigte Abwesenheit → Cooldown. Keine Wine-/Native-Prozesse gestartet.
- Gesamtsuite `python3 -m unittest discover -s tools -p 'test_*.py'`: **91/91 PASS, 3.985 s**, jetzt 19 Runtime-Adapter-Tests.
- Vorheriger Adapterstand unter PR #47, GitHub Commit `507217ccfd82407ffcb5e3ded473d51309e16d64` publiziert; veröffentlichter Tree `a79f824f7c15e64c0e89802698a6fc9800c3cb60` lokal verifiziert. Dieser Follow-up erhält gesonderten Commit. PR verbleibt Draft.
- PR46-Runtime zur Probezeit 18:00:22 UTC: `MEASURING_3600`, 3044 s erfasst, keine Kollision erzeugt.

### Task3b Vorbereitung 18:07 UTC – native, aber noch nicht gestartet
- `tools/qualify_integrated_wine.py` erweitert um Opt-in `--identity-record`, ausschließlich `--stage one` und niemals Public-/Reference-Modus. Profil0 und GUID-Sidecar dürfen nur **nach bestätigtem eigenem Overlay-Mount** geschrieben werden; originäre Profile/Standardeinstellungen und die alten Stufen ohne Flag bleiben unverändert.
- Die vorhandene Build04-Human-KI erhält im separaten Einzelspieler-Startskript den festen Nickname über PLC4, `bot_iProfile0` und `bot_iProfileSeed`. Farbe bleibt deaktiviert.
- Statischer Verweigerungs-/Private-Mount-Fixture-Test: Versuch auf Nicht-Mount verweigert ohne Schreibzugriff, simuliertes Mount-Fixture patcht nur die private Kopie und verifiziert Sidecar/Hash. **Keine native Abnahme dadurch.**
- Suite: **92/92 PASS**, davon 20 Runtime-Adapter-Tests; ursprünglich laufende PR46-Messung hatte bei 18:07 noch Ressourcenpriorität. Erst nach tatsächlicher Qualifikation und erneuter Prüfung isolierten Single-Retail-Smoke erwägen.

### Fortsetzung 18:29 UTC – native Einzelverbindungs-Gates erfüllt, Gesamtziel weiterhin offen
- Fremde PR46-Abnahme: `PASS_ISOLATED_LIFECYCLE_AND_60MIN` / 3600 s / 0 neue Throttles / öffentlicher 8er und privater 8er gleichzeitig. Private fremde Prozesse und Mounts danach beendet, Public bleibt aktiv.
- Eigene isolated Retail Stage-one: 2 Plain-Läufe mit *derselben* SQLite-Identität je 120+70 s, jeweils `PASS_LIMITED`, `ACTIVE_OK`, volle Query-Vanilla 1.07, identischer PLC4-SHA, 0 CPU-Throttles und 6/6 ausgehängte Overlay-Mounts.
- Separater Farbmarkup-**Probe**lauf `^c80D8FFMika^r`: 45 s `PASS_LIMITED` und GameSpy-Name `Mika` ohne Rohcodes. HUD/Scoreboard **nicht** bewiesen, ein privater Xvfb-Screenshot zeigte Splash, deshalb `colors_enabled` weiterhin unverändert deaktiviert.
- Same-Server-Rejoin-Probe: eigens gestarteter Bot-Prozess verlässt nach regulären WM_DELETE_WINDOW-Signalen den **laufenden** isolierten Dedicated, GameSpy meldet seine Abwesenheit 3× während Originalclient im Server bleibt; neuer Bot-PID tritt mit identischem Profil und GUID-Sidecar wieder bei, Server-PID unverändert. Danach 45 s `PASS_LIMITED` / `ACTIVE_OK` / 0 neue Throttles; alle 6 Mounts zurückgebaut. Daten: `docs/reports/2026-10-21-identities-native-smokes.json`.
- In diesem Branch ausschließlich private opt-in Testflags `--identity-record`, `--color-probe`, `--identity-rejoin-smoke` vorbereitet; normale alte Harness-Modi bleiben unverändert. **Weder produktive Farbnamen noch 8 Einzelprozesse, kein Live-Supervisor-Sollzustand** eingeführt.
- Gesamte Python-Tools-Suite **94/94 PASS**, davon 22 Adaptertests; native und portable Beweise strikt getrennt. Aus Zeit-/Kapazitätsgründen nicht fälschlich vollständige 24/7/2x8-Einzelprozesse oder realistische Sessionzeiten behaupten.
- Nächster Umsetzungsschritt: eine wirklich eigentumsgebundene Exec-/Query-Bridge zum SQLite Planner, Integration mit PR46-desired-state statt Doppel-Supervisor, isoliert 1→4→8 **Einzelprozesse** mit Human-Reserve und Abbruchschwellen; erst nach echten HUD-/Query-Limit-Belegen kontrollierte Farbe.

### Task 3c: autonome Fortsetzung ab 23:20 UTC
- [x] Host/Worktree/PRs/Prozesse/Backups geprüft; 94 Bestandstests erneut PASS.
- [ ] Ausführende Bridge mit durable Launch/Leave-Claims, PID/start/CWD/cgroup und vollständigen Query-Abwesenheiten (RED/GREEN).
- [ ] Ein/four/eight individuelle private Retail-Prozesse, gestaffelte Joins/Quits/Rejoin, unveränderte Human-KI.
- [ ] Ressourcen-/Public-Guards; mindestens 60 Minuten nur bei bestandenen Kapazitätsgates.
- [ ] Farb-Sichtbeleg auf eigener Vanilla-Gegenstelle, weiterhin deaktiviert ohne Beleg.
- [ ] Recovery/Review, Ergebnisse und PR aktualisieren; kein Merge ohne alle Abschlussgates.
Ruling: vorhandene Human-KI/DLL beibehalten; keine parallele KI oder zusätzliche Gameplay-Features für diesen Abnahmelauf. Private Session-Bridge ist alleiniger Desired-State-Owner ihrer Runtime; PR46 bleibt unberührt.
