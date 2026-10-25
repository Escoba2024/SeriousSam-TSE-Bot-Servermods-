# HANDOFF – LMArena Agent 2 · HUMAN AI 2.0 Combat Behavior & QA · 25.10.2026

- **Branch:** `arena/501f5d01-serioussam-tse-bot-servermods` (vorgegebener
  Session-Branch; Aufgaben-Präfix `arena/20261025-combat-improvements-` wurde
  wegen fixer Session-Branchbindung nicht verwendet – Abweichung dokumentiert).
- **Basis:** `main` @ `ab0c740`. **Commits:** `4c770a0` (+ dieser Handoff-Commit).
- **PR:** siehe GitHub (eigener PR aus obigem Branch, kein Eingriff in #57/#62, kein Merge).
- **Schreibbereich eingehalten:** ausschließlich
  `poc/research/behavior-improvements/**` + `docs/research/behavior-improvements/**`.
  botcore u. a. Geschützte nur gelesen/out-of-tree gebaut.

## Testbefehle + Ergebnis (Offline)

```bash
cd poc/botcore && make test            # Baseline-Referenz, out-of-tree: alle PASS (555 Human-Checks)
cd poc/research/behavior-improvements
make && make test                      # COMBAT2: 107 Checks, 0 Failures PASS
python3 run_combat_qa.py --seeds 16    # INVARIANTS 11/11 PASS (committete results/)
./combat_sim --mover|--cover|--bench|--weapon-curve
```

Kenndaten: Seed-Basis `0xC0FFEE+977*i`, 16 Duelle/Zelle, 21 Zellen je Policy
+ 7 Cross-Zellen. Cross 7/7 Candidate; Mover t5 200 ms: 0,381 → 0,768;
Cover: LOS-Bruch 2,40 s vs. nie; CPU: 0,227 → 0,368 µs/Tick (Sandbox-Host).
**Retail: NOT_TESTED_RETAIL** – keine Serverprozesse, keine DLL-Berührung.

## Bekannte Einschränkungen

Offene 1v1-Arena (kein Team/Munition/Vertikal), Schadensmodell = Hypothese,
Latenz-Lead im Sim per Sense-Näherung (Aim-Point-Seam dokumentiert),
Zielpriorität modultestiert statt 1v2-simuliert, Deckung braucht echte
Nav-Daten (A3), Persona-Siege in Range-Zellen sind Präferenzfolgen.

## Konkrete Integrationsschritte (Codex)

Siehe [Integrationsplan](2026-10-25-integration-plan-codex.md) Schritte 0–7
mit Seams, Opt-in-Schaltern und Gates; vor Schritt 5/7 mit PR #57 abgleichen,
Schritt 6 braucht den CoverPoint-Vertrag mit A3 (Navigation).
