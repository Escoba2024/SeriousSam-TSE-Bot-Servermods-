#!/usr/bin/env python3
"""Read-only audit of Serious Sam TSE SYNCCHECK counters; never infers runtime PASS."""
import argparse
import json
import re
from pathlib import Path

TICK = r"\d+(?:\.\d+)?"  # Reject malformed numbers such as 12..3.
BAD = re.compile(rf"SYNCBAD: Client '([^']+)', Sequence (\d+) Tick ({TICK}) - bad (\d+)(?!\d)")
GOOD = re.compile(rf"SYNCOK: Client '([^']+)', Tick ({TICK})(?![\d.])")

def analyze(text):
    clients = {}
    bad = []
    ok = []
    disconnects = []
    for num, line in enumerate(text.splitlines(), 1):
        m = BAD.search(line)
        if m:
            client, seq, tick, count = m.groups()
            event = dict(line=num, client=client, sequence=int(seq),
                         tick=float(tick), count=int(count))
            bad.append(event)
            clients.setdefault(client, []).append(event)
        m = GOOD.search(line)
        if m:
            ok.append(dict(line=num, client=m[1], tick=float(m[2])))
        if "Too many bad syncs" in line and (
            "ordered to disconnect" in line or "Disconnected:" in line
        ):
            disconnects.append(dict(line=num, message=line.strip()[:160]))
    by_client = {}
    for name, events in clients.items():
        segments = []
        current = []
        for event in events:
            if current and event["count"] <= current[-1]["count"]:
                segments.append(current)
                current = []
            current.append(event)
        if current:
            segments.append(current)
        by_client[name] = {
            "bad_events": len(events),
            "max_reported_counter": max(v["count"] for v in events),
            "observed_segments": [{
                "first_tick": group[0]["tick"],
                "last_tick": group[-1]["tick"],
                "first_counter": group[0]["count"],
                "last_counter": group[-1]["count"],
                "events_seen": len(group),
            } for group in segments],
        }
    return {
        "bad_events": len(bad),
        "sync_ok_events": len(ok),
        "disconnect_events": len(disconnects),
        "disconnects": disconnects,
        "clients": by_client,
        "interpretation": "Log evidence only; this is not a stability PASS.",
    }

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("logs", nargs="+", help="Existing local SeriousSam/Dedicated log files")
    args = parser.parse_args()
    result = {}
    for raw in args.logs:
        f = Path(raw)
        if not f.is_file():
            parser.error("File not found: " + str(f))
        result[str(f)] = analyze(f.read_text(encoding="utf-8", errors="replace"))
    print(json.dumps(result, ensure_ascii=False, indent=2))

if __name__ == "__main__":
    main()
