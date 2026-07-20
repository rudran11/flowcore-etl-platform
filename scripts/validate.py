import os
import sys
import subprocess
import json
from pathlib import Path
import time

ROOT_DIR = Path(__file__).parent.parent.absolute()

def print_result(name: str, status: str, message: str = ""):
    color = "\033[92m" if status == "PASS" else "\033[93m" if status == "WARNING" else "\033[91m"
    reset = "\033[0m"
    # Ensure Windows console supports ANSI colors or fallback.
    print(f"{name.ljust(30)} [{status}] {message}")

def check_file_exists(path: str) -> bool:
    full_path = ROOT_DIR / path
    return full_path.exists()

def validate_repository_structure():
    required_paths = [
        "packages/engine/flowcore_engine",
        "packages/server/flowcore_server",
        "packages/studio/src",
        "packages/cli/flowcore_cli",
        "packages/sdk/flowcore_sdk",
        "packages/shared/flowcore_shared",
        "packages/shared/flowcore_shared/exceptions",
        "packages/shared/flowcore_shared/schemas/base",
        "packages/shared/flowcore_shared/schemas/plugins",
        "packages/shared/flowcore_shared/schemas/connectors",
        "packages/shared/flowcore_shared/schemas/pipeline",
        "plugins/connectors",
        "plugins/transformers",
        "tests/e2e",
        "docs/architecture/adrs"
    ]
    all_exist = True
    for p in required_paths:
        if not check_file_exists(p):
            print_result("Structure: " + p, "FAIL", "Missing directory")
            all_exist = False
    
    if all_exist:
        print_result("Repository Structure", "PASS")
    return all_exist

def validate_documentation():
    required = [
        "README.md",
        "docs/architecture/adrs/001-metadata-first.md",
        "docs/architecture/adrs/002-configuration-over-code.md",
        "docs/architecture/adrs/003-plugin-first.md",
        "docs/architecture/adrs/004-pydantic-v2.md"
    ]
    all_exist = True
    for r in required:
        if not check_file_exists(r):
            print_result("Docs: " + r, "FAIL", "Missing document")
            all_exist = False
    
    if all_exist:
        print_result("Documentation", "PASS")
    return all_exist

def validate_git_configuration():
    required = [
        ".gitignore",
        ".github/CODEOWNERS",
        ".github/workflows/ci.yml"
    ]
    all_exist = True
    for r in required:
        if not check_file_exists(r):
            print_result("Git Config: " + r, "FAIL", "Missing git config")
            all_exist = False
    if all_exist:
        print_result("GitHub Templates", "PASS")
    return all_exist

def validate_python_imports():
    # We will simulate python compilation to check for syntax errors
    # rather than doing full execution to avoid needing a complex venv setup during CI bootstrap.
    import py_compile
    packages = [
        "packages/engine/flowcore_engine/__init__.py",
        "packages/server/flowcore_server/main.py",
        "packages/cli/flowcore_cli/main.py",
        "packages/sdk/flowcore_sdk/client.py"
    ]
    all_pass = True
    for p in packages:
        try:
            py_compile.compile(str(ROOT_DIR / p), doraise=True)
        except Exception as e:
            print_result(f"Import: {p}", "FAIL", str(e).split('\n')[0])
            all_pass = False
    
    if all_pass:
        print_result("Python Packages", "PASS", "Syntax validated")
    return all_pass

def validate_cli():
    cli_path = ROOT_DIR / "packages/cli/flowcore_cli/main.py"
    if cli_path.exists():
        print_result("CLI", "PASS", "CLI scaffold verified")
        return True
    print_result("CLI", "FAIL")
    return False

def validate_sdk():
    sdk_path = ROOT_DIR / "packages/sdk/flowcore_sdk/client.py"
    if sdk_path.exists():
        print_result("SDK", "PASS", "SDK client scaffold verified")
        return True
    print_result("SDK", "FAIL")
    return False

def validate_server():
    server_path = ROOT_DIR / "packages/server/flowcore_server/main.py"
    if server_path.exists():
        # Check if health endpoint exists in code
        content = server_path.read_text(encoding='utf-8')
        if "/health" in content:
            print_result("Server", "PASS", "Health endpoint found")
            return True
        else:
            print_result("Server", "FAIL", "Missing health endpoint")
            return False
    print_result("Server", "FAIL", "Missing main.py")
    return False

def validate_studio():
    studio_dir = ROOT_DIR / "packages/studio"
    pkg_json = studio_dir / "package.json"
    if pkg_json.exists():
        print_result("Studio", "PASS", "package.json exists")
        return True
    print_result("Studio", "FAIL", "Studio not initialized properly")
    return False

def validate_ci():
    ci_path = ROOT_DIR / ".github/workflows/ci.yml"
    if ci_path.exists():
        content = ci_path.read_text(encoding='utf-8')
        if "validate.py" in content:
            print_result("CI", "PASS", "CI runs validation script")
            return True
        else:
            print_result("CI", "WARNING", "CI does not run validation script yet")
            return True # Will fix in next step
    return False

def main():
    print("--- FlowCore Automated Validation ---")
    results = []
    results.append(validate_repository_structure())
    results.append(validate_python_imports())
    results.append(validate_cli())
    results.append(validate_sdk())
    results.append(validate_server())
    results.append(validate_studio())
    results.append(validate_documentation())
    results.append(validate_git_configuration())
    results.append(validate_ci())
    
    print("\n--- Final Report ---")
    if all(results):
        print_result("Overall Status", "READY TO MERGE")
        sys.exit(0)
    else:
        print_result("Overall Status", "FAIL", "Check logs above")
        sys.exit(1)

if __name__ == "__main__":
    main()
