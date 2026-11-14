# A1: belegte VMA-Partitionierung und exakte Bereichsinvariante

Status: Offline vorbereitet und gezielt geprüft; unabhängiger Review, Rootfreeze
und neuer nativer Diagnosebeleg offen. Implementierung begann erst nach
geschlossenem Yodeller-Fenster und tatsächlichem RED gemäß Rootplan988dd7f.

Der private Lauf133108 bleibt FAIL, Result
`d2755f6d65122a3f27dfee577c9539cb7a4224cb1ed6e46eb99209668ac5d239`.
Seine Quittung07785fd462ff9351cfe67b89d5a73b8918b043180a5fb3d737ca4a19e0b5f096
belegt erstmals die genaue Abweichung: Vanilla/Engine.dll,20Soll- gegen22Istzeilen.
Die übrigen19Modulzeilen sind bytegleich, Dateisignatur/Device/Inode/Pfad/Base
gleich. Die22Istzeilen stimmen exakt mit der Modulauswahl aus allen1070gesicherten
Prozessmapszeilen überein. Keine heutige Live-/Flottenaussage daraus.

| Vorher | Nachher | Dateioffset |
|---|---|---|
| 600c0000–600fe000 r-xp | 600c0000–600cd000 r-xp | 0 |
| im ersten Bereich enthalten | 600cd000–600ce000 r-xp | d000 |
| im ersten Bereich enthalten | 600ce000–600fe000 r-xp | e000 |

Die drei neuen Intervalle bilden dieselbe ursprüngliche Adressdomäne exakt,
lückenlos und ohne Überlappung ab. Ihre Dateioffsets folgen exakt der virtuellen
Adressverschiebung. Damit ist ausschließlich eine andere VMA-Partitionierung
bei gleicher gemessener Bytezuordnung nachgewiesen. Maps allein beweisen weder
Byteinhalt noch interne vm_flags/COWzustände noch die verursachende Operation.
Originaldatei-/Prozess-/Base-/Originalbytegates bleiben erforderlich.

## Bindender Vertrag der vorgesehenen reinen Funktion

Zwei Zeilenlisten sind genau dann gleichdeckend, wenn ihre virtuellen
Adressdomänen identisch sind und für jede enthaltene Adresse dieselben Rechte
einschließlich private/shared, Device, Inode, exakter Pfad und derselbe affine
Dateioffset gelten. Keine bloße Gesamtgrößen- oder Bildbasisprüfung.

Jede vollständige Sechsfeldzeile streng parsen. Positive, aufsteigend sortierte,
nicht überlappende Intervalle verlangen; ungültige/umgeordnete/duplizierte Rows
nicht durch Sortierung, Auslassen oder Reparatur kaschieren. Nur direkt
benachbarte Bereiche mit gleichen sämtlichen Identattributen und exakt
fortlaufendem Dateioffset zusammenfassen. Beide maximal zusammengefassten
vollständigen Listen exakt vergleichen. Bestehende gepinnte Lücken und
Rechte-/Offsetgrenzen bleiben erhalten. Kein Clipping, keine Seite oder Alias-
Mapping ignorieren; neue, fehlende oder anders zugeordnete Bereiche bleibenFAIL.

Die Funktion darf keine Dateien, Prozesse oder Speicher lesen und verändert
keinen Pin. Aufruf aus genau der vorhandenen Modulzeilenprüfung unter Nutzung
derselben bereits gelesenen Listen. Keine nachträgliche Sollwertübernahme nach
Attach, keine Frida-Ausnahme oder Seitenwhitelist. Echte Ungleichheiten erhalten
die bereits geprüfte private Failurequittung; PID-/Dateisignaturgates bleiben
unverändert. A1-Hooks, Inputs, ACK/Gain/EPS, TTL/Raten und Cleanup unberührt.

Vorbereitete Tests umfassen die tatsächlichen archivierten20/22Rows, identische
und alternative zulässige Partitionen, exakte Rechte/Fileidentität/Offsets,
bekannte Lücken, verlorene/zusätzliche Bereiche, Überlappung/Umordnung/Duplikate,
ungültige Rows und Pfade mit Leerzeichen. Backend-/Pakettests müssen anschließend
unveränderte Readanzahl, PID-/Signaturfehler, private Fehlerquittung und die
geschützten bytegleichen Komponenten prüfen. Diese Fälle wurden nach Ende des nativen Fensters ausgeführt; siehe Abschluss unten.

Vorgesehener Ablauf war zuerst gezielte RED-Beobachtung, Wiederverwendung
der reinen Funktion, Backendadaption und deaktivierter A1-Fork vom exakten unveränderten
Rootbd83f6e3ad7320e7eed5b9059ec1d107dc295dd60168803eb2cef78f607750ae.
Danach fokussierte Verifikation und unabhängiger Review. Root allein integriert,
friert ein und führt nach Preflight einen begründeten passiven NoFire-Versuch
aus. Kein alterFAIL wird umetikettiert, keine A1-Schadensfreigabe vorweggenommen.

## Gefundene vorhandene Lösung — Wiederverwendung statt Neubau

Die vom Nutzer verlangte erneute Bestandsprüfung fand den bereits geprüften
Entwurf vom12.11.2026:
`/srv/tse-milestone-a-evidence-20261111/a3-damage013-normalized-root-frozen-20261112`.
Sein im früheren Gesamtplan benannter Manifestpin ist
`d13a063c8fb6f51cd1706c2275b6d50a4eafc143a6420606ca052235e204acd3`,
Controllerpin e8e7299db776f5943c7d2fb399a8b12bd6a0e33522f683a0fe475d1d4f3e705e.
Das dort gepinnte `mapped_rows.py` hat erwartete SHA256
e2c194c1dc06ea463317be074d153d6679564e173fa9ef97bf1a3bfa53a93064;
diese Pins wurden während STATICONLY nur aus vorhandenen Metadaten gelesen;
nach RootClosed wurden Manifest, Helper und Testquelle frisch nachgehasht.

Die statische Lektüre zeigt bereits exakt die benötigte reine Funktion
`canonical_mapped_rows`: begrenzter Parser, vollständige Attributdeckung,
Adjazenz/Offsetkontinuität, keine Sortierung oder ausgelassene Bereiche.
Der Helper wird nach beobachtetem RED BYTEGLEICH wiederverwendet, keine zweite
Normalisierungsimplementierung gebaut. Seine vorhandenen Tests und privaten
Originalfixtures werden ebenfalls wiederverwendet; die neuen Tests ergänzen
den tatsächlichen20/22-Fall sowie den aktuellen Failurequittungsbackend.
Device und Inode bleiben wie im reviewed Helper zusätzlich in ihrer exakten
Kerneltextdarstellung gebunden; keine neue Darstellungsnormalisierung nötig.

Ruling: vorhandenen Helper unverändert übernehmen und ausschließlich an die
aktuelle A1-Fehlerquittungsstelle anbinden. Grund: Vertrag passt bereits und
Historie/Review bleiben nachvollziehbar. Falls die Bewertung falsch ist, könnten
unerlaubte Coverageabweichungen akzeptiert werden; deshalb adversarielle und
tatsächliche Archivtests vor neuem deaktiviertem Paket und unabhängigem Review.
Der aktuelle A3-Workerparent besitzt diese Normalisierung bereits; keine
zusätzliche A3-Änderung aus diesem A1-Befund ableiten.

## Offlineabschluss und ausführbarer Handoff

Elf neue vorbereitete Fälle scheiterten zuerst tatsächlich wegen fehlendem
Helper/Adapter; zwei zusätzliche Paketfälle ebenfalls RED. Danach wurde der
historische Helper bytegleich übernommen. Keine neue Normalisierungsfunktion.
Der neue Backenddiff umfasst nur Helperimport und Vergleich beider vorhandener
Listen. Ungültige Daten (`ValueError`) bleiben fehlgeschlagen und durchlaufen
weiter die bestehende Assertion mit privater vollständiger Failurequittung.
Kein weiterer Prozess-/Speicher-/Dateistatread und keine Änderung der Startpins.

13 neue Fälle sowie die sechs unveränderten historischen Mappingfälle und
sieben vorhandene Failurequittungs-/Paketregressionen bestanden gemeinsam:
26 Pythonprüfungen, keine Skips,2,549s. Zusätzlich31 unveränderte A1-JS-VM-
Prüfungen bestanden.57 gezielte Offlinefälle insgesamt, keine Runtime-/Build-/
Fridaausführung durch den Autor. Der tatsächliche20/22-Archivtest und historische
Originalfixtures benötigen die vorhandenen privaten Belege; sie sind kein
Cloud-/Retail-Laufzeitnachweis. Ein erster reiner Helperaufruf verwendete den
falschen CWD und fand das Testmodul nicht; das ist separat ein Aufruffehler,
kein fachlicher RED-Beleg. Korrigierter CWD liefert acht reine Helperfälle PASS.

Neues deaktiviertes Paket:
`/srv/tse-a1-exact-mapping-coverage-disabled-20261114`, Manifest
`1b272b30a66b489342cb14dd8623984fc561166b1d213cf1a2b22d53ce4c6dbb`,70Runtimepins.
Der private Backenddiff liegt darin. Hook-JS/Guards, Failurequittungshelper,
CP/InputScope/Rotationreader, Originalbytesprüfung und Restore bleiben bytegleich.
Runner/Worker/Collector ändern zusätzlich nur Gatesfalse/Namespace/PRIVATE.
Alle Runtime-/Diagnostic-/Collector-Pins sind konsistent; alte Freezes bleiben
unverändert. A3 besitzt die historische Normalisierung bereits und wird hier
nicht zusätzlich verändert.

```sh
python3 tools/prepare_a1_exact_mapping_coverage.py --destination /ABSOLUTER/NEUER/PFAD
cd /srv/tse-a1-exact-mapping-coverage-disabled-20261114
python3 -m unittest test_mapped_rows test_exact_module_mapping_coverage test_a1_exact_mapping_backend test_prepare_a1_exact_mapping_coverage test_a1_mapping_failure_receipt test_prepare_a1_mapping_failure_receipt -v
```

Root muss unabhängig reviewen, eigene neue Kopie konsistent einfrieren und nach
frischem Preflight genau einen begründeten NoFire-Diagnoselauf ausführen.
Gleichdeckung allein qualifiziert weder echte Gameplaykalibrierung noch
Erstzustandsschaden/A1. Alle alten nativen FAILs bleiben unverändert.
