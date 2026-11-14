# A1-NoFire: eng begrenzte XRes-/RECORD-Attribution

> Implementierung erst nach Rootentscheidung zu diesem Plan. Root integriert,
> friert ein und führt Native allein aus; keine weitere Delegation.

**Goal:** Neue QueryPointer-/Warp-Requests des eigenen begrenzten NoFire-Laufs
an aktuelle eigene Original-Hostprozessgenerationen binden. Keine alte U
attribuieren, kein Gain-/Cachefix oder A1-PASS behaupten.

**Architecture:** Vorhandener Original154-Recorder/OwnChild/IPC/Normalcleanup
bleibt die Hülle. Metadaten erfolgen ausschließlich im frischen Recorderexec
auf dessen vorhandener Steuerverbindung, nie im Parent oder Inputhotpath.
Öffentliche XRes-ABI/GetClientPid-/Free-Kontrakte stammen aus dem echten V2-Fall;
Original-PID-/Module-/Display-/Sessionguards aus dem A1-Parent bleiben.

**Claim jetzt:** Nur dieser Plan und der neue Bericht
`docs/reports/2026-11-14-a1-xres-attribution-semantics.md` im eigenen WT
`/srv/tse-a1-xres-attribution-plan-20261114`. Noch keine Code-/Teständerung.

## Feste Herkünfte und unveränderte Verträge

- Tatsächlicher A1-Parent `/srv/tse-a1-xtest-preparation-root-frozen-20261114`,
  Manifest71b9c896e068e473d0fd8317871b0fa3ccc5f4a43828c87e8b1b09619c60170a.
- XResV2-Methodenfreeze `/srv/tse-own-xres-pid-v2-root-frozen-20261114`,
  Manifest09be57b6b0eec29a598b68a612376ebdb4939857b7fbc69342ecbdb2e924f687;
  echtes Methodenresult18d16f195c64d2d5f6564b0166422d63aa72011c4dcd71284f05d1d9a1afc953.
- Öffentliches vorhandenes `prepare_a1_xtest_preparation.py` sowie private
  Rootfreeze-/Methodenquittungen wiederverwenden. Bei späterem Builder alle
  Parent-/Runtime-/Collector-/Core-/Bibliotheks-/Headerpins frisch prüfen.
- Keine neue Eingabe, Pointerabfrage, User32-Funktion, FPSänderung, Hooksite oder
  neue CP-Route. Gleiche ursprünglichen NoFire-Kalibrier-/Aimaktionen, Argumente,
  Bodyalignment-Forwardimpulse, native Exceptions und notwendiger Keyupcleanup.
- Emissionguard b−a≤4, Max96Attemptjournal, ACK2s, Held350ms,
  CP85s/Runner90s, Arm3s/Stop3s, VorinputIPC100ms, Recorder15s,
  1024Records/2MiB/16KiBPayload und alle Ressourcen-/Normalcloses unverändert.
- Keine zusätzlichen RPCs pro Input/ACK. Metadatenarbeit muss IN den vorhandenen
  Arm-/Stopbudgets Platz finden; Überschreitung ist FAIL, keine Verlängerung.
- Alle alten A1-/XRes-Fails und Quittungen unverändert. Keine Produktivänderung.

## Vor Code erforderliche Scopeentscheidung

**Empfohlener vollständiger enger Scope:** Die beiden Lifecycleflags werden
zusätzlich zu den bisherigen festen Core-Ranges aktiviert, ohne neue Inputarten
oder sonstige Protokollranges. Die vier Coredateien bleiben bytegleich; eine
neue kleine Recorderableitung/adaptereigene Rangefabrik muss dieses explizite
Delta und GetContextcoverage prüfen. Das ist eine neue Beobachtungsbedingung
und benötigt gesonderten Review/Methodenbeleg; heutige Corequalifikation darf
nicht stillschweigend darauf übertragen werden.

**Falls Root ausschließlich unveränderte Ranges will:** Nur
`POINT_IN_TIME_XRES_PID_METADATA_ONLY`. Zwei Punkt-Snapshots, keinerlei
Request→Original-PID-Intervallclaim. Das kann Wine-PIDform klären, erfüllt aber
nicht das stärkere Zuordnungsziel. Kein automatischer Wechsel zwischen Varianten.

## Kleinster Ablauf mit tatsächlicher Intervallbindung

1. Bestehende Owned154-/Original-/Modul-/Namespaceguards und XTestQuery+Sync wie
   bisher. Recorder erstellt genau einen Kontext AllClients/FutureClients mit
   bisherigen Ranges plus ClientStarted/Died; kein fremder Display.
2. Enable und echtes StartOfData. **Erst bei aktiviertem Stream** den ersten
   XRes-Snapshot auf Recordercontrol lesen; gesamte Armoperation weiterhin≤3s.
   Keine Eingabefreigabe bis erfolgreicher Armantwort. Alle neuen Rohbelege
   exklusiv0600 erhalten, auch wenn Validierung scheitert.
3. Aktuelle positive Basen aus tatsächlichem Context/QueryClients ohne
   Outcomeauswahl höchstens32Zielbasen; serverBase0/Future2 nicht als Ziel
   abfragen. QueryClients maximal64; genau eine Success0/PIDmask2/Länge4-Abfrage
   je konkreter Zielbase, keine Wildcards. Bestehende Originalfenster- und
   Controller-GC-Resourcebindings gegen dieselben Ranges prüfen; beide Resource-
   PIDzuordnungen separat belegen. Maximal34Einzelqueries/Snapshot, genau2Snapshots.
   Dieses feste Maximalbudget muss vor Implementierung von Root bestätigt werden.
4. Vor/nach jeder Metadatenphase echte Parent-/Recorder-/Xvfb-/Original-
   HostPID, Startticks und PIDnamespace binden. Nur bekannte eigene Rollen in
   `/proc` prüfen; unbekannte numerische XRes-PIDs nicht durch fremde
   Prozessinspektion aufwerten. Controller und Original haben eigene Kategorien.
5. Bestehende Eingaben/ACKs/Frida-/Bodybeobachtung unverändert. Kein XRescall im
   Hotpath. Jede bisherige RECORDrow mit Base, Callbackserial, Clientsequenz,
   Xserverzeit und Empfangsmonotonie unverändert erhalten.
6. Im vorhandenen Stop vor Disable den zweiten Snapshot **bei weiter aktiviertem
   RECORD** nehmen, danach Disable+Sync und vollständiger Drain bis EndOfData.
   Alles in bisherigem Stop3s und Recorder15s. Keine Inputwiederholung; Close,
   FreeData/Arrays/Context/Connections, eigenes Workerreap und normale äußere
   Rollen-/Frida-/FileTransactionrestauration auch bei Metadatenfehlern.
7. Offline nur Basen binden, die in beiden Snapshots dieselbe exakte bekannte
   OwnOriginal-PIDgeneration haben UND über vollständigen Start→End-Stream keine
   ClientStarted-/ClientDied-Grenze für diese Base besitzen. Unbekannter/neuer/
   gestorbener/wiederverwendeter Client bleibt UNKNOWN; keine Annahme aus
   fehlendem Event bei deaktivierter/fehlerhafter Lifecycleaufnahme.
8. Zuordnung gilt ausschließlich diesem vollständig archivierten RECORDfenster.
   Keine Lifetime vor Start/nach End, keine Geräteursprungs-PID aus id_base0,
   keine Host-/JS-/Serverclockfusion. Eine aktuelle Original-Requestzuordnung
   trennt Netzwerkverbindung von Ursachen für zweimaligen GetInputwert.

## Noch zu belegende Rand- und Methodenfragen

- Lifecycleflag-Union/GetContext und tatsächliche Delivery/Drain-Grenzen sind
  neue Beobachtung. Vor Retail ein einziger eigener, inputfreier167-Methodenfall
  kann mit normalem bekannten Peer-Disconnect die ClientDied-Grenze zeigen;
  falls Base-Reuse nicht wirklich eintritt, nur synthetische Negativprüfung,
  keinen nativen Wiederverwendungsbeweis behaupten. Kein Methodenstartauftrag
  durch diesen Plan; Root entscheidet Reihenfolge und Notwendigkeit.
- Snapshotaufrufe sind nicht atomar. Vollständige Lifecycleaufnahme muss
  insbesondere Änderungen während eines Snapshotaufrufs entlarven. Konservativ
  jede Base mit Lifecyclegrenze im gesamten Start→End als nicht bindbar behandeln;
  kein günstiger Randzuschnitt oder Gleichsetzen gleicher Millisekunden.
- Reines Pump0 ist keine beliebige Zukunfts-/Queue-Leer-Garantie. EndOfData,
  lückenlose Callbackserials und native calls==freed==records, kein Drop/Overflow,
  genaue range_coverage und echte Enabledstate sind erforderlich. Ein Endmarker
  ersetzt keine Client-Lifecycleflagprüfung.
- ClientStarted-Setupdaten können groß sein. Bestehende16KiB-/Gesamtbounds bleiben;
  unpassender Payload oder ungültige Byteordnung/Setupform scheitert. Vor einer
  neuen Setupauswertung genaue libXtst1.2.3/Headerlayouts lesen, keine neue ABI
  aus Source1.10/TSE ableiten. Vorhandener Parser darf neue Daten nicht als
  Lebenszyklusbeleg mit ungeprüfter Base verwenden.
- Wine-/Peercredentials sind nativ noch ungemessen. Keine WindowsPID=TID=LinuxPID-
  Annahme, keine heuristische TGIDnormalisierung. Abweichende PID separat UNKNOWN.

## Gezielte TDD-Schritte erst nach Rootentscheidung

- [ ] Neuer isolierter ImplementierungsWT mit exklusiven NEUEN Dateien
  `a1_xres_attribution.py`, `a1_xres_attribution_worker.py`,
  `a1_xres_attribution_evidence.py`, `prepare_a1_xres_attribution.py` und Tests;
  enge Adapterstellen in eigener A1-Kopie, kein Live-/Coredateiclaim.
- [ ] RED Punktzuordnungen ohne aktivierte Lifecycleflags dürfen keinen
  Intervallstatus erzeugen. Mutationen: gleichesBase/PID mit Died→Started,
  neue Base erst im zweiten Snapshot, Änderung während Snapshot, falsche
  Namespace-/Startgeneration/Original-PID und fehlende Daten-/Endabdeckung.
- [ ] RED QueryStatus1,0IDs/fremdePID/Mask/Länge, Server0-Wildcard,65Clients,
  mehrals32Ziele, doppelte/ambigeRanges und nicht freigegebene Arrays scheitern.
- [ ] RED exakt bestehende Argumente/Return/Exceptions/Keyup und alle Budgets;
  zusätzliche Hotpathcalls, neue Eingabe oder geänderte Frida/CP/Guard-Hashes
  scheitern. RootA1-/XRes-Methodenquittungen sind echte Builderprerequisites.
- [ ] Engste GREEN-Implementation und begrenzte geerbte Regressionen; private
  echte RED/GREENlogs speichern. Neue deaktivierte Kopie mit neuen Pins/Namespaces,
  allen Gatesfalse; vollständiger Source-/Methoden-/Grenzdiff zur Rootprüfung.
- [ ] Rootreview/ggf.Methodenqualifikation/Backup, dann allein Root genau ein
  NoFirediagnostikfenster. Keine automatische Wiederholung/Promotion.

## Ergebnisstatus

`BOUND_CURRENT_RECORD_CONNECTION_TO_OWN_ORIGINAL_PID_ONLY` nur bei allen
beschriebenen Verbindungskriterien; andernfalls konkrete UNKNOWN/FAILgrenzen.
Haupt-A1-Gainprüfung bleibt unverändert und darf weiter FAIL sein.
Immer `qualified=False`, `a1_pass=False`, `gain_fixed=False`,
`old_u_attributed=False`, `continuous_lifetime_outside_record=False`.

Status dieses Commits: ausschließlich statischer Plan und Fähigkeitenbefund;
keine Implementierung/Tests/Hashes/native Methode. Offene Scopeentscheidungen
sind oben explizit, kein neuer Nutzerfreigabeprozess.
