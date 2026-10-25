#!/usr/bin/env python3
"""Client-/Server-Ereigniszuordnung: ordnet Server- und Client-Ereignisse
in eine gemeinsame Chronologie und erkennt Zuordnungslücken.

Quellen:
  * Server-Log (SYNCBAD/SYNCOK/SYNCLATE/SYNCEARLY/KICK/JOIN/LEAVE/MAP)
  * Client-Log (CLIENT_DISCONNECT, BOT_TICK, BOT_NOTE)

Erkennt:
  * Client-Disconnect-Zeilen ohne Server-KICK (zuordnungslos).
  * Server-KICKs ohne Client-Disconnect-Zeile (fragmentierter Client-Log).
  * Join-/Leave-Kette um den ersten KICK (Rejoin-Erkennung).

Die Client-Disconnect-Zeile trägt keine Client-ID; Zuordnung erfolgt
über das Vorkommen der Zeile. Cross-Log-Zeilenvergleich ist nicht
möglich (unterschiedliche Dateien).
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Dict, List

sys.path.insert(0, str(Path(__file__).resolve().parent))
from sync_forensics_common import (  # noqa: E402
    parse_server_log_events, parse_client_log_events, EVIDENCE_NOTE,
)


def map_events(server_log: str, client_log: str) -> Dict[str, object]:
    s_events = parse_server_log_events(server_log)
    c_events = parse_client_log_events(client_log)

    timeline: List[Dict[str, object]] = []
    for e in s_events:
        timeline.append({"source": "server", "line": e.line_no, **e.to_dict()})
    for e in c_events:
        timeline.append({"source": "client", "line": e.line_no, **e.to_dict()})
    timeline.sort(key=lambda x: (x["source"], x["line"]))

    server_has_kick = any(e.kind == "KICK" for e in s_events)
    client_disc_lines = [e for e in c_events if e.kind == "CLIENT_DISCONNECT"]

    # Client-Disconnect-Zeilen ohne zugeordneten Server-KICK.
    orphan_client_disconnects: List[Dict[str, object]] = []
    if client_disc_lines and not server_has_kick:
        orphan_client_disconnects.append({
            "count": len(client_disc_lines),
            "lines": [e.line_no for e in client_disc_lines],
            "detail": "Client-Disconnect-Zeile(n) ohne Server-KICK: Client-"
                      "seitige Trennung oder fragmentierter Server-Log",
        })

    # Server-KICKs ohne Client-Disconnect-Zeile.
    orphan_server_kicks: List[Dict[str, object]] = []
    if server_has_kick and not client_disc_lines:
        orphan_server_kicks = [
            {"line": e.line_no, "client": e.client}
            for e in s_events if e.kind == "KICK"
        ]

    # Join/Leave-Kette um den ersten KICK (Rejoin-Analyse).
    first_kick_line = next((e.line_no for e in s_events if e.kind == "KICK"), None)
    join_leave_around_kick: List[Dict[str, object]] = []
    if first_kick_line is not None:
        for e in s_events:
            if e.kind in ("JOIN", "LEAVE"):
                window = 200
                if abs(e.line_no - first_kick_line) <= window:
                    join_leave_around_kick.append({
                        "line": e.line_no, "kind": e.kind,
                        "client": e.client,
                        "offset_to_kick": e.line_no - first_kick_line,
                    })

    return {
        "event_counts": {
            "server": len(s_events), "client": len(c_events),
            "server_kinds": {k: sum(1 for e in s_events if e.kind == k)
                             for k in {e.kind for e in s_events}},
            "client_kinds": {k: sum(1 for e in c_events if e.kind == k)
                             for k in {e.kind for e in c_events}},
        },
        "timeline": timeline,
        "orphan_client_disconnects": orphan_client_disconnects,
        "orphan_server_kicks": orphan_server_kicks,
        "join_leave_around_first_kick": join_leave_around_kick,
        "first_server_kick_line": first_kick_line,
        "first_client_disconnect_line": (
            next((e.line_no for e in c_events if e.kind == "CLIENT_DISCONNECT"), None)
        ),
        "evidence_note": EVIDENCE_NOTE,
    }


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--server-log", required=True)
    ap.add_argument("--client-log", required=True)
    ap.add_argument("--out", help="Optional: JSON-Ausgabepfad")
    args = ap.parse_args()

    server_text = Path(args.server_log).read_text(encoding="utf-8", errors="replace")
    client_text = Path(args.client_log).read_text(encoding="utf-8", errors="replace")

    result = map_events(server_text, client_text)
    text = json.dumps(result, ensure_ascii=False, indent=2)
    if args.out:
        Path(args.out).write_text(text + "\n", encoding="utf-8")
    print(text)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
