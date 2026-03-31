"""Terminal output helpers."""

from __future__ import annotations

import typer

# -----------------------------------------
# Basic messages
# -----------------------------------------


def print_success(message: str) -> None:
    """Print a success message."""
    typer.echo(f"[OK] {message}")


def print_warning(message: str) -> None:
    """Print a warning message."""
    typer.echo(f"[WARN] {message}")


def print_error(message: str) -> None:
    """Print an error message to stderr."""
    typer.echo(message, err=True)


def print_cancelled() -> None:
    """Print a standard cancellation message."""
    print_warning("Nothing was changed.")


# -----------------------------------------
# Structured output
# -----------------------------------------


def print_kv(key: str, value: str) -> None:
    """Print a key/value pair."""
    typer.echo(f"{key}: {value}")


def print_section(title: str) -> None:
    """Print a section header."""
    typer.echo()
    typer.echo(title)


def print_list(title: str, items: list[str]) -> None:
    """Print a bullet list."""
    if not items:
        return

    print_section(title)
    for item in items:
        typer.echo(f"  - {item}")


def print_block(lines: list[str]) -> None:
    """Print a block of lines."""
    for line in lines:
        typer.echo(line)


# -----------------------------------------
# Composite helpers
# -----------------------------------------


def print_result_summary(
    *,
    title: str,
    success: bool,
    metadata: dict[str, str],
    warnings: list[str] | None = None,
) -> None:
    """Render a consistent result summary."""
    if success:
        print_success(title)
    else:
        print_warning(title)

    for key, value in metadata.items():
        print_kv(key, value)

    if warnings:
        print_list("Warnings", warnings)
