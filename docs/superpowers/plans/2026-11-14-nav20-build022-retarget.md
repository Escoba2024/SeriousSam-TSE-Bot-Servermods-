# Build022 Nav20 Einzelarm Implementation Plan

> Ausführung mit executing-plans/TDD im eigenen Worktree; keine Delegation.

**Goal:** Einen deaktivierten einzelnen RedStation600s-Arm für Build022 erzeugen.
**Architecture:** Exakten Nav20-020-Parent und vollständigen Build022-Closure
prüfen, nur Kandidatenpfad/-hash, ehrliche Kennungen und lokale Kandidatentabelle
retargeten. Reversebytes müssen die drei ursprünglichen Dateien exakt ergeben.
**Tech Stack:** Pythonstandardbibliothek; reine Datei-/AST-/Fixturetests.
**Spec:** Rootauftrag14.11.2026, Build022source621e92f/DLL28028e44.

## Grenzen und Reviewfokus

- Kein TSE/Wine/Frida/Display/Compiler/Netz/Rootfreeze/Live/Rollout.
- Ein einzelner600s-Arm, kein automatisches Dreierset/Retry.
- Hard2, DEMON3,8Bots+Original,20FPS, Nav/Seeds/Config/Readers/ProtocolV3,
  alle Readraten/Fristen/Ressourcen-/Restore-/Closegates unverändert.
- Exakter Parent7c1bd1ae…; Buildmanifest8557a3a3… mit47Source/28Overlay,
  DLL28028e44…/434176Bytes frisch prüfen. Falsche Pins/Closure hart ablehnen.
- Deaktivierte Gates, eindeutige Namespaces, keine implizite Runtimefreigabe.
- Neues Healthflag ist nur Proposal; keine tatsächliche Pickup-/Navabnahme.
- Alte Native-FAIL/PASS_LIMITED bleiben erhalten. Keine Rohlogdekompression nötig.

## Aufgaben

Dateien: neue tools/prepare_navigation_build022.py und
 tools/test_navigation_build022.py; eigener Bericht/Claim.

- [x] Echte Dateiretargtests zuerst RED: Reversebytes, exakte drei Deltas,
  Fixedoptions/Tiers, Parent-/Build-/DLL-/Sourcepins, neueDestination und Gates.
- [x] Minimalen Builder implementieren: prepare(destination), transform/reverse,
  validate_build und vollständige Pins/Metadaten; bestehende Dateien unverändert.
- [x] Gezielte Tests GREEN, deaktiviertes Paket erzeugen und Closure rücklesen.
- [x] Bereinigten Bericht/Quittung, Sourcecommit und sauberen Handoff liefern.
- [ ] Root unabhängiger Review/Freeze; Native nur Root und separat.
