# Milestone 6 Certified: Developer Experience (CLI)

The FlowCore CLI provides developers with an exceptional local and remote execution experience. This document certifies the completion, testing, and production-readiness of the CLI architecture in `v0.6.0`.

## 1. Architecture Overview

The FlowCore CLI (`flowcore_cli`) operates as a lightweight front-end wrapping the underlying `flowcore_engine` and `flowcore_shared` packages.

### Design Principles
- **Local-First Execution**: Developers can validate and execute pipelines entirely offline using the local engine and plugin manager.
- **Strict Boundary Enforcement**: The CLI is forbidden from importing server-side persistence modules (SQLAlchemy, Repositories). It treats the server strictly as an HTTP API.
- **Single-Responsibility Client**: All remote operations route through the `FlowCoreClient` (`api.py`), keeping command definitions concise and avoiding raw `httpx` pollution.

## 2. Command Matrix

The following commands are available in `v0.6.0`:

| Command            | Status   | Description                                           |
| ------------------ | -------- | ----------------------------------------------------- |
| `init`             | ✅        | Scaffolds a new FlowCore project                      |
| `doctor`           | ✅        | Validates the local environment and server connection |
| `validate`         | ✅        | Statically analyzes a YAML pipeline definition        |
| `validate --dry-run`| ✅      | Renders the topological dependency graph              |
| `run`              | ✅        | Executes the pipeline locally                         |
| `run --remote`     | ✅        | Executes the pipeline on the FlowCore Server          |
| `--version`        | ✅        | Prints the CLI version                                |
| `--help`           | ✅        | Displays Typer documentation                          |
| `push`             | Deferred | Deferring until server API enhancements               |
| `pull`             | Deferred | Deferring until server API enhancements               |

## 3. Testing & Certification Summary

- **End-to-End Test Suite**: Complete coverage mapping 1-to-1 with the Command Matrix.
- **AST Architecture Validation**: Dynamic AST-parsing ensures no command logic attempts direct ORM imports or rogue HTTP calls.
- **Stress Tested**: Successfully completed 25 consecutive localized runs and 25 consecutive remote executions with zero thread leakage, proving the ThreadPoolExecutor shutdown patterns are airtight.
- **Startup Performance**: Validated `<500ms` boot times for standard commands.

## 4. Known Limitations & Roadmap

- **Push/Pull Commands**: Deferred until Milestone X (Server API Enhancements), which will introduce `POST /api/v1/pipelines` and `GET /api/v1/pipelines/{pipeline_id}`.
- **WebSockets / SSE**: The `--remote` execution currently polls the server every 500ms. In a future milestone, this will transition to WebSocket subscriptions for instantaneous state synchronization.
