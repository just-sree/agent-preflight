from agent_preflight.models import ActionPayload
from agent_preflight.validator import ActionValidator


def test_default_validator_allows_action():
    result = ActionValidator().validate(ActionPayload(action_name="lookup_user"))

    assert result.allowed is True
    assert result.action_name == "lookup_user"
    assert result.reason == "Allowed by default"


def test_validator_returns_blocked_result_for_invalid_payload():
    result = ActionValidator().validate({"action_name": ""})

    assert result.allowed is False
    assert result.action_name == "<invalid>"
    assert result.reason == "Invalid action payload"


class FailingAuditWriter:
    def write(self, payload, result_allowed, reason):
        raise OSError("audit path is unavailable")


def test_audit_write_failure_does_not_block_validation(capsys):
    result = ActionValidator(audit_writer=FailingAuditWriter()).validate(
        ActionPayload(action_name="lookup_user")
    )

    captured = capsys.readouterr()

    assert result.allowed is True
    assert result.audit_id is None
    assert "Failed to write audit record" in captured.err
