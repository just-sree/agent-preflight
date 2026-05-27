from agent_preflight import ActionPayload, ActionSchema, ActionValidator


schema = ActionSchema(
    action_name="lookup_user",
    required_arguments={"user_id": "str"},
)

validator = ActionValidator(action_schema=schema)

result = validator.validate(
    ActionPayload(
        action_name="lookup_user",
        arguments={"user_id": "demo-user-001"},
        metadata={"source": "python-example"},
    )
)

print(result.model_dump_json(indent=2))
