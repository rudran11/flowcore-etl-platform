# FlowCore Connector SDK Overview

The FlowCore Connector SDK is a set of abstractions that allows developers to easily create and integrate custom data sources, destinations, and transformations into the FlowCore ETL Platform.

## Architecture

The SDK is designed around a strictly typed component architecture:

- **SourcePlugin**: Extracts data from an external system.
- **DestinationPlugin**: Loads data into an external system.
- **TransformPlugin**: Mutates data in-flight between sources and destinations.

These plugins communicate with the engine using a unified message format called the `FlowCoreMessage`, ensuring decoupling between the execution environment (FlowCore Engine) and the connector implementations.

## Plugin Capabilities

Plugins advertise their features to the engine using `ConnectorCapabilities`. For example, a source plugin might declare that it supports incremental synchronization (`supports_incremental=True`). The engine dynamically alters its execution strategy based on these declared capabilities.

## Plugin Hub Integration

All compliant plugins are automatically discovered and displayed in the FlowCore Studio Plugin Hub. By using Python's standard `entry_points` mechanism, installing a plugin into the environment is all that's required to make it available to your pipelines.
