# A1: deaktivierter XRes-/RECORD-Lifecycleadapter

Nur Offlinevorbereitung. Keine Displays, Xlib-/TSE-/Wine-/Frida-Aufrufe oder
Inputs durch diesen Agenten. Keine A1-Abnahme, kein Gainfix, keine Zuordnung
historischer Verbindung U. Root integriert, prüft, friert ein und führt später
höchstens den vorgesehenen einzelnen eigenen Methodenfall aus.

Quellencheckpoint `edb8a2d`, enger Scope-/Qualifikationsfolgefix `cd31b3e`.
Neue Dateien ausschließlich im isolierten Worktree
`/srv/tse-a1-xres-lifecycle-adapter-20261114`; frühere Pakete bleiben unverändert.
Der eigene167-Methodencontroller und beide Builder sind neue Dateien. Keine
bestehenden gemeinsamen Core-/Runtimequellen verändert.

## Quellen und Grenzen

A1-Parent `/srv/tse-a1-xtest-preparation-root-frozen-20261114`, Manifest
`71b9c896e068e473d0fd8317871b0fa3ccc5f4a43828c87e8b1b09619c60170a`.
Qualifizierter öffentlicher XRes-Parent
`/srv/tse-own-xres-pid-v2-root-frozen-20261114`, Manifest
`09be57b6b0eec29a598b68a612376ebdb4939857b7fbc69342ecbdb2e924f687`;
echtes begrenztes PIDmethodenergebnis
`18d16f195c64d2d5f6564b0166422d63aa72011c4dcd71284f05d1d9a1afc953`.
Alle vorhandenen Runtime-/Source-/Library-/Header-/Evidencepins wurden vor den
Kopien frisch geprüft. Die ursprüngliche Metadatenqualifikation81c402 und die
XTest-Metadatenvorbereitung bleiben erhalten.

Explizite neue Recorderableitung setzt nur die beiden Lifecycleflags auf frischen
Ranges. Der enge kopierte Armkörper liest Snapshot1 nach StartOfData. Snapshot2
liegt vor unverändertem Core-Disable/Enddrain; A1 kennt keinen capture_final-RPC.
Manifest und Config erzwingen getrennt A1/154 oder eigene Methode/167.
Genau2Snapshots, maximal32positive Kontextbasen+2bestehende Ressourcen, höchstens
34PIDqueries/Snapshot und64QueryClients; Status0/PIDmask2/Länge4/PID>0 strikt.
Alle4Coredateien sind zum tatsächlichen Parent bytegleich. Keine Coreglobals,
zusätzlichen Input-/ACKabfragen oder CP-/Gain-/EPS-/FPS-/Fristenänderungen.

Vollständiger unveränderter Coredecoder replayt jede Rawrow. Beide Metadaten-
Snapshots müssen innerhalb derselben Recorder-Monotonic-/Start-End-Grenzen liegen;
es gibt keine Fusion mit XServer-/JS-/Gameclocks. Jede Start-/Died-Grenze macht
die betroffene Base für positive Intervallzuordnung UNKNOWN. Eine abweichende
PID/TID wird nicht dem Original zugeschlagen. Falsche explizite Fenster-/GC-
Ressourcenbesitzer bleiben harte Fehler. Snapshot-only-Fallback fehlt bewusst.

Zwei erfolgreiche Snapshots allein belegen keinen Requestowner. Der neue
Qualifikationsguard verlangt zusätzlich driver_requests_bound=True. Der eigene
Methodenfall prüft genau einen lesenden Driver-QueryPointer: echte Window-ID,
Requestsequence, jeweils genau einen tatsächlichen Request/Reply, Callbackordnung
und native Antwortwerte. Wiederverwendet wird der qualifizierte unveränderte
Core.Native.query-Körper; nur neue öffentliche Bindungen im method-only Kind.
Es gibt dort keine Input-/Warp-/TSE-/Wine-/Frida-Operation. Der separate Peer
startet und geht normal während der Aufnahme; seine Base bleibt UNKNOWN, auch
wenn Snapshot2 die richtige PID liefert. Beide Driververbindungen bleiben bis
nach EndOfData offen. Dies beweist keine erzwungene Base-Reuse und keine
lückenlose Lebenszeit außerhalb der tatsächlich beobachteten Aufnahme.

Jede Aufnahme reserviert einen begrenzten Versuch. Metadaten-/capture_final-
Fehler bleiben sticky und verhindern dritten Snapshot, lassen jedoch Corecleanup
und alle normalen eigenen Rolecloses weiterlaufen. Erfolgreiche und abgelehnte
Rohmetadaten liegen in eigener Sidecar0600/O_EXCL≤262144Byte, Stop-/Nativeclose-
Quittungen tragen nur Hash/Länge/Pfad und kompakte Zähler. IPC bleibt16384Byte,
Recorder15s, Arm3s/Stop3s; eigene Methode30s+höchstens5sCleanup pro Kind. Die
vier Coredateien und qualifizierten XRes-Helfer werden unverändert kopiert; deren
Native-Bindungen bleiben gesonderte qualifizierte Abhängigkeiten. Neue ausführende
Adapter-/Worker-/Methodengates und die jeweiligen Manifeste bleiben False.

## Tatsächliche Offlinebelege

58 gezielte Fälle PASS/0Skips/3,839s: neue Adapter/Evidence/Fake-C/Scope/Methoden-
und Builderfälle,8OwnChild-Fälle,12Attempt-/Release-Regressionsfälle und5XTest-
Vorbereitungsfälle. Keine Native-Xlib-Tests. Insbesondere:

- Null-Request-Modell lieferte zuerst echten falschen Methoden-PASS; RED,
  danach expliziter tatsächlicher Request-/Replybeleg und negativer Mutationsfall.
- Eigener Scopeguard fehlte zuerst (RED); jetzt früh vor Native und in den
  qualifizierten Quellenfingerprints enthalten.
- capture_final-RPCfail-Modell: genau1Versuch, alle4Cleanupaufrufe; Recorder vor
  Driverclose, kein versteckter Retry. Fake-C-Fehlerpfade geben erhaltene Arrays
  frei; sticky Metadatenfehler überspringen Core-Disable/Enddrain nicht.
- Builder prüfen Parentpins, unveränderte Corebytes, identische Workerfingerprints
  beider Pakete, unveränderten action_step-/native_rotation_pair-Körper,
  unverändertes Hostbudget und fehlende echte Methodenqualifikation im A1-Fork.

Private Logs liegen in `/srv/tse-a1-xres-lifecycle-evidence-20261114/`:

| Log | SHA256 | Ergebnis |
| --- | --- | --- |
| red-method-positive-request-and-scope.log | 7b156425b223355b91b11eeb4b9d939a1da2d6d131aed9499419b8512a0471e6 | tatsächlicher RED |
| red-method-qualification-positive-evidence.log | 519e50e59f6327e4d050015e01a5391b751a3036e9e5738f54130c30f26792fa | tatsächlicher RED |
| red-method-actual-query-binding.log | 9d1279f6fcf8da85ba0368df031e3d540c2d1b8d60ef8d41449daf9fbd4ef682 | tatsächlicher RED |
| red-disabled-builders.log | 1b94c09d1a4d0c957323e44ac62e9f664abf47bbd75705e8ee16487978fd245a | fehlende neue Builder |
| green-builders-first.log | 17dfaa9cccec8369d257fe1b507e810bfada0acdeb37e329da8d64cf51a90f8c | FAIL: Test suchte verschachtelte Funktion nur top-level |
| green-builders-corrected-test-lookup.log | 37c1097bf242d9feb9cb5408976444c81e2c2bf624ea3b8db70100ac5d996975 | 2PASS nach Test-Lookupkorrektur |
| green-final-focused.log | 3b562ba42678761471391b32b07be3f49cf31c3e7c70efcb184b1618111c6eb6 | 58PASS |

```sh
cd /srv/tse-a1-xres-lifecycle-adapter-20261114/tools
python3 -B -m unittest test_a1_xres_attribution test_a1_xres_attribution_worker test_a1_xres_attribution_evidence test_a1_xres_lifecycle_method test_prepare_a1_xres_lifecycle test_xrecord_core_process test_a1_passive_attempt_journal.Attempts test_a1_xtest_preparation.Preparation -v
```

## Deaktivierte Pakete / nächster ausführbarer Schritt

Eigene Methode `/srv/tse-own-xres-record-lifecycle-disabled-20261115`, Manifest
`9b45467eef4fff1151a19c11b1a7c0cc8f598136ad1548aff26e4347605dddb1`;
21Runtime-,4Library-,4Header-,13Evidencepins.

A1-Kopie `/srv/tse-a1-xres-lifecycle-disabled-20261115`, Manifest
`6633998b718567c38f2a55470a47d0218b728f2570a357b8a298f82ee145413d`;
103Runtime-,84Diagnose-,14Collectorpins. Echte neue Methodenqualifikation=None.
Beide Pakete enthalten dieselben tatsächlichen Workerfingerprints. Vollständige
private Paketquittung `final-disabled-package-receipt.json`, SHA256
`c2bba8466590a97008cb374fff2ee8060090bb185f00c526e5aea72bf0023867`.

Nach Rootreview, Sicherung, exklusiven Projekt-/167Locks und frischem
Display/PID/Namespace/8GiB-Preflight kann Root genau eine eigene Methodenkopie
einfrieren. Nur dort neue Methoden-/Workerflags und Manifest freigeben, Runtime-
Pins aktualisieren; keine ursprünglichen Pakete überschreiben. Vorgesehener
Befehl im noch deaktivierten Paket, erst nach dieser Rootableitung:

```sh
python3 -E -s -B /srv/tse-own-xres-record-lifecycle-disabled-20261115/a1_xres_lifecycle_method.py --directory /srv/tse-cecil-rollout-evidence-20261114/own-xres-record-lifecycle-method-NEW
```

Erst ein tatsächlicher erfolgreicher begrenzter Methodenfall mit passenden
Fingerprints darf die A1-Builderoption `--qualification` versorgen. Der Builder
verlangt reale geschlossene Rollen, Lifecycle, Requestownerbeleg und Sourcepins;
er erstellt auch dann ausschließlich ein deaktiviertes neues A1-Paket. Ein
darauffolgender Retaildiagnoselauf benötigt erneut Rootfreeze/Preflight und bleibt
NoFire. AlteU, historischeGain-/A1-FAILs und offene Gesamtziele bleiben unverändert.
