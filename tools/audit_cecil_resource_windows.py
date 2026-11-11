#!/usr/bin/env python3
"""Read-only CPU comparison of three fixed 120-second Cecil resource windows.

Example (redirect stdout to a private evidence file if desired)::

  python3 tools/audit_cecil_resource_windows.py --baseline baseline-clean.json \
    --candidate timeseries.jsonl --candidate-report report.json \
    --scenario-pins resource-pins.json

Baseline accepts samples[].cpu_s plus optional per-sample start_ticks/pids, or
samples[].processes. Candidate accepts qualify_cecil_live JSONL sample records.
CPU percentages are recomputed from cumulative counters; supplied cpu_percent
fields are ignored. Native 1s observations are aggregated to approximately 5s
before computing median and nearest-rank P95. No interpolation or extrapolation.

Pins JSON has baseline/candidate objects, each containing map, bots, settings,
seed, render, namespace and concurrent_load. Values describe matched conditions
(namespace means isolation/topology, not necessarily identical namespace IDs).
Additional supplied keys must match too. DLL hashes belong to input artifacts,
not to shared scenario pins: baseline and candidate binaries intentionally differ.
Pins are caller assertions, not independently authenticated runtime evidence.

Historical baselines lacking per-sample process-start identity retain descriptive
statistics, but cannot close the CPU audit. Missing/mismatched pins, coverage gaps
and identity changes leave OPEN. A supplied native report must include an observed
query_identity.mapname; null/missing identity also leaves OPEN. This tool never assesses RSS, gameplay, sync,
the full qualification, or controls any process. Valid audits exit 0 even if OPEN
or EXCEEDS_LIMIT; malformed inputs exit 2. Only stdout contains the audit output.
"""
import argparse
from bisect import bisect_left
import hashlib
import json
import math
from pathlib import Path
import statistics

PIN_KEYS = ("map", "bots", "settings", "seed", "render", "namespace", "concurrent_load")
WINDOW_SECONDS = 120
WINDOW_COUNT = 3
BIN_SECONDS = 5
BOUNDARY_TOLERANCE_S = 1.0
BASELINE_MAX_GAP_S = 6.0
CANDIDATE_MAX_GAP_S = 1.5
LIMIT_RATIO = 1.2


def number(value):
    if isinstance(value, bool):
        raise ValueError("boolean telemetry number")
    result = float(value)
    if not math.isfinite(result) or result < 0:
        raise ValueError("nonfinite or negative telemetry number")
    return result


def identity_number(value):
    if value is None:
        return None
    result = number(value)
    if result <= 0 or result != int(result):
        raise ValueError("invalid process identity")
    return int(result)


def normalize(document, metadata=None):
    """Copy CPU observations from either supported schema; never alter inputs."""
    metadata = metadata or {}
    if isinstance(document, dict):
        metadata = {**metadata, **document}
        raw_rows = document.get("samples", [])
    else:
        raw_rows = document
    rows = []
    for record in raw_rows:
        if "sample" in record:
            raw = record["sample"]
        elif "elapsed_s" in record and ("processes" in record or "cpu_s" in record):
            raw = record
        else:
            continue  # Native event/state records contain no CPU observation.
        t = number(raw["elapsed_s"])
        if rows and t <= rows[-1]["elapsed_s"]:
            raise ValueError("CPU observation times must increase strictly")
        processes = raw.get("processes")
        if processes is None:
            processes = {role: {"cpu_s": cpu,
                               "start_ticks": raw.get("start_ticks", {}).get(role)}
                         for role, cpu in raw.get("cpu_s", {}).items()}
        copied = {}
        for role, process in processes.items():
            cpu = number(process["cpu_s"])
            pid = process.get("pid", raw.get("pids", {}).get(role,
                              metadata.get("pids", {}).get(role)))
            declared_pid = identity_number(metadata.get("pids", {}).get(role))
            actual_pid = identity_number(pid)
            copied[role] = dict(cpu_s=cpu,
                                start_ticks=identity_number(process.get("start_ticks")),
                                pid=actual_pid,
                                declared_pid_mismatch=declared_pid is not None and actual_pid != declared_pid)
        rows.append(dict(elapsed_s=t, processes=copied,
                         map=raw.get("map"), players=raw.get("players")))
    if not rows:
        raise ValueError("no cumulative CPU observations")
    return rows


def describe(values):
    if not values:
        return dict(samples=0, median=None, p95=None)
    return dict(samples=len(values), median=statistics.median(values),
                p95=sorted(values)[math.ceil(.95 * len(values)) - 1])


def compare(baseline, candidate, complete, comparable):
    b, c = describe(baseline), describe(candidate)
    ratios = {}
    exceeds = False
    for statistic in ("median", "p95"):
        bv, cv = b[statistic], c[statistic]
        ratios[statistic + "_ratio"] = (cv / bv if bv and cv is not None
                                        else 1.0 if cv == bv == 0 else None)
        if bv is not None and cv is not None:
            exceeds |= cv > LIMIT_RATIO * bv + 1e-9
    status = ("OPEN" if not complete or not comparable or not baseline or not candidate
              else "EXCEEDS_LIMIT" if exceeds else "WITHIN_OBSERVED_LIMIT")
    return dict(baseline=b, candidate=c, status=status, **ratios)


def measure_window(rows, start, roles, max_gap):
    times = [r["elapsed_s"] for r in rows]
    indices = []
    for bin_number in range(WINDOW_SECONDS // BIN_SECONDS + 1):
        target = start + bin_number * BIN_SECONDS
        at = bisect_left(times, target)
        options = [i for i in (at - 1, at) if 0 <= i < len(rows)]
        nearest = min(options, key=lambda i: (abs(times[i] - target), times[i]))
        indices.append(nearest if abs(times[nearest] - target) <= BOUNDARY_TOLERANCE_S else None)
    values = {role: [] for role in roles}
    issues, intervals = [], []
    for bin_number, (left, right) in enumerate(zip(indices, indices[1:])):
        nominal = start + bin_number * BIN_SECONDS
        if left is None or right is None:
            issues.append(dict(bin_start_s=nominal, code="BOUNDARY_MISSING"))
            continue
        segment = rows[left:right + 1]
        dt = times[right] - times[left]
        intervals.append(dict(nominal_start_s=nominal, actual_start_s=times[left],
                              actual_end_s=times[right], duration_s=dt))
        common = []
        if not 4 <= dt <= 6:
            common.append("CADENCE_MISMATCH")
        if any(b["elapsed_s"] - a["elapsed_s"] > max_gap for a, b in zip(segment, segment[1:])):
            common.append("SAMPLE_GAP")
        for role in roles:
            errors = list(common)
            processes = [row["processes"].get(role) for row in segment]
            if any(p is None for p in processes):
                errors.append("ROLE_MISSING")
            else:
                if any(p["start_ticks"] is None for p in processes):
                    errors.append("IDENTITY_UNOBSERVED")
                starts = {p["start_ticks"] for p in processes if p["start_ticks"] is not None}
                pids = {p["pid"] for p in processes if p["pid"] is not None}
                if len(starts) > 1 or len(pids) > 1:
                    errors.append("IDENTITY_CHANGE")
                if any(p["declared_pid_mismatch"] for p in processes):
                    errors.append("DECLARED_PID_MISMATCH")
                if any(b["cpu_s"] < a["cpu_s"] for a, b in zip(processes, processes[1:])):
                    errors.append("COUNTER_RESET")
            # Legacy identity absence permits descriptive arithmetic, never PASS.
            if not set(errors) - {"IDENTITY_UNOBSERVED"}:
                values[role].append(100 * (processes[-1]["cpu_s"] - processes[0]["cpu_s"]) / dt)
            issues.extend(dict(bin_start_s=nominal, role=role, code=code) for code in errors)
    coverage = dict(status="COMPLETE" if not issues else "INCOMPLETE",
                    expected_intervals=24, measured_intervals=len(intervals),
                    max_raw_gap_s=max_gap, boundary_tolerance_s=BOUNDARY_TOLERANCE_S,
                    intervals=intervals, issues=issues)
    return values, coverage


def comparability(pins, baseline_rows, candidate_rows, baseline_start, candidate_start, report):
    reasons = []
    supplied = pins if isinstance(pins, dict) else {}
    b, c = supplied.get("baseline", {}), supplied.get("candidate", {})
    if not isinstance(b, dict) or not isinstance(c, dict):
        raise ValueError("scenario pins must contain baseline/candidate objects")
    json.dumps(supplied, allow_nan=False)
    for key in sorted(set(PIN_KEYS) | set(b) | set(c)):
        if key not in b or key not in c or b[key] is None or c[key] is None or b[key] == "" or c[key] == "":
            reasons.append("MISSING_PIN:" + key)
        elif b[key] != c[key]:
            reasons.append("MISMATCHED_PIN:" + key)
    for label, rows, start, expected in (("baseline", baseline_rows, baseline_start, b),
                                         ("candidate", candidate_rows, candidate_start, c)):
        # CPU arithmetic includes nearest observed boundaries, which may lie
        # just outside nominal time bounds. Their scenario must match as well.
        actual_start = min(rows, key=lambda r: (abs(r["elapsed_s"] - start), r["elapsed_s"]))["elapsed_s"]
        end = start + WINDOW_COUNT * WINDOW_SECONDS
        actual_end = min(rows, key=lambda r: (abs(r["elapsed_s"] - end), r["elapsed_s"]))["elapsed_s"]
        for row in rows:
            if not actual_start <= row["elapsed_s"] <= actual_end:
                continue
            if row["map"] is not None and row["map"] != expected.get("map"):
                reasons.append("OBSERVED_MAP_MISMATCH:" + label)
            if row["players"] is not None and row["players"] != expected.get("bots"):
                reasons.append("OBSERVED_POPULATION_MISMATCH:" + label)
    if report and "bots" in report and report["bots"] != c.get("bots"):
        reasons.append("REPORT_POPULATION_MISMATCH")
    query_identity = (report or {}).get("query_identity")
    reported_map = query_identity.get("mapname") if isinstance(query_identity, dict) else None
    if report is not None and not reported_map:
        reasons.append("REPORT_QUERY_IDENTITY_UNOBSERVED")
    if reported_map is not None and reported_map != c.get("map"):
        reasons.append("REPORT_MAP_MISMATCH")
    return dict(status="OPEN" if reasons else "PINNED_MATCH", reasons=sorted(set(reasons)),
                supplied=supplied,
                limitation="Caller-supplied pins; runtime configuration is not independently authenticated.")


def analyze(baseline_document, candidate_records, *, scenario_pins=None,
            candidate_report=None, baseline_start=0, candidate_start=600):
    baseline_start, candidate_start = number(baseline_start), number(candidate_start)
    baseline = normalize(baseline_document)
    candidate = normalize(candidate_records, candidate_report)
    context = comparability(scenario_pins, baseline, candidate, baseline_start,
                            candidate_start, candidate_report)
    roles = sorted({role for row in baseline + candidate for role in row["processes"]})
    if isinstance(scenario_pins, dict):
        bots = scenario_pins.get("baseline", {}).get("bots")
        if bots in (1, 4, 8):
            roles = sorted(set(roles) | {"server", "botA"} | ({"botB"} if bots == 8 else set()))
    comparable = context["status"] == "PINNED_MATCH"
    windows = []
    totals = {side: {role: [] for role in roles} for side in ("baseline", "candidate")}
    complete = True
    for index in range(WINDOW_COUNT):
        bstart = baseline_start + index * WINDOW_SECONDS
        cstart = candidate_start + index * WINDOW_SECONDS
        bv, bc = measure_window(baseline, bstart, roles, BASELINE_MAX_GAP_S)
        cv, cc = measure_window(candidate, cstart, roles, CANDIDATE_MAX_GAP_S)
        covered = bc["status"] == cc["status"] == "COMPLETE"
        complete &= covered
        comparisons = {}
        for role in roles:
            totals["baseline"][role].extend(bv[role]); totals["candidate"][role].extend(cv[role])
            comparisons[role] = compare(bv[role], cv[role], covered, comparable)
        bp = [v for role in roles for v in bv[role]]
        cp = [v for role in roles for v in cv[role]]
        windows.append(dict(index=index + 1, baseline_range_s=[bstart, bstart + WINDOW_SECONDS],
                            candidate_range_s=[cstart, cstart + WINDOW_SECONDS],
                            baseline_coverage=bc, candidate_coverage=cc, roles=comparisons,
                            pooled=compare(bp, cp, covered, comparable)))
    aggregate = {role: compare(totals["baseline"][role], totals["candidate"][role], complete, comparable)
                 for role in roles}
    pooled = compare([v for role in roles for v in totals["baseline"][role]],
                     [v for role in roles for v in totals["candidate"][role]], complete, comparable)
    results = [r["status"] for r in aggregate.values()] + [pooled["status"]]
    for window in windows:
        results.extend(r["status"] for r in window["roles"].values())
        results.append(window["pooled"]["status"])
    status = ("EXCEEDS_LIMIT" if "EXCEEDS_LIMIT" in results else
              "OPEN" if "OPEN" in results else "WITHIN_OBSERVED_LIMIT")
    return dict(schema_version=1, qualified=False, cpu_comparison=status,
                comparability=context, windows=windows, roles=aggregate, pooled=pooled,
                method=dict(window_count=3, window_seconds=120, bin_seconds=5,
                            percent="100 * delta cumulative process CPU seconds / actual elapsed seconds",
                            percentile="nearest-rank P95", limit_ratio=LIMIT_RATIO,
                            pooled="Unweighted distribution of process-bin CPU percentages across all roles; each role and window must also pass.",
                            interpolation=False),
                artifacts=dict(baseline_dll_hashes=baseline_document.get("dll_hashes", {})
                               if isinstance(baseline_document, dict) else {},
                               candidate_dll_sha256=(candidate_report or {}).get("dll_sha256")),
                limitation="CPU-window evidence only. RSS, host load, gameplay, sync, native gates and full qualification are not assessed.")


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--baseline", type=Path, required=True)
    parser.add_argument("--candidate", type=Path, required=True)
    parser.add_argument("--candidate-report", type=Path)
    parser.add_argument("--scenario-pins", type=Path)
    parser.add_argument("--baseline-start", type=float, default=0)
    parser.add_argument("--candidate-start", type=float, default=600)
    args = parser.parse_args()
    try:
        inputs, documents = {}, {}
        for key in ("baseline", "candidate", "candidate_report", "scenario_pins"):
            path = getattr(args, key)
            if path is None:
                continue
            raw = path.read_bytes()
            inputs[key] = dict(name=path.name, sha256=hashlib.sha256(raw).hexdigest(), bytes=len(raw))
            documents[key] = ([json.loads(line) for line in raw.decode("utf-8").splitlines() if line.strip()]
                              if key == "candidate" else json.loads(raw))
        result = analyze(documents["baseline"], documents["candidate"],
                         scenario_pins=documents.get("scenario_pins"),
                         candidate_report=documents.get("candidate_report"),
                         baseline_start=args.baseline_start, candidate_start=args.candidate_start)
        result["inputs"] = inputs
        print(json.dumps(result, indent=2, allow_nan=False))
    except (OSError, ValueError, TypeError, KeyError) as error:
        parser.error(str(error))


if __name__ == "__main__":
    main()
