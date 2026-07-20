# Changelog

All notable changes to this project will be documented in this file.
The format is based on Keep a Changelog, and this project adheres to Semantic Versioning.

## [0.6.0] - 2026-07-20
### Added
- **Developer Experience (CLI)**
  - `flowcore init` to scaffold new projects.
  - `flowcore doctor` to diagnose environment and server health.
  - `flowcore validate` for strict DAG schema, graph cycle, and plugin validation.
  - `flowcore run` for seamless offline pipeline execution via the embedded Engine.
  - `flowcore run --remote` for pushing execution to a remote FlowCore server.
  - `FlowCoreClient` built over `httpx` to abstract communication.
  - Beautiful Rich CLI UX with live spinners and syntax highlighting.
  - Architectural AST validation testing suite.

## [Unreleased]
- Initial repository scaffolding.
