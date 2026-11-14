# Build023: einzelner deaktivierter Red600-Arm

**PASS_OFFLINE_DISABLED_ONLY.** Keine eigene Runtime, kein Build, keine
Promotion. Root allein reviewt, friert ein und startet gegebenenfalls genau
einen600s-Arm. Die existierenden022-Pakete und historischen Ergebnisse bleiben
unverändert.

## Herkunft und enges Delta

Exakter deaktivierter022-Parent
`/srv/tse-nav20-022-red600-disabled-20261114`, Manifest
`aa5783efbed7dc53a33ccee9f0755890eba6c2bdc8f5e9b43e76ff0059d648df`.
Tatsächlicher von Root fertiggebauter Kandidat
`/srv/tse-milestone-a-build-023-20261114`, Quellcommit
`4190bafe6e4c149f9f13ce23b003e4a0c9f0ecf8`, Tree
`9f3ef9587484b4ccada66964439d857b676c4d34`, Buildmanifest
`a7b057ba42cfe60eff057bddfde40436720074aa9247515990f9f92944b23080`.
DLL `4dec2aa434c50ad602f1f9f136bf7f8663e9d16c5896a17ea1d343db8faf4883`,
438272Bytes. Builder prüft47Source-/28Overlaydateien, Manifest, DLL und genaue
Größe frisch; der tatsächliche Header ist f070a62a… wie im Fixbericht.

Neuer Builder `tools/prepare_navigation_build023.py` übernimmt das geprüfte022-
Muster mit drei fest umkehrbaren Quelländerungen: Kandidatenpfad/Versions- und
Namespacebezeichnung im Runner, gepinnter DLL-/Armcheck im Adapter und zusätzlicher
023-Katalogeintrag. Andere Optionen sind nicht erlaubt. Keine neue Probe, kein
Memorydecoder, keine Inventory-/Query-/Inputoperation. Die übrigen63Quellen des
Parents sind bytegleich; jede der drei Änderungen reversiert bytegenau.

Bedingungen bleiben Red Station,600s,8eigeneBots+Original,20FPS,Hard2,
DEMON/tier3,Diagnostics0, identische Nav-/Seed-/Konfigurationsbedingungen und
V3-Beobachtungsvertrag. Ressourcen-/Identity-/Fehler-/Readrate-/Close-/Restoregates
bleiben unverändert. Kein Retry und keine automatische Folgearmsequenz.

## Offlinebelege und Paket

Vor Implementierung erwarteter RED: fehlender023-Builder, ein gezielter Test,
Exit1. Nach tatsächlichen Rootpins sieben neue Tests sowie sechs Observer20-
und neun Vergleichsregressionen: **22/22 PASS**, alle Exit0. Frischer Generator-
und separater Paketcheck ebenfalls Exit0. Keine Runtimecontroller importiert.

```sh
python3 -B -m unittest discover -s tools -p test_navigation_build023.py -v
python3 -B tools/test_navigation_observer20.py -v
python3 -B tools/test_navigation_comparison.py -v
python3 -B tools/prepare_navigation_build023.py --destination /NEUER/PRIVATER/PFAD
```

Neuer deaktivierter Fork `/srv/tse-nav20-023-red600-disabled-20261114`:

- Manifest `51d72a2cf233ff87d2f0cac0d3ad2a532f6f287e6ef62bd154b43e6e4ba8e5e8`.
- Controller `14c955b48ec546110c6ff729d8192f09c9e72fe72a84bb9d5703245aa50408d2`.
- 139Runtime-/71Source-/43Pythonpins frisch richtig; alle Review-/Runtimegates
  false.77Buildpins enthalten, alte022-Buildabhängigkeiten entfernt.

Private Commands/Outputs und Quittung im eigenen Worktree
`/srv/tse-nav20-build023-retarget-20261114/.codex/evidence/build023-retarget/`.
`final-receipt.json` SHA256
`ebeb445f6475198faf346a4c98957af423dc18e01c2765ad32f9af7873932ef8`.
Quittung pinnt beide neuen Quellen, vollständige Commands, Paket und Abschluss.
Dateien0600; keine Retaildateien oder privaten Logs im öffentlichen Git.

## Aussagegrenze für einen späteren nativen Arm

`CecilImportantOriginRecovery … proposal=1` ist ausschließlich ein Quellvorschlag.
Akzeptierte Bewegung und Positionsänderung sind getrennt zu prüfen. Eine tatsächliche
Position innerhalb des ursprünglichen Quellradius sowie der anschließende bestehende
Exit müssen unabhängig aus Nativebeobachtungen/Sourcekontext belegt werden; weder
Vorschlag noch neuer DLLhash beweisen dies. Keine zusätzlichen Leser wurden dafür
in den Runner eingeführt.

Die längsten Leben ohne brauchbare Waffe bleiben zu messen. Diagnostics0 gibt den
konkreten alten Weapon-unavailable-Grund weiterhin als UNKNOWN aus. Healthproposal
und tatsächlicher Healthgewinn/Pickup sind ebenfalls getrennte Aussagen. Alte rote
Läufe werden nicht umetikettiert; diese Vorbereitung ist kein A4-/A-Abschluss und
keine Dauer-, Sync- oder Publicqualifikation. Keine eigenen Jobs laufen weiter.
