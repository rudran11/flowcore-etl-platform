# Copyright (c) 2026 Rudran
# Licensed under the MIT License.
# See LICENSE file in the project root for full license information.

import time
import subprocess
import pytest
from pathlib import Path

import sys

def test_cli_startup_performance_help():
    start = time.time()
    result = subprocess.run([sys.executable, "-m", "flowcore_cli.main", "--help"], capture_output=True, text=True)
    duration = time.time() - start
    
    assert result.returncode == 0
    assert duration < 3.0, f"CLI --help took {duration:.2f}s, which exceeds the 3.0s limit"

def test_cli_startup_performance_version():
    start = time.time()
    result = subprocess.run([sys.executable, "-m", "flowcore_cli.main", "--version"], capture_output=True, text=True)
    duration = time.time() - start
    
    assert result.returncode == 0
    assert duration < 3.0, f"CLI --version took {duration:.2f}s, which exceeds the 3.0s limit"
