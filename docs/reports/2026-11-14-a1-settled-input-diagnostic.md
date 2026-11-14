# A1: begrenzte ACK-Korrektur und Original-Controls-Diagnose

Status: **portable Prüfung bestanden, native ABI-/Ursachenprüfung offen**. Keine
Spielprozesse gestartet, keine Live-Dateien verändert. Der private neue Launcher
ist weiterhin durch `RUNTIME_REVIEWED=False` gesperrt. Dies ist keine A1-Abnahme.

## Befund und Änderung

Die erhaltene native Prescan-aus-Probe vom 12.11. endet bei ihrem ersten
`ack-look_horizontal`-Sample, Tick 14,500037: Server und Client zeigen −6 Grad
gegen erwartete −3 Grad. Der Controller verglich die Verstärkung bereits vor
seiner eigenen Stabilitätsbeobachtung von 0,1 nativen Sekunden. Ein stabiler
Endwert dieses Eingabeereignisses ist dadurch nicht dokumentiert.

[Der Quellpatch](milestone-a-20261114/settled-ack.patch) verschiebt genau diesen
Vergleich hinter die bestehende Stabilitätsbedingung. EPS, Verstärkungsbereich,
kalibrierter Sollwert, Deadline, Monotonie, Lebens-/Prozessidentität und sämtliche
Schadens-/Fire-Grenzen bleiben unverändert. Insbesondere bleibt ein Überschwingen
mit anschließender Richtungsumkehr FAIL. Der historische −6-Grad-Fehler wird
hierdurch nicht nachträglich bestanden.

Original-`GameMP.dll` SHA256
`1c41da35b3fc47378c407b770e1bd1dcc2b7e6bf676c140586bc6035461d4208`:
Die statische Disassemblierung bei `0x60850390` bestätigt die unabhängige
Controls-Glättung. Globalflag bei Controls+0x15c und Achsenflag bei Axis+0x14
wirken als Oder; der Zweig berechnet `(aktuell + vorherig) * 0,5`.
Gesicherte Controls0-/Default-Dateien enthalten `GlobalSmoothAxes`, obwohl die
einzelnen Achsen `NotSmooth` tragen. Prescan und Engine-Mausfilter schalten diese
separate Glättung nicht aus. Ihre tatsächliche Beteiligung am Fehler ist offen.

## Artefakte und Pins

Privates Paket: `/srv/tse-a1-settled-input-private-20261114`.
Neue Quellen und Tests liegen im Branch `codex/20261114-a1-settled-input`.
Der veröffentlichte Bericht enthält keine Retaildateien, Profile oder Rohlogs.

| Datei | SHA256 |
| --- | --- |
| Ursprünglicher eingefrorener Paketmanifest | `1819bbfdb593acd251b1f6741e19d83ce18fa54f6256d1d7f7828153950c11df` |
| Ursprünglicher `colt_preparation.py` | `46bccee495c276166fcc9f48c7041d5aec8e9a39e9694eabc76e08b74fc9dc56` |
| Korrigierter `colt_preparation.py` | `a8b86fc863a9d3b06da7641df0744573b9de66a36af7f846b5a877fe1973d61e` |
| Unveränderter privater Basisreader | `b5627e91094594d0e1a0fae52ef8dc36be33f416436b92d0286396d37b31463a` |
| Gesichertes Controls0-Ausgangsprofil | `5d525c46993be88d45941fe14f4638fa001ba9583d1151a27d6df9129d9b9d9b` |
| Vorbereitetes Controls0 ohne globale Glättung | `76a947f52a88271133e1f9699da38858c14f293f8fe04700594fa3b85788b6d9` |

Der separate passive Reader `tools/a1_controls_diagnostic.py` prüft die originalen
Engine-/GameMP-Modulhashes und sechs geladene Instruktionsbereiche einschließlich
HIGHLOW-Relokation. Er folgt dem Original-Gamepointer, der expliziten lokalen
Slot-/Profilzuordnung und dem nach Namen verifizierten Engine-`_pInput`-Export.
Ausgabe: globales/individuelles Glättungsflag, effektives Oder, Achsenbindung,
Einfluss, vorheriger und integrierter Wert sowie aktueller Engine-Achsenwert.
Zwei gleiche Lesepässe sind ausdrücklich keine atomare Beobachtung. Änderungen,
Kurzlesungen, ungültige Zeiger oder andere Mausbindungen führen zu ungültiger
Evidenz mit erhaltenen Rohlesewerten.

## Ausführbare Offline-Prüfungen

```sh
cd /srv/tse-a1-settled-input-20261114
TSE_A1_PACKAGE=/srv/tse-a1-settled-input-private-20261114 python3 -B tools/test_a1_settled_ack.py
TSE_A1_PACKAGE=/srv/tse-a1-settled-input-private-20261114 python3 -B tools/test_a1_controls_diagnostic.py
cd /srv/tse-a1-settled-input-private-20261114
python3 -B -m unittest test_colt_preparation test_rotation_diagnostics test_colt_reader
```

Ergebnis: 3 neue ACK-Tests, 9 Controls-/Originalguard-Tests und 35 bestehende
Controller-/Reader-Tests bestehen. Die neuen Verhaltensprüfungen liefen zuvor
gegen den alten Controller rot: Teilantwort wurde voreilig abgewiesen;
abweichender Endwert wurde vor Stabilität entschieden. Der korrigierte Controller
akzeptiert erst stabil korrekte Antworten und verwirft weiterhin stabil falsche
Verstärkung sowie Überschwingen/Richtungsumkehr vor Fire.

Die zusätzliche vollständige Discovery der kopierten historischen Tests ist
**nicht grün**: 67 Tests, 3 FAIL. Zwei Sticky-Profile-Tests erwarten ältere
Rohlesen-Anzahlen ohne die später ergänzte Prescan-Beobachtung; dieselben zwei
FAIL wurden separat mit unverändertem Originalcontroller reproduziert. Der dritte
Test verlangt absichtlich den alten Controller-SHA und erkennt den vorliegenden
Quellpatch. Keine dieser Prüfungen wurde umgeschrieben. Eine anfänglich fehlende
Testumgebungsvariable, Planfixture und Evidenzablage wurden anschließend ergänzt;
der wiederholte Lauf hatte keine entsprechenden Umgebungsfehler mehr.
[Maschinenlesbare Prüfung](milestone-a-20261114/settled-input-offline.json).

## Nächster nativer Schritt des Hauptagenten

Zuerst Original-Labbelegung und exklusive Locks frisch prüfen. Originalmodule,
Prozessstartticks, Restoretransaktion und Ressourcen binden. Das neue Paket vor
einem Launcherstart eigenständig einfrieren; die historische Paketfreigabe gilt
hierfür nicht. Der Launcher wurde nicht um einen automatischen Folgeversuch
erweitert.

Ein einzelnes passives Controls-Sample eines bereits eindeutig eigenen
Original-Labprozesses ist nach dieser Bestandsprüfung ausführbar:

```sh
python3 -B /srv/tse-a1-settled-input-20261114/tools/a1_controls_diagnostic.py sample \
  --reader-package /srv/tse-a1-settled-input-private-20261114 \
  --pid "$OWN_VANILLA_PID" --start-ticks "$OWN_VANILLA_START_TICKS" \
  --root /srv/tse-arena-isolated-20261111/vanilla --local-slot 0
```

PID und Startticks stammen aus der eigenen frischen Prozessquittung, nicht aus
einem historischen Wert. Vor der Intervention anhand der gemessenen Profilnummer
die tatsächlich ausgewählte Controls-Datei bestätigen. Die vorbereitete
`Controls0-nosmooth.ctl` darf nur bei passendem ursprünglichem Hash und Profil 0
innerhalb der versiegelten, ruhenden Lab-Restoretransaktion eingesetzt werden.
Andere Dateien, Sensitivität, Beschleunigung und Prescan bleiben unverändert.
Nach dem Start müssen globales und beide effektiven Glättungsflags tatsächlich 0
sein; Dateiinhalt allein reicht nicht. Native Zuordnung und Lesekosten sind noch
nicht gemessen. Kein Original-Gameplaylauf wurde durch diese Vorbereitung ersetzt.

Eine neue isolierte Profilvariante lässt sich ohne Installation erzeugen:

```sh
python3 -B tools/a1_controls_diagnostic.py prepare-controls \
  --source /srv/tse-a1-settled-input-private-20261114/Controls0-before.ctl \
  --output /srv/tse-a1-settled-input-private-20261114/Controls0-new-variant.ctl
```

Das Ausgabeziel muss fehlen. Nur genau ein globaler Glättungsschalter wird
ersetzt; alle übrigen Bytes bleiben erhalten. Ob dies die Eingabeabweichung
beseitigt, muss eine neu gebundene native Probe entscheiden. Es wird weder eine
Eingabeduplizierung noch Glättung als endgültige Ursache behauptet.
