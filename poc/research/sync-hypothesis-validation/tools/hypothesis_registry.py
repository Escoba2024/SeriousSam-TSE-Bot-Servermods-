#!/usr/bin/env python3
"""Machine-readable hypothesis and assumption registry for the TSE 1.07 sync work.

Design rule: a hypothesis is only useful if it comes with

* a **claim** (what it asserts),
* a **prediction** (which observation must be true if the claim holds),
* a **falsifier** (which observation would kill it),
* the **required observations** (a missing measurement yields ``NOT_TESTED``
  instead of an opinion),
* a **minimum evidence class** (an offline model can never produce a
  ``NATIVE_SUPPORTED`` verdict).

Two lists exist on purpose:

``HYPOTHESES``
    Candidates for the *cause* of a sync divergence. These are evaluated by
    ``verdict_engine.py``.

``ASSUMPTIONS``
    Statements the toolchain relies on but cannot test itself (checksum scope,
    single-slot action storage, 20 Hz tick, unmodified vanilla components).
    They are validated for structure and printed in reports, but they are never
    "supported" by data - they are either verified statically elsewhere
    (``verified_by``) or they remain open. Evaluating them as hypotheses would
    fake a result.

Numbering note: PR #58 (``poc/research/sync-forensics``) uses P1-P6 / H1-H6.
``pr58_id`` records the mapping so the two reports never silently renumber
each other.

Exit codes
----------
0  registry valid
5  registry invalid (incomplete entry / unknown operator)
2  usage error
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import Dict, List

sys.path.insert(0, str(Path(__file__).resolve().parent))

from syncval_common import (  # noqa: E402
    EVIDENCE_CLASSES, EXIT_INVALID, EXIT_OK, EXIT_USAGE,
    SyncValError, base_payload, emit, require,
)

TOOL = "hypothesis_registry"

# Operators understood by verdict_engine._compare().
OPS = ("eq", "ne", "lt", "le", "gt", "ge", "is_true", "is_false",
       "is_null", "not_null", "in", "not_in")

HYPOTHESES: List[Dict[str, object]] = [
    {
        "id": "H1_ACTION_CADENCE",
        "pr58_id": "P3 / H3 (timing)",
        "priority": 1,
        "title": "20 Hz cadence and single-slot action loss",
        "claim": (
            "CPlayerSource::SetAction() keeps exactly one action (latest wins) and "
            "is called once per timer tick per local slot. If timer ticks, SetAction "
            "calls and network sends do not stay in a 1:1:1 relation, the server "
            "applies a different action sequence than the client intended, which "
            "changes the simulated player state."
        ),
        "prediction": (
            "A failing run shows telemetry windows where timer invocations/second "
            "deviate from 20, or SetAction calls per tick deviate from the number of "
            "local slots."
        ),
        "falsifier": (
            "Telemetry of the failing run is cadence-clean: tick ratio within "
            "0.8..1.2, action fidelity within 0.9..1.1 and zero divergence windows "
            "in every active window while SYNCBAD occurs."
        ),
        "required_observations": ["cadence.tick_rate_ratio", "cadence.action_fidelity",
                                  "cadence.divergence_windows"],
        "support_when": {
            "mode": "any",
            "rules": [
                {"obs": "cadence.divergence_windows", "op": "gt", "value": 0},
                {"obs": "cadence.tick_rate_ratio", "op": "lt", "value": 0.8},
                {"obs": "cadence.tick_rate_ratio", "op": "gt", "value": 1.2},
                {"obs": "cadence.action_fidelity", "op": "lt", "value": 0.9},
                {"obs": "cadence.action_fidelity", "op": "gt", "value": 1.1},
            ],
        },
        "refute_when": {
            "mode": "all",
            "rules": [
                {"obs": "cadence.tick_rate_ratio", "op": "ge", "value": 0.8},
                {"obs": "cadence.tick_rate_ratio", "op": "le", "value": 1.2},
                {"obs": "cadence.action_fidelity", "op": "ge", "value": 0.9},
                {"obs": "cadence.action_fidelity", "op": "le", "value": 1.1},
                {"obs": "cadence.divergence_windows", "op": "eq", "value": 0},
            ],
        },
        "min_evidence_class": "telemetry",
        "source_refs": [
            "docs/research/2026-10-21-independent-review-cpu-optimization.md#1.1",
            "poc/VERIFIKATION.md#3 (pa_llCreated, SetAction semantics)",
            "poc/release/gamemp/BotDriver.cpp:259 (BotDriver_HandleTimer)",
            "poc/release/gamemp/Game.cpp:754 (early-out before the vanilla input path)",
        ],
    },
    {
        "id": "H2_ACTION_COMPOSITION",
        "pr58_id": "P4 / H6 (ComposeActionPacket)",
        "priority": 1,
        "title": "Composed action bytes differ from a vanilla-equivalent action",
        "claim": (
            "The bot passes a normalised movement axis and a rotation of "
            "'target minus current accumulator' into ctl_ComposeActionPacket with a "
            "zeroed control buffer. If that composition yields different action bytes "
            "than a human input with the same intent, the client action checksum and "
            "the server replay disagree."
        ),
        "prediction": (
            "Aligned client/server action byte images differ inside the bytes covered "
            "by CPlayerAction::ChecksumForSync, and the first such tick is at or "
            "before the first reported SYNCBAD tick."
        ),
        "falsifier": (
            "No checksum-visible byte difference in any aligned action sample, or a "
            "visible difference that starts after the first logged SYNCBAD tick."
        ),
        "required_observations": ["coverage.verdict", "coverage.log_consistency"],
        "support_when": {
            "mode": "any",
            "rules": [
                {"obs": "coverage.verdict", "op": "eq",
                 "value": "CHECKSUM_VISIBLE_DIVERGENCE"},
            ],
        },
        "refute_when": {
            "mode": "any",
            "rules": [
                {"obs": "coverage.verdict", "op": "eq", "value": "NO_ACTION_DIVERGENCE"},
                {"obs": "coverage.log_consistency", "op": "eq",
                 "value": "INCONSISTENT_TOO_LATE"},
            ],
        },
        "min_evidence_class": "telemetry",
        "source_refs": [
            "poc/release/gamemp/BotDriver.cpp:459-478",
            "poc/release/gamemp/Game.cpp:430-452 (CControls::CreateAction)",
            "docs/research/2026-09-30-readiness-gamemp-crc-addendum.md (action semantics)",
            "docs/reports/2026-10-17-retail107-sync-check-investigation.md (4-byte checksum)",
        ],
    },
    {
        "id": "H3_FP_MODEL",
        "pr58_id": "new (not in PR #58)",
        "priority": 2,
        "title": "Floating-point model / build-flag divergence",
        "claim": (
            "Two builds of identical source can produce different binary32 state if "
            "compiled with different FP models (x87 extended intermediates, "
            "/fp:fast simplifications, different constant folding). The sync check "
            "compares raw floats, so a bit-level difference is enough for SYNCBAD."
        ),
        "prediction": (
            "The offline model shows an early divergent tick for at least one mode "
            "pair AND the recorded build provenance of the two code paths differs in "
            "compiler version or FP flags."
        ),
        "falsifier": (
            "Identical build provenance (compiler, FP flags, CRT) for the compared "
            "code paths, or a model that never diverges: then H3 cannot act here."
        ),
        "required_observations": ["fp.earliest_divergence_tick",
                                  "build.fp_provenance_match"],
        "support_when": {
            "mode": "all",
            "rules": [
                {"obs": "fp.earliest_divergence_tick", "op": "not_null"},
                {"obs": "build.fp_provenance_match", "op": "is_false"},
            ],
        },
        "refute_when": {
            "mode": "any",
            "rules": [
                {"obs": "build.fp_provenance_match", "op": "is_true"},
                {"obs": "fp.earliest_divergence_tick", "op": "is_null"},
            ],
        },
        "min_evidence_class": "telemetry",
        "source_refs": [
            "poc/research/sync-hypothesis-validation/tools/fp_determinism_probe.py",
            "docs/reports/2026-10-21-integrated-gamemp-build.json (build provenance example)",
            "poc/release/gamemp/BotDriver.cpp:459 (delta composition round-trip)",
        ],
    },
    {
        "id": "H4_CLIENT_SIM_MODIFICATION",
        "pr58_id": "P1 / H4 (ground lookahead)",
        "priority": 1,
        "title": "Client simulation modification (ground lookahead / renderer path)",
        "claim": (
            "A client-side gameplay change (ground lookahead, physics or trace "
            "changes, null-render early-out interacting with the timer) makes the "
            "client entity state differ from the vanilla server simulation even when "
            "every action byte is identical."
        ),
        "prediction": (
            "Entity-state fields differ in aligned dumps while the checksum-visible "
            "action bytes are identical, and the ground-lookahead candidate fails "
            "where the qualified candidate passes."
        ),
        "falsifier": (
            "Entity-state fields are identical in aligned dumps, or the failing "
            "candidate does not modify the client simulation path in that run."
        ),
        "required_observations": ["dumps.entity_state_divergence", "dumps.aligned_pairs"],
        "support_when": {
            "mode": "all",
            "rules": [
                {"obs": "dumps.entity_state_divergence", "op": "is_true"},
                {"obs": "dumps.aligned_pairs", "op": "gt", "value": 0},
            ],
        },
        "refute_when": {
            "mode": "all",
            "rules": [
                {"obs": "dumps.aligned_pairs", "op": "gt", "value": 0},
                {"obs": "dumps.entity_state_divergence", "op": "is_false"},
            ],
        },
        "min_evidence_class": "native",
        "source_refs": [
            "docs/reports/2026-10-12-shadow-development-status.md (ground-lookahead FAIL)",
            "docs/reports/2026-10-17-retail107-sync-check-investigation.md (B9)",
            "README.md (ground lookahead has no native acceptance)",
        ],
    },
    {
        "id": "H5_BINARY_INVENTORY",
        "pr58_id": "P5 / H5 (engine build differences)",
        "priority": 2,
        "title": "Client/server binary or network-build mismatch",
        "claim": (
            "A different SeriousSam.exe / Engine.dll / EntitiesMP.dll build or a "
            "different network build version between BotClient and server changes "
            "simulation or CRC coverage."
        ),
        "prediction": (
            "The four vanilla component hashes differ between client and server "
            "processes, or the major/minor network version differs."
        ),
        "falsifier": (
            "All four hashes and the network version are identical in every process "
            "of the run."
        ),
        "required_observations": ["build.hash_inventory_match"],
        "support_when": {
            "mode": "any",
            "rules": [{"obs": "build.hash_inventory_match", "op": "is_false"}],
        },
        "refute_when": {
            "mode": "any",
            "rules": [{"obs": "build.hash_inventory_match", "op": "is_true"}],
        },
        "min_evidence_class": "telemetry",
        "source_refs": [
            "docs/reports/2026-10-17-retail107-sync-check-investigation.md (B1, B17)",
            "AGENTS.md (1.10 is not 1.07)",
        ],
    },
    {
        "id": "H6_LOG_ARTIFACT",
        "pr58_id": "P6 / H2 (log interpretation)",
        "priority": 3,
        "title": "Counter artifact / incomplete log rather than real divergence",
        "claim": (
            "Some apparent sync failures are logging artifacts: missing SYNCOK lines, "
            "counter jumps greater than one, truncated logs, or a kick without "
            "preceding SYNCBAD events."
        ),
        "prediction": "Counter jumps, missing resets, or a kick without root events.",
        "falsifier": (
            "Monotone +1 counter per SYNCBAD with SYNCOK resets and a kick only after "
            "exactly the documented limit."
        ),
        "required_observations": ["log.counter_jumps", "log.disconnect_after_kick"],
        "support_when": {
            "mode": "any",
            "rules": [{"obs": "log.counter_jumps", "op": "gt", "value": 0}],
        },
        "refute_when": {
            "mode": "all",
            "rules": [
                {"obs": "log.counter_jumps", "op": "eq", "value": 0},
                {"obs": "log.disconnect_after_kick", "op": "is_true"},
            ],
        },
        "min_evidence_class": "log",
        "source_refs": [
            "poc/research/sync-forensics (PR #58: E1-E6 classifier)",
            "tools/analyze_sync_log.py",
            "docs/reports/2026-10-17-retail107-sync-check-investigation.md",
        ],
    },
    {
        "id": "H7_BOT_TICK_SEMANTICS",
        "pr58_id": "new (not in PR #58)",
        "priority": 2,
        "title": "bs_iTick counts timer invocations, not network ticks",
        "claim": (
            "BotDriver increments bs.bs_iTick once per timer invocation and resets it "
            "when the player source object changes; per-tick log lines are gated by "
            "bot_iLogEvery. A BotDriver tick value is therefore not a game tick, and "
            "a missing log line is not a missing action."
        ),
        "prediction": (
            "Timer invocations per second differ from 20, or the BotDriver tick scale "
            "disagrees with elapsed time or server ticks."
        ),
        "falsifier": (
            "Measured 20.0 timer invocations per second and exactly one SetAction per "
            "slot per invocation across the whole run."
        ),
        "required_observations": ["cadence.tick_rate_ratio", "cadence.action_fidelity",
                                  "cadence.divergence_windows"],
        "support_when": {
            "mode": "any",
            "rules": [
                {"obs": "cadence.tick_rate_ratio", "op": "lt", "value": 0.95},
                {"obs": "cadence.tick_rate_ratio", "op": "gt", "value": 1.05},
                {"obs": "cadence.divergence_windows", "op": "gt", "value": 0},
            ],
        },
        "refute_when": {
            "mode": "all",
            "rules": [
                {"obs": "cadence.tick_rate_ratio", "op": "ge", "value": 0.95},
                {"obs": "cadence.tick_rate_ratio", "op": "le", "value": 1.05},
                {"obs": "cadence.action_fidelity", "op": "ge", "value": 0.99},
                {"obs": "cadence.action_fidelity", "op": "le", "value": 1.01},
                {"obs": "cadence.divergence_windows", "op": "eq", "value": 0},
            ],
        },
        "min_evidence_class": "telemetry",
        "source_refs": [
            "poc/release/gamemp/BotDriver.cpp:259-330 (tick increment, reset, gating)",
            "poc/candidates/integrated-human-cpu-20261021/BotTelemetry.h (silence != health)",
            "docs/reports/2026-10-22-p0-bot-tick-diagnosis.md",
        ],
    },
]

ASSUMPTIONS: List[Dict[str, object]] = [
    {
        "id": "A1_CHECKSUM_SCOPE",
        "statement": (
            "The per-player action contribution to the sync checksum covers only the "
            "bytes read by CPlayerAction::ChecksumForSync (4 consecutive bytes per "
            "call, two calls per player). Differences outside that window cannot "
            "affect the action checksum."
        ),
        "status": "OPEN",
        "verified_by": [
            "static: docs/reports/2026-10-17-retail107-sync-check-investigation.md "
            "(PR #21 disassembly: 4 bytes per call)",
        ],
        "open_question": (
            "The byte offsets of the two calls inside the 1.07 CPlayerAction struct "
            "are not verified in this repository; they must come from the 1.07 SDK "
            "header."
        ),
        "tool": "checksum_coverage_probe.py",
    },
    {
        "id": "A2_SINGLE_SLOT_ACTION",
        "statement": (
            "CPlayerSource::SetAction() stores one action with a pa_llCreated stamp "
            "('latest wins'); a second call inside the same tick overwrites the first."
        ),
        "status": "OPEN",
        "verified_by": [
            "reference: poc/VERIFIKATION.md#3 (SE 1.10 PlayerSource.cpp:155-162)",
            "code review: poc/release/gamemp/BotDriver.cpp:23",
        ],
        "open_question": "Not binary-verified for 1.07.",
        "tool": "cadence_model.py (indirectly, via action fidelity)",
    },
    {
        "id": "A3_TICK_20HZ",
        "statement": "The game tick is 1/20 s and GameHandleTimer runs once per tick.",
        "status": "OPEN",
        "verified_by": [
            "reference: SE 1.10 Engine/Base/Timer.cpp:54",
            "docs/research/2026-10-21-independent-review-cpu-optimization.md#1.1",
        ],
        "open_question": (
            "WinMM timeSetEvent(50 ms) can coalesce under load; the measured rate is "
            "what counts, not the nominal one."
        ),
        "tool": "cadence_model.py",
    },
    {
        "id": "A4_VANILLA_COMPONENTS",
        "statement": (
            "Server, human clients and the four vanilla components are unmodified; "
            "only the BotClient GameMP.dll differs."
        ),
        "status": "OPEN",
        "verified_by": [
            "docs/reports/2026-10-12-source-verification.json",
            "poc/release/gamemp (13 captured GameMP changes)",
        ],
        "open_question": (
            "Per-process SHA256 inventory is required for every native run "
            "(requirement R1)."
        ),
        "tool": "evidence_bundle_audit.py",
    },
    {
        "id": "A5_KICK_LIMIT_UNTOUCHED",
        "statement": (
            "ser_iKickOnSyncBad stays at the documented retail default (10). Lowering "
            "or disabling it invalidates any 'no SYNCBAD' statement."
        ),
        "status": "ENFORCED",
        "verified_by": [
            "docs/reports/2026-10-17-retail107-sync-check-investigation.md (0x602A7EB4)",
            "AGENTS.md (do not lower it to manufacture stable runs)",
        ],
        "open_question": "None; enforced by the bundle audit.",
        "tool": "evidence_bundle_audit.py",
    },
]

REGISTRY_SCHEMA_NOTE = (
    "support_when/refute_when use mode 'any' (OR) or 'all' (AND). A hypothesis "
    "without both blocks is not testable and fails --check."
)


def by_id() -> Dict[str, Dict[str, object]]:
    return {str(entry["id"]): entry for entry in HYPOTHESES}


def validate() -> List[str]:
    problems: List[str] = []
    seen = set()
    for entry in HYPOTHESES:
        ident = entry.get("id")
        if not isinstance(ident, str) or not ident:
            problems.append("entry without id")
            continue
        if ident in seen:
            problems.append("duplicate id: %s" % ident)
        seen.add(ident)
        for key in ("title", "claim", "prediction", "falsifier", "pr58_id"):
            if not str(entry.get(key, "")).strip():
                problems.append("%s: missing %s" % (ident, key))
        if entry.get("priority") not in (1, 2, 3):
            problems.append("%s: priority must be 1, 2 or 3" % ident)
        if entry.get("min_evidence_class") not in EVIDENCE_CLASSES:
            problems.append("%s: invalid min_evidence_class" % ident)
        refs = entry.get("source_refs") or []
        if not isinstance(refs, list) or not refs:
            problems.append("%s: source_refs must be a non-empty list" % ident)
        required = entry.get("required_observations") or []
        if not isinstance(required, list) or not required:
            problems.append("%s: required_observations must be a non-empty list" % ident)
        for block_name in ("support_when", "refute_when"):
            block = entry.get(block_name)
            if not isinstance(block, dict):
                problems.append("%s: missing %s" % (ident, block_name))
                continue
            if block.get("mode") not in ("any", "all"):
                problems.append("%s: %s.mode must be 'any' or 'all'" % (ident, block_name))
            rules = block.get("rules")
            if not isinstance(rules, list) or not rules:
                problems.append("%s: %s.rules must be non-empty" % (ident, block_name))
                continue
            for rule in rules:
                if not isinstance(rule, dict):
                    problems.append("%s: rule must be an object" % ident)
                    continue
                if rule.get("op") not in OPS:
                    problems.append("%s: unknown op %r" % (ident, rule.get("op")))
                if not isinstance(rule.get("obs"), str):
                    problems.append("%s: rule without obs" % ident)
                elif rule["obs"] not in required:
                    problems.append("%s: rule obs %s not in required_observations"
                                    % (ident, rule["obs"]))
                if rule.get("op") not in ("is_true", "is_false", "is_null", "not_null") \
                        and "value" not in rule:
                    problems.append("%s: op %s needs a value" % (ident, rule.get("op")))

    assumption_ids = set()
    for entry in ASSUMPTIONS:
        ident = entry.get("id")
        if not isinstance(ident, str) or not ident.startswith("A"):
            problems.append("assumption without A-prefixed id")
            continue
        if ident in assumption_ids:
            problems.append("duplicate assumption id: %s" % ident)
        assumption_ids.add(ident)
        if ident in seen:
            problems.append("assumption id collides with hypothesis id: %s" % ident)
        for key in ("statement", "status", "verified_by", "open_question"):
            if not entry.get(key):
                problems.append("%s: missing %s" % (ident, key))
    return problems


def build_payload() -> Dict[str, object]:
    payload = base_payload(TOOL, "model")
    payload.update({
        "hypotheses": HYPOTHESES,
        "assumptions": ASSUMPTIONS,
        "operators": list(OPS),
        "note": REGISTRY_SCHEMA_NOTE,
        "ordering": "priority 1 = strongest prior / cheapest to falsify",
        "evaluated_by": "verdict_engine.py (hypotheses only; assumptions are never "
                        "data-supported)",
    })
    return payload


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--check", action="store_true", help="validate the registry")
    parser.add_argument("--ids", action="store_true", help="print only the ids")
    parser.add_argument("--out")
    args = parser.parse_args()

    problems = validate()
    if args.check and problems:
        print("registry invalid:", file=sys.stderr)
        for problem in problems:
            print("  - %s" % problem, file=sys.stderr)
        return EXIT_INVALID

    if args.ids:
        for entry in HYPOTHESES:
            print("%s\t%s" % (entry["id"], entry["title"]))
        for entry in ASSUMPTIONS:
            print("%s\t[assumption] %s" % (entry["id"], str(entry["statement"])[:70]))
        return EXIT_OK if not problems else EXIT_INVALID

    payload = build_payload()
    payload["validation"] = {"problems": problems, "valid": not problems}
    emit(payload, args.out)
    return EXIT_OK if not problems else EXIT_INVALID


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except SyncValError as exc:
        print("error: %s" % exc, file=sys.stderr)
        raise SystemExit(EXIT_USAGE)
