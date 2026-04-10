"""Managed hooks command group."""

from __future__ import annotations

from envctl.cli.commands.hooks.command import (
    hooks_install_command,
    hooks_remove_command,
    hooks_repair_command,
    hooks_status_command,
)
from envctl.cli.typer_theme import create_typer_app

hooks_app = create_typer_app(
    help_text="Manage envctl-owned Git [bold]hooks[/bold] for local secret protection."
)

hooks_app.command("status")(hooks_status_command)
hooks_app.command("install")(hooks_install_command)
hooks_app.command("repair")(hooks_repair_command)
hooks_app.command("remove")(hooks_remove_command)
