# CecilBotMod ↔ Alpha-Gaming-Bot-KI – Technische Transferanalyse

**Datum:** 25.10.2026 · **Autor:** unabhängiger Senior-C++-Analyseagent (Arena-Sandbox, paralleler Entwicklungsauftrag)
**Projekt:** Serious Sam The Second Encounter Classic **Retail 1.07**, Vanilla-kompatible Bot-Clients
**Alpha-Gaming-Basiscommit:** `107d28a276c4fe4428cc3c8bf5bbd876e1a85351` (`main`)
**CecilBotMod-Referenz:** `953b477e53fdc5a5d84c8ae8d759c84fdf6c973c` (öffentlicher Klon, Read-only)
**Status:** reine Quellcode-Analyse. **Kein** MSVC-Build, **keine** Retail-Runtime, **keine** Hetzner-Messung in diesem Beitrag. Produktivsysteme, die qualifizierte DLL `61DC…`/`7fc9…` und offene Codex-Branches wurden nicht berührt.

## Kennzeichnung

| Kürzel | Bedeutung |
|---|---|
| **VERIFIZIERT** | in dieser Sitzung am konkreten Quellstand per Datei/Zeile oder Kommando geprüft |
| **IMPLEMENTIERT** | Code liegt vor, aber nicht im Ziel-Build nativ qualifiziert |
| **GETESTET** | hier offline automatisiert ausgeführt, Ergebnis im Text |
| **VORSCHLAG** | begründete Empfehlung, nicht umgesetzt |
| **OFFEN** | nicht prüfbar ohne Windows-/Retail-/Netzwerkzugang |

**In dieser Sitzung ausgeführte Prüfläufe (GETESTET):** `cd poc/botcore && make test` → `ALL CHECKS PASSED`, `ALL AI CHECKS PASSED`, `COMBAT POLICY PASS (0 failures)`, `OBSTACLE RECOVERY PASS`, `HUMAN AI PASS: 555 checks, 0 failures`. `make bench` → 0,44–0,51 µs/Tick pro Bot bei 4 Rays/Tick, `BENCH PASS` (Linux-Sandbox, g++, `-O2`; keine Retail-Aussage).

---

## 0. Executive Summary

1. **Kein CecilBotMod-Bestandteil ist als Ganzes übernehmbar.** CecilBotMod implementiert Bots als **Server-Entities** (`CPlayerBot : CPlayer`, `Sources/Bots/Classes/PlayerBot.es:38`) in modifizierten `EntitiesMP/GameMP/GameGUIMP`-DLLs, mit **Binärdetours** auf Engine-Netzwerkfunktionen (`Sources/Bots/NetworkPatch/ServerIntegration.cpp:57–80`) und einem **eigenen Netzwerkpaket** `MSG_CECIL_SANDBOX = 49` (`CustomPackets.h:23`), dessen Stream-Blöcke an **alle** Sessions angehängt werden (`ServerIntegration.cpp:36–55`). Das verletzt die verbindliche Alpha-Gaming-Vorgabe „Dedicated Server, Engine, Entities und menschliche TSE-1.07-Clients bleiben unverändert" (README, Absatz 1). Ob unveränderte Vanilla-Clients einem Cecil-Server technisch beitreten könnten, ist aus dem Quellcode **nicht entscheidbar** und wird hier nicht behauptet.
2. **Die Alpha-Gaming-KI ist CecilBotMod in Wahrnehmung, Zielen und Menschlichkeit überlegen; CecilBotMod ist in Navigation, Coop-/Item-Verhalten und Betriebsführung überlegen.** Die größten echten Lücken des eigenen Projekts sind: (a) **globale Navigation** (Cecil: Navmesh + A\*; Alpha-Gaming: nur reaktive Hinderniserholung, `WaypointGraph` liegt ungenutzt im Baum), (b) **Abgrund-/Sprungverhalten**, (c) **Item-Nutzung und Coop-Verhalten**, (d) **Sniper-Zoom**, (e) **Bedrohungs- und Gesundheitsgewichtung bei der Zielwahl**, (f) **Respawn-Verzögerung nach Schwierigkeit**.
3. **Übernommen werden sollen ausschließlich Mechanik-Ideen und Parameterordnungen als enginefreie Neuimplementierung in den bestehenden `poc/botcore/`-Schichten** – keine zweite Bot-Engine, kein kopierter Cecil-Code. Damit bleiben Vanilla-Kompatibilität, Sync-Sicherheit und die GPL-Lage kontrollierbar (Abschnitt C.6).
4. **Ein bekanntes Projektrisiko begrenzt die Navigation:** Der Ground-Lookahead-Versuch (11.–12.10.) erzeugte native `Too many bad syncs`-Abbrüche ohne bestandene Abnahme (README; `docs/reports/2026-10-17-retail107-sync-check-investigation.md:71`). Jede Boden-/Abgrundprüfung (Cecil `CheckPit`) fällt in dieselbe Risikoklasse und benötigt ein isoliertes natives Sync-Gate **vor** Integration.
5. Der priorisierte Integrationsplan (Abschnitt E) beginnt mit fünf enginefreien, offline testbaren Verbesserungen (P1), die **keine** neue Engine-API, **keine** neuen Rays und **keine** Netzwerkänderung brauchen.

---

## A. Architekturvergleich

### A.1 Alpha-Gaming („Pfad D") – VERIFIZIERT

```
Bot-Client = normales SeriousSam.exe mit modifizierter GameMP.dll
  CGameTimerHandler::HandleTimer -> CGame::GameHandleTimer   (poc/release/gamemp/Game.cpp:746–754)
    -> BotDriver_HandleTimer(this)                            (BotDriver.cpp, 20 Hz, Slots 0..3)
        botcore::HumanBotPolicy  (bot_human.h)  <- Profil (bot_profile.h)
          Perception (bot_perception.h)  Aim (bot_aim.h)  Loadout (bot_loadout.h)
        Legacy: botcore::DecideCombat (bot_combat.h)          [Standardpfad, bot_bHumanAI=0]
        ObstacleRecovery (bot_navigation.h), CombatWeaponInput (bot_weapon_input.h)
    -> CPlayerAction -> ctl_ComposeActionPacket -> CPlayerSource::SetAction   (regulärer Netzwerkpfad)
```

Eigenschaften (Quellen: `poc/release/gamemp/BotDriver.cpp`, `poc/candidates/integrated-human-cpu-20261021/BotDriver.cpp`, `poc/botcore/*.h`):

| Merkmal | Ist-Zustand |
|---|---|
| Bot-Identität | regulärer Netzwerkspieler; Server/Entities/Vanilla-Clients unverändert |
| Wirkungsort der KI | ausschließlich **clientseitig**, pro Bot-Client-Prozess ≤ 4 lokale Spieler |
| Entscheidungsschichten | enginefreie Header (`botcore`), deterministisch, 20 Hz, unit-getestet (555 Checks) |
| Zielwahl | Legacy: nächster sichtbarer Spieler (`SelectTarget`); Human-Pfad: Stickiness ×1,35 + 1,4×-Wechselschwelle (`bot_human.h::ChooseTarget`) |
| Wahrnehmung | FOV-Kegel 55–80°, Sichtweite 60–100 m, Reaktionszeit 0,15–0,55 s, Zielgedächtnis 1,2–3,0 s, Schadensalarm, Ray-Budget 4–8/Tick (`bot_perception.h`, `bot_profile.h`) |
| Zielen | Rate-/Beschleunigungsmodell mit Bremswegplanung, OU-korrelierter Bias, Überschwinger, Triggerdisziplin (`bot_aim.h`) |
| Waffen | Utility-Score (Distanzband, Genauigkeit, Selbstschaden) + Hysterese (`bot_loadout.h`); natives Select-Gruppen-Pulsprotokoll (`bot_weapon_input.h`) |
| Bewegung | vorwärts/zurück + (deaktivierter) Strafe-Anteil `bot_fStrafeScale=0`; reaktive `ObstacleRecovery` mit Front-/Seitenstrahlen; **kein** Navmesh, `WaypointGraph` ungenutzt (nur in `botcore_ai.h:151` definiert, 0 Verwendungen im Integrationscode – VERIFIZIERT per grep) |
| CPU-Drossel | `bot_iScanInterval`, `bot_fTargetRange`, `bot_iMaxLosRays`, `bot_iObstacleInterval` (Patch `0009`) |
| Spielmodi | Deathmatch (`GM_SCOREMATCH`/`GM_FRAGMATCH`); Coop nicht implementiert |
| Schwierigkeit | 5 Fähigkeitsstufen × 6 Persönlichkeiten, orthogonal, monoton, Seed-roster (`bot_profile.h`) |
| Telemetrie | `BotTelemetry.csv`-Watchdog im P0-Kandidaten (`poc/candidates/p0-nullrender-20261022/`, nicht gebaut/qualifiziert) |

### A.2 CecilBotMod – VERIFIZIERT

```
Modifizierter Dedicated/Host: EntitiesMP.dll + GameMP.dll + GameGUIMP.dll
  CPlayerBot : CPlayer                       (Sources/Bots/Classes/PlayerBot.es:38)
  Player.es-Hook: ApplyAction -> BotApplyAction   (Sources/EntitiesMP/Player.es:1253, 3625)
    -> BotThinking -> BotWeapons -> BotSelectNewWeapon   (PlayerBot.es:125–131)
       BotThinking (BotStructure.cpp:324–493):
         ClosestEnemy (BotFunctions.cpp:224)   – WELTSCAN aller Entities, pro Kandidat CastBotRay
         BotAim (BotMovement.cpp:229–338)      – P-Regler + 0,5-s-Genauigkeitsjitter + Vorhalten
         BotItemSearch (BotItems.cpp:37)       – Health/Armor/Ammo/Weapon mit Typdistanzen
         BotPathFinding (BotMovement.cpp:34–227) – Navmesh + A* (Navmesh.cpp) + „wichtige Punkte"
         BotMovement (BotMovement.cpp:395–604) – Strafe, Jump/Crouch aus Punktflags, CheckPit/AvoidPits
  Netzwerk: CPatch-Detours auf CMessageDispatcher::ReceiveFromClient(+Reliable) und
            CSessionState::ProcessGameStreamBlock (ServerIntegration.cpp:57–80);
            MSG_CECIL_SANDBOX=49 (CustomPackets.h:23); Blöcke an alle Sessions (ServerIntegration.cpp:36–55)
```

| Merkmal | Ist-Zustand |
|---|---|
| Bot-Identität | **Server-Entity**; Bots existieren nie als Netzwerk-Clients |
| Wirkungsort der KI | ausschließlich **serverseitig**, voller Entity-/Weltzugriff |
| Wahrnehmung | **kein** FOV, **keine** Reaktionszeit; Sichtbarkeit nur per `CastBotRay` (`BotFunctions.cpp:164`, `TT_NONE`, `BPOF_PASSABLE`, `cr_bHitTranslucentPortals`) |
| Zielwahl | `ClosestEnemy` scannt **jede Welt-Entity jeden Tick** (`BotStructure.cpp:337` → `BotFunctions.cpp:243 FOREACHINDYNAMICCONTAINER`), Prioritäten: sichtbar, wenig HP, nah, „hat mich im Ziel" (`BotFunctions.cpp:285–288`); Wiederwahl-Cooldown `fTargetCD` 1–3 s (`BotSettings.cpp:33,72`) |
| Zielen | Winkel zu Körperzentrum + 0,25-m-Höhenoffset bei Spielern (`BotMovement.cpp:278–279`); Vorhalten `Geschwindigkeit × (fPrediction + FRnd×fPredictRnd) × (1 − Waffengenauigkeit)` (`BotMovement.cpp:272–275`); Genauigkeitsjitter uniform ±`fAccuracyAngle`/2, alle 0,5 s erneuert (`BotMovement.cpp:292–302`); Drehrate = Fehler / `Clamp(dist/fRotSpeedDist, min, max)`, hart begrenzt auf ±`fRotSpeedLimit`=30°/Tick ≈ 600°/s (`BotMovement.cpp:310–330`) |
| Schießen | `|Winkelfehler| < fShootAngle` (15°) **und** (sichtbar oder `m_penRayHit==Ziel`) (`BotMovement.cpp:330–338`); Kadenz `bw_tmShotFreq` pro Waffe, z. B. Granatwerfer 1,0 s (`BotStructure.cpp:405–420`, `BotWeapons.cpp:35`) |
| Waffenwahl | `damage × (accuracy + (1−accuracy)×(1−Distanzanteil))` über Distanzband,Cooldown `fWeaponCD` 3–5 s (`BotStructure.cpp:245–315`); getrennte Tabellen Deathmatch/Coop (`BotWeapons.cpp:27–60`); Messer bei >2 s ohne Feindkontakt für Laufgeschwindigkeit (`BotStructure.cpp:258–270`) |
| Bewegung | Translationsvektor „wie Controller" (`BotMovement.cpp:591–597`); Nahkampf-Strafe mit gesundheitsgewichteter Bandbreite (`BotMovement.cpp:416–420`), Seitenwechsel alle 2–4 s (`BotMovement.cpp:404–407`); Jump/Crouch/Walk aus Navmesh-Punktflags; `CheckPit`/`AvoidPits` über `WouldFallInNextPosition` mit manipuliertem `en_vNextPosition`/`en_fStepDnHeight` (`BotMovement.cpp:341–397`); Coop-Teleport >200 m (`BotStructure.cpp:468`) |
| Navigation | kartenabhängiges Navmesh aus Brush-Polygonen (`Navmesh.cpp`, Generation `NavMeshGenerator.es`), A\* `FindNextPoint` mit linearer Open-Liste, Punktflags `PPF_WALK/JUMP/CROUCH/OVERRIDE/UNREACHABLE/TELEPORT/IMPORTANT` (`PathPoint.h:23–29`); 9 mitgelieferte `.nav`-Dateien 6–22 KB (`Cecil/Navmeshes/`); „wichtige Punkte" (Items/Switches/Marker) mit Chance `fImportantChance` (`BotMovement.cpp:66–86`, `BotFunctions.cpp:124–160`) |
| Schwierigkeit | 4 Presets Dummy/Easy/Normal/Hard als flache Parametersätze (`BotSettings.cpp:20–176`), zur Laufzeit pro Bot änderbar (`BotUpdate`, `SandboxActions.cpp:690–695`) |
| Respawn | `fRespawnDelay` pro Preset 0–3 s, Feuerpuls über `ButtonAction()` 0,2-s-Raster (`PlayerBot.es:133–157`, `BotStructure.cpp:210–222`) |
| Sonstiges | Sniper-Zoom über `PLACT_SNIPER_USE|PLACT_SNIPER_ZOOMIN` + 0,2×-Genauigkeitsbonus beim Zoom (`BotWeapons.cpp:64–89`, `BotMovement.cpp:295–297`); Bot-Zustand serialisierbar (`BotStructure.cpp:54–186`); Namen/Skins aus Textdateien; Item-Suche mit Such-Cooldown 5 s |
| CPU-Charakter | Weltscan + Rays pro Kandidat **jeden Tick** pro Bot; A\* mit `new CPathPoint` pro Punkt pro Suche und linearer Minimum-Suche (O(n²)) (`Navmesh.cpp FindNextPoint`); Repath-Cooldown 5 s (`BotMovement.cpp:224`) |

### A.3 Kernunterschied in einem Satz

Alpha-Gaming erzeugt **menschliche Eingaben auf einem normalen Client** und muss dafür Wahrnehmung, Reaktion und Fehler mechanisch modellieren; CecilBotMod **ist** der Server, kennt die Welt direkt und kann sich auf Navigations- und Verhaltensbreite konzentrieren – bezahlt das aber mit vollständiger Server-/Netzwerkmodifikation.

---

## B. Funktionsmatrix

Legende: **A** = Alpha-Gaming-Stand (Commit `107d28a`), **C** = CecilBotMod (`953b477`). ● vorhanden, ◐ teilweise, ○ fehlt.

| # | Mechanik | A | C | Befund / Beleg |
|---|---|:-:|:-:|---|
| 1 | Navigation – global | ○ | ● | A: `WaypointGraph` nur definiert, nie verwendet (grep VERIFIZIERT); C: Navmesh+A\*, 9 `.nav`-Karten |
| 2 | Navigation – reaktiv | ● | ◐ | A: `ObstacleRecovery` (Stuck+Blocked, Turn/Advance-Phasen, Cooldowns); C: Nahdistanz-Ausweichen per Strafe/Jump (`BotMovement.cpp:565–575`) |
| 3 | Abgrund-/Fallvermeidung | ○ | ● | C: `CheckPit`/`AvoidPits` (`BotMovement.cpp:341–397`); A: nichts; **Sync-Vorbelastung** durch Ground-Lookahead-Fehlversuch |
| 4 | Sprung-/Crouch-Nutzung | ◐ | ● | A: nur Test-Jump im Nicht-KI-Pfad (`TestJump`); C: Jump/Crouch aus Punktflags + Sprung über Gruben |
| 5 | Gegnererkennung – Modell | ● | ○ | A: FOV, Reaktionszeit, Gedächtnis, Alarm, Ray-Budget; C: sofort, allwissend (nur LOS-Ray) |
| 6 | Gegnererkennung – Zielmenge | ◐ | ● | A: nur replizierte Spieler (16); C: Spieler **und** Monster (`IsEnemyMonster`, `BotFunctions.cpp:216–222`) |
| 7 | Zielverfolgung nach Sichtverlust | ● | ◐ | A: Zielgedächtnis mit Konfidenzablauf; C: 2-s-Nachsicht (`m_tmLastSawTarget`), dann Laufrichtung statt Ziel |
| 8 | Zielpriorisierung | ◐ | ● | C: sichtbar/HP-niedrig/nah/**„zielt auf mich"** (`BotFunctions.cpp:285–288`); A: nur Distanz+Stickiness |
| 9 | Zielwechsel-Hysterese | ● | ◐ | A: Hard-Lock + 1,4×-Schwelle; C: nur Zeit-Cooldown `fTargetCD` |
| 10 | Aiming – Dynamik | ● | ◐ | A: Rate/Beschleunigung/Overshoot; C: P-Regler mit 600°/s-Cap → Hard ≈ Snap-Aim mit Jitter |
| 11 | Aiming – Fehlermodell | ● | ◐ | A: OU-Prozess + Ziel-Offset + Triggerdisziplin, reproduzierbar per Seed; C: uniformer Jitter, 0,5-s-Refresh, `rand()`-basiert |
| 12 | Aiming – Vorhalten | ● | ● | A: physikalisch `distanz/proj_speed × prediction_gain`; C: `v × (0,1..0,5 + Rnd) × (1−acc)` |
| 13 | Aiming – Zielpunkt | ◐ | ● | C: Körperzentrum + 0,25 m; Zoom-Bonus; A: Augpunkt, kein Scope |
| 14 | Schussverhalten – Auslösung | ● | ● | A: `fire_tol` 1,5–5° + `settle_s` + frische LOS; C: 15°-Kegel + RayHit |
| 15 | Schussverhalten – Kadenz | ◐ | ● | C: Waffen-Kadenz `bw_tmShotFreq` (Granatwerfer 1 s); A: Dauerfeuer bei Freigabe, Legacy-Puls |
| 16 | Waffenwahl – Modell | ● | ● | beide Distanzband-Scores; A zusätzlich Selbstschaden-Strafterm + Hysterese + Persönlichkeits-Tilt |
| 17 | Waffenwahl – Modus-Tabellen | ○ | ● | C: getrennte Coop-Tabelle (`BotWeapons.cpp:45–64`); A: nur Deathmatch |
| 18 | Waffenwahl – Messer-Laufen | ○ | ● | C: Messer nach 2 s ohne Feind (DM-Geschwindigkeitsbonus); A: `knife_while_travelling` existiert, **default aus** (`bot_human.h:284`) |
| 19 | Sniper-Zoom | ○ | ● | C: `UseWeaponScope` (`BotWeapons.cpp:75–89`) |
| 20 | Ausweichen – Strafe | ◐ | ● | A: Strafe-Absicht vorhanden, aber `bot_fStrafeScale=0` (nicht nativ verifiziert); C: aktiv, gesundheitsgeweitet, Richtungsrandom 2–4 s |
| 21 | Ausweichen – Rückzug | ● | ◐ | A: Retreat unter `retreat_health`-Schwelle; C: kein HP-Rückzug, nur größerer Strafe-Radius + Item-Suche (`fHealthSearch`) |
| 22 | Reaktionszeiten | ● | ○ | A: 0,15–0,55 s + Alarmverkürzung; C: keine (Sofortreaktion) |
| 23 | Schwierigkeitsgrade | ● | ● | A: 5×6 orthogonal, monotoniegetestet; C: 4 flache Presets, dafür **laufzeitänderbar pro Bot** |
| 24 | Entscheidungslogik-Struktur | ● | ◐ | A: enginefrei, unit-getestet, zwei Pfade + Telemetrie; C: monolithisch im Entity-Kontext, `SBotThoughts`-Debugausgabe |
| 25 | Item-Nutzung | ○ | ● | C: `BotItemSearch` mit Health/Armor/Ammo/Weapon-Distanzen, HP-Schwelle, 5-s-Cooldown |
| 26 | Coop-Verhalten | ○ | ● | C: Spieler folgen (3 Modi), Monster-Targets, Follow-Teleport |
| 27 | Respawn-Steuerung | ◐ | ● | A: fester 4-Tick-Press/Release-Puls; C: Preset-Verzögerung 0–3 s + 0,2-s-Buttonraster |
| 28 | CPU-Effizienz-Design | ● | ◐ | A: FOV-Gate + hartes Ray-Budget + Throttle-Symbole, 0,44–0,51 µs/Tick Entscheidung (GETESTET); C: Vollscan + Ray pro Kandidat pro Tick, A\*-Allocation |
| 29 | Vanilla-Client-Kompatibilität | ● | ○ | A: Bots sind normale Clients (bestandene Abnahmen); C: Server-DLL-Tausch + Netzwerkdetours + Custom-Pakete |
| 30 | Sync-Risikoprofil | ● | n/a | A: nur `CPlayerAction`-Eingaben; bekannte offene `Too many bad syncs`-Historie bei Ground-Features; C: serverseitig → kein Client-Sync, aber eigener Netzwerkstrom |

**Fazit der Matrix:** 11 Zeilen sprechen klar für Alpha-Gaming (2, 5, 7, 9, 10, 11, 21, 22, 24, 28, 29), 14 klar für CecilBotMod (1, 3, 4, 6, 8, 13, 15, 17, 18, 19, 20, 25, 26, 27), 4 sind gleichauf mit unterschiedlichem Charakter (12, 14, 16, 23), Zeile 30 nicht vergleichbar. Die Cecil-Stärken liegen fast vollständig in **Verhaltensbreite** (Navigation, Items, Coop, Zoom), die Alpha-Gaming-Stärken in **KI-Qualität pro Kampfhandlung** (Wahrnehmung, Zielen, Reaktion, Effizienz) und in der Vanilla-Kompatibilität.

---

## C. Übertragbarkeitsbewertung

Bewertungsklassen: **1** = direkt als enginefreie Idee übernehmbar · **2** = nach Anpassung übernehmbar · **3** = nur algorithmisches Vorbild · **4** = mit Projektvorgaben unvereinbar.

| Mechanik (Cecil-Quelle) | Klasse | Technische Übertragbarkeit | Vanilla-Client | GameMP-Eingriff | MP-/Sync-Risiko | CPU/RAM | Lizenz |
|---|:-:|---|---|---|---|---|---|
| Bedrohungs-/HP-Zielpriorität (`BotFunctions.cpp:285–288`) | **1** | als Score-Term in `ChooseTarget`; „zielt auf mich" clientseitig über replizierte Blickvektoren anderer Spieler approximierbar (Position+Yaw stehen im Snapshot, `BotDriver.cpp [BotSnapshot]`) | unverändert | keiner (nur Entscheidungscode) | keins (deterministisch, client-lokal) | ~0 | Idee, GPL-konform neu formuliert |
| Respawn-Verzögerung (`PlayerBot.es:133–157`) | **1** | Pro-Stufen-Feld `respawn_delay_s` + Tick-Fenster im Human-Pfad; Fire-Puls existiert schon | unverändert | keiner | keins | 0 | wie oben |
| Waffen-Kadenz `bw_tmShotFreq` (`BotWeapons.cpp:35`, `BotStructure.cpp:405–420`) | **1** | neues Feld `shot_period_s` in `WeaponProfile`, Feuer-Gate in `bot_aim`/`bot_human` | unverändert | keiner | keins | 0 | wie oben |
| Messer-Laufen (`BotStructure.cpp:258–270`) | **1** | `knife_while_travelling` **existiert bereits** (`bot_loadout.h:140`), nur default aus; Aktivierung per Konsole-Flag + Runtime-Prüfung | unverändert | keiner | keins | 0 | wie oben |
| Sniper-Zoom (`BotWeapons.cpp:75–89`) | **2** | Buttons `PLACT_SNIPER_USE/ZOOMIN` als normale Action-Bits; Bitwerte aus SDK-`Player.es` übernehmen, Zoom-Bonus als Skill-Parameter | unverändert | minimal (Button-Komposition) | **niedrig, aber OFFEN**: Zoom-Button-Rising-Edge-Verhalten in Retail 1.07 nicht nativ verifiziert | 0 | Bit-Konventionen sind Vanilla-Fakten, kein Cecil-Ausdruck |
| Genauigkeitsbonus bei Zoom (`BotMovement.cpp:295–297`) | **2** | Skill-Feld; hängt an Zoom-Status, den der Client aus `m_bSniping` lesen kann | unverändert | keiner | keins | 0 | Idee |
| Strafe-Radius nach Gesundheit (`BotMovement.cpp:416–420`) | **1** | Term in `MoveIntent`; Basis-Strafe bereits implementiert | unverändert | keiner | keins | 0 | Idee |
| Coop-Waffentabelle (`BotWeapons.cpp:45–64`) | **2** | zweite `WeaponProfile`-Tabelle + Modus-Umschaltung; nutzbar erst mit Coop-Zielen (Monster), sonst nur Tabelle | unverändert | keiner | keins | minimal | Tabellenwerte sind Cecil-Kalibrierung → **eigene Werte** verwenden |
| Item-Suche (`BotItems.cpp:37–131`) | **3** | Prinzip (Typdistanzen, HP-Schwelle, Such-Cooldown) übernehmbar; Umsetzung braucht Entity-Iteration im Client und Item-Klassenerkennung per Klassenname (Cecil nutzt `IsOfClass`-Strings) | unverändert | mittel (neue Weltzugriffe) | **mittel**: mehr Weltzugriffe unter `ga_csNetwork`; Read-only, aber Last auf Coop-Karten mit vielen Entities | Entity-Scan muss gedrosselt werden (Cecil: 5-s-Cooldown) | Idee |
| Coop-Folgen/Monster-Targets (`BotStructure.cpp:432–480`) | **3** | nur mit Item-/Monster-Grundlage sinnvoll; Follow-Teleport ist serverseitig → **nicht** übertragbar (Cheatschutz/Vanilla) | unverändert | mittel | mittel | Scan-Last | Idee |
| Abgrundvermeidung `CheckPit` (`BotMovement.cpp:341–397`) | **3** | `WouldFallInNextPosition` + Feldmanipulation ist Server-Entity-Code; clientseitiges Äquivalent = zusätzliche Boden-`CCastRay`s (gleiche Primitiven wie `BotObstacleDistance`) | unverändert | klein (neue Rays) | **hoch**: Ground-Lookahead-Versuch endete mit `Too many bad syncs`-Disconnects (Sync-Bericht, Zeile 71); Ursache ungeklärt → erst isoliertes natives Sync-Gate | +1–3 Rays/Bot/Tick, drosselbar | Idee |
| Navmesh + A\* (`Navmesh.cpp`, `PathPoint.h`, `NavMeshGenerator.es`) | **3** | größter Brocken: Generator ist Engine-nah (Brush-Polygone); für Alpha-Gaming nur als **clientseitiges** Offline-/Ladezeit-Werkzeug denkbar, `.nav`-Äquivalent pro Karte in der Bot-Installation; A\*-Logik (Distanzheuristik, Punktflags) neu implementierbar | unverändert (Daten bleiben client-lokal) | mittel–hoch | mittel: reine Entscheidungsdaten, aber Generierung/Dateiformat sind neue Infrastruktur | A\* mit Budget + Open-Liste als Heap; Cecil erzeugt pro Suche Allocation → nicht kopieren | Code-Idee GPL-frei neu; **`.nav`-Daten aus Retail-Geometrie sind Croteam-abgeleitet → nicht redistribuieren** |
| Wichtige Punkte / Patrouille (`BotMovement.cpp:66–86`) | **2** | mit vorhandenem `WaypointGraph` + pro Karte handautorisierten/Generierten `.wpt`-Dateien als Zwischenstufe vor Navmesh | unverändert | keiner (Datei-I/O client-lokal) | keins | minimal | Idee |
| Schwierigkeits-Presets (`BotSettings.cpp`) | **1** | als Strukturvorbild bereits 2026-10-20 übernommen; Rest: **Laufzeit-Profilwechsel** pro Bot als Konsole-Kommando | unverändert | keiner | keins | 0 | Idee |
| Bot-Zustand-Serialisierung (`BotStructure.cpp:54–186`) | **4** | benötigt Entity-Lebenszyklus; Alpha-Gaming-Bots sind Sessions, Persistenz passt nicht zum Reconnect-Modell | — | — | — | — | — |
| `CPlayerBot`-Entity + `BotApplyAction` (`PlayerBot.es`) | **4** | modifizierte `EntitiesMP.dll` → verletzt „Entities unverändert" | **verletzt** | — | — | — | — |
| Netzwerkdetours + `MSG_CECIL_SANDBOX` (`ServerIntegration.cpp`, `CustomPackets.*`, `Patcher/`) | **4** | gepatchte Engine-Funktionen + eigener Strom an alle Sessions → verletzt „Engine/Server unverändert" | **verletzt** | — | — | — | — |
| `SBotThoughts`, Namen/Skins, Crosshair-Kosmetik | **4** | Chat-/Denktexte und Meme-Namen widersprechen der administrativen `BOT-`-Kennzeichnung; nicht übernehmen | — | — | — | — | — |
| Server-Teleport-Follow >200 m (`BotStructure.cpp:468`) | **4** | `Teleport()` am Entity; clientseitig unmöglich/cheatartig | **verletzt** | — | — | — | — |

### C.6 Lizenzbewertung (GPLv2) – VERIFIZIERT

- CecilBotMod ist **GPL-2.0** (`LICENSE`, Dateiköpfe „Copyright (c) 2018–2025 Dreamy Cecil … version 2 of the GNU General Public License").
- Alpha-Gaming veröffentlicht GameMP-Anpassungen bereits als **GPL-2.0-only** (`THIRD-PARTY-NOTICES.md`, `poc/release/LICENSE`) und nennt CecilBotMod als Referenz. Die Lizenzen sind damit kompatibel.
- **Empfohlener Weg (entspricht der Praxis des Berichts 2026-10-20):** keine Cecil-Quelldatei kopieren; Mechaniken enginefrei neu formulieren und **eigene** Kalibrierwerte verwenden. Dann entsteht keine zusätzliche Fremdcode-Verpflichtung; `THIRD-PARTY-NOTICES.md` bleibt gültig.
- Falls dennoch Cecil-Code übernommen wird: Copyright-Kopf behalten, GPL-2.0-only kennzeichnen, Hinweis in `THIRD-PARTY-NOTICES.md` ergänzen. Für eine reine Server-/Bot-Client-Modifikation ohne Weiterverbreitung von Cecil-Binärcode bleibt die Pflichtenkette überschaubar; eine **Veröffentlichung** abgeleiteter Quellen (wie dieses Repo sie übt) muss den Cecil-Hinweis tragen.
- **Daten vs. Code:** die 9 `.nav`-Dateien sind aus Croteam-Retail-Karten abgeleitete Positionsdaten. Sie sind **nicht** in dieses Repository zu übernehmen; eigene Navmesh-Daten aus lokal rechtmäßig vorhandenen Karten bleiben privat (analog der `.codex/`-Regel).

---

## D. Priorisierte Verbesserungen

Bewertung: **Nutzen** (Spielqualität/Betriebsführung) × **Kosten** (Code, Risiko, Abnahmeaufwand). Alle Punkte bauen auf der **bestehenden** Architektur auf (`poc/botcore` + `BotDriver`), keine neue Engine.

| Rang | Verbesserung | Quelle (Vorbild) | Nutzen | Kosten/Risiko | Gate-Bedarf |
|---|---|---|---|---|---|
| **P1.1** | Bedrohungs-/HP-gewichtete Zielwahl („wer schießt auf mich", low-HP-Bonus) | `BotFunctions.cpp:285–288` | hoch (Kampf wirkt situativ statt distanzfixiert) | niedrig, enginefrei | Offline-Tests |
| **P1.2** | Waffenfeuer-Kadenz (Granatwerfer/Cannon getaktet statt Dauerfeuer) | `bw_tmShotFreq` | mittel–hoch (spart Ammo, wirkt menschlich) | niedrig, enginefrei | Offline-Tests |
| **P1.3** | Respawn-Verzögerung pro Fähigkeitsstufe | `fRespawnDelay` | mittel (Anfänger respawnen langsamer) | niedrig | Offline-Tests + Smoke |
| **P1.4** | Messer-Laufen zwischen Kämpfen (Flag-gated) | `BotStructure.cpp:258` | mittel (natürliches DM-Verhalten) | niedrig; **Vorbehalt:** Weapon-Switch-Puls bereits nativ erprobt | Runtime-Smoke |
| **P1.5** | Strafe-Radius nach Gesundheit + Wiederaktivierung von `bot_fStrafeScale` im Testprofil | `BotMovement.cpp:416–420` | hoch (Ausweichen ist größte Sichtbarkeitslücke) | mittel: `pa_vTranslation(1)` ist **nicht nativ verifiziert** | isolierter Retail-Join + Sync-Gate |
| **P2.1** | Patrouille/Waypoint-Nutzung ohne Ziel (`WaypointGraph` + `.wpt`-Dateien) | „wichtige Punkte" | hoch (Bots stehen nicht mehr nur drehend herum) | mittel: Datei-Loader + Kartenarbeit | Offline-Tests + Map-Lauf |
| **P2.2** | Abgrund-/Bodenprüfung per clientseitigem Bodenray (nicht `WouldFallInNextPosition`) | `CheckPit`/`AvoidPits` | hoch (Karten mit Gruben) | **hoch**: Ground-Lookahead-Sync-Historie | **erst** isoliertes natives Sync-Gate, dann Integration |
| **P2.3** | Sniper-Zoom + Zoom-Genauigkeitsbonus | `UseWeaponScope` | mittel | mittel: Button-Edges Retail-unverifiziert | Runtime-Smoke |
| **P2.4** | Laufzeit-Profilwechsel pro Bot (Konsole: `bot_SetProfile(slot,tier,persona)`) | `BotUpdate` | mittel (Betrieb ohne Rejoin) | niedrig | Offline + Smoke |
| **P3.1** | Item-Nutzung (Health/Armor/Ammo/Weapon, HP-Schwelle, Such-Cooldown) | `BotItemSearch` | hoch für Coop, mittel für DM | mittel–hoch: Entity-Scan im Client, Drosselung Pflicht | Offline + CPU-A/B + Runtime |
| **P3.2** | Clientseitiges Navmesh (Generator-Werkzeug + `.nav`-Cache + budgetiertes A\*) | `Navmesh.cpp`/`NavMeshGenerator.es` | **sehr hoch** (einzige echte Navigationslösung) | hoch: neues Subsystem, Kartendaten, CPU-Budget | mehrstufig (E.3) |
| **P3.3** | Coop-Modus (Monster-Targets, Folgen, Coop-Waffentabelle) | `iTargetType`, `iFollowPlayers` | hoch (Zielgruppen-Erweiterung) | hoch: setzt P3.1/P3.2 voraus | eigene Phase |

**Explizit nicht übernommen:** Server-Entities, Netzwerkpatches, Custom-Pakete, Teleport-Follow, Bot-Gedanken/-Namen (Klasse 4, Abschnitt C).

---

## E. Integrationsplan

Grundregeln: (1) alles in den bestehenden Schichten `poc/botcore/*.h` + `poc/patch/00NN-gamemp-*.patch`; (2) `poc/release/gamemp/**` bleibt bytegenau unangetastet (Provenance `61DC…`); (3) jede Stufe hat ein Offline-Gate, bevor Windows-/Retail-Gates überhaupt relevant werden; (4) keine Änderung berührt Reliability, dynamische Sessions oder Serverbetrieb; (5) Standardverhalten neuer Kandidaten bleibt mit Default-Flags bitgleich zum jeweiligen Basispfad.

### E.1 Phase 1 – Enginefreie Entscheidungs-Upgrades (P1.1–P1.3, kein neuer Engine-Code)

| Schritt | Datei | Funktion/Änderung | Abhängigkeit |
|---|---|---|---|
| 1a | `poc/botcore/bot_perception.h` | `SenseInput`/`TrackState` um Blickrichtung des Kandidaten (yaw/pitch aus Replikation) ergänzen; Helfer `AimsAtMe(self, other, tol_deg)` | Snapshot liefert Yaw bereits (`[BotSnapshot]`-Zeile) |
| 1b | `poc/botcore/bot_human.h` | `ChooseTarget`: Score = `1/(d+1) × (1 + w_threat·aims_at_me) × (1 + w_lowhp·(1−hp/max))`; Gewichte pro Stufe in `SkillParams` | 1a |
| 1c | `poc/botcore/bot_loadout.h` | `WeaponProfile.shot_period_s` (0 = Dauerfeuer); `WeaponSelector::Update` gibt „fire window" heraus | — |
| 1d | `poc/botcore/bot_human.h` | `Step`: Feuer nur innerhalb Kadenzfenster; `respawn_delay_s` aus `SkillParams` → Respawn-Puls-Timing an den Driver melden | 1c |
| 1e | `poc/botcore/bot_profile.h` | neue Skill-Felder `threat_weight`, `lowhp_weight`, `shot_period_s`-Zuordnung, `respawn_delay_s`; Monotonie-/Orthogonalitätstests erweitern | 1b–1d |
| 1f | `poc/botcore/test_bot_human_ai.cpp` | neue Checks: Bedrohungspräferenz, HP-Präferenz, Kadenzfenster (Granatwerfer ≤ 1 Schuss/s), Respawn-Timing, Determinismus mit Seeds | 1a–1e |
| 1g | `poc/patch/0010-gamemp-*.patch` | `BotDriver.cpp`: Blickwinkel anderer Spieler in `SenseInput` füllen; Respawn-Puls verwendet Policy-Wert | 1a–1e |

**Reproduzierbare Tests:** `cd poc/botcore && make test` (alle bestehenden + neuen Checks grün, **erst RED-Demonstration** des Fehlverhaltens), `make bench` (≤ +0,1 µs/Tick), `python3 poc/botcore/verify_patch.py`-Äquivalent für Patch 0010. **Vanilla/Sync:** keine neue Engine-API, keine Netzwerkänderung → kein zusätzliches Sync-Risiko gegenüber dem qualifizierten Pfad; trotzdem gilt jeder Rebuild als neuer Kandidat ohne automatische Runtime-Abnahme (AGENTS.md).

### E.2 Phase 2 – Bewegung sichtbar machen (P1.4, P1.5, P2.3, P2.4)

| Schritt | Inhalt | Gate |
|---|---|---|
| 2a | `knife_while_travelling` hinter `bot_bKnifeTravel` (Default 0) | Offline: Loadout-Test „Messer nach 2 s ohne Ziel, nur wenn Gruppe 1 frei"; Runtime: `[BotCombatWeapon]`-Zeilen zeigen Gruppe-1-Puls |
| 2b | Strafe-Aktivierung: `bot_fStrafeScale` A/B (0 vs. 0,5) im **isolierten** Retail-Join; Gesundheitsradius-Term in `MoveIntent` | **natives Sync-Gate**: 1 Bot 10 min, `tools/analyze_sync_log.py` = 0 SYNCBAD; erst danach Vier-Bot-Stunde |
| 2c | Sniper-Zoom: `PLACT_SNIPER_USE/ZOOMIN`-Bits aus SDK-`Player.es` übernehmen, Rising-Edge-Protokoll analog `CombatWeaponInput` | Runtime-Smoke: Zoom-Status in `m_bSniping` sichtbar wechselt; Sync-Gate wie 2b |
| 2d | `bot_SetProfile(iLP,tier,persona)`-Konsolenfunktion → `BotHumanAttach`-Neuaufruf | Offline: Profilwechsel-Reset-Test; Runtime: `[BotHuman]`-Zeile zeigt neues Label |

**Risikosteuerung:** 2b/2c erzeugen erstmals Actions jenseits des nativ abgenommenen Musters (Lateralachse, Zoom-Buttons). Reihenfolge zwingend: einzeln, isolierte Kopie, eigene Ports, nicht auf dem öffentlichen Server, Kontrolllauf ohne Flag.

### E.3 Phase 3 – Navigation (P2.1, P2.2, P3.2)

1. **Zwischenstufe Waypoints (P2.1):** `WaypointGraph::ParseLine` (vorhanden, `botcore_ai.h:229`) per Datei-Loader im BotDriver füttern (`Scripts\Bots\<Map>.wpt`); Zielauswahl: ohne Gegner → nächster erreichbarer Knoten statt Stand-Drehung. CPU: BFS ≤ 256 Knoten, vernachlässigbar. Gate: Offline-Loader-Tests + Map-Lauf mit Fortschrittsnachweis (Analogon: `Test-ObstacleEvidence.py`).
2. **Abgrundprüfung (P2.2):** **vor** jeder Implementierung isolierte native Probe (1 Bot, Testkarte mit known pit, 30 min, `analyze_sync_log.py`), da Ground-Lookahead historisch `Too many bad syncs` erzeugte. Umsetzung nur als **zusätzliche read-only `CCastRay` nach unten** (Muster `BotObstacleDistance`), nie `WouldFallInNextPosition`/Entity-Feldmanipulation. Ergebnis fließt als `NavigationInput.front`-Äquivalent in die bestehende `ObstacleRecovery`.
3. **Navmesh (P3.2, eigene Phase mit separatem Auftrag):** Offline-Generator (eigener Karten-Scan im isolierten Bot-Client oder Editor-Werkzeug), binäres `.nav`-Äquivalent **privat** in der Bot-Installation, clientseitiger A\* mit Heap und Punktebudget (Cecils O(n²)-Open-Liste und Such-Allocation **nicht** kopieren), Punktflags WALK/JUMP/CROUCH analog `PathPoint.h:23–29`. Reihenfolge: Datenformat → Generator → Loader+Tests → A\*+Tests → CPU-Budget (≤ 1 ms/Pfad bei ~500 Punkten) → Kartenabnahme. Kartenabhängige Daten niemals ins öffentliche Git.

### E.4 Phase 4 – Coop und Items (P3.1, P3.3)

Item-/Monster-Scan nur gedrosselt (Cooldown ≥ 1 s, Distanzfilter, `ga_csNetwork`-Lock bleibt), Klassenerkennung per Klassenname-String statt DLL-Klassenzeiger (portabler gegenüber SDK-Ständen), kein Servereingriff. Coop-Ziellogik erst nach bestandener Navmesh-Phase; Follow-Teleport entfällt ersatzlos.

### E.5 Abgrenzung zur Parallelarbeit

- Keine Berührung von: Reliability-/Reconnect-Pfaden (`bot_reconnect.h`, Patches 0002/0003), dynamischen Sessions/Population (`poc/scripts/PopulationCore.ps1`), P0-Telemetrie/Null-Render (`poc/candidates/p0-nullrender-20261022/`), produktiven Hetzner-Läufen, qualifizierten DLLs.
- Dieser Auftrag liefert **nur** diesen Bericht + PR. Jede Codephase startet als eigener Branch/Kandidat mit eigenen Gates.

---

## F. Test- und Abnahmekriterien

### F.1 Offline (jede Phase, Linux-Sandbox, ohne Retail)

| Kriterium | Verfahren | Bestanden, wenn |
|---|---|---|
| Entscheidungssemantik | `cd poc/botcore && make test` | alle bestehenden **und** neuen Checks grün; neuer Check vorher demonstrativ RED |
| Determinismus | gleiche Seeds + Eingabefolge | bitgleiche `BotCommand`-Folgen (`TestReproducibility`-Muster) |
| Orthogonalität/Monotonie | `SkillUnaffectedByPersonality`, Stufen-Monotonie | unverändert erfüllt trotz neuer Skill-Felder |
| CPU-Budget | `make bench` | ≤ 0,6 µs/Tick pro Bot (Ist: 0,44–0,51, GETESTET) |
| Patch-Hygiene | `git apply --check` + Reproduktionsskript | Patch wendet sauber an, Integrationskopie reproduzierbar |
| Ray-Budget | `TestRayBudget`-Muster | neue Kandidaten erhöhen Rays/Tick nicht über das Stufenbudget |

### F.2 Windows-Build-Gate (vor jeder Runtime-Aussage)

VS2022/v143/x86, SDK-Pin `aa7869c…`/Includes `94ff8cd…`, WinSDK 10.0.19041.0; Warnungsfreiheit für geänderte Module; neuer DLL-SHA256 wird eigener Kandidat (keine automatische Abnahme, AGENTS.md).

### F.3 Native Retail-Gates (isolierte Kopien, nie produktiv)

| Gate | Inhalt | Abbruchkriterium |
|---|---|---|
| G1 Ein-Bot-Smoke | Testkarte, `bot_iLogEvery=20`, neue Logzeilen plausibel | Crash, fehlende Actions, falsche Waffenprotokoll-Zeilen |
| G2 Sync-Gate (für jede neue Action-Art: Strafe, Zoom, Kadenz) | 1 Bot 10–30 min, Serverlog → `tools/analyze_sync_log.py` | **≥ 1 SYNCBAD** → Feature zurück, keine `ser_iKickOnSyncBad`-Maskierung |
| G3 Boden-/Abgrund-Spezialgate | bekannter Pit, 30 min, Kontrolllauf ohne Feature | SYNCBAD oder Absturz → P2.2 gestoppt |
| G4 Vier-Bot-A/B CPU | gleicher Build, Flag 0/1, `pidstat`/`measure_window.sh` nach `docs/reports/2026-10-22-cpu-measurement-protocol.md` | Entscheidungs-CPU-Delta > Messrauschen ohne Nutzen |
| G5 Acht-Bot-Stunde + Vanilla-Observer | zwei Clients (Roster 0/4), Mapwechsel, externer Original-Client tritt bei und spielt | SYNCBAD, Disconnect, Observersync-Fehler |
| G6 Externe Sichtbarkeit | nur bei Bedarf: separater Browser-/WAN-Nachweis | Vermischung mit Direkt-IP-Join = kein PASS |

### F.4 Abnahme pro Verbesserung (Zusammenfassung)

| Verbesserung | Offline | G1 | G2 | G3 | G4 | G5 |
|---|:-:|:-:|:-:|:-:|:-:|:-:|
| P1.1 Zielwahl | ● | ● | ● | – | ○ | ● |
| P1.2 Kadenz | ● | ● | ● | – | – | ● |
| P1.3 Respawn-Delay | ● | ● | – | – | – | ○ |
| P1.4 Messer-Laufen | ● | ● | – | – | – | ○ |
| P1.5 Strafe + HP-Radius | ● | ● | **●** | – | ● | ● |
| P2.1 Waypoint-Patrouille | ● | ● | – | – | ○ | ● |
| P2.2 Abgrundprüfung | ● | ● | **●** | **●** | ● | ● |
| P2.3 Sniper-Zoom | ● | ● | **●** | – | – | ○ |
| P2.4 Profilwechsel | ● | ● | – | – | – | – |
| P3.1 Items | ● | ● | – | – | **●** | ● |
| P3.2 Navmesh | ● | ● | – | ○ | **●** | ● |
| P3.3 Coop | ● | ● | ● | ○ | ● | ● (Coop-Map) |

● Pflicht · ○ empfohlen · – nicht anwendbar.

---

## H. Handoff

| | |
|---|---|
| Branch | `arena/8317e1d6-serioussam-tse-bot-servermods` (isolierter Arena-Branch) |
| Geänderte Dateien | nur dieser Bericht (`docs/audits/…`) – **keine** Code-, Skript- oder Konfigurationsänderung |
| Referenzen | CecilBotMod-Klon `953b477` (öffentlich, Read-only, außerhalb des Repos); Alpha-Gaming-Basis `107d28a` |
| Ausgeführt | `make test` (PASS, 555+ Checks), `make bench` (PASS), grep-/Zeilenverifikation aller Zitate |
| Nicht ausgeführt | MSVC-Build, Retail-Join, Sync-Läufe, Hetzner-Messungen – alles **OFFEN** und als solches gekennzeichnet |
| Nächster Schritt bei Annahme | Phase E.1 als eigener Branch/Kandidat mit Patch `0010` und RED→GREEN-Offline-Tests |
