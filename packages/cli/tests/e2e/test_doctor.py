# Copyright (c) 2026 Rudran
# Licensed under the MIT License.
# See LICENSE file in the project root for full license information.

from typer.testing import CliRunner
from flowcore_cli.main import app

runner = CliRunner()

def test_cli_doctor_command():
    result = runner.invoke(app, ["doctor"])
    assert result.exit_code == 3 # Fails because no project config in tests/
    assert "FlowCore Doctor" in result.stdout
    assert "Python Version" in result.stdout
    assert "Project Config" in result.stdout
    assert "FlowCore Server" in result.stdout
