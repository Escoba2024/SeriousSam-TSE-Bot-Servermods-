# Passive Picker-Kustodie – Source-/SDK-Beleg, kein Nativefix

Keine Runtime/Pakete/DLLs verändert; isolierte portable Sourcevorbereitung.
Isolierter Worktree und Claim: `codex/20261115-a4-picker-custody`, Parent df1edd8.

Der tatsächliche SDK107-Body zeigte zuerst 3972 Checks/2 Behavior-FAILs:
normaler erfolgreicher Waffencommit und tatsächlicher No-anchor-Return waren
beide stumm; ihre jeweiligen Entscheidungsvorbedingungen bestanden. Neue feste
DIAG1-Quittungen erfassen die originalen Normalpicker-/Mapped-Guardbitmaps,
Scanfilter/Snapshotgrenze, gewählte Versuche und vorhandene Clear-/Nearest-
Resultate. Ein eigener Same-call-Arbitrationbeleg lässt das alte DriverFinal-
Schema und dessen Admission unverändert. Nur die tatsächlich kurzgeschlossen
ausgewerteten Operanden werden bekannt; SetAction ist kein ACK-/Physicsbeweis.

Weitere echte Behavior-REDs grenzten zunächst fälschlich als bekannt markiertes
not-ready Supply und fehlende Ursprungshints ein; danach GREEN. Ein Typ-/Snippet-
Compilerfehler im Testgenerator davor war kein Behavior-RED und bleibt separat
im privaten Log. Ein weiterer RED wies ein unzulässiges Match eines unbekannten
actor0 aus; positive Same-call-Kustodie erfordert jetzt eine nichtnullige Actor-
und Generationbindung sowie denselben Tick. Die normale Entscheidung ändert
sich dadurch nicht.

Vor Root-STATICONLY: SDK107 normal und ASan/UBSan jeweils4043/0. Die enge letzte
Snapshotergänzung zeigte anschließend zwei echte Behavior-REDs (fehlende Kopie
der ursprünglichen Inputposition/des gewählten Snapshotitems). Nach ausschließlich
Scalar-Kopien bestanden normal4047/0. Ein letzter strenger Rate-RED4048/1 zeigte,
dass Generationrebinding das Diagnoseintervall voreilig erneuerte. Es erneuert
dieses Intervall jetzt nicht; der frühere positive Test war dafür zu großzügig.
**Final normal4048/0 und ASan+UBSan4048/0**, beide nach dieser Korrektur, Exit0.
Alle Läufe seriell nice15,
mit echtem SDK107-Player-/Brush-/Ray-Vertrag und Windows-empty-far-Makro über dem
tatsächlichen Produktionssource. Höchstens acht normale Versuche/drei Hints,
1Hz/Life-/Reset-/Zeitumkehrgrenzen, tatsächliche Snapshot128-Grenze, invalid /
budget / leer-ohneCast / blocked / clear, Lazy-Guards und Formatfehler getestet.
Extremer Summaryformatfall einschließlich ursprünglicher Inputposition war
1003 Byte <1024; Attempt-/Origin-/Arbitrationformat und kurze Overflowbuffer
werden ebenfalls geprüft. Position/value/generation kommen ausschließlich aus
dem schon erzeugten Input bzw. dem tatsächlich gewählten Snapshot, nicht aus
einer zweiten Entity-/Playerabfrage.

Zwei vollständige Sourceinversen ergeben exakt die Parentdateien (Header777d196e,
Driver7af47d87); Änderungen an Radius-/Urgencyguards werden zurückgewiesen.
Zusätzlicher tatsächlicher Vergleich mit vollständig invertiertem Parent:
24 vollständige geordnete Operationlanes (12 Fälle × DIAG0/1), jeweils CURRENT0
gleich PARENT0 und CURRENT1 gleich PARENT1 einschließlich State/Action/RNG/Budget.
**Keine** globale DIAG0-vs-DIAG1-Querygleichheit: schon der Parent hat in drei
Recoveryfällen den zusätzlichen vorhandenen GetGameTime-Read des früheren
ReacquireDecision.End. Dieser Call wird weder herausgefiltert noch beseitigt.
Root hat genau diesen laneweisen Gegenbeweis als Ruling bestätigt.

Die neuen Schemafelder sind absichtlich explizit: normale `gates` Bit0=!goal,
Bit1=cooldown vorbei, Bit2=Search; `mapped` Bit0=goal gesetzt, Bit1=Cooldown,
Bit2=ungültige Feindistanz, Bit3=Feinddistanz<8, Bit4=Search aus, Bit5=HasRanged.
Jeweils `(known,true)` bewahrt originales Shortcircuit. `scan` enthält
scanned/count/Readcalls/Readfail/Rejected/Far/Close/Filtered/WindowFull/Reasonbits;
Readreasonbits0–18 entsprechen der festen Tabelle im Header,31 bedeutet UNKNOWN.
Probe0=uncalled,1=input-unbekannt,2=Budget,3=leeres Segment ohne Cast,
4=PhysicalCast-Helper fehlgeschlagen (ob die native Query lief bleibt UNKNOWN),
5=tatsächlich blocked,6=tatsächlich clear.
Origin und Attempt-Nearest enthalten höchstens die drei originalen Hints.
`pathKnown` trennt eine wirklich abgefragte gerichtete Pfaddistanz von keinem
Read; echtes inf bei diesem Read bedeutet unerreichbar, nicht erfundene Geometrie.
Die Summary endet am Pickerreturn; der zweite Refresh findet danach statt und
steht, soweit ausgewertet, im Same-call-Arbitrationrecord nach SetAction.

Pro Quellsekunde höchstens eine Summary+Origin+acht Attempts+Arbitration;
ein normaler Generationswechsel erneuert dieses Intervall nicht.
jeweils feste1024-Bytebuffer: maximal11264 zusätzliche Bytes/Batch, zusätzlich
zu existierendem DIAG1. Formatüberlauf ergibt einen expliziten PickerFault statt
erfolgreich abgeschnittenem Text. ClearGoal verlängert keine Aufnahme und ist
keine Freigabe; explizites Reset und Actor-/Generations-/Tickgleichheit bleiben
getrennt. Fehlender oder nicht zugelassener Pickeraufruf ist weiterhin UNKNOWN,
kein Beweis, dass ein Kandidat abgelehnt wurde.
Readfail-Reasonbits sind aggregiert, keine Zuordnung aller nichtgewählten
WeaponEntities und keine vollständige Erklärung einer stummen Kandidatenmenge.
Ein späterer Diagnoseauditor muss jeden PickerFault/overflow, fehlende erlaubte
Batchzeile oder ungeklärte Custody als Fehler/UNKNOWN behandeln; der Source
unterbricht dafür nicht die Simulation und behauptet selbst keinen PASS.

Reproduktion aus dem Repository, ohne Retailruntime:

```
nice -n 15 python3 -B poc/candidates/redstation-supply-20261107/test_cecil_native_bridge.py --sdk-player /srv/tse-sdk-20261021/Sources/EntitiesMP/Player.es
nice -n 15 python3 -B poc/candidates/redstation-supply-20261107/test_cecil_native_bridge.py --sdk-player /srv/tse-sdk-20261021/Sources/EntitiesMP/Player.es --sanitize
nice -n 15 python3 -B poc/candidates/redstation-supply-20261107/test_picker_custody_source.py
```

Der spätere Rootbuild muss den neuen `picker_custody.h` in seiner vollständigen
Source-/Overlayclosure einschließen. Es wurde kein Build-/Paketmanifest durch
diesen Sourceauftrag erzeugt oder verändert.

Grenzen bleiben sichtbar: bounded/throttled Pickerbatches sind keine vollständige
Ereignisliste, Snapshotzähler keine globale 128-Kandidaten-Rangfolge. Nicht im
Originalpfad ausgewertete Inputs/Proben bleiben unbekannt. Root muss Source-
Actor/Generation/Spawn/WPO über echte Epoch-/Registry-/NativeLife-Bindungen
zuordnen; keine SourceTick/20-Interpolation. Child-Engine-Stubs sind portable
Mechanismenbelege, keine Retailcollision-/Timing-/ABI-Abnahme. Keine Skulls-/
Resetursache bewiesen, kein Waffen-/A4-PASS, keine Promotion. Root entscheidet
separat über Sourceintegration, neuen Diagnosebuild und genau ein Fenster.
