# Bot-KI: Fähigkeitsstufen, Persönlichkeiten, Wahrnehmung und menschliches Zielen

> **Status:** Code + Offline-Tests **fertig und bestanden**; **kein** MSVC-Build, **kein** natives Retail-1.07-Gate, **keine** Hetzner-Laufzeit in diesem Beitrag. Was unten als IMPLEMENTIERT/GETESTET markiert ist, bezieht sich ausschließlich auf enginefreien Code und einen Stub-Smoke-Test des Integration-Blocks. Es ist **nicht** als „im Server aktiv“ zu lesen.
>
> Basiscommit: `30a674775934f4298b338219b37137f8f060f0f8` (`main`), Branch `arena/fc36ae4f-serioussam-tse-bot-servermods`.
> Berichtsdatum: 2026-10-20.

## Kennzeichnung

| Kürzel | Bedeutung |
|---|---|
| **VERIFIZIERT** | am konkreten Quellstand / per Kommando geprüft, Beleg im Text |
| **IMPLEMENTIERT** | Code liegt vor, kompiliert aber nicht zwingend im Ziel-Build |
| **GETESTET** | automatisiert ausgeführt, Ergebnis unten |
| **VORSCHLAG** | begründete Empfehlung, nicht umgesetzt |
| **OFFEN** | nicht geprüft / nicht erreichbar |

---

## A. Bestandsaufnahme

### A.1 Zugriffsumfang

**VERIFIZIERT.** Vollständiger Lese-/Schreibzugriff auf den Git-Checkout dieses Repositories (`git log`, `git status` sauber, Remote `Escoba2024/SeriousSam-TSE-Bot-Servermods-`). Zusätzlich wurde `https://github.com/DreamyCecil/CecilBotMod` als flacher Klon gelesen (öffentlicher Read-only-Zugriff, 5,3 MB, Quellstand `main`).

**Nicht vorhanden und hier ausdrücklich nicht behauptet:** SSH/Hetzner, laufender Dedicated Server, Retail-1.07-Binaries, Windows-/MSVC-Toolchain, SE1-ModSDK, Ghidra-Session. Jede Aussage über Laufzeit, Sync, CRC oder echte CPU-Last ist deshalb **OFFEN** und als solche markiert.

### A.2 Tatsächlich aktiver KI-Pfad

**VERIFIZIERT** (`poc/release/gamemp/Game.cpp`, `BotDriver.cpp`):

```
CGame::GameHandleTimer()            Game.cpp:754  -> BotDriver_HandleTimer(this)
  pro Tick (20 Hz), pro lokalem Slot 0..3:
    CPlayerAction pa; pa.Clear()
    pa.pa_vTranslation(3) = -moveFactor
    pa_aRotation = bs_aHeading - m_aLocalRotation
    ctl_ComposeActionPacket(...)          // vanilla Skalierung
    pa.pa_ulButtons |= BOT_PLACT_FIRE ...
    CPlayerSource::SetAction(pa)          // regulaerer Netzwerkpfad
```

Damit ist die Architektur bestätigt: **Bots sind normale Netzwerkspieler**, es gibt keinen Server-seitigen Bot-Entity und keine Sonderbehandlung im Dedicated Server. Jeder Bot erzeugt ausschließlich `CPlayerAction`s. Keine HP-, Schaden-, Tempo- oder Trefferbox-Eingriffe.

### A.3 Was die derzeitige Entscheidungslogik tatsächlich tut

**VERIFIZIERT** (`bot_combat.h`, Wortlaut geprüft):

| Aspekt | Ist-Zustand | Grenze |
|---|---|---|
| Zielwahl | `SelectTarget`: nächster lebender, sichtbarer, nicht-lokaler Spieler | kein Gedächtnis, kein Verfolgen nach Sichtverlust |
| Sicht | `CCastRay` je Kandidat je Tick (`TT_COLLISIONBOX`) | alle lebenden Spieler werden jeden Tick geraycastet (bis 15) |
| Drehen | `TestTurnDelta` mit `limit = abs(bot_fYawSpeed)*fTick` | **ein globaler Wert 45 °/s für alle Bots im Prozess** |
| Feuern | `aligned && !(melee && dist>2)`; „aligned“ = Restfehler < **3,0°** | identisch für alle Bots, kein Reaktionsverzug |
| Waffe | `SelectWeapon`: feste Bänder `<10 m` / `≤30 m` / `>30 m` | keine Ammo-/Distanz-Utility, kein Hysterese-Wert |
| Bewegung | nur vorwärts (`moveFactor` 0..1) + `ObstacleRecovery` | kein Distanzmanagement, kein Rückzug, kein Strafe |

**Wichtig:** Es gibt derzeit **keine** Fähigkeitsstufen und **keine** Persönlichkeiten. Unterschiede zwischen Bots entstehen nur durch die zufällige Startposition und die Phase des Feuerpulses.

### A.4 Toter Code im Integrationspfad

**VERIFIZIERT** (`grep` über `poc/release/gamemp/*.cpp *.h`):

| Symbol | Vorkommen | Status |
|---|---|---|
| `WaypointGraph` | nur `botcore_ai.h` | **ungenutzt** — keine Navigation im Build |
| `PresenceSchedule` | nur `botcore_ai.h` | **ungenutzt** |
| `PopulationStep` / `DesiredBots` | nur `botcore_ai.h` | **ungenutzt** (Population macht `poc/scripts/`) |
| `VariantFor` | nur `botcore_ai.h` | **ungenutzt** |
| `SelectTarget` / `SelectWeapon` | über `DecideCombat` | aktiv (Legacy-Pfad) |
| `StuckDetector` | über `ObstacleRecovery` | aktiv |

Konsequenz für den Auftrag: „vorhandene Navigationsdaten nutzen“ ist derzeit nicht möglich — es gibt im Build **keine** Navigationsdaten, nur eine reaktive Hinderniserholung. Das ist in Abschnitt H als offener Punkt geführt.

---

## B. CecilBotMod — Eignung und Übernahmeentscheidung

### B.1 Lizenz und Version

**VERIFIZIERT:** GPL-2.0 (LICENSE im Klon), Ziel „classic Serious Sam: The Second Encounter v1.07“, Basis SE1-ModSDK. README nennt ausdrücklich v1.07 — dieselbe Zielversion wie unser Projekt.

### B.2 Architektur — der entscheidende Punkt

**VERIFIZIERT** an folgenden Stellen:

| Befund | Datei / Zeile |
|---|---|
| Bots sind **Server-Entities** `CPlayerBot : CPlayer` mit `BotApplyAction`-Override | `Sources/Bots/Classes/PlayerBot.es:38,117` |
| Binärpatches auf `CMessageDispatcher::ReceiveFromClient*` und `CSessionState::ProcessGameStreamBlock` | `Sources/Bots/NetworkPatch/ServerIntegration.cpp:57-80` |
| Eigenes Netzwerkpaket `MSG_CECIL_SANDBOX = 49` | `Sources/Bots/CustomPackets.h:23` |
| Eigener Stream-Block wird **an alle Sessions** angehängt | `ServerIntegration.cpp:36-55` (`CECIL_AddBlockToAllSessions`) |
| Kartenabhängige Navmeshes `Cecil/Navmeshes/<Map>_<CRC>.nav` | Repo-Verzeichnis, 9 Dateien |

Daraus folgt zwingend: CecilBotMod **ersetzt EntitiesMP/GameMP des Servers** und verändert den Netzwerkstrom. Unsere verbindliche Vorgabe lautet „Dedicated Server, Engine, Entities und menschliche TSE-1.07-Clients bleiben unverändert“ (README, Abschnitt 1). Eine Übernahme als Ganzes ist damit **unvereinbar** — unabhängig davon, ob unveränderte Clients technisch beitreten könnten. Diese Frage ist mit dem vorliegenden Code **nicht** entscheidbar und wird hier nicht behauptet.

Zusätzlich wäre eine Navmesh pro Karte nötig (`Cecil/Navmeshes`), was ohne Serverzugriff und ohne Map-Daten nicht bereitstellbar ist.

### B.3 Übernahmetabelle

Kategorien: **1** = direkt übernehmbar, **2** = nach Anpassung verwendbar, **3** = nur algorithmisches Vorbild, **4** = mit unseren Vorgaben unvereinbar.

| Quellfunktion / Datei | Zweck | Abhängigkeiten | Strategie | Integrationsstelle im Projekt | Risiko |
|---|---|---|---|---|---|
| `SBotSettings` + `PresetDummy/Easy/Normal/Hard` (`Logic/BotSettings.cpp:19-176`) | 4 Schwierigkeitsstufen als Parametersatz | keine (reine Daten) | **2** — Struktur übernommen, auf 5 Stufen und getrennte Persönlichkeit erweitert | `poc/botcore/bot_profile.h` | niedrig |
| `props.m_vAccuracy` + 0,5-s-Refresh (`Logic/BotMovement.cpp:289-307`) | zeitlich korrelierter Zielfehler | `_pTimer` | **3** — als OU-Prozess mit Korrelationszeit neu implementiert (stetiger, begründbarer Fehler) | `bot_aim.h::AimController` | niedrig |
| Rotationstempo `Clamp(dist/fRotSpeedDist, min, max)`, Limit `fRotSpeedLimit` (`BotMovement.cpp:311-330`) | distanzabhängige Drehgeschwindigkeit | `en_plViewpoint` | **3** — ersetzt durch Rate-/Beschleunigungsmodell mit Bremswegplanung | `bot_aim.h` | niedrig |
| Vorhalten `fPrediction + FRnd()*fPredictRnd`, skaliert mit Waffenkgenauigkeit (`BotMovement.cpp:272-275`) | Lead-Kompensation | Zielgeschwindigkeit | **2** — gleiche Idee, deterministisch und mit Profilkompetenz skaliert | `bot_human.h::Step` | niedrig |
| `ClosestEnemy` mit Prioritäten + `fTargetCD` (`BotFunctions.cpp:224-320`, `BotStructure.cpp:339-352`) | Zielwahl mit Cooldown | Welt-Entities | **2** — Zielbindung/Hysterese übernommen, Bewertung auf replizierte Spieler beschränkt | `bot_human.h::ChooseTarget` | niedrig |
| Waffenwahl `damage × accuracy-mul` über Distanzband (`BotStructure.cpp:272-320`) | situationsgerechte Waffe | `CPlayerWeapons` | **2** — Utility-Score + Mindesthaltedauer; Explosiv-Selbstschaden als Strafterm | `bot_loadout.h` | mittel (Werte sind Hypothesen) |
| `CastBotRay` mit `BPOF_PASSABLE` (`BotFunctions.cpp:164-182`) | Sichtlinie | `CCastRay` | **2** — unsere bestehende `BotCombatVisible` bleibt unverändert | `BotDriver.cpp` (unverändert) | niedrig |
| `CheckPit` / `AvoidPits` (`BotMovement.cpp:341-397`) | Abgrundvermeidung | `WouldFallInNextPosition` | **3** — Vorbild für einen späteren Navigationsschritt | offen | mittel |
| Navmesh + `CBotPathPoint` (`PathFinding/*.cpp`, 1.050 Zeilen) | globale Wegeplanung | `NavMeshGenerator`, kartenabhängige `.nav`-Daten | **4** in diesem Schritt — keine Navigationsdaten im Build, keine `.nav`-Quellen | offen (Abschnitt H) | hoch |
| `CPlayerBot`-Entity + `BotApplyAction` (`PlayerBot.es`) | serverseitige Bots | modifizierte EntitiesMP.dll | **4** — verletzt „Server/Entities unverändert“ | — | — |
| `CCecilStreamBlock`, `MSG_CECIL_SANDBOX` (`NetworkPatch/*`) | eigener Netzwerkstrom | gepatchte Engine | **4** — verletzt den unveränderten Netzwerkpfad | — | — |
| `SBotThoughts` (`Logic/BotThoughts.h`) | Textzeilen/Logs | `CTString` | **4** — Chat-/Denktexte werden nicht übernommen | — | — |

**Ergebnis:** Kein CecilBot-Bestandteil wird als Code kopiert. Übernommen werden ausschließlich **Ideen und Parameterordnungen**; die Umsetzung ist neu und enginefrei. Damit bleibt `THIRD-PARTY-NOTICES.md` unverändert gültig (keine zusätzliche GPL-Fremdquelle im Baum).

---

## C. Architektur und Integrationspunkte

### C.1 Schichten (IMPLEMENTIERT, enginefrei)

```
poc/botcore/
  bot_profile.h      Fähigkeitsstufen (5) + Persönlichkeiten (6) + Validierung + Roster
  bot_perception.h   Sichtfeld-Gate, Sichtlinien-Bestaetigung, Zielgedaechtnis, Alarm
  bot_aim.h          Reaktions-/Rate-/Beschleunigungsmodell, korrelierter Fehler, Abzug
  bot_loadout.h      Waffen-Utility + Hysterese (darf bot_weapon_input.h weiter nutzen)
  bot_human.h        Orchestrierung: BeginTick -> PlanLosQueries -> Step -> BotCommand
```

Der Agent gibt **nur Absicht** aus (`BotCommand`: Delta-Winkel, forward/strafe, Feuerbit, Waffennummer). Die Umwandlung in `CPlayerAction`, `ctl_ComposeActionPacket`, `SetAction` und der gesamte Netzwerkpfad bleiben **unverändert**.

### C.2 Datenfluss pro Tick, pro Bot

```
1. BotCombatEye(player)                      -> Position + absolute Blickwinkel
2. WorldView {tick, pose, health, ammo-gefilterte Waffen}
3. Kandidaten 0..15 (lebend, nicht self, optional ohne lokale Geschwister)
4. policy.BeginTick(world)
5. policy.PlanLosQueries(kandidaten)         -> bool needs[16]   (FOV + Distanz + Budget)
6. nur fuer needs[i]:  BotCombatVisible()    -> bool los[16]
7. policy.Step(...)                          -> BotCommand
8. decision.* = command.*;  humanFire = command.fire
9. bestehender Codepfad: combatWeapon -> CombatWeaponInput.Poll -> pa_ulButtons
10. ppls->SetAction(pa)                      (unveraendert)
```

Schritt 5 ist die CPU-Bremse: Kandidaten außerhalb des Sichtkegels und außerhalb der Sichtweite erhalten **keinen** Ray. Zusätzlich ist die Zahl der Rays pro Tick durch `max_los_per_tick` (4–8 je Stufe) hart begrenzt; bereits verfolgte Ziele haben Vorrang.

### C.3 Synchronisationsschutz

- **Keine** neue Zufallslogik in Engine-, Welt- oder Simulationsberechnungen. Zufall existiert ausschließlich in der clientseitigen Entscheidung, genau wie der bisherige Feuerpuls; übertragen wird nur die resultierende `CPlayerAction`.
- Jeder Bot hat eine **eigene** RNG-Instanz, abgeleitet aus `seed ^ slot ^ tier ^ persona` (`DeriveSeed`). Kein gemeinsamer Zustand zwischen Bots oder Prozessen.
- Zeitbasis ist der 20-Hz-Tick (`WorldView.tick`), nicht die Wanduhr. Profiling ist davon getrennt (eigenes Benchmark-Binary).
- Zustand ist pro Slot getrennt (`BotHumanPolicy(iLP)`); ein Mapwechsel/Rejoin ruft `Reset()` über den bestehenden Attach-Pfad.

---

## D. Profilmatrix

### D.1 Fähigkeitsstufen (5) — Kalibrierungshypothesen, keine gemessenen Menschenwerte

Alle Einheiten: s, °, °/s, °/s², m.

| Parameter | Anfänger 1 | Gelegenheit 2 | Durchschnitt 3 | Fortgeschritten 4 | Sehr gut 5 |
|---|---|---|---|---|---|
| `reaction_s` (Sicht bis nutzbar) | 0,55 | 0,42 | 0,30 | 0,22 | 0,15 |
| `memory_s` (Zielgedächtnis) | 1,2 | 1,6 | 2,0 | 2,5 | 3,0 |
| `fov_half_deg` | 55 | 62 | 68 | 74 | 80 |
| `sight_range_m` | 60 | 70 | 80 | 90 | 100 |
| `max_los_per_tick` | 4 | 5 | 6 | 7 | 8 |
| `turn_rate_deg_s` | 110 | 150 | 200 | 270 | 340 |
| `turn_accel_deg_s2` | 320 | 450 | 650 | 900 | 1300 |
| `aim_sigma_deg` | 4,50 | 3,20 | 2,20 | 1,50 | 1,00 |
| `aim_corr_s` (Korrelationszeit) | 0,55 | 0,45 | 0,38 | 0,30 | 0,24 |
| `overshoot` (0..1) | 0,55 | 0,45 | 0,34 | 0,24 | 0,16 |
| `fire_tol_deg` | 5,0 | 4,0 | 3,0 | 2,2 | 1,5 |
| `settle_s` | 0,35 | 0,28 | 0,22 | 0,16 | 0,10 |
| `prediction_gain` (0..1) | 0,05 | 0,20 | 0,45 | 0,70 | 0,90 |
| `weapon_dwell_s` | 2,5 | 2,0 | 1,6 | 1,2 | 0,9 |
| `switch_margin` | 1,45 | 1,35 | 1,28 | 1,22 | 1,18 |
| `preferred_range_m` | 7 | 9 | 12 | 16 | 22 |
| `retreat_health` (0..1) | 0,55 | 0,50 | 0,42 | 0,35 | 0,28 |
| `search_rate_deg_s` | 40 | 45 | 52 | 60 | 70 |

Monotonie in **allen** mechanischen Dimensionen ist per Test erzwungen (`TestSkillMonotonicity`).

### D.2 Persönlichkeiten (6) — ohne jeden Wahrnehmungs-/Zielparameter

| Persönlichkeit | aggression | range_bias_m | strafe_bias | caution | range_preference | mood_period_s / swing |
|---|---|---|---|---|---|---|
| Aggressor | 0,90 | −6 | 0,40 | 0,15 | −0,55 | 0 / 0 |
| Überlebenskünstler | 0,25 | +4 | 0,70 | 0,90 | +0,35 | 0 / 0 |
| Duellant | 0,60 | 0 | 0,95 | 0,40 | 0,00 | 0 / 0 |
| Kartenkontrolle | 0,45 | +2 | 0,60 | 0,60 | +0,25 | 0 / 0 |
| Distanzschütze | 0,20 | +12 | 0,50 | 0,50 | +0,85 | 0 / 0 |
| Wechselhaft | 0,50 | 0 | 0,55 | 0,50 | +0,10 | 75 / 0,45 |

Die Orthogonalität ist **strukturell** garantiert (`PersonalityParams` enthält kein Skill-Feld) und per Test geprüft: `SkillUnaffectedByPersonality(tier, a, b)` über alle 5×15 Kombinationen. Ein Anfänger darf aggressiv sein, ein Experte darf dauerhaft auf Distanz spielen — die Mechanik bleibt identisch.

### D.3 Acht Beispielbots (Standardverteilung, konfigurierbar)

| # | Name | Stufe | Persönlichkeit | Charakter im Spiel |
|---|---|---|---|---|
| 0 | `BOT-Rookie-Rush` | 1 Anfänger | Aggressor | läuft drauflos, feuert zu früh, trifft selten |
| 1 | `BOT-Rookie-Guard` | 1 Anfänger | Überlebenskünstler | bleibt hinten, reagiert spät, weicht zurück |
| 2 | `BOT-Casual-Flaky` | 2 Gelegenheit | Wechselhaft | 75-s-Stimmungswechsel zwischen Vorrücken und Verstecken |
| 3 | `BOT-Casual-Holder` | 2 Gelegenheit | Kartenkontrolle | hält Sichtlinien, mittlere Distanz |
| 4 | `BOT-Average-Duelist` | 3 Durchschnitt | Duellant | strafft konstant, mittlere Distanz |
| 5 | `BOT-Average-Rifle` | 3 Durchschnitt | Distanzschütze | sucht Distanz, bevorzugt Reichweite |
| 6 | `BOT-Veteran-Push` | 4 Fortgeschritten | Aggressor | drückt schnell, gute Waffenwahl |
| 7 | `BOT-Expert-Rifle` | 5 Sehr gut | Distanzschütze | reagiert in 3 Ticks, hält 22 m, präzise |

Verteilung: 2/2/2/1/1 über die Stufen, 6 unterschiedliche Persönlichkeiten (Aggressor doppelt, auf Stufe 1 und 4). Zwei Clients à vier Slots: Client A `bot_iRosterOffset=0`, Client B `=4`. Administrative Erkennbarkeit: Präfix `BOT-`, zusätzlich `label = "<name> t<tier>p<persona>"` in jedem Log. Keine Nachahmung realer Spieleridentitäten, keine Chattexte.

---

## E. Codeänderungen

### E.1 Neue Dateien

| Datei | Zeilen | Inhalt |
|---|---:|---|
| `poc/botcore/bot_profile.h` | 430 | Stufen, Persönlichkeiten, Validierung, Roster, Seed-Ableitung |
| `poc/botcore/bot_perception.h` | 255 | FOV-Gate, Tracks, Gedächtnisablauf, Alarm |
| `poc/botcore/bot_aim.h` | 279 | Zielcontroller |
| `poc/botcore/bot_loadout.h` | 219 | Waffen-Utility + Hysterese |
| `poc/botcore/bot_human.h` | 387 | Orchestrierung |
| `poc/botcore/test_bot_human_ai.cpp` | 996 | 555 Offline-Checks |
| `poc/botcore/test_botdriver_block.cpp` | 181 | Stub-Smoke des Integration-Blocks |
| `poc/botcore/extract_block.py` | 37 | zieht den Block aus einer gepatchten `BotDriver.cpp` |
| `poc/botcore/verify_patch.py` | 63 | beweist, dass Patch 0008 sauber anwendet und die Integrationskopie reproduziert |
| `poc/botcore/bench_bot_human.cpp` | 89 | Entscheidungs-Mikrobenchmark |
| `poc/patch/0008-gamemp-human-bot-ai.patch` | 269 | **+181 / −3** in `BotDriver.cpp` |
| `poc/ai-integration/gamemp/BotDriver.cpp` | — | gepatchte Fassung zur Review (nicht die freigegebene Quelle) |
| `poc/scripts/Phase1HumanAI.ini` | — | Beispielkonfiguration |

`poc/release/gamemp/**` wurde **nicht** angefasst: diese 13 Dateien sind bytegenau an den qualifizierten Kandidaten `61DC…` gebunden (`tools/Verify-SourceProvenance.py`). Der Patch liegt deshalb — wie 0001–0007 — in `poc/patch/`.

### E.2 Was der Patch ändert

1. `#include "bot_human.h"`.
2. Acht neue Konsolensymbole: `bot_bHumanAI` (Standard **0**), `bot_iRosterOffset`, `bot_iProfile0..3`, `bot_iProfileSeed`, `bot_fStrafeScale` (Standard **0**).
3. Pro Slot: `BotHumanPolicy(iLP)` und `BotHumanProfile(iLP)` als funktionslokale Statics; `BotHumanAttach(iLP)` im bestehenden Rejoin-/Mapwechsel-Reset.
4. Neuer Zweig `if (bot_bHumanAI) { … }` **vor** dem bisherigen `DecideCombat`-Block. Er füllt dieselbe `CombatDecision`-Struktur — der nachfolgende Anwendungscode (Waffenwahl-Protokoll, Heading-Übernahme, `combatHold`) bleibt unverändert.
5. Feuerkomposition: bei aktiver Human-AI `bFire = (humanFire && testAimReady) || respawnPulse`; der Respawn-Puls ist jetzt ein 4-Tick-Press/Release, damit eine echte Flanke entsteht.
6. Suchdrehung ohne Ziel nutzt die Profilrate statt `bot_fYawSpeed`.
7. Optionaler Lateralanteil `pa_vTranslation(1) = strafe * bot_fStrafeScale`, **standardmäßig 0** (nicht nativ verifiziert).

**Standardverhalten ohne INI-Änderung ist bitgleich zum qualifizierten Kandidaten**: `bot_bHumanAI=0` schaltet den neuen Zweig vollständig ab.

### E.3 Anwenden

```bash
cd <checkout>
git apply --check poc/patch/0008-gamemp-human-bot-ai.patch   # muss still bleiben
git apply         poc/patch/0008-gamemp-human-bot-ai.patch
cp poc/botcore/bot_profile.h   poc/release/gamemp/
cp poc/botcore/bot_perception.h poc/release/gamemp/
cp poc/botcore/bot_aim.h        poc/release/gamemp/
cp poc/botcore/bot_loadout.h    poc/release/gamemp/
cp poc/botcore/bot_human.h      poc/release/gamemp/
# dann wie bisher mit SE1-ModSDK aa7869c… / VS2022 v143 / WinSDK 10.0.19041.0 bauen
```

`git apply` ist **ausgeführt und bestanden** (siehe F.1); der anschließende MSVC-Build ist **OFFEN**.

---

## F. Tests

### F.1 Ausgeführte Kommandos und beobachtete Ergebnisse

Umgebung: Linux-Sandbox, g++ 13, `-std=c++17 -O2 -Wall -Wextra`, keine Warnungen in den Modulen.

```bash
cd poc/botcore && make test
```
```
ALL CHECKS PASSED                 (test_botcore,        bestehend)
ALL AI CHECKS PASSED              (test_botcore_ai,     bestehend)
BOT RECONNECT POLICY PASS         (test_bot_reconnect,  bestehend)
COMBAT POLICY PASS (0 failures)   (test_bot_combat,     bestehend)
NATIVE WEAPON INPUT PASS          (test_bot_weapon_input, bestehend)
OBSTACLE RECOVERY PASS            (test_bot_navigation, bestehend)
bot human-AI policy tests
  overshoot: sloppy=4.28 deg precise=0.38 deg
  profile differentiation: first shot t1=1.90s t5=0.45s,
    fire ticks 1..5 = 51/85/122/130/129, mean aim error t1=9.64 t5=1.46 deg
HUMAN AI PASS: 555 checks, 0 failures
```

```bash
python3 poc/botcore/verify_patch.py
```
```
PATCH VERIFY PASS: 0008 applies cleanly and matches the integration copy
```

```bash
cd poc/botcore && make smoke          # setzt die gepatchte BotDriver.cpp voraus
```
```
integration block: target=1 first-acquire-tick=3 weapon=12
                   move=-0.60 strafe=0.30 fires=16/40
INTEGRATION BLOCK PASS
```

```bash
cd poc/botcore && make bench
```
```
BOT-Rookie-Rush      tier=1 persona=aggressor   0.41 us/tick  4.0 rays/tick
…
BOT-Expert-Rifle     tier=5 persona=marksman    0.48 us/tick  4.0 rays/tick
BENCH PASS
```

Zusätzlich geprüft: die neuen Header kompilieren unter `-std=c++11`, `c++14` und `c++17` (MSVC-Kompatibilität wahrscheinlich, aber **OFFEN**, solange nicht mit MSVC gebaut).

### F.2 Abnahmekriterien aus dem Auftrag → Test

| Kriterium (§11) | Test | Ergebnis |
|---|---|---|
| Profilvalidierung und Parametergrenzen | `TestProfiles`, `TestSkillMonotonicity` | **GETESTET** |
| reproduzierbare Entscheidungen bei festem Seed und gleicher Eingabefolge | `TestReproducibility`, `TestDeterministicSeeds` | **GETESTET** |
| Sichtkontaktverlust, Gedächtnisablauf, Reaktionsverzögerung | `TestReactionDelay`, `TestMemoryExpiryAndNoWallTracking`, `TestAlertOnDamage` | **GETESTET** |
| maximale Drehgeschwindigkeit, kein Sofort-Einrasten | `TestNoInstantLockAndTurnLimit`, `TestTurnLimitRespectedAtLargeAngles` | **GETESTET** |
| Ziel-/Waffenwechsel mit Hysterese | `TestTargetSwitchHysteresis`, `TestWeaponHysteresis` | **GETESTET** |
| situationsgerechte Waffenentscheidung | `TestWeaponUtility`, `TestWeaponPreferenceByPersonality` | **GETESTET** |
| kein Feuern ohne frische Sichtlinie | `TestNoFireWithoutLineOfSight` | **GETESTET** |
| Fehlerkorrelation (kein Frame-Zittern) | `TestCorrelatedErrorNotPerFrameJitter` (mittlere Bias-Änderung < 1,5° bei σ = 4,5°) | **GETESTET** |
| Überschwingen hat mechanische Ursache | `TestOvershootHasMechanicalCause` (4,28° vs. 0,38°) | **GETESTET** |
| Persönlichkeit verändert Mechanik nicht | `TestSkillPersonalityOrthogonality`, `TestPersonalityDoesNotBreakSkillOrder` | **GETESTET** |
| gemischte Profile unterscheiden sich messbar | `TestProfilesActuallyDiffer`, `TestMixedRosterOverTime` | **GETESTET** |
| Ray-Budget / CPU-Gate | `TestRayBudget`, `TestRayBudgetProtectsCurrentTarget` | **GETESTET** |
| Feststeckerkennung und Wiederherstellung | bestehender `test_bot_navigation` | **GETESTET (unverändert)** |
| Retail-Client tritt bei, 8 Bots, 2 Maps, 60 min | — | **OFFEN** (kein Runtime-Zugriff) |
| menschliche Spielprobe | — | **OFFEN** |

### F.3 Grenzen dieser Tests

Die Offline-Tests beweisen **Entscheidungssemantik**, nicht Engine-Verhalten. Insbesondere sind nicht abgedeckt: reale `ctl_ComposeActionPacket`-Skalierung, Winkelnormalisierung über `m_aLastRotation`, Netzwerk-Jitter, Prädiktion fremder Spieler, tatsächliche Trefferwahrscheinlichkeit. Der Stub-Smoke deckt nur Syntax/Typen/Verdrahtung des Integrationsblocks ab.

---

## G. CPU- und Runtime-Bewertung

**Getrennt gemessen (GETESTET, eng umrissen):** Der enginefreie Entscheidungsanteil kostet **0,38–0,48 µs pro Bot und Tick** (8 Kandidaten, Xeon 2,60 GHz, `-O2`). Bei 20 Hz und vier Bots sind das ≈ 32–38 µs/s, also < 0,01 % eines Kerns. **Raycasts, Entity-Lookups, Action-Komposition sind darin nicht enthalten.**

**Ray-Budget (GETESTET):** Das Sichtfeld-Gate senkt die Zahl der Sichtlinienprüfungen. Mit 8 Kandidaten (4 im Kegel) werden 4 statt 8 Strahlen angefordert; mit 16 Kandidaten im Kegel greift die harte Obergrenze (4 bei Stufe 1, 8 bei Stufe 5). Der bisherige Pfad prüft **jeden** lebenden Spieler jeden Tick.

**Nicht gemessen (OFFEN):** Gesamt-CPU eines Bot-Clients, Einfluss auf die parallele Render-/Headless-Optimierung, Serverlast, RAM. Die vorhandene Acht-Bot-Baseline (`docs/reports/2026-10-21-hetzner-eight-bot-cpu-headless-baseline.md`) zeigt 60–87 % einer CPU pro Client bei 320×240 unter llvmpipe; der dominante Posten ist dort Rendering/Wine, nicht die Entscheidungslogik. Eine belastbare Aussage „Human-AI kostet X %“ ist ohne Laufzeitmessung **nicht** möglich.

**Erwartete Mehrkosten, begründet aber unbelegt:** Der neue Pfad ersetzt 15 ungefilterte Raycasts durch 4–8 gefilterte und fügt ~0,5 µs Entscheidungszeit hinzu. Die Sichtlinienprüfungen dürften damit **sinken**; das ist eine Hypothese, die im isolierten A/B-Lauf (gleiche Map, gleiche Botzahl, `pidstat`) zu prüfen ist.

---

## H. Handoff

### H.1 Basis und Umfang

| | |
|---|---|
| Basiscommit | `30a674775934f4298b338219b37137f8f060f0f8` |
| Branch | `arena/fc36ae4f-serioussam-tse-bot-servermods` |
| geänderte/neue Dateien | `poc/botcore/{bot_profile,bot_perception,bot_aim,bot_loadout,bot_human}.h`, `poc/botcore/{test_bot_human_ai.cpp,test_botdriver_block.cpp,bench_bot_human.cpp,extract_block.py,verify_patch.py,Makefile,.gitignore}`, `poc/patch/0008-gamemp-human-bot-ai.patch`, `poc/ai-integration/gamemp/BotDriver.cpp`, `poc/scripts/Phase1HumanAI.ini`, dieser Bericht |
| unverändert | `poc/release/gamemp/**` (13 bytegenau gebundene Dateien), `Game.cpp`, `Game.vcxproj` |

### H.2 Nachweise

| Nachweis | Kommando | Status |
|---|---|---|
| 555 Offline-Checks | `make test` | **GETESTET — PASS** |
| Patchanwendung + Reproduktion | `python3 verify_patch.py` | **GETESTET — PASS** |
| Integration-Block kompiliert/läuft | `make smoke` | **GETESTET — PASS** |
| Entscheidungskosten | `make bench` | **GETESTET — PASS** |
| C++11/14/17-Kompilierbarkeit | `g++ -std=c++NN -c` | **GETESTET — PASS** |
| MSVC-Build | — | **OFFEN** |
| Retail-1.07-Join, Sync, 60 min | — | **OFFEN** |

### H.3 Restarbeiten, in Reihenfolge

1. **Windows-Build** mit dem gepatchten `BotDriver.cpp` + den fünf Headern (VS2022/v143, SDK-Pin). Erwartete Fehlerquellen: `CPlayerWeapons`-Feldnamen, `en_vCurrentTranslationAbsolute`-Sichtbarkeit, `bool`-Nutzung im Engine-Header-Kontext.
2. **Ein-Bot-Smoke auf einer Testmap**, `bot_bHumanAI=1`, `bot_iLogEvery=20`: prüfen, dass `[BotHuman]`-Zeilen Target/Weapon/Fire plausibel zeigen und `[BotCombatWeapon]` die Waffe tatsächlich wechselt.
3. **Vier-Bot-A/B** gleicher Client-Build, `bot_bHumanAI` 0 vs. 1, gleiche Map, `pidstat` 10 min: Ray-/CPU-Differenz und Sync-Verhalten.
4. **Acht-Bot-Mischserver** (2 Clients, Offset 0/4), zwei Maps + Mapwechsel, 60 min, Vanilla-Observer-Join.
5. **Erst danach** Bewegung ausbauen: `bot_fStrafeScale` aktivieren, Rückzug/Deckung, Pickup-Bewertung, und — als eigener größerer Schritt — Navigation (siehe H.4).

### H.4 Offene Integrationsrisiken

| Risiko | Wirkung | Gegenmaßnahme |
|---|---|---|
| `bot_human.h` (13,5 KB) plus die vier profil-/wahrnehmungs-/ziel-/lastout-Header (~46 KB zusammen) sind Template-freier Code in Engine-Header-Pfaden | Kompilierzeit, aber kein Laufzeitrisiko | bleibt header-only, keine Allokation |
| `CPlayer::en_vCurrentTranslationAbsolute` bei Remote-Spielern | Lead-Kompensation evtl. ungenau | `prediction_gain ≤ 0,9`, Vorhalten ist optional; bei Problemen auf 0 setzen |
| Feuern während laufendem Waffenwechsel | ein Tick ohne Schuss | bereits durch `testAimReady`-UND abgefangen |
| Neuartiges Rotationsprofil (bis 17°/Tick bei Stufe 5) | theoretisch Sync-relevant | im A/B-Lauf explizit auf `SYNCBAD` prüfen; Rückfall auf `bot_fYawSpeed` durch `bot_bHumanAI=0` jederzeit möglich |
| Keine Navigation im Build | Bots bleiben an Wänden hängen, nur reaktiv gelöst | eigener Schritt; `WaypointGraph` liegt ungenutzt bereit |
| Persönlichkeitsparameter nur theoretisch kalibriert | Profile könnten sich zu ähnlich sein | Telemetrie `[BotHuman]` liefert Distanz, Waffe, Fehler, Wechsel pro Bot |

### H.5 Exakt nächster Schritt

Build des gepatchten Clients auf einem Windows-/Wine-System mit vorhandenem SDK und **ein** Bot auf `DM_LittleTrouble` (oder einer vorhandenen Testmap), `bot_iLogEvery=20`, 120 s, danach Auswertung der `[BotHuman]`-Zeilen: Erwartet werden pro Bot 2–5 Zielwechsel, Waffenwechsel nur mit `weapon_dwell_s`-Abstand, `rays` ≤ 8 und `fire=0` in Ticks ohne `vis=1`. Weicht das ab, ist der Fehler in der Schicht zu suchen, die die Abweichung erzeugt (Perception → `vis`, Aim → `err`/`fire`, Loadout → `weapon`).

---

## Anhang: Warum diese Fehler und keine anderen

| Fehlerursache | Umsetzung | Begründung |
|---|---|---|
| Reaktionszeit | `reaction_s` als Bedingung „ununterbrochen sichtbar“, nicht als Zufallsverzögerung | ein Mensch braucht Zeit, ein Ziel zu *erkennen*, nicht pro Schuss zu würfeln |
| Zielfehler | Ornstein-Uhlenbeck-Prozess mit Korrelationszeit 0,24–0,55 s | benachbarte Ticks sind korreliert; das Ergebnis ist Drift, kein Frame-Zittern |
| Überschwingen | Bremswegplanung mit *geplanter* Beschleunigung, tatsächliches Bremsen schwächer (`overshoot`) | physikalisch begründet: der Bot verschätzt sich in seiner eigenen Bremswirkung |
| Erster Schuss zu früh | `settle_s` + `fire_tol_deg` auf dem *wahrgenommenen* Fehler | der Spieler schießt, wenn das Fadenkreuz für ihn stimmt — nicht wenn es objektiv stimmt |
| Zielwechsel-Flackern | Zielbindung 1,35×, Wechsel nur bei 1,4× näherem Gegner, Mindesthaltezeit | Hysterese statt Neubewertung pro Tick |
| Wandverfolgung | Position wird beim Sichtverlust **eingefroren**, Geschwindigkeit genullt, Konfidenz läuft ab | keine Extrapolation durch Geometrie |
| „Was hat mich getroffen?“ | eigener Health-Verlust öffnet 0,35–0,55 s lang den Sichtkegel | das ist die einzige nicht-visuelle Information, die der Client wirklich hat |

Ausdrücklich **nicht** verwendet: Zufallstreffer als Schwierigkeitsregler, sofortiges Einrasten, positionsunabhängige Trefferwahrscheinlichkeit, serverseitiges Wissen, LLM-Aufrufe.
