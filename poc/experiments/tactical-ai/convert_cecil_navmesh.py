#!/usr/bin/env python3
"""Convert CecilBotMod BNMV-v6 navmesh into directional BotCore waypoints.

CecilBotMod (c) Dreamy Cecil, GPL-2.0. Source reference at commit 953b477:
Sources/Bots/PathFinding/{Navmesh,PathPoint,PathPolygon}.cpp.
This converter does not require game binaries and cannot validate pit/door edges.
"""
import argparse
import math
import struct
from pathlib import Path


class Reader:
    def __init__(self, data):
        self.data = data
        self.offset = 0

    def get(self, fmt):
        size = struct.calcsize("<" + fmt)
        if size + self.offset > len(self.data):
            raise ValueError("Truncated navmesh")
        values = struct.unpack_from("<" + fmt, self.data, self.offset)
        self.offset += size
        return values if len(values) != 1 else values[0]

    def tag(self, expected):
        tag = self.get("4s")
        if tag != expected:
            raise ValueError(f"Bad tag at {self.offset - 4}: {tag!r} != {expected!r}")


def read_navmesh(data):
    r = Reader(data)
    r.tag(b"BNMV")
    version, generated, next_id, count = r.get("iiii")
    if version != 6:
        raise ValueError(f"Only BNMV version 6 supported, got {version}")
    if not 1 <= count <= 512 or generated not in (0, 1):
        raise ValueError(f"Invalid header: generated={generated}, nodes={count}")
    nodes, arcs, locks, flags = [], [], [], []
    for idx in range(count):
        r.tag(b"BPPH")
        point_id = r.get("i")
        x, y, z = r.get("fff")
        radius = r.get("f")
        point_flags = r.get("I")
        important, next_point, locked_by = r.get("iii")
        if any(not math.isfinite(v) for v in (x, y, z, radius)):
            raise ValueError(f"Non-finite coordinate or radius at point {idx}")
        if locked_by != -1:
            r.get("6f")  # version-6 placement (position, orientation)
            locks.append(idx)
        degree = r.get("i")
        if not 0 <= degree <= 16:
            raise ValueError(f"Node {idx}: degree {degree} exceeds graph limit")
        neighbors = [r.get("i") for _ in range(degree)]
        if any(n < 0 or n >= count or n == idx for n in neighbors):
            raise ValueError(f"Invalid neighbor at point {idx}")
        arcs.extend((idx, n) for n in neighbors)
        has_polygon = r.get("B")
        if has_polygon:
            poly_tag = r.get("4s")
            if poly_tag == b"PPO1":
                ct_vertices = 3
            elif poly_tag == b"PPO2":
                ct_vertices = r.get("i")
            else:
                raise ValueError(f"Unknown polygon tag {poly_tag!r}")
            if not 1 <= ct_vertices <= 4096:
                raise ValueError("Invalid polygon vertex count")
            for _ in range(ct_vertices):
                r.get("fff")
        nodes.append((x, y, z))
        if point_flags:
            flags.append((idx, point_flags))
    if r.offset != len(data):
        raise ValueError(f"Trailing {len(data)-r.offset} bytes after navmesh")
    return {"nodes": nodes, "arcs": arcs, "locks": locks, "flags": flags,
            "next_id": next_id, "generated": generated}


def to_waypoints(nav, source):
    lines = [
        "# CecilBotMod derived waypoints (Dreamy Cecil; GPL-2.0).",
        f"# Source: {source}; BNMV v6; map hash must match the Retail world.",
        "# Directed arcs retained. Door locks, jump/crouch flags and pit safety",
        "# require runtime validation before any automatic path following.",
        f"# points={len(nav['nodes'])} arcs={len(nav['arcs'])} locked={len(nav['locks'])}",
    ]
    for idx, x in enumerate(nav["nodes"]):
        lines.append("node " + " ".join(format(float(v), ".9g") for v in x))
    for a, b in nav["arcs"]:
        lines.append(f"arc {a} {b}")
    for idx in nav["locks"]:
        lines.append(f"# locked {idx}")
    for idx, flags in nav["flags"]:
        lines.append(f"# flags {idx} 0x{flags:08X}")
    return "\n".join(lines) + "\n"


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("source", type=Path, help="BNMV-v6 CecilBotMod .nav file")
    p.add_argument("destination", type=Path, help="Output BotCore text graph")
    args = p.parse_args()
    parsed = read_navmesh(args.source.read_bytes())
    args.destination.parent.mkdir(parents=True, exist_ok=True)
    args.destination.write_text(to_waypoints(parsed, args.source.name), encoding="utf-8")
    print(f"{args.source.name}: {len(parsed['nodes'])} nodes, "
          f"{len(parsed['arcs'])} directed arcs, {len(parsed['locks'])} locks")


if __name__ == "__main__":
    main()
