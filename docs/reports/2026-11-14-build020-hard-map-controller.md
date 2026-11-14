# Deaktivierter Build020-Hard2-Kartencontroller

Status: Sourcevorbereitung/Offlinechecks bestanden; unabhängiger Review, Root-Freeze und native Fenster offen. Keine Karten-, Kampf-, Traversal-, Stabilitäts- oder A4-Abnahme.

Eigenworktree `/srv/tse-a4-hard-map-adapter-20261114`, Basis `efcb7eb`.
Privates Endpaket `/srv/tse-a4-build020-hard-map-controller-final-20261114`, Manifest `0a6c0990de1cb4cd4f01d9daa906ab8ed4c572b2b11ab998a23615e02e46ea0e`. 61 Runtimepins,39 aktuelle Source-/Artefaktpins und22Pythonpins frisch passend. Codegate und Manifest-Runtime-/Qualified-/Functional-Gates false. Der Reproducer verlangt ein neues Ziel und verweigert bestehende Pakete.

Exakter Singlemapparent `/srv/tse-combat-a4-build013-preflight-draft-20261112`, Manifest `ab364a9a4107686a66c5f94b3e90a6406033084ec48cac789afc1b2b525278f9`; alle56 geerbten Runtimepins vor Ableitung frisch passend. Dieser Parent hat **keine Frida-Hooks**. Der Adapter fügt keine Frida-Verbindung hinzu und benötigt daher keinen A3-Damageworker. Das Originalserver-Inventar stammt weiterhin ausschließlich vom vorhandenen passiven Reader.

Kandidat exakt020: DLL `094ec8edbedd5e63d8e4eb03fcce70518283b22440e5f80ba4c2482ff81fe6c0`, Quellcommit `e5f7a65502fbea683014ef8fcc95ecdd2a927b6a`, Buildmanifest `3099a0be953be1ff8047289de056b6cddf931cac9a4791f2520d3898357950c6`. Alle75 Build-/Overlayquellpins werden vor Kopie geprüft. Beide Botgruppen behalten kanonisches DEMON-Profil7; nur die vorhandenen RosterOffsets0/4 unterscheiden ihre Configs.

Die Änderungen beschränken sich auf020-/Namespacepins, genau600s/diag0, Hard2 und die freigegebene V2-Feuerbeobachtung. Die native Hardpolicy ist bytegleich `stability_hard_rules.py` (`9e255659…`), kontrolliert sämtliche vorhandenen Session156-Proben einschließlich Pausen-/Joinbarriere und alle vorhandenen direkten Querywege. Falsche/unvollständige Regeln führen zum Fehler. Die vorhandene Preflightquery wird auch bei Fehler unverändert archiviert, bevor Hardvalidierung scheitert.

V2 und das konservative Native-/Source-Lifejoin werden bytegleich aus dem geprüften Paket `/srv/tse-a4-fire020-v2-controller-20261114` übernommen (Manifest `86662c479b4a0928ba140fc8437ac7ea8f8683a9145dc9e69204606aa316329f`). Ausschließlich bereits akzeptierte Gameplay-Inventarsamples bekommen Phase0/PID-Start/Sourceoffset0. Der erste tatsächlich vollständige Neuner-Durchgang liefert die aktuelle Entity-/Pointer-/Worldregistry über den unveränderten V2-Registrybuilder. Fehlende Registry verhindert den Abschluss. Alle Samples und Sourcezeilen bleiben demselben unveränderten Singlemap-Load gebunden; bestehende Map-/Nav-/Querybelege kontrollieren die konkrete Welt separat.

Nur das sekündliche `fire_action_rows`-Gate verliert seine autoritative Rolle. Stattdessen müssen echte native FIRE/current-owned/ammo und Sourcecounterwachstum im nachgewiesenen selben Leben sowie ein tatsächlicher Useful-Inventargewinn vorliegen. Alle übrigen bisherigen Aktivitätsfelder bleiben Fehlerbedingungen. `functional_pass`/`qualified` bleiben false. Eine vorhandene Waffe im ersten Sample ist kein Pickupbeleg.

Readeraufrufe und Samplingpausen sind ASTgleich zum Parent. Transaction, Backend, Hostbudget, vorbereitete Map-/Loadpolicy, kanonische Config und Karten-/Navmetadaten bleiben bytegleich. CPU75%, RAM1,5GiB, Disk8GiB unverändert. Kein neuer Gameplayinput; Originalobserver erhält weiterhin ausschließlich die vorhandenen Pauseaktionen. Der geprüfte V2-Teilstartclose wird übernommen: fehlende Startidentity nur bei streng eigener ready-Rolle frisch beziehen; bei falscher/wechselnder Identity kein Close. Start des eigenen systemd-Dienstaufrufs hat denselben20s-Timeout wie V2; normale35s/30s-Closefenster bleiben erhalten.

## Offlineprüfung

81 gezielt benannte Fälle in0,124s PASS:10 neueAdapter-/Registry-/Hard-/Teilstartfälle,9V2,13Nativefire-Lifejoin,6Hardregeln und43 geerbte reine Adapter-/Asset-/Backend-/Host-/Transaction-/Preflightfälle. Keine breite Discovery, kein Compiler, kein Fridaimport/-attach und kein nativer Prozess.

RED wurde gegen den originalen013-Launcher für fehlendesV2/Hard600/Teilstartclose beobachtet; initial war das neue Policymodul noch nicht vorhanden. Der erste Builderlauf scheiterte beim falschen Manifestkey einer kopierten V2-Testquelle; nur Sourcevorbereitung, getrennt erhalten. Im ersten vollständigen Offlinepaket scheiterten zwei geerbte Queryfixtures erwartungsgemäß an fehlendemHard-Feld. Die gültige Fixture trägt jetztHard, die ungültige erwartet den Fehler; rohe Queryarchivierung erfolgt vor Ablehnung. Diese Fehlpakete bleiben unter `…-source-fail-20261114` und `…-offline-fail-20261114` erhalten. Kein fehlgeschlagener Lauf wird als nativeAbnahme umgedeutet.

Das konkrete Testkommando im privaten Endpaket ist:

```text
TSE_HARD_MAP_PACKAGE=/srv/tse-a4-build020-hard-map-controller-final-20261114 python3 -m unittest test_a4_hard_maps test_a4_fire_observer_v2 test_audit_a4_native_fire_observer_v2 test_stability_hard_rules test_a4_adapter test_assets_and_cleanup test_backend test_host_budget test_transaction test_preflight_startup -q
```

Reproducer im Repository: `python3 tools/prepare_build020_hard_maps.py --destination NEW_EMPTY_PATH`. Nativebefehle des deaktivierten Pakets schlagen am Codegate fehl. Nach eigenem Rootreview/-Freeze und frischem exklusivem Originalpreflight wäre ausschließlich ein einzelnes `python3 run-a4.py MAP --seconds 600 --diagnostics 0` vorgesehen, Reihenfolge redstation/yodeller/skulls/trouble/hole. Kein automatischer Serienstart oder Retry. Root besitzt Integration und Runtime.

## Neun-Karten-Bestand

[Statische Metadatenmatrix](2026-11-14-build020-hard-map-static-inventory.json): acht Worldmembers sind im vorhandenen Levelarchiv enthalten; alle acht Central-Directory-CRC stimmen zur vorhandenen Cecil-Bindung und alle acht Nav-CRC stimmen. Zusätzliches Nav DesertTemple vorhanden, entsprechendeWelt im untersuchten vorhandenen Archiv nicht enthalten. Archivhash ist in diesem Metadatenbeleg ausdrücklich geerbt, kein neu berechneter Vollhash; der Builder prüft seine vorhandenen Quell-/Runtimepins separat.

Der ausführbare Katalog bleibt bytegleich auf den fünf bestehenden Flottenkarten. TheLostTomb, Fortress und KuntaKinte sind **vorhanden**, aber wegen fehlender vollständiger Query-/Katalogbindung und020Hard-Kartenabnahme gesperrt; keine Behauptung fehlenderWelten. DesertTemple bleibt wegen fehlenderWorld gesperrt. Auch die fünf Katalogkarten haben durch diese Sourcevorbereitung noch keinen neuen020Hard-Singlemap-PASS. Höhen-/Teleporter-/Bouncer-/Recovery-/Gefahrenfälle bleiben bis tatsächlicher Beobachtung NOT_EXERCISED. Keine vollständige Cecil-Parität.
