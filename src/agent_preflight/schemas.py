from pathlib import Path
from typing import Any
import json

from pydantic import BaseModel, Field, field_validator


ALLOWED_ARGUMENT_TYPES = {"str", "int", "float", "bool", "dict", "list", "any"}


class ActionSchema(BaseModel):
    action_name: str
    required_arguments: dict[str, str] = Field(default_factory=dict)
    optional_arguments: dict[str, str] = Field(default_factory=dict)

    @field_validator("action_name")
    @classmethod
    def action_name_must_not_be_empty(cls, value: str) -> str:
        if not value.strip():
            raise ValueError("action_name must not be empty")
        return value

    @field_validator("required_arguments", "optional_arguments")
    @classmethod
    def argument_types_must_be_supported(
        cls,
        value: dict[str, str],
    ) -> dict[str, str]:
        unsupported_types = sorted(
            {
                expected_type
                for expected_type in value.values()
                if expected_type not in ALLOWED_ARGUMENT_TYPES
            }
        )
        if unsupported_types:
            raise ValueError(
                "Unsupported argument type(s): " + ", ".join(unsupported_types)
            )
        return value


def load_action_schema(path: str | Path) -> ActionSchema:
    with Path(path).open(encoding="utf-8") as schema_file:
        schema_data = json.load(schema_file)
    return ActionSchema.model_validate(schema_data)


def validate_argument_type(value: Any, expected_type: str) -> bool:
    if expected_type == "any":
        return True
    if expected_type == "str":
        return isinstance(value, str)
    if expected_type == "int":
        return isinstance(value, int) and not isinstance(value, bool)
    if expected_type == "float":
        return isinstance(value, (int, float)) and not isinstance(value, bool)
    if expected_type == "bool":
        return isinstance(value, bool)
    if expected_type == "dict":
        return isinstance(value, dict)
    if expected_type == "list":
        return isinstance(value, list)
    return False
