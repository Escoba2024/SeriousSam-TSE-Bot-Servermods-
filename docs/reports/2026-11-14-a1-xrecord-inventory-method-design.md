# A1: XRecord-Bestand und kleinster getrennter Methodenentwurf

**Nur statischer Bestand und Entwurf zur Rootprüfung. Nicht ausführungsfreigegeben.**
Basis `f78a1fd`; keine Installation, kein XOpenDisplay, kein Display-/Methoden-/
Wine-/Frida-/TSE-/Inputstart. Kein Paket und kein Implementierungscode erstellt.
Der Gain-Fehllauf144306 bleibt FAIL; Diagnosecommit `4415be9` bleibt maßgeblich.

## Tatsächlich vorhandener lokaler Bestand

| Bestandteil | Vorhanden / Grenze |
|---|---|
| libXtst | `/lib/x86_64-linux-gnu/libXtst.so.6` → `libXtst.so.6.1.0`; Paket `2:1.2.3-1.1ubuntu0.1` |
| libX11 | x86_64 und i386; Paket `2:1.8.7-1ubuntu0.1` |
| libXi | x86_64, Paket `2:1.8.1-1build1` |
| XRecord-Symbole | QueryVersion/CreateContext/GetContext/EnableContext/EnableContextAsync/ProcessReplies/DisableContext/FreeContext/FreeData tatsächlich im ELF exportiert |
| Werkzeuge | `/usr/bin/{Xvfb,xev,xdpyinfo,xwininfo,xlsclients,nm,readelf,python3}` vorhanden; keine Displaywerkzeuge ausgeführt |
| xtrace / xinput / pkg-config | nicht im PATH gefunden |
| Entwicklerheader | record.h/recordproto.h/recordconst.h/XTest.h/XInput2.h/XI2proto.h/Xproto.h und xcb/record.h an Standardpfaden nicht vorhanden; gezielte Dateisuche ohne weiteren Treffer |
| Dev-Pakete | libxtst-dev/libx11-dev/libxi-dev/x11proto-dev nicht als installiert bestätigt; kein unversionierter libXtst.so-Link |
| Python | ctypes und select vorhanden; Xlib/xcffib/xcb im geprüften `/usr/bin/python3` nicht gefunden |
| Xvfb-RECORD/XTEST/XInput | **NICHT abgefragt und NICHT bewiesen**; Bibliothekssymbole beweisen keine Serverextension |

Gelesene lokale Hashes:

- libXtst.so.6: `a29f93b5c3eb10744ae503dbc9280f9e709061b9b8529f604e961fb77e4f2b70`
- libX11.so.6: `edd2ddf6e00a81c40b8645f7dbb6d6603c6a0a78d583bdbe7491d8a84de6e3b6`
- libXi.so.6: `a51348c921ce1a35123fa7c99dc59bfd3e815be6829874fe15ae55172901d3e4`
- Xvfb: `6b27845931670c8c9b3ce7423696a452ce3cab1c7f316ce5f7ea7f1297fa2f84`

`xev` beobachtet zugestellte Ereignisse seines Beobachtungskontexts und ist
kein Ersatz für Requests plus nicht zugestellte Geräteereignisse aller
eindeutig eigenen Displayclients. `xtrace` wäre ohnehin ein zusätzlicher
Proxy-/Verbindungsweg; es ist lokal nicht vorhanden.

## Offizielle Primärquellen und Formatbefunde

Die fehlenden Header wurden ausschließlich aus offiziellen Xorg-Quellarchiven
gelesen, nicht installiert:

- [libXtst1.2.3](https://www.x.org/releases/individual/lib/libXtst-1.2.3.tar.bz2),
  Archiv-SHA `4655498a1b8e844e3d6f21f3b2c4e2b571effb5fd83199d428a6ba7ea4bf5204`.
  record.h: `744232d2fa7c64d158ef3bd535fe723c0f55d9cb1bebf65408d385002efc391c`;
  XRecord.c: `e502689fb91a37d7778eca8ef606c1ff7f84ef0acd0aad9f66067fe9722534c4`;
  XTest.c: `bb99ec88549c6d59cab3f2475ab4cbc8319d6f416d81d47ceaf4d5bf84a5db60`.
- [xorgproto2024.1](https://www.x.org/releases/individual/proto/xorgproto-2024.1.tar.xz),
  Archiv-SHA `372225fd40815b8423547f5d890c5debc72e88b91088fbfb13158c20495ccb59`.
  recordproto.h: `1572d360f49327192887869a5ca5532a0841b69d45a970c0b7fb73b8f0ed8168`;
  XI2proto.h: `b419ceee6265f5e1b31ae4f09ad611c27dfc350be7daee0b16d9eb3fc69b62a5`.

Private Lesekopien liegen ausschließlich unter
`.codex/evidence/xorg-primaries/` dieses Worktrees. Die Upstreamversion passt
zur lokalen libXtst-Basis, beweist aber nicht deren Ubuntu-Patchdelta oder
den konkreten Xvfb-Serverstand. Direkte GitLab-Rawzugriffe über das Webtool
waren nicht erreichbar; die offiziellen Xorg-Archive waren lesbar.

Aus diesen Headern/Quellen ergibt sich:

- Native `XRecordInterceptData` hat XID/Time/unsigned-long-Felder und einen
  Datenpointer; `data_len` zählt **4-Byte-Einheiten**. Die spätere native
  ctypes-ABI darf nicht mit dem festen32-Bit-Wireformat verwechselt werden.
- RECORD-Metadaten: Kategorie, id_base, server_time, client_seq,
  client_swapped und Rohdaten. Datumflags1/2/4 fordern Serverzeit pro
  Server-/Clientelement und Clientsequenz an. Byteordnung muss berücksichtigt
  werden; unbekannte/ungültige Formate dürfen keine Erfolgsquittung erzeugen.
- Core WarpPointer-Opcode41 hat24Byte; QueryPointer38 liefert eine32-Byte-
  Antwort. XTEST hat dynamischen Majoropcode, FakeInput-Minor2 und36Byte.
  `XTestFakeRelativeMotionEvent` erzeugt im gelesenen Quellcode genau einen
  MotionNotify-FakeInput mit detail=True, root=None und dx/dy in rootX/rootY.
  XIWarpPointer ist dagegen XInput-Minor41 und36Byte; Majorwerte nicht hart
  erfinden. Ein vollständiger Requestbeleg muss diese mögliche Form beachten.
- **Wichtige XI2-Grenze:** XRecord.c1.2.3 behandelt Serverevents im Parser
  pauschal als32Byte. Xproto.h/XI2proto.h definieren längere GenericEvents.
  Ubuntu-Patch-/Serververhalten hierfür ist ungeprüft. Daher GenericEvent
  nicht blind einschließen und aus fehlenden XI2-Daten niemals Abwesenheit
  weiterer Bewegung ableiten. Zunächst höchstens
  **PARTIAL_CORE_MOTION_OR_REQUEST_TRACE**.
- Auch `EnableContextAsync` liest in der Quelle zunächst synchron
  StartOfData. Ein vermeintlich asynchroner API-Name ersetzt keinen externen
  begrenzten Exec-Worker und dessen Parentfrist.

Die offizielle [RECORD-Protokollspezifikation](https://www.x.org/releases/X11R7.7/doc/recordproto/record.html)
unterscheidet device_events von delivered_events. Erstere werden auch ohne
Zustellung aufgezeichnet; Grabs unterdrücken sie nicht. WarpPointer und
XTestFakeInput erzeugen zugehörige Geräteereignisse. Requests werden vor
ihrer Ausführung erfasst: ein aufgezeichneter Warprequest allein beweist
keinen erreichten Pointerort.

Die [RECORD-Bibliotheksspezifikation](https://www.x.org/releases/X11R7.7/doc/libXtst/recordlib.html)
beschreibt getrennte Steuer-/Datenverbindungen, Start-/EndOfData und
XRecordFreeData. Geräteereignisse können id_base0 haben; eine Client-ID ist
kein PID. Für Core-Motion-Geräteevents sind nur Zeit, Root und Root-X/Y als
gültig festgelegt. Zusätzliche Felder dürfen keine erfundene Zuordnung liefern.

## Kleinster Methodenentwurf, noch keine Ausführungsanweisung

1. **Root prüft zunächst diesen Entwurf.** Danach getrennte reine Own-X11-
   Methodenprobe auf einem frisch exklusiv belegten Wegwerfdisplay; niemals
   vorab am TSE-Display154. Keine Wine-/Frida-/TSE-Abhängigkeit für die erste
   Qualifikation. Keine Paketinstallation nötig, falls eine korrekt geprüfte
   ctypes-Bindung mit den vorhandenen versionierten Bibliotheken ausreicht.
2. Native Strukturen, Protokolllängen, Endianness und dynamische Opcodes durch
   fokussierte Offlinefixtures prüfen; malformed/oversized/unsupported-
   GenericEvent bleibt Fehler oder ausdrücklich nicht abgedeckt. Keine
   Bibliothek ersetzen, um eine Qualifikation vorzutäuschen.
3. Root startet einen frischen begrenzten Recorderworker mit zwei eigenen
   X-Verbindungen, eigenem Context, identifizierbarem Kontrollclient und
   ausschließlich bekannten Probeclients. Extension/Version, StartOfData,
   ausgewählte Ranges und korrekte Client-/Displayzuordnung müssen tatsächlich
   belegt sein, bevor irgendeine eigene Methodenbewegung stattfindet.
4. Minimaler bekannter Ablauf auf ausschließlich eigener Probeoberfläche:
   ein +12-FakeInput, anschließender eigener Warp zum vorigen Zentrum;
   eigens erzeugte QueryPointer-Antworten dürfen **nur in dieser Methodenprobe**
   die tatsächlichen Positionen gegenprüfen. Aufgezeichnete Requests,
   device_motion und delivered_motion separat zählen, damit eine doppelte
   Darstellung desselben Ereignisses nicht als zweite Bewegung gilt.
   Dynamische XI2-Requests dürfen roh erkannt werden; ihre Ereignisabdeckung
   ist ein gesondertes, noch offenes Methoden-Gate.
5. Nach normalem Disable über die Steuerverbindung vollständiges EndOfData
   abwarten, Context freigeben, beide Verbindungen schließen und das Ende
   jedes eigenen Kindes nachweisen. Parent-IPC/Start-/Stopfristen und feste
   Queue-/Byte-/Zeitlimits müssen **vor Implementierung** im Rootplan stehen.
   Verlust, Timeout, unklarer Childstart oder fehlendes Ende bleibt stickyFAIL;
   keine fremden X-Server/Wineserver/Gameprozesse terminieren. Xlib bleibt
   ausschließlich im Worker mit klarer Verbindungs-/Threadzuständigkeit.
6. Erst nach getrenntem Review und bestandenem Methodennachweis kann Root
   einen passiven Einsatz am eindeutig eigenen154 planen. Bestehende
   TSE-Hooks/Inputfolge/ACK/Gain/350-ms-Grenze bleiben unverändert. Keine
   zusätzlichen Pointer-/Win32-Abfragen dort einschleusen. Recorder mit
   und ohne Beobachtung kontrollieren; Ressourcen-/Latenzeffekt messen.

## Kausale Auswertung und verbleibende Grenze

Für das Problem müssen ein realer Warp/Recenter nach400 und eine spätere
Original-GetCursorPos-Rückgabe412 zeitlich passend gebunden werden.
Ein nachgewiesener zweiter Request oder neues Motion-Geräteevent nach412
würde eine X11-seitige Bewegung belegen. Clientzuordnung erfolgt nur über
tatsächlich gebundene Clientbasis/Socket/PID-Startbelege; id_base0 bleibt
ohne eigene Zuordnung. Geräte- und zugestellte Ereigniskopien nicht addieren.

Nur eine belegte serverseitige Position400 mit vollständig qualifizierter
relevanter Ereignisabdeckung könnte den weiterhin412 liefernden Win32-Pfad
oberhalb X11 eingrenzen. Ein Core-Teiltrace oder bloße Warp-Anfrage reicht
dazu ausdrücklich nicht: Cache-/Queue-/Recenterursache bleibt UNKNOWN.
Unbekannte XI2-Abdeckung verbietet eine vollständige X11-/Cache-Abgrenzung.

Serverzeit/Clientsequenz, Hostmonotonie und JS/Wine-Date.now getrennt
aufzeichnen. Serverzeitwrap, Empfangsverzögerung, Batchgrenzen und
Zeitzuordnungsunsicherheit müssen aus der Methodenprobe stammen; keine
Gleichsetzung anhand der IPC-Ankunftszeit oder bequemer Millisekundengleichheit.
Keine Summen-Gainauswertung oder dieser Entwurf qualifiziert CP-Zielsteuerung,
input_once, A1-Schaden oder öffentliche Synchronisationsfreiheit.
