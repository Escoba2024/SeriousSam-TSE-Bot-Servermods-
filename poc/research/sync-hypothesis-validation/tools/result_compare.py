#!/usr/bin/env python3
"""Merge tool results into one report and detect contradictory evidence.

"Improve the result comparison" means more than concatenating JSON: the merge
must notice when two artifacts cannot both be true, and it must never let a
weaker (offline) artifact borrow the authority of a stronger (native) one.

Checked conflicts
-----------------
GRADE_INFLATION
    A payload declares an evidence class that its tool kind cannot produce
    (e.g. the offline float model claiming ``native``).
NATIVE_CLAIM_WITHOUT_COMPLETE_BUNDLE
    A verdict payload contains ``NATIVE_SUPPORTED`` while the bundle audit is
    missing or not ``COMPLETE``.
SIMULATED_INPUT_MIXED
    The audit says ``SIMULATED_NEVER_NATIVE`` while a verdict payload still
    claims native support.
TOOL_DISAGREEMENT
    Two inputs of the same kind report different verdicts.
INCONSISTENT_TIMELINE
    The checksum-scope probe reports a checksum-visible action divergence that
    starts *after* the first logged SYNCBAD tick - the probe then contradicts
    its own causal claim.
MANIFEST_SIMULATED_FLAG
    ``simulated`` is not ``false`` in an audit result yet another input treats
    the run as native.

Exit codes
----------
0  NO_CONFLICT (and a complete bundle with verdicts is present)
4  INSUFFICIENT (no complete bundle and/or no verdicts)
6  CONFLICT
2  usage error
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import Dict, List, Optional

sys.path.insert(0, str(Path(__file__).resolve().parent))

from syncval_common import (  # noqa: E402
    EVIDENCE_CLASSES, EXIT_CONFLICT, EXIT_INCOMPLETE, EXIT_OK, EXIT_USAGE,
    SyncValError, base_payload, emit, read_json, require,
)

TOOL = "result_compare"

ALLOWED_GRADES: Dict[str, set] = {
    "fp": {"model"},
    "cadence": {"simulation", "model", "log", "telemetry", "native"},
    "coverage": {"simulation", "model", "log", "telemetry", "native"},
    "audit": {"simulation", "telemetry", "native"},
    "verdicts": {"model"},
    "crc_diff": {"simulation", "log", "telemetry", "native"},
    "opaque": set(EVIDENCE_CLASSES),
}

NATIVE_STATES = {"NATIVE_SUPPORTED"}
BLOCKING_STATES = {"CONFLICT"}


def _load(kind: str, path: str) -> Dict[str, object]:
    require(kind in ALLOWED_GRADES, "unknown input kind: %s" % kind)
    payload = read_json(path)
    require(isinstance(payload, dict), "%s: payload must be a JSON object" % path)
    return payload


def _facts(kind: str, payload: Dict[str, object]) -> Dict[str, object]:
    facts: Dict[str, object] = {
        "kind": kind,
        "tool": payload.get("tool"),
        "evidence_class": payload.get("evidence_class"),
        "verdict": payload.get("verdict"),
    }
    if kind == "verdicts":
        facts["native_supported"] = list(payload.get("native_supported") or [])
        facts["hypothesis_counts"] = payload.get("counts")
        facts["conflicts"] = list(payload.get("conflicts") or [])
        facts["resolved"] = list(payload.get("resolved") or [])
        facts["unresolved"] = list(payload.get("unresolved") or [])
    if kind == "coverage":
        facts["first_checksum_visible_divergence_tick"] = \
            payload.get("first_checksum_visible_divergence_tick")
        facts["consistency_with_log"] = (payload.get("consistency_with_log") or {}).get("status")
        facts["layout_status"] = (payload.get("layout") or {}).get("status")
    if kind == "cadence":
        summary = payload.get("summary") or {}
        facts["divergence_windows"] = summary.get("divergence_windows")
        facts["tick_rate_hz_measured"] = summary.get("tick_rate_hz_measured")
    if kind == "audit":
        facts["simulated"] = payload.get("manifest_simulated")
        facts["missing"] = list(payload.get("missing") or [])
        facts["observations_grade"] = payload.get("evidence_class_after_audit")
        facts["aligned_pairs"] = (payload.get("dumps") or {}).get("aligned_pairs")
    if kind == "fp":
        facts["earliest_divergence_tick"] = payload.get("earliest_divergence_tick")
    return facts


def compare(inputs: List[Dict[str, object]]) -> Dict[str, object]:
    facts = [_facts(str(entry["kind"]), entry["payload"]) for entry in inputs]
    conflicts: List[Dict[str, object]] = []
    notes: List[str] = []

    # --- grade inflation ---------------------------------------------------
    for fact in facts:
        kind = str(fact["kind"])
        grade = fact.get("evidence_class")
        allowed = ALLOWED_GRADES[kind]
        if grade not in EVIDENCE_CLASSES:
            conflicts.append({"rule": "GRADE_INFLATION", "kind": kind,
                              "detail": "missing or unknown evidence_class %r" % (grade,)})
            continue
        if grade not in allowed:
            conflicts.append({
                "rule": "GRADE_INFLATION", "kind": kind,
                "declared": grade, "allowed_for_kind": sorted(allowed),
                "detail": "tool kind cannot produce this evidence grade",
            })

    # --- tool disagreement -------------------------------------------------
    by_kind: Dict[str, List[Dict[str, object]]] = {}
    for fact in facts:
        by_kind.setdefault(str(fact["kind"]), []).append(fact)
    for kind, group in by_kind.items():
        verdicts = {str(f.get("verdict")) for f in group if f.get("verdict") is not None}
        if len(verdicts) > 1:
            conflicts.append({"rule": "TOOL_DISAGREEMENT", "kind": kind,
                              "verdicts": sorted(verdicts)})

    # --- native claim vs bundle completeness -------------------------------
    audits = [f for f in facts if f["kind"] == "audit"]
    verdicts = [f for f in facts if f["kind"] == "verdicts"]
    bundle_complete = any(f.get("verdict") == "COMPLETE" for f in audits)
    simulated_audit = any(f.get("verdict") == "SIMULATED_NEVER_NATIVE" for f in audits)
    native_claims = [f for f in verdicts if f.get("native_supported")]

    if native_claims and not bundle_complete:
        conflicts.append({
            "rule": "NATIVE_CLAIM_WITHOUT_COMPLETE_BUNDLE",
            "hypotheses": sorted({h for f in native_claims for h in f["native_supported"]}),
            "detail": "no COMPLETE evidence bundle was provided",
        })
    if native_claims and simulated_audit:
        conflicts.append({
            "rule": "SIMULATED_INPUT_MIXED",
            "detail": "audited bundle is a generated fixture but verdicts claim native support",
        })
    for fact in audits:
        if fact.get("simulated") not in (False, None) and fact.get("verdict") != "SIMULATED_NEVER_NATIVE":
            conflicts.append({
                "rule": "MANIFEST_SIMULATED_FLAG", "kind": "audit",
                "detail": "manifest.simulated=%r" % (fact.get("simulated"),),
            })

    # --- internal timeline contradiction -----------------------------------
    for fact in [f for f in facts if f["kind"] == "coverage"]:
        if fact.get("verdict") == "CHECKSUM_VISIBLE_DIVERGENCE" and \
                fact.get("consistency_with_log") == "INCONSISTENT_TOO_LATE":
            conflicts.append({
                "rule": "INCONSISTENT_TIMELINE", "kind": "coverage",
                "detail": ("checksum-visible action divergence starts after the first "
                           "logged SYNCBAD tick, so it cannot be that tick's cause"),
            })
    for fact in [f for f in facts if f["kind"] == "verdicts"]:
        if fact.get("conflicts"):
            conflicts.append({"rule": "HYPOTHESIS_CONFLICT", "kind": "verdicts",
                              "hypotheses": fact["conflicts"]})

    # --- evidence inventory ------------------------------------------------
    inventory = {
        "bundle_audit": bool(audits),
        "bundle_complete": bundle_complete,
        "hypothesis_verdicts": bool(verdicts),
        "cadence_telemetry": any(f["kind"] == "cadence" for f in facts),
        "checksum_scope": any(f["kind"] == "coverage" for f in facts),
        "fp_model": any(f["kind"] == "fp" for f in facts),
        "aligned_dumps": any((f.get("aligned_pairs") or 0) > 0 for f in audits),
    }
    missing_evidence = [name for name, present in inventory.items() if not present]

    payload = base_payload(TOOL, "model")
    payload.update({
        "inputs": [{"kind": e["kind"], "file": Path(str(e["path"])).name} for e in inputs],
        "facts": facts,
        "conflicts": conflicts,
        "notes": notes,
        "evidence_inventory": inventory,
        "missing_evidence": missing_evidence,
        "native_acceptance": False,
        "interpretation": (
            "NO_CONFLICT means the supplied artifacts do not contradict each other. "
            "It is explicitly not a stability pass and not a root-cause confirmation; "
            "only a native run with a complete bundle plus a discriminating "
            "experiment can decide between the supported hypotheses."
        ),
    })

    if conflicts:
        payload["overall"] = "CONFLICT"
    elif not bundle_complete or not verdicts:
        payload["overall"] = "INSUFFICIENT"
    else:
        payload["overall"] = "NO_CONFLICT"

    payload["next_actions"] = _next_actions(inventory, conflicts)
    return payload


def _next_actions(inventory: Dict[str, bool],
                  conflicts: List[Dict[str, object]]) -> List[str]:
    actions: List[str] = []
    rules = {str(conflict["rule"]) for conflict in conflicts}
    if not inventory["bundle_audit"]:
        actions.append("produce a native bundle per the instrumentation contract "
                       "and audit it (evidence_bundle_audit.py --bundle ...)")
    if inventory["bundle_audit"] and not inventory["bundle_complete"]:
        actions.append("close the bundle gaps listed in audit.missing / audit.problems")
    if not inventory["cadence_telemetry"]:
        actions.append("record BotTelemetry.csv with the shipped telemetry build and "
                       "declare --source-class telemetry only for a real run")
    if not inventory["checksum_scope"]:
        actions.append("capture aligned client/server action traces (byte images) to "
                       "run checksum_coverage_probe.py")
    if "INCONSISTENT_TIMELINE" in rules:
        actions.append("re-stamp action traces and dumps with the same tick origin as "
                       "the server log (requirement R4) and re-run the probe")
    if "GRADE_INFLATION" in rules:
        actions.append("fix the evidence class of the offending input; an offline "
                       "model must never be declared native")
    if "NATIVE_CLAIM_WITHOUT_COMPLETE_BUNDLE" in rules:
        actions.append("do not cite native support: the bundle audit is not COMPLETE")
    if not actions:
        actions.append("run the discriminating experiment S5 (see the C2 native plan) "
                       "to separate the supported hypotheses")
    return actions


def exit_code_for(overall: str) -> int:
    if overall == "CONFLICT":
        return EXIT_CONFLICT
    if overall == "INSUFFICIENT":
        return EXIT_INCOMPLETE
    return EXIT_OK


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--input", action="append", default=[],
                        metavar="KIND=PATH",
                        help="kinds: fp, cadence, coverage, audit, verdicts, "
                             "crc_diff, opaque (repeatable)")
    parser.add_argument("--out")
    args = parser.parse_args()

    require(args.input, "at least one --input KIND=PATH is required")
    inputs: List[Dict[str, object]] = []
    for raw in args.input:
        require("=" in raw, "--input must be KIND=PATH, got %r" % raw)
        kind, path = raw.split("=", 1)
        kind = kind.strip().lower()
        payload = _load(kind, path)
        inputs.append({"kind": kind, "path": path, "payload": payload})

    payload = compare(inputs)
    payload["inputs_declared"] = [raw.split("=", 1)[0] for raw in args.input]
    emit(payload, args.out)
    return exit_code_for(str(payload["overall"]))


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except SyncValError as exc:
        print("error: %s" % exc, file=sys.stderr)
        raise SystemExit(EXIT_USAGE)
