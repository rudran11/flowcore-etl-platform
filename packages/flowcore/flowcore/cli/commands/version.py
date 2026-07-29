# Copyright (c) 2026 Rudran
# Licensed under the MIT License.
# See LICENSE file in the project root for full license information.

import typer
import importlib.metadata
from rich.console import Console

app = typer.Typer(help="Show the CLI version.")

@app.callback(invoke_without_command=True)
def version_command():
    console = Console()
    try:
        __version__ = importlib.metadata.version("flowcore-cli")
    except importlib.metadata.PackageNotFoundError:
        __version__ = "0.0.0"
        
    console.print(f"FlowCore CLI 0.6.0")
