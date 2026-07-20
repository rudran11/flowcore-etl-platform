# ADR-004: Selection of Pydantic V2 for Validation

## Status
Accepted

## Context
FlowCore relies on a strict logical metadata model representing thousands of pipelines, connectors, and execution states. We must validate these schemas extensively both at runtime (parsing DSL) and in the Server API payloads. We evaluated Python `dataclasses`, `marshmallow`, and `pydantic`.

## Decision
We have selected **Pydantic V2** as the foundational schema and validation library for all FlowCore metadata models.

## Consequences
- **Positive:** Pydantic V2 provides Rust-backed, highly performant JSON serialization and deserialization. It supports automatic JSONSchema generation (useful for Studio UI and API specs), and its strict type coercion aligns perfectly with FlowCore's requirement for rigorous configuration validation.
- **Negative:** Pydantic introduces a large dependency footprint into the `shared` module and mandates specific syntax (`ConfigDict`, `Field`) that developers must learn.

## Alternatives Rejected
- **Standard Library `dataclasses`:** Rejected because they lack out-of-the-box recursive validation and JSONSchema export.
- **Marshmallow:** Rejected due to performance overhead and verbosity compared to modern Pydantic V2 class definitions.
