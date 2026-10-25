"""Float-model probe: determinism, mode differences and error propagation."""

from __future__ import annotations

import unittest

import _support
from _support import run_json

import fp_determinism_probe as probe
from syncval_common import f32, f32_bits


class FloatHelperTests(unittest.TestCase):
    def test_f32_rounds_to_binary32(self):
        self.assertEqual(f32_bits(0.1), 0x3DCCCCCD)
        self.assertNotEqual(f32(0.1), 0.1)

    def test_ulp_nudge_changes_one_bit(self):
        value = f32(1.0)
        nudged = probe._ulp_nudge(value, 1)
        self.assertEqual(f32_bits(nudged) - f32_bits(value), 1)


class ModelTests(unittest.TestCase):
    def test_model_is_deterministic_across_runs(self):
        first = probe.simulate("f32_strict", 120)
        second = probe.simulate("f32_strict", 120)
        self.assertEqual([probe._bits_state(s) for s in first],
                         [probe._bits_state(s) for s in second])

    def test_representable_heading_is_self_healing(self):
        """Sterbenz-exactness: the composer round-trip cannot drift for these
        inputs, so a strict and a simplifying build agree bit-exactly."""
        strict = probe.simulate("f32_strict", 200, yaw_rate_deg=45.0)
        simplified = probe.simulate("f32_simplified", 200, yaw_rate_deg=45.0)
        self.assertIsNone(probe._first_divergence(strict, simplified))

    def test_extended_precision_differs_from_strict(self):
        strict = probe.simulate("f32_strict", 200, yaw_rate_deg=45.7)
        extended = probe.simulate("f32_extended", 200, yaw_rate_deg=45.7)
        self.assertEqual(probe._first_divergence(strict, extended), 3)

    def test_no_32bit_rounding_differs_immediately(self):
        strict = probe.simulate("f32_strict", 50, yaw_rate_deg=45.7)
        ideal = probe.simulate("f64_ideal", 50, yaw_rate_deg=45.7)
        self.assertEqual(probe._first_divergence(strict, ideal), 1)

    def test_accumulator_perturbation_is_absorbed(self):
        reference = probe.simulate("f32_strict", 100)
        perturbed = probe.simulate("f32_strict", 100, acc_perturbation_ulp=1)
        drift = probe._max_axis_drift(reference, perturbed)
        self.assertEqual(drift["max_abs_position_drift_units"], 0.0)
        self.assertEqual(drift["max_abs_entity_angle_drift_deg"], 0.0)

    def test_velocity_perturbation_persists(self):
        reference = probe.simulate("f32_strict", 100)
        perturbed = probe.simulate("f32_strict", 100,
                                   velocity_perturbation_ulp=1)
        drift = probe._max_axis_drift(reference, perturbed)
        self.assertGreater(drift["max_abs_position_drift_units"], 0.0)
        self.assertEqual(probe._first_divergence(reference[1:], perturbed[1:]), 0)


class CliTests(unittest.TestCase):
    def test_cli_reports_model_divergence(self):
        payload, code = run_json("fp_determinism_probe.py", "--ticks", "200")
        self.assertEqual(payload["verdict"], "MODEL_DIVERGENCE")
        self.assertEqual(code, 3)
        self.assertEqual(payload["earliest_divergence_tick"], 1)
        self.assertEqual(payload["evidence_class"], "model")

    def test_cli_observations_are_model_class(self):
        payload, _ = run_json("fp_determinism_probe.py", "--ticks", "50")
        ids = {obs["id"]: obs for obs in payload["observations"]}
        self.assertIn("fp.earliest_divergence_tick", ids)
        self.assertEqual(ids["fp.earliest_divergence_tick"]["evidence_class"], "model")
        self.assertTrue(ids["fp.accumulator_perturbation_absorbed"]["value"])

    def test_scenario_is_echoed_for_reproducibility(self):
        payload, _ = run_json("fp_determinism_probe.py", "--ticks", "10",
                              "--yaw-rate", "30.5", "--speed-forward", "9.0")
        scenario = payload["scenario"]
        self.assertEqual(scenario["ticks"], 10)
        self.assertEqual(scenario["yaw_rate_deg_per_s"], 30.5)
        self.assertEqual(scenario["speed_forward_units_per_s"], 9.0)
        self.assertEqual(scenario["tick_hz"], 20)

    def test_invalid_tick_count_is_usage_error(self):
        result = _support.run_tool("fp_determinism_probe.py", "--ticks", "0")
        self.assertEqual(result.returncode, 2)

    def test_payload_never_claims_a_pass(self):
        payload, _ = run_json("fp_determinism_probe.py", "--ticks", "20")
        _support.assert_no_false_claim(self, payload)


if __name__ == "__main__":
    unittest.main()
