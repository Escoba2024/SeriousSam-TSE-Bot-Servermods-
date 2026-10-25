# RAM-/CPU-Effizienz-Werkzeuge für die Wine-Bot-Flotte (Retail 1.07)

Offline entwickelte, isolierte Prototypen zur Untersuchung „RAM/CPU pro
unabhängigem Bot“. **Nichts hier startet, verändert oder beendet produktive
Prozesse.** Analyse und Pläne: [`docs/research/ram-efficiency/`](../../../docs/research/ram-efficiency/2026-10-25-ram-analysis.md).

> **Provenienz:** In der LMArena-Sandbox existiert keine Wine-/Retail-
> Laufzeit. Alles hier wurde ausschließlich gegen synthetische Fixtures und
> Dummy-Prozesse getestet („Offline getestet“). Kein Werkzeug-Output aus
> dieser Umgebung ist ein Spielmesswert.

## Inhalt

| Datei | Zweck | Teststatus |
|---|---|---|
| `memsample.py` | RSS/**PSS**/USS-, cgroup- und CPU-Sampler je Prozessgruppe (read-only, JSONL) | 9 Unit-Tests gegen /proc-Fixtures |
| `resource_model.py` | Ressourcenmodell 1/4/8/16 Bots für Architekturen A/B/C/D; jede Zelle mit Evidenz-Tag | 11 Unit-Tests inkl. Fit-Validierung gegen unabhängigen Redstation-Lauf |
| `measurements.json` | Gemessene Hetzner-Anker mit Quellenzitat — einzige Dateneingabe des Modells | von Tests konsumiert |
| `slotplan.py` | Hybrid-Architektur-C-Prototyp: Session→Slot-Scheduler (DYNAMIC_SLOT / ROSTER_RESTART) | 11 Unit-Tests (Packung, Hysterese, Batching, Invarianten) |
| `ksm_probe.py` | Read-only-KSM-Probe: Verfügbarkeit, prctl-Fähigkeit (Kernel ≥ 6.4), Ersparnis nach Kernel-Doku | 5 Unit-Tests gegen sysfs-Fixtures |
| `bench_harness.sh` | Reproduzierbarer Benchmark-Harness; `simulate` offline, `real` doppelt verriegelt (Env-Flag + Launch-Datei, Koexistenz-Abbruch) | Simulate-Modus in Sandbox ausgeführt; `real` absichtlich nie |

## Schnellstart

```sh
# komplette Offline-Testsuite (35 Tests)
python3 -m unittest discover -s . -p 'test_*.py'

# Ressourcenmodell ansehen (Markdown-Tabelle, Evidenz je Zeile)
python3 resource_model.py
python3 resource_model.py --coexist-public --format json

# Scheduler-Prototyp mit Beispiel-Trace
printf '0 b1 JOIN\n60 b2 JOIN\n120 b1 LEAVE\n' > /tmp/trace.txt
python3 slotplan.py /tmp/trace.txt --mode ROSTER_RESTART

# Harness-Plumbing offline prüfen (Dummy-Prozesse, KEIN Spielmesswert)
./bench_harness.sh simulate --clients 4 --duration 10 --out /tmp/ram-bench
```

Echte Messungen: nur nach dem Protokoll in
[`docs/research/ram-efficiency/2026-10-25-measurement-protocol.md`](../../../docs/research/ram-efficiency/2026-10-25-measurement-protocol.md)
(Autorisierung, Isolation, Provenienzdatei, Telemetrie-Gate).
