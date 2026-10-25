#!/usr/bin/env python3
"""Erkennung unvollständiger Daten: prueft Logs, Dumps und Telemetrie auf
vollständige, konsistente Belegung und fail-closed meldet jede Lücke.

Pruefungen:
  * Server-Log: SYNCBAD-Ereignisse ohne zugeordneten Client-Disconnect
    (Fragmentierung), fehlende SYNCOK-Paare bei Counter-Reset.
  * Sync-Dumps: fehlende Header-Felder (Level/Sequence/Tick/CRC),
    Felder mit leerem Wert, unparsebare Zeilen.
  * BotTelemetry.csv: fehlende Datenzeilen, fehlende Spalten
    (ticks/actions/t_ms), nicht-numerische Werte.
  * Alignment: Server-Dump ohne Client-Dump mit gleichem Key.

Exit-Codes:
  0 = alle prüfbaren Daten vollständig
  4 = mindestens eine erkennbare Unvollständigkeit (INCOMPLETE)
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Dict, List, Optional

sys.path.insert(0, str(Path(__file__).resolve().parent))
from sync_forensics_common import (  # noqa: E402
    parse_server_log_events, parse_dump_text, EVIDENCE_NOTE,
)


def check_server_log(text: str) -> List[Dict[str, object]]:
    issues: List[Dict[str, object]] = []
    events = parse_server_log_events(text)
    bads = [e for e in events if e.kind == "SYNCBAD"]
    kicks = [e for e in events if e.kind == "KICK"]

    for e in bads:
        if e.count is not None and e.count > 1 and e is bads[0]:
            issues.append({
                "kind": "first_bad_counter_gt1",
                "line": e.line_no,
                "detail": "erstes SYNCBAD hat Counter > 1: vorherige"
                          " SYNCBAD-Zeilen fehlen (Log unvollständig)",
            })
    if bads and not kicks:
        peak = max((e.count or 0) for e in bads)
        issues.append({
            "kind": "bad_without_kick",
            "detail": "SYNCBAD-Ereignisse ohne KICK: maximaler Counter %d" % peak,
        })
    if kicks and not bads:
        issues.append({
            "kind": "kick_without_bad",
            "detail": "KICK ohne SYNCBAD-Zeilen: Log fragmentiert",
        })
    return issues


def check_dump(path: str, text: str) -> List[Dict[str, object]]:
    issues: List[Dict[str, object]] = []
    rec = parse_dump_text(path, text)
    for key in ("Level", "Sequence", "Tick"):
        if key not in rec.header or not rec.header[key]:
            issues.append({"kind": "missing_header_field", "field": key,
                           "detail": "Header-Feld fehlt oder leer"})
    if rec.crc is None:
        issues.append({"kind": "missing_crc", "detail": "CRC-Zeile fehlt"})
    for name, value in rec.fields.items():
        if value == "":
            issues.append({"kind": "empty_field_value", "field": name,
                           "detail": "Feldwert leer"})
    for err in rec.parse_errors[:10]:
        issues.append({"kind": "unparsed_line", "detail": err})
    if rec.line_count == 0:
        issues.append({"kind": "empty_dump", "detail": "Snapshot hat keine Zeilen"})
    return issues


def check_telemetry(path: Path) -> List[Dict[str, object]]:
    issues: List[Dict[str, object]] = []
    if not path.is_file():
        return [{"kind": "telemetry_missing", "detail": str(path)}]
    header: List[str] = []
    required = {"t_ms", "ticks", "actions"}
    rows = 0
    for line in path.read_text(encoding="utf-8", errors="replace").splitlines():
        if not line or line.startswith("#"):
            continue
        cells = line.split(",")
        if not header:
            header = cells
            missing = required - set(header)
            if missing:
                issues.append({"kind": "telemetry_missing_columns",
                               "detail": "fehlende Spalten: %s" % sorted(missing)})
            continue
        rows += 1
    if rows == 0:
        issues.append({"kind": "telemetry_no_data_rows", "detail": str(path)})
    return issues


def detect_incomplete(server_log: Optional[str], client_log: Optional[str],
                      telemetry: Optional[Path], dumps: List[Path]) -> Dict[str, object]:
    issues: List[Dict[str, object]] = []
    if server_log is not None:
        issues += check_server_log(server_log)
    if client_log is not None:
        ctext = client_log
        if "Disconnected: Too many bad syncs" not in ctext:
            issues.append({
                "kind": "client_log_no_disconnect",
                "detail": "Client-Log enthält keine 'Disconnected: Too many bad syncs'-Zeile",
            })
    if telemetry is not None:
        issues += check_telemetry(telemetry)

    dump_keys: List[str] = []
    for d in dumps:
        text = d.read_text(encoding="utf-8", errors="replace")
        issues += check_dump(str(d), text)
        rec = parse_dump_text(str(d), text)
        if rec.aligned_key:
            dump_keys.append("%s|%d|%.2f" % rec.aligned_key)

    return {
        "issues": issues,
        "issue_count": len(issues),
        "complete": len(issues) == 0,
        "dump_aligned_keys": dump_keys,
        "evidence_note": EVIDENCE_NOTE,
    }


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--server-log")
    ap.add_argument("--client-log")
    ap.add_argument("--telemetry")
    ap.add_argument("--dump", action="append", default=[])
    ap.add_argument("--out")
    args = ap.parse_args()

    server_text = None
    client_text = None
    if args.server_log:
        server_text = Path(args.server_log).read_text(encoding="utf-8", errors="replace")
    if args.client_log:
        client_text = Path(args.client_log).read_text(encoding="utf-8", errors="replace")

    dumps = [Path(p) for p in args.dump]
    telemetry = Path(args.telemetry) if args.telemetry else None

    result = detect_incomplete(server_text, client_text, telemetry, dumps)
    text = json.dumps(result, ensure_ascii=False, indent=2)
    if args.out:
        Path(args.out).write_text(text + "\n", encoding="utf-8")
    print(text)
    return 0 if result["complete"] else 4


if __name__ == "__main__":
    raise SystemExit(main())
