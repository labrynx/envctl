"""Config commands."""

from __future__ import annotations

import typer

from envctl.cli.decorators import handle_errors
from envctl.services.config_service import run_config_init
from envctl.utils.output import print_kv, print_success

config_app = typer.Typer(help="Manage envctl configuration.")


@config_app.command("init")
@handle_errors
def config_init() -> None:
    """Create the default envctl config file."""
    config_path = run_config_init()
    print_success("Created envctl config file")
    print_kv("config", str(config_path))
