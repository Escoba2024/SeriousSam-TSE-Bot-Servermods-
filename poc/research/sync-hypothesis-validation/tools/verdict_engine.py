#!/usr/bin/env python3
"""Evaluate the hypothesis registry against observations.

Verdict states (deliberately not binary, deliberately never "confirmed"):

=============== ==========================================================
NOT_TESTED      None of the required observations is present.
INCONCLUSIVE    Some required observations are present, but neither the
                support nor the refute block fires.
MODEL_SUPPORTED The support block fires, but at least one contributing
                observation is offline (``model``/``simulation``), so the
                result may not be used as native evidence.
NATIVE_SUPPORTED The support block fires and every contributing observation
                comes from a real run (``log``/``telemetry``/``native``).
REFUTED         The refute block fires (and support does not).
CONFLICT        Support and refute both fire, or two observations of the
                same id disagree. Fail-closed: a conflict blocks downstream
                conclusions and is reported as such.
=============== ==========================================================

There is intentionally no state called "proven" or "root cause". The engine
also refuses to derive ``NATIVE_SUPPORTED`` from a hypothesis whose
``min_evidence_class`` is ``native`` unless the observations are actually at
least that strong.

Input
-----
One or more JSON files. Every file may contain an ``observations`` array
anywhere in its structure (all probes and the bundle audit emit one), so tool
outputs can be piped in unchanged::

    {"observations": [{"id": "cadence.divergence_windows", "value": 7,
                       "evidence_class": "telemetry", "source": "BotTelemetry.csv"}]}

Exit codes
----------
0  no conflict, at least one hypothesis resolved
4  nothing testable (every hypothesis NOT_TESTED / INCONCLUSIVE)
6  conflict detected
2  usage error
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import Dict, List, Optional, Tuple

sys.path.insert(0, str(Path(__file__).resolve().parent))

from syncval_common import (  # noqa: E402
    EVIDENCE_CLASSES, EXIT_CONFLICT, EXIT_INCOMPLETE, EXIT_OK, EXIT_USAGE,
    NATIVE_OK, SyncValError, base_payload, collect_observations, emit,
    read_json, require,
)
from hypothesis_registry import HYPOTHESES, OPS  # noqa: E402

TOOL = "verdict_engine"

VERDICT_STATES = ("NOT_TESTED", "INCONCLUSIVE", "MODEL_SUPPORTED",
                  "NATIVE_SUPPORTED", "REFUTED", "CONFLICT")

CLASS_RANK = {name: index for index, name in enumerate(EVIDENCE_CLASSES)}


def _compare(actual: object, op: str, expected: object) -> bool:
    if op == "is_true":
        return actual is True
    if op == "is_false":
        return actual is False
    if op == "is_null":
        return actual is None
    if op == "not_null":
        return actual is not None
    if op == "in":
        return isinstance(expected, list) and actual in expected
    if op == "not_in":
        return isinstance(expected, list) and actual not in expected
    if actual is None or expected is None:
        return False
    try:
        if op == "eq":
            return actual == expected
        if op == "ne":
            return actual != expected
        if op == "lt":
            return float(actual) < float(expected)
        if op == "le":
            return float(actual) <= float(expected)
        if op == "gt":
            return float(actual) > float(expected)
        if op == "ge":
            return float(actual) >= float(expected)
    except (TypeError, ValueError):
        return False
    raise SyncValError("unknown operator: %s" % op)


def evaluate_block(block: Dict[str, object], observations: Dict[str, List[dict]]
                   ) -> Tuple[bool, List[Dict[str, object]]]:
    """Return (block_fires, per-rule trace)."""
    rules = block.get("rules") or []
    traces: List[Dict[str, object]] = []
    fired: List[bool] = []
    for rule in rules:
        obs_id = rule["obs"]
        entries = observations.get(obs_id) or []
        if not entries:
            traces.append({"obs": obs_id, "op": rule.get("op"),
                           "value": rule.get("value"), "result": None,
                           "reason": "observation missing"})
            fired.append(False)
            continue
        # A rule fires only if *every* recorded value of that observation
        # matches. Disagreeing duplicates therefore suppress a fire and show
        # up as a conflict instead of silently picking a winner.
        results = [_compare(entry.get("value"), str(rule.get("op")),
                            rule.get("value")) for entry in entries]
        fired.append(all(results))
        traces.append({
            "obs": obs_id,
            "op": rule.get("op"),
            "value": rule.get("value"),
            "observed": [entry.get("value") for entry in entries],
            "result": all(results),
            "partial": any(results) and not all(results),
        })
    mode = block.get("mode", "any")
    block_fires = (any(fired) if mode == "any" else all(fired)) and bool(fired)
    return block_fires, traces


def evaluate_hypothesis(entry: Dict[str, object],
                        observations: Dict[str, List[dict]]) -> Dict[str, object]:
    required = list(entry.get("required_observations") or [])
    present = [obs_id for obs_id in required if observations.get(obs_id)]
    missing = [obs_id for obs_id in required if not observations.get(obs_id)]

    support_fires, support_trace = evaluate_block(entry["support_when"], observations)
    refute_fires, refute_trace = evaluate_block(entry["refute_when"], observations)

    result: Dict[str, object] = {
        "id": entry["id"],
        "priority": entry.get("priority"),
        "title": entry.get("title"),
        "required_observations": required,
        "missing_observations": missing,
        "support_trace": support_trace,
        "refute_trace": refute_trace,
        "support_fires": support_fires,
        "refute_fires": refute_fires,
    }

    if not present:
        result["verdict"] = "NOT_TESTED"
        result["reason"] = "no required observation available"
        return result
    if missing:
        result["verdict"] = "INCONCLUSIVE"
        result["reason"] = "missing observations: %s" % ", ".join(missing)
        return result
    if support_fires and refute_fires:
        result["verdict"] = "CONFLICT"
        result["reason"] = "support and refute blocks both fire"
        return result
    if refute_fires:
        result["verdict"] = "REFUTED"
        result["reason"] = "refute block fires"
        return result
    if not support_fires:
        result["verdict"] = "INCONCLUSIVE"
        result["reason"] = "no threshold reached"
        return result

    # Support fires: decide the evidence grade.
    contributing = []
    for obs_id in required:
        contributing.extend(observations.get(obs_id) or [])
    classes = {str(obs.get("evidence_class")) for obs in contributing}
    unknown = classes - set(EVIDENCE_CLASSES)
    if unknown:
        raise SyncValError("observations with unknown evidence class: %s"
                           % ", ".join(sorted(unknown)))
    weakest = min(classes, key=lambda name: CLASS_RANK[name])
    min_required = str(entry.get("min_evidence_class", "telemetry"))
    result["observation_evidence_classes"] = sorted(classes)
    result["weakest_evidence_class"] = weakest
    if weakest not in NATIVE_OK:
        result["verdict"] = "MODEL_SUPPORTED"
        result["reason"] = ("support fires, but the weakest contributing evidence "
                            "is %r (offline)" % weakest)
        return result
    if CLASS_RANK[weakest] < CLASS_RANK[min_required]:
        result["verdict"] = "MODEL_SUPPORTED"
        result["reason"] = ("support fires, but evidence class %r is below the "
                            "hypothesis minimum %r" % (weakest, min_required))
        return result
    result["verdict"] = "NATIVE_SUPPORTED"
    result["reason"] = "support fires on runtime evidence of class %r" % weakest
    return result


def evaluate(observations: List[dict], registry: Optional[List[dict]] = None
             ) -> Dict[str, object]:
    index: Dict[str, List[dict]] = {}
    for obs in observations:
        require(isinstance(obs, dict), "observation must be an object")
        require(isinstance(obs.get("id"), str) and obs["id"],
                "observation needs an id")
        require(obs.get("evidence_class") in EVIDENCE_CLASSES,
                "observation %s has invalid evidence_class" % obs["id"])
        index.setdefault(str(obs["id"]), []).append(obs)

    disagreements = []
    for obs_id, entries in index.items():
        values = {repr(entry.get("value")) for entry in entries}
        if len(values) > 1:
            disagreements.append({
                "observation": obs_id,
                "values": [entry.get("value") for entry in entries],
                "sources": [entry.get("source") for entry in entries],
            })

    entries = registry if registry is not None else HYPOTHESES
    results = [evaluate_hypothesis(entry, index) for entry in entries]
    counts: Dict[str, int] = {}
    for result in results:
        counts[str(result["verdict"])] = counts.get(str(result["verdict"]), 0) + 1

    payload = base_payload(TOOL, "model")
    payload.update({
        "observation_count": len(observations),
        "observations_known": sorted(index),
        "observation_disagreements": disagreements,
        "hypotheses": results,
        "counts": counts,
        "resolved": [r["id"] for r in results
                     if r["verdict"] in ("REFUTED", "MODEL_SUPPORTED", "NATIVE_SUPPORTED")],
        "unresolved": [r["id"] for r in results
                       if r["verdict"] in ("NOT_TESTED", "INCONCLUSIVE")],
        "conflicts": [r["id"] for r in results if r["verdict"] == "CONFLICT"],
        "native_supported": [r["id"] for r in results
                             if r["verdict"] == "NATIVE_SUPPORTED"],
        "model_supported": [r["id"] for r in results
                            if r["verdict"] == "MODEL_SUPPORTED"],
        "refuted": [r["id"] for r in results if r["verdict"] == "REFUTED"],
        "root_cause_status": "NOT_ESTABLISHED",
        "interpretation": (
            "NATIVE_SUPPORTED means 'the recorded runtime observation matches this "
            "hypothesis', not 'this hypothesis is the root cause'. Multiple "
            "hypotheses may be supported at once; only a discriminating native "
            "experiment (docs/research/sync-hypothesis-validation/"
            "2026-10-25-codex-c2-native-validation-plan.md) can separate them."
        ),
    })
    if disagreements:
        payload["conflicts"] = list(payload["conflicts"]) + ["OBSERVATION_DISAGREEMENT"]
    return payload


def exit_code_for(payload: Dict[str, object]) -> int:
    if payload["conflicts"]:
        return EXIT_CONFLICT
    if not payload["resolved"]:
        return EXIT_INCOMPLETE
    return EXIT_OK


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("inputs", nargs="+", help="tool outputs or observation files")
    parser.add_argument("--out")
    args = parser.parse_args()

    observations: List[dict] = []
    for raw in args.inputs:
        payload = read_json(raw)
        found = collect_observations(payload)
        require(found, "no observations found in %s" % raw)
        observations.extend(found)

    payload = evaluate(observations)
    payload["inputs"] = [Path(p).name for p in args.inputs]
    emit(payload, args.out)
    return exit_code_for(payload)


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except SyncValError as exc:
        print("error: %s" % exc, file=sys.stderr)
        raise SystemExit(EXIT_USAGE)
