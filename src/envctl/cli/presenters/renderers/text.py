from __future__ import annotations

import typer

from envctl.cli.presenters.models import (
    CommandOutput,
    OutputItem,
    OutputMessage,
    OutputSection,
)


def _emit_message(message: OutputMessage) -> None:
    """Emit one top-level message."""
    if message.level == "success":
        typer.secho(f"[OK] {message.text}", fg="green", bold=True, err=message.err)
        return
    if message.level == "warning":
        typer.secho(f"[WARN] {message.text}", fg="yellow", bold=True, err=message.err)
        return
    if message.level in {"failure", "error"}:
        typer.secho(f"[ERROR] {message.text}", fg="red", bold=True, err=message.err)
        return
    typer.echo(message.text, err=message.err)


def _emit_item(item: OutputItem) -> None:
    """Emit one section item."""
    if item.kind == "field":
        typer.secho(
            f"  {item.text}:",
            fg="bright_black",
            bold=True,
            nl=False,
            err=item.err,
        )
        typer.echo(f" {item.value or ''}", err=item.err)
        return

    if item.kind == "bullet":
        typer.echo(f"  - {item.text}", err=item.err)
        return

    typer.echo(item.text, err=item.err)


def _emit_section(section: OutputSection, *, leading_blank: bool = True) -> None:
    """Emit one titled section."""
    if leading_blank:
        typer.echo(err=section.err)

    if section.title:
        typer.secho(section.title, fg="bright_blue", bold=True, err=section.err)

    for item in section.items:
        _emit_item(item)


def emit_text(output: CommandOutput) -> None:
    """Emit one command output as styled terminal text."""
    rendered_any = False

    if output.title:
        typer.secho(output.title, fg="bright_blue", bold=True)
        rendered_any = True

    for message in output.messages:
        _emit_message(message)
        rendered_any = True

    for section in output.sections:
        _emit_section(section, leading_blank=rendered_any)
        rendered_any = True


__all__ = ["emit_text"]