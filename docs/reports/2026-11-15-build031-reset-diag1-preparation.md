# Build031 Reset-DIAG1: deaktivierte Vorbereitung

Genau ein neuer ResetV3-Diagnosefall ist vorbereitet. Parent ist das unveränderte deaktivierte Build030-Timestamp-Paket, Manifest `98294d1ca2c21df380cc10c43a66a9c1b6c0a97500dceae7d3faf854fd15ba11`.

Das neue private Paket liegt unter `/srv/tse-a4-build031-hard-reset-v3-diag1-disabled-20261115`. Manifest: `25c97a964e51b52679e221a948bccf83583279574a742a4acdd4dc6df5dabdbc`; Controller: `3fea59c27b928afc8016967a5ac0ceab2905459c8acb0e2b9ff63c129287dafa`. Sämtliche Runtime-/Qualifikationsgates bleiben false. Kein Nativefall wurde gestartet.

`tools/prepare_a4_reset_build031.py` nutzt die exakt gepinnte tatsächliche Closure aus `tools/build031_reset_candidate.json`: 49 Quell-,30 Overlay-,ein Manifest- und ein DLL-Ziel. Alle81 Dateien wurden gehasht. Buildmanifest `9c8cabf8d2a3a56803ac25ce8af55a38884a14de47ebeb5b1399095a2d4b40c5`, DLL `5c5c21d651f5513bcba4c1c3cc8ddc6495fbfbe7cdbbee506c70853bd15bbb0b`,461824Bytes, Quellcommit `226276880c847ed145ee36f1415eb53fd3c01588`. Gegen030 ändern sich in beiden Quellmengen nur BotDriver.cpp/BotSupplyNative.h; ausschließlich picker_custody.h kommt hinzu. Die übrigen Inputs bleiben bytegleich. Alle79 aktiven030-Buildabhängigkeiten sind entfernt; die alte Herkunft liegt ausdrücklich unter historischen Metadaten.

Drei ganze Sourceinversen belegen ausschließlich DLL-/Hashretarget, eigene Namespaces/Sessionlabel, feste DIAG1-Admission einschließlich tatsächlichem CLI-Argument sowie ausdrücklich begrenzte Diagnosemetadaten. 85 übrige Parentdateien bleiben bytegleich. 152 Runtime-,92 Source- und47 Python-Pinwerte wurden vollständig geprüft. Timestamp-/Cgroup-/Restorecode, sämtliche Reader, Ereignis-/Inventarbeweise und technische Finalizerstatus bleiben unverändert.

Der feste Fall bleibt Red→Red→Red mit zwei Resets,24 Slotphasen,480Sekunden, Hard2, acht DEMON3-Bots, Original30FPS und Zeitlimits2/2/0. DIAG1 ist eine neue Bedingung mit zusätzlichem Diagnoseaufwand. Die bisherigen Fehler bleiben Fehler; weder alte Ressourcen-/Aktivitätsfreigaben noch eine A4-Abnahme werden übertragen. Ein accepted_proposal beweist keine Bewegung oder Aufnahme. Gedrosselte oder nicht protokollierte Entscheidungen bleiben UNKNOWN. Ein semantischer Auditor der neuen Pickerzeilen gehört zum nächsten getrennten Auswertungsschritt.

Nachweis: Der unveränderte Parent erzeugte in vier tatsächlichen AST-extrahierten Admission-/CLI-/Optionschecks fünf Assertionsfehler: DIAG1 zurückgewiesen, CLI noch0, falsche Dauer/Map/diag0 akzeptiert. Nach Umsetzung bestehen13 gezielte Tests in0,160s. Zusätzliche Gegenfälle prüfen falsche Kandidatenherkunft, Manifesthash, Closurehash/-menge, teilweise bereits retargetete Quellen, falsche Konfiguration, deaktiviertes Gate und frisches Ziel. Diese portablen Checks starten oder importieren keine Runtimecontroller.

Reproduktion:

```sh
python3 -m unittest discover -s tools -p test_prepare_a4_reset_build031.py -v
python3 tools/prepare_a4_reset_build031.py --destination /srv/NEUER-FRISCHER-DISABLED-PFAD
```

Private vollständige Pin-/Inverse-/Parentquittung samt Reader und ursprünglichem RED/GREEN liegt im eigenen Worktree unter `.codex/evidence/reset031-diag1/`. Root prüft, integriert, friert separat ein und entscheidet allein über genau einen begrenzten Nativefall. MeilensteinA bleibt offen; B hat nicht begonnen.
