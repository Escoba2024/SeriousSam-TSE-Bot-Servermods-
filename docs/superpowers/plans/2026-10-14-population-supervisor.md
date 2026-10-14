# Population Supervisor Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan inline. User's autonomous continuation is the preserved execution method.

**Goal:** Kontinuierliche konservative Populationssteuerung für vorbereitete Prozessgruppen.
**Architecture:** Reines Snapshot-/Gruppenmodell plus Adapter über bestehende Fleet-Skripte; Gesamtbelegung statt Human-Präfixklassifikation.
**Tech Stack:** PowerShell7, Windows, vorhandene UDP-/Fleet-Werkzeuge.
**Spec:** docs/superpowers/specs/2026-10-14-population-supervisor-design.md

## Global Constraints
- TSE1.07, pro Gruppe1..4 lokale Spieler; GameMP/Engine/Entities unverändert.
- Cap=min(TargetPopulation,MaxPlayers−ReservedHumanSlots).
- Drei konsistente vollständige Antworten; keine Aktion bei unsicherem Sample.
- Starts zwei konsistente Beobachtungen, Wiederstart-Cooldown10s, Join-Deadline45s; Stops priorisiert.
- Nur eigene Prozesse; exklusive Clientlocks und begrenzbarer Loop.

## Review Focus
- Andere Prozesse/Controller dürfen nicht gestoppt oder übernommen werden.
- Keine Human-Präfixklassifikation oder Annahme, dass Count allein Join bestätigt.
- Fehler nach Teilstart/bei State-Schreiben müssen endlich bereinigen.
- Truncation/Mapwechsel und Human-Namen-Dubletten müssen korrekt behandelt werden.
- Reale Reserve und Gruppengranularität dürfen nicht als exakte Einzelslot-/Race-Garantie berichtet werden.

### Task1: Snapshot und Gruppenmodell
**Files:** Create poc/scripts/PopulationSupervisorCore.ps1, Test-PopulationSupervisor.Tests.ps1.
**Interfaces:** ConvertTo-PopulationSample(StatusBefore,Players,StatusAfter); Get-PopulationGroupDecision(Sample,Groups,TargetPopulation,ReservedHumanSlots,Now).
- [x] Tests für gültige/ungültige/fenced Samples und4er-Gruppenszenarien schreiben.
- [x] Tests ausführen: erwarteter RED „Supervisor functions are missing“.
- [x] Minimales Modell implementieren.
- [x] Tests ausführen: alle Modellfälle PASS; Commit.

### Task2: Kontinuierlicher Adapter und Loop
**Files:** Create PopulationSupervisor.ps1, Manage-BotPopulation.ps1, Test-PopulationSupervisorControl.Tests.ps1.
**Interfaces:** Invoke-PopulationSupervisor(Config,StateDirectory,TargetPopulation,ReservedHumanSlots,PollMilliseconds,Iterations,ObserveOnly,FleetState), getrennte austauschbare Query/Start/Stop/Running-Adapter für Tests.
- [x] Controller-Tests für Stabilisierung, Pending/Timeout, Cooldown, Lock, Fehler/Cleanup schreiben und erwarteten RED prüfen.
- [x] Vorhandene Get-FleetConfig/Get-FleetIdentities/Invoke-FleetQuery/Start-BotFleet/Stop-BotFleet verwenden.
- [x] Tests, alle vorhandenen portablen Regressionen und PS-Parser ausführen; PASS; Commit.

### Task3: Nachweis und Publikation
**Files:** docs/reports/2026-10-14-population-supervisor.md, poc/POPULATION-SUPERVISOR.md, README.md.
- [x] Neue Funktionen gegen echte lokale Runtime nach Scope abnehmen: endgültige hashgebundene 8→9→5→4→8-Probe bestanden.
- [x] Grenzen/Bedienung und Prüfkommandos dokumentieren.
- [x] Unabhängige gesamte Branch-Prüfung; erforderliche Korrekturen durch Regression belegen.
- [ ] Geprüften Branch/PR veröffentlichen, Remote prüfen, bestehende Drive-Handoff-Dokumente aktualisieren.
