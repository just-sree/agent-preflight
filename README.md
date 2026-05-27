# agent-preflight

[![CI](https://github.com/just-sree/agent-preflight/actions/workflows/ci.yml/badge.svg)](https://github.com/just-sree/agent-preflight/actions/workflows/ci.yml)
[![License](https://img.shields.io/badge/License-Apache_2.0-blue.svg)](https://opensource.org/licenses/LICENSE-2.0)

A tiny local Python package for validating structured agent actions before execution.

## Quickstart

```bash
pip install -e .
agent-preflight validate examples/allowed_action.json
agent-preflight validate examples/blocked_action.json --block-action delete_rows
agent-preflight validate examples/allowed_action.json --audit-log .agent-preflight/audit.jsonl
agent-preflight validate examples/allowed_action.json --schema examples/action_schema.json
agent-preflight validate examples/blocked_action.json --config examples/preflight.yml
```

## Schema-bound validation

`agent-preflight` can validate action arguments against a small JSON schema.

```bash
agent-preflight validate examples/allowed_action.json --schema examples/action_schema.json
agent-preflight validate examples/invalid_missing_argument.json --schema examples/action_schema.json
agent-preflight validate examples/invalid_wrong_type.json --schema examples/action_schema.json
```

Example schema:

```json
{
  "action_name": "lookup_user",
  "required_arguments": {
    "user_id": "str"
  }
}
```

This is intentionally small and local-first. It is not a full policy engine or production security layer.

## Config file

`agent-preflight` can load simple YAML config for local validation.

```bash
agent-preflight validate examples/blocked_action.json --config examples/preflight.yml
```

Example:

```yaml
blocked_actions:
  - delete_rows

schemas:
  lookup_user: examples/action_schema.json

audit:
  enabled: true
  path: .agent-preflight/audit.jsonl
```

CLI flags override config values.

## Current Scope

This early version supports:

* structured action payloads
* required-field validation
* schema-bound argument validation
* YAML config files
* simple action-name blocking
* JSONL audit records
* local CLI usage

## Not Included Yet

* framework integrations
* advanced policy evaluation
* risk scoring
* SQL validation
* model calls
* remote services
* production security guarantees

## License

This project is licensed under the Apache License, Version 2.0 - see the [LICENSE](LICENSE) file for details.

## Documentation

- [Functional Requirements Document](docs/FRD.md)
- [Technical Design Document](docs/TDD.md)

