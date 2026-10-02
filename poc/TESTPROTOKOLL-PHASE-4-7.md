# Testprotokoll – Phase 4 bis 7: KI, Population, Presence, Multi-Server

**Status: VORBEREITET, NICHT ABGENOMMEN.** Voraussetzung je Phase: alle vorherigen Phasen vollständig bestanden. Keine Runtime-Evidenz für Phase 4–7 vorhanden. Die Standalone-Logik (Targeting, Waffenwahl, Waypoints, Populationsregeln, Presence-Jitter) ist in `poc/botcore/botcore_ai.h` implementiert und durch `test_botcore_ai.cpp` sowie `Test-FleetAndPopulation.Tests.ps1` abgedeckt – das ersetzt **keine** native Abnahme.

---

## Phase 4 – einfache KI / externe Navigation

**Start:** `Scripts\Phase4Ai.ini` (`bot_iAiMode = 1`), optional `bot_strWaypoints`.

Harte Grenzen dieser KI-Stufe (bewusst): nur lesende replizierte Spieler-Snapshots; keine Sichtlinien-/Kollisionsprüfung; Waypoint-Graph nur als Stuck-Fallback, von Hand pro Map gepflegt; keine CecilBot-Simulations-Entities.

| # | Prüfung | Erwartung | Ergebnis | Notiz / Beweis |
|---|---|---|---|---|
| 1 | Zielwahl | Bot dreht auf den nächsten lebenden Nicht-Lokal-Spieler auf und verfolgt ihn; Zielwechsel bei Tod des Ziels | | |
| 2 | Kein Blindfeuer | Ohne lebendes Ziel feuert der Bot im KI-Modus nicht | | |
| 3 | Waffenwahl | Distanzband-Wechsel sichtbar (nah: Shotgun-Klasse, mittel: Tommygun/Minigun, fern: Sniper/Laser sofern vorhanden); keine Raketen-/Grenade-Autowahl | | |
| 4 | Stuck-Erkennung | Bot an Wand: nach ~2 s Jump-Impuls im Log (`[BotDriver] botN stuck`), danach Fortschritt | | |
| 5 | Waypoint-Fallback | Mit gepflegter Waypoint-Datei: Stuck löst Umweg über Graphknoten aus; fehlerhafte Datei deaktiviert Navigation laut Log | | |
| 6 | Sync unverändert | 10-Minuten-Lauf im KI-Modus ohne SYNCCHECK-Kick/Desync/Crash (`Test-Phase1Telemetry.ps1 -SyncMinutes 10`) | | |
| 7 | Vanilla-Koexistenz | Observer unverändert verbunden; CRC OK; Frags werden dem richtigen Bot zugeschrieben | | |

**Ergebnis Phase 4:** ☐ BESTANDEN  ☐ FAIL

---

## Phase 5 – Population Manager

**Start:** `Manage-BotPopulation.ps1 -Config <fleet.json> -StateDir <neu> -TargetPopulation N -ReservedHumanSlots R`.

Regeln (Spiegel `botcore::PopulationStep`): Zielpopulation auffüllen, reservierte Human-Slots nie belegen, Menschen verdrängen Bots, eine Aktion pro Poll, keine künstliche `GetPlayersCount()`-Semantik (Zählung nur über die normale `\players\`-Antwort + Namenspräfix).

| # | Prüfung | Erwartung | Ergebnis | Notiz / Beweis |
|---|---|---|---|---|
| 1 | Auffüllen | Leerer Server erreicht TargetPopulation schrittweise (gestaffelte, gejitterte Joins laut `population-log.jsonl`) | | |
| 2 | Human-Priorität | Menschlicher Join über Target → innerhalb weniger Polls verlässt genau die nötige Zahl Bots den Server (bevorzugt `graceful`) | | |
| 3 | Reserve | Bei fast vollem Server bleiben R Slots dauerhaft frei; „Server full!" trifft nie einen Menschen wegen Bots | | |
| 4 | Wiederauffüllen | Nach menschlichem Leave füllt der Manager wieder auf Target auf | | |
| 5 | Zustand konsistent | `population-state.json` deckt sich mit laufenden Prozessen und `\players\` | | |
| 6 | Langlauf | 60 Minuten Manager-Betrieb mit mehreren Human-Join/Leave-Zyklen ohne Fehlentscheidung/Oszillation | | |

**Ergebnis Phase 5:** ☐ BESTANDEN  ☐ FAIL

---

## Phase 6 – Presence / Chat

**Start:** `Scripts\Phase6Presence.ini` (Chat) + Manager-Jitter (Join/Leave) aus Phase 5.

| # | Prüfung | Erwartung | Ergebnis | Notiz / Beweis |
|---|---|---|---|---|
| 1 | Join-/Leave-Verzögerungen | Keine zwei Bot-Joins im selben Sekundenraster; Delays variieren (LCG, `population-log.jsonl`) | | |
| 2 | Namensprofile | Bots tragen Namen aus dem gepflegten Pool (`BotNames.sample.txt`-Kopie); keine Duplikate serverweit | | |
| 3 | Chat niederfrequent | Chatzeilen erscheinen beim Observer; Abstände gejittert (±50 % um `bot_fChatPeriod`), keine identischen Muster zwischen Bots/Instanzen (`bot_iChatSeed` verschieden) | | |
| 4 | Chat über normalen Pfad | Chat kommt als regulärer Spielerchat an (Absender = Bot-Name), keine Konsolen-/Serverinjektion | | |
| 5 | Kein Sync-Einfluss | 30-Minuten-Lauf mit aktivem Chat ohne Kick/Desync/Crash | | |

**Ergebnis Phase 6:** ☐ BESTANDEN  ☐ FAIL

---

## Phase 7 – mehrere Dedicated Server

**Start:** `Start-ServerFarm.ps1 -Config <farm.json> -State <neu>`; je Instanz eigener `Scripts\Dedicated\<name>\`-Ordner mit `net_iPort = <port>;` und eigene Fleet-/Population-Konfiguration.

| # | Prüfung | Erwartung | Ergebnis | Notiz / Beweis |
|---|---|---|---|---|
| 1 | Getrennte Ports | Beide Instanzen gleichzeitig erreichbar (`\status\` auf port+1 je Instanz); keine Portkollision | | |
| 2 | Getrennte Bot-Gruppen | Jede Instanz nur „ihre" Bots (Präfix/Profile); keine Querverbindungen | | |
| 3 | Getrennte Populationen | Zwei Manager halten unterschiedliche Targets stabil (z. B. 12 vs. 8) | | |
| 4 | Server unverändert | Weiterhin keinerlei Binary-Tausch auf Serverseite; Original-Logs je Instanz getrennt | | |
| 5 | Reproduzierbarer Start/Stop | Farm-Start/Stop über State-Dateien wiederholbar; Exitcodes dokumentiert | | |
| 6 | Koexistenz-Soak | 60 Minuten beide Instanzen parallel mit Bots + menschlichem Join/Leave ohne Abbruchkriterium | | |

**Ergebnis Phase 7:** ☐ BESTANDEN  ☐ FAIL

---

**Abbruchkriterien aller Stufen (Spec):** `MSG_SYNCCHECK`-Kick, sichtbarer Desync, Crash, Doppel-Entity/GUID-Kollision, Bot nicht als regulärer Spieler behandelt. Erst Ursache dokumentieren und beheben, dann skalieren.
