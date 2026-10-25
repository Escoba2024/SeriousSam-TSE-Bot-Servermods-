# CecilBotMod – Item-Logik: Analyse und Übertragbarkeitsbewertung

**Datum:** 25.10.2026 · **Rolle:** Agent 5 (Item-Utility & Resource Management)
**Alpha-Gaming-Basis:** `main` @ `107d28a276c4fe4428cc3c8bf5bbd876e1a85351`
**CecilBotMod-Referenz:** `953b477e53fdc5a5d84c8ae8d759c84fdf6c973c` (öffentlicher Klon, nur gelesen)
**Bezug:** PR #54 (CecilBotMod↔Alpha-Gaming-Transferanalyse), Abschnitt C Zeile 25 „Item-Nutzung" und Abschnitt E.4 „Phase 4 – Coop und Items"

**Beweisklassen:** **VERIFIZIERT** = am konkreten Quellstand per Datei:Zeile geprüft ·
**BEWERTUNG** = begründete Einordnung · **NICHT GEPRÜFT** = ohne Retail/Windows nicht entscheidbar.

> Dieses Dokument ist eine **algorithmische** Referenzanalyse. Es wurde **kein** Cecil-Quelltext,
> keine Entity-Klasse, kein Setting-Name und keine Zahlenkonstante übernommen. Die Umsetzung in
> `poc/research/item-utility/` ist eine eigenständige, enginefreie Neuentwicklung (GPL-2.0-only,
> siehe `THIRD-PARTY-NOTICES.md`).

---

## 1. Wo die Item-Entscheidung im Cecil-Bot sitzt — VERIFIZIERT

```
CPlayerBot : CPlayer                             Sources/Bots/Classes/PlayerBot.es
  ApplyAction -> BotThinking                     Sources/Bots/BotStructure.cpp (BotThinking)
    ...
    BotItemSearch(sbl)                           BotStructure.cpp:482   (Kommentar: "more important than players")
    BotPathFinding(sbl)                          danach: Navigation zum Ziel
    BotMovement(pa, sbl)
```

Die Item-Suche ist damit **ein Aufruf pro Tick** und liegt **vor** dem Pathfinding. Sie setzt
`m_penFollow`/`BLF_ITEMEXISTS` (`Sources/Bots/Logic/BotLogic.h:23,54`) und wird von der Bewegung
ausgewertet. Ein eigenes Item-Subsystem, eine Bewertungsfunktion oder ein Vergleich zwischen
Item-Typen existiert nicht.

## 2. Der Entscheidungsablauf im Detail — VERIFIZIERT

### 2.1 Einstieg und Kooldown (`BotItems.cpp:37–90`)

| Schritt | Code | Wirkung |
|---|---|---|
| Nächstes Item **irgendeines Typs** suchen | `BotItemSearch`, `ClosestItemType(CItem_DLLClass, …)` (`:39`) | nur zur Prüfung „gibt es überhaupt etwas" |
| „zu nah" = kein Ziel | `fCloseItemDist = max(|size.x|,|size.z|)/2`, `bWantItem = fItemDist > fCloseItemDist` (`:47–56`) | verhindert Zielen auf ein Item, auf dem man steht |
| Wichtiger Navmesh-Punkt als Sonderfall | `props.m_bImportantPoint` → `bNeedItem = (fItemDist < 8.0)` (`:59–62`) | Item wird nur bei sehr großer Nähe genommen, sonst gilt der Important-Point |
| Zielauswahl | `GetClosestItem(fItemDist, sbl)` (`:63`) | siehe 2.2 |
| Kooldown setzen | `m_tmLastItemSearch = now + fItemSearchCD` (`:68`) | **5 s** in allen Presets (`BotSettings.cpp:48,87,126`) |
| Ziel binden | `m_penLastItem`, `BLF_ITEMEXISTS`, `m_penFollow` (`:76–80`) | Bewegung läuft zum Item |
| Ziel verwerfen | „not pickable anymore" → `m_penLastItem = NULL`, `m_tmLastItemSearch = 0` (`:82–86`) | sofortige Neusuche möglich |

Der Kooldown wird **beim Setzen** eines Ziels gestartet, nicht beim Abbruch. Ein Abbruch setzt ihn
sogar auf 0 zurück — der Bot kann also im schlimmsten Fall jedes zweite Tick ein neues Item wählen.

### 2.2 Die feste Prioritätskette (`GetClosestItem`, `BotItems.cpp:118–201`)

Reihenfolge, jeweils mit **typabhängiger Maximaldistanz**:

1. **Waffe** (`CWeaponItem_DLLClass`), `fWeaponDist` = 16 m, zusätzlich `fItemDist < m_fTargetDist`
   (nur wenn kein näherer Gegner) → `:126`
2. **Gesundheit**, nur wenn `health < fHealthSearch` (Preset: 50/80/100), dann **wertabhängige**
   Staffelung (`:133–151`):
   - Itemwert ≤ 10 und HP < 75 → nehmen
   - Itemwert ≤ 50 und HP < 85 → nehmen
   - Itemwert ≥ 100 und HP < 150 → nehmen
3. **Powerup** (`CPowerUpItem_DLLClass`), `fWeaponDist` → `:158`
4. **Rüstung**, nur wenn `armor < 100`, analoge Wertstaffel (10/75, 50/85, ≥100) → `:165–183`
5. **Munition**: erst `CAmmoPack`, dann `CAmmoItem`, `fAmmoDist` = 16 m → `:186–198`
6. sonst `NULL`

Zusätzlich (`ClosestItemType`, `BotItems.cpp:205–241`):
- **Ein Scan über alle Welt-Entities** pro Typ (`FOREACHINDYNAMICCONTAINER`) — bis zu 5 Scans/Tick.
- **Sichtprüfung** per `CastBotRay`, wenn `bItemVisibility` (Presets: TRUE) → ein Ray pro Kandidat.
- **Vertikale Differenz ×3** (`vPosDiff(2) *= 3.0f`) — Items in anderer Etage gelten als weiter.
- **Dasselbe Item wird nicht erneut gewählt** (`penReturn == props.m_penLastItem → NULL`) — ein
  einfacher Flatter-Schutz, der aber jede Wiederaufnahme des gleichen Ziels verhindert.

### 2.3 Parameterflächen (`BotSettings.h:62–69`, `BotSettings.cpp:47–55,86–94,125–131,165–173`)

| Parameter | Dummy | Easy | Normal | Hard |
|---|---:|---:|---:|---:|
| `bItemSearch` | TRUE | TRUE | TRUE | TRUE |
| `fItemSearchCD` | 5 s | 5 s | 5 s | 5 s |
| `fWeaponDist` | 16 | 16 | 16 | 16 |
| `fHealthSearch` | 100 | 50 | 80 | 100 |
| `fHealthDist` | **0** | 32 | 32 | 32 |
| `fArmorDist` | **0** | 16 | 16 | 16 |
| `fAmmoDist` | **0** | 16 | 16 | 16 |

`fHealthDist = 0` in „Dummy" bedeutet: Gesundheit ist praktisch nie erreichbar (jede Distanz ist
größer) — die Item-Suche ist dort effektiv deaktiviert, nicht „vorsichtiger". Die Item-Parameter
sind damit ein grober Schwierigkeits-Schalter, **keine** Verhaltensmodellierung.

### 2.4 Kopplung an die Navigation (`BotMovement.cpp` „wichtige Punkte", `BotFunctions.cpp:111–160`)

Items, Schalter und Marker werden beim Navmesh-Aufbau als „important points" markiert
(`ImportantForNavMesh`). Mit Wahrscheinlichkeit `fImportantChance` (0,1–0,4 pro 5 s) wählt der Bot
einen solchen Punkt als Zielpfad, statt aktiv nach einem Item zu suchen (`m_tmPickImportant`,
`FindImportantPoint`). Das ist Cecils **eigentliche** Item-Navigation: opportunistisches Ablaufen
von Item-Punkten, wenn gerade nichts anderes ansteht. Der normale `BotItemSearch`-Pfad läuft
zusätzlich und überstimmt ihn, sobald ein Item in Reichweite ist.

---

## 3. Bewertung: was die Cecil-Logik leistet und was nicht

### 3.1 Stärken (übernommene **Ideen**, nicht Code)

| # | Idee | Cecil-Beleg | Umsetzung in Agent 5 |
|---|---|---|---|
| 1 | **Bedarfsgating**: Item-Typen haben unterschiedliche Auslöseschwellen, Gesundheit/Rüstung nur unter HP-/Armor-Grenzen | `BotItems.cpp:133,165` | `HealthNeed`/`ArmorNeed` mit konvexem Defizit (`item_scoring.h`) |
| 2 | **Wertbewusstsein**: ein kleiner Trank wird nur bei sehr niedriger HP genommen, ein großer früher | `BotItems.cpp:139–150` | `Capability`: Item-Wert relativ zum offenen Defizit |
| 3 | **Typabhängige Reichweite**: Munition wird anders gesucht als eine Waffe | `GetItemDist`, `:94–115` | `TravelSeconds` + `max_search_time_s` (hartes Reisebudget statt Distanzkonstante) |
| 4 | **Kein Doppelziel**: dasselbe Item wird nicht endlos erneut angesteuert | `ClosestItemType`, `:236–239` | `blacklist_` (30 s) + Per-Item-Kooldown nach Abbruch |
| 5 | **Suche mit Kooldown** statt Neubewertung jedes Tick | `m_tmLastItemSearch` | globaler Such-Kooldown **nach Trouble-Abbruch**, nicht nach Erfolg |
| 6 | **Item-Suche vor Bewegung/Navigation** als eigene Stufe | `BotStructure.cpp:482` | `ItemPlanner::Step` liefert ein Ziel, Navigation folgt |
| 7 | **Items als „wichtige Punkte"** ohne Feindkontakt | `ImportantForNavMesh`, `fImportantChance` | `ItemKind::kStrategic` mit Bedarf ↑ wenn `engaged == false` |

### 3.2 Schwächen — und warum Agent 5 sie nicht übernimmt

| # | Schwäche | Beleg | Konsequenz im Prototyp |
|---|---|---|---|
| 1 | **Keine Vergleichbarkeit**: feste Kette statt Bewertung; eine Waffe gewinnt immer, auch wenn sie schlechter ist als die vorhandene | `:124–129` | Multiplikatives Utility über alle Typen, ein gemeinsamer Wertebereich |
| 2 | **Kein Kampfbezug**: sichtbarer Gegner, Beschuss und Kampfpriorität beeinflussen die Item-Wahl nicht (nur `m_fTargetDist` als Waffen-Gate) | `:126`, `BotStructure.cpp:482` | `ThreatFactor`, `PriorityFactor`, `CombatLock`, `ThreatAbort`, `DamageAbort` |
| 3 | **Kein Risiko**: der Weg zum Item wird nicht danach bewertet, ob er durch eine Feuerlinie führt | — | `Exposure`-Term, skaliert mit `risk_awareness` des Skill-Levels |
| 4 | **Kein Skill-/Persönlichkeitsunterschied**: alle Bots eines Presets entscheiden gleich | `BotSettings.cpp` (flache Presets) | `ItemSkillBlock` (Horizont, Risiko, Disziplin) × `ItemPersonalityBlock` (Appetit, Vorsicht) |
| 5 | **Keine Hysterese gegenüber Alternativen**: nur „nicht dasselbe Item" | `:236` | `commit_margin` + `min_commit_s` (Dwell) + Start-/Fortsetzungsschwelle |
| 6 | **Kein Zeitbudget**: ein unerreichbares Ziel bleibt bis „nicht mehr pickable" aktiv | `:82` | `max_search_time_s`, `NavStatus::kUnreachable/kStalled` |
| 7 | **Kein Abbruch durch Beschuss**: nur `IsItemPickable` beendet die Suche | `:78` | Abbruch bei Damage-Fenster, Nahgegner, Kampfpriorität, Stall |
| 8 | **Aufwand/Halluzination**: bis zu 5 Weltscans + 1 Ray pro Kandidat **pro Tick**; allwissende Server-Perspektive | `:205–241` | Ein Snapshot pro Tick (max. 64 Items), keine Rays in der Entscheidungsschicht |
| 9 | **Nicht übertragbar**: Server-Entity, `CItem`-DLL-Klassenzeiger, `m_ulPickedMask`, `en_plViewpoint` — alles serverseitig | `IsOfDllClass`, `Item.es:31` | Nur enginefreie Werte (`ItemKind`-Enum, Zahlenfelder) |

**Fazit:** Cecil liefert ein brauchbares **Bedarfsmodell** (Schwellen + Item-Wert + Kooldown +
Wichtige-Punkte), aber **keine Entscheidungslogik im engeren Sinn**: es gibt keine Alternativen-
bewertung, keinen Kampfbezug und keine Verhaltensdifferenzierung. Genau diese drei Lücken füllt
Agent 5.

## 4. Lizenz- und Abgrenzungsbehandlung — BEWERTUNG

- CecilBotMod steht unter **GPL-2.0** (`LICENSE` im Klon; Dateiköpfe „version 2 of the GNU General
  Public License"). Der Prototyp ist deshalb ebenfalls **GPL-2.0-only** lizenziert (SPDX-Header in
  jeder Datei) und in `THIRD-PARTY-NOTICES.md` als eigenständige Neuentwicklung eingeordnet.
- **Nicht übernommen:** Quelltext, Entity-Klassen (`CItem`, `CPlayerBot`), Setting-Namen
  (`fHealthSearch`, `fItemSearchCD`, …), Konstanten (`MAX_ITEM_DIST 256`, Distanzwerte 16/32),
  Preset-Zahlen, Netzwerk-/Serverintegration.
- **Übernommen:** ausschließlich die in 3.1 genannten **Ideen** in neu formulierter, eigener
  Mathematik (konkave/kovexe Bedarfsfunktionen, multiplikatives Utility, Hysterese, Kooldowns).
  Keine dieser Ideen ist Cecil-spezifisch; sie sind allgemeines Utility-AI-Handwerk.
- Der Prototyp liest **keine** Retail- oder Cecil-Binärdateien und enthält keine Spieldaten.

## 5. Offene Punkte — NICHT GEPRÜFT

- Ob Retail 1.07 `m_ulPickedMask`-Semantik (Item pro Spieler einmal bzw. Respawn) exakt so
  repliziert, wie es der `consumable_blacklist_s`-Ansatz annimmt, ist **nicht** nativ geprüft.
  Der Prototyp behandelt es als Kalibrierungsannahme (`tuning.consumable_blacklist_s`).
- Die reale Item-Dichte pro Karte (relevant für `kMaxItems = 64` und das CPU-Budget) ist nicht
  gemessen; die Benchmarks decken 0–64 Items ab.
- Cecil-Verhalten in Coop (Monster als Ziele) ist für Agent 5 irrelevant, weil Coop in
  Alpha-Gaming nicht implementiert ist.
