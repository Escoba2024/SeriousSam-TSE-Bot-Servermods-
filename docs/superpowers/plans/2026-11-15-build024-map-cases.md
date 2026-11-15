# Build024: vier deaktivierte Kartenfälle – Umsetzungsplan

> Umsetzung durch a4_diagnosis mit superpowers:executing-plans; keine Delegation.

**Ziel:** Vier eigenständig vorbereitbare, strikt deaktivierte 600s-Fälle für
Skulls, Little Trouble, Hole und Yodeller aus exakt dem bestehenden024Red600-
Parent erzeugen, um tatsächlich fehlende Kartenfunktion später zu prüfen.

**Architektur:** Neuer Offlinebuilder mit festem `--map`-Enum erzeugt genau ein
Paket je Aufruf. Runner erhält nur eigene Service-/Evidence-Namensräume.
`adapter_policy.options` bindet eine neue reine Fixed-case-Policy statt der
Red-only-Vergleichsoption; der bestehende Tiercheck bleibt bytegleich.
Alle übrigen geerbten Codes, Nav-/Worldkatalog und alle Laufzeitgates bleiben
bytegleich. Gegenrichtung stellt jeden der zwei veränderten Sourcefiles exakt
wieder her. Metadaten unterscheiden Kartenbeobachtung von Redvergleich.

**Tech Stack:** Python3 stdlib; AST-/Byte-/Hashprüfungen, keine Runtimeimports.

**Spec:** Rootauftrag15.11.; ursprüngliche Neunkartenmatrix in
`2026-11-11-milestones-a-b.md`; gepinnter024Red600-Parent
`/srv/tse-nav20-024-red600-disabled-20261114`, Manifest
`ea00456a147418f54db3b3b83c96a61a122ae8c5d652a3608317c5919c379f5a`.

## Feste Grenzen

- Build024/DLL192169fe…, Hard2, achtDEMON3/duelist+Original20FPS,600s,diag0.
- Gleiche Config/Seeds/Readraten/V3-Gruppen/Life-/Source-/Error-/Restoregates.
- Alle Runtime-/Rootgatesfalse, keine neue Freigabe aus Offlinevorbereitung.
- Ein Fall pro Aufruf, kein Retry, keine AutoSequence, kein Live-/Native-/Build.
- Keine Ersatzkarte; Compound/KuntaKinte und DesertTemple bleiben eigene offene
  Matrixpunkte. Keine Kopie/Retailbytes im öffentlichen Git.
- Skulls historische223/263s ohneUseful bleiben fehlgeschlagene Belege. Hole
  verlangt gesonderte Liquid-/Lava-/Höhen-/Recoverybewertung;600sallein ist kein
  Hazards-/Reset-/Paritäts-/A4nachweis. Yodeller020 ist keine024Abnahme.

## Konkrete World-/Navbindungen

Alle Pfade unter `Levels/LevelsMP/Deathmatch/`; Katalogsha
`11fc9080480dfa23cf0fc1f117a486b8f785daefbdeeb53dce26797c644018c3`.

| Case | World | WorldCRC | Nav-Datei unter Scripts/Cecil | NavCRC | Nodes |
|---|---|---|---|---|---:|
| skulls | WeGotSkullsNBonesToo.wld |42d03dd2|WeGotSkullsNBonesToo_9B573405.nav|70b554dd|296|
| trouble | DM_LittleTrouble.wld |4060d0dd|DM_LittleTrouble_6C64BF87.nav|980013d4|110|
| hole | Hole.wld |582bd040|Hole_1AD627D0.nav|d7cac057|139|
| yodeller | Yodeller.wld |b3c8ceeb|Yodeller_FC72665B.nav|a4a7950c|111|

Vorläufige statische Prüfung: vorhandene Archive-Central-Directory-CRCs passen;
alle vier NavSHA/CRC/BNMV6/Nodezahlen frisch geprüft. Kein frisch gerechneter
Vollarchivhash und kein geladener Worldnachweis. Builder soll für die genau
gewählte Karte auch WorldmemberSHA frisch lesen/prüfen; bestehender Runtime-
Assetvalidator bleibt unverändert.

## Reviewfokus

Falsche Karte/Default-Red, geänderte Duration/diag/build, unzulässiger Ersatz,
zu frühe Runtimefreigabe und stille geerbte Codeänderung jeweils fail closed.
Falsche Asset-/Build-/Sourcepins müssen vor Zielkopie scheitern. Eine tatsächliche
falsche Loadzeile, falsches Leben oder Source/Readbinding bleibt bestehender FAIL.

### Task1: echte RED-Tests, dann minimale reine Policy

- [x] Neues Testfile testet fehlenden Builder zuerst RED.
- [x] Fixed-case-Policy erlaubt nur vier Casekeys und exakt dazugehörige Karte,
  Build024,600,diag0; bool/NaN/599/601/diag1/Red/Ersatzkarten werden abgewiesen.
- [x] Tiercheck unverändert; tatsächliche gespeicherte Canonicalprofiles bytegleich.

### Task2: reproduzierbarer Offlinebuilder

- [x] Parentmanifest/alle Runtime-,Source-,Pythonpins sowie tatsächliche024-
  Build77pins (47Quellen+28Overlay+Manifest+DLL) frisch prüfen.
- [x] Gewählte WorldSHA/CRC und NavSHA/CRC/Header prüfen, keine neuen Assets.
- [x] Nur runner2Namespaces und adapter-options2Zeilen verändern; reverse exact.
- [x] Eine neue reine Policy+Builder+Tests kopieren, zusätzliche Runtimepolicy pinnen,
  alle Repins korrekt. Feste map_case-Metadaten ohne Vergleichs-/Freigabeclaim.
- [x] Existierendes Ziel/partielle Retargets/unbekannte Karte vor Mutation ablehnen.

### Task3: fokussierte Verifikation und Handoff

- [x] Adversariale Anchor-/Pin-/Assetmutation, geerbte Codes bytegleich und alle
  Quellenpins prüfen. Vorhandene024Retargetregression gezielt mitlaufen lassen.
- [x] Vier Pakete jeweils einzeln offline erzeugen; Manifeste/Controller/Pinanzahl
  und Grenzen im bereinigten Bericht sowie privater Quittung festhalten.
- [x] Report/Quellen/Tests committen; Jobs beenden und Root exakte SHAs liefern.

Abschluss:16gezielteTestsPASS, vier einzelne deaktivierte Pakete und private Vollquittung gesichert. Rootreview/Freeze/Native offen.
