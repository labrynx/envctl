"""Shared Typer application configuration."""

from __future__ import annotations

from typing import Any, cast

import typer

from envctl.cli.lazy_group import LazyTyperGroup
from envctl.cli.types import LazySubcommands

_HELP_OPTION_NAMES = ["-h", "--help"]
_LAZY_SUBCOMMANDS_KEY = "lazy_subcommands"


def create_typer_app(
    *,
    help_text: str,
    lazy_subcommands: LazySubcommands | None = None,
) -> typer.Typer:
    """Create one Typer app with envctl-consistent help styling."""
    context_settings: dict[str, Any] = {"help_option_names": _HELP_OPTION_NAMES}
    if lazy_subcommands:
        context_settings[_LAZY_SUBCOMMANDS_KEY] = dict(lazy_subcommands)

    app = typer.Typer(
        cls=LazyTyperGroup,
        help=help_text,
        add_completion=False,
        no_args_is_help=True,
        rich_markup_mode="rich",
        context_settings=context_settings,
    )
    info = cast(Any, app.info)
    if not hasattr(info, "add_completion"):
        info.add_completion = False
    return app
