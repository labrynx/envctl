"""Main Typer application."""

from __future__ import annotations

import typer

from envctl.cli.callbacks import version_callback
from envctl.cli.commands.add import add_command
from envctl.cli.commands.check import check_command
from envctl.cli.commands.config import config_app
from envctl.cli.commands.doctor import doctor_command
from envctl.cli.commands.explain import explain_command
from envctl.cli.commands.export import export_command
from envctl.cli.commands.fill import fill_command
from envctl.cli.commands.init import init_command
from envctl.cli.commands.inspect import inspect_command
from envctl.cli.commands.profile import profile_app
from envctl.cli.commands.project import project_app
from envctl.cli.commands.remove import remove_command
from envctl.cli.commands.run import run_command_cli
from envctl.cli.commands.set import set_command
from envctl.cli.commands.status import status_command
from envctl.cli.commands.sync import sync_command
from envctl.cli.commands.unset import unset_command
from envctl.cli.commands.vault import vault_app
from envctl.cli.runtime import set_cli_state
from envctl.config.loader import load_config
from envctl.config.profile_resolution import resolve_active_profile
from envctl.domain.runtime import OutputFormat

VERSION_OPTION = typer.Option(
    None,
    "--version",
    "-V",
    help="Show the version and exit.",
    callback=version_callback,
    is_eager=True,
)
JSON_OPTION = typer.Option(
    False,
    "--json",
    help="Emit structured JSON output for supported commands.",
)
PROFILE_OPTION = typer.Option(
    None,
    "--profile",
    "-p",
    help="Select the active environment profile.",
)

app = typer.Typer(help="envctl - local environment control plane")
app.add_typer(config_app, name="config")
app.add_typer(vault_app, name="vault")
app.add_typer(project_app, name="project")
app.add_typer(profile_app, name="profile")


@app.callback()
def main(
    ctx: typer.Context,
    version: bool = VERSION_OPTION,
    json_output: bool = JSON_OPTION,
    profile: str | None = PROFILE_OPTION,
) -> None:
    """envctl - local environment control plane."""
    del version

    config = load_config()
    active_profile = resolve_active_profile(
        profile,
        config_default_profile=config.default_profile,
    )

    set_cli_state(
        ctx,
        output_format=OutputFormat.JSON if json_output else OutputFormat.TEXT,
        profile=active_profile,
    )


app.command("doctor")(doctor_command)
app.command("init")(init_command)
app.command("add")(add_command)
app.command("set")(set_command)
app.command("unset")(unset_command)
app.command("remove")(remove_command)
app.command("fill")(fill_command)
app.command("check")(check_command)
app.command("inspect")(inspect_command)
app.command("explain")(explain_command)
app.command("sync")(sync_command)
app.command("export")(export_command)
app.command(
    "run",
    context_settings={"allow_extra_args": True, "ignore_unknown_options": True},
)(run_command_cli)
app.command("status")(status_command)
