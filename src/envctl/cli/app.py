"""Main Typer application."""

from __future__ import annotations

from pathlib import Path
from typing import Literal

import typer

from envctl.cli.callbacks import version_callback
from envctl.cli.commands.add import add_command
from envctl.cli.commands.check import check_command
from envctl.cli.commands.config import config_app
from envctl.cli.commands.doctor import doctor_command
from envctl.cli.commands.explain import explain_command
from envctl.cli.commands.export import export_command
from envctl.cli.commands.fill import fill_command
from envctl.cli.commands.guard import guard_app
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
from envctl.cli.decorators import emit_handled_error, emit_usage_error
from envctl.cli.runtime import set_cli_state
from envctl.cli.typer_theme import create_typer_app
from envctl.config.loader import load_config
from envctl.config.profile_resolution import resolve_active_profile
from envctl.domain.runtime import OutputFormat
from envctl.domain.selection import ContractSelection
from envctl.errors import EnvctlError
from envctl.observability import initialize_observability_context

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
GROUP_OPTION = typer.Option(
    None,
    "--group",
    "-g",
    help="Target only variables whose contract groups include NAME.",
)
SET_OPTION = typer.Option(
    None,
    "--set",
    help="Target one named contract set.",
)
VAR_OPTION = typer.Option(
    None,
    "--var",
    help="Target one explicit contract variable.",
)
TRACE_OPTION = typer.Option(
    None,
    "--trace/--no-trace",
    help="Enable/disable observability trace output for this execution.",
)
TRACE_FORMAT_OPTION = typer.Option(
    None,
    "--trace-format",
    help="Trace renderer format: human or jsonl.",
)
TRACE_OUTPUT_OPTION = typer.Option(
    None,
    "--trace-output",
    help="Trace destination: stderr, file, or both.",
)
TRACE_FILE_OPTION = typer.Option(
    None,
    "--trace-file",
    help="Trace output file path when --trace-output includes file.",
)
PROFILE_OBSERVABILITY_OPTION = typer.Option(
    None,
    "--profile-observability/--no-profile-observability",
    help="Print slow phase profile summary at command end.",
)
DEBUG_ERRORS_OPTION = typer.Option(
    False,
    "--debug-errors",
    help="Show Python traceback for unexpected internal errors.",
)

app = create_typer_app(
    help_text=(
        "[bold]envctl[/bold] keeps project environment requirements explicit and local.\n\n"
        "[bright_blue]Core flows[/bright_blue]\n"
        "  - [bold]check[/bold], [bold]inspect[/bold], [bold]explain[/bold] for resolution\n"
        "  - [bold]run[/bold], [bold]sync[/bold], [bold]export[/bold] for projection\n"
        "  - [bold]set[/bold], [bold]unset[/bold], [bold]fill[/bold] for local values"
    )
)
app.add_typer(config_app, name="config")
app.add_typer(vault_app, name="vault")
app.add_typer(project_app, name="project")
app.add_typer(profile_app, name="profile")
app.add_typer(guard_app, name="guard")


@app.callback()
def main(
    ctx: typer.Context,
    version: bool = VERSION_OPTION,
    json_output: bool = JSON_OPTION,
    profile: str | None = PROFILE_OPTION,
    group: str | None = GROUP_OPTION,
    set_name: str | None = SET_OPTION,
    variable: str | None = VAR_OPTION,
    trace_enabled: bool | None = TRACE_OPTION,
    trace_format: Literal["human", "jsonl"] | None = TRACE_FORMAT_OPTION,
    trace_output: Literal["stderr", "file", "both"] | None = TRACE_OUTPUT_OPTION,
    trace_file: Path | None = TRACE_FILE_OPTION,
    profile_observability: bool | None = PROFILE_OBSERVABILITY_OPTION,
    debug_errors: bool = DEBUG_ERRORS_OPTION,
) -> None:
    """envctl - local environment control plane."""
    del version

    command_name = ctx.invoked_subcommand or "envctl"
    initialize_observability_context(
        command_name=command_name,
        trace_enabled=trace_enabled,
        trace_format=trace_format,
        trace_output=trace_output,
        trace_file=trace_file,
        profile_observability=profile_observability,
    )

    try:
        selection = ContractSelection.from_selectors(
            group=group,
            set_name=set_name,
            variable=variable,
        )
        config = load_config()
        active_profile = resolve_active_profile(
            profile,
            config_default_profile=config.default_profile,
        )
    except ValueError as exc:
        emit_usage_error(str(exc), command="envctl")
        raise typer.Exit(code=2) from exc
    except EnvctlError as exc:
        command = "envctl"
        if ctx.invoked_subcommand is not None:
            command = f"envctl {ctx.invoked_subcommand}"
        emit_handled_error(
            exc,
            json_output=json_output,
            command=command,
        )
        raise typer.Exit(code=1) from exc

    set_cli_state(
        ctx,
        output_format=OutputFormat.JSON if json_output else OutputFormat.TEXT,
        profile=active_profile,
        group=selection.group,
        set_name=selection.set_name,
        variable=selection.variable,
        trace_enabled=trace_enabled,
        trace_format=trace_format,
        trace_output=trace_output,
        trace_file=trace_file,
        profile_observability=profile_observability,
        debug_errors=debug_errors,
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
