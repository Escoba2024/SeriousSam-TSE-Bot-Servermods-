# TSE Sync-Forensics Werkzeuge

Reproduzierbare, offline-testbare Diagnosewerkzeuge für die
Multiplayer-Sync-/CRC-Analyse von Serious Sam TSE Classic 1.07.

**Status:** 25.10.2026 – Offline-Tools, keine Runtime-Änderung.

## Safety

- Alle Werkzeuge sind **read-only**: sie lesen Logs/Dumps/CSV und schreiben
  ausschließlich JSON-Belege.
- Es werden **keine Prozesse** gestartet, **keine DLLs** verändert,
  **keine Server** berührt.
- Alle Tests verwenden **synthetische Fixtures**; keine echten Logs,
  Binaries oder Spieldaten.
- Fail-closed: UNALIGNED/INCOMPLETE statt erfundener Divergenz;
  Log-Diagnosen sind **keine Root-Cause-Bestätigungen**.

## Werkzeuge

| Werkzeug | Aufgabe | Exit-Codes |
|----------|---------|------------|
| `sync_correlator.py` | Server-SYNCBAD/KICK mit Client-Disconnect + BotTelemetry korrelieren | 0 |
| `sync_tick_compare.py` | Tick-Serien, Counter-Jump-Erkennung | 0 |
| `sync_crc_diff.py` | aligned Sync-Dump-Vergleich (Felder/CRC), fail-closed | 0 identisch / 3 divergent / 2 unalignbar |
| `sync_event_mapper.py` | Client/Server-Ereignischronologie, orphan-Events | 0 |
| `sync_error_classifier.py` | E1–E6-Fehlerklassifizierung | 0 |
| `sync_incomplete_detector.py` | Unvollständigkeitserkennung (fail-closed) | 0 vollständig / 4 incomplete |
| `make_synthetic_logs.py` | Deterministische synthetische Fixtures | 0 |

## Tests

```bash
cd poc/research/sync-forensics
python3 -m unittest discover -s tests -v
```

Ergebnis: **29/29 PASS** (Python 3.11, Linux-Sandbox).

## Nutzung am echten Log

```bash
# 1. Fehlerklassifizierung
python3 tools/sync_error_classifier.py /path/to/server.log

# 2. Server/Client-Korrelation
python3 tools/sync_correlator.py \
    --server-log /path/to/server.log \
    --client-log /path/to/client.log \
    --telemetry /path/to/BotTelemetry.csv

# 3. Tick-Vergleich
python3 tools/sync_tick_compare.py \
    --server-log /path/to/server.log \
    --client-log /path/to/client.log \
    --telemetry /path/to/BotTelemetry.csv

# 4. aligned Dump-Vergleich (erfordert echte cli_bDumpSync-Dumps)
python3 tools/sync_crc_diff.py \
    --server-dir /path/to/server-dumps \
    --client-dir /path/to/client-dumps

# 5. Ereigniszuordnung
python3 tools/sync_event_mapper.py \
    --server-log /path/to/server.log \
    --client-log /path/to/client.log

# 6. Unvollständigkeitsprüfung
python3 tools/sync_incomplete_detector.py \
    --server-log /path/to/server.log \
    --client-log /path/to/client.log \
    --telemetry /path/to/BotTelemetry.csv \
    --dump /path/to/server-dump.txt \
    --dump /path/to/client-dump.txt
```

## Dokumentation

- Hauptbericht: [`docs/research/sync-forensics/2026-10-25-sync-root-cause-analysis.md`](../../../docs/research/sync-forensics/2026-10-25-sync-root-cause-analysis.md)
- Grundlage: [Retail-1.07-Sync-Check-Untersuchung](../../../docs/reports/2026-10-17-retail107-sync-check-investigation.md)
- PR #21 (Sync-Dump-Pfad, 4-Byte-CRC): https://github.com/Escoba2024/SeriousSam-TSE-Bot-Servermods-/pull/21
- PR #54 (CecilBotMod, Ground-Lookahead-Risiko): https://github.com/Escoba2024/SeriousSam-TSE-Bot-Servermods-/pull/54
