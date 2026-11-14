# Hard2-Kartenadapter Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:executing-plans task-by-task.

**Goal:** Deaktivierten Build020-Adapter für genau ein vorhandenes600s-Kartenfenster vorbereiten.

**Architecture:** Exakten013-Singlemapparent ableiten; vorhandene Reader und reine V2-/Hardpolicys übernehmen. Kein Frida im Parent oder Adapter. Root allein integriert/freezt/startet.

**Tech Stack:** Python3, reine Offline-Unittests, gepinnte private Controllerquellen.

**Spec:** docs/superpowers/plans/2026-11-14-build020-hard-map-adapter.md

## Global Constraints

- Exakter Parentmanifestab364a9a4107686a66c5f94b3e90a6406033084ec48cac789afc1b2b525278f9.
- Build020094ec8ed…/Sourcee5f7a655…, Hard2/Spawn0,600s/diag0, achtBots+Originalobserver.
- Reader/Sampling/Ressourcen/Spielphysik und alle bisherigen Aktivitätsgates erhalten; nur sparseFiregate durch strengereV2 ersetzen.
- Keine Frida-/TSEstarts, Compiler, breite Discovery oder Liveänderungen.
- Unveränderter Fünf-Karten-Katalog; weitere vorhandene Welten bleiben ungeprüft/gesperrt.

## Review Focus

- Falsches/fehlendes Session156 oder Query-Hard führt vor/nachStart zum Fehler.
- Native-/Source-/Map-/PID-/Slot-/Entity-/Worldepoch dürfen nicht vermischt werden.
- Useful-Besitz ab erstem Sample ist kein Pickupübergang; falscheFire/Life/Counterbedingungen bleiben fehlend.
- Teilstart mit verlorenerIdentity darf ausschließlich über tatsächlichen eigenen ready-Prozess regulär schließen.
- Deaktiviertes Paket erbt keine nativeAbnahme; alteDateien/Pins unverändert.

### Task1: enge Policy und deaktivierter Reproducer

**Files:** tools/a4_hard_map_policy.py, tools/prepare_build020_hard_maps.py, tools/test_a4_hard_maps.py.
**Interfaces:** policy.registry(rows,mapping,server,logs,map_data) erzeugt V2Registry für Phase0; finalize delegiert bestehenden aktivenBeleg+unveränderteV2. Builder main(parent,destination,build,v2) schreibt nur neues privatesPaket.

- [x] Tests RED: Policy fehlt; falsche Registry/Epoch/Hard; Bounds; tatsächliches Launcherclose im Teilstart.
- [x] Minimale Policy/Builder implementieren; Parentquellen/Buildsourcepins frisch prüfen.
- [x] Fokussierte GREEN; geerbte reine Tests und V2tests nur benannteModule.
- [x] SeparatesdisabledPaket erzeugen; Hash-/Minimaldiff/Sourceprovenienz prüfen.
- [ ] Bereinigten Handoff/Report und Commit erstellen; unabhängiger Rootreview offen.
