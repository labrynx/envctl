"""Main Typer application."""

from __future__ import annotations

import typer

from envctl.cli.callbacks import version_callback
from envctl.cli.commands.config import config_app
from envctl.cli.commands.doctor import doctor_command
from envctl.cli.commands.init import init_command
from envctl.cli.commands.remove import remove_command
from envctl.cli.commands.repair import repair_command
from envctl.cli.commands.set import set_command
from envctl.cli.commands.status import status_command
from envctl.cli.commands.unlink import unlink_command

app = typer.Typer(help="envctl - local environment vault manager")
app.add_typer(config_app, name="config")


@app.callback()
def main(
    version: bool = typer.Option(
        None,
        "--version",
        "-V",
        help="Show the version and exit.",
        callback=version_callback,
        is_eager=True,
    ),
) -> None:
    """envctl - local environment vault manager."""
    return None


@app.command("help")
def help_command(
    command: str | None = typer.Argument(default=None),
) -> None:
    """Show help for envctl or one command."""
    argv = [command, "--help"] if command else ["--help"]
    app(argv, standalone_mode=False)


app.command("doctor")(doctor_command)
app.command("init")(init_command)
app.command("repair")(repair_command)
app.command("unlink")(unlink_command)
app.command("remove")(remove_command)
app.command("status")(status_command)
app.command("set")(set_command)
