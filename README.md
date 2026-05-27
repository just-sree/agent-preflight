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
```

## Current Scope

This early version supports:

* structured action payloads
* required-field validation
* simple action-name blocking
* JSONL audit records
* local CLI usage

## Not Included Yet

* framework integrations
* advanced policy evaluation
* model calls
* remote services
* production security guarantees

## License

This project is licensed under the Apache License, Version 2.0 - see the [LICENSE](LICENSE) file for details.

## Documentation

- [Functional Requirements Document](docs/FRD.md)
- [Technical Design Document](docs/TDD.md)

