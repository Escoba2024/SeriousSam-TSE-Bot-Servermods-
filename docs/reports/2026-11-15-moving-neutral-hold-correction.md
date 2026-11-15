# Neutraler Waffenweg: tatsächliche Bewegung von Stillstand trennen

Der echte SDK107-Bridge-Reproducer zeigte einen konkreten Mechanismus im
unveränderten029-Header: Bei neutralem Navigatorwunsch läuft der2s-Holdtimer
weiter, auch wenn sich die tatsächliche Position erheblich verändert.
`BotSupplyTick` verwarf den gehaltenen W9-Versuch als `unreachable_hold` bei
Tick42. Der zugehörige geschlossene029-Fall bleibt unverändert dokumentiert
im [vorherigen Audit](2026-11-15-build029-skulls-closed-audit.md).

Der kleine Produktivdelta beobachtet ausschließlich den bereits vorliegenden
Motioninput. Nur ein gewöhnlicher gemappter Weaponversuch auf einer passenden,
ungesperrten Navigator-Kante kann Positionsfortschritt anrechnen. Spieler-,
Worldpointer-, Entity-/Generation-, Graphspeicher-/Navigatorreset-, Item-,
Goal-/Source-/Hop- und Versuch-/Deadlinebindung müssen identisch bleiben.
Der direkte SDK107-Worldpointer wird nur verglichen, niemals dereferenziert.
Der echte Caller hat Alive/Frame bereits geprüft; es kommt kein Engineaufruf
hinzu. Die World-/Navladehülle ersetzt die vollständigen SupplyStates; Reset,
Tod und ClearGoal verwerfen die neue Historie ebenfalls.

Bei aufeinanderfolgenden Source-Ticks, gleichem Tickquantum, exakter Gravity
und höchstens bestehender0,25s-Beobachtungslücke setzt erst eine tatsächliche
volle3D-Verschiebung von mindestens0,75m den vorhandenen Holdtimer zurück.
Die Distanz stammt aus `CecilNavigator::Update`; die Frischegrenze aus
`CecilGroundProgress` in `cecil_motion.h`. Weder Radius noch2s-Grenze noch
GoalDeadline werden geändert. Keine neue Bewegung, Ankunft, Groundsupport,
Physicsfreigabe oder Flightauthority entsteht. Velocity, FALL-Zustand und
beabsichtigte Bewegung reichen nicht. Neue/ungültige/gewechselte Kontexte
erzeugen nur einen passiven Anker und keinen frischen2s-Bonus. Der vorhandene
erste Hold-/Hopwechselpfad bleibt unverändert.

Die Fixture benutzt die echten267-/112-/0-Koordinaten, Radien, Flags und die
gerichtete267→112-Kante mit W9-Item1025. Hinter112 ist der restliche Weg auf
eine direkte Verbindung zuGoal0 reduziert. Zwischen den zwei belegten nativen
Höhenankern sind die20Hz-Positionen ausdrücklich synthetische Testwerte.
Dies ist ein Mechanismusnachweis, kein vollständiger Topologie-/Flug- oder
Retail-Kollisionsreplay und keine nachgewiesene native Verbesserung.

Tatsächlich ausgeführte Prüfungen:

| Prüfung | Ergebnis und Grenze |
| --- | --- |
| Erster Lauf | Compilerfehler: alter Bridge-Stub kannte den passiven DriverFinal-Receipt noch nicht; erhalten, kein Behavior-RED |
| Unveränderter Header mit schmal korrigiertem Teststub |3748Checks/1echter Fehler: bewegte Neutralpose endet Tick42 |
| Erste Korrektur, normale vollständige Bridge |3933Checks/0Fehler |
| Finale vollständige Bridge mit ASan/UBSan |3968Checks/0Fehler, Exit0 |
| Bewegte Position, Velocity0 | Versuch bisTick84 erhalten, GoalSince0/Deadline45 unverändert |
| Stationär, FALL, Velocity-only oder vor Ablauf unter0,75m | Weiterhin Tick42 `unreachable_hold` |
| Fortschritt bisTick4, danach Stillstand | Weiterhin Tick44, genau2s nach letztem Fortschritt |
| Bewegung bei festem Deadline1,5 | Weiterhin Tick30 `timeout` |
| Produktionshelfer direkt |0,749/0,75m-Grenze; Kontext-/Tick-/Clock-/dt-/Gravity-/World-/Navwechsel, NoGoal/Follow/Sonderpfade; keine zusätzlichen Rays/World-Lookups |
| Ganze Header-/Testinverse | Unveränderter029-Header und alle alten Bridge-Tests exakt wiederhergestellt |

Alle alten GroundedReplan-/Support-/Budget-/Safetytests bleiben erhalten.
Nur der Bridgeanschluss ergänzt den tatsächlichen Formatterheader und einen
neutralen lokalen Receipt für das schon produktive Driverprädikat. Kein
altes Prädikat oder alter Test wurde abgeschwächt. Keine weitere Diagnose,
kein Windowsbuild, kein Native-/Liveeingriff und keine A4-Abnahme erfolgte.

Reproduktion vom Worktree mit vorhandenem SDK:

```sh
python3 -B poc/candidates/redstation-supply-20261107/test_cecil_native_bridge.py \
  --support-dir poc/candidates/redstation-supply-20261107 \
  --sdk-player /srv/tse-sdk-20261021/Sources/EntitiesMP/Player.es --sanitize
```

Private Logs, genaue Source-/Loghashes und die vollständige inverse Prüfung:
`/srv/tse-moving-neutral-hold-evidence-20261115/`. Rohspieleridentitäten oder
Retaildateien gehören nicht zu diesem Commit. Root übernimmt Review und
Integration; ein neuer Kandidat braucht weiterhin eigene native Abnahme.
