from typing import Any

from pydantic import BaseModel, Field

from agent_preflight.models import ValidationResult


class ValidationReport(BaseModel):
    allowed: bool
    action_name: str
    reason: str
    audit_id: str | None = None
    policy_name: str | None = None
    output_version: str = "0.5"
    metadata: dict[str, Any] = Field(default_factory=dict)


def build_validation_report(result: ValidationResult) -> ValidationReport:
    policy_name = (
        result.policy_decision.policy_name
        if result.policy_decision is not None
        else None
    )

    return ValidationReport(
        allowed=result.allowed,
        action_name=result.action_name,
        reason=result.reason,
        audit_id=result.audit_id,
        policy_name=policy_name,
    )
