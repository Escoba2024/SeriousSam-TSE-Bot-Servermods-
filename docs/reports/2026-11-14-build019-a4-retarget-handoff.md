# Build019: deaktivierter A4-Vergleich wie Build018

Neues privates Paket: `/srv/tse-a4-build019-controller-20261114`.
Manifest-SHA256 `4eaeadf32e84f9543ae14b3591e66f4b94a672abba70cbb7f1f6424f97f60da0`.
**Nur offline vorbereitet; kein nativer Start, keine Labdatei verändert.**

Kandidat: Build019, DLL SHA256
`671df77a06eb9df8822032418e4d9ae2550f5581a2bf89c3e45b83c0f32472be`,
431104 Bytes; Buildmanifest SHA256
`e1c921282c3c43257357f72914e4aea5da7f72021468ec9ed5260ed084fbffa5`;
Quelle `a1e77b9f1aa6e2b5332e099c2d40ab5b51ba3f15`.

Das geschlossene Build018-Elternpaket bleibt bytegenau erhalten, Manifest
`9064439561caac5deed96b1be4e546d8fa0c69ac6fbdf24a5c836b3538d0817c`.
Geändert sind ausschließlich Kandidaten-/Quellpins, neue eigene
`ssam-a4-reset019-extended-20261114`-/`a4-reset019-extended-*`-Präfixe und deaktivierte
Runtimegates. Die zwölf übrigen Runtimequelldateien bleiben identisch. Nach
Normalisierung dieser erlaubten Literale sind Controllerbytes und AST identisch
zum Elterncontroller. Eine erwartete Kandidatenkonstante im vorhandenen
Source-Contract-Test wurde ebenfalls ausschließlich auf Build019 umgestellt.

Unverändert bleiben der 480-s-Höchstzeitraum, Red→Red→Red, 2/2/0 Minuten,
mindestens 120 reale und native Sekunden in Phase3, alle fünf Aktivitätsfelder
für alle 24 Slotphasen, Inventarabtastung, Observerwechsel, Restore, Ressourcen-
und Prozessgrenzen. Für den kausalen Vergleich bleibt die ursprüngliche
Testschwierigkeit **Serious 3** erhalten. Das entspricht ausdrücklich den
historischen Testbedingungen, nicht einer Änderung der öffentlichen Spielregeln.

Alle 51 übernommenen externen Pins, sämtliche 65 neuen Runtime-Abhängigkeiten
und alle 75 Quell-/Overlaypins des Builds wurden frisch zurückgeprüft. Das ist
ein Datei-/Quellnachweis, keine Laufzeitfreigabe. Acht spezifische Retargetprüfungen
und die 47 bestehenden fokussierten Protokoll-/Inventartests bestehen. Der erste
47er-Lauf scheiterte genau an der noch auf Build018 stehenden erwarteten
Kandidatenkonstante; nach deren isolierter Pinaktualisierung bestehen alle 47.

[Vollständiger Runtime-/Testpindiff](milestone-a-20261114/build019-a4-runtime.patch),
[Pins und Protokoll](milestone-a-20261114/build019-a4-pins.json),
[Offlineprüfungen](milestone-a-20261114/build019-a4-offline.json).

Nach unabhängiger Prüfung, frischem ursprünglichem Labpreflight und neuem
Hauptagenten-Freeze ist genau ein Aufruf vorgesehen:

```sh
python3 -B /srv/tse-a4-build019-controller-20261114/run-mapreset.py
```

Aktuell blockiert `RUNTIME_REVIEWED=False` vor Runtimezugriffen;
`runtime_reviewed=false` und `RUNPLAN-disabled.json:runtime_allowed=false` bleiben
ebenfalls gesetzt. Die geerbte Runtime verwendet weiterhin Port27850/Display154
und darf erst nach bestätigtem Ende des getrennten A1-Laufs belegt werden.
Der Hauptagent muss nach Review die neue Freezequittung und die dabei geänderten
Launcher-/Manifestpins selbst binden. Eine native Wirksamkeits-, Dev-, A4- oder
Dauerabnahme wird nicht behauptet; maximal ein Fenster, kein automatischer Retry.
