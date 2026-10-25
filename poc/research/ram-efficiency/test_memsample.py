#!/usr/bin/env python3
"""Tests for memsample.py against a synthetic /proc fixture (no game, no Wine)."""

from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

import memsample  # noqa: E402


def make_proc(root: Path, pid: int, cmdline: str, rss_kib: int, pss_kib: int,
              private_kib: int, shared_kib: int, utime: int, stime: int):
    d = root / str(pid)
    d.mkdir(parents=True)
    (d / "cmdline").write_bytes(cmdline.replace(" ", "\x00").encode() + b"\x00")
    (d / "smaps_rollup").write_text(
        "00400000-7fff0000 ---p 00000000 00:00 0    [rollup]\n"
        f"Rss:     {rss_kib} kB\n"
        f"Pss:     {pss_kib} kB\n"
        f"Private_Clean:   0 kB\n"
        f"Private_Dirty:   {private_kib} kB\n"
        f"Shared_Clean:    {shared_kib} kB\n"
        f"Shared_Dirty:    0 kB\n"
        "Swap:    0 kB\n"
        "SwapPss: 0 kB\n"
    )
    comm = cmdline.split()[0].rsplit("/", 1)[-1][:15]
    prefix = f"{pid} ({comm}) S "
    rest = ["0"] * 49
    rest[10] = str(utime)   # field 14 overall -> index 11 after ')' split... see memsample
    rest[11] = str(stime)
    (d / "stat").write_text(prefix + " ".join(rest) + "\n")
    (d / "status").write_text(f"VmRSS:\t{rss_kib} kB\n")


def make_cgroup(root: Path, current: int, peak: int):
    root.mkdir(parents=True, exist_ok=True)
    (root / "memory.current").write_text(str(current))
    (root / "memory.peak").write_text(str(peak))
    (root / "memory.stat").write_text("anon 1048576\nfile 2097152\nslab 4096\n")
    (root / "cpu.stat").write_text(
        "usage_usec 123456\nuser_usec 100000\nsystem_usec 23456\n"
        "nr_throttled 0\nthrottled_usec 0\n")


class MemsampleTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.proc = Path(self.tmp.name) / "proc"
        make_proc(self.proc, 101, "wine SeriousSam.exe +connect 1.2.3.4",
                  rss_kib=188000, pss_kib=120000, private_kib=90000,
                  shared_kib=98000, utime=500, stime=100)
        make_proc(self.proc, 102, "wine SeriousSam.exe +connect 1.2.3.4",
                  rss_kib=188500, pss_kib=121000, private_kib=91000,
                  shared_kib=97500, utime=600, stime=120)
        make_proc(self.proc, 103, "wine DedicatedServer.exe BotTest",
                  rss_kib=51000, pss_kib=40000, private_kib=35000,
                  shared_kib=16000, utime=50, stime=20)
        self.cgroup = Path(self.tmp.name) / "cgroup"
        make_cgroup(self.cgroup, current=555 * 1024 * 1024, peak=1158 * 1024 * 1024)

    def tearDown(self):
        self.tmp.cleanup()

    def test_smaps_rollup_parsing(self):
        mem = memsample.read_smaps_rollup(self.proc, 101)
        self.assertTrue(mem["pss_available"])
        self.assertEqual(mem["Rss"], 188000)
        self.assertEqual(mem["Pss"], 120000)

    def test_status_fallback_without_rollup(self):
        (self.proc / "101" / "smaps_rollup").unlink()
        mem = memsample.read_smaps_rollup(self.proc, 101)
        self.assertFalse(mem["pss_available"])
        self.assertEqual(mem["Rss"], 188000)

    def test_cpu_jiffies(self):
        self.assertEqual(memsample.read_cpu_jiffies(self.proc, 101), (500, 100))

    def test_match_groups_clients_and_server(self):
        import re
        groups = memsample.match_pids(self.proc, [
            ("client", re.compile(r"SeriousSam\.exe")),
            ("server", re.compile(r"DedicatedServer\.exe")),
        ])
        self.assertEqual(groups["client"], [101, 102])
        self.assertEqual(groups["server"], [103])

    def test_group_aggregation_pss_vs_rss(self):
        prev = {}
        g = memsample.sample_group(self.proc, "client", [101, 102], prev)
        self.assertEqual(g["process_count"], 2)
        self.assertEqual(g["rss_kib"], 376500)
        self.assertEqual(g["pss_kib"], 241000)
        self.assertEqual(g["uss_kib"], 181000)
        # PSS must be below RSS when pages are shared
        self.assertLess(g["pss_kib"], g["rss_kib"])
        # first sample has no CPU delta basis
        self.assertEqual(g["cpu_jiffies_delta"], 0)
        # second sample sees deltas
        d = self.proc / "101" / "stat"
        text = d.read_text().split()
        text[13] = "700"  # utime 500 -> 700
        d.write_text(" ".join(text) + "\n")
        g2 = memsample.sample_group(self.proc, "client", [101, 102], prev)
        self.assertEqual(g2["cpu_jiffies_delta"], 200)

    def test_cgroup_reading(self):
        cg = memsample.read_cgroup(self.cgroup)
        self.assertEqual(cg["memory.current"], 555 * 1024 * 1024)
        self.assertEqual(cg["memory.peak"], 1158 * 1024 * 1024)
        self.assertEqual(cg["memory.stat"]["anon"], 1048576)
        self.assertEqual(cg["cpu.stat"]["nr_throttled"], 0)

    def test_cli_end_to_end_fixture_tagged(self):
        out = subprocess.run(
            [sys.executable, str(HERE / "memsample.py"),
             "--proc-root", str(self.proc), "--match", r"SeriousSam\.exe",
             "--label", "client", "--cgroup", str(self.cgroup), "--count", "1"],
            capture_output=True, text=True, check=True)
        record = json.loads(out.stdout.strip())
        self.assertEqual(record["source"], "fixture")
        labels = {g["label"]: g for g in record["groups"]}
        self.assertIn("client", labels)
        self.assertEqual(labels["client"]["process_count"], 2)
        self.assertEqual(record["cgroup"]["memory.peak"], 1158 * 1024 * 1024)

    def test_vanished_process_is_skipped(self):
        prev = {}
        g = memsample.sample_group(self.proc, "x", [101, 99999], prev)
        self.assertEqual(g["process_count"], 1)
        self.assertEqual(g["pids"], [101])


if __name__ == "__main__":
    unittest.main()
