# Build024: deaktivierter Red600-Controller vorbereitet

Genau ein neues deaktiviertes Paket wurde aus dem unveränderten023-Parent
abgeleitet. **23 gezielte Offlinechecks bestanden**, keine Runtime, kein
Rootfreeze, kein Build oder Deployment ausgeführt. Die äußere Hostbeobachtung
wird separat von Root verwendet; der Nativecontroller wurde dafür nicht geändert.

Paket: `/srv/tse-nav20-024-red600-disabled-20261114`.
Manifest-SHA256 `ea00456a147418f54db3b3b83c96a61a122ae8c5d652a3608317c5919c379f5a`;
Controller-SHA256 `a38de9486848783e6046d3be6be54724bd044deef5abcc211b0c53b3172e8fb9`.
Frisch geprüft: **139 Runtime-, 76 Source- und 45 Pythonpins**.

Die Bedingungen bleiben RedStation, Hard2, acht DEMON/Tier3-Bots plus
unveränderter Originalclient mit20FPS-Vorlage, 600s, Diagnostics0. V3-Lesevertrag,
Beobachter, Konfiguration/Nav, Seeds/Profiles, Protokoll, Messraten, Grenzen,
Cleanup und Wiederherstellung bleiben unverändert. Keine automatische Sequenz
oder Wiederholung; keine tatsächlich gemessenen FPS aus einer Vorlage behauptet.
Runtime-/Review-/Qualifikationsflags und beide privaten Freigaben bleiben false.

## Tatsächliche Herkunft und enges Delta

Der bereits abgeschlossene Root-MSVC-Build wurde hier nur lesend überprüft:

- Manifest `8903d7db0437f8c9ff0f71e056523be35d9c6ef75c165e2f0491cb67818691c9`.
- Quelle `100bda43eb46c7d671d71b7a50fae673a9e4406e`, Tree
  `a1c049f440ed1600a718c07ef3fcd5477668250f`.
- DLL `192169fe8396bfe1fb9c49419657b9146120c64eb3ac15095ac50a6f8659753c`,
  438272 Byte; alle47 Quellen und28 Overlays frisch gehasht. Zusammen mit
  Manifest/DLL sind77 Buildpins vollständig validiert.

Parent `/srv/tse-nav20-023-red600-disabled-20261114`, Manifest
`51d72a2cf233ff87d2f0cac0d3ad2a532f6f287e6ef62bd154b43e6e4ba8e5e8`.
68 Parentquellen bleiben bytegleich. Genau drei Runtime-Dateien ändern sich:

| Datei | Exaktes Delta |
|---|---|
| run-a4.py | DLLpfad024, getrennte Service-/Evidencenamespaces, zwei Kandidatenlabels |
| adapter_policy.py | DLLhash024 und Arm024 an beiden vorhandenen Policyaufrufen |
| navigation_comparison_policy.py | Ein zusätzlicher Katalogeintrag024 mit tatsächlicher Herkunft |

Jeder dieser Texte wurde invers **bytegleich** zum Parent geprüft. Im Paket
liegen die drei `.024.diff`-Dateien. Alle übrigen geerbten Dateien, alten Builder,
Pakete und FAIL-Ergebnisse wurden unverändert erhalten. Neue Dateien sind nur
Builder/Test und ihre Dokumentation; keine Botlogik oder Memorydecoder geändert.
Manifestpfade/Hashes werden auf das neue Paket und den tatsächlichen Build
umgebunden; alte023-Buildpins ersetzen keine024-Herkunftsprüfung.

`CecilGroundReplan` belegt höchstens einen erfolgreichen Source-Replanreset.
Tatsächliche Bewegung, ursprüngliche Radiusankunft und Aufnahme brauchen getrennte
Nativebelege. Health-/ImportantOrigin-Recoveryvorschläge bleiben Vorschläge;
keine Healthaufnahme oder Ursache alter Diagnostics0-Waffenunverfügbarkeiten
wird aus diesem Paket abgeleitet. Null neue GroundReplans wären weiterhin kein
Wirksamkeitsnachweis des Fixes.

## Tests und reproduzierbarer Handoff

Zuerst sieben echte Missingbuilder-Assertions rot, danach7/7 grün. Abschließend
neue024-Prüfungen, unveränderte023-Builderprüfungen und bestehende
Navigationcomparison-Policychecks gemeinsam: **23/23, 0,462s, Exit0**.
Geprüft werden vollständige Buildclosure, absichtlich falsche Manifest-/Sourcepins,
mehrdeutige/teilweise Retargets, exakte Umkehrung, feste Map/Dauer/Diagnostics,
Tiercohorten, nichtüberschreibbares Ausgabeziel sowie sämtliche resultierenden
Pins und unveränderte Konfigurations-/Budget-/Readmetadaten. Kein Controllerimport.

```sh
PYTHONPATH=tools nice -n 15 python3 -B -m unittest tools/test_navigation_build024.py tools/test_navigation_build023.py tools/test_navigation_comparison.py
python3 -B tools/prepare_navigation_build024.py --destination NEW_UNUSED_DISABLED_PATH
```

Eigener Worktree `/srv/tse-nav20-build024-retarget-20261114` ab dem genannten
Rootquellcommit. Plan/Claim `541cd16`, RED-Tests `224eb70`, Builder
`43d14898dc566803b629a9d2375a1932b972f4b0`.
Builder-SHA256 `81a7ce6ea56c5b3269c12514b1ae36e0933467fcce2e46e7e5d26caf5a5e65b5`;
Test-SHA256 `df2c8394743936c596bc1f87748c35152ad23c0df8ee3a226705f7fdcdbcfd20`.

Private Quittung `.codex/evidence/navigation024/final-receipt.json`, SHA256
`89de6aa52a4d62263041fb086457591408e166ad829a3f3b8dfb6cbdf1eb7bd5`,
pinnt Tests, tatsächliche Buildherkunft, unveränderte Quellen und alle inversen
Hashes. Keine alten komprimierten Nativearme restauriert. Rootreview,
Rootfreeze und genau ein künftiger begrenzter Test bleiben getrennte Schritte.
Alle eigenen Jobs sind beendet; keine A4-/Budget-/Retailqualifikation behauptet.
