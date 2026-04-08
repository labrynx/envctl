"""Project command group."""

from __future__ import annotations

from envctl.cli.commands.project.commands import (
    project_bind_command,
    project_rebind_command,
    project_repair_command,
    project_unbind_command,
)
from envctl.cli.typer_theme import create_typer_app

project_app = create_typer_app(
    help_text="Operate on project [bold]identity[/bold], [bold]binding[/bold], and recovery."
)

project_app.command("bind")(project_bind_command)
project_app.command("unbind")(project_unbind_command)
project_app.command("rebind")(project_rebind_command)
project_app.command("repair")(project_repair_command)
