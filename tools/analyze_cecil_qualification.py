#!/usr/bin/env python3
"""Offline Cecil monitor evidence, never a complete qualification verdict.

Read existing report.json/timeseries.jsonl only; do not query, launch or change
runtime processes. Thresholds come from qualification.md (2026-11-07).
Coordinates and raw event lines are deliberately excluded from the output.
"""
import argparse
from collections import defaultdict
import hashlib
import json
import math
from pathlib import Path
import re
import statistics

DURATION = {1: 3600, 4: 3600, 8: 7200}
COUNTERS = ("shots", "pickups", "deaths", "respawns")
EVENT = re.compile(r"\[(CecilGoal|CecilGoalEnd|CecilPickup)\]\s+(.*)")
FIELDS = re.compile(r"(\w+)=([^\s]+)")
MAX_OBSERVATION_GAP_S = 5


def number(value):
    result = float(value)
    if not math.isfinite(result):
        raise ValueError("non-finite telemetry")
    return result


def percentile(values):
    """Nearest-rank P95, stated explicitly for reproducible comparisons."""
    return sorted(values)[max(0, math.ceil(.95 * len(values)) - 1)]


def window_coverage(rows, elapsed):
    """Bound observation gaps, including both censored window boundaries."""
    result = dict(status="MISSING", max_allowed_gap_s=MAX_OBSERVATION_GAP_S)
    if rows:
        times = [number(row["elapsed_s"]) for row in rows]
        leading, trailing = times[0], elapsed - times[-1]
        gap = max((b - a for a, b in zip(times, times[1:])), default=0)
        covered = 0 <= leading <= MAX_OBSERVATION_GAP_S and 0 <= trailing <= MAX_OBSERVATION_GAP_S and gap <= MAX_OBSERVATION_GAP_S
        result.update(status="FULL_WINDOW_COVERED" if covered else "INCOMPLETE",
                      leading_gap_s=leading, trailing_gap_s=trailing, max_sample_gap_s=gap)
    return result


def score_trajectory(samples, bots):
    """Observed expected scores only; missing samples break change comparisons.

    OBSERVED means at least two complete observations, never a behavior gate.
    Between-sample changes, kill attribution and unobserved scores remain unknown.
    """
    result = {}
    for name in ("Dev-" + str(i) for i in range(1, bots + 1)):
        info = dict(status="OPEN", first=None, last=None, min=None, max=None,
                    change_count=0, positive_change_count=0, negative_change_count=0,
                    observed_samples=0, missing_samples=0)
        previous = None
        for sample in samples:
            scores = sample.get("scores", {})
            if not isinstance(scores, dict):
                raise ValueError("invalid score sample")
            if name not in scores:
                info["missing_samples"] += 1
                previous = None
                continue
            value = scores[name]
            if type(value) not in (int, float) or (isinstance(value, float) and not math.isfinite(value)):
                raise ValueError("invalid expected score")
            if info["observed_samples"] == 0:
                info.update(first=value, min=value, max=value)
            info.update(last=value, min=min(info["min"], value), max=max(info["max"], value))
            info["observed_samples"] += 1
            if previous is not None and value != previous:
                info["change_count"] += 1
                info["positive_change_count" if value > previous else "negative_change_count"] += 1
            previous = value
        if info["observed_samples"] >= 2 and info["missing_samples"] == 0:
            info["status"] = "OBSERVED"
        result[name] = info
    return result


def slot_summary(rows):
    first, last = rows[0], rows[-1]
    resets = [k for k in COUNTERS if any(b[k] < a[k] for a, b in zip(rows, rows[1:]))]
    result = {k + "_delta": None if k in resets else last[k] - first[k] for k in COUNTERS}
    result["fire_actions_delta"] = result.pop("shots_delta")
    result.update(samples=len(rows), counter_resets=resets,
                  max_sample_gap_s=max((b["elapsed_s"] - a["elapsed_s"] for a, b in zip(rows, rows[1:])), default=0),
                  current_weapons=sorted({r["current"] for r in rows if r["alive"]}),
                  wanted_weapons=sorted({r["wanted"] for r in rows if r["alive"]}),
                  owned_masks=sorted({r["owned"] for r in rows}),
                  max_rays=max(r["rays"] for r in rows),
                  inactive_graph_samples=sum(r["ready"] != 1 for r in rows),
                  ray_budget_breaches=sum(r["rays"] > 16 for r in rows),
                  max_stationary_s=0, max_unexplained_stationary_s=0,
                  max_stationary_window_s=None, max_unexplained_stationary_window_s=None,
                  observed_dead_intervals_s=[], respawn_activity_delays_s=[],
                  respawn_gate="NOT_PROVEN", weapon_transitions=[])
    anchor = first["pos"]
    still_since = quiet_since = first["elapsed_s"]
    dead_since = None
    pending_spawn = None
    prev = None
    moved_samples = 0
    for row in rows:
        t = row["elapsed_s"]
        if not row["alive"]:
            if dead_since is None:
                dead_since = t
            pending_spawn = None
            still_since = quiet_since = t
            anchor = row["pos"]
        else:
            spawned = prev is not None and (not prev["alive"] or row["respawns"] > prev["respawns"])
            if spawned:
                if dead_since is not None:
                    result["observed_dead_intervals_s"].append(t - dead_since)
                dead_since = None
                pending_spawn = (t, row["pos"])
                still_since = quiet_since = t
                anchor = row["pos"]
            combat = prev is not None and row["vis"] == 1 and row["shots"] > prev["shots"]
            moved = math.dist(anchor, row["pos"]) > .25
            if moved:
                moved_samples += 1
                anchor = row["pos"]
                still_since = quiet_since = t
            if combat:
                quiet_since = t
            if t - still_since > result["max_stationary_s"]:
                result["max_stationary_s"] = t - still_since
                result["max_stationary_window_s"] = [still_since, t]
            if t - quiet_since > result["max_unexplained_stationary_s"]:
                result["max_unexplained_stationary_s"] = t - quiet_since
                result["max_unexplained_stationary_window_s"] = [quiet_since, t]
            if pending_spawn and (combat or math.dist(pending_spawn[1], row["pos"]) > .25):
                result["respawn_activity_delays_s"].append(t - pending_spawn[0])
                pending_spawn = None
            if prev and row["current"] != prev["current"]:
                result["weapon_transitions"].append(dict(elapsed_s=t, current=row["current"],
                                                         wanted=row["wanted"], owned=row["owned"]))
        prev = row
    result.update(movement_observations=moved_samples,
                  stationary_review="REVIEW_REQUIRED" if result["max_unexplained_stationary_s"] > 10 else "NO_OBSERVED_BREACH",
                  final_alive=bool(last["alive"]), unresolved_respawn_activity=pending_spawn is not None,
                  open_dead_interval_s=None if dead_since is None else last["elapsed_s"] - dead_since,
                  timing_limit="Sampled intervals, not exact event timing; first sample is left-censored. Gaps and between-sample combat require review.")
    return result


def resources(samples, baseline):
    out = dict(processes={}, process_identity_changes=[], host_limit="NOT_PROVEN",
               percentile_method="nearest-rank P95", swap_gate="NOT_PROVEN", disk_gate="NOT_PROVEN",
               comparison_limit="Observed window only; equal scenarios and three 120s windows require separate review.")
    disk=[number(s["disk_free_bytes"]) for s in samples if "disk_free_bytes" in s]
    if disk and len(disk)==len(samples):
        out["disk_min_free_gib"]=min(disk)/2**30
        out["disk_gate"]="WITHIN_OBSERVED_LIMIT" if min(disk)>=8*2**30 else "EXCEEDS_LIMIT"
    memory=[s["memory"] for s in samples if "memory" in s]
    if memory and len(memory)==len(samples):
        totals=[number(m["swap_total_kib"]) for m in memory]
        used=[number(m["swap_used_kib"]) for m in memory]
        if any(u<0 or u>t for u,t in zip(used,totals)):raise ValueError("invalid swap sample")
        out["memory_min_available_mib"]=min(number(m["available_kib"]) for m in memory)/1024
        out["swap_peak_used_mib"]=max(used)/1024
        out["swap_net_used_mib"]=(used[-1]-used[0])/1024
        out["swap_gate"]="NOT_APPLICABLE_NO_SWAP" if max(totals)==0 else "REVIEW_REQUIRED"
    host = [number(s["host_percent"]) for s in samples if "host_percent" in s]
    if host:
        out["host_percent"] = dict(median=statistics.median(host), p95=percentile(host))
        out["host_limit"] = "WITHIN_OBSERVED_LIMIT" if percentile(host) < 85 else "EXCEEDS_LIMIT"
    for role in sorted({r for s in samples for r in s.get("processes", {})}):
        values = [(number(s["elapsed_s"]), s["processes"][role]) for s in samples if role in s.get("processes", {})]
        if len({v["start_ticks"] for _, v in values}) != 1:
            out["process_identity_changes"].append(role)
        cpu = [number(s["cpu_percent"][role]) for s in samples if role in s.get("cpu_percent", {})]
        info = dict(cpu_limit="NOT_PROVEN", rss_gate="NOT_PROVEN")
        if cpu:
            info["cpu_percent"] = dict(median=statistics.median(cpu), p95=percentile(cpu))
            ref = (baseline or {}).get("cpu_percent", {}).get(role)
            if role.startswith("bot") and role not in out["process_identity_changes"] and ref and ref["median"] > 0 and ref["p95"] > 0:
                info["cpu_baseline_ratios"] = {k: info["cpu_percent"][k] / number(ref[k]) for k in ("median", "p95")}
                info["cpu_limit"] = "WITHIN_OBSERVED_LIMIT" if max(info["cpu_baseline_ratios"].values()) <= 1.2 + 1e-12 else "EXCEEDS_LIMIT"
        if values:
            end = values[-1][0]
            warm = [(t, number(v["rss_kib"]) / 1024) for t, v in values if t >= 600]
            start = end - 3600
            window = []
            if warm and warm[0][0] <= start:
                before = max(i for i, value in enumerate(warm) if value[0] <= start)
                window = warm[before:]
                if window[0][0] < start and len(window) > 1:
                    t0, v0 = window[0]; t1, v1 = window[1]
                    window[0] = (start, v0 + (v1 - v0) * (start - t0) / (t1 - t0))
                    info["rss_boundary_interpolated"] = True
            if len(window) > 1 and window[-1][0] - window[0][0] >= 3600 and role not in out["process_identity_changes"]:
                xs = [t / 60 for t, _ in window]
                ys = [v for _, v in window]
                mx, my = statistics.mean(xs), statistics.mean(ys)
                slope = sum((x - mx) * (y - my) for x, y in zip(xs, ys)) / sum((x - mx) ** 2 for x in xs)
                net = ys[-1] - ys[0]
                info.update(rss_trend_mib_min=slope, rss_net_mib=net,
                            rss_gate="WITHIN_OBSERVED_LIMIT" if slope <= 1 and net <= 32 else "EXCEEDS_LIMIT")
            info["rss_last_mib"] = number(values[-1][1]["rss_kib"]) / 1024
        out["processes"][role] = info
    return out


def weapon_scenario(events, bots):
    goals = []
    active = {}
    for event in events:
        match = EVENT.search(event["line"])
        if not match:
            continue
        kind, fields = match[1], dict(FIELDS.findall(match[2]))
        slot = event["role"] + ":" + str(int(fields["local"]))
        if kind == "CecilGoal":
            previous = active.pop(slot, None)
            if previous and previous["outcome"] == "unresolved":
                previous["outcome"] = "superseded"
            if int(fields["kind"]) != 0:
                continue
            goal = dict(slot=slot, elapsed_s=event["elapsed_s"], tick=int(fields["tick"]),
                        entity=int(fields["entity"]), weapon=int(fields["weapon"]),
                        outcome="unresolved", compatible_inventory_gain=False, same_goal_pick_mask_and_gain=False,
                        source_pickability="planner selected after typed snapshot validation; not independently observed")
            # New optional instrumentation is acknowledged, never treated as proof blindly.
            goal["optional_evidence_fields"] = sorted(set(fields) - {"local", "tick", "entity", "kind", "weapon", "anchor"})
            goals.append(goal)
            active[slot] = goal
        elif kind == "CecilPickup" and slot in active:
            goal = active[slot]
            if goal["outcome"] == "unresolved" and 1 <= goal["weapon"] <= 30:
                gained = int(fields["owned"]) & ~int(fields["old"])
                if gained & (1 << (goal["weapon"] - 1)):
                    goal["compatible_inventory_gain"] = True
                    if int(fields.get("goal_entity", -1)) == goal["entity"] and int(fields.get("goal_picked", 0)) == 1:
                        goal["same_goal_pick_mask_and_gain"] = True
        elif kind == "CecilGoalEnd" and slot in active:
            goal = active[slot]
            if goal["entity"] == int(fields["entity"]) and goal["outcome"] == "unresolved":
                goal["outcome"] = fields["reason"]
    return dict(first_ten=goals[:10], observed_weapon_goals=len(goals), confirmed_reached=0,
                gate="NOT_PROVEN" if bots == 1 else "NOT_APPLICABLE_POPULATION",
                first_pickup_latency_gate="NOT_PROVEN",
                limitation="First ten observed selections are frozen, not replaced after failures. Observation must start before scenario selection. Existing pickup masks lack exact item identity; unavailable is not success. Picked masks are set only for weapons-stay items and before ReceiveItem; a matching mask plus gain is corroboration, not universal proof. Optional fields still require spatial and availability review.")


def analyze(records, report, baseline=None):
    if report["schema_version"] != 1 or report["bots"] not in DURATION:
        raise ValueError("unsupported monitor schema/population")
    if not re.fullmatch(r"[0-9a-f]{64}", report["dll_sha256"]):
        raise ValueError("invalid DLL identity")
    slots, samples, events = defaultdict(list), [], []
    for record in records:
        if set(record) == {"sample"}:
            row = record["sample"]
            t = number(row["elapsed_s"])
            if samples and t <= samples[-1]["elapsed_s"]:
                raise ValueError("nonmonotonic sample time")
            samples.append(row)
        elif set(record) == {"slot", "state"}:
            key, row = record["slot"], record["state"]
            t = number(row["elapsed_s"])
            if len(row["pos"]) != 3:
                raise ValueError("invalid position")
            for v in row["pos"]:
                number(v)
            for k in COUNTERS + ("tick", "alive", "ready", "vis", "owned", "current", "wanted", "rays"):
                if not isinstance(row[k], int):
                    raise ValueError("invalid state field " + k)
            if slots[key] and (t < slots[key][-1]["elapsed_s"] or row["tick"] <= slots[key][-1]["tick"]):
                raise ValueError("nonmonotonic bot telemetry")
            slots[key].append(row)
        elif set(record) == {"event"}:
            event = record["event"]
            number(event["elapsed_s"])
            events.append(event)
        else:
            raise ValueError("unknown telemetry record")
    bots = report["bots"]
    expected = {"botA:" + str(i) for i in range(min(bots, 4))}
    if bots == 8:
        expected.update("botB:" + str(i) for i in range(4))
    summaries = {slot: slot_summary(rows) for slot, rows in sorted(slots.items())}
    elapsed = number(report["elapsed_s"])
    sample_coverage = window_coverage(samples, elapsed)
    for slot, summary in summaries.items():
        summary["coverage"] = window_coverage(slots[slot], elapsed)
        if summary["coverage"]["status"] != "FULL_WINDOW_COVERED" and summary["stationary_review"] == "NO_OBSERVED_BREACH":
            summary["stationary_review"] = "NOT_PROVEN_INCOMPLETE_COVERAGE"
    complete_coverage = (set(slots) == expected and sample_coverage["status"] == "FULL_WINDOW_COVERED"
                         and all(s["coverage"]["status"] == "FULL_WINDOW_COVERED" for s in summaries.values()))
    # Older reports lack pinned endpoint identity: retain their observations,
    # but do not upgrade them to a controlled duration gate.
    identity = report.get("query_identity")
    scenario_integrity = "NOT_PROVEN"
    if isinstance(identity, dict) and isinstance(report.get("port"), int) and samples:
        identity_ok = (identity.get("gamename") == "serioussamse" and identity.get("gamever") == "1.07"
                       and identity.get("hostport") == str(report["port"]) and bool(identity.get("mapname")))
        scenario_integrity = ("WITHIN_OBSERVED_SCENARIO" if identity_ok and
                              all(s.get("players") == bots and s.get("map") == identity["mapname"] for s in samples)
                              else "FAILED")
    if elapsed < DURATION[bots]:
        duration_status = "NOT_MET"
    elif not complete_coverage:
        duration_status = "NOT_PROVEN_INCOMPLETE_COVERAGE"
    elif scenario_integrity != "WITHIN_OBSERVED_SCENARIO":
        duration_status = "NOT_PROVEN_SCENARIO_INTEGRITY"
    elif report["status"] != "DURATION_ACTIVITY_SYNC_PASS_BEHAVIOR_REVIEW_REQUIRED" or report.get("errors") != []:
        duration_status = "NOT_PROVEN_MONITOR_STATUS"
    else:
        duration_status = "DURATION_ONLY_MET"
    trajectories = score_trajectory(samples, bots)
    scores = {}
    if samples:
        first, last = samples[0].get("scores", {}), samples[-1].get("scores", {})
        # Only expected development identities; no unknown player names are published.
        scores = {name: last[name] - first[name] for name in ("Dev-" + str(i) for i in range(1, bots + 1))
                  if name in first and name in last}
    return dict(schema_version=1, qualified=False, dll_sha256=report["dll_sha256"],
                monitor_status=report["status"], monitor_gate_requested=bool(report["gate"]),
                monitor_error_count=len(report.get("errors", [])),
                duration_gate=dict(required_s=DURATION[bots], observed_s=elapsed,
                                   status=duration_status),
                telemetry_coverage=dict(status="FULL_WINDOW_COVERED" if complete_coverage else "INCOMPLETE",
                                        max_allowed_gap_s=MAX_OBSERVATION_GAP_S),
                sample_coverage=sample_coverage,
                scenario_integrity=scenario_integrity,
                missing_slots=sorted(expected - set(slots)), unexpected_slot_count=len(set(slots) - expected),
                slots=summaries, score_deltas=scores, score_trajectory=trajectories,
                observed_maps=sorted({s["map"] for s in samples if s.get("map")}),
                deaths_observed=sum(s["deaths_delta"] or 0 for s in summaries.values()),
                death_count_gate="COUNT_ONLY_MET" if sum(s["deaths_delta"] or 0 for s in summaries.values()) >= 100 else "NOT_MET",
                resources=resources(samples, baseline), weapon_scenario=weapon_scenario(events, bots),
                interpretation="Evidence only. Fire counters count actions, not hits. Sampled motion/visibility cannot prove continuous behavior. Missing identity, timing, pickup, map, retail-join and fleet gates remain unqualified.")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("evidence", type=Path, help="existing monitor output directory")
    parser.add_argument("--baseline", type=Path, help="clean baseline summary JSON")
    args = parser.parse_args()
    try:
        report_bytes = (args.evidence / "report.json").read_bytes()
        report = json.loads(report_bytes)
        baseline = json.loads(args.baseline.read_text()) if args.baseline else None
        series = args.evidence / "timeseries.jsonl"
        digest = hashlib.sha256()
        def records():
            with series.open("rb") as stream:
                for line in stream:
                    digest.update(line)
                    yield json.loads(line)
        result = analyze(records(), report, baseline)
        result["input_sha256"] = dict(report=hashlib.sha256(report_bytes).hexdigest(),
                                     timeseries=digest.hexdigest())
        print(json.dumps(result, ensure_ascii=False, indent=2, allow_nan=False))
    except (OSError, ValueError, KeyError, TypeError) as exc:
        parser.exit(2, "Evidence error: " + str(exc) + "\n")


if __name__ == "__main__":
    main()
