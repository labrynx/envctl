"""Shared Typer application configuration."""

from __future__ import annotations

from typing import Any, cast

import typer

_HELP_OPTION_NAMES = ["-h", "--help"]


def create_typer_app(*, help_text: str) -> typer.Typer:
    """Create one Typer app with envctl-consistent help styling."""
    app = typer.Typer(
        help=help_text,
        add_completion=False,
        no_args_is_help=True,
        rich_markup_mode="rich",
        context_settings={"help_option_names": _HELP_OPTION_NAMES},
    )
    info = cast(Any, app.info)
    if not hasattr(info, "add_completion"):
        info.add_completion = False
    return app
