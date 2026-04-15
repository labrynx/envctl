"""Hook command group."""

from __future__ import annotations

from envctl.cli.typer_theme import create_typer_app

hook_app = create_typer_app(
    help_text="Run internal envctl-managed [bold]hook[/bold] policies.",
    lazy_subcommands={
        "run": {
            "import_path": "envctl.cli.commands.hook.commands.run:hook_run_command",
            "short_help": "Run one managed hook policy.",
        },
    },
)
