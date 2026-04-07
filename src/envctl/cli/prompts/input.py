"""Terminal input adapters."""

from __future__ import annotations

import getpass

import typer


def prompt_string(
    message: str,
    *,
    default: str | None = None,
) -> str:
    """Prompt for a visible string value."""
    suffix = f" [{default}]" if default is not None else ""
    full_message = f"{message}{suffix}"

    return str(
        typer.prompt(
            full_message,
            default=default or "",
            show_default=False,
        )
    )


def prompt_secret(
    message: str,
    *,
    default: str | None = None,
) -> str:
    """Prompt for a secret value (hidden input)."""
    suffix = f" [{default}]" if default is not None else ""
    full_message = f"{message}{suffix}"

    value = getpass.getpass(f"{full_message}: ")
    return value if value else (default or "")


def confirm(
    message: str,
    *,
    default: bool = False,
) -> bool:
    """Prompt for a boolean confirmation."""
    return typer.confirm(message, default=default, show_default=True)
