from agent_preflight.models import ActionPayload
from agent_preflight.policy import BlockActionNamesPolicy


def test_block_action_names_policy_blocks_configured_action():
    policy = BlockActionNamesPolicy({"delete_rows"})

    decision = policy.evaluate(ActionPayload(action_name="delete_rows"))

    assert decision.allowed is False
    assert decision.reason == "Action is blocked by policy"
    assert decision.policy_name == "block_action_names"


def test_block_action_names_policy_allows_other_actions():
    policy = BlockActionNamesPolicy({"delete_rows"})

    decision = policy.evaluate(ActionPayload(action_name="lookup_user"))

    assert decision.allowed is True
    assert decision.reason == "Allowed by policy"
