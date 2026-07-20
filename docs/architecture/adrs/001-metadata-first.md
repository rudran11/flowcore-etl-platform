# ADR-001: Metadata First

## Status
Accepted

## Context
FlowCore needs to scale to thousands of pipelines across disparate organizational teams. Hardcoding pipeline definitions creates sprawl, duplication, and makes enterprise auditing impossible.

## Decision
All pipeline executions, platform configurations, and plugin registries will be strictly driven by a logical metadata model. The execution engine will possess no business logic regarding data extraction or transformation. 

## Consequences
- **Positive:** Enables centralized governance, automated lineage tracking, and strict security isolation.
- **Negative:** Introduces a learning curve for engineers accustomed to writing raw Python scripts for ETL.

## Alternatives Rejected
- Allowing imperative Python scripts to bypass the metadata definitions (Rejected because it breaks auditability and sandbox isolation).
