# Session-Hybrid-Lab – Hybrid-Architektur C1 (Konzept)

**Datum:** 2026-10-25 · **Status:** Entwurf / Offline-Prototyp (keine Live-Messung)
· **Zuständig:** Session-Hybrid-Lab & Ressourcenmodellierung (exklusiver
Schreibbereich `poc/research/session-hybrid-lab/` und
`docs/research/session-hybrid-lab/`)

> **Wichtiger Abgrenzungshinweis:** Dieses Dokument beschreibt einen
> Offline-Prototyp und ein Ressourcenmodell. Es enthält **keine** Live-Wine-,
> keine Retail- und keine Laufzeitmessung. Keine Zahl ist eine
> Kapazitätsfreigabe. Evidenzklassen: `[T]` = zitierte Hetzner-/PR-Messung,
> `[O]` = offline getestet (Fixture, dieser Sandbox), `[A]` =
> Architekturvorschlag, `[N]` = noch nicht geprüft.

## 1. Auftrag

Entwicklung eines ressourcensparenden Ansatzes für dynamische Botidentitäten,
Join-/Leave-Verhalten und größere Botpopulationen bei Serious Sam TSE Classic
1.07, unter Wahrung der bestehenden qualifizierten Zwei-Viererclient-Architektur
(Achitektur A: 2 Clients × 4 lokale Spieler, 8 Bots, Stunde bestanden [T]).

Die bestehende Architektur wird **nicht** geändert und bleibt die Referenz.
Dieses Lab liefert einen eigenständigen Prototyp sowie ein
Ressourcenmodell für 4/8/16 Bots; die Integration in produktive Codex-Skripte
bleibt eine spätere, separate Entscheidung.

## 2. Ausgangslage (ausgewertet, nicht verändert)

Folgende schreibgeschützte Vorarbeiten wurden ausgewertet und bilden die
Basis (keine Änderungen an diesen Dateien):

| Quelle | Inhalt | Evidenz |
|---|---|---|
| PR #45 | Integrierte Build04-DLL, 8-Bot-Stunde 3600 s, 0 SYNCBAD, öffentliche Flotte 8/16 | [T] |
| PR #47 | `tools/bot_sessions.py`: SQLite-Session-Planner, stabile UUIDv5-GUIDs, OFFLINE→WAITING→JOINING→PLAYING→LEAVING→COOLDOWN, min_bots, Human-Slot-Reserve, Epochen-Schutz | [T] (portable Core, nativ blockiert) |
| PR #50 | Fleet-Supervisor, guarded recovery, Host-Reserve, Spieler-Schutz | [T] (Draft) |
| PR #56 | `poc/research/ram-efficiency/`: `resource_model.py` (A/B/C/D, 1/4/8/16), `slotplan.py` (ROSTER_RESTART-Scheduler), `memsample.py`, `ksm_probe.py`, Messprotokoll | [T]/[O] |

Kernbefund aus PR #56 [T]:
* Architektur A kostet ca. 419 MiB RSS / 69 % eines Kerns für 8 Bots (2 Viererclients).
* Architektur B (1 Client pro Bot) kostet ca. 200 MiB marginal pro Bot; 8 unabhängige Clients wurden am 1068-MiB-Reserve-Gate zweimal blockiert.
* Der Retail-Client erlaubt max. 4 lokale Spieler (`gm_lpLocalPlayers[4]`); ein sichtbarer Einzel-Entfernen-Pfad für eine `CPlayerSource` ist in GameMP nicht belegt (E2 [N]).

## 3. Architekturentscheidung: Hybrid C1 (ROSTER_RESTART)

Das Lab verfolgt **Architektur C1** als risikofreien Unterbau:

* Es werden weiterhin nur `⌈N/4⌉` Viererclients verwendet (gleiche Prozessanzahl wie A).
* Logische Bot-Sessions werden auf die 4 Slots der Clients gepackt.
* Join/Leave-Änderungen werden in einem Batch-Fenster (Vorschlag 20–30 s) gesammelt und durch einen Client-Neustart mit neuem Roster umgesetzt.
* Jede Session behält eine stabile Identität (GUID, Profil, Spiel-Seed, Nickname) über Crash, Cooldown und Rejoin hinweg [O-Prototyp].
* Co-Residenten eines neu gestarteten Clients werden kurz unterbrochen und rejoinen mit identischer Identität.

**C1 benötigt keine neue Engine-Fähigkeit.** Es verwendet ausschließlich bereits qualifizierte Primitive: Client-Start mit festem Roster, Join-Bestätigung, kontrollierter Stopp, persistente GUID/Profil-Identität über Rejoin (PR #47), Reconnect-Mechanik (poc/patch/0002/0003). Sichtbare Kosten: Join-Latenz ≤ Batch-Fenster + Clientstart.

**C2 (Dynamic-Slot)** – mid-session `_pNetwork->AddPlayer_t` / Spielerquelle-Entfernung auf bestehender Verbindung – ist **nicht** Teil dieses Lab. E1/E2/E3 (siehe §8) sind unverifiziert [N] und werden nur als spätere Option dokumentiert. Keine neue Retail-Engine-Fähigkeit wird vorausgesetzt.

## 4. Abgrenzung zu anderen Agenten-Bereichen

Dieses Lab besitzt ausschließlich Session-Hybrid-Lab und Ressourcenmodellierung. Es folgt bewusst nicht:

* keine produktiven Supervisor-Skripte (Codex C1 / PR #46);
* keine Combat-KI (LMArena A2);
* keine Navigation / Item-Utility (LMArena A3);
* keine GameMP.dll-Änderungen;
* keine nativen Sync-Diagnosen (Codex C2).

Wo eine Schnittstelle zu einem anderen Bereich benötigt wird, wird sie dokumentiert und gemockt (z. B. der native Runtime-Adapter für den Session-Planner, §7).

## 5. Prototyp (`poc/research/session-hybrid-lab/`)

| Datei | Aufgabe |
|---|---|
| `session_hybrid_lab.py` | Hybrid-Session-Prototyp: Session-Planner (stabile Identität, Lifecycle, min_bots, Human-Reserve), Hybrid-Scheduler C1 (ROSTER_RESTART), Ghost-Recovery, deterministischer SimRunner |
| `trace_simulator.py` | Reine Trace-Generatoren: geordnete Joins, zufällige Joins/Leaves, Crash+Cooldown+Rejoin, Server-Neustart, Szenarien 4/8/16 |
| `resource_model_hybrid.py` | Ressourcenmodell A/B/C1 für 1/4/8/16 Bots mit Evidenzklassen |
| `measurements.json` | Mess-Anker (zitiert, keine Sandbox-Messung) |
| `bench_harness_offline.py` | Offline-Harness (simuliert, read-only, Provenienz) |
| `test_*.py` | 55 reproduzierbare Unit-Tests, alle offline/fixture-basiert |

Der Prototyp startet **keine** Prozesse, benutzt **kein** Wine und **keine**
Retail-Binary. Er ist deterministisch (ge Seeder PRNG, virtuelle Uhr) und
wiederholbar [O].

## 6. Testanforderungen (umgesetzt)

Alle im Auftrag genannten Szenarien sind als reproduzierbare Tests abgedeckt:

1. Vier Bots in einer Clientgruppe → 1 Client [O-Test]
2. Acht Bots in zwei Clientgruppen → 2 Clients [O-Test]
3. Zufällige Sessionzeiten (Poisson + Band-Dauern) [O-Test]
4. Geordnete Joins [O-Test]
5. Geordnete Leaves [O-Test]
6. Crash und Cooldown [O-Test]
7. Rejoin mit stabiler Identität (GUID unverändert) [O-Test]
8. Server-Neustart-Simulation (alle trennen, stabiler Rejoin) [O-Test]
9. Human-Slot-Reserve (Kapazität = maxplayers − reserved − humans) [O-Test]
10. Ressourcenmangel / Kapazitätsgrenze (max_clients → Warteschlange) [O-Test]
11. Verwaiste Sessions / Ghost-Zustände (verifizierte Abwesenheit vor Wiederverwendung) [O-Test]
12. Doppelstartverhinderung (Epochen-Schutz) [O-Test]
13. Simulation größerer Populationen (16 Bots, 4 Clients) [O-Test]

Erfasste (modellierte) Größen: Client-Prozesse, Peak-Clients, Restarts,
Co-Resident-Unterbrechungen, Join-Wartezeit, geschätzter Peak-RAM (RSS-Basis,
DERIVED). Keine Live-CPU/RAM-Messung [N für echte Messwerte].

## 7. Native Runtime-Vertrag (Schnittstelle, gemockt)

Der Session-Planner erzeugt nur Absichten (Intents). Eine spätere native
Anbindung muss vor jedem Start/Stop eigenständig prüfen: PID, Startzeit,
CWD, cgroup, Port, GUID. Ein JOINING-Epoch darf nur einmal gestartet werden
(`claim_launch`-Semantik, PR #47). Ein zweiter Controller darf dieselbe
Identität nicht doppelt starten. Geplante Pausen dürfen nicht als
fehlgeschlagene Pflichtslots aufgefüllt werden (Konflikt mit PR-46-Supervisor
dokumentiert). Diese Schnittstelle ist in diesem Lab gemockt, nicht
implementiert [A].

## 8. Offene Punkte (E1–E3)

| Punkt | Frage | Status |
|---|---|---|
| E1 | Funktioniert `_pNetwork->AddPlayer_t` mid-session auf bestehender Verbindung? | [N] |
| E2 | Gibt es einen sauberen Einzel-Entfernen-Pfad für eine `CPlayerSource`? | [N] |
| E3 | Bleiben CRC/Sequenz/Sync bei E1/E2 für Vanilla-Gegenstellen neutral (SYNCBAD-Historie beachten)? | [N] |

Verifikationsweg [A]: erst statisch per GhidraMCP auf der originalen
`Engine.dll`, dann isolierter Laufzeitversuch mit Wegwerf-Kopie. C1 bleibt
unabhängig davon funktionsfähig.

## 9. Abgrenzung / Nicht-Ziele

* Keine behaupteten Leistungsverbesserungen ohne Messung.
* Keine echten Wine-/Retail-Benchmarks in diesem Lab.
* Keine Änderungen an `poc/research/ram-efficiency/`, `poc/botcore/`,
  `poc/patch/`, `poc/release/`, `poc/scripts/`, `tools/operations/`, `AGENTS.md`
  (alles READ-ONLY für dieses Lab).
* Keine produktive Aktivierung; `enabled=False` ist der Default.
