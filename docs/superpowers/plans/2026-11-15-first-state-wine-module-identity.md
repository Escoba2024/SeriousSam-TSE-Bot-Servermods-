# Wine module identity Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Strikte Wine-taugliche Modulidentität für den deaktivierten inputfreien Methodenfork ohne Frida-PE-Modulliste.
**Architecture:** Exakter reversibler Sourceabschnitt ersetzt nur moduleIdentity; tatsächliche alte Observer-VM mit synthetischen Standard-PE-Headern und bewusst fehlender Frida-Modulliste. Frischer Fork und vollständige erwartete Hashwerte.
**Tech Stack:** Pythonstdlib, vorhandener Node-VM-Harness; keine Runtime oder Compiler.
**Spec:** docs/superpowers/specs/2026-11-15-first-state-wine-module-identity.md

## Global Constraints

Body7d93b441/JSfec627f2/G/38/11/18/Registry2/Limits unverändert bis auf moduleIdentity. MZ/PE/I386/PE32/optional224/exaktes und bounded e_lfanew/SizeOfImage. Keine NativeFunction/Writes/Frida-PE-Liste/Fallback. Nur neue öffentliche selbstgeschriebene Quellen, Retailbytes ausschließlich privat. Alle Authorgates false; alte Pakete und NativeFAIL behalten.

## Review Focus

Moduleliste wirft wie Native; fehlende/ungültige Header vor Hooks; falsches Originalbody-/IAT trotz korrektem Header; PE-offset außerhalb erster4KiB; repinnte Body-/Policy-/Binding-/Grenzwertänderung darf nicht passieren.

### Task1 actual VM RED→GREEN

Create tools/first_state_wine_identity_patch.py +tools/test_first_state_wine_identity_patch.py +own VMcase JS. patch_body/reverse_body/patch_compiled/reverse_compiled only pinnedparents. Privateharness ergänzt nur Standardheader-Memory und modulelistthrows.
- [x] Nativeähnliche fehlendeModulliste-RED am alten tatsächlichen Observer; negative Header-, Base-, Memory-, Body-/IAT- und lifetime-Mutationen müssen den richtigen Guard vor attach treffen.
- [x] Minimaler Guard und exakte Inversen; GREEN mit tatsächlicher Getter-/Init-/Colt-VM-Kette und NoWrites/DefaultFalse. Keine Änderung am alten Harness/Body.

### Task2 fresh disabled fork

Create tools/prepare_first_state_wine_identity.py +focused tests; Parent51e1bc45 behalten. Body+compiledJS, zwei Runnernamespaces und abgeleitete Manifeste/Pins ausschließlich; Helper/API/Runnerbodies sonstbytegleich.
- [x] RED Repin-/Closure-/G-/Gate-/Policyänderung, dann minimaler Freshbuilder mit vollständigen erwarteten151+72Werten.
- [x] Fokussierter Gesamtlauf, private Belege/Hashes, bereinigter Report/Commit/alleJobsended. Root reviewed/enables/runs separat.

## Ledger

PreflightTask1→Task2: Gprefix ist kein veränderbarer Pincontainer; Headerpins außerhalbG. Headerdateifelder dürfen als Metadaten veröffentlicht werden, keine Retailcodebytes. Rootruling vorImplementation gesendet; alle anderen Identitätsbelege bleiben. No delegation.

Task1 complete: tatsächlicher alter Observer RED `unable to find module Engine.dll` (1 failure, nach korrigiertem privatem Bindingpfad); neuer Transform/VM 19 Tests GREEN (1.235s), inklusive neun Headergegenfällen auch für Entities. Zwei Testpräzisierungen benannten vorhandene frühe `pointer bounds` und `original import target changed` statt erfundener Meldungen; Produktionsguards nicht geändert. Ganze Body-/JSinverse und Gbytegleich. Logs privat `.codex/evidence/first-state-wine-identity/{red,green}.log`.

Task2 complete: Freshbuilder fehlend RED6/6, GREEN6/6; vollständiger Abschluss mit zusätzlichem admitted-leave-Gegenfall und geerbten MethodWindow-Tests 38/38 PASS/12.308s. Tatsächlicher Leave-Headerfehler folgt unverändertem fault/terminal-Catch, nicht dem zunächst erwarteten bounded(false)-aborted-Zweig; Test berichtigt, Counter nicht verändert. Freshmanifest87d4c55a,151/72Pins/89lokaleDateienbytegleich und3Sourceinversen geprüft. Keine Parent-/Runtimeänderung. Öffentliche Quellen/Tests und Bericht zur unabhängigen Rootreview bereit; keine Delegation. Kein gleichartiger weiterer Testlauf vorgesehen.
