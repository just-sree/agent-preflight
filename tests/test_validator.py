from agent_preflight.models import ActionPayload
from agent_preflight.schemas import ActionSchema
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


def test_schema_bound_validation_requires_argument():
    schema = ActionSchema(
        action_name="lookup_user",
        required_arguments={"user_id": "str"},
    )

    result = ActionValidator(action_schema=schema).validate(
        ActionPayload(action_name="lookup_user", arguments={})
    )

    assert result.allowed is False
    assert result.reason == "Missing required argument: user_id"


def test_schema_bound_validation_blocks_wrong_argument_type():
    schema = ActionSchema(
        action_name="lookup_user",
        required_arguments={"user_id": "str"},
    )

    result = ActionValidator(action_schema=schema).validate(
        ActionPayload(action_name="lookup_user", arguments={"user_id": 123})
    )

    assert result.allowed is False
    assert result.reason == "Invalid type for argument user_id: expected str"


def test_schema_bound_validation_allows_valid_action():
    schema = ActionSchema(
        action_name="lookup_user",
        required_arguments={"user_id": "str"},
    )

    result = ActionValidator(action_schema=schema).validate(
        ActionPayload(
            action_name="lookup_user",
            arguments={"user_id": "demo-user-001"},
        )
    )

    assert result.allowed is True
    assert result.reason == "Allowed by default"


def test_schema_bound_validation_checks_optional_argument_type():
    schema = ActionSchema(
        action_name="lookup_user",
        required_arguments={"user_id": "str"},
        optional_arguments={"include_history": "bool"},
    )

    result = ActionValidator(action_schema=schema).validate(
        ActionPayload(
            action_name="lookup_user",
            arguments={"user_id": "demo-user-001", "include_history": "yes"},
        )
    )

    assert result.allowed is False
    assert result.reason == "Invalid type for argument include_history: expected bool"


def test_schema_bound_validation_checks_action_name():
    schema = ActionSchema(action_name="lookup_user")

    result = ActionValidator(action_schema=schema).validate(
        ActionPayload(action_name="send_email")
    )

    assert result.allowed is False
    assert result.reason == "Action name does not match schema"
