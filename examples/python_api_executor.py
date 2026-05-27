from agent_preflight import ActionExecutor, ActionPayload


def lookup_user(arguments: dict):
    return {
        "user_id": arguments["user_id"],
        "status": "example-only",
    }


executor = ActionExecutor()
executor.register("lookup_user", lookup_user)

dry_run_result = executor.run(
    ActionPayload(
        action_name="lookup_user",
        arguments={"user_id": "demo-user-001"},
    )
)

print("Dry run:")
print(dry_run_result.model_dump_json(indent=2))

execute_result = executor.run(
    ActionPayload(
        action_name="lookup_user",
        arguments={"user_id": "demo-user-001"},
    ),
    dry_run=False,
)

print("Executed:")
print(execute_result.model_dump_json(indent=2))
