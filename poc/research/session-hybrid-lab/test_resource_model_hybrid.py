#!/usr/bin/env python3
"""Reproduzierbare Tests für resource_model_hybrid.py (offline, Fixtures)."""

from __future__ import annotations

import unittest

import resource_model_hybrid as rm


class ModelStructureTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.m = rm.load_measurements()
        cls.model = rm.build_model(cls.m)
        cls.rows = {(r["architecture"], r["bots"]): r for r in cls.model["rows"]}

    def test_evidence_classes_present(self):
        self.assertIn("T", self.model["evidence_classes"])
        self.assertIn("D", self.model["evidence_classes"])
        self.assertIn("P", self.model["evidence_classes"])

    def test_disclaimer_present(self):
        self.assertIn("keine Kapazitaetsfreigabe", self.model["disclaimer"])

    def test_host_anchor(self):
        self.assertEqual(self.model["host"]["total_mib"], 3819)
        self.assertEqual(self.model["host"]["vcpus"], 2)


class ArchATests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.m = rm.load_measurements()
        cls.rows = {(r["architecture"], r["bots"]): r
                    for r in rm.build_model(cls.m)["rows"]}

    def test_a8_measured_anchor(self):
        a8 = self.rows[("A", 8)]
        self.assertEqual(a8["ram_evidence"], rm.MEASURED)
        self.assertAlmostEqual(a8["ram_mib"], 418.6, delta=1.0)
        self.assertEqual(a8["cpu_evidence"], rm.MEASURED)
        self.assertAlmostEqual(a8["cpu_core_percent"], 69.0, delta=0.5)
        self.assertEqual(a8["game_client_processes"], 2)

    def test_a_process_count_ceil_div_4(self):
        for n, procs in ((1, 1), (4, 1), (8, 2), (16, 4)):
            self.assertEqual(self.rows[("A", n)]["game_client_processes"], procs)

    def test_a16_projected(self):
        self.assertEqual(self.rows[("A", 16)]["ram_evidence"], rm.PROJECTED)


class ArchBTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.m = rm.load_measurements()
        cls.rows = {(r["architecture"], r["bots"]): r
                    for r in rm.build_model(cls.m)["rows"]}

    def test_b1_b4_measured(self):
        self.assertEqual(self.rows[("B", 1)]["ram_evidence"], rm.MEASURED)
        self.assertAlmostEqual(self.rows[("B", 1)]["ram_mib"], 555.8, delta=0.5)
        self.assertEqual(self.rows[("B", 4)]["ram_evidence"], rm.MEASURED)
        self.assertAlmostEqual(self.rows[("B", 4)]["ram_mib"], 1158.0, delta=0.5)

    def test_b16_exceeds_budget(self):
        self.assertIn("exceeds", self.rows[("B", 16)]["host_fit"])

    def test_b_independent_join_leave(self):
        for n in (1, 4, 8, 16):
            self.assertEqual(self.rows[("B", n)]["independent_join_leave"],
                             "ja (ein Prozess pro Bot)")


class ArchC1Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.m = rm.load_measurements()
        cls.rows = {(r["architecture"], r["bots"]): r
                    for r in rm.build_model(cls.m)["rows"]}

    def test_c1_process_count_equals_a(self):
        for n in (1, 4, 8, 16):
            self.assertEqual(self.rows[("C1", n)]["game_client_processes"],
                             self.rows[("A", n)]["game_client_processes"])

    def test_c1_independent_join_leave(self):
        self.assertTrue(self.rows[("C1", 8)]["independent_join_leave"].startswith(
            "pro-Bot"))

    def test_c1_ram_a_plus_transient(self):
        # C1 8 Bots = A-Prozesszahl (2) + 1 transienter Client bei Restart
        a8 = self.rows[("A", 8)]["ram_mib"]
        c18 = self.rows[("C1", 8)]["ram_mib"]
        self.assertAlmostEqual(c18, a8 + 184.2, delta=0.5)
        self.assertEqual(self.rows[("C1", 8)]["ram_evidence"], rm.DERIVED)

    def test_c1_one_bot_no_transient(self):
        c11 = self.rows[("C1", 1)]["ram_mib"]
        a1 = self.rows[("A", 1)]["ram_mib"]
        self.assertAlmostEqual(c11, a1, delta=0.5)  # kein Restart bei 1 Bot


class FitAssessmentTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.m = rm.load_measurements()

    def test_budget_split(self):
        self.assertEqual(rm.fit_assessment(1000), "fits (<80% von 3119 MiB Budget)")
        self.assertIn("tight", rm.fit_assessment(2600))
        self.assertIn("exceeds", rm.fit_assessment(4000))

    def test_coexist_public_shrinks_budget(self):
        model = rm.build_model(self.m, (8,), coexist_public=True)
        row_b8 = [r for r in model["rows"] if r["architecture"] == "B"][0]
        self.assertIn("2588", row_b8["host_fit"])


if __name__ == "__main__":
    unittest.main(verbosity=2)
