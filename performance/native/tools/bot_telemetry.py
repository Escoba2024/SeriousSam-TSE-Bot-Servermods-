#!/usr/bin/env python3
"""Analyse the P0 evidence CSV written by the candidate GameMP build.

The candidate (poc/candidates/p0-nullrender-20261022) writes one data row per
second from a watchdog thread that never touches engine state:

    #bot-telemetry,rev=1
    #build,tag=p0-telemetry-20261022,built=...
    #exe,...
    #columns,t_ms,ticks,actions,frames,renderskip,renderdraw,lp,gameon,
             enabled,disabled,gameoff,nolocal,noentity,lock_ms_max,
             lock_ms_last,tick_ms_max,tick_ms_avg,cpu_user_ms,
             cpu_kernel_ms,stall_s,reason
    <rows>

This tool answers a narrow question: *did the bot driver actually produce
actions, and if not, why?* It deliberately does not claim anything about
gameplay quality, sync or CPU.

Exit codes
    0  ACTIVE_OK       ticks and actions at the expected rate
    2  usage/parse error
    3  INACTIVE        driver disabled / game off / no local players
    4  STALLED         timer stopped, or actions starved while ticks run
    5  NO_DATA         no usable data rows
"""

from __future__ import annotations

import argparse
import json
import statistics
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional

COLUMNS = [
    "t_ms",
    "ticks",
    "actions",
    "frames",
    "renderskip",
    "renderdraw",
    "lp",
    "gameon",
    "enabled",
    "disabled",
    "gameoff",
    "nolocal",
    "noentity",
    "lock_ms_max",
    "lock_ms_last",
    "tick_ms_max",
    "tick_ms_avg",
    "cpu_user_ms",
    "cpu_kernel_ms",
    "stall_s",
    "reason",
]

REASON_NAMES = {
    0: "ACTIVE",
    1: "DISABLED",
    2: "GAMEOFF",
    3: "NOLOCAL",
    4: "NOENTITY",
}

EXIT_ACTIVE = 0
EXIT_USAGE = 2
EXIT_INACTIVE = 3
EXIT_STALLED = 4
EXIT_NO_DATA = 5


class TelemetryError(ValueError):
    """Malformed telemetry file."""


@dataclass
class Sample:
    t_ms: int
    ticks: int
    actions: int
    frames: int
    renderskip: int
    renderdraw: int
    lp: int
    gameon: int
    enabled: int
    disabled: int
    gameoff: int
    nolocal: int
    noentity: int
    lock_ms_max: float
    lock_ms_last: float
    tick_ms_max: float
    tick_ms_avg: float
    cpu_user_ms: int
    cpu_kernel_ms: int
    stall_s: int
    reason: int


@dataclass
class Recording:
    build: Dict[str, str] = field(default_factory=dict)
    config: Dict[str, str] = field(default_factory=dict)
    notes: List[str] = field(default_factory=list)
    states: List[str] = field(default_factory=list)
    rows: List[Sample] = field(default_factory=list)


def _int(value: str, what: str) -> int:
    try:
        return int(float(value))
    except ValueError as exc:
        raise TelemetryError("invalid %s: %r" % (what, value)) from exc


def _float(value: str, what: str) -> float:
    try:
        return float(value)
    except ValueError as exc:
        raise TelemetryError("invalid %s: %r" % (what, value)) from exc


def _meta(payload: str) -> Dict[str, str]:
    result: Dict[str, str] = {}
    for item in payload.split(","):
        if "=" in item:
            key, value = item.split("=", 1)
            result[key.strip()] = value.strip()
    return result


def parse(text: str) -> Recording:
    """Parse a telemetry file. Raises TelemetryError on any schema drift."""
    recording = Recording()
    columns: Optional[List[str]] = None

    for lineno, raw in enumerate(text.splitlines(), 1):
        line = raw.strip()
        if not line:
            continue
        if line.startswith("#"):
            if line.startswith("#columns,"):
                columns = [name.strip() for name in line[len("#columns,"):].split(",")]
            elif line.startswith("#build,"):
                recording.build = _meta(line[len("#build,"):])
            elif line.startswith("#config,"):
                recording.config = _meta(line[len("#config,"):])
            elif line.startswith("#state,"):
                recording.states.append(line[len("#state,"):])
            elif line.startswith("#note,"):
                recording.notes.append(line[len("#note,"):])
            continue
        if columns is None:
            raise TelemetryError("data row before #columns header (line %d)" % lineno)
        if columns != COLUMNS:
            raise TelemetryError(
                "unsupported column layout at line %d: %s (expected %s)"
                % (lineno, ",".join(columns), ",".join(COLUMNS))
            )
        parts = line.split(",")
        if len(parts) != len(COLUMNS):
            raise TelemetryError(
                "line %d has %d fields, expected %d" % (lineno, len(parts), len(COLUMNS))
            )
        try:
            recording.rows.append(
                Sample(
                    t_ms=_int(parts[0], "t_ms"),
                    ticks=_int(parts[1], "ticks"),
                    actions=_int(parts[2], "actions"),
                    frames=_int(parts[3], "frames"),
                    renderskip=_int(parts[4], "renderskip"),
                    renderdraw=_int(parts[5], "renderdraw"),
                    lp=_int(parts[6], "lp"),
                    gameon=_int(parts[7], "gameon"),
                    enabled=_int(parts[8], "enabled"),
                    disabled=_int(parts[9], "disabled"),
                    gameoff=_int(parts[10], "gameoff"),
                    nolocal=_int(parts[11], "nolocal"),
                    noentity=_int(parts[12], "noentity"),
                    lock_ms_max=_float(parts[13], "lock_ms_max"),
                    lock_ms_last=_float(parts[14], "lock_ms_last"),
                    tick_ms_max=_float(parts[15], "tick_ms_max"),
                    tick_ms_avg=_float(parts[16], "tick_ms_avg"),
                    cpu_user_ms=_int(parts[17], "cpu_user_ms"),
                    cpu_kernel_ms=_int(parts[18], "cpu_kernel_ms"),
                    stall_s=_int(parts[19], "stall_s"),
                    reason=_int(parts[20], "reason"),
                )
            )
        except IndexError as exc:  # pragma: no cover - guarded by field count
            raise TelemetryError("truncated row at line %d" % lineno) from exc

    if columns is None:
        raise TelemetryError("missing #columns header")
    return recording


def _median(values: List[float]) -> Optional[float]:
    return statistics.median(values) if values else None


def analyze(
    recording: Recording,
    warmup_s: float = 0.0,
    duration_s: Optional[float] = None,
    min_tick_hz: float = 18.0,
    min_action_ratio: float = 0.9,
    expect_bots: Optional[int] = None,
    expect_nullrender: Optional[int] = None,
) -> Dict[str, object]:
    rows = list(recording.rows)
    if rows and warmup_s > 0:
        cutoff = rows[0].t_ms + int(warmup_s * 1000)
        rows = [row for row in rows if row.t_ms >= cutoff]
    if rows and duration_s is not None:
        end = rows[0].t_ms + int(duration_s * 1000)
        rows = [row for row in rows if row.t_ms <= end]

    config = recording.config or {}
    enabled_cfg = config.get("bot_enabled")
    disabled_cfg = enabled_cfg is not None and enabled_cfg not in ("1", "true", "TRUE")

    result: Dict[str, object] = {
        "samples": len(rows),
        "warmup_s": warmup_s,
        "build": recording.build,
        "config": recording.config,
        "states": recording.states,
        "notes": recording.notes,
        "reasons": {},
        "warnings": [],
    }

    if not rows:
        result.update(verdict="NO_DATA", exit_code=EXIT_NO_DATA)
        return result

    ticks = [row.ticks for row in rows]
    actions = [row.actions for row in rows]
    frames = [row.frames for row in rows]
    skipped = [row.renderskip for row in rows]
    drawn = [row.renderdraw for row in rows]
    lp_values = [row.lp for row in rows]
    stalls = [row.stall_s for row in rows]

    total_ticks = sum(ticks)
    total_actions = sum(actions)
    total_expected = sum(row.ticks * row.lp for row in rows)
    action_ratio = (total_actions / float(total_expected)) if total_expected else None

    tick_hz = [row.ticks for row in rows]
    bot_lp = _median([row.lp for row in rows]) or 0
    actions_per_s = _median(actions)
    actions_per_bot_s = (actions_per_s / bot_lp) if bot_lp else None

    reasons: Dict[str, int] = {}
    for row in rows:
        name = REASON_NAMES.get(row.reason, "UNKNOWN_%d" % row.reason)
        reasons[name] = reasons.get(name, 0) + 1

    result.update(
        tick_hz_median=_median(tick_hz),
        tick_hz_min=min(tick_hz),
        action_total=total_actions,
        actions_per_s_median=actions_per_s,
        actions_per_bot_s=actions_per_bot_s,
        action_ratio=action_ratio,
        lp_median=bot_lp,
        frames_per_s_median=_median(frames),
        render_skip_total=sum(skipped),
        render_draw_total=sum(drawn),
        lock_ms_max=max(row.lock_ms_max for row in rows),
        lock_ms_last_last=rows[-1].lock_ms_last,
        tick_ms_max=max(row.tick_ms_max for row in rows),
        stall_max=max(stalls),
        stall_rows=sum(1 for value in stalls if value > 0),
        cpu_user_ms_total=sum(row.cpu_user_ms for row in rows),
        cpu_kernel_ms_total=sum(row.cpu_kernel_ms for row in rows),
        reasons=reasons,
    )

    disabled_share = sum(row.disabled for row in rows) / float(total_ticks or 1)
    gameoff_share = sum(row.gameoff for row in rows) / float(total_ticks or 1)
    nolocal_share = sum(row.nolocal for row in rows) / float(total_ticks or 1)

    warnings: List[str] = result["warnings"]  # type: ignore[assignment]
    if expect_bots is not None and bot_lp != expect_bots:
        warnings.append("local players median %s != expected %s" % (bot_lp, expect_bots))
    if expect_nullrender is not None:
        nullrender_cfg = config.get("nullrender")
        if nullrender_cfg is not None and _int(nullrender_cfg, "nullrender") != expect_nullrender:
            warnings.append(
                "config nullrender=%s != expected %s" % (nullrender_cfg, expect_nullrender)
            )
    if result["lock_ms_max"] and float(result["lock_ms_max"]) > 1000.0:
        warnings.append(
            "ga_csNetwork wait reached %.0f ms; check for a lock stall"
            % float(result["lock_ms_max"])
        )
    if result["tick_ms_max"] and float(result["tick_ms_max"]) > 200.0:
        warnings.append(
            "tick interval reached %.0f ms (quantum is 50 ms)" % float(result["tick_ms_max"])
        )
    if bot_lp == 0:
        warnings.append("no local player source in the whole window")
    if config.get("bot_enabled") == "0":
        warnings.append("bot_bEnabled=0 in the loaded build (driver never acts)")

    verdict = "ACTIVE_OK"
    exit_code = EXIT_ACTIVE

    if disabled_cfg or disabled_share > 0.5:
        verdict, exit_code = "INACTIVE", EXIT_INACTIVE
        warnings.append("driver disabled for %.0f%% of ticks" % (100.0 * disabled_share))
    elif gameoff_share > 0.5:
        verdict, exit_code = "INACTIVE", EXIT_INACTIVE
        warnings.append("game off for %.0f%% of ticks (menu/loading?)" % (100.0 * gameoff_share))
    elif nolocal_share > 0.5 or bot_lp == 0:
        verdict, exit_code = "INACTIVE", EXIT_INACTIVE
    elif reasons.get("NOENTITY", 0) > 0.5 * len(rows):
        verdict, exit_code = "INACTIVE", EXIT_INACTIVE
        warnings.append(
            "local player sources exist but no player entity was available"
            " (join/loading window?)"
        )
    elif max(stalls) >= 2:
        verdict, exit_code = "STALLED", EXIT_STALLED
        warnings.append("timer stall lasted %d s (heartbeat present, no ticks)" % max(stalls))
    elif (_median(ticks) or 0) < min_tick_hz:
        verdict, exit_code = "STALLED", EXIT_STALLED
        warnings.append(
            "median %.1f timer ticks/s below %.1f/s" % (_median(ticks) or 0, min_tick_hz)
        )
    elif action_ratio is None or action_ratio < min_action_ratio:
        verdict, exit_code = "ACTION_STARVED", EXIT_STALLED
        warnings.append(
            "only %.0f%% of the expected actions reached SetAction()"
            % (100.0 * (action_ratio or 0.0))
        )

    result.update(verdict=verdict, exit_code=exit_code)
    return result


def summarize(result: Dict[str, object]) -> str:
    if result.get("verdict") == "NO_DATA":
        return "NO_DATA: no usable telemetry rows"

    lines = [
        "verdict: %s" % result["verdict"],
        "samples: %d" % result["samples"],
        "timer ticks/s: median %.1f, min %s"
        % (float(result["tick_hz_median"] or 0), result.get("tick_hz_min")),
        "actions/s: median %.1f, per bot %s"
        % (
            float(result["actions_per_s_median"] or 0),
            ("%.1f" % result["actions_per_bot_s"]) if result.get("actions_per_bot_s") else "n/a",
        ),
        "action/expected ratio: %s"
        % ("%.2f" % result["action_ratio"] if result.get("action_ratio") is not None else "n/a"),
        "local players: median %s" % result.get("lp_median"),
        "frames/s: %s" % result.get("frames_per_s_median"),
        "render skip/draw: %s/%s"
        % (result.get("render_skip_total"), result.get("render_draw_total")),
        "ga_csNetwork wait: max %.1f ms, last %.1f ms"
        % (float(result["lock_ms_max"] or 0), float(result["lock_ms_last_last"] or 0)),
        "tick interval: max %.1f ms" % float(result["tick_ms_max"] or 0),
        "cpu (in-process): user %s ms, kernel %s ms"
        % (result.get("cpu_user_ms_total"), result.get("cpu_kernel_ms_total")),
        "reasons: %s" % (result.get("reasons") or {}),
    ]
    for warning in result.get("warnings") or []:
        lines.append("warning: %s" % warning)
    return "\n".join(lines)


def main(argv: Optional[List[str]] = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("csv", type=Path, help="BotTelemetry.csv from the candidate")
    parser.add_argument("--warmup", type=float, default=0.0, help="ignore the first N seconds")
    parser.add_argument("--duration", type=float, default=None, help="analyse at most N seconds")
    parser.add_argument("--expect-bots", type=int, default=None)
    parser.add_argument("--expect-nullrender", type=int, choices=[0, 1], default=None)
    parser.add_argument("--min-tick-hz", type=float, default=18.0)
    parser.add_argument("--min-action-ratio", type=float, default=0.9)
    parser.add_argument("--json", type=Path, default=None)
    args = parser.parse_args(argv)

    try:
        recording = parse(args.csv.read_text(encoding="utf-8", errors="replace"))
    except OSError as exc:
        print("error: %s" % exc, file=sys.stderr)
        return EXIT_USAGE
    except TelemetryError as exc:
        print("error: %s" % exc, file=sys.stderr)
        return EXIT_USAGE

    result = analyze(
        recording,
        warmup_s=args.warmup,
        duration_s=args.duration,
        min_tick_hz=args.min_tick_hz,
        min_action_ratio=args.min_action_ratio,
        expect_bots=args.expect_bots,
        expect_nullrender=args.expect_nullrender,
    )
    print(summarize(result))
    if args.json is not None:
        args.json.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return int(result["exit_code"])


if __name__ == "__main__":
    sys.exit(main())
