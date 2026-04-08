"""Guard commands."""

from __future__ import annotations

from envctl.cli.commands.guard.command import guard_secrets_command
from envctl.cli.typer_theme import create_typer_app

guard_app = create_typer_app(
    help_text="Protect Git history from [bold]envctl[/bold]-specific secrets."
)
guard_app.command("secrets")(guard_secrets_command)
