# Getterrestore Boundary Implementation Plan

> REQUIRED: executing-plans / TDD / verification-before-completion. Kein zusätzlicher Agent, keine Runtime. Spec: docs/superpowers/specs/2026-11-15-first-state-getter-restore-boundary.md.

## Grenzen und Interfaceledger

Parent ist ausschließlich der deaktivierte Wine-Identity-Fork87d4c55a. Bodyd80e65ab/compiled34e31ff8. Task1 liefert exakt reversiblen Transform; Task2 konsumiert genau diese vollständigen Hashwerte und den unveränderlichen Elternmanifestpin. Keine Änderungen am alten Winebuilder/VM/MethodWindow/Transport/API. Root allein integriert/freezt/startet.

## Task1 — tatsächliches deferred-restore RED→GREEN

- [x] Neue VM auf tatsächlichem unverändertem Harness: Standardheader/Wineguards erhalten; Detach pending bis Callbackexit/RPCreturn. Alter Inside-Getter-Check muss tatsächlichen Fault vor Exit zeigen.
- [x] Gegenfälle vor Änderung: fehlender Commit/Byte-Drift vor main/nonmain Row, stopped drain ohne Folgecallback, hoststop-beforecommit und admitted leave, TTL/Identity/Body/IAT unverändert hart.
- [x] Minimaler Transform: nur Inside-Getter-Check entfernen, Fullgettercheck an emit-Eingang sowie stopped-drain hinzufügen; lifetime unverändert. Ganze Body/JS/G-Inversen.

## Task2 — frischer deaktivierter Fork

- [x] Neue151/72Closure-/Repin-/G-/Gate-/Schema-/Grenzwerttests RED, dann enger Builder mit vollständigen erwarteten Werten. Nur Body/JS/zweiNamespaces/abgeleiteteManifeste.
- [x] Ein fokussierter Abschlusslauf, Freshfork, private Quittung/echteAusgaben, bereinigter Bericht und Commits. AlleJobs beenden und Rootstatus melden. Keine native Methoden-/A1-Qualifikation.

## Ledger

Rootruling bestätigt zusätzliche emit/stopped-drain-Checks, da nonmain nicht durch lifetime läuft und stopped drain bislang nur restored-Status enthielt. Keine Guardlockerung; keine Schema-/Counteränderung. Offizieller Beleg: https://frida.re/docs/javascript-api/#interceptor (automatisches Commit bei Runtimeaustritt/send/RPC).

Task1: tatsächlicher alter Getter RED1/2 (Legacy-Faultbeleg PASS, Commit-Success FAIL mit exakt1restore-Fault); remove-only Sourcegegenprobe RED2/2 an nonmain/stopped-drain. Danach17actualVM-/Inversefälle GREEN0.906s. Bestehendes lifetime bytegleich, keine weitere Interfaceänderung. Private Logs `.codex/evidence/first-state-getter-boundary/{red,adversarial-red,green}.log`. Rootruling zu den2Boundarysites vor Implementierung erhalten.

Task2: Freshbuilder RED6/6, GREEN6/6/11.596s; Abschluss35/35PASS12.439s einschließlich unverändertem MethodWindow. Freshmanifestb365d06a/nested1ba94da7,151/72Pins/89lokaleDateienbytegleich/3volleSourceinversen. Keine Runtime, keine Kontrolltransferfreigabe, Rootreview noch ausstehend. Keine gleichartige weitere Testsuite erforderlich.
