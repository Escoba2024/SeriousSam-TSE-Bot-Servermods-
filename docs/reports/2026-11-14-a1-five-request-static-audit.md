# A1: tatsächliche Fünfer-Spanne, statische Initialisierungskette

Reine Analyse des geschlossenen Laufs vom14.11.2026,20:50:26. Keine
Implementierung, Tests, Eingaben, Xlib-Aufrufe, Nativeprozesse oder Builds.
Eigenes Worktree ab`a2dfab4777fd3752d424868c8d77bd62697fb30d`;
Claim ausschließlich dieser neue Bericht. RED/GREEN-Ausgaben des vorherigen
Journalfixes existieren nur im Tooltranskript, keine nachträglich erfundenen
Logdateien.

## Tatsächlich belegt

Der erste Aufruf `XTestFakeRelativeMotionEvent(+12,0,0)` kehrte mit1 zurück.
Die öffentlichen Counter davor/danach waren26/31; lokale monotone Zeiten
1315855,347632290 und1315855,347849137, also0,216847ms. Die fünf tatsächlich
belegten Sequenzplätze überschreiten den unveränderten höchstens4-Guard.
Dies ist die unmittelbare Fehlerursache. Kein Clockfehler, kein ausgeführter
zweiter+12-Aufruf und kein ACK-/Gainbefund werden daraus abgeleitet.

Das Journal erhält den REJECTED-Datensatz; die gültige Liste bleibt leer.
Raw40 enthält ausschließlich19QueryPointer-Anfragen,19Antworten, Start und
Ende; alle40Callbacks wurden freigegeben, keine unbekannten/fehlerhaften/
verlorenen Records, Recorder normal beendet. Der Filter zeichnet core98
QueryExtension und GenericEvent-QueryVersion nicht auf. Die Ausnahme liegt
weiterhin vor dem normalen Transport-XSync. Deshalb fehlen sämtliche fünf
konkreten Wireidentitäten im aktuellen Archiv; auch FakeInput kann noch
gepuffert gewesen sein. Dies darf nicht zu einem angeblich beobachteten
Fünf-Request-Protokolltrace umgedeutet werden.

## Konkrete statische Erklärung

Offizielle libXtst1.2.3- und libXext1.3.4-Quellen sowie die tatsächlich
installierten ELF-Binaries liefern folgende Kette beim ersten Aufruf auf
einer noch nicht initialisierten Verbindung:

| Sequenz bei diesem Cold-Pfad | Request | Ursache und Gegenprüfung |
|---:|---|---|
|26|QueryExtension `XInputExtension`|Xtst `get_xinput_base`, XTest.c74–86; ELF2e9e ruft XQueryExtension|
|27|QueryExtension `XTEST`|Xtst find_display→XextAddDisplay→XInitExtension; ELF2ed6→Xext683b→X112d092|
|28|QueryExtension `Generic Event Extension`|Xext registriert jede Nicht-GE-Extension bei XGE; extutil.c124–126, Xge.c95–127; ELF69db→6490→64fe→XInitExtension|
|29|GEQueryVersion|xgeExtRegister→_xgeCheckExtInit→_xgeGetExtensionVersion; Xge.c134–196/302–312; ELF69f2→4a10→4adc _XGetRequest|
|30|XTEST FakeInput, RelativeMotion+12|XTest.c229–248; ELF45fb _XGetRequest, anschließend return1|

Das erklärt exakt vier Bibliotheks-Metadatenrequests plus einen FakeInput.
Der häufig übersehene Anteil sind die zwei Generic-Event-Requests. Die ELF-
Strings bestätigen `Generic Event Extension`; _XGetRequest inkrementiert den
Sequenzzähler einmal je angelegtem Request (X1144dff). XNextRequest liefert den
nächsten Sequenzwert (X112a3f0).

Die Tabelle ist eine quell-/disassemblygestützte Rekonstruktion für den
Cold-Pfad, keine native Einzelrequestbeobachtung des geschlossenen Laufs.
Eine eigene Methodenprobe muss Coldzustand, tatsächliche Requests und den
Unterschied zum Folgeaufruf noch direkt belegen. Die Analyse trägt weder ein
pauschales `5 erlauben` noch einen bereits umgesetzten Warmup des Originalclients.
Der vorhandene Guard bleibt unverändert. Root koordiniert die Methodenprobe
innerhalb des bestehenden Nutzerauftrags; keine neue Nutzerfreigabe ist nötig.

Installiert: libXtst6 `2:1.2.3-1.1ubuntu0.1`, libXext6
`2:1.3.4-1build2`, libX11-6 `2:1.8.7-1ubuntu0.1`.
ELF-SHA256:

- Xtst:`a29f93b5c3eb10744ae503dbc9280f9e709061b9b8529f604e961fb77e4f2b70`
- Xext:`2907e6a996465de5b32a0dd10534d4416b87f1dee5670aaa7b19301a1fc93f44`
- X11:`edd2ddf6e00a81c40b8645f7dbb6d6603c6a0a78d583bdbe7491d8a84de6e3b6`

Primärquellen, begrenzt im Speicher gelesen, nichts installiert/extrahiert:
[libXtst1.2.3](https://xorg.freedesktop.org/releases/individual/lib/libXtst-1.2.3.tar.bz2),
ArchivSHA`4655498a1b8e844e3d6f21f3b2c4e2b571effb5fd83199d428a6ba7ea4bf5204`,
XTest.cSHA`bb99ec88549c6d59cab3f2475ab4cbc8319d6f416d81d47ceaf4d5bf84a5db60`;
[libXext1.3.4](https://xorg.freedesktop.org/releases/individual/lib/libXext-1.3.4.tar.bz2),
ArchivSHA`59ad6fcce98deaecc14d39a672cf218ca37aba617c9a0f691cac3bcd28edf82b`,
extutil.cSHA`785d3f8e1f346f1d881dd8843a97e75e104cd5332e912189f7dc1b1dc237bae8`,
Xge.cSHA`01fbc45b3f03a4db4aface41b11c4ea58a6ed8901ae78a51ee30cf644fe8820d`.
Xge.c ist Latin1; ein erster UTF8-Decode scheiterte, danach korrekt gelesen.
Keine Quellenänderung oder Nativequalifikation daraus.

## Kleinster nächster Methodenbeleg im bestehenden Auftrag

Getrennte deaktivierte Own167-Methode ohne TSE/Wine/Frida, frischer Execdriver
und separater Execrecorder. Bestehende Freshdisplay-/PID-/Socket-/Lock-/8GiB-
und boundedOwnChild-Hüllen wiederverwenden. Grenzen unverändert15s,
1024Records/2MiB/16KiB, Arm/Stop3s, Driverop2s, insgesamt30s plus Cleanup5s.

Der Driver darf vor dem ersten FakeInput auf seiner tatsächlichen Verbindung
keine XTestQueryExtension-/XGE-Warmupfunktion aufrufen. Der vorhandene Driver
öffnet/mappt/queryt nur ein eigenes Fenster; dessen erste Relativeaktion ist
daher als Grundlage geeignet. Versions-/Opcodeermittlung erfolgt ausschließlich
im separaten Recorderprozess auf dessen eigenen Verbindungen.

Nur diese eigene Methode ergänzt Recordranges und Rohdecoder für core98 samt
Extensionnamen und Antworten sowie den dynamischen GE-Major/minor0 samt Antwort.
Keine unveränderte Coredatei oder produktive A1-Filter stillschweigend ersetzen.
Reale Driververbindung über eigene Fenster-/Querysequenzen beziehungsweise den
qualifizierten öffentlichen Ressourcenlookup binden, niemals Clientbase=PID.

Genau zwei feste+12Relativecalls auf derselben Driververbindung: beim ersten
und zweiten jeweils vorhandene öffentliche Counter unmittelbar vor/nach der
C-Funktion erfassen, danach regulär XSync und eigene QueryPointer-Belege.
Erwartete Methode: erster Coldcall genau5 mit der obigen vollständigen
Sequenz, Folgecall genau1 FakeInput. Eigener Pointer400→412→424, je tatsächlicher
Return1, vollständiger Request-/Reply-/End-/Free-/Closebeleg und0Fehler.
Keine Counterwerte durch Annahmen ergänzen; jeder Widerspruch bleibt FAIL.
Die Methode beobachtet die fünfer Spanne, sie lockert den A1-Guard nicht.

Root führt nach Quellenreview, Offline-Decoder-/Lifecycle-TDD und Sicherung
genau eine eigene Methodenqualifikation aus. Während des derzeitigen022-Laufs
bleiben Implementierung/Tests/Methodenausführung pausiert. Der konkrete Plan
steht in`docs/superpowers/plans/2026-11-14-own-xrecord-cold-warm-method.md`.
Keine Aussage zu doppeltem Engineinput, Wine-Cursorcache, vollständigem XI2
oder A1-Abschluss.

Private Archivpins: Result`269295bf…`, Manifest`e26d3c6e…`,
Attemptjournal`62bed0eb…`, Rawstream`16a897ff…`; volleHashes in der privaten
RootEV-Diagnosequittung. Historischer Lauf bleibt FAIL, Root664Dateien/
8Absenzen/3Closedlogs-RestorePASS wird als Rootbeleg übernommen.
