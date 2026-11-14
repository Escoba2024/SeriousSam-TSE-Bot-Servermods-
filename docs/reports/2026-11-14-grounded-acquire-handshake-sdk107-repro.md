# GroundedReplan: reproduzierter Acquire-Handshakefehler

**SDK107-Reproducer: 3274 Checks, 2 RED; kein Produktionsfix.** Der unveränderte
Parent bestand zuvor 3223 Checks. Beide neuen Fehler betreffen denselben engen
Handshake nach einem ausgefallenen regulären Scan. Die realen Produktionskörper
wurden durch den bestehenden Harness kompiliert und ausgeführt; kein Algorithmus
wurde nachgebaut. Kein DLL-Build, Spielprozess oder Nativefenster gestartet.

## Sequenz und genaue Guardursache

Neue Fixtures `groundedAcquireHandshakeFixture` und
`groundedAcquireHandshakeReproduction` in `test_cecil_native_bridge.py` verwenden
Originalslots 69/71 mit hohen Positionen, Radien, Flags und ihren Original-Links.
Ein gültiger bisheriger Waffenzielversuch 71/Item311 mit Deadline12 ist als
Retained-Kontext vorgegeben. Die vollständige anfängliche Itemwahl wird damit
nicht behauptet. Tatsächliches `BotCecilChooseGoal` findet oben Anker69;
`BotSupplyTick` bildet während FALL die echte Navigator-Kante69→71.

Nach dem zweiten Tick landet die Fixture unten in STAND auf gültigem
WorldBase-Support bei Geschwindigkeit0. **Kein Anker wird nach Landung gesetzt.**
Die echte Scanplanung führt ChooseGoal bei22/42 aus; der unveränderte
Zweisekunden-Hold endet bei43. Bodenpunkte0/1 samt Verbindungen sind dieselbe
synthetische Supportroute der bestehenden positiven Fixture, keine vollständige
Rekonstruktion der Nativekarte. Auch die Bodenpose stammt aus dieser älteren
Fixture; sie wird nicht als exakte Pose des neuen Diagnostics1-Lebens ausgegeben.

| Bedingung | Anker nach Scan42 | Frisches Nearest am Hold | Replan / Ziel |
|---|---:|---:|---|
| Budget16, freie Sicht | 0 | 0 | 1 / 311 bleibt |
| Budget2 nur bei Scans22/42 | 69 | 0 | 0 / unreachable_hold: RED |
| Sicht nur bei Scans22/42 blockiert | 69 | 0 | 0 / unreachable_hold: RED |
| Sicht dauerhaft blockiert | 69 | −1 | 0 / korrektes Veto |
| Kein WorldBase-Support | 0 | 0 | 0 / korrektes Veto |
| Kontaktgeschwindigkeit0,101 | 0 | 0 | 0 / korrektes Veto |

In beiden RED-Fällen erhält `BotCecilChooseGoal` beim Scan keinen Nearestwert
und behält wegen `HasCommittedEdge` den hohen Anker69 (Produktionszeilen813–817).
Am Tick43 ist das normale Budget wieder16 und der aktuelle Cast frei.
`BotCecilGroundedReplan` führt selbst einen frischen Cast exakt zu Bodenpunkt0
aus: ein Cast, Restbudget15. Kandidat0 ist frei, vom hohen Source/Hop verschieden
und besitzt einen durch echte separate `CecilNavSearch` belegten gerichteten
Suffix zum unveränderten Ziel71. Trotzdem scheitert der Helper an
`candidate != s.anchor` in `BotSupplyNative.h:1254`.

Der nachfolgende tatsächliche Holdpfad beendet deshalb Item311 als
`unreachable_hold`. Die positive Kontrolle mit erfolgreichen Scans replante
stattdessen regulär, behielt `goalSince=0`/`goalDeadline=12` und löschte den
aktuellen Nav-/Floorstempel. Fehlende aktuelle Sicht, Support oder ruhiger Kontakt
bleiben Vetos. Radien, Locks, Budgets, Holdzeit und Deadline wurden nicht geändert.

Vor dem finalen Tick gibt es pro Fixture einen ausdrücklich diagnostischen
Aufruf des echten `BotSupplyNearest`; er verändert keinen Anker. Danach wird
das normale Tickbudget16 gesetzt. Das aktuelle Tick43-Endpoint/Castzähler-
Ergebnis belegt zusätzlich, dass der Helper dieselbe Messung selbst ausführt.
Das ist reine Fixtureinstrumentierung; keine zusätzliche Produktionsabfrage
oder vergrößerte Produktionsbudgetfreigabe wurde eingeführt.

## Grenzen der Diagnose

Das portable RED belegt einen möglichen falschen Abbruch bei veraltetem
Acquire-Hint und inzwischen frischem, sonst gültigem Bodenhint. Es beweist
**nicht**, dass dieser Guard das konkrete Diagnostics1-Leben verursachte:
Dessen Support-/Geschwindigkeits-/Raybudget-/LOS-/Nearestwerte sind unbekannt.
Die alten Diagnostics0-Leben werden ebenfalls nicht nachträglich erklärt.
Keine tatsächliche Waffenaufnahme, Verbesserung oder A4-Abnahme wird behauptet.

Die bestehende `groundedReplanFixture/groundedReplanGuards` bleibt bytegleich
im Testkörper erhalten. Sie setzt ihren Bodenanker ausdrücklich vorab und
bestand weiter; genau die fehlende Acquire-Handshakephase wird jetzt separat
geprüft. Alle 3223 bisherigen Checks blieben bestanden. Kein ASanlauf für
diesen reinen Diagnoseauftrag; keine breite neue Testschleife.

## Reproduktion und Handoff

Basis `55886edfe5c4178d6e39e6f53e1f27200756fcea`, eigener Worktree
`/srv/tse-a4-grounded-acquire-handshake-repro-20261114`.

```sh
nice -n 15 python3 -B poc/candidates/redstation-supply-20261107/test_cecil_native_bridge.py --sdk-player /srv/tse-sdk-20261021/Sources/EntitiesMP/Player.es
```

Erster neuer Reprostand: 3260/2; nach zusätzlichen Stage-/Suffix-/Endpointchecks
abschließend3274/2, jeweils Exit1 wegen ausschließlich der zwei genannten REDs.
Es liefen keine parallelen Compiler. Private Parent-/RED-Logs und strukturierte
Quittung: `.codex/evidence/grounded-acquire/`, Quittung-SHA256
`0dd789aaab30816c99217447b3ae6a794c5b8a51c9b0252dc15f178637ab4ae8`.

Produktionsheader bytegleich zur Basis:
`BotSupplyNative.h` SHA256 `f070a62ac096c01203d6c28ebc621d591c0489346aabadfb628fae0bb685b1af`.
Auch `BotCecilItems.h`, `cecil_motion.h` und `cecil_rules.h` unverändert.
Neuer Test-SHA256 `ce701637fbd110a650399bd2d16feacc0ffda4e812d970302fdd60fcd0ee20bf`.
Root entscheidet nach Review über einen getrennten Fix; diese Änderung endet
bewusst beim nachvollziehbaren RED. Alle eigenen Jobs sind beendet.
