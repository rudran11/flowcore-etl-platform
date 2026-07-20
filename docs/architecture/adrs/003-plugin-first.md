# ADR-003: Plugin First

## Status
Accepted

## Context
An enterprise ETL platform must connect to hundreds of internal and external data sources. Tightly coupling these connectors to the core execution engine prevents the engine from scaling securely and makes platform releases dangerously brittle.

## Decision
The core execution engine will be implemented using a Microkernel architecture. All data sources, sinks, and complex transformations will be externalized as Plugins. 

## Consequences
- **Positive:** Connectors can be versioned independently of the Engine. A crash in a custom plugin will not take down the entire platform.
- **Negative:** Introduces Inter-Process Communication (IPC) serialization overhead between the engine sandbox and the plugin runtime.

## Alternatives Rejected
- Monolithic engine compiling all internal connectors into the same codebase (Rejected due to vendor lock-in and release bottleneck risks).
