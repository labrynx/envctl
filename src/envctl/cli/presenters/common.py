"""Shared helpers for CLI presentation model construction."""

from __future__ import annotations

from collections.abc import Iterable
from typing import Any

from envctl.cli.presenters.models import (
    CommandOutput,
    OutputItem,
    OutputMessage,
    OutputSection,
)


def merge_outputs(*outputs: CommandOutput) -> CommandOutput:
    """Merge multiple command outputs into one."""
    title = next((output.title for output in outputs if output.title), None)

    messages: list[OutputMessage] = []
    sections: list[OutputSection] = []
    metadata: dict[str, Any] = {}

    for output in outputs:
        messages.extend(output.messages)
        sections.extend(output.sections)
        metadata.update(output.metadata)

    return CommandOutput(
        title=title,
        messages=messages,
        sections=sections,
        metadata=metadata,
    )


def blank_item(*, err: bool = False) -> OutputItem:
    """Build one blank raw line."""
    return OutputItem(kind="raw", text="", err=err)


def title_item(text: str, *, err: bool = False) -> OutputItem:
    """Build one title raw line."""
    return OutputItem(kind="raw", text=text, err=err)


def section(title: str, *items: OutputItem, err: bool = False) -> OutputSection:
    """Build one output section."""
    return OutputSection(title=title, items=list(items), err=err)


def field_item(key: str, value: str, *, err: bool = False) -> OutputItem:
    """Build one field item."""
    return OutputItem(kind="field", text=key, value=value, err=err)


def bullet_item(text: str, *, err: bool = False) -> OutputItem:
    """Build one bullet item."""
    return OutputItem(kind="bullet", text=text, err=err)


def raw_item(text: str, *, err: bool = False) -> OutputItem:
    """Build one raw text item."""
    return OutputItem(kind="raw", text=text, err=err)


def bullet_items(items: Iterable[str], *, err: bool = False) -> list[OutputItem]:
    """Build bullet items from an iterable of strings."""
    return [bullet_item(item, err=err) for item in items]


def field_items(items: Iterable[tuple[str, str]], *, err: bool = False) -> list[OutputItem]:
    """Build field items from key/value tuples."""
    return [field_item(key, value, err=err) for key, value in items]


def info_message(text: str, *, err: bool = False) -> OutputMessage:
    """Build one info message."""
    return OutputMessage(level="info", text=text, err=err)


def success_message(text: str, *, err: bool = False) -> OutputMessage:
    """Build one success message."""
    return OutputMessage(level="success", text=text, err=err)


def warning_message(text: str, *, err: bool = False) -> OutputMessage:
    """Build one warning message."""
    return OutputMessage(level="warning", text=text, err=err)


def failure_message(text: str, *, err: bool = False) -> OutputMessage:
    """Build one failure message."""
    return OutputMessage(level="failure", text=text, err=err)


def error_message(text: str, *, err: bool = True) -> OutputMessage:
    """Build one error message."""
    return OutputMessage(level="error", text=text, err=err)


def action_list_section(
    actions: Iterable[str],
    *,
    title: str = "Next steps",
    err: bool = False,
) -> OutputSection | None:
    """Build one action-list section when actions are available."""
    rendered = tuple(actions)
    if not rendered:
        return None

    return section(
        title,
        *(bullet_item(f"Run `{action}`", err=err) for action in rendered),
        err=err,
    )


def help_hint_section(
    command: str | None,
    *,
    title: str = "Next steps",
    err: bool = True,
) -> OutputSection:
    """Build one stable help-hint section for CLI usage errors."""
    target = "envctl --help" if not command else f"{command} --help"
    return section(
        title,
        bullet_item(f"Run `{target}`", err=err),
        err=err,
    )


def result_summary_messages(title: str, *, success: bool, err: bool = False) -> list[OutputMessage]:
    """Build summary messages for one action result."""
    if success:
        return [success_message(title, err=err)]
    return [warning_message(title, err=err)]


def result_summary_section(
    metadata: dict[str, str],
    *,
    title: str = "Details",
    err: bool = False,
) -> OutputSection | None:
    """Build one metadata section for a result summary."""
    if not metadata:
        return None

    return section(
        title,
        *(field_item(key, value, err=err) for key, value in metadata.items()),
        err=err,
    )


def warnings_section(
    warnings: Iterable[str],
    *,
    title: str = "Warnings",
    err: bool = False,
) -> OutputSection | None:
    """Build one warnings section when warnings are available."""
    rendered = tuple(warnings)
    if not rendered:
        return None

    return section(
        title,
        *(bullet_item(warning, err=err) for warning in rendered),
        err=err,
    )


def cancelled_message(*, err: bool = False) -> OutputMessage:
    """Build the standard cancellation message."""
    return warning_message("Nothing was changed.", err=err)


def cancelled_output(
    *,
    kind: str,
    err: bool = False,
    **metadata: Any,
) -> CommandOutput:
    """Build one standard cancelled command output."""
    return CommandOutput(
        messages=[cancelled_message(err=err)],
        metadata={
            "kind": kind,
            "cancelled": True,
            **metadata,
        },
    )
