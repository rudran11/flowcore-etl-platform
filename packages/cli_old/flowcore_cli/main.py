# Copyright (c) 2026 Rudran
# Licensed under the MIT License.
# See LICENSE file in the project root for full license information.

import typer
from rich.console import Console

from flowcore_cli.context import create_context
from flowcore_cli.commands import init, doctor
from flowcore_cli.commands.validate import validate_command
from flowcore_cli.commands.run import run_command
import importlib.metadata

try:
    __version__ = importlib.metadata.version("flowcore-cli")
except importlib.metadata.PackageNotFoundError:
    __version__ = "0.0.0"

app = typer.Typer(
    name="flowcore",
    help="FlowCore Enterprise ETL Platform CLI.",
    no_args_is_help=True
)

app.add_typer(init.app, name="init", help="Initialize a new FlowCore project")
app.add_typer(doctor.app, name="doctor", help="Check environment health and configuration")
app.command(name="validate", help="Validate FlowCore pipeline definitions")(validate_command)
app.command(name="run", help="Run FlowCore pipelines locally")(run_command)

def version_callback(value: bool):
    if value:
        console = Console()
        console.print("FlowCore CLI 0.6.0")
        raise typer.Exit()

@app.callback()
def main(
    ctx: typer.Context,
    verbose: bool = typer.Option(False, "--verbose", "-v", help="Enable verbose logging"),
    version: bool = typer.Option(None, "--version", callback=version_callback, is_eager=True, help="Show the CLI version and exit"),
):
    """
    FlowCore Enterprise ETL Platform CLI.
    """
    # Create the shared CLIContext and inject it into typer Context
    ctx.obj = create_context(verbose=verbose)

if __name__ == "__main__":
    app()
