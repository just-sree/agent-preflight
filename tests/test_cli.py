import json

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
