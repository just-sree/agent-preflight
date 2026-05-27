from agent_preflight import ActionPayload, ActionValidator


validator = ActionValidator()

result = validator.validate(
    ActionPayload(
        action_name="lookup_user",
        arguments={"user_id": "demo-user-001"},
        metadata={"source": "python-example"},
    )
)

print(result.model_dump_json(indent=2))
