# Eigene XRes-PID-Methode Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking. Root allein installiert, integriert, friert ein und führt Native aus; keine weiteren Agenten.

**Goal:** In einer eigenen frischen167-Methode ausschließlich lokale XclientBase-/Resource→OSPID-Attribution für bekannte eigene Prozesse qualifizieren.

**Architecture:** Eigene neue Methodendateien verwenden die vorhandenen Cold/Warm-Display-, OwnChild-, IPC-, Normalclose- und Receiptmechaniken. Parent lädt keine X-Bibliotheken; ein frischer Execworker übernimmt Metadaten. Zwei Driververbindungen und ein separater normaler Peer liefern bekannte Ressourcen und echte PIDs; kein TSE/Wine/Frida/Input.

**Tech Stack:** Python/ctypes, regulär bereitgestelltes libXRes1.2.1, öffentliche Xlib-/XRes-Header, eigenes Xvfb167, vorhandenes boundedOwnChild.

**Spec:** `docs/decisions/2026-11-14-xres-client-attribution-feasibility.md` plus Rootauftrag: genau zwei Driververbindungen, separater Peer, Base UND Resource, Namespace/Startgeneration, vollständiger Cleanup; Task1–3 sind offline umgesetzt; tatsächliche Displayqualifikation bleibt Root-only offen.

## Global Constraints

- Root-Nativefenster bleiben STATICONLY. Nach RootClosed sind ausschließlich die hier dokumentierten Offline-Schritte erlaubt; keine Agenten-Display-/Native-/Compiler-/Installationsaufrufe.
- Root stellt später regulär `libxres1=2:1.2.1-1build1` und `libxres-dev=2:1.2.1-1build1` bereit; vorher frische Simulation, keine Updates gepinnter Runtimes/Daemonpakete, mindestens8GiB frei.
- Hüllenparent:`/srv/tse-own-xrecord-cold-warm-root-frozen-20261114`, Manifest laut bestehender Freezequittung`5749113983ea2462e60d84630d5823ff04f6f8b1b7147c3effc600f6124d928c`; erst nach RootClosed frisch gegen Dateien prüfen. Alte Pakete unverändert.
- Neuer Methodennamespace, eigene frische167 nur bei tatsächlich freien Socket/Lock; vorhandene vier Runtime-/Build-/Fleet-/Deploymentlocks aus Root-Methodenwrapper und Methodenlock`/run/lock/ssam-own-xrecord-core-method167.lock` erhalten.
- Controller30s; Display/Driver/Peer-TTL30s, Attributor-TTL15s; Driver-/Peeroperation2s, Metadata-Arm/Snapshot/Stop maximal3s, stets zusätzlich vom Rest der globalen30s begrenzt. Cleanup5s je eigenem Kind; IPC16384Bytes, private0700/0600/O_EXCL-Dateien, kein Retry.
- Vorhandene PID/Start/argv/CWD/PGID/Display-/Socket-/Lockguards und Normalsignal-/Reapregeln unverändert. Kein normaler PASS bei Force/Timeout/fehlendem Nativeclosebeleg.
- Keine FakeInput-/Warp-/Focus-/User32-/TSE-/Wine-/Frida-/XRecord-Aufrufe. Keine alte Cold/Warm-`execute`/`run_method`/Driver-`initialize` aufrufen: deren Programm enthält Mausbewegungen. Nur die Hülle wiederverwenden.
- Keine alten A1-Gates/ACK/Gain/EPS/Inputgrenzen ändern. Alte U bleibtUNKNOWN; zwei Metadatensnapshots beweisen keine lückenlose Clientbase-Lebensdauer.

## Review Focus

1. QueryClientIds-Erfolg ist0, Extension/Version-Erfolg1; leere positive Protokollantwort ist kein PIDbeleg → Task1 Status-/Leer-/Maskentests.
2. Native LP64-Structs sind nicht32bit-Wirefelder; falsche Länge/Pointer/Arrays müssen vor Wertzugriff scheitern → Task1 Fake-C-ABI-/Freefälle und Task4 tatsächliche Header-/Layoutgegenprüfung.
3. Richtiger PID bei falscher Startgeneration/Namespace/Base darf nicht passen → Task1 Mutationen, Task2 echte OwnChildvergleiche.
4. Teilstart/IPC-/Closefehler darf fremde Prozesse/Display nicht treffen oder Cleanup überspringen → Task2 geerbte Fehlerfälle/Fakekinder.
5. Keine durch Legacyhüllen versehentlich erreichbaren Eingaben und kein Whole-interval-Claim aus Snapshotgleichheit → Task2/3 AST-/Schema-Negativtests.

---

## Dateigrenzen und feste Schnittstellen

Nur neu erstellen:

- `tools/xres_pid_method.py`: pure Validierung und eingeschränkter Ergebnisstatus, kein CDLL/Prozessstart.
- `tools/xres_pid_worker.py`: frischer Execworker für Rollen`driver`, `peer`, `attributor`; öffentliche Xlib-/XRes-Metadaten und Nativeclosebelege.
- `tools/xres_pid_controller.py`: eng adaptierte vorhandene Parenthülle, unveränderte Display-/OwnChild-/IPC-Guards, fester Ablauf und normale vierteilige Cleanupreihenfolge.
- `tools/prepare_xres_pid_method.py`: neuer deaktivierter Paketbuilder; kopiert OwnChild`xrecord_core_process.py` bytegleich, bindet frisch bereitgestellte Header/Libs und Quellen.
- `tools/test_xres_pid_method.py`, `tools/test_xres_pid_lifecycle.py`: ausschließlich pure/Fake-C-/Fake-Kindfälle, keine Displayöffnung.
- Neuer eigener Bericht; kein Root-Handoff oder A1-/Nav-/Livecodeclaim.

Schnittstellen:

- Worker`initialize` bei Driver öffnet genau zwei Verbindungen, erzeugt je ein kleines **ungemapptes** eigenes Fenster und XSync; Peer genau eine Verbindung/ein Fenster. Rückgabe`resources:[XID,...]`, keine behauptete PID als Autorität.
- Attributor`initialize` öffnet nur die Metadatenverbindung, prüft XResExtension und Protokoll≥1.2, meldet echte Version. Keine XTest-/XRecordbibliothek laden.
- Attributor`snapshot(resources:list[int]) -> {clients,results,native_checks}`: genau drei Ressourcen; XResQueryClients liefert Base/Mask; pro Resource genau eine QueryClientIds(Resource,PIDmask2) und eine QueryClientIds(Base,PIDmask2). Maximal64Clientranges, sechs Einzelqueries, je eine eindeutige PIDantwort. Jede C-Ausgabe vollständig freigeben.
- Jede Ergebnisrow:`requested_xid`, `requested_kind`, `reply_spec_client`, `resource_base`, `resource_mask`, `mask`, `length`, `pid`. Rückgabespec kann die Resource oder deren bewiesene Clientkomponente darstellen; ausschließlich dieselbe konkrete QueryClients-Range akzeptieren, kein freier XID-/PIDfallback.
- Pure`validate_snapshot(snapshot:dict, expected:dict) -> dict`: expected aus echten OwnChild.identities und den authentischen initialize-IPCantworten; prüft Driver-PID für beide Verbindungen, anderen Peer-PID, Resource und Base identisch pro Ziel, positive PID und aktuelle gleiche PIDnamespace-/Startticks.
- Controller`run_method(directory:Path) -> dict`: einzig neuer Programmeinstieg, manifest-/sourcegated und standardmäßig deaktiviert. Endstatus ausschließlich`PASS_METHOD_XRES_LOCAL_PID_METADATA_ONLY` oder begrenzterFAIL; immer`historical_u_attributed=False`, `continuous_client_lifetime_proven=False`, `a1_pass=False`, `retail_qualified=False`.

### Task1: Öffentliche ABI und strikte Einzel-Snapshotvalidierung

- [x] Nach RootClosed/Umsetzungsauftrag erst tatsächliche installierte Header/Symbole/Pins lesen; XRes.h/XRes.c aus geprüfter Primärversion gegenprüfen. Eigene frische Implementierungsworktree/Claims sichern.
- [x] RED schreiben:`test_success_zero_and_exact_resource_base_pid_pairs`, `test_empty_ids_and_negative_pid_are_unknown_not_pass`, `test_foreign_base_namespace_or_start_rejected`, `test_bad_mask_length_pointer_or_duplicate_ids_rejected`. Fixtures: DriverPID101/Start1001 mit zwei verschiedenen Bases, PeerPID102/Start1002 mit dritter Base; keine PID=Base-Annahme.
- [x] RED ausführen und echte0600-Ausgabe sichern: `python3 -B -m unittest test_xres_pid_method -v`; zunächst fehlende Implementierung/ungeprüfte Felder müssen scheitern.
- [x] Minimalen Worker-Nativeadapter und pure`validate_snapshot` implementieren. `XResQueryExtension` Bool, QueryVersion1, QueryClientIds Success0; positive eindeutige PID nötig. XID/long als native Headergrößen, PIDpayloadCARD32; Getter`XResGetClientPid`, danach`XResClientIdsDestroy`; QueryClientsarray mit XFree. Alle Ausgangspointer vor Call NULL/Counts0; jede Fehlerkante freigeben.
- [x] Fake-C-Fälle für Queryfehler/0IDs/zu vieleIDs/ungültige Längen, Ausnahmepfad nach Allokation, Freefehler und normale doppelte/idempotente Closefolge ergänzen. Keine Xlibfunktion in diesen Tests wirklich aufrufen.
- [x] Dieselben gezielten Fälle GREEN,0Skips; Quellen/Tests committen.

### Task2: Vorhandene Hülle, zwei Snapshotgrenzen, vier normale Rollen

- [x] RED in`test_xres_pid_lifecycle`: OwnDriver2Verbindungen+Peer1, genau zwei Metadatensnapshots, alle vier Kinder normalclosed/reaped; veränderte PID/Start/Namespace, Teil-Popenfehler, falscher Replyserial, Deadline/IPCüberschreitung und Metadatencleanupfehler bleiben stickyFAIL.
- [x] `python3 -B -m unittest test_xres_pid_lifecycle -v` RED sichern.
- [x] Parenthülle eng adaptieren: `fresh_display_available`, `guard_display`, `wait_display`, `check_disk`, boundedOwnChild und normale Close-/Reaplogik wiederverwenden; eigene Rollen`display,driver,peer,attributor`, Cleanup`attributor→peer→driver→display`. Zusätzlicher Peer erweitert nur bekannte Rollenliste, keine neue Prozesssteuerung.
- [x] Fester Ablauf: Displayguard→Driverinitialize→Peerinitialize→Attributorinitialize→Snapshot1→OwnChild/PIDnamespace/Startguard→Snapshot2→Normalcleanup. Vor und nach jedem Snapshot alle eigenen Rollenidentitäten prüfen. Keine künstliche Pause, Unterbrechung eines Peers, Input oder optionaler weiterer Methodenlauf.
- [x] AST-/Fake-Nativefall:`test_no_input_or_legacy_execute_reachable`; verbiete jede erreichbare XTestFake*/XWarpPointer/XSetInputFocus/alteexecute-/User32-/Frida-/TSEfunktion. Parent muss ohne CDLL bleiben. Startup/Closebelege auch bei Fehler vor vollständiger Rollenzahl erhalten; positiver Endstatus verlangt alle vier.
- [x] Beide gezielten Testmodule GREEN; geerbte pure OwnChild-Regressionen nur begrenzt ergänzen, kein breites Discovery; committen.

### Task3: Deaktiviertes reproduzierbares Paket und Reviewquittung

- [x] RED:`test_disabled_package_pins_installed_headers_libs_and_immutable_ownchild`, `test_false_interval_or_historical_u_claim_cannot_pass`, `test_stale_source_or_occupied_namespace_has_no_execution`. Neues Zieldirectory muss fehlen; keine native Paketprobe.
- [x] Builder implementieren: neuer Pfad`/srv/tse-own-xres-pid-disabled-20261114`, alle Ausführungsgates/ManifestFalse, eigener Evidenceprefix. Parentquellen/alten Methodenbeleg sowie installierte libXRes/X11/Xext/Headers und Xvfb exakt pinnen; Paket diff/Quellderivation und Normalsignal-/Boundsvertrag dokumentieren. Qualifikation vererbter Hülle ist keine XRes-ABIqualifikation.
- [x] `python3 -B -m unittest test_xres_pid_method test_xres_pid_lifecycle -v` GREEN,0Skips; tatsächliche RED/GREEN0600 speichern. Keine Ausgabe als gespeicherten Log behaupten, wenn sie nur im Tooltranskript existiert.
- [x] Builder ausschließlich offline ausführen, Quellen/Libpins frisch vergleichen, eigene Quittung/Bericht und saubere Commits liefern. Root prüft unabhängig und erstellt separaten Freeze; kein Agent startet ihn.

### Task4: Root-only Bereitstellung und genau eine eigene Nativequalifikation

- [ ] Erst geschlossenes fremdes Nativefenster, technische Locks/Jobsfrei/Ressourcen und Backup prüfen. Frische APTsimulation muss weiterhin0Runtimeupgrades ergeben; Root führt nur reguläre kostenfreie Paketbereitstellung aus und prüft gepinnte Bibliothekshashes davor/danach.
- [x] Tatsächliche Header-ABI mit eigenem minimalen Layoutbeleg qualifizieren: sizeof/offsetof von XResClientIdSpec/Value, XID/long/pid_t und öffentliche Signaturen gegen ctypes; nur Root kompiliert/führt diese eigene Quelle aus. Kein TSE/Displayzugriff durch den Layoutbeleg.
- [ ] Nach unabhängiger Source-/Pin-/Gate-/NoInputreview und Sicherung Rootwrapper genau einmal auf eigenem freien167 starten; eigene Grenzen/Locks oben, keine parallel belastenden Tests/Publikation. Versions-/Leere-PID-/ABIfehler bleibenFAIL, kein automatischer Retry.
- [ ] Tatsächliche zwei Driverbasen und Peerbase über Resource UND Base den erwarteten positiven PIDs/Startgenerationen/Namespaces zuordnen. Rohantworten/Counts/Returns, sechs Einzelqueryergebnisse je Snapshot und echte Verbindungs-/Fensteridentitäten behalten; nichts durch erwartete Werte ergänzen.
- [ ] Alle XResarrays/QueryClientsarrays/Fenster/Verbindungen freigeben; jeden Nativeclose/PID-/Reap-/Displayabsenzbeleg prüfen, keine Normal-PASS-Umwertung von Force/Timeout. Gemeinsame Ressourcen-/Log-/Quellenquittung mit tatsächlichem Hash rücklesen.
- [ ] Status begrenzt ausweisen. Erst dann kann Root einen separaten A1-Metadatensnapshotplan prüfen; diese Methode implementiert ihn nicht. Keine Attribution der alten U, keine BaseLifetime-/Recenter-Warp-/Gain-/A1behauptung.

## Planstatus / Handoff

Task1–3 offline fertig: 20 neue Fälle plus 8 geerbte OwnChild-Fälle PASS,
0 Skips; gespeicherte RED/GREEN-Quittungen und Pins im neuen Bericht.
Zwei echte Snapshots und die tatsächlichen XRes-Aufrufe wurden NICHT ausgeführt.
Root stellte Bibliotheken/Header bereit und belegte das Headerlayout separat;
ctypes wurde offline dagegen verglichen. Kein Agentencompiler/Display/Input.

Deaktiviertes Paket: `/srv/tse-own-xres-pid-disabled-20261114`, Manifest
`21ff26bc3b5b60e42a6cd16874577ad3c176a7bff3544c6d01b930130e074a42`.
Nächster Schritt: unabhängiger Review; danach Root-only ein eigener Methodenfall.
Alte U bleibt UNKNOWN; kein A1-, Warpursachen- oder Lebensdauerbeweis.
