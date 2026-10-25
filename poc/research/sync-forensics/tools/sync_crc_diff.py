#!/usr/bin/env python3
"""CRC-Differenzen: Vergleich aligned Sync-Dump-Snapshots (Server vs Client)
fuer identische Level/Sequence/Tick.

Berechtigungen:
  * Ein Snapshot muss Level, Sequence und Tick mit dem Gegenstück
    sharing. Unterschiedliche Alignment-Keys -> UNALIGNED (Exit 2),
    niemals veraenderter Vergleich.
  * Feldunterschiede werden mit Feldname, Linie und Kategorie
    (session / player_action / player_entity / unknown) gemeldet.
  * Werte werden nicht ausgegeben; nur Feldnamen + Kategorien +
    positionsbasierte Differenzliste. Spieler- und GUID-Daten nie.
  * Erster *tatsächlich* divergenter Tick wird nur gemeldet, wenn beide
    Serien aligned vorhanden sind; fehlende Gegenstucke -> INCOMPLETE.

Exit-Codes:
  0 = aligned und identisch
  3 = aligned, aber CRC/Zustand abweichend
  2 = nicht alignbar / unvollständig / invalid
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Dict, List, Optional, Tuple

sys.path.insert(0, str(Path(__file__).resolve().parent))
from sync_forensics_common import (  # noqa: E402
    DumpRecord, parse_dump_text, classify_field, EVIDENCE_NOTE,
)

EXIT_IDENTICAL = 0
EXIT_UNALIGNED = 2
EXIT_INCOMPLETE = 2
EXIT_DIVERGENT = 3


def compare_snapshot(server: DumpRecord, client: DumpRecord) -> Dict[str, object]:
    sk, ck = server.aligned_key, client.aligned_key
    if sk is None or ck is None:
        return {"status": "UNALIGNED",
                "reason": "missing header Level/Sequence/Tick",
                "server_key": sk, "client_key": ck}
    if sk != ck:
        return {"status": "UNALIGNED", "reason": "alignment keys differ",
                "server_key": list(sk), "client_key": list(ck)}

    result: Dict[str, object] = {"status": "COMPARABLE", "level": sk[0],
                                 "sequence": sk[1], "tick": sk[2]}
    if server.crc is not None and client.crc is not None:
        result["crc_server"] = "0x%08X" % server.crc
        result["crc_client"] = "0x%08X" % client.crc
        result["crc_equal"] = server.crc == client.crc
    else:
        result["crc_equal"] = None
        result["crc_note"] = "CRC-Zeile fehlt in mindestens einem Snapshot"

    diffs: List[Dict[str, object]] = []
    for name in sorted(set(server.fields) | set(client.fields)):
        sv = server.fields.get(name)
        cv = client.fields.get(name)
        if sv != cv:
            diffs.append({
                "field": name,
                "category": classify_field(name),
                "server_line_no": _field_line(server, name),
                "client_line_no": _field_line(client, name),
            })
    result["field_differences"] = diffs
    result["field_difference_count"] = len(diffs)
    result["crc_divergent_or_fields_divergent"] = (
        (result.get("crc_equal") is False) or len(diffs) > 0
    )
    return result


def compare_series(server_dir: Path, client_dir: Path) -> Dict[str, object]:
    """Serienanalyse: mindestens ein aligned Paar muss existieren."""
    server_dumps = sorted(server_dir.glob("*.txt")) if server_dir.is_dir() else []
    client_dumps = sorted(client_dir.glob("*.txt")) if client_dir.is_dir() else []
    if not server_dumps or not client_dumps:
        return {"status": "INCOMPLETE", "reason": "missing snapshot files"}

    srecs = [parse_dump_text(str(p), p.read_text(encoding="utf-8", errors="replace"))
             for p in server_dumps]
    crecs = [parse_dump_text(str(p), p.read_text(encoding="utf-8", errors="replace"))
             for p in client_dumps]

    smap = {r.aligned_key: r for r in srecs if r.aligned_key}
    cmap = {r.aligned_key: r for r in crecs if r.aligned_key}
    aligned_keys = sorted(set(smap) & set(cmap))
    unmatched_server = sorted(set(smap) - set(cmap))
    unmatched_client = sorted(set(cmap) - set(smap))

    if not aligned_keys:
        return {"status": "UNALIGNED", "reason": "no common Level/Sequence/Tick",
                "server_keys": [list(k) for k in smap],
                "client_keys": [list(k) for k in cmap]}

    first_divergence: Optional[Dict[str, object]] = None
    compared = 0
    for key in aligned_keys:
        cmp = compare_snapshot(smap[key], cmap[key])
        compared += 1
        if cmp.get("status") == "COMPARABLE" and cmp.get("crc_divergent_or_fields_divergent"):
            first_divergence = {"key": list(key), "comparison": cmp}
            break

    return {
        "status": "COMPARABLE",
        "aligned_pairs": len(aligned_keys),
        "compared_pairs": compared,
        "first_observed_divergence": first_divergence,
        "unmatched_server_keys": [list(k) for k in unmatched_server],
        "unmatched_client_keys": [list(k) for k in unmatched_client],
        "crc_equal_all_aligned": all(
            compare_snapshot(smap[k], cmap[k]).get("crc_equal") is True
            for k in aligned_keys
        ),
        "evidence_note": EVIDENCE_NOTE,
    }


def _field_line(rec: DumpRecord, name: str) -> Optional[int]:
    for i, line in enumerate(rec.raw_lines, 1):
        if line.strip().startswith(name + "=") or line.strip().startswith(name + ":"):
            return i
    return None


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--server", help="einzelner Server-Snapshot .txt")
    ap.add_argument("--client", help="einzelner Client-Snapshot .txt")
    ap.add_argument("--server-dir", help="Server-Snapshot-Verzeichnis (Serienanalyse)")
    ap.add_argument("--client-dir", help="Client-Snapshot-Verzeichnis (Serienanalyse)")
    ap.add_argument("--out", help="Optional: JSON-Ausgabepfad")
    args = ap.parse_args()

    if args.server_dir or args.client_dir:
        if not (args.server_dir and args.client_dir):
            ap.error("--server-dir und --client-dir müssen zusammen gegeben werden")
        result = compare_series(Path(args.server_dir), Path(args.client_dir))
    else:
        if not (args.server and args.client):
            ap.error("entweder --server/--client oder --server-dir/--client-dir")
        srec = parse_dump_text(args.server,
                               Path(args.server).read_text(encoding="utf-8", errors="replace"))
        crec = parse_dump_text(args.client,
                               Path(args.client).read_text(encoding="utf-8", errors="replace"))
        result = compare_snapshot(srec, crec)

    text = json.dumps(result, ensure_ascii=False, indent=2)
    if args.out:
        Path(args.out).write_text(text + "\n", encoding="utf-8")
    print(text)

    if result.get("status") == "UNALIGNED":
        return EXIT_UNALIGNED
    if result.get("status") == "INCOMPLETE":
        return EXIT_INCOMPLETE
    if result.get("crc_divergent_or_fields_divergent") or \
            result.get("first_observed_divergence"):
        return EXIT_DIVERGENT
    return EXIT_IDENTICAL


if __name__ == "__main__":
    raise SystemExit(main())
