from agent_preflight import ActionPayload, ActionValidator, BlockActionNamesPolicy


policy = BlockActionNamesPolicy(blocked_actions={"delete_rows"})
validator = ActionValidator(policy=policy)

result = validator.validate(
    ActionPayload(
        action_name="delete_rows",
        arguments={"table": "users"},
        metadata={"source": "python-example"},
    )
)

print(result.model_dump_json(indent=2))
