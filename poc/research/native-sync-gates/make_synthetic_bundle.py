#!/usr/bin/env python3
"""Create an explicitly synthetic capture-contract example in a NEW directory."""
import argparse
import hashlib
import json
from pathlib import Path


def create(destination):
    destination.mkdir(parents=True, exist_ok=False)

    def artifact(name, data):
        (destination / name).write_bytes(data)
        return {"path": name, "sha256": hashlib.sha256(data).hexdigest()}

    manifest = {
        "schema": "tse-native-sync-capture/v1", "source_kind": "synthetic",
        "session_id": "synthetic-session", "connection_id": "synthetic-connection",
        "level_id": "synthetic-map", "level_epoch": 1,
        "map": artifact("map.fixture", b"synthetic map; no game data"),
        "config": artifact("config.fixture", b"synthetic config"),
        "tick_unit": "engine_tick_index",
        "window": {"first_sequence": 10, "last_sequence": 12, "first_tick": 100, "tick_step": 1},
        "layout": {"id": "synthetic-layout", "phase": "before_sync_crc",
                   "players": ["slot0"], "action_bytes": 2,
                   "state_fields": {"session": 2, "entity": 2}, "binding_status": "synthetic",
                   "evidence": artifact("layout.fixture", b"synthetic contract; not a Retail layout")},
        "producer": {"id": "synthetic-generator", "version": "1",
                     "artifact": artifact("producer.py", Path(__file__).read_bytes())},
        "participants": {},
    }
    for role in ("server", "client"):
        rows = [{"session_id": manifest["session_id"], "connection_id": manifest["connection_id"],
                 "level_epoch": 1, "sequence": sequence, "tick": sequence + 90,
                 "crc32": "12345678", "actions": {"slot0": "0001"},
                 "state": {"session": "0100", "entity": "0200"}}
                for sequence in range(10, 13)]
        manifest["participants"][role] = {
            "capture_id": role + "-synthetic", "complete": True, "dropped_records": 0,
            "binaries": {key: artifact(role + "." + key + ".fixture", ("synthetic " + key).encode())
                         for key in ("executable", "engine", "gamemp", "entities")},
            "records": artifact(role + ".jsonl", "".join(json.dumps(row) + "\n" for row in rows).encode()),
        }
    (destination / "manifest.json").write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("destination", type=Path)
    args = parser.parse_args()
    try:
        create(args.destination)
    except OSError as error:
        parser.exit(2, "Cannot create new synthetic directory: " + str(error) + "\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
