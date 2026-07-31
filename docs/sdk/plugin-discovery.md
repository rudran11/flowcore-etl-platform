# Plugin Discovery Architecture

FlowCore heavily leverages Python's native `importlib.metadata.entry_points` mechanism to securely and dynamically discover installed plugins.

## Discovery Flow

```mermaid
sequenceDiagram
    participant OS as Host Environment
    participant Uvicorn as API Server
    participant PM as PluginManager
    participant Studio as FlowCore Studio

    OS->>Uvicorn: pip install my-custom-source
    Uvicorn->>PM: Server Starts (get_plugin_manager)
    PM->>PM: entry_points(group="flowcore.plugins")
    loop For each Entry Point
        PM->>PM: Load plugin class
        PM->>PM: Validate against PluginMetadata schema
        PM->>PM: Register Plugin
    end
    Studio->>Uvicorn: GET /api/v1/plugins
    Uvicorn-->>Studio: List[PluginMetadata]
```

## Creating an Entry Point

When packaging your plugin, you must declare it in your `pyproject.toml` configuration:

```toml
[project.entry-points."flowcore.plugins"]
my-custom-source = "my_custom_source.plugin:MyCustomSourcePlugin"
```

The FlowCore engine will detect this group upon startup and automatically register the plugin in the UI and engine registries.
