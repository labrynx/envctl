"""Guard commands."""

from __future__ import annotations

from envctl.cli.typer_theme import create_typer_app

guard_app = create_typer_app(
    help_text="Protect Git history from [bold]envctl[/bold]-specific secrets.",
    lazy_subcommands={
        "secrets": {
            "import_path": "envctl.cli.commands.guard.command:guard_secrets_command",
            "short_help": "Block staged envctl vault artifacts and master keys.",
        },
    },
)
