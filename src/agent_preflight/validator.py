from typing import Any

from pydantic import ValidationError

from agent_preflight.audit import AuditWriter
from agent_preflight.models import ActionPayload, ValidationResult
from agent_preflight.policy import BasePolicy


class ActionValidator:
    def __init__(
        self,
        policy: BasePolicy | None = None,
        audit_writer: AuditWriter | None = None,
    ):
        self.policy = policy
        self.audit_writer = audit_writer

    def validate(self, payload: ActionPayload | dict[str, Any]) -> ValidationResult:
        try:
            action_payload = (
                payload
                if isinstance(payload, ActionPayload)
                else ActionPayload.model_validate(payload)
            )
        except ValidationError:
            return ValidationResult(
                allowed=False,
                action_name="<invalid>",
                reason="Invalid action payload",
            )

        policy_decision = (
            self.policy.evaluate(action_payload)
            if self.policy is not None
            else None
        )
        allowed = policy_decision.allowed if policy_decision is not None else True
        reason = (
            policy_decision.reason
            if policy_decision is not None
            else "Allowed by default"
        )

        result = ValidationResult(
            allowed=allowed,
            action_name=action_payload.action_name,
            reason=reason,
            policy_decision=policy_decision,
        )

        if self.audit_writer is not None:
            result.audit_id = self.audit_writer.write(action_payload, allowed, reason)

        return result
