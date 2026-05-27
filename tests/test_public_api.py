import agent_preflight


def test_public_imports_work_from_agent_preflight():
    expected_names = {
        "ActionPayload",
        "ActionSchema",
        "ActionValidator",
        "BlockActionNamesPolicy",
        "AuditWriter",
        "SQLiteAuditWriter",
        "ValidationResult",
        "ValidationReport",
        "ActionExecutor",
        "ExecutionResult",
    }

    for name in expected_names:
        assert hasattr(agent_preflight, name)


def test_basic_python_api_validation_allows_valid_action():
    payload = agent_preflight.ActionPayload(
        action_name="lookup_user",
        arguments={"user_id": "demo-user-001"},
    )
    validator = agent_preflight.ActionValidator()

    result = validator.validate(payload)

    assert result.allowed is True
    assert result.action_name == "lookup_user"


def test_policy_import_blocks_configured_action():
    policy = agent_preflight.BlockActionNamesPolicy(blocked_actions={"delete_rows"})
    validator = agent_preflight.ActionValidator(policy=policy)

    result = validator.validate(
        agent_preflight.ActionPayload(
            action_name="delete_rows",
            arguments={"table": "users"},
        )
    )

    assert result.allowed is False
    assert result.reason == "Action is blocked by policy"


def test_schema_import_validates_required_argument():
    schema = agent_preflight.ActionSchema(
        action_name="lookup_user",
        required_arguments={"user_id": "str"},
    )
    validator = agent_preflight.ActionValidator(action_schema=schema)

    result = validator.validate(
        agent_preflight.ActionPayload(
            action_name="lookup_user",
            arguments={"user_id": "demo-user-001"},
        )
    )

    assert result.allowed is True


def test_report_builder_import_works():
    result = agent_preflight.ValidationResult(
        allowed=True,
        action_name="lookup_user",
        reason="Allowed by default",
    )

    report = agent_preflight.build_validation_report(result)

    assert isinstance(report, agent_preflight.ValidationReport)
    assert report.allowed is True


def test_audit_writer_imports_work(tmp_path):
    jsonl_writer = agent_preflight.AuditWriter(tmp_path / "audit.jsonl")
    sqlite_writer = agent_preflight.SQLiteAuditWriter(tmp_path / "audit.db")

    assert jsonl_writer.path.name == "audit.jsonl"
    assert sqlite_writer.path.name == "audit.db"


def test_executor_imports_work():
    executor = agent_preflight.ActionExecutor()

    result = executor.run(agent_preflight.ActionPayload(action_name="lookup_user"))

    assert isinstance(result, agent_preflight.ExecutionResult)
    assert result.allowed is True
