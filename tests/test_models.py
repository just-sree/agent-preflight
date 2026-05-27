import pytest
from pydantic import ValidationError

from agent_preflight.models import ActionPayload


def test_valid_action_payload():
    payload = ActionPayload(action_name="lookup_user")

    assert payload.action_name == "lookup_user"
    assert payload.arguments == {}
    assert payload.metadata == {}


def test_empty_action_name_rejected():
    with pytest.raises(ValidationError):
        ActionPayload(action_name="")
