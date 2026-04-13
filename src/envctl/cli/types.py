"""Shared CLI typing helpers."""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypedDict


class LazySubcommandSpec(TypedDict, total=False):
    """Specification for one lazily loaded CLI subcommand."""

    import_path: str
    context_settings: dict[str, Any]
    short_help: str


LazySubcommandValue = str | LazySubcommandSpec
LazySubcommands = Mapping[str, LazySubcommandValue]
