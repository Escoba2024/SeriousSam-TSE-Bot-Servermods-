# Architekturvergleich und Optimierungsplan: 1/4/8/16 unabhängige Bots auf 4 GB

**Datum:** 2026-10-25 · **Grundlage:** ausschließlich die in
[`2026-10-25-ram-analysis.md`](2026-10-25-ram-analysis.md) zitierten
Hetzner-Messungen; Modell und Tabellen sind mit
`poc/research/ram-efficiency/resource_model.py` reproduzierbar
(`python3 resource_model.py [--coexist-public]`). **Keine Zeile dieses
Dokuments ist eine Kapazitätsfreigabe.**

## 1. Die vier Architekturen

| | Prozesse für N Bots | Join/Leave-Granularität | Isolation/Sicherheit | Status |
|---|---|---|---|---|
| **A** Status quo | ⌈N/4⌉ Clients + Server | nur ganzer Viererclient | gut (2 Prozesse), aber 4 Bots teilen Schicksal | qualifiziert (8 Bots, Stunde) [T] |
| **B** PR #47 | N Clients (+ privater Server) | **echt pro Bot** | maximal (eigener Prozess/NS/cgroup je Bot) | 4 Bots PASS_LIMITED; 8 blockiert [T] |
| **C** Hybrid (neu) | ⌈N/4⌉ Clients | pro Bot (Scheduler) | wie A je Prozess; Fehlerradius 4 Bots | Scheduler-Prototyp offline getestet [O]; Laufzeit [N] |
| **D** B + Footprint-Optimierungen | N Clients | pro Bot | wie B | reine Projektion [N] |

### Architektur C im Detail (zwei Stufen)

**C1 – Roster-Restart (keine neue Engine-Fähigkeit nötig):**
`slotplan.py`-Scheduler packt logische Sessions auf 4-Slot-Clients.
Join/Leave-Anforderungen werden im Batchfenster (Vorschlag 20–30 s)
gesammelt; betroffene Clients starten mit neuem Roster neu. Primitive, die
dafür nötig sind, sind **sämtlich bereits qualifiziert**: Client-Start mit
festem Roster, Join-Bestätigung, kontrollierter Stop, persistente
GUID/Profil-Identität über Rejoin (PR #47: `unchanged_after_rejoin=true`
[T]), Reconnect-Mechanik (`poc/patch/0002/0003`). Sichtbare Kosten:
Join-Latenz ≤ Batchfenster + Clientstart; Co-Residenten eines neu
gestarteten Clients verschwinden kurz und rejoinen mit identischer
Identität. Für eine „öffentliche Flotte mit natürlich wirkenden
Sessions“ (Minuten-bis-Stunden-Rhythmus aus PR #47) ist diese Latenz
unkritisch; für sekundengenaue Einzel-Leaves ist sie es nicht.

**C2 – Dynamic-Slot (benötigt E1/E2/E3, alle [N]):**
mid-session `_pNetwork->AddPlayer_t`/Player-Source-Entfernung auf bestehender
Verbindung. Dann entfallen Restarts und Unterbrechungen vollständig;
Prozesszahl bleibt ⌈N/4⌉. Verifikationsweg: GhidraMCP-Statik → isolierter
Wegwerf-Laufzeitversuch → Vanilla-/Sync-Gate (E3). C1 ist der risikofreie
Unterbau, C2 die spätere Veredelung desselben Schedulers (gleiches
Interface, Modus-Flag).

## 2. Ressourcenmodell 1/4/8/16 (generiert, Provenienz je Zelle)

Standalone-Budget: 3819 − 700 MiB OS-/Monitor-Reserve = 3119 MiB.
RSS-Basis ≠ cgroup-Basis: A/C-Zahlen sind Spielprozess-RSS [T-Basis],
B/D-Zahlen cgroup-Peaks inkl. privatem Server/Xvfb/Wine — konservativ
nicht direkt mischbar; genau deshalb verlangt das Messprotokoll PSS (M2).

| Arch | Bots | Clients | RAM MiB | RAM-Evidenz | CPU %Kern | CPU-Evidenz | Host-Fit |
|---|---:|---:|---:|---|---:|---|---|
| A | 1 | 1 | 234,4 | DERIVED | 36,6 | DERIVED | fits |
| B | 1 | 1 | 555,8 | **MEASURED** | 51,5 | **MEASURED** | fits |
| C | 1 | 1 | 234,4 | DERIVED | 36,6 | DERIVED | fits |
| D | 1 | 1 | 500,6 | PROJ_UNVERIFIED_OPT | n/a | – | fits |
| A | 4 | 1 | 234,4 | DERIVED | 39,0 | DERIVED | fits |
| B | 4 | 4 | 1158,0 | **MEASURED** | 72,5 | **MEASURED** | fits |
| C | 4 | 1 | 234,4 | DERIVED | 39,0 | DERIVED | fits |
| D | 4 | 4 | 937,2 | PROJ_UNVERIFIED_OPT | n/a | – | fits |
| A | 8 | 2 | 418,6 | **MEASURED** | 69,0 | **MEASURED** | fits |
| B | 8 | 8 | 1960,9 | PROJECTED | 100,5 | PROJECTED | fits* |
| C | 8 | 2 | 418,6 | DERIVED | 69,0 | DERIVED | fits |
| D | 8 | 8 | 1519,3 | PROJ_UNVERIFIED_OPT | n/a | – | fits |
| A | 16 | 4 | 787,0 | PROJECTED | 131,2 | PROJECTED | fits** |
| B | 16 | 16 | 3566,7 | PROJECTED | 156,5 | PROJECTED | **exceeds** |
| C | 16 | 4 | 787,0 | PROJECTED | 131,2 | PROJECTED | fits** |
| D | 16 | 16 | 2683,5 | PROJ_UNVERIFIED_OPT | n/a | – | tight |

\* **Modell-vs-Gate-Diskrepanz, ausdrücklich:** „fits“ gilt nur gegen die
pauschale 700-MiB-Reserve des Modells. Das real geltende PR-#47-Gate
verlangt **1068 MiB verfügbar vor jedem weiteren Client** und hat 8×B neben
der Publikflotte zweimal tatsächlich blockiert [T]. Das Gate ist die
verbindliche Instanz, nicht das Modell. Zusätzlich wären B8 ≈ 100 % eines
Kerns **plus** Publikflotte ≈ 65 % ≈ 82 % beider vCPU — oberhalb der
30-%-Zielreserve aus `2026-10-21-hetzner-capacity.md`.
\*\* 16 Bots erfordern eine zweite 16-Slot-Serverinstanz und lassen sonst
keine Menschenplätze (Slot-Limit) — CPU ≈ 131 % eines Kerns ≈ 66 % des
Hosts, vor Menschen-/OS-Last; nur rechnerisch.

Koexistenz-Variante (`--coexist-public`, Budget 2588 MiB) im Tool
reproduzierbar; B16/D16 überschreiten dort das Budget ebenfalls.

## 3. Bewertung: Unabhängigkeit × RAM × CPU × Sicherheit

| Kriterium (8 Bots) | A | B | C1 | C2 | D |
|---|---|---|---|---|---|
| Echte Einzel-Session | ✗ | ✓✓ | ✓ (Latenz/Restart) | ✓✓ | ✓✓ |
| RAM | ✓✓ 419 MiB [T] | ✗ ~1,9 GiB [P] | ✓✓ ~419 MiB [D] | ✓✓ | ✓ ~1,5 GiB [P,N] |
| CPU | ✓✓ 69 % [T] | ✗ ~100 % [P] | ✓✓ ~69 % [D] | ✓✓ | ✗ wie B + ksmd |
| Isolation/Blast-Radius | ✓ (4 Bots/Prozess) | ✓✓ (1 Bot) | ✓ | ✓ | ✓✓ |
| Qualifizierungsaufwand | 0 (ist produktiv) | hoch (blockiert) | mittel (nur Orchestrierung) | hoch (E1–E3) | hoch (K1–K3, Z1) |
| Vanilla-Kompatibilität | ✓ [T] | ✓ [T] | ✓ (nur Start/Stop außen) | [N] E3! | ✓ wie B |

**Empfehlung (hybride Architektur = ja):**

1. **Sofort:** C1 auf Basis des getesteten Schedulers in den vorhandenen
   PR-#47-Session-Planer integrieren (der Planer liefert bereits Sessions,
   Identitäten, Claims; es ändert sich nur das Ausführungs-Backend von
   „1 Client/Bot“ auf „Slot in ⌈N/4⌉ Clients“). Erwartung laut Modell:
   8 unabhängig wirkende Sessions zum **gemessenen** A-Preis. Public-Smoke +
   Stunde als Gate.
2. **Parallel (billig, read-only):** Messaufträge M1–M5 ausführen → PSS-
   Wahrheit statt RSS-Schätzung, Prefix-/Xvfb-Kosten, RSS-Treppe 1/2/4
   lokale Spieler.
3. **Mittelfristig:** E1/E2 per Ghidra statisch klären; nur bei positivem
   Befund C2-Experiment. KSM/zram (K1–K3, Z1) isoliert testen — sie nützen
   auch C (mehrere Clients) und wären die einzige realistische Brücke, um B
   jemals auf diesem Host zu qualifizieren.
4. **B unverändert aufbewahren:** für einen größeren Host oder nach D-Erfolg;
   die PR-#47-Schutzmechanik (Gate 1068, Drain, Ghost-Quarantäne) bleibt
   maßgeblich und wird nicht aufgeweicht, um „8 passend zu rechnen“.

## 4. Konkreter Optimierungsplan (priorisiert, je mit Stop-Kriterium)

| # | Maßnahme | Erwartung (Evidenz) | Gate/Stop |
|---|---|---|---|
| O1 | C1-Backend im Session-Planer (Orchestrierung, kein Engine-Code) | 8 unabhängige Sessions @ ~419 MiB/69 % [D aus T] | Vierslot-Lifecycle-Test wie PR #47; Stop bei Join-Latenz > Batchfenster+60 s oder Sync-Regression |
| O2 | M1–M5 Messkampagne (read-only) | PSS/Prefix/Xvfb-Fakten [N→T] | nur Freigabefenster; kein Stop-Risiko |
| O3 | zram 512 MiB + `memory.high` im privaten Scope | +200–400 MiB effektiv [N] | 20-Hz-Telemetrie ACTIVE_OK, 0 neue SYNCBAD; Stop bei Latenzspikes |
| O4 | KSM via `PR_SET_MEMORY_MERGE`-Launcher (Kernel ≥ 6.4 prüfen: `ksm_probe.py`) | −15–40 % Anon-Marginal [N, Annahmeband] | K1 Dedup-Quote > 10 % sonst Abbruch; ksmd < 5 % Kern; Sync-Gate |
| O5 | Footprint: 320×240×16, Texture-Downsizing, `WINEDEBUG=-all`, Services trimmen | −20–60 MiB/Client [N] | A/B je Einzelmaßnahme nach Messprotokoll |
| O6 | E1/E2-Statik (Ghidra) → ggf. C2 | Restart-freie Slots [N] | E3-Sync-Abnahme zwingend vor jedem Einsatz |
| O7 | Level-3-Headless (`GAT_NONE`) | GL-Speicher entfällt [N] | nur gemäß Leiter in `2026-10-22-nullrender-and-headless-paths.md` |

## 5. Integrationsplan in die vorhandene Architektur

1. **Keine Änderung an main/Runtime jetzt:** dieser Branch liefert nur
   `poc/research/ram-efficiency/**` und `docs/research/ram-efficiency/**`.
2. **PR #47-Anschluss:** `bot_session_executor` erhält ein zweites Backend
   (`slot_backend`), das `slotplan.SlotPlanner` als Platzierungslogik nutzt;
   Claims/Ghost-Quarantäne/Gates bleiben unverändert, nur das Ziel eines
   „Join“ ist ein Slot statt ein Prozess. Der Scheduler ist absichtlich
   zustandsarm und seiteneffektfrei, damit er dort als Bibliothek einziehen
   kann.
3. **PR #50/#46-Verträglichkeit:** C1 reduziert die Prozesszahl → weniger
   Supervisor-Objekte; die Fail-closed-Pfade aus #50 gelten pro Client
   unverändert. Keine Überschneidung mit deren Dateien (hier wurde nichts
   davon angefasst).
4. **PR #51:** Die öffentliche Flotte bleibt unberührt; C1 würde erst nach
   eigener Qualifikation (Smoke → Stunde → Soak) die heutige statische
   Zweiclient-Flotte ersetzen und dabei äußerlich identisch aussehen
   (gleiche DLL, gleiche Profile, gleiche Query-Signatur).
5. **Abnahmegates (unverändert streng):** Hash-Pins, Vierslot-Lifecycle,
   Achtslot-Stunde, Vanilla-Gegenstelle, Sync-Null-Regression, Reserve-Gate.
   `NOT_TESTED` wird ausgewiesen, bis die Läufe real existieren.

## 6. Was dieser Branch ausdrücklich NICHT behauptet

- keinen gemessenen RAM-/CPU-Gewinn irgendeiner Optimierung (alles [N] bis
  zur Hetzner-Kampagne);
- keine Lauffähigkeit von C1/C2 zur Laufzeit — nur der Scheduler ist
  offline bewiesen;
- keine Entschärfung der bekannten Blocker (Achtbot-RAM-Gate, Drain-Timeout,
  externe SYNCBAD-Historie);
- keine Kapazitätsfreigabe für 16 Bots.
