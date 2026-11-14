# XRes: lokale Client-PID-Attribution, Bestand und Methodenvoraussetzungen

Reine Leseprüfung am14.11.2026, separater Worktree ab`d67f802`.
Keine Installation/apt-update, Displayöffnung, Xlib-/XRes-/Nativefunktion,
TSE-/Originalwiederholung, Eingabe, Build oder Implementierung. Alte Verbindung
U bleibt **UNKNOWN**; ihre Prozesse/Verbindungen sind bereits beendet.

## Tatsächlicher lokaler Bestand

`libxres1`, `libxres-dev`, `libxcb-res0` und dessen Devpaket sind nicht
installiert; ldconfig und die üblichen amd64/i386-/usr/local-Libpfade enthalten
keine XRes-/xcb-res-Bibliothek. Unter den geprüften Includeverzeichnissen liegen
keine X11-/XCB-Devheader. xlsclients/xprop existieren, xrestop fehlt.
Die gezielte Projektsuche ergab keinen vorhandenen XRes-Adapter. Vorhandener
XRecord-Ressourcenlookup bindet Clientbases, aber keine OS-PIDs.

Vorhanden sind Xvfb`2:21.1.12-1ubuntu1.8`, X11`2:1.8.7-1ubuntu0.1`,
libxcb1`1.15-1ubuntu2`; dessen generische Requestsymbole sind exportiert.
Eine neue handgeschriebene XCB-Protokollimplementierung ist derzeit nicht nötig:
der normale Distributionsweg für libXRes ist konkret verfügbar. Ob ein späterer
eigener Xvfb-Server X-Resource≥1.2 und lokale Client-PIDs tatsächlich liefert,
ist **nicht nativ geprüft** und folgt weder aus Paketname noch Symbolbestand.

## Regulärer kostenfreier Distributionsweg, nur simuliert

Konfigurierte Noble-main-Quelle: Hetzner-Ubuntu-Mirror. Candidate für libxres1
und libxres-dev jeweils`2:1.2.1-1build1`.

- `apt-get -s --no-upgrade install libxres1`:0Upgrades,1NEW,0Entfernungen;
  Paket6778Bytes Download,33KiB Installed-Size.
- Zusammen mit libxres-dev:0Upgrades,11NEW,0Entfernungen,33nicht aktualisiert.
  Zusätzliche Pakete:libpthread-stubs0-dev, xorg-sgml-doctools, x11proto-dev,
  libxau-dev, libxdmcp-dev, xtrans-dev, libxcb1-dev, libx11-dev, libxext-dev.
  Summe der Candidatefelder:1639904Bytes Download,5735KiB Installed-Size;
  kein Ersatz für Diskreserve inklusive APTcache/Logs.

Solver verlangt kein Upgrade bestehender X11/Xtst/Xext/XCB-Runtimes und kein
Daemonpaket. X11-/Xext-Devversionen passen exakt zu installierten Runtimes.
Dies ist eine tatsächlich ausgeführte Dry-run-Simulation, kein Installations-
oder Maintainerscriptnachweis. Root kann nach geschlossenem Nativefenster die
reguläre Bereitstellung mit frischer Simulation und Vorher/Nachher-Hashkontrolle
der gepinnten Bibliotheken durchführen. Fehlende Header sind kein externer
Restblocker. Dieser Autor hat nichts installiert oder zur Installation gestartet.

## Primärvertrag und wichtige ABI-Grenzen

[Offizielles libXres1.2.1](https://www.x.org/releases/individual/lib/libXres-1.2.1.tar.bz2)
und [Xorgproto2024.1](https://www.x.org/releases/individual/proto/xorgproto-2024.1.tar.xz)
wurden begrenzt im Speicher gelesen; nur ausgewählte Quellen privat0600 gesichert.
Kein Archiv in Systempfade entpackt. Maßgeblich:XRes.h, XRes.c und resproto.txt.

- Ab XRes1.2: `XResQueryClientIds`, Maske LocalClientPid=2. Als Auswahl genügt
  eine resource_base, auch wenn die Verbindung keine eigene Fensterresource
  besitzt; ebenso ist eine tatsächliche Resource-XID zulässig. Base ist kein PID.
- Lokaler Anfrager und lokal identifizierbarer Zielclient erforderlich. Fehlende
  PID/0zurückgegebene IDs sind zulässige Protokollergebnisse: keine Attribution.
- Extension/Version zuerst prüfen. QueryExtension ist Bool, QueryVersion liefert
  bei Erfolg1; **QueryClientIds liefert bei Erfolg Success=0**, nicht1. Zusätzlich
  sind eindeutige positive PID, passende Spec/Base/Maske und gültige Werte nötig.
- Header: XID ist native unsigned long; Spec enthält XID+unsigned int,
  Value enthält Spec+long length+void-pointer. LP64 ist nicht das32bit-Wirelayout.
  Rückgabewerte sind CARD32-Daten, keine long-Liste. Öffentlicher Getter
  `XResGetClientPid` liest CARD32 und liefert−1 bei fehlendem Wert; Arrays mit
  `XResClientIdsDestroy` freigeben. Prosa zur length-Einheit nicht als Ersatz
  für tatsächlichen Header/Reader/Getter verwenden. Keine native ABIqualifikation
  aus diesen statischen Definitionen behaupten.
- XRes liefert numerische OS-PID, keine Prozessstartgeneration. PID-Namespace,
  Prozessstartticks, ausführbare Datei/OwnChildbindung und Lebensdauer müssen
  separat legitim aus eigenen Prozessbelegen geprüft werden.

## Kleinste Inputs für einen separaten Root-Methodenplan

Zuerst nur eigene frische167-Methode ohne TSE/Wine/Frida/Input. Bestehende
Freshdisplay-/OwnChild-/IPC-/Normalclose-/Ressourcenhüllen wiederverwenden;
keine neue allgemeine Ausführungsarchitektur. libXRes/Header nach Bereitstellung
frisch pinnen und API/Layouts im tatsächlichen eigenen Prozess qualifizieren.

Bekannter OwnDriver mit eigenem Fenster und zwei gewöhnlichen X-Verbindungen
im selben PID; separater bekannter eigener Peer mit eigenem Fenster/anderem PID.
Vorhandene Ressourcengetters/Clientrange-Information für tatsächliche Bases
nutzen. Auf separater Metadatenverbindung Extension/Version, dann dieselben
Clients einmal über Resource und einmal über Base abfragen. Ergebnis muss die
beiden Driver-Verbindungen genau dem bekannten Driver-PID und den Peer dessen
bekanntem PID zuordnen. PID-Namespaces/Startgenerationen vor/nach jeder eigenen
Abfrage gleich; mehrdeutige/fehlende PID, Fehler, Timeout oder Prozessende bleiben
sichtbar. Keine _NET_WM_PID-Heuristik und kein Socket-/PIDraten als Ersatz.
Freigaben/Close/Reap und Libpins müssen tatsächlich geprüft werden.

Erst nach Methodenbeleg kommt ein enger zukünftiger A1-Metadatenadapter infrage:
Snapshot vor Arm, zweiter nach beendetem Input/Capture und vor Rollenclose,
außerhalb aller Release-/Inputhotpaths. Keine zusätzlichen User32-Proben:
der vorhandene Collector beobachtet bereits passive Original-GetCursorPos- und
SetCursorPos-Returns. Ein möglicher Wine-Helper-PID wird nicht ungeprüft dem
Originalprozess gleichgesetzt.

**Zwei Snapshots beweisen keine lückenlose Clientbase-Lebensdauer zwischen ihnen.**
Verbindungsende/-Neuanlage und Basereuse müssen separat belegt oder betreffend
Attribution als offen behandelt werden. Ebenso wird aus PIDgleichheit keine
eindeutige Zuordnung eines bestimmten SetCursorPos-Aufrufs zu einem Wirewarp.
Historische U-Attribution und A1-Gain/InputOnce bleiben unabhängig offen.
Keine neue Toleranz, kein Guardwechsel und keine Fixempfehlung aus diesem Bestand.

Primärquelldateien privat unter`/srv/tse-xres-attribution-primary-20261114/`:

| Quelle | SHA256 |
|---|---|
|libXres1.2.1-Archiv|`b6e6fb1ebb61610e56017edd928fb89a5f53b3f4f990078309877468663b2b11`|
|XRes.h|`b35400d3f5437eb6175479f564534c875504b49f7b8e6d9538595f57a5b376db`|
|XRes.c|`51f2200d59f05263b07adce203311751c9a059a7ba909f6d18fba9d4ffce016c`|
|resproto.txt|`e0b6933668423d84de06a41f5f94914bc912bcf29bc285dd1c884cbe742767d5`|
|XResproto.h|`7ebe2398f4eed157e0de1dcce51ebddad81c50b06137b18b5389fb594bee7ab3`|

APT-/Toolinventur ist im tatsächlichen Tooltranskript belegt, nicht als bereits
gespeicherter Log ausgegeben. Keine Fähigkeitsbehauptung über eine Display-
Verbindung oder Bibliotheksausführung; beides fand in dieser Untersuchung nicht statt.
