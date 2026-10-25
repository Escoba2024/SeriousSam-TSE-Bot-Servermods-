#!/usr/bin/env python3
"""Read and compare sealed local capture bundles; never grants native acceptance.

No process attachment, networking, game configuration or input artifact writes.
This is a proposed interchange contract, not a Retail 1.07 dump parser or hook.
"""
import argparse
import hashlib
import json
from pathlib import Path
import re

MAX_BYTES = 64 * 1024 * 1024
MAX_RECORDS = 1_000_000
SHA = re.compile(r"[0-9a-f]{64}\Z")
HEX = re.compile(r"(?:[0-9a-fA-F]{2})+\Z")
CRC = re.compile(r"[0-9a-fA-F]{8}\Z")
NAME = re.compile(r"[A-Za-z0-9_.:-]{1,128}\Z")
RECORD_KEYS = {"session_id", "connection_id", "level_epoch", "sequence", "tick",
               "crc32", "actions", "state"}
LIMITATIONS = (
    "Offline comparison only. Native labels and binding status are producer attestation; "
    "hashes prove local artifact integrity, not truthful capture or live module identity. "
    "No native Retail acceptance, ABI proof, CRC coverage proof, stability PASS or root cause. "
    "First observed difference is restricted to the declared complete window."
)


class Blocked(Exception):
    def __init__(self, code, where):
        self.code = code
        self.where = where


def require(condition, code, where):
    if not condition:
        raise Blocked(code, where)


def integer(value):
    return type(value) is int and 0 <= value <= (2**63 - 1)


def name(value):
    return isinstance(value, str) and NAME.fullmatch(value) is not None


def digest(data):
    return hashlib.sha256(data).hexdigest()


def unique_object(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError("duplicate key")
        result[key] = value
    return result


def parse_json(data, where):
    def nonfinite(_):
        raise ValueError("nonfinite JSON")
    try:
        return json.loads(data, object_pairs_hook=unique_object, parse_constant=nonfinite)
    except (ValueError, UnicodeError, RecursionError):
        raise Blocked("JSON_INVALID", where) from None


def read_bytes(path, where):
    try:
        require(path.is_file(), "ARTIFACT_IO", where)
        with path.open("rb") as handle:
            data = handle.read(MAX_BYTES + 1)
    except OSError:
        raise Blocked("ARTIFACT_IO", where) from None
    require(len(data) <= MAX_BYTES, "ARTIFACT_SIZE", where)
    return data


def artifact(root, descriptor, where, provenance):
    require(isinstance(descriptor, dict) and set(descriptor) == {"path", "sha256"},
            "MANIFEST_SCHEMA", where)
    raw_path, expected = descriptor["path"], descriptor["sha256"]
    require(isinstance(raw_path, str) and raw_path and isinstance(expected, str)
            and SHA.fullmatch(expected), "MANIFEST_SCHEMA", where)
    path = Path(raw_path)
    require("\u0000" not in raw_path and not path.is_absolute() and ".." not in path.parts, "ARTIFACT_PATH", where)
    try:
        resolved = (root / path).resolve()
        require(resolved.is_relative_to(root), "ARTIFACT_PATH", where)
    except (OSError, RuntimeError):
        raise Blocked("ARTIFACT_PATH", where) from None
    data = read_bytes(resolved, where)
    require(bool(data), "ARTIFACT_EMPTY", where)
    require(digest(data) == expected, "HASH_MISMATCH", where)
    provenance[where] = {"sha256": expected, "bytes": len(data)}
    return data


def validate_manifest(m):
    required = {"schema", "source_kind", "session_id", "connection_id", "level_id",
                "level_epoch", "map", "config", "tick_unit", "window",
                "layout", "producer", "participants"}
    require(isinstance(m, dict) and set(m) == required, "MANIFEST_SCHEMA", "manifest")
    require(m["schema"] == "tse-native-sync-capture/v1"
            and m["source_kind"] in ("synthetic", "native")
            and m["tick_unit"] == "engine_tick_index", "MANIFEST_SCHEMA", "format")
    require(all(name(m[k]) for k in ("session_id", "connection_id", "level_id"))
            and integer(m["level_epoch"]), "MANIFEST_SCHEMA", "identity")
    w = m["window"]
    require(isinstance(w, dict) and set(w) == {"first_sequence", "last_sequence", "first_tick", "tick_step"}
            and all(integer(v) for v in w.values()), "MANIFEST_SCHEMA", "window")
    count = w["last_sequence"] - w["first_sequence"] + 1
    require(1 <= count <= MAX_RECORDS and w["tick_step"] >= 1
            and integer(w["first_tick"] + (count - 1) * w["tick_step"]), "MANIFEST_SCHEMA", "window")
    layout = m["layout"]
    require(isinstance(layout, dict) and set(layout) == {"id", "phase", "players", "action_bytes", "state_fields", "binding_status", "evidence"}
            and name(layout["id"]) and layout["phase"] == "before_sync_crc",
            "MANIFEST_SCHEMA", "layout")
    players = layout["players"]
    require(isinstance(players, list) and players and all(name(v) for v in players)
            and len(players) == len(set(players)), "MANIFEST_SCHEMA", "layout.players")
    require(integer(layout["action_bytes"]) and layout["action_bytes"] > 0,
            "MANIFEST_SCHEMA", "layout.action_bytes")
    fields = layout["state_fields"]
    require(isinstance(fields, dict) and fields and all(name(k) and integer(v) and v > 0 for k, v in fields.items()),
            "MANIFEST_SCHEMA", "layout.state_fields")
    require(layout["binding_status"] in ("synthetic", "proposed", "verified-retail107"),
            "MANIFEST_SCHEMA", "layout.binding_status")
    require(m["source_kind"] != "native" or layout["binding_status"] == "verified-retail107",
            "UNVERIFIED_BINDING", "layout")
    producer = m["producer"]
    require(isinstance(producer, dict) and set(producer) == {"id", "version", "artifact"}
            and name(producer["id"]) and name(producer["version"]), "MANIFEST_SCHEMA", "producer")
    participants = m["participants"]
    require(isinstance(participants, dict) and set(participants) == {"server", "client"},
            "MANIFEST_SCHEMA", "participants")
    for role, participant in participants.items():
        require(isinstance(participant, dict) and set(participant) == {"capture_id", "dropped_records", "complete", "binaries", "records"}
                and name(participant["capture_id"]), "MANIFEST_SCHEMA", role)
        require(participant["complete"] is True and type(participant["dropped_records"]) is int
                and participant["dropped_records"] == 0, "CAPTURE_INCOMPLETE", role)
        require(isinstance(participant["binaries"], dict) and set(participant["binaries"]) == {"executable", "engine", "gamemp", "entities"},
                "MANIFEST_SCHEMA", role + ".binaries")
    require(participants["server"]["capture_id"] != participants["client"]["capture_id"],
            "MANIFEST_SCHEMA", "capture_id")
    return count


def records(data, m, count, role):
    try:
        lines = data.decode("utf-8").splitlines()
    except UnicodeError:
        raise Blocked("JSON_INVALID", role) from None
    require(len(lines) == count, "COVERAGE", role)
    result = []
    w = m["window"]
    for index, line in enumerate(lines):
        where = role + ".record." + str(index + 1)
        row = parse_json(line, where)
        require(isinstance(row, dict) and set(row) == RECORD_KEYS, "RECORD_SCHEMA", where)
        require(all(integer(row[k]) for k in ("level_epoch", "sequence", "tick"))
                and all(name(row[k]) for k in ("session_id", "connection_id"))
                and isinstance(row["crc32"], str) and CRC.fullmatch(row["crc32"]), "RECORD_SCHEMA", where)
        for key, schema_key in (("actions", "players"), ("state", "state_fields")):
            fields = row[key]
            require(isinstance(fields, dict) and set(fields) == set(m["layout"][schema_key])
                    and all(isinstance(v, str) and HEX.fullmatch(v)
                            and len(v) == 2 * (m["layout"]["action_bytes"] if key == "actions" else m["layout"]["state_fields"][k])
                            for k, v in fields.items()),
                    "RECORD_SCHEMA", where + "." + key)
        require(all(row[k] == m[k] for k in ("session_id", "connection_id", "level_epoch"))
                and row["sequence"] == w["first_sequence"] + index
                and row["tick"] == w["first_tick"] + index * w["tick_step"], "ALIGNMENT", where)
        result.append(row)
    return result


def field_hash(fields):
    canonical = {key: value.lower() for key, value in fields.items()}
    return digest(json.dumps(canonical, sort_keys=True, separators=(",", ":")).encode("ascii"))


def compare_capture(path):
    """Return BLOCKED before comparing any pair if a required artifact fails."""
    base = {"retail_runtime": "NOT_TESTED", "limitations": LIMITATIONS}
    try:
        path = Path(path).resolve()
        raw = read_bytes(path, "manifest")
        m = parse_json(raw, "manifest")
        count = validate_manifest(m)
        provenance = {"manifest_sha256": digest(raw), "artifacts": {}}
        verified = provenance["artifacts"]
        artifact(path.parent, m["map"], "map", verified)
        artifact(path.parent, m["config"], "config", verified)
        artifact(path.parent, m["layout"]["evidence"], "layout.evidence", verified)
        artifact(path.parent, m["producer"]["artifact"], "producer.artifact", verified)
        captures = {}
        for role, participant in m["participants"].items():
            for component, descriptor in participant["binaries"].items():
                artifact(path.parent, descriptor, role + ".binary." + component, verified)
            data = artifact(path.parent, participant["records"], role + ".records", verified)
            captures[role] = records(data, m, count, role)
        for component in ("engine", "entities"):
            hashes = [m["participants"][r]["binaries"][component]["sha256"] for r in ("server", "client")]
            require(hashes[0] == hashes[1], "SHARED_BINARY_MISMATCH", component)
        differences = []
        for index, (server, client) in enumerate(zip(captures["server"], captures["client"]), 1):
            domains = []
            if server["crc32"].lower() != client["crc32"].lower():
                domains.append("crc32")
            for domain in ("actions", "state"):
                if field_hash(server[domain]) != field_hash(client[domain]):
                    domains.append(domain)
            if domains:
                differences.append({"sequence": server["sequence"], "tick": server["tick"],
                                    "domains": domains,
                                    "record_line": index,
                                    "previous_pair_matched": not differences and server["sequence"] > m["window"]["first_sequence"]})
        result = {**base, "status": "DIFFERENT_WINDOW" if differences else "MATCHED_WINDOW",
                  "source_kind": m["source_kind"], "pairs_compared": count,
                  "different_pairs": len(differences), "window": m["window"],
                  "layout_id": m["layout"]["id"], "provenance": provenance}
        if differences:
            result["first_observed_difference"] = differences[0]
        return result
    except Blocked as error:
        return {**base, "status": "BLOCKED", "issues": [{"code": error.code, "where": error.where}]}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("manifest", type=Path)
    args = parser.parse_args()
    result = compare_capture(args.manifest)
    print(json.dumps(result, sort_keys=True, indent=2))
    return {"MATCHED_WINDOW": 0, "DIFFERENT_WINDOW": 3, "BLOCKED": 2}[result["status"]]


if __name__ == "__main__":
    raise SystemExit(main())
