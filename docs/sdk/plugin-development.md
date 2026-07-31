# Plugin Development Guide

This guide walks you through scaffolding, developing, and running a custom FlowCore plugin.

## 1. Scaffolding a Plugin

FlowCore includes a robust CLI to automatically generate boilerplate for your plugins.

```bash
# Generate a new Source Plugin
flowcore plugin init my-custom-source --type source
```

This will create a new directory `my-custom-source` containing:
- `pyproject.toml` with the entry point configured.
- `my_custom_source/plugin.py` containing a template `SourcePlugin`.
- Sample tests and a README.

## 2. Implementing the Contract

Open `my_custom_source/plugin.py` and implement the abstract methods from `SourcePlugin` (or `DestinationPlugin` / `TransformPlugin`):

- **`metadata`**: Return a strictly typed `PluginMetadata` object describing your plugin.
- **`check()`**: Validate API keys, ping databases, and ensure the configuration is correct.
- **`discover()`**: Return the schemas of the data streams you can extract.
- **`read()`**: Yield `FlowCoreMessage` objects containing your extracted data and incremental state.

## 3. Local Installation

To make the plugin available to the FlowCore engine, install it locally into the same Python environment using pip's editable mode:

```bash
cd my-custom-source
pip install -e .
```

Restart your backend server, and the PluginManager will discover your plugin!
