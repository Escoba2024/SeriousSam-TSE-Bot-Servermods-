# A4 Build016: Rotationsgrenze und Aktivitätsbelege

## Ergebnis und Geltungsbereich

**Die neue Winkelbasis wird bei beiden Kartenwechseln bei allen acht Bots übernommen. Die vollständige A4-Abnahme bleibt FAIL**, weil die unveränderten Aktivitätsanforderungen in acht von 24 Slot/Phase-Kombinationen nicht vollständig belegt sind. Vier fehlende 1-Hz-Feuerzeilen sind durch native Feuerzustände samt serverseitigem Eingabebit als Abtastlücken erklärbar. Weitere Restlücken bleiben bestehen. Es wurde keine Anforderung ersetzt oder gelockert.

Trial: `/srv/tse-milestone-a-evidence-20261111/a4-reset016-early-inventory-20261112-104821`
Zeitraum laut Ergebnis: 2026-11-12T10:48:21.373214+00:00 bis 2026-11-12T10:53:27.033484+00:00.
Quelle für Endstatus: `result.json`, Fehler `reset observed but required per-phase active evidence incomplete`.

Die konkrete Versuchsfolge ist **Red Station → Red Station → Red Station** mit drei tatsächlich neu ausgeführten Kartenepochen. Die beiden hier genannten Kartenwechsel sind Reloads derselben Welt; ein erfolgreicher Übergang zu einer anderen Karte wird aus diesem Lauf nicht abgeleitet.

Diese Auswertung liest ausschließlich vorhandene Dateien. Geschrieben wurden nur diese Analyse und ihre JSON-Belege in einem neuen Analyseverzeichnis. Keine Runtime-, Paket-, Quellcode- oder Produktionsänderung; kein weiterer Versuch. Root bewertet Close/Restore und Gesamtfreigabe unabhängig.

## 1. Frische Kartenbasis und tatsächlicher Blick

| Slot | Alter Sollpitch vor Reload 1 | Alter Sollpitch vor Reload 2 | Übernommener nativer Pitch / erste lebende View |
|---|---:|---:|---:|
| A0 | 8.937° | -23.804° | 0° / 0° bei beiden Reloads |
| A1 | 79.697° | 104.778° | 0° / 0° bei beiden Reloads |
| A2 | 12.241° | -1.313° | 0° / 0° bei beiden Reloads |
| A3 | 114.528° | -17.437° | 0° / 0° bei beiden Reloads |
| B0 | 5.394° | 253.581° | 0° / 0° bei beiden Reloads |
| B1 | 0.123° | 22.068° | 0° / 0° bei beiden Reloads |
| B2 | 5.188° | -36.814° | 0° / 0° bei beiden Reloads |
| B3 | 68.725° | -6.118° | 0° / 0° bei beiden Reloads |

Für die erste Grenzübernahme wurden die **ungeschnittenen Closed-Logs** ausgewertet. Die Phasenlogs beginnen erst mit frischer CecilLoad-Veröffentlichung und zeigen bereits einen zweiten Attach innerhalb derselben Kartenepoche.

Rohstellen:

- `botA-closed.log`: erste Grenzen Zeilen 1777, 1781, 1784, 1787 sowie 3338, 3342, 3346, 3349.
- `botB-closed.log`: erste Grenzen Zeilen 1727, 1730, 1734, 1738 sowie 3336, 3338, 3342, 3345.
- Erste lebende View-/Input-/Last-Werte Phase 1: `phase-1-redstation/botA.log` Zeilen 69, 72, 75, 78; B Zeilen 69, 71, 73, 75.
- Erste lebende Werte Phase 2: `phase-2-redstation/botA.log` Zeilen 68, 71, 74, 76; B Zeilen 72, 90, 99, 108.

Besonders aussagekräftig ist **Phase 2 B0**: Entity-ID 559 und dieselbe World bleiben gleich, Attach ist 0; dennoch wird bei map_serial 3 / prior_map 2 der alte Sollpitch 253,580994° auf native_last 0° übernommen (`botB-closed.log:3336`). Bei Tick 3400 ist die erste lebende View 0°. Die ursprüngliche Inputallokation ist hier gewechselt; eine gleichzeitige Wiederverwendung von ID und Adresse ist in diesem Lauf nicht behauptet.

Die Diagnose vor dem ersten Spawn enthält teilweise noch nicht initialisierte View-Werte. Sie wurde ausdrücklich **nicht** als lebender Blick verwendet. Die erste lebende 1-Hz-Probe beweist außerdem nicht den allerersten Simulationszustand. Alle acht initialen lebenden Phase-0-Views sind ebenfalls 0°.

## 2. Normale Respawns getrennt

Es gibt 49 protokollierte normale Respawns innerhalb der Phasen: 14 / 15 / 20. In allen 49 Fällen bleibt die Entity-ID gleich. In 48 Fällen ist der native kumulative Pitch vor und in der ersten lebenden Folgeprobe exakt gleich; es gibt dabei keine neue BotRotationBaseline. Ein Folge-Sample enthält bereits eine kleine neue Zielkorrektur (Phase 1 A1: -0,4037724° → -0,2958188°, View 0,1079536°); daraus wird keine Basenänderung abgeleitet.

Beispiele:

| Phase / Slot | Respawn-Tick | Vorheriger nativer Last-Pitch | Erster lebender Last-Pitch / View | Beleg |
|---|---:|---:|---:|---|
| 0 / A1 | 950 | 77,5792160° | 77,5792160° / 0° | `phase-0-redstation/botA.log:1006,1021,1049` |
| 0 / A3 | 1206 | 114,5276642° | 114,5276642° / 0° | `phase-0-redstation/botA.log:1363,1366,1385` |
| 2 / A0 | 4478 | 24,4890213° | 24,4890213° / 0° | `phase-2-redstation/botA.log:910,929,941` |
| 2 / A2 | 4518 | -61,1999969° | -61,1999969° / 0° | `phase-2-redstation/botA.log:957,959,974` |

Damit wird normale kumulative Eingabe nach Respawn erhalten, während eine neue Kartenepoche eine frische Basis erhält. Alle 49 Vergleiche stehen im privaten `analysis.json`.

## 3. Frühe Inventardeckung

| Phase | Erster akzeptierter nativer Game-Tick | Letzter Early-Tick | Akzeptierte Gruppenproben | Spätere Registry |
|---:|---:|---:|---:|---|
| 0 | 0,950 | reguläre Erfassung | – | vorhanden |
| 1 | 7,400 | 18,350 | 131 | REGISTRY_CONFIRMED |
| 2 | 2,700 | 13,600 | 128 | REGISTRY_CONFIRMED |

Quelle: `result.json / early_inventory`, gebunden an Phase, Logoffsets, privat gepinnte Serveridentität und acht Entity-ID/Adresse/World-Tupel. Phase 1 erhält etwa 10,95 Sekunden zusätzliche Abdeckung vor der späten Registry, Phase 2 etwa 10,90 Sekunden. Die Gesamtinventarerfassung berichtet 3198 gültige Gruppenproben, 72 verworfene veränderte Zwischenlesungen, maximal 15,106 ms pro Probe.

Die eigenständigen Early-Receipt-Dateien wurden noch während SAMPLING geschrieben; die spätere Registry-Bestätigung steht im endgültigen `result.json`. Ein dort nicht erneut gespeicherter Zwischenstand wird nicht als fehlgeschlagene Bestätigung ausgelegt.

Die ersten 7,4 beziehungsweise 2,7 Game-Sekunden bleiben unvollständig abgedeckt. Kein Erstbesitz wird deshalb zu einer beobachteten Aufnahme umgewertet.

## 4. Alle 24 Aktivitätsfelder

Ready, Bewegung, Feuerzeile, beobachteter Nutzwaffenzuwachs und nativer Nutzwaffen-Feuerzustand sind weiterhin getrennte Anforderungen. **16/24 Slot/Phase-Kombinationen erfüllen alle fünf Felder**, acht nicht.

| Phase | Slot | Ready | Bewegung | Feuerzeilen | Echte Pickup-Leben | Native Nutzwaffen-Feuerproben | Δ Inputzähler |
|---:|---|---:|---:|---:|---:|---:|---:|
| 0 | A:0 | 69 | 50 | 0 | 1 | 0 | 2 |
| 0 | A:1 | 69 | 56 | 3 | 1 | 17 | 73 |
| 0 | A:2 | 69 | 60 | 3 | 1 | 0 | 33 |
| 0 | A:3 | 69 | 51 | 8 | 2 | 61 | 194 |
| 0 | B:0 | 61 | 56 | 9 | 1 | 58 | 195 |
| 0 | B:1 | 61 | 56 | 6 | 1 | 29 | 123 |
| 0 | B:2 | 61 | 55 | 14 | 2 | 82 | 272 |
| 0 | B:3 | 61 | 50 | 2 | 2 | 18 | 57 |
| 1 | A:0 | 60 | 55 | 0 | 1 | 4 | 33 |
| 1 | A:1 | 60 | 55 | 13 | 2 | 71 | 271 |
| 1 | A:2 | 60 | 53 | 0 | 1 | 2 | 10 |
| 1 | A:3 | 60 | 53 | 2 | 1 | 22 | 72 |
| 1 | B:0 | 60 | 56 | 1 | 2 | 4 | 16 |
| 1 | B:1 | 60 | 41 | 1 | 0 | 1 | 18 |
| 1 | B:2 | 60 | 52 | 3 | 1 | 20 | 66 |
| 1 | B:3 | 60 | 52 | 7 | 2 | 37 | 113 |
| 2 | A:0 | 74 | 69 | 2 | 1 | 3 | 22 |
| 2 | A:1 | 74 | 67 | 0 | 1 | 2 | 14 |
| 2 | A:2 | 74 | 66 | 0 | 0 | 0 | 0 |
| 2 | A:3 | 74 | 67 | 0 | 1 | 1 | 14 |
| 2 | B:0 | 74 | 64 | 7 | 1 | 47 | 152 |
| 2 | B:1 | 74 | 62 | 7 | 2 | 39 | 120 |
| 2 | B:2 | 74 | 65 | 11 | 2 | 63 | 232 |
| 2 | B:3 | 74 | 61 | 10 | 3 | 60 | 208 |

Quelle: `result.json / phases[*].slots`; Inputzähler aus den vollständigen sechs Phasenlogs. Er zählt emittierte Inputs, keine Treffer, Schäden oder diskrete Projektile. Differenzen über Kartenwechsel wären wegen weiterlaufender Zähler und der Rundenpause irreführend; verwendet werden nur Differenzen innerhalb derselben Phase.

### Vier belegte Abtastlücken der Feuerzeile

| Phase / Slot | Native Game-Ticks | Aktuelle Waffe | Inventory-Zeilen |
|---|---|---:|---|
| 1 / A0 | 43,249626; 43,399624; 43,499622; 43,649620 | 4, Shotgun | 1737, 1741, 1742, 1745 |
| 1 / A2 | 31,649803; 31,949799 | 4, Shotgun | 1526, 1529 |
| 2 / A1 | 72,549828; 72,699837 | 9, Laser | 3172, 3175 |
| 2 / A3 | 14,650038 | 9, Laser | 2194 |

Alle neun nach Phase/Slot/Entity/Lebensbeginn/Game-Tick deduplizierten Proben haben **health > 0, has_ammo = 1, fire_requested = 1 und server last_buttons = 1**, passende World/Entity-Adressen und dieselbe gepinnte Serverprozessidentität. Quelle: `inventory.jsonl`, genaue Rohfelder im privaten `analysis.json`. Überlappende Gruppen wurden dedupliziert. Colt-Proben und tote Spieler wurden nicht als Nutzwaffenfeuer gezählt. Dies ist ein Beleg für verpasste kurze Inputs in der 1-Hz-Zeile, kein Treffer- oder Schadensnachweis und keine nachträgliche Erfüllung des unveränderten fire_action_rows-Gates.

### Verbleibende Restlücken

- **Phase 0 A0:** fünf beobachtete Leben, nützlicher Besitz nur im ersten. Die erste Aufnahme liegt bei Game 3,400, dessen Tod bei 11,150. Kein natives Nutzwaffenfeuer. Der Inputzähler wächst erst bis zur letzten Probe von 0 auf 2 bei aktuellem Colt; damit ist Nutzwaffenfeuer nicht belegt. Pickups in `phase-0-redstation/botA.log:376,442`; letzter Zähler Zeile 1487.
- **Phase 0 A2:** ein Leben, nützlicher Erstbesitz erst Game 42,050. Alle 33 Feuerinputs liegen bereits vor der Waffenaufnahme im Colt-Abschnitt; der Zähler bleibt nach Tick 380 unverändert. Die drei vorhandenen Feuerzeilen sind ebenfalls Colt. Pickups Tick 1020 / 1113 in `phase-0-redstation/botA.log:1160,1252`. Es fehlt natives Nutzwaffenfeuer; längere Laufzeit würde dessen Auftreten nicht garantieren.
- **Phase 1 B1:** Cannon-Aufnahme ist im vollständigen Log tatsächlich vorhanden: `phase-1-redstation/botB.log:97`, Tick 1767, owned 3→8195. Vorher/nachher liegen außerdem gleiche Entity 560 und Generation 4 in Zeilen 92 / 104 vor. Die erste native Inventarprobe bei Game 7,400 sieht die Cannon schon besessen. Daher bleibt das streng native Vorher/Nachher-Pickupfeld unerfüllt. Keine Erfindung einer Aufnahme aus dem Erstsample.
- **Phase 2 A2:** über 74 Statezeilen bleibt shots 43→43; vier beobachtete Leben und drei Tode. Native Abdeckung Game 2,700–74,200; im vollständigen Log ausschließlich owned 3 oder 7. Zwei Aufnahmen 3→7 sind außerhalb der Nutzwaffenmaske 0x3df8 und erfüllen sie korrekt nicht (`phase-2-redstation/botA.log:1090,1169`). Weder Nutzwaffenaufnahme noch Nutzwaffenfeuer vorhanden.

Für A2 Phase 2 ist eine fehlende frische Mapbasis ausgeschlossen: zunächst lebende View/Input/Last 0°. Pitch -61,1999969° entsteht erst innerhalb dieser Phase zwischen Tick 3600 und 3620; er wird nicht aus der alten Map übernommen. Während des ersten Lebens melden die Lieferziele 248, 544, 267 und 243 vor Erreichen `reason=render_type` / unavailable (Zeilen 191, 214, 342, 778); die Bouncer-Flugfortsetzung endet tatsächlich mit arrived (Zeile 398). Das stützt eine reale nicht abgeschlossene Waffenversorgung in diesem Fenster, beweist aber allein weder eine neue Resetregression noch Fehlerfreiheit aller späteren Ziel-/Navigationsentscheidungen. Maximale kurze Stationarität ist kein Beweis gegen Schleifen. Eine ursächliche Änderung oder längeres Protokoll wird aus diesem Einzellauf nicht als Erfolg zugesagt.

## 5. Cleanup, Wiederherstellung und Ressourcen laut finalem Ergebnis

Das finale `result.json` meldet **vier von vier finalen Rollen geschlossen** (Server, botA, botB, Vanilla), jeweils mit stabiler Identitätswarteprobe, sowie **648 geprüfte Wiederherstellungspfade: 643 vorhandene Dateien und fünf wieder abwesende Pfade**. `restored=true`, Fehlerliste leer. Alle vier nach Close gesicherten Logs werden akzeptiert; die erfassten Kategorien BadSync, SyncDisconnect, CRC, Crash, InvalidAction und JoinFailure sind leer. Dies ist die Wiedergabe des Controllerreceipts; Root führt die unabhängige Gesamtbewertung.

| Ressourcenfeld | Gemessener Wert |
|---|---:|
| Host-Samples | 229 |
| Maximaler gemessener Host-CPU-Intervallwert | 57,037037 % |
| Minimales MemAvailable | 2.167.332.864 Bytes (2.018 GiB) |
| Minimal freier Datenträger | 17.203.908.608 Bytes (16.022 GiB) |
| Größte Samplelücke insgesamt | 46,741683 s |
| Größte Samplelücke Gameplay | 2,234942 s |
| budget_pass_claim | false |

Grenzen bleiben 75 % CPU, 1,5 GiB MemAvailable und 8 GiB Datenträger. Die Werte sind Intervallmessungen einschließlich anderer Hostlast, keine momentanen Spitzen; aus dem unverändert falschen Budget-Passfeld wird kein PASS gemacht.

## 6. Pins und Rohbelege

| Beleg | Bytes | SHA-256 laut finalem Controllerreceipt |
|---|---:|---|
| server-closed.log | 32736 | `b2d6b8681880408b5e67459fb64e4bab0c865640ff5fb49825870688c7a9dd37` |
| botA-closed.log | 1683755 | `429413136ab6b18199adbb1952444472db703ec4c06b8419b341342ce398c430` |
| botB-closed.log | 1774457 | `ecda182a2a6f7ec77f57b3d81cd09e5b0898c1f7058cec8d1b13f17c98fa198c` |
| vanilla-closed.log | 7805 | `ae534ed995547887eba13c3f44706ea97b9ac125c37eb5256ed5d1259edb073b` |

Weitere Pins:

- `result.json`: `e48cf93025d0c158a8c396e0722b14ad7d933e7d582cc2ea806f4dec5f8acebf` (vollständig gelesen, 310101 ASCII-Bytes stimmen mit Remote-Dateigröße überein).
- Build016 DLL: `e5a80634b5247c900ae25b5b18869c433c30dcfb49b890338fb231da63b04825`.
- Laufender eingefrorener Controller: `1c97519925808ffad0e315a8f7bca989f7836e1e61bcd29d7c57eb8d1c09310c`.
- Passiver Inventarreader: `920613df96771c14d3600f7f15fbbf5ae44254365774a9168fe16dbcee735cbb`.
- Buildsource: `58e8559903d999772218a6b5fd1d042b1759b547`.

Alle relativen Rohpfade und Zeilennummern oben beziehen sich auf den vollständigen Trialpfad am Anfang. Das Analyse-JSON enthält sämtliche 16 Grenzvergleiche, 49 Respawnvergleiche, 24 Aktivitätszeilen, neun deduplizierte native Feuerbelege, verbleibende Zählerverläufe und die unveränderten Abschlusswerte. Alte FAIL-Trials bleiben unverändert.

## Root-Verifikation

Root hat Analyse- und Ergebnis-Hashes sowie alle vier abgeschlossenen Rohlogs unabhängig nachgehasht. Anschließend wurden sämtliche648 aktuell restaurierten Fixturepfade erneut direkt geprüft:643 Dateien stimmen im SHA256, fünf temporäre Pfade fehlen wieder. Die Quittung liegt privat unter `a4-build016-analysis-root-verification.json`. Der Gesamtstatus bleibt unverändert FAIL. Die vollständige JSON-Auswertung liegt privat in `/srv/tse-a4-build016-analysis-20261112-104821/analysis.json`.
