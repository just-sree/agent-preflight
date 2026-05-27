import argparse
import json
from pathlib import Path
import sys

from agent_preflight.audit import AuditWriter, SQLiteAuditWriter
from agent_preflight.config import AUDIT_BACKENDS, PreflightConfig, load_preflight_config
from agent_preflight.models import ValidationResult
from agent_preflight.policy import BlockActionNamesPolicy
from agent_preflight.reports import ValidationReport, build_validation_report
from agent_preflight.schemas import load_action_schema
from agent_preflight.validator import ActionValidator


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="agent-preflight")
    subparsers = parser.add_subparsers(dest="command", required=True)

    validate_parser = subparsers.add_parser(
        "validate",
        help="Validate a structured agent action JSON file.",
    )
    validate_parser.add_argument("json_file")
    validate_parser.add_argument(
        "--block-action",
        action="append",
        default=[],
        help="Action name to block. May be provided more than once.",
    )
    validate_parser.add_argument(
        "--audit-log",
        help="Path to a JSONL audit log.",
    )
    validate_parser.add_argument(
        "--audit-backend",
        help="Audit backend to use.",
    )
    validate_parser.add_argument(
        "--schema",
        help="Path to an action schema JSON file.",
    )
    validate_parser.add_argument(
        "--config",
        help="Path to a local YAML preflight config file.",
    )
    validate_parser.add_argument(
        "--output",
        choices=["json", "text"],
        help="Output format for stdout.",
    )
    validate_parser.add_argument(
        "--report-file",
        help="Path to write a JSON validation report.",
    )

    return parser


def _select_schema_path(
    payload: dict,
    cli_schema_path: str | None,
    config: PreflightConfig,
) -> str | None:
    if cli_schema_path:
        return cli_schema_path

    action_name = payload.get("action_name") if isinstance(payload, dict) else None
    if not isinstance(action_name, str):
        return None

    # TODO: Add config-relative path resolution after the v0.3 CLI contract settles.
    return config.schemas.get(action_name)


def _build_audit_writer(
    audit_path: str | None,
    audit_backend: str,
) -> AuditWriter | SQLiteAuditWriter | None:
    if not audit_path:
        return None

    if audit_backend == "jsonl":
        return AuditWriter(audit_path)
    if audit_backend == "sqlite":
        return SQLiteAuditWriter(audit_path)

    raise ValueError(f"Unknown audit backend: {audit_backend}")


def _format_text_report(report: ValidationReport) -> str:
    return "\n".join(
        [
            f"allowed: {str(report.allowed).lower()}",
            f"action_name: {report.action_name}",
            f"reason: {report.reason}",
            f"audit_id: {report.audit_id if report.audit_id is not None else 'none'}",
        ]
    )


def _write_report_file(report: ValidationReport, path: str) -> None:
    report_path = Path(path)
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(
        json.dumps(report.model_dump(), indent=2) + "\n",
        encoding="utf-8",
    )


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    if args.command != "validate":
        parser.error("unknown command")

    try:
        with open(args.json_file, encoding="utf-8") as payload_file:
            payload = json.load(payload_file)
    except FileNotFoundError as exc:
        print(json.dumps({"error": str(exc)}), file=sys.stderr)
        return 1
    except json.JSONDecodeError as exc:
        result = ValidationResult(
            allowed=False,
            action_name="<invalid>",
            reason=f"Invalid JSON payload: {exc.msg}",
        )
        print(json.dumps(result.model_dump(exclude_none=True), indent=2))
        return 2

    try:
        config = load_preflight_config(args.config) if args.config else PreflightConfig()
        blocked_actions = set(config.blocked_actions) | set(args.block_action)
        policy = (
            BlockActionNamesPolicy(blocked_actions)
            if blocked_actions
            else None
        )
        audit_log_path = (
            args.audit_log
            if args.audit_log
            else config.audit.path
            if config.audit.enabled
            else None
        )
        audit_backend = (
            args.audit_backend
            if args.audit_backend
            else config.audit.backend
            if config.audit.enabled
            else "jsonl"
        )
        audit_writer = _build_audit_writer(audit_log_path, audit_backend)
        schema_path = _select_schema_path(payload, args.schema, config)
        action_schema = load_action_schema(schema_path) if schema_path else None
        validator = ActionValidator(
            policy=policy,
            audit_writer=audit_writer,
            action_schema=action_schema,
        )
        result = validator.validate(payload)
    except Exception as exc:
        print(json.dumps({"error": str(exc)}), file=sys.stderr)
        return 1

    report = build_validation_report(result)

    try:
        if args.report_file:
            _write_report_file(report, args.report_file)
    except Exception as exc:
        print(json.dumps({"error": str(exc)}), file=sys.stderr)
        return 1

    if args.output == "json":
        print(json.dumps(report.model_dump(), indent=2))
    elif args.output == "text":
        print(_format_text_report(report))
    else:
        result_data = result.model_dump(exclude={"policy_decision"}, exclude_none=True)
        print(json.dumps(result_data, indent=2))

    return 0 if result.allowed else 2

if __name__ == "__main__":
    sys.exit(main())
