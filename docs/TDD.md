# Technical Design Document

## 1. Overview
This document outlines the technical architecture for the `agent-preflight` early scaffold. The system is designed as a local middleware layer to parse, validate, and log AI agent action proposals before they reach an execution layer.

## 2. Design Principles
* **Offline-First:** No reliance on network APIs for validation.
* **Extensible:** Simple interfaces allowing users to inject custom policy hooks.
* **Stateless Validation:** Each payload is evaluated in isolation.

## 3. System Boundaries
`agent-preflight` operates strictly between the AI agent's generation step and the execution environment. It does not generate payloads, nor does it execute them.

## 4. High-Level Architecture
```text
CLI / Python API
   |
ActionPayload parser
   |
Validator
   |
Policy hook
   |
ValidationResult
   |
Optional AuditWriter
```

## 5. Package Structure

```text
src/agent_preflight/
  __init__.py
  cli.py
  config.py
  models.py
  reports.py
  schemas.py
  validator.py
  policy.py
  audit.py
examples/
  allowed_action.json
  blocked_action.json
  preflight.yml
tests/
  test_config.py
  test_models.py
  test_validator.py
  test_policy.py
  test_audit.py
  test_cli.py
docs/
  FRD.md
  TDD.md
```

## 6. Core Data Models

* `ActionPayload`: Represents the incoming unverified tool or action request.
* `ActionSchema`: Represents optional per-action argument requirements and simple expected types.
* `PreflightConfig`: Represents optional local YAML config for blocked actions, schema mapping, and audit settings.
* `ValidationResult`: Contains the boolean `allowed` flag, `action_name`, `reason`, optional policy decision, and optional audit identifier.
* `ValidationReport`: Represents the stable public report schema for CLI and automation output.
* `PolicyDecision`: The intermediate output from a policy hook evaluating a specific rule.
* `AuditRecord`: The serialized record combining the action name, outcome, reason, timestamp, audit ID, and metadata for local storage.

## 7. Main Components

* **Parser:** Deserializes incoming JSON data into an `ActionPayload`.
* **Config Loader:** Deserializes local YAML config into a `PreflightConfig`.
* **Schema Loader:** Deserializes local schema JSON into an `ActionSchema`.
* **Validator Core:** Orchestrates Pydantic payload validation, optional action schema validation, optional policy evaluation, and optional audit writing.
* **Report Builder:** Converts a `ValidationResult` into a stable `ValidationReport`.
* **Policy Hook:** Applies one configured static policy check, such as blocked action names. Multi-policy orchestration is deferred.
* **Audit Writer:** Appends validation records to a local JSONL file.
* **SQLite Audit Writer:** Writes validation records to a local SQLite database.

## 8. Control Flow

1. API/CLI receives raw data.
2. Parser attempts to structure the data; malformed inputs become structured rejections.
3. If configured, the CLI loads local YAML config.
4. Validator validates the payload against the `ActionPayload` schema.
5. If configured, the action schema validates the action name, required arguments, and simple argument types.
6. The optional policy hook evaluates the action intent.
7. A `ValidationResult` is generated.
8. If configured, the event is written to local storage via the `AuditWriter`.
9. If requested, a `ValidationReport` is generated for stdout and/or file output.
10. The result is returned to the caller.

## 9. Storage Design

Storage is restricted to optional local audit logs. The implementation supports append-only JSONL and SQLite, configurable by the user through code, config, or CLI flags.

Audit metadata is shallow-copied. Metadata values that cannot be serialized as JSON are replaced with their string representation before being written.

SQLite storage uses a single `audit_records` table with one row per validation event. It stores metadata as a JSON string and does not use SQLAlchemy.

## 10. Configuration Design

Configuration is intentionally small. `PreflightConfig` can be loaded from local YAML and supports blocked actions, schema path mappings by action name, and audit settings. Audit backend values are limited to `jsonl` and `sqlite`. Schema paths inside config are resolved relative to the current working directory.

## 11. CLI Design

Built with the standard library `argparse` module.

Command pattern:

```bash
agent-preflight validate <path_to_json> [--config <path>] [--schema <path>] [--block-action <name>] [--audit-backend <jsonl|sqlite>] [--audit-log <path>] [--output <json|text>] [--report-file <path>]
```

`ValidationReport` output is a stable public integration surface for local automation, CI checks, and future framework adapters. Reports do not include raw payload arguments by default.

Exit codes:

* `0` when validation allows the action.
* `2` when validation blocks or rejects the action.
* `1` for file or runtime errors that prevent validation.

## 12. Testing Strategy

* **Unit Tests:** `pytest` covering model validation, parser edge cases, audit writing, and individual policy hooks.
* **CLI Tests:** Tests verifying standard out and exit codes through the CLI entry point.

## 13. Failure Modes

* **Invalid Schema:** Validator returns `allowed: false`.
* **Schema Mismatch:** Validator returns `allowed: false` with a stable reason such as a missing required argument or invalid argument type.
* **Malformed JSON:** CLI returns a `ValidationResult`-shaped rejection.
* **Invalid Config:** CLI exits with code `1` and writes an error to `stderr`.
* **Unknown Audit Backend:** CLI exits with code `1` and writes an error to `stderr`.
* **Audit Write Failure:** The system logs an error to `stderr` but still returns the validation result to avoid blocking the critical path.

## 14. Security and Privacy Considerations

This is a non-production scaffold. It relies on the host environment's security for file access. It does not sanitize inputs for execution security, as its primary role is structural validation, not action execution.

## 15. Extensibility

The `policy.py` module defines a small `BasePolicy` class, allowing developers to subclass and inject their own pre-execution checks.

## 16. Deferred Work

* Config-relative path resolution.
* Multiple policy orchestration.
* Framework integrations.
* Complex stateful validation, such as checking whether action B is allowed after action A.
* Native dashboard or complex query interfaces for the audit log.

## 17. Open Questions

* How strict should type coercion be during the parsing phase?
