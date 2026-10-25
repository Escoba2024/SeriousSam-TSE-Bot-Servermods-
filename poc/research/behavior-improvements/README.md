# HUMAN AI 2.0 – Combat Behavior Improvements (research, offline)

Enginefreie Candidate-Module gegen die Befunde F-1…F-9 aus PR #62, als Overlay
auf der **unveränderten** Human-KI in `poc/botcore/` (read-only eingebunden).
Keine BotDriver-/GameMP-Änderung, keine Navigation, keine Item-KI.

## Inhalt

| Datei | Zweck |
|---|---|
| `combat2_profile.h` | komprimierte Skill-Kurve (Anfänger-Floor F-2), Persona-Orthogonalität bleibt |
| `combat2_weapon.h` | Waffen-Scoring mit Sweet-Spots, Persona-Klassen-Affinität, Skill-Kompetenz (F-1) |
| `combat2_tactics.h` | Zielpriorität (F-7), Latenz-/Projektil-Lead (F-3), Alert-Kegel (F-8), Zweiwege-Suche (F-6), Strafe-Controller (F-5), Deckungs-Rückzug (F-4), Respawn-Plan, Wunschdistanz |
| `combat_sim.cpp` | deterministischer 20-Hz-Duell-Simulator mit echter `HumanBotPolicy`; Modi `--battery --mover --cover --bench --weapon-curve` |
| `test_combat2.cpp` | 107 deterministische Unit-Checks |
| `run_combat_qa.py` | Orchestrator: Batterie + 11 Invarianten + Report |
| `results/` | committete Evidenz (16 Seeds/Zelle) |

## Reproduzieren

```bash
cd poc/research/behavior-improvements
make            # combat_sim + test_combat2 (g++ -std=c++17 -O2 -Wall -Wextra, warnungsfrei)
make test       # Unit-Tests + QA mit 8 Seeds
python3 run_combat_qa.py --seeds 16   # committeter Referenzlauf, 11/11 Invarianten
./combat_sim --weapon-curve           # F-1 vorher/nachher
./combat_sim --mover                  # F-3 Latenz-Probe
./combat_sim --cover                  # F-4 LOS-Bruch-Probe
./combat_sim --bench                  # CPU µs/Bot-Tick
```

## Baseline-Definition

Baseline = qualifiziertes botcore-Profil + ausgelieferte Integrations-Defaults
(`bot_fStrafeScale=0` aus Patch 0008 → Strafe unterdrückt). Candidate =
`AdjustedProfile` + Combat2-Overlays. Beide fahren dieselbe
`botcore::HumanBotPolicy` und **dasselbe** simulierte Waffen-/Schadensmodell
(faires A/B). Cross-Zellen lassen Candidate direkt gegen Baseline antreten.

**Alles Offline-Simulation. Retail-Status: `NOT_TESTED_RETAIL`.** Das
Schadensmodell ist eine Kalibrierhypothese (gleicher Status wie botcores eigene
Tabellen), keine extrahierte Retail-Konstante. Relative Deltas sind das Signal.
