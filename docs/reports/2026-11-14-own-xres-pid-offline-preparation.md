# Eigene XRes-PID-Methode: Offlinevorbereitung

Task1–3 des Plans sind als neue, standardmäßig deaktivierte Methodendateien
umgesetzt. Es wurde keine X-Verbindung geöffnet, kein Display gestartet, kein
Input ausgegeben und keine native Bibliotheksfunktion aufgerufen. Root allein
installierte die normalen Pakete und kompilierte/führte den separaten reinen
Headerlayoutbeleg aus. Die vorhandenen A1-/Core-/Cold-Dateien bleiben unverändert.

## Verhalten und Grenzen

Der Parent verwendet die bestehenden acht Display-/Disk-/Receiptguards
AST-identisch und kopiert `xrecord_core_process.py` bytegleich aus dem geprüften
Cold/Warm-Parent. Neuer fester Ablauf: eigenes frisches167, Driver mit zwei
Verbindungen und je einem ungemappten Fenster, separater Peer mit einer
Verbindung/einem Fenster, separater Attributor. Ausschließlich dieser frische
Execworker lädt X11/XRes; der Parent lädt keine X-Bibliothek. Kein alter
Cold-Driver-Initialisierer oder dessen Inputprogramm ist erreichbar.

Genau zwei Snapshotaufrufe fordern jeweils sechs Einzelqueries: je bekannter
Resource und deren tatsächlicher QueryClients-Base. Die pure Prüfung fordert
Success0, genau eine positive PID, Maske2, CARD32-Länge4, dieselbe nachgewiesene
Base-Range, genau drei unterschiedliche Verbindungen und dieselben echten
OwnChild-PID-/Startticks-/argv-/Display-/PIDnamespace-Identitäten vor und nach dem
Snapshot. Ein leeres Ergebnis bedeutet keinen PIDbeleg. Snapshotantworten werden
vor ihrer Validierung exklusiv0600 gespeichert. Ein falscher erster Snapshot
führt ohne zweiten Versuch zum normalen Cleanup.

QueryClientsarray und jede sichere IDarray-Allokation werden auch im Fehlerpfad
freigegeben und gezählt. Bei einer unmöglichen IDarray-Länge über64 wird kein
unbeschränktes Fremdarray durchlaufen; dies ist stickyFAIL und nur der eigene
Worker wird durch den geerbten begrenzten Cleanup beendet. Es gibt dafür keinen
Free-/Normal-PASS. Fehlgeschlagene Teilinitialisierungen schließen alle bereits
eigenen Verbindungen; Close ist idempotent. Errorhandler wird wiederhergestellt.

Controller30s, Attributor15s, übrige Kinder30s, Operation2s, Snapshot/Metadata3s,
Cleanup5s je Kind, IPC16384Bytes, höchstens64Clients. Native-Stop folgt
Attributor→Peer→Driver→Display. Reap, tatsächlicher Exit und Nativeclosebelege
sind für PASS erforderlich; Force/Timeout/fehlende Belege bleibenFAIL. Die
geerbte technische Cleanuphülle kann nach Timeout ausschließlich eigene Kinder
beenden; ein solcher Fall besteht nicht als normale Methodenqualifikation.

Zwei gleiche Snapshots beweisen keine lückenlose Base-Lebensdauer. Die alte
Verbindung U bleibt UNKNOWN; A1-/Retailqualifikation sowie Warp-/Cacheursache
werden nicht behauptet. Keine ACK-/Gain-/EPS-/Input-/Zeitgrenze wurde geändert.

## ABI und Herkunft

- Parentmanifest: `5749113983ea2462e60d84630d5823ff04f6f8b1b7147c3effc600f6124d928c`.
- Vorhandener Cold/Warm-Methodenbeleg: `45adbbad603ab49fde34e3b20f51c8b38ba62a0cb403937a27d15458ccd7a7d2`; Hüllenherkunft, kein XRes-Nachweis.
- Regulär bereitgestelltes libXRes1.2.1: `c2aefa4bf373492430f48aec108c5ead95e1dc757d52968775e905e23a2ad56c`.
- Öffentliches installiertes XRes.h: `b35400d3f5437eb6175479f564534c875504b49f7b8e6d9538595f57a5b376db`.
- Root-C-Headerlayout und ctypes stimmen exakt: XID/long8, pid_t/CARD32 4;
  Client16 mit Offsets0/8, Spec16 mit0/8, Value32 mit0/16/24; PIDmask2, Success0.
  Root prüfte C-Signaturen zusätzlich; dies ersetzt keine Displayfähigkeit.

## Gezielte Tests und gespeicherte Nachweise

20 neue Testfälle plus 8 unveränderte OwnChild-Fälle PASS, 0 Skips, 2,260s.
Nur pure Policy, Fake-C-Funktionen, Fake-Kinder und geerbte OwnChild-Modelle;
kein Xlib-/Display-/Compileraufruf. Die Fixture-PIDs sind erfunden.

Echte REDs wurden vor Implementation gespeichert: fehlende Policy, fehlender
Worker/Snapshotordnung, fehlender Controller sowie nicht erhaltene
Fehlerpfad-Freezähler, fehlender Builder und unzulässiger Lebensdauerclaim.
Ein früher zusätzlicher RED-Aufruf enthielt einen Testsyntaxfehler; er bleibt
separat erhalten und wird nicht als Verhaltens-RED gezählt. Danach wurde derselbe
gezielte fehlende Worker-/Ordnungsfall korrekt reproduziert.

Private0700-Belege: `/srv/tse-xres-pid-method-evidence-20261114/`.
Alle Logs0600 und exakte Hashliste in `offline-receipt.json`, SHA256
`f7b8317b3a7a64ad43b6f5193fbf6725c39609751e08e0013935db1c185bad65`.
Finales `green-final-focused.log`:
`bad20564631789559e4084decd085a21a468374e23dd26b9c40d680d7457cd3d`.

Reproduktion der engen Offlineprüfung:

```sh
cd /srv/tse-xres-pid-method-20261114/tools
python3 -B -m unittest test_xres_pid_method test_xres_pid_lifecycle test_xrecord_core_process -v
```

## Deaktiviertes Paket und Root-Handoff

Paket `/srv/tse-own-xres-pid-disabled-20261114`, Manifest
`21ff26bc3b5b60e42a6cd16874577ad3c176a7bff3544c6d01b930130e074a42`.
Frisch geprüft: 7 Paketdateien, 4 Bibliotheks-/Xvfbpins, 4 öffentliche Headerpins,
13 Herkunfts-/Provisionierungs-/ABIbelege. Beide Codegates und Manifestfalse.
Builder verweigert vorhandene Ziele und veränderte Parent-/Bibliothekspins.

Root prüft Quellen/Pins/NoInput/Lifecycle unabhängig, erstellt einen neuen Freeze
mit ausschließlich den beiden Codegates und Manifesttrue und repinnt die
geänderten Quelldateien. Kein bestehendes Paket überschreiben. Die vier
Projektlocks und der geerbte exklusive Own167-Methodenlock bleiben verbindlich;
frischer tatsächlicher Socket-/Lock-/Ressourcenpreflight und Sicherung voraus.
Erst dann genau ein Root-only Methodenfall über den neuen Controller.

Der Nativeaufruf ist noch offen. Es läuft kein unbeaufsichtigter Auftrag.
