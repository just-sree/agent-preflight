from pathlib import Path
from typing import Any

from pydantic import BaseModel, Field, ValidationError, field_validator
import yaml


AUDIT_BACKENDS = {"jsonl", "sqlite"}


class AuditConfig(BaseModel):
    enabled: bool = False
    backend: str = "jsonl"
    path: str | None = None

    @field_validator("backend")
    @classmethod
    def backend_must_be_supported(cls, value: str) -> str:
        if value not in AUDIT_BACKENDS:
            raise ValueError(f"Unknown audit backend: {value}")
        return value


class PreflightConfig(BaseModel):
    blocked_actions: list[str] = Field(default_factory=list)
    schemas: dict[str, str] = Field(default_factory=dict)
    audit: AuditConfig = Field(default_factory=AuditConfig)


def load_preflight_config(path: str | Path) -> PreflightConfig:
    try:
        with Path(path).open(encoding="utf-8") as config_file:
            config_data: Any = yaml.safe_load(config_file)
    except FileNotFoundError:
        raise
    except yaml.YAMLError as exc:
        raise ValueError(f"Invalid YAML config: {exc}") from exc

    if config_data is None:
        return PreflightConfig()

    try:
        return PreflightConfig.model_validate(config_data)
    except ValidationError as exc:
        raise ValueError(f"Invalid preflight config: {exc}") from exc
