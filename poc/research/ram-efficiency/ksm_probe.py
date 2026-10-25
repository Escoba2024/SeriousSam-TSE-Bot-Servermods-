#!/usr/bin/env python3
"""ksm_probe.py - read-only Kernel Samepage Merging (KSM) probe and savings
reporter for the Wine bot fleet investigation.

Why KSM matters here: eight independent Retail clients load the same
GRO/texture/world data into **private anonymous** memory, so the kernel
cannot share it via the page cache (unlike the wine/.so file pages, which
are shared automatically). KSM can deduplicate identical anonymous pages -
but only for processes that opted in:

* classic path: ``madvise(addr, len, MADV_MERGEABLE)`` - Wine does not call
  this, so it would require a preloader shim;
* kernel >= 6.4: ``prctl(PR_SET_MEMORY_MERGE, 1)`` is inherited by children,
  so a tiny launcher wrapper can enable it for a whole Wine process tree
  without touching any game or Wine binary.

This tool does **not** enable KSM and does not write to sysfs. It reports:

* whether the kernel exposes KSM and whether it is running;
* the kernel-documented savings figure: ``pages_sharing`` pages saved
  (Documentation/admin-guide/mm/ksm.rst: "pages_sharing ... how much saved");
* efficiency ratios so an operator can judge whether ksmd CPU cost is paying
  for itself (``pages_sharing / pages_shared`` and unshared volume).

All inputs can be redirected with ``--sysfs-root`` / ``--osrelease`` so unit
tests and sandboxes without KSM run against fixtures (output then carries
``"source": "fixture"``).
"""

from __future__ import annotations

import argparse
import json
import platform
from pathlib import Path

PAGE_SIZE = 4096
FIELDS = (
    "run",
    "pages_shared",
    "pages_sharing",
    "pages_unshared",
    "pages_volatile",
    "full_scans",
    "pages_to_scan",
    "sleep_millisecs",
)


def read_ksm(sysfs_root: Path) -> dict | None:
    ksm_dir = sysfs_root / "kernel" / "mm" / "ksm"
    if not ksm_dir.is_dir():
        return None
    out = {}
    for field in FIELDS:
        try:
            out[field] = int((ksm_dir / field).read_text().strip())
        except (OSError, ValueError):
            continue
    return out or None


def kernel_supports_process_merge(release: str) -> bool:
    """PR_SET_MEMORY_MERGE needs Linux >= 6.4."""
    try:
        major, minor = release.split(".")[:2]
        return (int(major), int(minor.split("-")[0])) >= (6, 4)
    except (ValueError, IndexError):
        return False


def report(sysfs_root: Path, release: str, source: str) -> dict:
    ksm = read_ksm(sysfs_root)
    result = {
        "source": source,
        "kernel_release": release,
        "prctl_memory_merge_supported": kernel_supports_process_merge(release),
        "ksm_available": ksm is not None,
    }
    if ksm is None:
        result["note"] = "no /sys/kernel/mm/ksm - kernel without KSM or sysfs hidden"
        return result
    result["ksm"] = ksm
    result["ksm_running"] = ksm.get("run", 0) == 1
    sharing = ksm.get("pages_sharing", 0)
    shared = ksm.get("pages_shared", 0)
    unshared = ksm.get("pages_unshared", 0)
    result["saved_mib"] = round(sharing * PAGE_SIZE / 1048576.0, 2)
    result["dedup_ratio"] = round(sharing / shared, 2) if shared else None
    result["unshared_mib_scanned"] = round(unshared * PAGE_SIZE / 1048576.0, 2)
    if not result["ksm_running"]:
        result["note"] = ("KSM present but not running; enabling it is an operator "
                          "decision - this probe never writes to sysfs")
    return result


def main(argv=None) -> int:
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    p.add_argument("--sysfs-root", default="/sys", help="sysfs root (fixture dir in tests)")
    p.add_argument("--osrelease", default=None, help="override kernel release string (tests)")
    args = p.parse_args(argv)
    source = "host" if args.sysfs_root == "/sys" and args.osrelease is None else "fixture"
    release = args.osrelease or platform.release()
    print(json.dumps(report(Path(args.sysfs_root), release, source), indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
