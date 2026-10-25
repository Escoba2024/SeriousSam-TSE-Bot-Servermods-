#!/usr/bin/env python3
"""Log-Korrelation: Server-SYNCBAD/SYNCOK/KICK Events mit Client-Log und
BotTelemetry.csv in einem gemeinsamen Zeitstrahl verbinden.

Nutzen:
  * Korreliert den Server-Sync-Status pro Client mit clientseitigen
    Disconnect-Meldungen und Bot-Aktivität (Ticks/Actions).
  * Erkennt Server-KICKs, wenn der Client-Log keine Disconnect-Meldung
    zeigt (geteilte Session / fragmentierter Client-Log).
  * Erkennt Client-Disconnect-Meldungen ohne Server-KICK.
  * Erkennt Clients, die nach einem KICK wieder verbinden (Rejoin).

Die Client-Disconnect-Zeile ("Disconnected: Too many bad syncs") trägt
keine Client-ID; die Zuordnung erfolgt daher über das Vorkommen der
Zeile, nicht über eine ID. Zeilennummern aus Server- und Client-Log
dürfen NICHT verglichen werden (unterschiedliche Dateien).

Das Werkzeug lesen nur lokale Logs; es startet keine Prozesse.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Dict, List, Optional

sys.path.insert(0, str(Path(__file__).resolve().parent))
from sync_forensics_common import (  # noqa: E402
    parse_server_log_events, parse_client_log_events, EVIDENCE_NOTE,
)


def parse_bot_telemetry_csv(path: Path) -> List[Dict[str, object]]:
    """Liest BotTelemetry.csv; die #columns-Zeile liefert den Header."""
    rows: List[Dict[str, object]] = []
    header: Optional[List[str]] = None
    if not path.is_file():
        return rows
    for line in path.read_text(encoding="utf-8", errors="replace").splitlines():
        if not line:
            continue
        if line.startswith("#columns"):
            header = line.split(",", 1)[1].split(",") if "," in line else []
            continue
        if line.startswith("#"):
            continue
        cells = line.split(",")
        if header is None:
            header = cells
            continue
        row: Dict[str, object] = {}
        for i, name in enumerate(header):
            raw = cells[i] if i < len(cells) else ""
            try:
                row[name] = float(raw) if ("." in raw or raw.lstrip("-").isdigit()) else raw
            except ValueError:
                row[name] = raw
        rows.append(row)
    return rows


def correlate(server_log: str, client_log: Optional[str],
              telemetry_rows: List[Dict[str, object]]) -> Dict[str, object]:
    """Stellt Server-Events, Client-Events und Telemetrie nebeneinander."""
    server_events = parse_server_log_events(server_log)
    client_events = parse_client_log_events(client_log or "")

    server_bad = [e for e in server_events if e.kind == "SYNCBAD"]
    server_kick = [e for e in server_events if e.kind == "KICK"]
    server_ok = [e for e in server_events if e.kind == "SYNCOK"]
    client_disc = [e for e in client_events if e.kind == "CLIENT_DISCONNECT"]
    client_ticks = [e for e in client_events if e.kind == "BOT_TICK"]

    kick_clients = sorted({e.client for e in server_kick if e.client})
    client_disconnect_present = len(client_disc) > 0

    per_client: Dict[str, object] = {}
    for client in kick_clients:
        bads = [e for e in server_bad if e.client == client]
        oks = [e for e in server_ok if e.client == client]
        per_client[client] = {
            "bad_events": len(bads),
            "first_bad_tick": bads[0].tick if bads else None,
            "last_bad_tick": bads[-1].tick if bads else None,
            "max_bad_counter": max((e.count or 0) for e in bads) if bads else 0,
            "sync_ok_events": len(oks),
            "server_kicks": 1,
        }

    return {
        "server_bad_events": len(server_bad),
        "server_kick_events": len(server_kick),
        "server_sync_ok_events": len(server_ok),
        "client_disconnect_events": len(client_disc),
        "client_bot_tick_events": len(client_ticks),
        "telemetry_rows": len(telemetry_rows),
        "telemetry_first_t_ms": telemetry_rows[0].get("t_ms") if telemetry_rows else None,
        "telemetry_last_t_ms": telemetry_rows[-1].get("t_ms") if telemetry_rows else None,
        "kick_without_client_disconnect": (
            kick_clients if not client_disconnect_present else []
        ),
        "client_disconnect_without_server_kick": (
            [{"client": "unknown", "count": len(client_disc),
              "detail": "Client-Disconnect-Zeile(n) ohne Server-KICK"}]
            if client_disconnect_present and not server_kick else []
        ),
        "per_client": per_client,
        "cross_log_line_note": (
            "Zeilennummern aus Server- und Client-Log dürfen nicht verglichen "
            "werden; für echte Ereigniszuordnung brauchen wir Timestamps oder "
            "gemeinsame Ticks (siehe sync_event_mapper.py + natives Protokoll)."
        ),
        "evidence_note": EVIDENCE_NOTE,
    }


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--server-log", required=True, help="Server-Dedicated-Log")
    ap.add_argument("--client-log", help="Optional: Client-SeriousSam-Log")
    ap.add_argument("--telemetry", help="Optional: BotTelemetry.csv")
    ap.add_argument("--out", help="Optional: JSON-Ausgabepfad")
    args = ap.parse_args()

    telemetry: List[Dict[str, object]] = []
    if args.telemetry:
        telemetry = parse_bot_telemetry_csv(Path(args.telemetry))

    server_text = Path(args.server_log).read_text(encoding="utf-8", errors="replace")
    client_text = ""
    if args.client_log:
        client_text = Path(args.client_log).read_text(encoding="utf-8", errors="replace")

    result = correlate(server_text, client_text, telemetry)
    text = json.dumps(result, ensure_ascii=False, indent=2)
    if args.out:
        Path(args.out).write_text(text + "\n", encoding="utf-8")
    print(text)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
