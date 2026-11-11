"""Pure final evidence gate for an already observed, privately owned native trial.

This checks recorded completion, not live process state or gameplay quality.
It never promotes an unfinished/failed window or changes qualification scope.
Call after all cleanup attempts, persist ``result.status`` and ``result.reasons``,
then raise/exit nonzero if ``not result.accepted``. The input is not mutated.
"""

from collections.abc import Mapping, Sequence
from dataclasses import dataclass


@dataclass(frozen=True)
class TrialEvidence:
    accepted: bool
    status: str
    reasons: tuple[str, ...]


def finalize_trial_evidence(report: Mapping, *, expected_roles: Sequence[str]) -> TrialEvidence:
    """Require a completed PASS window and complete recorded cleanup of every role."""
    status = report.get("status")
    passed = isinstance(status, str) and (status == "PASS" or status.startswith("PASS_"))
    reasons = [] if passed else ["window_not_passed"]
    errors = report.get("errors")
    if not isinstance(errors, (list, tuple)):
        reasons.append("errors_missing_or_invalid")
    elif errors:
        reasons.append("recorded_errors")

    roles_valid = (
        isinstance(expected_roles, (list, tuple))
        and bool(expected_roles)
        and all(isinstance(role, str) and role.strip() for role in expected_roles)
        and len(set(expected_roles)) == len(expected_roles)
    )
    if not roles_valid:
        reasons.append("expected_roles_invalid")
    cleanup = report.get("cleanup")
    if not isinstance(cleanup, Mapping) or not cleanup:
        reasons.append("cleanup_missing_or_empty")
    else:
        if roles_valid and set(cleanup) != set(expected_roles):
            reasons.append("cleanup_roles_mismatch")
        for role, record in cleanup.items():
            if not isinstance(record, Mapping):
                reasons.append(f"cleanup_record_invalid:{role}")
                continue
            identity = record.get("identity")
            if not (
                isinstance(identity, (list, tuple))
                and len(identity) == 2
                and all(type(value) is int for value in identity)
                and identity[0] > 1
                and identity[1] > 0
            ):
                reasons.append(f"cleanup_identity_invalid:{role}")
            if record.get("closed") is not True:
                reasons.append(f"cleanup_not_closed:{role}")
    return TrialEvidence(not reasons, status if not reasons else "FAIL", tuple(reasons))
