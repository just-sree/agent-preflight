import json
import sqlite3

from agent_preflight.cli import main


def test_cli_allows_allowed_action(capsys):
    exit_code = main(["validate", "examples/allowed_action.json"])

    captured = capsys.readouterr()
    result = json.loads(captured.out)

    assert exit_code == 0
    assert result["allowed"] is True
    assert result["action_name"] == "lookup_user"


def test_cli_blocks_blocked_action(capsys):
    exit_code = main(
        [
            "validate",
            "examples/blocked_action.json",
            "--block-action",
            "delete_rows",
        ]
    )

    captured = capsys.readouterr()
    result = json.loads(captured.out)

    assert exit_code == 2
    assert result["allowed"] is False
    assert result["action_name"] == "delete_rows"


def test_cli_missing_file_returns_error(capsys):
    exit_code = main(["validate", "examples/missing.json"])

    captured = capsys.readouterr()

    assert exit_code == 1
    assert "error" in json.loads(captured.err)


def test_cli_malformed_json_returns_structured_rejection(tmp_path, capsys):
    json_path = tmp_path / "bad.json"
    json_path.write_text("{", encoding="utf-8")

    exit_code = main(["validate", str(json_path)])

    captured = capsys.readouterr()
    result = json.loads(captured.out)

    assert exit_code == 2
    assert result["allowed"] is False
    assert result["action_name"] == "<invalid>"
    assert result["reason"].startswith("Invalid JSON payload")


def test_cli_schema_allows_valid_action(capsys):
    exit_code = main(
        [
            "validate",
            "examples/allowed_action.json",
            "--schema",
            "examples/action_schema.json",
        ]
    )

    captured = capsys.readouterr()
    result = json.loads(captured.out)

    assert exit_code == 0
    assert result["allowed"] is True


def test_cli_schema_blocks_invalid_action(capsys):
    exit_code = main(
        [
            "validate",
            "examples/invalid_missing_argument.json",
            "--schema",
            "examples/action_schema.json",
        ]
    )

    captured = capsys.readouterr()
    result = json.loads(captured.out)

    assert exit_code == 2
    assert result["allowed"] is False
    assert result["reason"] == "Missing required argument: user_id"


def test_cli_config_blocked_action_blocks_action(capsys):
    exit_code = main(
        [
            "validate",
            "examples/blocked_action.json",
            "--config",
            "examples/preflight.yml",
        ]
    )

    captured = capsys.readouterr()
    result = json.loads(captured.out)

    assert exit_code == 2
    assert result["allowed"] is False
    assert result["reason"] == "Action is blocked by policy"


def test_cli_config_schema_allows_valid_action(capsys):
    exit_code = main(
        [
            "validate",
            "examples/allowed_action.json",
            "--config",
            "examples/preflight.yml",
        ]
    )

    captured = capsys.readouterr()
    result = json.loads(captured.out)

    assert exit_code == 0
    assert result["allowed"] is True


def test_cli_config_schema_blocks_missing_required_argument(capsys):
    exit_code = main(
        [
            "validate",
            "examples/invalid_missing_argument.json",
            "--config",
            "examples/preflight.yml",
        ]
    )

    captured = capsys.readouterr()
    result = json.loads(captured.out)

    assert exit_code == 2
    assert result["allowed"] is False
    assert result["reason"] == "Missing required argument: user_id"


def test_cli_schema_overrides_config_schema(tmp_path, capsys):
    override_schema = tmp_path / "override_schema.json"
    override_schema.write_text(
        json.dumps(
            {
                "action_name": "lookup_user",
                "required_arguments": {},
            }
        ),
        encoding="utf-8",
    )

    exit_code = main(
        [
            "validate",
            "examples/invalid_missing_argument.json",
            "--config",
            "examples/preflight.yml",
            "--schema",
            str(override_schema),
        ]
    )

    captured = capsys.readouterr()
    result = json.loads(captured.out)

    assert exit_code == 0
    assert result["allowed"] is True


def test_cli_audit_log_overrides_config_audit_path(tmp_path, capsys):
    audit_path = tmp_path / "audit.jsonl"

    exit_code = main(
        [
            "validate",
            "examples/allowed_action.json",
            "--config",
            "examples/preflight.yml",
            "--audit-log",
            str(audit_path),
        ]
    )

    captured = capsys.readouterr()
    result = json.loads(captured.out)

    assert exit_code == 0
    assert result["audit_id"]
    assert audit_path.exists()


def test_cli_block_action_combines_with_config_blocked_actions(capsys):
    exit_code = main(
        [
            "validate",
            "examples/allowed_action.json",
            "--config",
            "examples/preflight.yml",
            "--block-action",
            "lookup_user",
        ]
    )

    captured = capsys.readouterr()
    result = json.loads(captured.out)

    assert exit_code == 2
    assert result["allowed"] is False
    assert result["reason"] == "Action is blocked by policy"


def test_cli_writes_sqlite_audit_record_with_backend_flag(tmp_path, capsys):
    audit_path = tmp_path / "audit.db"

    exit_code = main(
        [
            "validate",
            "examples/allowed_action.json",
            "--audit-backend",
            "sqlite",
            "--audit-log",
            str(audit_path),
        ]
    )

    captured = capsys.readouterr()
    result = json.loads(captured.out)

    assert exit_code == 0
    assert result["audit_id"]

    with sqlite3.connect(audit_path) as connection:
        row_count = connection.execute(
            "SELECT COUNT(*) FROM audit_records"
        ).fetchone()[0]

    assert row_count == 1


def test_cli_config_can_enable_sqlite_audit_backend(tmp_path, capsys):
    audit_path = tmp_path / "audit.db"
    config_path = tmp_path / "preflight_sqlite.yml"
    config_path.write_text(
        f"""
schemas:
  lookup_user: examples/action_schema.json
audit:
  enabled: true
  backend: sqlite
  path: {audit_path.as_posix()}
""",
        encoding="utf-8",
    )

    exit_code = main(
        [
            "validate",
            "examples/allowed_action.json",
            "--config",
            str(config_path),
        ]
    )

    captured = capsys.readouterr()
    result = json.loads(captured.out)

    assert exit_code == 0
    assert result["audit_id"]
    assert audit_path.exists()


def test_cli_audit_backend_overrides_config_backend(tmp_path, capsys):
    audit_path = tmp_path / "audit.jsonl"

    exit_code = main(
        [
            "validate",
            "examples/allowed_action.json",
            "--config",
            "examples/preflight_sqlite.yml",
            "--audit-backend",
            "jsonl",
            "--audit-log",
            str(audit_path),
        ]
    )

    captured = capsys.readouterr()
    result = json.loads(captured.out)

    assert exit_code == 0
    assert result["audit_id"]
    assert audit_path.exists()
    assert json.loads(audit_path.read_text(encoding="utf-8").splitlines()[0])[
        "audit_id"
    ] == result["audit_id"]


def test_cli_unknown_audit_backend_fails_clearly(capsys):
    exit_code = main(
        [
            "validate",
            "examples/allowed_action.json",
            "--audit-backend",
            "unknown",
            "--audit-log",
            "audit.out",
        ]
    )

    captured = capsys.readouterr()

    assert exit_code == 1
    assert "Unknown audit backend" in captured.err


def test_cli_output_json_prints_validation_report(capsys):
    exit_code = main(
        [
            "validate",
            "examples/allowed_action.json",
            "--config",
            "examples/preflight.yml",
            "--output",
            "json",
        ]
    )

    captured = capsys.readouterr()
    report = json.loads(captured.out)

    assert exit_code == 0
    assert report["allowed"] is True
    assert report["action_name"] == "lookup_user"
    assert report["output_version"] == "0.5"
    assert report["metadata"] == {}


def test_cli_output_text_prints_human_readable_fields(capsys):
    exit_code = main(
        [
            "validate",
            "examples/blocked_action.json",
            "--config",
            "examples/preflight.yml",
            "--output",
            "text",
        ]
    )

    captured = capsys.readouterr()

    assert exit_code == 2
    assert "allowed: false" in captured.out
    assert "action_name: delete_rows" in captured.out
    assert "reason: Action is blocked by policy" in captured.out
    assert "audit_id:" in captured.out


def test_cli_report_file_writes_report_json(tmp_path, capsys):
    report_path = tmp_path / "blocked-result.json"

    exit_code = main(
        [
            "validate",
            "examples/blocked_action.json",
            "--config",
            "examples/preflight.yml",
            "--report-file",
            str(report_path),
        ]
    )

    captured = capsys.readouterr()
    stdout_result = json.loads(captured.out)
    report = json.loads(report_path.read_text(encoding="utf-8"))

    assert exit_code == 2
    assert stdout_result["allowed"] is False
    assert report["allowed"] is False
    assert report["action_name"] == "delete_rows"
    assert report["policy_name"] == "block_action_names"
    assert report["output_version"] == "0.5"


def test_cli_report_file_creates_parent_directory(tmp_path, capsys):
    report_path = tmp_path / "reports" / "result.json"

    exit_code = main(
        [
            "validate",
            "examples/allowed_action.json",
            "--report-file",
            str(report_path),
        ]
    )

    capsys.readouterr()

    assert exit_code == 0
    assert report_path.exists()


def test_cli_report_output_does_not_include_raw_arguments(tmp_path, capsys):
    payload_path = tmp_path / "payload.json"
    payload_path.write_text(
        json.dumps(
            {
                "action_name": "lookup_user",
                "arguments": {
                    "user_id": "secret-user-id",
                },
            }
        ),
        encoding="utf-8",
    )
    report_path = tmp_path / "result.json"

    exit_code = main(
        [
            "validate",
            str(payload_path),
            "--output",
            "json",
            "--report-file",
            str(report_path),
        ]
    )

    captured = capsys.readouterr()
    stdout_report = json.loads(captured.out)
    file_text = report_path.read_text(encoding="utf-8")

    assert exit_code == 0
    assert "secret-user-id" not in captured.out
    assert "secret-user-id" not in file_text
    assert "arguments" not in stdout_report


def test_cli_output_json_blocked_action_still_exits_2(capsys):
    exit_code = main(
        [
            "validate",
            "examples/blocked_action.json",
            "--config",
            "examples/preflight.yml",
            "--output",
            "json",
        ]
    )

    captured = capsys.readouterr()
    report = json.loads(captured.out)

    assert exit_code == 2
    assert report["allowed"] is False


def test_cli_output_json_allowed_action_still_exits_0(capsys):
    exit_code = main(
        [
            "validate",
            "examples/allowed_action.json",
            "--config",
            "examples/preflight.yml",
            "--output",
            "json",
        ]
    )

    captured = capsys.readouterr()
    report = json.loads(captured.out)

    assert exit_code == 0
    assert report["allowed"] is True
