# Copyright (c) 2026 Rudran
# Licensed under the MIT License.
# See LICENSE file in the project root for full license information.

import typer
import yaml
import time
from pathlib import Path
from rich.console import Console
from rich.panel import Panel
from rich.tree import Tree
from flowcore_cli.context import CLIContext

# Remove app = typer.Typer() from here
def validate_command(
    ctx: typer.Context,
    pipeline_file: str = typer.Argument(..., help="Path to the pipeline YAML file"),
    dry_run: bool = typer.Option(False, "--dry-run", help="Display the execution plan and topological order")
):
    start_time = time.time()
    
    context: CLIContext = ctx.obj
    console = context.console
    
    file_path = Path(pipeline_file)
    if not file_path.exists():
        context.error(f"File not found: {pipeline_file}")
        raise typer.Exit(code=1)
        
    console.print(f"Validating [bold cyan]{pipeline_file}[/bold cyan]...\n")
    
    # 1. Parse YAML
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            raw_data = yaml.safe_load(f)
    except yaml.YAMLError as e:
        context.error(f"YAML Syntax Error: {e}")
        raise typer.Exit(code=1)
        
    # 2. Schema Validation (via DSLParser)
    from flowcore.parsing.parser import DSLParser
    from flowcore_shared.exceptions.parsing import DSLParseError
    
    try:
        pipeline, steps = DSLParser.parse_pipeline_dsl(raw_data)
    except DSLParseError as e:
        context.error(f"Schema Validation Failed: {e}")
        raise typer.Exit(code=1)
        
    # 3. Duplicate Step IDs
    step_ids = [s.step_id for s in steps]
    if len(step_ids) != len(set(step_ids)):
        duplicates = [x for i, x in enumerate(step_ids) if x in step_ids[:i]]
        context.error(f"Duplicate step IDs found: {', '.join(duplicates)}")
        raise typer.Exit(code=1)
        
    # 4. Dependency Graph & Cycles
    from flowcore.models.dependencies.dependency_graph import DependencyGraph
    from flowcore.models.dependencies.node import Node
    from flowcore.models.dependencies.edge import Edge
    
    try:
        nodes = {s.step_id: Node(node_id=s.step_id) for s in steps}
        edges = []
        for s in steps:
            for dep in s.depends_on:
                edges.append(Edge(source=dep, target=s.step_id))
                
        graph = DependencyGraph(nodes=nodes, edges=edges)
    except (ValueError, Exception) as e:
        context.error(f"Dependency Error: {e}")
        raise typer.Exit(code=1)
        
    # 5. Plugin Validation
    from flowcore_engine.plugins.manager import PluginManager
    plugin_manager = PluginManager()
    
    # Ideally we'd call plugin_manager.discover_plugins(...) here using context.project_root
    if context.project_root:
        plugin_manager.discover_plugins([str(context.project_root / "plugins")])
        
    missing_plugins = []
    for s in steps:
        if s.connector_id not in plugin_manager._instance_registry:
            missing_plugins.append(s.connector_id)
    
    if missing_plugins:
        context.error(f"Unknown plugins referenced: {', '.join(set(missing_plugins))}")
        raise typer.Exit(code=1)
        
    if not dry_run:
        elapsed = time.time() - start_time
        console.print(f"[bold green]✔ Validation successful[/bold green] in {elapsed * 1000:.0f} ms")
        return
        
    # --- Dry Run Execution Plan ---
    
    # Calculate execution layers (BFS)
    in_degree = {n: 0 for n in graph.nodes}
    adj = {n: [] for n in graph.nodes}
    
    for e in graph.edges:
        in_degree[e.target] += 1
        adj[e.source].append(e.target)
        
    queue = [n for n, d in in_degree.items() if d == 0]
    layers = []
    
    while queue:
        # Sort for deterministic output
        queue.sort()
        layers.append(list(queue))
        next_queue = []
        for current in queue:
            for neighbor in adj[current]:
                in_degree[neighbor] -= 1
                if in_degree[neighbor] == 0:
                    next_queue.append(neighbor)
        queue = next_queue
        
    # Print tree plan
    tree = Tree(f"[bold cyan]{pipeline.name}[/bold cyan]")
    
    for i, layer in enumerate(layers):
        layer_node = tree.add(f"[bold magenta]Layer {i+1}[/bold magenta]")
        for step_id in layer:
            layer_node.add(f"[green]{step_id}[/green]")
            
    console.print("\n[bold underline]Execution Plan[/bold underline]\n")
    console.print(tree)
    console.print()
    
    # Validation Summary
    elapsed = time.time() - start_time
    summary_text = (
        f"Pipeline:      [cyan]{pipeline.name}[/cyan]\n"
        f"Steps:         [bold]{len(steps)}[/bold]\n"
        f"Plugins:       [bold]{len(set([s.connector_id for s in steps]))}[/bold]\n"
        f"Parallel Layers:[bold]{len(layers)}[/bold]\n"
        f"Warnings:      [yellow]0[/yellow]\n"
        f"Errors:        [red]0[/red]\n\n"
        f"Validation completed in [bold]{elapsed * 1000:.0f} ms[/bold]"
    )
    
    console.print(Panel(summary_text, title="Validation Summary", expand=False))
    console.print("\n[bold green]✔ Ready to Execute[/bold green]")
