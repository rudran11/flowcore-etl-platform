# Copyright (c) 2026 Rudran
# Licensed under the MIT License.
# See LICENSE file in the project root for full license information.

import time
import threading
import uuid
from pathlib import Path
from typing import Dict

import typer
from rich.console import Console
from rich.live import Live
from rich.text import Text
from rich.panel import Panel

from flowcore_cli.context import CLIContext
from flowcore.parsing.parser import DSLParser
from flowcore_shared.exceptions.parsing import DSLParseError
from flowcore.models.dependencies.dependency_graph import DependencyGraph
from flowcore.models.dependencies.node import Node
from flowcore.models.dependencies.edge import Edge
from flowcore.models.operational.execution import ExecutionRun
from flowcore_shared.schemas.base.enums import ExecutionState
from flowcore_engine.plugins.manager import PluginManager
from flowcore_engine.coordinator.manager import ExecutionCoordinator
from flowcore_engine.executor.thread import ThreadExecutor
from flowcore_engine.runner.engine import EngineRunner
from flowcore_cli.client.api import FlowCoreClient, FlowCoreClientError
import yaml

app = typer.Typer(help="Run FlowCore pipelines.")

class StepTracker:
    def __init__(self, step_id: str):
        self.step_id = step_id
        self.state = ExecutionState.PENDING
        self.start_time = None
        self.end_time = None

    def update_state(self, new_state: ExecutionState):
        if self.state == new_state:
            return
            
        self.state = new_state
        if new_state == ExecutionState.RUNNING and self.start_time is None:
            self.start_time = time.time()
        elif new_state in (ExecutionState.COMPLETED, ExecutionState.FAILED) and self.end_time is None:
            self.end_time = time.time()

    @property
    def duration(self) -> float:
        if self.start_time:
            end = self.end_time or time.time()
            return end - self.start_time
        return 0.0

@app.callback(invoke_without_command=True)
def run_command(
    ctx: typer.Context,
    pipeline_file: str = typer.Argument(..., help="Path to the pipeline YAML file"),
    remote: bool = typer.Option(False, "--remote", help="Execute the pipeline on the remote FlowCore Server"),
    server_url: str = typer.Option(None, "--server", help="Override the server URL from flowcore.toml")
):
    context: CLIContext = ctx.obj
    console = context.console
    
    file_path = Path(pipeline_file)
    if not file_path.exists():
        context.error(f"File not found: {pipeline_file}")
        raise typer.Exit(code=1)
        
    console.print(f"Running Pipeline from: [bold cyan]{pipeline_file}[/bold cyan]\n")
    
    # 1. Parse YAML
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            raw_data = yaml.safe_load(f)
        pipeline, steps = DSLParser.parse_pipeline_dsl(raw_data)
    except Exception as e:
        context.error(f"Failed to parse pipeline: {e}")
        raise typer.Exit(code=1)
        
    # 2. Build Dependency Graph
    try:
        nodes = {s.step_id: Node(node_id=s.step_id) for s in steps}
        edges = [Edge(source=dep, target=s.step_id) for s in steps for dep in s.depends_on]
        graph = DependencyGraph(nodes=nodes, edges=edges)
    except Exception as e:
        context.error(f"Dependency Error: {e}")
        raise typer.Exit(code=1)
        
    # 3. Discover Plugins
    plugin_manager = PluginManager()
    if context.project_root:
        plugin_manager.discover_plugins([str(context.project_root / "plugins")])
        
    missing_plugins = [s.connector_id for s in steps if s.connector_id not in plugin_manager._instance_registry]
    if missing_plugins:
        context.error(f"Unknown plugins referenced: {', '.join(set(missing_plugins))}")
        raise typer.Exit(code=1)
        
    # Remote Execution Flow
    config = context.config or {}
    if remote or config.get("execution", {}).get("mode") == "remote":
        url = server_url or config.get("server", {}).get("url")
        if not url:
            context.error("Server URL must be provided via --server or flowcore.toml for remote execution.")
            raise typer.Exit(code=2)
            
        console.print(f"Submitting pipeline to server at [cyan]{url}[/cyan]...")
        client = FlowCoreClient(base_url=url)
        
        try:
            response = client.execute_pipeline(pipeline_id=pipeline.name, version="1.0.0")
            run_id = response.get("run_id")
            console.print(f"\nRun ID: [bold magenta]{run_id}[/bold magenta]")
            console.print("Monitoring...\n")
            
            # Simple polling loop
            start_time = time.time()
            with Live(console=console, refresh_per_second=2) as live:
                while True:
                    status_res = client.get_run_status(run_id)
                    status = status_res.get("status", "UNKNOWN")
                    duration_ms = status_res.get("duration_ms", 0)
                    duration_sec = (duration_ms / 1000) if duration_ms else (time.time() - start_time)
                    
                    if status == "COMPLETED":
                        ui = Text(f"[✓] Pipeline Execution (Status: {status}) ({duration_sec:.2f}s)\n", style="green")
                    elif status in ("FAILED", "CANCELLED"):
                        ui = Text(f"[✗] Pipeline Execution (Status: {status}) ({duration_sec:.2f}s)\n", style="red")
                    else:
                        ui = Text(f"[>] Pipeline Execution (Status: {status}) ({duration_sec:.2f}s)\n", style="yellow")
                    
                    live.update(ui)
                    
                    if status in ("COMPLETED", "FAILED", "CANCELLED"):
                        break
                        
                    time.sleep(0.5)
            
            console.print("\n────────────────────────────\n")
            if status == "COMPLETED":
                console.print("[bold green]Pipeline completed successfully[/bold green]\n")
            else:
                console.print("[bold red]Pipeline failed[/bold red]\n")
                if status_res.get("error"):
                    console.print(f"Error: {status_res['error']}\n")
                raise typer.Exit(code=1)
                
            return
            
        except FlowCoreClientError as e:
            context.error(f"Unable to connect to FlowCore Server.\n\nServer:\n{url}\n\nReason:\n{e}")
            raise typer.Exit(code=3)
            
    # Local Execution Flow
    # 4. Engine Initialization
    # We must convert Pipeline to PipelineVersion for ExecutionCoordinator
    from flowcore.models.pipeline.pipeline_version import PipelineVersion
    pipeline_version = PipelineVersion(
        id=str(uuid.uuid4()),
        pipeline_id=pipeline.id,
        version="1.0.0",
        steps=steps
    )
    
    coordinator = ExecutionCoordinator(pipeline=pipeline_version, graph=graph)
    executor = ThreadExecutor(max_workers=10)
    runner = EngineRunner(coordinator=coordinator, plugin_manager=plugin_manager, executor=executor)
    
    run_record = ExecutionRun(
        id=str(uuid.uuid4()),
        pipeline_id=pipeline.id,
        pipeline_version_id=pipeline_version.id,
        trigger_type="MANUAL"
    )
    coordinator.initialize_run(run_record)
    
    # 5. UI State
    trackers = {s.step_id: StepTracker(s.step_id) for s in steps}
    
    def generate_ui() -> Text:
        ui = Text()
        for s in steps:
            tracker = trackers[s.step_id]
            
            # Format state icon
            if tracker.state == ExecutionState.COMPLETED:
                icon = "[green][✓][/green]"
            elif tracker.state == ExecutionState.FAILED:
                icon = "[red][✗][/red]"
            elif tracker.state == ExecutionState.RUNNING:
                icon = "[yellow][>][/yellow]"
            elif tracker.state == ExecutionState.RETRYING:
                icon = "[magenta][R][/magenta]"
            else:
                icon = "[dim][ ][/dim]"
                
            dur_str = f"({tracker.duration:.2f}s)" if tracker.start_time else ""
            ui.append_text(Text.from_markup(f"{icon} {tracker.step_id:<25} {dur_str}\n"))
        return ui

    engine_error = None
    def run_engine_safe():
        nonlocal engine_error
        try:
            runner.run()
        except Exception as e:
            engine_error = e

    # Start the engine loop in a background thread
    engine_thread = threading.Thread(target=run_engine_safe, daemon=True)
    start_time = time.time()
    engine_thread.start()
    
    # Render loop
    try:
        with Live(generate_ui(), refresh_per_second=10, console=console) as live:
            while engine_thread.is_alive():
                # Sync state
                for step_id, tracker in trackers.items():
                    current_state = coordinator.get_step_state(step_id)
                    tracker.update_state(current_state)
                    
                live.update(generate_ui())
                time.sleep(0.1)
                
            # Final sync
            for step_id, tracker in trackers.items():
                current_state = coordinator.get_step_state(step_id)
                tracker.update_state(current_state)
            live.update(generate_ui())
            
    except KeyboardInterrupt:
        console.print("\n[bold red]Execution interrupted by user (Ctrl+C).[/bold red]")
        executor.shutdown(wait=False)
        raise typer.Exit(code=1)
        
    finally:
        executor.shutdown(wait=True)
        
    if engine_error:
        console.print(f"[bold red]Engine Error:[/bold red] {engine_error}")
        raise typer.Exit(code=1)
        
    total_duration = time.time() - start_time
    
    failures = sum(1 for t in trackers.values() if t.state == ExecutionState.FAILED)
    completed = sum(1 for t in trackers.values() if t.state == ExecutionState.COMPLETED)
    
    console.print("\n────────────────────────────\n")
    if failures == 0:
        console.print("[bold green]Pipeline completed successfully[/bold green]\n")
    else:
        console.print("[bold red]Pipeline failed[/bold red]\n")
        
    summary = (
        f"Steps:      [bold]{completed}/{len(steps)}[/bold]\n"
        f"Duration:   [bold]{total_duration:.2f}s[/bold]\n"
        f"Failures:   [bold]{failures}[/bold]"
    )
    console.print(summary)
    
    if failures > 0:
        raise typer.Exit(code=1)
