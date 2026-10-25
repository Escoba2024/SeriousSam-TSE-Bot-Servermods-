# HUMAN AI 2.0 – Combat-Verbesserungen: Befunde → Fixes → Messwerte

Stand 25.10.2026 · LMArena Agent 2 · Schreibbereich ausschließlich
`poc/research/behavior-improvements/**` + `docs/research/behavior-improvements/**`.
Grundlage: PR #45 (qualifizierte Human-KI), PR #54 (Cecil-Transferanalyse),
PR #57 (Cecil-P1), PR #62 (Behavior-QA, F-1…F-9). botcore wurde vorab
out-of-tree verifiziert: **alle Suiten PASS (555 Human-AI-Checks)** an
`ab0c740`. Alle Zahlen: Offline-Simulation, **NOT_TESTED_RETAIL**.

Reproduktion: `cd poc/research/behavior-improvements && make && make test` bzw.
`python3 run_combat_qa.py --seeds 16` (Seed-Basis `0xC0FFEE + 977*i`, Duel-Cap 45 s).

## P0-Fixes (höchste Wirkung, kleinste Integrationsfläche)

### F-1 Laser-Dominanz / tote Waffen / Persona-Gleichheit → `combat2_weapon.h`
Reproduziert: `BestWeapon(alle Waffen)` = Laser 4–30 m und Cannon >30 m,
identisch für range_preference −0,55/0/+0,85 (Ursachen: flaches `RangeFit=1`
im ganzen Band; Persona-Tilt hängt an der Zieldistanz statt an der Waffe und
ist dadurch wirkungslos). Candidate: Sweet-Spot-Glocken, rebalancierte Peaks,
Persona×Waffenklassen-Affinität (gedeckelt ×1,6), **skillabhängige
Waffenkompetenz** (Sniper Faktor 0,40→1,05 über Tiers), Self-Blast-Veto,
skillgesteuerte Suboptimal-Wahl (t1 35 %→t5 0 %).
Messung: Baseline-Topwaffen über 2–70 m = 3, Candidate ≥6; Aggressor≠Marksman
an 49 % der Distanzen (Baseline 0 %); Laser-Anteil in Mirror-Duellen
0,93–0,98 → 0,00–0,02 bei 3–6 genutzten Waffen; Histogramm-L1
Aggressor↔Marksman 0,02 → 0,89. Lernschleife: Ohne Skill-Kompetenz verlor der
Candidate-Marksman das 40-m-Cross-Duell 4-12 (Sniper-Überschätzung); mit
Kompetenzfaktor + Affinitäts-Cap 10-6 (Cannon) – beides im Header dokumentiert.

### F-5 Strafe deaktiviert + schwach → `StrafeController` + Integrations-Default
Patch 0008 setzt `bot_fStrafeScale=0`. Candidate: Persona-ADAD mit gejittertem
Flip-Intervall (Duelist 0,55 s, Marksman 1,25 s), Diagonal-Strafe beim
Schließen, Dodge-Flip bei Schaden; `StrafeFireTolMult` modelliert die
Eigenbewegungs-Kompensation je Tier. Messung: Baseline 0 Strafe-Ticks/Duell,
Candidate 137–462; Survival-/TTK-Effekt sichtbar an längeren Mirror-Duellen.

### F-3 Keine Hitscan-Latenzführung → `LatencyLeadFactor`/`ProjectileLeadTime`
Mover-Probe (lateral ~5 m/s, 18 m): Baseline Trefferquote Tier 5 fällt
0,798→0,544→0,381 (0/100/200 ms) – PR-#62-Befund reproduziert. Candidate
0,781→0,774→0,768. Zusätzlich iterativer (2×) Projektil-Lead statt 1×;
schwache Tiers kompensieren nur teilweise (Monotonie der Kompetenz).

### F-2 Anfänger funktionsuntüchtig → `combat2_profile.h` + Wunschdistanz
Sigma-Kurve unten komprimiert (4,50°→3,40°, Experte unverändert 1,00°),
Prediction-Floor 0,05→0,25, Anfänger kämpfen über `DesiredRange2` näher
(Komfortdistanz statt Lehrbuchband). Messung t1-Mirror: Draws 6→3 von 16,
Trefferquote 0,213→0,302; Zielfehler t1…t5 = 3,54/2,74/2,22/1,66/1,33°
(strikt fallend). Keine Magic-Genauigkeit: Anfänger bleibt in jeder Spalte
schwächste Stufe (Ladder unten).

## P1-Fixes

### F-4 Rückzug bricht nie LOS → `PlanRetreat` (Schnittstelle zu A3/Nav)
Baseline: geradeaus rückwärts. Candidate: Deckungspunkte kommen über ein
dokumentiertes Interface (`CoverPoint{x,z,blocks_los}`) von der
Navigation-Schicht; Auswahl minimiert Exposition, sonst Zickzack. Probe mit
seitlich versetzter Deckung: Baseline bricht LOS **nie** (−1, läuft 140 m),
Candidate in **2,40 s**. Rückzugsschwelle persona- und zahlenabhängig
(2. Sichtbedrohung +0,12).

### F-7 Nächste Bedrohung ignoriert → `ChooseTarget2`
Score = Nähe + Bedrohung (letzter Schädiger, auf mich gerichtet, <8 m) +
Finish-Bonus, Persona-gewichtet; harter Override für sichtbaren Schädiger
oder Gegner <6 m; Stickiness ×1,25 sonst. 5 deterministische Szenarien in
`test_combat2.cpp`. (Im 1v1-Sim nicht messbar – als Modultest + dokumentierter
Seam in `ChooseTarget` geliefert, kein Fake-Sim-Befund.)

### F-8 Alert = Fast-360° → `AlertHalfAngleDeg`/`AlertReactionTicks`
Alert weitet den Halbwinkel höchstens auf 125° (statt Bypass) und hält ≥2
Reaktions-Ticks (100 ms) Boden. F-6: Suche wechselt seeded die Drehrichtung
(2,5-s-Blöcke) statt konstant einseitig.

### F-9 Mittelstufen-Kompression / Skill-Spreizung (Aufgabe 10)
Reaction/Settle/Prediction neu gespreizt. Gesamtbild Candidate (16 Seeds):

| Metrik | t1 | t2 | t3 | t4 | t5 |
|---|---|---|---|---|---|
| Zielfehler Mirror [°] | 3,54 | 2,74 | 2,22 | 1,66 | 1,33 |
| Trefferquote Mirror | 0,302 | 0,373 | 0,382 | 0,449 | 0,569 |
| Erster Schuss [s] | 2,94 | 1,56 | 0,98 | 0,68 | 0,55 |
| Mirror-Dauer [s] | 26,3 | 13,4 | 13,2 | 8,1 | 7,0 |

Ladder (höhere Stufe gewinnt): t2>t1 14-2, t3>t2 11-4, t4>t3 12-4, t5>t4 15-1,
t5>t1 15-1. Hinweis: Mirror-Trefferquote t2≈t3 ist ein echter Systemeffekt
(schwächere Stufen kämpfen näher → größeres Winkelziel); deshalb ist I2 auf
Zielfehler definiert – im Orchestrator begründet.

## Cross-Policy: Candidate vs. Baseline, gleiche Stufe (16 Duelle/Zelle)

t1 15-0 · t2 12-2 · t3 12-1 · t4 14-2 · t5 13-3 (je D-Rest), Aggressor@10 m
13-3 (Shotgun), Marksman@40 m 10-6 (Cannon). **7/7 Zellen Candidate.**
Ehrliche Einordnung: Ein Teil des Vorsprungs ist designbedingt „bessere
Waffenwahl im selben Weltmodell"; er beweist Konsistenz und Richtwirkung,
keine Retail-Stärke. Persona-Zellen: Mittelreichweiten-Spreizung 8,0 m;
Marksman gewinnt die 45-m-Zelle gegen Aggressor 8-5-3, Aggressor die 8-m-Zelle
16-0 – Präferenzen wirken jetzt sichtbar (Aufgaben 8/10).

## Aufgaben 4 (Zielwechsel/Reaktion) und 9 (Respawn)

Reaktions-/Wechselverhalten: Reaktions-Ticks inkl. Alert-Boden (oben),
Target-Hysterese in `ChooseTarget2`, Waffen-Dwell ohne Flicker (Unit-Test:
≤6 Wechsel bei oszillierender Distanz über 400 Ticks). Respawn: `PlanRespawn`
mit Press-Delay 26→8 Ticks (t1→t5), Scan-Phase, seedierter Erstblick-Richtung,
Waffen-Bereit-Sperre; Survivor +4, Aggressor −2 Ticks. Kompatibel zu PR #57s
Tier-Delays (dort Integration, hier Modul + Tests).

## CPU

`--bench` (200k Ticks, Sandbox-Host): Baseline-Policy 0,227 µs/Tick, Candidate
inkl. Overlays 0,368 µs/Tick (**+0,14 µs** ≈ +0,0003 % Kern @20 Hz/Bot).
Reine Overlay-Kosten sind vernachlässigbar; Retail-CPU bleibt Codex-Gate.

## Grenzen

Offene Arena ohne Vertikalität/Munition/Team; Schadensmodell Hypothese;
Latenz-Lead im Sim an der Sense-Näherung statt am Aim-Point (Seam dokumentiert);
Zielpriorität nur modultestiert; Deckung braucht echte Nav-Daten (A3). Kein
Ergebnis ist ein Retail-Spielergebnis: **NOT_TESTED_RETAIL**.
