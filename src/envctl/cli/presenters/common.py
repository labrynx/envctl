"""Shared helpers for human-oriented terminal presentation."""

from __future__ import annotations

from collections.abc import Iterable

import typer


def print_blank_line(*, err: bool = False) -> None:
    """Print one blank line."""
    typer.echo(err=err)


def print_title(title: str, *, err: bool = False) -> None:
    """Print a top-level section title."""
    typer.secho(title, fg="bright_blue", bold=True, err=err)


def print_section(title: str, *, err: bool = False) -> None:
    """Print a titled section with a blank line before it."""
    print_blank_line(err=err)
    typer.secho(title, fg="bright_blue", bold=True, err=err)


def print_kv_line(label: str, value: str, *, err: bool = False) -> None:
    """Print one aligned key/value line."""
    typer.secho(f"  {label}:", fg="bright_black", bold=True, nl=False, err=err)
    typer.echo(f" {value}", err=err)


def print_bullet_list(items: Iterable[str], *, err: bool = False) -> None:
    """Print one bullet list."""
    for item in items:
        typer.echo(f"  - {item}", err=err)


def print_error_title(message: str) -> None:
    """Print one styled error title to stderr."""
    typer.secho("Error:", fg="red", bold=True, nl=False, err=True)
    typer.echo(f" {message}", err=True)


def print_action_list(actions: Iterable[str], *, err: bool = False) -> None:
    """Print one compact action list when actions are available."""
    rendered = tuple(actions)
    if not rendered:
        return

    print_section("Next steps", err=err)
    for action in rendered:
        typer.echo(f"  - Run `{action}`", err=err)


def print_help_hint(command: str | None, *, err: bool = True) -> None:
    """Print one stable help hint for CLI usage errors."""
    target = "envctl --help" if not command else f"{command} --help"
    print_section("Next steps", err=err)
    typer.echo(f"  - Run `{target}`", err=err)


def render_present_missing(value: bool) -> str:
    """Render one boolean as present/missing."""
    return "present" if value else "missing"


def render_valid_invalid(value: bool) -> str:
    """Render one boolean as valid/invalid."""
    return "valid" if value else "invalid"


def render_action_state(has_issues: bool) -> str:
    """Render a top-level human status."""
    return "action needed" if has_issues else "healthy"


def render_check_prefix(status: str) -> str:
    """Render a standard prefix for inspection output."""
    mapping = {
        "ok": "[OK]",
        "warn": "[WARN]",
        "fail": "[FAIL]",
    }
    return mapping.get(status, "[INFO]")
