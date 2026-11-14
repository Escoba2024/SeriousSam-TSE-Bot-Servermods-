# A1: vollständiges deaktiviertes Nosmooth-Diagnosepaket

Status: **offline vorbereitet; native Ausführung weiterhin gesperrt**.
Paket: `/srv/tse-a1-nosmooth-controller-20261114`.
Manifest-SHA256:
`02bdaa2f9a8bfaab9292751f265875366c05636f0f2542d61e5d545e941e184d`.

Das Paket übernimmt den vollständigen eingefrorenen Prescan-V2-Manifest mit
unveränderten `host_budget`, `world`, `executable_resolution`,
`fixture_preflight_pins`, `preparation` und `originals`. Die alte Reviewquittung
bleibt ausdrücklich historische Elternprovenienz. Sie qualifiziert das neue
Paket nicht. Alle 52 neuen/übernommenen Runtime-Abhängigkeiten wurden nachgehasht;
keine externe Erwartung wurde durch einen neu erfassten Wert ersetzt.

Der vollständige [Controller-Quellunterschied](milestone-a-20261114/nosmooth-controller.patch)
umfasst den bereits geprüften ACK-Vergleich nach Stabilität sowie drei begrenzte
Einbindungen: Import des Helfers, Profilinstallation nach `transaction.seal()`
und eine einmalige passive Controlsprüfung unmittelbar vor der vorhandenen
Kalibrierung. `RUNTIME_REVIEWED=False` und `runtime_reviewed=false` bleiben aktiv.
Startupbefehle, normale Eingaben, Kontrollen, Zeitgrenzen und Cleanup bleiben
ansonsten unverändert. Die neue Controlsprüfung wird nicht bei jedem ACK gelesen.

## Installation und Nachweis

`a1_nosmooth_intervention.install()` akzeptiert ausschließlich die vorhandene
versiegelte `FileTransaction` und deren genau gesichertes
`vanilla/Controls/Controls0.ctl`. Ausgangshash:
`5d525c46993be88d45941fe14f4638fa001ba9583d1151a27d6df9129d9b9d9b`.
Modus, Eigentümer und Gruppe müssen weiterhin zur Sicherungsquittung passen.
Nur `GlobalSmoothAxes` wird durch `GlobalDontSmoothAxes` ersetzt; erwarteter
Ausgabehash:
`76a947f52a88271133e1f9699da38858c14f293f8fe04700594fa3b85788b6d9`.
Andere Controlsprofile oder Rollen werden nicht geändert. Die bestehende
Transaktion sichert und restauriert auch diese Datei.

Vor jedem Kalibrierungsinput erhält der Helfer den bereits vorhandenen eigenen
Vanilla-`InventoryReader`. Er nimmt genau ein passives Controls-Sample für
Local-Slot 0. Tatsächliches Profil 0 sowie globales, beide individuelle und beide
effektive Glättungsflags müssen alle exakt Integer 0 sein. Der vollständige
Erfolgs-/Fehlersample wird unter `controls-effective.json` und im Resultbericht
gesichert. Ein falsches Profil, Glättung, Lesefehler oder Journalausfall setzt
sticky FAIL und unterbindet die Kalibrierungsclosure vollständig. Ein späterer
günstiger Sample kann denselben fehlgeschlagenen Lauf nicht wieder freigeben.

## Verifikation

53 relevante Tests bestehen: sechs Installations-/Restore-/Gate-Tests, drei
ACK-Regressionsfälle, neun Controls-/Originalguard-Tests und 35 vorhandene
Controller-/Reader-Tests. Die neuen Helfertests waren zunächst wegen fehlender
Implementierung rot. Installationstests verwenden die echte vorhandene
`FileTransaction` in temporären Verzeichnissen. Sie prüfen unveränderte BotA-Datei,
exakte Rückkehr der Vanilla-Bytes und des Dateimodus sowie Abweisung von Hash- und
Metadatendrift. Gate-Tests prüfen falsches Profil/Flags, Rohlesenfehler und nicht
schreibbare Ergebnisablage jeweils ohne nachfolgende Eingaben.

Die vollständige historische Discovery bleibt **67 Tests, drei FAIL**. Zwei sind
bereits mit unverändertem Elterncontroller reproduzierte Sticky-Profile-Tests
mit alten Rohlesen-Annahmen. Der dritte verlangt unveränderte alte
Controllerfunktionen/-hashes und erkennt die vorliegende bewusste Einbindung.
Die historischen Tests wurden nicht umgeschrieben. Namen und Quittungen stehen
in [der maschinenlesbaren Prüfung](milestone-a-20261114/nosmooth-offline.json).

```sh
cd /srv/tse-a1-settled-input-20261114
TSE_A1_PACKAGE=/srv/tse-a1-nosmooth-controller-20261114 python3 -B tools/test_a1_nosmooth_intervention.py
TSE_A1_PACKAGE=/srv/tse-a1-nosmooth-controller-20261114 python3 -B tools/test_a1_settled_ack.py
TSE_A1_PACKAGE=/srv/tse-a1-nosmooth-controller-20261114 python3 -B tools/test_a1_controls_diagnostic.py
cd /srv/tse-a1-nosmooth-controller-20261114
python3 -B -m unittest test_colt_preparation test_rotation_diagnostics test_colt_reader
```

## Übergabe an den Hauptagenten

Keine Spielprozesse wurden gestartet, keine Live-Dateien verändert. Vor nativer
Ausführung bleiben unabhängige Quellprüfung, aktuelle eigene Lab-/Lockbelegung,
sämtliche geerbten Prozess-/Welt-/Modul-/Ressourcen-Preflights und eine neue
Root-Freezequittung erforderlich. Der Hauptagent muss nach seiner Prüfung beide
Ausführungsgates freigeben und den dadurch veränderten Launcherhash im neuen
Manifest binden. Die alte Freigabe darf nicht kopiert werden.

Der danach vorgesehene einzelne Aufruf lautet:

```sh
python3 -B /srv/tse-a1-nosmooth-controller-20261114/run_dual.py --seconds 90
```

Im hier übergebenen Zustand endet dieser Pfad bereits an der deaktivierten
Reviewbedingung. Es gibt keine automatische Versuchsserie oder Wiederholung.
Die native Controls-ABI und Profilzuordnung sind noch nicht praktisch bestätigt;
der neue passive Gate muss sie zuerst tatsächlich lesen. Weder die Wirkung der
Glättungsintervention noch Originalschaden oder der erste Respawnzustand werden
aus den Offline-Prüfungen behauptet.
