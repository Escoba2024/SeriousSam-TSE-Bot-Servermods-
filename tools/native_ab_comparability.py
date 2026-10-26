"""Read-only, privacy-minimal A/B receipt comparability prerequisite.

This tool NEVER establishes Retail sync health, causation or release readiness.
It does not read gameplay logs, process state or any client identifiers.
"""
import argparse
import json
import re
from pathlib import Path

HEX64 = re.compile(r"^[a-fA-F0-9]{64}$")
HARNESS = (
    "qualify_bot_sessions.py",
    "bot_session_executor.py",
    "bot_session_runtime.py",
    "bot_sessions.py",
    "qualify_integrated_wine.py",
)
SETTINGS = (
    "accelerated",
    "original_client",
    "colors_enabled",
    "private_color_probe",
    "low_memory_rendering",
    "observer_fps_cap",
    "preset",
)
EXPECTED_SCOPE = "ISOLATED_NETNS_RETAIL_WINE"
ALLOWED_STATUS = frozenset({"FAIL", "PASS", "PASS_LIMITED", "PASS_LIMITED_SESSION_LIFECYCLE", "BLOCKED", "INCOMPLETE"})


def _read_json(folder: Path, name: str) -> dict:
    try:
        p = folder / name
        value = json.loads(p.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, ValueError) as exc:
        raise ValueError(f"unreadable or malformed {name}") from exc
    if not isinstance(value, dict):
        raise ValueError(f"invalid {name} structure")
    return value


def _validate_receipt(value: dict) -> None:
    h = value.get("dll_sha256")
    if not isinstance(h, str) or not HEX64.fullmatch(h):
        raise ValueError("missing or invalid dll_sha256")
    status = value.get("status")
    if not isinstance(status, str) or status not in ALLOWED_STATUS:
        raise ValueError("unknown or missing status")
    if not isinstance(value.get("scope"), str):
        raise ValueError("missing scope")


def _observation(value: dict) -> dict:
    """Whitelist of non-private, status-only fields; never copy raw errors."""
    return {
        "status": value["status"],
        "elapsed_s": value.get("elapsed_s") if isinstance(value.get("elapsed_s"), (int, float)) else None,
        "max_bots": value.get("max_bots") if type(value.get("max_bots")) is int else None,
        "peak_playing": value.get("peak_playing") if type(value.get("peak_playing")) is int else None,
    }


def compare_runs(control_dir: Path, candidate_dir: Path) -> dict:
    """Contrast receipts; matching metadata is NOT native gameplay acceptance."""
    control = _read_json(control_dir, "result.json")
    candidate = _read_json(candidate_dir, "result.json")
    sources_control = _read_json(control_dir, "source-sha256.json")
    sources_candidate = _read_json(candidate_dir, "source-sha256.json")
    for result in (control, candidate):
        _validate_receipt(result)

    problems = []
    if control["scope"] != EXPECTED_SCOPE or candidate["scope"] != EXPECTED_SCOPE:
        problems.append("scope_MISMATCH_OR_NON_NATIVE")
    if control["dll_sha256"].lower() != candidate["dll_sha256"].lower():
        problems.append("DLL_SHA256_MISMATCH")
    if control.get("cecil_p1") is not False or candidate.get("cecil_p1") is not True:
        problems.append("CECIL_P1_NOT_EXPLICIT_OFF_ON")

    for item in ("max_bots", "peak_playing"):
        if any(type(d.get(item)) is not int or d.get(item) != 4 for d in (control, candidate)):
            problems.append(f"{item}_NOT_FOUR")
    for key in SETTINGS:
        if key not in control or key not in candidate or control[key] is None or candidate[key] is None:
            problems.append(f"{key}_MISSING")
        elif control[key] != candidate[key] or type(control[key]) is not type(candidate[key]):
            problems.append(f"{key}_MISMATCH")
    if control.get("original_client") is not True or candidate.get("original_client") is not True:
        problems.append("ORIGINAL_CLIENT_NOT_VERIFIED")

    for key in HARNESS:
        v1, v2 = sources_control.get(key), sources_candidate.get(key)
        if v1 is None or v2 is None:
            problems.append(f"HARNESS_{key}_MISSING")
        elif not isinstance(v1, str) or not HEX64.fullmatch(v1) or not isinstance(v2, str) or not HEX64.fullmatch(v2):
            problems.append(f"HARNESS_{key}_INVALID_HASH")
        elif v1.lower() != v2.lower():
            problems.append(f"HARNESS_{key}_MISMATCH")

    return {
        "verdict": "CONFOUNDED" if problems else "CONTROLLED_TOGGLE_RECEIPTS_ONLY",
        "reasons": sorted(set(problems)),
        "evidence_class": "UNVERIFIED_NATIVE_RECEIPT_METADATA",
        "release_qualification": "NOT_ESTABLISHED",
        "native_crc_causation": "NOT_ESTABLISHED",
        "control": _observation(control),
        "candidate": _observation(candidate),
    }


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--control", required=True, type=Path)
    parser.add_argument("--candidate", required=True, type=Path)
    args = parser.parse_args(argv)
    try:
        result = compare_runs(args.control, args.candidate)
    except ValueError:
        print(json.dumps({
            "verdict": "INVALID_INPUT",
            "release_qualification": "NOT_ESTABLISHED",
            "native_crc_causation": "NOT_ESTABLISHED",
        }))
        return 2
    print(json.dumps(result, sort_keys=True, indent=2))
    return 3 if result["verdict"] == "CONFOUNDED" else 0


if __name__ == "__main__":
    raise SystemExit(main())
