"""Guard commands."""

from __future__ import annotations

import typer

from envctl.cli.commands.guard.command import guard_secrets_command

guard_app = typer.Typer(help="Protect Git history from envctl-specific secrets.")
guard_app.command("secrets")(guard_secrets_command)
