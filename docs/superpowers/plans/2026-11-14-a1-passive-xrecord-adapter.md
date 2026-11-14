# A1: deaktivierter passiver XRecord-Adapter

**Goal:** Die vorhandenen No-Fire-Kalibriereingaben des eigenen Originalclients
mit privaten XTEST-/Warp-/Query-/Core-Motionrecords zusammenführen, ohne neue
Inputs/Pointerabfragen oder geänderte Gain-/ACK-/EPS-/350ms-/CP-Fristen.
**Base:** a308756. Root hat die Offlineimplementation ausdrücklich beauftragt;
keine zusätzliche Nutzerrunde, keine eigene native Ausführung oder Delegation.
**Architecture:** Neue kleine Adaptermodule erben die bereits methodisch
verwendeten unveränderten Core-Bindungen/Recorder-/OwnChild-Implementierungen.
Ein frischer Exec-Recorder läuft auf dem vorhandenen eigenen Originaldisplay154.
Der eingefrorene A1-Controller wird nur in einer neuen privaten deaktivierten
Kopie um Start/Guard/Quittung/Cleanup und eine XTEST-Proxyhülle ergänzt.

## Verbindlicher Ausgangspunkt

- A1-Parent `/srv/tse-a1-release-deadline-root-frozen-20261114`, Manifest
  `2665517067a491e00607c7e4f88d5c3585739c66896f24c26b25eff672b7d136`.
- Methodisch verwendeter Core-Freeze
  `/srv/tse-own-xrecord-core-method-root-frozen-20261114`, Manifest
  `43d38e727666d171bc9c6d021d4af018c60fe0279583c6636949d246e0f549ec`.
  Methodenergebnis f0c3acc9… ist PARTIAL_CORE_REQUESTS_ONLY, kein TSE-Nachweis.
- Keine bestehenden xrecord_core_*-Dateien, ursprünglichen WIPs, Root-Live-
  Runtime, Profile, Retaildateien oder vorhandenen Controller verändern.
- Der vorhandene InputScope erlaubt ausschließlich dieselben ursprünglichen
  vier Kalibrieraktionen (einschließlich der zwei100msForwardimpulse), zwei
  Pitchimpulse und bestehende Aimimpulse. Kein Fire oder neuer Routenpfad.
- Capture bleibt15s/1024Records/2MiB/16KiBPayload, Arm3s/Stop3s;
  Vor-Input-IPC100ms. Die CP85s-/Runner90s-/ACK2s-/350ms-Grenzen bleiben exakt.
  Ein zu langer oder übervoller passiver Trace ist stickyFAIL, keine
  automatischen Segmente, Verlängerungen oder Inputwiederholungen.

## Designentscheidungen und wissenschaftliche Grenzen

- :154 wird von eigenem Dedicated und Original geteilt; es gelten weder167
  noch die3/4Clientzahlen des reinen Methodenfalls. Socket/Listener/FD,
  Xvfb-PID/Start/Cgroup, Original-PID/Start/Display, Parent und exklusive
  Arena-Locks werden frisch gebunden; keine fremden Displays/Prozesse anfassen.
- AllClients/FutureClients bewahren die tatsächlichen ausgewählten Rohrecords;
  ihre Clientbasen werden nicht PIDs gleichgesetzt. Unbekannte Wine-Verbindungen
  und XI2 bleiben ausdrücklich unqualifiziert, auch bei fehlenden Coreevents.
- Zwei zusätzliche öffentliche reine Getter XDefaultGC/XGContextFromGC lesen
  die bereits vorhandene Default-GC-XID des bestehenden Controllertransports.
  Keine Ressource/Pointerabfrage oder Eingabe wird dafür erzeugt. Die Prototypen
  stammen aus offiziellem Xlib.h; XDefaultGC/CrGC.c sind Gegenbelege.
  Der Worker ordnet diese GC und die bereits PID-geprüfte Originalfenster-XID
  über getrennte unaktivierte RECORD-Lookupkontexte serverseitig zu. Damit
  entsteht eine tatsächliche ResourceOwner-Zuordnung ohne private Display-ABI.
  **Diese Getter-/Lookupkombination ist NEU und nativ noch nicht qualifiziert.**
  A1-Arm verlangt eine getrennte, gehashte erfolgreiche Own-Methodenquittung.
- Ein dünner Proxy lässt jedes bestehende XTEST-Argument/Ergebnis/Exception
  genau einmal unverändert durch und protokolliert öffentliche XNextRequest-
  Intervalle/Hostzeiten. Kein Dateischreiben oder IPC zwischen finalem
  Frischzustandscheck und tatsächlicher Eingabe; nur begrenzter Speicherappend.
  Bestehende Xlib-/CP-Aktionskörper und ihre Zeitgrenzen bleiben byte-/ASTgleich.
- Der Auditor verlangt für jede protokollierte tatsächliche Controlleremission
  genau einen passenden XTEST-Record der serverseitig gebundenen GC-Clientbasis
  mit passender Sequenz/Argumenten. Kein günstiges Fremdclientfallback.
  WindowClient-Warps, Controllerqueries und Device/Delivered-Kopien bleiben
  getrennt. Empfangsmonotonie ist keine Gleichsetzung mit X-Server-/JS-Zeit.
- Der unveränderte Coredecoder kennzeichnet Nicht-Motion-XTEST als unsupported.
  Der neue Offlineauditor kann genau bekannte Keypress/-release-Wireformen
  typisieren, erhält den ursprünglichen Unsupportedzähler und weist alle
  verbleibenden unbekannten Formen aus; keine stillen Null-/Vollständigkeitsclaims.
- Stop/End/FreeData/FreeContext/Connectionclose laufen vor geerbtem normalen
  Frida-/Rollen-/FileTransactioncleanup. XRecord hat keine Spieltrampolines;
  nur das präzise eigene neue Exec-Kind darf bei Timeout beendet werden.
  Jedes Timeout/ForcedCleanup bleibt FAIL; die normalen äußeren Cleanupwege
  laufen trotzdem weiter. Keine Spiel-/Displayrolle wird vom Adapter signalisiert.

## Umsetzung und fokussierte RED→GREEN-Schritte

- [x] Neue Dateien `tools/a1_passive_xrecord.py`,
  `a1_passive_xrecord_worker.py`, `a1_passive_xrecord_evidence.py`,
  `prepare_a1_passive_xrecord.py`, jeweilige fokussierte Tests und Bericht.
- [x] Vor Code: Fixtures für Ressource→Clientbindung, Datenclientausschluss,
  beliebige exakte Range-Packung, falsche Ressource/Client-/PID-/Socketbindung,
  fehlende separate Methodenquittung, einmalige Nativeargumente/Exceptions,
  fehlende/doppelte/fremde XTESTrecords und separate Eventkopien RED ausführen.
- [x] Nur bestehende öffentliche API-Signaturen/immutablen Corecode verwenden;
  Quellen-/Parent-/Methodenpins prüfen. Keine Native-/Xlibtests hier starten.
- [x] Frischer eigener Worker übernimmt kontinuierliches ProcessReplies und
  bounded private Rohdatei; Parent nutzt vorhandene OwnChild-IPC/Cleanup.
  Tests nur Python-/OS-Fixturen/Fake-ABI-/Fakekindfälle, keine Displays.
- [x] Privaten A1-Fork reproduzierbar ableiten. Nur neue Imports/Observerstellen,
  eigener Namespace, GateFalse und notwendige Pins/PRIVATE-Pfade ändern.
  CP/RD/InputScope/x11_endpoint/Gain/ACK/Held-/Release-/Restorekörper erhalten;
  geerbte Frida-Worker-/JS-Logik nur unverändert umgebunden/deaktiviert.
- [x] Vor Freigabe AST-/Byteabgleich der unveränderten Verträge, benannte neue
  und relevante vorhandene Regressionen, bereinigter Bericht, frisches
  deaktiviertes Paket, Commit und vollständige Hash-/Jobabschlussquittung.
- [ ] Root reviewt, integriert und entscheidet getrennten Metadatenmethoden-
  Smoke/Freeze/Preflight/native A1-Diagnose. Autorenarbeit behauptet weder
  abgeschlossene Methodenqualifikation noch Gainfix/A1-/Schadensabnahme.

## Offlineabschluss

29neue und63gezielte geerbte Fälle PASS; frisches Disabledpaket
`/srv/tse-a1-passive-xrecord-disabled-20261114`, Manifest
`63860770eab431a9178f6e57baaaa579eaefdcec4493a7af2e1d96c32443b8fa`,
77Runtime-/69Diagnostic-/14Collector-Pins und4bytegleiche Coredateien.
Keine native Getter-/Lookupqualifikation, kein Display-/Xlib-/TSE-/Fridastart.
Bericht `docs/reports/2026-11-14-a1-passive-xrecord-adapter.md` beschreibt
getrennten Root-Methodenlauf und offene Overhead-/A1-Gates.
