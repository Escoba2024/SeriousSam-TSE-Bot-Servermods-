# Public011: unterschiedliche Beobachtungsphasen im selben Spawn-Tick

Der Lauf `arena011public-checked-swap0-trial-1-000606` bleibt **FAIL** (`initial placement mismatch slot6`). Seine aufbewahrten Inventarproben belegen aber einen Phasenwechsel innerhalb desselben positiven Spawn-/Game-Ticks `0.9000001549720764`. Alle neun Spieler erreichen darin auch die exakten unveränderten Referenzpositionen einschließlich Yaw. Das ist keine rückwirkende Laufabnahme und kein Beweis des ersten Simulationszustands. Die bereinigten Zahlen, Zeilen und privaten Dateihashes stehen in [der JSON-Beilage](2026-11-12-native011-initial-phase.json).

## Tatsächliche Beobachtungen

In `inventory.jsonl`, Zeile 8 (elapsed `0.07571882591582835`), haben Slots 6–8 Physicsflags `0x40000287`. In Zeile 11 (elapsed `0.1165362629108131`) haben dieselben Slots bei unveränderter Spawn- und Game-Uhr `0x40000284`. HP=100, Armor=0, Owned=3, Current/Wanted=2, Render=3, CurrentTranslation=(0,0,0), Support=null und LastButtons=0 bleiben gleich. Slot 6 verändert sich von Y=`0.4749999940395355`, Yaw=`-60.0` auf Y=`0.3999999761581421`, Yaw=`-60.00000762939453`. Analog erreichen Slots 7/8 die unveränderten Referenzwerte. Zeilen 10–12 enthalten zusammen alle neun passenden neutralen Proben.

Die Referenz stammt unverändert aus `arena008public-checked-swap0-trial-1-225500`: Zeilen 12/13 enthalten die neutrale Phase bei Tick `0.7500001192092896`; Zeile 15 wiederholt sie. Erst Zeile 17 zeigt Tick `0.8000001311302185`, wieder aktivierte Gravityflags `0x40000287` und fallende Bewegung (Slot 6: Y=`0.32499998807907104`, Vy=-1.5). Referenzdatei SHA256: `073f4d9af0c3a1075462716aef09f628913597b5c80c5670cc4578df9861e66c`.

## Originale Retail-1.07-Gegenprüfung

Originale `EntitiesMP.dll`, SHA256 `7f595f2a7fc96a978b3467983e8f17c70d827f17a5f4ee887f9c7a1f20b1d350`; statische `objdump`-Prüfung, keine Runtime-Eingriffe:

- `InitializePlayer` (`60402c40`) setzt bei `60402d72` Physicsflags `0x40000287`.
- `PostMoving` (`603fc320`) prüft bei `603fc45f` `PLF_APPLIEDACTION`; der Pfad ohne dieses Bit ruft bei `603fc46a` `SetUnconnected` auf.
- `SetUnconnected` (`603fc490`) ruft bei `603fc4b2` `ForceFullStop` auf und löscht bei `603fc4bd` mit `and al,0xfc` exakt Physicsbits 0/1; der Setter folgt bei `603fc4c0`.
- `SetConnected` (`603fc540`) setzt dieselben Bits bei `603fc55a` mit `or al,3`. `ApplyAction` (`603fe900`) prüft bei `603fe92c` den Nichtverbunden-Status, ruft bei `603fe931` `SetConnected` auf und setzt bei `603fe941` `PLF_APPLIEDACTION`.
- Der tatsächliche SDK107-Header `Sources/Includes/Engine107/Engine/Entities/Entity.h:116–117` bezeichnet Bits 0/1 als `EPF_ORIENTEDBYGRAVITY`/`EPF_TRANSLATEDBYGRAVITY`. `Sources/EntitiesMP/Player.es:2750–2797` enthält die entsprechenden PostMoving-/Verbindungswege; Initialisierung ab 4964 und Physicszuweisung 4991.

Das belegt die unterschiedlichen Flagphasen. Die vollständige Instruktionskette, die Y um ungefähr 0.075 verändert, wurde nicht verfolgt; `30 * 0.05²` bleibt eine damit vereinbare Erklärung. Auch zwei gleiche Speicherlesungen machen die Mehrfeldprobe nicht atomar. Der neue Qualifier prüft die beobachtete Konfiguration, ohne zu behaupten, den ursprünglichen `SetUnconnected`-Aufruf unmittelbar aufgezeichnet zu haben.

## Prospektiver privater v2-Draft

Separates Verzeichnis `/srv/tse-nav-public011-v2-draft-20261112`; Frozen011 und sein FAIL bleiben unverändert. Der Controller erhält einen eigenen `arena011public-v2`-Prefix. `InitialObservations` bewahrt die erste positive Spawnprobe dauerhaft auf und wählt unabhängig von Placement/Yaw die erste neutrale Probe je tatsächlichem Slot. Voraussetzung: positiver endlicher gemeinsamer Spawn-Tick gleich Game-Tick; HP100, Armor0, Owned3, Current/Wanted2; Physics exakt `0x40000284`, Render3, Velocity exakt null, Support null, LastButtons0. Keine pauschale Bitmaskierung anderer Physicsbits.

Auch die rohe erste Probe muss dieselben unveränderten Lebens-/Inventar-/Bewegungsbedingungen erfüllen; ausschließlich `0x40000287` ist zusätzlich als frühere Flagphase erlaubt. Spätere Heilung, Inventarwechsel, andere Identität, neuer Respawn oder Abwarten nach früher Aktivität können die Abnahme nicht retten. Erst nach dieser Auswahl werden Placement und Yaw aller neun Slots exakt gegen die unveränderte Referenz geprüft. Ein ungünstiger erster qualifizierter Ort wird nie ersetzt. Beide Proben werden getrennt archiviert; `first_simulation_state_proven` bleibt false.

Gezieltes RED gegen die alte Policy: realer gespeicherter FAIL-Replay, fehlende neutrale Feldfilter und erster falscher qualifizierter Ort. Zusätzlich RED für versuchte spätere Rettung nach früher Aktivität. GREEN: **24 Offline-Tests**, einschließlich Referenz008-Replay, beider adversarialer Ortsfolgen, fehlender Slots, strikter Flags/Velocity/Support/Input, Identitäts-/Lebenswechsel, getrennter Archivierung, unveränderter DLL-/Config-/Dependency-Pins und importierter Controller ohne Runtimeaufruf. Kommando im privaten Draft: `python3 -m unittest test_controller_policy test_initial_phase -v`.

Keine neue Runtime oder A3-Freigabe. Die prospektive Phasenauswahl benötigt Rootreview und einen neuen nativen Lauf.

## Gegenreview und privater v3-Nachtrag

Der unabhängige Combat-Review fand nach dem v2-Entwurf eine konkrete Lücke: Auf eine erlaubte rohe Erstprobe (`physics=0x40000287`) konnten eine Zwischenprobe mit HP90/Velocity=(1,0,0) und danach wieder eine neutrale HP100-Probe folgen. v2 ignorierte die Zwischenprobe und akzeptierte die spätere. Die oben beschriebene Absicht, frühere Aktivität nicht zu retten, war in v2 daher **nicht vollständig umgesetzt**. v2 bleibt unverändert als Reviewbeleg; keine Runtime wurde damit durchgeführt.

Separater Draft `/srv/tse-nav-public011-v3-draft-20261112`: Jede beobachtete Zwischenprobe eines bereits roh erfassten, noch nicht neutral qualifizierten Slots muss die unveränderten Baseline-/Kinematik-/Identitäts-/Lebensbedingungen erfüllen. Die erste Abweichung bleibt dauerhaft als Fehler erhalten, maximal ein Eintrag je Slot. Das geschieht vor dem bisherigen Überspringen fehlender Spieler oder ungültiger/Null-Spawnuhren. Nach der ersten neutralen Probe ändern spätere normale Gameplayzustände die eingefrorene Anfangsauswahl nicht. Position/Yaw beeinflussen die Auswahl weiterhin nicht und werden anschließend exakt verglichen. Das zusätzliche Archiv `pending-phase-errors.json` erhält die Ablehnungsgründe auch bei einer Exception aus `finish()`.

RED gegen v2: 13 konkrete Zwischenabweichungen und eine abweichende Game-Uhr, insgesamt 14 fehlgeschlagene Negativfälle. GREEN v3: **29 Offline-Tests**, einschließlich begrenzter unveränderlicher Fehleraufzeichnung, erlaubter Zwischenphase mit anderer Position, unveränderlicher falscher erster neutraler Position und gespeichertem echten FAIL-Replay. Policy SHA256 `c2314263f266b49fe86d6e6b6c21f485aa6e014b2d132550e00ae52797763e2e`, Controller SHA256 `403f714aeeef32fee8941eae621a208a36fd1abb13134365208cb3a51bbca24f`. Keine native oder Erstzustandsabnahme daraus.
