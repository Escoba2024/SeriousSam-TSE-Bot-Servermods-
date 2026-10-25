# Session-Hybrid-Lab – Integrationsplan für Codex und Handoff-Vorlage

**Datum:** 2026-10-25 · **Status:** Entwurf · **Zuständig:** Session-Hybrid-Lab

## 1. Was dieses Lab liefert

| Liefergegenstand | Pfad | Status |
|---|---|---|
| Funktionsfähiger Hybrid-Session-Prototyp | `poc/research/session-hybrid-lab/session_hybrid_lab.py` | [O] getestet |
| Unabhängiger Session-Scheduler (Hybrid C1, ROSTER_RESTART) | `session_hybrid_lab.py` (`HybridScheduler`) | [O] getestet |
| Session-Planner (stabile Identität, Lifecycle, min_bots, Human-Reserve) | `session_hybrid_lab.py` (`SessionPolicy`) | [O] getestet |
| Ghost-Recovery | `session_hybrid_lab.py` (`GhostRecovery`) | [O] getestet |
| Trace-Simulator (geordert, zufällig, Crash/Cooldown/Rejoin, Server-Neustart) | `poc/research/session-hybrid-lab/trace_simulator.py` | [O] getestet |
| Ressourcenmodell 1/4/8/16 (A/B/C1) | `poc/research/session-hybrid-lab/resource_model_hybrid.py` + `measurements.json` | [D]/[T]-Anker |
| Offline-Bench-Harness (simuliert, Provenienz) | `poc/research/session-hybrid-lab/bench_harness_offline.py` | [O] |
| Reproduzierbare Tests (55) | `poc/research/session-hybrid-lab/test_*.py` | [O] 55 PASS |
| CPU-/Speicherauswertung (modelliert, mit Evidenzklassen) | `docs/research/session-hybrid-lab/2026-10-25-resource-model-hybrid.md` | [T]/[D]/[P] |
| Risikobewertung | `docs/research/session-hybrid-lab/2026-10-25-risk-assessment.md` | [A] |
| Integrationsplan + Handoff | dieses Dokument | [A] |

**Keine** produktiven Supervisor-Skripte, keine Combat-KI, keine Navigation,
keine GameMP.dll-Änderungen in diesem Lab.

## 2. Abgrenzung und Schnittstellen

Das Lab besitzt ausschließlich Session-Hybrid-Lab und Ressourcenmodellierung.
Schnittstellen zu anderen Bereichen (Codex C1 Supervisor, LMArena A2/A3,
Codex C2 Sync-Diagnose) werden **dokumentiert und gemockt**, nicht implementiert:

* **Session-Planner → Runtime-Adapter:** Der Planner erzeugt nur Absichten
  (Intents) mit `(identity_id, epoch)`. Ein späterer Adapter muss vor jedem
  Start/Stop eigenständig PID, Startzeit, CWD, cgroup, Port und GUID prüfen
  und einen Launch-Claim verbrauchen (at-most-once, PR #47-Semantik).
* **Scheduler → Prozesssteuerung:** Der Hybrid-Scheduler entscheidet, welche
  Sessions auf welchem Client/Slot laufen und wann ein Client neu gestartet
  wird. Er startet selbst keine Prozesse.
* **Ghost/Recovery:** Verifizierte Abwesenheit vor Slot-Wiederverwendung;
  Epoch-Schutz gegen Doppelstart.

## 3. Integrationspfad für Codex (konkret, nicht aktivierend)

1. **Offline-Prototyp validieren:** 55 Unit-Tests grün (PASS), keine Live-Messung.
2. **Ressourcenmodell absichern:** Messaufträge M1–M5
   (`2026-10-25-measurement-plan.md`) auf dem autorisierten Wine-Host
   ausführen, um Projektionen durch PSS/RSS-Messwerte zu ersetzen.
3. **Native C1-Gate:** Einzelverbindungs-Smoke auf eigenen Ports mit
   regulärem Join/Quit und stabilem GUID-Rückkehr (kleinster nächster Schritt
   aus PR #47-Handoff, erst nach Abschluss fremder PR-46-Qualifikation).
4. **Supervisor-Abstimmung:** Sollzustand des Session-Planners mit dem
   PR-46-Supervisor abstimmen, sodass geplante Pausen nicht als fehlgeschlagene
   Pflichtslots aufgefüllt werden (R7).
5. **Erst 1/4/8, dann 2×8:** Qualifizierung in steigender Populationsstufe,
   ≥ 3600 s gemeinsame Stabilität, CPU/RAM/20 Hz/SYNCBAD/Disconnect/Restart.
6. **Produktiv nur nach allen nativen Gates:** `enabled=False` bleibt Default,
   bis die native Abnahme bestanden ist.

## 4. Handoff-Vorlage (bei PR-Erstellung zu füllen)

```
Branch: arena/20261025-session-hybrid-c1-lab
SHA: <commit-SHA>
PR-Link: <https://github.com/Escoba2024/SeriousSam-TSE-Bot-Servermods-/pull/N>
Dateien:
  poc/research/session-hybrid-lab/**
  docs/research/session-hybrid-lab/**
Testbefehle:
  cd poc/research/session-hybrid-lab
  python3 -m unittest discover -s . -p 'test_*.py'
  python3 resource_model_hybrid.py --format markdown
  python3 bench_harness_offline.py --scenario 8b_ordered --out /tmp/out.json
PASS/FAIL: 55 Tests OK / keine Live-Wine- oder Retail-Zugriffe
Benchmark-Provenienz: alle Läufe simulate-Modus, wine_used=false,
retail_binary_used=false, evidence="[O]"; Mess-Anker zitiert aus PR #45/#47/#51
bekannte Grenzen: keine echten CPU/RAM/PSS-Messwerte; C1-Join-Latenz ≤
Batch-Fenster + Clientstart; E1/E2/E3 unverifiziert; enabled=False Default
native Abnahmebedingungen: Runtime-Adapter, nativen Join/Quit/Rejoin, SYNCBAD=0,
20 Hz, ≥3600 s Stabilität, PR-46-Supervisor-Abstimmung
```

## 5. Git-Regeln (für den zu erstellenden PR)

* Branch: `arena/20261025-session-hybrid-c1-lab` (Präfix `arena/20261025-session-hybrid-`)
* Keine Änderungen an `main`; kein Force-Push; kein Auto-Merge
* Keine Änderungen an bestehenden PR-Branches oder READ-ONLY-Dateien
* Eigener Pull Request von diesem Branch; kein Überschreiben anderer Agenten-PRs
* Schreibausschluss außerhalb von `poc/research/session-hybrid-lab/` und
  `docs/research/session-hybrid-lab/` eingehalten

## 6. Blocker (falls kein GitHub-Schreibzugriff)

Commits und Patch lokal erhalten, Blocker dokumentieren, keinen eigenständigen
Merge auf `main` durchführen.
