#!/usr/bin/env python3
"""Checksum-scope probe for ``CPlayerAction`` byte images.

Why this tool exists
--------------------
The strongest static finding about the 1.07 sync checksum is narrow: PR #21
reports that ``CPlayerAction::ChecksumForSync`` (RVA ``0x6019EC10``) consumes
**exactly four consecutive bytes per call** and that
``CSessionState::ChecksumForSync`` calls it twice per player. That means the
per-player part of the sync CRC is computed over a small window of the action
byte image - not over "the action" as a whole.

Consequence, and the question this probe answers mechanically:

* Fields outside the covered window **cannot** change the checksum even if the
  bot composes them differently from vanilla.
* Fields inside the window **must** be byte-identical between the action the
  client used and the action the server applied, otherwise SYNCBAD follows.

The probe therefore cannot prove a root cause. It can falsify scope claims:

* "the bot's action differs from vanilla only in field X" is worthless if X is
  outside the covered window, and fatal if X is inside it.
* A covered-byte divergence that starts *later* than the first observed
  SYNCBAD tick cannot explain that SYNCBAD.

Inputs
------
* ``--layout``: a layout *hypothesis* (JSON). ``status`` must be
  ``VERIFIED_107`` for the result to count as more than a layout hypothesis.
  The 1.07 struct layout is **not** verified in this repository; only offsets
  taken from the actual 1.07 SDK header may be marked ``VERIFIED_107``.
* ``--client-trace`` / ``--server-trace``: ``syncval action trace`` files with
  the raw action byte image per (tick, slot).
* optional ``--first-bad-tick``: the tick reported by the server log, so the
  probe can test whether an action-level divergence could even precede it.
  This comparison is only meaningful when both artefacts share one tick origin
  (instrumentation requirement R4); with different origins the consistency
  field is meaningless and must not be cited.

Exit codes
----------
0  no divergence in the traces
3  divergence found (visible in checksum scope, or only outside it)
4  incomplete / unalignable input
5  layout hypothesis unverified (result is layout-conditional only)
2  usage or parse error
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import Dict, List, Optional

sys.path.insert(0, str(Path(__file__).resolve().parent))

from syncval_common import (  # noqa: E402
    EXIT_DIVERGENCE, EXIT_INCOMPLETE, EXIT_OK, EXIT_USAGE, EXIT_INVALID,
    SyncValError, base_payload, differing_bytes, emit, observation,
    parse_action_trace, parse_layout, read_json, require,
)

TOOL = "checksum_coverage_probe"


def coverage_report(layout) -> Dict[str, object]:
    covered = layout.covered_bytes()
    table = []
    for span in layout.fields:
        table.append({
            "field": span.name,
            "offset": span.offset,
            "size": span.size,
            "in_checksum_scope": layout.coverage_of(span),
        })
    inside = [row["field"] for row in table if row["in_checksum_scope"] == "INSIDE"]
    partial = [row["field"] for row in table if row["in_checksum_scope"] == "PARTIAL"]
    outside = [row["field"] for row in table if row["in_checksum_scope"] == "OUTSIDE"]
    return {
        "covered_byte_offsets": covered,
        "covered_byte_count": len(covered),
        "fields_fully_covered": inside,
        "fields_partially_covered": partial,
        "fields_never_covered": outside,
        "fields": table,
    }


def _analyse_inner(client, server, layout, first_bad_tick: Optional[float],
                   trace_class: str = "simulation") -> Dict[str, object]:
    covered = set(layout.covered_bytes())
    shared = sorted(set(client.samples) & set(server.samples))
    only_client = sorted(set(client.samples) - set(server.samples))
    only_server = sorted(set(server.samples) - set(client.samples))

    pairs: List[Dict[str, object]] = []
    first_any: Optional[int] = None
    first_visible: Optional[int] = None
    mismatched_lengths = 0

    for key in shared:
        left = client.samples[key]
        right = server.samples[key]
        if len(left) != len(right):
            mismatched_lengths += 1
            continue
        diff = differing_bytes(left, right)
        visible = [i for i in diff if i in covered]
        outside = [i for i in diff if i not in covered]
        tick, slot = key
        if diff and first_any is None:
            first_any = tick
        if visible and first_visible is None:
            first_visible = tick
        if diff:
            pairs.append({
                "tick": tick,
                "slot": slot,
                "differing_byte_offsets": diff,
                "visible_in_checksum": visible,
                "outside_checksum": outside,
                "fields_visible": sorted({name for i in visible
                                          for name in layout.field_at(i)}),
                "fields_outside": sorted({name for i in outside
                                          for name in layout.field_at(i)}),
            })

    layout_verified = layout.status == "VERIFIED_107"
    payload = base_payload(TOOL, trace_class)
    payload.update({
        "layout": {
            "status": layout.status,
            "source": layout.source,
            "struct_size": layout.struct_size,
            "checksum_calls": [{"offset": o, "length": n}
                               for o, n in layout.checksum_calls],
            "errors": layout.errors,
        },
        "coverage": coverage_report(layout),
        "alignment": {
            "aligned_samples": len(shared),
            "client_only": len(only_client),
            "server_only": len(only_server),
            "length_mismatches": mismatched_lengths,
            "client_parse_errors": client.errors[:20],
            "server_parse_errors": server.errors[:20],
        },
        "first_any_divergence_tick": first_any,
        "first_checksum_visible_divergence_tick": first_visible,
        "divergent_sample_count": len(pairs),
        "divergent_samples": pairs[:50],
        "first_bad_tick_reported_by_log": first_bad_tick,
        "consistency_with_log": _log_consistency(first_visible, first_any, first_bad_tick),
    })

    if client.errors or server.errors or not shared or mismatched_lengths \
            or only_client or only_server:
        payload["verdict"] = "INCOMPLETE"
        payload["verdict_detail"] = (
            "traces are not a complete aligned pair; missing counterparts or parse "
            "errors forbid a divergence statement"
        )
        return payload

    if not layout_verified:
        payload["verdict"] = "LAYOUT_UNVERIFIED"
        payload["verdict_detail"] = (
            "Offsets are a hypothesis. The result only states what would follow "
            "*if* this layout were correct; it cannot be used as native evidence."
        )
        return payload

    if first_visible is not None:
        payload["verdict"] = "CHECKSUM_VISIBLE_DIVERGENCE"
        return payload

    if first_any is not None:
        payload["verdict"] = "DIVERGENCE_OUTSIDE_CHECKSUM_SCOPE"
        payload["verdict_detail"] = (
            "The action byte images differ, but not in the bytes the checksum "
            "covers. Such a difference cannot be the direct cause of a SYNCBAD "
            "of this client's action checksum; look at entity/session state."
        )
        return payload

    payload["verdict"] = "NO_ACTION_DIVERGENCE"
    return payload


def analyse(client, server, layout, first_bad_tick: Optional[float],
            trace_class: str = "simulation") -> Dict[str, object]:
    """Analyse traces and attach the observation block for verdict_engine."""
    payload = _analyse_inner(client, server, layout, first_bad_tick, trace_class)
    source = "%s|%s" % (Path(client.path).name, Path(server.path).name)
    payload["observations"] = [
        observation("coverage.verdict", payload["verdict"], trace_class, source),
        observation("coverage.layout_status", layout.status, "model", layout.source),
        observation("coverage.log_consistency",
                    payload["consistency_with_log"]["status"], trace_class, source),
        observation("coverage.first_checksum_visible_divergence_tick",
                    payload["first_checksum_visible_divergence_tick"],
                    trace_class, source),
        observation("coverage.first_any_divergence_tick",
                    payload["first_any_divergence_tick"], trace_class, source),
    ]
    return payload


def _log_consistency(first_visible: Optional[int], first_any: Optional[int],
                     first_bad_tick: Optional[float]) -> Dict[str, object]:
    if first_bad_tick is None:
        return {"status": "NO_LOG_TICK"}
    if first_visible is None:
        return {"status": "NO_VISIBLE_DIVERGENCE",
                "detail": "action bytes cannot explain the reported SYNCBAD"}
    if first_visible <= first_bad_tick:
        return {"status": "CONSISTENT_PRECEDES",
                "detail": "action-level divergence precedes or coincides with the log tick"}
    return {
        "status": "INCONSISTENT_TOO_LATE",
        "detail": ("first checksum-visible action divergence (%s) is later than the "
                   "first reported SYNCBAD (%s); the action path alone cannot explain it"
                   % (first_visible, first_bad_tick)),
    }


def exit_code_for(verdict: str) -> int:
    if verdict == "INCOMPLETE":
        return EXIT_INCOMPLETE
    if verdict == "LAYOUT_UNVERIFIED":
        return EXIT_INVALID
    if verdict in ("CHECKSUM_VISIBLE_DIVERGENCE", "DIVERGENCE_OUTSIDE_CHECKSUM_SCOPE"):
        return EXIT_DIVERGENCE
    return EXIT_OK


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--client-trace", required=True)
    parser.add_argument("--server-trace", required=True)
    parser.add_argument("--layout", required=True)
    parser.add_argument("--first-bad-tick", type=float, default=None)
    parser.add_argument("--trace-class", default="simulation",
                        choices=["simulation", "model", "log", "telemetry", "native"],
                        help="provenance of the action traces (default: simulation)")
    parser.add_argument("--out")
    args = parser.parse_args()

    layout = parse_layout(read_json(args.layout), args.layout)
    client = parse_action_trace(args.client_trace)
    server = parse_action_trace(args.server_trace)
    require(client.samples, "client trace contains no samples")
    require(server.samples, "server trace contains no samples")

    payload = analyse(client, server, layout, args.first_bad_tick, args.trace_class)
    emit(payload, args.out)
    return exit_code_for(str(payload["verdict"]))


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except SyncValError as exc:
        print("error: %s" % exc, file=sys.stderr)
        raise SystemExit(EXIT_USAGE)
