# Eigene explizite QJS-Bedingung, ausschließlich Source

Der neue reine `first_state_qjs_runtime_patch.py` verwendet den vorhandenen
SHA-gebundenen V8-Transform. Gegen dessen Pythonergebnis ändern sich genau drei
Fragmente: literal `runtime='qjs'`, archivierter Request'qjs', erwartete tatsächliche
Runtime'QJS'. Eine kalte Antwort direkt nach load, dieselbePID/ia32/4, exaktes
Schlüssel-/Typenschema, Rawquittung vor Prüfung und bestehendes privates
`atomic_json` bleiben erhalten. Kein Fallback, Retry oder frei wählbarer Parameter.
Der neue Helper hängt deshalb auch vom unveränderten V8helper ab; beide gehören
in einen späteren Root-Sourceclosurepin.

Body und compiledJS sind **bytegleich der zusätzlichen kalten V8-RPC-Version**,
keine neue engineabhängige JS-Variante. Alle drei ganzen Inversen reichen zurück
zum unveränderten Getterreceipt-Parent cd61d6b0…; G-Prefix, Originalbodies,
Warmhooks, Guards, Limits und alte Gates bleiben gleich. Keine alten Pakete,
Python-/JSdateien oder Rootdateien verändert, kein neues Paket erstellt.

Tatsächlicher Behavior-RED: vorhandenes V8-erweitertes `NativePorts.load`, direkt
per AST extrahiert, fordertv8 stattqjs:1Test/1AssertionFAIL/0.011s, kein Importfehler.
Der FakeScript meldet hierbei die tatsächlich angeforderte Runtime; es ist kein
alsV8 verkleidetes QJS-Antwortmodell. Während Roots Reset030-Native danach keine
Tests ausgeführt; nur kleiner Sourceentwurf. Nach ausdrücklichem Closed/Resume
sieben gezielte Tests PASS/0.792s, keine Fehlerkorrekturrunde erforderlich.

GREEN nutzt die tatsächlichen load-/atomic_json-Bodies mit bestehenden FakePorts:
Request/Rohquittung0600, V8-/PID-/Architektur-/Pointer-/Typ-/Schemaschäden,
Create/Load/RPC-/Rawfehler und Cleanupverfügbarkeit ohne Retry. Ganze Inversen,
kein Fremdquellen-/Gatewechsel, tatsächliches identisches compiledJS in NodeVM
(kalte QJS-/V8-Wahrheit, weiterhin falsches Arm-Gate und neun vorhandene strikte
I1/I2-/TTL-/Identitäts-/Header-/Body-/IAT-/Stopfälle). Keine Frida- oder Retail-
Ausführung aus diesen Modellen ableiten.

Reproduktion: `nice -n 15 python3 -m unittest tools.test_first_state_qjs_runtime_patch`.
Private Reproducer/Pins/RED-/GREEN-Logs unter
`.codex/evidence/first-state-explicit-qjs/` im Autorenworktree.

ExplizitesQJS ist eine neue deklarierte Bedingung. Alte runtime=None-Fälle bleiben
RuntimeUNKNOWN; weder die alte CPUursache noch der neue V8-Crash sind erklärt.
Kein V8-Retailretry, keine FPSänderung, kein CPUfix-/A1-/NativeReady-Claim.
Root entscheidet separat über Sourceclosure, Freeze, neue passende Kontrolle,
Originalclient-FPS-Bedingung und höchstens das beauftragte native Fenster.
