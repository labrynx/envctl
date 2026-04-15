"""Main Typer application."""

from __future__ import annotations

from pathlib import Path
from typing import Literal

import typer

from envctl.cli.callbacks import version_callback
from envctl.cli.typer_theme import create_typer_app
from envctl.domain.runtime import OutputFormat

VERSION_OPTION = typer.Option(
    None,
    "--version",
    "-V",
    help="Show the version and exit.",
    callback=version_callback,
    is_eager=True,
)
OUTPUT_OPTION = typer.Option(
    OutputFormat.TEXT,
    "--output",
    "-o",
    help="Output format: json or text.",
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
        "  - [bold]check[/bold], [bold]inspect[/bold], [bold]inspect KEY[/bold] for resolution\n"
        "  - [bold]run[/bold], [bold]sync[/bold], [bold]export[/bold] for projection\n"
        "  - [bold]set[/bold], [bold]unset[/bold], [bold]fill[/bold] for local values"
    ),
    lazy_subcommands={
        "config": {
            "import_path": "envctl.cli.commands.config.app:config_app",
            "short_help": "Manage envctl configuration.",
        },
        "vault": {
            "import_path": "envctl.cli.commands.vault.app:vault_app",
            "short_help": "Inspect and maintain the local vault artifact.",
        },
        "project": {
            "import_path": "envctl.cli.commands.project.app:project_app",
            "short_help": "Operate on project identity, binding, and recovery.",
        },
        "profile": {
            "import_path": "envctl.cli.commands.profile.app:profile_app",
            "short_help": "Manage local environment profiles.",
        },
        "guard": {
            "import_path": "envctl.cli.commands.guard.app:guard_app",
            "short_help": "Protect Git history from envctl-specific secrets.",
        },
        "hooks": {
            "import_path": "envctl.cli.commands.hooks.app:hooks_app",
            "short_help": "Manage envctl-owned Git hooks for local secret protection.",
        },
        "hook": {
            "import_path": "envctl.cli.commands.hook.app:hook_app",
            "short_help": "Manage envctl-owned individual hook policies.",
        },
        "init": {
            "import_path": "envctl.cli.commands.init.command:init_command",
            "short_help": "Initialize the current project in the local vault.",
        },
        "add": {
            "import_path": "envctl.cli.commands.add.command:add_command",
            "short_help": (
                "Add one variable to the contract and store its"
                " initial value in the active profile."
            ),
        },
        "set": {
            "import_path": "envctl.cli.commands.set.command:set_command",
            "short_help": "Set one local value in the active profile.",
        },
        "unset": {
            "import_path": "envctl.cli.commands.unset.command:unset_command",
            "short_help": "Remove one local value from the active profile.",
        },
        "remove": {
            "import_path": "envctl.cli.commands.remove.command:remove_command",
            "short_help": "Remove one key from the contract and all persisted profiles.",
        },
        "fill": {
            "import_path": "envctl.cli.commands.fill.command:fill_command",
            "short_help": "Interactively fill missing required values for the active profile.",
        },
        "check": {
            "import_path": "envctl.cli.commands.check.command:check_command",
            "short_help": "Validate the current project environment against the contract.",
        },
        "inspect": {
            "import_path": "envctl.cli.commands.inspect.command:inspect_command",
            "short_help": "Inspect the resolved environment or one key in detail.",
        },
        "sync": {
            "import_path": "envctl.cli.commands.sync.command:sync_command",
            "short_help": "Write the resolved environment into a repository env file.",
        },
        "export": {
            "import_path": "envctl.cli.commands.export.command:export_command",
            "short_help": "Print the resolved environment as shell export lines.",
        },
        "run": {
            "import_path": "envctl.cli.commands.run.command:run_command_cli",
            "context_settings": {"allow_extra_args": True, "ignore_unknown_options": True},
        },
        "status": {
            "import_path": "envctl.cli.commands.status.command:status_command",
            "short_help": "Show a human-oriented project status summary.",
        },
    },
)


@app.callback()
def main(
    ctx: typer.Context,
    version: bool | None = VERSION_OPTION,
    output_format: OutputFormat = OUTPUT_OPTION,
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

    from envctl.cli.runtime import set_cli_state
    from envctl.config.loader import load_config

    config = load_config()

    set_cli_state(
        ctx,
        output_format=output_format,
        requested_profile=profile,
        requested_group=group,
        requested_set_name=set_name,
        requested_variable=variable,
        trace_enabled=trace_enabled,
        trace_format=trace_format,
        trace_output=trace_output,
        trace_file=trace_file,
        profile_observability=profile_observability,
        debug_errors=debug_errors,
        config=config,
    )
