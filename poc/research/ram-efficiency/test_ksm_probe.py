#!/usr/bin/env python3
"""Tests for ksm_probe.py against synthetic sysfs fixtures."""

from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

import ksm_probe  # noqa: E402


def make_ksm(root: Path, **values):
    d = root / "kernel" / "mm" / "ksm"
    d.mkdir(parents=True)
    for k, v in values.items():
        (d / k).write_text(f"{v}\n")


class KsmProbeTests(unittest.TestCase):
    def test_missing_ksm_reported_as_unavailable(self):
        with tempfile.TemporaryDirectory() as tmp:
            r = ksm_probe.report(Path(tmp), "6.8.0-generic", "fixture")
            self.assertFalse(r["ksm_available"])
            self.assertTrue(r["prctl_memory_merge_supported"])

    def test_savings_use_kernel_doc_formula(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            make_ksm(root, run=1, pages_shared=1000, pages_sharing=51200,
                     pages_unshared=2000, pages_volatile=10, full_scans=3,
                     pages_to_scan=100, sleep_millisecs=20)
            r = ksm_probe.report(root, "6.8.0", "fixture")
            self.assertTrue(r["ksm_running"])
            # pages_sharing * 4096 / 1 MiB = 51200*4096/1048576 = 200 MiB
            self.assertEqual(r["saved_mib"], 200.0)
            self.assertEqual(r["dedup_ratio"], 51.2)

    def test_present_but_disabled_gets_note_and_no_write(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            make_ksm(root, run=0, pages_shared=0, pages_sharing=0,
                     pages_unshared=0, pages_volatile=0, full_scans=0,
                     pages_to_scan=100, sleep_millisecs=20)
            before = (root / "kernel/mm/ksm/run").read_text()
            r = ksm_probe.report(root, "6.1.0", "fixture")
            self.assertFalse(r["ksm_running"])
            self.assertFalse(r["prctl_memory_merge_supported"])  # 6.1 < 6.4
            self.assertIn("note", r)
            self.assertEqual((root / "kernel/mm/ksm/run").read_text(), before)

    def test_kernel_version_parsing(self):
        self.assertTrue(ksm_probe.kernel_supports_process_merge("6.4.0"))
        self.assertTrue(ksm_probe.kernel_supports_process_merge("6.10.1-foo"))
        self.assertFalse(ksm_probe.kernel_supports_process_merge("5.15.0"))
        self.assertFalse(ksm_probe.kernel_supports_process_merge("weird"))

    def test_cli_fixture_tagging(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            make_ksm(root, run=1, pages_shared=10, pages_sharing=100,
                     pages_unshared=5, pages_volatile=0, full_scans=1,
                     pages_to_scan=100, sleep_millisecs=20)
            out = subprocess.run(
                [sys.executable, str(HERE / "ksm_probe.py"),
                 "--sysfs-root", str(root), "--osrelease", "6.8.0"],
                capture_output=True, text=True, check=True)
            r = json.loads(out.stdout)
            self.assertEqual(r["source"], "fixture")
            self.assertTrue(r["ksm_available"])


if __name__ == "__main__":
    unittest.main()
