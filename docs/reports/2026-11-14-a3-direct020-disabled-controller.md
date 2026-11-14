# A3: deaktivierter direkter Build020-Tiervergleich

Status: deaktivierter Hard2-Controller, fokussierte Offlineprüfungen bestanden;
unabhängiger Rootreview und native Fenster offen.
Kein nativer Start, kein Treffer-/Stärke-/A3-Nachweis.

## Kandidat und Herkunft

- Originalparent: `/srv/tse-milestone-a-continuation-evidence-20261112/a3-build018-root-frozen`, Manifest `412755b8bc5d2c962321f1bfeaeb6ad51efc43af0c3a8c659d2631c1145f9e69`.
- Originalanalyzer: benachbartes `a3-build018-analysis/analyze.py` und `behavior.py`.
- Bisherige erste Sourcevorbereitung: `/srv/tse-a3-direct020-controller-20261114`. Sie erbte noch die historische Serious3-Serverbedingung und ist kein vorgesehener Nativekandidat.
- Neuer Hard2-Sourcecontainer: `/srv/tse-a3-direct020-hard-controller-20261114`. Finales Manifest `7730510ef9f6e4ef8455f6b0de9fffed5afc750a1beb917abed685240982d269`, 98 Source-/Artefaktpins und 77 Runtimeabhängigkeiten. Sämtliche Runtimegates bleibenfalse; ausschließlich Root reviewed, friert ein und startet.
- Build020-DLL `094ec8edbedd5e63d8e4eb03fcce70518283b22440e5f80ba4c2482ff81fe6c0`,431104Bytes; Buildmanifest `3099a0be953be1ff8047289de056b6cddf931cac9a4791f2520d3898357950c6`; Source `e5f7a65502fbea683014ef8fcc95ecdd2a927b6a`.
- Kanonische Kampfconfig unverändert gepinnt auf `9f2dfea816c3bd4d3ca0de9f3d09c2e457c208a3b50e5765575c9d0c888e465a`. Beide Gruppen benutzen dieselbe DLL und exakt dieselben Configbytes außer je einer angehängten `bot_iArenaTier`-Zeile.

Der reproduzierbare Offlinebuilder `tools/build_a3_direct020_package.py`
verlangt ein neues Ziel und den exakten Parent-/Buildmanifest-/DLL-Hash.
Er startet keine Runtime und kopiert keine Dateien in das Labor. Eine
fehlgeschlagene frühere Sourcevorbereitung liegt getrennt unter
`/srv/tse-a3-direct020-source-preparation-fail-20261114`; sie wurde nicht gestartet.

## Enger Runtime-Diff

Der Originalcontroller behält seine Namespace-, PID/Start-, geladenen
Moduleinode-, Original-ABI-/Body-, Hostbudget-, Pause-/Initialreferenz-,
Normalclose-, Postcloselog- und FileTransaction-Prüfungen. Originaldamagehook,
Damagevalidation/-aggregation, Hostbinding und Restorecode werden bytegleich
übernommen. Die Initialreferenz mit neun Teilnehmern und die125000ms-Hook-TTL
mit2000ms-Reserve bleiben erhalten. Beobachtungsdauer120s und bestehende
Samplerraten bleiben unverändert. Die öffentliche Hard2-Prüfpolicy aus Roots
Stabilitätsvorbereitung wird bytegleich übernommen und gepinnt:
`stability_hard_rules.py`, SHA256
`9e255659101eee27b6d4dcf285129a52488db29cab021ff380c290f2d34d7472`.
Sie prüft tatsächliche156Byte-Sessions und echte GameSpy-Queries.

Die Startvorlage wird innerhalb derselben versiegelten FileTransaction eng
angepasst: ausschließlich die eindeutige bisherige Difficulty2/3-Zeile wird2.
Vorhandene Ammo-/Limit-/Blut-/Gibs-Regeln müssen bereits den Auftragswerten
entsprechen; fremde oder mehrdeutige Werte führen vor dem ersten Launch zum
Abbruch. Native Hard2-/Regelprüfung nutzt die bereits vorhandene gemeinsame
Pausebarriere und Healthsamples aller vier Rollen; Query-Hardprüfung nutzt
den vorhandenen2s-Takt. Keine zusätzliche Prozesslesung oder Samplingrate.
Der geschlossene Analyzer prüft diese bereits gespeicherten Rohsamples erneut.
Historische Serious3-/109:33-Ergebnisse bleiben getrennt.

Die neue Policy wählt zwei benachbarte Tiers und vertauscht deren physische
Starts. Beide Vierergruppen sind jetzt Kandidatengruppen. Die bereits geprüften
Originalregistry-Ergebnisse erhalten anhand ihrer tatsächlichen Slot-, Entity-
und Pointerbindung MITTEL/STARK/DEMON-Labels; die unveränderte Vanilla bleibt
separat. Tatsächliche `[BotHuman]`-Profilzeilen müssen alle vier lokalen Slots
und den jeweils vorgesehenen Tier bestätigen.

Es gibt ausschließlich vier einzeln ausgewählte Fenster:1↔2/Swap0,
1↔2/Swap1,2↔3/Swap0,2↔3/Swap1. Kein automatischer Serienstart oder Retry.
Eigenes Prefix `ssam-direct020-hard-pair{lower}{upper}-swap{swap}-20261114` und
frischer Evidenzpfad mit Datum/Uhrzeit. Der unverändert geerbte Runtime-Lock
schließt gleichzeitige Labbenutzung aus.

## Auswertung

Der geschlossene Damageanalyzer reproduziert beide Configs, prüft die
tatsächlichen Profile und wertet Leben/Waffenbesitz/Cecil-Lebensereignisse
beidseitig aus. Bereits beim ersten lebenden Inventarsample vorhandene
Zusatzwaffen werden ausdrücklich als links zensierte Besitzbeobachtung
markiert. Diese Markierung ist kein beobachteter Pickupübergang.

Die vollständige Originaldamage-Partition bleibt erhalten: tatsächlicher
Fremd-, Selbst-, unbekannter, Corpse- und außerhalb des Fensters liegender
Schaden. Roher HP-Verlust, auf Vorher-HP begrenzter Verlust, Rüstungsverlust und
tödliche Calls werden je konkretem Tierpaar ausgewiesen. Originalserverkillpaare
müssen weiterhin exakt den tödlichen Calls entsprechen. Beide Behaviorausgaben
enthalten die jeweiligen Aimfehler, Waffen, Feueraktionszähler und bisherigen
Bewegungs-/Stuckmaße; AI-Feuerwünsche sind kein Treffernachweis.

`a3_compare_direct_closed.py` analysiert beide geschlossenen Rohfenster frisch,
verlangt gleiche Build-/Config-/World-/Nav-/Controller-/Hostbedingung sowie beide
Swaps und berichtet die unveränderten Ereignisrichtungen. Eine fehlende
Schadensrichtung zählt ausschließlich nach Prüfung des vollständigen
Originalcallstreams als null. Gleichstände und widersprüchliche Starts bleiben
sichtbar. `tier_strength_accepted` und `native_qualified` bleibenfalse; keine neue
Killmarge, Stichprobensicherheit oder allgemeine Dominanzbehauptung.

## Checks und nächste Schritte

Nach Roots ausdrücklicher Quiet-Endmeldung bestanden 23 fokussierte Fälle in
0,062s: acht reine Tier-/Config-/Vergleichsfälle, neun Adapter-/Originalregistry-/
Damagepartition-/Hardfälle, ein beidseitiger Behaviorparserfall, vier
Closed-Comparatorfälle und eine vollständige synthetische geschlossene
Analyzerfixture. Letztere prüft beide Tiergruppen und verwirft einen falschen
Serious-Query. Synthetic-zero-Damage ist kein nativer Kampfnachweis.

Der erste 22-Fälle-Aufruf hatte einen Fehler im Source-Test: er erwartete den
nicht existierenden Text `server=launch`; der echte Code ruft `launch` auf.
Nur dieser Teststring wurde korrigiert; anschließend alle 22 und nach der neuen
geschlossenen Fixture alle 23 grün. Die acht reinen Policyfälle hatten zuvor
echtes fehlende-Implementierung-ROT und anschließendes GRÜN. Keine breite
Discovery, kein Compiler, kein Fridaimport/-attach und kein nativer Prozess.

Frisch geprüft am 14.11.2026, 10:43:22 UTC: 77 Runtimeabhängigkeiten,
75 Build-/Overlaypins, 142 Originalparentquellen und zehn unveränderte
Originaldamage-/Host-/Restoredateien, alle passend. Ein separater Offline-
Reproduktionscontainer erzeugte dieselben 18 maßgeblichen Controller-/Analyzer-/
Hook-/Policyquellen bytegleich. Das ist Dateiprovenienz, keine ABI-/Retail-
Freigabe. Der endgültige Manifest wurde rückgelesen und sämtliche 98 eigenen
Pins plus die 77 Runtimepins erneut verglichen. Rootreview, Freeze und frischer
exklusiver Originalpreflight bleiben offen.

Die bereinigten Reviewdiffs und Hash-/Testquittungen liegen unter
[`a3-direct020-disabled-20261114`](a3-direct020-disabled-20261114).
Das synthetische Testkommando lautet im Worktree-Verzeichnis `tools`:

```text
TSE_A3_DIRECT_PACKAGE=/srv/tse-a3-direct020-hard-controller-20261114 python3 -m unittest test_a3_direct_tiers test_a3_direct_adapter test_a3_direct_behavior test_a3_direct_compare_closed test_a3_direct_closed_fixture -v
```

Reproduzierbare Sourcevorbereitung mit neuem Ziel, ohne Runtime:

```text
python3 tools/build_a3_direct020_package.py --parent /srv/tse-milestone-a-continuation-evidence-20261112/a3-build018-root-frozen --analysis-parent /srv/tse-milestone-a-continuation-evidence-20261112/a3-build018-analysis --destination NEW_EMPTY_PATH --build /srv/tse-milestone-a-build-020-20261114 --hard-rules /srv/tse-cecil-rollout-a-b-20261114/tools/stability_hard_rules.py
```

Der Reproducer erzeugt zunächst ehrlich unreviewte Sourcevorbereitung mit
ausstehenden Test-/Freshpin-Markierungen. Die oben genannten Quittungen des
konkret geprüften Containers werden nicht auf neue Pfade vererbt.

Nach Rootreview/Freeze und frischem Originalpreflight sind ausschließlich die
einzelnen folgenden Argumentfolgen vorgesehen, jeweils erst nach geschlossenem
Vorgänger und Restore-/Ressourcenprüfung:

```text
python3 run-a3-direct020.py --instrumentation 1 1 120 0 0
python3 run-a3-direct020.py --instrumentation 1 1 120 0 1
python3 run-a3-direct020.py --instrumentation 1 2 120 0 0
python3 run-a3-direct020.py --instrumentation 1 2 120 0 1
```

Das deaktivierte Sourcepaket verweigert diese Starts. Der Hauptagent muss einen
gesonderten reviewed Freeze erzeugen; historische018-/Legacy-Siege und
Fehlversuche bleiben davon getrennt.

Geschlossene Artefakte erst danach mit `analyze-direct020.py WINDOW`,
`behavior-direct020.py WINDOW` und für ein Paar
`a3_compare_direct_closed.py SWAP0_WINDOW SWAP1_WINDOW` auswerten. Keine
Runtimefreigabe oder Stundenstabilität aus diesen Offlinewerkzeugen ableiten.
