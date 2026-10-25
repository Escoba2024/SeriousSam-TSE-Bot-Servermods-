#!/usr/bin/env python3
"""Tests for resource_model.py: anchors echo back as MEASURED, projections
stay tagged, and the linear B fit stays consistent with the independent
Redstation 7/8-client observation."""

from __future__ import annotations

import sys
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

import resource_model as rm  # noqa: E402


class ResourceModelTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.m = rm.load_measurements()
        cls.model = rm.build_model(cls.m)
        cls.rows = {(r["architecture"], r["bots"]): r for r in cls.model["rows"]}

    def test_measured_anchors_echoed_not_recomputed(self):
        b1 = self.rows[("B", 1)]
        self.assertEqual(b1["ram_mib"], 555.8)
        self.assertEqual(b1["ram_evidence"], rm.MEASURED)
        b4 = self.rows[("B", 4)]
        self.assertEqual(b4["ram_mib"], 1158.0)
        self.assertEqual(b4["ram_evidence"], rm.MEASURED)
        a8 = self.rows[("A", 8)]
        self.assertEqual(a8["ram_evidence"], rm.MEASURED)
        self.assertAlmostEqual(a8["ram_mib"], 418.6, delta=1.5)

    def test_projections_are_tagged_projected(self):
        self.assertEqual(self.rows[("B", 8)]["ram_evidence"], rm.PROJECTED)
        self.assertEqual(self.rows[("B", 16)]["ram_evidence"], rm.PROJECTED)
        self.assertEqual(self.rows[("A", 16)]["ram_evidence"], rm.PROJECTED)
        for n in (1, 4, 8, 16):
            self.assertEqual(self.rows[("D", n)]["ram_evidence"], rm.PROJECTED_OPT)

    def test_b_linear_fit_vs_redstation_independent_run(self):
        """Fit prediction for 7-8 clients must bracket the independent
        Redstation measurement within a sane tolerance (fit is allowed to be
        conservative, not optimistic by more than 15%)."""
        b = self.m["arch_b_individual_clients"]
        d = self.m["derived"]
        fit_7 = d["arch_b_base_overhead_mib"] + 7 * d["arch_b_marginal_client_mib"]
        measured = b["redstation_attempt_cgroup_peak_mib"]  # 7 joined + 1 joining
        self.assertGreater(fit_7, measured * 0.85)
        self.assertLess(fit_7, measured * 1.30)

    def test_b_ram_grows_strictly_with_bots(self):
        values = [self.rows[("B", n)]["ram_mib"] for n in (1, 4, 8, 16)]
        self.assertEqual(values, sorted(values))
        self.assertLess(values[0], values[-1])

    def test_b16_exceeds_host_budget(self):
        self.assertIn("exceeds", self.rows[("B", 16)]["host_fit"])

    def test_a8_fits_host_budget(self):
        self.assertIn("fits", self.rows[("A", 8)]["host_fit"])

    def test_c_matches_a_process_count(self):
        for n in (1, 4, 8, 16):
            self.assertEqual(self.rows[("C", n)]["game_client_processes"],
                             self.rows[("A", n)]["game_client_processes"])

    def test_d_band_is_below_b_projection(self):
        for n in (8, 16):
            self.assertLess(self.rows[("D", n)]["ram_mib"], self.rows[("B", n)]["ram_mib"])

    def test_coexist_public_shrinks_budget(self):
        coexist = rm.build_model(self.m, (8,), coexist_public=True)
        row_b8 = [r for r in coexist["rows"] if r["architecture"] == "B"][0]
        # budget shrinks from 3819-700=3119 to 3819-700-531=2588 MiB
        self.assertIn("2588", row_b8["host_fit"])
        self.assertEqual(coexist["assumptions"]["coexist_public_fleet_mib"], 530.926)

    def test_disclaimer_present(self):
        self.assertIn("not capacity clearances", self.model["disclaimer"])

    def test_markdown_renders_all_rows(self):
        md = rm.to_markdown(self.model)
        self.assertEqual(md.count("| A |") + md.count("| B |")
                         + md.count("| C |") + md.count("| D |"), 16)


if __name__ == "__main__":
    unittest.main()
