# A1-XRes-Lifecycle: bestätigter Offline-Umsetzungsumfang

Root bestätigt den vollständigen Scope aus
`2026-11-14-a1-xres-record-attribution.md`: Lifecycleflags ausdrücklich aktiv,
kein Snapshot-only-Fallback, höchstens32positive Kontextbasen plus2bestehende
Resourcequeries je Snapshot, genau2Snapshots innerhalb Start/End. Kein Input-,
Gain-, FPS-, Toleranz-, Hook- oder Fristenwechsel.

Eigener Worktree `/srv/tse-a1-xres-lifecycle-adapter-20261114` ab Root1af4ab2.
Claim nur neue Adapter-/Evidence-/Builder-/Testdateien und eigener Bericht.
Alle vier Coredateien bleiben bytegleich; keine gemeinsamen Coreglobals ändern.
Root allein Native/Displays/Compiler/Live und Integration. Vor angekündigten
Rootfenstern sämtliche eigenen CPU-/Test-/Generatorjobs beenden.

## Enger Methodenvertrag vor Retail

Ein neuer deaktivierter eigener167-Fall erbt OwnChild/Displayguards/IPC/Normalclose
und den qualifizierten öffentlichen XRes-Getter. Kein TSE/Wine/Frida/Input.
Genau zwei feste Driververbindungen liefern bestehende eigene Fensterressourcen;
ein separat gestarteter normaler Peer liefert eine dritte bekannte Verbindung.

1. Eigenes frisches Display, Driver2Verbindungen, Recorder starten.
2. Recorder aktiviert feste Core-Ranges plus ClientStarted/Died; echtes
   StartOfData, dann Snapshot1 bei aktivierter Aufnahme.
3. Peer normal starten und genau eine ungemappte eigene Fensterresource erzeugen.
   Im ausschließlich eigenen167-Methodentreiber genau einen lesenden QueryPointer
   auf das eigene Driverfenster ausführen. Der unveränderte qualifizierte
   Core.Native.query-Körper liefert Window/Sequence/Antwort; vollständiger RECORD-
   Request und Reply müssen genau daran gebunden sein. Keine Eingabe, kein Warp,
   keine zusätzliche QueryPointer-Operation im A1-Programm.
4. Snapshot2 bei weiter aktiver Aufnahme, bevor der Peer regulär geht. Der
   Methodencontroller bindet dessen echte PID/Startgeneration/Namespace und die
   eigene Resource gegen die tatsächlich gelesene Base-/PIDantwort.
5. Peer regulär schließen; anschließend Recorder normal Stop/Disable/Enddrain.
   Vollständige Rohdaten müssen den zugehörigen Start und Tod enthalten. Kein
   Peerrejoin/erzwungener Base-Reuse/erneuter Methodenversuch.
6. Beide Snapshotqueries/Arrays vollständig frei; alle vier Kinder normal
   closed/reaped, Display abwesend. Eigene Start-/Died-Records, exakte Rangeunion,
   Quellen-/Methodenfingerprints und vollständige Drainquittung erhalten.

Ein methodenspezifischer Capture-final-Befehl darf nur mode=method/167 die zweite
bereits vorgesehene Snapshotoperation vor Peerleave auslösen. A1/154 kennt diesen
Befehl nicht: dort ausschließlich erste Aufnahme nach Arm und zweite im normalen
Stop vor Disable. Keine zusätzliche dritte Snapshotoperation.

Die normale Peer-Sitzung ist ein echter Lifecyclebeleg; fehlende tatsächliche
Base-Reuse bleibt unbewiesen. Der konservative Auditor verwirft jede betroffene
Base bei irgendeiner Start-/Died-Grenze im vollständigen Stream, auch bei gleicher
PID in beiden Snapshots. Ein alter und neuer Linux-PID/TID darf nicht heuristisch
dem Original gleichgesetzt werden. Alte U bleibt UNKNOWN.

## Umsetzung / TDD

- [x] Reine Attributionsregeln als zuerst fehlendes Modul RED protokolliert.
- [ ] Pure GREEN; echte serverbasierte0-Hintergrundrow, zweiSnapshots,
  Prozessgeneration/Namespace, strikte Queries/Freezähler, Raw-Replay und alle
  Lifecycle-/Drain-Negativfälle. Keine Clockfusion oder günstigen Randzuschnitte.
- [ ] Fake-C-/Lifecyclebounds vor Workerimplementation RED, danach GREEN.
- [ ] Explizite Recorderableitung: kopierter enger Armkörper mit nachvollziehbarer
  Rangefactory-/Metadatenabweichung; ursprünglicher Close im finally weiterwirksam.
- [ ] Separat deaktivierten inputfreien167-Methodenfall mit bekannten Kindrollen
  und dieselben tatsächlichen Worker-/Fingerprintdateien vorbereiten.
- [ ] Engsten A1-Fork aus tatsächlichem XTest-Preparation-Rootparent ableiten,
  eigener Namespace/Gatesfalse/Pins. Retailarm verlangt später echte erfolgreiche
  neue Lifecyclemethodenquittung mit passenden Sourcefingerprints.
- [ ] Bericht/echte RED-/GREENlogs/Pinquittung/saubere Commits; Rootreview.

Aktualisierung nach geschlossenem Root024-Messfenster: reine Adapter-/Worker- und
Methoden-/Buildertests RED→GREEN, 58 gezielte Fälle ohne Skips. Neue Pakete bleiben
deaktiviert; echter Lifecyclemethodenbeleg und Rootreview fehlen weiterhin.
Der ursprüngliche23-Fall-Quellcheckpoint bleibt als historischer Zwischenstand
erhalten. Näheres im Abschlussbericht vom15.11.
