# Deaktivierter eigener Core-XRecord-Methodencontroller

Status: ausschließlich Offlinevorbereitung. Kein XOpenDisplay, Xvfb, Xlibload,
TSE, Frida, Paketinstallieren oder nativer Methodenlauf. Grundlage ist der
Rootplan `2026-11-14-own-xrecord-core-method.md` auf Basis `0ab3774`.
Die zwischenzeitliche ausdrückliche Runtimepause wurde eingehalten; danach
wurden ausschließlich die von Root erneut erlaubten Offlinearbeiten fortgesetzt.
Die Live-Rückstellung auf Dev048/PublicGen2 wird dadurch nicht verändert.

## Erhaltene Ausgangsarbeit

Der ursprüngliche Worktree `/srv/tse-own-xrecord-core-method-20261114` wurde
nicht verändert. Seine drei Dateien wurden zunächst und bis zum Abschluss
byteidentisch übernommen:

| Datei | SHA256 |
|---|---|
| xrecord_core_method.py | ca4de66b67603924d00fb0acb4cf381f46877a76fc4e798784309649c52b27cf |
| test_xrecord_core_method.py | fba18e1de8fe47767d8066c6f87ee250e028f1d6d0475cd23c64fbac1d5caffe |
| test_xrecord_core_controller.py | 73957ef1618fecad5a2a03b872595308be42431b5a9cfa64ddffa930eaa9989c |

Die historische `UNEXECUTED`-Docstring der unveränderten Testkopie beschreibt
nur ihren damaligen Entwurfszustand; die tatsächlichen heutigen Läufe stehen
unten. Root hatte zuvor18ParserfällePASS und10ControllerfälleRED beobachtet.

## Aufbau und harte Grenzen

Fünf kleine Module trennen reinen Parser, eigene Prozesshülle, Parent,
Native-API und Recorder/Treiber. Der Parent lädt keine X-Bibliothek. Native
APIs liegen nur in frisch ausgeführten eigenen Pythonkindern. Deren PID,
Starttick, exakte argv, CWD, eigene Prozessgruppe und tatsächliches
`/proc/PID/environ`-DISPLAY werden geprüft. Es wird nur DISPLAY gelesen und
veröffentlicht, kein sonstiger Environmentinhalt. Fehlende/doppelte/überlange
Environmentfelder bleiben FAIL. Kinder erhalten nur DISPLAY/PATH/LANG.

Unmittelbar nach Popen existiert eine private0600-Startquittung vor jedem
/proc-Leseversuch, danach eine volle Bindungsquittung. Auch ein fehlgeschlagener
Teilstart behält den Popenhandle, räumt genau dieses eigene Kind begrenzt auf
und hinterlässt soweit möglich eine private Failure-/Reapquittung.
IPC ist16KiB begrenzt; falsche oder boolesche Seriennummer, EOF, Timeout,
überlange Daten und Identitätswechsel bleiben stickyFAIL. Keine Kindhandlung
führt nach einem Fehler einen Methodenimpuls erneut aus.

Nur ein vorher freies Display167 mit eigener exklusiver Methodensperre und
gepinntem Xvfb ist vorgesehen. Der Listener wird über eigenen PID/Start,
X-Lock-PID, Socketdatei, den tatsächlichen SO_ACCEPTCON-Listenerinode aus
/proc/net/unix und den FD desselben Xvfb gebunden; verbundene Socketkopien
mit gleichem Pfad werden nicht mit dem Listener verwechselt. Kein vorhandenes
Display, kein Wineserver und keine Spielrolle wird verändert oder beendet.

Limits bleiben: Recorder15s/1024Records/2MiBGesamt/16KiBPayload,
Arm3s/Stop3s, Treiberoperation2s, Controller30s plus5sCleanup je eigener Rolle.
Der Worker besitzt zusätzlich eine echte OS-Alarmfrist; Blockaden nativer
APIs können den Parent nicht blockieren. Normales Stop wird zuerst versucht.
Nur präzise eigene Methodenkinder dürfen nach Timeout terminiert/reaped
werden; jede solche erzwungene Bereinigung bleibt FAIL. Cleanup versucht
Recorder, Treiber und Display auch nach vorangegangenem Fehler unabhängig.

Der Treiber erstellt ein eigenes Fenster, initialisiert400,300 vor Arm,
sendet genau einen relativen+12-Request, bestätigt412,300 über die öffentliche
XQueryPointer-API, sendet genau einen Warp400,300 und bestätigt diesen Ort.
Keine weiteren Inputs oder Wiederholungen. XNextRequest wird über seine
öffentliche exportierte Funktion aufgerufen; keine private Displaystruktur.

Der Recorder besitzt getrennte Steuer-/Datenverbindungen. Er verlangt die
beobachteten Versionen RECORD1.13/XTEST2.2, tatsächlichen dynamischen
XTEST-Majoropcode, exakte ausgewählte Request-/Reply-/Core-Motion-Ranges und
StartOfData vor dem ersten Methodenimpuls. Callback-Ausnahmen verlassen die
C-Grenze nicht. Payloadgrenzen greifen vor string_at; FreeData steht im finally.
Fehler, abgewiesene Records, Verlust und Overflows sind keine Nullmessung.
Rohrecords liegen ausschließlich im privaten, mengenbegrenzten JSONL-Stream.

Eigene Clientbindung entsteht aus dem vom eigenen Treiber erzeugten Fenster
und seinen echten aufgezeichneten QueryPointer-Requests, Sequenzen und
Antworten, denselben Clientbasen bei XTEST/Warp und den zugestellten eigenen
Fensterereignissen. Eine Clientbasis wird niemals einem PID gleichgesetzt.
Deviceereignisse mit id_base0 bleiben ohne erfundene Clientherkunft.
Device- und zugestellte Motionkopien werden separat ausgewiesen.

## Primärquellen und während der Offlineprüfung korrigierte Annahmen

Der korrekte bestehende private Primärpfad ist
`/srv/tse-a1-xrecord-method-inventory-20261114/.codex/evidence/xorg-primaries/`,
mit den beiden Originalarchiven und deren `.selected`-Unterverzeichnissen.
Der ältere Inventorytext meinte nicht den späteren WIP-Worktree. Diese Dateien
und die ursprünglichen Hashes wurden gegen den Inventorybericht geprüft.

Zusätzlich wurden ausschließlich offizielle Xorg-Quelldokumente per HTTPS
privat gelesen, niemals installiert:

- libX11-1.8.7.tar.xz: `05f267468e3c851ae2b5c830bcf74251a90f63f04dd7c709ca94dc155b7e99ee`.
  Xlib.h: `748265b305975ae8396cdb310bcafa47d338211c977bfda9bf88d187a3a37c03`.
  Öffentliche Prototypen XCreateSimpleWindow1621, XDefaultRootWindow1773,
  XNextRequest1810, XQueryExtension2984, XQueryPointer2997, XWarpPointer3528;
  die sechs hier nachgeprüften Xlib-APIs sind im lokalen ELF tatsächlich exportiert.
- Die offizielle RECORD-Bibliotheksspezifikation `recordlib.html`:
  `aea9fa484ff73de0ddcaf3160048d73da5f203171e2a7495c1b0adb9555388bd`.
- xorg-server-21.1.12.tar.xz:
  `1e016e2be1b5ccdd65eac3ea08e54bd13ce8f4f6c3fb32ad6fdac4e71729a90f`;
  record/record.c: `c0b7908a5b6ed6c852ca76571043aaaf32d2800cda9185d8af98badb340e8a80`.
  Das ist offizielle Implementierungsevidenz, keine Behauptung identischer
  Ubuntu-Quellpatches. Der reale Server bleibt ein gesondertes Methoden-Gate.

XRecordAllocRange muss laut öffentlicher API verwendet werden. Deshalb
allokiert der Worker alle vier Ranges über diese API und gibt sämtliche
Allokationen auch bei Teilfehlern mit XFree frei. Die reine Parserfixture
behält native32Byte von RecordRange und das tatsächlich vom gelesenen
XRecord.c verwendete24Byte-Wireformat strikt getrennt; der ältere anders
benannte32Byte-Makrowert beweist keine32Byte-SendRange-Payload.

GetContext liefert aktuelle Einzelclients plus FutureClients. Beim Enable
wird die Datenverbindung ausdrücklich unregistriert: unsere drei echten
Verbindungen plus FutureClients ergeben vorher4 und danach3 Einträge.
Außerdem rekonstruiert der Server seine Ranges aus Protokollmengen; ihre
Zeilenanzahl/Packung ist kein Invariant. Der Validator vergleicht deshalb
exakte Protokollunionen. Er akzeptiert keine zusätzlichen/fehlenden Opcodes,
Ereignisse, Erweiterungsspannen oder Flags und begrenzt Strukturanzahlen.
Die relevanten Quellen sind recordlib-AllClients/GetContext und
ProcRecordGetContext/ProcRecordEnableContext im offiziellen record.c.

Der bereits nativ benutzte Wrapper
`/srv/tse-a1-release-deadline-root-frozen-20261114/x11_endpoint.py` hat frisch
SHA `652147c86c52ce3a49afa7ef39c499df7c7a16a357259b4e09b66b2b8d40cb2b`;
dieser Wert steht auch im dortigen SourceManifest. Sein XOpenDisplay- und
XQueryPointer-Pfad wurde als Gegenkontrolle gelesen; er wird nicht verändert.

Offizielle Quellen:
https://www.x.org/releases/individual/lib/libX11-1.8.7.tar.xz
https://www.x.org/releases/X11R7.7/doc/libXtst/recordlib.html
https://www.x.org/releases/individual/xserver/xorg-server-21.1.12.tar.xz

## Verifikation und offene Abnahme

RED wurde jeweils vor der zugehörigen Implementierung beobachtet:
fehlende Controller-/Native-/Worker-/Binding-/Paketfunktionen, fehlende private
Teilstartquittung, boolesche Reply-ID, erwarteter statt tatsächlicher
DISPLAY-Wert, fehlendes/doppeltes/überlanges Environment, falsche
GetContext-Clientzahl/Range-Packung sowie ausgelassene XRecordAllocRange.
Der erste Prozesszwischenlauf hatte zusätzlich einmal eine Identitätsabweichung
vor dem ersten IPC. Es gibt dafür keine belegte native Ursache und keinen
Produktionsretry; die scharfe Identitätsprüfung bleibt bestehen. Ein früherer
nichtdeterministischer Test für falsches DISPLAY wurde durch die tatsächlich
trennende /proc-Fixture ersetzt und nicht als Displaybeleg übernommen.

Finaler gezielter Befehl (nur diese benannten Module, keine tools-Discovery):

```sh
PYTHONPATH=tools python3 -m unittest test_xrecord_core_method test_xrecord_core_controller test_xrecord_core_process test_xrecord_core_native test_xrecord_core_binding test_xrecord_core_worker test_xrecord_core_orchestration test_prepare_xrecord_core_method -v
```

Tatsächlich ausgeführt: **61/61 PASS in2,236s**, keine Skips.
Privates deaktiviertes Reviewpaket:
`/srv/tse-own-xrecord-core-method-disabled-20261114`,14frisch geprüfte Quellpins,
Manifest-SHA256 `bb80d1ac85d8edc49e629fe36a3906186cbd382dda7aae1d3eb4b343b87e0b8b`.
Private Offlinequittung: `.codex/evidence/xrecord-core-offline-result.json`.
Auch die drei Dateien im originalen WIP wurden anschließend nochmals direkt
gegen ihre Anfangshashes gelesen und stimmen bytegenau überein. Die Prozessfälle starten ausschließlich
kleine eigene Python-Fakekinder, die geschlossen und reapgeprüft werden.
Alle übrigen Fälle sind Parser, lokale OS-Fixturen oder ABI-förmige Fakes.

Drei Code-Gates und das Manifest bleiben deaktiviert. Root muss vor einem
Methodenlauf unabhängig reviewen, eine eigene Freeze-Kopie erzeugen, nur dort
die Gates ändern, alle betroffenen Quellpins erneuern und den freien eigenen
Display-/Prozess-/Ressourcenstand frisch prüfen. Vorgesehener späterer Aufruf
ist ausschließlich Root-Freeze/xrecord_core_controller.py mit einer frischen
privaten --directory; dieses Autorenpaket verweigert jede Ausführung.

Der maximal mögliche Erfolg lautet PASS_METHOD_PARTIAL_CORE_REQUESTS_ONLY.
RECORD-/XTEST-Verfügbarkeit, tatsächliche Core-Motionabdeckung, Ressourcen-
und Latenzkosten sowie normale native Cleanupwege sind weiterhin UNGETESTET.
Keine XI2-Vollständigkeit, kein Retail-/A1-PASS, keine Erklärung des Gainfehlers,
keine geänderte A1-Toleranz und keine Freigabe einer Bot-Promotion.

## Abschließender Diskcheck-Folgecommit

Root beauftragte nach geschlossenem Spätjoinfenster ausschließlich die noch
offene Abschlussprüfung. Eine vorab ausgeführte Fixture mit8GiB minus1Byte
ergab zunächst fälschlich PASS und blieb als beobachtetes RED erhalten.
Die einzige Produktionsänderung prüft nun nach sämtlichen Cleanupwegen den
tatsächlich gemessenen freien Abschlussplatz; unter8GiB fügt sie einen
stickyFAIL hinzu. Keine native API, Inputfolge oder Frist wurde geändert.

Finaler gleicher benannter Gesamtlauf: **62/62 PASS in2,239s**, keine Skips.
Neues unveränderliches deaktiviertes Paket:
`/srv/tse-own-xrecord-core-method-final-disabled-20261114`,14frisch geprüfte Pins,
Manifest-SHA256 `f8f5f47c037f539a017bf5d48212e35b01950028b27d72be4acde206e9651d4d`.
Das frühere bb80d1ac-Paket bleibt erhalten und ist nicht der finale Stand.
Drei Code-Gates und das Manifest sind weiterhin False; der ursprüngliche
WIP wurde nochmals gegen alle drei Anfangshashes geprüft und ist unverändert.
Private finale Quittung: `.codex/evidence/xrecord-core-final-offline-result.json`.
Keine Xlib-, Display- oder Runtimeausführung; alle gestarteten Fakekinder
sind geschlossen/reaped, es läuft keine unbeaufsichtigte Weiterarbeit.
