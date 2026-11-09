#!/usr/bin/env python3
"""Read-only Linux/Wine equivalent of Test-TSEExternalVanillaPreflight.ps1.

READY_AT_CHECK_TIME is a short-lived observation, never a launch or join test.
Uses the same four-entry Path/Hash manifest; source paths may be Windows paths.
Every fixture option forbids canStart, including --proc-root without a fixture.
Exit 0: ready at check time; exit 2: blocked or simulated. Never changes files,
launches a process, sends signals, or adjusts any game or server configuration.
"""
import sys
sys.dont_write_bytecode = True

import argparse
import datetime
import hashlib
import json
import os
from pathlib import Path, PureWindowsPath
import re
import time

from gamespy_query import QueryError, parse_response, query

COMPONENTS = {"SeriousSam.exe", "GameMP.dll", "Engine.dll", "EntitiesMP.dll"}


def require(ok, message):
    if not ok:
        raise ValueError(message)


def sha(path):
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def unique_pairs(pairs):
    result = {}
    for key, value in pairs:
        require(key not in result, "Duplicate manifest JSON key")
        result[key] = value
    return result


def manifest_pins(path):
    entries = json.loads(path.read_text(encoding="utf-8-sig"), object_pairs_hook=unique_pairs)
    require(isinstance(entries, list) and len(entries) == 4,
            "Manifest requires exactly four original retail components")
    pins = {}
    for entry in entries:
        require(isinstance(entry, dict) and set(entry) == {"Path", "Hash"}, "Expected Path/Hash manifest entry")
        require(isinstance(entry["Path"], str) and isinstance(entry["Hash"], str), "Invalid Path/Hash value")
        name = PureWindowsPath(entry["Path"]).name
        require(name in COMPONENTS and name not in pins, "Duplicate or unexpected original component")
        require(re.fullmatch(r"[a-fA-F0-9]{64}", entry["Hash"]), "Invalid expected SHA256")
        pins[name] = entry["Hash"].lower()
    return pins


def start_ticks(process):
    return int((process / "stat").read_text().rsplit(") ", 1)[1].split()[19])


def scan_occupancy(observer, proc_root=Path("/proc")):
    """Inspect Wine/game cmdline, cwd and mappings; never act on a process.

    Only a process that has actually disappeared may be skipped mid-inspection.
    An existing relevant process with unavailable identity/cwd/maps blocks.
    """
    root = observer.resolve()
    components = {((root / "Bin" / name).stat().st_dev, (root / "Bin" / name).stat().st_ino)
                  for name in COMPONENTS}
    occupied = []
    for process in Path(proc_root).iterdir():
        if not process.name.isdigit():
            continue
        try:
            try:
                argv = (process / "cmdline").read_bytes().split(b"\0")
            except OSError:
                # An unreadable command line cannot hide a Wine/game process.
                comm = (process / "comm").read_text().strip().lower()
                if comm.startswith(("serioussam", "wine")):
                    raise ValueError("Could not inspect relevant process command line")
                continue
            names = [arg.replace(b"\\", b"/").rsplit(b"/", 1)[-1].lower() for arg in argv]
            relevant = any(name == b"serioussam.exe" or name.startswith(b"wine") for name in names)
            if not relevant:
                comm = (process / "comm").read_text().strip().lower()
                relevant = comm.startswith(("serioussam", "wine"))
            if not relevant:
                continue
            before = start_ticks(process)
            cwd = (process / "cwd").resolve(strict=True)
            used = cwd == root or root in cwd.parents
            for arg in argv:
                value = os.fsdecode(arg).replace("\\", "/")
                if value[:2].lower() == "z:":
                    value = value[2:]
                used = used or value == str(root / "Bin/SeriousSam.exe")
            for line in (process / "maps").read_text().splitlines():
                fields = line.split(maxsplit=5)
                require(len(fields) >= 5, "Malformed relevant process mappings")
                major, minor = (int(v, 16) for v in fields[3].split(":"))
                if (os.makedev(major, minor), int(fields[4])) in components:
                    used = True
                if len(fields) == 6:
                    mapped = re.sub(r"\\([0-7]{3})", lambda match: chr(int(match[1], 8)), fields[5])
                    mapped = mapped.removesuffix(" (deleted)")
                    if mapped.startswith(str(root) + "/"):
                        used = True
            require(start_ticks(process) == before, "Relevant process identity changed during inspection")
            if used:
                occupied.append(int(process.name))
        except FileNotFoundError:
            if process.exists():
                raise ValueError("Could not inspect existing process")
        except (OSError, IndexError) as exc:
            raise ValueError("Could not inspect local Wine/game occupancy") from exc
    return occupied


def check_preflight(observer, manifest, server, query_port, game_port, expected_player="Dev-1",
                    timeout=3.0, status_fixture=None, proc_root=None):
    report = dict(status="BLOCKED", canStart=False, simulated=status_fixture is not None or proc_root is not None,
                  filesVerified=0, checks=[], live=False, oneBotOnly=False, reasons=[],
                  scope="Read-only preflight, not an accepted runtime or join")
    started = time.monotonic()
    try:
        require(1 <= query_port <= 65535 and 1 <= game_port <= 65535, "Invalid server port")
        require(0.1 <= timeout <= 10 and bool(server) and bool(expected_player), "Invalid query parameters")
        observer, manifest = Path(observer).absolute(), Path(manifest)
        require(observer.is_dir() and observer.resolve() == observer, "Observer directory missing or noncanonical")
        require(not (observer / "Bin").is_symlink(), "Observer Bin must not be a symlink")
        pins = manifest_pins(manifest)
        for name, digest in pins.items():
            path = observer / "Bin" / name
            ok = path.is_file() and not path.is_symlink() and sha(path) == digest
            report["checks"].append(dict(name=name, ok=ok))
            report["filesVerified"] += int(ok)
            if not ok:
                report["reasons"].append("Original binary missing or SHA256 mismatch: " + name)
        require(report["filesVerified"] == 4, "Four original hashes required")
        occupied = scan_occupancy(observer) if proc_root is None else scan_occupancy(observer, Path(proc_root))
        report["occupiedPids"] = occupied
        require(not occupied, "Observer installation already running")
        if status_fixture is not None:
            response = parse_response(Path(status_fixture).read_text(encoding="latin1"))
        else:
            response = query(server, query_port, timeout=timeout, attempts=1)
            report["live"] = True
        players = {key: value for key, value in response.items() if re.fullmatch(r"player_\d+", key)}
        report["oneBotOnly"] = (response.get("gamename") == "serioussamse" and response.get("gamever") == "1.07"
                                and response.get("hostport") == str(game_port) and response.get("numplayers") == "1"
                                and response.get("dedicatedserver") == "yes" and response.get("activemod") == ""
                                and players == {"player_0": expected_player})
        require(report["oneBotOnly"], "Current query does not contain exactly the expected vanilla single bot")
        # Query latency must not hide a newly launched observer or changed DLL.
        occupied = scan_occupancy(observer) if proc_root is None else scan_occupancy(observer, Path(proc_root))
        require(not occupied, "Observer installation became occupied during query")
        require(all(not (observer / "Bin" / name).is_symlink() and sha(observer / "Bin" / name) == digest
                    for name, digest in pins.items()), "Original binaries changed during query")
        if report["simulated"]:
            report["status"] = "FIXTURE_MATCH_ONLY"
            report["reasons"].append("Fixture mode never authorizes actual game launches")
        else:
            report.update(status="READY_AT_CHECK_TIME", canStart=True)
    except (OSError, ValueError, KeyError, TypeError, RuntimeError, QueryError) as exc:
        report["reasons"].append("Preflight failed: " + str(exc))
    report["checkedUtc"] = datetime.datetime.now(datetime.timezone.utc).isoformat()
    report["elapsed_s"] = time.monotonic() - started
    return report


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--observer-dir", type=Path, required=True)
    parser.add_argument("--manifest", type=Path, required=True)
    parser.add_argument("--server", required=True)
    parser.add_argument("--query-port", type=int, required=True)
    parser.add_argument("--game-port", type=int, required=True)
    parser.add_argument("--expected-player", default="Dev-1")
    parser.add_argument("--timeout", type=float, default=3.0)
    parser.add_argument("--status-fixture", type=Path)
    parser.add_argument("--proc-root", type=Path, help="synthetic /proc; always simulated, never canStart")
    args = parser.parse_args()
    result = check_preflight(args.observer_dir, args.manifest, args.server, args.query_port, args.game_port,
                             args.expected_player, args.timeout, args.status_fixture, args.proc_root)
    print(json.dumps(result, indent=2, allow_nan=False))
    return 0 if result["canStart"] else 2


if __name__ == "__main__":
    raise SystemExit(main())
