from agent_preflight.models import PolicyDecision, ValidationResult
from agent_preflight.reports import build_validation_report


def test_build_validation_report_from_allowed_result():
    result = ValidationResult(
        allowed=True,
        action_name="lookup_user",
        reason="Allowed by default",
        audit_id="audit-123",
    )

    report = build_validation_report(result)

    assert report.allowed is True
    assert report.action_name == "lookup_user"
    assert report.reason == "Allowed by default"
    assert report.audit_id == "audit-123"
    assert report.policy_name is None
    assert report.output_version == "0.5"
    assert report.metadata == {}


def test_build_validation_report_from_blocked_policy_result():
    result = ValidationResult(
        allowed=False,
        action_name="delete_rows",
        reason="Action is blocked by policy",
        policy_decision=PolicyDecision(
            allowed=False,
            reason="Action is blocked by policy",
            policy_name="block_action_names",
        ),
    )

    report = build_validation_report(result)

    assert report.allowed is False
    assert report.action_name == "delete_rows"
    assert report.reason == "Action is blocked by policy"
    assert report.policy_name == "block_action_names"
    assert report.output_version == "0.5"
