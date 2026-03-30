"""CLI runtime state helpers."""

from __future__ import annotations

from dataclasses import dataclass

import click
import typer

from envctl.domain.runtime import OutputFormat


@dataclass(frozen=True)
class CliState:
    """Current CLI execution state."""

    output_format: OutputFormat = OutputFormat.TEXT


def set_cli_state(
    ctx: typer.Context,
    *,
    output_format: OutputFormat,
) -> None:
    """Persist the CLI state on the Typer/Click context."""
    ctx.obj = CliState(output_format=output_format)


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


def get_command_path() -> str | None:
    """Return the current command path when available."""
    ctx = click.get_current_context(silent=True)
    if ctx is None:
        return None
    return ctx.command_path