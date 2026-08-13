# Milestone 16: Pipeline Live Preview System

## Overview

The live preview system provides users with an instant execution environment to observe how data transformations behave inside the browser before committing their pipeline to production. Unlike a static mock or external simulator, this system deeply integrates with FlowCore's real execution engine, extracting state natively via interceptors.

## Key Technical Decisions & Architecture

1. **True Engine Re-Use via Interceptors**
   - Instead of building a secondary "preview" executor, the real `ExecutionEngine` is used to run the pipeline exactly as it would in production.
   - We introduced an `intercepting_generator` within the engine's worker threads. This safely captures records as they are yielded between steps, appending them directly to the in-memory execution state up to a specified bound.

2. **Graph Pruning (Upstream Traversal)**
   - When a user selects a node to preview, we perform a reverse post-order traversal to compute the precise subset of the DAG that needs to run. 
   - Unrelated branches are never instantiated or executed, keeping latency and resource overhead minimal.

3. **Production Isolation & Security (Destinations)**
   - The preview system executes without writing to the `ExecutionRun` database, eliminating garbage state in the production schema.
   - Crucially, destination nodes are structurally pruned. If a user tries to preview a destination connector, the execution is blocked to prevent accidental writes or destructive operations in preview mode.

4. **Resource Constraints**
   - Preview executions are bounded heavily. A `PreviewExecutionContext` propagates through all executing plugins.
   - We enforce a default maximum record ceiling (e.g. 50 records) and a strict 15-second `asyncio.wait_for` timeout envelope to prevent unbounded background hanging if a plugin misbehaves.

5. **Robust Error Propagation**
   - We surfaced full native execution stack traces directly to the API level.
   - The system intercepts `ExecutionState.FAILED` statuses seamlessly and propagates them dynamically to the UI, allowing engineers to visualize misconfigurations immediately without checking backend server logs.

## Implemented Components

### Backend
- **Execution Service (`execution_service.py`)**: Implements graph pruning, dependency isolation, and preview bounds. Handles `preview_execution`.
- **Engine Modifications (`engine.py`)**: Enhanced worker execution. Yields intercepted metrics and state back to the Pydantic run structures natively across thread boundaries.
- **Preview Context (`models.py`, `manager.py`)**: Centralized `PreviewExecutionContext` to share cancellation events and limits globally.
- **Filter Fallback (`filter.py`)**: Integrated string-regex fallback to accommodate simple UI inputs dynamically without crashing.

### Frontend
- **Preview Panel Component (`PreviewPanel.tsx`)**: Reconstructed to display detailed data grids, execution metrics, and dynamically extracted schema JSONs.
- **Pipeline API (`pipelinesApi.ts`)**: Wired up `previewPipeline` REST endpoint, integrated API contracts.

## Verification
- Local verification tests passed for complex multi-node preview cases.
- Validated state extraction correctly yields both incoming dependencies and the node's output schema natively.
- Tested failure states correctly mapping to the frontend error handler.

**Status:** Completed & Approved ✅
