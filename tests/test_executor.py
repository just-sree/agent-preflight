from agent_preflight.executor import ActionExecutor
from agent_preflight.models import ActionPayload, ExecutionResult
from agent_preflight.policy import BlockActionNamesPolicy
from agent_preflight.validator import ActionValidator


def test_executor_validates_and_dry_runs_valid_action():
    executor = ActionExecutor()

    result = executor.run(
        ActionPayload(
            action_name="lookup_user",
            arguments={"user_id": "demo-user-001"},
        )
    )

    assert isinstance(result, ExecutionResult)
    assert result.allowed is True
    assert result.executed is False
    assert result.reason == "Dry run: action validated but not executed"


def test_executor_does_not_execute_during_dry_run():
    calls = []
    executor = ActionExecutor()
    executor.register("lookup_user", lambda args: calls.append(args))

    result = executor.run(
        ActionPayload(
            action_name="lookup_user",
            arguments={"user_id": "demo-user-001"},
        )
    )

    assert result.allowed is True
    assert result.executed is False
    assert calls == []


def test_executor_executes_registered_handler_when_not_dry_run():
    executor = ActionExecutor()
    executor.register(
        "lookup_user",
        lambda args: {"user_id": args["user_id"], "status": "ok"},
    )

    result = executor.run(
        ActionPayload(
            action_name="lookup_user",
            arguments={"user_id": "demo-user-001"},
        ),
        dry_run=False,
    )

    assert result.allowed is True
    assert result.executed is True
    assert result.reason == "Action executed"
    assert result.output == {"user_id": "demo-user-001", "status": "ok"}


def test_executor_returns_no_handler_result():
    executor = ActionExecutor()

    result = executor.run(
        ActionPayload(action_name="lookup_user"),
        dry_run=False,
    )

    assert result.allowed is True
    assert result.executed is False
    assert result.reason == "No handler registered for action"


def test_executor_does_not_execute_blocked_action():
    calls = []
    policy = BlockActionNamesPolicy(blocked_actions={"delete_rows"})
    executor = ActionExecutor(validator=ActionValidator(policy=policy))
    executor.register("delete_rows", lambda args: calls.append(args))

    result = executor.run(
        ActionPayload(
            action_name="delete_rows",
            arguments={"table": "users"},
        ),
        dry_run=False,
    )

    assert result.allowed is False
    assert result.executed is False
    assert result.reason == "Action is blocked by policy"
    assert calls == []


def test_executor_catches_handler_exception_safely():
    def failing_handler(args):
        raise RuntimeError("example failure")

    executor = ActionExecutor()
    executor.register("lookup_user", failing_handler)

    result = executor.run(
        ActionPayload(action_name="lookup_user"),
        dry_run=False,
    )

    assert result.allowed is True
    assert result.executed is False
    assert result.reason == "Handler execution failed"
    assert result.error == "example failure"
