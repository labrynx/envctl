"""Lazy-loading Typer group support for the envctl CLI."""

from __future__ import annotations

import importlib
from collections.abc import Mapping
from dataclasses import dataclass
from typing import Any

import click
import typer
from typer.core import TyperGroup

_LAZY_SUBCOMMANDS_KEY = "lazy_subcommands"


@dataclass(frozen=True, slots=True)
class _LazyTargetConfig:
    """Normalized configuration for one lazily loaded command target."""

    import_path: str
    context_settings: dict[str, Any] | None = None
    short_help: str | None = None


class LazyTyperGroup(TyperGroup):
    """Typer group that resolves configured subcommands only when needed."""

    def __init__(self, *args: Any, **attrs: Any) -> None:
        context_settings = dict(attrs.get("context_settings") or {})
        lazy_subcommands = context_settings.pop(_LAZY_SUBCOMMANDS_KEY, None) or {}
        attrs["context_settings"] = context_settings

        super().__init__(*args, **attrs)

        self._lazy_subcommands: dict[str, str | dict[str, Any]] = dict(lazy_subcommands)

    def list_commands(self, ctx: click.Context) -> list[str]:
        """Return both eagerly registered and lazily declared command names."""
        eager_commands = set(super().list_commands(ctx))
        lazy_commands = set(self._lazy_subcommands)
        return sorted(eager_commands | lazy_commands)

    def format_help(self, ctx: click.Context, formatter: click.HelpFormatter) -> None:
        """Mark help rendering so lazy commands can expose static metadata only."""
        ctx.meta["envctl_rendering_help"] = True
        try:
            super().format_help(ctx, formatter)
        finally:
            ctx.meta.pop("envctl_rendering_help", None)

    def get_command(self, ctx: click.Context, cmd_name: str) -> click.Command | None:
        """Resolve one command, materializing lazy targets on first access."""
        existing = super().get_command(ctx, cmd_name)
        if existing is not None:
            return existing

        target = self._lazy_subcommands.get(cmd_name)
        if target is None:
            return None

        config = _parse_lazy_target(target)
        if ctx.meta.get("envctl_rendering_help"):
            placeholder = _build_help_placeholder(cmd_name=cmd_name, config=config)
            if placeholder is not None:
                return placeholder

        command = _load_click_command(cmd_name=cmd_name, config=config)
        command.name = cmd_name
        self.commands[cmd_name] = command
        return command


def _build_help_placeholder(*, cmd_name: str, config: _LazyTargetConfig) -> click.Command | None:
    """Build one lightweight command placeholder for help rendering only."""
    if not config.short_help:
        return None

    return click.Command(
        name=cmd_name,
        help=config.short_help,
        short_help=config.short_help,
    )


def _load_click_command(*, cmd_name: str, config: _LazyTargetConfig) -> click.Command:
    """Load one Click command, Click group, or Typer app from an import target."""
    import_path = config.import_path
    context_settings = config.context_settings

    module_path, separator, attribute_name = import_path.partition(":")
    if not separator:
        raise ValueError(f"Invalid lazy command path: {import_path}")

    module = importlib.import_module(module_path)
    obj = getattr(module, attribute_name)

    if isinstance(obj, click.Command):
        return obj

    if isinstance(obj, typer.Typer):
        group = typer.main.get_group(obj)
        group.name = cmd_name
        return group

    if callable(obj):
        wrapper = typer.Typer(
            add_completion=False,
            rich_markup_mode="rich",
            context_settings=context_settings,
        )
        wrapper.command(name=cmd_name)(obj)
        command = typer.main.get_command(wrapper)
        command.name = cmd_name
        return command

    raise TypeError(
        f"Lazy command target {import_path!r} resolved to unsupported object {type(obj)!r}"
    )


def _parse_lazy_target(target: str | Mapping[str, Any]) -> _LazyTargetConfig:
    """Normalize one lazy target definition into one stable config object."""
    if isinstance(target, str):
        return _LazyTargetConfig(import_path=target)

    import_path = str(target["import_path"])
    context_settings = dict(target.get("context_settings") or {}) or None
    short_help = str(target["short_help"]) if "short_help" in target else None
    return _LazyTargetConfig(
        import_path=import_path,
        context_settings=context_settings,
        short_help=short_help,
    )
