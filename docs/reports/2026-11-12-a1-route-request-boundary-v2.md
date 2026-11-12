# A1 Route V2: letzte Prüfung an der tatsächlichen XTest-Anfrage

Datum: 2026-11-12

**Status: READY_FOR_INDEPENDENT_ROOT_REVIEW. Beide Gates bleiben false; kein nativer Lauf dieses Pakets.**

## Bestätigter Befund und enge Korrektur

Der unabhängige Review des V1-Pakets war wegen einer Important/P1-Lücke BLOCKED. Die finale Zustands-/Pending-Action-/Budgetprüfung lief vor weiteren Endpoint-/Transportguards. Die unveränderte Reproduktion wurde erneut rein im Speicher ausgeführt: Ein zusätzlicher Guard von 0,30 s ließ eine entsprechend alte Eingabe mit PASS zu; ein Guard von 2 s konnte Down bei 85,8 s nach der 85-s-Grenze senden. emissions.started zeigte zuvor den Zeitpunkt vor diesen Guards.

V2 führt denselben finalen Policycallback durch Endpoint.down bis an X11Transport.event beziehungsweise X11Transport.look. Alle bisherigen Prozess-, Display-, Fokus- und Neutralprüfungen bleiben erhalten. Der genehmigte XTest-Funktionszeiger und seine Argumente stehen fest, bevor der Submit-Callback die finale Zustands-/Pending-/Budgetprüfung ausführt und unmittelbar die tatsächliche XTest-Anfrage aufruft. Danach folgt kein weiterer langsamer Guard vor dem Request.

emissions.started und held_started verwenden denselben tatsächlichen Requestbeginn. emissions.finished erfasst die Rückkehr der XTest-Funktion; transport_finished getrennt das spätere Transport-/XSync-Ende. Ein nicht begonnener Request behält started/finished=null. Eine bestätigte Anfrage bleibt auch dann sichtbar, wenn nachfolgende Arbeit fehlschlägt. Eine unklare Ausnahme wird aufgezeichnet und niemals als Anlass für einen Eingaberetry verwendet.

Die sichere Freigabe bleibt unabhängig: Endpoint.up und released sind unverändert. Bei Key-/Button-up wird der neue Submit-/Policycallback selbst dann nicht aufgerufen, wenn ein solcher Callback übergeben würde. Die vorhandenen Display-Identitätsguards bleiben aktiv. Eine abgelaufene Policyfrist verhindert daher nicht die Freigabe bereits gedrückter oder möglicherweise gedrückter Tasten.

## Exakter deaktivierter Stand

- Worktree: /srv/tse-milestone-a-a1-route-completion-20261112
- Branch: codex/20261112-a1-route-after-rotation
- Basis dieses Follow-ups: 8ee03167e73749eea79bc41f4a9fada474fa867f
- Neues Paket: /srv/tse-a1-route-after-rotation-completion-v2-20261112
- Claim: /srv/tse-milestone-a-continuation-evidence-20261112/a1-route-v2-claim.json
- Plan: docs/superpowers/plans/2026-11-12-a1-route-request-boundary.md

| Artefakt im V2-Paket | SHA-256 |
| --- | --- |
| source-manifest.json | 6ea34a1fa6a11c86c9b25db554535a509fabcccb8b18ba6347603b12fd210ee8 |
| run_dual.py | 266245d1dc78852b0ac42a869b941227b64b2927616051d256a643c263611a6f |
| x11_endpoint.py | 39c55059287e3ea1b8b607b619f7bda623ca5b5b1d31ab3f68318403e58fbd08 |
| preparation_policy.py — unverändert | 57aa07c533cf3c61be81dde36064d2de97cf3689eded71f27393ca7730541c83 |
| evidence/route-v2-normalized-delta.json | 518fd2bd51122291a024ad0a721e6bef6a7df559c920556324ea9f6fb1133456 |
| evidence/route-v2-test-receipt.json | 21213618409597b5bcd3c6e823304410a77f2776515692e69b34c59fadb949ed |

Das Manifest umfasst 48 Runtime-, 42 eigene Quell- und 72 Evidence-Pins. Source-/Evidence-Closure, tatsächliche Runtime-Abhängigkeiten und vorhandene Fixture-Preflightpins wurden geprüft. Der Repository-Commit enthält die öffentliche Dokumentation; die ausführbaren privaten Quellen werden durch diese Pins identifiziert.

## Nachgewiesene Regressionen

Die vollständige kleine Privatsuite bestand mit **149 Tests in 0,751 s**. Die Testquittung enthält den exakten Befehl, den Logpfad und dessen SHA-256. Es gab keine Kompilierung, keinen Spielprozess, kein XOpenDisplay und keinen tatsächlichen XTest-Request.

Die 11 neuen Tests führen reale action_step-, Endpoint.down- und X11Transport.event/look-Funktionen aus. Der Transport wird ohne Konstruktor angelegt; lediglich C-Zielfunktionen, Uhr und Guard-Latenz sind Speicherfakes. Die ersten 10 Tests erzeugten vor dem Fix 17 fachliche Fehler und einen Fehler wegen der noch fehlenden Submit-API. Der zusätzliche Zeitstempeltest zeigte anschließend separat RED→GREEN, dass Haltebudget und Emissionsbeleg genau denselben Requestbeginn verwenden.

Geprüft sind:

- Verzögerungen im letzten Endpoint-Prozessguard und im letzten Key-/Button-/Motion-Transport-/Fokusguard.
- Frische Zustandsprüfung nach allen solchen Guards.
- Abweisung alter Zustände, geänderter Route und erschöpfter Restbudgets vor Down/Motion.
- Tatsächliche Requestbeginn-/Rückkehrzeiten, getrennt vom späteren XSync-Ende.
- XTest-Ablehnung oder unklare Ausnahme ohne zusätzlichen Request.
- Freigabe auch nach erst während einer bereits begonnenen Anfrage abgelaufener Frist; kein erneuter Policycallback bei Up.

Die korrigierte Reproduktion ist als evidence/route-v2-corrected-reproduction.json erhalten. Beim 0,30-s-Guard beträgt der Abstand zwischen letzter abgeschlossener Policyprüfung und tatsächlichem Requestbeginn im kontrollierten Speicherfall jetzt 0. Im Fristfall wird der finale Callback erst bei 85,8 s erreicht und weist ab: **0 Down-Requests**, keine gehaltene Taste. Dies ist ein gezielter Kontrollflussnachweis und keine Behauptung einer atomaren Zustands-/Inputgarantie gegenüber Betriebssystem-Scheduling oder einer Spieleingabewirkung.

## Tatsächlicher Dateidelta und Erhaltung

Nur run_dual.action_step und Endpoint.down / X11Transport.look / X11Transport.event ändern Verhalten. Zwei Unit-/Evidence-Labels unterscheiden spätere V2-Läufe. Zwei bestehende Speicherfixtures übernehmen lediglich die Submit-Signatur; ihre bisherigen Assertions bleiben erhalten. Die Diffs liegen getrennt unter evidence/route-v2-*.diff.

Der gesamte Controller lässt sich durch Rücknahme der action_step-Änderung und der zwei Labels exakt auf V1 normalisieren. Dasselbe gilt für x11_endpoint.py nach Rücknahme der drei genannten Methoden. 32 gemeinsame Controllerfunktionen sind AST-identisch; die neue innere Submit-Funktion ist ausdrücklich dokumentiert. 19 der 21 eigenen Runtime-Dateien sind bytegleich zu V1; geändert sind nur run_dual.py und x11_endpoint.py. Die 27 externen Runtime-Pins bleiben unverändert.

Alle **98 Dateien des V1-Pakets** und alle **82 Dateien des früheren V3-Pakets** sind an ihren bisherigen Orten unverändert. Das ist eine Erhaltungszusage für die alten Pakete, keine Behauptung, dass die neue x11_endpoint.py noch bytegleich sei. Die frühere pauschale Transport-Bytegleichheit beschreibt V2 ausdrücklich nicht mehr. Preparation-Policy, RD, Route, Reader, Host-/Welt-/Identitätsregeln, Close-/Restore-Funktionen sowie die Release-Methoden bleiben unverändert.

## Unveränderter Umfang und Übergabe

Es gelten weiterhin die gemeinsamen 85/90 s, Route 45 s, Flug 8 s, Waffenwahl 3 s, insgesamt 48 Actions und die vorhandenen Frische-/Read-Retry-/Overrun-Grenzen. Es gibt keine Grenzwerterhöhung, keinen Inputretry, keinen neuen Hook und keine Erweiterung des Route-/Fire-Experiments. qualified, input_once_proven, actual_shot_proven, foreign_hit_proven und first_processed_state_proven bleiben false.

Der Reviewinput ist unverändert referenziert: /srv/tse-a1-route-review-names-worker-20261112/REVIEW.md, SHA-256 04166f76e5ec53e1c7084a646b88178e8068437488f4be97c2d1e27a3447f6d8. Seine Reproduktion und die korrigierten Ergebnisse sind im neuen Paket getrennt erhalten.

Root lässt diesen exakt eingefrorenen V2-Stand erneut unabhängig prüfen. Erst danach besitzt Root die Freigabeentscheidung, erstellt eine eigene Gate-/Pfadkopie mit aktualisierten Selfpins und führt gegebenenfalls das exklusive native Fenster aus. Das Autorenpaket bleibt deaktiviert, und dieser Follow-up behauptet keine native A1-Abnahme.
