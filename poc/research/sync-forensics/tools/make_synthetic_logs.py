#!/usr/bin/env python3
"""Erzeugt synthetische, reproduzierbare Testdaten für die Sync-Forensics-
Werkzeuge. Es werden KEINE echten Logs oder Spieldaten verwendet.

Szenarien (jede Ausgabe ist eine selbständige Log-Datei):
  sustained   : SYNCBAD 1..10 monoton + KICK (E1-Muster)
  transient   : SYNCBAD 1..3, SYNCOK-Reset, SYNCBAD 1..2 (E2-Muster)
  jump        : Counter springt 1 -> 3 (E3-Muster)
  kick_only   : KICK ohne SYNCBAD (E4-Muster)
  bad_no_kick : SYNCBAD 1..5 ohne KICK (E5-Muster)
  empty       : kein Sync-Event (E6-Muster)
  client_only : Client-Log mit Disconnect, Server-Log ohne KICK
  aligned_dump_pair : zwei aligned Dumps, einmal identisch, einmal divergent
  misaligned_dump_pair : Dumps mit unterschiedlichem Tick

Usage:
  python make_synthetic_logs.py --out-dir /tmp/sync-forensics-fixtures
"""

from __future__ import annotations

import argparse
import random
from pathlib import Path
from typing import List

TICK_BASE = 100.0  # synthetische Tick-Basis (nicht Engine-Ticks!)


def sustained_log(seed: int = 42) -> str:
    rnd = random.Random(seed)
    lines = ["[Dedicated] Level Yodeller started", "Client '127.0.0.1' connected"]
    tick = TICK_BASE
    for i in range(1, 11):
        tick += rnd.uniform(0.2, 0.9)
        lines.append("SYNCBAD: Client '127.0.0.1', Sequence %d Tick %.2f - bad %d"
                     % (1600 + i, tick, i))
    lines.append("Client '127.0.0.1' ordered to disconnect: Too many bad syncs")
    lines.append("Client '127.0.0.1' left")
    return "\n".join(lines) + "\n"


def transient_log(seed: int = 7) -> str:
    rnd = random.Random(seed)
    lines = ["[Dedicated] Level Yodeller started", "Client '127.0.0.1' connected"]
    tick = TICK_BASE
    for i in range(1, 4):
        tick += rnd.uniform(0.2, 0.9)
        lines.append("SYNCBAD: Client '127.0.0.1', Sequence %d Tick %.2f - bad %d"
                     % (1700 + i, tick, i))
    tick += 1.5
    lines.append("SYNCOK: Client '127.0.0.1', Tick %.2f" % tick)
    for i in range(1, 3):
        tick += rnd.uniform(0.2, 0.9)
        lines.append("SYNCBAD: Client '127.0.0.1', Sequence %d Tick %.2f - bad %d"
                     % (1800 + i, tick, i))
    return "\n".join(lines) + "\n"


def jump_log(seed: int = 11) -> str:
    rnd = random.Random(seed)
    lines = ["[Dedicated] Level Yodeller started", "Client '127.0.0.1' connected"]
    tick = TICK_BASE
    lines.append("SYNCBAD: Client '127.0.0.1', Sequence 1901 Tick %.2f - bad 1" % tick)
    tick += 2.5
    lines.append("SYNCBAD: Client '127.0.0.1', Sequence 1902 Tick %.2f - bad 3" % tick)
    tick += 2.5
    lines.append("SYNCBAD: Client '127.0.0.1', Sequence 1903 Tick %.2f - bad 4" % tick)
    return "\n".join(lines) + "\n"


def kick_only_log() -> str:
    return "\n".join([
        "[Dedicated] Level Yodeller started",
        "Client '127.0.0.1' connected",
        "Client '127.0.0.1' ordered to disconnect: Too many bad syncs",
        "Client '127.0.0.1' left",
    ]) + "\n"


def bad_no_kick_log(seed: int = 21) -> str:
    rnd = random.Random(seed)
    lines = ["[Dedicated] Level Yodeller started", "Client '127.0.0.1' connected"]
    tick = TICK_BASE
    for i in range(1, 6):
        tick += rnd.uniform(0.2, 0.9)
        lines.append("SYNCBAD: Client '127.0.0.1', Sequence %d Tick %.2f - bad %d"
                     % (2000 + i, tick, i))
    return "\n".join(lines) + "\n"


def empty_sync_log() -> str:
    return "\n".join([
        "[Dedicated] Level Yodeller started",
        "Client '127.0.0.1' connected",
        "Client '127.0.0.1' left",
    ]) + "\n"


def client_only_log(seed: int = 31) -> str:
    rnd = random.Random(seed)
    lines = ["[BotDriver] bot0 tick=100 pos=(10.0,20.0,30.0) heading=45.0 fire=0",
             "Disconnected: Too many bad syncs"]
    return "\n".join(lines) + "\n"


def dump_text(level: str, seq: int, tick: float, crc: int,
              player_action_crc: int = 0, entity_health: int = 100,
              extra_fields: bool = True) -> str:
    lines = [
        "Level: %s" % level,
        "Sequence: %d" % seq,
        "Tick: %.2f" % tick,
        "CRC: 0x%08X" % crc,
        "PlayerActions=%d" % player_action_crc,
        "PlayerEntitys.health=%d" % entity_health,
    ]
    if extra_fields:
        lines.append("SessionTime=1234.5")
        lines.append("Pause=0")
    return "\n".join(lines) + "\n"


def dump_pair_identical(seed: int = 41) -> (str, str):
    rnd = random.Random(seed)
    seq = 5000
    tick = TICK_BASE
    s = dump_text("Yodeller", seq, tick, 0xDEADBEEF, 1, 100)
    c = dump_text("Yodeller", seq, tick, 0xDEADBEEF, 1, 100)
    return s, c


def dump_pair_divergent(seed: int = 43) -> (str, str):
    rnd = random.Random(seed)
    seq = 5100
    tick = TICK_BASE
    s = dump_text("Yodeller", seq, tick, 0x11111111, 1, 100)
    c = dump_text("Yodeller", seq, tick, 0x22222222, 2, 95)
    return s, c


def dump_pair_misaligned(seed: int = 45) -> (str, str):
    s = dump_text("Yodeller", 5200, TICK_BASE, 0x33333333)
    c = dump_text("Yodeller", 5200, TICK_BASE + 1.0, 0x33333333)
    return s, c


def telemetry_csv(seed: int = 51, rows: int = 20) -> str:
    rnd = random.Random(seed)
    lines = [
        "#bot-telemetry,rev=1",
        "#build,tag=synthetic-fixture",
        "#columns,t_ms,ticks,actions,frames,lp,gameon,enabled",
    ]
    t = 0
    for i in range(rows):
        t += 1000
        lines.append("%d,%d,%d,%d,%d,%d,%d,%d" % (
            t, rnd.randint(18, 22), rnd.randint(0, 80), rnd.randint(0, 20),
            4, 1, 1, 1))
    return "\n".join(lines) + "\n"


SCENARIOS = {
    "sustained": sustained_log,
    "transient": transient_log,
    "jump": jump_log,
    "kick_only": kick_only_log,
    "bad_no_kick": bad_no_kick_log,
    "empty": empty_sync_log,
    "client_only": client_only_log,
}


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--out-dir", required=True)
    args = ap.parse_args()
    out = Path(args.out_dir)
    out.mkdir(parents=True, exist_ok=True)

    written: List[str] = []
    for name, fn in SCENARIOS.items():
        p = out / ("server_%s.log" % name)
        p.write_text(fn(), encoding="utf-8")
        written.append(str(p))

    p = out / "client_only.log"
    p.write_text(client_only_log(), encoding="utf-8")
    written.append(str(p))

    s, c = dump_pair_identical()
    (out / "dump_server_identical.txt").write_text(s, encoding="utf-8")
    (out / "dump_client_identical.txt").write_text(c, encoding="utf-8")

    s, c = dump_pair_divergent()
    (out / "dump_server_divergent.txt").write_text(s, encoding="utf-8")
    (out / "dump_client_divergent.txt").write_text(c, encoding="utf-8")

    s, c = dump_pair_misaligned()
    (out / "dump_server_misaligned.txt").write_text(s, encoding="utf-8")
    (out / "dump_client_misaligned.txt").write_text(c, encoding="utf-8")

    (out / "telemetry.csv").write_text(telemetry_csv(), encoding="utf-8")
    written.append(str(out / "telemetry.csv"))

    print("\n".join(written))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
