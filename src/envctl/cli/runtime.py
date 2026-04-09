"""CLI runtime state helpers."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Literal

import click
import typer

from envctl.constants import DEFAULT_PROFILE
from envctl.domain.runtime import OutputFormat
from envctl.domain.selection import ContractSelection


@dataclass(frozen=True)
class CliState:
    """Current CLI execution state."""

    output_format: OutputFormat = OutputFormat.TEXT
    profile: str = DEFAULT_PROFILE
    group: str | None = None
    set_name: str | None = None
    variable: str | None = None
    trace_enabled: bool | None = None
    trace_format: Literal["jsonl", "human"] | None = None
    trace_output: Literal["stderr", "file", "both"] | None = None
    trace_file: Path | None = None
    profile_observability: bool | None = None
    debug_errors: bool = False


def set_cli_state(
    ctx: typer.Context,
    *,
    output_format: OutputFormat,
    profile: str = DEFAULT_PROFILE,
    group: str | None = None,
    set_name: str | None = None,
    variable: str | None = None,
    trace_enabled: bool | None = None,
    trace_format: Literal["jsonl", "human"] | None = None,
    trace_output: Literal["stderr", "file", "both"] | None = None,
    trace_file: Path | None = None,
    profile_observability: bool | None = None,
    debug_errors: bool = False,
) -> None:
    """Persist the CLI state on the Typer/Click context."""
    ctx.obj = CliState(
        output_format=output_format,
        profile=profile,
        group=group,
        set_name=set_name,
        variable=variable,
        trace_enabled=trace_enabled,
        trace_format=trace_format,
        trace_output=trace_output,
        trace_file=trace_file,
        profile_observability=profile_observability,
        debug_errors=debug_errors,
    )


def get_cli_state() -> CliState:
    """Return the current CLI state, falling back to text output."""
    ctx = click.get_current_context(silent=True)
    if ctx is None or not isinstance(ctx.obj, CliState):
        return CliState()
    return ctx.obj


def get_output_format() -> OutputFormat:
    """Return the current output format."""
    return get_cli_state().output_format


def is_json_output() -> bool:
    """Return whether the current command should emit JSON."""
    return get_output_format() == OutputFormat.JSON


def get_active_profile() -> str:
    """Return the active CLI profile."""
    return get_cli_state().profile


def get_selected_group() -> str | None:
    """Return the active CLI group filter."""
    return get_cli_state().group


def get_selected_set() -> str | None:
    """Return the active CLI set selector."""
    return get_cli_state().set_name


def get_selected_var() -> str | None:
    """Return the active CLI variable selector."""
    return get_cli_state().variable


def get_contract_selection() -> ContractSelection:
    """Return the normalized active contract selection."""
    state = get_cli_state()
    return ContractSelection.from_selectors(
        group=state.group,
        set_name=state.set_name,
        variable=state.variable,
    )


def get_trace_enabled() -> bool | None:
    """Return trace override, if set."""
    return get_cli_state().trace_enabled


def get_trace_format() -> Literal["jsonl", "human"] | None:
    """Return trace format override, if set."""
    return get_cli_state().trace_format


def get_trace_output() -> Literal["stderr", "file", "both"] | None:
    """Return trace output override, if set."""
    return get_cli_state().trace_output


def get_trace_file() -> Path | None:
    """Return trace output file override, if set."""
    return get_cli_state().trace_file


def get_profile_observability() -> bool | None:
    """Return profile observability override, if set."""
    return get_cli_state().profile_observability


def get_command_path() -> str | None:
    """Return the current command path when available.

    Click/Typer test runners often expose the root command as ``root``.
    Normalize that prefix to the public CLI name so structured errors stay stable.
    """
    ctx = click.get_current_context(silent=True)
    if ctx is None:
        return None

    command_path = ctx.command_path.strip()
    if not command_path:
        return "envctl"

    if command_path == "root":
        return "envctl"

    if command_path.startswith("root "):
        return f"envctl{command_path[4:]}"

    return command_path


def is_error_debug_enabled() -> bool:
    """Return whether detailed error tracebacks should be shown."""
    return get_cli_state().debug_errors
