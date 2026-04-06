"""Shared helpers for human-oriented terminal presentation."""

from __future__ import annotations

from collections.abc import Iterable

import typer


def print_blank_line() -> None:
    """Print one blank line."""
    typer.echo()


def print_title(title: str) -> None:
    """Print a top-level section title."""
    typer.echo(title)


def print_section(title: str) -> None:
    """Print a titled section with a blank line before it."""
    print_blank_line()
    typer.echo(title)


def print_kv_line(label: str, value: str) -> None:
    """Print one aligned key/value line."""
    typer.echo(f"  {label}: {value}")


def print_bullet_list(items: Iterable[str]) -> None:
    """Print one bullet list."""
    for item in items:
        typer.echo(f"  - {item}")


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
