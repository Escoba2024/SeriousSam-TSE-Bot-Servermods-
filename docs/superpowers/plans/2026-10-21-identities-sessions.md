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
- [ ] Nach Ende fremder Qualifikation Ressourcen/Prozesse/Ports erneut prüfen.
- [ ] Einzelverbindungs-Smoke ohne neue DLL und Farbe/visible/Query/Meldung/Name-Limit messen.
- [ ] Echte individuelle Join/Quit/Rückkehr mit stabiler GUID; Crash vs. geplant nachweisen.
- [ ] Produktions-Supervisor erst nach Integration an session desired-state binden; keine doppelte Wiederherstellung.
- [ ] Poolfarbe erst nach Native-Gate aktivierbar machen.

### Task 4: Verhalten, Kapazität und Abnahme
**Files:** gezielte vorhandene Human-KI-Erweiterungen, Tests, Berichte.
- [ ] Fehlende Ressourceninteressen und zeitlich zusammenhängende Orientierungspausen gezielt anbinden.
- [ ] Neue DLL falls nötig separat MSVC-bauen, Hash und 1/4/8-Gates.
- [ ] Isoliert acht, danach 2x8 mit Baseline und >=60 min gemeinsamer Stabilität.
- [ ] Normale Sessions und beschleunigte Zustandswechsel getrennt messen.
- [ ] Profile unter gleichen Bedingungen beobachten; Messungen von subjektiven Urteilen trennen.
- [ ] Eigene Ressourcen schließen, Hash-/Restore-Nachweis.

### Task 5: Review, PR und Handoff
- [ ] Review, Konfigurations-/Aktivierungs-/Rollback-Anleitung und präzise offene Gates.
- [ ] Eigenen Branch pushen und PR erstellen. Bei externem Blocker ausdrücklich Draft/Teilstand.
- [ ] Handoff mit SHA, Tests, Produktionsstatus, belegtem Blocker und kleinstem nächsten Schritt aktualisieren.

## Ausführungsstand / Handoff
Portabler Kern 8467149: 72 Python-Tests (29 neu) OK, unabhängiger Review ohne belegten blockierenden Kernfehler. Echte gleichzeitige Controller und 200 virtuelle Sitzungen mit normalen Zeitbändern geprüft; keine reale Stundenabnahme. Task3/4 BLOCKED_NATIVE_ACTIVE_PR46_QUALIFICATION: fremder MEASURING_3600-Lauf und kollidierende Supervisor-Lebenszyklusarbeit. Keine Runtime-Anbindung oder Gameplay-Erweiterung fertig behauptet. Vollständiger Befund, private Belegorte und kleinster nächster Schritt: docs/reports/2026-10-21-identities-sessions-handoff.md. PR bleibt Draft, Produktion unverändert.
