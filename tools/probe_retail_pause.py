#!/usr/bin/env python3
"""Read pause flags from an authorized, isolated original Retail 1.07 process.

No hooks, calls into the process, writes, input events or process control.
Offsets are pinned to the original Engine hash and native getter instructions.
This reports raw session flags, not IsPaused's disconnected/global fallback.
The caller still owns process authorization and the complete native test gate.
"""
import argparse
import hashlib
import json
import math
from pathlib import Path
import struct


ENGINE_SHA256 = "b79bf8bb3927fe4f8f252e141d721ae5c738df02218f0ecc12da5c1afbcb534f"
TOGGLE_RVA = 0xDAB40
TOGGLE_BYTES = bytes.fromhex("8b412033c98b90ac00000085d20f94c18988ac000000c3")
IS_PAUSED_RVA = 0xDAB60
IS_PAUSED_BYTES = bytes.fromhex("85c97413a1b8d62c6085c0750a8b41208b80a8000000c3")
RND_RVA = 0xE42E0
RND_BYTES = bytes.fromhex("8b417c8bd0c1e21103d08d045089417cc3")
RESET_RND_RVA = 0xE4300
RESET_RND_BYTES = bytes.fromhex(
    "53568bb1a0000000c7417c214365878b597c57c781a000000001000000ba20000000"
    "8bc38bf8c1e71103f84a8d04788bd875ef89b1a00000005f89597c5e5bc3")
NETWORK_POINTER_RVA = 0x20D6A4


def _require(condition, message):
    if not condition:
        raise RuntimeError(message)


def _file_identity(stat):
    return stat.st_dev, stat.st_ino, stat.st_size, stat.st_mtime_ns, stat.st_ctime_ns


def _identity(proc):
    # Linux stat field22, after the possibly space-containing process name.
    return int((proc / "stat").read_text().rsplit(") ", 1)[1].split()[19])


def read_pause(pid, root):
    """Return pause flags, last processed game tick and current native PRNG state.

    Each call independently verifies the module and process. A concurrent game
    tick may advance during reading; this is not an atomic simulation snapshot.
    Require repeated stable samples and actual player state for a pause gate.
    """
    _require(isinstance(pid, int) and pid > 0, "invalid process id")
    root = Path(root).resolve(strict=True)
    proc = Path("/proc") / str(pid)
    identity = _identity(proc)
    _require((proc / "cwd").resolve(strict=True) == root, "process directory mismatch")
    image = root / "Bin" / "Engine.dll"
    stat = image.stat()
    _require(hashlib.sha256(image.read_bytes()).hexdigest() == ENGINE_SHA256,
             "unsupported Engine image")
    rows = [line.split(maxsplit=5) for line in (proc / "maps").read_text().splitlines()]
    rows = [row for row in rows if len(row) == 6 and row[5] == str(image)]
    _require(rows and all(int(row[4]) == stat.st_ino for row in rows),
             "mapped Engine identity mismatch")
    bases = [int(row[0].split("-")[0], 16) for row in rows if int(row[2], 16) == 0]
    _require(len(bases) == 1, "ambiguous Engine base")
    base = bases[0]
    with (proc / "mem").open("rb", buffering=0) as memory:
        def read(address, length):
            memory.seek(address)
            value = memory.read(length)
            _require(len(value) == length, "short process read")
            return value

        def word(address):
            return struct.unpack("<I", read(address, 4))[0]

        _require(read(base + TOGGLE_RVA, len(TOGGLE_BYTES)) == TOGGLE_BYTES,
                 "TogglePause instructions differ")
        _require(read(base + IS_PAUSED_RVA, len(IS_PAUSED_BYTES)) == IS_PAUSED_BYTES,
                 "IsPaused instructions differ")
        _require(read(base + RND_RVA, len(RND_BYTES)) == RND_BYTES,
                 "Rnd instructions differ")
        _require(read(base + RESET_RND_RVA, len(RESET_RND_BYTES)) == RESET_RND_BYTES,
                 "ResetRND instructions differ")
        network = word(base + NETWORK_POINTER_RVA)
        _require(network > 0x10000, "network not initialized")
        session = word(network + 0x20)
        _require(session > 0x10000, "session not initialized")
        actual, requested = struct.unpack("<II", read(session + 0xA8, 8))
        tick = struct.unpack("<f", read(session + 0x4C, 4))[0]
        random_seed = word(session + 0x7C)
        _require(actual in (0, 1) and requested in (0, 1) and math.isfinite(tick),
                 "invalid session pause snapshot")
        _require(word(base + NETWORK_POINTER_RVA) == network and word(network + 0x20) == session,
                 "session changed during observation")
    _require(_identity(proc) == identity and (proc / "cwd").resolve(strict=True) == root,
             "process changed during observation")
    _require(_file_identity(image.stat()) == _file_identity(stat), "Engine file changed during observation")
    return {"actual_pause": actual, "requested_pause": requested,
            "game_tick": tick, "random_seed": random_seed}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--pid", type=int, required=True)
    parser.add_argument("--root", type=Path, required=True)
    args = parser.parse_args()
    print(json.dumps(read_pause(args.pid, args.root)))


if __name__ == "__main__":
    main()
