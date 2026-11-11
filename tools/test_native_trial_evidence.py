import copy
import unittest

from native_trial_evidence import finalize_trial_evidence


ROLES = ("server", "botA", "botB", "vanilla")
PASS = "PASS_LIMITED_CONTROLLED_WINE_SESSION_FIELD_AND_POPULATION"


def completed_report():
    return {
        "status": PASS,
        "errors": [],
        "cleanup": {
            role: {"identity": [100 + i, 5000 + i], "closed": True}
            for i, role in enumerate(ROLES)
        },
        "qualified": False,
    }


class NativeTrialEvidenceTests(unittest.TestCase):
    def finalize(self, report):
        return finalize_trial_evidence(report, expected_roles=ROLES)

    def assert_rejected(self, report):
        result = self.finalize(report)
        self.assertIs(result.accepted, False)
        self.assertEqual(result.status, "FAIL")
        self.assertTrue(result.reasons)
        return result

    def test_clean_completion_preserves_limited_scope_without_mutating_report(self):
        report = completed_report()
        before = copy.deepcopy(report)
        result = self.finalize(report)
        self.assertIs(result.accepted, True)
        self.assertEqual(result.status, PASS)
        self.assertEqual(result.reasons, ())
        self.assertEqual(report, before)
        self.assertIs(report["qualified"], False)

    def test_cleanup_error_cannot_leave_earlier_window_pass_accepted(self):
        report = completed_report()
        report["errors"].append("cleanup botB: normal close timed out")
        report["cleanup"]["botB"]["closed"] = False
        before = copy.deepcopy(report)
        result = self.assert_rejected(report)
        self.assertEqual(report, before)
        with self.assertRaises(RuntimeError):
            if not result.accepted:
                raise RuntimeError("native trial final evidence rejected")

    def test_error_still_rejects_when_all_processes_eventually_closed(self):
        report = completed_report()
        report["errors"] = ["unpause cleanup: process identity changed"]
        self.assert_rejected(report)

    def test_prior_failure_or_unfinished_window_cannot_be_promoted(self):
        for status in ("FAIL", "IN_PROGRESS", "", None, "PASSING"):
            with self.subTest(status=status):
                report = completed_report()
                report["status"] = status
                self.assert_rejected(report)

    def test_missing_or_empty_cleanup_and_missing_or_unexpected_roles_reject(self):
        for cleanup in (None, {}, {"server": {"identity": [100, 5000], "closed": True}}):
            with self.subTest(cleanup=cleanup):
                report = completed_report()
                report["cleanup"] = cleanup
                self.assert_rejected(report)
        report = completed_report()
        del report["cleanup"]
        self.assert_rejected(report)
        report = completed_report()
        report["cleanup"]["unregistered"] = {"identity": [999, 6000], "closed": True}
        self.assert_rejected(report)

    def test_partial_launch_missing_identity_or_unclosed_role_rejects(self):
        for record in ({"closed": True}, {"identity": None, "closed": True},
                       {"identity": [101, 5001]}, {"identity": [101, 5001], "closed": False},
                       {"identity": [101, 5001], "closed": 1}, None):
            with self.subTest(record=record):
                report = completed_report()
                report["cleanup"]["botA"] = record
                self.assert_rejected(report)

    def test_malformed_process_identity_cannot_count_as_pinned(self):
        for identity in ([], [101], [101, 5001, 9], [0, 5001], [1, 5001],
                         [101, -1], [101, 0], [True, 5001], [101, True],
                         [101.0, 5001], "101:5001"):
            with self.subTest(identity=identity):
                report = completed_report()
                report["cleanup"]["botA"]["identity"] = identity
                self.assert_rejected(report)

    def test_missing_or_malformed_error_record_is_not_proof_of_no_errors(self):
        for errors in (None, "", {}, False):
            with self.subTest(errors=errors):
                report = completed_report()
                report["errors"] = errors
                self.assert_rejected(report)
        report = completed_report()
        del report["errors"]
        self.assert_rejected(report)

    def test_invalid_expected_role_contract_rejects(self):
        for roles in ((), "server", ("server", "server"), ("",), (None,)):
            with self.subTest(roles=roles):
                result = finalize_trial_evidence(completed_report(), expected_roles=roles)
                self.assertIs(result.accepted, False)
                self.assertEqual(result.status, "FAIL")


if __name__ == "__main__":
    unittest.main()
