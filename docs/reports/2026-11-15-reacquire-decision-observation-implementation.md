# Passiver Reacquire-Entscheidungsbeleg – SDK107-Umsetzung

Der neue `[CecilReacquireDecision]`-Datensatz beobachtet den vorhandenen
`BotCecilReacquire`-Aufruf. Er verändert keine Versorgungs-, Navigations-,
Bewegungs- oder Sicherheitsentscheidung. Dies ist eine Diagnosevorbereitung,
kein Fix oder nativer Ursachenbeleg für die lange unbewaffnete Skulls-Lebensphase.
Retailbuild, Runtime, Liveflotte und ursprüngliche fehlgeschlagene Abnahmen
wurden in diesem Worktree nicht verändert.

## Enger Produktionsumfang

Nur `poc/candidates/redstation-supply-20261107/BotSupplyNative.h` erhält einen
passiven Ratezeitstempel, einen festen lokalen Datensatz mit drei Hintrecords
und explizite Abschlussstellen an den bestehenden normalen Returns. Es gibt
keine RAII-Ausgabe, Allokation, zweite Suche, RNG-Auswertung oder zusätzliche
physische Probe. BotDriver, PhysicalCast, Navigator, Decoder und Controller
bleiben unverändert.

Bei ausgeschalteter Diagnose gibt es keinen neuen Statewrite, Log oder
Nativezeitread. Bei eingeschalteter Diagnose wird höchstens eine neue Zeile
pro State und Policysekunde ausgegeben. Rückläufige und nichtfinite Policyzeit
öffnen keine neue Rate. Goal-/Hint-/Scan-Clear setzen die Rate nicht zurück;
der vorhandene explizite `SSupplyState::Reset()` beginnt einen neuen Zyklus.
Bestehende Supportlogs behalten ihr bisheriges Verhalten.

Die vorhandenen Grenzwerte bleiben unverändert: Supportsegment und
Trefferintervall, Normal- und Bewegungsprüfung, drei Hints, zwei reservierte
Sicherheitsrays, lokale/far-Geometrie, Locks, Bitmaps, sechs Sekunden Retention
und sechs Sekunden Rejectbackoff. Insbesondere erzeugt ungültige Graphmetadata
keinen neuen Return an einer Stelle, an der der Parent weiterläuft.

## Felder und Beweisgrenzen

Der Datensatz enthält Actor/Generation, Policyzeit und einen tatsächlich am
Abschluss gelesenen NativeGameTime-Wert mit eigenem Gültigkeitsflag. Es findet
keine Umrechnung aus SourceTick statt. Fehlendes Network oder ungültige
Nativezeit bleiben UNKNOWN und beeinflussen den Bewegungsvorschlag nicht.

Anchor/Goal/Item/Deadline sowie Hint/Since/Rejected/Retry werden vor/nach dem
Aufruf gebunden. Position wird erst aus dem bereits vorhandenen Positionlocal
übernommen; ein früherer Return hat `position_known=0`. Ground/Shape/Metadata/
Air/Liquid, Supportstadium, Budget und tatsächlich ausgeführte lokale
Geometrieprüfung bleiben getrennt.

Die Support-Knownbits bedeuten ausschließlich, dass die jeweilige vorhandene
Berechnung erreicht wurde: `valid` und `verticalSpeed` nach dem Originalloop,
Segmentresultat und dessen Lengthlocal nach genau einem ursprünglichen
RayLength-Aufruf, Hitdistanz erst nach gültigem PhysicalCast und Normal-Dotwert
erst nach dessen Originalberechnung. Der Segmentsetter bindet das Lengthlocal
als Referenz; er liest es erst nach abgeschlossener Argumentauswertung.
Nicht erreichte Render-/Hit-/Normalprüfungen werden nicht nachgeholt.

Ein Hinttuple lautet
`(slot,distance2,height_known,height,probe,result,probe_valid,cast,length,hit_distance)`.
`slot=-1` bezeichnet keinen ausgewählten Hint. Endgültige Slots und bereits
berechnete Distanz² werden kopiert. Height wird nur aus dem ohnehin berechneten
Local nach klarem LOS übernommen; bei nicht erreichten/blockierten Kandidaten
bleibt sie UNKNOWN. Dafür wird keine Geometrieberechnung wiederholt.

Nur ein gültiges positives Segment mit vorhandenem gültigem Castdetail hat
`cast=1`. FALSE allein wird niemals als Blockade ausgegeben: ungültige Probes
sind `probe_unknown`, unversuchte Slots `unattempted`, leere klare Segmente
`empty_segment`. Ein leeres Segment hat keinen nativen Cast ausgeführt.
`accepted_proposal`/`proposal=1` belegt den vorhandenen Vorschlag, keine
SafeMotion-Annahme, tatsächliche Bewegung, Radiusankunft, Versorgung oder Route.
`no_candidate_after_filters` behauptet keine geometrische Abwesenheit;
tried-/Backoff-/Lockfilter bleiben mögliche Ursachen. Die Zeilenrate kann
weitere Entscheidungen derselben Sekunde verpassen: fehlende Zeilen sind UNKNOWN.

## TDD und Verifikation

Der echte vorhandene SDK107-Bridgeharness führt unveränderte Produktionsbodies
gegen vorhandene World-/Raystubs aus. Der erste Lauf ergab **3445/4**, der vor
Produktionsänderung ergänzte adversariale Lauf **3464/23** erwartete Fehler.
Die ursprünglichen 3440 Prüfungen bestanden weiterhin.

Der erste passive Stand bestand **3518/0**, danach die Rate-/Retention-/Format-
Gegenfälle **3527/0** normal und mit ASan/UBSan. Rootreview fand fehlende
Supportlocals; fünf neue tatsächliche REDs ergaben **3532/5**. Nach der engen
Ergänzung blieb **3532/1** wegen einer Stringerwartung `0` gegenüber dem
tatsächlichen berechneten `-0`. Die vollständige synthetische Zeile wurde
aufgezeichnet; die Prüfung liest jetzt die Zahl und verlangt unverändert
exakte numerische Null, ohne EPS oder Produktionsänderung.

Der abschließende normale Lauf besteht **3532/0**. Darin sind 18 gepaarte
Diagnose-aus/an-Fälle enthalten: identische Aktionsfelder, alle im
Reacquirebody berührten operationalen Statefelder/Bitmaps, Navigatorzustand,
Goal-/Retrydeadlines und Cast-/Lookup-/Normalize-/Budgetzähler. Nur der neue
Diagnosestempel und genau ein Nativezeitread pro fälliger Zeile unterscheiden
sich. Die feste Beobachtung allokiert keinen Heap.

Nach Entfernung ausschließlich der benannten Diagnoseeinschübe und optionalen
Argumente ist der ursprüngliche Reacquirebody bytegleich zu
`88950482f46137a5af41a6214451221855be8aa5c4c41ac25f443ddea06493df`.
Eine Mutation des bestehenden Heightguards wird weiterhin erkannt. Das ist
zusätzlich zu den dynamischen Paaren ein Nachweis gegen verdeckte Änderungen
anderer Guard-/Stateoperationen, kein Retail-ABI-/Laufzeitbeweis.

Die konkrete vollständige Zeile mit drei Hintrecords und extremen endlichen
Zahlen benötigt **1540 Bytes**. Eine zusätzliche konservative Rechnung gewährt
sogar jedem Bool den vollen Intbereich, jedem Unsigned64Bits, jedem Enum32Bytes
und den Zahlen ihre maximalen Formatbreiten: **2029 Bytes plus Nullbyte** liegen
unter dem unveränderten 2048-Byte-BotLogpuffer. Die längste tatsächliche
Reasonkonstante ist26Bytes; eine anfängliche25Byte-Planannahme wurde bei der
statischen Hüllenprüfung zurückgewiesen. Der2048Byte-Grenzwert blieb unverändert.
Keine Trunkierung oder zweite Ausgabe ist nötig.

Der finale eingefrorene Source-/Testcommit besteht **3532/0 normal** und
**3532/0 mit ASan/UBSan**, jeweils Exit0 ohne Sanitizerbefund. Zusätzlich
bestanden alle **16** geerbten Parentprogramme: zwölf bekannte C++-Programme
und vier gezielte Nativeadapter-/Export-/Observerprüfungen, seriellnice15,
alle Compile-/Programmexits0. Keine breite Testdiscovery, parallelen Compiler
oder zusätzlichen Langzeitschleifen. Die letzte ASan-Runde wurde nach den
präzisierten Probe-Tuple-Prüfungen gegen genau den committed Source-/Teststand
ausgeführt; ältere Runs werden getrennt erhalten.

## Reproduktion und Handoff

```sh
nice -n 15 python3 -B poc/candidates/redstation-supply-20261107/test_cecil_native_bridge.py --sdk-player /srv/tse-sdk-20261021/Sources/EntitiesMP/Player.es
nice -n 15 python3 -B poc/candidates/redstation-supply-20261107/test_cecil_native_bridge.py --sdk-player /srv/tse-sdk-20261021/Sources/EntitiesMP/Player.es --sanitize
```

Privater Belegordner im eigenen Worktree:
`.codex/evidence/reacquire-decision/`; rohe ältere REDs und Zwischenfehler
bleiben erhalten. Öffentliche Testfälle enthalten ausschließlich synthetische
Actor-/Worlddaten. Root integriert, reviewt und entscheidet über einen neuen
Retailkandidaten separat. A bleibt offen, B wurde hier nicht begonnen.

| Pin | SHA256 bzw. Commit |
|---|---|
| Basis | `8f9b88fd95c6bd81575d85fbc6ba501259d75b5a` |
| Initialer RED/Claim | `2e22992a6f80a7f0f364b52143109437bb13be80` |
| Produktion und Tests | `dd42a7b3247fbbe24da0606461f997a6c93c1be2` |
| BotSupplyNative.h | `6f7f8adb341b2163349f115c49dc820f74d83917ecfc9c9c4c48bf86b5d549b1` |
| test_cecil_native_bridge.py | `dbdd28713e4578c7d878d1b13294d1468fc48c6238a9dc770a28149191780980` |
| Private final-receipt.json | `c72ace674454fe43411d3957ed89e9b3346b9103376f872715a5d0634cd916f6` |

`final-normal.log`, `final-asan-pinned.log`, `verified-parent.json` und die
älteren fehlgeschlagenen Logs sind in der privaten Quittung gehasht. Dort
liegen auch `verify_parents.py` mit den16 geerbten Commands und `finalize.py`
für die abschließende O_EXCL-Quittung. Private Dateien0600/Belegordner0700.
Alle eigenen Test-/Compiler-/Generatorjobs sind regulär beendet; es läuft
keine unbeaufsichtigte Weiterarbeit. Root hat Header und vollständige Tests
statisch unabhängig gelesen und vor Integration keine weiteren kritischen
oder wichtigen Befunde gemeldet; eigene Rootchecks/Integration bleiben getrennt.
