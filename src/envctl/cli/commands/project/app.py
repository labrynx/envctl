"""Project command group."""

from __future__ import annotations

from envctl.cli.typer_theme import create_typer_app

project_app = create_typer_app(
    help_text="Operate on project [bold]identity[/bold], [bold]binding[/bold], and recovery.",
    lazy_subcommands={
        "bind": {
            "import_path": "envctl.cli.commands.project.commands.bind:project_bind_command",
            "short_help": "Bind the current repository checkout to an existing vault.",
        },
        "unbind": {
            "import_path": "envctl.cli.commands.project.commands.unbind:project_unbind_command",
            "short_help": "Remove the local repo-to-vault binding for the current checkout.",
        },
        "rebind": {
            "import_path": "envctl.cli.commands.project.commands.rebind:project_rebind_command",
            "short_help": "Rebind the current checkout to a fresh project identity.",
        },
        "repair": {
            "import_path": "envctl.cli.commands.project.commands.repair:project_repair_command",
            "short_help": "Repair a missing, recovered, or incomplete local binding.",
        },
    },
)
