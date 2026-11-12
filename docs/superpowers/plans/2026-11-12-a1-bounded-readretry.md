# A1 Bounded Read Retry Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox syntax for tracking.

**Goal:** Nur zwei explizite passive Konsistenzfehler begrenzt erneut lesen, ohne Eingaben zu wiederholen oder Prüfgrenzen zu lockern.

**Architecture:** Die neue private V3-Kopie übernimmt V2 vollständig. Nur `sample()` klassifiziert die beiden transienten EvidenceError-Texte enger und `native_rotation_pair()` erhält die begrenzte Neuerfassung. Bestehende Raw-Receipts und alle Policy-/Lifecycle-Funktionen bleiben erhalten.

**Tech Stack:** Python 3.12, unittest, stdlib AST-/Hashprüfung; keine neuen Abhängigkeiten.

**Spec:** `docs/superpowers/specs/2026-11-12-a1-bounded-readretry.md`

## Global Constraints

- Nur eigener Worktree und neue private V3-Kopie; keine Änderungen an V2, Frozen oder Fixture.
- Maximal 8 Paar-Leseversuche inklusive periodic-Read; zusätzliche 0,2 s nach periodic; 0,01 s zwischen transienten Versuchen.
- Nur zwei exakte EvidenceError-Nachrichten; alle fatalen Fehler sofort weiterreichen.
- Kein Cache-Rückfall, keine Eingabewiederholung, keine Toleranzänderung; 2/85/90 s bleiben bestehen.
- Gate False, Runtime NOT_TESTED, keine Compiles. Root prüft und integriert.

## Review Focus

- Erfolgreiche, aber alte/falsche Daten dürfen keine weitere Auswahl auslösen.
- Ein langsamer letzter erfolgreicher Read an/nach der Deadline muss scheitern und erhalten bleiben.
- Fehler im zweiten Reader müssen den ersten vollständigen Snapshot erhalten.
- Erschöpfung nach rechts + forward muss jede linke Eingabe verhindern.
- Fataler Fehler nach einem transienten Fehler muss sofort abbrechen.

## Task 1: Tatsächliche Reader-Verdrahtung begrenzt korrigieren

**Files:** Private V3 `run_dual.py`, `test_read_retry.py`, eng angepasster `test_diagnostic_controller.py`.
**Interfaces:** Unveränderte `periodic()`, `read_rotation_pair(..., receipt=...)`, `RD.run_calibration(...)`; Tests führen tatsächliche verschachtelte Funktionen mit reinen In-Memory-Readern aus.

- [x] V2-Manifest, nativen Fehlerpfad und tatsächlichen Quelltext lesen; isolierten sauberen Worktree verifizieren.
- [x] Neue V3-Kopie anlegen, V2-Dateihashes sichern und unveränderte private 103er-Suite ausführen.
- [x] Regressionen schreiben: beide Transienttypen -> frisch, Erschöpfung, Deadline, alter Cache, veralteter Erfolg, fataler Fehler/Teilreceipt, keine Folgeeingabe; reale Funktion statt Modell testen.
- [x] Neue Fälle gegen unverändertes V2 ausführen und belegte RED-Ausgaben behalten.
- [x] Nur `sample()` und `native_rotation_pair()` korrigieren; neue V3-Labels setzen.
- [x] Fokussierte Fälle und vollständige kleine private Suite GREEN ausführen.

## Task 2: V3-Paket und Review-Handoff

**Files:** Private V3 `README.md`, `source-manifest.json`, `evidence/v3-*`; Repo-Bericht und dieser Plan.
**Interfaces:** Verwendet das geprüfte V3 aus Task 1; liefert unabhängige SHA-Closure und eng normalisierten Vergleich zu V2.

- [x] Manifest ausschließlich für eigene Kopie/Pfade/Tests/Evidenz erneuern; externe Pins unverändert übernehmen.
- [x] V2-Erhalt, unveränderte Reader-/Policy-/Lifecycle-Quellen und exakten normalisierten Controllerdelta nachweisen.
- [x] Bericht und Root-Runplan aktualisieren, Gate False und Runtime NOT_TESTED ausdrücklich beibehalten.
- [x] Finalen Offline-Suitenlauf, SHA-Prüfung und git diff --check protokollieren.
- [x] Repo-Dokumentation committen; konkrete Pins/Logs/Abgrenzung an Root zum unabhängigen Review melden.

## Ausführungsentscheidungen

- Ausführung ist durch Root bereits beauftragt; keine zusätzliche Planfreigabe nötig.
- Root übernimmt das unabhängige Schlussreview; wegen ausdrücklich begrenzter Worker-Zahl wird kein weiterer Subagent gestartet.
- Der Plan und ein privates `evidence/v3-progress.md` bleiben als dauerhafter Handoff erhalten; keine fremden Plan-Workspaces werden angefasst.
