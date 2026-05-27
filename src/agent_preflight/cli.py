import argparse
import json
import sys

from agent_preflight.audit import AuditWriter
from agent_preflight.models import ValidationResult
from agent_preflight.policy import BlockActionNamesPolicy
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

    return parser


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
        policy = (
            BlockActionNamesPolicy(set(args.block_action))
            if args.block_action
            else None
        )
        audit_writer = AuditWriter(args.audit_log) if args.audit_log else None
        validator = ActionValidator(policy=policy, audit_writer=audit_writer)
        result = validator.validate(payload)
    except Exception as exc:
        print(json.dumps({"error": str(exc)}), file=sys.stderr)
        return 1

    result_data = result.model_dump(exclude={"policy_decision"}, exclude_none=True)
    print(json.dumps(result_data, indent=2))
    return 0 if result.allowed else 2

if __name__ == "__main__":
    sys.exit(main())
