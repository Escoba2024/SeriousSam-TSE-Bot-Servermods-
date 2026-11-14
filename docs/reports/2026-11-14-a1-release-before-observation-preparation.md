# A1: Freigabe vor verspäteter weiterer Beobachtung

**Deaktiviert, offline vorbereitet; unabhängiger Review und native Prüfung offen.**
Plan `58790d2`, getrennte Branch `codex/20261114-a1-release-before-observation`.
Der reale Lauf141819 und alle früheren Fehlläufe bleiben FAIL.

Das neue Paket `/srv/tse-a1-release-deadline-final-disabled-20261114` stammt
vollständig vom Root-Parent `/srv/tse-a1-exact-coverage-root-frozen-20261114`,
Manifest `6534c8b447418f4a2a5310160ff0672b3b41aa742cbc3eb9389bfb648fef919a`.
Der Zwischenentwurf `/srv/tse-a1-release-deadline-disabled-20261114` wurde
unbenutzt erhalten; allein das Paket mit `final-disabled` ist Reviewinput.

| Finales Artefakt | SHA256 |
|---|---|
| source-manifest.json | `3b140fdc395db64082303719dc60473af71aa196b1c01558f0e618d69ba23043` |
| collector/source-manifest.json | `7f7c1db5aa11e868451ad1875bd2f86c5aa5572f0ab61be695b8fb2741bc97f0` |
| run_dual.py | `da9ec49d65d00a49c91f890394f65e34068ecaed175e4120efeb70e96a5e15eb` |

70 Runtime-, 61 Diagnosequell- und 14 Collector-Pins wurden frisch geprüft.
Alle drei Codegates und beide Manifestgates sind false. Geschützte externe
Pins, Originalmodule, Hostbudget, Controls, Mapping- und Originalbytequittung,
Worker-/Collectorcode, JS-Hooks, TTL, ACK, Gain und sämtliche CP-Eingaben
bleiben erhalten. Der Worker ändert nur sein false-Gate, der Collector
false-Gate und seinen eigenen privaten Paketpfad.

Die einzige Verhaltensänderung liegt in `action_step`: geplantes Ende vor
den Held-Guards und nach deren unveränderten Prüfungen beachten. Ist das Ende
erreicht, folgt der bestehende Capture-/`before_release`-/finally-Releasepfad
ohne weiteren verspäteten Observer. Die Post-observe-Prüfung bleibt bestehen.
Harte Grenze weiterhin exakt `seconds+.25`; keine EPS-/Friständerung.
`timing.held_observations` zählt tatsächlich begonnene Held-observe-Aufrufe,
einschließlich eines später fehlgeschlagenen Aufrufs. Null bleibt null.

CP und sein erfolgreicher After-Input-Observer sind bytegleich. Nach echter
Freigabe muss der bestehende Ablauf weiterhin seine fälligen periodischen
Checks und tatsächlichen ACK-/Body-/Gainbedingungen erfüllen. Ein Emissions-
oder Releasebeleg ersetzt keine dieser Bedingungen. Ein noch rechtzeitig
begonnener Observer, Guard, Capture oder Release über 350 ms bleibt FAIL.

## Tatsächliche Offlineprüfungen

- Neue echte Actionloop vor Transformation: 15 Fälle, 1 FAIL und 3 Errors
  wegen verspäteter Beobachtung beziehungsweise fehlendem Zähler. Derselbe
  Loop nach enger Transformation 15/15 PASS; später zwei unveränderte
  RouteFlight-Abbruchfälle ergänzt. Mit drei Paketfällen final **20/20 PASS**.
- Paketbuilder separat zuerst fachliches RED wegen fehlender Ableitung,
  danach GREEN. Kein Spiel-/Display-/Frida-/Compilerstart.
- Historische unveränderte `test_action_timing`, `test_post_observation_clock`,
  `test_runtime_steps`, `test_request_boundary` gegen den neuen Runner:
  **27/27 PASS**. Echte Endpoint-/Transportfunktionen, ausschließlich
  Speicherersatz für Uhr/C-Ziele; keine native XTest-Anfrage.
- Weitere fünf passende NoFire-CP-Fälle, Worker-/Scope-/Quittungs- und
  Mappingbackendfälle ergeben mit diesen 27 insgesamt **49/49 PASS**.
  Die kleinen Python-Worker-Testkinder wurden geordnet beendet/reaped.
- Zusätzlich ausgeführt und **unverändert fehlgeschlagen**:
  `test_a1_trace_preparation.NoFirePreparationTests.test_all_protected_nested_read_start_close_and_restore_functions_are_exact`,
  Subtest `own_identity`. Dieser historische Test vergleicht gegen den
  älteren NoSmooth-Parent vor der bereits integrierten Mapping-Fehlerquittung.
  Die Assertion wurde nicht verändert oder grün umetikettiert. Der neue
  Pakettest beweist stattdessen alle verschachtelten Controllerfunktionen
  gegen den unmittelbar gepinnten6534c8b4-Parent AST-identisch.

Die 20 neuen und 49 passenden geerbten Fälle sind 69 unterschiedliche
gezielte Fälle. Kein breiter Repositorytestlauf war im gemeinsam genutzten
Ressourcenfenster beauftragt. Der historische Vergleichs-FAIL bleibt separat
sichtbar. Hashes der vollständigen privaten Testlogs stehen in
`2026-11-14-a1-release-deadline-offline-tests.json` neben diesem Bericht.

Die Prüfungen umfassen den aufgezeichneten frühen Read bis69,365668 ms und
den folgenden Guardabschluss bei144,422824 ms: der 208-ms-Observer wird dann
nicht mehr begonnen. Null Heldbeobachtungen, normale schnelle Beobachtung,
102-Iterationsgrenze, strikte350-ms-Fehler, ungültige Uhr, Capture-/Guard-/
Press-/Releasefehler und garantierter Releaseversuch werden explizit geprüft.

## Reproduktion und Root-Handoff

Im Worktree:

```sh
cd /srv/tse-a1-release-before-observation-20261114/tools
python3 -m unittest test_a1_release_before_observation test_prepare_a1_release_before_observation -v
python3 prepare_a1_release_before_observation.py --destination /ABSOLUTER/FRISCHER/PRIVATER/PFAD
```

Der Generator lehnt bereits vorhandene Zielpfade sowie falsche Parent-
Manifeste, Runtime-/Quell-/Collector-Pins und unpassende Runnerbytes ab.
Der vollständige Controllerdiff liegt im Paket als
`release-before-observation.diff`. Außer action_step ändern sich im Runner
nur false-Gate und eigene Dienst-/Evidence-Bezeichner; alle anderen äußeren
Funktionen und sämtliche verschachtelten Main-Funktionen sind geschützt.

Root prüft und integriert allein, erstellt gegebenenfalls eine neue eigene
Gate-/Namespace-/Pfadkopie mit vollständigen Selfpins und frischem Preflight.
Erst dann ist genau ein unverändertes Original-NoFire-Fenster vorgesehen.
Keine automatische Wiederholung, kein Route-/Fire-/Schadenslauf und keine
A1-, A3- oder Flottenqualifikation wird aus diesen Offlinefällen abgeleitet.
