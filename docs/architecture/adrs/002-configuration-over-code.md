# ADR-002: Configuration over Code

## Status
Accepted

## Context
Data engineering teams spend the majority of their time writing boilerplate integration code. When a source schema changes, code must be refactored, recompiled, and redeployed.

## Decision
FlowCore will adopt a strict 'Configuration over Code' philosophy. Pipelines are defined using a declarative DSL (Domain Specific Language) in YAML or JSON format, rather than procedural programming languages.

## Consequences
- **Positive:** Reduces time-to-market for new pipelines, allows non-engineers to define data flows, and prevents code rot.
- **Negative:** The DSL schema parser must be extraordinarily robust to handle edge cases that procedural code would normally handle easily.

## Alternatives Rejected
- Providing a Python-based DAG definition similar to Airflow (Rejected because we want a strict separation between execution instructions and metadata definition).
