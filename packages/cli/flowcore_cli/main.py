# Copyright (c) 2026 Rudran
# Licensed under the MIT License.
# See LICENSE file in the project root for full license information.

"""
Main Entrypoint for FlowCore CLI.

Provides basic version and help commands.
"""

import click
from . import __version__

@click.group()
@click.version_option(version=__version__, message="FlowCore CLI v%(version)s")
def cli():
    """
    FlowCore Enterprise ETL Platform CLI.
    """
    pass

if __name__ == "__main__":
    cli()
