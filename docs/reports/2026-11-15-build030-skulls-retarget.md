# Build030: deaktivierter Skulls600-Diagnosefall vorbereitet

Der neue reine Builder `tools/prepare_navigation_build030_skulls.py` leitet
genau einen deaktivierten Fall vom vorhandenen029-Timestamp-Paket ab.
Keine Laufzeit wurde gestartet und kein vorhandenes Paket verändert.

| Beleg | Tatsächlicher Wert |
| --- | --- |
| Parentmanifest | `cb35162436f466b697f00b53cc04ace272c04f059a8a6464dcaed4aead406c36` |
| Build030-Manifest | `89eef08dfce8f2b5f40fba0290e5778bdb42831c7280731ad5cd44c21338a5d3` |
| DLL/Größe | `bf70585708cb5cc0d0d62416b641c1df758c90b8cdbd062a04dccecca2a29412`,454144Bytes |
| Quellcommit | `7aedcdb21f7180b9abfeed2ea9e8bbbf5553564e` |
| Quellbaum | `e48736240423b15d0d31af8508418b9dae8e1ae3` |
| Neues Paketmanifest | `2b910ac7c2dc13faac888ea932e81644656dbef9f9963c6568590eb07fef6844` |
| Neuer Controller | `cfaf5663447a97eae448cd9feb0b6a66ae9c0ca4430061e4614f34e878797fe5` |

Destination:
`/srv/tse-nav20-030-skulls600-diag1-timestamps-disabled-20261115`.

Die vollständigen48Source-/29Overlayhashmaps stimmen mit dem tatsächlichen
Build überein. Gegen029 ändert sich ausschließlich `BotSupplyNative.h`
von72cea9… auf777d196e…; Driver und Formatter bleiben bytegleich. Alle79alten
029-Buildtargets wurden aus aktiven Runtimepins entfernt und durch exakt79
030-Targets ersetzt. Alte029-Policydatei und Katalogeintrag bleiben erhalten;
der neue feste030-Eintrag wird ergänzt.

Exakt drei geerbte Quelldateien ändern sich: `run-a4.py` mit DLLpfad, zwei
privaten Namespaces und Beschriftung; `adapter_policy.py` mit DLLhash und
festem030-Policynamen; `navigation_comparison_policy.py` mit zusätzlichem
030-Katalogeintrag. Die vollständigen drei Inversen stellen jeweils exakt den
Parent wieder her. Die übrigen109geerbten Dateien sind bytegleich. Dazu kommen
nur zwei neue reine Builder-/Policydateien und drei Textdiffs. Manifest und
Handoff werden neu ausgestellt.

Erhalten bleiben Skulls, Hard2, acht DEMON/tier3 mit den tatsächlich vorhandenen
Canonicalprofilen, unveränderter Originalobserver bei20FPS,600s und diag1.
Cgroup-/Cleanup-/Nanosekunden-Restore, sämtliche Reader/V2/V3/Finalizer,
Hostbudgets, Sperren und Inputbedingungen bleiben unverändert. Das Runtimegate
bleibtFalse. Alle anderen Manifestwerte sind außerhalb der ausdrücklich
abgegrenzten Candidate-/Repin-/Herkunftsfelder gleich. Insbesondere gibt es
keine zusätzliche Runtimefreigabe oder veränderten Beobachtungsgrenzen.

Actual Offlinegeneration und ein separater vollständiger Pin-/Inversecheck
endeten jeweils mit Exit0: **145Runtime-,116Source- und67Pythonpins PASS**.
Die tatsächlichen Zielhashwerte wurden vollständig geprüft, nicht nur Mengen.
Der Katalog sowie ausgewählte World-/Navdaten bestanden unveränderte
Hash-/CRC-/Navheader-/Knotenprüfungen. Jeder Asset-/Fixture-/Hashread verwendet
nach explizitem `resolve` ein `O_NOATIME|O_NOFOLLOW`-Handle ohne Fallback.
Es wurde kein Runtimecontroller importiert oder ausgeführt und keine weitere
Testsuite gebaut. Ein früher uncommitteter Policyentwurf hatte durch eine zu
breite Zahlersetzung drei fremde Hashwerte verändert; der volle Mapvergleich
fing dies vor der Paketgeneration ab. Die finale030-Policy hat ausschließlich
die beabsichtigten Headerhash-/030-Optionsänderungen.

Reproduktion der Vorbereitung ausschließlich in einem neuen Zielverzeichnis:

```sh
python3 -B tools/prepare_navigation_build030_skulls.py --destination /NEUES/PRIVATES/ZIEL
```

Die private vollständige Quittung mit allen Zielhashwerten liegt unter
`/srv/tse-navigation030-skulls-evidence-20261115/final-receipt.json`, SHA256
`b2d919c76f618bfef725a008cdeb51c0b7077c2d4bf169648afa20982c02168b`.
Generatorlog, reiner Verifikationsreader und sein tatsächliches Ergebnis
liegen daneben. Keine Retaildateien oder Rohidentitäten sind veröffentlicht.

**Keine A4-, Funktions-, Native- oder Überlegenheitsabnahme.** Historische
029/027- und frühere Ergebnisse bleiben unverändert. Root übernimmt Review,
Integration, Freeze, Sicherung und einen gegebenenfalls gesonderten Nativefall.
