#!/usr/bin/env python3
"""Read-only CPU profiler for the TSE bot clients on Linux/Wine.

Subcommands
    sample    record /proc and cgroup counters for one or more PIDs
    analyze   per-role medians, thread split and a validity verdict
    compare   A/B comparison of >=3 repetitions per variant

Why a custom sampler
    The 2026-10-21 A/B ran both variants under a shared 45%-of-one-core cgroup
    cap and reported 35.56% CPU for both. That number was the cap, not the
    renderer. This tool records the evidence needed to reject such a window:
    cgroup throttle counters, per-thread CPU (llvmpipe vs main), host busy
    fraction and process liveness. `analyze` refuses to qualify a throttled or
    saturated run; `compare` refuses to qualify overlapping repetitions.

Exit codes
    sample : 0 ok, 2 usage, 6 a sampled process disappeared before the end
    analyze: 0 valid, 6 invalid, 2 usage
    compare: 0 QUALIFIED, 7 UNQUALIFIED, 2 usage

The sampler only reads procfs. It never signals, stops or reniches a process.
"""

from __future__ import annotations

import argparse
import json
import os
import statistics
import sys
import time
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, Iterable, List, Optional, Sequence, Tuple

CLK_TCK = os.sysconf("SC_CLK_TCK")
PAGE_SIZE = os.sysconf("SC_PAGE_SIZE")

EXIT_OK = 0
EXIT_USAGE = 2
EXIT_INVALID = 6
EXIT_UNQUALIFIED = 7


# --------------------------------------------------------------------------
# procfs primitives (pure functions where possible, so they are testable)
# --------------------------------------------------------------------------


def parse_proc_stat(text: str) -> Dict[str, int]:
    """Parse one /proc/<pid>/stat line. The comm field may contain spaces."""
    close = text.rindex(")")
    fields = text[close + 2:].split()
    # fields[0] is state (field 3 overall)
    return {
        "utime": int(fields[11]),
        "stime": int(fields[12]),
        "threads": int(fields[17]),
        "rss_pages": int(fields[21]),
    }


def parse_cpu_stat(text: str) -> Dict[str, int]:
    """Parse cgroup cpu.stat for v1 and v2 (throttled_time in ns on v1)."""
    result: Dict[str, int] = {}
    for line in text.splitlines():
        parts = line.split()
        if len(parts) != 2:
            continue
        try:
            result[parts[0]] = int(parts[1])
        except ValueError:
            continue
    if "throttled_time" in result:
        result["throttled_usec"] = result["throttled_time"] // 1000
    return result


def parse_cpu_max(text: str) -> Tuple[Optional[int], Optional[int]]:
    """Parse cgroup v2 `cpu.max` ('max 100000' or '45000 100000')."""
    parts = text.split()
    if not parts:
        return None, None
    quota = None if parts[0] == "max" else int(parts[0])
    period = int(parts[1]) if len(parts) > 1 else None
    return quota, period


def parse_host_stat(text: str) -> Tuple[int, int]:
    """Return (total, busy) jiffies from /proc/stat, excluding guest time."""
    for line in text.splitlines():
        if not line.startswith("cpu "):
            continue
        values = [int(value) for value in line.split()[1:]]
        while len(values) < 8:
            values.append(0)
        user, nice, system, idle, iowait, irq, softirq, steal = values[:8]
        busy = user + nice + system + irq + softirq + steal
        total = busy + idle + iowait
        return total, busy
    raise ValueError("no aggregate cpu line in /proc/stat")


def classify_thread(comm: str, tid: int, pid: int) -> str:
    if "llvmpipe" in comm:
        return "llvmpipe"
    if tid == pid:
        return "main"
    return "other"


# --------------------------------------------------------------------------
# live sampling
# --------------------------------------------------------------------------


def _read(path: str) -> Optional[str]:
    try:
        with open(path, "r", encoding="utf-8", errors="replace") as handle:
            return handle.read()
    except OSError:
        return None


def read_threads(pid: int) -> Dict[str, object]:
    """Per-thread CPU split into main / llvmpipe / other."""
    task_dir = "/proc/%d/task" % pid
    try:
        tids = os.listdir(task_dir)
    except OSError:
        return {"main": 0, "llvmpipe": 0, "other": 0, "threads_seen": 0, "llvmpipe_threads": 0}
    totals = {"main": 0, "llvmpipe": 0, "other": 0}
    seen = 0
    llvmpipe_threads = 0
    for tid_text in tids:
        try:
            tid = int(tid_text)
        except ValueError:
            continue
        stat = _read("%s/%s/stat" % (task_dir, tid_text))
        comm = _read("%s/%s/comm" % (task_dir, tid_text))
        if stat is None:
            continue
        try:
            parsed = parse_proc_stat(stat)
        except (ValueError, IndexError):
            continue
        name = (comm or "").strip()
        group = classify_thread(name, tid, pid)
        totals[group] += parsed["utime"] + parsed["stime"]
        seen += 1
        if group == "llvmpipe":
            llvmpipe_threads += 1
    return {
        "main": totals["main"],
        "llvmpipe": totals["llvmpipe"],
        "other": totals["other"],
        "threads_seen": seen,
        "llvmpipe_threads": llvmpipe_threads,
    }


def read_cgroup(pid: int) -> Optional[Dict[str, object]]:
    member = _read("/proc/%d/cgroup" % pid)
    if member is None:
        return None
    v2_path = None
    v1_path = None
    for line in member.splitlines():
        parts = line.split(":", 2)
        if len(parts) != 3:
            continue
        hierarchy, controllers, path = parts
        if hierarchy == "0" and controllers == "":
            v2_path = path
        elif "cpu" in controllers.split(","):
            v1_path = path
    bases = []
    if v2_path is not None:
        bases.append(("/sys/fs/cgroup", v2_path, "v2"))
    if v1_path is not None:
        bases.append(("/sys/fs/cgroup/cpu,cpuacct", v1_path, "v1"))
    for base, rel, version in bases:
        stat_text = _read(os.path.join(base, rel.lstrip("/"), "cpu.stat"))
        if stat_text is None:
            continue
        info: Dict[str, object] = {"path": os.path.join(base, rel.lstrip("/")), "version": version}
        info.update(parse_cpu_stat(stat_text))
        max_text = _read(os.path.join(base, rel.lstrip("/"), "cpu.max"))
        if max_text is not None:
            quota, period = parse_cpu_max(max_text)
            info["quota_us"], info["period_us"] = quota, period
        else:
            quota_text = _read(os.path.join(base, rel.lstrip("/"), "cpu.cfs_quota_us"))
            period_text = _read(os.path.join(base, rel.lstrip("/"), "cpu.cfs_period_us"))
            info["quota_us"] = int(quota_text.strip()) if quota_text and quota_text.strip() != "-1" else None
            info["period_us"] = int(period_text.strip()) if period_text else None
        return info
    return None


def sample_pid(pid: int) -> Optional[Dict[str, object]]:
    stat = _read("/proc/%d/stat" % pid)
    if stat is None:
        return None
    try:
        parsed = parse_proc_stat(stat)
    except (ValueError, IndexError):
        return None
    threads = read_threads(pid)
    return {
        "utime": parsed["utime"],
        "stime": parsed["stime"],
        "threads": parsed["threads"],
        "rss_kb": parsed["rss_pages"] * PAGE_SIZE // 1024,
        "thread_cpu": {key: threads[key] for key in ("main", "llvmpipe", "other")},
        "threads_seen": threads["threads_seen"],
        "llvmpipe_threads": threads["llvmpipe_threads"],
        "cgroup": read_cgroup(pid),
        "alive": True,
    }


def host_sample(previous: Optional[Tuple[int, int]]) -> Tuple[Dict[str, object], Tuple[int, int]]:
    stat = _read("/proc/stat")
    load = _read("/proc/loadavg")
    result: Dict[str, object] = {}
    state = previous
    if stat is not None:
        total, busy = parse_host_stat(stat)
        state = (total, busy)
        if previous is not None:
            d_total = total - previous[0]
            d_busy = busy - previous[1]
            if d_total > 0:
                result["busy"] = d_busy / float(d_total)
    if load is not None:
        result["load1"] = float(load.split()[0])
    return result, state or (0, 0)


@dataclass
class PidSpec:
    pid: int
    role: str


def parse_pid_specs(values: Iterable[str]) -> List[PidSpec]:
    specs = []
    for value in values:
        pid_text, _, role = value.partition(":")
        specs.append(PidSpec(int(pid_text), role or "client"))
    if not specs:
        raise ValueError("at least one --pid is required")
    return specs


def cmd_sample(args: argparse.Namespace) -> int:
    specs = parse_pid_specs(args.pid)
    meta = {
        "type": "meta",
        "tool": "tse_cpu_profile/1",
        "started_utc": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "interval_s": args.interval,
        "duration_s": args.duration,
        "clk_tck": CLK_TCK,
        "nproc": os.cpu_count(),
        "label": args.label,
        "pids": [
            {
                "pid": spec.pid,
                "role": spec.role,
                "cmdline": (_read("/proc/%d/cmdline" % spec.pid) or "").replace("\x00", " ").strip(),
                "cgroup": (_read("/proc/%d/cgroup" % spec.pid) or "").strip(),
            }
            for spec in specs
        ],
    }
    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    start = time.monotonic()
    previous_host: Optional[Tuple[int, int]] = None
    missing_at_end: List[int] = []
    with out.open("w", encoding="utf-8") as handle:
        handle.write(json.dumps(meta, sort_keys=True) + "\n")
        while time.monotonic() - start < args.duration:
            tick = time.monotonic() - start
            host, previous_host = host_sample(previous_host)
            pids: Dict[str, object] = {}
            alive = 0
            for spec in specs:
                value = sample_pid(spec.pid)
                if value is None:
                    pids[str(spec.pid)] = {"alive": False}
                else:
                    pids[str(spec.pid)] = value
                    alive += 1
            handle.write(
                json.dumps({"type": "sample", "t": tick, "host": host, "pids": pids}, sort_keys=True)
                + "\n"
            )
            handle.flush()
            if alive == 0 and args.stop_when_exit:
                missing_at_end = [spec.pid for spec in specs]
                break
            elapsed = time.monotonic() - start - tick
            time.sleep(max(0.0, args.interval - elapsed))
    if missing_at_end:
        print("sampled processes exited during the window: %s" % missing_at_end, file=sys.stderr)
        return EXIT_INVALID
    return EXIT_OK


# --------------------------------------------------------------------------
# analysis
# --------------------------------------------------------------------------


def _stats(values: Sequence[float]) -> Dict[str, Optional[float]]:
    if not values:
        return {"median": None, "p95": None, "max": None, "min": None}
    ordered = sorted(values)
    index = min(len(ordered) - 1, int(round(0.95 * (len(ordered) - 1))))
    return {
        "median": statistics.median(ordered),
        "p95": ordered[index],
        "max": ordered[-1],
        "min": ordered[0],
    }


def load_recording(path: Path) -> Tuple[Dict[str, object], List[Dict[str, object]]]:
    meta = None
    samples = []
    with path.open("r", encoding="utf-8") as handle:
        for line in handle:
            line = line.strip()
            if not line:
                continue
            record = json.loads(line)
            if record.get("type") == "meta":
                meta = record
            elif record.get("type") == "sample":
                samples.append(record)
    if meta is None:
        raise ValueError("recording has no meta line: %s" % path)
    return meta, samples


def analyze_recording(
    meta: Dict[str, object],
    samples: List[Dict[str, object]],
    warmup_s: float = 0.0,
    allow_busy_host: bool = False,
    max_throttle_pct: float = 1.0,
    min_samples: int = 10,
) -> Dict[str, object]:
    reasons: List[str] = []
    t0 = samples[0]["t"] if samples else 0.0
    window = [sample for sample in samples if sample["t"] >= t0 + warmup_s]

    pids_meta = {str(item["pid"]): item for item in meta.get("pids", [])}
    roles = sorted({item["role"] for item in meta.get("pids", [])})

    result: Dict[str, object] = {
        "tool": meta.get("tool"),
        "label": meta.get("label"),
        "started_utc": meta.get("started_utc"),
        "nproc": meta.get("nproc"),
        "interval_s": meta.get("interval_s"),
        "warmup_s": warmup_s,
        "window_s": (window[-1]["t"] - window[0]["t"]) if len(window) > 1 else 0.0,
        "samples": len(window),
        "roles": {},
        "host": {},
        "checks": {},
        "reasons": reasons,
        "valid": False,
    }

    if len(window) < min_samples:
        reasons.append("only %d samples after warmup (need %d)" % (len(window), min_samples))
        result["checks"] = {"enough_samples": False}
        return result

    # Per-role delta accumulation.
    role_cpu: Dict[str, List[float]] = {role: [] for role in roles}
    role_threads: Dict[str, Dict[str, float]] = {
        role: {"main": 0.0, "llvmpipe": 0.0, "other": 0.0} for role in roles
    }
    role_rss: Dict[str, List[float]] = {role: [] for role in roles}
    role_throttle: Dict[str, Dict[str, float]] = {}
    max_proc_cpu = 0.0
    alive_end = True

    by_pid: Dict[str, List[Tuple[float, Dict[str, object]]]] = {}
    for sample in window:
        for pid_text, value in sample.get("pids", {}).items():
            if value.get("alive"):
                by_pid.setdefault(pid_text, []).append((sample["t"], value))
            elif sample is window[-1]:
                alive_end = False

    for pid_text, series in by_pid.items():
        role = pids_meta.get(pid_text, {}).get("role", "client")
        pairs = list(zip(series, series[1:]))
        total_delta = 0.0
        previous_threads = None
        for (t_a, a), (t_b, b) in pairs:
            dt = t_b - t_a
            if dt <= 0:
                continue
            ticks = (b["utime"] - a["utime"]) + (b["stime"] - a["stime"])
            cores = ticks / float(CLK_TCK) / dt
            total_delta += cores * dt
            role_cpu[role].append(cores)
            if previous_threads is None:
                previous_threads = a["thread_cpu"]
            for key in ("main", "llvmpipe", "other"):
                delta = b["thread_cpu"][key] - previous_threads[key]
                role_threads[role][key] += max(0, delta)
            previous_threads = b["thread_cpu"]
            role_rss[role].append(b["rss_kb"])
        if pairs and role_cpu[role]:
            average_cores = total_delta / max(1e-9, (pairs[-1][1][0] - pairs[0][0][0]))
            max_proc_cpu = max(max_proc_cpu, average_cores)

        cgroup_series = [value.get("cgroup") for _, value in series if value.get("cgroup")]
        if cgroup_series:
            first, last = cgroup_series[0], cgroup_series[-1]
            periods = int(last.get("nr_periods", 0)) - int(first.get("nr_periods", 0))
            throttled = int(last.get("nr_throttled", 0)) - int(first.get("nr_throttled", 0))
            throttled_us = int(last.get("throttled_usec", 0)) - int(first.get("throttled_usec", 0))
            wall_us = (series[-1][0] - series[0][0]) * 1e6
            quota = last.get("quota_us")
            period_us = last.get("period_us")
            role_throttle[role] = {
                "nr_periods": periods,
                "nr_throttled": throttled,
                "period_ratio": (throttled / float(periods)) if periods else 0.0,
                "time_ratio": (throttled_us / wall_us) if wall_us else 0.0,
                "quota_us": quota,
                "period_us": period_us,
                "quota_cores": (quota / float(period_us)) if quota and period_us else None,
            }

    host_busy = [sample["host"]["busy"] for sample in window if sample["host"].get("busy") is not None]
    host_load = [sample["host"]["load1"] for sample in window if sample["host"].get("load1") is not None]

    worst_period_ratio = 0.0
    worst_time_ratio = 0.0
    for role in roles:
        data = role_throttle.get(role, {})
        worst_period_ratio = max(worst_period_ratio, float(data.get("period_ratio", 0.0)))
        worst_time_ratio = max(worst_time_ratio, float(data.get("time_ratio", 0.0)))
        thread_total = sum(role_threads[role].values())
        shares = {
            key: (value / thread_total if thread_total else None)
            for key, value in role_threads[role].items()
        }
        result["roles"][role] = {
            "cpu_cores": _stats(role_cpu[role]),
            "threads": shares,
            "thread_ticks": role_threads[role],
            "rss_kb": _stats(role_rss[role]),
            "throttle": role_throttle.get(role),
            "pids": [int(pid) for pid, item in pids_meta.items() if item["role"] == role],
        }

    result["host"] = {
        "busy": _stats(host_busy),
        "load1": _stats(host_load),
    }

    nproc = float(meta.get("nproc") or os.cpu_count() or 1)
    checks = {
        "enough_samples": len(window) >= min_samples,
        "processes_alive": alive_end,
        "no_throttling": worst_period_ratio <= (max_throttle_pct / 100.0),
        "throttle_time_low": worst_time_ratio <= 0.02,
        "host_headroom": (not host_busy) or (statistics.median(host_busy) <= 0.90) or allow_busy_host,
        "not_machine_bound": max_proc_cpu <= 0.90 * nproc,
    }
    result["checks"] = checks
    result["max_process_cores"] = max_proc_cpu
    result["throttle"] = {"period_ratio": worst_period_ratio, "time_ratio": worst_time_ratio}

    if not checks["enough_samples"]:
        reasons.append("too few samples")
    if not checks["processes_alive"]:
        reasons.append("a sampled process disappeared during the window")
    if not checks["no_throttling"]:
        reasons.append(
            "cgroup throttled %.1f%% of periods (limit %.1f%%)"
            % (100.0 * worst_period_ratio, max_throttle_pct)
        )
    if not checks["throttle_time_low"]:
        reasons.append("cgroup throttled %.1f%% of wall time" % (100.0 * worst_time_ratio))
    if host_busy and statistics.median(host_busy) > 0.90 and not allow_busy_host:
        reasons.append("host CPU busy %.1f%% (limit 90%%)" % (100.0 * statistics.median(host_busy)))
    if not checks["not_machine_bound"]:
        reasons.append(
            "process used %.2f cores on %d CPUs (machine-bound)"
            % (max_proc_cpu, int(nproc))
        )

    result["valid"] = all(checks.values())
    return result


def cmd_analyze(args: argparse.Namespace) -> int:
    meta, samples = load_recording(Path(args.input))
    result = analyze_recording(
        meta,
        samples,
        warmup_s=args.warmup,
        allow_busy_host=args.allow_busy_host,
        max_throttle_pct=args.max_throttle_pct,
    )
    text = json.dumps(result, indent=2, sort_keys=True)
    if args.json:
        Path(args.json).write_text(text + "\n", encoding="utf-8")
    role = result["roles"].get(args.role)
    if role is None:
        print("no data for role %r" % args.role, file=sys.stderr)
        return EXIT_USAGE
    cpu = role["cpu_cores"]["median"]
    print(
        "%s: %.2f cores median (p95 %s) | llvmpipe %s | throttle %.2f%% | host busy %s"
        % (
            args.role,
            cpu or 0.0,
            ("%.2f" % role["cpu_cores"]["p95"]) if role["cpu_cores"]["p95"] is not None else "n/a",
            ("%.0f%%" % (100.0 * role["threads"]["llvmpipe"]))
            if role["threads"].get("llvmpipe") is not None
            else "n/a",
            100.0 * result["throttle"]["period_ratio"],
            ("%.0f%%" % (100.0 * result["host"]["busy"]["median"]))
            if result["host"]["busy"]["median"] is not None
            else "n/a",
        )
    )
    if not result["valid"]:
        for reason in result["reasons"]:
            print("INVALID: %s" % reason)
        return EXIT_INVALID
    return EXIT_OK


# --------------------------------------------------------------------------
# comparison
# --------------------------------------------------------------------------


def compare_runs(
    baselines: List[Dict[str, object]],
    candidates: List[Dict[str, object]],
    role: str = "client",
    min_saving_pct: float = 5.0,
    min_repeats: int = 3,
) -> Dict[str, object]:
    reasons: List[str] = []

    def values(runs: List[Dict[str, object]]) -> List[float]:
        out = []
        for run in runs:
            entry = (run.get("roles") or {}).get(role)
            if entry and entry["cpu_cores"]["median"] is not None:
                out.append(float(entry["cpu_cores"]["median"]))
        return out

    base = values(baselines)
    cand = values(candidates)

    if len(base) < min_repeats:
        reasons.append("only %d valid baseline repetitions (need %d)" % (len(base), min_repeats))
    if len(cand) < min_repeats:
        reasons.append("only %d valid candidate repetitions (need %d)" % (len(cand), min_repeats))
    for label, runs in (("baseline", baselines), ("candidate", candidates)):
        invalid = [run.get("label") or run.get("started_utc") for run in runs if not run.get("valid")]
        if invalid:
            reasons.append("%s run(s) invalid: %s" % (label, ", ".join(str(v) for v in invalid)))

    base_median = statistics.median(base) if base else None
    cand_median = statistics.median(cand) if cand else None
    saving = None
    separated = False
    if base and cand:
        saving = (base_median - cand_median) / base_median * 100.0 if base_median else None
        separated = max(cand) < min(base)

    qualified = (
        not reasons
        and saving is not None
        and saving >= min_saving_pct
        and separated
    )
    if saving is not None and saving < min_saving_pct:
        reasons.append("median saving %.1f%% below required %.1f%%" % (saving, min_saving_pct))
    if base and cand and not separated:
        reasons.append("repetitions overlap (max candidate %.2f >= min baseline %.2f cores)"
                       % (max(cand), min(base)))

    return {
        "role": role,
        "baseline_cores": base,
        "candidate_cores": cand,
        "baseline_median": base_median,
        "candidate_median": cand_median,
        "saving_pct": saving,
        "separated": separated,
        "min_saving_pct": min_saving_pct,
        "verdict": "QUALIFIED_MEASUREMENT" if qualified else "NOT_QUALIFIED",
        "reasons": reasons,
    }


def cmd_compare(args: argparse.Namespace) -> int:
    def load(paths: List[str]) -> List[Dict[str, object]]:
        return [json.loads(Path(path).read_text(encoding="utf-8")) for path in paths]

    result = compare_runs(
        load(args.baseline),
        load(args.candidate),
        role=args.role,
        min_saving_pct=args.min_saving_pct,
    )
    text = json.dumps(result, indent=2, sort_keys=True)
    if args.out:
        Path(args.out).write_text(text + "\n", encoding="utf-8")
    print(text)
    return EXIT_OK if result["verdict"] == "QUALIFIED_MEASUREMENT" else EXIT_UNQUALIFIED


# --------------------------------------------------------------------------
# CLI
# --------------------------------------------------------------------------


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    sub = parser.add_subparsers(dest="command", required=True)

    sample = sub.add_parser("sample", help="record procfs counters")
    sample.add_argument("--pid", action="append", required=True, metavar="PID[:ROLE]")
    sample.add_argument("--duration", type=float, required=True)
    sample.add_argument("--interval", type=float, default=0.5)
    sample.add_argument("--out", required=True)
    sample.add_argument("--label", default=None)
    sample.add_argument("--stop-when-exit", action="store_true")
    sample.set_defaults(func=cmd_sample)

    analyze = sub.add_parser("analyze", help="reduce a recording to a validity verdict")
    analyze.add_argument("--input", required=True)
    analyze.add_argument("--json", default=None)
    analyze.add_argument("--warmup", type=float, default=0.0)
    analyze.add_argument("--role", default="client")
    analyze.add_argument("--max-throttle-pct", type=float, default=1.0)
    analyze.add_argument("--allow-busy-host", action="store_true")
    analyze.set_defaults(func=cmd_analyze)

    compare = sub.add_parser("compare", help="A/B comparison of >=3 repetitions")
    compare.add_argument("--baseline", action="append", required=True)
    compare.add_argument("--candidate", action="append", required=True)
    compare.add_argument("--role", default="client")
    compare.add_argument("--min-saving-pct", type=float, default=5.0)
    compare.add_argument("--out", default=None)
    compare.set_defaults(func=cmd_compare)
    return parser


def main(argv: Optional[List[str]] = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        return int(args.func(args))
    except (OSError, ValueError) as exc:
        print("error: %s" % exc, file=sys.stderr)
        return EXIT_USAGE


if __name__ == "__main__":
    sys.exit(main())
