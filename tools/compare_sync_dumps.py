#!/usr/bin/env python3
"""Compare two aligned Retail TSE syncdump.txt snapshots without exposing player data.

This is an offline diagnostic helper, NOT a sync acceptance test.
Only compare original files from an authorized, isolated Retail run. It does
not modify or start game processes and never publishes raw snapshot text.
"""
import argparse
from decimal import Decimal, InvalidOperation
import hashlib
import json
import re
from pathlib import Path

MAX_SIZE = 8 * 1024 * 1024
HEX = re.compile(r"^\s*CRC:\s*0x([0-9A-Fa-f]{8})\s*$", re.M)
SEQUENCE = re.compile(r"^\s*Sequence:\s*(-?\d+)\s*$", re.M)
LEVEL = re.compile(r"^\s*Level:\s*(-?\d+)\s*$", re.M)
TICK = re.compile(r"^\s*Tick:\s*(-?\d+(?:\.\d+)?)\s*$", re.M)
SAFE_LABEL = re.compile(r"^([A-Za-z_][\w. -]{0,48}):")
BASELINE_FIELDS = ("crc", "level", "sequence", "tick")


def parse_snapshot(text):
    """Require full metadata to prevent accidental comparisons of plain server logs."""
    crc_matches = list(HEX.finditer(text))
    if len(crc_matches) != 1:
        raise ValueError("expected exactly one CRC header (not concatenated snapshots)")
    matches = {"crc": crc_matches[0], "level": LEVEL.search(text),
               "sequence": SEQUENCE.search(text), "tick": TICK.search(text)}
    missing = [key for key, match in matches.items() if match is None]
    if missing:
        raise ValueError("not a complete sync dump; missing " + ", ".join(missing))
    try:
        tick = Decimal(matches["tick"].group(1))
    except InvalidOperation as exc:
        raise ValueError("malformed Tick field") from exc
    meta = {"crc": matches["crc"].group(1).upper(),
            "level": int(matches["level"].group(1)),
            "sequence": int(matches["sequence"].group(1)),
            "tick": tick}
    # Compare dump-state lines, excluding the checksum header and blank formatting.
    lines = text.splitlines()
    first = next((i for i, line in enumerate(lines)
                  if LEVEL.fullmatch(line.strip())), None)
    if first is None:
        raise ValueError("no leading state metadata")
    state_lines = [line.strip() for line in lines[first:]
                   if line.strip() and not re.fullmatch(r"[_= -]{6,}", line.strip())
                   and not any(pattern.fullmatch(line.strip())
                               for pattern in (LEVEL, SEQUENCE, TICK))]
    return meta, state_lines


def mask_label(line):
    match = SAFE_LABEL.match(line)
    if match and match.group(1) in {
        "Level", "Sequence", "Tick", "Paused", "Finished", "Random seed",
        "pa_vTranslation", "pa_aRotation", "pa_aViewRotation", "pa_ulButtons",
    }:
        return match.group(1)
    return "<redacted>"


def fingerprint(line):
    return hashlib.sha256(line.encode("utf-8")).hexdigest()[:12]


def compare(server_text, client_text, maximum=12):
    server, left = parse_snapshot(server_text)
    client, right = parse_snapshot(client_text)
    same_identity = all(server[k] == client[k] for k in ("level", "sequence", "tick"))
    if not same_identity:
        return {
            "status": "UNALIGNED", "can_compare": False,
            "server": {k: str(server[k]) for k in BASELINE_FIELDS},
            "client": {k: str(client[k]) for k in BASELINE_FIELDS},
            "reason": "Different level/sequence/tick; no state comparison is valid.",
        }
    differences = []
    for i in range(max(len(left), len(right))):
        a = left[i] if i < len(left) else None
        b = right[i] if i < len(right) else None
        if a == b:
            continue
        if len(differences) < maximum:
            differences.append({
                "normalized_line_index": i + 1,
                "server_label": mask_label(a) if a is not None else "<missing>",
                "client_label": mask_label(b) if b is not None else "<missing>",
                "server_fingerprint": fingerprint(a) if a is not None and mask_label(a) != "<redacted>" else None,
                "client_fingerprint": fingerprint(b) if b is not None and mask_label(b) != "<redacted>" else None,
            })
    same_crc = server["crc"] == client["crc"]
    diff_count = sum(1 for i in range(max(len(left), len(right)))
                     if (left[i] if i < len(left) else None) !=
                        (right[i] if i < len(right) else None))
    return {
        "status": "MATCHING_SNAPSHOT" if same_crc and not diff_count else "DIFFERENT_SNAPSHOT",
        "can_compare": True,
        "level": server["level"], "sequence": server["sequence"],
        "tick": str(server["tick"]), "crc_equal": same_crc,
        "server_crc": server["crc"], "client_crc": client["crc"],
        "state_line_count_server": len(left),
        "state_line_count_client": len(right),
        "state_line_differences": diff_count,
        "first_differences_redacted": differences,
        "interpretation": (
            "Aligned static snapshots only. No claim about the first divergent "
            "game tick, the root cause, native stability or server acceptance."
        ),
    }


def read_limited(path):
    source = Path(path)
    if not source.is_file():
        raise ValueError("not a regular file")
    if source.stat().st_size > MAX_SIZE:
        raise ValueError("snapshot exceeds 8 MiB size limit")
    return source.read_text(encoding="utf-8", errors="replace")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--server", required=True, help="Server syncdump.txt")
    parser.add_argument("--client", required=True, help="Client syncdump.txt")
    args = parser.parse_args()
    try:
        result = compare(read_limited(args.server), read_limited(args.client))
    except (OSError, ValueError) as exc:
        print(json.dumps({"status": "INVALID", "can_compare": False,
                          "reason": str(exc)}, ensure_ascii=False))
        return 2
    print(json.dumps(result, ensure_ascii=False, indent=2))
    if result["status"] == "UNALIGNED":
        return 2
    return 0 if result["status"] == "MATCHING_SNAPSHOT" else 3


if __name__ == "__main__":
    raise SystemExit(main())
