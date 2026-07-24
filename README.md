# FlowCore

Enterprise Metadata-Driven ETL Platform

FlowCore is a next-generation, metadata-driven platform for Extract, Transform, and Load operations in enterprise environments.

> **Current Status**: v0.7.0 - Feature Complete ETL Platform with Visual Studio.

## Architecture

FlowCore is divided into three main components:
1. **Engine & Shared Core (`flowcore_engine`, `flowcore_shared`)**: The standalone execution engine, plugins, and domain schemas.
2. **Server (`flowcore_server`)**: FastAPI-based backend providing REST endpoints, scheduling, and orchestrating execution.
3. **Studio (`flowcore_studio`)**: React/Vite-based modern enterprise frontend with visual pipeline building, scheduling, and execution monitoring.

## Features

- **Metadata First**: Everything is a declarative YAML definition.
- **Visual Builder**: Build complex DAGs via drag and drop, synced bi-directionally with Monaco YAML editor.
- **Enterprise Scheduler**: Advanced scheduling with CRON, interval, retry policies, blackout windows, and holiday calendars.
- **Robust Execution**: Live monitoring, output tracking, error isolation, and detailed run logs.
- **Extensible Plugins**: Plug-and-play architecture for Connectors, Transformers, and custom actions.
