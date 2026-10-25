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
    # Fail closed on repeated metadata: a second header can falsely align
    # snapshots from different ticks or concatenated captures.
    fields = {"level": LEVEL, "sequence": SEQUENCE, "tick": TICK}
    matches = {"crc": crc_matches[0]}
    for name, pattern in fields.items():
        found = list(pattern.finditer(text))
        if len(found) != 1:
            raise ValueError(f"expected exactly one {name} field, found {len(found)}")
        matches[name] = found[0]
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


def load_snapshot_directory(directory):
    """Read only top-level .txt snapshots, never traverse symlinks or game paths."""
    folder = Path(directory)
    if not folder.is_dir() or folder.is_symlink():
        raise ValueError("not a regular snapshot directory")
    entries = sorted(folder.iterdir(), key=lambda item: item.name)
    if not entries or len(entries) > 128:
        raise ValueError("expected 1..128 snapshot .txt files per directory")
    if any(not entry.is_file() or entry.is_symlink() or entry.suffix.lower() != ".txt"
           for entry in entries):
        raise ValueError("snapshot directory must contain only regular .txt files")
    if sum(entry.stat().st_size for entry in entries) > 32 * 1024 * 1024:
        raise ValueError("snapshot series exceeds 32 MiB size limit")
    return [read_limited(entry) for entry in entries]


def compare_series(server_texts, client_texts):
    """Find first *observed* differing aligned sample, not first game divergence.

    Inputs need comparable captures over the same single level and time span.
    Missing samples make the series inconclusive; no interpolation is attempted.
    """
    def index(texts, side):
        captures = {}
        for text in texts:
            meta, _ = parse_snapshot(text)
            key = (meta["level"], meta["sequence"], meta["tick"])
            if key in captures:
                raise ValueError(f"duplicate level/sequence/tick in {side} series")
            captures[key] = text
        return captures

    server = index(server_texts, "server")
    client = index(client_texts, "client")
    if not server or not client:
        raise ValueError("both series require snapshots")
    levels = {key[0] for key in server.keys() | client.keys()}
    if len(levels) != 1:
        raise ValueError("multiple levels; segment map changes into separate comparisons")
    aligned = sorted(server.keys() & client.keys(), key=lambda key: (key[2], key[1]))
    missing_server = len(client.keys() - server.keys())
    missing_client = len(server.keys() - client.keys())
    differences = 0
    first = None
    for level, sequence, tick in aligned:
        result = compare(server[(level, sequence, tick)],
                         client[(level, sequence, tick)], maximum=0)
        if result["status"] != "MATCHING_SNAPSHOT":
            differences += 1
            if first is None:
                first = {
                    "level": level, "sequence": sequence, "tick": str(tick),
                    "crc_equal": result["crc_equal"],
                    "state_line_differences": result["state_line_differences"],
                }
    complete = missing_server == 0 and missing_client == 0 and bool(aligned)
    status = ("UNALIGNED" if not aligned else
              "INCOMPLETE_ALIGNMENT" if not complete else
              "OBSERVED_DIFFERENCE" if first else "MATCHED_OBSERVATIONS")
    return {
        "status": status,
        "can_compare": bool(aligned),
        "complete_pairing": complete,
        "server_samples": len(server),
        "client_samples": len(client),
        "aligned_samples": len(aligned),
        "unpaired_server_samples": missing_client,
        "unpaired_client_samples": missing_server,
        "differing_aligned_samples": differences,
        "first_observed_difference": first,
        "interpretation": (
            "Earliest differing *captured and aligned* snapshot only. "
            "Sparse captures, unprinted state and CRC inputs cannot establish "
            "the first divergent game tick or the root cause. "
            "No native stability acceptance is implied."
        ),
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--server", help="Single server syncdump.txt")
    parser.add_argument("--client", help="Single client syncdump.txt")
    parser.add_argument("--server-dir", help="Directory of archived server snapshots (.txt)")
    parser.add_argument("--client-dir", help="Directory of archived client snapshots (.txt)")
    args = parser.parse_args()
    try:
        if bool(args.server) != bool(args.client) or bool(args.server_dir) != bool(args.client_dir):
            raise ValueError("server/client inputs must be supplied as matching pairs")
        if bool(args.server) == bool(args.server_dir):
            raise ValueError("supply either two files or two directories")
        if args.server_dir:
            result = compare_series(load_snapshot_directory(args.server_dir),
                                    load_snapshot_directory(args.client_dir))
        else:
            result = compare(read_limited(args.server), read_limited(args.client))
    except (OSError, ValueError) as exc:
        print(json.dumps({"status": "INVALID", "can_compare": False,
                          "reason": str(exc)}, ensure_ascii=False))
        return 2
    print(json.dumps(result, ensure_ascii=False, indent=2))
    if result["status"] in ("UNALIGNED", "INCOMPLETE_ALIGNMENT"):
        return 2
    return 0 if result["status"] in ("MATCHING_SNAPSHOT", "MATCHED_OBSERVATIONS") else 3


if __name__ == "__main__":
    raise SystemExit(main())
