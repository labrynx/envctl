"""Shared helpers for CLI presentation model construction."""

from __future__ import annotations

from collections.abc import Iterable, Mapping
from typing import Any, TypeVar, cast

from envctl.cli.presenters.models import (
    CommandOutput,
    OutputItem,
    OutputMessage,
    OutputSection,
)

T = TypeVar("T")


_CONCAT_KEYS = {
    "warnings",
    "problems",
    "results",
    "findings",
    "runtime_warnings",
}

_FIRST_WINS_KEYS = {
    "command",
}

_EXCLUDED_KEYS = {
    "kind",
}


def _materialize(items: Iterable[T]) -> list[T]:
    """Materialize one iterable into a list."""
    return list(items)


def _merge_lists(left: list[Any], right: list[Any]) -> list[Any]:
    """Merge two metadata lists preserving order."""
    return [*left, *right]


def _deep_merge_dicts(left: Mapping[str, Any], right: Mapping[str, Any]) -> dict[str, Any]:
    """Deep-merge two metadata dictionaries."""
    merged: dict[str, Any] = dict(left)

    for key, right_value in right.items():
        if key not in merged:
            merged[key] = right_value
            continue

        left_value = merged[key]

        if isinstance(left_value, Mapping) and isinstance(right_value, Mapping):
            merged[key] = _deep_merge_dicts(
                cast("Mapping[str, Any]", left_value),
                cast("Mapping[str, Any]", right_value),
            )
            continue

        if isinstance(left_value, list) and isinstance(right_value, list):
            merged[key] = _merge_lists(left_value, right_value)
            continue

        merged[key] = right_value

    return merged


def _resolve_kind(current_kind: str | None, metadata: Mapping[str, Any]) -> str | None:
    """Resolve the effective output kind."""
    candidate = metadata.get("kind")
    if isinstance(candidate, str) and candidate:
        return candidate
    return current_kind


def _merge_concat_key(existing: Any, incoming: Any) -> list[Any]:
    """Merge one concatenated metadata field."""
    left = existing if isinstance(existing, list) else [existing]
    right = incoming if isinstance(incoming, list) else [incoming]
    return _merge_lists(left, right)


def _merge_existing_metadata_value(existing: Any, incoming: Any) -> Any:
    """Merge two existing metadata values."""
    if isinstance(existing, Mapping) and isinstance(incoming, Mapping):
        return _deep_merge_dicts(
            cast("Mapping[str, Any]", existing),
            cast("Mapping[str, Any]", incoming),
        )

    if isinstance(existing, list) and isinstance(incoming, list):
        return _merge_lists(existing, incoming)

    return incoming


def _merge_metadata_entry(
    merged: dict[str, Any],
    *,
    key: str,
    value: Any,
) -> None:
    """Merge one metadata entry into the accumulated dictionary."""
    if key in _EXCLUDED_KEYS:
        return

    if key not in merged:
        merged[key] = value
        return

    if key in _FIRST_WINS_KEYS:
        return

    if key in _CONCAT_KEYS:
        merged[key] = _merge_concat_key(merged[key], value)
        return

    merged[key] = _merge_existing_metadata_value(merged[key], value)


def _merge_one_metadata(
    merged: dict[str, Any],
    metadata: Mapping[str, Any],
) -> str | None:
    """Merge one metadata mapping and return its resolved kind, if any."""
    resolved_kind = _resolve_kind(None, metadata)

    for key, value in metadata.items():
        _merge_metadata_entry(
            merged,
            key=key,
            value=value,
        )

    return resolved_kind


def _merge_metadata(*metadatas: Mapping[str, Any]) -> dict[str, Any]:
    """Merge multiple metadata dictionaries with CLI-aware semantics."""
    merged: dict[str, Any] = {}
    resolved_kind: str | None = None

    for metadata in metadatas:
        if not metadata:
            continue

        resolved_kind = _resolve_kind(resolved_kind, metadata)
        _merge_one_metadata(merged, metadata)

    if resolved_kind is not None:
        merged["kind"] = resolved_kind

    return merged


def merge_outputs(*outputs: CommandOutput) -> CommandOutput:
    """Merge multiple command outputs into one.

    Rules:
    - title: first non-empty wins
    - messages: concatenated
    - sections: concatenated
    - metadata:
        - warnings and similar lists are concatenated
        - nested dicts are deep merged
        - scalar conflicts: last wins, except selected keys
        - kind: last non-empty wins
    """
    title = next((output.title for output in outputs if output.title), None)

    messages: list[OutputMessage] = []
    sections: list[OutputSection] = []

    for output in outputs:
        messages.extend(output.messages)
        sections.extend(output.sections)

    metadata = _merge_metadata(*(output.metadata for output in outputs))

    return CommandOutput(
        title=title,
        messages=messages,
        sections=sections,
        metadata=metadata,
    )


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
    rendered = _materialize(actions)
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
