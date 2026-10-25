"""Registry completeness tests: a hypothesis without falsifier is not allowed."""

from __future__ import annotations

import copy
import unittest

import _support
from _support import run_json, run_tool

import hypothesis_registry as registry
import verdict_engine
from syncval_common import EVIDENCE_CLASSES


class RegistryValidationTests(unittest.TestCase):
    def test_registry_is_valid(self):
        self.assertEqual(registry.validate(), [])

    def test_check_cli_exit_zero(self):
        result = run_tool("hypothesis_registry.py", "--check")
        self.assertEqual(result.returncode, 0, result.stderr)

    def test_ids_unique_and_prefixed(self):
        ids = [entry["id"] for entry in registry.HYPOTHESES]
        self.assertEqual(len(ids), len(set(ids)))
        for ident in ids:
            self.assertTrue(ident.startswith("H"), ident)

    def test_assumptions_have_distinct_prefix(self):
        ids = {entry["id"] for entry in registry.HYPOTHESES}
        for entry in registry.ASSUMPTIONS:
            self.assertTrue(str(entry["id"]).startswith("A"))
            self.assertNotIn(entry["id"], ids)

    def test_every_hypothesis_has_falsifier_and_evidence_floor(self):
        for entry in registry.HYPOTHESES:
            self.assertTrue(str(entry["falsifier"]).strip())
            self.assertIn(entry["min_evidence_class"], EVIDENCE_CLASSES)

    def test_pr58_mapping_present_for_all(self):
        for entry in registry.HYPOTHESES:
            self.assertTrue(str(entry["pr58_id"]).strip())

    def test_unknown_operator_is_rejected(self):
        broken = copy.deepcopy(registry.HYPOTHESES)
        broken[0]["support_when"]["rules"][0]["op"] = "approximately"
        original = registry.HYPOTHESES
        try:
            registry.HYPOTHESES = broken
            problems = registry.validate()
        finally:
            registry.HYPOTHESES = original
        self.assertTrue(any("unknown op" in problem for problem in problems))

    def test_rule_must_reference_required_observation(self):
        broken = copy.deepcopy(registry.HYPOTHESES)
        broken[1]["refute_when"]["rules"][0]["obs"] = "coverage.not_declared"
        original = registry.HYPOTHESES
        try:
            registry.HYPOTHESES = broken
            problems = registry.validate()
        finally:
            registry.HYPOTHESES = original
        self.assertTrue(any("not in required_observations" in problem
                            for problem in problems))

    def test_missing_falsifier_is_reported(self):
        broken = copy.deepcopy(registry.HYPOTHESES)
        broken[0]["falsifier"] = ""
        original = registry.HYPOTHESES
        try:
            registry.HYPOTHESES = broken
            problems = registry.validate()
        finally:
            registry.HYPOTHESES = original
        self.assertTrue(any("missing falsifier" in problem for problem in problems))

    def test_payload_lists_hypotheses_and_assumptions(self):
        payload, code = run_json("hypothesis_registry.py")
        self.assertEqual(code, 0)
        self.assertEqual(len(payload["hypotheses"]), len(registry.HYPOTHESES))
        self.assertEqual(len(payload["assumptions"]), len(registry.ASSUMPTIONS))
        self.assertTrue(payload["validation"]["valid"])

    def test_checksum_scope_is_an_assumption_not_a_hypothesis(self):
        ids = {entry["id"] for entry in registry.HYPOTHESES}
        self.assertNotIn("A1_CHECKSUM_SCOPE", ids)
        assumption_ids = {entry["id"] for entry in registry.ASSUMPTIONS}
        self.assertIn("A1_CHECKSUM_SCOPE", assumption_ids)


class VerdictStateTests(unittest.TestCase):
    def test_no_confirmed_state_exists(self):
        for state in verdict_engine.VERDICT_STATES:
            self.assertNotIn("CONFIRM", state.upper())
            self.assertNotIn("PROVEN", state.upper())

    def test_registry_feeds_engine_without_observations(self):
        payload = verdict_engine.evaluate([])
        self.assertTrue(all(result["verdict"] == "NOT_TESTED"
                            for result in payload["hypotheses"]))
        self.assertEqual(payload["root_cause_status"], "NOT_ESTABLISHED")
        _support.assert_no_false_claim(self, payload)


if __name__ == "__main__":
    unittest.main()
