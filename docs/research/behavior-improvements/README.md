# HUMAN AI 2.0 – Combat Behavior & QA (LMArena Agent 2, research)

- [Befunde → Fixes → Messwerte](2026-10-25-findings-and-improvements.md)
- [Integrationsplan für Codex (7 Schritte, Seams, Gates)](2026-10-25-integration-plan-codex.md)
- Code + Simulator + Tests: [`poc/research/behavior-improvements/`](../../../poc/research/behavior-improvements/README.md)
- Committete Mess-Evidenz: `poc/research/behavior-improvements/results/`

Kurz: PR-#62-Funde F-1…F-9 reproduziert und mit enginefreien Overlay-Modulen
adressiert (Waffen-Nischen statt Laser-Dominanz, Anfänger-Floor, Hitscan-Lead,
aktives Strafing, LOS-brechender Rückzug, Threat-Zielwahl, Alert-Kegel,
Respawn-Plan, Skill-Spreizung). 107 Unit-Checks + 11 Batterie-Invarianten
PASS; Candidate schlägt Baseline in 7/7 Cross-Zellen der Simulation.
Overlay-Kosten +0,14 µs/Bot-Tick. **Alles Offline – NOT_TESTED_RETAIL.**
Produktive Human-KI (`poc/botcore/**`) unverändert; Integration obliegt Codex.
