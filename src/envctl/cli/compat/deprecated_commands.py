"""Helpers for deprecated CLI command aliases."""

from __future__ import annotations

from envctl.domain.diagnostics import CommandWarning


def build_deprecated_command_warning(
    *,
    command_name: str,
    replacement: str,
    removal_version: str,
) -> CommandWarning:
    """Build one stable deprecated-command warning."""
    return CommandWarning(
        kind="deprecated_command",
        message=(
            f"Warning: `{command_name}` is deprecated and will be removed in {removal_version}.\n"
            f"Use `{replacement}` instead."
        ),
    )
