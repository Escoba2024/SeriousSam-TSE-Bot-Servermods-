#!/usr/bin/env python3
"""Audit a native evidence bundle against the agreed instrumentation contract.

Purpose
-------
Offline tools can only be as good as the data a native run produces. This tool
is the machine-checkable contract for that data: it decides whether a bundle is
*usable as native evidence* before any hypothesis verdict is computed from it.

It never interprets gameplay. It checks structure, provenance and safety
invariants, and it refuses to upgrade anything:

* ``simulated: true`` (or any ``SIMULATED`` marker) => ``SIMULATED_NEVER_NATIVE``
  and every derived observation is downgraded to the ``simulation`` class.
* A lowered ``ser_iKickOnSyncBad`` => ``INVALID``: suppressing the kick would
  make "no SYNCBAD" meaningless (AGENTS.md forbids this).
* Missing dumps / unaligned dumps / missing telemetry => ``INSUFFICIENT``
  (never "clean"), and observations are capped at ``telemetry`` class so they
  cannot produce a ``NATIVE_SUPPORTED`` verdict.

Bundle layout and manifest fields are documented in
``docs/research/sync-hypothesis-validation/2026-10-25-instrumentation-requirements.md``.
``--emit-template`` writes a ready-to-fill manifest.

Boundary to PR #58: detailed dump field diffing stays in
``poc/research/sync-forensics/tools/sync_crc_diff.py``. This audit only counts
aligned pairs and extracts boolean facts; an existing crc-diff JSON can be
ingested with ``--crc-diff`` to refine the entity/action classification.

Exit codes
----------
0  COMPLETE
4  INSUFFICIENT
5  INVALID or SIMULATED_NEVER_NATIVE
2  usage error
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import Dict, List, Optional, Tuple

sys.path.insert(0, str(Path(__file__).resolve().parent))

from syncval_common import (  # noqa: E402
    EXIT_INCOMPLETE, EXIT_INVALID, EXIT_OK, EXIT_USAGE,
    SyncValError, base_payload, emit, observation, parse_bot_telemetry,
    parse_server_sync, read_json, require, sha256_file,
)

TOOL = "evidence_bundle_audit"

EXPECTED_KICK_LIMIT = 10          # documented retail default (Ghidra 0x602A7EB4)
REQUIRED_TOP_LEVEL = ("bundle_id", "simulated", "run", "config", "processes", "artifacts")
REQUIRED_RUN = ("id", "date_utc", "operator", "platform", "tick_hz", "map")
REQUIRED_PROCESS_HASHES = ("exe_sha256", "engine_sha256", "entities_sha256")

# Field-name needles used only to separate "entity-ish" from "action-ish" dump
# fields. The authoritative field diff remains PR #58's sync_crc_diff.py.
ENTITY_NEEDLES = ("position", "placement", "rotation", "velocity", "health",
                  "armor", "ammo", "entity", "player_entity", "state")
ACTION_NEEDLES = ("action", "pa_", "buttons", "fire", "weapon")

DUMP_HEADER_KEYS = ("level", "sequence", "tick")


def emit_template(path: Path) -> None:
    template = {
        "bundle_id": "syncval-native-<run>-<yyyymmdd>-<hhmm>",
        "simulated": False,
        "run": {
            "id": "<run id>",
            "date_utc": "YYYY-MM-DDTHH:MM:SSZ",
            "operator": "<name>",
            "platform": "windows-native | wine-<version>",
            "tick_hz": 20,
            "map": "<map name>",
            "bots": 1,
            "clients": 1,
            "candidate": "<dll sha256 or 'vanilla'>",
            "notes": "",
        },
        "config": {
            "cli_bDumpSync": 1,
            "cli_bDumpSyncEachTick": 0,
            "ser_bReportSyncBad": 1,
            "ser_iKickOnSyncBad": EXPECTED_KICK_LIMIT,
            "ser_iExtensiveSyncCheck": 0,
            "frida_or_debugger_attached": False,
        },
        "processes": {
            "server": {
                "exe_sha256": "<64 hex>",
                "engine_sha256": "<64 hex>",
                "entities_sha256": "<64 hex>",
                "network_version": "1.07",
            },
            "clients": [
                {
                    "name": "botclient-1",
                    "exe_sha256": "<64 hex>",
                    "engine_sha256": "<64 hex>",
                    "entities_sha256": "<64 hex>",
                    "gamemp_sha256": "<64 hex>",
                    "gamemp_candidate": "<candidate id>",
                    "role": "bot",
                }
            ],
        },
        "artifacts": {
            "server_log": {"path": "server.log", "sha256": "<64 hex>"},
            "client_logs": [{"path": "client.log", "sha256": "<64 hex>"}],
            "telemetry": [{"path": "BotTelemetry.csv", "sha256": "<64 hex>"}],
            "server_dumps": ["dumps/server/<file>.txt"],
            "client_dumps": ["dumps/client/<file>.txt"],
            "action_traces": {
                "client": ["traces/client-actions.csv"],
                "server": ["traces/server-actions.csv"],
            },
        },
    }
    path.parent.mkdir(parents=True, exist_ok=True)
    import json
    path.write_text(json.dumps(template, ensure_ascii=False, indent=2) + "\n",
                    encoding="utf-8")


def _dump_key(path: Path) -> Optional[Tuple[str, int, float]]:
    """Read a sync-dump header (Level/Sequence/Tick) without interpreting it."""
    level = sequence = tick = None
    try:
        text = path.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return None
    for line in text.splitlines()[:40]:
        stripped = line.strip()
        lowered = stripped.lower()
        for key in DUMP_HEADER_KEYS:
            if lowered.startswith(key) and ":" in stripped or lowered.startswith(key) and "=" in stripped:
                separator = ":" if ":" in stripped else "="
                value = stripped.split(separator, 1)[1].strip()
                if key == "level":
                    level = value
                elif key == "sequence":
                    try:
                        sequence = int(value)
                    except ValueError:
                        sequence = None
                elif key == "tick":
                    try:
                        tick = float(value)
                    except ValueError:
                        tick = None
    if level is None or sequence is None or tick is None:
        return None
    return (level, sequence, tick)


def _dump_fields(path: Path) -> Dict[str, str]:
    fields: Dict[str, str] = {}
    try:
        text = path.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return fields
    for line in text.splitlines():
        if "=" not in line or line.strip().startswith("#"):
            continue
        name, value = line.split("=", 1)
        name = name.strip()
        if name and name.lower() not in DUMP_HEADER_KEYS:
            fields[name] = value.strip()
    return fields


def _classify_field(name: str) -> str:
    lowered = name.lower()
    if any(needle in lowered for needle in ACTION_NEEDLES):
        return "action"
    if any(needle in lowered for needle in ENTITY_NEEDLES):
        return "entity"
    return "other"


def _verify_artifact(bundle: Path, entry: object, problems: List[Dict[str, object]],
                     role: str) -> Optional[Path]:
    if isinstance(entry, str):
        path_value, recorded = entry, None
    elif isinstance(entry, dict):
        path_value, recorded = entry.get("path"), entry.get("sha256")
    else:
        problems.append({"artifact": role, "issue": "malformed artifact entry"})
        return None
    if not isinstance(path_value, str) or not path_value:
        problems.append({"artifact": role, "issue": "missing path"})
        return None
    path = bundle / path_value
    if not path.is_file():
        problems.append({"artifact": role, "issue": "file missing", "path": path_value})
        return None
    if isinstance(recorded, str) and len(recorded) == 64:
        actual = sha256_file(path)
        if actual.lower() != recorded.lower():
            problems.append({"artifact": role, "issue": "sha256 mismatch",
                             "path": path_value, "recorded": recorded.upper(),
                             "actual": actual})
            return None
    return path


def audit(bundle: Path, crc_diff: Optional[dict] = None) -> Dict[str, object]:
    payload = base_payload(TOOL, "simulation")
    manifest_path = bundle / "manifest.json"
    if not manifest_path.is_file():
        payload.update({"verdict": "INVALID", "verdict_detail": "manifest.json missing",
                        "missing": ["manifest.json"],
                        "evidence_class_after_audit": "simulation"})
        return payload

    manifest = read_json(str(manifest_path))
    require(isinstance(manifest, dict), "manifest.json must be an object")
    problems: List[Dict[str, object]] = []
    missing: List[str] = []
    warnings: List[str] = []

    for key in REQUIRED_TOP_LEVEL:
        if key not in manifest:
            missing.append(key)
    simulated = manifest.get("simulated")
    run = manifest.get("run") if isinstance(manifest.get("run"), dict) else {}
    config = manifest.get("config") if isinstance(manifest.get("config"), dict) else {}
    processes = manifest.get("processes") if isinstance(manifest.get("processes"), dict) else {}
    artifacts = manifest.get("artifacts") if isinstance(manifest.get("artifacts"), dict) else {}

    for key in REQUIRED_RUN:
        if key not in run:
            missing.append("run.%s" % key)

    marker = bundle / "GENERATED_FIXTURE.txt"
    if marker.is_file():
        payload.update({
            "verdict": "SIMULATED_NEVER_NATIVE",
            "verdict_detail": (
                "The bundle contains GENERATED_FIXTURE.txt. Generated fixtures are "
                "structurally complete by design, which is exactly why they must "
                "never be graded as native evidence."
            ),
            "marker": str(marker.name),
            "evidence_class_after_audit": "simulation",
        })
        payload["observations"] = _observations(payload, "simulation", None, None,
                                                None, 0, False, None, False)
        return payload

    if simulated is not False:
        payload.update({
            "verdict": "SIMULATED_NEVER_NATIVE",
            "verdict_detail": (
                "manifest.simulated must be exactly false. Generated or model "
                "data is never native Retail evidence, regardless of how complete "
                "it looks."
            ),
            "manifest_simulated": simulated,
            "evidence_class_after_audit": "simulation",
        })
        payload["observations"] = _observations(payload, "simulation",
                                                first_bad=None, jump_count=None,
                                                kick_connected=None, aligned=0,
                                                entity_div=False,
                                                hash_match=None, complete=False)
        return payload

    # --- safety invariants -------------------------------------------------
    kick_limit = config.get("ser_iKickOnSyncBad")
    if kick_limit != EXPECTED_KICK_LIMIT:
        problems.append({
            "config": "ser_iKickOnSyncBad",
            "issue": "must equal the documented retail default",
            "expected": EXPECTED_KICK_LIMIT,
            "recorded": kick_limit,
            "why": "lowering it suppresses kicks and makes 'no SYNCBAD' meaningless",
        })
    if config.get("cli_bDumpSync") != 1:
        missing.append("config.cli_bDumpSync==1 (aligned dumps are the core artifact)")
    if config.get("ser_bReportSyncBad") != 1:
        missing.append("config.ser_bReportSyncBad==1 (sync events must be logged)")
    if config.get("frida_or_debugger_attached"):
        warnings.append("debugger/instrumentation attached: timing behaviour may differ")

    # --- hash inventory ----------------------------------------------------
    server = processes.get("server") if isinstance(processes.get("server"), dict) else {}
    clients = processes.get("clients") if isinstance(processes.get("clients"), list) else []
    hash_match: Optional[bool] = None
    if not all(server.get(key) for key in REQUIRED_PROCESS_HASHES):
        missing.append("processes.server hashes")
    if not clients:
        missing.append("processes.clients")
    inventory_ok = bool(server) and bool(clients)
    differing: List[Dict[str, object]] = []
    for client in clients:
        if not isinstance(client, dict):
            missing.append("processes.clients[].<object>")
            inventory_ok = False
            continue
        if not all(client.get(key) for key in REQUIRED_PROCESS_HASHES):
            missing.append("processes.clients[].%s" % "/".join(REQUIRED_PROCESS_HASHES))
            inventory_ok = False
        for key in REQUIRED_PROCESS_HASHES:
            if server.get(key) and client.get(key) and \
                    str(server[key]).upper() != str(client[key]).upper():
                differing.append({"component": key, "client": client.get("name"),
                                  "server": server[key], "client_value": client[key]})
                inventory_ok = False
    if inventory_ok:
        hash_match = True
    elif differing:
        hash_match = False

    # --- artifacts ---------------------------------------------------------
    server_log = _verify_artifact(bundle, artifacts.get("server_log"), problems, "server_log")
    client_logs = []
    for index, entry in enumerate(artifacts.get("client_logs") or []):
        verified = _verify_artifact(bundle, entry, problems, "client_logs[%d]" % index)
        if verified:
            client_logs.append(verified)
    telemetry_paths = []
    for index, entry in enumerate(artifacts.get("telemetry") or []):
        verified = _verify_artifact(bundle, entry, problems, "telemetry[%d]" % index)
        if verified:
            telemetry_paths.append(verified)
    if server_log is None:
        missing.append("server.log")
    if not client_logs:
        missing.append("client.log")
    if not telemetry_paths:
        missing.append("BotTelemetry.csv")

    telemetry_columns: List[str] = []
    if telemetry_paths:
        tel = parse_bot_telemetry(str(telemetry_paths[0]))
        telemetry_columns = tel.columns
        if tel.errors:
            problems.extend({"artifact": "telemetry", "issue": error}
                            for error in tel.errors[:5])

    # --- dumps -------------------------------------------------------------
    server_dumps = [bundle / str(p) for p in (artifacts.get("server_dumps") or [])]
    client_dumps = [bundle / str(p) for p in (artifacts.get("client_dumps") or [])]
    server_keys = {}
    for path in server_dumps:
        key = _dump_key(path)
        if key:
            server_keys[key] = path
    client_keys = {}
    for path in client_dumps:
        key = _dump_key(path)
        if key:
            client_keys[key] = path
    aligned = sorted(set(server_keys) & set(client_keys))
    if not server_dumps or not client_dumps:
        missing.append("dumps/server/*.txt and dumps/client/*.txt")
    elif not aligned:
        missing.append("at least one aligned (Level, Sequence, Tick) dump pair")

    entity_divergence = False
    action_divergence = False
    first_divergent_tick: Optional[float] = None
    divergent_detail: List[Dict[str, object]] = []
    if aligned:
        for key in aligned:
            server_fields = _dump_fields(server_keys[key])
            client_fields = _dump_fields(client_keys[key])
            differing_fields = []
            for name in sorted(set(server_fields) & set(client_fields)):
                if server_fields[name] != client_fields[name]:
                    differing_fields.append(name)
            kinds = {_classify_field(name) for name in differing_fields}
            if "entity" in kinds:
                entity_divergence = True
            if "action" in kinds:
                action_divergence = True
            if differing_fields:
                if first_divergent_tick is None:
                    first_divergent_tick = key[2]
                divergent_detail.append({
                    "tick": key[2],
                    "sequence": key[1],
                    "fields": differing_fields[:20],
                    "kinds": sorted(kinds),
                })
    if isinstance(crc_diff, dict):
        if crc_diff.get("entity_state_divergence") is True:
            entity_divergence = True
        if isinstance(crc_diff.get("first_divergent_tick"), (int, float)):
            first_divergent_tick = crc_diff["first_divergent_tick"]

    # --- server log facts --------------------------------------------------
    first_bad: Optional[float] = None
    jump_count: Optional[int] = None
    kick_connected: Optional[bool] = None
    if server_log is not None:
        text = server_log.read_text(encoding="utf-8", errors="replace")
        events = parse_server_sync(text)
        bads = [e for e in events if e.kind == "SYNCBAD"]
        jumps = 0
        previous: Dict[str, int] = {}
        for event in bads:
            client = str(event.client)
            if client in previous and (event.counter or 0) - previous[client] > 1:
                jumps += 1
            previous[client] = event.counter or 0
        jump_count = jumps
        first_bad = bads[0].tick if bads else None
        kicks = [e for e in events if e.kind == "KICK"]
        kick_connected = None
        if kicks:
            kick_connected = any(e.kind == "CLIENT_DISCONNECT" for e in events)
            warnings.append("kick observed: the run is a FAIL run by definition")

    complete = (not missing) and (not problems)
    if problems:
        verdict = "INVALID"
    elif not complete:
        verdict = "INSUFFICIENT"
    else:
        verdict = "COMPLETE"

    evidence_class = "native" if verdict == "COMPLETE" else "telemetry"
    payload.update({
        "verdict": verdict,
        "bundle_id": manifest.get("bundle_id"),
        "manifest_simulated": simulated,
        "missing": missing,
        "problems": problems,
        "warnings": warnings,
        "config": config,
        "run": run,
        "hash_inventory": {
            "match": hash_match,
            "differences": differing,
        },
        "dumps": {
            "server_dumps": len(server_dumps),
            "client_dumps": len(client_dumps),
            "aligned_pairs": len(aligned),
            "first_divergent_tick": first_divergent_tick,
            "entity_state_divergence": entity_divergence,
            "action_state_divergence": action_divergence,
            "divergent_samples": divergent_detail[:20],
        },
        "telemetry": {"files": [p.name for p in telemetry_paths],
                      "columns": telemetry_columns},
        "server_log": {"first_bad_tick": first_bad,
                       "counter_jumps": jump_count,
                       "disconnect_after_kick": kick_connected},
        "evidence_class_after_audit": evidence_class,
        "interpretation": (
            "COMPLETE only means the bundle satisfies the instrumentation contract. "
            "It is not a stability pass; the verdicts are computed by "
            "verdict_engine.py from the observations below."
        ),
    })
    payload["observations"] = _observations(payload, evidence_class, first_bad,
                                            jump_count, kick_connected, len(aligned),
                                            entity_divergence, hash_match, complete)
    return payload


def _observations(payload: Dict[str, object], evidence_class: str,
                  first_bad: Optional[float], jump_count: Optional[int],
                  kick_connected: Optional[bool], aligned: int,
                  entity_div: bool, hash_match: Optional[bool],
                  complete: bool) -> List[Dict[str, object]]:
    source = str(payload.get("bundle_id") or "bundle")
    return [
        observation("evidence.bundle_complete", complete, evidence_class, source),
        observation("log.first_bad_tick", first_bad, evidence_class, source),
        observation("log.counter_jumps", jump_count, evidence_class, source),
        observation("log.disconnect_after_kick", kick_connected, evidence_class, source),
        observation("dumps.aligned_pairs", aligned, evidence_class, source),
        observation("dumps.entity_state_divergence", entity_div, evidence_class, source),
        observation("build.hash_inventory_match", hash_match, evidence_class, source),
    ]


def exit_code_for(verdict: str) -> int:
    if verdict == "COMPLETE":
        return EXIT_OK
    if verdict == "INSUFFICIENT":
        return EXIT_INCOMPLETE
    return EXIT_INVALID


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--bundle", required=True, help="bundle directory")
    parser.add_argument("--crc-diff", help="optional sync_crc_diff.py JSON (PR #58)")
    parser.add_argument("--emit-template", help="write a manifest template here and exit")
    parser.add_argument("--out")
    args = parser.parse_args()

    if args.emit_template:
        emit_template(Path(args.emit_template))
        print("template written: %s" % args.emit_template)
        return EXIT_OK

    bundle = Path(args.bundle)
    require(bundle.is_dir(), "bundle directory not found: %s" % bundle)
    crc_diff = read_json(args.crc_diff) if args.crc_diff else None
    payload = audit(bundle, crc_diff)
    emit(payload, args.out)
    return exit_code_for(str(payload["verdict"]))


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except SyncValError as exc:
        print("error: %s" % exc, file=sys.stderr)
        raise SystemExit(EXIT_USAGE)
