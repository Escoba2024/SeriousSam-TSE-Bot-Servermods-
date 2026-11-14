# A1: private Quittung der weiterhin fehlgeschlagenen Mappingprüfung

Status: OFFLINE vorbereitet, Review/Rootfreeze/neuer nativer Diagnosebeleg offen.
Plan: `docs/superpowers/plans/2026-11-14-a1-mapping-failure-receipt.md` (783b0e7).
Keine Runtime-, Compiler- oder Frida-Ausführung durch den Autor.

## Beleg und Aussagegrenze

Der geschlossene A1-Lauf130456 bleibt FAIL, ResultSHA256
`3d33b79367b718bb9b38acc38bcf4634ed3493c23b566e27d18b464ce957fea5`.
Backend91 verglich vollständige Modulzeilen aus `/proc/PID/maps` gegen den
vorherigen Pin; Rolle/Modul und tatsächliche Differenz wurden nicht archiviert.
Signaturprüfung90 war zuvor erfolgreich. Keine konkrete Mappingursache bewiesen.

Der Trace936eaf68b869fbd8a26297749320aac0bb9f3c7d5ce2b7a83f62948b1de1cd2d
enthält zwei vollständige passive Input→Action/Compose-Paare,0Faults/0Drops und
korrekte EDI-Bindung an Entry/Return, ausschließlich Nullbewegung. Kein
Gameplayinput, keine Kalibrierungs- oder A1-Abnahme.1,142s ist Gesamtvorbereitung
inklusive1,039sArm; die Assertion lag binnen ungefähr25ms nach Armreturn.
Das frühere Null-Action-Ergebnis beschreibt diesen neuen Lauf nicht.

## Enger Eingriff

Der Offlinebuilder verlangt exakt den vollständigen Rootparent
`/srv/tse-a1-instruction-probe-root-frozen-20261114`, Manifest
`7521e53cec5bdfac3263adef82dd6ed6a2d654ee53259ce5c3505beacfec0c39`,
Collector `b5f5f6c51fdd5248c9616e7fd1e4c0eaa57219ced7181832cdbae43418861f2f`.
Alle vererbten Runtime-, Diagnostic- und Collectorpins wurden vor Kopieren frisch
geprüft. Frischer Zielpfad erforderlich; alter Rootfreeze bleibt unverändert.

An genau Backend91 wird dieselbe ausgewählte Zeilenliste benannt. Dieselbe
Ungleichheit erzeugt sofort einen `AssertionError()` mit strukturierter Quittung:
Rolle, gebundene PID/Start, Modul/Modulpfad, erwartete SHA/Base/Dateisignatur,
bereits geprüfte aktuelle Signatur, exakte expected/actual-Modulzeilen und die
bereits einmal gelesenen vollständigen Prozessmaps. Kein zusätzlicher Prozess-,
Dateistat- oder Speicherread, keine Normalisierung, Filteränderung, Ausnahme,
Rebaseline oder neue akzeptierte Mapkonfiguration.

`own_identity` schreibt ausschließlich diese Failurequittung ins bestehende
private Evidenceverzeichnis und wirft denselben Fehler weiter. Datei0600 mit
O_EXCL; kein Überschreiben/Linkfolgen. IO-/JSONfehler bleiben ebenfalls FAIL,
die ursprüngliche Assertion bleibt Exceptioncontext. Identitäts-/Signaturfehler
bekommen keine falsche Mappingquittung. Erfolgsablauf unverändert.

Zusätzlich nur deaktivierte Ausführungsgates, neuer Namespace/Evidenceprefix,
Collector-PRIVATE und konsistente aktive Pins. Hook-JS/Guards, InputScope,
CP/Input-/ACK-/EPSlogik, Rotationreader, Worker-/Originalreceiptbody, sämtliche
Fristen, Raten, Hostgates und Restorecode unverändert; kein Hook-/Inputzuwachs.

## Verifikation und ausführbarer Handoff

Fünf vorbereitete Tests wurden nach Root-A4-Closed zuerst RED wegen fehlender
Implementierung ausgeführt; nach Implementierung GREEN. Sie führen die
TATSÄCHLICH transformierten Verifier-/Handler-Python-ASTs mit Stubdateien aus:
gleicheMapsPASS; ungleicheMapsAssertion+vollständigeQuittung; exakt ein vorhandener
Mapsread/Dateistat; Identitäts-/Signaturfehler bleiben unverändert; Writefehler
bleibtFAIL mit ursprünglichem Kontext; vorhandene Quittung wird nicht ersetzt.
Zwei zusätzliche vollständige Paket-/Ablehnungschecks bestanden. Insgesamt
sieben gezielte Tests PASS1,224s, keine Skips; kein nativer Methodenbeleg.

```sh
cd tools
python3 -m unittest test_a1_mapping_failure_receipt test_prepare_a1_mapping_failure_receipt -v
```

Neues deaktiviertes Paket:
`/srv/tse-a1-mapping-failure-disabled-20261114`, Manifest
`84cc6ec64c6c6b3b4ae8539f47508e3b808f1597957bc8c6d47541e6971aa361`,69Runtimepins.
Die vollständigen Controller-/Backenddiffs liegen privat darin. Keine
Retailbytes oder tatsächlich ausgelesenen Prozessmaps im öffentlichen Repository.

Reproduktion ausschließlich offline in einen neuen Pfad:

```sh
python3 tools/prepare_a1_mapping_failure_receipt.py --destination /ABSOLUTER/NEUER/PFAD
```

Root prüft Quellen/Pins unabhängig, friert eine eigene neue Kopie konsistent ein
und führt nach frischem exklusivem Preflight genau einen bestehenden NoFire-
Diagnoselauf aus. Eine Mappingabweichung muss weiterhin sofort FAIL erzeugen;
die Quittung dient ausschließlich ihrer tatsächlichen Ursachenanalyse. Keine
Kalibrierungs-/A1-Freigabe und kein automatischer Retry aus dieser Vorbereitung.
