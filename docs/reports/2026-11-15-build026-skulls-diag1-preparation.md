# Build026: deaktivierter Skulls600-Diagnosefall

Die reine Offlinevorbereitung ist abgeschlossen. Ein frischer, deaktivierter
Fall verwendet Build026 auf Skulls mit Hard2, acht DEMON3-Bots, unverändertem
Original20FPS und 600 Sekunden, Diagnostics1. Kein Lauf, Freeze, DLL-Build oder
Livewechsel wurde durch diesen Auftrag ausgeführt. Die bisherige Skulls-Lücke
bleibt offen; die neue Reacquireausgabe soll ihre Ursache eingrenzen.

## Herkunft und Paket

Parent `/srv/tse-nav20-024-skulls600-disabled-20261115`, Manifest
`9254b47fddb163bfc476df1198cab090c0c814bf16f59154d390919189389f0e`,
bleibt unverändert. Neuer Fork:
`/srv/tse-nav20-026-skulls600-diag1-disabled-20261115`.

| Beleg | SHA256 |
| --- | --- |
| Neues Paketmanifest | `cdb5b9584351b21d552f5e82a171d91fc6ef805eae0047b769ff61e10840b745` |
| Neuer Controller | `8efcdef9660024fe678254fb9c523d72efdd9dbfe30bc0a37df3cc93440c3185` |
| Tatsächliches Build026-Manifest | `be0513a059e2dcf5bda364ea70c4f2dee800fb084d2c44861912eaa22e186fd3` |
| Tatsächliche DLL, 443392 Bytes | `2c9a238191b9642bf7f9613f01a461cf711f97fe62e581bdd7c93b5f58a9bcdd` |

Buildquelle `05e1708abc8b886895157b57a28e35d7375c4f29`, Tree
`1f96c7a6d439f9f894de0dca214d56a846ddc5c5`. Alle47 Sources,
28 Overlays, Manifest und DLL sind frisch gegen die tatsächlichen Builddateien
geprüft. Alle77 aktiven Build024-Targets wurden entfernt und genau77 Build026-
Targets eingebunden. Die vollständigen beiden Listen stehen in der privaten
Quittung; ursprüngliche024-Metadaten bleiben ausdrücklich Herkunft.

World `Levels\LevelsMP\Deathmatch\WeGotSkullsNBonesToo.wld` und Nav
`Scripts/Cecil/WeGotSkullsNBonesToo_9B573405.nav` bleiben gleich, mit CRCs
`42d03dd2` / `70b554dd`, 296 Navknoten. Keine Retaildateien werden veröffentlicht.

## Exakte Änderungen und Grenzen

Vier bestehende Paketdateien sind verändert und exakt auf die Parentbytes
invertierbar: `run-a4.py`, `adapter_policy.py`,
`navigation_comparison_policy.py`, `a4_hard_map_policy.py`. Die ersten drei
retargeten Kandidat, Namespace und feste Fallpolicy. Die vierte ändert nur das
vorhandene Diagnosticsliteral0 auf1 samt Fehlermeldung. Der tatsächliche
Hardmapoptionscall bleibt erhalten. Die ursprüngliche Drei-Datei-Annahme
scheiterte im echten extrahierten Optionsbody mit `Hard map: fixed diagnostics0`;
dieser RED bleibt archiviert. Root autorisierte die vierte Byteinverse.

Alle übrigen77 Parent-Sourcedateien sind bytegleich. Neu sind der schmale
Builder, die feste Optionspolicy und gezielte Tests. Keine Änderung an
Botlogik, Readern, V3-/Life-/Pickup-/FIRE-Bindungen, OriginalCore, Konfiguration
außer Diagnostics1, Ressourcen-, Fehler-, Restore- oder Stopgrenzen. Keine
automatische Sequenz oder Wiederholung. Frisch geprüft:140 Runtime-,88 Source-
und51 Pythonpins. Sämtliche Runtimegates und Qualifikations-/Funktionsflags
sowie privaten Approvals bleibenFalse.

Der unveränderte reine `finalize_trial_evidence` akzeptiert `PASS_`-Statusnamen
und behält alle Fehler-/Cleanupvetos. Der neue technische Status lautet
`PASS_LIMITED_REACQUIRE_DIAGNOSTIC_OBSERVATION_ONLY`; er verändert weder
`verdict.accepted` noch die Beweisgrenze. Offlinefälle prüfen auch dessen
Ablehnung bei Fehlern, fehlenden und nicht geschlossenen Rollen.

`accepted_proposal` beweist keine Bewegung, finalen SafeMotion-Ausgang,
Radiusankunft oder Aufnahme. Nicht erreichte Felder und durch1Hz-Throttling
fehlende Entscheidungen bleiben UNKNOWN. Diagnostics1 erzeugt zusätzliche
Beobachtungskosten: dieser Fall ist kein gematchter Vergleich, keine
Ressourcenqualifikation und keine Skulls-/A4-Abnahme.

## Überprüfung und Wiederholung

Initial9/9 RED bei fehlendem Builder. Nach erstem GREEN wurde der zusätzliche
Hardmapfehler als echter RED festgehalten. Der abschließende gezielte Lauf
bestand11/11 Fälle in0,323 Sekunden. Er prüft falsche Kandidaten, Manifeste,
Closure, Pfade, Hashes, Map/Dauer/Diagnostics/Konfiguration, Mutationen und
mehrdeutige Transformationsanker sowie alle vier Inversen und die tatsächlichen
unveränderten Cohort-/Finalizerfunktionen. Kein Parent-Gesamtcompile erforderlich.

```sh
python3 -B -m unittest discover -s tools -p test_navigation_build026_skulls.py -v
python3 -B tools/prepare_navigation_build026_skulls.py --destination /srv/tse-nav20-026-skulls600-diag1-disabled-20261115
python3 -B .codex/evidence/build026-skulls/audit.py
```

Der Builder verlangt ein frisches Ziel; der bestehende Fork wird nicht
überschrieben. Der private Auditor protokolliert alle Dateilisten, Pinprüfungen
und Parent/New/Restored-SHAs der vier Inversen exklusiv. Vollquittung:
`.codex/evidence/build026-skulls/final-receipt.json`, SHA256
`dd08715588f65ac2a9a3c5097e73f40c286ebe3da1cf9a2d7b36b1b85b9e1665`.
Private Logs enthalten beide REDs und den finalen GREEN, ohne öffentliche Rohdaten.

Plan/Claim `c29fa934246c7a808b93135bea6e0e7953af905e`, RED-Tests
`ce7de6f64a55c8a96f7d2a8cfd0b27ff8008e6cb`, Umsetzung
`aa8471cc615260026137dce21273cb45ed4811d2`. Alle Jobs beendet. Root allein
integriert und reviewt die Policy, friert separat ein und startet gegebenenfalls
einen ausdrücklich begrenzten Diagnosefall; keine Promotion aus der Vorbereitung.
