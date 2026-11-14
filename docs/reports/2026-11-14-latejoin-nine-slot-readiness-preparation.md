# Spätjoin: vollständige Originaltabelle abwarten, Rohreads erhalten

Nur Offline-Diagnose/TDD/Vorbereitung ab`2d0899a`; Plan vor Code:
`f6db761`,[Neun-Slot-Vertrag](../superpowers/plans/2026-11-14-latejoin-nine-slot-readiness.md).
Keine Runtime, Displays, Frida, Inputs, Netz/Capture, Builds oder Delegation.

## Geschlossener tatsächlicher Fehler

Archiv`/srv/tse-milestone-a-evidence-20261111/own-latejoin018-root-20261114-173005`,
Result-SHA`b44bab627e5cebbfa325a6fb9d6808a36f041c70d6534f7a9e0235d30b9e0a14`:
FAIL`exact native global slots`; Capture meldet anschließend fehlende
Originaladmission. Vier normale Closes/640Dateien+4Closedlogs-RestorePASS
sind separate Rootbelege. Alter FAIL und alle Dateien bleiben unverändert.

| Rawframe | Tatsächliche erste/zweite Beobachtung | SHA256 |
|---|---|---|
|13server/14A/15B|jeweils0..8, Tick23,099934/23,149933/23,199932|vollständige einzelne Rawquittungen im Archiv|
|16Original|beide0..7, Tick22,649940|`dbbb920eb8bda8bf76c51a6bb18d377380187cf1ac75b7f50cb5ce446d398bd1`|
|20Original|beide0..8, Tick23,199932|`3a43104f511e8c291ed3a52c13062fc3e20b0689df2908408a8b85f30efdc892`|

Query9/echte vierte Endpointbindung beweisen keinen bereits vollständigen
Original-Simulationsstand. Die unveränderte Frameprüfung hat korrekt
abgelehnt. Das Archiv enthält nur eine vollständige Originalrunde; eine
zweite progressive volle Runde wird nicht rückwirkend erfunden.

Der alte Kontrollfluss erreichte die abschließende Frameprüfung nach den
localSource-/beiden Slot8-Inventarreads und deren vorherigen Assertions.
Diese Beobachtungen wurden jedoch nur im späten Erfolgsresultat gespeichert;
das Archiv enthält lediglich die Endpointquittung. Deshalb sind ihre
tatsächlichen Rawwerte **nicht nachträglich rekonstruierbar** und daraus
folgt keine abgeschlossene native ABIqualifikation.

## Enge Änderung

Einziger geänderter vorhandener Runtimequellpfad:
`tools/ownns_latejoin_runtime.py`, ausschließlich Admission und neue
`admission_frames`. Builder prüft AST-Gleichheit aller übrigen Körper,
einschließlich private_prestart, native_frame, Launcher,20s-Readiness und
Host-/Cleanupkopplung. preflight.validate_frames bleibt byteidentisch.

Der neue Loop hält die bestehenden native_frame-Readpaare/Rawquittungen und
0,2s-Rundenabstände. Er akzeptiert als **NotReady**, nicht als Admission,
allein das anfängliche Fehlen von Originalslot8. Sein Auftauchen zwischen
beiden Rawreads macht diese Runde ebenfalls noch nicht vollständig.
Vorhandene0..7-Pointer sind pro alter Rolle an die letzte eigene
Prestartbeobachtung gebunden; Original0..7 wird bei erster tatsächlicher
Beobachtung festgehalten. Jeder bereits gesehene8-Pointer bleibt ebenfalls
gebunden. Slotverlust/-wechsel, PID/Module/Session-/Endpointabweichung und
rückläufige Clock scheitern sofort. Dies sind vorhandene Slot-/Entitypointer-
Belege; kein neu erfundenes Entity-ID- oder atomarer Snapshotnachweis.

Erst zwei aufeinanderfolgende vollständige Neunerrunden mit pro Rolle
fortschreitender nativer Clock gehen in die unveränderte range(9)-Frameprüfung.
Gleiche Clock liefert keinen Fortschrittsbeleg. Alle NotReady-/Fehlframes
bleiben privat erhalten. Capturestart+30s wird vor/nach den Runden/Reads
weiter geprüft; keine neue Frist, Launchwiederholung oder Gameplayeingabe.

Erfolgreiche localSource-/Inventarreads werden sofort **vor** Folgeassertions
O_EXCL/0600 geschrieben. Der gesamte Admissionpfad hat jetzt eine private
Fehlquittung, auch bei später Frame-/Bindingprüfung: vorhandene Ergebnisse,
Readinessmetadaten, Rawframe-Seriennummern und Originalfehler bleiben erhalten.
Die neuen Dateien heißen`private-original-local-source-sample.json`,
`private-original-slot8-{server,vanilla}-inventory.json` und bei Fehler
`private-original-slot8-failure.json`. Flags bleiben unqualifiziert.

## TDD und Regressionsgrenze

- Erste7neue Tests: RED mit15erwarteten Assertionsfehlern wegen fehlender
  Readinessmethode/fehlender Sofortquittung; danach GREEN.
- 12neue Admissionfälle decken8→9→9, dauerhaft8, gefrorene/reverse Clock,
  PID/Hash/Session/altePointer/fremdeSlots,8-Verlust/Pointerwechsel,
  Endpointwechsel,8-Auftauchen zwischen Rawreads, keine Query-/Launchinferenz
  und vollständige0600-Fehlerquittung ab.
- 3neue Builderfälle zunächst RED wegen fehlendem Builder, danach GREEN.
  Ein zusätzlicher Assertion-RED zeigte, dass eine alte HANDOFF-disabled-
  Sourcepinmenge nicht unbemerkt verloren gehen darf; korrigiert, alle alten
  Sourcepinnamen erhalten. Der erste unbenutzte Entwurf bleibt separat.
- Final aus`tools/`:

```text
python3 -m unittest test_latejoin_nine_ready test_prepare_latejoin_nine_ready test_ownns_latejoin_runtime test_ownns_latejoin_preflight test_owned_latejoin_capture test_ownns_latejoin_local_mapping test_ownns_latejoin_readiness test_prepare_owned_latejoin test_a4_ordered_memory_v3
Ran 95 tests in 0.522s — OK, keine Skips
```

Das sind15neue+56vorhandene Latejoin-+24V3-Fälle. IO und Clock sind in den
neuen Tests ausschließlich modelliert; kein tatsächlicher Native-Retest.

## Finales deaktiviertes Paket

`/srv/tse-owned-sync018-latejoin-nine-ready-final-disabled-20261114`
Manifest-SHA`c068c51086d1048ff992dac79d9224bea8d9352eb160ea13a6c0eab7df1a1f16`.
74Runtime/79Source/56Pythonpins frisch nachgeprüft, alle alten Sourcepinnamen
erhalten. Vier Runtimegates False. qualified/functional_pass/a4_accepted/
runtime_performed False. Gegenüber Autorenparent0d6b1660… ändert Runtime
lediglich den Adapter sowie eigene Service-/Evidencepräfixe im Launcher;
übrige Runtimebytes bleiben gleich. Voller Diff:`nine-ready-runtime.diff`.

Neuer Offlinebuilder, ausschließlich frisches Ziel:

```text
python3 tools/prepare_latejoin_nine_ready.py --destination /srv/NEW-disabled-latejoin-package
```

Der vorher erzeugte unbenutzte Entwurf
`/srv/tse-owned-sync018-latejoin-nine-ready-disabled-20261114` mit Manifest
452b4a0c… ist **nicht** der finale Stand. Alte Eltern/freezes und173005-FAIL
bleiben unverändert. Root muss unabhängig prüfen und eine neue konsistente
Gate-/Namespace-/Pin-Ableitung einfrieren. Kein automatischer Retest.
Native Admission, neuer Originalreader,600s Sync, Navigation/A/B/Flotten-
Qualifikation bleiben offen; erfolgreiche Modellfälle sind kein Ersatz.
