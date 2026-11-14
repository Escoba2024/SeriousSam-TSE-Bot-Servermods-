# A1: deaktivierter passiver XRecord-Adapter

Status: ausführbare Offlinevorbereitung, keine neue Methoden-/Retailabnahme,
kein Gainfix, kein A1-Schadensnachweis. Weder Xlib noch Display, Spiel, Frida
oder Capture wurden durch diesen Arbeitszweig ausgeführt. Root besitzt allein
Integration, Freeze und native Ausführung. Alle vorherigen Fehler bleiben Fehler.

## Herkunft und unveränderte Verträge

Plan/Claim liegen auf Basis `a308756` im eigenen Worktree
`/srv/tse-a1-passive-xrecord-adapter-20261114`. Acht neue Quelldateien ergänzen
vier vorhandene unveränderte Coremodule; keine bestehende Coredatei, kein
Original-WIP und kein älterer Controller wurde verändert.

Der tatsächliche A1-Parent ist
`/srv/tse-a1-release-deadline-root-frozen-20261114`, Manifest
`2665517067a491e00607c7e4f88d5c3585739c66896f24c26b25eff672b7d136`.
Der Core-Methodenparent ist
`/srv/tse-own-xrecord-core-method-root-frozen-20261114`, Manifest
`43d38e727666d171bc9c6d021d4af018c60fe0279583c6636949d246e0f549ec`.
Root hat für diesen Core den Methodenbeleg `f0c3acc9…` geliefert:
PARTIAL_CORE_REQUESTS_ONLY, keine Qualifikation der neuen Ressourcenbindung.

Die Paketprüfung erhält CP, RotationDiagnostics, InputScope, X11Transport,
FileTransaction und Hostbudget bytegleich sowie action_step/read_rotation_pair
ASTgleich. Die vier Coredateien werden bytegleich aus dem geprüften Freeze
unter passive-core kopiert. Nur neue Imports/Observerstellen, deaktivierte
Gates, PRIVATE-/Paketpfade, eigener Namespace und Pins ändern sich.

Die ursprünglichen No-Fire-Kalibrier-/Aimimpulse einschließlich der beiden
100msForwardimpulse bleiben unverändert. Keine zusätzliche Pointerabfrage,
kein neuer Input, keine Route, kein Fire und keine Änderung an Gain, ACK,
EPS, finaler Frischzustandsprüfung, Held-/Releasegrenzen, CP85s oder Runner90s.
Die bestehenden Frida-Worker-/JS-/Originalbyterestorewege bleiben erhalten.

## Bindung und Grenzen

Ein frischer eigener Exec-Recorder öffnet nur das schon vorhandene eigene
Originaldisplay154. PID/Start, argv, tatsächliches DISPLAY, Xvfb-Unit,
X-Lock-PID, Socketdatei und SO_ACCEPTCON-Listenerinode im selben Xvfb-FD werden
geprüft. Der A1-Worker verwendet außerdem unverändert die vorhandene
Parent-/ArenaFLOCK-/Drei-Rollen-/CWD-/Namespacebindung. Keine Spiel-/Displayrolle
wird vom Adapter signalisiert. Der getrennte Methodenfall167 verlangt einen
Xvfb-Prozess, der tatsächlich Kind desselben gebundenen Methodenparents ist.

XDefaultGC und XGContextFromGC lesen die bereits vorhandene GC des bestehenden
Controllertransports. Zwei inaktive RECORD-Kontexte binden GC und das bereits
Original-PID-geprüfte Fenster serverseitig an zwei unterschiedliche tatsächliche
Clientbasen. Eine Clientbasis ist kein PID. AllClients/FutureClients und exakte
Rangeunionen bleiben erhalten; die feste3/4Clientzahl des Methodenfalls wird
nicht auf das geteilte Dedicated-/Originaldisplay übertragen. Alle bekannten
erforderlichen Clients bleiben enthalten, nur die eindeutig entfernte
Datenverbindung wird ausgeschlossen.

Ein Proxy ruft die vorhandene XTEST-Funktion mit identischen Argumenten genau
einmal auf und erhält Ergebnis/Exception. Er liest lediglich öffentliche
XNextRequest-Zähler vor/nach dem Aufruf und hängt begrenzt Speicherrecords an;
keine Datei-/IPC-Arbeit zwischen finalem ACK und nativer Eingabe. Die Einträge
werden mit der tatsächlichen vorhandenen action_step-Emission verschachtelt:
Kontrolle/Pixel beziehungsweise identischer Forward-Key und Releaseintervall.
Genau ein Record derselben gebundenen GC-Clientbasis muss Sequenz und Argumente
bestätigen. Fehlende/doppelte/fremde Records haben kein günstiges Fallback.

Limits bleiben15s/1024Records/2MiB/16KiBPayload, Arm3s/Stop3s und Vorinput-IPC100ms.
Emissionsspeicher hat maximal96Einträge. Der frische Worker besitzt eine echte
OS-Alarmfrist. Die unveränderte OwnChild-Hülle hat begrenztes IPC und5sCleanup,
bewahrt Popen-/PID-/Startquittungen und darf nur genau ihr eigenes Kind nach
Timeout beenden. Timeout/ForcedCleanup bleibt FAIL. Ein Trace über15s wird
nicht segmentiert oder verlängert. Native Callbackfehler verlassen die C-Grenze
nicht; FreeData steht im unveränderten finally. Stop/End/FreeContext/Close laufen
vor geerbtem normalem Frida-/Rollen-/FileTransactioncleanup. Ein Journalfehler
überspringt die Kindbereinigung nicht.

Der Auditor prüft alle Rohstreamserien, endliche monotone Empfangszeiten,
einmaliges Start/End, tatsächliche Byte-/Callback-/Freezähler und native
Cleanup-/Budgetfehler. XTEST, Query/Warp, Device- und Delivered-Kopien bleiben
getrennt. Die wenigen bekannten Nicht-Motion-XTEST-Keyformen werden offline
typisiert; der originale Unsupportedzähler und alle Rohbytes bleiben erhalten.
Unbekannte Wineverbindungen und XI2 bleiben unqualifiziert. Empfangsmonotonie
ist keine Gleichsetzung mit X-Server-, JS- oder Simulationszeit. Die neue
Messarbeit und ihr Einfluss auf das harte Host-/Inputbudget sind nativ offen.

## Neue Metadatenmethode: vor A1 zwingend offen

Das Paket enthält `binding_qualification=null`; die Runner-Vorprüfung verlangt
vor jedem Spielstart eine echte passende separate Methodenquittung. Bloßes
Setzen der Runtimegates reicht dafür nicht. Neue Kombination aus GC-Gettern,
ResourceSpec→ClientBase und öffentlichem Zähler bleibt prospektiv.

Root kann den neuen Worker separat und ohne A1 starten, nachdem ein eigener
Methodenparent unter den vorhandenen Runtime-/Build-/Methodensperren einen
frisch gebundenen eigenen Xvfb167 erstellt hat. Keine bestehende Displayinstanz
übernehmen. Der Methodenfreeze benötigt nur Worker-/Manifestfreigabe; A1-Runner,
Adapter und Frida-Gates können dabei deaktiviert bleiben. Das eigene0700-CWD
enthält vor Start eine0600-Konfiguration mit:

```
controller_root: der separat geprüfte Methodenfreeze
parent: pid, start_ticks des lebenden eigenen Methodenparents
passive:
  mode: method
  display: :167
  display_owner: identity=[PID,Start], exakte argv, socket_pin=[dev,ino,uid]
  evidence: dasselbe eigene0700-CWD
```

Der Parent startet ausschließlich den eigenen frischen Exec über OwnChild:
`python3 -E -s -B a1_passive_xrecord_worker.py --config CONFIG --display :167`.
Diese Methode benötigt kein Arm-IPC: sie führt genau zwei eigene Verbindungen,
ein ungemapptes1×1Fenster, die beiden GC-Getter und Ressourcenlookups sowie zwei
öffentliche XNextRequest-Lesungen aus. Kein XTEST, Warp oder QueryPointer.
Parent wartet höchstens3s auf den eigenen normalen Exit; OwnChild.cleanup()
bleibt der unabhängige begrenzte Fehlerpfad, jede erzwungene Bereinigung FAIL.
Xvfb wird ausschließlich durch seinen bestehenden Methodenowner geschlossen.

Nur Exit0, PASS_OWN_XRECORD_METADATA_BINDING_ONLY, zwei normale Closeversuche
ohne Fehler, no_inputs und die frisch passenden Methodenfingerprints ergeben
eine geeignete private `metadata-method.json`. Root muss diese tatsächliche
Quittung samt Herkunft/Hash prüfen und in einen neuen A1-Freeze übernehmen.
Keine historische Corequittung dafür umetikettieren. Danach bleibt ein einzelner
begrenzt instrumentierter No-Fire-A1-Diagnoselauf eine gesonderte Entscheidung.

## Primärquellen

Bereits vorhandene offizielle Quellen wurden nur gelesen, nicht installiert:

| Beleg | SHA256 |
|---|---|
| libX11-1.8.7.tar.xz | 05f267468e3c851ae2b5c830bcf74251a90f63f04dd7c709ca94dc155b7e99ee |
| Xlib.h | 748265b305975ae8396cdb310bcafa47d338211c977bfda9bf88d187a3a37c03 |
| Macros.c | 697538a3b1f0dc8628108307c0b777a35add82b472ddff8e6b8844cbb6db6fa2 |
| src/CrGC.c im Archiv | 1d72fb51626a4e95d61305ff068e2a73acc95c69a24429de3d467a2e25c15280 |
| tatsächlicher A1-x11_endpoint.py | 652147c86c52ce3a49afa7ef39c499df7c7a16a357259b4e09b66b2b8d40cb2b |

Xlib.h1590/1786/1810 belegen die öffentlichen GC-/Zählerprototypen;
Macros.c60/145 und CrGC.c belegen deren Definitionen. Keine private
Displaystruktur wird geraten. Primärpfad:
`/srv/tse-own-xrecord-core-controller-20261114/.codex/evidence/xorg-primaries/`.
Die älteren Xtst-/Protokollarchive bleiben unverändert im korrekten Inventorypfad
`/srv/tse-a1-xrecord-method-inventory-20261114/.codex/evidence/xorg-primaries/`.
Quellursprung: https://www.x.org/releases/individual/lib/libX11-1.8.7.tar.xz

## Offlineverifikation und ausführbarer Handoff

RED wurde vor zugehörigen Änderungen beobachtet: fehlende neue Adapterfunktionen,
fehlende öffentliche Zählerprototypen, nicht fortgesetzter Lookupcleanup nach
FreeStatefehler, fälschlich typisierter anderer Extensionopcode, fehlende
Phasenbindung, ausgelassener Close nach fehlgeschlagener Openprüfung, fehlende
Zählerausführung in der separaten Methode, ungeprüfte Rohbyte-/Start-/Endzähler
und fremder Methoden-Xvfb-Parent. Ein fehlerhaft konstruierter temporärer
Listenerpfad wurde ausschließlich in der Testfixture korrigiert.

Fokussierte neue29Fälle und vorhandene63Regressionen bestehen. Keine breite
Discovery, Compiler oder Runtime. Exakte Befehle:

```
PYTHONPATH=tools python3 -m unittest test_a1_passive_xrecord test_a1_passive_xrecord_worker test_a1_passive_xrecord_evidence test_prepare_a1_passive_xrecord -v
PYTHONPATH=tools python3 -m unittest test_xrecord_core_method test_xrecord_core_native test_xrecord_core_worker test_xrecord_core_process test_xrecord_core_binding test_a1_release_before_observation test_prepare_a1_release_before_observation -v
PYTHONPATH=tools python3 tools/prepare_a1_passive_xrecord.py --destination /srv/tse-a1-passive-xrecord-disabled-20261114
```

Nur OwnChild-Regressionen führen kurzlebige eigene Python-Fakekinder aus;
Fake-ABI-/Dateifixturen laden keine X-Bibliothek. Paketmanifest und private
PASSIVE-HANDOFF.json liefern exakte Sourcepins. Root muss das neue Paket
unabhängig reviewen; alle nativen Methoden-/A1-/Overheadgates bleiben offen.
