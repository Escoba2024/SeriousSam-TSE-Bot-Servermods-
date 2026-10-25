# Session-Hybrid-Lab – CPU-/RAM-/PSS-Messplan

**Datum:** 2026-10-25 · **Status:** Vorschlag, keine Live-Messung · **Evidenz:** übernimmt Messaufträge M1–M5 von PR #56 ([T] zitiert, [N] offen)

> **Wichtig:** In der LMArena-Sandbox wurde kein Wine-/Retail-Benchmark
> ausgeführt. Kein Wert aus diesem Dokument ist ein Spielmesswert. Alle
> Messungen erfordern explizite Operator-Autorisierung auf dem autorisierten
> Wine-Host (analog `TSE_RAM_BENCH_AUTHORIZED=1` in PR #56) und dürfen keine
> produktiven Prozesse/Ports berühren.

## 1. Ziele der Verbesserung

Die bestehenden Messwerte (RSS, cgroup-Peak, CPU) sollen um folgende Größen
ergänzt werden, wie im Auftrag gefordert (Aufgabe 11):

* **PSS** (Proportional Set Size) als Leitmetrik für ehrliche Pro-Client-
  Attribution geteilter Wine-Seiten (statt RSS, das geteilte Seiten mehrfach
  zählt) [N];
* **USS** (Unique Set Size) – was ein Client-Exit wirklich freigibt [N];
* **Speicher-Peak** über `memory.peak` pro Phase [N];
* **Scheduler-Overhead** und **Anzahl aktiver Sessions** aus dem Hybrid-Lab
  [O-Prototyp];
* **Fehlerraten** (SYNCBAD, Disconnect, Join-Fehler) als Telemetrie-Gate [T aus PR #45].

## 2. Übernommene Messaufträge (aus PR #56, unverändert gültig)

| Auftrag | Zweck | Status |
|---|---|---|
| M1 | Prozessinventur je Architektur (SeriousSam.exe, DedicatedServer.exe, wineserver, Xvfb, Dienste) | [N] |
| M2 | PSS-Wahrheit: PSS vs. RSS je Client-Gruppe; ersetzt RSS-Basis im Modell | [N] |
| M3 | Driftprofil: 3600-s-Fenster, lineare Regression PSS über Zeit; > 1 MiB/h = Leck-Verdacht | [N] |
| M4 | CPU-Threadsplit (llvmpipe vs. Mainthread) parallel zu memsample | [N] |
| M5 | RSS/PSS-Treppe lokale Spieler: identischer Client mit 1/2/4 Spielern | [N] |

## 3. Messverfahren (übernommen, unverändert)

* Warm-up 180 s, Messfenster ≥ 600 s, Intervall 5 s (≥ 120 Samples) – identisch zum etablierten CPU-Protokoll (`docs/reports/2026-10-22-cpu-measurement-protocol.md`).
* Peak-Werte aus `memory.peak` (nach Phasenstart zurücksetzen, wo Kernel das unterstützt, sonst Phase in frischer cgroup starten).
* Jede Messung erzeugt `provenance.json` (Host, Kernel, UTC, Modus, Parameter).
* Rohlogs/Profile bleiben privat; nur bereinigte Aggregate in Git.
* Telemetrie-Gate (ACTIVE_OK, 20 Hz, 0 SYNCBAD) ist Bestandteil jedes PASS – ein RAM-Wert ohne gesunde Action-Pipeline ist wertlos.

## 4. Szenariomatrix (isolierte Fenster)

| Szenario | Architektur | Zweck |
|---|---|---|
| S-A8 | A (2×4) | Referenz, Abgleich mit 69 % / 419 MiB [T] |
| S-B1 / S-B4 | B (1×1 / 4×1) | Reproduzierbarkeitsnachweis des Harness |
| S-C8 | C1 (2×4 + Scheduler) | wie S-A8 plus Join/Leave-Trace aus dem Hybrid-Lab |
| S-H2 | 4×2 | M5-Treppe im Flottenkontext |

## 5. Auswertung und Rückfluss

1. JSONL-Samples → Mittel/P95/Peak je Gruppe.
2. `measurements.json` aktualisieren: neue Anker ersetzen Projektionen;
   Evidenzfeld anheben (z. B. DERIVED → MEASURED_HETZNER), Quelle = Berichtspfad.
3. Modell neu generieren (`resource_model_hybrid.py`) und die Tabellen in
   `2026-10-25-resource-model-hybrid.md` ersetzen. Diskrepanzen > 15 % zwischen
   alter Projektion und neuer Messung sind im Bericht auszuweisen.
4. Keine Zahl aus Simulate-/Fixture-Läufen darf in `measurements.json`
   aufgenommen werden.

## 6. Grenzbedingungen

* Kein Lauf ohne explizite Autorisierung.
* Der Harness bricht ab, wenn laufende `SeriousSam.exe`/`DedicatedServer.exe`
  erkannt werden (außer Coexistence-Ack nach Isolationsprüfung).
* Keine Testclients auf produktiven Ports; keine Serverneustarts;
  keine produktiven Hetzner-Prozesse geändert.
