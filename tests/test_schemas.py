import pytest
from pydantic import ValidationError

from agent_preflight.schemas import ActionSchema, load_action_schema, validate_argument_type


def test_load_action_schema_from_json():
    schema = load_action_schema("examples/action_schema.json")

    assert schema.action_name == "lookup_user"
    assert schema.required_arguments == {"user_id": "str"}
    assert schema.optional_arguments == {"include_history": "bool"}


def test_action_schema_rejects_empty_action_name():
    with pytest.raises(ValidationError):
        ActionSchema(action_name="")


def test_action_schema_rejects_unsupported_type():
    with pytest.raises(ValidationError):
        ActionSchema(action_name="lookup_user", required_arguments={"user_id": "uuid"})


def test_validate_argument_type_supports_basic_types():
    assert validate_argument_type("demo", "str") is True
    assert validate_argument_type(1, "int") is True
    assert validate_argument_type(True, "int") is False
    assert validate_argument_type(1, "float") is True
    assert validate_argument_type(1.5, "float") is True
    assert validate_argument_type(False, "float") is False
    assert validate_argument_type(False, "bool") is True
    assert validate_argument_type({}, "dict") is True
    assert validate_argument_type([], "list") is True
    assert validate_argument_type(object(), "any") is True
