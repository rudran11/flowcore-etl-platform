# ADR-005: ExecutionState Evolution

## Status
Approved

## Context
During Milestone 2, the `ExecutionState` enumeration was defined broadly with the following values: `PENDING`, `INITIALIZING`, `RUNNING`, `SUCCESS`, `FAILED`, `CANCELLED`. 
As we transitioned to Milestone 3 (Execution Engine), it became apparent that these states were insufficiently granular to safely manage the execution lifecycle of complex directed acyclic graphs (DAGs) and plugins.

## Decision
We have evolved the `ExecutionState` enumeration to the following precise values: `PENDING`, `QUEUED`, `RUNNING`, `RETRYING`, `FAILED`, `CANCELLED`, `COMPLETED`.

### Why additional runtime states are required
The engine relies on a strict state machine to prevent illegal transitions (e.g., preventing a cancelled job from restarting). A richer vocabulary allows the `StateManager` to accurately reflect the internal phase of execution.

### Why INITIALIZING becomes QUEUED
`INITIALIZING` implies active work by the engine. However, in our asynchronous DAG execution model, steps that have had their context hydrated but are waiting for compute resources (thread/process availability) are technically idle. `QUEUED` accurately describes a unit of work that is ready but blocked on system resources.

### Why SUCCESS becomes COMPLETED
`SUCCESS` implies a binary positive outcome. `COMPLETED` is a more robust lifecycle term that signifies the engine has fully finished the finalization and teardown phases of the step, regardless of whether it yielded data. This aligns with standard workflow orchestration terminology.

### Why RETRYING is introduced
Transient failures (like network timeouts) are handled by the `RetryManager`. Without a `RETRYING` state, a step would ping-pong between `FAILED` and `RUNNING`, artificially polluting the audit logs. `RETRYING` acts as a distinct holding state during backoff sleep periods.

## Consequences
- **Metadata Models:** `ExecutionRun` and `ExecutionStep` naturally inherit this new granularity without database schema changes since they rely on the same Enum.
- **Audit Logs:** Operational telemetry will now differentiate between actual failures and retry delays.
- **Engine Logic:** The ExecutionCoordinator can now safely enforce terminal transitions, completely eliminating zombie processes or out-of-order execution bugs.
