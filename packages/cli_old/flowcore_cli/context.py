# Copyright (c) 2026 Rudran
# Licensed under the MIT License.
# See LICENSE file in the project root for full license information.

import os
from pathlib import Path
from dataclasses import dataclass
import tomlkit
from rich.console import Console

@dataclass
class CLIContext:
    console: Console
    verbose: bool
    project_root: Path | None = None
    config: dict | None = None
    server_url: str = "http://localhost:8000"
    execution_mode: str = "local"

    def log(self, message: str):
        if self.verbose:
            self.console.print(f"[dim]{message}[/dim]")

    def error(self, message: str):
        self.console.print(f"[bold red]Error:[/bold red] {message}")

    def load_config(self):
        """Attempts to find and load flowcore.toml from the current directory or parents."""
        current = Path.cwd()
        while current != current.parent:
            config_path = current / "flowcore.toml"
            if config_path.exists():
                self.project_root = current
                try:
                    with open(config_path, "r", encoding="utf-8") as f:
                        self.config = tomlkit.parse(f.read())
                    self.log(f"Loaded configuration from {config_path}")
                    
                    # Validate required sections
                    if "project" not in self.config or "name" not in self.config["project"]:
                        self.error("Invalid configuration: missing [project.name]")
                        import sys
                        sys.exit(2)
                        
                    if "server" not in self.config or "url" not in self.config["server"]:
                        self.error("Invalid configuration: missing [server.url]")
                        import sys
                        sys.exit(2)
                        
                    if "execution" not in self.config or "mode" not in self.config["execution"]:
                        self.error("Invalid configuration: missing [execution.mode]")
                        import sys
                        sys.exit(2)
                    
                    self.server_url = str(self.config["server"]["url"])
                    self.execution_mode = str(self.config["execution"]["mode"])
                    return
                except Exception as e:
                    self.error(f"Failed to parse flowcore.toml: {e}")
                    return
            current = current.parent
        
        self.log("No flowcore.toml found. Running in standalone mode.")

def create_context(verbose: bool = False) -> CLIContext:
    console = Console()
    ctx = CLIContext(console=console, verbose=verbose)
    ctx.load_config()
    return ctx
