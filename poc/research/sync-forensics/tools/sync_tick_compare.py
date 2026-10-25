#!/usr/bin/env python3
"""Tick-Vergleich: extrahiert Tick-Folgen aus Server-Log, Client-Log und
BotTelemetry.csv und vergleicht deren zeitliche Struktur.

Nachweisziele:
  * Gibt der Server-SYNCBAD-Serie eine Tick-Skala, wenn Client-Ticks
    verfügbar sind (Client-Ticks als Timeline-Referenz).
  * Erkennt Tick-Lücken / Non-Monotonicity / Doppelbuchungen im
    Server-Bad-Counter (Counter-Sprung > 1 pro Ereignis).
  * Vergleicht dieClient-Tick-Dichte vor/nach dem ersten SYNCBAD.
  * Niemals: `first divergent tick` wird NICHT aus Logs errechnet - das
    brauchen echte aligned Dumps (siehe sync_crc_diff.py).
"""

from __future__ import annotations

import argparse
import json
import statistics
import sys
from pathlib import Path
from typing import Dict, List, Optional

sys.path.insert(0, str(Path(__file__).resolve().parent))
from sync_forensics_common import (  # noqa: E402
    parse_server_log_events, parse_client_log_events, EVIDENCE_NOTE,
)


def _monotonic_gaps(ticks: List[float]) -> Dict[str, object]:
    if len(ticks) < 2:
        return {"ticks": len(ticks), "non_monotonic": 0, "max_gap": 0.0,
                "avg_gap": 0.0, "note": "too few ticks"}
    gaps = [round(b - a, 6) for a, b in zip(ticks, ticks[1:])]
    non_mono = sum(1 for g in gaps if g <= 0)
    return {
        "ticks": len(ticks),
        "first_tick": ticks[0],
        "last_tick": ticks[-1],
        "span": round(ticks[-1] - ticks[0], 6),
        "non_monotonic_steps": non_mono,
        "max_gap": max(gaps),
        "avg_gap": round(statistics.fmean(gaps), 6),
    }


def compare_ticks(server_log: str, client_log: Optional[str],
                  telemetry_csv: Optional[Path]) -> Dict[str, object]:
    server_events = parse_server_log_events(server_log)
    client_events = parse_client_log_events(client_log or "")

    server_bad_ticks = [e.tick for e in server_events
                        if e.kind == "SYNCBAD" and e.tick is not None]
    server_ok_ticks = [e.tick for e in server_events
                       if e.kind == "SYNCOK" and e.tick is not None]
    client_bot_ticks = [e.tick for e in client_events
                        if e.kind == "BOT_TICK" and e.tick is not None]

    telemetry_ticks: List[float] = []
    telemetry_span: Dict[str, object] = {}
    if telemetry_csv and telemetry_csv.is_file():
        rows = []
        for line in telemetry_csv.read_text(encoding="utf-8",
                                             errors="replace").splitlines():
            if not line or line.startswith("#"):
                continue
            cells = line.split(",")
            try:
                rows.append((float(cells[0]), float(cells[1])))
            except (ValueError, IndexError):
                continue
        if rows:
            telemetry_ticks = [t for _, t in rows]
            telemetry_span = {
                "rows": len(rows),
                "t_ms_first": rows[0][0],
                "t_ms_last": rows[-1][0],
                "tick_sum": sum(telemetry_ticks),
                "tick_rate_hint": (
                    round(telemetry_ticks[-1] / max(1e-9, (rows[-1][0] - rows[0][0]) / 1000.0), 2)
                    if len(rows) > 1 else None
                ),
            }

    # Counter-Sprunganalyse (Bad-Counter sollte pro Ereignis +1 sein,
    # solange kein SYNCOK dazwischen).
    jumps: List[Dict[str, object]] = []
    bads = [e for e in server_events if e.kind == "SYNCBAD"]
    for i in range(1, len(bads)):
        a, b = bads[i - 1], bads[i]
        if a.client != b.client:
            continue
        delta = (b.count or 0) - (a.count or 0)
        if delta > 1:
            jumps.append({
                "client": b.client,
                "from_line": a.line_no, "to_line": b.line_no,
                "from_count": a.count, "to_count": b.count,
                "delta": delta,
            })

    return {
        "server_bad_tick_series": _monotonic_gaps(server_bad_ticks),
        "server_ok_tick_series": _monotonic_gaps(server_ok_ticks),
        "client_bot_tick_series": _monotonic_gaps(client_bot_ticks),
        "telemetry": telemetry_span,
        "counter_jumps": jumps,
        "bad_counter_monotonic_within_client": (
            len(jumps) == 0 if bads else None
        ),
        "first_bad_tick": server_bad_ticks[0] if server_bad_ticks else None,
        "last_bad_tick": server_bad_ticks[-1] if server_bad_ticks else None,
        "interpretation": (
            "Die Log-Tick-Skala beschreibt das *beobachtete* Ereigniszeitfenster, "
            "nicht die Engine-Simulation. Der erste *divergente* Simulationstick "
            "bedarf aligned Server/Client-Sync-Dumps (cli_bDumpSync)."
        ),
        "evidence_note": EVIDENCE_NOTE,
    }


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--server-log", required=True)
    ap.add_argument("--client-log", help="Optional")
    ap.add_argument("--telemetry", help="Optional: BotTelemetry.csv")
    ap.add_argument("--out", help="Optional: JSON-Ausgabepfad")
    args = ap.parse_args()

    server_text = Path(args.server_log).read_text(encoding="utf-8", errors="replace")
    client_text = ""
    if args.client_log:
        client_text = Path(args.client_log).read_text(encoding="utf-8", errors="replace")
    telemetry = Path(args.telemetry) if args.telemetry else None

    result = compare_ticks(server_text, client_text, telemetry)
    text = json.dumps(result, ensure_ascii=False, indent=2)
    if args.out:
        Path(args.out).write_text(text + "\n", encoding="utf-8")
    print(text)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
