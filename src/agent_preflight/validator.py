from typing import Any
import sys

from pydantic import ValidationError

from agent_preflight.audit import AuditWriter
from agent_preflight.models import ActionPayload, ValidationResult
from agent_preflight.policy import BasePolicy
from agent_preflight.schemas import ActionSchema, validate_argument_type


class ActionValidator:
    """Validate one structured action payload without executing it."""

    def __init__(
        self,
        policy: BasePolicy | None = None,
        audit_writer: AuditWriter | None = None,
        action_schema: ActionSchema | None = None,
    ):
        self.policy = policy
        self.audit_writer = audit_writer
        self.action_schema = action_schema

    def validate(self, payload: ActionPayload | dict[str, Any]) -> ValidationResult:
        """Return an allow/block result for an action payload."""
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

        if self.action_schema is not None:
            schema_result = self._validate_schema(action_payload)
            if schema_result is not None:
                self._write_audit(action_payload, schema_result)
                return schema_result

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

        self._write_audit(action_payload, result)
        return result

    def _validate_schema(self, payload: ActionPayload) -> ValidationResult | None:
        if self.action_schema is None:
            return None

        if payload.action_name != self.action_schema.action_name:
            return ValidationResult(
                allowed=False,
                action_name=payload.action_name,
                reason="Action name does not match schema",
            )

        for argument_name, expected_type in self.action_schema.required_arguments.items():
            if argument_name not in payload.arguments:
                return ValidationResult(
                    allowed=False,
                    action_name=payload.action_name,
                    reason=f"Missing required argument: {argument_name}",
                )

            if not validate_argument_type(payload.arguments[argument_name], expected_type):
                return ValidationResult(
                    allowed=False,
                    action_name=payload.action_name,
                    reason=(
                        f"Invalid type for argument {argument_name}: "
                        f"expected {expected_type}"
                    ),
                )

        for argument_name, expected_type in self.action_schema.optional_arguments.items():
            if argument_name not in payload.arguments:
                continue

            if not validate_argument_type(payload.arguments[argument_name], expected_type):
                return ValidationResult(
                    allowed=False,
                    action_name=payload.action_name,
                    reason=(
                        f"Invalid type for argument {argument_name}: "
                        f"expected {expected_type}"
                    ),
                )

        return None

    def _write_audit(
        self,
        action_payload: ActionPayload,
        result: ValidationResult,
    ) -> None:
        if self.audit_writer is not None:
            try:
                result.audit_id = self.audit_writer.write(
                    action_payload,
                    result.allowed,
                    result.reason,
                )
            except Exception as exc:
                print(f"Failed to write audit record: {exc}", file=sys.stderr)
