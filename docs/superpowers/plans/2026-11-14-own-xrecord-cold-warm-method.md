# Own167: Cold5→Warm1 nativ belegen

Rootauftrag,14.11.2026. Implementierer `/root/candidate_audit`, separater WT
`/srv/tse-a1-five-request-audit-20261114` ab`a2dfab4777fd3752d424868c8d77bd62697fb30d`.
Claims ausschließlich neue Cold/Warm-Methodenquelldateien, deren gezielte Tests,
Builder und dieser Plan/Bericht. Bestehende Core-/A1-/Rootquellen und laufende
Nativefenster bleiben unangetastet. Keine Delegation.

## Frage und festes Ergebnis

Der geschlossene A1-Versuch return1/Counter26→31 beweist eine Fünfer-Spanne;
seine einzelnen Wireidentitäten fehlen. Statische Primärquellen und ELF liefern
die passende Cold-Kette XInputDiscovery→XTESTDiscovery→XGEDiscovery→GEVersion→
FakeInput. Diese Wirefolge und ihre Cacheabhängigkeit bleiben bis zu diesem
eigenen Methodenbeleg eine ungeprüfte Hypothese.

Genau eine Methodenqualifikation auf eigenem frischem Xvfb167, ohne
TSE/Wine/Frida und ohne Originalclient. Der vorhandene Auftrag deckt die
Ausführung; Root übernimmt sie nach technischer Vorbereitung und Sicherung.
Kein zusätzlicher Nutzerfreigabeschritt und keine neue Hüllenarchitektur.

Festes Programm auf einer einzigen frischen Driververbindung:

1. Vorhandene Driverinitialisierung öffnet/mappt eigenes Fenster und setzt
   Pointer400/300. Kein XTestQueryExtension-/XGE-Aufruf auf diesem Driver.
2. Recorder separat frisch execen. Versions-/Majorermittlung ausschließlich
   auf dessen eigenen Verbindungen; dies erwärmt nicht den Drivercache.
3. Zwei feste`XTestFakeRelativeMotionEvent(+12,0,0)` auf demselben Driver.
   Öffentliche Counter direkt vor und nach jedem C-Aufruf erfassen; kein Sync
   oder anderer X-Aufruf innerhalb dieses Intervalls. Anschließend normal
   XSync und bestehende eigene QueryPointer-Belege:412/300,424/300.
4. Cold: genau5Requests in der oben genannten Reihenfolge, mit tatsächlichem
   dynamischem XTEST-/GE-Major und passendem Namen/Minor/Parametern. Warm:
   genau1FakeInput. Je Return1; keine angenommene/ergänzte Sequenznummer.
5. Voller Start/End-/Callback-Free-/Context-Free-/Connection-/Child-/Display-
   Nachweis, eigene gespeicherte Quittungen und echte Prozessenden. Fehler
   bleibt FAIL; keine automatische zweite Methodenqualifikation.

PASS-Label ausschließlich`PASS_METHOD_COLD_WARM_LIBRARY_REQUESTS_ONLY`;
`a1_pass=False`, `retail_qualified=False`, `xi2_complete=False`, kein Gainfix.

## Kleinster Fork vorhandener Lösungen

Vor Implementierung die tatsächlichen Controller-/Driver-/Recorder-Schnittstellen
nochmals eng lesen. Geprüfter Coreparent:
`/srv/tse-own-xrecord-core-method-root-frozen-20261114`, Manifest`43d38e72…`.
Der Driver ruft bislang keine Versionsabfrage auf seiner eigenen Verbindung
auf; genau diese Eigenschaft beibehalten. OwnChild/IPC-/Freshdisplay-/PID-/
Socket-/Lock-/Cleanup-/Recordbudget-Hüllen wiederverwenden und ihre Originale
bytegleich erhalten. Neuer Methodenfork mit getrennten Pfaden/Prefix/Gates.

Nur methodenspezifisch erforderlich:

- Counterquittungen um die beiden tatsächlichen C-Aufrufe; zweiter fester
  Relativecall anstelle eines beliebig parametrisierbaren Programms.
- Zusätzliche Recordranges für core98QueryExtension samt Antworten und
  dynamischen GE-Major/minor0 samt Antwort; bestehende Pointer-/XTEST-Ranges
  weiterführen. Vorhandene Coredateien werden nicht mutiert; Änderungen am
  separaten Methodenfork müssen als kleiner Quelldiff nachvollziehbar sein.
- Enger Rohdecoder/Auditor: Extensionnamen, Request-/Reply-Sequenzzuordnung,
  dynamische Majors und tatsächliche feste FakeInputparameter überprüfen.
  Paket-/Wirelayouts vorher anhand tatsächlich verfügbarer Xorg-Primärheader
  und Quellen bestätigen, keine neue private Display-ABI.
- Echte Driververbindung über eigenes Fenster/Querysequenzen oder den bereits
  qualifizierten öffentlichen Ressourcenlookup binden. Keine Clientbase=PID-
  Gleichsetzung und keine Auswahl günstiger fremder Verbindungen.

Keine A1-Source, Inputfolge, ACK-/Gain-/EPS-/4er-Guardänderung. Keine weiteren
Events erzeugen, um einen Decoder zu füttern. Kein Methodenstart auf154 oder
einem belegten Display. Keine Liveänderung/zusätzlicher Dienst/Installation.

## Unveränderte Grenzen und Lifecycle

15sRecorder,1024Records,2MiBgesamt,16KiBjeRecord; Arm/Stop3s, Driverop2s,
Controller30s plus Cleanup5s je eigenem Kind. Mindestens8GiB Disk. Vorhandene
exklusive Locks, eigenes frisches167, PID/start/argv/CWD/Socketinode/ListenerFD,
Parentbindung und normale boundedOwnChild-Cleanupregeln übernehmen. Parent
lädt keine Xlib. Alle C-Callbacks fangen Fehler und geben Daten im Finally frei.
Timeout/Overflow/Parsing-/Ownership-/Cleanupfehler bleiben stickyFAIL; kein
Forcecleanup als normalen PASS verbuchen. Alte qualifizierte Methodenquittungen
bleiben erhalten und werden nicht zur neuen Cold/Warm-Abnahme umetikettiert.

## TDD und persistente Belege

Während022 läuft nur Textvorbereitung. Nach RootClosed zuerst den tatsächlichen
Forkvertrag und Primärlayouts prüfen, dann gezielte RED→GREEN-Fälle, keine breite
Suite. Neue Tests müssen die reale neue Decoder-/Auditorlogik ausführen:

1. Exakte Cold5/Warm1-Wirefixture samt gebundenen dynamischen Majors und
   Replies; kein PASS nur aus Counterdelta und Pointerpositionen.
2. Fehlender/falscher/umgeordneter Discovery-/GEVersionrequest, fehlende
   Replybindung, falscher Extensionname/Major oder zusätzlicher FakeInput.
3. Fremde Clientbase mit passenden Requests, falsche Queryfenster/-sequenzen,
   abweichende Returnwerte/Pointer und fehlende Rawrecords bleiben FAIL.
4. Cold1 beziehungsweise Warm5 bleiben als Widerspruch sichtbar, nicht durch
   günstige Verbindungswahl oder ein stilles Warmup normalisiert.
5. Ausgeschöpfte Budgets, IPC-/Childstart-/Stop-/Cleanup- und Schreibfehler:
   keine weitere Eingabe, normaler eigener Cleanup und ehrliche Fehlerquittung.
6. Deaktivierter frischer Paketbuilder prüft Coreparent/Quellen/Pins, feste167/
   zweiCalls/Grenzen/Claims; bestehende Corepakete bleiben bytegleich.

RED/GREEN-Ausgaben diesmal tatsächlich in privaten0600-Dateien sichern und
ihre exakten Pfade/Hashes im Bericht nennen; Tooltranskript und gespeicherter
Rohlog werden ausdrücklich unterschieden. Nach GREEN deaktiviertes Paket,
Pins/Quelldiff/Handoff/Commit an Root. Root prüft/friert separat ein und führt
genau eine Methode unter dem bestehenden Auftrag aus.

## Danach, nur bei tatsächlichem Methoden-PASS

Dann ist ein enger A1-Fixkandidat vorzubereiten: öffentliche
`XTestQueryExtension`-Vorbereitung auf der echten Controllertransportverbindung
außerhalb des Inputhotpaths und vor Recorderarm. Diese Bibliotheksinitialisierung
muss im Methodenbeleg die späteren Einzelcallintervalle tatsächlich erklären.
Sie ist kein zusätzlicher Mausimpuls. Jetzt weder implementieren noch ausführen.
`b-a>4`, ACK/Gain/EPS, tatsächliche Eingaben und Sicherheitsrelease bleiben
unverändert. Bei Methoden-FAIL erst tatsächlichen Widerspruch diagnostizieren;
keine Folgeversuchsserie und keine neue Hülle als Ersatz für den fehlenden Beleg.

Status: Plan/Text vorbereitet; noch keine Implementierung, kein OfflineRED,
kein Methodenlauf. Root022 läuft unabhängig; alle eigenen Rechenjobs beendet.
