# FirstStateV2 Method Adapter Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Deaktivierter, reviewbarer Getter-/Quiescence-/FreshExec-Adapter für den unveränderten Zwei-Originalspieler-Observer.
**Architecture:** Gepinnte private Eltern bleiben unverändert. Ein enger Sourcepatch erzeugt einen privaten Fork; neue Ports/Worker isolieren Frida vom Rollenparent. Alter Runner bleibt unverändert.
**Tech Stack:** Python standard library, Node VM mit vorhandenen privaten Originalfixtures; kein Native.
**Spec:** docs/superpowers/specs/2026-11-15-first-state-v2-method-adapter.md

## Global Constraints

Keine AI/Population/Input-/ABI-/TTL-/Schemaänderung. 38 Bindings/18 Listener/exakt2 Registry bleiben. Alle Gates false. Kein Retailcode öffentlich; nur selbstgeschriebene Patch-/Transportquellen. IPC Payload2MiB+Envelope16KiB, kein Truncieren. Keine Delegation/Runtime.

## Review Focus

Aktive Calls beim Stop; TTL/Fault während zugelassenem Leave; zu große/malformed IPC-Antworten vor Validation archivieren; PIDreuse/fehlende Rollenbereinigung; unsichere Unload-/Detachlage. Diese Fälle gehören in Task1/2.

### Task 1: enger Observerpatch

Files: tools/first_state_method_patch.py; tools/test_first_state_method_patch.py. Consumes: pinned private observer body; produces patch_body(text), reverse_body(text). Reuse actual VM/harness privately.
- [x] RED echte function-Registrierung, aktive Callstop/Idle, TTL/Faultsticky, unverändertes Drainschema, Reverse+Guardmutation.
- [x] Minimaler Patch; GREEN mit echten VM-Fällen und gezielten I1/I2-Regressionen; Commit.

### Task 2: bounded Ports und FreshExec-Worker

Files: tools/first_state_method_transport.py; tools/test_first_state_method_transport.py. Consumes: unveränderter NativeContext/ObserverSession; produces LegacyWorkerPorts + finish_after_roles_closed. Worker startet per neuem subprocess ohne geerbte Locks; kein Parent-Frida.
- [x] RED OS-Fixturen für vollständige Rawpersistenz, Payloadgrenzen, Seq/malformed/Timeoutsticky, eigene PID/Startbindung, unarmed Startfehlerreap, Reap erst nach Rollenclose, Stop-Idle-Absolutdeadline.
- [x] Minimales vorhandenes FreshExecmuster adaptieren; sichere Cleanupversuche trotz sticky Fehler; GREEN; Commit.

### Task 3: deaktiviertes Reviewpaket

Files: tools/prepare_first_state_method_adapter.py; tools/test_prepare_first_state_method_adapter.py; neuer bereinigter Report.
- [x] RED falsche Eltern-/Bindingpins, Mutation unveränderter I1/I2/Runner, falsches Registry-/Limits-/Gateprofil.
- [x] Neuer privater Fork mit unveränderten38Bindings, alten Quellen+neuen Adapterdateien, falschen Gates und exakter Sourceinverse; keine Runnerintegration.
- [x] Fokussierter Gesamtlauf, Source-/Pinbelege, Report/Commit und alle Jobs beendet melden.

## Ledger

Pre-flight Task1→Task2: neues status/finishstop bleibt außerhalb des alten Drainschemas. Task2→Task3: Transportports sind API, keine Aktivierung des alten Runners. Rootentscheidung siehe Spec. Tests nur fokussiert, keine breite unveränderte Discovery.

Task1: complete173e2bb; actualVM RED9/10, GREEN10/10. Rootreview callbackpartialadmission ergänzt: dropped1/aborted1/terminalEnter bleiben FAIL. Task2: GREEN16 transport+10VM=26/26 in0.810s; tatsächliche OwnLock/3Kinder-Identitätskontrolle, kein Fridaimport. Journalfehler darf sichere finishstop-Bereinigung nicht überspringen (adversariales RED→GREEN). Passive cleanup-drain bleibt trotz sticky Transportfehlers zugänglich; keine neue Admission.

Task3: complete: actual 5/5 missingbuilderRED, missingNativeContextClosure RED, GREEN34/34 focused2.759s. Disabledpackage manifest65453847,72pins/37byteequalparents/oneinverseobserver. Final author self-review: no further confirmed material finding; Root independent review requested. Native/runnerintegration remain open. No extra task/delegation.

Rootreview unusedCLI: RepinGateTrue adversarialRED→GREEN; finale35/35PASS3.189s. Finalfreshpackage1e59d326/72pins, vorbereitendes65453847 bleibt unverändert. QualifiedBaseWorker806d4c33→disabledacf3fa01 nur ein GateTrue→False, zusätzlicher CLI bleibt auch späterfalse.
