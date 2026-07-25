# Copyright (c) 2026 Rudran
# Licensed under the MIT License.
# See LICENSE file in the project root for full license information.

import sys
import typer
from rich.table import Table
from flowcore.cli.context import CLIContext
from flowcore.cli.client.api import FlowCoreClient, FlowCoreClientError

app = typer.Typer(help="Check environment health and configuration.")

@app.callback(invoke_without_command=True)
def doctor(ctx: typer.Context):
    context: CLIContext = ctx.obj
    console = context.console
    
    console.print("[bold cyan]FlowCore Doctor[/bold cyan] \U0001fa7a\n")
    
    table = Table(show_header=True, header_style="bold magenta")
    table.add_column("Component")
    table.add_column("Status")
    table.add_column("Details")
    
    failures = 0
    
    # 1. Python Version
    py_version = sys.version.split()[0]
    if sys.version_info >= (3, 11):
        table.add_row("Python Version", "[green]✓ OK[/green]", f"v{py_version}")
    else:
        table.add_row("Python Version", "[red]✗ FAIL[/red]", f"v{py_version} (Requires >= 3.11)")
        failures += 1
        
    # 2. Project Config
    if context.project_root:
        table.add_row("Project Config", "[green]✓ OK[/green]", f"Found at {context.project_root / 'flowcore.toml'}")
    else:
        table.add_row("Project Config", "[red]✗ FAIL[/red]", "No flowcore.toml found. Run 'flowcore init' to create one.")
        failures += 1
        
    # 3. Server Connectivity
    try:
        client = FlowCoreClient(base_url=context.server_url, timeout=3)
        if client.ping():
            table.add_row("FlowCore Server", "[green]✓ OK[/green]", f"Connected to {context.server_url}")
        else:
            table.add_row("FlowCore Server", "[red]✗ FAIL[/red]", f"Server returned non-200 status")
            failures += 1
    except FlowCoreClientError:
        table.add_row("FlowCore Server", "[red]✗ FAIL[/red]", f"Could not connect to {context.server_url}")
        failures += 1
        
    console.print(table)
    console.print()
    
    if failures == 0:
        console.print("[bold green]System Status: HEALTHY[/bold green]")
    else:
        console.print(f"[bold red]System Status: {failures} ERRORS FOUND[/bold red]")
        raise typer.Exit(code=3)
