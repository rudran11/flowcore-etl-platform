# Copyright (c) 2026 Rudran
# Licensed under the MIT License.
# See LICENSE file in the project root for full license information.

import typer
from rich.console import Console
from pathlib import Path
from enum import Enum
import json
import textwrap

app = typer.Typer(help="Manage FlowCore plugins (Source, Destination, Transform)")
console = Console()

class PluginType(str, Enum):
    source = "source"
    destination = "destination"
    transform = "transform"

@app.command("init")
def plugin_init(
    name: str = typer.Argument(..., help="The name of the plugin (e.g., source-stripe, destination-postgres)"),
    plugin_type: PluginType = typer.Option(..., "--type", "-t", help="Type of plugin: source, destination, or transform"),
    author: str = typer.Option("FlowCore Developer", "--author", "-a", help="Author of the plugin"),
    directory: Path = typer.Option(Path("."), "--dir", "-d", help="Directory to scaffold the plugin in")
):
    """Scaffold a new FlowCore plugin."""
    plugin_dir = directory / name
    
    if plugin_dir.exists():
        console.print(f"[bold red]Error:[/] Directory '{plugin_dir}' already exists.")
        raise typer.Exit(code=1)
        
    plugin_dir.mkdir(parents=True)
    
    # 1. Create __init__.py
    (plugin_dir / "__init__.py").write_text("")
    
    # 2. Create spec.json (Configuration JSON Schema)
    spec_json = {
        "type": "object",
        "title": f"{name} Spec",
        "required": ["api_key"] if plugin_type == PluginType.source else ["host", "port", "username", "password"],
        "properties": {
            "api_key": {
                "type": "string",
                "title": "API Key",
                "description": "API Key for authentication."
            }
        } if plugin_type == PluginType.source else {
            "host": {"type": "string"},
            "port": {"type": "integer", "default": 5432},
            "username": {"type": "string"},
            "password": {"type": "string", "writeOnly": True}
        }
    }
    
    (plugin_dir / "spec.json").write_text(json.dumps(spec_json, indent=2))
    
    # 3. Create pyproject.toml
    pyproject_toml = textwrap.dedent(f"""\
        [project]
        name = "{name}"
        version = "0.1.0"
        description = "A {plugin_type.value} plugin for FlowCore."
        authors = [
            {{ name = "{author}" }}
        ]
        dependencies = [
            "flowcore-shared>=1.0.0"
        ]

        [project.entry-points."flowcore.plugins"]
        {name} = "{name.replace('-', '_')}.plugin:{name.title().replace('-', '')}Plugin"
    """)
    (plugin_dir / "pyproject.toml").write_text(pyproject_toml)
    
    # 4. Create README.md
    readme_md = textwrap.dedent(f"""\
        # {name}
        
        This is a {plugin_type.value} plugin for FlowCore.
        
        ## Usage
        Install the plugin into your FlowCore environment:
        ```bash
        pip install -e .
        ```
    """)
    (plugin_dir / "README.md").write_text(readme_md)
    
    # 5. Create plugin.py based on type
    plugin_class_name = f"{name.title().replace('-', '')}Plugin"
    
    if plugin_type == PluginType.source:
        plugin_code = textwrap.dedent(f"""\
            from typing import Any, Dict, Iterator, List, Optional
            import json
            from pathlib import Path
            from flowcore_shared.plugins.cdk.source import SourcePlugin
            from flowcore_shared.plugins.cdk.messages import FlowCoreMessage, MessageType, RecordMessage, StateMessage
            from flowcore_shared.plugins.models import PluginMetadata, ConnectorCapabilities
            from flowcore_shared.plugins.enums import PluginType
            
            class {plugin_class_name}(SourcePlugin):
                @property
                def metadata(self) -> PluginMetadata:
                    return PluginMetadata(
                        plugin_id="{name}",
                        name="{name}",
                        version="0.1.0",
                        plugin_type=PluginType.CONNECTOR,
                        author="{author}",
                        description="Scaffolded Source Plugin",
                        connector_type="Source",
                        flowcore_version_constraint=">=1.0.0",
                        capabilities=ConnectorCapabilities()
                    )
                    
                def check(self, config: Dict[str, Any]) -> bool:
                    if "api_key" not in config:
                        raise ValueError("Missing api_key")
                    return True
                    
                def discover(self, config: Dict[str, Any]) -> List[Dict[str, Any]]:
                    return [{{"stream": "default_stream", "json_schema": {{"type": "object"}}}}]
                    
                def read(self, config: Dict[str, Any], catalog: Optional[Any] = None, state: Optional[Dict[str, Any]] = None) -> Iterator[FlowCoreMessage]:
                    last_id = state.get("last_id", 0) if state else 0
                    
                    # Example implementation: yield 5 records
                    for i in range(1, 6):
                        current_id = last_id + i
                        yield FlowCoreMessage(
                            type=MessageType.RECORD,
                            record=RecordMessage(stream="default_stream", data={{"id": current_id, "value": "test"}})
                        )
                        yield FlowCoreMessage(
                            type=MessageType.STATE,
                            state=StateMessage(state_data={{"last_id": current_id}})
                        )
        """)
    elif plugin_type == PluginType.destination:
        plugin_code = textwrap.dedent(f"""\
            from typing import Any, Dict, Iterator
            import json
            from pathlib import Path
            from flowcore_shared.plugins.cdk.destination import DestinationPlugin
            from flowcore_shared.plugins.cdk.messages import FlowCoreMessage, MessageType
            from flowcore_shared.plugins.models import PluginMetadata, ConnectorCapabilities
            from flowcore_shared.plugins.enums import PluginType
            
            class {plugin_class_name}(DestinationPlugin):
                @property
                def metadata(self) -> PluginMetadata:
                    return PluginMetadata(
                        plugin_id="{name}",
                        name="{name}",
                        version="0.1.0",
                        plugin_type=PluginType.CONNECTOR,
                        author="{author}",
                        description="Scaffolded Destination Plugin",
                        connector_type="Destination",
                        flowcore_version_constraint=">=1.0.0",
                        capabilities=ConnectorCapabilities()
                    )
                    
                def check(self, config: Dict[str, Any]) -> bool:
                    return True
                    
                def write(self, config: Dict[str, Any], catalog: Any, message_stream: Iterator[FlowCoreMessage]) -> Iterator[FlowCoreMessage]:
                    for msg in message_stream:
                        if msg.type == MessageType.RECORD:
                            # Write record to destination here
                            pass
                        elif msg.type == MessageType.STATE:
                            # Forward state after committing records
                            yield msg
        """)
    elif plugin_type == PluginType.transform:
        plugin_code = textwrap.dedent(f"""\
            from typing import Any, Dict, Iterator
            import json
            from pathlib import Path
            from flowcore_shared.plugins.cdk.transform import TransformPlugin
            from flowcore_shared.plugins.cdk.messages import FlowCoreMessage, MessageType
            from flowcore_shared.plugins.models import PluginMetadata, ConnectorCapabilities
            from flowcore_shared.plugins.enums import PluginType
            
            class {plugin_class_name}(TransformPlugin):
                @property
                def metadata(self) -> PluginMetadata:
                    return PluginMetadata(
                        plugin_id="{name}",
                        name="{name}",
                        version="0.1.0",
                        plugin_type=PluginType.CONNECTOR,
                        author="{author}",
                        description="Scaffolded Transform Plugin",
                        connector_type="Transform",
                        flowcore_version_constraint=">=1.0.0",
                        capabilities=ConnectorCapabilities()
                    )
                    
                def check(self, config: Dict[str, Any]) -> bool:
                    return True
                    
                def transform(self, config: Dict[str, Any], message_stream: Iterator[FlowCoreMessage]) -> Iterator[FlowCoreMessage]:
                    for msg in message_stream:
                        if msg.type == MessageType.RECORD and msg.record:
                            # Example: Add a transformed flag
                            msg.record.data["_transformed"] = True
                        yield msg
        """)

    pkg_dir = plugin_dir / name.replace("-", "_")
    pkg_dir.mkdir(parents=True)
    (pkg_dir / "__init__.py").write_text("")
    (pkg_dir / "plugin.py").write_text(plugin_code)
    
    # 6. Contract Test Template
    test_dir = plugin_dir / "tests"
    test_dir.mkdir(parents=True)
    (test_dir / "__init__.py").write_text("")
    
    test_code = textwrap.dedent(f"""\
        import pytest
        from {name.replace("-", "_")}.plugin import {plugin_class_name}
        
        def test_plugin_metadata():
            plugin = {plugin_class_name}()
            assert plugin.metadata.name == "{name}"
            assert plugin.metadata.connector_type == "{plugin_type.value.capitalize()}"
            
        def test_plugin_check():
            plugin = {plugin_class_name}()
            assert plugin.check({{"api_key": "test"}} if "{plugin_type.value}" == "source" else {{}})
    """)
    (test_dir / "test_contract.py").write_text(test_code)

    console.print(f"[bold green]Successfully scaffolded {plugin_type.value} plugin '{name}' in {plugin_dir}.[/]")
    console.print("To get started:")
    console.print(f"  cd {plugin_dir}")
    console.print("  pip install -e .")
    console.print("  pytest tests/")


@app.command("test")
def plugin_test(
    plugin_path: str = typer.Argument(..., help="Path to the plugin package or import string"),
):
    """
    Validate a plugin against the CDK contract.
    """
    console.print(f"[bold blue]Validating plugin at {plugin_path}...[/]")
    
    import importlib
    try:
        module = importlib.import_module(f"{plugin_path}.plugin")
        # Find the plugin class
        from flowcore_shared.plugins.base import BasePlugin
        
        import inspect
        
        plugin_class = None
        for item_name in dir(module):
            item = getattr(module, item_name)
            if isinstance(item, type) and issubclass(item, BasePlugin) and not inspect.isabstract(item):
                plugin_class = item
                break
                
        if not plugin_class:
            console.print("[bold red]Error:[/] Could not find any class inheriting from BasePlugin.")
            raise typer.Exit(code=1)
            
        plugin_instance = plugin_class()
        metadata = plugin_instance.metadata
        
        console.print(f"[green]Found Plugin:[/] {metadata.name} (v{metadata.version})")
        console.print(f"[green]Type:[/] {metadata.connector_type}")
        
        # Test Check
        try:
            console.print("[blue]Running check()...[/]")
            # Provide an empty config, expect it to either pass or raise a known error, not crash
            try:
                plugin_instance.check({})
                console.print("[green]check() passed with empty config.[/]")
            except Exception as e:
                console.print(f"[yellow]check() correctly raised exception on invalid config:[/] {e}")
        except Exception as e:
            console.print(f"[bold red]Contract Validation Failed:[/] {e}")
            raise typer.Exit(code=1)
            
        console.print("[bold green]Plugin successfully validated against FlowCore CDK contracts![/]")
        
    except ImportError as e:
        console.print(f"[bold red]Failed to import plugin:[/] {e}")
        raise typer.Exit(code=1)
