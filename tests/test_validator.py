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
