# Nativer Integrationsplan für Codex C4 (`GameMP.dll` / `BotDriver.cpp`)

- **Datum:** 2026-10-25
- **Ziel-Konsument:** Codex C4 (nativer Serious-Sam-TSE-1.07-Integrationszweig)
- **Referenz-Treiber:** `poc/candidates/integrated-human-cpu-20261021/BotDriver.cpp`
- **Status:** Architektur- & Integrationsspezifikation auf Basis des verifizierten Offline-Prototyps `poc/research/nav-item-bridge/**`. **In diesem Forschungszweig wurden keine Produktions-DLLs (`GameMP.dll`) oder `.es`-Dateien verändert.**

---

## 1. Harte Leitplanken für den C4-Transfer (`SYNCBAD`-Schutz)

Aus `AGENTS.md` und der bisherigen Live-Qualifikation (`61DC…` / `7fc9…`) gelten für die native Übernahme vier unverhandelbare Regeln:

1. **Ausschließlich clientseitige `CPlayerAction`-Erzeugung im Bot-Prozess:**
   `NavItemBridgeAgent` liefert `BotDriverIntent { yaw_delta_deg, pitch_delta_deg, forward, strafe, fire, weapon, jump_hint }`. Der Server und sämtliche `.es`-Entity-Klassen (`Player.es`, `PlayerWeapons.es`, `HealthItem.es`, `ArmorItem.es`, `WeaponItem.es`, `AmmoItem.es`) bleiben **100 % unverändert**.
2. **Keinerlei Ground-Lookahead-Rays (`SYNCBAD`-Lehre):**
   Weder `NavGraphSink` noch `WorldPathEnricher` verlangen Boden-Abtaststrahlen vor dem Bot. Es werden ausschließlich die **bestehenden, bereits MP-qualifizierten** Sichtlinien-Checks (`BotCombatVisible`) sowie die drei horizontalen Hindernis-Fühler (`BotObstacleDistance(player, yaw / yaw+60 / yaw-60)`) weiterverwendet.
3. **Standardmäßig deaktiviert hinter CVars (`Default OFF`):**
   Ohne explizites Einschalten (`bot_bNavItemBridge = 0`) muss `BotDriver.cpp` exakt das bisher qualifizierte Verhalten ausführen.
4. **Kein dynamischer Heap im 20-Hz-Tick:**
   `NavItemBridgeAgent` (`89.896 B` pro lokalem Bot-Slot) und `navlab::NavGraph` (`173.060 B` einmalig pro geladener Welt) werden statisch im `BotState` bzw. Modul-Kontext gehalten.

---

## 2. Exakte Einbettung in `BotDriver.cpp`

### 2.1 Erweiterung des statischen Slot- & Weltzustands
```cpp
// Einmalig pro Prozess (geteilt, im Tick strikt const!):
static navlab::NavGraph g_worldNavGraph;
static uint32_t         g_worldNavEpoch = 1;
static CTFileName       g_loadedWorldFile;

// Pro lokalem Bot-Slot (MAX_LOCAL_PLAYERS = 4 -> ~351 KiB gesamt):
struct BotSlotState {
  // ... bestehende Felder ...
  navbridge::NavItemBridgeAgent bs_bridge;
  BOOL bs_bridgeConfigured;
};
```

Beim Weltwechsel (`pwo->wo_fnmFileName != g_loadedWorldFile`) wird `g_worldNavGraph` einmalig außerhalb des heißen Ticks geladen/aufgebaut (aus `.nav`-Datei oder aus den im `CWorld::wo_cenEntities` vorhandenen Item-/Spawn-Ankern) und `++g_worldNavEpoch` erhöht. Findet sich kein Graph (`node_count() == 0`), fällt `NavItemBridgeAgent` automatisch und sicher auf `ArbitrationReason::kMaplessScan` zurück.

### 2.2 Extraktion der `itemai::ItemSnapshot`-Liste ohne `.es`-Patch
Im Client-Weltzustand (`pwo->wo_cenEntities`) sind alle Pickup-Entities bereits repliziert vorhanden. Ein gedrosselter Scan (z. B. alle `bot_iItemScanInterval = 4` Ticks = `200 ms`, gecacht in einem flachen Puffer `ItemSnapshot[64]`) liest rein lesend:
- **Position:** `pen->GetPlacement().pl_PositionVector` → `ItemSnapshot::pos`
- **Verfügbarkeit / Respawn:** Ist `pen->GetRenderType() == CEntity::RT_EDITORMODEL` bzw. `en_ulFlags & ENF_HIDDEN` aktiv (aufgenommenes Item wartet auf Respawn), wird `respawn_s` konservativ auf die bekannte TSE-DM-Respawnzeit gesetzt (bzw. lokal ab dem beobachteten Verschwinden heruntergezählt); ist das Modell sichtbar, gilt `respawn_s = 0.0`.
- **Klassifikation (`ItemKind`, `weapon_index`, `value`, `amount`):** Über `IsDerivedFromClass(pen, "Health Item")` / `"Armor Item"` / `"Weapon Item"` / `"Ammo Item"` (reiner String-/DLL-Klassen-Check auf `en_pecClass->ec_pdecDLLClass->dec_strName`, keinerlei Header-Abhängigkeit zu `.es`-Interna nötig).
- **Wichtig für Mehrbot-Betrieb:** Kein Bot greift auf Server-Timer zu; verschwindet ein Item durch einen anderen Spieler/Bot, sieht `BotDriver` beim nächsten Snapshot regulär `ENF_HIDDEN` und routet wie in Szenario `S09` sofort um.

### 2.3 Ablauf eines 20-Hz-Ticks in `BotDriver_RunTick` (wenn `bot_bNavItemBridge != 0`)

1. **`BridgeTickInput` befüllen:**
   - `in.world` aus `player` (`tick`, `BotCombatEye(player)`, `GetHealth()`, `alive`, `current_weapon`, `deathmatch`).
   - `in.armor = player->m_fArmor`, `in.owned_weapons = weapons->m_iAvailableWeapons`, `in.ammo[2..14]` aus `weapons->m_iBullets`, `m_iShells`, `m_iRockets`, `m_iGrenades`, `m_iNapalm`, `m_iElectricity`, `m_iCannonBalls`, `m_iSniperBullets`.
2. **Zweistufiges LOS-Budget (identisch zum bestehenden `BotDriver.cpp`):**
   - `bs.bs_bridge.PlanLosQueries(in.world, sensed, ctSensed, needsRay);`
   - Nur für `needsRay[k] == true` wird `BotCombatVisible(player, other)` aufgerufen.
3. **Drei horizontale Hindernis-Fühler:**
   - `in.obstacle_front_m = BotObstacleDistance(player, yaw);`
   - `in.obstacle_left_m  = BotObstacleDistance(player, yaw + 60.0f);`
   - `in.obstacle_right_m = BotObstacleDistance(player, yaw - 60.0f);`
4. **Brücken-Schritt & Übersetzung in `CPlayerAction`:**
   ```cpp
   const navbridge::BridgeTickOutput out =
       bs.bs_bridge.Step(g_worldNavGraph, g_worldNavEpoch, in);

   bs.bs_aHeading = player->m_aLastRotation(1) + (FLOAT)out.intent.yaw_delta_deg;
   bs.bs_aPitch   = Clamp(player->m_aLastRotation(2) + (FLOAT)out.intent.pitch_delta_deg,
                          -85.0f, 85.0f);
   pa.pa_vTranslation(3) = -(FLOAT)out.intent.forward * speed_mps;
   pa.pa_vTranslation(1) =  (FLOAT)out.intent.strafe  * speed_mps;

   const INDEX selectBits = bs.bs_weaponInput.Poll(
       bs.bs_iTick, out.intent.weapon,
       weapons->m_iWantedWeapon, player->m_ulLastButtons);
   const BOOL weaponReady = (weapons->m_iCurrentWeapon == out.intent.weapon &&
                             weapons->m_iWantedWeapon  == out.intent.weapon);
   if (out.intent.fire && weaponReady) pa.pa_ulButtons |= PLACT_FIRE;
   if (out.intent.jump_hint)           pa.pa_ulButtons |= PLACT_JUMP;
   ```

### 2.4 Kritischer Befund für C4: `ObstacleRecovery`-Handoff auf Waypoint-Karten
Wie in `test_scenarios_matrix` (`S08`) nachgewiesen, erzwingt `botcore::ObstacleRecovery` nach einer Wanddrehung standardmäßig `40` Ticks (`~24 m`) Blind-Geradeauslauf. Sobald C4 Waypoint-Navigation aktiviert, **muss** der in `NavItemBridgeAgent::Step` bereits enthaltene 6-Tick-Freigabe-Handoff (`recovery_advance_ticks_ >= 6` bei `obstacle_front_m >= 1.8 m` sowie `Reset()` bei `goal_move.replanned`) beibehalten werden, damit Bots nach dem Lösen von einer Mauerkante sofort wieder auf den A*-Pfad einschwenken.

---

## 3. Vorgeschlagene CVars & Telemetrie

| CVar | Default | Bedeutung |
|---|---:|---|
| `bot_bNavItemBridge` | `0` | Master-Schalter (`0` = bisheriger Pfad, `1` = `NavItemBridgeAgent` aktiv) |
| `bot_iNavMaxExpandPerTick` | `192` | Hartes A*-Expansionsbudget pro Bot und 20-Hz-Tick |
| `bot_iNavCostProbesPerTick` | `4` | Max. ungecachte Graph-Distanz-Probes pro Bot und Tick |
| `bot_iItemScanInterval` | `4` | Intervall (in Ticks) für den Client-Item-Entity-Snapshot (`4` = `5 Hz`) |
| `bot_iBridgeLogEvery` | `0` | Wenn `> 0`, schreibt `out.trace.summary` alle `N` Ticks ins `BotLog` |

Beispiel einer kompakten `BotLog`-Zeile direkt aus `ArbitrationTrace::summary`:
```text
[BotBridge] slot=0 tick=240 owner=item-navigation(item-goal-active-no-visible-enemy) tgt=-1(vis=0) goal=302(keep:kept) nav=in-progress exp=0/192
```

---

## 4. Compiler-Kompatibilität (MSVC / MinGW für `GameMP.dll`)

- `poc/research/nav-item-bridge/include/*.h` nutzt ausschließlich `<cmath>`, `<cstdint>`, `<cstdio>` und feste POD-Arrays.
- Beachte beim Zusammenführen mit älteren MSVC-Toolchains: PR #55 (`poc/research/item-utility`) benötigt mindestens **C++14** (Aggregat-Initialisierung auf Structs mit Default-Member-Initializern in `item_weapons.h` und `item_profile.h`). Unter MinGW-w64 / modernem MSVC (`-std=c++17` bzw. `/std:c++17`) kompiliert die gesamte Kette warnungsfrei (`make compat` grün für C++14, C++17, C++20).

---

## 5. Abgestufte Übernahme & offene Retail-Gates

1. **Stufe C4-1 (Reihenfolge der Merges):**
   Zuerst PR #54 (`poc/navigation-lab`) und PR #55 (`poc/research/item-utility`) nach `main` übernehmen, danach diesen Adapter (`poc/research/nav-item-bridge`). `upstream_seams.h` schaltet dann automatisch von den Fallback-Spiegeln auf die direkten Pfade um (verifizierbar mit `-DNAV_ITEM_BRIDGE_REQUIRE_UPSTREAM`).
2. **Stufe C4-2 (Lokaler Build hinter `bot_bNavItemBridge = 0`):**
   Einbau in einen dedizierten C4-Kandidaten-Zweig; Nachweis per Regressionstest, dass bei `bot_bNavItemBridge = 0` identisches Verhalten zum qualifizierten Build vorliegt.
3. **Stufe C4-3 (Offene Retail-Qualifikations-Gates — noch NICHT durch Offline-Tests abgedeckt):**
   - Echte TSE-1.07-Karten-Geometrie (Treppenstufen, Aufzüge, Teleporter, Jumppads, Lava-/Abgrund-Kanten `kEdgeDanger`).
   - Echte Pickup-Berührungsradien und Höhenversätze (`y`-Differenz bei Podesten) in Retail-Deathmatch-Maps.
   - Mehrminütiger Live-Multiplayer-Sync-Test (`0` `SYNCBAD`-Meldungen im Dedizierten Server + 4–8 Bot-Clients unter Last).
   - Messung der realen `GameMP.dll`-Framezeit auf Ziel-Hardware mit aktiviertem `bot_bNavItemBridge = 1`.
