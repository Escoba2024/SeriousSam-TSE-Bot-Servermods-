#!/usr/bin/env python3
"""Tests for tools/benchmarks/tse_cpu_profile.py (synthetic procfs fixtures)."""

from __future__ import annotations

import json
import statistics
import tempfile
import unittest
from pathlib import Path

import tse_cpu_profile as prof


def write_recording(
    path: Path,
    role="client",
    pid=1000,
    seconds=60.0,
    interval=0.5,
    cores=0.5,
    host_busy=0.30,
    throttle_ratio=0.0,
    live_at_end=True,
    shares=(0.50, 0.40, 0.10),
    label=None,
) -> Path:
    meta = {
        "type": "meta",
        "tool": "tse_cpu_profile/1",
        "started_utc": "2026-10-22T10:00:00Z",
        "interval_s": interval,
        "duration_s": seconds,
        "clk_tck": prof.CLK_TCK,
        "nproc": 2,
        "label": label,
        "pids": [{"pid": pid, "role": role, "cmdline": "wine SeriousSam.exe", "cgroup": "0::/test"}],
    }
    count = int(seconds / interval)
    lines = [json.dumps(meta)]
    for index in range(count + 1):
        t = index * interval
        total_ticks = cores * t * prof.CLK_TCK
        utime = int(total_ticks * 0.8)
        stime = int(total_ticks * 0.2)
        thread_ticks = int(total_ticks)
        periods = int(t * 10)
        throttled = int(round(periods * throttle_ratio))
        throttled_us = int(t * 1e6 * throttle_ratio)
        alive = live_at_end or index < count
        sample = {
            "type": "sample",
            "t": t,
            "host": {"busy": host_busy, "load1": 0.8},
            "pids": {
                str(pid): {
                    "alive": alive,
                    "utime": utime,
                    "stime": stime,
                    "threads": 12,
                    "rss_kb": 240000 + index,
                    "thread_cpu": {
                        "main": int(thread_ticks * shares[0]),
                        "llvmpipe": int(thread_ticks * shares[1]),
                        "other": int(thread_ticks * shares[2]),
                    },
                    "threads_seen": 12,
                    "llvmpipe_threads": 4,
                    "cgroup": {
                        "path": "/sys/fs/cgroup/test",
                        "version": "v2",
                        "nr_periods": periods,
                        "nr_throttled": throttled,
                        "throttled_usec": throttled_us,
                        "quota_us": None,
                        "period_us": 100000,
                    },
                }
            },
        }
        lines.append(json.dumps(sample))
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return path


class ParseTests(unittest.TestCase):
    def test_proc_stat_with_spaces_in_comm(self):
        text = "1234 (Serious Sam (x)) S 1 2 3 4 5 6 7 8 9 10 11 12 13 14 15 16 17 18 19 20 21 22 23"
        parsed = prof.parse_proc_stat(text)
        self.assertEqual(parsed["utime"], 11)
        self.assertEqual(parsed["stime"], 12)
        self.assertEqual(parsed["threads"], 17)

    def test_cpu_stat_v1_and_v2(self):
        v2 = prof.parse_cpu_stat("usage_usec 10\nnr_periods 100\nnr_throttled 7\nthrottled_usec 5000\n")
        self.assertEqual(v2["nr_throttled"], 7)
        self.assertEqual(v2["throttled_usec"], 5000)
        v1 = prof.parse_cpu_stat("nr_periods 100\nnr_throttled 3\nthrottled_time 123456789\n")
        self.assertEqual(v1["throttled_usec"], 123456)

    def test_cpu_max(self):
        self.assertEqual(prof.parse_cpu_max("max 100000"), (None, 100000))
        self.assertEqual(prof.parse_cpu_max("45000 100000"), (45000, 100000))

    def test_thread_classification(self):
        self.assertEqual(prof.classify_thread("SeriousSam.exe", 10, 10), "main")
        self.assertEqual(prof.classify_thread("llvmpipe-3", 11, 10), "llvmpipe")
        self.assertEqual(prof.classify_thread("wine-preloader", 12, 10), "other")

    def test_host_stat_excludes_guest(self):
        total, busy = prof.parse_host_stat(
            "cpu  100 0 50 1000 10 5 5 0 999 999\ncpu0 1 2 3 4 5 6 7 8\n"
        )
        self.assertEqual(busy, 160)
        self.assertEqual(total, 1170)


class AnalyzeTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.dir = Path(self.tmp.name)

    def tearDown(self):
        self.tmp.cleanup()

    def analyze(self, **kwargs):
        path = write_recording(self.dir / "run.jsonl", **kwargs)
        meta, samples = prof.load_recording(path)
        return prof.analyze_recording(meta, samples, **{k: v for k, v in kwargs.items() if k == "warmup_s"})

    def test_valid_window(self):
        result = self.analyze()
        self.assertTrue(result["valid"], result["reasons"])
        self.assertAlmostEqual(result["roles"]["client"]["cpu_cores"]["median"], 0.5, places=2)
        self.assertAlmostEqual(result["roles"]["client"]["threads"]["llvmpipe"], 0.40, places=1)
        self.assertGreater(result["samples"], 100)

    def test_throttled_window_is_invalid(self):
        result = self.analyze(throttle_ratio=0.803)
        self.assertFalse(result["valid"])
        self.assertTrue(any("throttled" in reason for reason in result["reasons"]))

    def test_busy_host_is_invalid_unless_allowed(self):
        path = write_recording(self.dir / "busy.jsonl", host_busy=0.95)
        meta, samples = prof.load_recording(path)
        result = prof.analyze_recording(meta, samples)
        self.assertFalse(result["valid"])
        override = prof.analyze_recording(meta, samples, allow_busy_host=True)
        self.assertTrue(override["valid"], override["reasons"])

    def test_dead_process_is_invalid(self):
        result = self.analyze(live_at_end=False)
        self.assertFalse(result["valid"])
        self.assertTrue(any("disappeared" in reason for reason in result["reasons"]))

    def test_warmup_excludes_early_spike(self):
        path = self.dir / "spike.jsonl"
        meta = {
            "type": "meta",
            "tool": "tse_cpu_profile/1",
            "started_utc": "2026-10-22T10:00:00Z",
            "interval_s": 0.5,
            "duration_s": 60,
            "clk_tck": prof.CLK_TCK,
            "nproc": 2,
            "pids": [{"pid": 7, "role": "client"}],
        }
        lines = [json.dumps(meta)]
        cumulative = 0.0
        for index in range(121):
            t = index * 0.5
            cores = 2.0 if t < 10 else 1.0
            cumulative += cores * 0.5 * prof.CLK_TCK
            lines.append(json.dumps({
                "type": "sample",
                "t": t,
                "host": {"busy": 0.3, "load1": 0.5},
                "pids": {"7": {
                    "alive": True,
                    "utime": int(cumulative * 0.8),
                    "stime": int(cumulative * 0.2),
                    "threads": 4,
                    "rss_kb": 1000,
                    "thread_cpu": {"main": int(cumulative * 0.5),
                                   "llvmpipe": int(cumulative * 0.4),
                                   "other": int(cumulative * 0.1)},
                    "threads_seen": 4,
                    "llvmpipe_threads": 1,
                    "cgroup": None,
                }},
            }))
        path.write_text("\n".join(lines) + "\n", encoding="utf-8")
        recorded = prof.load_recording(path)
        raw = prof.analyze_recording(*recorded)
        warm = prof.analyze_recording(*recorded, warmup_s=15.0)
        self.assertGreater(raw["roles"]["client"]["cpu_cores"]["max"], 1.5)
        self.assertLess(warm["roles"]["client"]["cpu_cores"]["median"], 1.1)


class CompareTests(unittest.TestCase):
    def runs(self, cores, valid=True):
        return [
            {
                "valid": valid,
                "label": "rep%d" % index,
                "roles": {"client": {"cpu_cores": {"median": value}}},
            }
            for index, value in enumerate(cores)
        ]

    def test_qualified_saving(self):
        result = prof.compare_runs(self.runs([1.0, 1.02, 0.98]), self.runs([0.5, 0.52, 0.49]))
        self.assertEqual(result["verdict"], "QUALIFIED_MEASUREMENT")
        self.assertGreater(result["saving_pct"], 45.0)

    def test_overlapping_runs_are_rejected(self):
        result = prof.compare_runs(self.runs([0.60, 0.62, 0.58]), self.runs([0.59, 0.61, 0.57]))
        self.assertEqual(result["verdict"], "NOT_QUALIFIED")
        self.assertTrue(any("overlap" in reason for reason in result["reasons"]))

    def test_two_repetitions_are_rejected(self):
        result = prof.compare_runs(self.runs([1.0, 1.0]), self.runs([0.5, 0.5]))
        self.assertEqual(result["verdict"], "NOT_QUALIFIED")
        self.assertTrue(any("baseline repetitions" in reason for reason in result["reasons"]))

    def test_invalid_runs_are_rejected(self):
        result = prof.compare_runs(self.runs([1.0, 1.0, 1.0], valid=False), self.runs([0.5, 0.5, 0.5]))
        self.assertEqual(result["verdict"], "NOT_QUALIFIED")


class CliTests(unittest.TestCase):
    def test_analyze_exit_codes(self):
        with tempfile.TemporaryDirectory() as tmp:
            good = write_recording(Path(tmp) / "good.jsonl")
            self.assertEqual(prof.main(["analyze", "--input", str(good), "--json", str(Path(tmp) / "a.json")]), 0)
            bad = write_recording(Path(tmp) / "bad.jsonl", throttle_ratio=0.9)
            self.assertEqual(prof.main(["analyze", "--input", str(bad)]), prof.EXIT_INVALID)

    def test_compare_exit_codes(self):
        with tempfile.TemporaryDirectory() as tmp:
            paths = []
            for index in range(3):
                path = write_recording(Path(tmp) / ("a%d.jsonl" % index), cores=1.0, label="a%d" % index)
                meta, samples = prof.load_recording(path)
                out = Path(tmp) / ("a%d.json" % index)
                out.write_text(json.dumps(prof.analyze_recording(meta, samples)))
                paths.append(str(out))
            cand = []
            for index in range(3):
                path = write_recording(Path(tmp) / ("b%d.jsonl" % index), cores=0.5, label="b%d" % index)
                meta, samples = prof.load_recording(path)
                out = Path(tmp) / ("b%d.json" % index)
                out.write_text(json.dumps(prof.analyze_recording(meta, samples)))
                cand.append(str(out))
            args = ["compare", "--role", "client", "--min-saving-pct", "5"]
            for path in paths:
                args += ["--baseline", path]
            for path in cand:
                args += ["--candidate", path]
            self.assertEqual(prof.main(args), 0)


if __name__ == "__main__":
    unittest.main()
