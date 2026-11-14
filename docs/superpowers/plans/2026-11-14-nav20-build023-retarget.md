# Build023: einzelner deaktivierter Red600-Retarget

> Umsetzung mit executing-plans/TDD im eigenen Worktree; Root allein baut,
> integriert, friert ein und startet native Prüfungen.

**Goal:** Genau einen deaktivierten Build023-Arm aus dem geprüften
Build022-RedStation600-Muster reproduzierbar vorbereiten.
**Architecture:** Neuer enger Builder mit fest gepinntem deaktiviertem022-Parent,
exakten drei Quelldeltas und bytegenauer Rücktransformation. Keine Leser-,
Botlogik-, Memorydecoder-, Input-, Timing- oder Gateänderung.
**Tech Stack:** Python-Standardbibliothek, Offline-unittest, AST-/Hashprüfung.
**Spec:** Rootauftrag nach abgeschlossenem Important-Origin-Fix eecac110;
ursprünglicher022-Plan und tools/prepare_navigation_build022.py bleiben erhalten.

## Globale Grenzen

- Ein Arm, Red Station, 600 Sekunden, acht eigene Bots plus unveränderter
  Originalclient, 20 FPS, Hard2, DEMON/tier3, Diagnostics0.
- Gleiche Navdaten, Seeds, Konfigurationen, V3-Protokoll, Leser, Raten, Ressourcen-,
  Close-/Restore-/Identity-/Fehlergates. Kein Retry oder automatischer Folgearm.
- Parent /srv/tse-nav20-022-red600-disabled-20261114,
  Manifest aa5783efbed7dc53a33ccee9f0755890eba6c2bdc8f5e9b43e76ff0059d648df.
- Keine erfundenen Buildpins. Tatsächliche023-Buildmanifest-/Source-/DLLpins
  liefert Root nach abgeschlossenem Build; zuvor nur Plan und Testfixtures.
- runtime_reviewed/qualifiziert/funktional/native_started bleiben false;
  alle Runtimegates und Rootreviewfreigaben bleiben deaktiviert.
- Alte022-Dateien, Pakete, FAILs und geschlossenen Belege bleiben unverändert.

## Reviewfokus

- Manifest/DLL/47Source-/28Overlaypins und Dateigröße vollständig frisch prüfen;
  falscher oder unvollständiger Kandidat scheitert vor Zielerstellung.
- Derivate nur aus genau deaktiviertem022-Parent; bereits/teilweise retargetete
  oder mehrdeutige Anker scheitern. Jede der drei Quellen reversiert bytegenau.
- Alle unveränderten Dateien bytegleich, alle externen/relativen Pins korrekt;
  keine alten022-Buildabhängigkeiten im023-Laufzeitabschluss.
- ImportantOriginRecovery proposal=1 ist nur ein Quellvorschlag, kein Beleg für
  akzeptierte Bewegung, Radiusankunft, Exit, Pickup oder native Heilung.
- Ein späterer nativer Bericht muss tatsächliche Positionen relativ zum originalen
  Radius und anschließenden bestehenden Exit separat belegen. Diagnostics0 lässt
  bislang unbekannte Weapon-unavailable-Gründe weiter UNKNOWN. Kein A4-PASS daraus.

## Aufgaben und Dateien

Neue Dateien: tools/prepare_navigation_build023.py,
tools/test_navigation_build023.py, dieser Plan,
docs/reports/2026-11-14-nav20-build023-retarget.md und eigener Claim.
Keine Änderung an022-Builder/Katalog/Tests oder Produktionscode.

- [x] Isolierten Worktree/Claim mit Ausgangscommit4190baf anlegen.
- [x] Konkrete Rootbuildpins entgegennehmen und Quellenabschluss nachweisen.
- [x] RED: fehlender023-Builder; echte Parentquelldeltas/reverse bytes;
  feste Bedingungen; fehlerhafte Manifest-/Sourcepins; frisches Ziel;
  vollständige Source-/Runtime-/Pythonpins und alle deaktivierten Gates.
- [x] Minimalen023-Builder nach022-Muster implementieren; tatsächliche Pins
  fixieren, alte022-Buildpins entfernen, eigene Ableitungsmetadaten hinzufügen.
- [x] GREEN und gezielte geerbte Policyprüfungen; deaktiviertes Paket in neuem
  Pfad erzeugen, Pins und Rücktransformation unabhängig aus dem Paket prüfen.
- [x] Report mit Commands/Ergebnissen/Paketmanifest/Grenzen und saubere Commits;
  Rootreview offen lassen. Keine eigene Runtime-/Buildausführung.

Abgeschlossen offline: tatsächlicher Rootbuild0234190baf/Tree9f3ef958,
77Buildpins frisch geprüft;22Tests PASS; neuer deaktivierter Fork mit
139Runtime-/71Source-/43Pythonpins.63Parentquellen bytegleich, drei exakt
reversierbar. Rootreview/Freeze/Native bleiben getrennt und offen.
