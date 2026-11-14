# A3-Swap1: Spawnzählung und Beobachtungsgrenze

Status: **DIAGNOSIS_ONLY**. Claim `a4_diagnosis`, Branch `codex/20261114-a3-swap-spawn-diagnosis` ab Root `1704b21`. Ausschließlich geschlossene Dateien lesend untersucht; keine Runtime-, Display-, Netzwerk-, Compiler-, Test- oder Analyzer-Ausführung, keine Produktionsänderung. Root-Handoff unverändert.

## Befund

Der geschlossene Swap1-Lauf `direct020-hard-probe-root-pair12-swap1-20261114-155849` hat Native-Status `PASS_LIMITED_A3_DAMAGE_OBSERVATION_REVIEW_REQUIRED`, 120,04979534889571 Sekunden Beobachtung und Result-SHA256 `b0562be36a881553e25fcbd8199dd6f40ab6935722acf971f3d77a4b211191d8`. Root meldete vier normale Closes und unabhängigen 640-Dateien-/4-Schlusslog-Restore. Die vier archivierten Schlussloghashes stimmen mit dem Result überein. Das ist keine erfolgreiche A3-Stärkeabnahme; der geschlossene Vergleich bleibt am unveränderten Analyzer fehlgeschlagen.

Die einzige Lebenszählungsdifferenz betrifft **botA/local1, Serverslot2, STARK**. Die Raw-Inventarbeobachtungen enthalten drei Spawnclocks, das vollständige während der Schlussauswertung kopierte Clientlog vier `CecilSpawn`-Ereignisse. Es gibt einen positiven vierten Source-Spawn, aber keine Inventarbeobachtung dieses vierten Lebens. Damit ist eine Beobachtungslücke am Schluss belegt; eine falsche Slot-/PID-/Entitätszuordnung wird durch die untersuchten Daten nicht gestützt.

| Rolle/local | Serverslot | Inventarleben | Client-Spawns | Client-Tode |
|---|---:|---:|---:|---:|
| botA/0 | 0 | 1 | 1 | 0 |
| botA/1 | 2 | 3 | 4 | 3 |
| botA/2 | 3 | 3 | 3 | 2 |
| botA/3 | 4 | 4 | 4 | 3 |
| botB/0 | 5 | 4 | 4 | 3 |
| botB/1 | 6 | 2 | 2 | 1 |
| botB/2 | 7 | 3 | 3 | 2 |
| botB/3 | 8 | 5 | 5 | 4 |

## Konkrete Zeit- und Zeilenbelege

Die tatsächlichen BotDriver-Anbindungen stehen privat in `botA.log:183/196/200/204` und `botB.log:183/196/200/204`: botA→Slots0,2,3,4; botB→5,6,7,8; Original→1. Dies entspricht `result.actual_slot_mapping`. Alle 2071 Inventarzeilen binden denselben gestarteten Server-PID/Start; alle vorhandenen Spieler stimmen nach Slot, interner Entität und Pointer mit der privaten Damage-Registry überein. Beide endgültigen Bot-PID-/Startpaare stimmen mit ihren Cleanupidentitäten überein. Der vorherige botA-Bootstrap wurde als eigenes früheres Start-/Closepaar behandelt; dessen Identität wird nicht für die endgültige Zuordnung verwendet.

Für botA/local1:

| Beobachtetes Leben | Server-Spawnclock | Inventarzeilen | Erster beobachteter Tod | Clientgeneration |
|---|---:|---|---:|---:|
| 1 | 0.9000001549720764 | 40–1163 | 64.84935760498047 | 6 |
| 2 | 66.29944610595703 | 1164–1371 | 77.20011138916016 | 7 |
| 3 | 78.70020294189453 | 1372–2071 | 119.05266571044922 | 8 |

Das sind Zeilenbereiche mit überlappenden Gruppensamples, keine lückenlos für nur diesen Slot geschriebenen Zeilen. Ihre Entitätszuordnung ist unverändert. Für alle25 beobachteten Botleben stimmen die jeweilige Todanzahl und das boolesche Vorliegen eines brauchbaren Waffenbesitzes mit den entsprechenden Source-Tod-/Pickupintervallen überein; null zusätzliche Abweichungen wurden in dieser gezielten Gegenrechnung gefunden. Daraus folgt keine Vollständigkeit eines nicht beobachteten Lebens. Leben2 und3 dieses Slots haben innerhalb ihrer beobachteten Alive-Samples keinen brauchbaren Waffenbesitz; diese negativen Belege bleiben bestehen.

Der letzte Tod des dritten Lebens ist zusätzlich im nativen Damagestrom belegt: Sequenz206, Eintritt `16:01:36.549 UTC`, Austritt `16:01:36.550 UTC`, Serverclock `118.9526596069336`, unveränderter Spawnclock `78.70020294189453`, HP `1.631765365600586`→`-28.368234634399414`. Sequenz207 bei `16:01:36.586 UTC`, Clock `119.0026626586914`, ist danach ein Treffer auf den bereits toten Körper. Keine Übertragung dieses Corpseereignisses in einen lebenden Killbeleg erfolgt. Alle207 Damage-Records haben konsistente Sequenz, identische Vorher-/Nachher-Lebensclock und Tick sowie Registry-/Pointerbindung; die übrige vollständige Vergleichsauswertung hinter der fehlgeschlagenen Assertion wurde damit nicht ersetzt.

Die letzten Slot2-Inventarbeobachtungen sind Zeilen2069 und2071: Loopelapsed `119.87010943493806`, Serverclock `120.6027603149414`, noch Spawnclock `78.70020294189453`, HP `-58.36823272705078`. Die letzte vorhandene botA-Sessionprobe hat ebenfalls Clock `120.6027603149414`.

Danach enthält `botA.log:1891` einen zusätzlichen `CecilSpawn`, local1, Driver-Tick2614, Generation9, Respawnzähler4. Direkt zugehörig folgt `CecilWeaponObserve` in Zeile1894 mit demselben Tick/Generation und **clientseitiger** `native_time=120.702766`; Zeile1895 zeigt Tick2616/Generation9 und `native_time=120.802773`. Es gibt keine zugeordnete Inventarzeile mit einem vierten Server-Spawnclock. Source-Tod in Zeile1859 und States in1862/1874 zeigen zuvor Generation8, Todzähler3, Respawnzähler3. Es ist kein zurückgesetzter oder kollidierter Zähler: der Sourceübergang auf Generation9 ist positiv protokolliert.

Wichtige Grenze: Client-Nativeclock, Serverclock und Wallclock sind verschiedene Messungen. Clientlogzeilen haben hier keinen eigenen Hostzeitstempel. Der numerisch spätere clientseitige Clockstand liegt nach der letzten gleich großen botA-Sessionprobe und die neue Serverlebensbeobachtung fehlt. **Nicht exakt beweisbar ist, ob der Spawn noch im ungesampelten Schlussintervall des nativen Fensters oder erst knapp danach lag.** Eine lineare Tick→Wallzeit-Interpolation wäre ein neuer unbelegter Schluss. Der Damage-Window-Endmarker lautet `16:01:38.3925217 UTC`, `window_completed` wurde `16:01:38.465029 UTC` geschrieben; die späteren regulären Rollencloses sind nicht die Samplegrenze.

## Quellvertrag und Ursache des Analyzerfehlers

`analyze-direct020.py:37–47` berücksichtigt ausschließlich Inventarhüllen mit `elapsed` und erzeugt Leben aus tatsächlich vorhandenen `(slot, entity, spawned_tick)`-Beobachtungen. Zeilen63–70 lesen dagegen sämtliche Spawnereignisse des gesamten `botA.log` und verlangen `len(inventory_lives)==len(client_spawns)`. Für diesen Slot liefert die Assertion folgerichtig `(1,3,4)`.

Der archivierte `controller-source.py:300–363` liest Session/Inventar nur innerhalb der 120-Sekunden-Schleife und schläft anschließend wie vorgesehen. Zeile364 setzt danach den Damage-Window-Endmarker. Erst Zeilen369–372 lesen und kopieren die weiterhin laufenden Clientlogs, bevor der normale Cleanup beginnt. Der Vertrag garantiert somit keine identischen zeitlichen Endgrenzen von Memorybeobachtungen und vollständigem Log-Snapshot. Genau diese unbewiesene Gleichmächtigkeit trifft die Assertion hier.

Der Build020-Quelltext bestätigt die Clock-/Ereignisbedeutung: `Sources/Game/BotSupplyNative.h:1465–1478` erhöht Death/Respawn/Generation an beobachteten Alive-Übergängen und protokolliert `CecilSpawn`. `Sources/Game/BotDriver.cpp:1136–1151` führt den Driver-Tick seit eigenem Join; dieser ist keine absolute Server-/Wallzeit. `BotDriver.cpp:660` setzt den Weaponobserver-Nativeclock über den eigenen `_pNetwork->GetGameTime()`; Zeilen1627–1629 rufen diese Beobachtung im gleichen Driverdurchlauf mit dem aktuellen Supplygenerationwert auf. Der zusätzliche Source-Spawn ist deshalb kein rein aus Inventarzählung erfundener Datensatz.

Der belegte Fehler liegt in der Gleichsetzung zweier unterschiedlich begrenzter Beobachtungsmengen. Offen bleibt die exakte Wallzuordnung des ungesampelten Spawns. **Keine Assertion entfernt, keine Toleranz gelockert, kein Spawn verworfen, kein Leben ergänzt und kein Vergleichsergebnis neu akzeptiert.** Eine Entscheidung über prospektiv benötigte Grenzbelege und die erlaubte Auswertungssemantik gehört in einen gesonderten Rootplan. Swap0-Erfolg ersetzt diese fehlende Swap1-Auswertung nicht.

## Reproduzierbarkeit und Handoff

Private Evidencebasis: `/srv/tse-milestone-a-evidence-20261111/direct020-hard-probe-root-pair12-swap1-20261114-155849`. Maßgebliche Datei-SHA256:

| Datei | SHA256 |
|---|---|
| result.json | `b0562be36a881553e25fcbd8199dd6f40ab6935722acf971f3d77a4b211191d8` |
| inventory.jsonl | `326f5790ee6988ccc0bb4777ddf57cec72f9af85c6bce7f1cea3a5a4bd7a1831` |
| botA.log | `512042bf6e2c477b2cfca8003287a03117d735a2a077888f12e5af04c9203017` |
| botB.log | `e673b881925cd72ba9ffe9c144a751faf3f877fab347288578bf54d1747cb25b` |
| session-health.jsonl | `73e2a92a2883029783af31643685048092c38336bbadc3649b2848bb740459c1` |
| frida-damage.jsonl | `4776bf9ee999e7ae9f1d463d1eeb5e640d59bd3bbfe5700041d5c3115da88381` |
| damage-cohort-registry.json | `5f3903b84391f31ff3a71e75a862cbc186042d4e1602e02b846ad857207d77aa` |
| controller-source.py | `f9cb4c4991d101e096787c5ccd5ee26a552b0a34dc8f43e600e7f75f07a7433a` |

Read-only Nachrechnung: JSON-Hüllen nach tatsächlichem `elapsed` filtern; alle vorhandenen Rows nach `(slot, entity, spawned_tick)` gruppieren; Client-Spawns je tatsächlichem local aus den `[CecilSpawn]`-Zeilen zählen; die acht obigen Paarzahlen vergleichen. Für alle Vorher-/Nachher-Damagewerte Sequenz, unveränderte Spawnclock/Tick und Registrypointer prüfen. Es wurde kein geänderter Analyzer oder Test zur Erzeugung eines PASS ausgeführt. Öffentlicher Inhalt enthält keine Anzeigenamen, GUIDs, Rohadressen oder Pointer.

Nächster Schritt ist Rootbewertung dieses Befunds vor jedweder neuen Auswertungs- oder Controlleränderung. Kein eigener Prozess, Runtimeauftrag oder Retry läuft.
