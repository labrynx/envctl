"""Managed hooks command group."""

from __future__ import annotations

from envctl.cli.typer_theme import create_typer_app

hooks_app = create_typer_app(
    help_text="Manage envctl-owned Git [bold]hooks[/bold] for local secret protection.",
    lazy_subcommands={
        "status": {
            "import_path": "envctl.cli.commands.hooks.command:hooks_status_command",
            "short_help": "Show managed hooks status.",
        },
        "install": {
            "import_path": "envctl.cli.commands.hooks.command:hooks_install_command",
            "short_help": "Install envctl-managed hooks.",
        },
        "repair": {
            "import_path": "envctl.cli.commands.hooks.command:hooks_repair_command",
            "short_help": "Repair envctl-managed hooks.",
        },
        "remove": {
            "import_path": "envctl.cli.commands.hooks.command:hooks_remove_command",
            "short_help": "Remove envctl-managed hooks.",
        },
    },
)
