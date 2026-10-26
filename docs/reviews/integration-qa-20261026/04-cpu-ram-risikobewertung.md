# Deliverable 4: CPU-, Stack- und RAM-Risikobewertung (`integration-qa-20261026`)

> **Evidenzhinweis:** Alle Strukturgrößen (`sizeof`) und der C++-Offline-CPU-Benchmark wurden direkt gegen die echten Header von PR #54, #55, #57 und #69 gemessen (`[OFFLINE-PROVED]`). Alle Laufzeitkosten in `SeriousSam.exe` / `DedicatedServer.exe` unter Wine/32-Bit-MSVC sowie unter voller Serverlast mit 4/8/16 Bots sind **`NOT_TESTED_RETAIL`**. Host-RAM-Zahlen aus PR #62 tragen explizit ihre Herkunftskennzeichnung (`[T]` gemessener Einzelwert, `[D]` abgeleitetes Summenmodell, `[P]` lineare Projektion).

---

## 1. Exakt gemessene C++-Speichergrößen (`sizeof`, `[OFFLINE-PROVED]`)

Kompiliert gegen die unveränderten Header aus PR #57 (`poc/botcore`), PR #54 (`poc/navigation-lab`), PR #55 (`poc/research/item-utility`) und PR #69 (`poc/research/nav-item-bridge`):

| Klasse / Struktur | Herkunft | Gemessene Größe (Bytes) | Größe (KiB) | Bewertung für `GameMP.dll` (32-Bit PE) |
| :--- | :--- | ---: | ---: | :--- |
| `botcore::HumanBotPolicy` (PR #45) | `main` | ~`5.200` B | `~5,08 KiB` | Unkritisch im statischen Slot-Array |
| `botcore::HumanBotPolicy` (PR #57) | PR #57 | `7.568` B | `7,39 KiB` | `+45 %` durch `RouteMemory` + `history_[21]`, weiterhin BSS-sicher |
| `itemai::ItemPlanner` | PR #55 | `~6.400` B | `~6,25 KiB` | Unkritisch im BSS |
| `navlab::NavGraph` (`1024` Nodes, `4096` Edges) | PR #54 | `173.060` B | **`169,00 KiB`** | **Darf nur 1× global im BSS/Heap existieren — niemals pro Bot und niemals auf dem Stack!** |
| `navbridge::ConstrainedNavSearch` | PR #69 | `~34.800` B | `~33,98 KiB` | Könnte als 1× Thread-Local/Global Scratch geteilt werden statt 16× pro Agent! |
| `navbridge::NavItemBridgeAgent` | PR #69 | `95.080` B | **`92,85 KiB`** | `16` Bots = `1.521.280` B (`1.485,63 KiB`) |
| `1 × NavGraph + 16 × NavItemBridgeAgent` | PR #54 + #69 | `1.694.340` B | **`1.654,63 KiB` (`1,62 MiB`)** | Als statisches BSS in `GameMP.dll` vertretbar, aber unnötig aufgebläht (geteiltes `ConstrainedNavSearch` spart `~530 KiB`) |
| `navbridge::ArenaSim` | PR #69 | `949.600` B | **`927,34 KiB`** | **AKUTES STACK-OVERFLOW-RISIKO (`QA-12`):** Überschreitet zusammen mit Aufrufframes das `1.024 KiB` (`1 MiB`) Standard-Stacklimit einer 32-Bit-Windows-PE (`SeriousSam.exe`) sofort (`STATUS_STACK_OVERFLOW`), falls jemals lokal auf dem Stack konstruiert! |

### Konkrete Speicherschutz-Anforderungen vor Integration in `GameMP.dll`
1. **Kein Stack-Alloc großer Strukturen:** `NavGraph`, `NavItemBridgeAgent` und Test-Simulatoren niemals als lokale Stack-Variablen anlegen; `ConstrainedNavSearch` als einzelnes statisches Scratch-Objekt im Single-Thread-Server-Tick teilen (reduziert pro-Bot-Footprint von `92,85 KiB` auf `< 55 KiB`).
2. **Kein dynamischer Heap im Tick-Pfad (`OnPreThink` / `BotDriver`):** PR #54, #55 und #69 halten `0` `new`/`malloc`-Aufrufe im Tick-Pfad ein (`[IMPL-VERIFIED]`); diese Invariante muss beim Einbau in `BotDriver.cpp` erhalten bleiben.

---

## 2. CPU-Lastanalyse & gemessener Tick-Benchmark

### 2.1 Gemessene reine KI-CPU-Kosten ohne Engine-Raycasts (`[OFFLINE-PROVED]`)

Wir haben `8` `NavItemBridgeAgent`-Instanzen über `200` Welt-Ticks auf einem `1024`-Knoten-Gitter (`32 × 32`) mit `32` aktiven Items gebenchmarkt (`-O2`):

| Metrik | Gemessener Wert | Anteil an `50.000 µs` (`20 Hz` Welt-Tick) |
| :--- | ---: | ---: |
| **Gesamtzeit pro Welt-Tick (8 Bots, reine C++-Logik)** | **`1.019,51 µs` (`1,02 ms`)** | `2,04 %` (64-Bit-Host, ohne Wine/32-Bit-Overhead) |
| **Zeit pro einzelnem Bot-Tick** | **`127,44 µs`** | `0,25 %` |
| **Projiziert auf 16 Bots (linear)** | **`~2.039 µs` (`2,04 ms`)** | `4,08 %` (ohne Raycasts!) |

### 2.2 Verdeckter algorithmischer Hotspot: Uncached `NearestNode`-Linearscans (`QA-12`)

- In `nav_cost_cache.h:808–951` ruft `WorldPathEnricher::Enrich` pro Bot und pro Tick für sich selbst plus alle `M` Kandidaten-Items `graph.NearestNode(x, z)` auf.
- `NavGraph::NearestNode` iteriert linear über alle `1.024` Knoten:
  $$8 \text{ Bots} \times (1 + 32) \text{ Ankerungen} \times 1.024 \text{ Knoten} = 270.336 \text{ Knotendistanz-Prüfungen pro Tick}$$
  (`5,41 Millionen` Knotenscans pro Sekunde bei 8 Bots bzw. **`10,81 Millionen/s` bei 16 Bots**!).
- **Vermeidbarkeit:** Da Item-Spawnpunkte in Serious Sam TSE **ortsfest** sind, reduziert ein einmaliges Vorberechnen des `anchor_node` pro Item-Entity beim Map-Start diese Kosten um **> 95 %** auf `1` Anker-Lookup pro Bot-Tick!

### 2.3 Kritischer CPU-Multiplikator in Retail 1.07: Unbudgetierte `CCastRay`-Aufrufe (`NOT_TESTED_RETAIL`)

- **Das eigentliche CPU-Risiko liegt nicht in A*, sondern in `CCastRay`:**
  - PR #45 begrenzte Gegner-Sichtlinienprüfungen (`PlanLosQueries`) bewusst hart auf **maximal `2` `CCastRay`-Aufrufe pro Bot-Tick** (`16 Rays/Welt-Tick` bei 8 Bots), weil BSP-/Polygon-Raycasting in Serious Engine 1.07 teuer ist.
  - **PR #55 und PR #69 setzen `ItemSnapshot::visible` voraus, definieren aber keinerlei Raycast-Budget (`PlanItemLosQueries` fehlt komplett!).**
  - Würde ein naiver `BotDriver`-Adapter pro Bot und Tick für `32` Items jeweils `CCastRay` ausführen, entstünden:
    - bei **8 Bots:** `256 CCastRay/Tick` = **`5.120 CCastRay/s`** (`16×` über dem qualifizierten PR-#45-Ray-Budget!),
    - bei **16 Bots:** `512 CCastRay/Tick` = **`10.240 CCastRay/s`** (`32×` über PR #45!),
    - zuzüglich `3` `ObstacleRecovery`-Feelerrays pro Bot (`48 Rays/Tick` bei 16 Bots).
  - Unter 32-Bit-Wine auf einer geteilten Hetzner-vCPU droht dadurch unmittelbar das Reißen des `50 ms`-Server-Tick-Budgets (`SYNCLATE` / `SYNCBAD`, siehe Deliverable 5). **Reale Kosten in Retail 1.07: `NOT_TESTED_RETAIL`.**

---

## 3. Host-RAM-Risikobewertung für den Produktionsserver (Hetzner CX22)

Basisdaten des Zielsystems laut Repository-Telemetrie (PR #62 / PR #67):
- **Physischer RAM:** `3.819 MiB`
- **Swap:** **`0 MiB`** (kein Swap konfiguriert -> harte OOM-Killer-Grenze!)
- **Basisbelegung OS + Dienste + 1 Dedicated Server + Reserveziel (`1.068 MiB` frei):** Effektives nutzbares Bot-/Prozessbudget **`~2.100–2.400 MiB`** vor Unterschreitung der Sicherheitsreserve.

| Architektur-Variante | 8 Bots Gesamt-RAM | 16 Bots Gesamt-RAM | Evidenzklasse | Risikourteil auf `3.819 MiB` / `0 Swap` |
| :--- | ---: | ---: | :--- | :--- |
| **Architektur A** (Server-seitige Bots in `DedicatedServer.exe`) | `~418,6 MiB` | `< 500 MiB` (`+1,6 MiB` BSS durch Nav/Item) | `[T]` (8p gemessen) / `[D]` (16p) | **NIEDRIGES RAM-RISIKO** (weit innerhalb Reserve; erfordert jedoch strikte Sync-Disziplin auf Server) |
| **Hybrid C1** (Dedizierter Server + geteilter Bot-Host-Prozess, PR #68) | `~602,8 MiB` | `~750–900 MiB` | `[D]` (Modell PR #62, **`NOT_TESTED_RETAIL`**) | **MODERATES RAM-RISIKO**, aber Prozess-/Slot-Isolationsmodell nativ unbewiesen |
| **Architektur B** (1 isolierter Wine-`SeriousSam.exe`-Client pro Bot, PR #57) | **`~1.725,9 MiB`** (`7+1` gemessen) | **`~3.566,7 MiB`** | `[T]` (`7+1`) / `[P]` (`16p`, **`NOT_TESTED_RETAIL`**) | **HOHES / KRITISCHES OOM-RISIKO:** Bereits `8` Clients schöpfen das Reserveziel (`1.068 MiB` frei) fast vollständig aus; **`16` isolierte Wine-Clients führen ohne Swap nahezu sicher zu Linux-OOM-Kills!** |

### Fazit für CPU & RAM
1. **Für 16 gleichzeitige Bots auf Hetzner CX22 (`3.819 MiB`, `0 Swap`) ist Architektur B physikalisch nicht tragfähig (`~3,57 GiB` `[P]`).** Soll Architektur B genutzt werden, muss `max_bots` auf diesem Host hart auf `<= 6..7` begrenzt oder der Host-RAM auf `>= 8 GiB` skaliert werden.
2. Vor jedem Einbau von PR #54/#55/#69 in `GameMP.dll` sind **(a) statisches Item-Anchor-Caching**, **(b) Verzicht auf unbudgetierte Item-LOS-`CCastRay`-Aufrufe** und **(c) Verbot großer Stack-Objekte (`ArenaSim`, `NavGraph`)** zwingend umzusetzen.
