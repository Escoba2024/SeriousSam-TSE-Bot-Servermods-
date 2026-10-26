# Deliverable 5: Multiplayer-Sync-Risikobewertung (`integration-qa-20261026`)

> **Verbindliche Retail-1.07-Randbedingungen (`AGENTS.md`):**
> - In Serious Sam Classic: The Second Encounter **Retail 1.07** existiert eine harte Draht-/ABI- und Paket-CRC-Prüfung gegen unveränderte Vanilla-1.07-Clients.
> - Der Sync-Check läuft über `Engine.dll` (`FUN_601A2D10`, Schwelle `0x602A7EB4`).
> - `CPlayerAction` (`36 Bytes`: `pa_vTranslation`, `pa_aRotation`, `pa_aViewRotation`, `pa_ulButtons`) ist der einzige zulässige Eingabekanal für menschlich kompatible Bot-Steuerung.
> - **Gesamtstatus der Mehrspieler-Synchronität aller offenen Kandidaten (`#54, #55, #57, #58, #63, #65, #66, #67, #68, #69`) unter realer Mehrspielerlast (`4/8/16` Slots + Vanilla-1.07-Human-Client): `NOT_TESTED_RETAIL`.**

---

## 1. Übersicht der Sync-Risikofaktoren nach Subsystem

| Nr. | Risikovektor | Betroffene PRs | Wirkmechanismus in Retail 1.07 | Risiko | Nachweisstand |
| :--- | :--- | :--- | :--- | :---: | :--- |
| **S-01** | **Wire-ABI / `CPlayerAction`-Layout & Entity-Tabellen** | `#45`, `#57`, `#69` | Jede Änderung an serialisierten Entity-Properties (`.es`-Klassentabellen), `Write_t`/`Read_t` oder `CPlayerAction` (`36 B`) bricht sofort die Vanilla-1.07-CRC | **Niedrig** *(solange rein in `BotDriver.cpp`)* | `[IMPL-VERIFIED]` in `#45`/`#57`; kombinierter Build = `NOT_TESTED_RETAIL` |
| **S-02** | **Server-Tick-Überziehung (`> 50 ms`) -> `SYNCLATE` / `SYNCBAD`** | `#54`, `#55`, `#69` | Überschreitet der `20 Hz`-Server-Tick durch unbudgetierte Item-LOS-`CCastRay`-Aufrufe (`bis 5.120–10.240 Rays/s`) + lineare `NearestNode`-Scans die `50 ms`-Grenze, driften Stream-Sequenzen (`FUN_601A2D10`) -> Client-Disconnect / Rubberbanding | **HOCH** | `[IMPL-VERIFIED]` (fehlender Ray-Cap), `[OFFLINE-PROVED]` (`1,02 ms` ohne Rays), **`NOT_TESTED_RETAIL`** |
| **S-03** | **20-Hz-Konsole `cmd_cmdOnTick` im Dedicated Server** | `#63` | `tools/redstation_preset.py:21–29` hängt einen mehrteiligen Bedingungsstring an `cmd_cmdOnTick`, der von `CShell::Execute` **auf jedem einzelnen Welt-Tick (`20×/s`)** geparst und ausgewertet wird | **MITTEL–HOCH** | `[IMPL-VERIFIED]`, **`NOT_TESTED_RETAIL`** |
| **S-04** | **Unterminierter `SYNCBAD`-Logscan & fehlende cgroup-Bindung im Supervisor** | `#50` (dokumentiert in `#67` C1) | `DedicatedServer_107.py` liest `SYNCBAD` ohne saubere Terminierung/Rotation und startet `SeriousSam.exe` außerhalb der überwachten cgroup; fehlerhafte Sync-Zustände werden entweder übersehen oder hinterlassen verwaiste Prozesse | **HOCH** | `[IMPL-VERIFIED]` (Patch in PR #67 liegt nur als `.patch` vor, nicht angewendet!), **`NOT_TESTED_RETAIL`** |
| **S-05** | **Sieben blinde Flecken im Sync-Gate-Harness** | `#58` (dokumentiert in `#67` C2) | PR #58 akzeptiert synthetische/unvollständige Logs ohne strikte Prüfung von `GameMP.dll`-SHA256, echter Vanilla-Client-Präsenz, monotoner Tick-Dauer und Null-Toleranz für `SYNCBAD`/`CRC` | **HOCH** *(Falsch-Grün-Gefahr!)* | `[IMPL-VERIFIED]`, `[OFFLINE-PROVED]` (PR #67 `c2_sync_gates.py`), **`NOT_TESTED_RETAIL`** |
| **S-06** | **Nicht-deterministische Gleitkomma- oder Padding-Abhängigkeiten auf Serverseite** | `#54`, `#55`, `#66`, `#69` | Solange KI-Zustand **nur** auf dem Server (Arch A) bzw. **nur** im jeweiligen Bot-Client vor Erstellung von `CPlayerAction` (Arch B) lebt und **nicht** Teil des synchronisierten Weltzustands (`ChecksumForSync`) ist, erzeugt internes `double`-Rounding keinen CRC-Mismatch; fließt KI-Zustand jedoch jemals in `ChecksumForSync` oder gemeinsame globale RNGs (`IRnd()`!) ein, bricht die Client-Sync sofort! | **KRITISCH bei `IRnd()`-Nutzung** | `[IMPL-VERIFIED]`: `botcore`, `#54`, `#55`, `#66`, `#69` nutzen eigene lokale PRNGs (`XorShift`/`LCG`), kein Engine-`IRnd()` |
| **S-07** | **Server-seitige Pseudo-Client-/Action-Injektionshypothesen (`H1`, `F11`, `F12`)** | `#65`, `#68` | PR #65 diskutiert mögliche Mechanismen (`H1` Tick-Jitter-Korrelation, `F11`/`F12` Server-Slot-Action-Pfade); diese Pfade sind in Retail 1.07 **reine unbewiesene Hypothesen** | **HOCH (falls ohne Beweis umgesetzt)** | **Unbewiesene Annahme — `NOT_TESTED_RETAIL`** |

---

## 2. Detailanalyse der kritischen Sync-Punkte

### 2.1 Reinhaltung von `ChecksumForSync` und `IRnd()` (`[IMPL-VERIFIED]`)
Positiv hervorzuheben ist:
- Keiner der geprüften C++-Header (`poc/botcore/*.h`, PR #54 `nav_*.h`, PR #55 `item_*.h`, PR #66 `combat2_*.h`, PR #69 `nav_item_bridge.h`) ruft den globalen synchronisierten Engine-Zufallsgenerator `CEntity::IRnd()` auf oder verändert serialisierte `CPlayer`/`CPlayerWeapons`-Felder direkt.
- Alle Entscheidungen münden am Ende in `CPlayerAction`-Werte (`pa_vTranslation`, `pa_aRotation`, `pa_aViewRotation`, `pa_ulButtons`).
- **Zwingende Invariante für den Integrations-PR:** Beim Einbau von Navigation 2.0 und Item-Utility in `BotDriver.cpp` darf das Auslesen von Item-Entitäten (`wo_cenEntities`) **ausschließlich Read-Only** erfolgen (keine Mutation von Entity-Flags, keine Trigger-Aufrufe, kein `IRnd()`!).

### 2.2 Tick-Budget-Gefährdung durch Raycasts und `cmd_cmdOnTick` (`QA-12`, `S-02`, `S-03`)
Selbst bei 100 % korrekter Paket-CRC treten in Retail 1.07 `SYNCLATE`- und `SYNCBAD`-Ereignisse auf, sobald der Dedicated Server sein `50 ms`-Tick-Intervall (`0,05 s`) unter Last reißt:
1. **Unbudgetierte Item-LOS-Raycasts (`#55` / `#69`):** Ein `BotDriver`-Einbau darf `ItemSnapshot::visible` **niemals** durch ungecappte `CCastRay`-Schleifen über alle Map-Items befüllen. Stattdessen ist die Sichtbarkeit/Verfügbarkeit von Pickups entweder über ein hartes Budget (`max. 1–2 CCastRay` pro Bot-Tick im Round-Robin) oder über den bereits bekannten Wegpunkt-Sichtgraphen zu bestimmen.
2. **PR #63 `cmd_cmdOnTick` (`tools/redstation_preset.py:21–29`):**
   ```ini
   cmd_cmdOnTick=cmd_cmdOnTick+"if((FLOAT)cmd_tmTick<(FLOAT)1){tmp_ai[9]=(INDEX)-1;}if((INDEX)cmd_tmTick>=(INDEX)300 && ((INDEX)cmd_tmTick/(INDEX)300)!=tmp_ai[9]){tmp_ai[9]=(INDEX)cmd_tmTick/(INDEX)300;Say(\"[ssam.ai] ...\");}\n";
   ```
   Dieser String wird in Serious Engine **jeden einzelnen Tick (`20×` pro Sekunde, `72.000×` pro Stunde)** vom Konsolen-Interpreter lexikalisch geparst und ausgewertet — nur um alle `300 Sekunden` (`1×` pro `6.000` Ticks!) eine Chat-Zeile auszugeben. Ob dies unter 8–16 Spielern zu messbarem Tick-Jitter führt, ist **`NOT_TESTED_RETAIL`**. Empfehlung: Komplett aus `cmd_cmdOnTick` entfernen und stattdessen im externen Python-Controller per `300 s`-Timer auslösen.

### 2.3 Offene Mängel in den Überwachungs- und Qualifikationswerkzeugen (`#50`, `#58`, `#67`)
- **Solange C1 (PR #50) ungepatcht ist**, kann ein echter `SYNCBAD`-Vorfall auf dem Server übersehen werden, weil der Log-Scanner laut PR #67 C1 nicht sauber terminiert bzw. rotiert.
- **Solange C2 (`c2_sync_gates.py` aus PR #67) nicht verbindlich vor jedem Freigabelauf erzwungen wird**, könnte ein fehlerhafter Lauf fälschlich als „Sync-stabil“ gewertet werden.
- **Auch PR #57s einziger nativer Kurztest (`1 Bot, 131,87 s`) liefert keinerlei Mehrspieler-Sync-Beweis**, da:
  1. nur `1` Bot ohne konkurrierende Bot-/Human-Interaktion lief,
  2. die Laufzeit (`131,87 s`) unterhalb eines aussagekräftigen Langzeitfensters (`>= 30–60 min`) lag, und
  3. kein gleichzeitiger Vanilla-1.07-Mensch-Client verbunden war (`4/8/16` Bots + Human = **`NOT_TESTED_RETAIL`**).
