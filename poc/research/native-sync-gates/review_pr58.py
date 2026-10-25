#!/usr/bin/env python3
"""Reproduce PR58 baseline and adversarial findings from its pinned git object.

Only synthetic temporary fixtures; never fetches, checks out or changes PR58.
The pinned upstream Python tests run as local subprocesses, not game processes.
"""
import importlib
import json
from pathlib import Path
import subprocess
import sys
import tempfile

PIN = "df7108ba04cafb120c6a035503fa2f9732a83b0f"
PREFIX = "poc/research/sync-forensics/"
ROOT = Path(__file__).resolve().parent
REPO = ROOT.parents[2]


def main():
    with tempfile.TemporaryDirectory(prefix="pr58-review-", dir=ROOT) as temporary:
        target = Path(temporary)
        files = subprocess.check_output(["git", "ls-tree", "-r", "--name-only", PIN], cwd=REPO, text=True).splitlines()
        for filename in files:
            if filename.startswith(PREFIX) and filename.endswith(".py"):
                destination = target / filename.removeprefix(PREFIX)
                destination.parent.mkdir(parents=True, exist_ok=True)
                destination.write_bytes(subprocess.check_output(["git", "show", PIN + ":" + filename], cwd=REPO))
        baseline = subprocess.run([sys.executable, "-B", "-m", "unittest", "discover", "-s", str(target / "tests"), "-q"], capture_output=True, text=True)
        if baseline.returncode:
            print(baseline.stderr, file=sys.stderr)
            return 1
        sys.path.insert(0, str(target / "tools"))
        sys.dont_write_bytecode = True
        common = importlib.import_module("sync_forensics_common")
        diff = importlib.import_module("sync_crc_diff")
        incomplete = importlib.import_module("sync_incomplete_detector")
        snapshot = "Level: Fixture\nSequence: 10\nTick: 1.0\nCRC: 0x11111111\nAction=00\n"
        rec = lambda text: common.parse_dump_text("synthetic", text)
        findings = {}
        missing = diff.compare_snapshot(rec(snapshot), rec(snapshot.replace("CRC: 0x11111111\n", "")))
        findings["missing_crc_accepted"] = missing["status"] == "COMPARABLE" and missing["crc_equal"] is None
        malformed = diff.compare_snapshot(rec(snapshot), rec(snapshot + "INVALID LINE\n"))
        findings["parse_error_accepted"] = malformed["status"] == "COMPARABLE"
        server, client = target / "server", target / "client"
        server.mkdir()
        client.mkdir()
        (server / "a.txt").write_text(snapshot)
        (client / "a.txt").write_text(snapshot)
        (server / "b.txt").write_text(snapshot.replace("Sequence: 10", "Sequence: 11").replace("Tick: 1.0", "Tick: 2.0"))
        result = diff.compare_series(server, client)
        findings["unmatched_series_accepted"] = result["status"] == "COMPARABLE" and bool(result["unmatched_server_keys"])
        (server / "b.txt").write_text(snapshot)
        (server / "a.txt").write_text(snapshot.replace("0x11111111", "0x22222222"))
        result = diff.compare_series(server, client)
        findings["duplicate_key_suppresses_difference"] = result["status"] == "COMPARABLE" and result["crc_equal_all_aligned"] and result["first_observed_divergence"] is None
        findings["no_inputs_complete"] = incomplete.detect_incomplete(None, None, None, [])["complete"]
        telemetry = target / "telemetry.csv"
        telemetry.write_text("t_ms,ticks,actions\ninvalid,invalid,invalid\n")
        findings["nonnumeric_telemetry_complete"] = not incomplete.check_telemetry(telemetry)
        try:
            common.parse_server_log_events("SYNCBAD: Client 'fixture', Sequence 1 Tick 1.2.3 - bad 1")
            findings["malformed_tick_raises"] = False
        except ValueError:
            findings["malformed_tick_raises"] = True
        print(json.dumps({"pin": PIN, "baseline_exit": baseline.returncode,
                          "baseline_summary": baseline.stderr.strip().splitlines()[-3:],
                          "synthetic_findings_reproduced": findings,
                          "retail_runtime": "NOT_TESTED"}, indent=2))
        return 0 if all(findings.values()) else 1


if __name__ == "__main__":
    raise SystemExit(main())
