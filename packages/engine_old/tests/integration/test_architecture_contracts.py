import os
import ast
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent.parent.parent.parent

def get_imports_from_file(filepath: Path) -> set:
    with open(filepath, "r", encoding="utf-8") as f:
        try:
            tree = ast.parse(f.read(), filename=str(filepath))
        except SyntaxError:
            return set()
            
    imports = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                imports.add(alias.name)
        elif isinstance(node, ast.ImportFrom):
            if node.module:
                imports.add(node.module)
    return imports

def test_shared_independence():
    # flowcore_shared must never import flowcore_engine
    shared_path = ROOT_DIR / "packages/shared/flowcore_shared"
    assert shared_path.exists(), f"Path not found: {shared_path}"
    
    for root, _, files in os.walk(shared_path):
        for file in files:
            if file.endswith(".py"):
                imports = get_imports_from_file(Path(root) / file)
                for imp in imports:
                    assert not imp.startswith("flowcore_engine"), f"Architectural violation: {file} imports {imp}"

def test_runner_independence():
    # Runner must not import scheduler or state machine directly (should go through coordinator)
    runner_path = ROOT_DIR / "packages/engine/flowcore_engine/runner/engine.py"
    assert runner_path.exists(), f"Path not found: {runner_path}"
    imports = get_imports_from_file(runner_path)
    for imp in imports:
        assert not imp.startswith("flowcore_engine.scheduler"), "Runner should not bypass Coordinator"
        assert not imp.startswith("flowcore_engine.state"), "Runner should not bypass Coordinator"

def test_plugin_independence():
    # Plugins must not import scheduler, coordinator, state, runner.
    plugin_manager_path = ROOT_DIR / "packages/engine/flowcore_engine/plugins/manager.py"
    assert plugin_manager_path.exists(), f"Path not found: {plugin_manager_path}"
    imports = get_imports_from_file(plugin_manager_path)
    for imp in imports:
        assert not imp.startswith("flowcore_engine.coordinator"), "PluginManager should not depend on Coordinator"
        assert not imp.startswith("flowcore_engine.scheduler"), "PluginManager should not depend on Scheduler"
        assert not imp.startswith("flowcore_engine.runner"), "PluginManager should not depend on Runner"

