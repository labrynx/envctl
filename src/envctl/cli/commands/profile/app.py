"""Profile command group."""

from __future__ import annotations

import typer

from envctl.cli.commands.profile.commands.copy import profile_copy_command
from envctl.cli.commands.profile.commands.create import profile_create_command
from envctl.cli.commands.profile.commands.list import profile_list_command
from envctl.cli.commands.profile.commands.path import profile_path_command
from envctl.cli.commands.profile.commands.remove import profile_remove_command

profile_app = typer.Typer(help="Manage environment profiles")

profile_app.command("list")(profile_list_command)
profile_app.command("create")(profile_create_command)
profile_app.command("copy")(profile_copy_command)
profile_app.command("remove")(profile_remove_command)
profile_app.command("path")(profile_path_command)
