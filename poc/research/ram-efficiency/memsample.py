#!/usr/bin/env python3
"""memsample.py - RAM/CPU sampler for Wine bot-client fleets (offline-testable).

Captures, per sample interval and per process group:

* RSS, PSS, USS (``Private_Clean+Private_Dirty``), ``Shared_Clean+Shared_Dirty``
  and swap from ``/proc/<pid>/smaps_rollup`` (fallback: ``/proc/<pid>/status``
  VmRSS only, flagged ``pss_available=false``).
* CPU user/system jiffies from ``/proc/<pid>/stat`` (reported as deltas).
* Optional cgroup v2 readings: ``memory.current``, ``memory.peak``,
  ``memory.stat`` (selected keys) and ``cpu.stat`` for one cgroup directory.

Design rules
------------
* **Read-only.** The tool never writes outside the ``--out`` file and never
  signals, throttles or reconfigures any process.
* **Offline-testable.** ``--proc-root`` and the cgroup path are plain
  directories, so unit tests (and sandboxes without Wine) can point the tool
  at synthetic fixtures. A real run simply uses the default ``/proc``.
* **Provenance.** Every output line records the sampling mode, so later
  reports cannot silently mix fixture data with host data: samples taken with
  a non-default ``--proc-root`` are tagged ``"source": "fixture"``.

RSS vs PSS: RSS double-counts file-backed pages (wine libraries, llvmpipe)
that several clients map. PSS divides each shared page by the number of
mappers and is the only honest way to attribute memory per independent
client. USS is the amount that would actually be freed if the process exited.

Usage examples::

    # three known pids plus the private test cgroup, 5s interval, 120 samples
    python3 memsample.py --pid 123 --pid 456 --pid 789 \
        --cgroup /sys/fs/cgroup/tse-ram-bench --interval 5 --count 120 \
        --out samples.jsonl

    # match whole fleets by command line
    python3 memsample.py --match 'SeriousSam\.exe' --label client \
        --match 'DedicatedServer\.exe' --label server --count 1
"""

from __future__ import annotations

import argparse
import json
import re
import sys
import time
from pathlib import Path

PAGE_SIZE = 4096
SMAPS_KEYS = (
    "Rss",
    "Pss",
    "Private_Clean",
    "Private_Dirty",
    "Shared_Clean",
    "Shared_Dirty",
    "Swap",
    "SwapPss",
)
MEMORY_STAT_KEYS = ("anon", "file", "kernel", "slab", "shmem", "file_mapped")


def _read_kv_kib(path: Path, keys) -> dict:
    """Parse ``Key:   123 kB`` style files; returns KiB values."""
    out = {}
    try:
        text = path.read_text()
    except OSError:
        return out
    for line in text.splitlines():
        parts = line.split()
        if len(parts) >= 2 and parts[0].rstrip(":") in keys:
            try:
                out[parts[0].rstrip(":")] = int(parts[1])
            except ValueError:
                continue
    return out


def read_smaps_rollup(proc_root: Path, pid: int) -> dict:
    """Memory accounting for one pid, in KiB. Empty dict if unreadable."""
    rollup = proc_root / str(pid) / "smaps_rollup"
    data = _read_kv_kib(rollup, SMAPS_KEYS)
    if data:
        data["pss_available"] = True
        return data
    status = _read_kv_kib(proc_root / str(pid) / "status", ("VmRSS",))
    if status:
        return {"Rss": status.get("VmRSS", 0), "pss_available": False}
    return {}


def read_cpu_jiffies(proc_root: Path, pid: int):
    """(utime, stime) jiffies from /proc/<pid>/stat, or None."""
    try:
        text = (proc_root / str(pid) / "stat").read_text()
    except OSError:
        return None
    # comm may contain spaces/parentheses; split after the last ')'
    rpar = text.rfind(")")
    if rpar < 0:
        return None
    fields = text[rpar + 2 :].split()
    if len(fields) < 13:
        return None
    try:
        return int(fields[11]), int(fields[12])  # utime, stime
    except ValueError:
        return None


def read_cmdline(proc_root: Path, pid: int) -> str:
    try:
        raw = (proc_root / str(pid) / "cmdline").read_bytes()
    except OSError:
        return ""
    return raw.replace(b"\x00", b" ").decode("utf-8", "replace").strip()


def list_pids(proc_root: Path):
    try:
        entries = list(proc_root.iterdir())
    except OSError:
        return []
    return sorted(int(e.name) for e in entries if e.name.isdigit())


def match_pids(proc_root: Path, patterns):
    """patterns: list of (label, compiled_regex). Returns {label: [pids]}."""
    groups = {label: [] for label, _ in patterns}
    for pid in list_pids(proc_root):
        cmd = read_cmdline(proc_root, pid)
        if not cmd:
            continue
        for label, rx in patterns:
            if rx.search(cmd):
                groups[label].append(pid)
                break
    return groups


def read_cgroup(cgroup_dir: Path) -> dict:
    """memory.current/peak, selected memory.stat and cpu.stat keys (bytes/usec)."""
    out = {}
    for name in ("memory.current", "memory.peak"):
        try:
            out[name] = int((cgroup_dir / name).read_text().strip())
        except (OSError, ValueError):
            pass
    try:
        for line in (cgroup_dir / "memory.stat").read_text().splitlines():
            k, _, v = line.partition(" ")
            if k in MEMORY_STAT_KEYS:
                try:
                    out.setdefault("memory.stat", {})[k] = int(v)
                except ValueError:
                    pass
    except OSError:
        pass
    try:
        for line in (cgroup_dir / "cpu.stat").read_text().splitlines():
            k, _, v = line.partition(" ")
            if k in ("usage_usec", "user_usec", "system_usec", "nr_throttled", "throttled_usec"):
                try:
                    out.setdefault("cpu.stat", {})[k] = int(v)
                except ValueError:
                    pass
    except OSError:
        pass
    return out


def sample_group(proc_root: Path, label: str, pids, prev_cpu: dict) -> dict:
    """Aggregate one labelled pid group. Mutates prev_cpu for CPU deltas."""
    agg = {k: 0 for k in SMAPS_KEYS}
    cpu_delta = 0
    live = []
    pss_ok = True
    for pid in pids:
        mem = read_smaps_rollup(proc_root, pid)
        if not mem:
            continue  # process gone between discovery and read
        live.append(pid)
        pss_ok = pss_ok and bool(mem.get("pss_available"))
        for k in SMAPS_KEYS:
            agg[k] += mem.get(k, 0)
        cpu = read_cpu_jiffies(proc_root, pid)
        if cpu is not None:
            total = cpu[0] + cpu[1]
            prev = prev_cpu.get(pid)
            prev_cpu[pid] = total
            if prev is not None and total >= prev:
                cpu_delta += total - prev
    uss = agg["Private_Clean"] + agg["Private_Dirty"]
    return {
        "label": label,
        "pids": live,
        "process_count": len(live),
        "rss_kib": agg["Rss"],
        "pss_kib": agg["Pss"] if pss_ok else None,
        "uss_kib": uss if pss_ok else None,
        "shared_kib": (agg["Shared_Clean"] + agg["Shared_Dirty"]) if pss_ok else None,
        "swap_kib": agg["Swap"] if pss_ok else None,
        "pss_available": pss_ok,
        "cpu_jiffies_delta": cpu_delta,
    }


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    p.add_argument("--proc-root", default="/proc", help="proc filesystem root (fixture dir in tests)")
    p.add_argument("--pid", action="append", type=int, default=[], help="explicit pid (repeatable)")
    p.add_argument("--match", action="append", default=[], help="regex matched against /proc/<pid>/cmdline (repeatable)")
    p.add_argument("--label", action="append", default=[], help="label for the corresponding --match (repeatable)")
    p.add_argument("--cgroup", default=None, help="cgroup v2 directory to read memory.current/peak + stats from")
    p.add_argument("--interval", type=float, default=5.0, help="seconds between samples")
    p.add_argument("--count", type=int, default=1, help="number of samples (0 = forever)")
    p.add_argument("--out", default="-", help="output JSONL file, '-' for stdout")
    return p


def main(argv=None) -> int:
    args = build_parser().parse_args(argv)
    proc_root = Path(args.proc_root)
    source = "host" if args.proc_root == "/proc" else "fixture"

    patterns = []
    for i, pattern in enumerate(args.match):
        label = args.label[i] if i < len(args.label) else f"match{i}"
        patterns.append((label, re.compile(pattern)))

    out = sys.stdout if args.out == "-" else open(args.out, "w", encoding="utf-8")
    prev_cpu: dict = {}
    n = 0
    try:
        while True:
            groups = {}
            if args.pid:
                groups["pids"] = list(args.pid)
            for label, pids in match_pids(proc_root, patterns).items():
                groups.setdefault(label, []).extend(pids)
            record = {
                "ts": time.time(),
                "source": source,
                "groups": [sample_group(proc_root, label, pids, prev_cpu) for label, pids in groups.items()],
            }
            if args.cgroup:
                record["cgroup"] = read_cgroup(Path(args.cgroup))
            out.write(json.dumps(record, sort_keys=True) + "\n")
            out.flush()
            n += 1
            if args.count and n >= args.count:
                break
            time.sleep(args.interval)
    finally:
        if out is not sys.stdout:
            out.close()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
