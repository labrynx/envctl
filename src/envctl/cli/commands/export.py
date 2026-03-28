"""Export command."""

from __future__ import annotations

import typer

from envctl.cli.decorators import handle_errors
from envctl.services.export_service import run_export


@handle_errors
def export_command() -> None:
    """Print shell export lines."""
    typer.echo(run_export(), nl=False)
