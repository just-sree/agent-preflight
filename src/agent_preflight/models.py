from typing import Any

from pydantic import BaseModel, Field, field_validator


class ActionPayload(BaseModel):
    action_name: str
    arguments: dict[str, Any] = Field(default_factory=dict)
    metadata: dict[str, Any] = Field(default_factory=dict)

    @field_validator("action_name")
    @classmethod
    def action_name_must_not_be_empty(cls, value: str) -> str:
        if not value.strip():
            raise ValueError("action_name must not be empty")
        return value


class PolicyDecision(BaseModel):
    allowed: bool
    reason: str
    policy_name: str = "default"


class ValidationResult(BaseModel):
    allowed: bool
    action_name: str
    reason: str
    policy_decision: PolicyDecision | None = None
    audit_id: str | None = None


class AuditRecord(BaseModel):
    audit_id: str
    timestamp_utc: str
    action_name: str
    allowed: bool
    reason: str
    metadata: dict[str, Any] = Field(default_factory=dict)


class ExecutionResult(BaseModel):
    allowed: bool
    executed: bool
    action_name: str
    reason: str
    output: Any | None = None
    error: str | None = None
    audit_id: str | None = None
