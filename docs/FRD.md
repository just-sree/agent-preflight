# Functional Requirements Document

## 1. Overview
`agent-preflight` is an early scaffold providing pre-execution validation primitives for AI agent actions. It acts as a local, lightweight checkpoint to inspect structured payloads before they are passed to execution environments, ensuring basic schema compliance and logging.

## 2. Goals
* Provide a minimal, reproducible interface for validating structured agent actions.
* Enable developers to intercept, inspect, and log tool-call payloads locally.
* Offer a clear allow/block decision mechanism based on public schema definitions.

## 3. Non-Goals
* This project does not execute the actions or tools themselves.
* It does not provide guaranteed security, jailbreak prevention, or compliance certifications.
* It is not a production-grade firewall or a managed proxy service.

## 4. Target Users
* **Solo Developers & Indie Hackers:** Building local agents and needing a simple safety net.
* **Researchers:** Testing autonomous workflows who require a local audit trail.
* **Open-Source Contributors:** Looking for extensible validation primitives for local AI pipelines.

## 5. Core User Stories
* As a developer, I want to validate an action payload before running it so that malformed actions are rejected early.
* As a developer, I want a clear allow/block result so that I can decide whether to execute, retry, or review an action.
* As a maintainer, I want validation events written to a local audit record so that behavior can be inspected later.
* As a contributor, I want small public interfaces so that I can add adapters without understanding private internals.

## 6. Functional Requirements
* **FR-AP-001:** The system must accept a structured action payload (e.g., JSON).
* **FR-AP-002:** The system must validate that required action fields are present according to a provided schema.
* **FR-AP-003:** The system must return a structured validation result containing an allow/block status and reasoning.
* **FR-AP-004:** The system must support configurable, static policy hooks for basic rule-checking.
* **FR-AP-005:** The system must write optional local audit records of the validation event.
* **FR-AP-006:** The CLI must validate a local JSON file to enable quick testing and demonstrations.
* **FR-AP-007:** The package must not require network access for its default operation.
* **FR-AP-008:** The system must optionally validate required action arguments against simple declared types.
* **FR-AP-009:** The audit logger must preserve local metadata in JSON-serializable form.
* **FR-AP-010:** The CLI must optionally load local YAML config for blocked actions, schema mapping, and audit settings.

## 7. Inputs and Outputs
| Component | Input | Output |
| :--- | :--- | :--- |
| **Validator** | `ActionPayload` (JSON/Dict) | `ValidationResult` (Object) |
| **Action Schema** | Schema JSON/Dict | Required argument and type expectations |
| **Config Loader** | YAML file | `PreflightConfig` (Object) |
| **Policy Hook** | `ActionPayload` | `PolicyDecision` (Boolean + Reason) |
| **Audit Logger** | `ActionPayload` + validation outcome | Local File Append (JSONL) |

## 8. CLI Requirements
The CLI will serve as an experimental interface. It must support a `validate` command that accepts a file path to a JSON payload, processes it through the validation primitives, and outputs the result to standard out.

The CLI may optionally accept a local action schema file for required argument and simple type validation. It may also accept a local YAML config file for simple blocked action, schema mapping, and audit settings.

## 9. Configuration Requirements
Configuration is provided through Python objects, CLI flags, or a local YAML file. CLI flags take precedence over config values. No remote configuration fetching is supported.

## 10. Error Handling Requirements
* Malformed JSON inputs must gracefully fail, returning a `ValidationResult`-shaped response with `allowed: false` and a descriptive parser error.
* Invalid YAML config must gracefully fail with a clear runtime/config error.
* Schema mismatches must not raise unhandled exceptions but rather return structured rejection reasons.

## 11. Observability Requirements
Observability is handled entirely locally via the audit logging mechanism. Each run should optionally emit a structured log containing the timestamp, action type, and outcome.

Audit metadata is shallow-copied and converted to JSON-serializable values before writing.

## 12. Security and Privacy Requirements
* **Local-First:** All validation occurs locally. No payloads are sent to external telemetry servers.
* **No Secrets:** The system assumes payloads do not contain sensitive credentials, and logs them exactly as provided. Users are responsible for masking data before logging.

## 13. Accessibility and Developer Experience
The library should follow a "low-friction" integration pattern. Type hints (Python) and clear docstrings should be provided. Setup should require zero external dependencies beyond standard schema libraries (e.g., Pydantic).

## 14. Milestones
* **M1:** Initial scaffold and CLI interface.
* **M2:** Core Pydantic schema validation.
* **M3:** Local policy hooks and audit logging integration.
* **M4:** Schema-bound action argument validation.
* **M5:** Local YAML config support.

## 15. Open Questions
* When should the audit logger add SQLite support for querying?
* What is the optimal base format for defining custom policy hooks in a public OSS context?
