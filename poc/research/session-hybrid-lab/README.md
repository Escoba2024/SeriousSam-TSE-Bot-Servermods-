# poc/research/session-hybrid-lab – Session-Hybrid-Lab (Architektur C1)

**Teil des LMArena-Agent-4-Auftrags „RESSOURCE OPTIMIZATION + HYBRID BOT SESSIONS“.**
**Stand: 25.10.2026**

## Zweck

Offline, deterministischer Prototyp für hybride Bot-Sessions bei Serious Sam
TSE Classic 1.07:

* stabile Botidentitäten (UUIDv5-GUID, Profil, Spiel-Seed, Nickname) über
  Crash, Cooldown und Rejoin hinweg;
* Session-Lifecycle OFFLINE → WAITING → JOINING → PLAYING → LEAVING → COOLDOWN,
  getrennt geplanter Abgang vs. Crash;
* Human-Slot-Reserve und Mindestpopulation (`min_bots`);
* Ghost-Zustände und Server-Neustart-Recovery (verifizierte Abwesenheit vor
  Slot-Wiederverwendung, Epoch-Schutz gegen Doppelstart);
* geordnete und zufällige Join/Leave-Traces;
* Hybrid-Scheduler C1 (ROSTER_RESTART): Sessions multiplexen auf shared
  4-Spieler-Retail-Clients, Mitgliedschaftsänderungen werden in Batch-Fenstern
  gebündelt und durch Client-Neustart mit neuem Roster umgesetzt.

## Abgrenzung (verbindlich)

* **Schreibbereich ausschließlich:**
  `poc/research/session-hybrid-lab/**` und
  `docs/research/session-hybrid-lab/**`.
* Alle anderen Dateien (insbesondere
  `poc/research/ram-efficiency/`, `poc/research/behavior-improvements/`,
  `poc/research/nav-item-bridge/`, `poc/research/sync-hypothesis-validation/`,
  `poc/botcore/`, `poc/patch/`, `poc/release/`, `poc/scripts/`,
  `tools/operations/`, `AGENTS.md`) sind für dieses Lab **READ-ONLY**.
* Keine produktiven Supervisor-Skripte, keine Combat-KI, keine Navigation,
  keine GameMP.dll-Änderungen.
* Keine neuen Retail-Engine-Fähigkeiten vorausgesetzt (C1 kommt ohne E1/E2 aus;
  C2/Dynamic-Slot bleibt unverifiziert und ist nicht Teil dieses Lab).
* Keine Live-Wine-, keine Retail- und keine Laufzeitmessung. Keine Zahl ist
  eine Kapazitätsfreigabe. Keine behaupteten Leistungsverbesserungen ohne
  Messung.

## Evidenzklassen

* `[T]` technisch nachgewiesen (zitierte Hetzner-/PR-Messung, Quelle angegeben)
* `[O]` offline getestet (Fixture, dieser Sandbox, kein Wine)
* `[A]` Architekturvorschlag (Entwurf, kein Laufzeitnachweis)
* `[N]` noch nicht geprüft

## Dateien

| Datei | Aufgabe |
|---|---|
| `session_hybrid_lab.py` | Prototyp: Session-Politik, Hybrid-Scheduler C1, Ghost-Recovery, SimRunner, CLI |
| `trace_simulator.py` | Reine Trace-Generatoren (geordnet, zufällig, Crash/Cooldown/Rejoin, Server-Neustart, Szenarien 4/8/16) |
| `resource_model_hybrid.py` | Ressourcenmodell A/B/C1 für 1/4/8/16 Bots mit Evidenzklassen |
| `measurements.json` | Mess-Anker (zitiert, keine Sandbox-Messung) |
| `bench_harness_offline.py` | Offline-Harness (simuliert, read-only, Provenienz) |
| `test_session_hybrid_lab.py` | Unit-Tests Scheduler, Policy, SimRunner |
| `test_resource_model_hybrid.py` | Unit-Tests Ressourcenmodell |
| `test_trace_simulator.py` | Unit-Tests Trace-Generatoren |

## Nutzung

```bash
# Alle 55 reproduzierbaren Unit-Tests (offline, keine Wine/Retail)
python3 -m unittest discover -s . -p 'test_*.py'

# Ressourcenmodell 1/4/8/16 (A/B/C1, Markdown)
python3 resource_model_hybrid.py

# Offline-Szenario 8 Bots geordnet (simuliert, mit Provenienz)
python3 bench_harness_offline.py --scenario 8b_ordered --out /tmp/result.json

# CLI des Prototyps (simuliert)
python3 session_hybrid_lab.py --bots 8 --out /tmp/session.json --ledger /tmp/ledger.json
```

## Bezug auf bestehende Arbeit (schreibgeschützt, nicht verändert)

Aufbauend auf (Referenz, keine Änderungen):
* PR #47: `tools/bot_sessions.py` (Identitäten, Lifecycle, Epochen, min_bots)
* PR #56: `poc/research/ram-efficiency/slotplan.py` (ROSTER_RESTART-Scheduler),
  `resource_model.py` (A/B/C/D RAM-Modell), `measurements.json`
* PR #45/#51: Hetzner-Messwerte (8-Bot-Stunde, Reserve-Gate, Redstation)

Dokumentation: `docs/research/session-hybrid-lab/` (Konzept, Lifecycle,
Ressourcenmodell, Messplan, Testplan, Risikobewertung, Integrationsplan).

## Testanforderungen (alle umgesetzt)

Vier Bots in einer Gruppe · Acht Bots in zwei Gruppen · zufällige
Sessionzeiten · geordnete Joins/Leaves · Crash und Cooldown · Rejoin mit
stabiler Identität · Server-Neustart-Simulation · Human-Slot-Reserve ·
Ressourcenmangel · verwaiste Sessions · Doppelstartverhinderung ·
größere Populationen (16 Bots).

## Git

Eigener Branch `arena/20261025-session-hybrid-c1-lab`; eigener Pull Request;
keine Änderungen an `main`; kein Force-Push; kein Auto-Merge.
