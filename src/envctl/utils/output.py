"""Terminal output helpers."""

from __future__ import annotations

import typer

# -----------------------------------------
# Basic messages
# -----------------------------------------


def print_success(message: str) -> None:
    """Print a success message."""
    typer.secho(f"[OK] {message}", fg="green", bold=True)


def print_warning(message: str) -> None:
    """Print a warning message."""
    typer.secho(f"[WARN] {message}", fg="yellow", bold=True)


def print_failure(message: str, *, err: bool = False) -> None:
    """Print a failure message."""
    typer.secho(f"[ERROR] {message}", fg="red", bold=True, err=err)


def print_error(message: str) -> None:
    """Print an error message to stderr."""
    typer.secho(message, fg="red", bold=True, err=True)


def print_cancelled() -> None:
    """Print a standard cancellation message."""
    print_warning("Nothing was changed.")


# -----------------------------------------
# Structured output
# -----------------------------------------


def print_kv(key: str, value: str) -> None:
    """Print a key/value pair."""
    typer.secho(f"{key}:", fg="bright_black", bold=True, nl=False)
    typer.echo(f" {value}")


def print_section(title: str) -> None:
    """Print a section header."""
    typer.echo()
    typer.secho(title, fg="bright_blue", bold=True)


def print_list(title: str, items: list[str]) -> None:
    """Print a bullet list."""
    if not items:
        return

    print_section(title)
    for item in items:
        typer.echo(f"  - {item}")


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
