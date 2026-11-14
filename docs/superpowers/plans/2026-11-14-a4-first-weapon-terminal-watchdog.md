# A4 first-weapon terminal watchdog Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement task-by-task.

**Goal:** Den vorhandenen passiven Itemabbruch auf genau die belegte gewöhnliche erste Waffen-Endannäherung erweitern; keine Bewegung freigeben und keinen Native-PASS behaupten.

**Architecture:** In BotCecilItemTransitFailed bleibt der bestehende Intermediatezweig erhalten. Ein enger alternativer Terminalzweig erlaubt ausschließlich hop==goal, passendes gemapptes WeaponItem, noch keinerlei nützlichen Waffenbesitz/-nutzbarkeit und Stand/Hocke innerhalb der bestehenden3m-Connectorhöhe. Sämtliche Flags/Locks/Spezial-/Follow-/USE-/Flight-/Ownership-/World-/Entity-/Generation-/Zeitguards und10s/.75m-Regeln bleiben erhalten. Ablauf beendet nur Item, bestehenden30s-Backoff und neutrale aktuelle Achsen; nächster normaler Selektor entscheidet.

**Tech Stack:** Tatsächlicher nativer C++-Bridgecode mit bestehendem enginefreiem Welt-/Raystub; fokussierter Einzelharness, keine Discovery/native/Liveänderung.

**Spec:** Root-Auftrag14.11.2026 nach geschlossenem Build019-Quiet-FAIL23/24; User A4 verlangt wirkliche Waffenbeschaffung und keine Umetikettierung offener Tests.

## Global Constraints

- Nur Hauptagent integriert, baut Retail und startet Native. Eigener Worktree codex/20261114-a4-terminal-watchdog.
- Ursprünglicher Lauf bleibt FAIL; Anfangsbesitz8195 wird nicht als niebewaffnet bezeichnet. Raw-Pickup vor Inventory7.7 ist separate Messlücke.
- Neue Terminalzulassung verändert weder10s noch.75m, ursprüngliche Deadlines oder30s-Itembackoff; keine zusätzliche Bewegung/Geometrie/Rays/Entitysuche.
- Terminaltyp aus bestehendem frischen Goalzustand/Graphbindung; gewöhnliche Intermediatebehandlung bleibt identisch. Kein globaler Konkurrenz-/Timeoutfix.
- Native DiagTerminal337.7..350.7 und State6760..7020 sind sparse Anker; synthetische20Hz-Halteintervalle im Replay ehrlich kennzeichnen. Physische Ablehnungsursache bleibt mangels vollständiger Probe unbekannt.

## Review Focus

- Passendes Weapon-Terminal nicht mit gewöhnlichem Health-/Ammo-/Powerup-/wichtigen Interaktionsziel verwechseln.
- Bereits nützlicher Besitz oder Nutzbarkeit, echte Annäherungsfortschritte und spezielle/vertikale/airborne Übergänge dürfen nicht abbrechen.
- Frame-/Owner-/World-/Entity-/Generation-/Goal-/Map-/Gravity-/Deadlinewechsel und Lücken dürfen alte Beobachtungszeit nicht übertragen.
- Exakte10s/.75m-Grenzen; bei Abbruch nur lokale Itemablehnung, neutrale Achsen und normaler nächster Selektor, keine zusätzlichen Ray-/Lookup-/Allokationskosten.
- Bestehende Intermediate-, Teleporter-/Bouncer-/Flight-/Lock-/Recoveryregressionen mit tatsächlichem Bridgecode prüfen.

## Aufgaben

- [x] Vollständige vorhandene Logs/Diag und Lifecycle geprüft; Terminal von beiden bisherigen Watchdogs ausgeschlossen. Kein kompletter Probe-Trace für dieses Leben.
- [x] RED: echte111→175-Anker, Erfolgspfad, Negativfälle und Kontextresets im bestehenden Bridgeharness ergänzen; gegen unveränderte Quelle erwartetes FAIL prüfen.
- [x] GREEN: enge Alternative im Eligibilityzweig implementieren; bestehende Uhr/Abbruchaktion unangetastet.
- [x] Fokussierten Bridgeharness und geeignete Sanitizerprüfung ausführen; keine breite parallele Suite.
- [x] Quell-/Testdiff, SHA-Provenienz, Ergebnisse/Grenzen und nächsten Rootschritt dokumentieren und committen.
