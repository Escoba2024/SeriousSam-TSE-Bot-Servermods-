# A4: begrenzte Rückannäherung nach not_usable

Lokaler Produktionsvorschlag, keine DLL und keine native Retail-Abnahme.
Der geschlossene022-Stand und seine offene Stationarität bleiben historische
Belege. Root allein reviewt, integriert und prüft einen neuen Kandidaten.

## Änderung und klare Grenze

Der SDK107-Repro40477b5 belegt das Warten am selbst zehn Sekunden vermiedenen,
außerhalbRadius stehenden Ausgangspunkt. Der Fix verändert weder Navigator,
Blockmaske, ursprüngliche Radien, Lockziele noch gerichtete Kanten. Nur ein
wirklich durch `FinishImportant(not_usable)` erzeugter temporärer Avoid kann
eine langsame Rückannäherung an SEINEN ORIGINALEN Quellpunkt autorisieren.
Erst die tatsächliche ursprüngliche Ankunftsgeometrie aktiviert wieder den
bereits vorhandenen erlaubten Exit aus einem besetzten gesperrten Ursprung.

`BotSupplyNative.h` speichert dazu World/Map/Player/Generation/Gravity und
Originalmetadaten des Quellpunkts (ID, Geometrie, Flags, ImportantEntity,
Lock/Next und bis32ursprüngliche Links) zusammen mit unverändertem AvoidNode
und seiner festen10s-Frist. Andere Finishgründe oder größere Metadatenfächer
sind ineligible. Eine noch nicht verwendete Provenienz gehört zum Avoid, damit
die echte nächste Goalwahl mit ihrem bestehenden ClearGoal möglich bleibt.
Ab dem ersten qualifizierten Recoveryversuch sind zusätzlich Ziel/Item,
Goalstart, rohe/effectiveDeadline, Zielmetadaten und Navigatorresetserial
gebunden. Späteres ClearGoal/Reset/Kontextwechsel kann diese Bindung nicht
reaktivieren. Vollreset/Death/Map-/Player-/Generationwechsel, Frame-/Gravity-
Fehler, fremde Movementownership und weitere Avoidgründe widerrufen sie.

Nur tatsächlicher neutraler Navigatorausgang, gleicher aktueller Anker,
gewöhnliches anderes nichtgesperrtes Ziel, Stand/Crouch, gültige endliche
Werte und kein Follow/Flight/Use/Liquid/Specialkontext sind zulässig. Die
vorbereitete vorhandene Pfadsuche prüft den aktuellen verbleibenden Weg gegen
alle Locks. Ein frischer bestehender LOS-Cast zum Quellpunkt (höchstens8m,
3mHöhe) reserviert die letzten zwei Safety-Rays. Budget<=2 wartet neutral,
ohne neue Rays oder verlängerte Fristen. Die vorhandene Reacquire-Projektion
liefert höchstens0.3normierten Vorschub; sie setzt keinen Anker, kein arrived
und keinen Nav-/Floorstempel. Die reguläre SafeMotion muss weiterhin aktuelle
physische Zulässigkeit ermitteln. Der neue begrenzte Logtyp
`CecilImportantOriginRecovery … proposal=1` bedeutet ausschließlich Vorschlag.

## Testbelege

Die tatsächliche SDK107-Produktionsbrücke führt reale FinishImportant-/Locks-/
Navigator-/Goalwahl-/Safetykörper mit deterministischen SDK-förmigen Stubs aus.
Keine nachgebaute Navigationsentscheidung und kein Runtime-/ABIbeweis.

- Repro3115/2RED, dann adversarialer Stand3191/7RED vor Produktion.
- Erste Umsetzung ließ einen inzwischen vom Parent verworfenen Followkontext
  durch. Zusätzlicher Framefehler-/Wiederkehrfall machte3201/2RED sichtbar;
  frühe reine Kontextvalidierung schloss beide.
- Zusätzliche endliche Snapshot-Gegenfälle ergaben3223/2RED für unendliche
  HP/Geschwindigkeit; explizite endliche Validierung schließt auch diese.
- Eine zunächst versehentlich auf eine ältere Bouncer-Testschleife angewandte
  Zähleränderung verursachte vier Fixturefehler. Die Parent-Testschleife wurde
  exakt wiederhergestellt; dies war kein Produktregressionsbeleg. Der korrigierte
  zusätzliche Gegenfalllauf zeigte ausschließlich die zwei genannten REDs.
- Finaler normaler SDK107-Lauf: **3223 Checks, 0 Fehler, Exit 0**.
- Finaler ASan-/UBSan-Lauf: **3223 Checks, 0 Fehler, Exit 0**. Einziger
  Compilerhinweis: Debug-Variablentracking im großen generierten `main`
  überschritt sein Limit; der Compiler wiederholte ohne dieses Tracking.
  Keine Sanitizerdiagnose.
- Zwölf gezielte C++14-Header-/Policyprogramme sowie die vier tatsächlichen
  Action-/Item-/Export-/Observer-Brücken: alle Build-/Test-Exits **0**.

Weitere Gegenfälle: tatsächliche nächste Armor-Goalwahl/ClearGoal, ursprünglicher
Radius-Eintritt und anschließender unveränderter committed-edge-Exit, blockierter
Source/Target und geschlossene Zwischentür, ImportantEntity-/ID-/Pose-/Radius-/
Linkmetadatenwechsel, World/Map/Generation/Reset/Timeback, Ziel-/Fristwechsel,
anderer Avoidgrund bei identischen Node-/Fristwerten, Budget0/1/2 mit Erholung,
frisch blockierte/wieder freie LOS, fehlender Floor, Wallveto und null
Allokationen pro warmem Tick. Die Blockmaske bleibt auch während Recovery gesetzt.

```sh
python3 poc/candidates/redstation-supply-20261107/test_cecil_native_bridge.py --sdk-player /srv/tse-sdk-20261021/Sources/EntitiesMP/Player.es
python3 poc/candidates/redstation-supply-20261107/test_cecil_native_bridge.py --sdk-player /srv/tse-sdk-20261021/Sources/EntitiesMP/Player.es --sanitize
```

Die zwölf Programme prüfen Aimtrace, Arena-Kampf/Rotation, Cecil-Frames,
Head/Body, Human, Integration, Itemretention, Motion, Nav, Regeln und Supply.
Die vier Pythonprüfungen heißen `test_cecil_action_native.py`,
`test_cecil_items_native.py`, `test_cecil_rules_exports.py` und
`test_supply_observer_native.py`; vollständige Commands und Outputs stehen
in `verified-parent.json`. Der warme Allokationsgegenfall umfasst neun
Fixtureticks und ist kein nativer Ressourcenbeleg.

## Quellen, Belege und Übergabe

- Repro: `40477b5a9007543d640e0ebf8a78dfa2a4dfd8d4`.
- Adversarialer RED-/Fixplan: `ac64a3a82ca84d1314d09d2be19f594c45575a57`.
- Produktion und abschließende Gegenfälle:
  `eecac110f1bffc277e02e241be20da93141aac4a`.
- `BotSupplyNative.h`: SHA256
  `f070a62ac096c01203d6c28ebc621d591c0489346aabadfb628fae0bb685b1af`.
- `test_cecil_native_bridge.py`: SHA256
  `d18f077f46c8b0fae7c66c171176df579db65914f446ad617712599bff978830`.
- Unverändert: `cecil_motion.h` SHA256
  `a32870d3a4d47c95f927e25d1b3bb881de8297f9245dedb632c56069cda88e09`,
  `BotDriver.cpp` SHA256
  `9e8a1ed5c058c4bd0a45c99b07ddedf29580bca38940c4dbb27403c05816b153`.

Private Quittung im eigenen Worktree
`/srv/tse-a4-blocked-origin-repro-20261114/.codex/evidence/blocked-origin-fix/final-receipt.json`,
SHA256 `80c57f3851a9500a2a787ce5c3387206e60edeb9f4c70019171c9443b4381d5a`.
Sie pinnt SDKquellen, Produktionsdateien, sämtliche früheren RED-/Zwischenlogs,
die finalen Normal-/Sanitizeroutputs und alle Parentcommands. Alte rote Runs
bleiben unverändert; private Dateien sind 0600. Keine Retaildateien oder
privaten Rohlogs gelangen ins öffentliche Git.

Nächster Schritt: unabhängiger Rootreview des Diffs und der Gegenfälle;
anschließend entscheidet Root über einen neuen Build und eine getrennte native
Prüfung. Kein Hintergrundauftrag läuft weiter.

Native Wirksamkeit, Ressourcen-/Syncstabilität und A4-/A-Abschluss bleiben
unbewiesen. Es ist keine allgemeine Freigabe blockierter Ursprünge, keine
Healthregression und keine vollständige ursprüngliche Cecil-Parität behauptet.
