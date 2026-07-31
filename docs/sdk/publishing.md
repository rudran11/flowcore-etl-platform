# Publishing Plugins

Once your plugin is fully implemented and tested, you can share it with the broader FlowCore community or keep it private within your organization.

## Validation and Testing

Before packaging your plugin, ensure it adheres strictly to the FlowCore SDK contracts. FlowCore provides a built-in testing utility to automatically run an assertion suite against your plugin.

```bash
# Test the plugin contract compliance
flowcore plugin test my-custom-source
```

This will instantiate your plugin and ensure that:
1. `metadata` returns a valid `PluginMetadata` instance.
2. The plugin implements the correct BaseClass (`SourcePlugin`, `DestinationPlugin`, or `TransformPlugin`).
3. (Optional) Run user-defined unit tests if available in the `tests/` directory.

## PyPI Publishing

FlowCore plugins are standard Python packages. You can build and publish them using traditional tools like `build` and `twine`.

```bash
# 1. Build the distribution wheel
python -m build

# 2. Upload to PyPI (or a private repository)
twine upload dist/*
```

Because of the `entry_points` architecture, any FlowCore user can now install your plugin simply by running `pip install your-plugin-package` and restarting their FlowCore server.
