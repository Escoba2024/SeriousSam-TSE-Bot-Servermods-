#!/usr/bin/env python3
"""Minimal read-only GameSpy v3 query client for Serious Sam TSE servers.

Used during CPU measurement windows to prove, from the *server* side, that the
bot players are present and still scoring while a client is sampled.  The same
protocol is used by poc/scripts/FleetQuery.ps1; nothing here writes to the
server and no game state is changed.

Examples
--------
  python3 tools/gamespy_query.py 91.99.75.33:25600 status
  python3 tools/gamespy_query.py host:25600 status --watch 30 --interval 5 \\
      --jsonl /tmp/query.jsonl --expect-players 9 --expect-prefix HetznerFleet

Exit codes: 0 success, 8 expectation/timeout failure, 2 usage error.
"""
import argparse
import json
import socket
import sys
import time
from pathlib import Path

EXIT_OK = 0
EXIT_FAIL = 8


class QueryError(Exception):
    pass


def parse_hostport(text):
    host, _, port = text.rpartition(":")
    if not host or not port.isdigit():
        raise QueryError("expected host:port, got %r" % text)
    return host, int(port)


def parse_response(text):
    """`\\key\\value\\key\\value` -> dict. GameSpy v3 has no escaping."""
    fields = text.split("\\")
    result = {}
    for index in range(1, len(fields) - 1, 2):
        result[fields[index]] = fields[index + 1]
    return result


def player_names(response):
    """Collect `player_N` entries in index order."""
    players = []
    for key, value in response.items():
        if key.startswith("player_") and key[7:].isdigit():
            players.append((int(key[7:]), value))
    return [name for _, name in sorted(players)]


def query(host, port, request="\\status\\", timeout=3.0, attempts=3, retry_delay=0.25):
    last_error = None
    for _ in range(attempts):
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.settimeout(timeout)
        try:
            sock.sendto(request.encode("ascii"), (host, port))
            payload, _ = sock.recvfrom(8192)
            return parse_response(payload.decode("latin-1"))
        except (socket.timeout, OSError) as exc:
            last_error = exc
            time.sleep(retry_delay)
        finally:
            sock.close()
    raise QueryError("no answer from %s:%d (%s)" % (host, port, last_error))


def summarize(response):
    return {
        "hostname": response.get("hostname"),
        "gametype": response.get("gametype"),
        "mapname": response.get("mapname"),
        "numplayers": int(response["numplayers"]) if response.get("numplayers", "").isdigit() else None,
        "maxplayers": int(response["maxplayers"]) if response.get("maxplayers", "").isdigit() else None,
        "password": response.get("password"),
        "players": player_names(response),
        "keys": sorted(response.keys()),
    }


def check_expectations(summary, expect_players=None, expect_prefix=None):
    problems = []
    if expect_players is not None:
        if summary["numplayers"] != expect_players:
            problems.append("numplayers=%s, expected %d"
                            % (summary["numplayers"], expect_players))
        if len(summary["players"]) != expect_players:
            problems.append("player list has %d entries, expected %d"
                            % (len(summary["players"]), expect_players))
    if expect_prefix:
        missing = [p for p in summary["players"] if not p.startswith(expect_prefix)]
        if missing:
            problems.append("players without prefix %r: %r" % (expect_prefix, missing))
    return problems


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("address", help="host:port of the game server (query port)")
    parser.add_argument("request", nargs="?", default="\\status\\",
                        choices=("\\status\\", "\\info\\", "\\rules\\", "\\players\\"))
    parser.add_argument("--count", type=int, default=1,
                        help="number of queries (default 1)")
    parser.add_argument("--interval", type=float, default=5.0)
    parser.add_argument("--timeout", type=float, default=3.0)
    parser.add_argument("--jsonl", default=None, help="append every sample here")
    parser.add_argument("--expect-players", type=int, default=None)
    parser.add_argument("--expect-prefix", default=None)
    args = parser.parse_args(argv)

    try:
        host, port = parse_hostport(args.address)
    except QueryError as exc:
        print("gamespy_query: %s" % exc, file=sys.stderr)
        return 2

    stream = None
    if args.jsonl:
        stream = Path(args.jsonl).open("a", encoding="utf-8")
    failures = 0
    try:
        for index in range(args.count):
            started = time.time()
            try:
                response = query(host, port, args.request, timeout=args.timeout)
            except QueryError as exc:
                failures += 1
                print("gamespy_query: %s" % exc, file=sys.stderr)
                if stream:
                    stream.write(json.dumps({"t": started, "error": str(exc)}) + "\n")
                    stream.flush()
                if index + 1 < args.count:
                    time.sleep(args.interval)
                continue
            summary = summarize(response)
            problems = check_expectations(summary, args.expect_players, args.expect_prefix)
            record = {
                "t": started,
                "address": args.address,
                "request": args.request,
                "summary": summary,
                "problems": problems,
                "raw_keys": len(response),
            }
            if stream:
                stream.write(json.dumps(record) + "\n")
                stream.flush()
            else:
                print(json.dumps(record, indent=2))
            if problems:
                failures += 1
                for problem in problems:
                    print("gamespy_query: %s" % problem, file=sys.stderr)
            if index + 1 < args.count:
                time.sleep(args.interval)
    finally:
        if stream:
            stream.close()
    return EXIT_OK if failures == 0 else EXIT_FAIL


if __name__ == "__main__":
    sys.exit(main())
