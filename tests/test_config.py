import pytest

from agent_preflight.config import PreflightConfig, load_preflight_config


def test_load_valid_config():
    config = load_preflight_config("examples/preflight.yml")

    assert config.blocked_actions == ["delete_rows", "send_email"]
    assert config.schemas == {"lookup_user": "examples/action_schema.json"}
    assert config.audit.enabled is True
    assert config.audit.backend == "jsonl"
    assert config.audit.path == ".agent-preflight/audit.jsonl"


def test_load_sqlite_config():
    config = load_preflight_config("examples/preflight_sqlite.yml")

    assert config.audit.enabled is True
    assert config.audit.backend == "sqlite"
    assert config.audit.path == ".agent-preflight/audit.db"


def test_load_empty_config(tmp_path):
    config_path = tmp_path / "empty.yml"
    config_path.write_text("", encoding="utf-8")

    config = load_preflight_config(config_path)

    assert config == PreflightConfig()


def test_missing_config_file_raises_error(tmp_path):
    with pytest.raises(FileNotFoundError):
        load_preflight_config(tmp_path / "missing.yml")


def test_invalid_yaml_raises_clear_error(tmp_path):
    config_path = tmp_path / "invalid.yml"
    config_path.write_text("blocked_actions: [delete_rows", encoding="utf-8")

    with pytest.raises(ValueError, match="Invalid YAML config"):
        load_preflight_config(config_path)


def test_invalid_config_shape_raises_clear_error(tmp_path):
    config_path = tmp_path / "invalid_shape.yml"
    config_path.write_text("blocked_actions: delete_rows", encoding="utf-8")

    with pytest.raises(ValueError, match="Invalid preflight config"):
        load_preflight_config(config_path)


def test_unknown_audit_backend_raises_clear_error(tmp_path):
    config_path = tmp_path / "unknown_backend.yml"
    config_path.write_text(
        """
audit:
  enabled: true
  backend: unknown
  path: audit.out
""",
        encoding="utf-8",
    )

    with pytest.raises(ValueError, match="Unknown audit backend"):
        load_preflight_config(config_path)
