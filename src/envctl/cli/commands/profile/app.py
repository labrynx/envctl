"""Profile command group."""

from __future__ import annotations

from envctl.cli.typer_theme import create_typer_app

profile_app = create_typer_app(
    help_text="Manage local environment [bold]profiles[/bold].",
    lazy_subcommands={
        "list": {
            "import_path": "envctl.cli.commands.profile.commands.list:profile_list_command",
            "short_help": "List available profiles.",
        },
        "create": {
            "import_path": "envctl.cli.commands.profile.commands.create:profile_create_command",
            "short_help": "Create one explicit empty profile.",
        },
        "copy": {
            "import_path": "envctl.cli.commands.profile.commands.copy:profile_copy_command",
            "short_help": "Copy one profile into another.",
        },
        "remove": {
            "import_path": "envctl.cli.commands.profile.commands.remove:profile_remove_command",
            "short_help": "Remove one explicit profile.",
        },
        "path": {
            "import_path": "envctl.cli.commands.profile.commands.path:profile_path_command",
            "short_help": "Show the filesystem path for one profile.",
        },
    },
)
