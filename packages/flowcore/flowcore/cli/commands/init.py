# Copyright (c) 2026 Rudran
# Licensed under the MIT License.
# See LICENSE file in the project root for full license information.

import typer
from flowcore.cli.context import CLIContext

app = typer.Typer(help="Initialize a new FlowCore project.")

@app.callback(invoke_without_command=True)
def init(
    ctx: typer.Context,
    project_name: str = typer.Argument(..., help="Name of the new project")
):
    context: CLIContext = ctx.obj
    
    context.console.print(f"Initializing FlowCore project: [bold cyan]{project_name}[/bold cyan]")
    
    import os
    from pathlib import Path
    import tomlkit
    
    base_dir = Path.cwd() / project_name
    if base_dir.exists():
        context.error(f"Directory {project_name} already exists.")
        raise typer.Exit(code=1)
        
    try:
        base_dir.mkdir()
        (base_dir / "pipelines").mkdir()
        (base_dir / "plugins").mkdir()
        
        # Create flowcore.toml
        config = tomlkit.document()
        
        project_table = tomlkit.table()
        project_table.add("name", project_name)
        config.add("project", project_table)
        
        server_table = tomlkit.table()
        server_table.add("url", "http://localhost:8000")
        config.add("server", server_table)
        
        execution_table = tomlkit.table()
        execution_table.add("mode", "local")
        config.add("execution", execution_table)
        
        plugins_table = tomlkit.table()
        plugins_table.add("directory", "plugins")
        config.add("plugins", plugins_table)
        
        with open(base_dir / "flowcore.toml", "w", encoding="utf-8") as f:
            f.write(tomlkit.dumps(config))
            
        context.console.print("[bold green][OK][/bold green] Created project directory")
        context.console.print("[bold green][OK][/bold green] Created flowcore.toml")
        context.console.print("[bold green][OK][/bold green] Created pipelines/ and plugins/ directories")
        context.console.print(f"\nNext steps:\n  cd {project_name}\n  flowcore doctor")
        
    except Exception as e:
        context.error(f"Failed to initialize project: {e}")
        raise typer.Exit(code=1)
