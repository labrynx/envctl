"""Project command group."""

from __future__ import annotations

import typer

from envctl.cli.commands.project.commands import (
    project_bind_command,
    project_rebind_command,
    project_repair_command,
    project_unbind_command,
)

project_app = typer.Typer(help="Operate on the local project artifact.")

project_app.command("edit")(project_bind_command)
project_app.command("check")(project_rebind_command)
project_app.command("path")(project_repair_command)
project_app.command("show")(project_unbind_command)
