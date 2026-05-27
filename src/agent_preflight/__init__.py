"""agent-preflight: Local pre-execution validation for structured agent actions."""

from agent_preflight.audit import AuditWriter, SQLiteAuditWriter
from agent_preflight.config import AuditConfig, PreflightConfig, load_preflight_config
from agent_preflight.executor import ActionExecutor
from agent_preflight.models import (
    ActionPayload,
    AuditRecord,
    ExecutionResult,
    PolicyDecision,
    ValidationResult,
)
from agent_preflight.policy import BasePolicy, BlockActionNamesPolicy
from agent_preflight.reports import ValidationReport, build_validation_report
from agent_preflight.schemas import (
    ActionSchema,
    load_action_schema,
    validate_argument_type,
)
from agent_preflight.validator import ActionValidator

__version__ = "0.7.0"

__all__ = [
    "ActionPayload",
    "AuditRecord",
    "PolicyDecision",
    "ValidationResult",
    "ExecutionResult",
    "ActionSchema",
    "ValidationReport",
    "ActionValidator",
    "ActionExecutor",
    "BasePolicy",
    "BlockActionNamesPolicy",
    "AuditWriter",
    "SQLiteAuditWriter",
    "AuditConfig",
    "PreflightConfig",
    "load_preflight_config",
    "load_action_schema",
    "validate_argument_type",
    "build_validation_report",
]
