# ssam.ai – Forschungs-Intake für Red-Station-Bot-KI (01.11.2026)

**Status:** REVIEWED / PLAN_ONLY / CODE_NOT_CHANGED / NATIVE_NOT_TESTED.  
**Eingang:** vom Eigentümer bereitgestellte Datei `deep research.txt`, drei externe KI-Forschungsberichte (Claude, Grok und dritte technische Analyse), 01.11.2026. Originaltext nicht ins Repository übernehmen.  
**Arbeitsziel:** brauchbare Vorschläge in **bestehende** M1/M2/M3-Arbeiten aufnehmen, Cecil-first/Vanilla 1.07 bewahren, **keine zweite Kampf-Policy** aufbauen.
**Quellabgleich:** GitHub `main` README + `poc/botcore/bot_human.h`/`bot_loadout.h`/`bot_aim.h`; Issue #93; PRs #39, #55, #74, #91, #95 und unabhängiges Audit/Handoff PR #96. Acht-Bot-RedStation-Originalclient-Gate nicht nachgewiesen. Lokale Änderungen aus PR #96-Kommentar sind Selbstbericht und noch nicht als Remote-Code geprüft.

## 1. Entscheidungen: Übernehmen, wiederverwenden, nicht übernehmen

| Thema | Bewertung gegen sichtbaren Quellstand | Integrationseigner / Referenz | Status |
|---|---|---|---|
| **Waffe suchen unmittelbar nach Respawn** statt ziellosem Kampf mit schwacher Ausrüstung | hoher Nutzen; im `bot_human.h` kein Pickup-Goal zu erkennen | **ein** übergeordneter Policy-Owner, mit NavV2 aus PR #91 und Item-Utility aus PR #55; Issue #93 | TODO |
| **Keine Leerlaufzeit**: ohne Gegner Item-/Strategiepunkt anlaufen, dann sicher weiterlaufen | konkrete Lücke: `HumanBotPolicy::Step` setzt im No-Target-Zweig `forward=0, strafe=0` und scannt | HumanBotPolicy + bestehende Hinderniserholung + reale Mapdaten; keine blind laufende Vorwärtssteuerung | TODO |
| **Echte RedStation-Navigation/Item-Quellen** | PR #39 hat Cecil `RedStation_5AF1A276.waypoints` (193 Punkte/879 gerichtete Kanten laut PR #96); PR #91 bislang Beispielgraph mit 12 Knoten | vorhandenen Parser/Graphen **wiederverwenden**, Kanten offline prüfen, im Retail begehen (T-03) | IN_PROGRESS, NATIVE_PENDING |
| **Waffenwahl mit Utility, Entfernung, Ammo, Eigenrisiko, Mindesthaltedauer** | `bot_loadout.h` enthält bereits entsprechende enginefreie Scoring-/Hysterese-Grundlagen; Tabellen sind **Kalibrierungshypothesen** | Bestehendes Modul **kalibrieren**, nicht neu implementieren; PR #82/#91 | PARTIAL, MEASUREMENT_PENDING |
| **Keine unproduktiven Colt-Fernschüsse**, noch weniger Schüsse auf großer Entfernung mit schwacher Treffchance | `ScoreWeapon` berücksichtigt Reichweite, aber konkrete Fire-Gates müssen nativ geprüft werden | Distanzband-basierte Feuerentscheidung, ammo/range abhängige Telemetrie; **nicht** starr alle Colt-Fernschüsse verbieten | TODO |
| **Starkes, aber variierendes Aim**, Vorhalten, schnellere Reaktion bei hohen Stufen | `bot_aim.h` hat bereits Rate/Acceleration/Korrelation/Trigger; `bot_human.h` hat einfachen `distance/proj_speed`-Vorhalt | vorhandene 5 Skill-Stufen + 6 Personas erhalten; echte Projektilgeschwindigkeiten messen, Interzept + ballistischer Fall erst nach Code-/Retail-Abgleich | PARTIAL |
| **Menschen priorisieren** bei ansonsten normaler Gefahrenbewertung | `ChooseTarget` benutzt hauptsächlich Distanz + Stickiness; sichere Klassifizierung über Namen allein **ungeeignet** | bestehendes Sidecar/Roster-Konzept prüfen, nur **verifizierte** Human-Klassifikation; Nahbedrohung vor Human-Bonus | TODO |
| **Strafe/Circle-Strafe/Zurückweichen/occasionally Jump** | `MoveIntent` besitzt Strafe-/Retreat-Ideen, aber Integrationsschalter war in qualifiziertem Build 0; Sprung-Action und Abgrundsicherheit unbewiesen | PR #96 T-07; seltene Sprünge nur an nachweislich sicheren Stellen, Nicht-Absturz-Gate | PARTIAL, NATIVE_PENDING |
| **Gegnergedächtnis nach LOS-Verlust** | `bot_perception.h` und `ChooseTarget` enthalten bereits Gedächtnis; kein Schuss ohne frische Sichtlinie | beibehalten, an Nav-Route als **letzte bekannte Position** koppeln | PARTIAL |
| **CecilBot-Verhaltensparität** | eigene Bot-Client-Architektur; Cecil-Server-Entities/Network-Stream inkompatibel | Issue #93, PR #39/#57; nur kompatible Algorithmen und Daten übernehmen, GPL-Attribution erhalten | IN_PROGRESS |
| **Messer sofort ziehen** | Behauptung der dritten Analyse: 10 m/s normal, 11 m/s Messer, 9 m/s schwere Waffe; **ohne reproduzierbaren Beleg** und widerspricht den zwei anderen Berichten | `bot_loadout.h` hat opt-in `knife_while_travelling=false`; vor Aktivierung exakt gleicher Laufversuch Messer/Colt/Rakete plus Switch-Kosten | MEASURE_REQUIRED |
| **8-Bot-Stabilität / SYNCBAD** | zusätzliche Laufzeit-Rays und unkontrollierte World-Locks gefährden M1 | PR #74 und #96 T-01/T-04/T-05; kein Ground-Lookahead blind aktivieren | BLOCKING_GATE |

## 2. Ausführungsplan (ein Haupt-Policy-Owner)

- [x] Drei Berichte vollständig sichten und falsche Gewissheiten kennzeichnen.
- [x] Sichtbaren Quellstand/aktuelle Issues/PRs vergleichen; keine zweite Navmesh- oder Aim-Implementierung starten.
- [ ] **A0 – Konvergenz (T-14 aus PR #96):** Human-AI, Cecil P1, Tactical AI und neuer M2/M3-Adapter zu **einem** dokumentierten Kampf-Policy-Owner zusammenführen. Lokale unveröffentlichte Worktrees zuerst lesen; keine fremden Commits überschreiben.
- [ ] **A1 – Enginefreie Baseline** auf Basis der neuesten, tatsächlich integrierten Quelle (nicht blind `main`): vor und nach Änderung fixe Szenarien für 5×6 Profile, Kill/Death/Respawn, Fern-Colt, Waffensuche, Bewegung ohne LOS und Human-Fokus; neue Unit-Tests.
- [ ] **A2 – RedStation-Mapdaten/Navigation:** PR #39 Converter+Datei wiederverwenden; Graph-Parser, Reachability, gefährliche/gesperrte Kanten offline testen; PR #91 NavV2 als Konsument nutzen, native Kanten-/Spawn-/Itemprüfung getrennt.
- [ ] **A3 – Respawn-Gear + Anti-Idle:** nach Respawn Loadout prüfen → erreichbare wertvolle Waffe nach Pfadzeit/Gefahr wählen → Bewegung und Stuck-Timeout. Bei unmittelbarer Bedrohung: Kampf-/Flucht-Override. Kein endloses Scan-Stehen.
- [ ] **A4 – Weapon/Combat:** `bot_loadout.h` kalibrieren statt ersetzen; Schießen nur bei sinnvoller Trefferchance/Distanz und frischer LOS; Projektil-Vorhalt mathematisch stabil (Sonderfall quadratischer Koeffizient nahe null), keine erfundenen Geschwindigkeiten; Aim/Skill-Profile beibehalten, Elite optional stärker.
- [ ] **A5 – Human-Fokus:** nur über **verifizierte** Slot/GUID/Sidecar-Identität, nicht aus Nickname-Präfix ableiten; Zielbonus parametrierbar, unmittelbare Bedrohung und Sichtlinie erhalten Vorrang; Tests für 0/1/mehrere Human-Spieler und unbekannte Identitäten.
- [ ] **A6 – Combat Movement:** bestehendes Strafe vorsichtig in isolierten A/B-Läufen aktivieren; gelegentliche Sprünge nur mit validierter Geometrie; 0 dauerhafte Blockaden als Ziel, nicht als Behauptung.
- [ ] **A7 – Messer-Test:** unveränderte Retail-Builds, gleiche Strecke/Spawn, je 10 wiederholte Messungen Messer/Colt/schwere Waffe, Zeit inklusive Waffenwechsel; nur bei belegtem Vorteil die Opt-in-Option einschalten.
- [ ] **A8 – Native Gates:** 1-Bot/4-Bot vor Acht-Bot-Gate; M1-SYNCBAD-Root-Cause/Host-RAM-Vorcondition klären; **ein** 8-Bot-RedStation-Lauf mit Originalclient, vollständig aktiven Bots, Hash/CRC und 0 SYNCBAD, keine Freigabe durch Kombination kürzerer Teiltests.
- [ ] **A9 – Rollout:** native Build-/DLL-Provenance, isolierter Smoke, Rollback-Probe und Nutzerfreigabe, **danach** Produktivänderungen. Keine Git-Merges oder Deployments aus diesem Plan.

## 3. Ausdrücklich verworfen bzw. zurückgestellt

1. Die behaupteten konkreten Messer-Laufgeschwindigkeiten und andere unzitierte 1.07-Waffen-/CPU-Zahlen **nicht** als Fakten übernehmen.
2. Kein CecilBot-Gesamtport samt gepatchten Server-Entities, Engine-Hooks oder eigenen Netzwerkpaketen; Vanilla-Dedicated/Originalclients müssen unverändert bleiben.
3. Kein neuer globaler GOAP-Planer als Pflicht-Architektur. Utility zur Zielwahl + kleiner FSM/Movement-Controller + vorberechneter Wegegraph ist geringer riskant und lässt sich nach Bedarf erweitern.
4. Kein `rand()` oder `IRnd()` im simulierten Session-Zustand. Bot-eigener PRNG, Laufzeit-Raycast-Budget, keine neuen synchronisierten Entities, keine Teleports.
5. Keine behauptete finale 8-Bot-RedStation-Stabilität ohne genau diese nativ belegte Abnahme. Offline-Tests ≠ Gameplay.
6. Keine ungeprüften Zielwerte wie „3,5 s bis zur Waffe“, „60 % Raketen-Treffer“ oder „K/D ≥1,5“ als verbindliche Gates: zuerst vergleichbare Baseline, dann messbare realistische Ziele.

## 4. Reproduzierbare Abnahmekriterien

| Messung | Abnahme |
|---|---|
| Ohne sichtbaren Gegner | gültiges Bewegungs-/Item-Ziel in jeder normalen Spielphase; endliche Recovery-/Timeout-Schleife; Standzeiten gegenüber Baseline verringert |
| Respawn | Median und p90 bis erste **erreichbare** brauchbare Waffe gemessen; gegen Baseline verbessert; sichere Notfallreaktion |
| Waffenwahl/Fernschüsse | Trefferquote, Schusszahl nach Waffen-/Distanzband; ungeeignete Colt-Schüsse gegenüber Baseline reduziert, keine ammo-losen Feueraktionen |
| Zielwahl Humans | verifizierte Erkennung; Menschen bei vergleichbarer Bedrohung häufiger ausgewählt, nahe tödliche Bedrohung bleibt priorisiert; unbekannte Teilnehmer nicht als Humans ausgeben |
| Aim/Bewegung | Reaktionslatenz und Feuerrhythmus je Skill, Trefferquote je Waffe, Strafe-Anteil, Jump-Ereignisse und Stuck/Damage; A/B mit unverändertem Rest |
| Offline | `poc/botcore make test/smoke/bench`, neue Tests; optional ASan/UBSan; keine Tests als bestanden ausgeben, bevor ausgeführt |
| Native | exakte Map, Botanzahl, Laufdauer, SDK/Build, DLL-SHA, Originalclient, CRC/SYNC-Scanner, Ressourcen und Rollback; für Produktivfreigabe alle Gates einzeln belegen |

## 5. Handoff / Eigentums- und Sicherheitsregeln

- **Vor Implementierung** PR #96 Stand und lokale `agent/chat/20261101-lmarena-integrated`-Commits prüfen; der Audit enthält Selbstberichte von bereits implementierten T-01–T-13, deren Pushergebnis noch nicht bestätigt war. Duplikate sind explizit zu vermeiden.
- Weitere Bindungen: Issue #93 (Cecil-first), PR #39 (Cecil Nav), PR #55 (Item-Utility), PR #74 (Sync/Supervisor), PR #91 (M2/M3 NavV2/Bridge), PR #95 (Respawn-Fix), PR #96 (Audit T-01…T-14).
- Eigene Branches/Worktrees, Commit-Themen trennen, keine Überschreibung fremder Stände, maximal vorhandene sinnvoll koordinierten Agenten nutzen. M1-Stabilität vor aggressivem KI-Tuning.
- **Dieser Branch selbst enthält ausschließlich diesen Intake-Plan.** Kein Build, Test, GameDLL-Wechsel, Commit in fremdem Worktree, Merge, Serverstart oder Rollout durchgeführt.
