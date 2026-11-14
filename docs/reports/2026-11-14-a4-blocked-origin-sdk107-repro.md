# A4: SDK107-Reproduktion des gesperrten Ausgangsankers

**REPRODUCED_RED**, kein Fix: Die tatsächliche SDK107-Brücke liefert
3115Checks mit genau zwei erwarteten Fehlern, Exit1. Alle zusätzlichen
Kontrollen und bestehenden3104Checks bleiben erfolgreich. Produktion ist
bytegleich zu Rootbasisf9fc13a; keine DLL-/Wine-/Spiel-/Frida-/Liveausführung.
Dies ist eine separate A4-Lücke, kein Healthregressionsclaim.

## Konkreter realer Pfad

Die neue Fixture in `test_cecil_native_bridge.py` erreicht beiPolicytick968
Nav138 innerhalb seines originalen Radius. Echter `BotSupplyTick` führt
`BotCecilImportant` und dessen `not_usable`-Zweig aus; tatsächlicher
`BotCecilFinishImportant` setzt avoidNode138 bisPolicyzeit58.4 (48.4+10).
Der Worldfixture-Partner401 ist ein nichtbenutzbares WeaponItem, keine erfundene
Switchentscheidung. Danach steht der Player wie im nativen022-Beleg außerhalb
Nav138 bei(63.150,.381,-79.827). Eine gewöhnliche Armor260 anNav182 wird als
lebendes, benötigtes Ziel im unveränderten Versuch gehalten.

Reale Produktionskörper `BotCecilLocks` und `CecilNavigator.Update` liefern
bei980: blocked138=1,anchor138,goal182,hop−1,active0,ownsMovement1,
forward/strafe0 und0Rays. Dasselbe neutrale Ergebnis bleibt bei1160 vor Ablauf
der10s-Sperre bestehen: beide Sollbewegungstests sind RED. Nach ursprünglichem
Ablauf bei1169 wird derselbe Versuch wieder aktiv, ohne neuen Start oder Timer.

Die Fixture benutzt193Slots; irrelevante Punkte sind explizit getrennt, statt
weitere Routen zu erfinden. Ursprüngliche relevante Nav138/182-Metadaten und
der originale direkte Link138→182 bleiben erhalten. Nav182 ist Slot182 mit
stabilerID184, Nav138 ist Slot138/stabil139. Die frühe native gewöhnliche
Patrolauswahl15 ist im vorangehenden Bericht dokumentiert; ihr kompletter Pfad
wird hier nicht reproduziert. Der spätere native direkte Armorweg182 genügt,
um die Ablehnung vor Pfadsuche unabhängig von einer Fernroute zu isolieren.

## Ursachenbewertung und unveränderte Sicherheitskontrollen

Der Effekt entsteht vor Bewegungssafety: `FinishImportant` sperrt10s den
verlassenen Importantknoten; `Locks` überträgt dies auf den Ausgangsanker;
der Navigator behandelt einen gesperrten Anker außerhalb seiner echten
Ankunftsgeometrie als gesperrtes erneut zu erreichendes Ziel und gibt neutral
zurück. Ein aktiv benutzter Switch, Powerupwartezeit oder sichtbarer Kampf ist
für den nativen Stillstand nicht belegt. Die Reproduktion stützt den im
022-Bericht beschriebenen Mechanismus; sie ersetzt keinen atomaren nativen
Branchtrace und keine vollständige ursprüngliche Cecil-Verhaltensqualifikation.

Kontrollen im selben tatsächlichen Bodyharness sind grün: noch innerhalb der
originalen Ankunftsgeometrie darf der gesperrte Ursprung wie bisher verlassen
werden; echte blockierte Ziele bleiben gesperrt; Ablauf der bestehenden
Deadline aktiviert die vorhandene Route; deren Bewegung unterliegt weiter dem
physischen Wall-/Floorveto. Es wurde weder LOS, Radius, Raybudget noch die
Sperrentscheidung verändert. Keine allgemeine Ausnahme für NAVlocks wird aus
diesem RED abgeleitet. Rootreview und konkrete getrennte Fixplanung fehlen.

```sh
python3 poc/candidates/redstation-supply-20261107/test_cecil_native_bridge.py --sdk-player /srv/tse-sdk-20261021/Sources/EntitiesMP/Player.es
```

Private Quittung `.codex/evidence/blocked-origin/receipt.json`, SHA
`c1880ac029cdd96770b4e072e0e35a9223ed7edb056ef62da2b85349a90f632a`; unveränderte Produktionspins, vollständiger Output und
exakte erwartete Fehler sind dort festgehalten. ASan oder ein weiterer Lauf
wurden für diesen bewusst roten Reprostand nicht als bestanden behauptet.
