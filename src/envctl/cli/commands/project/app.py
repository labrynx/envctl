"""Project command group."""

from __future__ import annotations

import typer

from envctl.cli.commands.project.commands import (
    project_bind_command,
    project_rebind_command,
    project_repair_command,
    project_unbind_command,
)

project_app = typer.Typer(help="Project identity and binding operations")

project_app.command("bind")(project_bind_command)
project_app.command("unbind")(project_unbind_command)
project_app.command("rebind")(project_rebind_command)
project_app.command("repair")(project_repair_command)
