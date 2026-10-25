# Session-Hybrid-Lab – Risikobewertung

**Datum:** 2026-10-25 · **Status:** Entwurf · **Evidenz:** [T] zitierte PR-Befunde, [A] Architektururteil, [N] nicht geprüft

## 1. Methode

Risiken werden nach Wirkung × Eintrittswahrscheinlichkeit eingeschätzt.
Bewertungen basieren auf den zitierten Hetzner-/PR-Befunden (PR #45/#47/#51/
#56) und dem Offline-Prototyp. Keine Bewertung ersetzt eine native
Retail-Abnahme.

## 2. Risikoregister

| ID | Risiko | Wirkung | Wahrscheinlichkeit | Bewertung | Gegenmaßnahme / Status |
|---|---|---|---|---|---|
| R1 | C1-Roster-Restart unterbricht Co-Residenten kurz (Join-Latenz ≤ Batch-Fenster + Clientstart) | Mittel | Sicher (by design) | **akzeptiert** | Für „natürlich wirkende Sessions“ (Minuten–Stunden) unkritisch; nicht für sekundengenaue Einzel-Leaves [A] |
| R2 | Architektur B (1 Client/Bot) wird am 1068-MiB-Reserve-Gate blockiert | Hoch | gesichert [T] | **vermieden** | C1 verwendet Viererclient-Multiplexing statt B [T] |
| R3 | PSS/RSS-Abweichung: das Modell rechnet mit RSS (geteilte Seiten mehrfach gezählt) | Mittel | möglich [N] | **offen** | Messauftrag M2 (PSS-Wahrheit) vor Modell-Update [N] |
| R4 | Transienter +1-Client während Roster-Restart-Fenster unterschätzt den Peak | Niedrig | möglich | **akzeptiert** | konservativ stop-vor-start kalkuliert [A] |
| R5 | Ghost-Zustände (verwaiste Slots) werden fälschlich wiederverwendet | Mittel | möglich | **gemildert** | verifizierte Abwesenheit + Epoch-Schutz vor Wiederverwendung [O-Prototyp] |
| R6 | Doppelstart derselben Identität (zwei Prozesse, gleiche GUID) | Hoch | unwahrscheinlich | **gemildert** | at-most-once Launch-Claim pro Epoch, transaktional [A, gemockt] |
| R7 | Konflikt mit PR-46-Supervisor (geplante Pause als fehlgeschlagener Slot aufgefüllt) | Hoch | möglich | **dokumentiert** | parallele Nutzung nicht aktivieren; Sollzustand abgestimmen [T aus PR #47-Handoff] |
| R8 | C2/Dynamic-Slot benötigt nicht verifizierte Engine-Fähigkeiten (E1/E2/E3) | Hoch | unklar | **nicht Teil dieses Lab** | C1 funktionsfähig ohne E1–E3; C2 nur nach statischer + isolierter Laufzeit-Verifikation [N] |
| R9 | Keine echten CPU/RAM-Messwerte (nur Projektionen) | Mittel | sicher | **dokumentiert** | alle Projektionen mit [P]/[D] gekennzeichnet; Messplan definiert [N] |
| R10 | Simulator-Connect-/Client-Start-Zeiten (8 s) sind Modellannahmen, keine Messwerte | Niedrig | sicher | **dokumentiert** | als solche gekennzeichnet; keine Kapazitätsfreigabe [A] |

## 3. Risiken, die explizit NICHT getragen werden

* Keine Änderungen an GameMP.dll oder der qualifizierten Build04-DLL.
* Keine neuen Retail-Engine-Fähigkeiten vorausgesetzt.
* Keine produktiven Supervisor-Skripte, keine Combat-KI, keine Navigation.
* Keine Testclients auf produktiven Ports, keine Serverneustarts,
  keine Änderungen an produktiven Hetzner-Prozessen.

## 4. Restrisiko für die Integration

Der Übergang vom Offline-Prototyp zur nativen Retail-Anbindung erfordert
einen qualifizierten Runtime-Adapter (PID/Start/CWD/cgroup/Port/GUID-Abgleich,
Launch-Claim, Query-Abwesenheit) sowie eine native Abnahme (Join/Quit/Rejoin,
SYNCBAD, 20 Hz, Stabilität). Bis dahin bleibt `enabled=False` [A].
