from collections.abc import Callable
from typing import Any

from agent_preflight.models import ActionPayload, ExecutionResult
from agent_preflight.validator import ActionValidator


class ActionExecutor:
    def __init__(self, validator: ActionValidator | None = None):
        self.validator = validator if validator is not None else ActionValidator()
        self._handlers: dict[str, Callable[[dict[str, Any]], Any]] = {}

    def register(
        self,
        action_name: str,
        handler: Callable[[dict[str, Any]], Any],
    ) -> None:
        if not action_name.strip():
            raise ValueError("action_name must not be empty")
        self._handlers[action_name] = handler

    def run(
        self,
        payload: ActionPayload | dict[str, Any],
        dry_run: bool = True,
    ) -> ExecutionResult:
        validation_result = self.validator.validate(payload)
        action_name = validation_result.action_name

        if not validation_result.allowed:
            return ExecutionResult(
                allowed=False,
                executed=False,
                action_name=action_name,
                reason=validation_result.reason,
                audit_id=validation_result.audit_id,
            )

        action_payload = (
            payload
            if isinstance(payload, ActionPayload)
            else ActionPayload.model_validate(payload)
        )

        if dry_run:
            return ExecutionResult(
                allowed=True,
                executed=False,
                action_name=action_payload.action_name,
                reason="Dry run: action validated but not executed",
                audit_id=validation_result.audit_id,
            )

        handler = self._handlers.get(action_payload.action_name)
        if handler is None:
            return ExecutionResult(
                allowed=True,
                executed=False,
                action_name=action_payload.action_name,
                reason="No handler registered for action",
                audit_id=validation_result.audit_id,
            )

        try:
            output = handler(action_payload.arguments)
        except Exception as exc:
            return ExecutionResult(
                allowed=True,
                executed=False,
                action_name=action_payload.action_name,
                reason="Handler execution failed",
                error=str(exc),
                audit_id=validation_result.audit_id,
            )

        return ExecutionResult(
            allowed=True,
            executed=True,
            action_name=action_payload.action_name,
            reason="Action executed",
            output=output,
            audit_id=validation_result.audit_id,
        )
