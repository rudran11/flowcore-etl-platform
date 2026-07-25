# Copyright (c) 2026 Rudran
# Licensed under the MIT License.
# See LICENSE file in the project root for full license information.

import ast
from pathlib import Path

def test_cli_architecture_imports():
    """
    Ensures that the CLI never imports SQLAlchemy or any ORM entities directly.
    """
    cli_root = Path(__file__).parent.parent.parent / "flowcore_cli"
    
    banned_imports = ["sqlalchemy", "flowcore_server.db.models", "psycopg2"]
    
    for py_file in cli_root.rglob("*.py"):
        tree = ast.parse(py_file.read_text(encoding="utf-8"), filename=str(py_file))
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    assert not any(alias.name.startswith(banned) for banned in banned_imports), \
                        f"Architecture Violation in {py_file.name}: Imported banned module {alias.name}"
            elif isinstance(node, ast.ImportFrom):
                if node.module:
                    assert not any(node.module.startswith(banned) for banned in banned_imports), \
                        f"Architecture Violation in {py_file.name}: Imported banned module {node.module}"

def test_cli_architecture_httpx_usage():
    """
    Ensures that `httpx` is ONLY used inside `flowcore_cli.client.api`.
    Commands should not make raw HTTP requests.
    """
    cli_root = Path(__file__).parent.parent.parent / "flowcore_cli"
    
    for py_file in cli_root.rglob("*.py"):
        # Skip the client itself
        if "client" in py_file.parts or py_file.name == "api.py":
            continue
            
        tree = ast.parse(py_file.read_text(encoding="utf-8"), filename=str(py_file))
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    assert alias.name != "httpx", \
                        f"Architecture Violation in {py_file.name}: Directly imported httpx outside of Client layer"
            elif isinstance(node, ast.ImportFrom):
                if node.module:
                    assert node.module != "httpx", \
                        f"Architecture Violation in {py_file.name}: Directly imported httpx outside of Client layer"
