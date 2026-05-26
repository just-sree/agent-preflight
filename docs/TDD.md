# Technical Design Document

## 1. Overview
This document outlines the technical architecture for the `agent-preflight` early scaffold. The system is designed as a local middleware layer to parse, validate, and log AI agent action proposals before they reach an execution layer.

## 2. Design Principles
* **Offline-First:** No reliance on network APIs for validation.
* **Extensible:** Simple interfaces allowing users to inject custom schemas.
* **Stateless Validation:** Each payload is evaluated in isolation.

## 3. System Boundaries
`agent-preflight` operates strictly between the AI agent's generation step and the execution environment. It does not generate payloads, nor does it execute them.

## 4. High-Level Architecture
```text
CLI / Python API
   ↓
ActionPayload parser
   ↓
Validator
   ↓
Policy hook
   ↓
ValidationResult
   ↓
Optional AuditWriter
```

## 5. Package Structure

```text
src/agent_preflight/
  __init__.py
  cli.py
  models.py
  validator.py
  policy.py
  audit.py
tests/
  test_models.py
  test_validator.py
  test_cli.py
docs/
  FRD.md
  TDD.md
```

## 6. Core Data Models

* `ActionPayload`: Represents the incoming unverified tool or action request.
* `ValidationResult`: Contains the boolean `allowed` flag, `reason`, and a unique identifier.
* `PolicyDecision`: The intermediate output from a policy hook evaluating a specific rule.
* `AuditRecord`: The serialized record combining the payload and the result for local storage.

## 7. Main Components

* **Parser:** Deserializes incoming string/JSON data into an `ActionPayload`.
* **Validator Core:** Orchestrates the checks against provided Pydantic schemas.
* **Policy Engine:** Iterates over configured `policy hooks` to apply static checks (e.g., blocked action names).

## 8. Control Flow

1. API/CLI receives raw data.
2. Parser attempts to structure the data; fails fast if malformed.
3. Validator cross-references the payload with the target schema.
4. Policy hooks evaluate the action intent.
5. A `ValidationResult` is generated.
6. The event is written to local storage via the `AuditWriter`.
7. The result is returned to the caller.

## 9. Storage Design

Storage is restricted to local audit logs. The initial implementation will support a simple append-only local file (e.g., SQLite or JSONL), configurable by the user.

## 10. Configuration Design

Configuration is handled via a `PreflightConfig` object, which can be instantiated via code or loaded from a local YAML file.

## 11. CLI Design

Built with a standard Python CLI library (e.g., Typer or Click).
Command pattern: `agent-preflight validate --payload <path_to_json> --config <path_to_yaml>`

## 12. Testing Strategy

* **Unit Tests:** `pytest` covering model validation, parser edge cases, and individual policy hooks.
* **CLI Tests:** Subprocess tests verifying standard out and exit codes.

## 13. Failure Modes

* **Invalid Schema:** Validator returns `allowed: false`.
* **Corrupt Audit Log:** The system should log an error to `stderr` but still return the validation result to avoid blocking the critical path.

## 14. Security and Privacy Considerations

This is a non-production scaffold. It relies on the host environment's security for file access (audit logs). It does not sanitize inputs for database injection, as its primary role is structural validation, not execution security.

## 15. Extensibility

The `policy.py` module defines an abstract base class `BasePolicyHook`, allowing developers to subclass and register their own pre-execution checks.

## 16. Deferred Work

* Complex stateful validation (e.g., checking if action B is allowed after action A).
* Native dashboard or complex query interfaces for the audit log.

## 17. Open Questions

* How strict should type coercion be during the parsing phase?
