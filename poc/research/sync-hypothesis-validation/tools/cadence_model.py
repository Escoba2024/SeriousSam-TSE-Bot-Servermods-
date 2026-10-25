#!/usr/bin/env python3
"""20 Hz cadence / action-fidelity model over BotTelemetry.csv.

Hypothesis under test (H1, see hypothesis_registry.py)
-----------------------------------------------------
The engine calls the registered timer handlers once per tick, in registration
order: first ``CNetworkTimerHandler`` (``_pNetwork->TimerLoop()``, which sends
the *previous* tick's actions) and then ``CGameTimerHandler``
(``CGame::GameHandleTimer`` -> ``BotDriver_HandleTimer``), which composes one
``CPlayerAction`` per local slot and hands it to
``CPlayerSource::SetAction()``.

``SetAction`` is a single-slot "latest wins" store: it keeps exactly one action
and stamps ``pa_llCreated``. Therefore the *only* cadence that reproduces
vanilla human input is

    one timer tick  ->  one action per local slot  ->  one network send

Any deviation has a mechanically different consequence:

* timer ticks slower than the network sends (starvation, lock hold, stall)
  -> the same action is sent again: the server applies a repeated action and
     the bot's intent is quantised into fewer simulation steps;
* more ``SetAction`` calls than timer ticks (double-invocation, re-entrancy)
  -> intermediate actions are silently dropped by the single slot;
* actions per tick != number of local slots
  -> a slot is starved while the others move, or extra actions appear.

This tool measures exactly those three quantities from the published
BotTelemetry.csv layout and reports **cadence divergence windows**. It does not
read server logs and it does not align telemetry time to game ticks: the
current telemetry has no shared monotonic clock with the server, which is an
explicit instrumentation requirement (docs/research/sync-hypothesis-validation/
2026-10-25-instrumentation-requirements.md, requirement R6).

Exit codes
----------
0  CADENCE_OK
3  CADENCE_DIVERGENCE (at least one non-OK active window)
4  CADENCE_UNMEASURABLE (no usable data rows - silence is not health)
2  usage / parse error
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import Dict, List, Optional

sys.path.insert(0, str(Path(__file__).resolve().parent))

from syncval_common import (  # noqa: E402
    EXIT_DIVERGENCE, EXIT_INCOMPLETE, EXIT_OK, EXIT_USAGE,
    SyncValError, base_payload, emit, observation, parse_bot_telemetry, require,
)

TOOL = "cadence_model"

STARVE_RATIO = 0.8
FAST_RATIO = 1.2
ACTION_LOW = 0.9
ACTION_HIGH = 1.1
MIN_WINDOW_MS = 50.0
MAX_WINDOW_MS = 5000.0


def _active(row: Dict[str, str], tel) -> bool:
    return (tel.numeric(row, "gameon") > 0) and (tel.numeric(row, "enabled") > 0)


def analyse(tel, expected_hz: float = 20.0,
            source_class: str = "simulation") -> Dict[str, object]:
    payload = base_payload(TOOL, source_class)
    if not tel.rows:
        payload.update({
            "verdict": "CADENCE_UNMEASURABLE",
            "verdict_detail": (
                "No usable telemetry rows. A missing CSV is not evidence that the "
                "driver was healthy: on this build silence only means no log line "
                "(BotTelemetry.h documents that pitfall)."
            ),
            "rows": 0,
            "windows": [],
            "parse_errors": tel.errors[:20],
        })
        return payload

    windows: List[Dict[str, object]] = []
    skipped = 0
    for prev, cur in zip(tel.rows, tel.rows[1:]):
        t0 = tel.numeric(prev, "t_ms")
        t1 = tel.numeric(cur, "t_ms")
        dt_ms = t1 - t0
        if dt_ms < MIN_WINDOW_MS or dt_ms > MAX_WINDOW_MS:
            skipped += 1
            continue
        d_ticks = tel.numeric(cur, "ticks") - tel.numeric(prev, "ticks")
        d_actions = tel.numeric(cur, "actions") - tel.numeric(prev, "actions")
        lp_prev = tel.numeric(prev, "lp")
        lp_cur = tel.numeric(cur, "lp")
        active = _active(prev, tel) and _active(cur, tel)
        expected_ticks = expected_hz * dt_ms / 1000.0
        ratio_ticks = d_ticks / expected_ticks if expected_ticks > 0 else None

        flags: List[str] = []
        classname = "OK"
        if not active:
            classname = "INACTIVE"
        else:
            if lp_prev != lp_cur:
                flags.append("LOCAL_SLOT_COUNT_CHANGED")
            lp = int(lp_cur)
            expected_actions = d_ticks * lp
            ratio_actions: Optional[float] = None
            if expected_actions > 0:
                ratio_actions = d_actions / expected_actions
            if d_ticks <= 0:
                flags.append("TIMER_DEAD")
            elif ratio_ticks is not None and ratio_ticks < STARVE_RATIO:
                flags.append("TIMER_STARVED")
            elif ratio_ticks is not None and ratio_ticks > FAST_RATIO:
                flags.append("TIMER_FAST")
            if lp <= 0 and d_actions > 0:
                flags.append("ACTIONS_WITHOUT_LOCAL_SLOT")
            elif ratio_actions is not None and ratio_actions > ACTION_HIGH:
                flags.append("ACTION_COALESCED")
            elif ratio_actions is not None and ratio_actions < ACTION_LOW:
                flags.append("ACTION_GAP")
            if "LOCAL_SLOT_COUNT_CHANGED" in flags:
                flags.append("UNMEASURABLE_SLOT_COUNT")
            for candidate in ("TIMER_DEAD", "ACTIONS_WITHOUT_LOCAL_SLOT",
                              "ACTION_COALESCED", "ACTION_GAP", "TIMER_STARVED",
                              "TIMER_FAST"):
                if candidate in flags:
                    classname = candidate
                    break
        window = {
            "t_ms_start": t0,
            "t_ms_end": t1,
            "dt_ms": round(dt_ms, 3),
            "ticks": d_ticks,
            "actions": d_actions,
            "local_slots": lp_cur,
            "tick_ratio_vs_expected_hz": None if ratio_ticks is None else round(ratio_ticks, 6),
            "class": classname,
            "flags": flags,
        }
        windows.append(window)

    exposure = [w for w in windows if w["class"] not in ("OK", "INACTIVE")]
    active_windows = [w for w in windows if w["class"] != "INACTIVE"]
    ratios = [w["tick_ratio_vs_expected_hz"] for w in active_windows
              if w["tick_ratio_vs_expected_hz"] is not None]
    min_window_ratio = min(ratios) if ratios else None
    total_ticks = sum(float(w["ticks"]) for w in windows)
    total_actions = sum(float(w["actions"]) for w in windows)
    span_ms = (windows[-1]["t_ms_end"] - windows[0]["t_ms_start"]) if windows else 0.0
    overall_hz = (total_ticks / (span_ms / 1000.0)) if span_ms > 0 else None

    summary: Dict[str, object] = {
        "rows": len(tel.rows),
        "windows": len(windows),
        "skipped_windows": skipped,
        "inactive_windows": sum(1 for w in windows if w["class"] == "INACTIVE"),
        "divergence_windows": len(exposure),
        "divergence_ticks": sum(float(w["ticks"]) for w in exposure),
        "tick_rate_hz_measured": None if overall_hz is None else round(overall_hz, 3),
        "action_fidelity_overall": (
            round(total_actions / total_ticks, 6) if total_ticks > 0 else None
        ),
        "class_counts": _count(windows),
        "min_window_tick_ratio": None if min_window_ratio is None else round(min_window_ratio, 6),
        "parse_errors": tel.errors[:20],
    }

    if not windows:
        payload.update({
            "verdict": "CADENCE_UNMEASURABLE",
            "verdict_detail": "No window with a plausible sampling interval.",
            "summary": summary,
            "windows": [],
        })
        return payload

    payload.update({
        "expected_hz": expected_hz,
        "thresholds": {
            "tick_ratio_starved_below": STARVE_RATIO,
            "tick_ratio_fast_above": FAST_RATIO,
            "action_ratio_below": ACTION_LOW,
            "action_ratio_above": ACTION_HIGH,
        },
        "summary": summary,
        "windows": windows[:2000],
        "divergence_window_list": exposure[:200],
        "interpretation": (
            "Windows in telemetry time. There is no shared clock between this CSV "
            "and the server log in the current build, so temporal overlap with a "
            "SYNCBAD window must NOT be claimed; requirement R6 asks for a shared "
            "monotonic timestamp plus game tick in both artifacts."
        ),
    })
    payload["verdict"] = "CADENCE_DIVERGENCE" if exposure else "CADENCE_OK"
    source = Path(tel.path).name
    payload["observations"] = [
        observation("cadence.divergence_windows", len(exposure), source_class, source),
        observation("cadence.tick_rate_ratio",
                    summary["tick_rate_hz_measured"] / expected_hz
                    if summary["tick_rate_hz_measured"] is not None else None,
                    source_class, source),
        observation("cadence.action_fidelity",
                    summary["action_fidelity_overall"], source_class, source),
        observation("cadence.min_window_tick_ratio",
                    summary["min_window_tick_ratio"], source_class, source),
    ]
    return payload


def _count(windows: List[Dict[str, object]]) -> Dict[str, int]:
    counts: Dict[str, int] = {}
    for window in windows:
        key = str(window["class"])
        counts[key] = counts.get(key, 0) + 1
    return counts


def exit_code_for(verdict: str) -> int:
    if verdict == "CADENCE_UNMEASURABLE":
        return EXIT_INCOMPLETE
    if verdict == "CADENCE_DIVERGENCE":
        return EXIT_DIVERGENCE
    return EXIT_OK


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--telemetry", required=True, help="BotTelemetry.csv")
    parser.add_argument("--expected-hz", type=float, default=20.0)
    parser.add_argument("--source-class", default="simulation",
                        choices=["simulation", "model", "log", "telemetry", "native"],
                        help="provenance of the CSV; a real run must declare "
                             "'telemetry' explicitly (default: simulation)")
    parser.add_argument("--out")
    args = parser.parse_args()

    require(args.expected_hz > 0, "--expected-hz must be positive")
    tel = parse_bot_telemetry(args.telemetry)
    if tel.errors and not tel.rows:
        raise SyncValError("telemetry rejected: %s" % "; ".join(tel.errors[:3]))

    payload = analyse(tel, args.expected_hz, args.source_class)
    emit(payload, args.out)
    return exit_code_for(str(payload["verdict"]))


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except SyncValError as exc:
        print("error: %s" % exc, file=sys.stderr)
        raise SystemExit(EXIT_USAGE)
