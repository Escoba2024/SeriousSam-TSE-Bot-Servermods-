# A1: XTest-Metadaten vor Recorderarm vorbereiten

Rootauftrag nach geschlossenem Own167-Methodenlauf; ausschließlich Offline-
Implementierung im separaten Worktree, Root allein integriert/friert/startet.
Claim: enger Prearm-Helfer in `tools/a1_passive_xrecord.py`, neue
`prepare_a1_xtest_preparation.py`, `test_a1_xtest_preparation.py`, dieser Plan
und eigener Bericht. Keine Änderungen an anderen Agentenclaims oder Runtime.

## Herkunft und unveränderte Grenzen

Parent ist der deaktivierte ReleaseSafeAttempt-Fork
`/srv/tse-a1-passive-attempt-release-safe-disabled-20261114`, Manifest
`f1cbd265f9b5ade97b8ec27748370b523f877524a6302118bf74fad3e8b18b18`.
Tatsächlicher eigener Cold5/Warm1-Methodenbeleg:
`/srv/tse-cecil-rollout-evidence-20261114/own-xrecord-cold-warm-root-20261114/method-result.json`,
SHA `45adbbad603ab49fde34e3b20f51c8b38ba62a0cb403937a27d15458ccd7a7d2`.
Er belegt die Bibliotheksrequests unter eigenen167-Bedingungen, keine A1-
Retail-/Gain-/Inputvorhersagbarkeit. Metadatenbindung81c402ed… bleibt separat.

`b-a>4` bleibt FAIL. CP/ACK/Gain/EPS, Originalinputs, Inputscope, Fristen,
Frida/Originalbytes/Normalclose, 15s/1024/2MiB/16KiB und alle Hostgates bleiben
unverändert. Keine zusätzliche Eingabe, kein Warmup-Input und kein Retry.
Alte Pakete werden weder verändert noch als PASS umetikettiert.

## Enger Ablauf

1. Vor Code zuerst Fake-C-RED am echten `PassiveRecorder.arm`: öffentliche
   XTestQueryExtension muss auf demselben vorhandenen Transporthandle laufen,
   Version2.2/Return/Metadaten müssen gültig sein; danach XSync derselben
   Verbindung; erst danach erster Recorderarm und Observerbindung.
2. Neuer Helfer verwendet bestehende `transport.t`/`transport.x`/`transport.d`.
   Öffentliche ctypes-Prototypen; keine CDLL/XOpenDisplay/weiteren XTest-Aufrufe.
   Own154/Vanilla/Proxy und unveränderte Displayguards prüfen. Fehler sind sticky
   und verhindern Arm/Inputs; kein Versuch einer Alternativverbindung.
3. Helper genau einmal vor dem bestehenden kid.arm aufrufen, erfolgreiche
   Metadatenquittung in Armreceipt. Keine Arbeit im Emissionshotpath.
4. Gezielte GREEN/Regressionsfälle inklusive ReleaseSafe-Keyup; keine Xlib-/
   Display-/Nativeausführung in Tests. Bestehende Methodenfingerprints und
   vier Coredateien exakt erhalten.
5. Neuer deaktivierter Builder prüft alle Parentpins und beide tatsächlichen
   Methodenbelege, kopiert Parent, ändert nur Adapter/Namespaces/PRIVATE/Pins und
   neue Quelldateien. Alle fünf Gates bleiben False; neue Zielpfade exklusiv.
   Vollständiger Diff, frische Pins,0600-RED/GREEN-Logs und Bericht/Commit an Root.

Rootreview und separate Sicherung/Freeze vor genau einem OriginalNoFire-
Diagnostiklauf. Dieser ist kein automatischer Folgeauftrag zum Rollout.

## Offlineabschluss

RED vor Implementierung tatsächlich gesichert; danach50/50 fokussierte Fälle
PASS ohne Skips. Neuer deaktivierter Fork und77/73/14Pins geprüft, qualifizierte
Methodenfingerprints/Core sowie alle Input-/Release-/ACK-/Zeitfunktionen
unverändert. Keine Xlib-/Display-/Input-/Nativeausführung durch den Autor.
Exakte Quellen-/Paket-/Logpins und Grenzen stehen im Bericht
`docs/reports/2026-11-14-a1-prearm-xtest-metadata-preparation.md`.
Rootreview, separater Rootfreeze/Sicherung und ein OriginalNoFire-Diagnostiklauf
bleiben die nächsten Schritte; keine native A1-Funktionsqualifikation behauptet.
