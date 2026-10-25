# Integrationsplan Item-Utility-AI → Human-KI (Pfad D)

**Datum:** 25.10.2026 · **Agent 5** · Basis `107d28a`
**Status:** Plan. In diesem PR ist **kein** Produktionscode geändert — Schreibbereich war
`poc/research/item-utility/**` und `docs/research/item-utility/**`.

Ziel: Die Item-Entscheidung später **ohne grundlegenden Umbau** in die bestehende Human-KI
(`botcore::HumanBotPolicy`, `BotDriver.cpp`) integrieren.

---

## 1. Warum das ohne Umbau passt

| Bestehende Schicht | Berührungspunkt | Änderungsbedarf |
|---|---|---|
| `botcore::HumanBotPolicy::Step` | entscheidet Ziel/Aim/Waffe/Bewegung, meldet „kein Ziel" | **eine** Abfrage: „hat die Item-Schicht ein Ziel?" |
| `BotCommand.forward/strafe/yaw_delta` | Bewegungsabsicht | Item-Ziel setzt `forward`/`yaw` **nicht** — das macht die Navigation |
| `botcore::WeaponSelector` | Waffenwahl | unverändert; Item-Schicht konsumiert dessen Score nur lesend |
| `botcore::Perception` | Sicht, Reaktionszeit, Ray-Budget | unverändert; liefert die Sichtbarkeit der Items **nicht** (Item-Sichtbarkeit kommt aus dem Item-Scan) |
| `BotDriver.cpp` | Snapshot füllen, `CPlayerAction` bauen | Snapshot erweitern, `ItemPlanner::Step` aufrufen, Ergebnis an Navigation/Kampf geben |
| `botcore::ObstacleRecovery` | reaktive Erholung | unverändert; bleibt **unter** der Item-Navigation |

Die Item-Schicht ist deshalb enginefrei, damit dieser Schritt ein **Mapping** ist, kein Rewrite:
`include/botcore_adapter.h` enthält genau dieses Mapping (Profil, Waffenmaske, Loadout-Input,
Director-Intent) und ist durch `tests/test_botcore_adapter.cpp` abgesichert.

---

## 2. Phasen

### Phase I – Offline-Integration (kein Engine-Code, keine Runtime)

| # | Datei | Änderung | Gate |
|---|---|---|---|
| I.1 | `poc/botcore/…` (fremder Scope) | `ItemProfileFrom(botcore::BotProfile)` in `bot_human.h` übernehmen, Item-Planner als Member | `make test` unverändert grün |
| I.2 | dito | `LoadoutInputFrom(SelfState)` statt eigener Maskenableitung | `test_botcore_adapter` bleibt grün |
| I.3 | dito | Waffen-Score auf `botcore::ScoreWeapon` umstellen (heute bitgleich, siehe Test) | `make bench`: kein Delta > Messrauschen |
| I.4 | dito | Bewegungsabsicht aus `GoalDecision` ableiten: bei aktivem Ziel `forward=0`, Heading zum Ziel nur über die Navigation | neue Tests: „Item-Ziel ändert keine Waffe, kein Feuer" |

**Gate I:** `cd poc/research/item-utility && make test` **und** `cd poc/botcore && make test` grün;
`make bench` ohne Regression.

### Phase II – Snapshot-Anbindung (Client, read-only)

| # | Ort | Änderung |
|---|---|---|
| II.1 | `BotDriver.cpp` (neuer Patch `0011-gamemp-item-utility.patch`) | Item-Scan: Welt-Entities mit `IsDerivedFromClass(pen, "Item")` **einmal pro Sekunde**, nicht pro Tick; Ergebnis in `ItemSnapshot[]` (max. 64) |
| II.2 | dito | Mapping `Item`-Klasse → `ItemKind` per **Klassenname** (`"Health"`, `"Armor"`, `"Ammo Pack"`, `"Weapon"`, `"PowerUp"`), nicht per DLL-Klassenzeiger — portabler gegenüber SDK-Ständen |
| II.3 | dito | Werte aus den Item-Properties lesen (`m_fValue` bei Health/Armor, Munitionstyp + Menge bei Ammo); **nur lesend** |
| II.4 | dito | Sichtbarkeit: ein `CCastRay` pro Item **nur** für die 8 nächsten Kandidaten, Budget aus `bot_iItemRays` |
| II.5 | dito | `ThreatState` aus `botcore::Perception` (sichtbare Feinde, Distanz, `NotifyDamage`-Zeitstempel) |
| II.6 | dito | Konsolenvariablen `bot_bItemAI` (Default **0**), `bot_iItemScanInterval`, `bot_iItemRays`, `bot_iItemLogEvery` |

**Wichtig:** Solange `bot_bItemAI = 0` ist, muss der Build **bitgleich** zum qualifizierten Pfad
bleiben (Default-aus-Prinzip der bisherigen Kandidaten).

### Phase III – Navigation koppeln

1. Sink implementieren (`BotcoreNavigationSink`, siehe `2026-10-25-navigations-schnittstelle.md`).
2. Wegpunkt/Wegfindung kommt vom Navigation-Agenten; bis dahin: **kein** Item-Trip, nur Logging
   (`[BotItem] select id=… need=… u=…`) — so ist die Entscheidung ohne Bewegung prüfbar.
3. Bewegungsanteil im BotDriver: bei aktivem Ziel Heading/Forward aus dem Navigationsergebnis,
   Kampfpriorität nur, wenn `suppress_combat == false`.

### Phase IV – Kampfkopplung

1. `suppress_combat` respektieren: Human-Policy darf Rückzug/Bewegung übernehmen, aber **nicht**
   feuern erzwingen.
2. `combat_priority` aus der bestehenden Ziel-/Distanzlage ableiten (0 = kein Feind, 1 = Kampf auf
   `preferred_range`), nicht aus neuen Sensoren.
3. `NotifyItemPicked` anbinden, sobald der Server das Item aus dem Snapshot entfernt.

---

## 3. Aufwand und Risiko

| Risiko | Bewertung | Gegenmaßnahme |
|---|---|---|
| Netzwerk/Sync | **niedrig**: nur clientseitige Entscheidung, keine neuen Action-Bits, keine neuen Pakete | Jeder Kandidat bleibt ein neuer Kandidat ohne automatische Abnahme (AGENTS.md); Gate G2 trotzdem Pflicht |
| CPU | **sehr niedrig**: 0,16–3,3 µs/Tick für 0–64 Items (gemessen, siehe README); Item-Scan 1 Hz statt 20 Hz | `bot_iItemScanInterval`, Ray-Budget |
| Fehlentscheidung (Bot läuft sinnlos) | **mittel**: sichtbares, aber falsches Verhalten | Default aus, Logging, Offline-Suite |
| Retail-Item-Namen/Properties | **offen**: Klassennamen sind aus dem SDK abgeleitet, nicht nativ geprüft | Klassenname-Mapping mit Fallback (unbekannt → `kNone`, ignoriert) |
| Wechselwirkung mit Waffenwahl | **niedrig**: Item-Schicht wählt keine Waffe | Adapter-Test + „Item-Ziel ändert keine Waffe"-Test |
| Doppelte Item-Suche (Cecil-Stil) | **niedrig**: nur eine Quelle für Item-Ziele | `ItemPlanner` ist die einzige Instanz pro Bot |

Geschätzter Umfang: Phase I ≈ 200 Zeilen in fremden Dateien, Phase II ≈ 250 Zeilen Patch,
Phase III/IV ≈ 150 Zeilen. Kein Umbau der bestehenden Schichten.

---

## 4. Abnahmegates (Projektstandard, aus PR #54 Abschnitt F übernommen)

| Gate | Inhalt | Bestanden, wenn |
|---|---|---|
| **O1** | `make test` in `poc/research/item-utility` | 3 Binaries grün (378 / 91 711 / 401 Checks) |
| **O2** | `make bench` | Budgets eingehalten (≤ 40 µs/Tick bei 64 Items) |
| **O3** | `make test` in `poc/botcore` | unverändert `HUMAN AI PASS` |
| **O4** | Patch-Hygiene | `git apply --check` für `0011-…` sauber, Default-aus bitgleich |
| **G1** | Ein-Bot-Smoke, `bot_bItemAI=1`, `bot_iItemLogEvery=20` | `[BotItem]`-Zeilen plausibel, kein Crash |
| **G2** | Sync-Gate: 1 Bot 10–30 min, `tools/analyze_sync_log.py` | **0 SYNCBAD**; sonst Feature zurück, keine Maskierung über `ser_iKickOnSyncBad` |
| **G3** | Boden-/Item-Karten-Gate (Items auf Kanten/Etagen) | kein SYNCBAD, kein Absturz |
| **G4** | Vier-Bot-A/B CPU (`bot_bItemAI` 0/1) | Delta im Messrauschen |
| **G5** | Acht-Bot-Stunde + Vanilla-Observer | keine Disconnects, keine Sync-Fehler |

**Nicht** in diesem PR: MSVC-Build, Retail-Join, Sync-Läufe, Hetzner. Alles **NOT_TESTED**.

---

## 5. Offene Punkte / Folgeaufträge

1. **Item-Reservierung zwischen Bots**: Zwei Bots können dasselbe Item ansteuern. Lösung wäre ein
   Reservierungsfenster im Planner (noch nicht implementiert, bewusst außerhalb des Scopes).
2. **Pfadkosten statt Luftlinie**: Sobald der Navigation-Agent echte Pfadlängen liefert, sollte
   `TravelSeconds` diese statt `Distanz/Speed` verwenden (Interface-Erweiterung `NavFeedback.path_remaining_m`
   existiert bereits, wird aber nicht gelesen).
3. **Retail-Item-Properties**: `m_fValue`/Munitionsmengen pro Item-Klasse müssen am Original
   verifiziert werden (SDK-Annahme, nicht native geprüft).
4. **Coop**: Cecil wertet Monster als Gegner; Alpha-Gaming hat keinen Coop-Modus. Die Item-Schicht
   ist modusneutral, `kStrategic` könnte Coop-Ressourcen abbilden.
5. **Telemetrie**: `BotTelemetry.csv` (P0-Kandidat) könnte `[BotItem]`-Zeilen aufnehmen; nicht Teil
   dieses Auftrags.
