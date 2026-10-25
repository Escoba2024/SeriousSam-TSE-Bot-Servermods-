# Reproduzierbares RAM-/CPU-Messverfahren für die Wine-Bot-Flotte

**Datum:** 2026-10-25 · **Werkzeuge:** `poc/research/ram-efficiency/`
(`memsample.py`, `ksm_probe.py`, `bench_harness.sh`, `resource_model.py`) ·
**Geltungsbereich:** isolierte, autorisierte Messfenster auf dem Wine-Host.
**In der LMArena-Sandbox wurde nur der Simulate-Modus (Dummy-Prozesse) und
die Fixture-Testsuite ausgeführt; kein Wert daraus ist ein Spielmesswert.**

## 0. Verbindliche Schutzregeln

1. Kein Lauf ohne explizite Operator-Autorisierung
   (`TSE_RAM_BENCH_AUTHORIZED=1`); der Harness verweigert sonst (Exit 3).
2. Erkennt der Harness laufende `SeriousSam.exe`/`DedicatedServer.exe`,
   bricht er ab, sofern nicht `TSE_RAM_BENCH_COEXIST_ACK=1` **nach**
   dokumentierter Isolationsprüfung (eigene Ports/Prefixe/cgroup, Preflight
   analog `Test-TSEExternalVanillaPreflight`) gesetzt wurde.
3. Alle Messungen sind **read-only** gegenüber fremden Prozessen; Start und
   Stop der Messclients erfolgt ausschließlich über die vorhandenen
   qualifizierten Runner (PR #47/Fleet-Skripte), nie durch den Harness.
4. Jede Messung erzeugt `provenance.json` (Host, Kernel, UTC, Modus,
   Parameter). Ergebnisse ohne Provenienzdatei sind ungültig.
5. Rohlogs/Profile bleiben privat auf dem Host; nur bereinigte Aggregate in
   Git (bestehende Repo-Regel).

## 1. Messgrößen und Begriffe

| Größe | Quelle | Warum |
|---|---|---|
| RSS | `smaps_rollup:Rss` | Vergleichbarkeit mit Altberichten; zählt geteilte Seiten mehrfach |
| **PSS** | `smaps_rollup:Pss` | ehrliche Pro-Client-Attribution geteilter Seiten — **Leitmetrik** |
| USS | `Private_Clean+Private_Dirty` | was ein Client-Exit real freigibt |
| cgroup | `memory.current/peak`, `memory.stat(anon,file)` | Gate-Relevanz (PR #47 misst so) |
| CPU | `/proc/<pid>/stat`-Deltas, `cpu.stat` | Kern-%-Vergleich mit Altberichten |
| MemAvailable | `/proc/meminfo` | die Größe, gegen die das 1068-MiB-Gate prüft |

Warm-up 180 s, Messfenster ≥ 600 s, Intervall 5 s (≥ 120 Samples) — identisch
zum etablierten CPU-Protokoll (`docs/reports/2026-10-22-cpu-measurement-protocol.md`).
Peak-Werte zusätzlich aus `memory.peak` (nach Phasenstart zurücksetzen, wo
Kernel das unterstützt, sonst Phase in frischer cgroup starten).

## 2. Messaufträge (read-only, Priorität absteigend)

**M1 – Prozessinventur je Architektur:**
`memsample.py --match 'SeriousSam\.exe' --label client --match
'DedicatedServer\.exe' --label server --match 'wineserver' --label
wineserver --match 'services\.exe|winedevice|plugplay|rpcss|explorer\.exe'
--label wine-services --match 'Xvfb' --label xvfb --count 120 --interval 5`.
Liefert erstmals belegte Prefix-/Xvfb-/Servicekosten (offene Punkte 1, 4, 7
der Analyse).

**M2 – PSS-Wahrheit:** gleiche Läufe, Auswertung PSS vs. RSS je Gruppe.
Erwartung (unbewiesen): A-Clients teilen erheblich (gemeinsames Lower +
Wine); B-Clients weniger. Ergebnis ersetzt die RSS-Basis im Modell
(`measurements.json` aktualisieren, Evidenz auf MEASURED heben).

**M3 – Driftprofil:** 3600-s-Fenster, lineare Regression PSS über Zeit je
Client; > 1 MiB/h = Leck-Verdacht → gezielte Frida-/Allocator-Analyse gemäß
AGENTS.md-Regeln.

**M4 – CPU-Threadsplit:** vorhandenen `tools/benchmarks/tse_cpu_profile.py`
parallel zu `memsample` laufen lassen (llvmpipe- vs. Mainthread-Anteil nach
NullRender).

**M5 – RSS/PSS-Treppe lokale Spieler:** identischer Client mit 1/2/4 lokalen
Spielern, je 600 s. Beantwortet, ob 4×2 eine sinnvolle Zwischenstufe wäre
und wie viel ein zusätzlicher lokaler Spieler wirklich kostet (erstmals
marginale Pro-Bot-RAM-Zahl).

## 3. Szenariomatrix (isolierte Fenster, je ≥ 600 s nach Warm-up)

| Szenario | Architektur | Clients×Slots | Zweck |
|---|---|---:|---|
| S-A8 | A | 2×4 | Referenz; Abgleich mit 69 %/419 MiB [T] |
| S-B1/S-B4 | B | 1×1 / 4×1 | Abgleich mit 555,8/1158,0 MiB [T] — Reproduzierbarkeitsnachweis des Harness |
| S-B8 | B | 8×1 | nur ohne Publikflotte und nur bis Gate; Peak + MemAvailable-Kurve |
| S-C8 | C1 | 2×4 + Scheduler | wie S-A8 plus Join/Leave-Trace aus `slotplan.py`-Beispiel |
| S-H2 | 4×2 | 4×2 | M5-Treppe im Flottenkontext |

Jedes Szenario: `bench_harness.sh real --launch-file <runner-cmds> --cgroup
<private-cgroup> --duration 600 --interval 5`; Telemetrie-Gate (ACTIVE_OK,
20 Hz, 0 SYNCBAD) ist Bestandteil des PASS — ein RAM-Wert ohne gleichzeitig
gesunde Action-Pipeline ist wertlos.

## 4. Optimierungs-Gates (erst nach M1/M2)

**K1 – KSM-Potenzial (read-only):** `ksm_probe.py` → Kernel/prctl-Fähigkeit.
**K2 – KSM-Pilot:** nur isolierte Testclients mit
`PR_SET_MEMORY_MERGE`-Wrapper; Erfolgskriterium Dedup > 10 % des
Anon-Bestands bei ksmd < 5 % Kern, sonst Abbruch. **K3 – Sync-Neutralität:**
600 s mit Vanilla-Gegenstelle, 0 neue SYNCBAD.
**Z1 – zram-Pilot:** 512 MiB zram, `memory.high` unterhalb Gate; Kriterium:
keine 20-Hz-Degradation (tick_hz_min ≥ 19), Latenz-P99 der Actions stabil.

## 5. Auswertung und Rückfluss

1. JSONL-Samples → Mittel/P95/Peak je Gruppe; Skript-frei mit `jq` oder
   direkt in `resource_model.py`-Anker überführen.
2. `measurements.json` aktualisieren (neue Anker **ersetzen** Projektionen;
   Evidenzfeld anheben, Quelle = Berichtspfad des neuen Laufs).
3. Modell neu generieren und die Tabellen in
   `2026-10-25-architecture-comparison.md` ersetzen — Diskrepanzen > 15 %
   zwischen alter Projektion und neuer Messung sind im Bericht auszuweisen.
4. Keine Zahl aus Simulate-/Fixture-Läufen darf in `measurements.json`
   aufgenommen werden (Tag `"source": "fixture"` ist das maschinenlesbare
   Verbotskriterium).
